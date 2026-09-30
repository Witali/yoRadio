// Emulator-only integration checks against the real ESP32-C3 codec library.
#include <assert.h>
#include <stdlib.h>
#include <string.h>

#include "native_aac_decoder.h"
#include "esp_audio_dec_default.h"
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

static void check_fixture(native_aac_decoder_t *decoder,
                           native_state_t *state, oled_display_t *display,
                           const char *name, const uint8_t *start,
                           const uint8_t *end, uint32_t rate, uint8_t channels) {
    uint8_t *pcm = malloc(16384);
    assert(pcm);
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
            esp_audio_simple_dec_out_t output = {.buffer = pcm, .len = 16384};
            assert(native_aac_decoder_process(decoder, &raw, &output) ==
                   ESP_AUDIO_ERR_OK);
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
    check_fixture(decoder, state, display, "Implicit SBR core", hev2_start, hev2_end, 22050, 1);
    assert(strcmp(state->stream_format, "AAC PCM 22.05 kHz mono") == 0);
    ESP_LOGW(TAG, "QEMU_AAC_LIMITATION implicit SBR/PS change needs stream restart");
    native_aac_decoder_destroy(decoder);
    decoder = native_aac_decoder_create();
    assert(decoder);
    check_fixture(decoder, state, display, "HEv2 restart", hev2_start, hev2_end, 44100, 2);
    native_aac_decoder_destroy(decoder);
    native_state_begin_stream(state, 2);
    assert(!state->sample_rate_hz && !state->channels && !state->audio_running);
    ESP_LOGI(TAG, "QEMU_AAC_FORMAT_PASS full-rate HE-AAC, PS stereo and in-stream layout changes");
}
