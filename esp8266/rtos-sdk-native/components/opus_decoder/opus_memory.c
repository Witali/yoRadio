#include "opus_memory.h"
#include "opus.h"
#include <string.h>

static unsigned char *byte_base, *word_base;
static size_t byte_capacity, word_capacity, byte_used, word_used;
static size_t history_bytes, peak_bytes, peak_words;
jmp_buf yoradio_opus_oom;

void yoradio_opus_memory_bind(void *bytes, size_t bytes_size,
                              void *words, size_t words_size) {
    byte_base = bytes; word_base = words;
    byte_capacity = bytes_size; word_capacity = words_size;
    byte_used = word_used = history_bytes = peak_bytes = peak_words = 0;
}

void *yoradio_opus_history(size_t bytes) {
    if (!word_base || bytes > word_capacity) return NULL;
    history_bytes = (bytes + 7U) & ~(size_t)7U;
    if (history_bytes > word_capacity) return NULL;
    word_used = history_bytes;
    return word_base;
}

opus_scratch_mark yoradio_opus_scratch_mark(void) {
    opus_scratch_mark mark = {byte_used, word_used}; return mark;
}
void yoradio_opus_scratch_restore(opus_scratch_mark mark) {
    byte_used = mark.bytes; word_used = mark.words;
}
void *yoradio_opus_scratch_alloc(size_t count, size_t size, int word_safe) {
    if (size && count > SIZE_MAX / size) longjmp(yoradio_opus_oom, 1);
    size_t bytes = count * size;
    if (bytes > SIZE_MAX - 7U) longjmp(yoradio_opus_oom, 1);
    bytes = (bytes + 7U) & ~(size_t)7U;
    /* Only audited word-safe arrays may use the shared IRAM arena. */
    if (word_safe && word_used <= word_capacity &&
        bytes <= word_capacity - word_used) {
        void *result = word_base + word_used;
        word_used += bytes;
        if (word_used > peak_words) peak_words = word_used;
        return result;
    }
    if (!byte_base || byte_used > byte_capacity || bytes > byte_capacity - byte_used)
        longjmp(yoradio_opus_oom, 1);
    void *result = byte_base + byte_used;
    byte_used += bytes;
    if (byte_used > peak_bytes) peak_bytes = byte_used;
    return result;
}
size_t yoradio_opus_scratch_peak_bytes(void) { return peak_bytes; }
size_t yoradio_opus_scratch_peak_words(void) { return peak_words; }

void yoradio_opus_copy(void *to, const void *from, size_t count, size_t size) {
    if (size == 4U || size == 8U) {
        /* These paths are called only with typed arrays aligned to 32 bits.
         * volatile prevents GCC lowering this back to byte-wise libc calls. */
        volatile uint32_t *dst = to;
        const volatile uint32_t *src = from;
        size_t words = count * (size / 4U);
        if ((uintptr_t)dst > (uintptr_t)src) {
            while (words) { --words; dst[words] = src[words]; }
        } else {
            for (size_t i = 0; i < words; ++i) dst[i] = src[i];
        }
    } else memmove(to, from, count * size);
}
void yoradio_opus_clear(void *to, size_t count, size_t size) {
    if (size == 4U || size == 8U) {
        volatile uint32_t *dst = to;
        for (size_t i = 0; i < count * (size / 4U); ++i) dst[i] = 0;
    } else memset(to, 0, count * size);
}

int yoradio_opus_decode_bounded(void *decoder, const unsigned char *packet,
                               int length, int16_t *pcm, int frame_size) {
    byte_used = 0; word_used = history_bytes;
    if (setjmp(yoradio_opus_oom)) {
        byte_used = 0; word_used = history_bytes;
        return OPUS_ALLOC_FAIL;
    }
    int result = opus_decode(decoder, packet, length, pcm, frame_size, 0);
    byte_used = 0; word_used = history_bytes;
    return result;
}
