#pragma once
#include "native_ota_sink.h"
#include "web_multipart.h"

// Bounded multipart envelope around the image-only sink. Target precedes one
// selected firmware file. Storage, maintenance and reboot belong to callers.
typedef struct {
    web_multipart_t parser;
    native_ota_sink_t image;
    const esp_partition_t *partition;
    bool target_seen, image_seen, image_complete, target_part;
    size_t target_length;
    char target[16];
    const char *error;
} native_ota_form_t;
bool native_ota_form_init(native_ota_form_t *, const char *, const native_ota_policy_t *);
bool native_ota_form_feed(native_ota_form_t *, const uint8_t *, size_t);
bool native_ota_form_finish(native_ota_form_t *);
bool native_ota_form_activate(native_ota_form_t *);
void native_ota_form_abort(native_ota_form_t *);
