// Emulator-only integration checks against the real ESP32-C3 codec library.
#include <assert.h>
#include <inttypes.h>
#include <stdlib.h>
#include <string.h>

#include "native_aac_decoder.h"
#include "decoder_pcm.h"
#include "esp_audio_dec_default.h"
#include "esp_audio_codec_version.h"
#include "esp_aac_dec.h"
#include "esp_audio_simple_dec.h"
#include "esp_audio_simple_dec_default.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "native_audio_output.h"
#include "native_state.h"
#include "oled_display.h"
#if defined(CONFIG_YORADIO_QEMU_AAC_BFP16_TEST) || defined(CONFIG_YORADIO_QEMU_AAC_PACKED_HISTORY_TEST)
#include "qemu_aac_bfp16.h"
#endif

#define FIXTURE(name, symbol) \
    extern const uint8_t name##_start[] asm("_binary_" symbol "_aac_start"); \
    extern const uint8_t name##_end[] asm("_binary_" symbol "_aac_end")
FIXTURE(lc44, "lc_44100_stereo");
FIXTURE(lc22, "lc_22050_mono");
FIXTURE(lc48, "lc_48000_stereo");
FIXTURE(he44, "he_44100_stereo");
FIXTURE(he48, "he_48000_stereo");
FIXTURE(hev2, "hev2_44100_stereo");

static const char *TAG = "qemu_aac";

#ifdef CONFIG_YORADIO_QEMU_AAC_PROFILE
void qemu_aac_calibration(void);
void qemu_codec_calibration(void);

static inline uint32_t instruction_count(void) {
    uint32_t value;
    __asm__ volatile("csrr %0, minstret" : "=r"(value) :: "memory");
    return value;
}

static void check_instruction_counter(void) {
    // Fail rather than publish host ticks as guest instructions when someone
    // launches this image without -icount. Mask IRQs only for this tiny probe.
    portMUX_TYPE lock = portMUX_INITIALIZER_UNLOCKED;
    uint32_t before, after;
    taskENTER_CRITICAL(&lock);
    __asm__ volatile("csrr %0, minstret\n"
                     ".rept 1024\n nop\n .endr\n"
                     "csrr %1, minstret\n"
                     : "=r"(before), "=r"(after) :: "memory");
    taskEXIT_CRITICAL(&lock);
    ESP_LOGI(TAG, "QEMU_AAC_WORK_COUNTER nop1024=%" PRIu32, after - before);
    assert(after - before == 1025);
}

static void profile_fixture(const char *name, const uint8_t *start,
                            const uint8_t *end, uint32_t rate, uint8_t channels) {
    uint8_t *pcm = malloc(16384);
    assert(pcm);
    for (unsigned run = 1; run <= 3; ++run) {
        size_t heap_before = heap_caps_get_free_size(MALLOC_CAP_8BIT);
        native_aac_decoder_t *decoder = native_aac_decoder_create();
        assert(decoder);
        uint64_t instructions = 0, samples = 0;
        uint32_t frames = 0, max_call = 0;
        // Warm up once, then measure eight complete repeats without reopening
        // the decoder. No PCM output, UI drawing or logging in the measured call.
        for (unsigned repeat = 0; repeat <= 8; ++repeat) {
            for (const uint8_t *p = start; p < end;) {
                size_t count = (size_t)(end - p);
                if (count > 997) count = 997;
                esp_audio_simple_dec_raw_t raw = {.buffer = (uint8_t *)p, .len = count};
                while (raw.len) {
                    esp_audio_simple_dec_out_t output = {.buffer = pcm, .len = 16384};
                    uint32_t before = instruction_count();
                    esp_audio_err_t result = native_aac_decoder_process(decoder, &raw, &output);
                    uint32_t work = instruction_count() - before;
                    assert(result == ESP_AUDIO_ERR_OK);
                    assert(raw.consumed <= raw.len && (raw.consumed || output.decoded_size));
                    raw.buffer += raw.consumed;
                    raw.len -= raw.consumed;
                    if (repeat) {
                        instructions += work;
                        if (work > max_call) max_call = work;
                    }
                    if (output.decoded_size) {
                        esp_audio_simple_dec_info_t info;
                        assert(native_aac_decoder_get_info(decoder, &info) == ESP_AUDIO_ERR_OK);
                        assert(info.sample_rate == rate && info.channel == channels && info.bits_per_sample == 16);
                        assert(output.decoded_size % (2 * channels) == 0);
                        if (repeat) {
                            samples += output.decoded_size / (2 * channels);
                            ++frames;
                        }
                    }
                }
                p += count;
            }
            // Keep the RTOS responsive without including voluntary sleeps in
            // the counter. Tick interrupts during decode remain in the count.
            vTaskDelay(1);
        }
        assert(frames > 80 && samples >= 4 * rate);
        size_t heap_after = heap_caps_get_free_size(MALLOC_CAP_8BIT);
        ESP_LOGI(TAG, "QEMU_AAC_WORK case=%s run=%u instructions=%" PRIu64
                 " samples=%" PRIu64 " rate=%" PRIu32 " channels=%u frames=%" PRIu32
                 " max_call=%" PRIu32 " decoder_heap=%u",
                 name, run, instructions, samples, rate, channels, frames, max_call,
                 (unsigned)(heap_before - heap_after));
        native_aac_decoder_destroy(decoder);
    }
    free(pcm);
}
#endif

