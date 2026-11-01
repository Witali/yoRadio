// Continuous public-handle integration oracle, separate from application tasks.
// This owns no private layouts, reset hooks or production parser/pending helper.
#include <algorithm>
#include <cassert>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include "esp_audio_simple_dec.h"
#include "esp_heap_caps.h"
#include "esp_system.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "psa/crypto.h"
extern "C" {
#include "aac_public_config.h"
#include "decoder_registration.h"
}
#include "contract_types.h"
#include "reference.h"

reference_t aac_references[AAC_REFERENCE_COUNT];
EventGroupHandle_t aac_reference_events;
extern "C" esp_audio_err_t __real_esp_audio_simple_dec_open(esp_audio_simple_dec_cfg_t *,esp_audio_simple_dec_handle_t *);
extern "C" esp_audio_err_t __real_esp_audio_simple_dec_process(esp_audio_simple_dec_handle_t,esp_audio_simple_dec_raw_t *,esp_audio_simple_dec_out_t *);
extern "C" esp_audio_err_t __real_esp_audio_simple_dec_get_info(esp_audio_simple_dec_handle_t,esp_audio_simple_dec_info_t *);
extern "C" void __real_esp_audio_simple_dec_close(esp_audio_simple_dec_handle_t);

static void verify(bool value,const char *reason) {
    if (!value) {
        printf("CYD_AAC_TASK_FAILURE reference=%s\n",reason);fflush(stdout);assert(value);
    }
}
static void finish(psa_hash_operation_t &hash,char hex[65]) {
    uint8_t digest[32];size_t bytes=0;
    verify(psa_hash_finish(&hash,digest,sizeof(digest),&bytes)==PSA_SUCCESS && bytes==32,"complete_sha");
    for (unsigned i=0;i<32;++i) snprintf(hex+2*i,3,"%02x",(unsigned)digest[i]);
}
static void observe(unsigned index,const fixture_t &fixture) {
    reference_t &result=aac_references[index];
    verify(!result.measured,"one_reference_measurement");
    size_t encoded_bytes=0;
    for (unsigned i=0;i<fixture.part_count;++i) encoded_bytes+=entries[fixture.parts[i]].bytes;
    uint8_t *encoded=(uint8_t *)malloc(encoded_bytes);
    uint32_t capacity=12288;
    uint8_t *pcm=(uint8_t *)malloc(capacity);
    verify(encoded && pcm,"public_reference_storage");
    size_t at=0;
    for (unsigned i=0;i<fixture.part_count;++i) {
        const entry_t &entry=entries[fixture.parts[i]];
        memcpy(encoded+at,entry.data,entry.bytes);at+=entry.bytes;
    }
    esp_aac_dec_cfg_t aac=native_aac_public_config();
    verify(aac.aac_plus_enable && !aac.no_adts_header,"public_plus_configuration");
    esp_audio_simple_dec_cfg_t config={};
    config.dec_type=ESP_AUDIO_SIMPLE_DEC_TYPE_AAC;config.dec_cfg=&aac;config.cfg_size=sizeof(aac);config.use_frame_dec=false;
    esp_audio_simple_dec_handle_t handle=nullptr;
    result.result=__real_esp_audio_simple_dec_open(&config,&handle);
    verify(result.result==ESP_AUDIO_ERR_OK && handle,"genuine_public_open");
    psa_hash_operation_t total=PSA_HASH_OPERATION_INIT,run=PSA_HASH_OPERATION_INIT;
    verify(psa_hash_setup(&total,PSA_ALG_SHA_256)==PSA_SUCCESS,"start_total");
    esp_audio_simple_dec_raw_t raw={};raw.buffer=encoded;raw.len=encoded_bytes;
    while (true) {
        const uint32_t offered=raw.len;
        esp_audio_simple_dec_out_t frame={};frame.buffer=pcm;frame.len=capacity;raw.consumed=0;
        result.result=__real_esp_audio_simple_dec_process(handle,&raw,&frame);++result.calls;
        verify(raw.consumed<=offered && frame.decoded_size<=capacity,"public_argument_bounds");
        raw.buffer+=raw.consumed;raw.len-=raw.consumed;result.input+=raw.consumed;
        if ((result.calls&31U)==0) vTaskDelay(1);
        if (result.result==ESP_AUDIO_ERR_BUFF_NOT_ENOUGH) {
            verify(!frame.decoded_size && frame.needed_size>capacity,"genuine_reference_buffer_growth");
            uint8_t *larger=(uint8_t *)realloc(pcm,frame.needed_size);verify(larger,"reference_growth_allocation");
            pcm=larger;capacity=frame.needed_size;++result.resizes;continue;
        }
        if (result.result!=ESP_AUDIO_ERR_OK) break;
        if (frame.decoded_size) {
            esp_audio_simple_dec_info_t info={};
            verify(__real_esp_audio_simple_dec_get_info(handle,&info)==ESP_AUDIO_ERR_OK,"genuine_public_metadata");
            verify(info.sample_rate && info.channel && info.channel<=2 && info.bits_per_sample==16 &&
                   !(frame.decoded_size%(info.channel*2)),"public_reference_PCM_geometry");
            pcm_run_t *current=result.run_count?&result.runs[result.run_count-1]:nullptr;
            if (!current || current->rate!=info.sample_rate || current->channels!=info.channel || current->bits!=info.bits_per_sample) {
                if (current) finish(run,current->sha);
                verify(result.run_count<AAC_MAX_RUNS,"bounded_public_metadata_runs");
                current=&result.runs[result.run_count++];current->rate=info.sample_rate;current->channels=info.channel;current->bits=info.bits_per_sample;
                verify(psa_hash_setup(&run,PSA_ALG_SHA_256)==PSA_SUCCESS,"start_public_metadata_run");
            }
            verify(psa_hash_update(&total,pcm,frame.decoded_size)==PSA_SUCCESS &&
                   psa_hash_update(&run,pcm,frame.decoded_size)==PSA_SUCCESS,"all_reference_PCM_bytes");
            current->bytes+=frame.decoded_size;result.pcm_bytes+=frame.decoded_size;++result.frames;
        }
        if (!raw.consumed && !frame.decoded_size) {
            if (raw.eos) {
                result.drained=!raw.len;result.success=result.drained && result.input==encoded_bytes;
                break;
            }
            // All original bytes were offered as one view. Mark only the
            // genuinely final remaining span EOS, without private cache repair.
            raw.eos=true;
        } else if (!raw.len) raw.eos=true;
    }
    finish(total,result.sha);
    if (result.run_count) finish(run,result.runs[result.run_count-1].sha);
    __real_esp_audio_simple_dec_close(handle);free(encoded);free(pcm);
    result.measured=true;
    if (index<AAC_BASE_COUNT) {
        const entry_t &entry=entries[index];
        verify(result.success && result.run_count==1 && result.pcm_bytes==entry.pcm_bytes &&
               !strcmp(result.sha,entry.pcm_sha) && result.runs[0].rate==entry.rate &&
               result.runs[0].channels==entry.channels && result.runs[0].bits==entry.bits,
               "whole_committed_same_vendor_contract");
    }
    printf("CYD_AAC_REFERENCE_CASE index=%u name=%s observed_only=%u success=%u result=%d drained=%u input=%u pcm_bytes=%u sha256=%s calls=%u frames=%u runs=%u resizes=%u core=1 priority=3\n",
           index,fixture.name,(unsigned)fixture.observational,(unsigned)result.success,result.result,(unsigned)result.drained,
           (unsigned)result.input,(unsigned)result.pcm_bytes,result.sha,result.calls,result.frames,result.run_count,result.resizes);
    for (unsigned i=0;i<result.run_count;++i) {
        const pcm_run_t &part=result.runs[i];
        printf("CYD_AAC_REFERENCE_RUN index=%u run=%u rate=%u channels=%u bits=%u pcm_bytes=%u sha256=%s\n",
               index,i,(unsigned)part.rate,(unsigned)part.channels,(unsigned)part.bits,(unsigned)part.bytes,part.sha);
    }
    verify(heap_caps_check_integrity_all(true),"reference_heap_integrity");fflush(stdout);vTaskDelay(1);
}

void aac_public_reference_worker(void *) {
    verify(xPortGetCoreID()==1 && uxTaskPriorityGet(nullptr)==3,"reference_worker_owner");
    const size_t before=esp_get_free_heap_size();
    verify(decoder_register_codecs()==ESP_AUDIO_ERR_OK,"public_registry_ownership");
    for (unsigned i=0;i<AAC_BASE_COUNT;++i) observe(i,base_fixtures[i]);
    for (unsigned i=0;i<AAC_OBSERVATION_COUNT;++i) observe(AAC_BASE_COUNT+i,observation_fixtures[i]);
    decoder_unregister_codecs();
    const size_t after=esp_get_free_heap_size();
    printf("CYD_AAC_REFERENCE_COMPLETE cases=10 registry_before=%u heap_free=%u retained=%d stack_free=%u heap_integrity=1 production_tasks=0 private_abi=0 reset_hooks=0\n",
           (unsigned)before,(unsigned)after,(int)before-(int)after,(unsigned)uxTaskGetStackHighWaterMark(nullptr));
    fflush(stdout);xEventGroupSetBits(aac_reference_events,AAC_REFERENCE_DONE);vTaskDelete(nullptr);
}
