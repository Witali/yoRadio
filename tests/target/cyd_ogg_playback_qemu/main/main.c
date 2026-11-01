// Actual application Ogg wrapper; only public calls and synchronous output observed.
#include <assert.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_heap_caps.h"
#include "esp_system.h"
#include "esp_task_wdt.h"
#include "psa/crypto.h"
#include "decoder_registration.h"
#include "ogg_playback.h"

#ifdef NDEBUG
#error "The playback diagnostic requires actual assertions"
#endif
extern const uint8_t short_start[] asm("_binary_fixture20_ogg_start");
extern const uint8_t short_end[] asm("_binary_fixture20_ogg_end");
extern const uint8_t long_start[] asm("_binary_fixture120_ogg_start");
extern const uint8_t long_end[] asm("_binary_fixture120_ogg_end");
extern const uint8_t vorbis_start[] asm("_binary_fixturevorbis_ogg_start");
extern const uint8_t vorbis_end[] asm("_binary_fixturevorbis_ogg_end");

typedef struct {
    const char *name;
    const uint8_t *begin, *end;
    const char *raw_sha, *pcm_sha;
    uint64_t raw_bytes;
    bool opus;
} fixture;
static const fixture fixtures[] = {
    {"opus20",short_start,short_end,"a773dc8a0db92aebd689c157bb504cd43e6d6544f8249362db57d59176cb316b",
     "b63b58b563d2a20d90a7bef235e5c1099dc52433db19083492d9c7098345469f",2115840,true},
    {"opus120",long_start,long_end,"670f7787b470d0e8bc101856bc16e42ed0cb15ef85abf3a0214db0261f4cb684",
     "4110db997c16a05c329284bb6105468752c25d67818e3a99b8c9d47c5f481fd0",2119680,true},
    {"vorbis",vorbis_start,vorbis_end,"e2c316f3e6b7a4a919027ab918cef54fc60a741a944aac26fc215ce33d396910",
     "e2c316f3e6b7a4a919027ab918cef54fc60a741a944aac26fc215ce33d396910",2112000,false},
};
typedef struct {
    const char *id;
    ogg_playback playback;
    const fixture *current;
    psa_hash_operation_t raw_hash, pcm_hash, window_hash;
    uint64_t raw_bytes, pcm_bytes, window_bytes, window_begin, window_end;
    uint64_t case_pcm;
    unsigned calls, link_calls, outputs, resizes, link_resizes, opens, closes, yields;
    bool live, cleanup, modified, chain;
} context;
static context *active;
static unsigned completed_cases;
static void configure_fixture(context *,const fixture *,bool);

static void digest(psa_hash_operation_t *hash, char hex[65])
{
    uint8_t bytes[32]; size_t size;
    assert(psa_hash_finish(hash,bytes,sizeof(bytes),&size)==PSA_SUCCESS && size==32);
    assert(psa_hash_abort(hash)==PSA_SUCCESS);
    for(unsigned i=0;i<32;++i) snprintf(hex+2*i,3,"%02x",bytes[i]);
}
static void begin_hash(psa_hash_operation_t *hash)
{
    *hash=psa_hash_operation_init();
    assert(psa_hash_setup(hash,PSA_ALG_SHA_256)==PSA_SUCCESS);
}

esp_audio_err_t __real_esp_audio_simple_dec_open(esp_audio_simple_dec_cfg_t *,esp_audio_simple_dec_handle_t *);
esp_audio_err_t __real_esp_audio_simple_dec_process(esp_audio_simple_dec_handle_t,esp_audio_simple_dec_raw_t *,esp_audio_simple_dec_out_t *);
void __real_esp_audio_simple_dec_close(esp_audio_simple_dec_handle_t);

