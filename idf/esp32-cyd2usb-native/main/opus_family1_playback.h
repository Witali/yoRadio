#ifndef YORADIO_OPUS_FAMILY1_PLAYBACK_H
#define YORADIO_OPUS_FAMILY1_PLAYBACK_H

/* Adapter for a caller's SAME CRC-verified ogg_page_input owner.
 * Only family1 is handled here; this does not feed a second page observer.
 * Initialize at a stable address with {0}; do not move a live owner. The caller
 * routes the verified HEAD and every following page through ofp_page, including
 * comment continuation/nil pages. AUDIO starts only at the committed TAGS event.
 *
 * Output is bounded, full logical-C PCM48/S16LE in Vorbis speaker order. It is
 * never a stereo truncation/downmix. Header gain is metadata, NOT applied here.
 * The callback must synchronously copy/consume a borrowed chunk and attach the
 * explicit family1 speaker layout and gain to its queue item. It must observe
 * generation/Stop itself while waiting for queue space. A false send is fatal:
 * neither advancing trim nor already queued chunks may be replayed.
 *
 * Successful EOS closes every public handle BEFORE the actual page ACK. A
 * failed close retains handles/config addresses, held page and packet storage.
 * Retry ofp_page on the SAME held EOS page, or call ofp_abandon until successful.
 * Any other error is terminal for this owner until successful ofp_abandon.
 * Never reset its page owner, publish a released generation or acknowledge
 * decoder maintenance while ofp_abandon reports cleanup_pending.
 * After successful abandon the caller must separately reset its page owner;
 * abandon does NOT fake an ACK or claim an incomplete link drained.
 *
 * Tags length/count and declared UTF-8 are streamed without comment allocation;
 * arbitrary binary tail is permitted. Tag names/R128 gains are not interpreted.
 * Container resynchronization/multiplexing and legal live joins remain separate
 * timeline gates. The 61440B cap applies only after TAGS. Peak allocations remain resource
 * gates: verified page + optional packet prefix + real public handles + scratch
 * <=23040B + <=92160B unique mapped-channel planes. Output gathers <=2048B in
 * the already-owned raw scratch AFTER every needed stream's PCM was staged.
 * Classic ESP32 splits large plane sets into word-only allocations, allowing
 * its public32-bit heap to use IRAM where available. Small/C1/C2 workspaces
 * retain their byte-DRAM path. This does not change public packet cadence.
 * All-silent maps use immutable zero storage, not a per-owner stack/heap chunk.
 */
#include "ogg_opus_audio_packets.h"
#include "opus_family1_decoder.h"
#include "opus_pcm_trim.h"
#include "opus_tags_stream.h"
#ifndef OFP_REALLOC
#define OFP_REALLOC realloc
#endif
#ifndef OFP_FREE
#define OFP_FREE free
#endif

#if defined(ESP_PLATFORM)
#include "sdkconfig.h"
#if defined(CONFIG_IDF_TARGET_ESP32) && CONFIG_IDF_TARGET_ESP32 && \
    !defined(OFP_WORD_ALLOC) && !defined(OFP_WORD_FREE)
#include "esp_heap_caps.h"
#define OFP_WORD_ALLOC(bytes) heap_caps_malloc((bytes),MALLOC_CAP_INTERNAL|MALLOC_CAP_32BIT)
#define OFP_WORD_FREE(pointer) heap_caps_free(pointer)
#endif
#endif
#if defined(OFP_WORD_ALLOC) != defined(OFP_WORD_FREE)
#error OFP_WORD_ALLOC and OFP_WORD_FREE must be provided together
#endif
#ifdef OFP_WORD_ALLOC
#include "pcm_word_plane.h"
#endif

