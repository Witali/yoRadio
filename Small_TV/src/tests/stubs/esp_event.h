#pragma once
#include <stdint.h>
#include "esp_err.h"
typedef const char *esp_event_base_t;
extern const char wifi_event_base[], ip_event_base[];
#define WIFI_EVENT wifi_event_base
#define IP_EVENT ip_event_base
enum
{
    ESP_EVENT_ANY_ID = -1,
    WIFI_EVENT_STA_START = 1,
    WIFI_EVENT_STA_DISCONNECTED,
    IP_EVENT_STA_GOT_IP
};
esp_err_t esp_event_loop_create_default(void);
esp_err_t esp_event_handler_register(esp_event_base_t base, int32_t id,
                                     void (*handler)(void *, esp_event_base_t, int32_t, void *),
                                     void *context);