esp_audio_err_t __wrap_esp_audio_simple_dec_open(esp_audio_simple_dec_cfg_t *cfg,esp_audio_simple_dec_handle_t *handle)
{
    context *c=active;
    assert(c && !c->live && c->current && c->playback.input.ready && c->playback.input.event.crc_verified);
    assert(c->opens==c->closes && cfg->dec_type==ESP_AUDIO_SIMPLE_DEC_TYPE_OGG);
    if(c->chain) {
        const fixture *found=NULL;
        for(unsigned i=0;i<3;++i) if(oopt_le32(fixtures[i].begin+14)==c->playback.input.event.serial) found=&fixtures[i];
        assert(found); configure_fixture(c,found,false);
    }
    esp_audio_err_t result=__real_esp_audio_simple_dec_open(cfg,handle);
    if(result==ESP_AUDIO_ERR_OK) {
        assert(*handle); c->live=true; ++c->opens;
        c->raw_bytes=c->pcm_bytes=c->window_bytes=0;
        c->link_calls=c->link_resizes=0;
        begin_hash(&c->raw_hash); begin_hash(&c->pcm_hash); begin_hash(&c->window_hash);
    }
    return result;
}
esp_audio_err_t __wrap_esp_audio_simple_dec_process(esp_audio_simple_dec_handle_t handle,
    esp_audio_simple_dec_raw_t *raw,esp_audio_simple_dec_out_t *frame)
{
    context *c=active;
    assert(c && c->live && c->playback.input.ready && c->playback.input.event.crc_verified);
    uint32_t length=raw->len,capacity=frame->len;
    esp_audio_err_t result=__real_esp_audio_simple_dec_process(handle,raw,frame);
    ++c->calls; ++c->link_calls;
    assert(raw->len==length && raw->consumed<=length && frame->decoded_size<=capacity);
    if(result==ESP_AUDIO_ERR_BUFF_NOT_ENOUGH) {
        ++c->resizes; ++c->link_resizes;
        printf("OGP_RESIZE case=%s link=%u call=%u len=%" PRIu32 " consumed=%" PRIu32
               " capacity=%" PRIu32 " needed=%" PRIu32 " decoded=%" PRIu32 " eos=%u result=%d\n",
               c->id,c->opens,c->calls,length,raw->consumed,capacity,frame->needed_size,
               frame->decoded_size,(unsigned)raw->eos,(int)result);
    }
    if(result==ESP_AUDIO_ERR_OK && frame->decoded_size) {
        esp_audio_simple_dec_info_t info={0};
        assert(esp_audio_simple_dec_get_info(handle,&info)==ESP_AUDIO_ERR_OK &&
               info.sample_rate==48000 && info.channel==2 && info.bits_per_sample==16 && !(frame->decoded_size%4));
        assert(psa_hash_update(&c->raw_hash,frame->buffer,frame->decoded_size)==PSA_SUCCESS);
        uint64_t first=c->raw_bytes>c->window_begin?c->raw_bytes:c->window_begin;
        uint64_t last=c->raw_bytes+frame->decoded_size;
        if(last>c->window_end) last=c->window_end;
        if(first<last) {
            assert(psa_hash_update(&c->window_hash,frame->buffer+(size_t)(first-c->raw_bytes),(size_t)(last-first))==PSA_SUCCESS);
            c->window_bytes+=last-first;
        }
        c->raw_bytes+=frame->decoded_size;
    }
    return result;
}
void __wrap_esp_audio_simple_dec_close(esp_audio_simple_dec_handle_t handle)
{
    context *c=active;
    assert(c && c->live);
    if(!c->cleanup) {
        assert(c->playback.input.ready && c->playback.input.timeline.pending &&
               (c->playback.input.event.flags&OOPT_LINK_END));
        char raw_hex[65],pcm_hex[65],window_hex[65];
        digest(&c->raw_hash,raw_hex); digest(&c->pcm_hash,pcm_hex); digest(&c->window_hash,window_hex);
        bool match=c->raw_bytes==c->current->raw_bytes && !strcmp(raw_hex,c->current->raw_sha) &&
                   c->pcm_bytes==c->window_bytes && c->window_bytes==c->window_end-c->window_begin &&
                   !strcmp(pcm_hex,window_hex) && (c->modified || !strcmp(pcm_hex,c->current->pcm_sha));
        printf("OGP_LINK case=%s link=%u fixture=%s raw=%" PRIu64 " raw_sha=%s pcm=%" PRIu64
               " sha=%s window_sha=%s begin=%" PRIu64 " end=%" PRIu64
               " calls=%u resizes=%u outputs=%u close_before_ack=1 match=%u\n",
               c->id,c->opens,c->current->name,c->raw_bytes,raw_hex,c->pcm_bytes,pcm_hex,window_hex,
               c->window_begin,c->window_end,c->link_calls,c->link_resizes,c->outputs,(unsigned)match);
        assert(fflush(stdout)==0 && match);
    } else {
        assert(psa_hash_abort(&c->raw_hash)==PSA_SUCCESS && psa_hash_abort(&c->pcm_hash)==PSA_SUCCESS &&
               psa_hash_abort(&c->window_hash)==PSA_SUCCESS);
    }
    __real_esp_audio_simple_dec_close(handle);
    c->live=false; ++c->closes;
}
static bool cancelled(void *opaque) {assert(opaque==active); return false;}
static bool output(void *opaque,const esp_audio_simple_dec_info_t *info,const uint8_t *pcm,size_t bytes)
{
    context *c=opaque;
    assert(c==active && c->live && c->playback.input.ready && info->sample_rate==48000 && info->channel==2 && info->bits_per_sample==16);
    assert(bytes && !(bytes%4) && psa_hash_update(&c->pcm_hash,pcm,bytes)==PSA_SUCCESS);
    c->pcm_bytes+=bytes; c->case_pcm+=bytes; ++c->outputs;
    return true;
}
static void yield(void *opaque) {assert(opaque==active); ++active->yields; vTaskDelay(1);}
static const ogg_playback_callbacks callbacks={.cancelled=cancelled,.output=output,.yield=yield};

