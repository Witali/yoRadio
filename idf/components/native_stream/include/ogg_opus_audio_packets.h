#ifndef YORADIO_OGG_OPUS_AUDIO_PACKETS_H
#define YORADIO_OGG_OPUS_AUDIO_PACKETS_H

/* Audio packets only, after the committed OpusTags completion event. Header /
 * comment syntax and their different size policies remain separate. Sources
 * must be real CRC-verified ogg_page_input leases. Complete contiguous packets
 * borrow the held page; only cross-page prefixes allocate. A page ACK is still
 * the caller's action after real synthesis/output/EOStream cleanup. This owner
 * never claims that a decoder drained or closes a codec on the caller's behalf.
 * Initialize with {0}, never copy a live owner, reset to cancel/release storage.
 */
#include "ogg_page_input.h"
#include "opus_multistream_framing.h"
#ifndef OPK_REALLOC
#define OPK_REALLOC realloc
#endif
#ifndef OPK_FREE
#define OPK_FREE free
#endif

typedef enum {
    OPK_NEED_PAGE=0,OPK_PACKET=1,OPK_PAGE_DONE=2,OPK_INVALID=-1,
    OPK_MEMORY=-2,OPK_PACKET_POLICY=-3,OPK_MISSING_PREFIX=-4,OPK_LIMIT=-5
} opk_status;
typedef struct {
    const uint8_t *data;
    size_t bytes;
    uint64_t token;
    uint32_t generation,serial;
    bool borrowed;
} opus_audio_packet_view;
typedef struct {
    uint8_t *prefix;
    size_t prefix_size,capacity;
    const ogg_page_input *source;
    const uint8_t *page_data;
    size_t payload_at,page_bytes;
    unsigned segment,page_segments;
    uint32_t generation,serial;
    uint64_t token_sequence;
    bool active,page_active,ready,partial,eos_released,page_eos;
    opus_audio_packet_view view;
} ogg_opus_audio_packets;

