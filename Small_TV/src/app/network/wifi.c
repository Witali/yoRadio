#include "network.h"
#include "settings.h"
#include <stdatomic.h>
#include <stdio.h>
#include <string.h>
#include "esp_event.h"
#include "esp_netif.h"
#include "esp_system.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static esp_netif_t *station_netif, *ap_netif;
static atomic_bool connected, ap_active, scanning, restarting, station_failed;
static atomic_uint_least32_t last_station_address;
static bool station_configured;
static unsigned station_retries;

static void wifi_event(void *context, esp_event_base_t base, int32_t id, void *data)
{
    /* Track station connectivity and handle the configured reconnect policy.
     * FIXED_RECONSTRUCTION: 0x4200c602 retains its last GOT_IP address across
     * station retries. Cache it atomically instead of inventing the AP address
     * whenever connectivity temporarily drops. */

    (void)context;
    if (base == IP_EVENT && id == IP_EVENT_STA_GOT_IP)
    {
        const ip_event_got_ip_t *event = data;
        if (!event)
            return;
        /* The event owns the assigned lease; a later netif query may already
         * reflect a following disconnect or address change. */
        atomic_store(&last_station_address, event->ip_info.ip.addr);
        atomic_store(&connected, true);
        station_retries = 0;
    }
    else if (base == WIFI_EVENT && id == WIFI_EVENT_STA_DISCONNECTED)
    {
        atomic_store(&connected, false);
        /* The factory retries four times, saves setup mode and reboots. */
        if (station_configured && !atomic_load(&scanning) && station_retries < 4)
        {
            ++station_retries;
            esp_wifi_connect();
        }
        else if (station_configured && !atomic_load(&scanning))
            atomic_store(&station_failed, true);
    }
    else if (base == WIFI_EVENT && id == WIFI_EVENT_STA_START && station_configured)
        esp_wifi_connect();
}

static esp_err_t start_access_point(void)
{
    /* Keep the setup AP and an idle station interface so the setup page can scan networks. */

    if (atomic_load(&ap_active))
        return ESP_OK;
    /* ESP-IDF cannot scan in WIFI_MODE_AP. STA_START does not connect while
     * station_configured is false; the station exists only for explicit scans. */
    esp_err_t result = esp_wifi_set_mode(WIFI_MODE_APSTA);
    if (result == ESP_OK)
        atomic_store(&ap_active, true);
    return result;
}

static void fallback_task(void *unused)
{
    /* Persist setup mode and restart after the factory station retries fail. */

    (void)unused;
    unsigned offline_seconds = 0;
    for (;;)
    {
        vTaskDelay(pdMS_TO_TICKS(1000));
        if (network_connected())
            offline_seconds = 0;
        else if ((++offline_seconds >= 18 || atomic_load(&station_failed)) && !network_ap_active())
        {
            /* Keep flash writes out of the Wi-Fi event callback. The saved mode
             * makes the next boot go directly to the setup screen, as in stock. */
            tv_settings_t s;
            settings_snapshot(&s);
            s.wifi_mode = 2;
            if (settings_replace(&s) == ESP_OK)
                network_restart_later();
        }
    }
}

