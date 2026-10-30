// Original public Espressif Ogg/Opus; baseline precedes shared caller adapters.
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
#include "decoder_pending_input.h"
#include "decoder_eof_input.h"

#ifdef NDEBUG
#error "The native vendor diagnostic requires assertions"
#endif
#if !CONFIG_IDF_TARGET_ESP32
#error "This diagnostic requires the CYD LX6 target"
#endif
extern const uint8_t fixture_start[] asm("_binary_fixture_ogg_start");
extern const uint8_t fixture_end[] asm("_binary_fixture_ogg_end");
static uint8_t pcm[12288];
static uint8_t reference_sha[32];
static uint64_t reference_bytes;
typedef struct {
    esp_audio_simple_dec_handle_t decoder;
    psa_hash_operation_t hash;
    decoder_pending_input_t pending;
    uint64_t pcm_bytes;
    size_t consumed, pending_max;
    unsigned calls, frames, feeds, coalesces, data_eos_calls, empty_eos_calls;
    bool drained;
} stream_t;

static void process(stream_t *stream, uint8_t *data, uint32_t length, bool eos, bool adapted) {
    esp_audio_simple_dec_raw_t raw = {.buffer=data, .len=length, .eos=eos};
    bool owned = false;
    if (adapted) assert(decoder_pending_input_prepare(&stream->pending,data,length,
        &raw.buffer,&raw.len,&owned) == DECODER_PENDING_INPUT_OK);
    do {
        esp_audio_simple_dec_out_t out = {.buffer=pcm,.len=sizeof(pcm)};
        raw.consumed = 0;
        if (raw.eos) {
            if (raw.len) ++stream->data_eos_calls;
            else ++stream->empty_eos_calls;
        }
        esp_audio_err_t result = esp_audio_simple_dec_process(stream->decoder,&raw,&out);
        assert(result == ESP_AUDIO_ERR_OK);
        assert(raw.consumed <= raw.len && out.decoded_size <= sizeof(pcm));
        if (raw.consumed) raw.buffer += raw.consumed;
        raw.len -= raw.consumed;
        stream->consumed += raw.consumed;
        ++stream->calls;
        if (out.decoded_size) {
            esp_audio_simple_dec_info_t info = {0};
            assert(esp_audio_simple_dec_get_info(stream->decoder,&info) == ESP_AUDIO_ERR_OK);
            assert(info.sample_rate == 48000 && info.channel == 2 && info.bits_per_sample == 16);
            assert(out.decoded_size % 4 == 0);
            assert(psa_hash_update(&stream->hash,out.buffer,out.decoded_size) == PSA_SUCCESS);
            stream->pcm_bytes += out.decoded_size;
            ++stream->frames;
        }
        if (!(stream->calls & 31U)) vTaskDelay(1);
        if (!raw.consumed && !out.decoded_size) {
            if (raw.eos) {
                assert(!raw.len);
                stream->drained = true;
            } else {
                assert(raw.len && adapted);
                assert(decoder_pending_input_retain(&stream->pending,raw.buffer,raw.len,owned)
                       == DECODER_PENDING_INPUT_OK);
                ++stream->coalesces;
                if (stream->pending.size > stream->pending_max) stream->pending_max=stream->pending.size;
            }
            break;
        }
    } while (raw.len || raw.eos);
}

