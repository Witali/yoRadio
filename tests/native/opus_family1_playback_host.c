/* HOST contract seam only. Positive synthesis and previous live objects use
 * actual public creator APIs. Scripted status/allocator refusals are NOT native
 * ESP allocation observations. Pages reach the adapter only via real CRC checks.
 */
#include <stddef.h>
#include <stdlib.h>
static void *plane_realloc(void *,size_t);
static void plane_free(void *);
static void *scratch_realloc(void *,size_t);
static void scratch_free(void *);
static void *packet_realloc(void *,size_t);
static void packet_free(void *);
#define OFP_REALLOC plane_realloc
#define OFP_FREE plane_free
#define OFD_REALLOC scratch_realloc
#define OFD_FREE scratch_free
#define OPK_REALLOC packet_realloc
#define OPK_FREE packet_free
#include "opus_family1_playback.h"
#include "opus_family1_public.h"
#include <ogg/ogg.h>
#include <assert.h>
#include <inttypes.h>
#include <math.h>
#include <stdio.h>
typedef struct OpusDecoder OpusDecoder;
extern OpusDecoder *opus_decoder_create(int32_t,int,int *);
extern int opus_decode_float(OpusDecoder *,const unsigned char *,int32_t,float *,int,int);
extern void opus_decoder_destroy(OpusDecoder *);
extern int opus_packet_get_nb_samples(const unsigned char *,int32_t,int32_t);

