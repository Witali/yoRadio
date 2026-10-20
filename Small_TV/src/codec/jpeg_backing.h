#ifndef SMALL_TV_JPEG_BACKING_H
#define SMALL_TV_JPEG_BACKING_H

#include "jpeg_decoder.h"
#include "jpeg_scratch.h"

typedef struct {
    jpeg_scratch_t scratch;
    uint8_t *fresh;
    size_t fresh_bytes;
    uint32_t capacity;
    unsigned mode; /*0not selected,1raw,2packed coefficient arrays. */
    jpeg_scratch_result_t last_error;
    bool active;
} jpeg_backing_t;

/* No allocation/globals. Caller zero-initializes once and serializes access.
 * Store must be freshly opened, exclusively disposable temporary space whose
 * physical ownership was already authorized. This does not replace the guard.
 * begin borrows NOR/check/bitmap until abort. Reopen NOR for every new job;
 * capacity stays fixed while a decoder retains the returned callback descriptor.
 * Abort only AFTER decode/cleanup (or before ever decoding), never in callbacks.
 * It drops dirty temp RAM without I/O; source/photos/cache/settings are separate. */
size_t jpeg_backing_bitmap_bytes(uint32_t capacity);
jpeg_scratch_result_t jpeg_backing_begin(jpeg_backing_t *backing,jpeg_nor_t *store,
    int (*check)(void *),void *check_context,uint8_t *bitmap,size_t bitmap_bytes);
jpeg_decode_backing_t jpeg_backing_callbacks(jpeg_backing_t *backing);
void jpeg_backing_abort(jpeg_backing_t *backing);

#endif