enum { OFP_CHUNK_FRAMES=128, OFP_RATE=48000, OFP_BYTE_PLANE_LIMIT=23040 };
static const uint8_t ofp_zero_chunk[OFP_CHUNK_FRAMES*8*2]={0};
typedef enum {
    OFP_OK=0,OFP_ARGUMENT,OFP_MOVED,OFP_BUSY,OFP_CANCELLED,OFP_CONTAINER,
    OFP_HEADER,OFP_PACKET,OFP_PACKET_POLICY,OFP_MEMORY,OFP_DECODER,OFP_TRIM,
    OFP_OUTPUT,OFP_CLEANUP
} ofp_status;
typedef struct {
    ofp_status code;
    int detail;
    ofd_result decoder;
    bool cleanup_pending;
} ofp_result;
typedef struct {
    bool (*cancelled)(void *);
    bool (*output48_s16le)(void *,uint32_t,const opus_family1_plan *,const uint8_t *,size_t);
    void (*yield)(void *);
    void *context;
} ofp_callbacks;
typedef enum { OFP_EMPTY=0,OFP_TAGS,OFP_AUDIO,OFP_EOS_CLOSE } ofp_phase;
typedef struct opus_family1_playback {
    const struct opus_family1_playback *anchor;
    ogg_page_input *source;
    opus_family1_decoder decoder;
    ogg_opus_audio_packets packets;
    opus_pcm_trim trim;
    opus_tags_stream tags;
    opus_family1_plan plan;
    uint8_t head[29],head_bytes;
    uint8_t plane_for_speaker[8],plane_slot[8],plane_channel[8],plane_count;
    uint8_t *planes;
    size_t capacity,produced[8];
#ifdef OFP_WORD_ALLOC
    volatile uint32_t *word_planes[8];
    size_t word_capacity; /* Rounded bytes per unique plane. */
    bool word_mode;
#endif
    uint16_t samples;
    uint32_t generation,serial;
    uint64_t close_page_token;
    ofp_phase phase;
    bool blocked,stage_active;
} opus_family1_playback;

static inline ofp_result ofp_code(ofp_status code) {
    ofp_result r={.code=code};return r;
}
static inline ofp_status ofp_decoder_code(ofd_result decoded) {
    if(decoded.code==OFD_MEMORY || (decoded.public_error_known && decoded.public_error==ESP_AUDIO_ERR_MEM_LACK))return OFP_MEMORY;
    return decoded.code==OFD_PACKET_POLICY?OFP_PACKET_POLICY:OFP_DECODER;
}
static inline ofp_result ofp_block(opus_family1_playback *s,ofp_status code,int detail) {
    s->blocked=true;ofp_result r=ofp_code(code);r.detail=detail;r.cleanup_pending=ofd_has_handles(&s->decoder);return r;
}
static inline bool ofp_has_input(const opus_family1_playback *s) {
    return s && (s->phase!=OFP_EMPTY || s->blocked || s->packets.active || s->packets.prefix ||
        s->planes || ofd_has_handles(&s->decoder)
#ifdef OFP_WORD_ALLOC
        || s->word_mode
#endif
        );
}

static inline void ofp_free_planes(opus_family1_playback *s) {
    OFP_FREE(s->planes);s->planes=NULL;s->capacity=0;
#ifdef OFP_WORD_ALLOC
    for(unsigned plane=0;plane<8;++plane) {
        if(s->word_planes[plane])OFP_WORD_FREE((void *)s->word_planes[plane]);
        s->word_planes[plane]=NULL;
    }
    s->word_capacity=0;s->word_mode=false;
#endif
}

#ifdef OFP_WORD_ALLOC
static inline bool ofp_reserve_word_planes(opus_family1_playback *s,uint16_t samples) {
    size_t bytes=((size_t)samples*2u+3u)&~(size_t)3u;
    if(s->word_mode && bytes<=s->word_capacity)return true;
    volatile uint32_t *candidate[8]={0};
    for(unsigned plane=0;plane<s->plane_count;++plane) {
        candidate[plane]=OFP_WORD_ALLOC(bytes);
        if(!candidate[plane] || ((uintptr_t)candidate[plane]&3u)) {
            for(unsigned owned=0;owned<=plane;++owned)
                if(candidate[owned])OFP_WORD_FREE((void *)candidate[owned]);
            return false;
        }
        pcm_word_plane_clear(candidate[plane],bytes/4u);
    }
    /* Previous-packet samples have already been published. Keep their storage
     * unchanged until every replacement succeeds; never realloc/copy bytes
     * through a pointer which may address32-bit-only IRAM.
     */
    ofp_free_planes(s);
    for(unsigned plane=0;plane<s->plane_count;++plane)s->word_planes[plane]=candidate[plane];
    s->word_capacity=bytes;s->capacity=bytes*s->plane_count;s->word_mode=true;
    return true;
}

