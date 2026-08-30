#include "CodecMemoryArena.h"

#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "codec_arena_native.h"
#include "esp_heap_caps.h"
#include "esp_log.h"

namespace {
uint8_t *s_arena;
bool s_fragmented;
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
    if (!capacity || s_capacity || s_owner != CODEC_ARENA_NONE)
        return false;
    s_arena = memory;
    s_fragmented = memory == nullptr;
    s_capacity = capacity;
    s_used = 0;
    return true;
}

bool CodecArenaUnbind(void) {
    if (s_owner != CODEC_ARENA_NONE) return false;
    s_arena = nullptr;
    s_capacity = 0;
    s_fragmented = false;
    s_used = 0;
    return true;
}

bool CodecArenaReserve() { return s_capacity != 0; }

bool CodecArenaDiscard() { return CodecArenaUnbind(); }

void *CodecArenaCalloc(CodecArenaOwner owner, size_t count, size_t size) {
    if (!s_capacity || owner == CODEC_ARENA_NONE || !count || !size ||
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
    uint32_t caps = MALLOC_CAP_8BIT;
    /* SubbandInfo is exactly 8708 bytes of aligned int32_t samples. */
    if (s_fragmented && owner == CODEC_ARENA_MP3 && bytes == 8708U)
        caps = MALLOC_CAP_32BIT;
    void *result = s_fragmented
        ? heap_caps_calloc(count, size, caps)
        : static_cast<void *>(s_arena + offset);
    if (!result) {
        ESP_LOGE("codec_arena",
                 "Allocation failed: %u bytes, used %u, cap free %u",
                 (unsigned)bytes, (unsigned)s_used,
                 (unsigned)heap_caps_get_free_size(caps));
        return nullptr;
    }
    if (!s_fragmented) memset(result, 0, bytes);
    s_used = offset + bytes;
    return result;
}

void CodecArenaFree(void *pointer) {
    if (pointer && !contains(pointer)) heap_caps_free(pointer);
}

void CodecArenaRelease(CodecArenaOwner owner) {
    if (s_owner == owner) {
        s_owner = CODEC_ARENA_NONE;
        s_used = 0;
    }
}

size_t CodecArenaCapacity() { return s_capacity; }
size_t CodecArenaUsed() { return s_used; }
