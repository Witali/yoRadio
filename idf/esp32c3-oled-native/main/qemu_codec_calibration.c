// Optional second fixture placed in the emulator-only app1 flash region.
#include <assert.h>
#include <inttypes.h>
#include <stdlib.h>
#include "esp_audio_simple_dec.h"
#include "esp_mp3_dec.h"
#include "esp_flac_dec.h"
#include "esp_vorbis_dec.h"
#include "esp_opus_dec.h"
#include "esp_log.h"
#include "esp_heap_caps.h"
#include "esp_partition.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

typedef struct {
    const char *name;
    esp_audio_simple_dec_type_t type;
    esp_audio_err_t (*register_decoder)(void);
    uint32_t bytes;
    struct { uint32_t calls, consumed, pcm; } windows[2];
} fixture_t;

static const fixture_t fixtures[] = {
    {"mp3", ESP_AUDIO_SIMPLE_DEC_TYPE_MP3, esp_mp3_dec_register, 441645,
     {{309, 202605, 972288}, {307, 200640, 963072}}},
    {"flac", ESP_AUDIO_SIMPLE_DEC_TYPE_FLAC, esp_flac_dec_register, 1771852,
     {{456, 823869, 976896}, {451, 816013, 976896}}},
    {"vorbis", ESP_AUDIO_SIMPLE_DEC_TYPE_OGG, esp_vorbis_dec_register, 703584,
     {{246, 325632, 964864}, {235, 317440, 962560}}},
    {"opus", ESP_AUDIO_SIMPLE_DEC_TYPE_OGG, esp_opus_dec_register, 706319,
     {{255, 327680, 975360}, {251, 321536, 963840}}},
};

static inline uint32_t instruction_count(void) {
    uint32_t value;
    __asm__ volatile("csrr %0, minstret" : "=r"(value) :: "memory");
    return value;
}

void qemu_codec_calibration(void) {
    const esp_partition_t *partition = esp_partition_find_first(
        ESP_PARTITION_TYPE_APP, ESP_PARTITION_SUBTYPE_APP_OTA_1, NULL);
    assert(partition);
    uint32_t header[4];
    assert(esp_partition_read(partition, 0, header, sizeof(header)) == ESP_OK);
    if (header[0] != 0x5143414c) return;
    assert(header[1] >= 1 && header[1] <= 4);
    const fixture_t *fixture = &fixtures[header[1] - 1];
    assert(header[2] == fixture->bytes && header[2] <= partition->size - sizeof(header));
    assert(fixture->register_decoder() == ESP_AUDIO_ERR_OK);
    uint8_t *input = malloc(2048);
    assert(input);
    for (unsigned run = 1; run <= 3; ++run) {
        size_t pcm_size = 12288;
        uint8_t *pcm = malloc(pcm_size);
        assert(pcm);
        esp_audio_simple_dec_handle_t decoder = NULL;
        esp_audio_simple_dec_cfg_t cfg = {
            .dec_type = fixture->type, .dec_cfg = NULL, .cfg_size = 0, .use_frame_dec = false,
        };
        assert(esp_audio_simple_dec_open(&cfg, &decoder) == ESP_AUDIO_ERR_OK);
        unsigned window = 0, calls = 0, consumed = 0, pcm_bytes = 0;
        uint64_t instructions = 0;
        for (size_t pos = 0; pos < fixture->bytes && window < 2;) {
            size_t size = fixture->bytes - pos;
            if (size > 2048) size = 2048;
            assert(esp_partition_read(partition, sizeof(header) + pos, input, size) == ESP_OK);
            esp_audio_simple_dec_raw_t raw = {.buffer = input, .len = size};
            while (raw.len && window < 2) {
                esp_audio_simple_dec_out_t out = {.buffer = pcm, .len = pcm_size};
                raw.consumed = 0;
                uint32_t before = instruction_count();
                esp_audio_err_t result = esp_audio_simple_dec_process(decoder, &raw, &out);
                instructions += (uint32_t)(instruction_count() - before);
                ++calls;
                // Match the historical grow-on-demand PCM path. Count the
                // decoder's BUFFER_NOT_ENOUGH call, but not realloc itself.
                if (result == ESP_AUDIO_ERR_BUFF_NOT_ENOUGH) {
                    assert(out.needed_size > pcm_size);
                    uint8_t *larger = realloc(pcm, out.needed_size);
                    assert(larger);
                    pcm = larger;
                    pcm_size = out.needed_size;
                    continue;
                }
                assert(result == ESP_AUDIO_ERR_OK);
                assert(raw.consumed <= raw.len && (raw.consumed || out.decoded_size));
                consumed += raw.consumed;
                pcm_bytes += out.decoded_size;
                raw.buffer += raw.consumed;
                raw.len -= raw.consumed;
                if (out.decoded_size) {
                    esp_audio_simple_dec_info_t info;
                    assert(esp_audio_simple_dec_get_info(decoder, &info) == ESP_AUDIO_ERR_OK);
                    assert(info.sample_rate == 48000 && info.channel == 2 && info.bits_per_sample == 16);
                }
                if (pcm_bytes >= fixture->windows[window].pcm) {
                    ESP_LOGI("qemu_cal", "QEMU_CODEC_CAL codec=%s run=%u window=%u"
                             " instructions=%" PRIu64 " calls=%u consumed=%u pcm=%u",
                             fixture->name, run, window + 1, instructions, calls, consumed, pcm_bytes);
                    assert(pcm_bytes == fixture->windows[window].pcm);
                    assert(calls == fixture->windows[window].calls);
                    assert(consumed == fixture->windows[window].consumed);
                    ++window;
                    calls = consumed = pcm_bytes = 0;
                    instructions = 0;
                }
            }
            pos += size;
            vTaskDelay(1);
        }
        assert(window == 2);
        assert(heap_caps_check_integrity_all(true));
        esp_audio_simple_dec_close(decoder);
        free(pcm);
        assert(heap_caps_check_integrity_all(true));
    }
    free(input);
    ESP_LOGI("qemu_cal", "QEMU_CODEC_STACK_FREE bytes=%u", (unsigned)uxTaskGetStackHighWaterMark(NULL));
    ESP_LOGI("qemu_cal", "QEMU_CODEC_CAL_PASS codec=%s", fixture->name);
}