static inline bool ofp_gather_word_planes(const opus_family1_playback *s,size_t first,
    size_t frames,uint8_t *output,size_t capacity,size_t *written) {
    size_t bytes=frames*s->plan.channels*2u;
    if(!output || !written || first>s->samples || frames>s->samples-first || bytes>capacity)return false;
    size_t at=0;
    for(size_t frame=0;frame<frames;++frame)for(unsigned speaker=0;speaker<s->plan.channels;++speaker) {
        unsigned plane=s->plane_for_speaker[speaker];uint16_t bits=0;
        if(plane!=OF1_SILENCE) {
            if(plane>=s->plane_count || !s->word_planes[plane])return false;
            bits=pcm_word_plane_load(s->word_planes[plane],first+frame);
        }
        output[at++]=(uint8_t)bits;output[at++]=(uint8_t)(bits>>8);
    }
    *written=at;return true;
}
#endif

/* Real public close is retryable. Preserve ALL page/packet/plane ownership if
 * even one handle remains. The caller's ogg_page_input is never reset here.
 */
static inline ofp_result ofp_abandon(opus_family1_playback *s) {
    if(!s)return ofp_code(OFP_ARGUMENT);
    if(s->anchor && s->anchor!=s)return ofp_code(OFP_MOVED);
    ofd_result closed=ofd_close(&s->decoder);
    if(closed.code!=OFD_OK || closed.cleanup_pending) {
        s->blocked=true;
        ofp_result r=ofp_code(OFP_CLEANUP);r.decoder=closed;r.cleanup_pending=closed.cleanup_pending;return r;
    }
    opk_reset(&s->packets);opt_reset(&s->trim);ots_reset(&s->tags);ofp_free_planes(s);
    s->source=NULL;s->head_bytes=0;s->plane_count=0;s->samples=0;s->generation=s->serial=0;
    s->close_page_token=0;s->blocked=s->stage_active=false;s->phase=OFP_EMPTY;
    memset(s->produced,0,sizeof(s->produced));return ofp_code(OFP_OK);
}

