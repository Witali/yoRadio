#include "CodecMemoryArena.h"

#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "codec_arena_native.h"
#include "esp_log.h"

namespace {
uint8_t *s_arena;
size_t s_capacity;
size_t s_used;
CodecArenaOwner s_owner = CODEC_ARENA_NONE;

bool contains(const void *pointer) {
    uintptr_t value = reinterpret_cast<uintptr_t>(pointer);
    uintptr_t first = reinterpret_cast<uintptr_t>(s_arena);
    return s_arena && value >= first && value < first + s_capacity;
}
}

bool CodecArenaBind(uint8_t *memory, size_t capacity) {
    if (!memory || !capacity || s_arena || s_owner != CODEC_ARENA_NONE)
        return false;
    s_arena = memory;
    s_capacity = capacity;
    s_used = 0;
    return true;
}

bool CodecArenaUnbind(void) {
    if (s_owner != CODEC_ARENA_NONE) return false;
    s_arena = nullptr;
    s_capacity = 0;
    s_used = 0;
    return true;
}

bool CodecArenaReserve() { return s_arena != nullptr; }

bool CodecArenaDiscard() { return CodecArenaUnbind(); }

void *CodecArenaCalloc(CodecArenaOwner owner, size_t count, size_t size) {
    if (!s_arena || owner == CODEC_ARENA_NONE || !count || !size ||
        size > SIZE_MAX / count) return nullptr;
    if (s_owner == CODEC_ARENA_NONE) s_owner = owner;
    if (s_owner != owner) return nullptr;
    const size_t alignment = alignof(max_align_t);
    size_t offset = (s_used + alignment - 1U) & ~(alignment - 1U);
    size_t bytes = count * size;
    if (offset > s_capacity || bytes > s_capacity - offset) {
        ESP_LOGE("codec_arena", "Arena exhausted: %u + %u > %u",
                 (unsigned)offset, (unsigned)bytes, (unsigned)s_capacity);
        return nullptr;
    }
    void *result = s_arena + offset;
    memset(result, 0, bytes);
    s_used = offset + bytes;
    return result;
}

void CodecArenaFree(void *pointer) {
    if (pointer && !contains(pointer)) free(pointer);
}

void CodecArenaRelease(CodecArenaOwner owner) {
    if (s_owner == owner) {
        s_owner = CODEC_ARENA_NONE;
        s_used = 0;
    }
}

size_t CodecArenaCapacity() { return s_capacity; }
size_t CodecArenaUsed() { return s_used; }
