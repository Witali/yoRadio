#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "bootloader_random.h"
#include "esp_app_desc.h"
#include "esp_app_format.h"
#include "esp_event.h"
#include "esp_http_server.h"
#include "esp_image_format.h"
#include "esp_mac.h"
#include "esp_netif.h"
#include "esp_ota_ops.h"
#include "esp_random.h"
#include "esp_system.h"
#include "esp_timer.h"
#include "esp_wifi.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#if CONFIG_IDF_TARGET_ESP32
#define RECOVERY_CHIP ESP_CHIP_ID_ESP32
#define YORADIO_PROJECT "yoradio_cyd2usb_native"
#elif CONFIG_IDF_TARGET_ESP32C3
#define RECOVERY_CHIP ESP_CHIP_ID_ESP32C3
#define YORADIO_PROJECT "yoradio_esp32c3_oled_native"
#else
#error Unsupported recovery target
#endif

#define IMAGE_PREFIX_SIZE (sizeof(esp_image_header_t) + sizeof(esp_image_segment_header_t) + sizeof(esp_app_desc_t))
#define UPLOAD_TIMEOUT_US INT64_C(180000000)

extern const char upload_html_start[] asm("_binary_upload_html_start");

static esp_err_t upload_error(httpd_req_t *request, httpd_err_code_t status, const char *message)
{
    httpd_resp_send_err(request, status, message);
    return ESP_FAIL;
}

static bool read_chunk(httpd_req_t *request, uint8_t *buffer, size_t count, int64_t started)
{
    while (count > 0 && esp_timer_get_time() - started < UPLOAD_TIMEOUT_US) {
        int received = httpd_req_recv(request, (char *)buffer, count);
        if (received <= 0) {
            return false;
        }
        buffer += received;
        count -= received;
    }
    return count == 0;
}

static bool matches_board(const uint8_t *prefix)
{
    esp_image_header_t header;
    esp_app_desc_t description;
    memcpy(&header, prefix, sizeof(header));
    memcpy(&description, prefix + sizeof(header) + sizeof(esp_image_segment_header_t),
           sizeof(description));
    return header.magic == ESP_IMAGE_HEADER_MAGIC && header.chip_id == RECOVERY_CHIP &&
           description.magic_word == ESP_APP_DESC_MAGIC_WORD &&
           strncmp(description.project_name, YORADIO_PROJECT, sizeof(description.project_name)) == 0;
}

static esp_err_t upload_firmware(httpd_req_t *request)
{
    const esp_partition_t *target = request->user_ctx;
    const size_t length = request->content_len;
    char type[sizeof("application/octet-stream")];
    if (httpd_req_get_hdr_value_str(request, "Content-Type", type, sizeof(type)) != ESP_OK ||
        strcmp(type, "application/octet-stream") != 0 ||
        length < IMAGE_PREFIX_SIZE || length > target->size) {
        return upload_error(request, HTTPD_400_BAD_REQUEST, "Send one application .bin that fits the OTA slot.");
    }

    uint8_t chunk[1024];
    const int64_t started = esp_timer_get_time();
    if (!read_chunk(request, chunk, IMAGE_PREFIX_SIZE, started) || !matches_board(chunk)) {
        return upload_error(request, HTTPD_400_BAD_REQUEST, "Choose the native yoRadio app.bin for this board.");
    }

    // Recovery can also have been selected by the bootloader after a failed app boot.
    // Clear any stale OTA boot selection before erasing sectors in the sole app slot.
    if (esp_ota_set_boot_partition(esp_ota_get_running_partition()) != ESP_OK) {
        return upload_error(request, HTTPD_500_INTERNAL_SERVER_ERROR, "Cannot keep recovery selected for boot.");
    }
    esp_ota_handle_t handle;
    if (esp_ota_begin(target, OTA_WITH_SEQUENTIAL_WRITES, &handle) != ESP_OK) {
        return upload_error(request, HTTPD_500_INTERNAL_SERVER_ERROR, "Cannot start OTA.");
    }

    size_t count = IMAGE_PREFIX_SIZE;
    size_t remaining = length;
    for (;;) {
        if (esp_ota_write(handle, chunk, count) != ESP_OK) {
            esp_ota_abort(handle);
            return upload_error(request, HTTPD_500_INTERNAL_SERVER_ERROR, "Flash write failed.");
        }
        remaining -= count;
        if (remaining == 0) {
            break;
        }
        count = remaining < sizeof(chunk) ? remaining : sizeof(chunk);
        if (!read_chunk(request, chunk, count, started)) {
            esp_ota_abort(handle);
            return upload_error(request, HTTPD_400_BAD_REQUEST, "Upload interrupted or timed out. Retry in recovery.");
        }
    }

    const esp_partition_pos_t position = {.offset = target->address, .size = target->size};
    esp_image_metadata_t metadata;
    if (esp_ota_end(handle) != ESP_OK ||
        esp_image_get_metadata(&position, &metadata) != ESP_OK || metadata.image_len != length) {
        return upload_error(request, HTTPD_400_BAD_REQUEST, "Firmware image verification failed.");
    }
    if (esp_ota_set_boot_partition(target) != ESP_OK) {
        return upload_error(request, HTTPD_500_INTERNAL_SERVER_ERROR, "Cannot select the new application for boot.");
    }

    httpd_resp_set_type(request, "text/plain; charset=utf-8");
    httpd_resp_sendstr(request, "Firmware installed. yoRadio is restarting.");
    vTaskDelay(pdMS_TO_TICKS(500));
    esp_restart();
}