static void decode(unsigned chunk, bool adapted) {
    assert(heap_caps_check_integrity_all(true));
    size_t before=esp_get_free_heap_size();
    stream_t stream={.hash=PSA_HASH_OPERATION_INIT};
    esp_audio_simple_dec_cfg_t config={.dec_type=ESP_AUDIO_SIMPLE_DEC_TYPE_OGG,.use_frame_dec=false};
    assert(esp_audio_simple_dec_open(&config,&stream.decoder) == ESP_AUDIO_ERR_OK && stream.decoder);
    assert(psa_hash_setup(&stream.hash,PSA_ALG_SHA_256) == PSA_SUCCESS);
    size_t length=(size_t)(fixture_end-fixture_start), fed=0;
    decoder_eof_input_t eof={0};
    if (!adapted) {
        // One borrowed complete encoded input, no pending or EOF adapter. EOS
        // accompanies real data; public processing drains all resulting PCM.
        process(&stream,(uint8_t *)fixture_start,(uint32_t)length,true,false);
        fed=length; stream.feeds=1;
    } else {
        while (!stream.drained) {
            uint32_t count=(uint32_t)(length-fed);
            if (count > chunk) count=chunk;
            bool terminal=!count;
            decoder_eof_segment_t segments[2];
            uint8_t previous=0;
            unsigned n=decoder_eof_input_prepare(&eof,true,(uint8_t *)fixture_start+fed,count,
                                                 terminal,&previous,segments);
            fed+=count;
            if (count) ++stream.feeds;
            for (unsigned i=0;i<n;++i) process(&stream,segments[i].data,segments[i].size,
                                               segments[i].eos,true);
        }
    }
    uint8_t digest[32]; size_t size=0; char hex[65];
    assert(psa_hash_finish(&stream.hash,digest,sizeof(digest),&size) == PSA_SUCCESS && size == sizeof(digest));
    assert(psa_hash_abort(&stream.hash) == PSA_SUCCESS);
    for (unsigned i=0;i<sizeof(digest);++i) snprintf(hex+2*i,3,"%02x",digest[i]);
    esp_audio_simple_dec_close(stream.decoder);
    assert(stream.drained && fed == length && stream.consumed == length && !stream.pending.size && !eof.present);
    decoder_pending_input_clear(&stream.pending);
    decoder_eof_input_clear(&eof);
    assert(stream.frames && stream.pcm_bytes && heap_caps_check_integrity_all(true));
    size_t after=esp_get_free_heap_size();
    printf("EOP_%s mode=%s chunk=%u input=%u calls=%u frames=%u pcm=%" PRIu64
           " sha256=%s sample_rate=48000 channels=2 bits_per_sample=16 feeds=%u coalesces=%u pending_max=%u"
           " data_eos_calls=%u empty_eos_calls=%u before=%u after=%u stack_free=%u core=%d priority=%u\n",
           adapted?"CASE":"BASELINE",adapted?"separate_eof_adapted":"inline_eos",chunk,
           (unsigned)stream.consumed,stream.calls,stream.frames,stream.pcm_bytes,hex,stream.feeds,
           stream.coalesces,(unsigned)stream.pending_max,stream.data_eos_calls,stream.empty_eos_calls,
           (unsigned)before,(unsigned)after,(unsigned)uxTaskGetStackHighWaterMark(NULL),xPortGetCoreID(),
           (unsigned)uxTaskPriorityGet(NULL));
    assert(fflush(stdout) == 0);
    if (!adapted) { memcpy(reference_sha,digest,sizeof(digest)); reference_bytes=stream.pcm_bytes; }
    else assert(before == after && stream.pcm_bytes == reference_bytes && !memcmp(reference_sha,digest,sizeof(digest)));
    assert(xPortGetCoreID() == 1 && uxTaskPriorityGet(NULL) == 3);
    vTaskDelay(1);
}

static void worker(void *unused) {
    (void)unused;
    assert(esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(0)) == ESP_OK);
    assert(esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(1)) == ESP_OK);
    assert(psa_crypto_init() == PSA_SUCCESS);
    size_t before=esp_get_free_heap_size();
    assert(decoder_register_codecs() == ESP_AUDIO_ERR_OK);
    decode((unsigned)(fixture_end-fixture_start),false);
    decode(4096,true); decode(257,true); decode(1,true);
    decoder_unregister_codecs();
    assert(heap_caps_check_integrity_all(true));
    size_t after=esp_get_free_heap_size();
    printf("EOP_COMPLETE target=esp32 cases=3 core=1 registry_before=%u heap_free=%u retained=%d heap_min=%u stack_free=%u heap_integrity=1\n",
           (unsigned)before,(unsigned)after,(int)before-(int)after,(unsigned)esp_get_minimum_free_heap_size(),
           (unsigned)uxTaskGetStackHighWaterMark(NULL));
    assert(fflush(stdout) == 0);
    esp_restart();
}
void app_main(void) {
    assert(xPortGetCoreID() == 0 && fixture_end-fixture_start == 706319);
    printf("EOP_BEGIN target=esp32 coordinator=0 worker=1 stack=16384 priority=3 output_capacity=12288 fixture=706319\n");
    assert(fflush(stdout) == 0);
    assert(xTaskCreatePinnedToCore(worker,"vendoropus",16384,NULL,3,NULL,1) == pdPASS);
    while (true) vTaskDelay(portMAX_DELAY);
}
