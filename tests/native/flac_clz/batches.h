#pragma once
#include <cstddef>
#include "candidates.h"

namespace flac_clz {
// Identical batch loops, with the candidate inline at its production call site.
// Dispatch is once per batch. Volatile RAM input forbids folding repeated loops
// or specializing based on constant corpora; there is no per-value indirect call.
#define FLAC_CLZ_BATCH(name, expression) \
    __attribute__((noinline)) inline uint32_t name(const volatile Sample* input, size_t count, unsigned repeats) { \
        uint32_t sum = 0; \
        for(unsigned repeat = 0; repeat < repeats; ++repeat) \
            for(size_t i = 0; i < count; ++i) { \
                Sample sample{input[i].cached, input[i].valid_bits}; \
                sum += expression; \
            } \
        return sum; \
    }
FLAC_CLZ_BATCH(batch_identity, static_cast<unsigned>(sample.cached) + sample.valid_bits)
FLAC_CLZ_BATCH(batch_intrinsic, rice_intrinsic(sample))
FLAC_CLZ_BATCH(batch_staged, rice_staged(sample))
FLAC_CLZ_BATCH(batch_groups, rice_groups(sample))
FLAC_CLZ_BATCH(batch_nibble, rice_nibble(sample))
FLAC_CLZ_BATCH(batch_table, rice_table(sample))
FLAC_CLZ_BATCH(batch_packed, rice_packed(sample))
#undef FLAC_CLZ_BATCH

using Batch = uint32_t (*)(const volatile Sample*, size_t, unsigned);
struct Variant { const char* name; Batch batch; bool identity; };
static const Variant kVariants[] = {
    {"identity", batch_identity, true}, {"intrinsic32-rice", batch_intrinsic, false},
    {"staged32-rice", batch_staged, false}, {"groups8-rice", batch_groups, false},
    {"nibble16-rice", batch_nibble, false}, {"byte256-rice", batch_table, false},
    {"packed-nibble-rice", batch_packed, false}
};
constexpr size_t kVariantCount = sizeof(kVariants) / sizeof(kVariants[0]);

// Full-width inputs are separate: Rice's uint8_t range can let the compiler
// eliminate the high stages of staged32, which is not a generic32 speed result.
#define FLAC_CLZ_BATCH32(name, expression) \
    __attribute__((noinline)) inline uint32_t name(const volatile uint32_t* input, size_t count, unsigned repeats) { \
        uint32_t sum = 0; \
        for(unsigned repeat = 0; repeat < repeats; ++repeat) \
            for(size_t i = 0; i < count; ++i) { \
                const uint32_t value = input[i]; \
                sum += expression; \
            } \
        return sum; \
    }
FLAC_CLZ_BATCH32(batch32_identity, value)
FLAC_CLZ_BATCH32(batch32_intrinsic, intrinsic32(value))
FLAC_CLZ_BATCH32(batch32_staged, staged32(value))
#undef FLAC_CLZ_BATCH32
using Batch32 = uint32_t (*)(const volatile uint32_t*, size_t, unsigned);
struct Variant32 { const char* name; Batch32 batch; bool identity; };
static const Variant32 kVariants32[] = {
    {"identity", batch32_identity, true}, {"intrinsic32", batch32_intrinsic, false},
    {"staged32", batch32_staged, false}
};
constexpr size_t kVariantCount32 = sizeof(kVariants32) / sizeof(kVariants32[0]);
} // namespace flac_clz
