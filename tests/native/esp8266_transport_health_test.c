#include "audio_service.h"
#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#include <errno.h>
typedef uint32_t TickType_t;
static unsigned critical_depth;
#define taskENTER_CRITICAL() (++critical_depth)
#define taskEXIT_CRITICAL() do { assert(critical_depth); --critical_depth; } while (0)
#define portTICK_PERIOD_MS 1U
static TickType_t xTaskGetTickCount(void) { return 1000; }
static unsigned s_audio_task = 1;
static unsigned uxTaskGetStackHighWaterMark(unsigned task) {
    assert(task == 1 && critical_depth == 0); return 1648;
}
/* HEALTH */
/* ADVANCE */
/* FILL_ENUM */
#define helix_codec_buffered(codec) (codec)
static void terminal_fill(int filled, bool *was_ended, unsigned bytes) {
    bool ended = *was_ended;
    int end_error = 0;
#if YORADIO_ESP8266_OPUS_STREAM_TEST
    const struct { uint32_t generation; } command = {s_generation};
    unsigned codec = bytes;
#else
    (void)bytes;
#endif
    /* TERMINAL_FILL */
    *was_ended = ended;
    (void)end_error;
}
int main(void) {
    _Static_assert(sizeof(audio_service_health_t) ==
        32U + 16U * YORADIO_ESP8266_OPUS_STREAM_TEST, "Exactly four diagnostic words");
    audio_service_health_t health;
    s_generation = 7; s_rx_bytes = 1234; s_pcm_frames = 960;
    s_pcm_rate = 48000; s_rx_tick = 999; s_pcm_tick = 998;
    audio_service_health(NULL); audio_service_health(&health);
    assert(health.generation == 7 && health.rx_bytes == 1234 && health.pcm_frames == 960);
    assert(health.rx_age_ms == 1 && health.pcm_age_ms == 2 && health.stack_free == 1648);
    bool ended = false;
    errno = ETIMEDOUT; terminal_fill(STREAM_FILL_TIMEOUT, &ended, 777);
    assert(ended && critical_depth == 0);
#if YORADIO_ESP8266_OPUS_STREAM_TEST
    for (unsigned phase = AUDIO_TRANSPORT_IDLE; phase <= AUDIO_TRANSPORT_CLOSE; ++phase) {
        audio_transport_phase((audio_transport_phase_t)phase);
        audio_service_health(&health);
        assert(health.transport_phase == phase && health.transport_result == STREAM_FILL_TIMEOUT);
        assert(health.transport_errno == ETIMEDOUT && health.input_bytes == 777);
    }
    /* Actual ended-queue branch must not replace TIMEOUT with synthetic EOF. */
    errno = EIO; terminal_fill(STREAM_FILL_EOF, &ended, 0);
    audio_service_health(&health);
    assert(health.transport_result == STREAM_FILL_TIMEOUT && health.transport_errno == ETIMEDOUT);
    assert(health.input_bytes == 777);
    assert(advance_generation() == 8);
    audio_transport_latch(7, STREAM_FILL_ERROR, ENOMEM, 1); /* Obsolete owner cannot relatch. */
    audio_service_health(&health);
    assert(health.transport_phase == AUDIO_TRANSPORT_CLOSE); /* Stop queued, close still active. */
    assert(health.transport_result == INT32_MIN && health.transport_errno == 0 && health.input_bytes == 0);
    ended = false; errno = EIO; terminal_fill(STREAM_FILL_EOF, &ended, 5);
    audio_service_health(&health);
    assert(health.transport_result == STREAM_FILL_EOF && health.transport_errno == 0 && health.input_bytes == 5);
    ended = false; errno = ECONNRESET; terminal_fill(STREAM_FILL_ERROR, &ended, 999);
    audio_service_health(&health);
    assert(health.transport_result == STREAM_FILL_ERROR && health.transport_errno == ECONNRESET);
#else
    unsigned evaluated = 0;
    audio_transport_latch(++evaluated, ++evaluated, ++evaluated, ++evaluated);
    audio_transport_phase(++evaluated);
    assert(evaluated == 0 && advance_generation() == 8);
#endif
    assert(critical_depth == 0);
    printf("transport health PASS: guard=%d, health=%u bytes, production calls erased\n",
        YORADIO_ESP8266_OPUS_STREAM_TEST, (unsigned)sizeof(health));
    return 0;
}
