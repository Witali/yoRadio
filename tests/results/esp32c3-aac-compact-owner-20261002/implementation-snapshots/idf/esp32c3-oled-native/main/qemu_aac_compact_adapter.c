// Runs the production TLS-scoped owner against the real RV32 SDK, with heap
// poisoning enabled in the test image. Does not add samples to the output WAV.
#include "native_aac_decoder.h"
#include "aac_compact_owner.h"
#include "aac_sbr_abi.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <assert.h>
#include <stdlib.h>
#include <string.h>

void *__wrap_media_lib_module_calloc(const char *,size_t,size_t);
void __wrap_media_lib_free(void *);
void aac_compact_owner_test_fail_next(size_t);
void aac_compact_owner_test_assert_idle(void);
esp_audio_err_t native_aac_decoder_reset_for_test(native_aac_decoder_t *);
static const char *TAG="compact_adapter";
static TaskHandle_t parent;
static void independent_task(void *unused) {
    (void)unused;
    // No inherited owner: an unrelated task must receive the original size.
    void *ordinary=__wrap_media_lib_module_calloc("AAC",1,sizeof(aac_sbr_owner_abi_t));
    assert(ordinary && heap_caps_get_allocated_size(ordinary)>=sizeof(aac_sbr_owner_abi_t));
    __wrap_media_lib_free(ordinary);
    aac_compact_owner_t other={0};aac_compact_owner_enter(&other);
    void *compact=__wrap_media_lib_module_calloc("AAC",1,sizeof(aac_sbr_owner_abi_t));
    assert(compact && other.owner==compact);
    __wrap_media_lib_free(compact);assert(!other.owner);aac_compact_owner_leave();
    xTaskNotifyGive(parent);vTaskDelete(NULL);
}

extern const uint8_t hev2_start[] asm("_binary_hev2_44100_stereo_aac_start");
extern const uint8_t hev2_end[] asm("_binary_hev2_44100_stereo_aac_end");
static unsigned decode(native_aac_decoder_t *decoder,uint8_t *pcm,bool expect_failure) {
    unsigned samples=0;
    for(const uint8_t *p=hev2_start;p<hev2_end;) {
        size_t count=hev2_end-p;if(count>193)count=193;
        esp_audio_simple_dec_raw_t raw={.buffer=(uint8_t *)p,.len=count};
        esp_audio_simple_dec_out_t out={.buffer=pcm,.len=8192};
        esp_audio_err_t result=native_aac_decoder_process(decoder,&raw,&out);
        if(result!=ESP_AUDIO_ERR_OK) {
            assert(expect_failure && result==ESP_AUDIO_ERR_MEM_LACK && !out.decoded_size);
            return 0;
        }
        assert(raw.consumed || out.decoded_size);p+=raw.consumed;
        if(out.decoded_size) {
            assert(!expect_failure);
            esp_audio_simple_dec_info_t info={0};
            assert(native_aac_decoder_get_info(decoder,&info)==ESP_AUDIO_ERR_OK);
            assert(info.sample_rate==44100 && info.channel==2 && info.bits_per_sample==16);
            samples+=out.decoded_size/2;
        }
    }
    assert(!expect_failure && samples);return samples;
}

void qemu_aac_compact_adapter_test(void) {
    aac_compact_owner_test_assert_idle();
    aac_compact_owner_t state={0};aac_compact_owner_enter(&state);
    void *owner=__wrap_media_lib_module_calloc("AAC",1,sizeof(aac_sbr_owner_abi_t));
    assert(owner && state.owner==owner);
    for(size_t i=0;i<sizeof(aac_sbr_compact_relocated_owner_abi_t);++i)assert(!((uint8_t *)owner)[i]);
    parent=xTaskGetCurrentTaskHandle();
    assert(xTaskCreate(independent_task,"aac_owner",3072,NULL,5,NULL)==pdPASS);
    assert(ulTaskNotifyTake(pdTRUE,pdMS_TO_TICKS(5000))==1);
    assert(state.owner==owner);__wrap_media_lib_free(owner);assert(!state.owner);
    aac_compact_owner_leave();vTaskDelay(2);aac_compact_owner_test_assert_idle();
    uint8_t *pcm=malloc(8192);assert(pcm);
    for(unsigned failure=0;failure<2;++failure) {
        native_aac_decoder_t *decoder=native_aac_decoder_create();assert(decoder);
        aac_compact_owner_test_fail_next(failure?sizeof(aac_sbr_control_abi_t):sizeof(aac_sbr_owner_abi_t));
        assert(!decode(decoder,pcm,true));
        native_aac_decoder_destroy(decoder);aac_compact_owner_test_assert_idle();
        assert(heap_caps_check_integrity_all(true));
    }
    native_aac_decoder_t *decoder=native_aac_decoder_create();assert(decoder);
    unsigned samples=decode(decoder,pcm,false);
    for(unsigned i=0;i<2;++i) {
        assert(native_aac_decoder_reset_for_test(decoder)==ESP_AUDIO_ERR_OK);
        assert(decode(decoder,pcm,false)==samples);
        assert(heap_caps_check_integrity_all(true));
    }
    native_aac_decoder_destroy(decoder);free(pcm);aac_compact_owner_test_assert_idle();
    ESP_LOGI(TAG,"AACCOMPACT_ADAPTER_PASS failures=2 tasks=2 resets=2 samples=%u cleanup=complete heap=valid",samples);
}
