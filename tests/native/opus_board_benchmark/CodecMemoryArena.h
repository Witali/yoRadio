#pragma once
#include <stddef.h>
#include <stdint.h>
enum CodecArenaOwner : uint8_t { CODEC_ARENA_NONE, CODEC_ARENA_MP3, CODEC_ARENA_AAC, CODEC_ARENA_OPUS };
void *CodecArenaCalloc32(CodecArenaOwner owner, size_t count, size_t bytes);
void CodecArenaFree(void *memory);
void CodecArenaRelease(CodecArenaOwner owner);
