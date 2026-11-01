/* HOST ONLY: creator-backed documented public-API contract seam.
 * Scripted open/decode/close statuses and scratch allocator refusals are TEST
 * DOUBLES, not observed ESP/native allocation failures. All positive synthesis,
 * previous live handles and destruction use real public creator APIs.
 */
#include <stddef.h>
#include <stdlib.h>
static void *scratch_realloc(void *,size_t);
static void scratch_free(void *);
#define OFD_REALLOC scratch_realloc
#define OFD_FREE scratch_free
#include "opus_family1_decoder.h"
#include "opus_family1_public.h"
#include <assert.h>
#include <inttypes.h>
#include <math.h>
#include <stdio.h>
typedef struct OpusDecoder OpusDecoder;
extern OpusDecoder *opus_decoder_create(int32_t,int,int *);
extern int opus_decode_float(OpusDecoder *,const unsigned char *,int32_t,float *,int,int);
extern void opus_decoder_destroy(OpusDecoder *);
extern int opus_packet_get_nb_samples(const unsigned char *,int32_t,int32_t);
typedef struct {OpusDecoder *decoder;const esp_opus_dec_cfg_t *cfg;esp_opus_dec_cfg_t expected;uint8_t *pending;unsigned pending_bytes;} host_handle;
typedef struct {unsigned opens,created,decodes,syntheses,closes,destroyed,live,open_refuse,decode_refuse,close_refuse;bool cache_full;} backend;
typedef struct {uint8_t head[40];uint8_t **packet;size_t *bytes;unsigned count,n,m,c;} corpus;
static backend stats;
static opus_family1_decoder *current_owner;
static unsigned scratch_calls,scratch_refuse;
static void *live_scratch;
static size_t scratch_bytes;
static unsigned controls,positive_cases;
static uint64_t compared_samples;
static void *scratch_realloc(void *p,size_t n) {
    assert(p==live_scratch && n<=23040);++scratch_calls;if(scratch_calls==scratch_refuse)return NULL;
    void *next=realloc(p,n);assert(next);live_scratch=next;scratch_bytes=n;return next;
}
static void scratch_free(void *p) {
    if(!p)return;
    assert(p==live_scratch);free(p);live_scratch=NULL;scratch_bytes=0;
}
static void cfg_stable(const host_handle *h) {
    const esp_opus_dec_cfg_t *p=h->cfg;assert(p->sample_rate==h->expected.sample_rate && p->channel==h->expected.channel &&
        p->frame_duration==h->expected.frame_duration && p->self_delimited==h->expected.self_delimited);
    bool found=false;for(unsigned i=0;i<8;++i)if(p==&current_owner->cfg[i])found=true;assert(found);
}
static int16_t rounded(double v){double x=v*32768.0;return x>32767?32767:x<-32768?-32768:(int16_t)llround(x);}
static void put16(uint8_t *p,int16_t v){unsigned n=(unsigned)(uint16_t)v;p[0]=(uint8_t)n;p[1]=(uint8_t)(n>>8);}
esp_audio_err_t esp_opus_dec_open(void *opaque,uint32_t bytes,void **out) {
    const esp_opus_dec_cfg_t *cfg=opaque;assert(bytes==sizeof(*cfg) && cfg && out && !*out && cfg->sample_rate==48000 &&
        (cfg->channel==1 || cfg->channel==2) && cfg->frame_duration==ESP_OPUS_DEC_FRAME_DURATION_INVALID);++stats.opens;
    if(stats.opens==stats.open_refuse)return ESP_AUDIO_ERR_MEM_LACK; /* Explicit HOST status seam, no creator call. */
    host_handle *h=calloc(1,sizeof(*h));assert(h);int error=0;h->decoder=opus_decoder_create(48000,cfg->channel,&error);assert(h->decoder && !error);
    h->cfg=cfg;h->expected=*cfg;cfg_stable(h);*out=h;++stats.created;++stats.live;return ESP_AUDIO_ERR_OK;
}
static void synthesize(host_handle *h,const uint8_t *data,size_t bytes,uint8_t *pcm,unsigned frames) {
    float *samples=malloc((size_t)frames*h->cfg->channel*sizeof(float));assert(samples);
    assert(opus_decode_float(h->decoder,data,(int32_t)bytes,samples,(int)frames,0)==(int)frames);++stats.syntheses;
    for(unsigned i=0;i<frames*h->cfg->channel;++i)put16(pcm+i*2u,rounded(samples[i]));
    free(samples);
}
esp_audio_err_t esp_opus_dec_decode(void *opaque,esp_audio_dec_in_raw_t *raw,esp_audio_dec_out_frame_t *out,esp_audio_dec_info_t *info) {
    host_handle *h=opaque;assert(h && raw && out && info && raw->frame_recover==ESP_AUDIO_DEC_RECOVERY_NONE);cfg_stable(h);++stats.decodes;
    if(stats.decodes==stats.decode_refuse)return ESP_AUDIO_ERR_FAIL; /* HOST status seam. */
    if(h->pending) {
        assert(!raw->len);out->needed_size=h->pending_bytes;
        if(out->len<h->pending_bytes)return ESP_AUDIO_ERR_BUFF_NOT_ENOUGH;
        memcpy(out->buffer,h->pending,h->pending_bytes);out->decoded_size=h->pending_bytes;free(h->pending);h->pending=NULL;h->pending_bytes=0;
    } else {
        opus_elementary_view view;assert(omf_element(raw->buffer,raw->len,h->cfg->self_delimited,&view)==OMF_OK && view.bytes==raw->len);
        size_t common_bytes=view.bytes-view.extra_bytes;uint8_t *common=malloc(common_bytes);assert(common);
        memcpy(common,view.data,view.extra_offset);memcpy(common+view.extra_offset,view.data+view.extra_offset+view.extra_bytes,view.bytes-view.extra_offset-view.extra_bytes);
        int frames=opus_packet_get_nb_samples(common,(int32_t)common_bytes,48000);assert(frames>0 && frames<=5760);unsigned needed=(unsigned)frames*h->cfg->channel*2u;
        if(out->len<needed) {
            out->needed_size=needed;
            if(stats.cache_full){h->pending=malloc(needed);assert(h->pending);h->pending_bytes=needed;synthesize(h,common,common_bytes,h->pending,(unsigned)frames);raw->consumed=raw->len;}
            free(common);return ESP_AUDIO_ERR_BUFF_NOT_ENOUGH;
        }
        synthesize(h,common,common_bytes,out->buffer,(unsigned)frames);free(common);raw->consumed=raw->len;out->decoded_size=needed;
    }
    info->sample_rate=48000;info->channel=h->cfg->channel;info->bits_per_sample=16;return ESP_AUDIO_ERR_OK;
}
esp_audio_err_t esp_opus_dec_close(void *opaque) {
    host_handle *h=opaque;assert(h);cfg_stable(h);++stats.closes;
    if(stats.closes==stats.close_refuse)return ESP_AUDIO_ERR_INVALID_PARAMETER; /* HOST close refusal, creator object stays real/live. */
    opus_decoder_destroy(h->decoder);free(h->pending);free(h);++stats.destroyed;assert(stats.live);--stats.live;return ESP_AUDIO_ERR_OK;
}
static void reset_backend(opus_family1_decoder *owner) {
    assert(!stats.live && !live_scratch && !scratch_bytes);memset(&stats,0,sizeof(stats));scratch_calls=scratch_refuse=0;current_owner=owner;
}
typedef struct {
    opus_family1_plan plan;
    uint8_t *buffers[8];size_t produced[8];
    const float *reference;
    unsigned samples,begins,writes,finishes,aborts,published,refuse_begin,refuse_write,refuse_finish;
} stage;
static bool stage_begin(void *opaque,const opus_family1_plan *plan,uint32_t generation,uint16_t samples) {
    stage *s=opaque;assert(generation==42 && plan->header_gain_q8==1536 && plan->pre_skip==312 && plan->input_rate==48000);++s->begins;s->plan=*plan;s->samples=samples;
    if(s->refuse_begin)return false;
    for(unsigned i=0;i<plan->needed;++i){assert(!s->buffers[i]);s->buffers[i]=calloc((size_t)samples*plan->stream_channels[i],2);assert(s->buffers[i]);s->produced[i]=0;}
    return true;
}
static bool stage_write(void *opaque,uint8_t slot,uint8_t stream,uint8_t channels,size_t offset,const uint8_t *pcm,size_t frames) {
    stage *s=opaque;++s->writes;assert(slot<s->plan.needed && stream==s->plan.stream_id[slot] && channels==s->plan.stream_channels[slot] && offset==s->produced[slot]);
    if(s->writes==s->refuse_write)return false;
    assert(frames<=s->samples-offset);memcpy(s->buffers[slot]+offset*channels*2u,pcm,frames*channels*2u);s->produced[slot]+=frames;return true;
}
static void release_stage(stage *s){for(unsigned i=0;i<8;++i){free(s->buffers[i]);s->buffers[i]=NULL;s->produced[i]=0;}}
static bool stage_finish(void *opaque) {
    stage *s=opaque;++s->finishes;if(s->refuse_finish)return false;assert(s->reference);of1_pcm_buffer buffers[8]={{0}};
    for(unsigned i=0;i<s->plan.needed;++i){assert(s->produced[i]==s->samples);buffers[i]=(of1_pcm_buffer){s->buffers[i],(size_t)s->samples*s->plan.stream_channels[i]*2u};}
    of1_channel_view views[8];assert(of1_channel_views(&s->plan,buffers,s->plan.needed,s->samples,views)==OF1_OK);uint8_t output[97*8*2];
    for(size_t first=0;first<s->samples;first+=97) {
        size_t count=s->samples-first;if(count>97)count=97;size_t written=0;assert(of1_gather_s16(views,s->plan.channels,first,count,output,sizeof(output),&written)==OF1_OK);
        for(size_t i=0;i<count*s->plan.channels;++i){uint8_t expected[2];put16(expected,rounded(s->reference[first*s->plan.channels+i]));assert(!memcmp(output+i*2u,expected,2));++compared_samples;}
    }
    ++s->published;release_stage(s);return true;
}
static void stage_abort(void *opaque){stage *s=opaque;++s->aborts;release_stage(s);}
static ofd_pcm_sink sink(stage *s){return (ofd_pcm_sink){stage_begin,stage_write,stage_finish,stage_abort,NULL,s};}
static void make_head(uint8_t head[40],const corpus *source,unsigned channels,const uint8_t *map) {
    memset(head,0,40);memcpy(head,"OpusHead",8);head[8]=1;head[9]=(uint8_t)channels;head[16]=0;head[17]=6;head[18]=1;
    unsigned pre_skip=of1_le32(source->head+20);head[10]=(uint8_t)pre_skip;head[11]=(uint8_t)(pre_skip>>8);head[12]=0x80;head[13]=0xbb;
    head[19]=(uint8_t)source->n;head[20]=(uint8_t)source->m;memcpy(head+21,map,channels);
}
static void positive(const corpus *source,unsigned channels,const uint8_t *map,bool cached) {
    opus_family1_decoder owner={0};reset_backend(&owner);stats.cache_full=cached;uint8_t head[40];make_head(head,source,channels,map);
    assert(ofd_open(&owner,head,21u+channels,42,NULL).code==OFD_OK && owner.active);int error=0;
    OpusMSDecoder *reference=opus_multistream_decoder_create(48000,(int)channels,(int)source->n,(int)source->m,map,&error);assert(reference && !error);
    unsigned needed=owner.plan.needed;float *reference_pcm=malloc(5760u*channels*sizeof(float));assert(reference_pcm);stage staged={0};ofd_pcm_sink output=sink(&staged);
    for(unsigned p=0;p<source->count;++p) {
        int frames=opus_multistream_decode_float(reference,source->packet[p],(int32_t)source->bytes[p],reference_pcm,5760,0);assert(frames>0);staged.reference=reference_pcm;
        assert(ofd_decode_packet(&owner,source->packet[p],source->bytes[p],&output).code==OFD_OK && owner.active && !staged.aborts && staged.published==p+1);
    }
    assert(ofd_close(&owner).code==OFD_OK && !owner.active && !ofd_has_handles(&owner) && stats.created==needed && stats.created==stats.destroyed && !stats.live && !live_scratch);
    assert(ofd_close(&owner).code==OFD_OK);opus_multistream_decoder_destroy(reference);free(reference_pcm);release_stage(&staged);++positive_cases;
}
static void negative_controls(const corpus *source,const corpus *long_source) {
    const uint8_t map[8]={0,6,1,2,3,4,5,7};uint8_t head[40];make_head(head,source,8,map);
    for(unsigned ordinal=1;ordinal<=5;++ordinal) {
        opus_family1_decoder owner={0};reset_backend(&owner);stats.open_refuse=ordinal;ofd_result result=ofd_open(&owner,head,29,42,NULL);
        assert(result.code==OFD_PUBLIC_OPEN && result.public_error_known && result.public_error==ESP_AUDIO_ERR_MEM_LACK && !result.cleanup_pending && !owner.active &&
            stats.opens==ordinal && stats.created==ordinal-1 && stats.destroyed==stats.created && !stats.live && !scratch_calls);++controls;
    }
    for(unsigned ordinal=1;ordinal<=5;++ordinal) {
        opus_family1_decoder owner={0};reset_backend(&owner);assert(ofd_open(&owner,head,29,42,NULL).code==OFD_OK);stats.decode_refuse=ordinal;stage s={0};ofd_pcm_sink output=sink(&s);
        ofd_result result=ofd_decode_packet(&owner,source->packet[0],source->bytes[0],&output);
        assert(result.code==OFD_PUBLIC_DECODE && result.public_error_known && result.public_error==ESP_AUDIO_ERR_FAIL && !result.cleanup_pending && s.aborts==1 && !s.published &&
            stats.created==5 && stats.destroyed==5 && stats.syntheses==ordinal-1 && !stats.live && !live_scratch);++controls;
    }
    for(unsigned failure=0;failure<3;++failure) {
        opus_family1_decoder owner={0};reset_backend(&owner);assert(ofd_open(&owner,head,29,42,NULL).code==OFD_OK);stage s={0};
        if(failure==0)s.refuse_begin=1;
        if(failure==1)s.refuse_write=1;
        if(failure==2)s.refuse_finish=1;
        ofd_pcm_sink output=sink(&s);
        ofd_result result=ofd_decode_packet(&owner,source->packet[0],source->bytes[0],&output);
        assert(result.code==OFD_SINK && !result.public_error_known && s.aborts==1 && !s.published && !stats.live && !live_scratch);++controls;
    }
    for(unsigned cached=0;cached<2;++cached)for(unsigned ordinal=1;ordinal<=2;++ordinal) {
        opus_family1_decoder owner={0};reset_backend(&owner);stats.cache_full=cached!=0;const uint8_t stereo[2]={0,1};uint8_t long_head[40];make_head(long_head,long_source,2,stereo);
        assert(ofd_open(&owner,long_head,23,42,NULL).code==OFD_OK);scratch_refuse=ordinal;stage s={0};ofd_pcm_sink output=sink(&s);
        ofd_result result=ofd_decode_packet(&owner,long_source->packet[0],long_source->bytes[0],&output);
        assert(result.code==OFD_MEMORY && result.detail==(ordinal==1?11520:23040) && !result.public_error_known && !result.cleanup_pending &&
            stats.created==1 && stats.destroyed==1 && !stats.live && !live_scratch && !scratch_bytes && s.aborts==(ordinal==2) && !s.published);++controls;
    }
    {
        opus_family1_decoder owner={0};reset_backend(&owner);assert(ofd_open(&owner,head,29,42,NULL).code==OFD_OK);unsigned opens=stats.opens;
        assert(ofd_open(&owner,head,29,42,NULL).code==OFD_BUSY && stats.opens==opens);opus_family1_decoder moved=owner;stage s={0};ofd_pcm_sink output=sink(&s);
        assert(ofd_decode_packet(&moved,source->packet[0],source->bytes[0],&output).code==OFD_MOVED && ofd_close(&moved).code==OFD_MOVED && !stats.decodes);
        assert(ofd_close(&owner).code==OFD_OK && stats.created==stats.destroyed);++controls;
    }
    {
        opus_family1_decoder owner={0};reset_backend(&owner);assert(ofd_open(&owner,head,29,42,NULL).code==OFD_OK);stats.close_refuse=2;
        ofd_result result=ofd_close(&owner);assert(result.code==OFD_PUBLIC_CLOSE && result.cleanup_pending && stats.live==1);
        assert(ofd_open(&owner,head,29,42,NULL).code==OFD_BUSY);stats.close_refuse=0;assert(ofd_close(&owner).code==OFD_OK && !stats.live && stats.created==stats.destroyed);++controls;
    }
    {
        const uint8_t final_only[1]={7};uint8_t one[40];make_head(one,source,1,final_only);opus_family1_decoder owner={0};reset_backend(&owner);
        assert(ofd_open(&owner,one,22,42,NULL).code==OFD_OK && stats.created==1);uint8_t *bad=malloc(source->bytes[0]);assert(bad);memcpy(bad,source->packet[0],source->bytes[0]);bad[0]=(uint8_t)((bad[0]&7u)|(30u<<3));
        stage s={0};ofd_pcm_sink output=sink(&s);ofd_result result=ofd_decode_packet(&owner,bad,source->bytes[0],&output);free(bad);
        assert(result.code==OFD_FRAMING && !result.public_error_known && !stats.decodes && !s.begins && !stats.live);++controls;
    }
    {
        opus_family1_decoder owner={0};reset_backend(&owner);assert(ofd_open(&owner,head,29,42,NULL).code==OFD_OK);uint8_t *large=calloc(61441,1);assert(large);stage s={0};ofd_pcm_sink output=sink(&s);
        ofd_result result=ofd_decode_packet(&owner,large,61441,&output);free(large);assert(result.code==OFD_PACKET_POLICY && !result.public_error_known && !stats.decodes && !stats.live);++controls;
    }
    {
        opus_family1_decoder owner={0};reset_backend(&owner);owner.plan.input_rate=12345;uint8_t bad[40];memcpy(bad,head,40);bad[8]=16;
        assert(ofd_open(&owner,bad,29,42,NULL).code==OFD_HEADER && owner.plan.input_rate==12345 && !owner.anchor && !stats.opens);
        ofd_public_api invalid={esp_opus_dec_open,esp_opus_dec_decode,NULL};assert(ofd_open(&owner,head,29,42,&invalid).code==OFD_ARGUMENT && !stats.opens && !owner.anchor);
        assert(ofd_open(&owner,head,29,42,NULL).code==OFD_OK);stage s={0};ofd_pcm_sink output=sink(&s);output.write=NULL;
        assert(ofd_decode_packet(&owner,source->packet[0],source->bytes[0],&output).code==OFD_ARGUMENT && owner.active && !stats.decodes);
        assert(ofd_close(&owner).code==OFD_OK && !stats.live);++controls;
    }
}
static corpus load(const char *path) {
    FILE *f=fopen(path,"rb");assert(f);corpus s={0};assert(fread(s.head,1,40,f)==40 && !memcmp(s.head,"OFAM101\0",8));s.c=of1_le32(s.head+8);s.n=of1_le32(s.head+12);s.m=of1_le32(s.head+16);s.count=of1_le32(s.head+28);
    assert(s.count && s.count<=100);s.packet=calloc(s.count,sizeof(*s.packet));s.bytes=calloc(s.count,sizeof(*s.bytes));assert(s.packet && s.bytes);
    for(unsigned i=0;i<s.count;++i){uint8_t length[4];assert(fread(length,1,4,f)==4);s.bytes[i]=of1_le32(length);s.packet[i]=malloc(s.bytes[i]);assert(s.packet[i] && fread(s.packet[i],1,s.bytes[i],f)==s.bytes[i]);}assert(fgetc(f)==EOF && !fclose(f));return s;
}
static void release(corpus *s){for(unsigned i=0;i<s->count;++i)free(s->packet[i]);free(s->packet);free(s->bytes);}
int main(int argc,char **argv) {
    assert(argc==5);corpus sources[4];for(unsigned i=0;i<4;++i)sources[i]=load(argv[i+1]);
    const uint8_t defaults[3][8]={{0,2,1},{0,4,1,2,3,5},{0,6,1,2,3,4,5,7}};for(unsigned i=0;i<3;++i)positive(sources+i,sources[i].c,defaults[i],false);
    const uint8_t variants[8][8]={{7},{6,0},{5,5,255},{7,0,6,1},{255,255,255,255,255},{0,1,2,3,4,5},{7,7,6,5,0,255,1},{0,7,0,7,255,5,6,255}};
    for(unsigned c=1;c<=8;++c)positive(sources+2,c,variants[c-1],false);
    const uint8_t stereo[2]={0,1};positive(sources+3,2,stereo,false);positive(sources+3,2,stereo,true);
    negative_controls(sources+2,sources+3);for(unsigned i=0;i<4;++i)release(sources+i);
    assert(!stats.live && !live_scratch && !scratch_bytes);
    printf("{\"suite\":\"opus-family1-decoder-owner\",\"passed\":true,\"positive_cases\":%u,\"host_contract_controls\":%u,\"creator_pcm_samples_exact\":%" PRIu64
        ",\"stable_cfg_addresses\":true,\"scripted_host_statuses\":true,\"owner_allocator_host_seam\":true,\"native_esp_oom_qualified\":false,\"production_selected\":false}\n",positive_cases,controls,compared_samples);return 0;
}
