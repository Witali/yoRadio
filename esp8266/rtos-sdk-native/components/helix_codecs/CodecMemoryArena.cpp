#include "CodecMemoryArena.h"

#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "codec_arena_native.h"
#include "esp_heap_caps.h"
#include "esp_log.h"

namespace {
constexpr size_t kWordArenaBytes = 16U * 1024U;
constexpr uint32_t kIramDataCaps = MALLOC_CAP_32BIT | MALLOC_CAP_EXEC;
uint8_t *s_arena;
uint8_t *s_word_arena;
bool s_fragmented;
size_t s_capacity;
size_t s_used;
size_t s_word_used;
CodecArenaOwner s_owner = CODEC_ARENA_NONE;

bool contains(const void *pointer) {
    uintptr_t value = reinterpret_cast<uintptr_t>(pointer);
    uintptr_t first = reinterpret_cast<uintptr_t>(s_arena);
    return s_arena && value >= first && value < first + s_capacity;
}

bool contains_word(const void *pointer) {
    uintptr_t value = reinterpret_cast<uintptr_t>(pointer);
    uintptr_t first = reinterpret_cast<uintptr_t>(s_word_arena);
    return s_word_arena && value >= first &&
           value < first + kWordArenaBytes;
}
}

bool CodecArenaPreallocateMp3(void) {
    if (s_word_arena) return true;
    s_word_arena = static_cast<uint8_t *>(
        heap_caps_calloc(1, kWordArenaBytes, kIramDataCaps));
    bool in_iram = s_word_arena != nullptr;
    if (!s_word_arena) {
        ESP_LOGW("codec_arena",
                 "IRAM cannot reserve %u-byte codec word arena; using DRAM",
                 (unsigned)kWordArenaBytes);
        s_word_arena = static_cast<uint8_t *>(
            heap_caps_calloc(1, kWordArenaBytes, MALLOC_CAP_8BIT));
    }
    if (!s_word_arena) {
        ESP_LOGE("codec_arena",
                 "Cannot reserve %u-byte codec word arena; heap free %u",
                 (unsigned)kWordArenaBytes,
                 (unsigned)heap_caps_get_free_size(MALLOC_CAP_32BIT));
        return false;
    }
    s_word_used = 0;
    ESP_LOGI("codec_arena", "Reserved %u-byte codec word arena at %p (%s)",
             (unsigned)kWordArenaBytes, s_word_arena,
             in_iram ? "IRAM" : "DRAM");
    return true;
}

size_t CodecArenaPreallocatedBytes(void) {
    return s_word_arena ? kWordArenaBytes : 0U;
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

static void *arena_calloc(CodecArenaOwner owner, size_t count, size_t size,
                          bool word_only) {
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
    void *result = nullptr;
    if (s_fragmented && word_only) {
        if (!s_word_arena && !CodecArenaPreallocateMp3()) return nullptr;
        const size_t word_offset =
            (s_word_used + alignment - 1U) & ~(alignment - 1U);
        if (word_offset <= kWordArenaBytes &&
            bytes <= kWordArenaBytes - word_offset) {
            result = s_word_arena + word_offset;
            s_word_used = word_offset + bytes;
            memset(result, 0, bytes);
        } else {
            ESP_LOGW("codec_arena",
                     "Word arena exhausted: %u + %u > %u; using DRAM",
                     (unsigned)word_offset, (unsigned)bytes,
                     (unsigned)kWordArenaBytes);
            result = heap_caps_calloc(count, size, caps);
        }
    } else {
        result = s_fragmented
            ? heap_caps_calloc(count, size, caps)
            : static_cast<void *>(s_arena + offset);
    }
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

void *CodecArenaCalloc(CodecArenaOwner owner, size_t count, size_t size) {
    return arena_calloc(owner, count, size, false);
}

void *CodecArenaCalloc32(CodecArenaOwner owner, size_t count, size_t size) {
    return arena_calloc(owner, count, size, true);
}

void CodecArenaFree(void *pointer) {
    if (contains_word(pointer)) return;
    if (pointer && !contains(pointer)) heap_caps_free(pointer);
}

void CodecArenaRelease(CodecArenaOwner owner) {
    if (s_owner == owner) {
        s_owner = CODEC_ARENA_NONE;
        s_used = 0;
        s_word_used = 0;
    }
}

size_t CodecArenaCapacity() { return s_capacity; }
size_t CodecArenaUsed() { return s_used; }
