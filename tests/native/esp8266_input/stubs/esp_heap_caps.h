#pragma once
#include <stdlib.h>
#define MALLOC_CAP_8BIT 1
#define heap_caps_malloc(size, caps) malloc(size)
#define heap_caps_calloc(count, size, caps) calloc(count, size)
#define heap_caps_realloc(pointer, size, caps) realloc(pointer, size)
#define heap_caps_free(pointer) free(pointer)
