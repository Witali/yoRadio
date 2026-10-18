#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Metadata only; never dereference a payload. Keep this on the AAC task stack,
// not in BSS/heap, so diagnostics do not reserve another large heap block.
#define HEAP_LAYOUT_ROWS 128
typedef struct {
    uintptr_t heap, address;
    uint32_t size_used; // Payload size, with the high bit marking an allocation.
} heap_layout_row_t;
typedef struct {
    heap_layout_row_t rows[HEAP_LAYOUT_ROWS], previous;
    size_t count, dropped, blocks, free_bytes, used_bytes;
    bool have_previous, next_neighbor;
} heap_layout_capture_t;

static inline void heap_layout_append(heap_layout_capture_t *s, heap_layout_row_t row) {
    if (s->count && s->rows[s->count-1].address == row.address &&
        s->rows[s->count-1].heap == row.heap) return;
    if (s->count == HEAP_LAYOUT_ROWS) { ++s->dropped; return; }
    s->rows[s->count++] = row;
}

static inline void heap_layout_record(heap_layout_capture_t *s, uintptr_t heap,
                                     uintptr_t address, size_t size, bool used) {
    heap_layout_row_t row = {heap, address, (uint32_t)size | (used ? UINT32_C(0x80000000) : 0)};
    if (s->have_previous && s->previous.heap != heap) {
        s->have_previous = false;
        s->next_neighbor = false;
    }
    ++s->blocks;
    if (used) s->used_bytes += size; else s->free_bytes += size;
    bool free_area = !used && size >= 256;
    if (free_area && s->have_previous) heap_layout_append(s, s->previous);
    if (free_area || (used && size >= 1024) || s->next_neighbor)
        heap_layout_append(s, row);
    s->next_neighbor = free_area;
    s->previous = row;
    s->have_previous = true;
}
