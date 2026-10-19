/* Host-only resource instrumentation for an unmodified libjpeg-turbo build. */
#ifndef SMALL_TV_JPEG_PROBE_MEMORY_H
#define SMALL_TV_JPEG_PROBE_MEMORY_H
#include <stddef.h>

typedef struct {
    size_t current_bytes, peak_bytes, limit_bytes;
    unsigned stores_opened, stores_closed;
    unsigned long long backing_capacity, bytes_read, bytes_written;
    int allow_backing;
} probe_memory_stats;

void probe_memory_reset(size_t limit_bytes, int allow_backing);
probe_memory_stats probe_memory_snapshot(void);
#endif
