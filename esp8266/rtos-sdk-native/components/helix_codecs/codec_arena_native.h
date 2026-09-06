#pragma once

#include <stddef.h>
#include <stdint.h>

bool CodecArenaBind(uint8_t *memory, size_t capacity);
bool CodecArenaUnbind(void);
bool CodecArenaPreallocateMp3(void);
size_t CodecArenaPreallocatedBytes(void);
size_t CodecArenaHeapUsed(void);
size_t CodecArenaWordUsed(void);
bool CodecArenaPreallocatedInIram(void);
