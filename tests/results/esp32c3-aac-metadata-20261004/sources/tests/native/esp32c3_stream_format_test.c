#include <assert.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "native_state.h"
#include "audio_completion.h"
#include "custom_flac_adapter.h"
#include "custom_legacy_adapter.h"

#define CONFIG_YORADIO_FLAC_DECODER_CUSTOM 1
#define YORADIO_CUSTOM_LEGACY_DECODER 1
#define PCM_PACKET_DATA_SIZE 3584
#define ESP_AUDIO_ERR_OK 0
#ifndef NATIVE_AAC_PLUS_ENABLED
#define NATIVE_AAC_PLUS_ENABLED true
#endif
#define ESP_LOGW(...) ((void)0)
typedef enum { NATIVE_CODEC_AUTO, NATIVE_CODEC_MP3, NATIVE_CODEC_AAC,
               NATIVE_CODEC_FLAC, NATIVE_CODEC_OGG } native_codec_t;
typedef struct {
    uint32_t sample_rate;
    uint8_t bits_per_sample, channel;
    uint32_t bitrate;
} esp_audio_simple_dec_info_t;

static native_state_t state;
static native_state_t *s_state = &state;
static atomic_uint s_generation;
static void *s_pcm;
static uint32_t packet_rate;
static unsigned packet_channels, packet_bits, packets, packet_bytes;
static bool fail_get_info;
static esp_audio_simple_dec_info_t next_info;
static const char *next_aac_label="AAC";
static unsigned next_aac_channels;

size_t strlcpy(char *to, const char *from, size_t capacity) {
    size_t length = strlen(from);
    if (capacity) {
        size_t copied = length < capacity - 1 ? length : capacity - 1;
        memcpy(to, from, copied);
        to[copied] = 0;
    }
    return length;
}

static int xRingbufferSendAcquire(void *ring, void **packet, size_t size,
                                  unsigned timeout) {
    (void)ring; (void)timeout;
    *packet = calloc(1, size);
    assert(*packet);
    return pdTRUE;
}
static int xRingbufferSendComplete(void *ring, void *packet);
static void state_set_decoder_bitrate(uint32_t generation, uint32_t bitrate) {
    native_state_set_bitrate(s_state, generation, bitrate / 1000);
}
static unsigned native_audio_output_get_volume(void) { return 42; }
static int native_audio_output_get_balance(void) { return 0; }
static unsigned audio_service_buffer_fill_percent(void) { return 50; }
static unsigned radio_control_current_item(void) { return 1; }
static bool display_settings_get_station_uppercase(void) { return false; }
static void radio_control_current_name(char *name, size_t size) {
    strlcpy(name, s_state->station, size);
}
static void log_runtime_memory(const char *unused) { (void)unused; }
static int esp_audio_simple_dec_get_info(void *decoder,
                                         esp_audio_simple_dec_info_t *info) {
    (void)decoder;
    *info = next_info;
    return fail_get_info ? -1 : 0;
}
typedef int esp_audio_err_t;
static int native_aac_decoder_get_info(void *decoder,
                                       esp_audio_simple_dec_info_t *info) {
    return esp_audio_simple_dec_get_info(decoder, info);
}
static const char *native_aac_decoder_label(void *decoder,
    const esp_audio_simple_dec_info_t *info, bool *format_is_pcm) {
    (void)decoder; (void)info;
    *format_is_pcm = !next_aac_channels;
    return next_aac_label;
}
static unsigned native_aac_decoder_source_channels(void *decoder) {
    (void)decoder;return next_aac_channels;
}

#include "production.inc"

static int xRingbufferSendComplete(void *ring, void *data) {
    (void)ring;
    pcm_packet_t *packet = data;
    assert(packet->generation == atomic_load(&s_generation));
    packet_rate = packet->sample_rate;
    packet_channels = packet->channels;
    packet_bits = packet->bits_per_sample;
    assert(packet->data_size % (packet_bits / 8 * packet_channels) == 0);
    ++packets;
    packet_bytes += packet->data_size;
    free(data);
    return pdTRUE;
}

