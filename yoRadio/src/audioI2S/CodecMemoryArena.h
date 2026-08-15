#pragma once

#include <stddef.h>
#include <stdint.h>

enum CodecArenaOwner : uint8_t {
    CODEC_ARENA_NONE = 0,
    CODEC_ARENA_MP3,
    CODEC_ARENA_AAC
};

// Reserve one contiguous block before a network connection can fragment the
// ESP32 heap. Only one software audio decoder is active at a time, so MP3 and
// AAC can safely reuse the same storage.
bool CodecArenaReserve();
void* CodecArenaCalloc(CodecArenaOwner owner, size_t count, size_t size);
void CodecArenaFree(void* pointer);
void CodecArenaRelease(CodecArenaOwner owner);

size_t CodecArenaCapacity();
size_t CodecArenaUsed();

