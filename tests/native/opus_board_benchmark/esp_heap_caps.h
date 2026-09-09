#pragma once
#include <stddef.h>
#ifdef __cplusplus
extern "C" {
#endif
#define MALLOC_CAP_8BIT 4U
void *heap_caps_malloc(size_t bytes, unsigned caps);
void heap_caps_free(void *pointer);
size_t heap_caps_get_free_size(unsigned caps);
#ifdef __cplusplus
}
#endif