static void begin(unsigned generation) {
    atomic_store(&s_generation, generation);
    native_state_begin_stream(s_state, generation);
}

int main(void) {
    native_state_init(s_state);
    begin(1);
    esp_audio_simple_dec_info_t cached = {0};
    bool ready = false;
    decode_stats_t stats = {.codec = NATIVE_CODEC_MP3};
    custom_legacy_output_context_t legacy = {1, &stats, &cached, &ready};
    custom_flac_output_context_t flac = {1, &stats, &cached, &ready};
    uint8_t pcm[4608] = {0};
    custom_legacy_info_t info = {.sample_rate = 44100, .bits_per_sample = 16,
        .channels = 2, .bitrate = 128000, .stream_sample_rate = 44100,
        .stream_channels = 2};
    assert(custom_legacy_output(&legacy, &info, pcm, sizeof(pcm)));
    assert(packet_rate == 44100 && packet_channels == 2 && packet_bits == 16);
    assert(strcmp(state.stream_format, "MP3 44.1 kHz stereo") == 0);
    assert(stats.audio_us == 1152ULL * 1000000 / 44100);

    native_state_t oled_snapshot;
    native_state_snapshot(s_state, &oled_snapshot);
    webui_status_key_t first, unchanged, changed;
    capture_status_key(&first);
    assert(custom_legacy_output(&legacy, &info, pcm, sizeof(pcm)));
    capture_status_key(&unchanged);
    assert(memcmp(&first, &unchanged, sizeof(first)) == 0);

    // The same stream and bitrate, but a different rate and channel layout.
    info.sample_rate = info.stream_sample_rate = 22050;
    info.channels = info.stream_channels = 1;
    assert(custom_legacy_output(&legacy, &info, pcm, sizeof(pcm)));
    assert(packet_rate == 22050 && packet_channels == 1);
    assert(state.bitrate_kbps == 128);
    capture_status_key(&changed);
    assert(memcmp(&first, &changed, sizeof(first)) != 0);
    char json[1280], text[96], frozen[96];
    format_status(json, sizeof(json)); // Also used for WebUI reconnect.
    assert(strstr(json, "MP3 22.05 kHz mono"));
    format_stream_details(&oled_snapshot, frozen, sizeof(frozen));
    assert(strcmp(frozen, "MP3 44.1 kHz stereo 128 kbps") == 0);
    format_stream_details(s_state, text, sizeof(text));
    assert(strcmp(text, "MP3 22.05 kHz mono 128 kbps") == 0);
    assert(!display_state_changed(s_state, &oled_snapshot));
    info.sample_rate = info.stream_sample_rate = 48000;
    info.channels = info.stream_channels = 2;
    assert(custom_legacy_output(&legacy, &info, pcm, sizeof(pcm)));
    assert(packet_rate == 48000 && packet_channels == 2);

    // Downmix describes PCM only. MP3 source still has two channels.
    info.channels = 1;
    assert(custom_legacy_output(&legacy, &info, pcm, sizeof(pcm)));
    assert(state.channels == 2 && packet_channels == 1);

    // HE-AAC nominal frequency must never change PCM timing/sizing.
    stats.codec = NATIVE_CODEC_AAC;
    info.sample_rate = 22050;
    info.stream_sample_rate = 44100;
    info.channels = info.stream_channels = 1;
    info.aac_sbr = info.aac_profile_known = info.channels_are_core = true;
    info.aac_profile = 1;
    stats.audio_us = 0;
    assert(custom_legacy_output(&legacy, &info, pcm, 2048));
    assert(strcmp(state.stream_format, "HE-AAC 44.1 kHz core mono") == 0);
    assert(state.pcm_sample_rate_hz == 22050 && packet_rate == 22050);
    assert(stats.audio_us == 1024ULL * 1000000 / 22050);
    info.aac_sbr = info.channels_are_core = false;
    info.stream_sample_rate = info.sample_rate;
    assert(custom_legacy_output(&legacy, &info, pcm, 2048));
    assert(strcmp(state.stream_format, "AAC-LC 22.05 kHz mono") == 0);

    // FLAC callbacks must refresh all PCM fields, including bit depth.
    custom_flac_info_t fi = {.sample_rate = 48000, .bits_per_sample = 16,
                             .channels = 2, .bitrate = 128000};
    assert(custom_flac_output(&flac, &fi, pcm, sizeof(pcm)));
    fi.sample_rate = 32000; fi.bits_per_sample = 24; fi.channels = 1;
    assert(custom_flac_output(&flac, &fi, pcm, sizeof(pcm)));
    assert(packet_rate == 32000 && packet_channels == 1 && packet_bits == 24);
    assert(state.bits_per_sample == 24);

    next_info = (esp_audio_simple_dec_info_t){44100, 16, 2, 128000};
    run_espressif_frame(1, NATIVE_CODEC_MP3, &cached);
    assert(packet_rate == 44100 && packet_channels == 2);
    next_info.sample_rate = 22050; next_info.channel = 1;
    run_espressif_frame(1, NATIVE_CODEC_MP3, &cached);
    assert(packet_rate == 22050 && packet_channels == 1);
    next_info.sample_rate = 48000; next_info.channel = 2;
    run_espressif_frame(1, NATIVE_CODEC_MP3, &cached);
    assert(packet_rate == 48000 && packet_channels == 2);
    run_espressif_frame(1, NATIVE_CODEC_AAC, &cached);
    assert(strcmp(state.stream_format, "AAC PCM 48 kHz stereo") == 0);
    // Native HE mono duplicates PCM into L/R; UI describes the source while
    // packet routing still follows the actual two-channel PCM buffer.
    next_aac_label="HE-AAC";next_aac_channels=1;next_info.sample_rate=32000;
    run_espressif_frame(1, NATIVE_CODEC_AAC, &cached);
    assert(strcmp(state.stream_format,"HE-AAC 32 kHz mono")==0);
    assert(state.channels==1 && state.pcm_channels==2 && packet_channels==2);
    format_status(json,sizeof(json));assert(strstr(json,"HE-AAC 32 kHz mono"));
    format_stream_details(s_state,text,sizeof(text));assert(strstr(text,"mono"));
    next_aac_label="HE-AACv2";next_aac_channels=2;next_info.sample_rate=44100;
    run_espressif_frame(1,NATIVE_CODEC_AAC,&cached);
    assert(strcmp(state.stream_format,"HE-AACv2 44.1 kHz stereo")==0);
    assert(state.channels==2 && state.pcm_channels==2 && packet_channels==2);
    unsigned sent = packets;
    fail_get_info = true;
    run_espressif_frame(1, NATIVE_CODEC_MP3, &cached);
    assert(packets == sent);
    fail_get_info = false;
    next_info.sample_rate = 0;
    run_espressif_frame(1, NATIVE_CODEC_MP3, &cached);
    assert(packets == sent);

    begin(2);
    native_state_set_audio(s_state, 2, false, "stopped");
    native_state_begin_stream(s_state, 1); // A delayed earlier Play command.
    assert(state.audio_generation == 2);
    assert(!custom_legacy_output(&legacy, &info, pcm, 2048));
    native_state_set_bitrate(s_state, 1, 333);
    native_state_set_audio(s_state, 1, true, "old stream");
    assert(!state.audio_running && !state.sample_rate_hz && !state.channels);
    assert(!state.bits_per_sample && !state.pcm_sample_rate_hz && !state.pcm_channels);
    assert(!state.bitrate_kbps && !state.codec[0]);
    format_status(json, sizeof(json));
    assert(strstr(json, "stopped") && !strstr(json, "kHz"));
    assert(display_state_changed(s_state, &oled_snapshot));
    begin(3);
    legacy.generation = 3;
    info.sample_rate = info.stream_sample_rate = 11025;
    assert(custom_legacy_output(&legacy, &info, pcm, 2048));
    format_status(json, sizeof(json));
    assert(strstr(json, "AAC-LC 11.025 kHz mono"));
    assert(!send_pcm(1, &cached, pcm, sizeof(pcm)));
    puts("PASS: callbacks/PCM, format changes, WebUI keys/reconnect, OLED snapshots, AAC rates, stop/restart");
    return 0;
}