static esp_err_t show_upload_page(httpd_req_t *request)
{
    httpd_resp_set_type(request, "text/html; charset=utf-8");
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    return httpd_resp_sendstr(request, upload_html_start);
}

static void start_access_point(void)
{
    wifi_config_t config = {.ap = {.channel = 1, .max_connection = 1, .authmode = WIFI_AUTH_WPA2_PSK}};
    uint8_t mac[6];
    ESP_ERROR_CHECK(esp_read_mac(mac, ESP_MAC_WIFI_SOFTAP));
    config.ap.ssid_len = snprintf((char *)config.ap.ssid, sizeof(config.ap.ssid),
                                   "yoRadio-Recovery-%02X%02X%02X", mac[3], mac[4], mac[5]);

    // Supply hardware entropy before Wi-Fi starts. The password lives only in RAM.
    uint8_t random[12];
    bootloader_random_enable();
    esp_fill_random(random, sizeof(random));
    bootloader_random_disable();
    const char hex[] = "0123456789abcdef";
    for (size_t i = 0; i < sizeof(random); ++i) {
        config.ap.password[2 * i] = hex[random[i] >> 4];
        config.ap.password[2 * i + 1] = hex[random[i] & 15];
    }

    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_ap();
    wifi_init_config_t init = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&init));
    ESP_ERROR_CHECK(esp_wifi_set_storage(WIFI_STORAGE_RAM));
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_AP));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_AP, &config));
    ESP_ERROR_CHECK(esp_wifi_start());
    printf("Recovery network: %s\nWPA2 password: %s\nOpen http://192.168.4.1/\n",
           (const char *)config.ap.ssid, (const char *)config.ap.password);
}

void app_main(void)
{
    const esp_partition_t *running = esp_ota_get_running_partition();
    const esp_partition_t *target = esp_partition_find_first(ESP_PARTITION_TYPE_APP,
                                                              ESP_PARTITION_SUBTYPE_APP_OTA_0, NULL);
    if (!running || running->subtype != ESP_PARTITION_SUBTYPE_APP_FACTORY || !target) {
        puts("Recovery requires a factory partition and an ota_0 partition.");
        return;
    }

    start_access_point();
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.stack_size = 6144;
    config.max_uri_handlers = 2;
    httpd_handle_t server;
    ESP_ERROR_CHECK(httpd_start(&server, &config));
    const httpd_uri_t page = {.uri = "/", .method = HTTP_GET, .handler = show_upload_page};
    const httpd_uri_t upload = {.uri = "/firmware", .method = HTTP_POST, .handler = upload_firmware,
                                .user_ctx = (void *)target};
    ESP_ERROR_CHECK(httpd_register_uri_handler(server, &page));
    ESP_ERROR_CHECK(httpd_register_uri_handler(server, &upload));
}
