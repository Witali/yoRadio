#pragma once
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
/* Diagnostic only: one locked snapshot; UINT32_MAX largest means bad links.
 * No allocation or logging. Coupled to the ESP8266 v3.4 untraced allocator. */
typedef struct { uint32_t free_dram, largest_dram; } native_heap_diag_t;
native_heap_diag_t native_heap_diag_snapshot(void);
#ifdef __cplusplus
}
#endif
