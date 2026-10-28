#ifndef SMALL_TV_JPEG_SCRATCH_H
#define SMALL_TV_JPEG_SCRATCH_H

#include "jpeg_nor.h"

#define JPEG_SCRATCH_MAX_FILES 16u

typedef enum {
    JPEG_SCRATCH_OK=0, JPEG_SCRATCH_ARGUMENT, JPEG_SCRATCH_STATE,
    JPEG_SCRATCH_RANGE, JPEG_SCRATCH_CAPACITY, JPEG_SCRATCH_UNINITIALIZED,
    JPEG_SCRATCH_IO, JPEG_SCRATCH_STOP, JPEG_SCRATCH_LIMIT
} jpeg_scratch_result_t;

typedef struct {
    uint32_t offset,bytes,initialized;
    uint64_t id;
    bool used;
} jpeg_scratch_region_t;

typedef struct {
    jpeg_nor_t *store;
    void *check_context;
    int (*check)(void *context);
    jpeg_scratch_region_t files[JPEG_SCRATCH_MAX_FILES];
    uint64_t next_id,read_bytes,write_bytes;
    uint32_t active_bytes,peak_bytes;
    unsigned active_files,peak_files;
    jpeg_nor_result_t last_nor_error;
    bool active,failed;
} jpeg_scratch_t;

typedef struct {
    jpeg_scratch_t *owner;
    uint64_t id;
    unsigned slot;
} jpeg_scratch_file_t;

/* Zero-initialize once; serialize access. Reopen preserves increasing IDs so
 * stale by-value file tokens cannot revive after close/abort/reuse of a slot.
 * One already-open NOR store/cache serves ALL byte-granular virtual files.
 * check is mandatory (e.g. jpeg_transport_check wrapper), including RAM-only I/O.
 * Owner must not zero/recycle this object's memory while old tokens exist. */
jpeg_scratch_result_t jpeg_scratch_open(jpeg_scratch_t *scratch,jpeg_nor_t *store,
    int (*check)(void *),void *check_context);
jpeg_scratch_result_t jpeg_scratch_allocate(jpeg_scratch_t *scratch,uint32_t bytes,jpeg_scratch_file_t *file);
/* Initialize in order, then allow arbitrary overwrite/read of that prefix.
 * Gaps/uninitialized reads are rejected before touching storage. This matches
 * the pinned libjpeg virtual-array contract, not an unrestricted POSIX file. */
jpeg_scratch_result_t jpeg_scratch_read(const jpeg_scratch_file_t *file,uint32_t offset,void *data,size_t bytes);
jpeg_scratch_result_t jpeg_scratch_write(const jpeg_scratch_file_t *file,uint32_t offset,const void *data,size_t bytes);
/* Cleanup is allowed after a failed job, without checkpoint or I/O. */
jpeg_scratch_result_t jpeg_scratch_close(const jpeg_scratch_file_t *file);
/* Invalidate all files and discard NOR dirty RAM, without flushing temp data. */
void jpeg_scratch_abort(jpeg_scratch_t *scratch);

#endif
