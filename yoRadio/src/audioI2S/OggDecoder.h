#pragma once

#include <stddef.h>
#include <stdint.h>

enum OggDecodeResult : int {
    OGG_DECODE_OK = 0,
    OGG_DECODE_OUTPUT_TOO_SMALL = 1,
    OGG_DECODE_ERROR = -1
};

bool OggDecoderOpen();
void OggDecoderClose();
OggDecodeResult OggDecoderDecode(uint8_t* input, size_t inputSize,
                                 uint8_t* output, size_t outputSize,
                                 size_t* consumed, size_t* decoded,
                                 size_t* requiredOutputSize);
bool OggDecoderGetInfo(uint32_t* sampleRate, uint8_t* channels,
                       uint8_t* bitsPerSample, uint32_t* bitrate);
