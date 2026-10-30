// Public Ogg/Opus resize observations. No private codec state or radio hardware.
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
#include "esp_audio_simple_dec.h"
#include "psa/crypto.h"
#include "decoder_registration.h"

#ifdef NDEBUG
#error "The resize probe requires assertions"
#endif
#if !CONFIG_IDF_TARGET_ESP32
#error "The resize probe requires ESP32 LX6"
#endif
extern const uint8_t fixture_start[] asm("_binary_fixture_ogg_start");
extern const uint8_t fixture_end[] asm("_binary_fixture_ogg_end");
static uint8_t reference_sha[32];
static uint64_t reference_bytes;

// Nonzero outcomes are observations, never silently converted into qualification.
enum { DRAINED=0, DECODE_ERROR=1, INVALID_SIZE=2, NO_PROGRESS=3,
       INVALID_RESIZE=4, ALLOCATION_FAILED=5, CALL_BOUND=6 };
static bool decode(unsigned strategy) {
    const char *name=strategy==0?"baseline":strategy==1?"retry_unchanged":"honor_consumed";
    assert(heap_caps_check_integrity_all(true));
    size_t before=esp_get_free_heap_size();
    size_t capacity=strategy?12288:24576;
    uint8_t *pcm=malloc(capacity);
    assert(pcm);
    esp_audio_simple_dec_cfg_t config={.dec_type=ESP_AUDIO_SIMPLE_DEC_TYPE_OGG,.use_frame_dec=false};
    esp_audio_simple_dec_handle_t decoder=NULL;
    assert(esp_audio_simple_dec_open(&config,&decoder)==ESP_AUDIO_ERR_OK && decoder);
    psa_hash_operation_t hash=PSA_HASH_OPERATION_INIT;
    assert(psa_hash_setup(&hash,PSA_ALG_SHA_256)==PSA_SUCCESS);
    esp_audio_simple_dec_raw_t raw={.buffer=(uint8_t *)fixture_start,
        .len=(uint32_t)(fixture_end-fixture_start),.eos=true};
    uint64_t pcm_bytes=0;
    unsigned calls=0,frames=0,resizes=0,error_consumed=0,consumed=0;
    unsigned outcome=CALL_BOUND;
    int last_result=ESP_AUDIO_ERR_OK;
    while (calls<4096) {
        esp_audio_simple_dec_out_t out={.buffer=pcm,.len=capacity};
        uint32_t before_len=raw.len;
        raw.consumed=0;
        esp_audio_err_t result=esp_audio_simple_dec_process(decoder,&raw,&out);
        last_result=result; ++calls;
        if (!(calls&31U)) vTaskDelay(1);
        if (result==ESP_AUDIO_ERR_BUFF_NOT_ENOUGH) {
            printf("EOR_RESIZE strategy=%s call=%u len_before=%u raw_len=%u consumed=%u decoded_size=%u needed_size=%u capacity=%u result=%d advance_on_error=%u\n",
                   name,calls,(unsigned)before_len,(unsigned)raw.len,(unsigned)raw.consumed,
                   (unsigned)out.decoded_size,(unsigned)out.needed_size,(unsigned)capacity,(int)result,(unsigned)(strategy==2));
            assert(fflush(stdout)==0);
            ++resizes; error_consumed+=raw.consumed;
            if (raw.len!=before_len || raw.consumed>raw.len) {outcome=INVALID_SIZE; break;}
            if (out.needed_size<=capacity || out.needed_size>24576) {outcome=INVALID_RESIZE; break;}
            uint8_t *larger=realloc(pcm,out.needed_size);
            if (!larger) {outcome=ALLOCATION_FAILED; break;}
            pcm=larger; capacity=out.needed_size;
            if (strategy==2) {
                if (raw.consumed) raw.buffer+=raw.consumed;
                raw.len-=raw.consumed; consumed+=raw.consumed;
            }
            continue;
        }
        if (result!=ESP_AUDIO_ERR_OK) {
            printf("EOR_ERROR strategy=%s call=%u raw_len=%u consumed=%u decoded_size=%u needed_size=%u capacity=%u result=%d\n",
                   name,calls,(unsigned)raw.len,(unsigned)raw.consumed,(unsigned)out.decoded_size,
                   (unsigned)out.needed_size,(unsigned)capacity,(int)result);
            assert(fflush(stdout)==0);
            outcome=DECODE_ERROR; break;
        }
        if (raw.len!=before_len || raw.consumed>raw.len || out.decoded_size>capacity) {outcome=INVALID_SIZE; break;}
        if (raw.consumed) raw.buffer+=raw.consumed;
        raw.len-=raw.consumed; consumed+=raw.consumed;
        if (out.decoded_size) {
            esp_audio_simple_dec_info_t info={0};
            assert(esp_audio_simple_dec_get_info(decoder,&info)==ESP_AUDIO_ERR_OK);
            assert(info.sample_rate==48000 && info.channel==2 && info.bits_per_sample==16 && out.decoded_size%4==0);
            assert(psa_hash_update(&hash,out.buffer,out.decoded_size)==PSA_SUCCESS);
            pcm_bytes+=out.decoded_size; ++frames;
        }
        if (!raw.consumed && !out.decoded_size) {
            outcome=raw.len?NO_PROGRESS:DRAINED;
            break;
        }
    }
    uint8_t digest[32]; char hex[65]; size_t digest_size=0;
    assert(psa_hash_finish(&hash,digest,sizeof(digest),&digest_size)==PSA_SUCCESS && digest_size==sizeof(digest));
    assert(psa_hash_abort(&hash)==PSA_SUCCESS);
    for (unsigned i=0;i<sizeof(digest);++i) snprintf(hex+2*i,3,"%02x",digest[i]);
    esp_audio_simple_dec_close(decoder);
    free(pcm);
    assert(heap_caps_check_integrity_all(true));
    size_t after=esp_get_free_heap_size();
    bool complete=outcome==DRAINED && !raw.len && consumed==(uint32_t)(fixture_end-fixture_start);
    if (!strategy) { assert(complete && pcm_bytes && frames && !resizes); reference_bytes=pcm_bytes; memcpy(reference_sha,digest,sizeof(digest)); }
    bool match=complete && pcm_bytes==reference_bytes && !memcmp(reference_sha,digest,sizeof(digest));
    printf("EOR_CASE strategy=%s complete=%u outcome=%u input=%u remaining=%u calls=%u frames=%u pcm=%" PRIu64
           " sha256=%s resizes=%u error_consumed=%u final_capacity=%u match=%u before=%u after=%u stack_free=%u core=%d priority=%u last_result=%d\n",
           name,(unsigned)complete,outcome,consumed,(unsigned)raw.len,calls,frames,pcm_bytes,hex,resizes,error_consumed,
           (unsigned)capacity,(unsigned)match,(unsigned)before,(unsigned)after,(unsigned)uxTaskGetStackHighWaterMark(NULL),
           xPortGetCoreID(),(unsigned)uxTaskPriorityGet(NULL),last_result);
    assert(fflush(stdout)==0);
    assert(xPortGetCoreID()==1 && uxTaskPriorityGet(NULL)==3);
    if (strategy) assert(before==after);
    vTaskDelay(1);
    return match;
}
static void worker(void *unused) {
    (void)unused;
    assert(esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(0))==ESP_OK);
    assert(esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(1))==ESP_OK);
    assert(psa_crypto_init()==PSA_SUCCESS);
    size_t before=esp_get_free_heap_size();
    assert(decoder_register_codecs()==ESP_AUDIO_ERR_OK);
    assert(decode(0));
    bool unchanged=decode(1),honor=decode(2);
    decoder_unregister_codecs();
    assert(heap_caps_check_integrity_all(true));
    size_t after=esp_get_free_heap_size();
    printf("EOR_COMPLETE target=esp32 cases=3 core=1 retry_unchanged_qualified=%u honor_consumed_qualified=%u registry_before=%u heap_free=%u retained=%d heap_min=%u stack_free=%u heap_integrity=1\n",
           (unsigned)unchanged,(unsigned)honor,(unsigned)before,(unsigned)after,(int)before-(int)after,
           (unsigned)esp_get_minimum_free_heap_size(),(unsigned)uxTaskGetStackHighWaterMark(NULL));
    assert(fflush(stdout)==0);
    esp_restart();
}
void app_main(void) {
    assert(xPortGetCoreID()==0 && fixture_end-fixture_start==707097);
    printf("EOR_BEGIN target=esp32 coordinator=0 worker=1 stack=16384 priority=3 initial_capacity=12288 baseline_capacity=24576 fixture=707097\n");
    assert(fflush(stdout)==0);
    assert(xTaskCreatePinnedToCore(worker,"opusresize",16384,NULL,3,NULL,1)==pdPASS);
    while (true) vTaskDelay(portMAX_DELAY);
}
