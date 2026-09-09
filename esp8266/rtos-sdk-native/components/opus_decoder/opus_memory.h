#pragma once
#include <stddef.h>
#include <stdint.h>
#include <setjmp.h>
#include <string.h>
#ifndef YORADIO_OPUS_WORD_ASM
#define YORADIO_OPUS_WORD_ASM 0
#endif
#if YORADIO_OPUS_WORD_ASM != 0 && YORADIO_OPUS_WORD_ASM != 1
#error "YORADIO_OPUS_WORD_ASM must be 0 or 1"
#endif
#ifdef __cplusplus
extern "C" {
#endif

typedef struct { size_t bytes, words; } opus_scratch_mark;
/* One active decoder. Binding/unbinding occurs outside decode calls. */
void yoradio_opus_memory_bind(void *bytes, size_t byte_capacity,
                              void *words, size_t word_capacity);
opus_scratch_mark yoradio_opus_scratch_mark(void);
void yoradio_opus_scratch_restore(opus_scratch_mark mark);
void *yoradio_opus_scratch_alloc(size_t count, size_t size, int word_safe);
/* Begin one decoder's persistent allocations, only outside a packet decode.
 * Each history call reserves a distinct aligned region until the next begin. */
int yoradio_opus_history_begin(void);
void *yoradio_opus_history(size_t bytes);
/* Private decoder RAM and audited read-only mapped flash only, never MMIO.
 * p must address a complete, four-byte-aligned word. The optional LX106 path
 * fixes the instruction width without volatile-C's per-access MEMW. A compiler
 * memory clobber retains ordering/alias visibility, including overlapping copy
 * and read-after-write. The private arena has one CPU owner, no DMA/device
 * publication and no self-modifying executable code. Hardware/device ordering
 * is deliberately outside this helper's contract. Keep the C path for hosts
 * and as the default-off A/B reference; do not change SDK volatile semantics. */
static inline uint32_t yoradio_opus_private_load_word(const void *p) {
#if YORADIO_OPUS_WORD_ASM && defined(__XTENSA__)
    uint32_t value;
    __asm__ volatile ("l32i %0, %1, 0" : "=a" (value) : "a" (p) : "memory");
    return value;
#else
    return *(const volatile uint32_t *)p;
#endif
}
static inline void yoradio_opus_private_store_word(void *p, uint32_t value) {
#if YORADIO_OPUS_WORD_ASM && defined(__XTENSA__)
    __asm__ volatile ("s32i %1, %0, 0" : : "a" (p), "a" (value) : "memory");
#else
    *(volatile uint32_t *)p = value;
#endif
}
/* Force full-width IRAM accesses even when only half of a value is consumed. */
static inline int32_t yoradio_opus_load32(const int32_t *p) {
    return (int32_t)yoradio_opus_private_load_word(p);
}
static inline void yoradio_opus_store32(int32_t *p, int32_t value) {
    yoradio_opus_private_store_word(p, (uint32_t)value);
}
/* Audited static flash tables only: every addressed halfword must belong to
 * a complete, readable, four-byte-aligned word. Native MDCT/FFT tables meet
 * this condition. Union halves preserve host byte order for PCM regressions. */
typedef union { uint32_t word; int16_t half[2]; } yoradio_opus_table_pair;
static inline yoradio_opus_table_pair yoradio_opus_table_load_pair(const void *p) {
    yoradio_opus_table_pair value;
#if defined(__XTENSA__)
    /* Do not let the compiler narrow this flash load to exception-emulated
     * l16si/l16ui instructions when it consumes the individual halves. */
    value.word = yoradio_opus_private_load_word(p);
#else
    /* Avoid effective-type/alignment assumptions in portable host builds. */
    memcpy(&value.word, p, sizeof(value.word));
#endif
    return value;
}
static inline int16_t yoradio_opus_table_read16(const int16_t *p) {
    uintptr_t address = (uintptr_t)p;
    yoradio_opus_table_pair value =
        yoradio_opus_table_load_pair((const void *)(address & ~(uintptr_t)3U));
    return address & 2U ? value.half[1] : value.half[0];
}
void yoradio_opus_copy(void *to, const void *from, size_t count, size_t size);
void yoradio_opus_clear(void *to, size_t count, size_t size);
size_t yoradio_opus_scratch_peak_bytes(void);
size_t yoradio_opus_scratch_peak_words(void);
/* Kept inside the C decoder wrapper; no C++ destructors are crossed. */
extern jmp_buf yoradio_opus_oom;
int yoradio_opus_decode_bounded(void *decoder, const unsigned char *packet,
                               int length, int16_t *pcm, int frame_size);
#ifdef __cplusplus
}
#endif
