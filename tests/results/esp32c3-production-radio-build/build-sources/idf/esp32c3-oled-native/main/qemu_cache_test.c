// Emulator-only cache trace. Markers are valid RISC-V no-ops, not MMIO.
#include <assert.h>
#include <inttypes.h>
#include <stdlib.h>
#include <string.h>
#include "native_aac_decoder.h"
#include "esp_aac_dec.h"
#include "esp_audio_codec_version.h"
#include "esp_audio_simple_dec_default.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define FIXTURE(name, symbol) \
    extern const uint8_t name##_start[] asm("_binary_" symbol "_aac_start"); \
    extern const uint8_t name##_end[] asm("_binary_" symbol "_aac_end")
FIXTURE(lc48, "lc_48000_stereo");
FIXTURE(he48, "he_48000_stereo");
FIXTURE(hev2, "hev2_44100_stereo");
#define MARK(word) __asm__ volatile(".word " #word ::: "memory")

static uint32_t instructions(void) {
    uint32_t value;
    __asm__ volatile("csrr %0, minstret" : "=r"(value) :: "memory");
    return value;
}

static void profile(unsigned id, const char *name, const uint8_t *start,
                    const uint8_t *end, unsigned rate, unsigned expected_samples) {
    uint8_t *input = malloc(2048), *pcm = malloc(16384);
    native_aac_decoder_t *decoder = native_aac_decoder_create();
    assert(input && pcm && decoder);
    // One full warm-up, then two measured passes; use RAM input like playback.
    for (unsigned pass = 0; pass < 3; ++pass) {
        if (pass) {
            switch (id) {
                case 0: MARK(0x6a000013); break;
                case 1: MARK(0x6a100013); break;
                case 2: MARK(0x6a200013); break;
                default: abort();
            }
        }
        uint64_t work = 0;
        unsigned samples = 0, frames = 0, calls = 0;
        for (const uint8_t *p = start; p < end;) {
            size_t size = end - p;
            if (size > 2048) size = 2048;
            memcpy(input, p, size);
            esp_audio_simple_dec_raw_t raw = {.buffer = input, .len = size};
            while (raw.len) {
                esp_audio_simple_dec_out_t out = {.buffer = pcm, .len = 16384};
                if (pass) MARK(0x6b000013);
                uint32_t before = instructions();
                esp_audio_err_t result = native_aac_decoder_process(decoder, &raw, &out);
                work += instructions() - before;
                if (pass) MARK(0x6b100013);
                ++calls;
                assert(result == ESP_AUDIO_ERR_OK);
                assert(raw.consumed <= raw.len && (raw.consumed || out.decoded_size));
                raw.buffer += raw.consumed;
                raw.len -= raw.consumed;
                if (out.decoded_size) {
                    esp_audio_simple_dec_info_t info;
                    assert(native_aac_decoder_get_info(decoder, &info) == ESP_AUDIO_ERR_OK);
                    assert(info.sample_rate == rate && info.channel == 2 && info.bits_per_sample == 16);
                    assert(out.decoded_size % 4 == 0);
                    samples += out.decoded_size / 4;
                    ++frames;
                }
            }
            p += size;
        }
        assert(samples == expected_samples);
        assert(heap_caps_check_integrity_all(true));
        if (pass) {
            MARK(0x6bf00013);
            ESP_LOGI("qemu_cache", "QEMU_CACHE_CASE case=%s pass=%u instructions=%" PRIu64
                     " rate=%u channels=2 samples=%u frames=%u calls=%u stack_free=%u",
                     name, pass, work, rate, samples, frames, calls,
                     (unsigned)uxTaskGetStackHighWaterMark(NULL));
        }
        vTaskDelay(1);
    }
    native_aac_decoder_destroy(decoder);
    free(input);
    free(pcm);
    assert(heap_caps_check_integrity_all(true));
}

void qemu_cache_test(void) {
    uint32_t before, after;
    portMUX_TYPE lock = portMUX_INITIALIZER_UNLOCKED;
    taskENTER_CRITICAL(&lock);
    __asm__ volatile("csrr %0, minstret\n.rept 1024\nnop\n.endr\ncsrr %1, minstret"
                     : "=r"(before), "=r"(after) :: "memory");
    taskEXIT_CRITICAL(&lock);
    assert(after - before == 1025);
    ESP_LOGI("qemu_cache", "QEMU_CACHE_ENV target=esp32c3 cpu_hz=%d codec_version=%s nop1024=%" PRIu32,
             CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ * 1000000, esp_audio_codec_get_version(), after - before);
    assert(esp_aac_dec_register() == ESP_AUDIO_ERR_OK);
    assert(esp_audio_simple_dec_register_default() == ESP_AUDIO_ERR_OK);
    profile(0, "lc48000_stereo", lc48_start, lc48_end, 48000, 26624);
    profile(1, "he48000_stereo", he48_start, he48_end, 48000, 30720);
    profile(2, "hev2_44100_stereo", hev2_start, hev2_end, 44100, 30720);
    ESP_LOGI("qemu_cache", "QEMU_CACHE_PASS modelled cache traffic; no physical timing");
}
