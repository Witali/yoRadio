// Observe the public parser callback; all vendor arguments/results stay unchanged.
#include <assert.h>
#include <inttypes.h>
#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_heap_caps.h"
#include "esp_system.h"
#include "esp_task_wdt.h"
#include "esp_audio_simple_dec.h"
#include "esp_audio_simple_dec_reg.h"
#include "impl/esp_ogg_dec.h"
#include "impl/esp_ogg_parse.h"
#include "psa/crypto.h"
#include "decoder_registration.h"
#include "window_ranges.h"

#ifdef NDEBUG
#error "Parser observation requires assertions"
#endif
extern const uint8_t short_start[] asm("_binary_fixture20_ogg_start");
extern const uint8_t short_end[] asm("_binary_fixture20_ogg_end");
extern const uint8_t long_start[] asm("_binary_fixture120_ogg_start");
extern const uint8_t long_end[] asm("_binary_fixture120_ogg_end");
static uint8_t pcm[24576];
static const char *active_case;
static bool active_observed;
static TaskHandle_t worker_task;
static unsigned parse_calls, successful_parses, free_calls;

static esp_es_parse_err_t observe_ogg(esp_es_parse_raw_t *raw, esp_es_parse_frame_info_t *info) {
    assert(active_case && active_observed && xTaskGetCurrentTaskHandle() == worker_task);
    uint32_t length=raw->len;
    bool bos=raw->bos, eos=raw->eos;
    // Do not read [out] fields before the vendor returns success. The callback
    // forwards the very same public arguments once and returns the same result.
    esp_es_parse_err_t result=esp_ogg_parse_frame(raw,info);
    ++parse_calls;
    if (result == ESP_ES_PARSE_ERR_OK) {
        ++successful_parses;
        const esp_ogg_parse_extra_info_t *extra=info->extra_data;
        bool is_opus=extra && extra->dec_type == ESP_AUDIO_TYPE_OPUS;
        printf("EOPP_PARSE case=%s seq=%u len=%" PRIu32 " bos=%u eos=%u result=%d"
               " sample_num=%d duration=%d padding_start_size=%" PRIu32 " padding_end_pos=%" PRIu32
               " frame_size=%" PRIu32 " skipped_size=%" PRIu32 " total_size=%" PRIu32
               " extra_present=%u dec_type=%" PRIu32 " extra_is_opus=%u opus_rate=%" PRIu32
               " opus_channels=%u opus_frame_duration=%d opus_self_delimited=%u\n",
               active_case,parse_calls,length,(unsigned)bos,(unsigned)eos,(int)result,
               info->aud_info.sample_num,info->aud_info.duration,info->aud_info.padding_start_size,
               info->aud_info.padding_end_pos,info->frame_size,info->skipped_size,info->total_size,
               (unsigned)(extra!=NULL),extra?(uint32_t)extra->dec_type:0,(unsigned)is_opus,
               is_opus?extra->opus_cfg.sample_rate:0,is_opus?(unsigned)extra->opus_cfg.channel:0,
               is_opus?(int)extra->opus_cfg.frame_duration:-1,is_opus?(unsigned)extra->opus_cfg.self_delimited:0);
    }
    return result;
}

static void observe_free(void *extra) {
    assert(active_case && active_observed && xTaskGetCurrentTaskHandle() == worker_task);
    ++free_calls;
    esp_ogg_parse_free_extra(extra);
}

// Static lifetime also avoids relying on undocumented registry copy behavior.
static esp_audio_simple_dec_reg_info_t observed_registration={
    .decoder_ops=ESP_OGG_DEC_DEFAULT_OPS(), .parser=observe_ogg, .free=observe_free,
};

typedef struct {
    uint64_t bytes, window_bytes;
    uint8_t digest[32], window_digest[32];
    unsigned calls, frames;
} result_t;

