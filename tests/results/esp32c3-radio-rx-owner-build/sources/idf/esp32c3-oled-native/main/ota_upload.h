#pragma once

#include "esp_ota_ops.h"
#include "web_multipart.h"

/* One bounded workspace per request; never buffer an entire application. */
typedef struct {
    web_multipart_t parser;
    const esp_partition_t *partition;
    esp_ota_handle_t handle;
    bool started, verified, target_seen, image_seen, image_complete;
    bool target_part;
    size_t received, buffered, target_length;
    char target[16];
    uint8_t buffer[4096];
    const char *error;
} ota_upload_t;

bool ota_upload_init(ota_upload_t *upload, const char *boundary);
bool ota_upload_feed(ota_upload_t *upload, const uint8_t *data, size_t size);
bool ota_upload_finish(ota_upload_t *upload);
bool ota_upload_activate(ota_upload_t *upload);
void ota_upload_abort(ota_upload_t *upload);