typedef struct {void *pointer;size_t bytes,peak;unsigned calls,refuse;} allocation;
static allocation plane_alloc,scratch_alloc,packet_alloc;
static void *resize(allocation *a,void *pointer,size_t bytes,size_t limit) {
    assert(pointer==a->pointer && bytes && bytes<=limit);++a->calls;if(a->calls==a->refuse)return NULL;
    void *next=realloc(pointer,bytes);assert(next);a->pointer=next;a->bytes=bytes;if(bytes>a->peak)a->peak=bytes;return next;
}
static void release(allocation *a,void *pointer) {
    if(!pointer)return;
    assert(pointer==a->pointer);free(pointer);a->pointer=NULL;a->bytes=0;
}
static void *plane_realloc(void *p,size_t n){return resize(&plane_alloc,p,n,92160);}
static void plane_free(void *p){release(&plane_alloc,p);}
static void *scratch_realloc(void *p,size_t n){return resize(&scratch_alloc,p,n,23040);}
static void scratch_free(void *p){release(&scratch_alloc,p);}
static void *packet_realloc(void *p,size_t n){return resize(&packet_alloc,p,n,61440);}
static void packet_free(void *p){release(&packet_alloc,p);}
typedef struct {OpusDecoder *decoder;const esp_opus_dec_cfg_t *cfg;esp_opus_dec_cfg_t expected;uint8_t *pending;unsigned pending_bytes;} host_handle;
typedef struct {
    unsigned opens,created,decodes,syntheses,closes,destroyed,live;
    unsigned open_refuse,decode_refuse,close_refuse,cancel_open;
    bool cache_full,*cancelled;
} backend;
static backend stats;
static opus_family1_playback *owner;
static unsigned positives,controls,libogg_walks,acknowledged,close_retries;
static uint64_t compared_samples;
static size_t maximum_planes,maximum_chunk;
static int16_t rounded(double v){double x=v*32768.0;return x>32767?32767:x<-32768?-32768:(int16_t)llround(x);}
static void put16(uint8_t *p,int16_t v){unsigned n=(unsigned)(uint16_t)v;p[0]=(uint8_t)n;p[1]=(uint8_t)(n>>8);}
static void put32(uint8_t *p,uint32_t v){for(unsigned i=0;i<4;++i)p[i]=(uint8_t)(v>>(8u*i));}
static void put64(uint8_t *p,uint64_t v){for(unsigned i=0;i<8;++i)p[i]=(uint8_t)(v>>(8u*i));}
static void cfg_stable(const host_handle *h) {
    assert(h->cfg->sample_rate==h->expected.sample_rate && h->cfg->channel==h->expected.channel &&
        h->cfg->frame_duration==h->expected.frame_duration && h->cfg->self_delimited==h->expected.self_delimited);
    bool found=false;for(unsigned i=0;i<8;++i)if(h->cfg==&owner->decoder.cfg[i])found=true;assert(found);
}
esp_audio_err_t esp_opus_dec_open(void *opaque,uint32_t bytes,void **out) {
    const esp_opus_dec_cfg_t *cfg=opaque;assert(cfg && out && !*out && bytes==sizeof(*cfg) && cfg->sample_rate==48000 &&
        (cfg->channel==1 || cfg->channel==2) && cfg->frame_duration==ESP_OPUS_DEC_FRAME_DURATION_INVALID);++stats.opens;
    if(stats.opens==stats.open_refuse)return ESP_AUDIO_ERR_MEM_LACK; /* HOST double, no creator call. */
    host_handle *h=calloc(1,sizeof(*h));assert(h);int error=0;h->decoder=opus_decoder_create(48000,cfg->channel,&error);assert(h->decoder && !error);
    h->cfg=cfg;h->expected=*cfg;cfg_stable(h);*out=h;++stats.created;++stats.live;
    if(stats.opens==stats.cancel_open){assert(stats.cancelled);*stats.cancelled=true;}
    return ESP_AUDIO_ERR_OK;
}
static void synthesize(host_handle *h,const uint8_t *packet,size_t bytes,uint8_t *pcm,unsigned frames) {
    float *data=malloc((size_t)frames*h->cfg->channel*sizeof(float));assert(data);
    assert(opus_decode_float(h->decoder,packet,(int32_t)bytes,data,(int)frames,0)==(int)frames);++stats.syntheses;
    for(unsigned i=0;i<frames*h->cfg->channel;++i)put16(pcm+i*2u,rounded(data[i]));
    free(data);
}
esp_audio_err_t esp_opus_dec_decode(void *opaque,esp_audio_dec_in_raw_t *raw,esp_audio_dec_out_frame_t *out,esp_audio_dec_info_t *info) {
    host_handle *h=opaque;assert(h && raw && out && info && raw->frame_recover==ESP_AUDIO_DEC_RECOVERY_NONE);cfg_stable(h);++stats.decodes;
    if(stats.decodes==stats.decode_refuse)return ESP_AUDIO_ERR_FAIL; /* Explicit HOST status, no synthesis. */
    if(h->pending) {
        assert(!raw->len);out->needed_size=h->pending_bytes;if(out->len<h->pending_bytes)return ESP_AUDIO_ERR_BUFF_NOT_ENOUGH;
        memcpy(out->buffer,h->pending,h->pending_bytes);out->decoded_size=h->pending_bytes;free(h->pending);h->pending=NULL;h->pending_bytes=0;
    } else {
        opus_elementary_view view;assert(omf_element(raw->buffer,raw->len,h->cfg->self_delimited,&view)==OMF_OK && view.bytes==raw->len);
        size_t bytes=view.bytes-view.extra_bytes;uint8_t *common=malloc(bytes);assert(common);
        memcpy(common,view.data,view.extra_offset);memcpy(common+view.extra_offset,view.data+view.extra_offset+view.extra_bytes,view.bytes-view.extra_offset-view.extra_bytes);
        int frames=opus_packet_get_nb_samples(common,(int32_t)bytes,48000);assert(frames>0 && frames<=5760);unsigned needed=(unsigned)frames*h->cfg->channel*2u;
        if(out->len<needed) {
            out->needed_size=needed;
            if(stats.cache_full){h->pending=malloc(needed);assert(h->pending);h->pending_bytes=needed;synthesize(h,common,bytes,h->pending,(unsigned)frames);raw->consumed=raw->len;}
            free(common);return ESP_AUDIO_ERR_BUFF_NOT_ENOUGH;
        }
        synthesize(h,common,bytes,out->buffer,(unsigned)frames);free(common);raw->consumed=raw->len;out->decoded_size=needed;
    }
    info->sample_rate=48000;info->channel=h->cfg->channel;info->bits_per_sample=16;return ESP_AUDIO_ERR_OK;
}
esp_audio_err_t esp_opus_dec_close(void *opaque) {
    host_handle *h=opaque;assert(h);cfg_stable(h);++stats.closes;
    if(stats.closes==stats.close_refuse)return ESP_AUDIO_ERR_INVALID_PARAMETER; /* HOST object remains really live. */
    opus_decoder_destroy(h->decoder);free(h->pending);free(h);assert(stats.live);--stats.live;++stats.destroyed;return ESP_AUDIO_ERR_OK;
}
static void reset_backend(opus_family1_playback *s) {
    assert(!stats.live && !plane_alloc.pointer && !scratch_alloc.pointer && !packet_alloc.pointer);
    memset(&stats,0,sizeof(stats));memset(&plane_alloc,0,sizeof(plane_alloc));memset(&scratch_alloc,0,sizeof(scratch_alloc));memset(&packet_alloc,0,sizeof(packet_alloc));owner=s;
}

