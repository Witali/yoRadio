// Reproduce the two saved hardware benchmark windows on the original AAC file.
// Compiled only into the optional QEMU instruction profile, never production.
#include <assert.h>
#include <inttypes.h>
#include <stdlib.h>
#include <string.h>
#include "esp_audio_simple_dec.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "native_aac_decoder.h"

extern const uint8_t fixture_start[] asm("_binary_aac_lc_320_aac_start");
extern const uint8_t fixture_end[] asm("_binary_aac_lc_320_aac_end");

static inline uint32_t instruction_count(void) {
    uint32_t value;
    __asm__ volatile("csrr %0, minstret" : "=r"(value) :: "memory");
    return value;
}

void qemu_aac_calibration(void) {
    assert(fixture_end - fixture_start == 443706);
    uint8_t *pcm = malloc(12288);
    uint8_t *input = malloc(2048);
    assert(pcm && input);
    for (unsigned current = 0; current <= 1; ++current) {
        for (unsigned run = 1; run <= 3; ++run) {
            // Historical firmware: streaming SDK parser, default AAC config
            // (Plus off), 2048-byte RAM input and a 12288-byte PCM buffer.
            esp_audio_simple_dec_handle_t legacy = NULL;
            native_aac_decoder_t *adapter = NULL;
            if (current) {
                adapter = native_aac_decoder_create();
                assert(adapter);
            } else {
                esp_audio_simple_dec_cfg_t cfg = {
                    .dec_type = ESP_AUDIO_SIMPLE_DEC_TYPE_AAC,
                    .dec_cfg = NULL, .cfg_size = 0, .use_frame_dec = false,
                };
                assert(esp_audio_simple_dec_open(&cfg, &legacy) == ESP_AUDIO_ERR_OK);
            }
            unsigned window = 1, calls = 0, consumed = 0, pcm_bytes = 0;
            uint64_t instructions = 0;
            for (const uint8_t *p = fixture_start; p < fixture_end;) {
                size_t count = (size_t)(fixture_end - p);
                if (count > 2048) count = 2048;
                memcpy(input, p, count);
                esp_audio_simple_dec_raw_t raw = {.buffer = input, .len = count};
                while (raw.len) {
                    esp_audio_simple_dec_out_t out = {.buffer = pcm, .len = 12288};
                    raw.consumed = 0;
                    uint32_t before = instruction_count();
                    esp_audio_err_t result = current
                        ? native_aac_decoder_process(adapter, &raw, &out)
                        : esp_audio_simple_dec_process(legacy, &raw, &out);
                    uint32_t work = instruction_count() - before;
                    assert(result == ESP_AUDIO_ERR_OK);
                    assert(raw.consumed <= raw.len && (raw.consumed || out.decoded_size));
                    instructions += work;
                    ++calls;
                    consumed += raw.consumed;
                    pcm_bytes += out.decoded_size;
                    raw.buffer += raw.consumed;
                    raw.len -= raw.consumed;
                    if (out.decoded_size) {
                        esp_audio_simple_dec_info_t info;
                        assert((current ? native_aac_decoder_get_info(adapter, &info)
                                        : esp_audio_simple_dec_get_info(legacy, &info)) == ESP_AUDIO_ERR_OK);
                        assert(info.sample_rate == 48000 && info.channel == 2 && info.bits_per_sample == 16);
                    }
                    // The saved hardware windows contain exactly 237 and 235
                    // AAC frames. Match both their input consumption and calls
                    // for the old path; compare the new path on the same PCM.
                    unsigned target_pcm = window == 1 ? 970752 : 962560;
                    if (window <= 2 && pcm_bytes >= target_pcm) {
                        assert(pcm_bytes == target_pcm);
                        if (!current) {
                            assert(calls == (window == 1 ? 335 : 334));
                            assert(consumed == (window == 1 ? 202528 : 202447));
                        }
                        ESP_LOGI("qemu_cal", "QEMU_AAC_CAL path=%s run=%u window=%u"
                                 " instructions=%" PRIu64 " calls=%u consumed=%u pcm=%u",
                                 current ? "current" : "legacy", run, window,
                                 instructions, calls, consumed, pcm_bytes);
                        ++window;
                        calls = consumed = pcm_bytes = 0;
                        instructions = 0;
                    }
                }
                p += count;
                vTaskDelay(1);
            }
            assert(window == 3);
            if (current) native_aac_decoder_destroy(adapter);
            else esp_audio_simple_dec_close(legacy);
        }
    }
    free(input);
    free(pcm);
    ESP_LOGI("qemu_cal", "QEMU_AAC_CAL_PASS matched physical-board PCM windows");
}
