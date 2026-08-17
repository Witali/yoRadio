#pragma once

#include <stddef.h>
#include <stdint.h>

enum OggDecodeResult : int {
    OGG_DECODE_OK = 0,
    OGG_DECODE_OUTPUT_TOO_SMALL = 1,
    OGG_DECODE_ERROR = -1
};

enum OggCodecType : uint8_t {
    OGG_CODEC_UNKNOWN = 0,
    OGG_CODEC_VORBIS,
    OGG_CODEC_OPUS
};

bool OggDecoderOpen();
void OggDecoderClose();
OggDecodeResult OggDecoderDecode(uint8_t* input, size_t inputSize,
                                 uint8_t* output, size_t outputSize,
                                 size_t* consumed, size_t* decoded,
                                 size_t* requiredOutputSize);
bool OggDecoderGetInfo(uint32_t* sampleRate, uint8_t* channels,
                       uint8_t* bitsPerSample, uint32_t* bitrate);
OggCodecType OggDecoderGetCodecType();
