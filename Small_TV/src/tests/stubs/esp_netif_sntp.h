#pragma once
#include <stdbool.h>
#include "esp_err.h"
typedef struct
{
    unsigned num_servers;
    const char *servers[3];
    bool wait_for_sync;
} esp_sntp_config_t;
#define ESP_SNTP_SERVER_LIST(...) __VA_ARGS__
#define ESP_NETIF_SNTP_DEFAULT_CONFIG_MULTIPLE(n, ...)                                             \
    {.num_servers = (n), .servers = {__VA_ARGS__}, .wait_for_sync = true}
esp_err_t esp_netif_sntp_init(const esp_sntp_config_t *config);
void esp_netif_sntp_deinit(void);