static size_t page_bytes(const uint8_t *p,size_t remaining)
{
    assert(remaining>=27 && !memcmp(p,"OggS",4));
    size_t n=27+p[26]; assert(n<=remaining);
    for(unsigned i=27;i<27u+p[26];++i) n+=p[i];
    assert(n<=remaining && n<=OGG_PAGE_INPUT_MAX);
    return n;
}
static size_t final_page(const fixture *f)
{
    size_t size=(size_t)(f->end-f->begin),at=0,last=0;
    while(at<size) {last=at;at+=page_bytes(f->begin+at,size-at);}
    assert(at==size && (f->begin[last+5]&4)); return last;
}
static void configure_fixture(context *c,const fixture *f,bool modified)
{
    c->current=f; c->modified=modified;
    c->window_begin=f->opus?(modified?512u:312u)*4u:0;
    c->window_end=f->opus?UINT64_C(528312)*4u:f->raw_bytes;
}
static ogg_playback_status feed(context *c,const uint8_t *data,size_t bytes,bool eof,
    esp_audio_simple_dec_handle_t *decoder,uint8_t **pcm,size_t *capacity,decoder_pending_input_t *pending)
{
    ogg_playback_callbacks cb=callbacks; cb.context=c;
    int32_t cause=0;
    ogg_playback_status status=ogp_feed(&c->playback,data,bytes,eof,decoder,pcm,capacity,pending,&cb,&cause);
    if(status!=OGP_OK) printf("OGP_FAILURE case=%s status=%d cause=%" PRId32 " bytes=%u\n",c->id,(int)status,cause,(unsigned)bytes);
    return status;
}
static void finish(context *c,esp_audio_simple_dec_handle_t *decoder,uint8_t **pcm,
    size_t *capacity,decoder_pending_input_t *pending,size_t before,unsigned links)
{
    assert(feed(c,NULL,0,true,decoder,pcm,capacity,pending)==OGP_OK && !*decoder && !pending->size &&
           !c->live && c->opens==links && c->closes==links && c->playback.input.timeline.link==links);
    decoder_pending_input_clear(pending); free(*pcm); *pcm=NULL; ogp_reset(&c->playback,10);
    assert(heap_caps_check_integrity_all(true));
    size_t after=esp_get_free_heap_size();
    printf("OGP_CASE id=%s links=%u calls=%u resizes=%u pcm=%" PRIu64 " before=%u after=%u heap_min=%u stack_free=%u core=%d priority=%u\n",
           c->id,links,c->calls,c->resizes,c->case_pcm,(unsigned)before,(unsigned)after,
           (unsigned)esp_get_minimum_free_heap_size(),(unsigned)uxTaskGetStackHighWaterMark(NULL),xPortGetCoreID(),(unsigned)uxTaskPriorityGet(NULL));
    assert(fflush(stdout)==0); active=NULL; ++completed_cases; vTaskDelay(1);
}
static void standard_case(const fixture *f,unsigned chunk)
{
    char id[48]; snprintf(id,sizeof(id),"%s_%u",f->name,chunk);
    context c={.id=id}; active=&c; ogp_reset(&c.playback,9); configure_fixture(&c,f,false);
    size_t before=esp_get_free_heap_size(),capacity=12288; uint8_t *pcm=malloc(capacity); assert(pcm);
    decoder_pending_input_t pending={0}; esp_audio_simple_dec_handle_t decoder=NULL;
    size_t size=(size_t)(f->end-f->begin),at=0;
    while(at<size) {
        size_t n=chunk?chunk:size; if(n>size-at)n=size-at;
        assert(feed(&c,f->begin+at,n,false,&decoder,&pcm,&capacity,&pending)==OGP_OK); at+=n;
    }
    finish(&c,&decoder,&pcm,&capacity,&pending,before,1);
}
static uint32_t crc(const uint8_t *p,size_t n)
{
    uint32_t value=0;
    for(size_t i=0;i<n;++i) {
        unsigned byte=i>=22&&i<26?0:p[i];
        for(unsigned bit=0;bit<8;++bit) {
            bool a=(value>>31)!=0,b=(byte&(0x80u>>bit))!=0;
            value<<=1; if(a!=b)value^=UINT32_C(0x04c11db7);
        }
    }
    return value;
}
static void put32(uint8_t *p,uint32_t n) {for(unsigned i=0;i<4;++i)p[i]=(uint8_t)(n>>(8u*i));}
static void put64(uint8_t *p,uint64_t n) {for(unsigned i=0;i<8;++i)p[i]=(uint8_t)(n>>(8u*i));}
static uint64_t le64(const uint8_t *p) {return (uint64_t)oopt_le32(p)|(uint64_t)oopt_le32(p+4)<<32;}

