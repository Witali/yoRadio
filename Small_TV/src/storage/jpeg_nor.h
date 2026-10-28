#ifndef SMALL_TV_JPEG_NOR_H
#define SMALL_TV_JPEG_NOR_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Portable storage core; its owner serializes access and validates the generated
 * layout/resource identities before passing a writable capability allowlist.
 * No memory allocation, ESP-IDF dependency, automatic flush or atomic publication.
 * The caller zero-initializes a handle, then closes/aborts it before reopening. */
#define JPEG_NOR_SECTOR_BYTES 4096u
#define JPEG_NOR_MAX_EXTENTS 16u
#define JPEG_NOR_MAX_PAGE_BYTES 256u

typedef enum {
    JPEG_NOR_OK = 0,
    JPEG_NOR_ARGUMENT,
    JPEG_NOR_RANGE,
    JPEG_NOR_STATE,
    JPEG_NOR_IO,
    JPEG_NOR_VERIFY
} jpeg_nor_result_t;

typedef struct {
    uint32_t offset, bytes;
} jpeg_nor_extent_t;

typedef struct {
    void *context;
    uint32_t flash_bytes, page_bytes;
    int (*read)(void *context, uint32_t address, void *data, size_t bytes);
    int (*program)(void *context, uint32_t address, const void *data, size_t bytes);
    int (*erase_sector)(void *context, uint32_t address);
} jpeg_nor_device_t;

typedef struct {
    /* Calls/bytes count requests sent to the transport, including failed ones.
     * Successful counts mean callback success, not a hardware endurance proof. */
    uint64_t read_calls, read_bytes, program_calls, program_bytes, erase_calls;
    uint64_t successful_program_bytes, successful_erases;
    uint64_t logical_read_bytes, logical_write_bytes, cache_loads;
} jpeg_nor_stats_t;

typedef struct {
    jpeg_nor_device_t device;
    jpeg_nor_extent_t extents[JPEG_NOR_MAX_EXTENTS];
    jpeg_nor_stats_t stats;
    uint32_t logical_bytes, cached_sector;
    unsigned extent_count;
    int last_io_error;
    bool open, failed, cached, dirty;
    uint32_t sector_data[JPEG_NOR_SECTOR_BYTES / sizeof(uint32_t)];
} jpeg_nor_t;

/* Extents and allowlist must be sorted, disjoint and sector aligned. The mapped
 * capacity is exactly ceil(logical_bytes/sector)*sector. All validation completes
 * before changing the handle or calling the transport. Descriptors are copied. */
jpeg_nor_result_t jpeg_nor_open(jpeg_nor_t *store, const jpeg_nor_device_t *device,
    const jpeg_nor_extent_t *extents, unsigned extent_count, uint32_t logical_bytes,
    const jpeg_nor_extent_t *allowed, unsigned allowed_count);
jpeg_nor_result_t jpeg_nor_read(jpeg_nor_t *store, uint32_t offset, void *data, size_t bytes);
jpeg_nor_result_t jpeg_nor_write(jpeg_nor_t *store, uint32_t offset, const void *data, size_t bytes);
jpeg_nor_result_t jpeg_nor_sync(jpeg_nor_t *store);
jpeg_nor_result_t jpeg_nor_close(jpeg_nor_t *store);
/* Discard dirty RAM without I/O. Failed writes may already have changed owned
 * flash: higher-level metadata must keep such content unpublished/invalid. */
void jpeg_nor_abort(jpeg_nor_t *store);

#endif