typedef struct {uint8_t head[40];uint8_t **packet;size_t *bytes;unsigned count,channels,streams,coupled,pre_skip,logical;bool plc;} corpus;
static corpus load(const char *path) {
    FILE *f=fopen(path,"rb");assert(f);uint8_t header[40];assert(fread(header,1,40,f)==40 && !memcmp(header,"OFAM101\0",8));
    corpus s={.channels=of1_le32(header+8),.streams=of1_le32(header+12),.coupled=of1_le32(header+16),.pre_skip=of1_le32(header+20),.logical=of1_le32(header+24),.count=of1_le32(header+28)};
    memcpy(s.head,"OpusHead",8);s.head[8]=1;s.head[9]=(uint8_t)s.channels;put16(s.head+10,(int16_t)s.pre_skip);put32(s.head+12,44100);put16(s.head+16,1536);
    s.head[18]=1;s.head[19]=(uint8_t)s.streams;s.head[20]=(uint8_t)s.coupled;memcpy(s.head+21,header+32,s.channels);
    assert(s.count && s.count<=100 && s.channels<=8);s.packet=calloc(s.count,sizeof(*s.packet));s.bytes=calloc(s.count,sizeof(*s.bytes));assert(s.packet && s.bytes);
    for(unsigned i=0;i<s.count;++i){uint8_t length[4];assert(fread(length,1,4,f)==4);s.bytes[i]=of1_le32(length);s.packet[i]=malloc(s.bytes[i]);assert(s.packet[i] && fread(s.packet[i],1,s.bytes[i],f)==s.bytes[i]);}
    assert(fgetc(f)==EOF && !fclose(f));return s;
}
static corpus variant(const corpus *source,unsigned channels,const uint8_t *map) {
    corpus s=*source;s.channels=channels;s.head[9]=(uint8_t)channels;memcpy(s.head+21,map,channels);return s;
}
static void corpus_free(corpus *s){for(unsigned i=0;i<s->count;++i)free(s->packet[i]);free(s->packet);free(s->bytes);}
static corpus plc_growth(void) {
    corpus s={.channels=8,.streams=5,.coupled=3,.logical=7680,.count=3,.plc=true};memcpy(s.head,"OpusHead",8);s.head[8]=1;s.head[9]=8;put32(s.head+12,44100);put16(s.head+16,1536);s.head[18]=1;s.head[19]=5;s.head[20]=3;
    const uint8_t map[8]={0,6,1,2,3,4,5,7};memcpy(s.head+21,map,8);s.packet=calloc(3,sizeof(*s.packet));s.bytes=calloc(3,sizeof(*s.bytes));assert(s.packet && s.bytes);
    for(unsigned p=0;p<3;++p) {
        bool long_packet=p==1;s.bytes[p]=long_packet?14:9;s.packet[p]=malloc(s.bytes[p]);assert(s.packet[p]);size_t at=0;
        for(unsigned stream=0;stream<5;++stream) {
            s.packet[p][at++]=(uint8_t)(0xf8u|(stream<3?4u:0u)|(long_packet?3u:0u));
            if(long_packet)s.packet[p][at++]=6;
            if(stream<4)s.packet[p][at++]=0; /* Appendix B, zero-byte coded frames. */
        }
        assert(at==s.bytes[p]);
    }
    return s;
}
typedef struct {uint8_t *pcm;size_t raw_frames,logical_frames;unsigned channels,pre_skip;} reference;
static reference creator_reference(const corpus *source) {
    reference r={.channels=source->channels,.pre_skip=source->pre_skip,.logical_frames=source->logical};
    for(unsigned i=0;i<source->count;++i){int n=opus_packet_get_nb_samples(source->packet[i],(int32_t)source->bytes[i],48000);assert(n>0 && n<=5760);r.raw_frames+=(unsigned)n;}
    assert(r.logical_frames+r.pre_skip<=r.raw_frames);r.pcm=malloc(r.raw_frames*r.channels*2u);float *samples=malloc(5760u*r.channels*sizeof(float));assert(r.pcm && samples);
    int error=0;OpusMSDecoder *decoder=opus_multistream_decoder_create(48000,(int)source->channels,(int)source->streams,(int)source->coupled,source->head+21,&error);assert(decoder && !error);size_t at=0;
    for(unsigned p=0;p<source->count;++p) {
        int n=opus_multistream_decode_float(decoder,source->packet[p],(int32_t)source->bytes[p],samples,5760,0);assert(n>0 && n<=5760);
        for(unsigned i=0;i<(unsigned)n*r.channels;++i)put16(r.pcm+(at*r.channels+i)*2u,rounded(samples[i]));
        at+=(unsigned)n;
    }
    assert(at==r.raw_frames);opus_multistream_decoder_destroy(decoder);free(samples);return r;
}
typedef struct {
    const reference *reference;size_t emitted;unsigned calls,published,yields,refuse_output,cancel_output,cancel_yield;bool cancelled;
} output_context;
static bool cancelled(void *opaque){return ((output_context *)opaque)->cancelled;}
static bool output(void *opaque,uint32_t generation,const opus_family1_plan *plan,const uint8_t *pcm,size_t bytes) {
    output_context *c=opaque;const reference *r=c->reference;++c->calls;
    assert(generation==42 && plan->channels==r->channels && plan->pre_skip==r->pre_skip && plan->input_rate==44100 && plan->header_gain_q8==1536 &&
        bytes && bytes<=128u*r->channels*2u && bytes%(r->channels*2u)==0);
    if(plan->needed)assert(pcm==owner->decoder.scratch && owner->decoder.capacity>=bytes && owner->decoder.active && stats.live);
    else assert(pcm==ofp_zero_chunk && !owner->decoder.scratch && !stats.live);
    size_t frames=bytes/(r->channels*2u);assert(c->emitted<=r->logical_frames && frames<=r->logical_frames-c->emitted);
    assert(!memcmp(pcm,r->pcm+(r->pre_skip+c->emitted)*r->channels*2u,bytes));
    if(c->calls==c->cancel_output){c->cancelled=true;return false;}
    if(c->calls==c->refuse_output)return false;
    c->emitted+=frames;++c->published;compared_samples+=bytes/2u;if(bytes>maximum_chunk)maximum_chunk=bytes;return true;
}
static void yield(void *opaque){output_context *c=opaque;if(++c->yields==c->cancel_yield)c->cancelled=true;}
static ofp_callbacks callbacks(output_context *c){return (ofp_callbacks){cancelled,output,yield,c};}