static void modified_case(const fixture *f)
{
    char id[48];snprintf(id,sizeof(id),"%s_offset_preskip",f->name);
    context c={.id=id};active=&c;ogp_reset(&c.playback,9);configure_fixture(&c,f,true);
    size_t before=esp_get_free_heap_size(),capacity=12288;uint8_t *pcm=malloc(capacity);assert(pcm);
    decoder_pending_input_t pending={0};esp_audio_simple_dec_handle_t decoder=NULL;
    size_t at=0,size=(size_t)(f->end-f->begin);
    while(at<size) {
        size_t n=page_bytes(f->begin+at,size-at);uint8_t *copy=malloc(n);assert(copy);memcpy(copy,f->begin+at,n);
        if(!at) {assert(copy[26]==1 && !memcmp(copy+28,"OpusHead",8));copy[38]=0;copy[39]=2;}
        uint64_t gp=le64(copy+6);
        if(at && gp && gp!=UINT64_MAX) put64(copy+6,gp+(UINT64_C(1)<<40));
        put32(copy+22,crc(copy,n));
        assert(feed(&c,copy,n,false,&decoder,&pcm,&capacity,&pending)==OGP_OK);
        memset(copy,0xa5,n);free(copy);at+=n;
    }
    finish(&c,&decoder,&pcm,&capacity,&pending,before,1);
}

static void chained_case(void)
{
    context c={.id="opus_vorbis_opus_chain",.chain=true};active=&c;ogp_reset(&c.playback,9);
    size_t before=esp_get_free_heap_size(),capacity=12288;uint8_t *pcm=malloc(capacity);assert(pcm);
    decoder_pending_input_t pending={0};esp_audio_simple_dec_handle_t decoder=NULL;
    const fixture *order[]={&fixtures[0],&fixtures[2],&fixtures[1]};
    size_t start=0;
    for(unsigned i=0;i<3;++i) {
        const fixture *f=order[i];configure_fixture(&c,f,false);
        size_t last=final_page(f);
        if(i==2) {
            assert(feed(&c,f->begin+start,(size_t)(f->end-f->begin)-start,false,&decoder,&pcm,&capacity,&pending)==OGP_OK);
            break;
        }
        assert(feed(&c,f->begin+start,last-start,false,&decoder,&pcm,&capacity,&pending)==OGP_OK);
        const fixture *next=order[i+1];size_t head=page_bytes(next->begin,(size_t)(next->end-next->begin));
        size_t tail=(size_t)(f->end-f->begin)-last,total=tail+head;
        uint8_t *cross=malloc(total);assert(cross);memcpy(cross,f->begin+last,tail);memcpy(cross+tail,next->begin,head);
        /* Complete next BOS shares the same caller buffer with old EOS. */
        assert(feed(&c,cross,total,false,&decoder,&pcm,&capacity,&pending)==OGP_OK);
        assert(decoder && c.opens==i+2 && c.closes==i+1 && c.current==next);
        memset(cross,0xa5,total);free(cross);start=head;
    }
    finish(&c,&decoder,&pcm,&capacity,&pending,before,3);
}

