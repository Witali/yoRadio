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

#ifdef CYD_OPENETH_RECLAIM_PROBE
void cyd_openeth_note_playback(void);
#endif

#ifdef CYD_OPENETH_PCM_CHANNEL_METRICS
static struct {
    uint64_t energy;
    uint32_t crossings;
    int8_t last_sign;
} metrics[8];
static pcm_channel_layout current_layout;
static uint8_t layout_channels;
static uint8_t measured_channels;

esp_err_t __real_native_audio_output_set_channel_layout(pcm_channel_layout layout,
                                                        uint8_t channels);
esp_err_t __wrap_native_audio_output_set_channel_layout(pcm_channel_layout layout,
                                                        uint8_t channels) {
    esp_err_t result = __real_native_audio_output_set_channel_layout(layout, channels);
    if (result == ESP_OK) {
        current_layout = layout;
        layout_channels = channels;
    }
    return result;
}

static bool measure_channels(const uint8_t *data, size_t size, uint8_t channels) {
    if (channels < 3 || channels > 8 || current_layout != PCM_CHANNEL_LAYOUT_VORBIS ||
        channels != layout_channels || (measured_channels && measured_channels != channels)) {
        return false;
    }

    measured_channels = channels;
    for (size_t offset = 0; offset < size;) {
        for (uint8_t channel = 0; channel < channels; ++channel, offset += 2) {
            int32_t sample = (int16_t)((uint16_t)data[offset] |
                                       ((uint16_t)data[offset + 1] << 8));
            metrics[channel].energy += (uint32_t)(sample * sample);
            if (sample) {
                int8_t sign = sample > 0 ? 1 : -1;
                if (metrics[channel].last_sign && sign != metrics[channel].last_sign) {
                    ++metrics[channel].crossings;
                }
                metrics[channel].last_sign = sign;
            }
        }
    }
    return true;
}
#endif

esp_err_t __real_native_audio_output_write_pcm(const uint8_t *data, size_t size,
                                              uint8_t bits, uint8_t channels);
esp_err_t __wrap_native_audio_output_write_pcm(const uint8_t *data, size_t size,
                                              uint8_t bits, uint8_t channels) {
    esp_err_t result = __real_native_audio_output_write_pcm(data, size, bits, channels);
    const size_t frame_bytes = 2u * channels;
    if (result != ESP_OK || bits != 16 || !frame_bytes || size % frame_bytes) {
        return result;
    }
    if (channels != 2) {
#ifdef CYD_OPENETH_PCM_CHANNEL_METRICS
        if (!measure_channels(data, size, channels)) {
            return result;
        }
#else
        return result;
#endif
    }
#ifdef CYD_OPENETH_PCM_MD5
    if (!pcm_frames) {
        esp_rom_md5_init(&pcm_md5);
    }
    esp_rom_md5_update(&pcm_md5, data, size);
#endif
    pcm_frames += size / frame_bytes;
#ifdef CYD_OPENETH_RECLAIM_PROBE
    if (channels == 2) cyd_openeth_note_playback();
#endif
    if (!last_report || pcm_frames - last_report >= 4800) {
        printf("CYD_OPENETH_PCM_PROGRESS frames=%" PRIu64 "\n", pcm_frames);
        last_report = pcm_frames;
    }
    return result;
}

esp_err_t __real_native_audio_output_flush_pcm(void);
esp_err_t __wrap_native_audio_output_flush_pcm(void) {
    esp_err_t result = __real_native_audio_output_flush_pcm();
    printf("CYD_OPENETH_PCM_FLUSH frames=%" PRIu64 " status=%d\n", pcm_frames, (int)result);
#ifdef CYD_OPENETH_PCM_CHANNEL_METRICS
    for (uint8_t channel = 0; channel < measured_channels; ++channel) {
        printf("CYD_OPENETH_PCM_CHANNEL index=%u energy=%" PRIu64 " crossings=%" PRIu32 "\n",
               (unsigned)channel, metrics[channel].energy, metrics[channel].crossings);
    }
#endif
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