static void hex_digest(const uint8_t digest[32],char hex[65]) {
    for (unsigned i=0;i<32;++i) snprintf(hex+2*i,3,"%02x",(unsigned)digest[i]);
}

static result_t decode(const char *name,const uint8_t *start,const uint8_t *end,
        uint64_t window_begin,uint64_t window_end,bool observed) {
    assert(!active_case && heap_caps_check_integrity_all(true));
    active_case=name; active_observed=observed;
    parse_calls=successful_parses=free_calls=0;
    size_t before=esp_get_free_heap_size();
    esp_audio_simple_dec_cfg_t config={.dec_type=observed?ESP_AUDIO_SIMPLE_DEC_TYPE_CUSTOM:ESP_AUDIO_SIMPLE_DEC_TYPE_OGG,
                                      .use_frame_dec=false};
    esp_audio_simple_dec_handle_t decoder=NULL;
    assert(esp_audio_simple_dec_open(&config,&decoder) == ESP_AUDIO_ERR_OK && decoder);
    psa_hash_operation_t hash=PSA_HASH_OPERATION_INIT,window_hash=PSA_HASH_OPERATION_INIT;
    assert(psa_hash_setup(&hash,PSA_ALG_SHA_256) == PSA_SUCCESS);
    assert(psa_hash_setup(&window_hash,PSA_ALG_SHA_256) == PSA_SUCCESS);
    esp_audio_simple_dec_raw_t raw={.buffer=(uint8_t *)start,.len=(uint32_t)(end-start),.eos=true};
    result_t measured={0};
    size_t consumed=0;
    for (;;) {
        esp_audio_simple_dec_out_t frame={.buffer=pcm,.len=sizeof(pcm)};
        raw.consumed=0;
        esp_audio_err_t result=esp_audio_simple_dec_process(decoder,&raw,&frame);
        assert(result == ESP_AUDIO_ERR_OK);
        assert(raw.consumed <= raw.len && frame.decoded_size <= sizeof(pcm));
        consumed+=raw.consumed;
        if (raw.consumed) raw.buffer+=raw.consumed;
        raw.len-=raw.consumed;
        ++measured.calls;
        if (frame.decoded_size) {
            esp_audio_simple_dec_info_t info={0};
            assert(esp_audio_simple_dec_get_info(decoder,&info) == ESP_AUDIO_ERR_OK);
            assert(info.sample_rate == 48000 && info.channel == 2 && info.bits_per_sample == 16);
            assert(frame.decoded_size%4 == 0);
            assert(psa_hash_update(&hash,frame.buffer,frame.decoded_size) == PSA_SUCCESS);
            // A separate read-only diagnostic hash of fixture-derived raw
            // emission positions. It neither trims playback nor changes PCM.
            uint64_t first=measured.bytes>window_begin*4?measured.bytes:window_begin*4;
            uint64_t last=measured.bytes+frame.decoded_size;
            if (last>window_end*4) last=window_end*4;
            if (first<last) {
                assert(psa_hash_update(&window_hash,frame.buffer+(size_t)(first-measured.bytes),(size_t)(last-first)) == PSA_SUCCESS);
                measured.window_bytes+=last-first;
            }
            measured.bytes+=frame.decoded_size;
            ++measured.frames;
        }
        if (!(measured.calls&31U)) vTaskDelay(1);
        if (!raw.consumed && !frame.decoded_size) { assert(!raw.len); break; }
    }
    assert(consumed == (size_t)(end-start) && measured.frames && measured.window_bytes == (window_end-window_begin)*4);
    size_t digest_bytes=0;
    assert(psa_hash_finish(&hash,measured.digest,32,&digest_bytes) == PSA_SUCCESS && digest_bytes == 32);
    assert(psa_hash_finish(&window_hash,measured.window_digest,32,&digest_bytes) == PSA_SUCCESS && digest_bytes == 32);
    assert(psa_hash_abort(&hash) == PSA_SUCCESS && psa_hash_abort(&window_hash) == PSA_SUCCESS);
    esp_audio_simple_dec_close(decoder);
    assert((observed && successful_parses && free_calls) || (!observed && !parse_calls && !free_calls));
    assert(heap_caps_check_integrity_all(true));
    char hex[65],window_hex[65]; hex_digest(measured.digest,hex);hex_digest(measured.window_digest,window_hex);
    printf("EOPP_CASE id=%s observed=%u input=%u calls=%u frames=%u pcm=%" PRIu64 " sha256=%s"
           " window_begin=%" PRIu64 " window_end=%" PRIu64 " window_bytes=%" PRIu64 " window_sha256=%s"
           " sample_rate=48000 channels=2 bits=16 parse_calls=%u successful_parses=%u free_calls=%u"
           " heap_before=%u heap_after=%u stack_free=%u core=%d priority=%u\n",
           name,(unsigned)observed,(unsigned)consumed,measured.calls,measured.frames,measured.bytes,hex,
           window_begin,window_end,measured.window_bytes,window_hex,parse_calls,successful_parses,free_calls,
           (unsigned)before,(unsigned)esp_get_free_heap_size(),(unsigned)uxTaskGetStackHighWaterMark(NULL),
           xPortGetCoreID(),(unsigned)uxTaskPriorityGet(NULL));
    assert(fflush(stdout) == 0);
    active_case=NULL;
    return measured;
}

