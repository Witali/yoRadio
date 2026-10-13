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
static bool uploading, in_alarm;
static time_t fake_time = 1791885600;
static struct tm fake_local = {
    .tm_year = 126, .tm_mon = 9, .tm_mday = 13, .tm_wday = 2, .tm_hour = 12};

void settings_snapshot(tv_settings_t *out)
{
    *out = preferences;
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
    return allocation_failure ? NULL : &sta;
}
esp_netif_t *esp_netif_create_default_wifi_ap(void)
{
    return &ap;
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
        sta_config = *config;
    else
    {
        assert(interface == WIFI_IF_AP);
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
static void got_ip(void)
{
    assert(event_callback);
    event_callback(NULL, IP_EVENT, IP_EVENT_STA_GOT_IP, NULL);
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
    stop_after = 22;
    run_task("wifi_fallback", stop_at_delay);
    CHECK(task_count == 1 && restarts == 0 && preferences.wifi_mode == 2);
}
static void test_wifi_reconnect(void)
{
    /* Four station retries, readiness after DHCP, retry reset and scan-event suppression. */
    station_start();
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
}
static void test_wifi_open(void)
{
    /* Open station credentials must select open authentication and no password. */
    preferences.wifi_mode = 1;
    strcpy(preferences.ssid, "open-fixture");
    preferences.password[0] = 0;
    CHECK(network_init() == ESP_OK);
    CHECK(sta_config.sta.threshold.authmode == WIFI_AUTH_OPEN && !sta_config.sta.password[0]);
}
static void test_wifi_fallback(void)
{
    /* The safety timeout changes saved mode only after 18 disconnected seconds. */
    station_start();
    stop_after = 18;
    run_task("wifi_fallback", stop_at_delay);
    CHECK(preferences.wifi_mode == 1 && task_count == 1);
    steps = 0;
    stop_after = 19;
    run_task("wifi_fallback", stop_at_delay);
    CHECK(preferences.wifi_mode == 2 && task_count == 2);
    CHECK(!strcmp(tasks[1].name, "restart"));
    stop_after = 1;
    steps = 0;
    run_task("restart", stop_at_delay);
    CHECK(restarts == 0);
    run_task("restart", NULL);
    CHECK(restarts == 1 && flushes == 1);
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
    allocation_failure = true;
    CHECK(network_init() == ESP_ERR_NO_MEM && task_count == 0);
}
static void test_wifi_task_failure(void)
{
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
    strcpy(preferences.city, "New York/测试");
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
        CHECK(!strcmp(timezone, "GMT0BST") && sntp_inits == 0);
        got_ip();
        preferences.ntp[0] = 0;
    }
    if (time_step == 2)
    {
        CHECK(sntp_inits == 1 && !strcmp(servers[0], "ntp1.aliyun.com") &&
              !strcmp(servers[1], "cn.pool.ntp.org") && !strcmp(servers[2], "pool.ntp.org"));
        strcpy(preferences.country, "HU");
        strcpy(preferences.city, "Budapest");
    }
    if (time_step == 3)
    {
        CHECK(!strcmp(timezone, "CET-1CEST") && sntp_inits == 1 && timezone_updates == 2);
        strcpy(preferences.ntp, "fixture.invalid");
        sntp_result = ESP_FAIL;
    }
    if (time_step == 4)
    {
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
        CHECK(sntp_inits == 3);
        strcpy(preferences.country, "ZZ");
    }
    if (time_step == 7)
    {
        CHECK(!strcmp(timezone, "GMT0BST") && timezone_updates == 3 && sntp_inits == 3);
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

static esp_err_t driver_result = ESP_OK;
static ledc_timer_config_t ledc_timer;
static ledc_channel_config_t ledc_channel;
static unsigned duty, duty_updates;
esp_err_t ledc_timer_config(const ledc_timer_config_t *config)
{
    ledc_timer = *config;
    return driver_result;
}
esp_err_t ledc_channel_config(const ledc_channel_config_t *config)
{
    ledc_channel = *config;
    return ESP_OK;
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
    driver_result = ESP_OK;
    CHECK(backlight_init() == ESP_OK);
    CHECK(ledc_timer.freq_hz == 1000 && ledc_timer.duty_resolution == LEDC_TIMER_13_BIT &&
          ledc_channel.gpio_num == 18 && ledc_channel.duty == 819);
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
    return ESP_OK;
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
static void clock_scenario(void)
{
    /* Advance the real clock task through startup, each theme, blocked upload and weather event. */
    ++clock_step;
    if (clock_step < 182)
        CHECK(animation_calls == 0 && photo_draws == 0);
    if (clock_step == 182)
        CHECK(animation_calls == 1);
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
        CHECK(transfers == blocked_transfers);
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
    weather_start();
    strcpy(preferences.weather_key, "fixture-key");
    run_task("weather_http", seed_weather);
    CHECK(display_init() == ESP_OK);
    clock_ui_start();
    run_task("clock_display", clock_scenario);
    CHECK(clock_step == 302 && photo_draws >= 1);
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

int main(int argc, char **argv)
{
    /* Select a fresh-process scenario and save a machine-readable result only after success. */
    CHECK(argc == 3);
    memset(&preferences, 0, sizeof(preferences));
    preferences.version = 1;
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
                 {"wifi_fallback_timeout", test_wifi_fallback},
                 {"wifi_failed_retries", test_wifi_failed_retries},
                 {"restart_persistence_failure", test_restart_failure},
                 {"wifi_allocation_failure", test_wifi_allocation_failure},
                 {"wifi_task_failure", test_wifi_task_failure},
                 {"weather_worker", test_weather_worker},
                 {"time_worker", test_time_worker},
                 {"backlight_schedule", test_backlight},
                 {"display_protocol_clipping", test_display},
                 {"ui_transitions", test_ui_transitions},
                 {"clock_coordinator", test_clock_coordinator},
                 {"timer_driver_failures", test_timer_driver_failures}};
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
