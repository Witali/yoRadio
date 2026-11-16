#include <inttypes.h>
#include <stdio.h>

#include "native_audio_output.h"

#ifdef CYD_OPENETH_PCM_MD5
#include "esp_rom_md5.h"

static md5_context_t pcm_md5;
#endif

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
#ifdef CYD_OPENETH_PCM_MD5
        if (!pcm_frames) {
            esp_rom_md5_init(&pcm_md5);
        }
        esp_rom_md5_update(&pcm_md5, data, size);
#endif
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
#ifdef CYD_OPENETH_PCM_MD5
    if (result == ESP_OK && pcm_frames) {
        static const char hex[] = "0123456789abcdef";
        md5_context_t snapshot = pcm_md5;
        uint8_t digest[ESP_ROM_MD5_DIGEST_LEN];
        char text[2 * sizeof(digest) + 1];
        esp_rom_md5_final(digest, &snapshot);
        for (size_t i = 0; i < sizeof(digest); ++i) {
            text[2 * i] = hex[digest[i] >> 4];
            text[2 * i + 1] = hex[digest[i] & 15];
        }
        text[sizeof(text) - 1] = '\0';
        printf("CYD_OPENETH_PCM_MD5 %s\n", text);
    }
#endif
    return result;
}
