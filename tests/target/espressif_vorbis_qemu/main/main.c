// Original vendor decoder, public interfaces only; not the radio application.
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

#ifdef NDEBUG
#error "The native vendor diagnostic requires assertions"
#endif
#if CONFIG_IDF_TARGET_ESP32
#define EVQ_TARGET "esp32"
enum { EVQ_CORE = 1 };
#elif CONFIG_IDF_TARGET_ESP32C3
#define EVQ_TARGET "esp32c3"
enum { EVQ_CORE = 0 };
#else
#error "Only ESP32 LX6 and ESP32-C3 RV32 are supported"
#endif

extern const uint8_t fixture_start[] asm("_binary_fixture_ogg_start");
extern const uint8_t fixture_end[] asm("_binary_fixture_ogg_end");
static uint8_t pcm[32768];
static uint8_t full_reference[32];
// The old lifecycle fixture stopped after one empty EOF call. Its exact bytes
// remain a prefix regression; the fixture's EOS granule is 528000 stereo frames.
enum { EVQ_PREFIX_BYTES = 2107648, EVQ_PCM_BYTES = 2112000 };
#define EVQ_PREFIX_SHA "eb2037928cd89a1922fd9ae9d055c03b587484b7378c55b0f319d79980976144"

static void decode(unsigned chunk, bool warmup) {
    assert(heap_caps_check_integrity_all(true));
    size_t before = esp_get_free_heap_size();
    esp_audio_simple_dec_cfg_t config = {
        .dec_type = ESP_AUDIO_SIMPLE_DEC_TYPE_OGG, .use_frame_dec = false,
    };
    esp_audio_simple_dec_handle_t decoder = NULL;
    assert(esp_audio_simple_dec_open(&config, &decoder) == ESP_AUDIO_ERR_OK && decoder);
    psa_hash_operation_t hash = PSA_HASH_OPERATION_INIT;
    psa_hash_operation_t prefix_hash = PSA_HASH_OPERATION_INIT;
    assert(psa_hash_setup(&hash, PSA_ALG_SHA_256) == PSA_SUCCESS);
    assert(psa_hash_setup(&prefix_hash, PSA_ALG_SHA_256) == PSA_SUCCESS);
    const size_t length = (size_t)(fixture_end - fixture_start);
    size_t fed_offset = 0, consumed_total = 0;
    decoder_pending_input_t pending = {0};
    uint64_t pcm_bytes = 0;
    unsigned calls = 0, frames = 0, feeds = 0, coalesces = 0;
    size_t pending_max = 0;
    bool drained = false;
    while (!drained) {
        size_t count = length - fed_offset;
        if (count > chunk) count = chunk;
        esp_audio_simple_dec_raw_t raw = {.eos = fed_offset + count == length};
        bool owned = false;
        assert(decoder_pending_input_prepare(&pending, (uint8_t *)fixture_start + fed_offset,
                   count, &raw.buffer, &raw.len, &owned) == DECODER_PENDING_INPUT_OK);
        fed_offset += count;
        if (count) ++feeds;
        do {
            esp_audio_simple_dec_out_t frame = {.buffer = pcm, .len = sizeof(pcm)};
            raw.consumed = 0;
            esp_audio_err_t result = esp_audio_simple_dec_process(decoder, &raw, &frame);
            // Deliberately ample storage: this baseline does not exercise the
            // original decoder's known small-buffer retry behavior.
            assert(result == ESP_AUDIO_ERR_OK);
            assert(raw.consumed <= raw.len && frame.decoded_size <= sizeof(pcm));
            raw.buffer += raw.consumed;
            raw.len -= raw.consumed;
            consumed_total += raw.consumed;
            ++calls;
            if (frame.decoded_size) {
                esp_audio_simple_dec_info_t info = {0};
                assert(esp_audio_simple_dec_get_info(decoder, &info) == ESP_AUDIO_ERR_OK);
                assert(info.sample_rate == 48000 && info.channel == 2 && info.bits_per_sample == 16);
                assert(frame.decoded_size % 4 == 0);
                if (pcm_bytes < EVQ_PREFIX_BYTES) {
                    size_t prefix_count = EVQ_PREFIX_BYTES - (size_t)pcm_bytes;
                    if (prefix_count > frame.decoded_size) prefix_count = frame.decoded_size;
                    assert(psa_hash_update(&prefix_hash, frame.buffer, prefix_count) == PSA_SUCCESS);
                }
                assert(psa_hash_update(&hash, frame.buffer, frame.decoded_size) == PSA_SUCCESS);
                pcm_bytes += frame.decoded_size;
                ++frames;
            }
            if (!(calls & 31U)) vTaskDelay(1);
            if (!raw.consumed && !frame.decoded_size) {
                if (raw.eos) {
                    // A pending suffix at EOF cannot be repaired by more input.
                    assert(raw.len == 0);
                    drained = true;
                } else {
                    assert(raw.len > 0);
                    assert(decoder_pending_input_retain(&pending, raw.buffer, raw.len, owned)
                           == DECODER_PENDING_INPUT_OK);
                    ++coalesces;
                    if (pending.size > pending_max) pending_max = pending.size;
                }
                break;
            }
            if (raw.eos && !raw.len && !frame.decoded_size) { drained = true; break; }
        } while (raw.len || raw.eos);
    }
    uint8_t digest[32];
    uint8_t prefix_digest[32];
    char hex[65];
    char prefix_hex[65];
    size_t digest_size = 0;
    assert(psa_hash_finish(&hash, digest, sizeof(digest), &digest_size) == PSA_SUCCESS);
    assert(digest_size == sizeof(digest) && psa_hash_abort(&hash) == PSA_SUCCESS);
    assert(psa_hash_finish(&prefix_hash, prefix_digest, sizeof(prefix_digest), &digest_size) == PSA_SUCCESS);
    assert(digest_size == sizeof(prefix_digest) && psa_hash_abort(&prefix_hash) == PSA_SUCCESS);
    for (unsigned i = 0; i < sizeof(digest); ++i) {
        snprintf(hex + 2 * i, 3, "%02x", digest[i]);
        snprintf(prefix_hex + 2 * i, 3, "%02x", prefix_digest[i]);
    }
    esp_audio_simple_dec_close(decoder);
    assert(fed_offset == length && consumed_total == length && !pending.size);
    decoder_pending_input_clear(&pending);
    assert(frames && pcm_bytes && heap_caps_check_integrity_all(true));
    size_t after = esp_get_free_heap_size();
    printf("EVQ_%s chunk=%u input=%u calls=%u frames=%u pcm=%" PRIu64
           " sha256=%s prefix_pcm=%u prefix_sha256=%s feeds=%u coalesces=%u pending_max=%u"
           " before=%u after=%u stack_free=%u core=%d priority=%u\n",
           warmup ? "WARMUP" : "CASE", chunk, (unsigned)consumed_total, calls, frames, pcm_bytes, hex,
           (unsigned)EVQ_PREFIX_BYTES, prefix_hex, feeds, coalesces, (unsigned)pending_max,
           (unsigned)before,
           (unsigned)after, (unsigned)uxTaskGetStackHighWaterMark(NULL), xPortGetCoreID(),
           (unsigned)uxTaskPriorityGet(NULL));
    assert(fflush(stdout) == 0);
    assert(pcm_bytes == EVQ_PCM_BYTES && !strcmp(prefix_hex, EVQ_PREFIX_SHA));
    if (warmup) memcpy(full_reference, digest, sizeof(digest));
    else assert(before == after && !memcmp(full_reference, digest, sizeof(digest)));
    assert(xPortGetCoreID() == EVQ_CORE && uxTaskPriorityGet(NULL) == 3);
    vTaskDelay(1);
}

