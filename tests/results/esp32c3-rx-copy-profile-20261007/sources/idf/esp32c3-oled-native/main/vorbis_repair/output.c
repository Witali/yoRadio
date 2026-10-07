// Reject undersized PCM before synthesis changes the overlap history.
// Vorbis I 4.3.1 / 4.3.8; pinned Tremor dsp.c uses the same block calculation.
#include "../vorbis_repair_abi.h"
#include "esp_vorbis_dec.h"

extern esp_audio_err_t __real_esp_vorbis_dec_decode(void *, esp_audio_dec_in_raw_t *,
    esp_audio_dec_out_frame_t *, esp_audio_dec_info_t *);

esp_audio_err_t __wrap_esp_vorbis_dec_decode(void *handle, esp_audio_dec_in_raw_t *raw,
    esp_audio_dec_out_frame_t *out, esp_audio_dec_info_t *info) {
    if (!handle || !raw || !out || !info || !raw->buffer || !out->buffer)
        return ESP_AUDIO_ERR_INVALID_PARAMETER;
    vorbis_dsp_state *dsp = ((vorbis_wrapper *)handle)->dsp;
    codec_setup_info *setup = dsp->vi->codec_setup;
    unsigned mode_bits = 0;
    for (unsigned modes = setup->modes - 1; modes; modes >>= 1) ++mode_bits;
    // There are at most 64 modes, so type and mode fit in the first byte.
    // A long block additionally needs both window flags (possibly byte 2).
    if (raw->len && !(raw->buffer[0] & 1U)) {
        unsigned mode = (raw->buffer[0] >> 1) & ((1U << mode_bits) - 1U);
        if (mode < (unsigned)setup->modes) {
            unsigned window = setup->mode_param[mode].blockflag;
            unsigned header_bits = 1U + mode_bits + (window ? 2U : 0U);
            if (raw->len >= (header_bits + 7U) / 8U) {
                size_t frames = dsp->out_begin == -1 ? 0 :
                    (setup->blocksizes[dsp->W] + setup->blocksizes[window]) / 4;
                size_t required = frames * dsp->vi->channels * sizeof(int16_t);
                if (out->len < required) {
                    raw->consumed = 0;
                    out->decoded_size = 0;
                    out->needed_size = required;
                    return ESP_AUDIO_ERR_BUFF_NOT_ENOUGH;
                }
            }
        }
    }
    // Preserve the original malformed-packet and PCM conversion behavior.
    return __real_esp_vorbis_dec_decode(handle, raw, out, info);
}
