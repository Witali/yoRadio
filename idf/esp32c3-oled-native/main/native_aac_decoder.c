#include "native_aac_decoder.h"

#include <stdlib.h>
#include <string.h>
#include "aac_decoder_config.h"
#include "codec_memory_trace.h"
#if CONFIG_FREERTOS_GENERATE_RUN_TIME_STATS
#include "cpu_profiler.h"
#define AAC_MEMORY(stage) cpu_profiler_memory(stage)
#else
#define AAC_MEMORY(stage) ((void)0)
#endif

// ADTS has a 13-bit frame length. Keep at most one complete encoded frame;
// network chunk boundaries must never become decoder reset boundaries.
struct native_aac_decoder {
    esp_audio_simple_dec_handle_t codec;
    size_t used;
    uint16_t signature;
    uint8_t data[8191];
};

native_aac_decoder_t *native_aac_decoder_create(void) {
    codec_memory_trace_dump("aac-before-adts");
    AAC_MEMORY("aac-before-adts");
    return calloc(1, sizeof(native_aac_decoder_t));
}

void native_aac_decoder_destroy(native_aac_decoder_t *decoder) {
    if (!decoder) return;
    if (decoder->codec) esp_audio_simple_dec_close(decoder->codec);
    codec_memory_trace_dump("aac-close");
    free(decoder);
}

esp_audio_err_t native_aac_decoder_process(native_aac_decoder_t *decoder,
    esp_audio_simple_dec_raw_t *raw, esp_audio_simple_dec_out_t *output) {
    if (!decoder || !raw || !output) return ESP_AUDIO_ERR_INVALID_PARAMETER;
    raw->consumed = 0;
    output->decoded_size = 0;
    // SBR stereo produces 2048 samples/channel. The SDK can split that frame
    // across calls for smaller buffers; keep one frame atomic here instead.
    if (output->len < 8192) {
        output->needed_size = 8192;
        return ESP_AUDIO_ERR_BUFF_NOT_ENOUGH;
    }
    for (;;) {
        size_t needed = 7;
        if (decoder->used >= 7) {
            const uint8_t *p = decoder->data;
            size_t header_size = (p[1] & 1) ? 7 : 9;
            size_t frame_size = ((p[3] & 3) << 11) | (p[4] << 3) | (p[5] >> 5);
            if (p[0] != 0xff || (p[1] & 0xf6) != 0xf0 ||
                ((p[2] >> 2) & 15) > 12 || frame_size < header_size) {
                // Resynchronize without trusting length bits in arbitrary data.
                memmove(decoder->data, decoder->data + 1, --decoder->used);
                continue;
            }
            needed = frame_size;
            if (decoder->used == needed) {
                bool opened = false;
                uint16_t signature = ((p[1] & 8) << 8) |
                    ((p[2] & 0xfd) << 2) | (p[3] >> 6);
                if (!decoder->codec || signature != decoder->signature) {
                    if (decoder->codec) esp_audio_simple_dec_close(decoder->codec);
                    codec_memory_trace_dump("aac-reopen-close");
                    decoder->codec = NULL;
                    AAC_MEMORY("aac-before-open");
                    esp_aac_dec_cfg_t aac = native_aac_decoder_config();
                    esp_audio_simple_dec_cfg_t config = {
                        .dec_type = ESP_AUDIO_SIMPLE_DEC_TYPE_AAC,
                        .dec_cfg = &aac, .cfg_size = sizeof(aac),
                        .use_frame_dec = true,
                    };
                    // Reapply AAC Plus too: the library retains SBR state
                    // across incompatible ADTS configurations otherwise.
                    esp_audio_err_t result = esp_audio_simple_dec_open(
                        &config, &decoder->codec);
                    codec_memory_trace_dump("aac-open");
                    if (result != ESP_AUDIO_ERR_OK) return result;
                    decoder->signature = signature;
                    opened = true;
                    AAC_MEMORY("aac-after-open");
                }
                esp_audio_simple_dec_raw_t frame = {
                    .buffer = decoder->data, .len = needed,
                };
                esp_audio_err_t result = esp_audio_simple_dec_process(
                    decoder->codec, &frame, output);
                codec_memory_trace_dump("aac-process");
                if (opened) AAC_MEMORY("aac-after-first-process");
                // Keep the frame for a larger PCM buffer retry. The caller
                // still advances input bytes already copied into our buffer.
                if (result != ESP_AUDIO_ERR_BUFF_NOT_ENOUGH) decoder->used = 0;
                return result;
            }
        }
        size_t available = raw->len - raw->consumed;
        if (!available) return ESP_AUDIO_ERR_OK;
        size_t count = needed - decoder->used;
        if (count > available) count = available;
        memcpy(decoder->data + decoder->used, raw->buffer + raw->consumed, count);
        decoder->used += count;
        raw->consumed += count;
    }
}

esp_audio_err_t native_aac_decoder_get_info(native_aac_decoder_t *decoder,
    esp_audio_simple_dec_info_t *info) {
    if (!decoder || !decoder->codec) return ESP_AUDIO_ERR_NOT_FOUND;
    return esp_audio_simple_dec_get_info(decoder->codec, info);
}

const char *native_aac_decoder_label(native_aac_decoder_t *decoder,
    const esp_audio_simple_dec_info_t *info, bool *format_is_pcm) {
    static const uint32_t rates[] = {
        96000, 88200, 64000, 48000, 44100, 32000, 24000,
        22050, 16000, 12000, 11025, 8000, 7350,
    };
    *format_is_pcm = true;
    if (!decoder || !decoder->codec || !info) return "AAC";
    unsigned index = (decoder->signature >> 4) & 15;
    unsigned core_channels = decoder->signature & 7;
    if (index < sizeof(rates) / sizeof(rates[0]) &&
        info->sample_rate == 2 * rates[index]) {
        *format_is_pcm = false;
        return core_channels == 1 && info->channel == 2 ? "HE-AACv2" : "HE-AAC";
    }
    return "AAC";
}
