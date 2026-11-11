#include "network_service.h"

#include "esp_eth.h"
#include "esp_eth_netif_glue.h"
#include "esp_event.h"
#include "esp_netif.h"
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
#include <stdio.h>

#define GOT_IPV4 BIT0

static EventGroupHandle_t s_events;
static esp_netif_t *s_eth_netif;

static void on_ipv4(void *arg, esp_event_base_t base, int32_t id, void *data) {
    (void)arg;
    (void)base;
    (void)id;
    const ip_event_got_ip_t *event = data;
    if (event->esp_netif == s_eth_netif && event->ip_info.ip.addr) {
        xEventGroupSetBits(s_events, GOT_IPV4);
    }
}

// The real app calls this once on its production startup task. OpenETH and
// lwIP supply the IP event; the radio, WebUI, TFT and audio paths follow it.
esp_err_t __wrap_network_service_start(native_state_t *state) {
    ESP_ERROR_CHECK(network_service_storage_init());
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());

    s_events = xEventGroupCreate();
    ESP_ERROR_CHECK(s_events ? ESP_OK : ESP_ERR_NO_MEM);
    const esp_netif_config_t netif_config = ESP_NETIF_DEFAULT_ETH();
    s_eth_netif = esp_netif_new(&netif_config);
    ESP_ERROR_CHECK(s_eth_netif ? ESP_OK : ESP_ERR_NO_MEM);

    eth_mac_config_t mac_config = ETH_MAC_DEFAULT_CONFIG();
    eth_phy_config_t phy_config = ETH_PHY_DEFAULT_CONFIG();
    phy_config.phy_addr = 1;
    phy_config.reset_gpio_num = -1;
    esp_eth_mac_t *mac = esp_eth_mac_new_openeth(&mac_config);
    esp_eth_phy_t *phy = esp_eth_phy_new_generic(&phy_config);
    ESP_ERROR_CHECK(mac && phy ? ESP_OK : ESP_ERR_NO_MEM);
    const esp_eth_config_t driver_config = ETH_DEFAULT_CONFIG(mac, phy);
    esp_eth_handle_t driver = NULL;
    ESP_ERROR_CHECK(esp_eth_driver_install(&driver_config, &driver));
    esp_eth_netif_glue_handle_t glue = esp_eth_new_netif_glue(driver);
    ESP_ERROR_CHECK(glue ? ESP_OK : ESP_ERR_NO_MEM);
    ESP_ERROR_CHECK(esp_netif_attach(s_eth_netif, glue));
    ESP_ERROR_CHECK(esp_event_handler_register(IP_EVENT, IP_EVENT_ETH_GOT_IP, on_ipv4, NULL));
    ESP_ERROR_CHECK(esp_eth_start(driver));

    EventBits_t events = xEventGroupWaitBits(s_events, GOT_IPV4, pdFALSE, pdTRUE,
                                           pdMS_TO_TICKS(30000));
    ESP_ERROR_CHECK((events & GOT_IPV4) ? ESP_OK : ESP_ERR_TIMEOUT);
    esp_netif_ip_info_t ipv4;
    ESP_ERROR_CHECK(esp_netif_get_ip_info(s_eth_netif, &ipv4));
    ESP_ERROR_CHECK(ipv4.ip.addr ? ESP_OK : ESP_ERR_INVALID_STATE);
    native_state_set_network(state, NATIVE_NETWORK_CLIENT, ipv4.ip.addr);
    puts("CYD_OPENETH_READY");
    return ESP_OK;
}
