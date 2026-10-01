// Real adapter/reservation code; the SDK mock intentionally returns core PCM
// after SBR OOM to verify that the adapter rejects that misleading success.
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
static unsigned live,fail_size,mode,opens,closes,fail_open;
static int open_error;
static void *tls,*sbr,*control;
static void *test_calloc(size_t n,size_t size) {
    if(size==fail_size){fail_size=0;return NULL;}
    void *p=calloc(n,size);if(p)++live;return p;
}
static void *test_realloc(void *p,size_t size) {
    int existed=p!=NULL;void *q=realloc(p,size);if(q && !existed)++live;return q;
}
static void test_free(void *p) {if(p){assert(live);--live;}free(p);}
void *pvTaskGetThreadLocalStoragePointer(void *t,int slot){(void)t;assert(slot==1);return tls;}
void vTaskSetThreadLocalStoragePointer(void *t,int slot,void *p){(void)t;assert(slot==1);tls=p;}
void *__real_media_lib_module_calloc(const char *m,size_t n,size_t size){(void)m;return test_calloc(n,size);}
#define calloc test_calloc
#define realloc test_realloc
#define free test_free
#include "aac_sbr_reserve.c"
#include "native_aac_decoder.c"
#undef calloc
#undef realloc
#undef free

esp_audio_err_t esp_audio_simple_dec_open(esp_audio_simple_dec_cfg_t *cfg,void **p) {
    if(fail_open){--fail_open;return open_error;}
    assert(cfg->use_frame_dec);*p=(void*)1;++opens;return ESP_AUDIO_ERR_OK;
}
void esp_audio_simple_dec_close(void *p){assert(p);test_free(sbr);test_free(control);sbr=control=NULL;++closes;}
esp_audio_err_t esp_audio_simple_dec_process(void *p,esp_audio_simple_dec_raw_t *raw,esp_audio_simple_dec_out_t *out){
    assert(p && raw->len==12 && tls);
    if(mode){sbr=__wrap_media_lib_module_calloc("AAC",1,55128);if(sbr)control=__wrap_media_lib_module_calloc("AAC",1,1180);}
    out->decoded_size=mode && sbr && control ? 8192:4096;raw->consumed=raw->len;
    return ESP_AUDIO_ERR_OK;
}
esp_audio_err_t esp_audio_simple_dec_get_info(void *p,esp_audio_simple_dec_info_t *info){(void)p;(void)info;return ESP_AUDIO_ERR_OK;}
static void run(unsigned test){
    mode=test!=0 && test<4;
    // Fail both the early reservation and the later native request in case 2.
    fail_size=test==2?55128:0;
    native_aac_decoder_t *d=native_aac_decoder_create();assert(d);
    assert((d->reserve.pending!=NULL)==(test!=2));
    fail_size=test==2?55128:test==3?1180:0;
    fail_open=test>=4;
    open_error=test==4?ESP_AUDIO_ERR_MEM_LACK:ESP_AUDIO_ERR_FAIL;
    uint8_t input[12]={0xff,0xf1,0x50,0x80,1,0x9f,0xfc},pcm[8192];
    esp_audio_simple_dec_raw_t raw={.buffer=input,.len=12};
    esp_audio_simple_dec_out_t out={.buffer=pcm,.len=sizeof(pcm)};
    esp_audio_err_t result=native_aac_decoder_process(d,&raw,&out);
    assert(!tls && raw.consumed==12 && !d->reserve.pending);
    if(test==2 || test==3){assert(result==ESP_AUDIO_ERR_MEM_LACK && !out.decoded_size);}
    else {assert(result==ESP_AUDIO_ERR_OK && out.decoded_size==(mode?8192:4096));}
    native_aac_decoder_destroy(d);assert(!live && opens==closes);
}
int main(void){
    for(unsigned i=0;i<6;++i)run(i);
    native_aac_decoder_t *d=native_aac_decoder_create();assert(d && d->reserve.pending);
    native_aac_decoder_destroy(d);assert(!live); // Stop before any input.
    puts("PASS: early SBR ownership, LC release, full HE, no core-only success on SBR/control OOM, close cleanup");
}
