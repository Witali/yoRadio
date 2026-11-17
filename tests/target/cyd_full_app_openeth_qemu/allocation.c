/* Diagnostic-only public libc allocation observations. No refusal injection,
 * replacement storage, codec internals or changes to allocator results. */
#include <stddef.h>
#include <stdint.h>
#include <stdatomic.h>
#include "esp_heap_caps.h"
#include "esp_rom_sys.h"

static atomic_uint observations;
enum { MINIMUM_BYTES = 32768, MAXIMUM_OBSERVATIONS = 12 };

void *__real_malloc(size_t bytes);
void *__real_calloc(size_t count, size_t size);

static unsigned ticket(size_t bytes) {
    return bytes >= MINIMUM_BYTES ? atomic_fetch_add(&observations, 1u) : MAXIMUM_OBSERVATIONS;
}

static void note(unsigned index, const char *call, size_t bytes, size_t free_before,
                 size_t largest_before, const void *result) {
    esp_rom_printf("CYD_OPENETH_ALLOCATION index=%u call=%s bytes=%u free_before=%u largest_before=%u success=%u\n",
                   index, call, (unsigned)bytes, (unsigned)free_before,
                   (unsigned)largest_before, result != NULL);
}

void *__wrap_malloc(size_t bytes) {
    unsigned index = ticket(bytes);
    if (index >= MAXIMUM_OBSERVATIONS) return __real_malloc(bytes);
    size_t free_before = heap_caps_get_free_size(MALLOC_CAP_8BIT);
    size_t largest_before = heap_caps_get_largest_free_block(MALLOC_CAP_8BIT);
    void *result = __real_malloc(bytes);
    note(index, "malloc", bytes, free_before, largest_before, result);
    return result;
}

void *__wrap_calloc(size_t count, size_t size) {
    if (!count || size > SIZE_MAX / count) return __real_calloc(count, size);
    size_t bytes = count * size;
    unsigned index = ticket(bytes);
    if (index >= MAXIMUM_OBSERVATIONS) return __real_calloc(count, size);
    size_t free_before = heap_caps_get_free_size(MALLOC_CAP_8BIT);
    size_t largest_before = heap_caps_get_largest_free_block(MALLOC_CAP_8BIT);
    void *result = __real_calloc(count, size);
    note(index, "calloc", bytes, free_before, largest_before, result);
    return result;
}