static void check_fixture(native_aac_decoder_t *decoder,
                           native_state_t *state, oled_display_t *display,
                           const char *name, const uint8_t *start,
                           const uint8_t *end, uint32_t rate, uint8_t channels) {
    uint8_t *pcm = malloc(NATIVE_AAC_PCM_FRAME_BYTES + 16);
    assert(pcm);
    memset(pcm + NATIVE_AAC_PCM_FRAME_BYTES, 0xa5, 16);
    size_t frames = 0;
    size_t samples = 0;
    // Exercise the SDK's streaming parser across non-aligned network chunks.
    while (start < end) {
        size_t size = (size_t)(end - start);
        if (size > 997) size = 997;
        esp_audio_simple_dec_raw_t raw = {
            .buffer = (uint8_t *)start, .len = size,
        };
        while (raw.len) {
            esp_audio_simple_dec_out_t output = {
                .buffer = pcm, .len = NATIVE_AAC_PCM_FRAME_BYTES};
            assert(native_aac_decoder_process(decoder, &raw, &output) ==
                   ESP_AUDIO_ERR_OK);
            assert(output.decoded_size <= NATIVE_AAC_PCM_FRAME_BYTES);
            for (unsigned i = 0; i < 16; ++i)
                assert(pcm[NATIVE_AAC_PCM_FRAME_BYTES + i] == 0xa5);
            assert(raw.consumed <= raw.len);
            assert(raw.consumed || output.decoded_size);
            raw.buffer += raw.consumed;
            raw.len -= raw.consumed;
            if (!output.decoded_size) continue;
            esp_audio_simple_dec_info_t latest = {0};
            assert(native_aac_decoder_get_info(decoder, &latest) == ESP_AUDIO_ERR_OK);
            assert(latest.sample_rate == rate && latest.channel == channels);
            assert(latest.bits_per_sample == 16);
            assert(output.decoded_size % (2 * channels) == 0);
            bool format_is_pcm;
            const char *label = native_aac_decoder_label(decoder, &latest, &format_is_pcm);
            native_stream_info_t info = {
                .codec = label, .sample_rate_hz = latest.sample_rate,
                .channels = latest.channel, .bits_per_sample = latest.bits_per_sample,
                .pcm_sample_rate_hz = latest.sample_rate, .pcm_channels = latest.channel,
                .format_is_pcm = format_is_pcm,
            };
            native_state_set_stream_info(state, 1, &info);
            native_state_t snapshot;
            native_state_snapshot(state, &snapshot);
            assert(snapshot.sample_rate_hz == latest.sample_rate &&
                   snapshot.channels == latest.channel);
            assert(native_audio_output_configure(latest.sample_rate) == ESP_OK);
            assert(native_audio_output_write_pcm(pcm, output.decoded_size,
                          latest.bits_per_sample, latest.channel) == ESP_OK);
            samples += output.decoded_size / (2 * channels);
            ++frames;
            vTaskDelay(1);
        }
        start += size;
    }
    assert(frames > 5 && samples >= rate / 4);
    char text[96];
    native_state_format_stream_details(state, text, sizeof(text));
    oled_display_clear(display);
    oled_display_draw_text(display, 0, 0, name);
    oled_display_draw_text(display, 0, 12, text);
    assert(oled_display_present(display) == ESP_OK);
    ESP_LOGI(TAG, "QEMU_AAC_CASE_PASS %s: %lu Hz %u ch, %u frames, %u samples, free %u min %u",
             name, (unsigned long)rate, channels, (unsigned)frames, (unsigned)samples,
             (unsigned)heap_caps_get_free_size(MALLOC_CAP_8BIT),
             (unsigned)heap_caps_get_minimum_free_size(MALLOC_CAP_8BIT));
    free(pcm);
}

