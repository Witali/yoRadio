#ifndef SMALL_TV_JPEG_DECODER_H
#define SMALL_TV_JPEG_DECODER_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Network/LCD/platform code needs no libjpeg types. Callbacks are serialized,
 * borrowed only during decode, and return0 on exact success. Output rows are
 * provisional: the owner may publish a cache/photo only after DECODE_OK. */
typedef enum {
    JPEG_DECODE_OK=0, JPEG_DECODE_ARGUMENT, JPEG_DECODE_INVALID, JPEG_DECODE_TRUNCATED,
    JPEG_DECODE_UNSUPPORTED, JPEG_DECODE_DIMENSIONS, JPEG_DECODE_POOL_LIMIT,
    JPEG_DECODE_ALLOCATION, JPEG_DECODE_BACKING_LIMIT, JPEG_DECODE_BACKING_FILES,
    JPEG_DECODE_INPUT_IO, JPEG_DECODE_OUTPUT_IO, JPEG_DECODE_BACKING_IO,
    JPEG_DECODE_CANCELLED, JPEG_DECODE_TIME_LIMIT, JPEG_DECODE_IO_LIMIT,
    JPEG_DECODE_INTERNAL
} jpeg_decode_status_t;

typedef enum { JPEG_CHECK_OK=0, JPEG_CHECK_CANCELLED, JPEG_CHECK_TIME, JPEG_CHECK_IO_LIMIT } jpeg_decode_check_t;
typedef enum {
    JPEG_DETAIL_NONE=0,JPEG_DETAIL_WIDTH,JPEG_DETAIL_HEIGHT,JPEG_DETAIL_PROCESS,
    JPEG_DETAIL_PRECISION,JPEG_DETAIL_SAMPLING,JPEG_DETAIL_ARITHMETIC,
    JPEG_DETAIL_COLORSPACE,JPEG_DETAIL_DNL,JPEG_DETAIL_FEATURE,JPEG_DETAIL_SAMPLE_RANGE
} jpeg_decode_detail_t;
typedef struct {
    jpeg_decode_status_t status;
    jpeg_decode_detail_t detail;
    int library_error,library_parameter,callback_error;
    uint64_t required,available,pool_peak,backing_required,backing_peak,input_bytes;
    uint32_t width,height,rows,stores_opened,stores_closed;
    size_t context_bytes,pool_retained;
    bool reused_object;
    bool available_known; /* false for allocator failure: free heap is unknown. */
} jpeg_decode_diagnostic_t;

typedef struct {
    void *context;
    void *(*allocate)(void *context,size_t bytes);
    void (*release)(void *context,void *data,size_t bytes);
} jpeg_decode_allocator_t;

typedef struct {
    void *context;
    uint32_t capacity;
    /* coefficients=true only for the direct progressive JBLOCK-only path.
     * An unsuccessful open owns no handle; close must release even after an
     * earlier I/O error, without flushing disposable temporary data. */
    int (*open)(void *context,uint32_t bytes,bool coefficients,uint64_t *handle);
    int (*read)(void *context,uint64_t handle,uint32_t offset,void *data,size_t bytes);
    int (*write)(void *context,uint64_t handle,uint32_t offset,const void *data,size_t bytes);
    int (*close)(void *context,uint64_t handle);
} jpeg_decode_backing_t;

typedef struct {
    jpeg_decode_allocator_t allocator;
    jpeg_decode_backing_t backing;
    size_t pool_limit; /* Library pools only; context/SDK/stack are separate. */
    uint32_t max_width,max_height; /*1..240, native unscaled image dimensions. */
} jpeg_decoder_config_t;

typedef struct {
    void *context;
    uint32_t length,expected_width,expected_height; /* expected0 accepts any <=max. */
    int (*read)(void *context,uint32_t offset,void *data,size_t bytes);
    int (*row)(void *context,uint32_t y,const uint16_t *rgb565,uint32_t pixels);
    jpeg_decode_check_t (*check)(void *context); /* Mandatory, including RAM work. */
} jpeg_decode_request_t;

typedef struct jpeg_decoder jpeg_decoder_t;
/* Context allocation is reported separately. Creation does not parse/decode.
 * One owner serializes calls; independent instances do not share mutable state.
 * Context/allocator/backing must outlive all operations. No stdio/ESP-IDF/logging. */
jpeg_decoder_t *jpeg_decoder_create(const jpeg_decoder_config_t *config,jpeg_decode_diagnostic_t *diagnostic);
jpeg_decode_status_t jpeg_decoder_decode(jpeg_decoder_t *decoder,const jpeg_decode_request_t *request,
                                        jpeg_decode_diagnostic_t *diagnostic);
void jpeg_decoder_destroy(jpeg_decoder_t *decoder);
const char *jpeg_decoder_status_name(jpeg_decode_status_t status);

#endif
