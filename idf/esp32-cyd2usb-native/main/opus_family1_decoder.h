#ifndef YORADIO_OPUS_FAMILY1_DECODER_H
#define YORADIO_OPUS_FAMILY1_DECODER_H

/* Independent documented public Opus handles, not decoder-private state.
 * Initialize at a stable address with {0}; never move/copy a live owner. Header
 * preparation is transactional before any active cfg/handle is touched. The
 * caller must establish the verified OpusHead/packet leases and own the staged
 * channel planes. begin/write are not play-ready publication; finish follows
 * complete all-N validation and complete synthesis of every needed stream.
 * No trim, gain, speaker mix, Ogg ACK or output queue operation occurs here.
 */
#include <stdlib.h>
#include "esp_opus_dec.h"
#include "opus_family1_mapping.h"
#include "opus_multistream_framing.h"
#ifndef OFD_REALLOC
#define OFD_REALLOC realloc
#endif
#ifndef OFD_FREE
#define OFD_FREE free
#endif
typedef enum {
    OFD_OK=0,OFD_ARGUMENT,OFD_MOVED,OFD_BUSY,OFD_HEADER,OFD_FRAMING,OFD_PACKET_POLICY,
    OFD_MEMORY,OFD_PUBLIC_OPEN,OFD_PUBLIC_DECODE,OFD_PUBLIC_CLOSE,OFD_CONTRACT,OFD_PROGRESS,OFD_SINK
} ofd_status;
typedef struct {
    ofd_status code;
    int detail;
    bool public_error_known,cleanup_error_known,cleanup_pending;
    esp_audio_err_t public_error,cleanup_error;
} ofd_result;
typedef struct {
    esp_audio_err_t (*open)(void *,uint32_t,void **);
    esp_audio_err_t (*decode)(void *,esp_audio_dec_in_raw_t *,esp_audio_dec_out_frame_t *,esp_audio_dec_info_t *);
    esp_audio_err_t (*close)(void *);
} ofd_public_api;
typedef struct {
    bool (*begin)(void *,const opus_family1_plan *,uint32_t,uint16_t);
    bool (*write)(void *,uint8_t,uint8_t,uint8_t,size_t,const uint8_t *,size_t);
    bool (*finish)(void *);
    void (*abort)(void *);
    void (*yield)(void *);
    void *context;
} ofd_pcm_sink;
typedef struct opus_family1_decoder {
    const struct opus_family1_decoder *anchor;
    opus_family1_plan plan;
    ofd_public_api api;
    esp_opus_dec_cfg_t cfg[8];
    void *handle[8];
    uint8_t *scratch;
    size_t capacity;
    uint32_t generation;
    bool active;
} opus_family1_decoder;

