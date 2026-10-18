#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "esp_app_format.h"
#include "esp_err.h"
#include "esp_ota_ops.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    esp_chip_id_t expected_chip; // ESP32's zero chip ID is valid.
    char expected_project[32];  // Exact, NUL-terminated app descriptor field.
    size_t image_limit;         // Explicit board limit; zero is invalid.
    // Called once after a valid prefix and before esp_ota_begin. Success means
    // the caller holds maintenance until failure cleanup or reboot. The caller
    // releases that lease; the sink never resumes audio or schedules a reboot.
    esp_err_t (*before_flash)(void *context);
    void *context;
} native_ota_policy_t;

// One bounded workspace per image. The caller serializes OTA operations and
// must finish/abort before reinitializing a workspace. No HTTP/form dependency.
// Current qualification covers unsigned application images on ESP32/C3 only.
typedef struct {
    native_ota_policy_t policy;
    const esp_partition_t *partition;
    esp_ota_handle_t handle;
    size_t limit, received, buffered;
    bool started, verified, activated, closed, maintenance_entered;
    uint8_t buffer[4096];
    const char *error; // First failure, static storage; never caller-owned.
} native_ota_sink_t;

bool native_ota_sink_init(native_ota_sink_t *sink,
                          const native_ota_policy_t *policy);
bool native_ota_sink_feed(native_ota_sink_t *sink,
                          const uint8_t *data, size_t size);
// Call only after the caller accepted the exact end of the image's envelope.
// Success verifies image contents and exact uploaded length, without changing
// boot selection. Repeated successful finish/activate calls are idempotent.
bool native_ota_sink_finish(native_ota_sink_t *sink);
bool native_ota_sink_activate(native_ota_sink_t *sink);
// Idempotent handle cleanup. Cannot undo a successful boot selection.
void native_ota_sink_abort(native_ota_sink_t *sink);

#ifdef __cplusplus
}
#endif
