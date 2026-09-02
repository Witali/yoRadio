#include "CodecMemoryArena.h"

#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "codec_arena_native.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "sdkconfig.h"

namespace {
#if !CONFIG_YORADIO_HELIX_AAC && CONFIG_YORADIO_MP3_DECODER_LIBMAD
/* libmad keeps mad_synth (4,236 bytes), xr_raw (4,608 bytes), and the Layer
 * III reorder scratch buffer (2,304 bytes) in aligned 32-bit IRAM. The 12-KiB
 * arena leaves more than 1 KiB for alignment and version headroom. */
constexpr size_t kWordArenaBytes = 12U * 1024U;
constexpr size_t kWordSpillBytes = 0U;
#elif !CONFIG_YORADIO_HELIX_AAC
/* Helix MP3 uses about 14.2 KiB across Huffman/dequant/subband state. */
constexpr size_t kWordArenaBytes = 15U * 1024U;
constexpr size_t kWordSpillBytes = 0U;
#else
/* The full MP3/AAC profile has a physically verified contiguous 16-KiB
 * IRAM arena. Larger and secondary allocations are not reliable with the
 * ESP8266 RTOS SDK heap regions, so the remaining MP3 state uses DRAM. */
constexpr size_t kWordArenaBytes = 16U * 1024U;
constexpr size_t kWordSpillBytes = 0U;
#endif
constexpr size_t kMaxHeapAllocations = 16U;
constexpr uint32_t kIramDataCaps = MALLOC_CAP_32BIT | MALLOC_CAP_EXEC;
struct HeapAllocation {
    void *pointer;
    size_t bytes;
};
uint8_t *s_arena;
uint8_t *s_word_arena;
uint8_t *s_word_spill;
bool s_fragmented;
bool s_word_arena_in_iram;
bool s_word_spill_in_iram;
size_t s_capacity;
size_t s_used;
size_t s_word_used;
size_t s_word_spill_used;
size_t s_heap_used;
HeapAllocation s_heap_allocations[kMaxHeapAllocations];
CodecArenaOwner s_owner = CODEC_ARENA_NONE;

bool contains(const void *pointer) {
    uintptr_t value = reinterpret_cast<uintptr_t>(pointer);
    uintptr_t first = reinterpret_cast<uintptr_t>(s_arena);
    return s_arena && value >= first && value < first + s_capacity;
}

bool contains_word(const void *pointer) {
    uintptr_t value = reinterpret_cast<uintptr_t>(pointer);
    uintptr_t first = reinterpret_cast<uintptr_t>(s_word_arena);
    if (s_word_arena && value >= first &&
        value < first + kWordArenaBytes) return true;
    first = reinterpret_cast<uintptr_t>(s_word_spill);
    return s_word_spill && value >= first &&
           value < first + kWordSpillBytes;
}

bool track_heap_allocation(void *pointer, size_t bytes) {
    for (HeapAllocation &allocation : s_heap_allocations) {
        if (!allocation.pointer) {
            allocation = {pointer, bytes};
            s_heap_used += bytes;
            return true;
        }
    }
    return false;
}

void untrack_heap_allocation(void *pointer) {
    for (HeapAllocation &allocation : s_heap_allocations) {
        if (allocation.pointer == pointer) {
            s_heap_used -= allocation.bytes;
            allocation = {};
            return;
        }
    }
    ESP_LOGW("codec_arena", "Freeing untracked allocation at %p", pointer);
}
}

bool CodecArenaPreallocateMp3(void) {
    if (s_word_arena) return true;
    s_word_arena = static_cast<uint8_t *>(
        heap_caps_calloc(1, kWordArenaBytes, kIramDataCaps));
    s_word_arena_in_iram = s_word_arena != nullptr;
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
    if (kWordSpillBytes && s_word_arena_in_iram) {
        s_word_spill = static_cast<uint8_t *>(
            heap_caps_calloc(1, kWordSpillBytes, kIramDataCaps));
        s_word_spill_in_iram = s_word_spill != nullptr;
        if (!s_word_spill) {
            ESP_LOGW("codec_arena",
                     "IRAM cannot reserve %u-byte codec spill arena",
                     (unsigned)kWordSpillBytes);
        }
    }
    s_word_spill_used = 0;
    ESP_LOGI("codec_arena",
             "Reserved %u+%u-byte codec word arena (%s)",
             (unsigned)kWordArenaBytes,
             (unsigned)(s_word_spill ? kWordSpillBytes : 0U),
             s_word_arena_in_iram ? "IRAM" : "DRAM");
    return true;
}

size_t CodecArenaPreallocatedBytes(void) {
    return s_word_arena
        ? kWordArenaBytes + (s_word_spill ? kWordSpillBytes : 0U)
        : 0U;
}

bool CodecArenaPreallocatedInIram(void) {
    return s_word_arena && s_word_arena_in_iram &&
           (!s_word_spill || s_word_spill_in_iram);
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
    if (s_owner != CODEC_ARENA_NONE || s_heap_used) return false;
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
    bool heap_backed = false;
    if (s_fragmented && word_only) {
        if (!s_word_arena && !CodecArenaPreallocateMp3()) return nullptr;
        const size_t word_offset =
            (s_word_used + alignment - 1U) & ~(alignment - 1U);
        const size_t spill_offset =
            (s_word_spill_used + alignment - 1U) & ~(alignment - 1U);
        if (word_offset <= kWordArenaBytes &&
            bytes <= kWordArenaBytes - word_offset) {
            result = s_word_arena + word_offset;
            s_word_used = word_offset + bytes;
            memset(result, 0, bytes);
        } else if (s_word_spill && spill_offset <= kWordSpillBytes &&
                   bytes <= kWordSpillBytes - spill_offset) {
            result = s_word_spill + spill_offset;
            s_word_spill_used = spill_offset + bytes;
            memset(result, 0, bytes);
        } else {
            ESP_LOGW("codec_arena",
                     "Word arenas exhausted for %u bytes; using DRAM",
                     (unsigned)bytes);
            result = heap_caps_calloc(count, size, caps);
            heap_backed = true;
        }
    } else {
        result = s_fragmented
            ? heap_caps_calloc(count, size, caps)
            : static_cast<void *>(s_arena + offset);
        heap_backed = s_fragmented;
    }
    if (!result) {
        ESP_LOGE("codec_arena",
                 "Allocation failed: %u bytes, used %u, cap free %u",
                 (unsigned)bytes, (unsigned)s_used,
                 (unsigned)heap_caps_get_free_size(caps));
        return nullptr;
    }
    if (heap_backed && !track_heap_allocation(result, bytes)) {
        ESP_LOGE("codec_arena", "Too many codec heap allocations");
        heap_caps_free(result);
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
    if (pointer && !contains(pointer)) {
        untrack_heap_allocation(pointer);
        heap_caps_free(pointer);
    }
}

void CodecArenaRelease(CodecArenaOwner owner) {
    if (s_owner == owner) {
        if (s_heap_used)
            ESP_LOGE("codec_arena", "Owner released with %u DRAM bytes live",
                     (unsigned)s_heap_used);
        s_owner = CODEC_ARENA_NONE;
        s_used = 0;
        s_word_used = 0;
        s_word_spill_used = 0;
    }
}

size_t CodecArenaCapacity() { return s_capacity; }
size_t CodecArenaUsed() { return s_used; }
size_t CodecArenaHeapUsed() { return s_heap_used; }
size_t CodecArenaWordUsed() {
    return s_word_used + s_word_spill_used;
}
