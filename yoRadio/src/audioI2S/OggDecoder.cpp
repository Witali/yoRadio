#include "OggDecoder.h"

#if defined(YORADIO_ESP_IDF_MINIMAL)

#include <Arduino.h>
#include <decoder/esp_audio_dec_default.h>
#include <simple_dec/esp_audio_simple_dec.h>
#include <simple_dec/esp_audio_simple_dec_default.h>

namespace {

esp_audio_simple_dec_handle_t decoder = nullptr;
bool registered = false;

bool registerDecoders() {
    if(registered) return true;
    const esp_audio_err_t codecResult = esp_audio_dec_register_default();
    const esp_audio_err_t parserResult = esp_audio_simple_dec_register_default();
    if(codecResult != ESP_AUDIO_ERR_OK || parserResult != ESP_AUDIO_ERR_OK) {
        log_e("OGG decoder registration failed: codec=%d parser=%d",
              codecResult, parserResult);
        return false;
    }
    registered = true;
    return true;
}

} // namespace

bool OggDecoderOpen() {
    OggDecoderClose();
    if(!registerDecoders()) return false;
    esp_audio_simple_dec_cfg_t config = {};
    config.dec_type = ESP_AUDIO_SIMPLE_DEC_TYPE_OGG;
    config.use_frame_dec = false;
    const esp_audio_err_t result = esp_audio_simple_dec_open(&config, &decoder);
    if(result != ESP_AUDIO_ERR_OK) {
        log_e("Unable to open OGG decoder: %d", result);
        decoder = nullptr;
        return false;
    }
    return true;
}

void OggDecoderClose() {
    if(decoder) {
        esp_audio_simple_dec_close(decoder);
        decoder = nullptr;
    }
}

OggDecodeResult OggDecoderDecode(uint8_t* input, size_t inputSize,
                                 uint8_t* output, size_t outputSize,
                                 size_t* consumed, size_t* decoded,
                                 size_t* requiredOutputSize) {
    if(consumed) *consumed = 0;
    if(decoded) *decoded = 0;
    if(requiredOutputSize) *requiredOutputSize = 0;
    if(!decoder || !input || !inputSize || !output || !outputSize) {
        return OGG_DECODE_ERROR;
    }

    esp_audio_simple_dec_raw_t raw = {};
    raw.buffer = input;
    raw.len = static_cast<uint32_t>(inputSize);
    esp_audio_simple_dec_out_t frame = {};
    frame.buffer = output;
    frame.len = static_cast<uint32_t>(outputSize);
    const esp_audio_err_t result = esp_audio_simple_dec_process(decoder, &raw, &frame);
    if(consumed) *consumed = raw.consumed;
    if(decoded) *decoded = frame.decoded_size;
    if(requiredOutputSize) *requiredOutputSize = frame.needed_size;
    if(result == ESP_AUDIO_ERR_BUFF_NOT_ENOUGH) {
        return OGG_DECODE_OUTPUT_TOO_SMALL;
    }
    if(result != ESP_AUDIO_ERR_OK && result != ESP_AUDIO_ERR_CONTINUE &&
       result != ESP_AUDIO_ERR_DATA_LACK) {
        log_e("OGG decode failed: %d", result);
        return OGG_DECODE_ERROR;
    }
    return OGG_DECODE_OK;
}

bool OggDecoderGetInfo(uint32_t* sampleRate, uint8_t* channels,
                       uint8_t* bitsPerSample, uint32_t* bitrate) {
    if(!decoder) return false;
    esp_audio_simple_dec_info_t info = {};
    if(esp_audio_simple_dec_get_info(decoder, &info) != ESP_AUDIO_ERR_OK) {
        return false;
    }
    if(sampleRate) *sampleRate = info.sample_rate;
    if(channels) *channels = info.channel;
    if(bitsPerSample) *bitsPerSample = info.bits_per_sample;
    if(bitrate) *bitrate = info.bitrate;
    return info.sample_rate && info.channel && info.bits_per_sample;
}

#else

bool OggDecoderOpen() { return false; }
void OggDecoderClose() {}
OggDecodeResult OggDecoderDecode(uint8_t*, size_t, uint8_t*, size_t,
                                 size_t*, size_t*, size_t*) {
    return OGG_DECODE_ERROR;
}
bool OggDecoderGetInfo(uint32_t*, uint8_t*, uint8_t*, uint32_t*) {
    return false;
}

#endif
