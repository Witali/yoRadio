#ifndef SMALL_TV_JPEG_PRIVACY_H
#define SMALL_TV_JPEG_PRIVACY_H

#include <stddef.h>
#include <stdint.h>

typedef enum {
    JPEG_PRIVACY_OK=0, JPEG_PRIVACY_ARGUMENT, JPEG_PRIVACY_INVALID,
    JPEG_PRIVACY_TRUNCATED, JPEG_PRIVACY_METADATA, JPEG_PRIVACY_THUMBNAIL,
    JPEG_PRIVACY_TRAILING, JPEG_PRIVACY_IO, JPEG_PRIVACY_STOP
} jpeg_privacy_result_t;

typedef struct {
    void *context;
    uint32_t length;
    int (*read)(void *context,uint32_t offset,void *data,size_t bytes);
    int (*check)(void *context);
} jpeg_privacy_source_t;

typedef struct {
    jpeg_privacy_result_t status;
    uint32_t offset,width,height,scans;
    uint8_t marker,process,precision,components;
    int callback_error;
} jpeg_privacy_diagnostic_t;

/* REQUESTED_CHANGE: structural metadata gate, separate from codec support and
 * resource validation. No heap, mutable globals, JPEG library or platform types.
 * A successful gate is NOT proof that entropy/tables/dimensions are decodable.
 * Only fixed JFIF without thumbnail and canonical structural Adobe APP14 are
 * allowed; all other APP/COM, including between scans, and trailing bytes fail.
 * Source/check contexts outlive the call. The owner serializes source updates
 * and supplies verified reads; every buffered parser step checks cancellation. */
jpeg_privacy_result_t jpeg_privacy_check(const jpeg_privacy_source_t *source,
                                       jpeg_privacy_diagnostic_t *diagnostic);
const char *jpeg_privacy_status_name(jpeg_privacy_result_t status);

#endif