typedef struct {uint8_t *data,*head,*tags;size_t size,capacity,head_bytes,tags_bytes;unsigned pages,serial;} physical;
static unsigned laces(uint8_t *table,size_t bytes) {unsigned n=0;while(bytes>=255){table[n++]=255;bytes-=255;}table[n++]=(uint8_t)bytes;assert(n<=255);return n;}
static void page(physical *p,unsigned flags,uint64_t gp,const uint8_t *table,unsigned count,const uint8_t *body,size_t bytes) {
    size_t header=27u+count,total=header+bytes;assert(count<=255 && bytes<=65025);size_t sum=0;for(unsigned i=0;i<count;++i)sum+=table[i];assert(sum==bytes);
    if(p->size+total>p->capacity){p->capacity=(p->size+total)*2u;p->data=realloc(p->data,p->capacity);assert(p->data);}
    uint8_t *to=p->data+p->size;memset(to,0,header);memcpy(to,"OggS",4);to[5]=(uint8_t)flags;put64(to+6,gp);put32(to+14,p->serial);put32(to+18,p->pages++);to[26]=(uint8_t)count;
    if(count)memcpy(to+27,table,count);
    if(bytes)memcpy(to+header,body,bytes);
    ogg_page independent={.header=to,.header_len=(long)header,.body=to+header,.body_len=(long)bytes};ogg_page_checksum_set(&independent);p->size+=total;
}
static physical make(const corpus *source,unsigned style,unsigned serial,bool long_tags,bool extended) {
    physical p={.serial=serial,.head_bytes=extended?300u:21u+source->channels,.tags_bytes=long_tags?70000:16};
    p.head=calloc(p.head_bytes,1);p.tags=calloc(p.tags_bytes,1);assert(p.head && p.tags);memcpy(p.head,source->head,21u+source->channels);
    if(extended)memset(p.head+21u+source->channels,0x5a,p.head_bytes-21u-source->channels);
    memcpy(p.tags,"OpusTags",8);
    if(long_tags){put32(p.tags+8,(uint32_t)p.tags_bytes-16u);memset(p.tags+12,'x',p.tags_bytes-16u);}
    uint8_t table[255];unsigned n=laces(table,p.head_bytes);page(&p,2,0,table,n,p.head,p.head_bytes);
    if(long_tags) {memset(table,255,255);page(&p,0,UINT64_MAX,table,255,p.tags,65025);page(&p,1,UINT64_MAX,NULL,0,NULL,0);n=laces(table,p.tags_bytes-65025);page(&p,1u|(!source->count?4u:0u),0,table,n,p.tags+65025,p.tags_bytes-65025);}
    else {n=laces(table,p.tags_bytes);page(&p,!source->count?4u:0u,0,table,n,p.tags,p.tags_bytes);}
    uint64_t raw=0;
    for(unsigned i=0;i<source->count;) {
        if(style==2) {
            unsigned batch=source->count-i;if(batch>3)batch=3;uint8_t payload[65025];size_t used=0;unsigned count=0;
            for(unsigned j=0;j<batch;++j){count+=laces(table+count,source->bytes[i+j]);assert(used+source->bytes[i+j]<=sizeof(payload));memcpy(payload+used,source->packet[i+j],source->bytes[i+j]);used+=source->bytes[i+j];int frames=opus_packet_get_nb_samples(source->packet[i+j],(int32_t)source->bytes[i+j],48000);assert(frames>0);raw+=(unsigned)frames;}
            i+=batch;bool final=i==source->count;page(&p,final?4u:0u,final?source->pre_skip+source->logical:raw,table,count,payload,used);
        } else {
            const uint8_t *body=source->packet[i];size_t bytes=source->bytes[i];int frames=opus_packet_get_nb_samples(body,(int32_t)bytes,48000);assert(frames>0);raw+=(unsigned)frames;
            bool final=++i==source->count;uint64_t gp=final?source->pre_skip+source->logical:raw;
            if(style==1 && bytes>255) {
                uint8_t lace=255;page(&p,0,UINT64_MAX,&lace,1,body,255);page(&p,i%2u,UINT64_MAX,NULL,0,NULL,0);
                n=laces(table,bytes-255);page(&p,1u|(final?4u:0u),gp,table,n,body+255,bytes-255);
            } else {n=laces(table,bytes);page(&p,final?4u:0u,gp,table,n,body,bytes);}
        }
    }
    return p;
}
static void physical_free(physical *p){free(p->data);free(p->head);free(p->tags);}
static void replace_tags(physical *p) {
    size_t at=0,copied=0;unsigned page_number=0;
    while(at<p->size && copied<p->tags_bytes) {
        uint8_t *start=p->data+at;unsigned count=start[26];size_t header=27u+count,bytes=0;for(unsigned i=0;i<count;++i)bytes+=start[27+i];
        if(page_number) {
            assert(bytes<=p->tags_bytes-copied);if(bytes)memcpy(start+header,p->tags+copied,bytes);copied+=bytes;
            ogg_page checked={.header=start,.header_len=(long)header,.body=start+header,.body_len=(long)bytes};ogg_page_checksum_set(&checked);
        }
        ++page_number;at+=header+bytes;
    }
    assert(copied==p->tags_bytes);
}
static void creator_walk(const physical *bytes,const corpus *source) {
    ogg_sync_state sync;ogg_stream_state stream;assert(!ogg_sync_init(&sync) && !ogg_stream_init(&stream,(int)bytes->serial));size_t at=0;unsigned pages=0,packets=0;
    while(at<bytes->size) {
        size_t n=bytes->size-at;if(n>257)n=257;char *buffer=ogg_sync_buffer(&sync,(long)n);assert(buffer);memcpy(buffer,bytes->data+at,n);assert(!ogg_sync_wrote(&sync,(long)n));at+=n;
        for(;;) {
            ogg_page current;int status=ogg_sync_pageout(&sync,&current);assert(status>=0);if(!status)break;++pages;assert(!ogg_stream_pagein(&stream,&current));
            for(;;) {ogg_packet packet;status=ogg_stream_packetout(&stream,&packet);assert(status>=0);if(!status)break;
                assert(packets<source->count+2u);
                const uint8_t *expected=packets==0?bytes->head:packets==1?bytes->tags:source->packet[packets-2];
                size_t count=packets==0?bytes->head_bytes:packets==1?bytes->tags_bytes:source->bytes[packets-2];assert(packet.bytes==(long)count && !memcmp(packet.packet,expected,count));++packets;}
        }
    }
    assert(pages==bytes->pages && packets==source->count+2u && ogg_stream_eos(&stream));assert(!ogg_stream_clear(&stream) && !ogg_sync_clear(&sync));++libogg_walks;
}
typedef struct {size_t at,chunk;} reader;
static bool ready(ogg_page_input *input,const physical *p,reader *r) {
    assert(!input->ready);
    for(;;) {
        size_t count=p->size-r->at;if(r->chunk && count>r->chunk)count=r->chunk;size_t used=0;
        ogg_page_input_status status=opi_feed(input,count?p->data+r->at:NULL,count,&used);assert(used<=count);r->at+=used;
        if(status==OPI_PAGE){assert(input->ready && input->event.crc_verified);return true;}
        assert(status==OPI_MORE);if(r->at==p->size)return false;assert(used);
    }
}
static void successful_page(opus_family1_playback *s,ogg_page_input *input,const ofp_callbacks *cb) {
    assert(input->ready);uint64_t token=input->event.token;ofp_result result=ofp_page(s,input,cb,NULL);assert(result.code==OFP_OK && !result.cleanup_pending && !input->ready && !input->size);
    assert(!input->timeline.pending && input->timeline.token_sequence>=token);++acknowledged;
}
static void clean(opus_family1_playback *s,ogg_page_input *input) {
    assert(ofp_abandon(s).code==OFP_OK && !ofp_has_input(s));opi_reset(input,43);
    assert(!stats.live && stats.created==stats.destroyed && !plane_alloc.pointer && !scratch_alloc.pointer && !packet_alloc.pointer);
    if(plane_alloc.peak>maximum_planes)maximum_planes=plane_alloc.peak;
}
static void positive(const corpus *source,const reference *ref,unsigned style,size_t chunk,bool cached,bool long_tags,bool extended) {
    physical bytes=make(source,style,77,long_tags,extended);creator_walk(&bytes,source);ogg_page_input input={0};opi_reset(&input,42);opus_family1_playback s={0};reset_backend(&s);stats.cache_full=cached;
    output_context out={.reference=ref};ofp_callbacks cb=callbacks(&out);stats.cancelled=&out.cancelled;reader r={.chunk=chunk};
    while(ready(&input,&bytes,&r))successful_page(&s,&input,&cb);
    assert(r.at==bytes.size && opi_finish(&input)==OPI_FINISHED && out.emitted==ref->logical_frames && !ofp_has_input(&s) && !stats.live && stats.created==stats.destroyed);
    if(!s.plan.needed)assert(!stats.created && !plane_alloc.calls && !scratch_alloc.calls);
    if(source->plc)assert(plane_alloc.peak==92160 && plane_alloc.calls==2 && scratch_alloc.calls==2);
    clean(&s,&input);physical_free(&bytes);++positives;
}

