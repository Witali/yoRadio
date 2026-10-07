#include <assert.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "native_state.h"
#include "audio_completion.h"

typedef enum { NATIVE_CODEC_AUTO, NATIVE_CODEC_MP3, NATIVE_CODEC_AAC } native_codec_t;
typedef struct { uint32_t sample_rate; uint8_t bits_per_sample, channel; } esp_audio_simple_dec_info_t;
typedef struct { unsigned unused; } decode_stats_t;
#define PCM_PACKET_DATA_SIZE 3584
static native_state_t state;
static native_state_t *s_state = &state;
static atomic_uint s_generation;
static void *s_encoded = (void *)1, *s_pcm = (void *)2;
static void *encoded[8], *pcm[8];
static unsigned encoded_count, pcm_count;
static bool cancel_on_wait;

size_t strlcpy(char *to, const char *from, size_t capacity) {
    size_t length = strlen(from);
    if (capacity) { size_t n = length < capacity-1 ? length : capacity-1;
        memcpy(to, from, n); to[n] = 0; }
    return length;
}
static int xRingbufferSendAcquire(void *ring, void **packet, size_t size, unsigned timeout) {
    (void)ring; (void)timeout;
    if (cancel_on_wait) { ++s_generation; cancel_on_wait = false; return 0; }
    *packet = malloc(size); assert(*packet);
    memset(*packet, 0xa5, size); // Real ring memory is reused, not zero-filled.
    return pdTRUE;
}
static int xRingbufferSendComplete(void *ring, void *packet) {
    if (ring == s_encoded) { assert(encoded_count < 8); encoded[encoded_count++] = packet; }
    else { assert(pcm_count < 8); pcm[pcm_count++] = packet; }
    return pdTRUE;
}
static void vRingbufferReturnItem(void *ring, void *packet) { (void)ring; free(packet); }
static void dispose_http_client(void *client) { (void)client; }
static void network_service_set_streaming(bool running) { assert(!running); }
#include "pipeline_profile.h"
#include "production.inc"

static void begin(uint32_t generation) {
    atomic_store(&s_generation, generation);
    native_state_begin_stream(s_state, generation);
    native_state_set_audio(s_state, generation, true, "connected");
}
static void delayed_frame(uint32_t generation) {
    // Full-rate HE-AAC is deliberately a late callback, after HTTP EOF.
    native_stream_info_t info = {.codec="HE-AAC", .sample_rate_hz=48000,
        .channels=2, .bits_per_sample=16, .pcm_sample_rate_hz=48000, .pcm_channels=2};
    native_state_set_stream_info(s_state, generation, &info);
    esp_audio_simple_dec_info_t layout = {48000,16,2};
    uint8_t samples[4096] = {0};
    assert(send_pcm(NULL, generation, &layout, samples, sizeof(samples)));
}
static void drain_pcm(void) {
    for (unsigned i=0; i<pcm_count; ++i) {
        pcm_packet_t *packet = pcm[i];
        if (packet->end_of_stream) {
            assert(i == pcm_count-1 && !packet->data_size);
            finish_output(packet);
        } else {
            assert(state.audio_running); // No premature stopped status.
            assert((uintptr_t)packet->data % 4 == 0);
            assert(packet->data_size && packet->sample_rate == 48000);
            free(packet);
        }
    }
    pcm_count = 0;
}

int main(void) {
    native_state_init(s_state);
    begin(1);
    finish_network(1, false);
    assert(state.audio_running && encoded_count == 1 && pcm_count == 0);
    delayed_frame(1);
    assert(state.audio_running && strcmp(state.codec,"HE-AAC") == 0);
    return_decoded_packet(encoded[--encoded_count], 0);
    assert(state.audio_running); // Decoder EOS waits behind both PCM packets.
    drain_pcm();
    assert(!state.audio_running && !state.sample_rate_hz && !state.pcm_sample_rate_hz);
    assert(strcmp(state.stream_format,"stream ended") == 0);

    begin(2);
    finish_network(2, true);
    delayed_frame(2);
    return_decoded_packet(encoded[--encoded_count], 0);
    drain_pcm();
    assert(!state.audio_running && strcmp(state.stream_format,"stream read failed") == 0);

    begin(3);
    finish_network(3, false);
    native_state_set_audio(s_state, 3, false, "decode failed");
    return_decoded_packet(encoded[--encoded_count], 3);
    assert(pcm_count == 0 && strcmp(state.stream_format,"decode failed") == 0);

    begin(4);
    assert(send_pcm_end(4, AUDIO_END_EOF));
    begin(5); // Play races the output task after its generation check.
    finish_output(pcm[--pcm_count]);
    assert(state.audio_running && strcmp(state.stream_format,"connected") == 0);
    assert(!send_pcm_end(4, AUDIO_END_EOF));
    cancel_on_wait = true;
    assert(!send_pcm_end(5, AUDIO_END_EOF));
    assert(pcm_count == 0);

    begin(7); // Empty stream also terminates without a PCM format.
    finish_network(7, false);
    return_decoded_packet(encoded[--encoded_count], 0);
    drain_pcm();
    assert(!state.audio_running && strcmp(state.stream_format,"stream ended") == 0);
    begin(8);
    assert(send_pcm_end(8, AUDIO_END_UNAVAILABLE));
    drain_pcm();
    assert(!state.audio_running && strcmp(state.stream_format,"station unavailable") == 0);
    puts("PASS: delayed HE-AAC PCM, ordered EOF, errors, empty stream, stale completion and cancellation");
    return 0;
}
