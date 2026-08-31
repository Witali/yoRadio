#pragma once

#include <stddef.h>
#include <stdint.h>

bool CodecArenaBind(uint8_t *memory, size_t capacity);
bool CodecArenaUnbind(void);
bool CodecArenaPreallocateMp3(void);
size_t CodecArenaPreallocatedBytes(void);