typedef enum { FAIL_OPEN,FAIL_DECODE,FAIL_PLANES,FAIL_SCRATCH,FAIL_PACKET,FAIL_OUTPUT,CANCEL_YIELD,CANCEL_OUTPUT,CANCEL_OPEN,CANCEL_HEAD } failure_kind;
static void failure(const corpus *source,const reference *ref,failure_kind kind,unsigned ordinal) {
    unsigned style=kind==FAIL_PACKET?1:0;physical bytes=make(source,style,91,false,false);creator_walk(&bytes,source);
    ogg_page_input input={0};opi_reset(&input,42);opus_family1_playback s={0};reset_backend(&s);output_context out={.reference=ref};ofp_callbacks cb=callbacks(&out);stats.cancelled=&out.cancelled;
    if(kind==FAIL_OPEN)stats.open_refuse=ordinal;
    if(kind==FAIL_DECODE)stats.decode_refuse=ordinal;
    if(kind==FAIL_PLANES)plane_alloc.refuse=ordinal;
    if(kind==FAIL_SCRATCH){scratch_alloc.refuse=ordinal;stats.cache_full=true;}if(kind==FAIL_PACKET)packet_alloc.refuse=ordinal;
    if(kind==FAIL_OUTPUT)out.refuse_output=ordinal;
    if(kind==CANCEL_YIELD)out.cancel_yield=ordinal;
    if(kind==CANCEL_OUTPUT)out.cancel_output=ordinal;
    if(kind==CANCEL_OPEN)stats.cancel_open=ordinal;
    if(kind==CANCEL_HEAD)out.cancelled=true;
    reader r={.chunk=257};ofp_result result=ofp_code(OFP_OK);
    while(ready(&input,&bytes,&r)) {result=ofp_page(&s,&input,&cb,NULL);if(result.code!=OFP_OK)break;assert(!input.ready);++acknowledged;}
    ofp_status expected=kind==FAIL_OPEN || kind==FAIL_PLANES || kind==FAIL_SCRATCH || kind==FAIL_PACKET?OFP_MEMORY:
        kind==FAIL_DECODE?OFP_DECODER:kind==FAIL_OUTPUT?OFP_OUTPUT:OFP_CANCELLED;
    assert(result.code==expected && s.blocked && input.ready && result.cleanup_pending==(stats.live!=0));
    if(kind==FAIL_OPEN)assert(result.decoder.public_error_known && result.decoder.public_error==ESP_AUDIO_ERR_MEM_LACK && stats.created==ordinal-1 && !stats.live);
    if(kind==FAIL_DECODE)assert(result.decoder.public_error_known && result.decoder.public_error==ESP_AUDIO_ERR_FAIL && stats.syntheses==ordinal-1 && !out.published);
    if(kind==FAIL_PLANES)assert(result.detail>0 && !result.decoder.public_error_known &&
        (ordinal==1?(!stats.syntheses && !out.published):(stats.syntheses==s.plan.needed && out.emitted==960)));
    if(kind==FAIL_SCRATCH)assert(result.decoder.code==OFD_MEMORY && !result.decoder.public_error_known && result.detail==(ordinal==1?11520:23040));
    if(kind==FAIL_OUTPUT || kind==CANCEL_OUTPUT)assert(out.published==ordinal-1 && out.emitted==(ordinal-1)*128u);
    if(kind==CANCEL_OPEN)assert(stats.created==s.plan.needed && !stats.decodes && stats.live==s.plan.needed);
    uint8_t *saved=malloc(input.size);assert(saved);memcpy(saved,input.page,input.size);size_t held=input.size;uint64_t token=input.event.token;unsigned calls=stats.decodes,published=out.published;
    ofp_result busy=ofp_page(&s,&input,&cb,NULL);
    assert(busy.code==OFP_BUSY && busy.cleanup_pending==(stats.live!=0) && input.ready && input.event.token==token && input.size==held && !memcmp(input.page,saved,held) && stats.decodes==calls && out.published==published);
    assert(ofp_abandon(&s).code==OFP_OK && input.ready && input.event.token==token && input.size==held && !memcmp(input.page,saved,held));free(saved);
    clean(&s,&input);physical_free(&bytes);++controls;
}
static void close_retry(const corpus *source,const reference *ref) {
    physical bytes=make(source,1,93,false,false);creator_walk(&bytes,source);ogg_page_input input={0};opi_reset(&input,42);opus_family1_playback s={0};reset_backend(&s);
    output_context out={.reference=ref};ofp_callbacks cb=callbacks(&out);reader r={.chunk=257};stats.close_refuse=2;bool retried=false;
    while(ready(&input,&bytes,&r)) {
        ofp_result result=ofp_page(&s,&input,&cb,NULL);
        if(result.code==OFP_CLEANUP) {
            assert(!retried && result.cleanup_pending && result.decoder.public_error_known && result.decoder.public_error==ESP_AUDIO_ERR_INVALID_PARAMETER &&
                input.ready && (input.event.flags&OOPT_LINK_END) && s.phase==OFP_EOS_CLOSE && !s.blocked && stats.live==1 && s.packets.prefix && s.planes && out.emitted==ref->logical_frames);
            unsigned calls=stats.decodes,published=out.published;uint64_t token=input.event.token;uint8_t *saved=malloc(input.size);assert(saved);memcpy(saved,input.page,input.size);size_t size=input.size;
            assert(s.packets.source==&input && s.packets.page_data==input.page && opk_page_exhausted(&s.packets) && !input.timeline.seen_eos);
            stats.close_refuse=0;successful_page(&s,&input,&cb);assert(stats.decodes==calls && out.published==published && !stats.live && input.timeline.seen_eos && input.timeline.token_sequence>=token && !memcmp(input.page,saved,size));free(saved);retried=true;++close_retries;
        } else {assert(result.code==OFP_OK && !input.ready);++acknowledged;}
    }
    assert(retried && opi_finish(&input)==OPI_FINISHED && !ofp_has_input(&s));clean(&s,&input);physical_free(&bytes);++controls;
}
static void abandon_retry(const corpus *source,const reference *ref) {
    physical bytes=make(source,1,95,false,false);creator_walk(&bytes,source);ogg_page_input input={0};opi_reset(&input,42);opus_family1_playback s={0};reset_backend(&s);
    output_context out={.reference=ref};ofp_callbacks cb=callbacks(&out);reader r={.chunk=257};
    while(!out.emitted){assert(ready(&input,&bytes,&r));successful_page(&s,&input,&cb);}
    assert(ready(&input,&bytes,&r));successful_page(&s,&input,&cb);assert(s.packets.partial && s.packets.prefix_size==255);
    assert(ready(&input,&bytes,&r) && input.page[26]==0);uint64_t token=input.event.token;size_t held=input.size,prefix=s.packets.prefix_size,capacity=s.capacity;
    uint8_t *saved=malloc(held);assert(saved);memcpy(saved,input.page,held);uint8_t prefix_saved[255];memcpy(prefix_saved,s.packets.prefix,255);uint8_t *planes=s.planes,*encoded=s.packets.prefix;
    stats.close_refuse=2;ofp_result result=ofp_abandon(&s);
    assert(result.code==OFP_CLEANUP && result.cleanup_pending && s.blocked && stats.live==1 && input.ready && input.event.token==token && input.size==held &&
        !memcmp(input.page,saved,held) && s.planes==planes && s.capacity==capacity && s.packets.prefix==encoded && s.packets.prefix_size==prefix && !memcmp(encoded,prefix_saved,255));
    result=ofp_page(&s,&input,&cb,NULL);assert(result.code==OFP_BUSY && result.cleanup_pending);stats.close_refuse=0;result=ofp_abandon(&s);
    assert(result.code==OFP_OK && !result.cleanup_pending && !ofp_has_input(&s) && input.ready && input.event.token==token && !memcmp(input.page,saved,held));free(saved);
    clean(&s,&input);physical_free(&bytes);++controls;
}
static void moved(const corpus *source,const reference *ref) {
    physical bytes=make(source,0,97,false,false);creator_walk(&bytes,source);ogg_page_input input={0};opi_reset(&input,42);opus_family1_playback s={0};reset_backend(&s);
    output_context out={.reference=ref};ofp_callbacks cb=callbacks(&out);reader r={.chunk=257};
    do {assert(ready(&input,&bytes,&r));successful_page(&s,&input,&cb);}while(s.phase!=OFP_AUDIO);
    assert(ready(&input,&bytes,&r));opus_family1_playback copy=s;unsigned live=stats.live;
    assert(ofp_page(&copy,&input,&cb,NULL).code==OFP_MOVED && ofp_abandon(&copy).code==OFP_MOVED && stats.live==live && !stats.decodes && input.ready);
    successful_page(&s,&input,&cb);clean(&s,&input);physical_free(&bytes);++controls;
}
static void malformed_unused(const corpus *source) {
    const uint8_t map[1]={7};corpus bad=variant(source,1,map);uint8_t **packets=malloc(source->count*sizeof(*packets));assert(packets);memcpy(packets,source->packet,source->count*sizeof(*packets));
    packets[0]=malloc(source->bytes[0]);assert(packets[0]);memcpy(packets[0],source->packet[0],source->bytes[0]);packets[0][0]=(uint8_t)((packets[0][0]&7u)|(30u<<3));bad.packet=packets;
    physical bytes=make(&bad,0,99,false,false);creator_walk(&bytes,&bad);ogg_page_input input={0};opi_reset(&input,42);opus_family1_playback s={0};reset_backend(&s);output_context out={0};ofp_callbacks cb=callbacks(&out);reader r={.chunk=257};ofp_result result=ofp_code(OFP_OK);
    while(ready(&input,&bytes,&r)){result=ofp_page(&s,&input,&cb,NULL);if(result.code!=OFP_OK)break;assert(!input.ready);++acknowledged;}
    assert(result.code==OFP_DECODER && result.decoder.code==OFD_FRAMING && !result.decoder.public_error_known && input.ready && !stats.decodes && !out.published && !stats.live);
    clean(&s,&input);physical_free(&bytes);free(packets[0]);free(packets);++controls;
}
static void tag_boundary(const corpus *source,const reference *ref,unsigned failure_mode) {
    physical bytes=make(source,1,103,true,false);
    const uint8_t scalar[4]={0xf0,0x90,0x80,0x80};memcpy(bytes.tags+65024,scalar,4);
    if(failure_mode==1)bytes.tags[65026]=0xff;
    if(failure_mode==2)put32(bytes.tags+8,UINT32_MAX);
    replace_tags(&bytes);creator_walk(&bytes,source);ogg_page_input input={0};opi_reset(&input,42);opus_family1_playback s={0};reset_backend(&s);
    output_context out={.reference=ref};ofp_callbacks cb=callbacks(&out);reader r={.chunk=257};bool refused=false;
    while(ready(&input,&bytes,&r)) {
        opus_tags_stream before=s.tags;ofp_result result=ofp_page(&s,&input,&cb,NULL);
        if(result.code!=OFP_OK) {
            assert(failure_mode && result.code==OFP_HEADER && result.detail==(failure_mode==1?OTS_UTF8:OTS_INVALID) && input.ready &&
                !stats.opens && !out.published && !memcmp(&s.tags,&before,sizeof(before)) && s.tags.parser.bytes==65025 && s.blocked);
            refused=true;break;
        }
        assert(!input.ready);++acknowledged;
    }
    if(failure_mode){assert(refused);++controls;}
    else {assert(!refused && out.emitted==ref->logical_frames && opi_finish(&input)==OPI_FINISHED && !ofp_has_input(&s));++positives;}
    clean(&s,&input);physical_free(&bytes);
}
static void chain(const corpus *sources,const reference *refs) {
    ogg_page_input input={0};opi_reset(&input,42);opus_family1_playback s={0};reset_backend(&s);
    for(unsigned link=0;link<3;++link) {
        physical bytes=make(sources+link,link%3u,110u+link,false,false);creator_walk(&bytes,sources+link);reader r={.chunk=257};output_context out={.reference=refs+link};ofp_callbacks cb=callbacks(&out);
        while(ready(&input,&bytes,&r))successful_page(&s,&input,&cb);
        assert(r.at==bytes.size && !stats.live && stats.created==stats.destroyed && !ofp_has_input(&s) && opi_finish(&input)==OPI_FINISHED && out.emitted==refs[link].logical_frames);physical_free(&bytes);
    }
    clean(&s,&input);++positives;
}
int main(int argc,char **argv) {
    assert(argc==5);corpus source[4];reference ref[4];for(unsigned i=0;i<4;++i){source[i]=load(argv[i+1]);ref[i]=creator_reference(source+i);}
    for(unsigned i=0;i<3;++i)for(unsigned style=0;style<3;++style)for(unsigned feed=0;feed<2;++feed)positive(source+i,ref+i,style,feed?257:0,false,false,false);
    const uint8_t maps[8][8]={{7},{6,0},{5,5,255},{7,0,6,1},{255,255,255,255,255},{0,1,2,3,4,5},{7,7,6,5,0,255,1},{0,7,0,7,255,5,6,255}};
    for(unsigned c=1;c<=8;++c){corpus v=variant(source+2,c,maps[c-1]);reference r=creator_reference(&v);positive(&v,&r,0,257,false,false,false);free(r.pcm);}
    for(unsigned cached=0;cached<2;++cached)positive(source+3,ref+3,1,257,cached!=0,false,false);
    positive(source+2,ref+2,1,1,false,true,true);chain(source,ref);
    corpus empty=source[2];empty.count=empty.pre_skip=empty.logical=0;put16(empty.head+10,0);reference empty_ref={.channels=8};positive(&empty,&empty_ref,0,1,false,true,false);
    corpus growth=plc_growth();reference growth_ref=creator_reference(&growth);for(unsigned cached=0;cached<2;++cached)positive(&growth,&growth_ref,0,257,cached!=0,false,false);
    for(unsigned i=1;i<=5;++i){failure(source+2,ref+2,FAIL_OPEN,i);failure(source+2,ref+2,FAIL_DECODE,i);}
    failure(source+2,ref+2,FAIL_PLANES,1);failure(&growth,&growth_ref,FAIL_PLANES,2);failure(source+2,ref+2,FAIL_SCRATCH,1);failure(source+3,ref+3,FAIL_SCRATCH,2);
    failure(source+2,ref+2,FAIL_PACKET,1);failure(source+2,ref+2,FAIL_OUTPUT,1);failure(source+2,ref+2,FAIL_OUTPUT,3);failure(source+2,ref+2,CANCEL_YIELD,1);
    failure(source+2,ref+2,CANCEL_OUTPUT,3);failure(source+2,ref+2,CANCEL_OPEN,1);failure(source+2,ref+2,CANCEL_HEAD,1);
    close_retry(source+2,ref+2);abandon_retry(source+2,ref+2);moved(source+2,ref+2);malformed_unused(source+2);
    for(unsigned mode=0;mode<3;++mode)tag_boundary(source+2,ref+2,mode);
    for(unsigned i=0;i<4;++i){free(ref[i].pcm);corpus_free(source+i);}free(growth_ref.pcm);corpus_free(&growth);
    assert(!stats.live && !plane_alloc.pointer && !scratch_alloc.pointer && !packet_alloc.pointer);
    printf("{\"suite\":\"opus-family1-playback\",\"passed\":true,\"positive_schedules\":%u,\"host_contract_controls\":%u,\"creator_libogg_walks\":%u,\"actual_page_acks\":%u,\"creator_pcm_samples_exact\":%" PRIu64
        ",\"eos_close_retry\":%u,\"maximum_unique_plane_bytes\":%zu,\"maximum_output_chunk_bytes\":%zu,\"whole_original_120ms_packets\":92,\"gain_metadata_only\":true,\"scripted_host_statuses\":true,\"native_esp_oom_qualified\":false,\"production_selected\":false}\n",
        positives,controls,libogg_walks,acknowledged,compared_samples,close_retries,maximum_planes,maximum_chunk);return 0;
}
