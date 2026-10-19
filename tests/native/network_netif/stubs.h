#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

typedef int esp_err_t;
#define ESP_OK 0
#define ESP_FAIL (-1)
#define ESP_ERR_NO_MEM 0x101
#define ESP_ERR_INVALID_ARG 0x102
#define ESP_ERR_INVALID_STATE 0x103
#define ESP_ERR_NOT_FOUND 0x105
#define ESP_ERR_ESP_NETIF_INVALID_PARAMS 0x5001
#define ESP_ERR_ESP_NETIF_DRIVER_ATTACH_FAILED 0x5002
#define TEST_REGISTER_ERROR 0x7001
#define TEST_DRIVER_ERROR 0x7002
#define TEST_SHUTDOWN_ERROR 0x7003
#define CONFIG_ESP_WIFI_SOFTAP_SUPPORT 1
#define LWIP_IPV4 1
#define LWIP_IGMP 0
#define LWIP_IPV6 0
#define LWIP_IPV6_MLD 0
#define MAX_WIFI_IFS 2
#define ESP_LOGE(...) ((void)0)
#define ESP_LOGD(...) ((void)0)

typedef struct esp_netif esp_netif_t;
typedef void *esp_netif_iodriver_handle;
typedef enum { WIFI_IF_STA, WIFI_IF_AP } wifi_interface_t;
typedef struct wifi_netif_driver *wifi_netif_driver_t;
typedef struct {
    esp_err_t (*post_attach)(esp_netif_t *, void *);
    esp_netif_t *netif;
} esp_netif_driver_base_t;
typedef struct {
    void *handle;
    esp_err_t (*transmit)(void *, void *, size_t);
    esp_err_t (*transmit_wrap)(void *, void *, size_t, void *);
    void (*driver_free_rx_buffer)(void *, void *);
} esp_netif_driver_ifconfig_t;
struct esp_netif {
    void *driver_handle;
    esp_err_t (*driver_transmit)(void *, void *, size_t);
    esp_err_t (*driver_transmit_wrap)(void *, void *, size_t, void *);
    void (*driver_free_rx_buffer)(void *, void *);
    bool ap, clear_called, clear_failed;
};

// Field models for the SDK config's pointer identity only; netif allocation,
// DHCP/lwIP and target layout remain explicit platform seams.
typedef struct { unsigned identity; } esp_netif_inherent_config_t;
typedef struct { unsigned identity; } esp_netif_netstack_config_t;
typedef struct {
    const esp_netif_inherent_config_t *base;
    const void *driver;
    const esp_netif_netstack_config_t *stack;
} esp_netif_config_t;
extern const esp_netif_inherent_config_t _g_esp_netif_inherent_sta_config;
extern const esp_netif_inherent_config_t _g_esp_netif_inherent_ap_config;
extern const esp_netif_netstack_config_t *_g_esp_netif_netstack_default_wifi_sta;
extern const esp_netif_netstack_config_t *_g_esp_netif_netstack_default_wifi_ap;
#include "sdk-default-macros.inc"

esp_netif_t *esp_netif_new(const esp_netif_config_t *config);
void esp_netif_destroy(esp_netif_t *netif);
esp_netif_iodriver_handle esp_netif_get_io_driver(esp_netif_t *netif);
esp_err_t esp_netif_set_driver_config(esp_netif_t *, const esp_netif_driver_ifconfig_t *);
esp_err_t esp_netif_attach(esp_netif_t *, esp_netif_iodriver_handle);
esp_err_t esp_netif_attach_wifi_station(esp_netif_t *);
esp_err_t esp_netif_attach_wifi_ap(esp_netif_t *);
esp_err_t esp_wifi_set_default_wifi_sta_handlers(void);
esp_err_t esp_wifi_set_default_wifi_ap_handlers(void);
esp_err_t esp_wifi_clear_default_wifi_driver_and_handlers(void *);
void esp_wifi_destroy_if_driver(wifi_netif_driver_t);
wifi_netif_driver_t esp_wifi_create_if_driver(wifi_interface_t);

typedef const char *esp_event_base_t;
typedef void (*esp_event_handler_t)(void *, esp_event_base_t, int32_t, void *);
typedef void (*shutdown_handler_t)(void);
#define WIFI_EVENT "WIFI_EVENT"
#define IP_EVENT "IP_EVENT"
enum { WIFI_EVENT_STA_START, WIFI_EVENT_STA_STOP, WIFI_EVENT_STA_CONNECTED,
       WIFI_EVENT_STA_DISCONNECTED, WIFI_EVENT_AP_START, WIFI_EVENT_AP_STOP,
       IP_EVENT_STA_GOT_IP };
esp_err_t esp_event_handler_register(esp_event_base_t, int32_t, esp_event_handler_t, void *);
esp_err_t esp_event_handler_unregister(esp_event_base_t, int32_t, esp_event_handler_t);
esp_err_t esp_register_shutdown_handler(shutdown_handler_t);
esp_err_t esp_unregister_shutdown_handler(shutdown_handler_t);
esp_err_t esp_wifi_stop(void);
esp_err_t esp_wifi_internal_reg_rxcb(wifi_interface_t, void *);
