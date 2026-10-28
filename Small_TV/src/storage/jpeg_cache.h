#ifndef SMALL_TV_JPEG_CACHE_H
#define SMALL_TV_JPEG_CACHE_H

#include "jpeg_guard.h"
#include "jpeg_journal.h"

typedef enum {
    JPEG_CACHE_OK=0,JPEG_CACHE_MISS,JPEG_CACHE_ARGUMENT,JPEG_CACHE_STATE,
    JPEG_CACHE_STOP,JPEG_CACHE_IO,JPEG_CACHE_HASH,JPEG_CACHE_VERIFY,
    JPEG_CACHE_SOURCE_CHANGED,JPEG_CACHE_JOURNAL,JPEG_CACHE_SOURCE_LIMIT
} jpeg_cache_result_t;

typedef struct {
    const jpeg_nor_extent_t *extents;
    unsigned count;
} jpeg_cache_map_t;

typedef struct {
    jpeg_journal_config_t journal;
    uint32_t width,height,source_offsets[JPEG_JOURNAL_SLOTS];
    jpeg_cache_map_t frames[JPEG_JOURNAL_SLOTS];
    const jpeg_nor_extent_t *allowed;
    unsigned allowed_count;
} jpeg_cache_layout_t;

typedef struct {
    /* Already authorized epoch-bound ports: source is readonly; frame/metadata
     * are restricted to their own capabilities. All share ONE transport budget. */
    jpeg_nor_device_t source,frames,metadata;
} jpeg_cache_devices_t;

typedef struct {
    jpeg_journal_t journal;
    jpeg_nor_t frame;
    const jpeg_cache_layout_t *layout;
    jpeg_cache_devices_t devices;
    jpeg_guard_sha256_t hash;
    int (*check)(void *context);
    void *check_context;
    uint8_t source_sha256[32],frame_sha256[32];
    uint32_t source_bytes,next_row;
    uint32_t required,available; /* Source-slot capacity refusal, before source I/O. */
    unsigned slot;
    jpeg_cache_result_t last_error;
    jpeg_nor_result_t nor_error;
    jpeg_journal_result_t journal_error;
    int callback_error;
    bool open,failed,writing,verified,hash_active;
} jpeg_cache_t;

/* No heap/globals. Zero-initialize once; serialize against ALL source/media and
 * resource updates until abort, including cache display reads after lookup.
 * Config/device/crypto/check contexts outlive the job. codec_id MUST bind codec,
 * RGB565 policy AND width/height; source length comes from committed settings or
 * the complete upload, never metadata alone. Open validates before readonly I/O.
 * Reopen for each new transport epoch; abort all borrowers before port reuse. */
jpeg_cache_result_t jpeg_cache_open(jpeg_cache_t *cache,const jpeg_cache_layout_t *layout,
    const jpeg_cache_devices_t *devices,const jpeg_guard_sha256_t *hash,
    int (*check)(void *),void *check_context);
/* Durable invalidation BEFORE source erase/write; no frame/source writes here. */
jpeg_cache_result_t jpeg_cache_invalidate(jpeg_cache_t *cache,unsigned slot);
/* Hash CURRENT physical JPEG and ENTIRE physical frame before authorizing reads.
 * Corrupt metadata/frame means a miss/verify failure, never permission to draw. */
jpeg_cache_result_t jpeg_cache_lookup(jpeg_cache_t *cache,unsigned slot,uint32_t source_bytes);
/* Begin invalidates durably, hashes physical source, opens disposable frame and
 * starts output SHA. Rows are provisional; only successful commit publishes. */
jpeg_cache_result_t jpeg_cache_begin(jpeg_cache_t *cache,unsigned slot,uint32_t source_bytes);
jpeg_cache_result_t jpeg_cache_write_row(jpeg_cache_t *cache,uint32_t row,const uint16_t *pixels,uint32_t count);
/* Exact bounded persistent input during begin/commit. Fresh256-byte readbacks
 * verify each returned buffer; budget these reads as well as the original read. */
jpeg_cache_result_t jpeg_cache_read_source(jpeg_cache_t *cache,uint32_t offset,void *data,size_t bytes);
/* Finish row SHA, sync, rehash physical source/frame, THEN journal publication.
 * Do not call after decoder failure, even if every row happened to be emitted. */
jpeg_cache_result_t jpeg_cache_commit(jpeg_cache_t *cache);
/* Only after lookup/commit OK; same owner/epoch/media lock remains required. */
jpeg_cache_result_t jpeg_cache_read_row(jpeg_cache_t *cache,uint32_t row,uint16_t *pixels,uint32_t count);
/* Discard dirty RAM/hash/transaction without flash I/O; never publish on cleanup. */
void jpeg_cache_abort(jpeg_cache_t *cache);

#endif