typedef struct {opus_family1_playback *s;const ofp_callbacks *cb;ofp_status error;int detail;} ofp_sink_context;
static inline bool ofp_sink_cancelled(ofp_sink_context *c) {
    if(!c->cb->cancelled(c->cb->context))return false;
    c->error=OFP_CANCELLED;return true;
}
static inline bool ofp_sink_begin(void *opaque,const opus_family1_plan *plan,uint32_t generation,uint16_t samples) {
    ofp_sink_context *c=opaque;opus_family1_playback *s=c->s;
    if(ofp_sink_cancelled(c))return false;
    if(generation!=s->generation || plan!=&s->decoder.plan || !samples || samples>5760 || s->stage_active) {
        c->error=OFP_DECODER;c->detail=OFD_CONTRACT;return false;
    }
    size_t bytes=(size_t)samples*s->plane_count*2u;
#ifdef OFP_WORD_ALLOC
    if(s->word_mode || bytes>OFP_BYTE_PLANE_LIMIT) {
        if(!ofp_reserve_word_planes(s,samples)){c->error=OFP_MEMORY;c->detail=(int)bytes;return false;}
    } else
#endif
    if(bytes>s->capacity) {
        uint8_t *larger=OFP_REALLOC(s->planes,bytes);
        if(!larger) {
#ifdef OFP_WORD_ALLOC
            /* A small byte workspace can still be refused after decoder/link
             * transitions. Try the same atomic word-plane storage before
             * reporting exhaustion; ordinary successful byte paths stay hot.
             */
            if(!ofp_reserve_word_planes(s,samples))
#endif
            {c->error=OFP_MEMORY;c->detail=(int)bytes;return false;}
        } else {s->planes=larger;s->capacity=bytes;}
    }
    memset(s->produced,0,sizeof(s->produced));s->samples=samples;s->stage_active=true;return true;
}
static inline bool ofp_sink_write(void *opaque,uint8_t slot,uint8_t stream,uint8_t width,size_t offset,const uint8_t *pcm,size_t frames) {
    ofp_sink_context *c=opaque;opus_family1_playback *s=c->s;
    if(ofp_sink_cancelled(c))return false;
    if(!s->stage_active || slot>=s->plan.needed || stream!=s->plan.stream_id[slot] || width!=s->plan.stream_channels[slot] ||
        offset!=s->produced[slot] || offset>s->samples || frames>s->samples-offset || (frames && !pcm)) {
        c->error=OFP_DECODER;c->detail=OFD_CONTRACT;return false;
    }
    /* Only referenced decoded channels are staged. A coupled stream's unused
     * companion does not double persistent plane memory; duplicate maps alias.
     */
#ifdef OFP_WORD_ALLOC
    if(s->word_mode) {
        for(unsigned plane=0;plane<s->plane_count;++plane)if(s->plane_slot[plane]==slot) {
            for(size_t frame=0;frame<frames;++frame) {
                const uint8_t *from=pcm+(frame*width+s->plane_channel[plane])*2u;
                uint16_t bits=(uint16_t)((uint16_t)from[0]|((uint16_t)from[1]<<8));
                pcm_word_plane_store(s->word_planes[plane],offset+frame,bits);
            }
        }
    } else
#endif
    for(unsigned plane=0;plane<s->plane_count;++plane)if(s->plane_slot[plane]==slot) {
        uint8_t *to=s->planes+((size_t)plane*s->samples+offset)*2u;
        for(size_t frame=0;frame<frames;++frame) {
            const uint8_t *from=pcm+(frame*width+s->plane_channel[plane])*2u;
            to[frame*2u]=from[0];to[frame*2u+1u]=from[1];
        }
    }
    s->produced[slot]+=frames;return true;
}
static inline bool ofp_sink_finish(void *opaque) {
    ofp_sink_context *c=opaque;opus_family1_playback *s=c->s;
    if(ofp_sink_cancelled(c))return false;
    if(!s->stage_active){c->error=OFP_DECODER;c->detail=OFD_CONTRACT;return false;}
    for(unsigned slot=0;slot<s->plan.needed;++slot)if(s->produced[slot]!=s->samples) {
        c->error=OFP_DECODER;c->detail=OFD_CONTRACT;return false;
    }
    of1_channel_view views[8]={{0}};
#ifdef OFP_WORD_ALLOC
    if(!s->word_mode)
#endif
    for(unsigned speaker=0;speaker<s->plan.channels;++speaker) {
        unsigned plane=s->plane_for_speaker[speaker];views[speaker].frames=s->samples;
        if(plane==OF1_SILENCE)views[speaker].silence=true;
        else {views[speaker].data=s->planes+(size_t)plane*s->samples*2u;views[speaker].stride=2;}
    }
    opus_pcm_span span={0};unsigned frame_bytes=s->plan.channels*2u;
    opus_pcm_trim_status trimmed=opt_clip(&s->trim,s->generation,OFP_RATE,s->plan.channels,16,(size_t)s->samples*frame_bytes,&span);
    if(trimmed!=OPT_OK){c->error=OFP_TRIM;c->detail=trimmed;return false;}
    size_t first=span.offset/frame_bytes,remaining=span.size/frame_bytes;
    while(remaining) {
        if(ofp_sink_cancelled(c))return false;
        size_t frames=remaining>OFP_CHUNK_FRAMES?OFP_CHUNK_FRAMES:remaining,written=0;
        const uint8_t *chunk=ofp_zero_chunk;
        if(s->plan.needed) {
            /* Public decode has returned and all referenced samples now live
             * in independent planes. No next decode/close occurs until this
             * synchronous output callback returns, so scratch is reusable.
             */
            bool gathered=false;
            if(s->decoder.scratch) {
#ifdef OFP_WORD_ALLOC
                if(s->word_mode)gathered=ofp_gather_word_planes(s,first,frames,s->decoder.scratch,s->decoder.capacity,&written);
                else
#endif
                gathered=of1_gather_s16(views,s->plan.channels,first,frames,s->decoder.scratch,s->decoder.capacity,&written)==OF1_OK;
            }
            if(!gathered) {
                c->error=OFP_DECODER;c->detail=OFD_CONTRACT;return false;
            }
            chunk=s->decoder.scratch;
        } else {
            written=frames*frame_bytes;
        }
        if(!c->cb->output48_s16le(c->cb->context,s->generation,&s->plan,chunk,written)) {
            c->error=c->cb->cancelled(c->cb->context)?OFP_CANCELLED:OFP_OUTPUT;return false;
        }
        first+=frames;remaining-=frames;
    }
    s->stage_active=false;s->samples=0;return true;
}
static inline void ofp_sink_abort(void *opaque) {
    ofp_sink_context *c=opaque;c->s->stage_active=false;c->s->samples=0;memset(c->s->produced,0,sizeof(c->s->produced));
}
static inline void ofp_sink_yield(void *opaque) {
    ofp_sink_context *c=opaque;if(c->cb->yield)c->cb->yield(c->cb->context);
}
static inline ofp_result ofp_ack_headers(opus_family1_playback *s,ogg_page_input *input) {
    return opi_ack(input,s->generation,input->event.token)?ofp_code(OFP_OK):ofp_block(s,OFP_CONTAINER,OPI_INVALID);
}
static inline ofp_result ofp_close_eos(opus_family1_playback *s,ogg_page_input *input) {
    ofd_result closed=ofd_close(&s->decoder);
    if(closed.code!=OFD_OK || closed.cleanup_pending) {
        ofp_result r=ofp_code(OFP_CLEANUP);r.decoder=closed;r.cleanup_pending=closed.cleanup_pending;return r;
    }
    bool audio=s->packets.page_active;
    if(!opi_ack(input,s->generation,s->close_page_token) || (audio && !opk_page_released(&s->packets,input)))
        return ofp_block(s,OFP_CONTAINER,OPI_INVALID);
    if(audio && !opk_finish_link(&s->packets))return ofp_block(s,OFP_PACKET,OPK_INVALID);
    /* Empty links end on TAGS, before an AUDIO page lease exists. */
    if(!audio)opk_reset(&s->packets);
    opt_reset(&s->trim);ots_reset(&s->tags);ofp_free_planes(s);s->head_bytes=s->plane_count=0;
    s->phase=OFP_EMPTY;s->source=NULL;s->close_page_token=0;return ofp_code(OFP_OK);
}