static void crc_case(void)
{
    const fixture *f=&fixtures[0];context c={.id="bad_crc_never_vendor"};active=&c;ogp_reset(&c.playback,9);configure_fixture(&c,f,false);
    size_t capacity=12288;uint8_t *pcm=malloc(capacity);assert(pcm);
    decoder_pending_input_t pending={0};esp_audio_simple_dec_handle_t decoder=NULL;
    size_t at=0,size=(size_t)(f->end-f->begin);
    while(at<size && oopt_le32(f->begin+at+18)<2) {
        size_t n=page_bytes(f->begin+at,size-at);assert(feed(&c,f->begin+at,n,false,&decoder,&pcm,&capacity,&pending)==OGP_OK);at+=n;
    }
    size_t n=page_bytes(f->begin+at,size-at);uint8_t *copy=malloc(n);assert(copy);memcpy(copy,f->begin+at,n);copy[22]^=1;
    unsigned calls=c.calls,outputs=c.outputs;
    assert(feed(&c,copy,n,false,&decoder,&pcm,&capacity,&pending)==OGP_CONTAINER && c.calls==calls && c.outputs==outputs && !c.raw_bytes);
    printf("OGP_GUARD id=bad_crc_never_vendor calls_before=%u calls_after=%u outputs=0 rejected=1\n",calls,c.calls);
    c.cleanup=true;if(decoder)esp_audio_simple_dec_close(decoder);
    decoder_pending_input_clear(&pending);free(pcm);free(copy);ogp_reset(&c.playback,10);
    assert(!c.live && heap_caps_check_integrity_all(true));active=NULL;++completed_cases;
}

static void worker(void *unused)
{
    (void)unused;assert(xPortGetCoreID()==1 && uxTaskPriorityGet(NULL)==3);
    assert(esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(0))==ESP_OK && esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(1))==ESP_OK);
    assert(psa_crypto_init()==PSA_SUCCESS && decoder_register_codecs()==ESP_AUDIO_ERR_OK);
    const unsigned chunks[]={0,4096,257,1};
    for(unsigned f=0;f<3;++f)for(unsigned i=0;i<4;++i)standard_case(&fixtures[f],chunks[i]);
    modified_case(&fixtures[0]);modified_case(&fixtures[1]);chained_case();crc_case();
    decoder_unregister_codecs();assert(heap_caps_check_integrity_all(true));
    printf("OGP_COMPLETE cases=%u heap_free=%u heap_min=%u stack_free=%u core=1 priority=3 heap_integrity=1\n",
           completed_cases,(unsigned)esp_get_free_heap_size(),(unsigned)esp_get_minimum_free_heap_size(),(unsigned)uxTaskGetStackHighWaterMark(NULL));
    assert(fflush(stdout)==0);esp_restart();
}
void app_main(void)
{
    assert(xPortGetCoreID()==0 && short_end-short_start==706319 && long_end-long_start==707097 && vorbis_end-vorbis_start==703584);
    printf("OGP_BEGIN sdk=6.0.2 coordinator=0 worker=1 priority=3 stack=16384 initial_capacity=12288 fixtures=3 hardware=0\n");
    assert(fflush(stdout)==0 && xTaskCreatePinnedToCore(worker,"oggplayback",16384,NULL,3,NULL,1)==pdPASS);
    while(true)vTaskDelay(portMAX_DELAY);
}
