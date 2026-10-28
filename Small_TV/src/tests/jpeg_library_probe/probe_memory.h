/* Host-only resource instrumentation for an unmodified libjpeg-turbo build. */
#ifndef SMALL_TV_JPEG_PROBE_MEMORY_H
#define SMALL_TV_JPEG_PROBE_MEMORY_H
#include <stddef.h>

typedef struct {
    size_t current_bytes, peak_bytes, limit_bytes;
    unsigned stores_opened, stores_closed;
    unsigned long long backing_capacity, bytes_read, bytes_written;
    int allow_backing;
    unsigned long long nor_calls,nor_read_bytes,nor_program_bytes,nor_erases,nor_fault_hits;
    unsigned scratch_peak_files,scratch_error;
    size_t scratch_peak_bytes;
} probe_memory_stats;

void probe_memory_reset(size_t limit_bytes, int allow_backing);
probe_memory_stats probe_memory_snapshot(void);
#endif
