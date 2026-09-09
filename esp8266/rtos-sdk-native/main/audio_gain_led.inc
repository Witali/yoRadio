/* Inline into the constant-channel I2S writers. Ordinary blocks have only
 * one LED flag check; selected blocks reuse samples already scaled in CPU
 * registers. No second PCM walk, timer lookup, allocation or per-frame lock. */
static inline __attribute__((always_inline)) int32_t output_gain_frame(
    int16_t *pcm, const uint8_t channels, uint32_t left_gain, uint32_t right_gain) {
    int32_t left = scale_sample(pcm[0], left_gain);
    pcm[0] = (int16_t)left;
    if (channels == 1) return left;
    int32_t right = scale_sample(pcm[1], right_gain);
    pcm[1] = (int16_t)right;
    return (left + right) / 2;
}

static inline __attribute__((always_inline)) void output_gain_with_led(
    int16_t *pcm, size_t frames, const uint8_t channels,
    uint32_t left_gain, uint32_t right_gain) {
    size_t frame = 0;
#if CONFIG_YORADIO_STATUS_LED
    if (status_led_capture_requested) {
        /* At most 32 peaks per window: every fourth of the first 128 frames.
         * All other samples are still scaled and played, without decimation. */
        size_t limit = frames < 128U ? frames : 128U;
        uint32_t peak = 0;
        while (frame < limit) {
            int32_t mono = output_gain_frame(pcm + frame * channels, channels, left_gain, right_gain);
            uint32_t magnitude = (uint32_t)(mono < 0 ? -mono : mono);
            if (magnitude > peak) peak = magnitude;
            ++frame;
            for (unsigned skipped = 0; skipped < 3U && frame < limit; ++skipped, ++frame)
                (void)output_gain_frame(pcm + frame * channels, channels, left_gain, right_gain);
        }
        status_led_publish_peak((uint16_t)peak);
    }
#endif
    for (; frame < frames; ++frame)
        (void)output_gain_frame(pcm + frame * channels, channels, left_gain, right_gain);
}
