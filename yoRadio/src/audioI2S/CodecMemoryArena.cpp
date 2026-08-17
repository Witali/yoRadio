#include "CodecMemoryArena.h"

#include <Arduino.h>
#include <esp_heap_caps.h>
#include <stdlib.h>
#include <string.h>

namespace {

#if defined(CONFIG_IDF_TARGET_ESP32S3) && defined(BOARD_HAS_PSRAM)
constexpr size_t kCodecArenaCapacity = 96 * 1024;
#else
// AAC-LC uses 20,584 bytes, minimp3 16,236 and legacy Helix about 23.3 KiB.
// Keep room for every selectable decoder while returning the rest to TLS.
constexpr size_t kCodecArenaCapacity = 24 * 1024;
#endif

uint8_t* arena = nullptr;
size_t used = 0;
CodecArenaOwner activeOwner = CODEC_ARENA_NONE;

bool contains(const void* pointer) {
    if(!arena || !pointer) return false;
    const uintptr_t address = reinterpret_cast<uintptr_t>(pointer);
    const uintptr_t first = reinterpret_cast<uintptr_t>(arena);
    return address >= first && address < first + kCodecArenaCapacity;
}

} // namespace

bool CodecArenaReserve() {
    if(arena) return true;

#if defined(CONFIG_IDF_TARGET_ESP32S3) && defined(BOARD_HAS_PSRAM)
    arena = static_cast<uint8_t*>(
        heap_caps_malloc(kCodecArenaCapacity, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT)
    );
#else
    arena = static_cast<uint8_t*>(
        heap_caps_malloc(kCodecArenaCapacity, MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT)
    );
#endif

    if(!arena) {
        log_e("Unable to reserve %u-byte codec arena; free heap %u, largest block %u",
              static_cast<unsigned>(kCodecArenaCapacity),
              static_cast<unsigned>(ESP.getFreeHeap()),
              static_cast<unsigned>(ESP.getMaxAllocHeap()));
        return false;
    }

    used = 0;
    activeOwner = CODEC_ARENA_NONE;
    log_i("Codec arena reserved: %u bytes, free heap: %u",
          static_cast<unsigned>(kCodecArenaCapacity),
          static_cast<unsigned>(ESP.getFreeHeap()));
    return true;
}

bool CodecArenaDiscard() {
    if(activeOwner != CODEC_ARENA_NONE) {
        log_e("Cannot discard codec arena owned by decoder %u",
              static_cast<unsigned>(activeOwner));
        return false;
    }
    free(arena);
    arena = nullptr;
    used = 0;
    return true;
}

void* CodecArenaCalloc(CodecArenaOwner owner, size_t count, size_t size) {
    if(owner == CODEC_ARENA_NONE || !count || !size || size > SIZE_MAX / count) {
        return nullptr;
    }
    if(!CodecArenaReserve()) return nullptr;

    if(activeOwner == CODEC_ARENA_NONE) {
        activeOwner = owner;
        used = 0;
    } else if(activeOwner != owner) {
        log_e("Codec arena is still owned by decoder %u",
              static_cast<unsigned>(activeOwner));
        return nullptr;
    }

    constexpr size_t alignment = alignof(max_align_t);
    const size_t alignedOffset = (used + alignment - 1) & ~(alignment - 1);
    const size_t bytes = count * size;
    if(alignedOffset > kCodecArenaCapacity || bytes > kCodecArenaCapacity - alignedOffset) {
        log_e("Codec arena exhausted: requested %u bytes, used %u of %u",
              static_cast<unsigned>(bytes), static_cast<unsigned>(used),
              static_cast<unsigned>(kCodecArenaCapacity));
        return nullptr;
    }

    void* result = arena + alignedOffset;
    used = alignedOffset + bytes;
    memset(result, 0, bytes);
    return result;
}

void CodecArenaFree(void* pointer) {
    if(pointer && !contains(pointer)) free(pointer);
}

void CodecArenaRelease(CodecArenaOwner owner) {
    if(activeOwner != owner) return;
    used = 0;
    activeOwner = CODEC_ARENA_NONE;
}

size_t CodecArenaCapacity() {
    return kCodecArenaCapacity;
}

size_t CodecArenaUsed() {
    return used;
}