static inline void opk_reset(ogg_opus_audio_packets *s) {
    uint64_t token=s->token_sequence;OPK_FREE(s->prefix);memset(s,0,sizeof(*s));s->token_sequence=token;
}
static inline bool opk_start_link(ogg_opus_audio_packets *s,const ogg_page_input *tags) {
    if(!s || !tags || s->active || s->page_active || s->ready || s->partial || !tags->ready ||
        !tags->event.crc_verified || !tags->event.opus || !(tags->event.flags&OOPT_TAGS) || tags->event.mapping>1)return false;
    s->generation=tags->event.generation;s->serial=tags->event.serial;s->active=true;s->eos_released=false;return true;
}
static inline opk_status opk_begin_page(ogg_opus_audio_packets *s,const ogg_page_input *input) {
    if(!s || !input || !s->active || s->page_active || s->ready || !input->ready || !input->event.crc_verified ||
        !(input->event.flags&OOPT_PAGE) || !input->event.opus || input->event.generation!=s->generation || input->event.serial!=s->serial ||
        (input->event.flags&(OOPT_HEAD|OOPT_TAGS)) || input->size<27 || !input->page || memcmp(input->page,"OggS\0",5))return OPK_INVALID;
    const uint8_t *page=input->page;unsigned count=page[26];size_t payload=27u+count,total=payload;
    if(payload>input->size || oopt_le32(page+14)!=input->event.serial || oopt_le32(page+18)!=input->event.sequence)return OPK_INVALID;
    for(unsigned i=0;i<count;++i)total+=page[27+i];
    if(total!=input->size)return OPK_INVALID;
    if(count && ((page[5]&1u)!=0)!=s->partial)return (page[5]&1u)?OPK_MISSING_PREFIX:OPK_INVALID;
    s->source=input;s->page_data=input->page;s->page_bytes=input->size;s->page_segments=count;
    s->page_eos=(input->event.flags&OOPT_LINK_END)!=0;s->payload_at=payload;s->segment=0;s->page_active=true;return OPK_NEED_PAGE;
}
static inline bool opk_page_exhausted(const ogg_opus_audio_packets *s) {
    return s && s->page_active && !s->ready && s->segment==s->page_segments && s->payload_at==s->page_bytes;
}
static inline opk_status opk_next(ogg_opus_audio_packets *s,opus_audio_packet_view *out) {
    if(!s || !out || !s->active)return OPK_INVALID;
    if(s->page_active && (!s->source->ready || s->source->page!=s->page_data || s->source->size!=s->page_bytes))return OPK_INVALID;
    if(s->ready){*out=s->view;return OPK_PACKET;}
    if(!s->page_active)return OPK_NEED_PAGE;
    const uint8_t *page=s->source->page;unsigned count=page[26];
    if(s->segment==count)return opk_page_exhausted(s)?OPK_PAGE_DONE:OPK_INVALID;
    unsigned next=s->segment;size_t span=0;bool complete=false;
    while(next<count) {unsigned lace=page[27+next++];span+=lace;if(lace<255){complete=true;break;}}
    if(s->payload_at>s->page_bytes || span>s->page_bytes-s->payload_at)return OPK_INVALID;
    if(s->prefix_size>OMF_FAMILY01_MAX_PACKET || span>OMF_FAMILY01_MAX_PACKET-s->prefix_size)return OPK_PACKET_POLICY;
    size_t bytes=s->prefix_size+span;
    if(complete && (!bytes || s->token_sequence==UINT64_MAX))return bytes?OPK_LIMIT:OPK_INVALID;
    bool borrowed=!s->partial && complete;
    if(!borrowed) {
        if(bytes>s->capacity) {
            size_t capacity=s->capacity?s->capacity:256;
            while(capacity<bytes)capacity=capacity>OMF_FAMILY01_MAX_PACKET/2u?OMF_FAMILY01_MAX_PACKET:capacity*2u;
            uint8_t *larger=OPK_REALLOC(s->prefix,capacity);if(!larger)return OPK_MEMORY;
            s->prefix=larger;s->capacity=capacity;
        }
        if(span)memcpy(s->prefix+s->prefix_size,page+s->payload_at,span);
        s->prefix_size=bytes;
    }
    const uint8_t *data=borrowed?page+s->payload_at:s->prefix;s->segment=next;s->payload_at+=span;s->partial=!complete;
    if(!complete)return opk_page_exhausted(s)?OPK_PAGE_DONE:OPK_INVALID;
    s->view=(opus_audio_packet_view){.data=data,.bytes=bytes,.token=++s->token_sequence,.generation=s->generation,.serial=s->serial,.borrowed=borrowed};
    s->ready=true;*out=s->view;return OPK_PACKET;
}
static inline bool opk_consume(ogg_opus_audio_packets *s,uint32_t generation,uint32_t serial,uint64_t token) {
    if(!s || !s->active || !s->ready || generation!=s->generation || serial!=s->serial || token!=s->view.token)return false;
    s->ready=false;s->prefix_size=0;memset(&s->view,0,sizeof(s->view));return true;
}

/* Call only AFTER the caller's actual successful opi_ack. No page pointer is
 * retained after this operation; a continuation prefix is independently owned.
 * It confirms metadata retirement, never decoder drain / output completion.
 */
static inline bool opk_page_released(ogg_opus_audio_packets *s,const ogg_page_input *input) {
    if(!s || !input || s->source!=input || !opk_page_exhausted(s) || input->ready || input->size ||
        input->page!=s->page_data || input->capacity<s->page_bytes)return false;
    s->eos_released=s->page_eos;s->source=NULL;s->page_data=NULL;s->payload_at=s->page_bytes=0;
    s->segment=s->page_segments=0;s->page_active=s->page_eos=false;return true;
}
static inline bool opk_finish_link(ogg_opus_audio_packets *s) {
    if(!s || !s->active || s->page_active || s->ready || s->partial || !s->eos_released)return false;
    OPK_FREE(s->prefix);s->prefix=NULL;s->prefix_size=s->capacity=0;s->active=false;return true;
}
#endif
