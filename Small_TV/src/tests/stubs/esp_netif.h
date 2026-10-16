#pragma once
#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>
#include "esp_err.h"
typedef struct
{
    uint32_t addr;
} esp_ip4_addr_t;
typedef struct
{
    esp_ip4_addr_t ip, gw, netmask;
} esp_netif_ip_info_t;
typedef struct
{
    int identity;
} esp_netif_t;
typedef struct
{
    esp_netif_t *esp_netif;
    esp_netif_ip_info_t ip_info;
    bool ip_changed;
} ip_event_got_ip_t;
typedef struct
{
    struct
    {
        int type;
        union
        {
            esp_ip4_addr_t ip4;
        } u_addr;
    } ip;
} esp_netif_dns_info_t;
enum
{
    ESP_IPADDR_TYPE_V4,
    ESP_NETIF_DNS_MAIN,
    ESP_NETIF_OP_SET,
    ESP_NETIF_DOMAIN_NAME_SERVER
};
#define IPSTR "%u.%u.%u.%u"
#define IP2STR(p)                                                                                  \
    (unsigned)((p)->addr & 255), (unsigned)(((p)->addr >> 8) & 255),                               \
        (unsigned)(((p)->addr >> 16) & 255), (unsigned)((p)->addr >> 24)
esp_err_t esp_netif_init(void);
esp_netif_t *esp_netif_create_default_wifi_sta(void);
esp_netif_t *esp_netif_create_default_wifi_ap(void);
void esp_netif_set_ip4_addr(esp_ip4_addr_t *ip, unsigned a, unsigned b, unsigned c, unsigned d);
esp_err_t esp_netif_dhcps_stop(esp_netif_t *netif);
esp_err_t esp_netif_dhcps_start(esp_netif_t *netif);
esp_err_t esp_netif_set_ip_info(esp_netif_t *netif, const esp_netif_ip_info_t *ip);
esp_err_t esp_netif_get_ip_info(esp_netif_t *netif, esp_netif_ip_info_t *ip);
esp_err_t esp_netif_set_dns_info(esp_netif_t *netif, int type, const esp_netif_dns_info_t *dns);
esp_err_t esp_netif_dhcps_option(esp_netif_t *netif, int operation, int option, void *data,
                                 size_t size);
