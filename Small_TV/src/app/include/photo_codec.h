#pragma once
#include "esp_err.h"
#include "jpeg_decoder.h"
#include "jpeg_privacy.h"
#include "jpeg_cache.h"

typedef enum {
    PHOTO_OK=0,PHOTO_BUSY,PHOTO_ARGUMENT,PHOTO_STORAGE,PHOTO_PRIVACY,
    PHOTO_DECODE,PHOTO_VERIFY,PHOTO_SETTINGS,PHOTO_MEMORY
} photo_status_t;
typedef struct {
    photo_status_t status;
    jpeg_decode_diagnostic_t decode;
    jpeg_privacy_diagnostic_t privacy;
    jpeg_cache_result_t cache;
    unsigned transport;
    int io;
    uint64_t required,available,program_bytes;
    bool available_known;
    bool cached,baseline,service_memory,write_limit;
} photo_diagnostic_t;

/* One owner, serialized by the media worker's codec mutex. Source mutations
 * must be excluded for the full job. Initialization authorizes immutable assets
 * before any cache/scratch writes. Draw's row callback paints only verified data. */
esp_err_t photo_codec_init(void);
esp_err_t photo_codec_invalidate(unsigned slot,photo_diagnostic_t *diagnostic);
esp_err_t photo_codec_prepare(unsigned slot,uint32_t length,bool background,uint64_t prior_program_bytes,
                             photo_diagnostic_t *diagnostic);
esp_err_t photo_codec_draw(unsigned slot,uint32_t length,
    int (*row)(void *,uint32_t,const uint16_t *,uint32_t),void *context,
    photo_diagnostic_t *diagnostic);
/* Platform binding and worker checkpoint; no HTTP/LCD types enter the codec. */
int photo_codec_cancelled(void);
void photo_diagnostic_describe(const photo_diagnostic_t *diagnostic,char *text,size_t bytes);
