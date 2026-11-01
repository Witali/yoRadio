#ifndef YORADIO_OPUS_FAMILY1_MAPPING_H
#define YORADIO_OPUS_FAMILY1_MAPPING_H

/* Family1 syntax/planning and borrowed public PCM views only. No decoder state,
 * allocation, gain, trim or downmix. A caller must establish page CRC/ownership
 * before accepting a header and keep all referenced PCM owners unchanged while
 * views are used. C denotes Vorbis speaker order, not decoded channel count.
 */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

typedef enum { OF1_OK=0,OF1_INVALID=-1,OF1_VERSION=-2,OF1_OTHER_FAMILY=-3 } of1_status;
enum { OF1_MAX_CHANNELS=8,OF1_SILENCE=255 };
typedef struct {
    uint32_t input_rate;
    uint16_t pre_skip;
    int16_t header_gain_q8;
    uint8_t channels,streams,coupled,needed;
    uint8_t map[8],stream_id[8],stream_channels[8];
    uint8_t speaker_slot[8],speaker_channel[8];
} opus_family1_plan;
typedef struct { const uint8_t *data;size_t bytes; } of1_pcm_buffer;
typedef struct { const uint8_t *data;size_t frames,stride;bool silence; } of1_channel_view;

static inline uint32_t of1_le32(const uint8_t *p) {
    return (uint32_t)p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;
}
static inline of1_status of1_plan_header(const uint8_t *head,size_t bytes,opus_family1_plan *out) {
    if(!head || !out || bytes<19 || memcmp(head,"OpusHead",8) || !head[9])return OF1_INVALID;
    if(head[8]&0xf0u)return OF1_VERSION;
    if(head[18]!=1)return OF1_OTHER_FAMILY;
    unsigned c=head[9];if(c>8 || bytes<21u+c || !head[19] || head[20]>head[19])return OF1_INVALID;
    unsigned decoded=(unsigned)head[19]+head[20];if(decoded>255)return OF1_INVALID;
    opus_family1_plan next={0};next.channels=(uint8_t)c;next.streams=head[19];next.coupled=head[20];
    next.input_rate=of1_le32(head+12);next.pre_skip=(uint16_t)((unsigned)head[10]|(unsigned)head[11]<<8);
    unsigned gain=(unsigned)head[16]|(unsigned)head[17]<<8;
    next.header_gain_q8=(int16_t)(gain<32768u?(int32_t)gain:(int32_t)gain-65536);
    for(unsigned speaker=0;speaker<c;++speaker) {
        unsigned index=head[21+speaker];next.map[speaker]=(uint8_t)index;
        if(index==255){next.speaker_slot[speaker]=OF1_SILENCE;continue;}
        if(index>=decoded)return OF1_INVALID;
        unsigned stream=index<2u*next.coupled?index/2u:index-next.coupled;
        unsigned channel=index<2u*next.coupled?index%2u:0u,slot=0;
        while(slot<next.needed && next.stream_id[slot]!=stream)++slot;
        if(slot==next.needed) {
            if(next.needed==8)return OF1_INVALID; /* C<=8 makes this unreachable for valid syntax. */
            next.stream_id[slot]=(uint8_t)stream;next.stream_channels[slot]=stream<next.coupled?2u:1u;++next.needed;
        }
        next.speaker_slot[speaker]=(uint8_t)slot;next.speaker_channel[speaker]=(uint8_t)channel;
    }
    *out=next;return OF1_OK;
}

/* Each needed buffer is public PCM16 LE in the plan's stream_id order. Empty
 * trimmed blocks may have zero frames/bytes. Silent/duplicate speakers borrow
 * no additional PCM. Outputs remain unchanged on invalid input.
 */
static inline of1_status of1_channel_views(const opus_family1_plan *plan,
    const of1_pcm_buffer *buffers,size_t count,size_t frames,of1_channel_view out[8]) {
    if(!plan || !out || !plan->channels || plan->channels>8 || plan->needed>8 || count!=plan->needed || (count && !buffers))return OF1_INVALID;
    for(unsigned slot=0;slot<plan->needed;++slot) {
        unsigned width=plan->stream_channels[slot];
        if((width!=1 && width!=2) || frames>SIZE_MAX/(width*2u) || buffers[slot].bytes!=frames*width*2u ||
            (buffers[slot].bytes && !buffers[slot].data))return OF1_INVALID;
    }
    of1_channel_view next[8]={{0}};
    for(unsigned speaker=0;speaker<plan->channels;++speaker) {
        unsigned slot=plan->speaker_slot[speaker];next[speaker].frames=frames;
        if(slot==OF1_SILENCE){next[speaker].silence=true;continue;}
        if(slot>=plan->needed || plan->speaker_channel[speaker]>=plan->stream_channels[slot])return OF1_INVALID;
        next[speaker].stride=(size_t)plan->stream_channels[slot]*2u;
        next[speaker].data=frames?buffers[slot].data+plan->speaker_channel[speaker]*2u:NULL;
    }
    memcpy(out,next,sizeof(next));return OF1_OK;
}

/* Bounded gather into caller-owned queue storage. This is only a permutation /
 * duplicate / exact-silence operation; no early clipping or stereo reduction.
 * Destination must not overlap referenced source PCM.
 */
static inline of1_status of1_gather_s16(const of1_channel_view views[8],uint8_t channels,
    size_t first,size_t frames,uint8_t *output,size_t capacity,size_t *written) {
    if(!views || !written || !channels || channels>8 || frames>SIZE_MAX/(channels*2u))return OF1_INVALID;
    size_t needed=frames*channels*2u;if(needed>capacity || (needed && !output))return OF1_INVALID;
    for(unsigned c=0;c<channels;++c) {
        const of1_channel_view *v=views+c;
        if(first>v->frames || frames>v->frames-first || (!v->silence && frames && (!v->data || (v->stride!=2 && v->stride!=4))))return OF1_INVALID;
        if(!v->silence && v->stride && v->frames>SIZE_MAX/v->stride)return OF1_INVALID;
    }
    for(size_t frame=0;frame<frames;++frame)for(unsigned c=0;c<channels;++c) {
        const of1_channel_view *v=views+c;uint8_t *to=output+(frame*channels+c)*2u;
        if(v->silence)to[0]=to[1]=0;
        else {const uint8_t *from=v->data+(first+frame)*v->stride;to[0]=from[0];to[1]=from[1];}
    }
    *written=needed;return OF1_OK;
}
#endif
