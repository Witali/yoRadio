/* Complete public AAC decoding, without the production parser, pending owner,
 * task pipeline, private ABI or decoder wrappers. */
#include <assert.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_audio_simple_dec.h"
#include "esp_audio_simple_dec_default.h"
#include "esp_aac_dec.h"
#include "esp_heap_caps.h"
#include "esp_system.h"
#include "psa/crypto.h"

#ifdef NDEBUG
#error "The reference requires assertions"
#endif
extern const uint8_t fixture_start[] asm("_binary_fixtures_bin_start");
extern const uint8_t fixture_end[] asm("_binary_fixtures_bin_end");
typedef struct { uint32_t magic, version, count, entry_size; } header_t;
typedef struct { char name[8]; uint32_t offset, size, frames, core_rate, channels, rate; } entry_t;
_Static_assert(sizeof(header_t) == 16 && sizeof(entry_t) == 32, "reference fixture ABI");

static void hex(const uint8_t sha[32], char text[65]) {
    for (unsigned i = 0; i < 32; ++i) snprintf(text + 2 * i, 3, "%02x", (unsigned)sha[i]);
}

static void decode(const entry_t *e, bool plus) {
    assert(xPortGetCoreID() == 1 && uxTaskPriorityGet(NULL) == 3);
    assert(e->offset >= 80 && e->size && e->offset < (size_t)(fixture_end - fixture_start));
    assert(e->size <= (size_t)(fixture_end - fixture_start) - e->offset);
    assert(e->rate == 48000 && e->channels == 2 && (e->core_rate == 24000 || e->core_rate == 48000));
    size_t before = esp_get_free_heap_size();
    uint8_t input_sha[32], input_after[32], pcm_sha[32];
    size_t sha_size = 0;
    assert(psa_hash_compute(PSA_ALG_SHA_256, fixture_start + e->offset, e->size,
                            input_sha, sizeof(input_sha), &sha_size) == PSA_SUCCESS && sha_size == 32);
    esp_aac_dec_cfg_t aac = ESP_AAC_DEC_CONFIG_DEFAULT();
    aac.aac_plus_enable = plus;
    esp_audio_simple_dec_cfg_t cfg = {.dec_type = ESP_AUDIO_SIMPLE_DEC_TYPE_AAC,
        .dec_cfg = &aac, .cfg_size = sizeof(aac), .use_frame_dec = false};
    esp_audio_simple_dec_handle_t decoder = NULL;
    assert(esp_audio_simple_dec_open(&cfg, &decoder) == ESP_AUDIO_ERR_OK && decoder);
    uint32_t capacity = 12288;
    uint8_t *pcm = malloc(capacity);
    assert(pcm);
    psa_hash_operation_t hash = PSA_HASH_OPERATION_INIT;
    assert(psa_hash_setup(&hash, PSA_ALG_SHA_256) == PSA_SUCCESS);
    esp_audio_simple_dec_raw_t raw = {.buffer = (uint8_t *)fixture_start + e->offset, .len = e->size};
    uint64_t bytes = 0, frames = 0;
    unsigned calls = 0, resizes = 0;
    const unsigned rate = plus ? e->rate : e->core_rate;
    for (;;) {
        esp_audio_simple_dec_out_t out = {.buffer = pcm, .len = capacity};
        raw.consumed = 0;
        esp_audio_err_t result = esp_audio_simple_dec_process(decoder, &raw, &out);
        assert(++calls < e->frames * 4 + 16);
        assert(raw.consumed <= raw.len && out.decoded_size <= capacity);
        raw.buffer += raw.consumed;
        raw.len -= raw.consumed;
        if (!(calls & 15u)) vTaskDelay(1);
        if (result == ESP_AUDIO_ERR_BUFF_NOT_ENOUGH) {
            assert(!out.decoded_size && out.needed_size > capacity);
            uint8_t *larger = realloc(pcm, out.needed_size);
            assert(larger);
            pcm = larger;
            capacity = out.needed_size;
            ++resizes;
            continue;
        }
        assert(result == ESP_AUDIO_ERR_OK);
        if (out.decoded_size) {
            esp_audio_simple_dec_info_t info = {0};
            assert(esp_audio_simple_dec_get_info(decoder, &info) == ESP_AUDIO_ERR_OK);
            assert(info.sample_rate == rate && info.channel == 2 && info.bits_per_sample == 16);
            assert(!(out.decoded_size % 4));
            assert(psa_hash_update(&hash, pcm, out.decoded_size) == PSA_SUCCESS);
            bytes += out.decoded_size;
            frames += out.decoded_size / 4;
        }
        if (!raw.consumed && !out.decoded_size) {
            if (raw.eos) { assert(!raw.len); break; }
            raw.eos = true;
        } else if (!raw.len) raw.eos = true;
    }
    assert(frames == (uint64_t)e->frames * 1024 * (rate / e->core_rate));
    assert(psa_hash_finish(&hash, pcm_sha, sizeof(pcm_sha), &sha_size) == PSA_SUCCESS && sha_size == 32);
    assert(psa_hash_compute(PSA_ALG_SHA_256, fixture_start + e->offset, e->size,
                            input_after, sizeof(input_after), &sha_size) == PSA_SUCCESS && sha_size == 32);
    assert(!memcmp(input_sha, input_after, 32));
    esp_audio_simple_dec_close(decoder);
    free(pcm);
    assert(heap_caps_check_integrity_all(true));
    char input_hex[65], pcm_hex[65];
    hex(input_sha, input_hex);
    hex(pcm_sha, pcm_hex);
    printf("AAC_TLS_REFERENCE profile=%s plus=%u input=%" PRIu32 " input_sha256=%s rate=%u channels=2 bits=16 frames=%" PRIu64
           " pcm_bytes=%" PRIu64 " pcm_sha256=%s calls=%u resizes=%u heap_before=%u heap_after=%u stack_free=%u core=1 priority=3 drained=1\n",
           e->name, (unsigned)plus, e->size, input_hex, rate, frames, bytes, pcm_hex, calls, resizes,
           (unsigned)before, (unsigned)esp_get_free_heap_size(), (unsigned)uxTaskGetStackHighWaterMark(NULL));
    fflush(stdout);
}

static void worker(void *arg) {
    (void)arg;
    assert(psa_crypto_init() == PSA_SUCCESS);
    assert(esp_aac_dec_register() == ESP_AUDIO_ERR_OK);
    assert(esp_audio_simple_dec_register_default() == ESP_AUDIO_ERR_OK);
    const header_t *h = (const header_t *)fixture_start;
    assert(h->magic == 0x41414354 && h->version == 1 && h->count == 2 && h->entry_size == 32);
    const entry_t *entries = (const entry_t *)(h + 1);
    for (unsigned i = 0; i < 2; ++i) {
        decode(&entries[i], true);
        decode(&entries[i], false);
        vTaskDelay(1);
    }
    esp_audio_simple_dec_unregister_default();
    esp_audio_dec_unregister_all();
    puts("AAC_TLS_REFERENCE_COMPLETE cases=4 handles_closed=4 heap_integrity=1");
    fflush(stdout);
    esp_restart();
}

void app_main(void) {
    assert(xPortGetCoreID() == 0);
    assert(xTaskCreatePinnedToCore(worker, "aac_reference", 16384, NULL, 3, NULL, 1) == pdPASS);
    while (true) vTaskDelay(portMAX_DELAY);
}
