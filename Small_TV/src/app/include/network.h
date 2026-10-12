#pragma once
#include <stdbool.h>
#include <stddef.h>
#include "esp_err.h"
#include "esp_wifi.h"
esp_err_t network_init(void);
bool network_connected(void);
bool network_ap_active(void);
void network_address(char *out, size_t size);
esp_err_t network_scan(wifi_ap_record_t *records, uint16_t *count);
void network_restart_later(void);
void dns_start(void);
