#pragma once

#include <stdbool.h>
#include <stddef.h>

// One fixed, aligned allocation slot. NULL means use the normal allocator;
// every returned pointer must be released through tls_large_reserve_free.
void *tls_large_reserve_calloc(size_t bytes);
bool tls_large_reserve_free(void *pointer);
void tls_large_reserve_poll(void);
