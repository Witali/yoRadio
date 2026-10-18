#pragma once
#include "esp_http_server.h"
#include "native_ota_sink.h"

#define NATIVE_OTA_BODY_OVERHEAD 4096U
#define NATIVE_OTA_IDLE_US UINT64_C(10000000)
#define NATIVE_OTA_OVERALL_US UINT64_C(180000000)
typedef struct {
    native_ota_policy_t policy;
    size_t max_body_bytes;
    // Reserve reboot/activity before receiving the body. The image policy's
    // before_flash callback must acquire synchronous audio maintenance.
    esp_err_t (*admit)(void *context, uint64_t absolute_deadline_us);
    // Once, after response attempt and shutdown. Activation requires a
    // preallocated reboot commit even if the response could not be sent.
    void (*finish)(void *context, bool activated);
    void *context;
} native_ota_http_config_t;
// Always ESP_FAIL: close this session, never SDK-purge an unread body or retain
// its request-scoped overrides. The wire response still reports HTTP success.
esp_err_t native_ota_http_upload(httpd_req_t *, const native_ota_http_config_t *);
esp_err_t native_ota_http_info(httpd_req_t *, size_t image_limit);
