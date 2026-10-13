// QEMU-only sink for the actual production decoder and PCM queue tasks.
// Capture before gain/resampling/DMA; do not infer hardware timing from this.
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "esp_system.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "native_audio_output.h"
#include "native_state.h"

enum { CAPTURE_CHUNK_BYTES = 128 };
static uint32_t sample_rate, sequence;
static size_t captured_bytes;
static unsigned flushes;

esp_err_t __wrap_native_audio_output_init(void) { return ESP_OK; }

esp_err_t __wrap_native_audio_output_configure(uint32_t rate) {
    assert(rate >= 8000 && rate <= 192000);
    sample_rate = rate;
    return ESP_OK;
}

esp_err_t __wrap_native_audio_output_write_pcm(uint8_t *data, size_t size,
        uint8_t bits, uint8_t channels) {
    assert(data && sample_rate && bits == 16 && channels && channels <= 2);
    assert(size && size % (channels * sizeof(int16_t)) == 0);
    assert(!flushes);
    static const char hex[] = "0123456789abcdef";
    char encoded[CAPTURE_CHUNK_BYTES * 2 + 1];
    for (size_t offset = 0; offset < size;) {
        size_t count = size - offset;
        if (count > CAPTURE_CHUNK_BYTES) count = CAPTURE_CHUNK_BYTES;
        for (size_t i = 0; i < count; ++i) {
            uint8_t byte = data[offset + i];
            encoded[2 * i] = hex[byte >> 4];
            encoded[2 * i + 1] = hex[byte & 15];
        }
        encoded[2 * count] = '\0';
        printf("PIPE_PCM seq=%lu offset=%u rate=%lu channels=%u hex=%s\n",
               (unsigned long)sequence++, (unsigned)captured_bytes,
               (unsigned long)sample_rate, channels, encoded);
        captured_bytes += count;
        offset += count;
    }
    // Keep queue backpressure and allow the decoder to reuse its workspace.
    vTaskDelay(1);
    return ESP_OK;
}

esp_err_t __wrap_native_audio_output_flush_pcm(void) {
    ++flushes;
    return ESP_OK;
}

void __real_native_state_set_audio(native_state_t *, uint32_t, bool, const char *);
void __wrap_native_state_set_audio(native_state_t *state, uint32_t generation,
        bool running, const char *status) {
    __real_native_state_set_audio(state, generation, running, status);
    if (!running && !strcmp(status, "stream ended")) {
        assert(captured_bytes && flushes == 1);
        printf("PIPE_PCM_END generation=%lu bytes=%u chunks=%lu flushes=%u\n",
               (unsigned long)generation, (unsigned)captured_bytes,
               (unsigned long)sequence, flushes);
        fflush(stdout);
        vTaskDelay(pdMS_TO_TICKS(100));
        esp_restart(); // QEMU -no-reboot exits after the verified EOF marker.
    }
}