/* Process exactly one ready verified family1 page. On a non-EOS successful
 * page the selected handles persist. A failed close is the ONLY retryable page
 * result; it cannot synthesize/publish that EOS PCM again. Public API seams are
 * optional and intended for explicitly labelled HOST contract qualification.
 */
static inline ofp_result ofp_page(opus_family1_playback *s,ogg_page_input *input,
    const ofp_callbacks *callbacks,const ofd_public_api *api) {
    if(!s || !input || !callbacks || !callbacks->cancelled || !callbacks->output48_s16le)return ofp_code(OFP_ARGUMENT);
    if(s->anchor && s->anchor!=s)return ofp_code(OFP_MOVED);
    if(s->blocked)return ofp_block(s,OFP_BUSY,0);
    if(!input->ready || !input->event.crc_verified || !input->event.opus || input->event.mapping!=1 ||
        !(input->event.flags&OOPT_PAGE))return ofp_code(OFP_ARGUMENT);
    if(s->phase!=OFP_EMPTY && (s->source!=input || input->event.generation!=s->generation || input->event.serial!=s->serial))
        return ofp_block(s,OFP_CONTAINER,OPI_INVALID);
    if(callbacks->cancelled(callbacks->context))return ofp_block(s,OFP_CANCELLED,0);
    bool eos=(input->event.flags&OOPT_LINK_END)!=0;
    if(s->phase==OFP_EOS_CLOSE) {
        if(!eos || input->event.token!=s->close_page_token)return ofp_block(s,OFP_CONTAINER,OPI_INVALID);
        return ofp_close_eos(s,input);
    }
    if(s->phase==OFP_EMPTY) {
        if(!(input->event.flags&OOPT_HEAD) || (input->event.flags&OOPT_TAGS) || input->size<27 || !input->page)return ofp_code(OFP_ARGUMENT);
        size_t payload=27u+input->page[26];opus_family1_plan plan;
        of1_status parsed=payload<=input->size?of1_plan_header(input->page+payload,input->size-payload,&plan):OF1_INVALID;
        if(parsed!=OF1_OK){ofp_result r=ofp_code(OFP_HEADER);r.detail=parsed;return r;}
        if(plan.channels!=input->event.channels || plan.pre_skip!=input->event.pre_skip)return ofp_code(OFP_ARGUMENT);
        s->anchor=s;s->source=input;s->plan=plan;s->generation=input->event.generation;s->serial=input->event.serial;
        s->head_bytes=(uint8_t)(21u+plan.channels);memcpy(s->head,input->page+payload,s->head_bytes);
        s->plane_count=0;
        for(unsigned speaker=0;speaker<plan.channels;++speaker) {
            unsigned plane=0;
            if(plan.map[speaker]==OF1_SILENCE){s->plane_for_speaker[speaker]=OF1_SILENCE;continue;}
            for(;plane<s->plane_count;++plane)if(s->plane_slot[plane]==plan.speaker_slot[speaker] && s->plane_channel[plane]==plan.speaker_channel[speaker])break;
            if(plane==s->plane_count) {
                s->plane_slot[plane]=plan.speaker_slot[speaker];s->plane_channel[plane]=plan.speaker_channel[speaker];++s->plane_count;
            }
            s->plane_for_speaker[speaker]=(uint8_t)plane;
        }
        opus_pcm_trim_status trimmed=opt_begin(&s->trim,s->generation,plan.pre_skip,plan.channels);
        if(trimmed!=OPT_OK)return ofp_block(s,OFP_TRIM,trimmed);
        if(!ots_begin(&s->tags,input))return ofp_block(s,OFP_HEADER,OTS_ARGUMENT);
        s->phase=OFP_TAGS;return ofp_ack_headers(s,input);
    }
    if(input->event.flags&OOPT_HEAD)return ofp_block(s,OFP_CONTAINER,OPI_INVALID);
    if(s->phase==OFP_TAGS) {
        opus_tags_status tags=ots_page(&s->tags,input);
        if(tags<0)return ofp_block(s,OFP_HEADER,tags);
        if(tags==OTS_MORE)return ofp_ack_headers(s,input);
        if(!opk_start_link(&s->packets,input))return ofp_block(s,OFP_PACKET,OPK_INVALID);
        if(!eos) {
            ofd_result opened=ofd_open(&s->decoder,s->head,s->head_bytes,s->generation,api);
            if(opened.code!=OFD_OK){ofp_result r=ofp_block(s,ofp_decoder_code(opened),opened.detail);r.decoder=opened;return r;}
            if(callbacks->cancelled(callbacks->context))return ofp_block(s,OFP_CANCELLED,0);
            s->phase=OFP_AUDIO;return ofp_ack_headers(s,input);
        }
    } else {
        if(input->event.flags&OOPT_TAGS)return ofp_block(s,OFP_CONTAINER,OPI_INVALID);
        opk_status begun=opk_begin_page(&s->packets,input);
        if(begun<0)return ofp_block(s,OFP_PACKET,begun);
    }
    if(eos) {
        opus_pcm_trim_status trimmed=input->event.raw_end_known?
            opt_end(&s->trim,s->generation,input->event.raw_end,input->event.raw_completed):OPT_INVALID;
        if(trimmed!=OPT_OK)return ofp_block(s,OFP_TRIM,trimmed);
    }
    if(s->phase==OFP_AUDIO)for(;;) {
        if(callbacks->cancelled(callbacks->context))return ofp_block(s,OFP_CANCELLED,0);
        opus_audio_packet_view packet;opk_status next=opk_next(&s->packets,&packet);
        if(next==OPK_PAGE_DONE)break;
        if(next!=OPK_PACKET)return ofp_block(s,next==OPK_MEMORY?OFP_MEMORY:next==OPK_PACKET_POLICY?OFP_PACKET_POLICY:OFP_PACKET,next);
        ofp_sink_context context={s,callbacks,OFP_OK,0};
        ofd_pcm_sink sink={ofp_sink_begin,ofp_sink_write,ofp_sink_finish,ofp_sink_abort,ofp_sink_yield,&context};
        ofd_result decoded=ofd_decode_packet(&s->decoder,packet.data,packet.bytes,&sink);
        if(decoded.code!=OFD_OK) {
            ofp_result r=ofp_block(s,context.error!=OFP_OK?context.error:ofp_decoder_code(decoded),context.error!=OFP_OK?context.detail:decoded.detail);
            r.decoder=decoded;return r;
        }
        if(!opk_consume(&s->packets,packet.generation,packet.serial,packet.token))return ofp_block(s,OFP_PACKET,OPK_INVALID);
    }
    if(eos) {
        opus_pcm_trim_status trimmed=opt_finish(&s->trim,s->generation);
        if(trimmed!=OPT_OK)return ofp_block(s,OFP_TRIM,trimmed);
        s->phase=OFP_EOS_CLOSE;s->close_page_token=input->event.token;return ofp_close_eos(s,input);
    }
    if(!opi_ack(input,s->generation,input->event.token) || !opk_page_released(&s->packets,input))return ofp_block(s,OFP_CONTAINER,OPI_INVALID);
    return ofp_code(OFP_OK);
}
#endif
