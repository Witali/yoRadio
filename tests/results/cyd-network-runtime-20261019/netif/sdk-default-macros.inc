#define ESP_NETIF_DEFAULT_WIFI_AP()                  \
    {                                                \
        .base = ESP_NETIF_BASE_DEFAULT_WIFI_AP,      \
        .driver = NULL,                              \
        .stack = ESP_NETIF_NETSTACK_DEFAULT_WIFI_AP, \
    }
#define ESP_NETIF_DEFAULT_WIFI_STA()                  \
    {                                                 \
        .base = ESP_NETIF_BASE_DEFAULT_WIFI_STA,      \
        .driver = NULL,                               \
        .stack = ESP_NETIF_NETSTACK_DEFAULT_WIFI_STA, \
    }
#define ESP_NETIF_BASE_DEFAULT_WIFI_AP         &_g_esp_netif_inherent_ap_config
#define ESP_NETIF_BASE_DEFAULT_WIFI_STA        &_g_esp_netif_inherent_sta_config
#define ESP_NETIF_NETSTACK_DEFAULT_WIFI_AP      _g_esp_netif_netstack_default_wifi_ap
#define ESP_NETIF_NETSTACK_DEFAULT_WIFI_STA     _g_esp_netif_netstack_default_wifi_sta