static void worker(void *unused) {
    (void)unused;
    assert(esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(0)) == ESP_OK);
#if CONFIG_IDF_TARGET_ESP32
    assert(esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(1)) == ESP_OK);
#endif
    // Initialize the supported SDK hashing provider before ownership baselines.
    assert(psa_crypto_init() == PSA_SUCCESS);
    size_t before = esp_get_free_heap_size();
    assert(decoder_register_codecs() == ESP_AUDIO_ERR_OK);
    decode(4096, true);
    decode(4096, false);
    decode(257, false);
    decode(1, false);
    decoder_unregister_codecs();
    assert(heap_caps_check_integrity_all(true));
    unsigned after = esp_get_free_heap_size();
    printf("EVQ_COMPLETE target=%s cases=3 core=%d registry_before=%u heap_free=%u retained=%d heap_min=%u stack_free=%u heap_integrity=1\n",
           EVQ_TARGET, xPortGetCoreID(), (unsigned)before, after, (int)before - (int)after,
           (unsigned)esp_get_minimum_free_heap_size(), (unsigned)uxTaskGetStackHighWaterMark(NULL));
    assert(fflush(stdout) == 0);
    esp_restart();
}

void app_main(void) {
    assert(xPortGetCoreID() == 0);
    printf("EVQ_BEGIN target=%s coordinator=0 worker=%d stack=16384 priority=3\n", EVQ_TARGET, EVQ_CORE);
    assert(fflush(stdout) == 0);
    assert(xTaskCreatePinnedToCore(worker, "vendorvorbis", 16384, NULL, 3, NULL, EVQ_CORE) == pdPASS);
    // Keep the coordinator's allocation stable while the worker measures the
    // stream/registry ownership; returning would defer its task free to idle.
    while (true) vTaskDelay(portMAX_DELAY);
}
