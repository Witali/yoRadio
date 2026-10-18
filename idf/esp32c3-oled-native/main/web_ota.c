#include "web_ota.h"
#include <string.h>
#include "deep_sleep_clock.h"
#include "display_settings.h"
#include "native_ota_http.h"
#include "websocket_service.h"

// The C3 audio owner currently has no acknowledged maintenance API. Until it
// provides that contract, reject application OTA before body/flash rather than
// using asynchronous audio_service_stop as permission to erase.
static esp_err_t ota_admit(void *context, uint64_t deadline) {
    (void)context; (void)deadline;
    return ESP_ERR_NOT_SUPPORTED;
}
static esp_err_t ota_before_flash(void *context) { (void)context; return ESP_ERR_NOT_SUPPORTED; }
static void ota_finished(void *context, bool activated) { (void)context; (void)activated; }

esp_err_t web_ota_handler(httpd_req_t *request) {
    const esp_partition_t *running = esp_ota_get_running_partition();
    const esp_partition_t *next = running ? esp_ota_get_next_update_partition(running) : NULL;
    native_ota_http_config_t config = {
        .policy = {.expected_chip = ESP_CHIP_ID_ESP32C3, .image_limit = next ? next->size : 1,
            .before_flash = ota_before_flash},
        .admit = ota_admit, .finish = ota_finished,
    };
    memcpy(config.policy.expected_project, esp_app_get_description()->project_name, sizeof(config.policy.expected_project));
    return native_ota_http_upload(request, &config);
}
esp_err_t web_ota_info_handler(httpd_req_t *request) {
    if (!deep_sleep_clock_begin_activity()) {
        httpd_resp_set_status(request, "503 Service Unavailable");
        return httpd_resp_sendstr(request, "Wake the radio with BOOT");
    }
    display_settings_note_activity();
    const esp_partition_t *running = esp_ota_get_running_partition();
    const esp_partition_t *next = running ? esp_ota_get_next_update_partition(running) : NULL;
    esp_err_t result = native_ota_http_info(request, next ? next->size : 0);
    deep_sleep_clock_end_activity();
    return result;
}
