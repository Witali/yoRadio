/* Execute production workers/drivers. Only ESP-IDF I/O and scheduling are adapted.
 * Each named case runs in a fresh process; no production static state is reset by tests.
 * longjmp stops an infinite worker at its next blocking call, never in a mutex/HTTP operation. */
#include <assert.h>
#include <setjmp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "display.h"
#include "factory_ui.h"
#include "media.h"
#include "network.h"
#include "services.h"
#include "settings.h"
#include "esp_event.h"
#include "esp_netif.h"
#include "esp_netif_sntp.h"
#include "esp_http_client.h"
#include "esp_system.h"
#include "driver/gpio.h"
#include "driver/spi_master.h"
#include "driver/ledc.h"
#include "driver/gptimer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"

static unsigned checks;
#define CHECK(value)                                                                               \
    do                                                                                             \
    {                                                                                              \
        ++checks;                                                                                  \
        if (!(value))                                                                              \
        {                                                                                          \
            fprintf(stderr, "FAIL %s:%d: %s\n", __FILE__, __LINE__, #value);                       \
            exit(1);                                                                               \
        }                                                                                          \
    } while (0)
static tv_settings_t preferences;
static esp_err_t flush_result = ESP_OK, task_result = pdPASS;
static unsigned flushes, restarts, connects, dns_started, delays, notifications;
static void (*blocking_hook)(void);
static jmp_buf blocked;
typedef struct
{
    void (*entry)(void *);
    const char *name;
    void *argument;
} captured_task_t;
static captured_task_t tasks[16];
static unsigned task_count;
static uint32_t preferences_generation = 1;
static uint32_t theme_selection_generation;
static bool uploading, in_alarm;
static time_t fake_time = 1791885600;
static struct tm fake_local = {
    .tm_year = 126, .tm_mon = 9, .tm_mday = 13, .tm_wday = 2, .tm_hour = 12};

void settings_snapshot(tv_settings_t *out)
{
    *out = preferences;
}
void settings_snapshot_with_revisions(tv_settings_t *out, uint32_t *configuration_revision,
                                      uint32_t *theme_selection_revision)
{
    /* Model one coherent settings/UI-command input to the production task. */
    *out = preferences;
    if (configuration_revision) *configuration_revision = preferences_generation;
    if (theme_selection_revision) *theme_selection_revision = theme_selection_generation;
}
esp_err_t settings_select_theme(unsigned theme)
{
    /* Keep explicit commands separate from stored configuration changes. */
    if (theme > 3) return ESP_ERR_INVALID_ARG;
    if (preferences.theme != theme) {preferences.theme = (uint8_t)theme; ++preferences_generation;}
    ++theme_selection_generation;
    return ESP_OK;
}
esp_err_t settings_replace(const tv_settings_t *value)
{
    preferences = *value;
    ++preferences_generation;
    return ESP_OK;
}
uint32_t settings_generation(void)
{
    return preferences_generation;
}
bool media_upload_active(void)
{
    return uploading;
}
time_t test_time(time_t *out)
{
    if (out)
        *out = fake_time;
    return fake_time;
}
struct tm *test_localtime_r(const time_t *now, struct tm *local)
{
    assert(*now == fake_time);
    *local = fake_local;
    return local;
}
struct tm *test_gmtime_r(const time_t *now, struct tm *local)
{
    /* Run the host CRT's real UTC calendar conversion; never substitute timezone logic. */
    return _gmtime64_s(local, now) ? NULL : local;
}
esp_err_t settings_flush(void)
{
    ++flushes;
    return flush_result;
}
SemaphoreHandle_t xSemaphoreCreateMutex(void)
{
    return (void *)1;
}
int xSemaphoreTake(SemaphoreHandle_t mutex, unsigned ticks)
{
    assert(mutex && ticks == portMAX_DELAY);
    return 1;
}
int xSemaphoreGive(SemaphoreHandle_t mutex)
{
    assert(mutex);
    return 1;
}
int xTaskCreate(void (*entry)(void *), const char *name, unsigned stack, void *argument,
                unsigned priority, void *handle)
{
    /* Capture real worker entry points instead of launching nondeterministic host threads. */
    (void)stack;
    (void)priority;
    if (task_result != pdPASS)
        return task_result;
    assert(task_count < 16);
    tasks[task_count] = (captured_task_t){entry, name, argument};
    if (handle)
        *(TaskHandle_t *)handle = &tasks[task_count];
    ++task_count;
    return pdPASS;
}
void vTaskDelay(unsigned ticks)
{
    delays += ticks;
    if (blocking_hook)
        blocking_hook();
}
void vTaskDelete(TaskHandle_t task)
{
    assert(task == NULL);
    longjmp(blocked, 1);
}
void xTaskNotifyGive(TaskHandle_t task)
{
    assert(task != NULL);
    ++notifications;
}
uint32_t ulTaskNotifyTake(int clear, unsigned ticks)
{
    /* Let the scenario inspect the completed request before delivering the next notification. */
    assert(clear == pdTRUE && ticks == portMAX_DELAY);
    assert(blocking_hook);
    blocking_hook();
    assert(notifications);
    unsigned result = notifications;
    notifications = 0;
    return result;
}
static void run_task(const char *name, void (*hook)(void))
{
    /* Run one captured production task until its scenario reaches a blocking boundary. */
    for (unsigned i = 0; i < task_count; ++i)
        if (!strcmp(tasks[i].name, name))
        {
            blocking_hook = hook;
            if (!setjmp(blocked))
                tasks[i].entry(tasks[i].argument);
            blocking_hook = NULL;
            return;
        }
    CHECK(false);
}

const char wifi_event_base[] = "wifi", ip_event_base[] = "ip";
static void (*event_callback)(void *, esp_event_base_t, int32_t, void *);
static esp_netif_t sta = {1}, ap = {2};
static bool allocation_failure, scan_disconnect;
static esp_err_t scan_result = ESP_OK;
static int wifi_mode;
static wifi_config_t sta_config, ap_config;
static esp_netif_ip_info_t ap_ip;
static unsigned dhcp_phase, scan_clears;
static unsigned station_netifs_created, ap_netifs_created, station_configs_set, ap_configs_set;
esp_err_t esp_event_loop_create_default(void)
{
    return ESP_OK;
}
esp_err_t esp_event_handler_register(esp_event_base_t base, int32_t id,
                                     void (*handler)(void *, esp_event_base_t, int32_t, void *),
                                     void *context)
{
    (void)id;
    assert(context == NULL && (base == WIFI_EVENT || base == IP_EVENT));
    event_callback = handler;
    return ESP_OK;
}
esp_err_t esp_netif_init(void)
{
    return ESP_OK;
}
esp_netif_t *esp_netif_create_default_wifi_sta(void)
{
    ++station_netifs_created;
    return allocation_failure ? NULL : &sta;
}
esp_netif_t *esp_netif_create_default_wifi_ap(void)
{
    ++ap_netifs_created;
    return allocation_failure ? NULL : &ap;
}
void esp_netif_set_ip4_addr(esp_ip4_addr_t *ip, unsigned a, unsigned b, unsigned c, unsigned d)
{
    ip->addr = a | (b << 8) | (c << 16) | (d << 24);
}
esp_err_t esp_netif_dhcps_stop(esp_netif_t *netif)
{
    assert(netif == &ap);
    dhcp_phase = 1;
    return ESP_OK;
}
esp_err_t esp_netif_set_ip_info(esp_netif_t *netif, const esp_netif_ip_info_t *ip)
{
    assert(netif == &ap && dhcp_phase == 1);
    ap_ip = *ip;
    dhcp_phase = 2;
    return ESP_OK;
}
esp_err_t esp_netif_set_dns_info(esp_netif_t *netif, int type, const esp_netif_dns_info_t *dns)
{
    assert(netif == &ap && type == ESP_NETIF_DNS_MAIN && dns->ip.u_addr.ip4.addr == ap_ip.ip.addr &&
           dhcp_phase == 2);
    dhcp_phase = 3;
    return ESP_OK;
}
esp_err_t esp_netif_dhcps_option(esp_netif_t *netif, int operation, int option, void *data,
                                 size_t size)
{
    assert(netif == &ap && operation == ESP_NETIF_OP_SET &&
           option == ESP_NETIF_DOMAIN_NAME_SERVER && size == 1 && *(uint8_t *)data == 1 &&
           dhcp_phase == 3);
    dhcp_phase = 4;
    return ESP_OK;
}
esp_err_t esp_netif_dhcps_start(esp_netif_t *netif)
{
    assert(netif == &ap && dhcp_phase == 4);
    dhcp_phase = 5;
    return ESP_OK;
}
esp_err_t esp_netif_get_ip_info(esp_netif_t *netif, esp_netif_ip_info_t *ip)
{
    assert(netif == &sta);
    esp_netif_set_ip4_addr(&ip->ip, 10, 0, 2, 15);
    return ESP_OK;
}
esp_err_t esp_wifi_init(const wifi_init_config_t *config)
{
    assert(config);
    return ESP_OK;
}
esp_err_t esp_wifi_set_storage(int storage)
{
    assert(storage == WIFI_STORAGE_RAM);
    return ESP_OK;
}
esp_err_t esp_wifi_set_mode(int mode)
{
    wifi_mode = mode;
    return ESP_OK;
}
esp_err_t esp_wifi_set_config(int interface, const wifi_config_t *config)
{
    if (interface == WIFI_IF_STA)
    {
        ++station_configs_set;
        sta_config = *config;
    }
    else
    {
        assert(interface == WIFI_IF_AP);
        ++ap_configs_set;
        ap_config = *config;
    }
    return ESP_OK;
}
esp_err_t esp_wifi_start(void)
{
    return ESP_OK;
}
esp_err_t esp_wifi_connect(void)
{
    ++connects;
    return ESP_OK;
}
esp_err_t esp_wifi_scan_start(const wifi_scan_config_t *config, bool block)
{
    assert(block && !config->show_hidden);
    if (scan_disconnect)
        event_callback(NULL, WIFI_EVENT, WIFI_EVENT_STA_DISCONNECTED, NULL);
    return scan_result;
}
esp_err_t esp_wifi_scan_get_ap_records(uint16_t *count, wifi_ap_record_t *records)
{
    assert(*count);
    *count = 1;
    strcpy((char *)records[0].ssid, "synthetic");
    records[0].rssi = -35;
    return ESP_OK;
}
esp_err_t esp_wifi_clear_ap_list(void)
{
    ++scan_clears;
    return ESP_OK;
}
void esp_restart(void)
{
    ++restarts;
}
void dns_start(void)
{
    ++dns_started;
}
static void got_ip_at(unsigned last_octet)
{
    /* Deliver the SDK event snapshot, independently of a later netif query. */
    assert(event_callback);
    ip_event_got_ip_t event={.esp_netif=&sta,.ip_changed=true};
    esp_netif_set_ip4_addr(&event.ip_info.ip,10,0,2,last_octet);
    event_callback(NULL, IP_EVENT, IP_EVENT_STA_GOT_IP, &event);
}
static void got_ip(void)
{
    /* Use the ordinary synthetic station lease for other scenarios. */
    got_ip_at(15);
}
static void disconnected(void)
{
    assert(event_callback);
    event_callback(NULL, WIFI_EVENT, WIFI_EVENT_STA_DISCONNECTED, NULL);
}
static void station_start(void)
{
    /* Initialize real station logic with wholly synthetic credentials. */
    preferences.wifi_mode = 1;
    strcpy(preferences.ssid, "fixture");
    strcpy(preferences.password, "12345678");
    CHECK(network_init() == ESP_OK);
    event_callback(NULL, WIFI_EVENT, WIFI_EVENT_STA_START, NULL);
}
static unsigned steps, stop_after;
static void stop_at_delay(void)
{
    if (++steps == stop_after)
        longjmp(blocked, 1);
}

static void test_wifi_setup(void)
{
    /* Mode 2 must keep the setup AP even when credentials were saved earlier. */
    preferences.wifi_mode = 2;
    strcpy(preferences.ssid, "saved-but-offline");
    CHECK(network_init() == ESP_OK);
    CHECK(station_netifs_created == 0 && ap_netifs_created == 1);
    CHECK(station_configs_set == 0 && ap_configs_set == 1);
    CHECK(network_ap_active() && !network_connected() && wifi_mode == WIFI_MODE_APSTA);
    CHECK(connects == 0 && !sta_config.sta.ssid[0]);
    CHECK(ap_config.ap.authmode == WIFI_AUTH_OPEN && ap_config.ap.channel == 1 &&
          ap_config.ap.max_connection == 3);
    CHECK(ap_config.ap.ssid_len == 8 && !memcmp(ap_config.ap.ssid, "Small_TV", 8));
    CHECK(ap_ip.ip.addr == 0x012ba8c0 && ap_ip.gw.addr == 0x012ba8c0 &&
          ap_ip.netmask.addr == 0x00ffffff && dhcp_phase == 5);
    char address[20];
    network_address(address, sizeof(address));
    CHECK(!strcmp(address, "192.168.43.1") && dns_started == 1);
    /* The real factory AP path has no STA TCP/IP netif. Scan still uses the
     * driver's idle STA role; its events must not start station retries. */
    event_callback(NULL, WIFI_EVENT, WIFI_EVENT_STA_START, NULL);
    scan_disconnect = true;
    wifi_ap_record_t records[2];
    uint16_t count = 2;
    CHECK(network_scan(records, &count) == ESP_OK && count == 1);
    CHECK(!strcmp((char *)records[0].ssid, "synthetic") && records[0].rssi == -35);
    CHECK(task_count == 0 && restarts == 0 && connects == 0 && preferences.wifi_mode == 2);
}
static void test_wifi_reconnect(void)
{
    /* Four station retries, readiness after DHCP, retry reset and scan-event suppression. */
    station_start();
    CHECK(station_netifs_created == 1 && ap_netifs_created == 0);
    CHECK(station_configs_set == 1 && ap_configs_set == 0 && dns_started == 0 && dhcp_phase == 0);
    CHECK(wifi_mode == WIFI_MODE_STA && !network_ap_active() && connects == 1);
    CHECK(!memcmp(sta_config.sta.ssid, "fixture", 7) &&
          sta_config.sta.threshold.authmode == WIFI_AUTH_WPA2_PSK);
    got_ip();
    CHECK(network_connected());
    char address[20];
    network_address(address, sizeof(address));
    CHECK(!strcmp(address, "10.0.2.15"));
    for (unsigned i = 0; i < 4; ++i)
    {
        disconnected();
        CHECK(!network_connected() && connects == i + 2);
        network_address(address,sizeof(address));
        CHECK(!strcmp(address,"10.0.2.15"));
    }
    disconnected();
    CHECK(connects == 5);
    got_ip();
    disconnected();
    CHECK(connects == 6);
    wifi_ap_record_t records[2];
    uint16_t count = 2;
    scan_disconnect = true;
    unsigned before = connects;
    CHECK(network_scan(records, &count) == ESP_OK);
    CHECK(count == 1 && !strcmp((char *)records[0].ssid, "synthetic") && records[0].rssi == -35 &&
          connects == before + 1);
    scan_result = ESP_FAIL;
    count = 2;
    before = connects;
    CHECK(network_scan(records, &count) == ESP_FAIL);
    CHECK(scan_clears == 1 && connects == before + 1);
    got_ip_at(21);disconnected();network_address(address,sizeof(address));
    CHECK(!strcmp(address,"10.0.2.21"));
}
static void test_wifi_open(void)
{
    /* Open station credentials must select open authentication and no password. */
    preferences.wifi_mode = 1;
    strcpy(preferences.ssid, "open-fixture");
    preferences.password[0] = 0;
    CHECK(network_init() == ESP_OK);
    CHECK(sta_config.sta.threshold.authmode == WIFI_AUTH_OPEN && !sta_config.sta.password[0]);
    CHECK(station_netifs_created == 1 && ap_netifs_created == 0 && dns_started == 0);
}
static void test_wifi_fallback(void)
{
    /* Pending DHCP is not failed Wi-Fi: retain credentials while the SDK connects. */
    station_start();
    stop_after = 61;
    run_task("wifi_fallback", stop_at_delay);
    CHECK(preferences.wifi_mode == 1 && task_count == 1);
    CHECK(!network_connected() && !restarts && !flushes);
    got_ip();
    CHECK(network_connected() && preferences.wifi_mode == 1);
}
static void test_wifi_failed_retries(void)
{
    /* Failed retries trigger setup fallback without waiting the safety timeout. */
    station_start();
    for (unsigned i = 0; i < 5; ++i)
        disconnected();
    stop_after = 2;
    run_task("wifi_fallback", stop_at_delay);
    CHECK(preferences.wifi_mode == 2 && task_count == 2);
    run_task("restart", NULL);
    CHECK(restarts == 1);
}
static void test_wifi_failure_recovered(void)
{
    /* A fresh lease retires an old failure before the next reconnect attempt. */
    station_start();
    for (unsigned i = 0; i < 5; ++i)
        disconnected();
    got_ip();
    disconnected();
    stop_after = 2;
    run_task("wifi_fallback", stop_at_delay);
    CHECK(preferences.wifi_mode == 1 && task_count == 1);
    CHECK(!restarts && !flushes);
}
static void test_restart_failure(void)
{
    /* Coalesce restart requests; never restart after a failed persistence write. */
    network_restart_later();
    network_restart_later();
    CHECK(task_count == 1);
    flush_result = ESP_FAIL;
    run_task("restart", NULL);
    CHECK(restarts == 0 && flushes == 1 && delays == 800);
    flush_result = ESP_OK;
    network_restart_later();
    CHECK(task_count == 2);
    run_task("restart", NULL);
    CHECK(restarts == 1 && flushes == 2 && delays == 1600);
}
static void test_wifi_allocation_failure(void)
{
    /* Setup must fail on its own AP allocation, without allocating STA first. */
    allocation_failure = true;
    CHECK(network_init() == ESP_ERR_NO_MEM && task_count == 0);
    CHECK(station_netifs_created == 0 && ap_netifs_created == 1 && dns_started == 0);
}
static void test_wifi_station_allocation_failure(void)
{
    /* Station allocation failure must not initialize an unrelated AP or DNS. */
    preferences.wifi_mode = 1;
    strcpy(preferences.ssid, "fixture");
    allocation_failure = true;
    CHECK(network_init() == ESP_ERR_NO_MEM && task_count == 0);
    CHECK(station_netifs_created == 1 && ap_netifs_created == 0 && dns_started == 0);
}
static void test_wifi_task_failure(void)
{
    /* The retry supervisor belongs to the station role. */
    preferences.wifi_mode = 1;
    strcpy(preferences.ssid, "fixture");
    task_result = 0;
    CHECK(network_init() == ESP_ERR_NO_MEM);
}

static esp_http_client_config_t http_config;
static const char weather_body[] =
    "{\"main\":{\"temp\":293.99,\"humidity\":73},\"wind\":{\"speed\":3.7,\"deg\":90},\"weather\":[{\"icon\":\"02d\",\"main\":\"Clouds\",\"description\":\"clear\"}]}";
static const char *http_body = weather_body;
static size_t http_length = sizeof(weather_body) - 1;
static int http_status = 200;
static esp_err_t http_result = ESP_OK;
static bool http_init_failure, http_stale, http_queue;
static unsigned http_calls, http_cleanups, weather_step;
static char fetched_url[512];
esp_http_client_handle_t esp_http_client_init(const esp_http_client_config_t *config)
{
    /* Capture transport configuration, while running the real bounded event callback. */
    http_config = *config;
    strcpy(fetched_url, config->url);
    return http_init_failure ? NULL : (void *)1;
}
esp_err_t esp_http_client_perform(esp_http_client_handle_t client)
{
    assert(client);
    ++http_calls;
    CHECK(weather_request_active());
    if (weather_step == 1)
        CHECK(!strcmp(
            fetched_url,
            "http://api.openweathermap.org/data/2.5/weather?q=New%20York%2F%E6%B5%8B%E8%AF%95,US&appid=key%26%3Dx"));
    CHECK(http_config.timeout_ms == 10000 && http_config.disable_auto_redirect &&
          http_config.buffer_size == 1024);
    for (size_t i = 0; i < http_length; i += 17)
    {
        size_t bytes = http_length - i;
        if (bytes > 17)
            bytes = 17;
        esp_http_client_event_t event = {HTTP_EVENT_ON_DATA, (int)bytes, (void *)(http_body + i),
                                         http_config.user_data};
        esp_err_t result = http_config.event_handler(&event);
        if (result != ESP_OK)
            return result;
    }
    if (http_stale)
    {
        strcpy(preferences.city, "Budapest");
        strcpy(preferences.country, "HU");
    }
    if (http_queue)
    {
        weather_request_update();
        CHECK(weather_request_active());
    }
    return http_result;
}
int esp_http_client_get_status_code(esp_http_client_handle_t client)
{
    assert(client);
    return http_status;
}
void esp_http_client_cleanup(esp_http_client_handle_t client)
{
    assert(client);
    ++http_cleanups;
}
static void weather_scenario(void)
{
    /* Inspect the previous iteration and then arrange one deterministic request. */
    weather_snapshot_t snapshot;
    weather_snapshot(&snapshot);
    if (weather_step == 0)
    {
        CHECK(!snapshot.valid && !weather_request_active());
    }
    else if (weather_step <= 7)
    {
        CHECK(snapshot.valid && snapshot.temperature_c == 20 && snapshot.humidity == 73 &&
              snapshot.generation == 2);
    }
    else if (weather_step <= 10)
    {
        CHECK(snapshot.valid && !strcmp(snapshot.city, "Budapest") &&
              snapshot.generation == weather_step - 4);
    }
    else
    {
        CHECK(!snapshot.valid && snapshot.generation == (weather_step == 13 ? 8 : 7));
    }
    CHECK(weather_request_active() == (weather_step == 9));
    if (weather_step == 13)
        longjmp(blocked, 1);
    http_init_failure = http_stale = http_queue = false;
    http_result = ESP_OK;
    http_status = 200;
    http_body = weather_body;
    http_length = sizeof(weather_body) - 1;
    if (weather_step == 1)
        http_status = 401;
    if (weather_step == 2)
        http_result = ESP_FAIL;
    if (weather_step == 3)
    {
        http_body = "{}";
        http_length = 2;
    }
    static char oversized[8193];
    if (weather_step == 4)
    {
        memset(oversized, ' ', sizeof(oversized));
        http_body = oversized;
        http_length = sizeof(oversized);
    }
    if (weather_step == 5)
        http_init_failure = true;
    if (weather_step == 6)
        http_stale = true;
    if (weather_step == 8)
        http_queue = true;
    if (weather_step == 10)
        preferences.weather_key[0] = 0;
    if (weather_step == 11)
        disconnected();
    if (weather_step == 12)
    {
        strcpy(preferences.weather_key, "fixture-key");
    }
    weather_request_update();
    CHECK(weather_request_active());
    ++weather_step;
}
static void test_weather_worker(void)
{
    /* Cover success, chunked bodies, HTTP/parse/overflow/init failures, stale/queued requests and
     * disable/offline. */
    station_start();
    got_ip();
    strcpy(preferences.city, "New York/\xe6\xb5\x8b\xe8\xaf\x95");
    strcpy(preferences.country, "US");
    strcpy(preferences.weather_key, "key&=x");
    weather_start();
    run_task("weather_http", weather_scenario);
    CHECK(http_calls == 9 && http_cleanups == 9 && !weather_request_active());
    CHECK(strstr(fetched_url, "appid=") != NULL);
}

static unsigned sntp_inits, sntp_deinits, timezone_updates, time_step;
static esp_err_t sntp_result = ESP_OK;
static char timezone[96], servers[3][65];
static esp_sntp_time_cb_t sntp_callback;
int test_setenv(const char *name, const char *value, int overwrite)
{
    assert(!strcmp(name, "TZ") && overwrite == 1);
    strcpy(timezone, value);
    return 0;
}
void test_tzset(void)
{
    ++timezone_updates;
}
esp_err_t esp_netif_sntp_init(const esp_sntp_config_t *config)
{
    assert(config->num_servers == 3 && !config->wait_for_sync);
    CHECK(config->sync_cb != NULL);
    sntp_callback = config->sync_cb;
    for (unsigned i = 0; i < 3; ++i)
        strcpy(servers[i], config->servers[i]);
    ++sntp_inits;
    return sntp_result;
}
void esp_netif_sntp_deinit(void)
{
    ++sntp_deinits;
}
static void time_scenario(void)
{
    /* Inject connectivity/location/server changes after each real monitor iteration. */
    ++time_step;
    if (time_step == 1)
    {
        CHECK(!services_time_synced());
        CHECK(!strcmp(timezone, "UTC-1:00:00") && sntp_inits == 0);
        got_ip();
        preferences.ntp[0] = 0;
    }
    if (time_step == 2)
    {
        CHECK(!services_time_synced()); /* Initializing SNTP alone is not synchronization. */
        struct timeval event = {.tv_sec=fake_time};
        sntp_callback(&event);
        CHECK(services_time_synced());
        CHECK(sntp_inits == 1 && !strcmp(servers[0], "ntp1.aliyun.com") &&
              !strcmp(servers[1], "cn.pool.ntp.org") && !strcmp(servers[2], "pool.ntp.org"));
        strcpy(preferences.country, "HU");
        strcpy(preferences.city, "Budapest");
    }
    if (time_step == 3)
    {
        CHECK(!strcmp(timezone, "UTC-2:00:00") && sntp_inits == 1 && timezone_updates == 2);
        strcpy(preferences.ntp, "fixture.invalid");
        sntp_result = ESP_FAIL;
    }
    if (time_step == 4)
    {
        CHECK(services_time_synced()); /* Failed client reconfiguration must retain valid time. */
        CHECK(sntp_inits == 2 && sntp_deinits == 1 && !strcmp(servers[1], "fixture.invalid"));
        sntp_result = ESP_OK;
    }
    if (time_step == 5)
    {
        CHECK(sntp_inits == 3 && sntp_deinits == 1);
        disconnected();
        strcpy(preferences.ntp, "offline.invalid");
    }
    if (time_step == 6)
    {
        CHECK(services_time_synced()); /* Disconnect does not invalidate a running clock. */
        CHECK(sntp_inits == 3);
        strcpy(preferences.country, "ZZ");
    }
    if (time_step == 7)
    {
        CHECK(!strcmp(timezone, "UTC-1:00:00") && timezone_updates == 3 && sntp_inits == 3);
        longjmp(blocked, 1);
    }
}
static void test_time_worker(void)
{
    /* Configure country timezones while offline; retry failed SNTP and reconfigure servers. */
    station_start();
    strcpy(preferences.country, "GB");
    strcpy(preferences.city, "London");
    services_start();
    CHECK(!strcmp(tasks[1].name, "weather_http") && !strcmp(tasks[2].name, "time_sync"));
    run_task("time_sync", time_scenario);
}

static const struct {time_t epoch; const char *tz;} time_boundaries[] = {
    {1772931600, "UTC-0:00:00"}, /* GB must not use the US March 8 transition. */
    {1774745999, "UTC-0:00:00"},
    {1774746000, "UTC-1:00:00"},
    {1792889999, "UTC-1:00:00"},
    {1792890000, "UTC-0:00:00"},
    {1774746000, "UTC-1:00:00"}, /* Backward epoch corrections revisit the rules. */
    {1774745999, "UTC-0:00:00"},
};
static void time_boundary_scenario(void)
{
    /* Observe actual worker TZ changes while offline, without changing country/city. */
    CHECK(!strcmp(timezone, time_boundaries[time_step].tz));
    CHECK(sntp_inits == 0);
    if (++time_step == sizeof(time_boundaries)/sizeof(time_boundaries[0]))
    {
        CHECK(timezone_updates == 5);
        longjmp(blocked, 1);
    }
    fake_time = time_boundaries[time_step].epoch;
}
static void test_time_zone_boundaries(void)
{
    /* Verify civil-time transitions do not require a new location or network connection. */
    station_start();
    strcpy(preferences.country, "GB");
    fake_time = time_boundaries[0].epoch;
    services_start();
    run_task("time_sync", time_boundary_scenario);
}

static const struct { const char *key, *tz; } regional_times[] = {
    {"AU-W","UTC-8:00:00"}, {"US-H","UTC+10:00:00"},
    {"AU","UTC-11:00:00"}, {"ZZ-ABCDEFGHIJKLMNOP","UTC-0:00:00"},
};
static void regional_time_scenario(void)
{
    /* Change only the regional key, keeping the same city and UTC epoch offline. */
    CHECK(!strcmp(timezone,regional_times[time_step].tz) && sntp_inits==0);
    if(++time_step==sizeof(regional_times)/sizeof(regional_times[0])) {
        CHECK(timezone_updates==4); longjmp(blocked,1);
    }
    strcpy(preferences.country,regional_times[time_step].key);
}
static void test_regional_time_worker(void)
{
    /* Exercise full-length time-task buffers, regional selection and unknown-key fallback. */
    station_start(); fake_time=1767248047;
    strcpy(preferences.country,regional_times[0].key);
    services_start(); run_task("time_sync",regional_time_scenario);
}

static unsigned regional_weather_step;
static void regional_weather_scenario(void)
{
    /* Inspect the real worker's publication before changing only the country suffix. */
    static const char *keys[]={"US-H","AU-W","ZZ-ABCDEFGHIJKLMNOP"};
    weather_snapshot_t snapshot; weather_snapshot(&snapshot);
    if(regional_weather_step) {
        CHECK(snapshot.valid && !strcmp(snapshot.country,keys[regional_weather_step-1]));
        CHECK(snapshot.generation==2*regional_weather_step);
        char expected[96]; snprintf(expected,sizeof(expected),"q=Fixture,%s&appid=",keys[regional_weather_step-1]);
        CHECK(strstr(fetched_url,expected)!=NULL);
    }
    if(regional_weather_step==3)longjmp(blocked,1);
    strcpy(preferences.country,keys[regional_weather_step++]);
    weather_request_update();
}
static void test_regional_weather_worker(void)
{
    /* Verify key changes invalidate the old cache and preserve suffixes in URLs/results. */
    station_start(); got_ip(); strcpy(preferences.city,"Fixture");
    strcpy(preferences.weather_key,"disabled");
    http_body=weather_body; http_length=sizeof(weather_body)-1;
    weather_start(); run_task("weather_http",regional_weather_scenario);
    CHECK(http_calls==3 && http_cleanups==3);
}

static esp_err_t driver_result = ESP_OK;
static ledc_timer_config_t ledc_timer;
static ledc_channel_config_t ledc_channel;
static unsigned duty, duty_updates;
static unsigned ledc_timer_calls, ledc_channel_calls;
static esp_err_t ledc_channel_result;
esp_err_t ledc_timer_config(const ledc_timer_config_t *config)
{
    ++ledc_timer_calls;
    ledc_timer = *config;
    return driver_result;
}
esp_err_t ledc_channel_config(const ledc_channel_config_t *config)
{
    ++ledc_channel_calls;
    ledc_channel = *config;
    return ledc_channel_result;
}
esp_err_t ledc_set_duty(int mode, int channel, unsigned value)
{
    assert(mode == LEDC_LOW_SPEED_MODE && channel == LEDC_CHANNEL_0);
    duty = value;
    return ESP_OK;
}
esp_err_t ledc_update_duty(int mode, int channel)
{
    assert(mode == LEDC_LOW_SPEED_MODE && channel == LEDC_CHANNEL_0);
    ++duty_updates;
    return ESP_OK;
}
static void test_backlight(void)
{
    /* Assert board PWM configuration and strict boundaries for every minute of a day. */
    driver_result = ESP_FAIL;
    CHECK(backlight_init() == ESP_FAIL);
    CHECK(ledc_timer_calls == 1 && ledc_channel_calls == 0 && duty_updates == 0);
    driver_result = ESP_OK;
    ledc_channel_result = ESP_ERR_NO_MEM;
    CHECK(backlight_init() == ESP_ERR_NO_MEM);
    CHECK(ledc_timer_calls == 2 && ledc_channel_calls == 1 && duty_updates == 0);
    ledc_channel_result = ESP_OK;
    CHECK(backlight_init() == ESP_OK);
    CHECK(ledc_timer.freq_hz == 1000 && ledc_timer.duty_resolution == LEDC_TIMER_13_BIT &&
          ledc_channel.gpio_num == 18 && ledc_channel.duty == 0);
    CHECK(duty == 819 && duty_updates == 1);
    unsigned unchanged_updates = duty_updates;
    preferences.day_level = 100;
    preferences.night_mode = 0;
    for (unsigned repeat = 0; repeat < 20; ++repeat)
        backlight_update(&preferences, 12, 0, true);
    CHECK(duty_updates == unchanged_updates);
    backlight_set_level(0);
    CHECK(duty == 0);
    backlight_set_level(1000);
    CHECK(duty == 8191);
    backlight_set_level(2000);
    CHECK(duty == 8191);
    preferences.day_level = 100;
    preferences.night_level = 800;
    preferences.night_mode = 1;
    for (unsigned start = 18; start <= 23; ++start)
        for (unsigned stop = 5; stop <= 12; ++stop)
        {
            preferences.night_start = start;
            preferences.night_stop = stop;
            for (unsigned minute = 0; minute < 1440; ++minute)
            {
                backlight_update(&preferences, minute / 60, minute % 60, true);
                unsigned expected = (minute <= stop * 60 || minute >= start * 60) ? 6552 : 819;
                CHECK(duty == expected);
                backlight_update(&preferences, minute / 60, minute % 60, false);
                CHECK(duty == expected);
            }
        }
    preferences.night_mode = 0;
    backlight_update(&preferences, 23, 59, false);
    CHECK(duty == 819);
    unchanged_updates = duty_updates;
    backlight_set_level(0); /* A fade must invalidate the old scheduled duty. */
    backlight_update(&preferences, 23, 59, false);
    CHECK(duty == 819 && duty_updates == unchanged_updates + 2);
    backlight_update(&preferences, 23, 59, false);
    CHECK(duty_updates == unchanged_updates + 2);
}

static uint16_t panel[240 * 240];
static unsigned dc, command, window_x, window_y, window_w, window_h, pixel_cursor, commands[32],
    command_count, transfers, max_transfer;
static gpio_config_t pin_config;
static spi_bus_config_t spi_bus;
static spi_device_interface_config_t spi_device;
static unsigned resets[2], reset_count;
esp_err_t gpio_config(const gpio_config_t *config)
{
    pin_config = *config;
    return driver_result;
}
esp_err_t gpio_set_level(int pin, unsigned value)
{
    if (pin == 5)
        dc = value;
    else
    {
        assert(pin == 1);
        assert(reset_count < 2);
        resets[reset_count++] = value;
    }
    return ESP_OK;
}
esp_err_t spi_bus_initialize(int host, const spi_bus_config_t *config, int dma)
{
    assert(host == SPI2_HOST && dma == SPI_DMA_CH_AUTO);
    spi_bus = *config;
    return ESP_OK;
}
esp_err_t spi_bus_add_device(int host, const spi_device_interface_config_t *config,
                             spi_device_handle_t *device)
{
    assert(host == SPI2_HOST);
    spi_device = *config;
    *device = (void *)1;
    return ESP_OK;
}
static bool digital_brightness_probe;
static unsigned expected_digital_duty, digital_ink;
esp_err_t spi_device_polling_transmit(spi_device_handle_t device, spi_transaction_t *transaction)
{
    /* Decode actual ST7789 command/data bytes at the peripheral boundary into a test panel. */
    assert(!in_alarm && device && transaction->length % 8 == 0);
    size_t bytes = transaction->length / 8;
    const uint8_t *data = transaction->tx_buffer;
    assert(bytes <= 1920 && bytes);
    ++transfers;
    if (bytes > max_transfer)
        max_transfer = (unsigned)bytes;
    if (digital_brightness_probe && dc && command == 0x2c)
        for (size_t i=0;i+1<bytes;i+=2)
            if (data[i] || data[i+1]) {
                CHECK(duty==expected_digital_duty);
                ++digital_ink;
            }
    if (!dc)
    {
        assert(bytes == 1);
        command = data[0];
        if (command_count < 32)
            commands[command_count++] = command;
        if (command == 0x2c)
            pixel_cursor = 0;
        return ESP_OK;
    }
    if (command == 0x2a)
    {
        assert(bytes == 4);
        window_x = (data[0] << 8) | data[1];
        unsigned end = (data[2] << 8) | data[3];
        assert(end >= window_x && end < 240);
        window_w = end - window_x + 1;
    }
    else if (command == 0x2b)
    {
        assert(bytes == 4);
        window_y = (data[0] << 8) | data[1];
        unsigned end = (data[2] << 8) | data[3];
        assert(end >= window_y && end < 240);
        window_h = end - window_y + 1;
    }
    else if (command == 0x3a)
    {
        assert(bytes == 1 && data[0] == 0x55);
    }
    else if (command == 0x36)
    {
        assert(bytes == 1 && data[0] == 0);
    }
    else if (command == 0x2c)
    {
        assert(bytes % 2 == 0 && window_w && window_h &&
               pixel_cursor + bytes / 2 <= window_w * window_h);
        for (size_t i = 0; i < bytes; i += 2, ++pixel_cursor)
            panel[(window_y + pixel_cursor / window_w) * 240 + window_x + pixel_cursor % window_w] =
                (data[i] << 8) | data[i + 1];
    }
    else
        assert(false);
    return ESP_OK;
}
static void test_display(void)
{
    /* Verify reset/SPI protocol, RGB565 byte order, clipping, stride and LSB-first glyphs. */
    driver_result = ESP_FAIL;
    CHECK(display_init() == ESP_FAIL);
    driver_result = ESP_OK;
    CHECK(display_init() == ESP_OK);
    CHECK(pin_config.pin_bit_mask == ((1ULL << 1) | (1ULL << 5)) && spi_bus.mosi_io_num == 6 &&
          spi_bus.sclk_io_num == 4 && spi_bus.miso_io_num == -1);
    CHECK(spi_device.mode == 3 && spi_device.clock_speed_hz == 40000000 &&
          spi_device.spics_io_num == -1 && max_transfer == 1920);
    CHECK(reset_count == 2 && resets[0] == 0 && resets[1] == 1 && delays == 540);
    const unsigned init[] = {0x11, 0x3a, 0x36, 0x2a, 0x2b, 0x2c,
                             0x21, 0x13, 0x29, 0x2a, 0x2b, 0x2c};
    CHECK(command_count == 12 && !memcmp(commands, init, sizeof(init)));
    display_fill(-2, -3, 5, 7, 0x1234);
    for (unsigned y = 0; y < 240; ++y)
        for (unsigned x = 0; x < 240; ++x)
            CHECK(panel[y * 240 + x] == ((x < 3 && y < 4) ? 0x1234 : 0));
    display_fill(238, 238, 8, 9, 0xabcd);
    CHECK(panel[239 * 240 + 239] == 0xabcd && panel[237 * 240 + 239] == 0);
    unsigned before = transfers;
    display_fill(240, 240, 2, 2, 0xffff);
    display_fill(0, 0, 0, 5, 0xffff);
    CHECK(transfers == before);
    const uint16_t source[] = {1, 2, 3, 4, 5, 6, 7, 8, 9};
    display_blit(-1, -1, 3, 3, source);
    CHECK(panel[0] == 5 && panel[1] == 6 && panel[240] == 8 && panel[241] == 9);
    uint8_t bits[] = {1, 2};
    tv_bitmap_t bitmap = {bits, 9, 1, 2};
    display_bitmap(10, 10, &bitmap, 0xff00, 0x00ff, false);
    for (unsigned x = 0; x < 9; ++x)
        CHECK(panel[10 * 240 + 10 + x] == (x == 0 ? 0xff00 : 0x00ff));
    bits[1] = 1;
    display_bitmap(10, 11, &bitmap, 0xffff, 0, false);
    CHECK(panel[11 * 240 + 18] == 0xffff);
    display_fill(20, 20, 9, 1, 0x1234);
    display_bitmap(20, 20, &bitmap, 0xffff, 0, true);
    CHECK(panel[20 * 240 + 20] == 0xffff && panel[20 * 240 + 21] == 0x1234 &&
          panel[20 * 240 + 28] == 0xffff);
    display_line(0, 230, 4, 234, 0x8888);
    for (unsigned n = 0; n < 5; ++n)
        CHECK(panel[(230 + n) * 240 + n] == 0x8888);
    before = transfers;
    display_text(0, 0, "x", 0, 0xffff, 0);
    display_text(0, 0, "x", 9, 0xffff, 0);
    CHECK(transfers == before);
}

static unsigned animation_calls, weather_draws, jpeg_draws, photo_draws, last_animation, last_frame;
static unsigned last_photo_slot;
static bool weather_pixels;
static esp_err_t weather_draw_result;
unsigned media_animation_frames(unsigned animation)
{
    const unsigned counts[] = {19, 15, 25, 16, 23};
    assert(animation < 5);
    return counts[animation];
}
esp_err_t media_draw_animation(unsigned animation, unsigned frame, int x, int y)
{
    assert(x == 160 && y == 160);
    ++animation_calls;
    last_animation = animation;
    last_frame = frame;
    return ESP_OK;
}
esp_err_t media_draw_weather(const char *code, int x, int y)
{
    assert(strlen(code) == 3 && x == 180 && y == 10);
    ++weather_draws;
    /* Only the cleanup scenario models full/partial output at the decoder boundary. */
    if (weather_pixels)
        display_fill(x, y, 60, weather_draw_result == ESP_OK ? 60 : 5, 0x1234);
    return weather_draw_result;
}
esp_err_t media_draw_jpeg(uint32_t address, size_t capacity, int x, int y)
{
    assert(address >= 0x3ba800 && capacity == 0x3c00 && x >= 0 && y >= 180);
    ++jpeg_draws;
    return ESP_OK;
}
esp_err_t media_draw_photo(unsigned slot)
{
    assert(slot < 5);
    ++photo_draws;
    last_photo_slot = slot;
    return ESP_OK;
}
static void test_ui_transitions(void)
{
    /* Test incremental/full redraw consistency and media dispatch; decoding is tested separately.
     */
    CHECK(display_init() == ESP_OK);
    factory_draw_setup();
    unsigned colored = 0;
    for (unsigned i = 0; i < 240 * 240; ++i)
        colored += panel[i] != 0;
    CHECK(colored > 1000);
    factory_draw_startup("10.0.2.15", 180);
    for (unsigned x = 29; x < 209; ++x)
        CHECK(panel[145 * 240 + x] == 0xffff);
    tv_bitmap_t glyph;
    const unsigned heights[] = {16, 24, 32, 40, 64, 80};
    for (unsigned i = 0; i < 6; ++i)
        CHECK(factory_glyph('0', heights[i], &glyph) && glyph.height == heights[i]);
    CHECK(!factory_glyph('0', 17, &glyph));
    weather_snapshot_t weather = {.valid = true,
                                  .temperature_c = 20,
                                  .humidity = 73,
                                  .wind_mps = 3.7,
                                  .temperature_min_c = 18,
                                  .temperature_max_c = 23,
                                  .generation = 1};
    strcpy(weather.icon, "02d");
    strcpy(weather.main, "Clouds");
    strcpy(weather.description, "clear");
    strcpy(weather.wind_direction, "East");
    struct tm local = {.tm_year = 126,
                       .tm_mon = 9,
                       .tm_mday = 13,
                       .tm_wday = 2,
                       .tm_yday = 285,
                       .tm_hour = 23,
                       .tm_min = 59,
                       .tm_sec = 58};
    preferences.colors[0] = 0xf800;
    preferences.colors[1] = 0xffe0;
    preferences.colors[2] = 0xffff;
    factory_draw_classic(&preferences, &local, &weather, 0, 0, true, true);
    CHECK(weather_draws == 1 && jpeg_draws == 4 && animation_calls == 1);
    static uint16_t incremental[240 * 240];
    for (unsigned units = 0; units < 2; ++units)
        for (unsigned date = 0; date < 3; ++date)
            for (unsigned step = 0; step < 10; ++step)
            {
                preferences.fahrenheit = units;
                preferences.miles = units;
                preferences.hour12 = units;
                preferences.date_format = date;
                preferences.animation = step % 5;
                local.tm_sec = step;
                local.tm_min = step / 3;
                factory_draw_classic(&preferences, &local, &weather, step, 99, false, false);
                memcpy(incremental, panel, sizeof(panel));
                factory_draw_classic(&preferences, &local, &weather, step, 99, true, true);
                CHECK(!memcmp(panel, incremental, sizeof(panel)));
                CHECK(last_animation == step % 5 &&
                      last_frame == 99 % media_animation_frames(step % 5));
            }
    weather.valid = false;
    ++weather.generation;
    factory_draw_classic(&preferences, &local, &weather, 0, 0, false, true);
    CHECK(animation_calls == 122);
    for (unsigned slot = 0; slot < 5; ++slot)
        factory_draw_photo(slot, "10.0.2.15");
    CHECK(photo_draws == 5);
}

static void test_text_fields(void)
{
    /* Compare scrolling windows against a full unscrolled glyph raster and guard pixels. */
    CHECK(display_init() == ESP_OK);
    const char *text = "ABCDEFGHIJKLMNOPQRS";
    display_factory_text(0, 0, text, 24, 0xffff, 0, false);
    static uint16_t raster[24 * 240];
    memcpy(raster, panel, sizeof(raster));
    const unsigned offsets[] = {0, 1, 7, 12, 73, 148, 149, 0xffffffff};
    for (unsigned test = 0; test < sizeof(offsets) / sizeof(offsets[0]); ++test)
    {
        display_fill(0, 0, 240, 240, 0x4567);
        display_factory_text_window(20, 5, 80, offsets[test], text, 24, 0xffff, 0);
        unsigned offset = offsets[test] < 148 ? offsets[test] : 148;
        for (unsigned y = 0; y < 240; ++y)
            for (unsigned x = 0; x < 240; ++x)
                CHECK(panel[y * 240 + x] == (x >= 20 && x < 100 && y >= 5 && y < 29
                    ? raster[(y - 5) * 240 + x - 20 + offset] : 0x4567));
    }
    unsigned before = transfers;
    display_factory_text_window(20, 5, 0, 0, text, 24, 0xffff, 0);
    display_factory_text_window(20, 5, -1, 0, text, 24, 0xffff, 0);
    CHECK(transfers == before);
    CHECK(display_factory_text_width("12\xa1\xe6", 24) == 48);
    display_fill(0, 0, 240, 240, 0x4567);
    display_factory_text_bounded(20, 5, 36, "12\xa1\xe6", 24, 0xffff, 0, false);
    for (unsigned y = 5; y < 29; ++y)
        for (unsigned x = 44; x < 80; ++x)
            CHECK(panel[y * 240 + x] == 0x4567); /* Unit pair is never split. */
    display_factory_text_window(200, 5, 80, 0xffffffff, text, 24, 0xffff, 0);
    for (unsigned y = 5; y < 29; ++y)
        for (unsigned x = 200; x < 240; ++x)
            CHECK(panel[y * 240 + x] == raster[(y - 5) * 240 + x - 200 + 188]);
    /* UTF-8 byte counts differ from rendered cells; every spelling of a unit
     * must preserve the literal factory unit raster, including edge clipping. */
    const char *cyrillic="\xd0\xa2\xd0\xb5\xd1\x81\xd1\x82";
    CHECK(display_factory_text_width(cyrillic,24)==48);
    CHECK(display_factory_text_width("\xe5\x8c\x97\xe4\xba\xac",24)==24);
    CHECK(display_factory_text_width("\xe2\x84\x83",24)==24);
    CHECK(display_factory_text_width("\xc2\xb0" "C",24)==24);
    CHECK(display_factory_text_width("\xc2\xb0",24)==12);
    CHECK(display_factory_text_width(NULL,24)==0);
    const char *units[]={"\xa1\xe6","\xe2\x84\x83","\xc2\xb0" "C"};
    static uint16_t unit_raster[240*24];
    for(unsigned i=0;i<3;++i){
        display_fill(0,0,240,240,0);
        display_factory_text(10,0,units[i],24,0xffff,0,false);
        if (!i) memcpy(unit_raster,panel,sizeof(unit_raster));
        else CHECK(!memcmp(unit_raster,panel,sizeof(unit_raster)));
    }
    display_fill(0,0,240,240,0);
    display_factory_text(0,0,"?A",24,0xffff,0,false);
    memcpy(unit_raster,panel,sizeof(unit_raster));
    display_fill(0,0,240,240,0);
    display_factory_text(0,0,"\x81" "A",24,0xffff,0,false);
    CHECK(!memcmp(unit_raster,panel,sizeof(unit_raster)));
    const char *mixed="A\xd0\xa2\xd0\xb5\xd1\x81\xd1\x82" "BCDEFG";
    CHECK(display_factory_text_width(mixed,24)==132);
    display_fill(0,0,240,240,0);
    display_factory_text(0,0,mixed,24,0xffff,0,false);
    memcpy(raster,panel,sizeof(raster));
    const unsigned unicode_offsets[]={0,1,7,12,51,52,0xffffffff};
    for(unsigned i=0;i<sizeof(unicode_offsets)/sizeof(unicode_offsets[0]);++i){
        unsigned offset=unicode_offsets[i]<52?unicode_offsets[i]:52;
        display_fill(0,0,240,240,0x4567);
        display_factory_text_window(20,5,80,unicode_offsets[i],mixed,24,0xffff,0);
        for(unsigned y=0;y<240;++y)
            for(unsigned x=0;x<240;++x)
                CHECK(panel[y*240+x]==(x>=20&&x<100&&y>=5&&y<29
                    ?raster[(y-5)*240+x-20+offset]:0x4567));
    }
}

static void test_weather_field_cleanup(void)
{
    /* Test retained frames, both scroll endpoints, content reset and failed icon cleanup. */
    CHECK(display_init() == ESP_OK);
    weather_pixels = true;
    struct tm local = {.tm_year=126,.tm_mon=9,.tm_mday=13,.tm_yday=285,
                       .tm_wday=2,.tm_hour=7,.tm_min=14};
    weather_snapshot_t weather = {.valid=true,.generation=1,.humidity=67,.temperature_c=26};
    strcpy(weather.icon, "01d");
    strcpy(weather.main, "Thunderstorm");
    strcpy(weather.description, "ABCDEFGHIJKLMNOPQRS");
    strcpy(preferences.city, "ABCDEFGHIJKLMNOPQRS");
    factory_draw_classic(&preferences,&local,&weather,6,0,true,true);
    CHECK(!factory_scroll_description_ready());
    static uint16_t initial[240*240];
    memcpy(initial,panel,sizeof(panel));
    unsigned before = transfers;
    for (unsigned tick=0; tick<15; ++tick) factory_scroll_tick();
    CHECK(transfers == before && !memcmp(initial,panel,sizeof(panel)));
    factory_scroll_tick();
    CHECK(memcmp(initial,panel,sizeof(panel)) != 0);
    /* The three independently clipped fields are the only possible changed pixels. */
    for (unsigned y=0; y<240; ++y)
        for (unsigned x=0; x<240; ++x)
            if (!((x<180 && ((y>=10 && y<34)||(y>=40 && y<64))) ||
                  (x>=160 && y>=83 && y<107)))
                CHECK(panel[y*240+x] == initial[y*240+x]);
    /* City and description travel 48px in 24 steps; the weather title needs 32. */
    for (unsigned tick=1; tick<24; ++tick) factory_scroll_tick();
    static uint16_t endpoint[24*180];
    for (unsigned y=0; y<24; ++y) memcpy(endpoint+y*180,panel+(y+10)*240,180*2);
    display_factory_text_window(0,10,180,48,preferences.city,24,0x07e0,0);
    for (unsigned y=0; y<24; ++y) CHECK(!memcmp(endpoint+y*180,panel+(y+10)*240,180*2));
    for (unsigned tick=24; tick<78; ++tick) factory_scroll_tick();
    CHECK(factory_scroll_description_ready());
    for (unsigned y=10; y<34; ++y) CHECK(!memcmp(panel+y*240,initial+y*240,180*2));
    for (unsigned y=40; y<64; ++y) CHECK(!memcmp(panel+y*240,initial+y*240,180*2));
    for (unsigned tick=78; tick<94; ++tick) factory_scroll_tick();
    for (unsigned y=83; y<107; ++y) CHECK(!memcmp(panel+y*240+160,initial+y*240+160,80*2));
    strcpy(preferences.city, "A");
    strcpy(weather.main, "Fog");
    strcpy(weather.description, "clear");
    ++weather.generation;
    factory_draw_classic(&preferences,&local,&weather,6,0,false,true);
    CHECK(factory_scroll_description_ready());
    memcpy(initial,panel,sizeof(panel));
    for (unsigned tick=0; tick<100; ++tick) factory_scroll_tick();
    CHECK(!memcmp(initial,panel,sizeof(panel)));
    /* Clean rendering must match a frame updated from much longer strings. */
    display_fill(0,0,240,240,0);
    factory_draw_classic(&preferences,&local,&weather,6,0,true,true);
    CHECK(!memcmp(initial,panel,sizeof(panel)));
    const unsigned guards[] = {34*240+179,180,83*240+159,107*240+160,9*240+180,70*240+180};
    for (unsigned i=0; i<sizeof(guards)/sizeof(guards[0]); ++i) panel[guards[i]]=0x5678;
    weather_draw_result = ESP_FAIL;
    factory_draw_classic(&preferences,&local,&weather,6,0,false,true);
    for (unsigned y=10; y<70; ++y)
        for (unsigned x=180; x<240; ++x) CHECK(panel[y*240+x]==0);
    for (unsigned i=0; i<sizeof(guards)/sizeof(guards[0]); ++i) CHECK(panel[guards[i]]==0x5678);
    weather_draw_result = ESP_OK;
    factory_draw_classic(&preferences,&local,&weather,6,0,false,true);
    weather.valid = false;
    strcpy(preferences.city, "");
    factory_draw_classic(&preferences,&local,&weather,6,0,false,true);
    for (unsigned y=0; y<34; ++y)
        for (unsigned x=0; x<180; ++x) CHECK(panel[y*240+x]==0);
    for (unsigned y=83; y<107; ++y)
        for (unsigned x=160; x<240; ++x) CHECK(panel[y*240+x]==0);
    for (unsigned y=10; y<70; ++y)
        for (unsigned x=180; x<240; ++x) CHECK(panel[y*240+x]==0);
}

static unsigned timer_calls, timer_failure, clock_step, blocked_transfers;
static gptimer_config_t timer_config;
static gptimer_alarm_config_t alarm_config;
static gptimer_event_callbacks_t timer_callbacks;
static esp_err_t timer_result(void)
{
    return ++timer_calls == timer_failure ? ESP_FAIL : ESP_OK;
}
esp_err_t gptimer_new_timer(const gptimer_config_t *config, gptimer_handle_t *timer)
{
    timer_config = *config;
    *timer = (void *)1;
    return timer_result();
}
esp_err_t gptimer_set_alarm_action(gptimer_handle_t timer, const gptimer_alarm_config_t *config)
{
    assert(timer);
    alarm_config = *config;
    return timer_result();
}
esp_err_t gptimer_register_event_callbacks(gptimer_handle_t timer,
                                           const gptimer_event_callbacks_t *callbacks,
                                           void *context)
{
    assert(timer && context == NULL);
    timer_callbacks = *callbacks;
    return timer_result();
}
esp_err_t gptimer_enable(gptimer_handle_t timer)
{
    assert(timer);
    return timer_result();
}
esp_err_t gptimer_start(gptimer_handle_t timer)
{
    assert(timer);
    return timer_result();
}
static void tick_clock(unsigned count)
{
    /* Inject real ISR callbacks; the SPI adapter rejects any drawing from the ISR. */
    in_alarm = true;
    for (unsigned i = 0; i < count; ++i)
        CHECK(!timer_callbacks.on_alarm((void *)1, NULL, NULL));
    in_alarm = false;
}
static void seed_weather(void)
{
    /* Complete one weather request before running the clock coordinator. */
    if (steps++)
        longjmp(blocked, 1);
    weather_request_update();
}
static void stop_time_worker_once(void)
{
    /* Stop only after the actual worker has configured its SDK callback. */
    longjmp(blocked, 1);
}
static void start_synced_clock_services(void)
{
    /* Start production services and deliver the SDK notification after successful init. */
    services_start();
    run_task("time_sync", stop_time_worker_once);
    CHECK(sntp_callback && sntp_result == ESP_OK && !services_time_synced());
    struct timeval event = {.tv_sec=fake_time};
    sntp_callback(&event);
    CHECK(services_time_synced());
}
static void clock_scenario(void)
{
    /* Advance the real clock task through startup, each theme, blocked upload and weather event. */
    ++clock_step;
    if (clock_step < 182)
        CHECK(animation_calls == 0 && photo_draws == 0);
    if (clock_step == 182)
    {
        CHECK(animation_calls == 1);
        struct timeval event = {.tv_sec = fake_time};
        sntp_callback(&event);
    }
    if (clock_step == 200)
    {
        preferences.theme = 1;
        ++preferences_generation;
    }
    if (clock_step == 220)
    {
        preferences.theme = 2;
        preferences.photo_mask = 31;
        for (unsigned i = 0; i < 5; ++i)
            preferences.photo_size[i] = 100;
        ++preferences_generation;
    }
    if (clock_step == 223)
        CHECK(photo_draws == 1);
    if (clock_step == 227)
        CHECK(duty == 819); /* configured day duty restored after six fade steps */
    if (clock_step == 240)
    {
        uploading = true;
        blocked_transfers = transfers;
    }
    if (clock_step > 240 && clock_step <= 245)
        CHECK(transfers == blocked_transfers);
    if (clock_step == 245)
        uploading = false;
    if (clock_step == 255)
    {
        preferences.theme = 3;
        ++preferences_generation;
    }
    if (clock_step == 280)
    {
        CHECK(panel[120 * 240 + 120] != 0);
        disconnected();
        blocked_transfers = transfers;
    }
    if (clock_step > 280 && clock_step <= 285)
        CHECK(!network_connected() && services_time_synced());
    if (clock_step == 285)
        got_ip();
    if (clock_step == 300)
        tick_clock(19811); /* periodic weather event, no SPI from ISR */
    if (clock_step == 301)
    {
        CHECK(weather_request_active());
        blocked_transfers = transfers;
    }
    if (clock_step == 302)
    {
        CHECK(transfers == blocked_transfers);
        longjmp(blocked, 1);
    }
    tick_clock(1);
    if (clock_step % 10 == 0)
    {
        ++fake_time;
        fake_local.tm_sec = (fake_local.tm_sec + 1) % 60;
    }
}
static void test_clock_coordinator(void)
{
    /* Exercise production clock_ui.c together with the timer/fade/rendering implementation. */
    preferences.wifi_mode = 1;
    strcpy(preferences.ssid, "fixture");
    preferences.day_level = 100;
    preferences.night_level = 800;
    preferences.night_start = 22;
    preferences.night_stop = 9;
    CHECK(clock_ui_timer_init() == ESP_OK);
    CHECK(timer_calls == 5 && timer_config.clk_src == GPTIMER_CLK_SRC_XTAL &&
          timer_config.resolution_hz == 1000000);
    CHECK(alarm_config.alarm_count == 100000 && alarm_config.reload_count == 0 &&
          alarm_config.flags.auto_reload_on_alarm);
    CHECK(network_init() == ESP_OK);
    got_ip();
    services_start();
    run_task("time_sync", stop_time_worker_once); /* Exercise the unchanged startup timeout. */
    CHECK(sntp_callback && !services_time_synced());
    strcpy(preferences.weather_key, "fixture-key");
    run_task("weather_http", seed_weather);
    CHECK(display_init() == ESP_OK);
    clock_ui_start();
    run_task("clock_display", clock_scenario);
    CHECK(clock_step == 302 && photo_draws >= 1);
}

static void digital_entry_scenario(void)
{
    /* Observe colored SPI pixels, rather than merely checking duty after a frame. */
    ++clock_step;
    if (clock_step==1) {
        CHECK(digital_ink>0); digital_ink=0;
        preferences.theme=1; ++preferences_generation;
        backlight_set_level(800); /* Simulate entering from a different visible duty. */
    }
    if (clock_step==2) {
        CHECK(digital_ink>0 && duty==expected_digital_duty);
        longjmp(blocked,1);
    }
    tick_clock(1);
}
static void test_first_digital_brightness(void)
{
    /* Both first classic and simple frames must use the configured brightness. */
    preferences.wifi_mode=1; strcpy(preferences.ssid,"fixture");
    preferences.day_level=500; expected_digital_duty=4095;
    CHECK(clock_ui_timer_init()==ESP_OK);
    CHECK(network_init()==ESP_OK); got_ip(); start_synced_clock_services();
    strcpy(preferences.weather_key,"fixture-key");
    run_task("weather_http",seed_weather);
    CHECK(display_init()==ESP_OK && backlight_init()==ESP_OK);
    CHECK(duty==819);
    digital_brightness_probe=true;
    clock_ui_start(); run_task("clock_display",digital_entry_scenario);
}

static unsigned idle_photo_transfers, idle_photo_duty_updates;
static void photo_idle_brightness_scenario(void)
{
    /* Settings and day/night changes must not wait for the next 60-second photo event. */
    ++clock_step;
    if (clock_step >= 6)
        CHECK(photo_draws == 1);
    if (clock_step == 6)
    {
        CHECK(duty == 819);
        idle_photo_transfers = transfers;
        preferences.day_level = 500;
        ++preferences_generation;
    }
    if (clock_step >= 7)
        CHECK(transfers == idle_photo_transfers);
    if (clock_step == 7)
    {
        CHECK(duty == 4095);
        preferences.night_mode = 1;
        preferences.night_level = 800;
        fake_time = 1791907200; /* CN 2026-10-14 00:00:00, synchronized night. */
        ++preferences_generation;
    }
    if (clock_step == 8)
    {
        CHECK(duty == 6552);
        fake_time = 1791885600; /* CN 18:00:00; calendar change without a settings write. */
    }
    if (clock_step == 9)
    {
        CHECK(duty == 4095);
        preferences.day_level = 0;
        ++preferences_generation;
    }
    if (clock_step == 10)
    {
        CHECK(duty == 0);
        idle_photo_duty_updates = duty_updates;
    }
    if (clock_step == 15)
    {
        CHECK(duty_updates == idle_photo_duty_updates);
        longjmp(blocked, 1);
    }
    tick_clock(1);
}
static void test_photo_idle_brightness(void)
{
    /* Exercise the real photo coordinator and cached LEDC setter during an idle interval. */
    preferences.wifi_mode = 1; strcpy(preferences.ssid, "fixture");
    preferences.theme = 2; preferences.photo_seconds = 60;
    preferences.photo_mask = 1; preferences.photo_size[0] = 100;
    preferences.day_level = 100; preferences.night_mode = 0;
    preferences.night_start = 22; preferences.night_stop = 9;
    CHECK(clock_ui_timer_init() == ESP_OK);
    CHECK(network_init() == ESP_OK); got_ip(); start_synced_clock_services();
    CHECK(display_init() == ESP_OK && backlight_init() == ESP_OK);
    clock_ui_start(); run_task("clock_display", photo_idle_brightness_scenario);
}

static void photo_reselect_scenario(void)
{
    /* Two explicit same-theme commands must each start one new six-step fade. */
    ++clock_step;
    if (clock_step == 6)
    {
        CHECK(photo_draws == 1 && duty == 0);
        CHECK(settings_select_theme(2) == ESP_OK);
    }
    if (clock_step == 7 || clock_step == 13)
        CHECK(duty == 2457); /* A new fade starts immediately instead of waiting 60 seconds. */
    if (clock_step == 9)
        CHECK(photo_draws == 2);
    if (clock_step == 12)
    {
        CHECK(photo_draws == 2 && duty == 0);
        /* Factory flags coalesce two commands arriving before the next pass. */
        CHECK(settings_select_theme(2) == ESP_OK && settings_select_theme(2) == ESP_OK);
    }
    if (clock_step == 15)
        CHECK(photo_draws == 3);
    if (clock_step == 18)
    {
        CHECK(photo_draws == 3 && duty == 0);
        CHECK(theme_selection_generation == 3);
        longjmp(blocked, 1);
    }
    tick_clock(1);
}
static void test_photo_reselect(void)
{
    /* Exercise the real coordinator with unchanged settings and transient selection revisions. */
    preferences.wifi_mode = 1; strcpy(preferences.ssid, "fixture");
    preferences.theme = 2; preferences.photo_seconds = 60; preferences.photo_mask = 31;
    for (unsigned slot = 0; slot < 5; ++slot) preferences.photo_size[slot] = 100;
    preferences.day_level = 0; preferences.night_mode = 0;
    CHECK(clock_ui_timer_init() == ESP_OK);
    CHECK(network_init() == ESP_OK); got_ip(); start_synced_clock_services();
    CHECK(display_init() == ESP_OK && backlight_init() == ESP_OK);
    clock_ui_start(); run_task("clock_display", photo_reselect_scenario);
}

static void photo_active_reselect_scenario(void)
{
    /* Restart a cancelled fade after its photo draw, retaining the next slot. */
    ++clock_step;
    if (clock_step == 3)
    {
        CHECK(photo_draws == 1 && last_photo_slot == 0 && duty == 8191);
        CHECK(settings_select_theme(2) == ESP_OK);
    }
    if (clock_step == 4)
        CHECK(duty == 2457); /* Reinit must begin at phase zero after clearing the old picture. */
    if (clock_step == 6)
        CHECK(photo_draws == 2 && last_photo_slot == 1);
    if (clock_step == 9)
    {
        CHECK(photo_draws == 2 && duty == 0);
        longjmp(blocked, 1);
    }
    tick_clock(1);
}
static void test_photo_active_reselect(void)
{
    /* A same-theme command during fade must not leave a blank screen for 60 seconds. */
    preferences.wifi_mode = 1; strcpy(preferences.ssid, "fixture");
    preferences.theme = 2; preferences.photo_seconds = 60; preferences.photo_mask = 3;
    for (unsigned slot = 0; slot < 5; ++slot) preferences.photo_size[slot] = 100;
    preferences.day_level = 0; preferences.night_mode = 0;
    CHECK(clock_ui_timer_init() == ESP_OK);
    CHECK(network_init() == ESP_OK); got_ip(); start_synced_clock_services();
    CHECK(display_init() == ESP_OK && backlight_init() == ESP_OK);
    clock_ui_start(); run_task("clock_display", photo_active_reselect_scenario);
}

static void startup_ready_scenario(void)
{
    /* A usable station clock must render at the first task pass, before 181 timer ticks. */
    CHECK(clock_step == 0 && network_connected());
    if (preferences.theme == 0)
        CHECK(animation_calls == 1);
    else if (preferences.theme == 2)
        CHECK(duty == 2457); /* First 30%-brightness fade action, without SNTP. */
    else
    {
        uint16_t rendered[240 * 240];
        memcpy(rendered, panel, sizeof(rendered));
        struct tm local;
        CHECK(services_local_time(preferences.country, fake_time, &local));
        if (preferences.theme == 1)
            factory_draw_simple(&preferences, &local, "10.0.2.15", true, true, true);
        else
            factory_draw_dial(&local, "10.0.2.15", true);
        CHECK(!memcmp(rendered, panel, sizeof(rendered)));
    }
    ++clock_step;
    longjmp(blocked, 1);
}
static void test_startup_ready(unsigned theme)
{
    /* Exercise the real coordinator's early-ready path for each independently booted theme. */
    preferences.wifi_mode = 1; strcpy(preferences.ssid, "fixture");
    preferences.theme = theme; preferences.day_level = 500;
    CHECK(clock_ui_timer_init() == ESP_OK);
    CHECK(network_init() == ESP_OK); got_ip();
    if (theme != 2)
        start_synced_clock_services();
    else
        services_start();
    CHECK(display_init() == ESP_OK && backlight_init() == ESP_OK);
    clock_ui_start(); run_task("clock_display", startup_ready_scenario);
    CHECK(clock_step == 1);
}
static void test_startup_ready_classic(void)
{
    /* Start classic rendering as soon as the clock is ready. */
    test_startup_ready(0);
}
static void test_startup_ready_simple(void)
{
    /* Start the simple clock as soon as its calendar is ready. */
    test_startup_ready(1);
}
static void test_startup_ready_photo(void)
{
    /* A connected photo theme needs no time synchronization. */
    test_startup_ready(2);
}
static void test_startup_ready_dial(void)
{
    /* Start analog rendering as soon as the calendar is ready. */
    test_startup_ready(3);
}

static bool startup_wait_address;
static void startup_wait_scenario(void)
{
    /* Supply the missing prerequisite after two passes; a lost link must not restart startup. */
    ++clock_step;
    if (clock_step <= 2)
        CHECK(animation_calls == 0);
    if (clock_step == 2)
    {
        if (startup_wait_address)
            got_ip();
        else
        {
            struct timeval event = {.tv_sec = fake_time};
            sntp_callback(&event);
        }
    }
    if (clock_step == 3)
    {
        CHECK(animation_calls == 1);
        disconnected();
    }
    if (clock_step == 4)
    {
        CHECK(animation_calls == 2 && !network_connected());
        longjmp(blocked, 1);
    }
    tick_clock(1);
}
static void test_startup_wait(bool address)
{
    /* Retain the startup screen until both a station lease and confirmed time are available. */
    startup_wait_address = address;
    preferences.wifi_mode = 1; strcpy(preferences.ssid, "fixture");
    CHECK(clock_ui_timer_init() == ESP_OK && network_init() == ESP_OK); got_ip();
    services_start(); run_task("time_sync", stop_time_worker_once);
    CHECK(sntp_callback && !services_time_synced());
    if (address)
    {
        struct timeval event = {.tv_sec = fake_time}; sntp_callback(&event);
        disconnected();
    }
    CHECK(display_init() == ESP_OK);
    clock_ui_start(); run_task("clock_display", startup_wait_scenario);
    CHECK(clock_step == 4);
}
static void test_startup_wait_sync(void)
{
    /* A station lease alone does not prove the clock is synchronized. */
    test_startup_wait(false);
}
static void test_startup_wait_address(void)
{
    /* A previously synchronized clock still waits for its initial station lease. */
    test_startup_wait(true);
}
static void test_timer_driver_failures(void)
{
    /* Every failed GPTimer initialization stage must propagate without later API calls. */
    for (unsigned i = 1; i <= 5; ++i)
    {
        timer_calls = 0;
        timer_failure = i;
        CHECK(clock_ui_timer_init() == ESP_FAIL && timer_calls == i);
    }
}

static void animation_scenario(void)
{
    /* Follow the factory cursor across a shorter GIF and a temporary theme switch. */
    ++clock_step;
    if (clock_step == 21)
    {
        CHECK(animation_calls == 21 && last_animation == 2 && last_frame == 20);
        preferences.animation = 1; /* 25 -> 15 frames, old cursor is 21. */
        ++preferences_generation;
    }
    if (clock_step == 22)
    {
        CHECK(last_animation == 1 && last_frame == 0);
        preferences.theme = 1;
        ++preferences_generation;
    }
    if (clock_step > 22 && clock_step <= 28)
        CHECK(animation_calls == 22);
    if (clock_step == 28)
    {
        preferences.theme = 0;
        ++preferences_generation;
    }
    if (clock_step == 29)
    {
        CHECK(animation_calls == 23 && last_frame == 1);
        longjmp(blocked, 1);
    }
    tick_clock(1);
}

static void test_clock_animation_selection(void)
{
    /* Exercise the real clock task, not just a helper, against an observed factory trace. */
    preferences.wifi_mode = 1;
    preferences.animation = 2;
    strcpy(preferences.ssid, "fixture");
    CHECK(clock_ui_timer_init() == ESP_OK);
    CHECK(network_init() == ESP_OK);
    got_ip();
    start_synced_clock_services();
    strcpy(preferences.weather_key, "fixture-key");
    run_task("weather_http", seed_weather);
    CHECK(display_init() == ESP_OK);
    clock_ui_start();
    run_task("clock_display", animation_scenario);
    CHECK(clock_step == 29);
}

static uint16_t clock_first_frame[240*240];
static void clock_text_scenario(void)
{
    /* Follow actual display-loop motion, upload suspension and theme re-entry. */
    ++clock_step;
    if (clock_step == 1) memcpy(clock_first_frame,panel,sizeof(panel));
    if (clock_step == 15) CHECK(!memcmp(clock_first_frame,panel,sizeof(panel)));
    if (clock_step == 16) CHECK(memcmp(clock_first_frame,panel,sizeof(panel)) != 0);
    if (clock_step == 20)
    {
        uploading = true;
        blocked_transfers = transfers;
        memcpy(clock_first_frame,panel,sizeof(panel));
    }
    if (clock_step > 20 && clock_step <= 25)
        CHECK(transfers == blocked_transfers && !memcmp(clock_first_frame,panel,sizeof(panel)));
    if (clock_step == 25) uploading = false;
    if (clock_step == 26) CHECK(memcmp(clock_first_frame,panel,sizeof(panel)) != 0);
    if (clock_step == 35) {preferences.theme=1; ++preferences_generation;}
    if (clock_step == 40) {preferences.theme=0; ++preferences_generation;}
    if (clock_step == 41) memcpy(clock_first_frame,panel,sizeof(panel));
    if (clock_step == 55) CHECK(!memcmp(clock_first_frame,panel,sizeof(panel)));
    if (clock_step == 56)
    {
        CHECK(memcmp(clock_first_frame,panel,sizeof(panel)) != 0);
        longjmp(blocked,1);
    }
}

static void test_clock_text_scroll(void)
{
    /* Run the production scheduler with long fields and no changing wall-clock seconds. */
    strcpy(preferences.city,"ABCDEFGHIJKLMNOPQRS");
    http_body="{\"main\":{\"temp\":293,\"humidity\":73},\"wind\":{\"speed\":3.7},"
              "\"weather\":[{\"icon\":\"02d\",\"main\":\"Thunderstorm\",\"description\":\"clear\"}]}";
    http_length=strlen(http_body);
    CHECK(clock_ui_timer_init() == ESP_OK);
    CHECK(network_init() == ESP_OK);
    got_ip();
    start_synced_clock_services();
    strcpy(preferences.weather_key,"fixture-key");
    run_task("weather_http",seed_weather);
    CHECK(display_init() == ESP_OK);
    clock_ui_start();
    run_task("clock_display",clock_text_scenario);
    CHECK(clock_step==56);
}

static void clock_calendar_scenario(void)
{
    /* Simulate a time-server year correction at unchanged local h/m/s/day number. */
    ++clock_step;
    if (clock_step==1)
    {
        fake_local.tm_year=126;
        fake_local.tm_wday=4;
        fake_time+=31536000;
    }
    if (clock_step==2)
    {
        static uint16_t incremental[240*240];
        memcpy(incremental,panel,sizeof(panel));
        weather_snapshot_t current;
        weather_snapshot(&current);
        char address[20];
        network_address(address,sizeof(address));
        display_fill(0,0,240,240,0);
        if (preferences.theme==0)
            factory_draw_classic(&preferences,&fake_local,&current,0,0,true,true);
        else
            factory_draw_simple(&preferences,&fake_local,address,true,true,true);
        CHECK(!memcmp(incremental,panel,sizeof(panel)));
        longjmp(blocked,1);
    }
}

static void test_clock_calendar(unsigned theme)
{
    /* Exercise actual task dispatch after a real epoch jump, without a minute timer event. */
    preferences.theme=theme;
    preferences.date_format=2;
    fake_local=(struct tm){.tm_year=125,.tm_mon=0,.tm_mday=1,.tm_yday=0,
                          .tm_wday=3,.tm_hour=18,.tm_min=14,.tm_sec=7};
    fake_time=_mkgmtime64(&fake_local)-8*3600; /* CN fixture and epoch must describe the same date. */
    CHECK(clock_ui_timer_init()==ESP_OK);
    CHECK(network_init()==ESP_OK);
    got_ip();
    start_synced_clock_services();
    strcpy(preferences.weather_key,"fixture-key");
    run_task("weather_http",seed_weather);
    CHECK(display_init()==ESP_OK);
    clock_ui_start();
    run_task("clock_display",clock_calendar_scenario);
    CHECK(clock_step==2);
}

static void test_clock_calendar_classic(void)
{
    /* Run the classic date-jump task scenario in its own fresh process. */
    test_clock_calendar(0);
}

static void test_clock_calendar_simple(void)
{
    /* Run the simple date-jump task scenario in its own fresh process. */
    test_clock_calendar(1);
}

static void clock_timezone_scenario(void)
{
    /* Compare the real loop's incremental output with independently specified local dates. */
    static const struct {int hour, minute, second, daylight;} expected[] = {
        {0,59,59,0}, {2,0,59,1}, {3,0,59,1}, {1,59,59,0}};
    struct tm local = {.tm_year=126,.tm_mon=2,.tm_mday=29,.tm_yday=87,.tm_wday=0,
                       .tm_hour=expected[clock_step].hour,.tm_min=expected[clock_step].minute,
                       .tm_sec=expected[clock_step].second,.tm_isdst=expected[clock_step].daylight};
    static uint16_t incremental[240*240];
    memcpy(incremental, panel, sizeof(panel));
    weather_snapshot_t current;
    weather_snapshot(&current);
    char address[20];
    network_address(address, sizeof(address));
    display_fill(0,0,240,240,0);
    if (preferences.theme==0)
        factory_draw_classic(&preferences,&local,&current,0,0,true,true);
    else
        factory_draw_simple(&preferences,&local,address,true,true,true);
    CHECK(!memcmp(incremental,panel,sizeof(panel)));
    if (++clock_step == 4)
        longjmp(blocked,1);
    if (clock_step == 1) fake_time = 1774746059;
    if (clock_step == 2) {strcpy(preferences.country,"HU"); ++preferences_generation;}
    if (clock_step == 3) fake_time = 1774745999;
}
static void test_clock_timezone(unsigned theme)
{
    /* Observe DST, a same-epoch country change and backward correction with unchanged seconds.
     * The colon retains the factory timer phase; these jumps do not raise its second event. */
    preferences.theme=theme;
    strcpy(preferences.country,"GB");
    fake_time=1774745999;
    CHECK(clock_ui_timer_init()==ESP_OK);
    CHECK(network_init()==ESP_OK);
    got_ip();
    start_synced_clock_services();
    strcpy(preferences.weather_key,"fixture-key");
    run_task("weather_http",seed_weather);
    CHECK(display_init()==ESP_OK);
    clock_ui_start();
    run_task("clock_display",clock_timezone_scenario);
    CHECK(clock_step==4);
}
static void test_clock_timezone_classic(void)
{
    /* Run the classic timezone-jump scenario in a fresh process. */
    test_clock_timezone(0);
}
static void test_clock_timezone_simple(void)
{
    /* Run the simple timezone-jump scenario in a fresh process. */
    test_clock_timezone(1);
}

static void clock_sync_scenario(void)
{
    /* Keep time and the last station address visible during disconnect/reconnect. */
    struct tm expected = clock_step < 2
        ? (struct tm){.tm_year=125,.tm_mon=8,.tm_mday=19,.tm_hour=17,.tm_min=4,.tm_sec=40,.tm_wday=5}
        : (struct tm){.tm_year=124,.tm_mon=1,.tm_mday=29,.tm_hour=12,.tm_min=3,.tm_sec=40,
                      .tm_wday=4,.tm_yday=59};
    if (clock_step >= 3) expected.tm_min=clock_step+1;
    static uint16_t incremental[240*240];
    memcpy(incremental,panel,sizeof(panel));
    weather_snapshot_t current;
    weather_snapshot(&current);
    display_fill(0,0,240,240,0);
    if (preferences.theme==0)
        factory_draw_classic(&preferences,&expected,&current,0,0,true,true);
    else
        factory_draw_simple(&preferences,&expected,"10.0.2.15",true,true,true);
    if (memcmp(incremental,panel,sizeof(panel)))
    {
        unsigned differences=0;
        for (unsigned i=0;i<240*240;++i) if(incremental[i]!=panel[i]) ++differences;
        fprintf(stderr,"Sync frame step %u theme %u differences %u\n",clock_step,preferences.theme,differences);
    }
    CHECK(!memcmp(incremental,panel,sizeof(panel)));
    if (clock_step == 3)
    {
        char address[20];
        CHECK(services_time_synced() && !network_connected() && !network_ap_active());
        network_address(address,sizeof(address));
        CHECK(!strcmp(address,"10.0.2.15"));
    }
    CHECK(services_time_synced() == (clock_step >= 2));
    if (++clock_step == 5)
        longjmp(blocked,1);
    if (clock_step == 1)
    {
        struct tm utc={.tm_year=124,.tm_mon=1,.tm_mday=29,.tm_hour=4,.tm_min=3,.tm_sec=40};
        fake_time=_mkgmtime64(&utc);
    }
    if (clock_step == 2)
    {
        struct timeval event={.tv_sec=fake_time};
        sntp_callback(&event); /* Epoch is unchanged; only actual synchronization becomes valid. */
    }
    if (clock_step == 3) {fake_time+=60; disconnected();}
    if (clock_step == 4) {fake_time+=60; got_ip();}
}
static void test_clock_sync(unsigned theme)
{
    /* A future year or initialized client must not authorize time before the first reply. */
    preferences.theme=theme;
    preferences.wifi_mode=1;
    strcpy(preferences.ssid,"fixture");
    struct tm future={.tm_year=130,.tm_mon=0,.tm_mday=1};
    fake_time=_mkgmtime64(&future);
    CHECK(clock_ui_timer_init()==ESP_OK);
    tick_clock(181); /* Complete the actual station startup before comparing clock frames. */
    CHECK(network_init()==ESP_OK);
    got_ip();
    services_start();
    run_task("time_sync",stop_time_worker_once);
    CHECK(sntp_inits==1 && !services_time_synced());
    strcpy(preferences.weather_key,"fixture-key");
    run_task("weather_http",seed_weather);
    CHECK(display_init()==ESP_OK);
    clock_ui_start();
    run_task("clock_display",clock_sync_scenario);
}
static void test_clock_sync_classic(void)
{
    /* Run classic first-sync and offline validity in a fresh process. */
    test_clock_sync(0);
}
static void test_clock_sync_simple(void)
{
    /* Run simple first-sync and offline validity in a fresh process. */
    test_clock_sync(1);
}

static void offline_dst_scenario(void)
{
    /* Cross the GB spring gap while STA is down, then recover without losing time. */
    struct tm expected={.tm_year=126,.tm_mon=2,.tm_mday=29,.tm_hour=clock_step?2:0,
                        .tm_min=clock_step==0?59:clock_step==2?1:0,
                        .tm_sec=clock_step?2:58,.tm_wday=0,.tm_yday=87,.tm_isdst=clock_step!=0};
    uint16_t observed[240*240];
    memcpy(observed,panel,sizeof(panel));
    weather_snapshot_t weather;weather_snapshot(&weather);
    display_fill(0,0,240,240,0);
    if (preferences.theme==0)
        /* 181 startup + 22 timer ticks crosses the next 3-second label event. */
        factory_draw_classic(&preferences,&expected,&weather,clock_step==2?1:0,0,true,true);
    else if (preferences.theme==1)
        factory_draw_simple(&preferences,&expected,"10.0.2.15",true,true,true);
    else {
        factory_draw_dial(&expected,"10.0.2.15",true);
        if (clock_step) factory_draw_dial(&expected,"10.0.2.15",false);
    }
    if (memcmp(observed,panel,sizeof(panel)))
        fprintf(stderr,"Offline DST frame step %u theme %u did not match\n",clock_step,preferences.theme);
    CHECK(!memcmp(observed,panel,sizeof(panel)));
    char address[20];network_address(address,sizeof(address));
    CHECK(!strcmp(address,"10.0.2.15") && services_time_synced());
    if (clock_step==1) CHECK(!network_connected() && !network_ap_active());
    if (++clock_step==3) longjmp(blocked,1);
    fake_time+=clock_step==1?4:60;
    tick_clock(11); /* A real pending second event is required by the dial. */
    if (clock_step==1) disconnected();else got_ip();
}
static void test_offline_dst(unsigned theme)
{
    /* Compose the actual time conversion, reconnect state and renderer during an offline DST edge. */
    preferences.theme=theme;preferences.wifi_mode=1;
    strcpy(preferences.ssid,"fixture");strcpy(preferences.country,"GB");
    struct tm utc={.tm_year=126,.tm_mon=2,.tm_mday=29,.tm_hour=0,.tm_min=59,.tm_sec=58};
    fake_time=_mkgmtime64(&utc);
    CHECK(clock_ui_timer_init()==ESP_OK);tick_clock(181);
    CHECK(network_init()==ESP_OK);got_ip();start_synced_clock_services();
    strcpy(preferences.weather_key,"fixture-key");run_task("weather_http",seed_weather);
    CHECK(display_init()==ESP_OK);clock_ui_start();
    run_task("clock_display",offline_dst_scenario);
}
static void test_offline_dst_classic(void)
{
    /* Keep the classic time/date current while disconnected. */
    test_offline_dst(0);
}
static void test_offline_dst_simple(void)
{
    /* Keep simple digits/Sunday current while disconnected. */
    test_offline_dst(1);
}
static void test_offline_dst_dial(void)
{
    /* Keep analog hands current on timer events while disconnected. */
    test_offline_dst(3);
}
static void offline_photo_scenario(void)
{
    /* Finish every fade step after a lost link, including photo selection and configured duty. */
    static const unsigned expected[]={2457,4914,8191,4914,2457,4095};
    CHECK(duty==expected[clock_step]);
    CHECK(photo_draws==(clock_step>=2));
    if (clock_step) CHECK(!network_connected() && services_time_synced());
    if (++clock_step==6) longjmp(blocked,1);
    if (clock_step==1) disconnected();
    tick_clock(1);
}
static void test_offline_photo(void)
{
    /* Exercise the real coordinator and fade algorithm, with only the photo blit stubbed. */
    preferences.theme=2;preferences.photo_mask=1;preferences.photo_size[0]=100;
    preferences.day_level=500;preferences.wifi_mode=1;strcpy(preferences.ssid,"fixture");
    CHECK(clock_ui_timer_init()==ESP_OK);tick_clock(181);
    CHECK(network_init()==ESP_OK);got_ip();start_synced_clock_services();
    strcpy(preferences.weather_key,"fixture-key");run_task("weather_http",seed_weather);
    CHECK(display_init()==ESP_OK && backlight_init()==ESP_OK);clock_ui_start();
    run_task("clock_display",offline_photo_scenario);
}

static void weather_pending_clock_scenario(void)
{
    /* Advance a synchronized minute while the actual weather request remains pending. */
    struct tm expected={.tm_year=126,.tm_mon=0,.tm_mday=1,.tm_hour=12,
                        .tm_min=3+(int)clock_step,.tm_sec=40,.tm_wday=4};
    uint16_t observed[240*240];
    memcpy(observed,panel,sizeof(panel));
    weather_snapshot_t weather;weather_snapshot(&weather);
    CHECK(weather.valid && http_calls==1 && network_connected());
    if(clock_step) CHECK(weather_request_active());
    display_fill(0,0,240,240,0);
    if(preferences.theme==0)
        factory_draw_classic(&preferences,&expected,&weather,clock_step==2?1:0,0,true,true);
    else if(preferences.theme==1)
        factory_draw_simple(&preferences,&expected,"10.0.2.15",true,true,true);
    else {
        factory_draw_dial(&expected,"10.0.2.15",true);
        if(clock_step) factory_draw_dial(&expected,"10.0.2.15",false);
    }
    CHECK(!memcmp(observed,panel,sizeof(panel)));
    if(++clock_step==3) longjmp(blocked,1);
    weather_request_update();
    fake_time+=60;
    tick_clock(11);
}

static void test_weather_pending_clock(unsigned theme)
{
    /* A queued worker request must not suspend clock rendering or cache snapshots. */
    preferences.theme=theme;preferences.date_format=2;preferences.wifi_mode=1;
    strcpy(preferences.ssid,"fixture");
    struct tm utc={.tm_year=126,.tm_mon=0,.tm_mday=1,.tm_hour=4,.tm_min=3,.tm_sec=40};
    fake_time=_mkgmtime64(&utc);
    CHECK(clock_ui_timer_init()==ESP_OK);tick_clock(181);
    CHECK(network_init()==ESP_OK);got_ip();start_synced_clock_services();
    strcpy(preferences.weather_key,"fixture-key");run_task("weather_http",seed_weather);
    CHECK(display_init()==ESP_OK);clock_ui_start();
    run_task("clock_display",weather_pending_clock_scenario);
}
static void test_weather_pending_classic(void)
{
    /* Require full classic clock frames while weather work is queued. */
    test_weather_pending_clock(0);
}
static void test_weather_pending_simple(void)
{
    /* Require full simple clock frames while weather work is queued. */
    test_weather_pending_clock(1);
}
static void test_weather_pending_dial(void)
{
    /* Require advancing analog hands while weather work is queued. */
    test_weather_pending_clock(3);
}
static void weather_pending_photo_scenario(void)
{
    /* Finish all six photo-fade actions without waiting for the weather worker. */
    static const unsigned expected[]={2457,4914,8191,4914,2457,4095};
    CHECK(duty==expected[clock_step] && network_connected());
    CHECK(photo_draws==(clock_step>=2));
    if(clock_step) CHECK(weather_request_active());
    if(++clock_step==6) longjmp(blocked,1);
    weather_request_update();tick_clock(1);
}
static void test_weather_pending_photo(void)
{
    /* Verify weather waiting cannot hold the backlight in an unfinished fade. */
    preferences.theme=2;preferences.photo_mask=1;preferences.photo_size[0]=100;
    preferences.day_level=500;preferences.wifi_mode=1;strcpy(preferences.ssid,"fixture");
    CHECK(clock_ui_timer_init()==ESP_OK);tick_clock(181);
    CHECK(network_init()==ESP_OK);got_ip();start_synced_clock_services();
    strcpy(preferences.weather_key,"fixture-key");run_task("weather_http",seed_weather);
    CHECK(display_init()==ESP_OK && backlight_init()==ESP_OK);clock_ui_start();
    run_task("clock_display",weather_pending_photo_scenario);
}

int main(int argc, char **argv)
{
    /* Select a fresh-process scenario and save a machine-readable result only after success. */
    CHECK(argc == 3);
    memset(&preferences, 0, sizeof(preferences));
    preferences.version = TV_SETTINGS_VERSION;
    preferences.wifi_mode = 2;
    preferences.photo_seconds = 5;
    strcpy(preferences.city, "Shenzhen");
    strcpy(preferences.country, "CN");
    strcpy(preferences.ntp, "fixture.invalid");
    const struct
    {
        const char *name;
        void (*run)(void);
    } cases[] = {{"wifi_setup", test_wifi_setup},
                 {"wifi_reconnect_scan", test_wifi_reconnect},
                 {"wifi_open_station", test_wifi_open},
                 {"wifi_pending_dhcp", test_wifi_fallback},
                 {"wifi_failure_recovered", test_wifi_failure_recovered},
                 {"wifi_failed_retries", test_wifi_failed_retries},
                 {"restart_persistence_failure", test_restart_failure},
                 {"wifi_allocation_failure", test_wifi_allocation_failure},
                 {"wifi_station_allocation_failure", test_wifi_station_allocation_failure},
                 {"wifi_task_failure", test_wifi_task_failure},
                 {"weather_worker", test_weather_worker},
                 {"time_worker", test_time_worker},
                 {"time_zone_boundaries", test_time_zone_boundaries},
                 {"regional_time_worker", test_regional_time_worker},
                 {"regional_weather_worker", test_regional_weather_worker},
                 {"backlight_schedule", test_backlight},
                 {"display_protocol_clipping", test_display},
                 {"ui_transitions", test_ui_transitions},
                 {"text_field_windows", test_text_fields},
                 {"weather_field_cleanup", test_weather_field_cleanup},
                 {"clock_coordinator", test_clock_coordinator},
                 {"clock_first_digital_brightness", test_first_digital_brightness},
                 {"clock_photo_idle_brightness", test_photo_idle_brightness},
                 {"clock_photo_reselect", test_photo_reselect},
                 {"clock_photo_active_reselect", test_photo_active_reselect},
                 {"clock_startup_ready_classic", test_startup_ready_classic},
                 {"clock_startup_ready_simple", test_startup_ready_simple},
                 {"clock_startup_ready_photo", test_startup_ready_photo},
                 {"clock_startup_ready_dial", test_startup_ready_dial},
                 {"clock_startup_wait_sync", test_startup_wait_sync},
                 {"clock_startup_wait_address", test_startup_wait_address},
                 {"clock_offline_dst_classic", test_offline_dst_classic},
                 {"clock_offline_dst_simple", test_offline_dst_simple},
                 {"clock_offline_dst_dial", test_offline_dst_dial},
                 {"clock_offline_photo", test_offline_photo},
                 {"clock_weather_pending_classic", test_weather_pending_classic},
                 {"clock_weather_pending_simple", test_weather_pending_simple},
                 {"clock_weather_pending_dial", test_weather_pending_dial},
                 {"clock_weather_pending_photo", test_weather_pending_photo},
                 {"timer_driver_failures", test_timer_driver_failures},
                 {"clock_animation_selection", test_clock_animation_selection},
                 {"clock_text_scroll", test_clock_text_scroll},
                 {"clock_calendar_classic", test_clock_calendar_classic},
                 {"clock_calendar_simple", test_clock_calendar_simple},
                 {"clock_timezone_classic", test_clock_timezone_classic},
                 {"clock_timezone_simple", test_clock_timezone_simple},
                 {"clock_sync_classic", test_clock_sync_classic},
                 {"clock_sync_simple", test_clock_sync_simple}};
    bool found = false;
    for (unsigned i = 0; i < sizeof(cases) / sizeof(cases[0]); ++i)
        if (!strcmp(argv[1], cases[i].name))
        {
            found = true;
            cases[i].run();
            break;
        }
    CHECK(found);
    FILE *file = fopen(argv[2], "wb");
    CHECK(file != NULL);
    fprintf(file, "{\"case\":\"%s\",\"passed\":true,\"checks\":%u}\n", argv[1], checks);
    fclose(file);
    printf("PASS %s: %u checks\n", argv[1], checks);
    return 0;
}