static inline ofd_result ofd_code(ofd_status code) {ofd_result r={.code=code};return r;}
static inline bool ofd_has_handles(const opus_family1_decoder *s) {
    for(unsigned i=0;i<8;++i)if(s->handle[i])return true;
    return false;
}
static inline ofd_result ofd_close(opus_family1_decoder *s) {
    if(!s)return ofd_code(OFD_ARGUMENT);
    if(s->anchor && s->anchor!=s)return ofd_code(OFD_MOVED);
    ofd_result result=ofd_code(OFD_OK);
    for(unsigned slot=0;slot<8;++slot)if(s->handle[slot]) {
        if(!s->api.close){result.code=OFD_CONTRACT;continue;}
        esp_audio_err_t r=s->api.close(s->handle[slot]);
        if(r==ESP_AUDIO_ERR_OK)s->handle[slot]=NULL;
        else if(!result.public_error_known){result.code=OFD_PUBLIC_CLOSE;result.public_error_known=true;result.public_error=r;}
    }
    OFD_FREE(s->scratch);s->scratch=NULL;s->capacity=0;s->active=false;result.cleanup_pending=ofd_has_handles(s);return result;
}
static inline ofd_result ofd_fail(opus_family1_decoder *s,ofd_result result) {
    ofd_result cleanup=ofd_close(s);result.cleanup_pending=cleanup.cleanup_pending;
    if(cleanup.public_error_known){result.cleanup_error_known=true;result.cleanup_error=cleanup.public_error;}
    return result;
}
static inline ofd_result ofd_open(opus_family1_decoder *s,const uint8_t *head,size_t bytes,uint32_t generation,const ofd_public_api *api) {
    if(!s)return ofd_code(OFD_ARGUMENT);
    if(s->anchor && s->anchor!=s)return ofd_code(OFD_MOVED);
    if(s->active || ofd_has_handles(s))return ofd_code(OFD_BUSY);
    opus_family1_plan prepared;of1_status parsed=of1_plan_header(head,bytes,&prepared);
    if(parsed!=OF1_OK){ofd_result r=ofd_code(OFD_HEADER);r.detail=parsed;return r;}
    ofd_public_api selected=api?*api:(ofd_public_api){esp_opus_dec_open,esp_opus_dec_decode,esp_opus_dec_close};
    if(!selected.open || !selected.decode || !selected.close)return ofd_code(OFD_ARGUMENT);
    /* Commit only non-live preparation. cfg objects never move after open. */
    s->anchor=s;s->plan=prepared;s->api=selected;s->generation=generation;
    for(unsigned slot=0;slot<prepared.needed;++slot) {
        s->cfg[slot]=(esp_opus_dec_cfg_t){.sample_rate=48000,.channel=prepared.stream_channels[slot],
            .frame_duration=ESP_OPUS_DEC_FRAME_DURATION_INVALID,.self_delimited=(unsigned)prepared.stream_id[slot]+1u<prepared.streams};
        esp_audio_err_t actual=s->api.open(&s->cfg[slot],sizeof(s->cfg[slot]),&s->handle[slot]);
        if(actual!=ESP_AUDIO_ERR_OK){ofd_result r=ofd_code(OFD_PUBLIC_OPEN);r.public_error_known=true;r.public_error=actual;return ofd_fail(s,r);}
        if(!s->handle[slot])return ofd_fail(s,ofd_code(OFD_CONTRACT));
    }
    s->active=true;return ofd_code(OFD_OK);
}
static inline ofd_result ofd_decode_packet(opus_family1_decoder *s,const uint8_t *packet,size_t bytes,const ofd_pcm_sink *sink) {
    if(!s || !sink || !sink->begin || !sink->write || !sink->finish || !sink->abort)return ofd_code(OFD_ARGUMENT);
    if(s->anchor && s->anchor!=s)return ofd_code(OFD_MOVED);
    if(!s->active)return ofd_code(OFD_BUSY);
    opus_elementary_view views[8];uint16_t samples=0;
    omf_status framing=omf_family01_packet(packet,bytes,s->plan.streams,s->plan.stream_id,s->plan.needed,views,&samples);
    if(framing!=OMF_OK){ofd_result r=ofd_code(framing==OMF_PACKET_POLICY?OFD_PACKET_POLICY:OFD_FRAMING);r.detail=framing;return ofd_fail(s,r);}
    if(s->plan.needed && !s->capacity) {
        /* INVALID duration's documented estimate is60ms. The public resize
         * protocol handles longer legal packets, never a private cache view.
         */
        uint8_t *buffer=OFD_REALLOC(NULL,11520);
        if(!buffer){ofd_result r=ofd_code(OFD_MEMORY);r.detail=11520;return ofd_fail(s,r);}
        s->scratch=buffer;s->capacity=11520;
    }
    ofd_result result=ofd_code(OFD_OK);bool began=true;
    if(!sink->begin(sink->context,&s->plan,s->generation,samples)){result=ofd_code(OFD_SINK);goto fail;}
    for(unsigned slot=0;slot<s->plan.needed;++slot) {
        unsigned width=s->plan.stream_channels[slot];size_t produced=0;
        esp_audio_dec_in_raw_t raw={.buffer=(uint8_t *)views[slot].data,.len=(uint32_t)views[slot].bytes,.frame_recover=ESP_AUDIO_DEC_RECOVERY_NONE};
        for(;;) {
            uint32_t before=raw.len;raw.consumed=0;esp_audio_dec_out_frame_t frame={.buffer=s->scratch,.len=(uint32_t)s->capacity};esp_audio_dec_info_t info={0};
            esp_audio_err_t actual=s->api.decode(s->handle[slot],&raw,&frame,&info);if(sink->yield)sink->yield(sink->context);
            if(raw.len!=before || raw.consumed>before || frame.decoded_size>s->capacity){result=ofd_code(OFD_CONTRACT);goto fail;}
            raw.buffer+=raw.consumed;raw.len-=raw.consumed;
            if(actual==ESP_AUDIO_ERR_BUFF_NOT_ENOUGH) {
                if(frame.decoded_size || frame.needed_size<=s->capacity || frame.needed_size>23040){result=ofd_code(OFD_CONTRACT);goto fail;}
                uint8_t *larger=OFD_REALLOC(s->scratch,frame.needed_size);
                if(!larger){result=ofd_code(OFD_MEMORY);result.detail=(int)frame.needed_size;goto fail;}
                s->scratch=larger;s->capacity=frame.needed_size;continue;
            }
            if(actual!=ESP_AUDIO_ERR_OK){result=ofd_code(OFD_PUBLIC_DECODE);result.public_error_known=true;result.public_error=actual;goto fail;}
            size_t frames=0;
            if(frame.decoded_size) {
                if(info.sample_rate!=48000 || info.channel!=width || info.bits_per_sample!=16 || frame.decoded_size%(width*2u)){
                    result=ofd_code(OFD_CONTRACT);goto fail;
                }
                frames=frame.decoded_size/(width*2u);
                if(frames>samples-produced){result=ofd_code(OFD_CONTRACT);goto fail;}
                if(!sink->write(sink->context,(uint8_t)slot,s->plan.stream_id[slot],(uint8_t)width,produced,s->scratch,frames)){
                    result=ofd_code(OFD_SINK);goto fail;
                }
                produced+=frames;
            }
            if(!raw.len && produced==samples)break;
            if(produced==samples || (!raw.consumed && !frames)){result=ofd_code(OFD_PROGRESS);goto fail;}
        }
    }
    if(!sink->finish(sink->context)){result=ofd_code(OFD_SINK);goto fail;}
    return result;
fail:
    if(began)sink->abort(sink->context);
    return ofd_fail(s,result);
}
#endif
