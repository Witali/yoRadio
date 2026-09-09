#pragma once
#include <stddef.h>
enum CodecArenaOwner { CODEC_ARENA_NONE, CODEC_ARENA_OPUS };
bool CodecArenaBind(void *memory, size_t capacity);
void *CodecArenaCalloc32(CodecArenaOwner owner, size_t count, size_t bytes);
bool CodecArenaFree(void *memory);
void CodecArenaRelease(CodecArenaOwner owner);
bool CodecArenaUnbind(void);
