#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "codec_bridge.h"

_Static_assert(sizeof(helix_stream_info_t) == 16, "Bounded stream/PCM metadata");
typedef int esp_err_t;
enum { ESP_OK = 0 };
#define ESP_LOGE(...) ((void)0)
static unsigned critical_depth;
#define taskENTER_CRITICAL() (++critical_depth)
#define taskEXIT_CRITICAL() (--critical_depth)
static uint32_t s_pcm_frames, s_pcm_rate, s_pcm_tick;
static uint32_t xTaskGetTickCount(void) { return 1234; }
static bool generation_current(uint32_t generation) { return generation == 42; }
static int state_codec(helix_codec_kind_t kind) { return (int)kind; }

typedef struct {
    int codec;
    uint32_t sample_rate_hz, bitrate_kbps;
    uint8_t channels;
} native_state_t;
static native_state_t state;
static unsigned publishes, writes;
static unsigned expected_pcm_channels;
static int output_error;
static int16_t *expected_pcm;
static esp_err_t native_audio_output_write(int16_t *pcm, size_t samples,
                                            uint32_t rate, uint8_t channels) {
    assert(!critical_depth && pcm == expected_pcm);
    assert(channels == expected_pcm_channels && rate && samples % channels == 0);
    ++writes;
    return output_error;
}
static void native_state_set_stream(int codec, uint32_t bitrate,
                                    uint32_t rate, uint8_t channels) {
    assert(!critical_depth);
    state = (native_state_t){codec, rate, bitrate, channels};
    ++publishes;
}
static const char *native_codec_name(int codec) {
    switch (codec) {
        case HELIX_CODEC_MP3: return "MP3";
        case HELIX_CODEC_AAC: return "AAC";
        case HELIX_CODEC_OPUS: return "OPUS";
        default: return "";
    }
}
#include "metadata_under_test.inc"

int main(void) {
    int16_t pcm[128] = {0};
    expected_pcm = pcm;
    for (int kind = HELIX_CODEC_MP3; kind <= HELIX_CODEC_OPUS; ++kind) {
        output_context_t context = {.generation = 42, .codec_kind = kind};
        helix_stream_info_t info = {48000, 128000, 1, 16, 2, 48000};
        expected_pcm_channels = 1;
        s_pcm_frames = publishes = writes = 0;
        assert(pcm_output(&context, &info, pcm, 64));
        assert(state.channels == 2 && context.decoder_channels == 2);
        assert(s_pcm_frames == 64 && s_pcm_rate == 48000 && s_pcm_tick == 1234);
        char text[64], expected[64];
        format_stream(&state, text, sizeof(text));
        snprintf(expected, sizeof(expected), "%s 128 kbps 48 kHz stereo", native_codec_name(kind));
        assert(!strcmp(text, expected));
        assert(pcm_output(&context, &info, pcm, 64));
        assert(publishes == 1 && s_pcm_frames == 128); // No redundant status update.

        info.source_channels = 1; // Only source layout changes; PCM remains mono.
        assert(pcm_output(&context, &info, pcm, 64));
        assert(publishes == 2 && state.channels == 1 && s_pcm_frames == 192);
        format_stream(&state, text, sizeof(text));
        assert(strstr(text, "mono") && !strstr(text, "stereo"));
        info.source_channels = 2;
        info.bitrate = 64000;
        assert(pcm_output(&context, &info, pcm, 64));
        assert(publishes == 3 && state.bitrate_kbps == 64 && state.channels == 2);

        // Failure and stale generation must not publish a format never played.
        output_error = -1;
        info.source_channels = 1;
        assert(!pcm_output(&context, &info, pcm, 64));
        assert(publishes == 3 && s_pcm_frames == 256);
        output_error = 0;
        context.generation = 41;
        const unsigned previous_writes = writes;
        assert(!pcm_output(&context, &info, pcm, 64));
        assert(writes == previous_writes && publishes == 3);
        context.generation = 42;

        // Genuine stereo PCM still uses two samples per frame.
        info.channels = expected_pcm_channels = info.source_channels = 2;
        assert(pcm_output(&context, &info, pcm, 128));
        assert(s_pcm_frames == 320 && state.channels == 2);
        assert(!critical_depth);
    }
    // HE-AAC source metadata must not change the PCM clock or frame accounting.
    output_context_t context = {.generation = 42, .codec_kind = HELIX_CODEC_AAC};
    helix_stream_info_t info = {22050, 48000, 1, 16, 2, 44100};
    expected_pcm_channels = 1;
    s_pcm_frames = publishes = 0;
    assert(pcm_output(&context, &info, pcm, 64));
    assert(s_pcm_rate == 22050 && state.sample_rate_hz == 44100 && s_pcm_frames == 64);
    char text[64];
    format_stream(&state, text, sizeof(text));
    assert(!strcmp(text, "AAC 48 kbps 44.1 kHz stereo"));
    info.source_sample_rate = 22050; // Following AAC-LC stream, same PCM format.
    assert(pcm_output(&context, &info, pcm, 64));
    assert(publishes == 2 && state.sample_rate_hz == 22050 && s_pcm_frames == 128);
    format_stream(&state, text, sizeof(text));
    assert(!strcmp(text, "AAC 48 kbps 22.05 kHz stereo"));
    puts("Stream metadata PASS: MP3/AAC/Opus stereo->mono->stereo, PCM stride, dedup and failure paths");
}
