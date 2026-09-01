#include "CodecMemoryArena.h"

#include <stdlib.h>

bool CodecArenaReserve() { return true; }
bool CodecArenaDiscard() { return true; }

void *CodecArenaCalloc(CodecArenaOwner, size_t count, size_t size) {
    return calloc(count, size);
}

void *CodecArenaCalloc32(CodecArenaOwner owner, size_t count, size_t size) {
    return CodecArenaCalloc(owner, count, size);
}

void CodecArenaFree(void *pointer) { free(pointer); }
void CodecArenaRelease(CodecArenaOwner) {}
size_t CodecArenaCapacity() { return 64U * 1024U; }
size_t CodecArenaUsed() { return 0; }
