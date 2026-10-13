#pragma once
#include <stdint.h>
#include <stdbool.h>
#include "esp_err.h"
typedef struct
{
    uint8_t ssid[33];
    int8_t rssi;
} wifi_ap_record_t;
typedef struct
{
    int placeholder;
} wifi_init_config_t;
#define WIFI_INIT_CONFIG_DEFAULT() {0}
typedef struct
{
    bool show_hidden;
} wifi_scan_config_t;
typedef union
{
    struct
    {
        uint8_t ssid[32], password[64];
        struct
        {
            int authmode;
        } threshold;
    } sta;
    struct
    {
        uint8_t ssid[32];
        unsigned ssid_len, channel, max_connection;
        int authmode;
    } ap;
} wifi_config_t;
enum
{
    WIFI_MODE_AP = 1,
    WIFI_MODE_APSTA,
    WIFI_MODE_STA,
    WIFI_IF_AP,
    WIFI_IF_STA,
    WIFI_AUTH_OPEN,
    WIFI_AUTH_WPA2_PSK,
    WIFI_STORAGE_RAM
};
esp_err_t esp_wifi_init(const wifi_init_config_t *config);
esp_err_t esp_wifi_set_storage(int storage);
esp_err_t esp_wifi_set_mode(int mode);
esp_err_t esp_wifi_set_config(int interface, const wifi_config_t *config);
esp_err_t esp_wifi_start(void);
esp_err_t esp_wifi_connect(void);
esp_err_t esp_wifi_scan_start(const wifi_scan_config_t *config, bool block);
esp_err_t esp_wifi_scan_get_ap_records(uint16_t *count, wifi_ap_record_t *records);
esp_err_t esp_wifi_clear_ap_list(void);