esp_err_t network_init(void)
{
    /* Configure station/AP interfaces, factory address, DHCP and Wi-Fi event handlers. */

    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    station_netif = esp_netif_create_default_wifi_sta();
    ap_netif = esp_netif_create_default_wifi_ap();
    if (!station_netif || !ap_netif)
        return ESP_ERR_NO_MEM;
    esp_netif_ip_info_t ip = {0};
    esp_netif_set_ip4_addr(&ip.ip, 192, 168, 43, 1);
    esp_netif_set_ip4_addr(&ip.gw, 192, 168, 43, 1);
    esp_netif_set_ip4_addr(&ip.netmask, 255, 255, 255, 0);
    ESP_ERROR_CHECK(esp_netif_dhcps_stop(ap_netif));
    ESP_ERROR_CHECK(esp_netif_set_ip_info(ap_netif, &ip));
    esp_netif_dns_info_t dns = {.ip.type = ESP_IPADDR_TYPE_V4};
    dns.ip.u_addr.ip4 = ip.ip;
    ESP_ERROR_CHECK(esp_netif_set_dns_info(ap_netif, ESP_NETIF_DNS_MAIN, &dns));
    uint8_t offer_dns = 1;
    ESP_ERROR_CHECK(esp_netif_dhcps_option(ap_netif, ESP_NETIF_OP_SET, ESP_NETIF_DOMAIN_NAME_SERVER,
                                           &offer_dns, sizeof(offer_dns)));
    ESP_ERROR_CHECK(esp_netif_dhcps_start(ap_netif));
    wifi_init_config_t config = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&config));
    ESP_ERROR_CHECK(esp_wifi_set_storage(WIFI_STORAGE_RAM));
    ESP_ERROR_CHECK(esp_event_handler_register(WIFI_EVENT, ESP_EVENT_ANY_ID, wifi_event, NULL));
    ESP_ERROR_CHECK(esp_event_handler_register(IP_EVENT, IP_EVENT_STA_GOT_IP, wifi_event, NULL));
    tv_settings_t s;
    settings_snapshot(&s);
    station_configured = s.wifi_mode == 1 && s.ssid[0];
    wifi_config_t station = {0};
    memcpy(station.sta.ssid, s.ssid, strlen(s.ssid));
    memcpy(station.sta.password, s.password, strlen(s.password));
    station.sta.threshold.authmode = s.password[0] ? WIFI_AUTH_WPA2_PSK : WIFI_AUTH_OPEN;
    wifi_config_t ap = {.ap = {.ssid = "Small_TV",
                               .ssid_len = 8,
                               .channel = 1,
                               .max_connection = 3,
                               .authmode = WIFI_AUTH_OPEN}};
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_APSTA));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_AP, &ap));
    if (station_configured)
        ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &station));
    if (station_configured)
        ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    else
        ESP_ERROR_CHECK(start_access_point());
    ESP_ERROR_CHECK(esp_wifi_start());
    atomic_store(&ap_active, !station_configured);
    dns_start();
    return xTaskCreate(fallback_task, "wifi_fallback", 2048, NULL, 2, NULL) == pdPASS
               ? ESP_OK
               : ESP_ERR_NO_MEM;
}

bool network_connected(void)
{
    /* Return the atomic station-address readiness flag. */
    return atomic_load(&connected);
}
bool network_ap_active(void)
{
    /* Return whether the setup access point is enabled. */
    return atomic_load(&ap_active);
}

void network_address(char *out, size_t size)
{
    /* Format the last station address or the explicitly active setup address.
     * FIXED_RECONSTRUCTION: the original 0x3fcb7b84 display string is updated
     * by GOT_IP, not cleared by DISCONNECTED in 0x4200c602. Retain it while
     * clocks keep running offline; only a setup AP selects its fixed address. */

    esp_netif_ip_info_t ip = {0};
    ip.ip.addr = (uint32_t)atomic_load(&last_station_address);
    if (!network_ap_active() && ip.ip.addr)
        snprintf(out, size, IPSTR, IP2STR(&ip.ip));
    else
        snprintf(out, size, "192.168.43.1");
}

esp_err_t network_scan(wifi_ap_record_t *records, uint16_t *count)
{
    /* Perform a real scan while preventing reconnect attempts from racing it. */

    atomic_store(&scanning, true);
    wifi_scan_config_t config = {.show_hidden = false};
    esp_err_t result = esp_wifi_scan_start(&config, true);
    if (result == ESP_OK)
        result = esp_wifi_scan_get_ap_records(count, records);
    else
        esp_wifi_clear_ap_list();
    atomic_store(&scanning, false);
    if (station_configured && !network_connected())
        esp_wifi_connect();
    return result;
}

static void restart_task(void *unused)
{
    /* Flush settings and restart after the HTTP response grace period. */

    (void)unused;
    vTaskDelay(pdMS_TO_TICKS(800));
    if (settings_flush() == ESP_OK)
        esp_restart();
    atomic_store(&restarting, false);
    vTaskDelete(NULL);
}

void network_restart_later(void)
{
    /* Schedule at most one deferred restart request. */

    if (!atomic_exchange(&restarting, true) &&
        xTaskCreate(restart_task, "restart", 2048, NULL, 3, NULL) != pdPASS)
        atomic_store(&restarting, false);
}
