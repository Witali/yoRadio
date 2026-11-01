#ifndef YORADIO_OPUS_MULTISTREAM_FRAMING_H
#define YORADIO_OPUS_MULTISTREAM_FRAMING_H

/* RFC6716 section3/AppendixB framing, not compressed-frame synthesis. Validate
 * all N elementary streams, retain pointer views only for selected stream IDs.
 * No allocation, decoder state, output ACK or mutation of encoded input. Views
 * borrow the complete caller-owned packet until its real consumer releases it.
 */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
typedef enum { OMF_OK=0,OMF_INVALID=-1,OMF_PACKET_POLICY=-2 } omf_status;
enum { OMF_FAMILY01_MAX_PACKET=61440,OMF_MAX_NEEDED=8 };
typedef struct {
    const uint8_t *data;
    size_t bytes,extra_offset,extra_bytes;
    uint16_t samples;
    uint8_t code,frames;
    bool self_delimited;
} opus_elementary_view;
static inline unsigned omf_samples_per_frame(uint8_t toc) {
    unsigned config=toc>>3;
    if(config<12){static const unsigned values[4]={480,960,1920,2880};return values[config&3u];}
    if(config<16)return config&1u?960u:480u;
    return 120u<<(config&3u);
}
static inline bool omf_size(const uint8_t *data,size_t bytes,size_t *at,unsigned *size) {
    if(*at>=bytes)return false;
    unsigned value=data[(*at)++];
    if(value>=252){if(*at>=bytes)return false;value+=4u*data[(*at)++];}
    if(value>1275)return false;
    *size=value;return true;
}
static inline omf_status omf_element(const uint8_t *data,size_t bytes,bool self_delimited,opus_elementary_view *out) {
    if(!data || !bytes || !out)return OMF_INVALID;
    unsigned code=data[0]&3u,count=code?2u:1u;bool vbr=code==2;size_t at=1,padding=0,known=0;
    if(code==3) {
        if(at>=bytes)return OMF_INVALID;
        unsigned control=data[at++];count=control&63u;vbr=(control&128u)!=0;
        if(!count || count>48 || count*omf_samples_per_frame(data[0])>5760)return OMF_INVALID;
        if(control&64u)for(;;) {
            if(at>=bytes)return OMF_INVALID;
            unsigned value=data[at++],add=value==255?254u:value;
            if(add>bytes-padding)return OMF_INVALID;
            padding+=add;if(value<255)break;
        }
    }
    if(vbr)for(unsigned i=1;i<count;++i) {
        unsigned value;if(!omf_size(data,bytes,&at,&value) || value>bytes-known)return OMF_INVALID;known+=value;
    }
    size_t extra=at,extra_bytes=0,total=0;
    if(self_delimited) {
        unsigned last;if(!omf_size(data,bytes,&at,&last))return OMF_INVALID;extra_bytes=at-extra;
        total=vbr?known+last:(size_t)last*count;
        if(total>bytes-at || padding>bytes-at-total)return OMF_INVALID;
        total+=at+padding;
    } else {
        if(padding>bytes-at)return OMF_INVALID;
        size_t payload=bytes-at-padding;
        if(vbr){if(known>payload || payload-known>1275)return OMF_INVALID;}
        else if(payload%count || payload/count>1275)return OMF_INVALID;
        total=bytes;
    }
    unsigned samples=count*omf_samples_per_frame(data[0]);if(samples>5760)return OMF_INVALID;
    opus_elementary_view next={.data=data,.bytes=total,.extra_offset=extra,.extra_bytes=extra_bytes,.samples=(uint16_t)samples,
        .code=(uint8_t)code,.frames=(uint8_t)count,.self_delimited=self_delimited};*out=next;return OMF_OK;
}

/* The explicit family0/1 policy is distinct from syntax and real allocation
 * refusal. N can be255; needed<=8 only bounds selected output views, not N.
 * All outputs remain unchanged if any used OR unused stream is malformed.
 */
static inline omf_status omf_family01_packet(const uint8_t *packet,size_t bytes,uint8_t streams,
    const uint8_t *selected,size_t needed,opus_elementary_view output[8],uint16_t *samples) {
    if(!packet || !bytes || !streams || needed>8 || (needed && (!selected || !output)) || !samples)return OMF_INVALID;
    if(bytes>OMF_FAMILY01_MAX_PACKET)return OMF_PACKET_POLICY;
    for(size_t i=0;i<needed;++i) {
        if(selected[i]>=streams)return OMF_INVALID;
        for(size_t j=0;j<i;++j)if(selected[i]==selected[j])return OMF_INVALID;
    }
    opus_elementary_view next[8]={{0}};size_t at=0;uint16_t duration=0;
    for(unsigned stream=0;stream<streams;++stream) {
        opus_elementary_view view;omf_status status=omf_element(packet+at,bytes-at,stream+1u<streams,&view);
        if(status!=OMF_OK || !view.bytes || view.bytes>bytes-at || (stream && view.samples!=duration))return OMF_INVALID;
        duration=view.samples;
        for(size_t slot=0;slot<needed;++slot)if(selected[slot]==stream)next[slot]=view;
        at+=view.bytes;
    }
    if(at!=bytes)return OMF_INVALID;
    if(needed)memcpy(output,next,needed*sizeof(*output));
    *samples=duration;return OMF_OK;
}
#endif
