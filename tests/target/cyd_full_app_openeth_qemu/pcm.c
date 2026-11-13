#include <inttypes.h>
#include <stdio.h>

#include "native_audio_output.h"

/* Both wrappers run on the real audio output task. Driver priming and idle
 * writes do not pass through the PCM API. */
static uint64_t pcm_frames;
static uint64_t last_report;

esp_err_t __real_native_audio_output_write_pcm(const uint8_t *data, size_t size,
                                              uint8_t bits, uint8_t channels);
esp_err_t __wrap_native_audio_output_write_pcm(const uint8_t *data, size_t size,
                                              uint8_t bits, uint8_t channels) {
    esp_err_t result = __real_native_audio_output_write_pcm(data, size, bits, channels);
    if (result == ESP_OK && bits == 16 && channels == 2 && size % 4 == 0) {
        pcm_frames += size / 4;
        if (!last_report || pcm_frames - last_report >= 4800) {
            printf("CYD_OPENETH_PCM_PROGRESS frames=%" PRIu64 "\n", pcm_frames);
            last_report = pcm_frames;
        }
    }
    return result;
}

esp_err_t __real_native_audio_output_flush_pcm(void);
esp_err_t __wrap_native_audio_output_flush_pcm(void) {
    esp_err_t result = __real_native_audio_output_flush_pcm();
    printf("CYD_OPENETH_PCM_FLUSH frames=%" PRIu64 " status=%d\n", pcm_frames, (int)result);
    return result;
}
