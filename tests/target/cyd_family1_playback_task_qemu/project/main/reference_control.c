/* Pure direct-public reference driver. No production map/frame/trim/mix helper. */
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "esp_heap_caps.h"
#include "esp_system.h"
#include "probe.h"
#include "reference_contract.h"
#include "asset_size.h"

af_observation af_obs;
f1_reference_t f1_references[F1_REFERENCE_COUNT];
EventGroupHandle_t f1_reference_events;
static unsigned live;
static void *handles[8];
static size_t dump_offset;
extern esp_audio_err_t __real_esp_opus_dec_open(void *,uint32_t,void **);
extern esp_audio_err_t __real_esp_opus_dec_decode(void *,esp_audio_dec_in_raw_t *,esp_audio_dec_out_frame_t *,esp_audio_dec_info_t *);
extern esp_audio_err_t __real_esp_opus_dec_close(void *);

static void ref_owner(void) {assert(xPortGetCoreID()==1 && uxTaskPriorityGet(NULL)==3);}
void af_begin(unsigned kind,unsigned id,unsigned schedule) {
    ref_owner();assert(!live);memset(&af_obs,0,sizeof(af_obs));
    af_obs.kind=kind;af_obs.id=id;af_obs.schedule=schedule;dump_offset=0;
}
esp_audio_err_t af_open(void *cfg,uint32_t size,void **handle) {
    ref_owner();esp_audio_err_t result=__real_esp_opus_dec_open(cfg,size,handle);
    printf("CYD_F1_REFERENCE_OPEN index=%u ordinal=%u result=%d handle=%u\n",af_obs.id,af_obs.opens++,result,(unsigned)(handle && *handle));
    if(result==ESP_AUDIO_ERR_OK && handle && *handle) {
        unsigned slot=0;while(slot<8 && handles[slot])++slot;assert(slot<8);handles[slot]=*handle;++live;
    }
    return result;
}
esp_audio_err_t af_decode(void *handle,esp_audio_dec_in_raw_t *raw,esp_audio_dec_out_frame_t *frame,esp_audio_dec_info_t *info) {
    ref_owner();uint32_t bytes=raw->len,capacity=frame->len;
    esp_audio_err_t result=__real_esp_opus_dec_decode(handle,raw,frame,info);
    ++af_obs.calls;af_obs.consumed+=raw->consumed;af_obs.decoded+=frame->decoded_size;
    printf("CYD_F1_REFERENCE_CALL index=%u call=%u input=%u consumed=%u capacity=%u decoded=%u needed=%u result=%d\n",
        af_obs.id,af_obs.calls,(unsigned)bytes,(unsigned)raw->consumed,(unsigned)capacity,(unsigned)frame->decoded_size,(unsigned)frame->needed_size,result);
    return result;
}
esp_audio_err_t af_close(void *handle) {
    ref_owner();esp_audio_err_t result=__real_esp_opus_dec_close(handle);++af_obs.closes;
    if(result==ESP_AUDIO_ERR_OK) {unsigned slot=0;while(slot<8 && handles[slot]!=handle)++slot;assert(slot<8 && live);handles[slot]=NULL;--live;}
    printf("CYD_F1_REFERENCE_CLOSE index=%u ordinal=%u result=%d live=%u\n",af_obs.id,af_obs.closes,result,live);
    return result;
}
unsigned af_live(void) {return live;}
void af_hash_begin(af_output *out) {
    memset(out,0,sizeof(*out));out->hash=psa_hash_operation_init();out->lifetime=true;
    assert(psa_hash_setup(&out->hash,PSA_ALG_SHA_256)==PSA_SUCCESS);
}
void af_hash_add(af_output *out,const uint8_t *pcm,size_t bytes) {
    assert(pcm && bytes && psa_hash_update(&out->hash,pcm,bytes)==PSA_SUCCESS);
    out->bytes+=bytes;++out->chunks;if(bytes>out->max_chunk)out->max_chunk=(unsigned)bytes;
    static const char digits[]="0123456789abcdef";
    char hex[513];
    for(size_t at=0;at<bytes;) {
        size_t n=bytes-at;if(n>256)n=256;
        for(size_t i=0;i<n;++i){hex[2*i]=digits[pcm[at+i]>>4];hex[2*i+1]=digits[pcm[at+i]&15];}hex[2*n]=0;
        printf("CYD_F1_REFERENCE_PCM index=%u offset=%u bytes=%u hex=%s\n",af_obs.id,(unsigned)dump_offset,(unsigned)n,hex);
        dump_offset+=n;at+=n;
    }
    vTaskDelay(1); /* Observation work leaves the real idle watchdog runnable. */
}
void af_hash_finish(af_output *out,char hex[65]) {
    uint8_t digest[32];size_t used=0;assert(psa_hash_finish(&out->hash,digest,sizeof(digest),&used)==PSA_SUCCESS && used==32);
    for(unsigned i=0;i<32;++i)snprintf(hex+2*i,3,"%02x",digest[i]);
}
void f1_public_reference_worker(void *unused) {
    (void)unused;ref_owner();assert(f1_reference_events && (size_t)(af_blob_end-af_blob)==F1_ASSET_BYTES);
    for(unsigned index=0;index<F1_REFERENCE_COUNT;++index) {
        const af_fixture *entry=(const af_fixture *)(af_blob+16+80u*index);
        assert(entry->id==index);af_begin(0,index,0);af_output output;af_hash_begin(&output);
        unsigned before=esp_get_free_heap_size();int driver=0;bool success=af_reference(entry,&output,&driver);
        f1_reference_t *result=f1_references+index;af_hash_finish(&output,result->sha);result->bytes=(size_t)output.bytes;
        result->complete=success && !live && output.bytes==(uint64_t)entry->logical*entry->channels*2u && dump_offset==output.bytes;
        printf("CYD_F1_REFERENCE_CASE index=%u complete=%u driver=%d channels=%u frames=%u pcm_bytes=%u sha256=%s opens=%u closes=%u calls=%u live=%u before=%u after=%u heap_min=%u largest_internal=%u stack_free=%u core=1 priority=3 private_helpers=0\n",
            index,(unsigned)result->complete,driver,(unsigned)entry->channels,(unsigned)entry->logical,(unsigned)output.bytes,result->sha,
            af_obs.opens,af_obs.closes,af_obs.calls,live,before,(unsigned)esp_get_free_heap_size(),(unsigned)esp_get_minimum_free_heap_size(),
            (unsigned)heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT),(unsigned)uxTaskGetStackHighWaterMark(NULL));
        assert(result->complete && heap_caps_check_integrity_all(true));
    }
    printf("CYD_F1_REFERENCE_COMPLETE cases=13 live=%u private_helpers=0 production_tasks=0 heap_integrity=%u\n",live,(unsigned)heap_caps_check_integrity_all(true));
    assert(fflush(stdout)==0);xEventGroupSetBits(f1_reference_events,F1_REFERENCE_DONE);vTaskDelete(NULL);
}