static void pair(const char *plain,const char *observed,const uint8_t *start,const uint8_t *end,
        uint64_t begin,uint64_t finish) {
    result_t a=decode(plain,start,end,begin,finish,false);
    result_t b=decode(observed,start,end,begin,finish,true);
    assert(a.bytes == b.bytes && a.window_bytes == b.window_bytes && a.frames == b.frames &&
           !memcmp(a.digest,b.digest,32) && !memcmp(a.window_digest,b.window_digest,32));
}

static void worker(void *unused) {
    (void)unused;worker_task=xTaskGetCurrentTaskHandle();
    assert(xPortGetCoreID() == 1 && uxTaskPriorityGet(NULL) == 3);
    assert(esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(0)) == ESP_OK &&
           esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(1)) == ESP_OK);
    assert(psa_crypto_init() == PSA_SUCCESS && decoder_register_codecs() == ESP_AUDIO_ERR_OK);
    assert(esp_audio_simple_dec_register(ESP_AUDIO_SIMPLE_DEC_TYPE_CUSTOM,&observed_registration) == ESP_AUDIO_ERR_OK);
    pair("F20plain","F20observed",short_start,short_end,SHORT_WINDOW_BEGIN,SHORT_WINDOW_END);
    pair("F120plain","F120observed",long_start,long_end,LONG_WINDOW_BEGIN,LONG_WINDOW_END);
    assert(esp_audio_simple_dec_unregister(ESP_AUDIO_SIMPLE_DEC_TYPE_CUSTOM) == ESP_AUDIO_ERR_OK);
    decoder_unregister_codecs();
    assert(heap_caps_check_integrity_all(true));
    printf("EOPP_COMPLETE pairs=2 cases=4 core=1 priority=3 heap_free=%u heap_min=%u stack_free=%u heap_integrity=1\n",
           (unsigned)esp_get_free_heap_size(),(unsigned)esp_get_minimum_free_heap_size(),
           (unsigned)uxTaskGetStackHighWaterMark(NULL));
    assert(fflush(stdout) == 0);esp_restart();
}

void app_main(void) {
    assert(xPortGetCoreID() == 0 && short_end-short_start == 706319 && long_end-long_start == 707097);
    printf("EOPP_BEGIN coordinator=0 worker=1 priority=3 stack=16384 output_capacity=24576 fixtures=2\n");
    assert(fflush(stdout) == 0);
    assert(xTaskCreatePinnedToCore(worker,"opusparser",16384,NULL,3,NULL,1) == pdPASS);
    while (true) vTaskDelay(portMAX_DELAY);
}
