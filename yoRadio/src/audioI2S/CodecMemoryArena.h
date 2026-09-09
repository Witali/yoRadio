#pragma once

#include <stddef.h>
#include <stdint.h>

enum CodecArenaOwner : uint8_t {
    CODEC_ARENA_NONE = 0,
    CODEC_ARENA_MP3,
    CODEC_ARENA_AAC,
    CODEC_ARENA_OPUS
};

// Reserve one contiguous block before a network connection can fragment the
// ESP32 heap. Only one software audio decoder is active at a time, so MP3 and
// AAC can safely reuse the same storage.
bool CodecArenaReserve();
bool CodecArenaDiscard();
void* CodecArenaCalloc(CodecArenaOwner owner, size_t count, size_t size);
// Allocate storage which is accessed exclusively as aligned 32-bit words.
// ESP8266 uses this to place decoder work arrays in its otherwise unused IRAM.
void* CodecArenaCalloc32(CodecArenaOwner owner, size_t count, size_t size);
void CodecArenaFree(void* pointer);
void CodecArenaRelease(CodecArenaOwner owner);

size_t CodecArenaCapacity();
size_t CodecArenaUsed();

