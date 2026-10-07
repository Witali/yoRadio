#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "native_aac_decoder.h"
#include "esp_aac_dec.h"

static unsigned opens, closes, frames;
static uint8_t expected[4][12];
static esp_audio_simple_dec_info_t current;

esp_audio_err_t esp_audio_simple_dec_open(esp_audio_simple_dec_cfg_t *cfg, void **out) {
    assert(cfg->use_frame_dec && cfg->cfg_size == sizeof(esp_aac_dec_cfg_t));
    assert(((esp_aac_dec_cfg_t *)cfg->dec_cfg)->aac_plus_enable);
    *out = malloc(1);
    ++opens;
    return *out ? ESP_AUDIO_ERR_OK : ESP_AUDIO_ERR_MEM_LACK;
}
void esp_audio_simple_dec_close(void *handle) { free(handle); ++closes; }
esp_audio_err_t esp_audio_simple_dec_process(void *handle,
    esp_audio_simple_dec_raw_t *raw, esp_audio_simple_dec_out_t *output) {
    assert(handle && raw->len == 12 && frames < 4);
    assert(memcmp(raw->buffer, expected[frames], 12) == 0);
    current = (esp_audio_simple_dec_info_t){
        .sample_rate = frames < 2 ? 44100 : 48000,
        .channel = frames < 2 ? 2 : 1, .bits_per_sample = 16,
    };
    ++frames;
    raw->consumed = raw->len;
    output->decoded_size = 1024 * 2 * current.channel;
    return ESP_AUDIO_ERR_OK;
}
esp_audio_err_t esp_audio_simple_dec_get_info(void *handle,
    esp_audio_simple_dec_info_t *info) {
    assert(handle); *info = current; return ESP_AUDIO_ERR_OK;
}

int main(void) {
    for (unsigned chunk = 1; chunk <= 53; ++chunk) {
        opens = closes = frames = 0;
        for (unsigned i = 0; i < 4; ++i) {
            uint8_t header[] = {0xff, 0xf1, 0x50, 0x80, 1, 0x9f, 0xfc};
            memcpy(expected[i], header, 7);
            memset(expected[i] + 7, 0x30 + i, 5);
        }
        // Private bit and VBR fullness must not recreate the decoder.
        expected[1][2] |= 2;
        expected[1][6] = 0;
        expected[2][2] = expected[3][2] = 0x4c; // 48 kHz
        expected[2][3] = expected[3][3] = 0x40; // mono
        expected[3][1] = 0xf0; // CRC present, same audio configuration
        uint8_t stream[55] = {0xff, 0xf1, 0xfc, 0, 0, 0, 0}; // invalid index/length
        memcpy(stream + 7, expected, sizeof(expected));
        uint8_t pcm[8192];
        native_aac_decoder_t *decoder = native_aac_decoder_create();
        assert(decoder);
        for (size_t offset = 0; offset < sizeof(stream);) {
            size_t size = sizeof(stream) - offset;
            if (size > chunk) size = chunk;
            esp_audio_simple_dec_raw_t raw = {.buffer = stream + offset, .len = size};
            while (raw.len) {
                esp_audio_simple_dec_out_t output = {.buffer = pcm, .len = 8};
                assert(native_aac_decoder_process(decoder, &raw, &output) == ESP_AUDIO_ERR_BUFF_NOT_ENOUGH);
                assert(raw.consumed == 0 && output.needed_size == sizeof(pcm));
                output.len = sizeof(pcm);
                assert(native_aac_decoder_process(decoder, &raw, &output) == ESP_AUDIO_ERR_OK);
                assert(raw.consumed > 0 && raw.consumed <= raw.len);
                raw.buffer += raw.consumed;
                raw.len -= raw.consumed;
                if (output.decoded_size) {
                    esp_audio_simple_dec_info_t info;
                    assert(native_aac_decoder_get_info(decoder, &info) == ESP_AUDIO_ERR_OK);
                    bool pcm_only = false;
                    assert(strcmp(native_aac_decoder_label(decoder, &info, &pcm_only), "AAC") == 0);
                    assert(pcm_only);
                }
            }
            offset += size;
        }
        assert(frames == 4 && opens == 2);
        native_aac_decoder_destroy(decoder);
        assert(opens == closes);
    }
    puts("PASS: AAC framing, 1..53-byte chunks, CRC, resync, buffer retry, configuration changes");
}
