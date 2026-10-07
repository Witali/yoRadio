// Real placement and ADTS adapter, with fault-injected SDK allocation calls.
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
static unsigned live, task, fail_size, mode, opens, closes, fail_open;
static int open_error;
static void *tls[2], *scratch, *sbr, *control;
static void *test_calloc(size_t n,size_t size) {
    if(size==fail_size){fail_size=0;return NULL;}
    void *p=calloc(n,size);if(p)++live;return p;
}
static void *test_realloc(void *p,size_t size) {
    int existed=p!=NULL;void *q=realloc(p,size);if(q && !existed)++live;return q;
}
static void test_free(void *p){if(p){assert(live);--live;}free(p);}
void *pvTaskGetThreadLocalStoragePointer(void *t,int slot){(void)t;assert(slot==1);return tls[task];}
void vTaskSetThreadLocalStoragePointer(void *t,int slot,void *p){(void)t;assert(slot==1);tls[task]=p;}
void *__real_media_lib_module_calloc(const char *m,size_t n,size_t size){(void)m;return test_calloc(n,size);}
#define calloc test_calloc
#define realloc test_realloc
#define free test_free
#include "aac_scratch_reserve.c"
#include "native_aac_decoder.c"
#undef calloc
#undef realloc
#undef free

esp_audio_err_t esp_audio_simple_dec_open(esp_audio_simple_dec_cfg_t *cfg,void **p){
    if(fail_open){--fail_open;return open_error;}
    assert(cfg->use_frame_dec);
    scratch=__wrap_media_lib_module_calloc("AAC",1,12288);
    if(!scratch)return ESP_AUDIO_ERR_MEM_LACK;
    for(unsigned i=0;i<12288;++i)assert(!((uint8_t*)scratch)[i]);
    *p=(void*)1;++opens;return ESP_AUDIO_ERR_OK;
}
void esp_audio_simple_dec_close(void *p){
    assert(p);test_free(scratch);test_free(sbr);test_free(control);
    scratch=sbr=control=NULL;++closes;
}
esp_audio_err_t esp_audio_simple_dec_process(void *p,esp_audio_simple_dec_raw_t *raw,esp_audio_simple_dec_out_t *out){
    assert(p && raw->len==12 && tls[task]);
    if(mode && !sbr){
        sbr=__wrap_media_lib_module_calloc("AAC",1,55128);
        if(sbr)control=__wrap_media_lib_module_calloc("AAC",1,1180);
    }
    out->decoded_size=mode && sbr && control?8192:4096;raw->consumed=raw->len;
    return ESP_AUDIO_ERR_OK; // Mimic vendor's misleading success on SBR OOM.
}
esp_audio_err_t esp_audio_simple_dec_get_info(void *p,esp_audio_simple_dec_info_t *i){(void)p;(void)i;return 0;}
static void run(unsigned test){
    mode=test!=0;
    fail_size=test==2?12288:0;
    native_aac_decoder_t *d=native_aac_decoder_create();assert(d);
    assert(!!d->scratch.pending==(test!=2));
    fail_size=test==3?55128:test==4?1180:0;
    fail_open=test==5 || test==6;
    open_error=test==5?ESP_AUDIO_ERR_MEM_LACK:ESP_AUDIO_ERR_FAIL;
    uint8_t input[12]={0xff,0xf1,0x50,0x80,1,0x9f,0xfc},pcm[8192];
    esp_audio_simple_dec_raw_t raw={.buffer=input,.len=12};
    esp_audio_simple_dec_out_t out={.buffer=pcm,.len=sizeof(pcm)};
    int result=native_aac_decoder_process(d,&raw,&out);
    assert(!tls[task] && !d->scratch.pending && raw.consumed==12);
    if(test==3 || test==4)assert(result==ESP_AUDIO_ERR_MEM_LACK && !out.decoded_size);
    else {
        assert(result==0 && out.decoded_size==(mode?8192:4096));
        // Different ADTS sample rate: close, reserve again, and reopen.
        input[2]=0x4c;raw.consumed=0;
        assert(native_aac_decoder_process(d,&raw,&out)==0);
        assert(!tls[task] && !d->scratch.pending && raw.consumed==12);
    }
    native_aac_decoder_destroy(d);assert(!live && opens==closes);
}
int main(void){
    for(unsigned i=0;i<7;++i)run(i);
    native_aac_decoder_t *d=native_aac_decoder_create();assert(d && d->scratch.pending);
    void *reserved=d->scratch.pending;
    aac_scratch_reserve_enter(&d->scratch);
    // Other tasks and differently shaped allocations cannot claim the owner.
    task=1;void *p=__wrap_media_lib_module_calloc("other",1,12288);
    assert(p!=reserved);test_free(p);task=0;
    p=__wrap_media_lib_module_calloc("other",2,6144);
    assert(p!=reserved && d->scratch.pending==reserved);test_free(p);
    p=__wrap_media_lib_module_calloc("AAC",1,12288);
    assert(p==reserved && !d->scratch.pending);aac_scratch_reserve_leave();test_free(p);
    native_aac_decoder_destroy(d);assert(!live);
    d=native_aac_decoder_create();native_aac_decoder_destroy(d);assert(!live);
    puts("PASS: scratch transfer, task isolation, zeroing, early OOM, open retries, SBR OOM, reopen and cleanup");
}