void qemu_aac_test(native_state_t *state, oled_display_t *display) {
    assert(esp_aac_dec_register() == ESP_AUDIO_ERR_OK);
    assert(esp_audio_simple_dec_register_default() == ESP_AUDIO_ERR_OK);
    void qemu_aac_fill_test(void);
    qemu_aac_fill_test();
#ifdef CONFIG_YORADIO_QEMU_AAC_LATE_SBR_TEST
    void qemu_aac_faults_test(void);
    qemu_aac_faults_test();
#endif
    void qemu_aac_metadata_test(void);
    qemu_aac_metadata_test();
    native_aac_decoder_t *decoder = native_aac_decoder_create();
    assert(decoder);
    native_state_begin_stream(state, 1);
    check_fixture(decoder, state, display, "HE44 first", he44_start, he44_end, 44100, 2);
    // One streaming adapter/generation. Only production ADTS configuration
    // detection may recreate the underlying library decoder between frames.
    check_fixture(decoder, state, display, "LC44 stereo", lc44_start, lc44_end, 44100, 2);
    check_fixture(decoder, state, display, "LC22 mono", lc22_start, lc22_end, 22050, 1);
    check_fixture(decoder, state, display, "LC48 stereo", lc48_start, lc48_end, 48000, 2);
    check_fixture(decoder, state, display, "HE44 stereo", he44_start, he44_end, 44100, 2);
    check_fixture(decoder, state, display, "HE48 stereo", he48_start, he48_end, 48000, 2);
    check_fixture(decoder, state, display, "HEv2 stereo", hev2_start, hev2_end, 44100, 2);
    assert(strcmp(state->stream_format, "HE-AACv2 44.1 kHz stereo") == 0);
    // An implicit SBR/PS change with identical ADTS headers is a known SDK
    // limitation. Verify honest PCM reporting and recovery on a new stream.
    native_aac_decoder_destroy(decoder);
    decoder = native_aac_decoder_create();
    assert(decoder);
    check_fixture(decoder, state, display, "LC22 same header", lc22_start, lc22_end, 22050, 1);
#ifdef CONFIG_YORADIO_QEMU_AAC_LATE_SBR_TEST
    check_fixture(decoder, state, display, "Implicit SBR full", hev2_start, hev2_end, 44100, 2);
    assert(strcmp(state->stream_format, "HE-AACv2 44.1 kHz stereo") == 0);
    ESP_LOGI(TAG, "QEMU_AAC_LATE_SBR_FORMAT_PASS history retained; PCM quality still unqualified");
#else
    check_fixture(decoder, state, display, "Implicit SBR core", hev2_start, hev2_end, 22050, 1);
    assert(strcmp(state->stream_format, "AAC PCM 22.05 kHz mono") == 0);
    ESP_LOGW(TAG, "QEMU_AAC_LIMITATION implicit SBR/PS change needs stream restart");
#endif
    native_aac_decoder_destroy(decoder);
    decoder = native_aac_decoder_create();
    assert(decoder);
    check_fixture(decoder, state, display, "HEv2 restart", hev2_start, hev2_end, 44100, 2);
    native_aac_decoder_destroy(decoder);
    native_state_begin_stream(state, 2);
    assert(!state->sample_rate_hz && !state->channels && !state->audio_running);
#ifdef CONFIG_YORADIO_QEMU_AAC_PROFILE
    check_instruction_counter();
    ESP_LOGI(TAG, "QEMU_AAC_WORK_ENV target=esp32c3 cpu_hz=%d codec_version=%s",
             CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ * 1000000, esp_audio_codec_get_version());
    qemu_aac_calibration();
    qemu_codec_calibration();
    profile_fixture("lc44100_stereo", lc44_start, lc44_end, 44100, 2);
    profile_fixture("lc22050_mono", lc22_start, lc22_end, 22050, 1);
    profile_fixture("lc48000_stereo", lc48_start, lc48_end, 48000, 2);
    profile_fixture("he44100_stereo", he44_start, he44_end, 44100, 2);
    profile_fixture("he48000_stereo", he48_start, he48_end, 48000, 2);
    profile_fixture("hev2_44100_stereo", hev2_start, hev2_end, 44100, 2);
    ESP_LOGI(TAG, "QEMU_AAC_WORK_PASS instruction demand only; no hardware CPU timing");
#endif
#if defined(CONFIG_YORADIO_QEMU_AAC_BFP16_TEST) || defined(CONFIG_YORADIO_QEMU_AAC_PACKED_HISTORY_TEST)
    qemu_aac_bfp16_test();
#endif
#ifdef CONFIG_YORADIO_QEMU_AAC_LATE_SBR_TEST
    void qemu_aac_late_sbr_test(void);
    qemu_aac_late_sbr_test();
#endif
#ifdef CONFIG_YORADIO_QEMU_AAC_COMPACT_ADAPTER_TEST
    void qemu_aac_compact_adapter_test(void);
    qemu_aac_compact_adapter_test();
#endif
    ESP_LOGI(TAG, "QEMU_AAC_FORMAT_PASS full-rate HE-AAC, PS stereo and in-stream layout changes");
}
