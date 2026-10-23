#ifndef SMALL_TV_JPEG_BASELINE_H
#define SMALL_TV_JPEG_BASELINE_H
#include "jpeg_decoder.h"

/* Factory-compatible TJpgd producer with an iMCU strip, never a full framebuffer.
 * A prepare-time unsupported result permits a different decoder before any rows.
 * Once rows are emitted, no fallback may publish them after a failed decode. */
jpeg_decode_status_t jpeg_baseline_decode(const jpeg_decode_request_t *request,
    const jpeg_decode_allocator_t *allocator,jpeg_decode_diagnostic_t *diagnostic);
#endif
