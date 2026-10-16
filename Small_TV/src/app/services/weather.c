#include "services.h"
#include "settings.h"
#include "network.h"
#include "cJSON.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdatomic.h>
#include "esp_crt_bundle.h"
#include "esp_http_client.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"

static SemaphoreHandle_t weather_mutex;
static weather_snapshot_t cached_weather;
static TaskHandle_t weather_task_handle;
enum
{
    REQUEST_RUNNING = 1,
    REQUEST_PENDING = 2
};
static atomic_uint request_state;
typedef struct
{
    char *body;
    size_t length;
    bool overflow;
} weather_response_t;

void weather_snapshot(weather_snapshot_t *out)
{
    /* Copy a consistent weather-cache snapshot under its mutex. */

    xSemaphoreTake(weather_mutex, portMAX_DELAY);
    *out = cached_weather;
    xSemaphoreGive(weather_mutex);
}

void weather_request_update(void)
{
    /* Wake the weather worker after location/key settings change. */
    if (weather_task_handle)
    {
        atomic_fetch_or(&request_state, REQUEST_PENDING);
        xTaskNotifyGive(weather_task_handle);
    }
}
bool weather_request_active(void)
{
    /* Report pending/running worker work for request coalescing and retry pacing. */
    return atomic_load(&request_state) != 0;
}

static esp_err_t weather_http_event(esp_http_client_event_t *event)
{
    /* Collect a bounded HTTP response body without exposing its request credentials. */

    weather_response_t *response = event->user_data;
    if (event->event_id == HTTP_EVENT_ON_DATA && event->data_len > 0)
    {
        if ((size_t)event->data_len > 8192 - response->length)
        {
            response->overflow = true;
            return ESP_ERR_INVALID_SIZE;
        }
        memcpy(response->body + response->length, event->data, event->data_len);
        response->length += event->data_len;
        response->body[response->length] = 0;
    }
    return ESP_OK;
}

static void url_escape(const char *source, char *target)
{
    /* Encode every non-ASCII URI byte, independent of the current C locale.
     * FIXED_FACTORY: 0x42010864 puts raw UTF-8 city bytes into the URL; its
     * client initialization can fail and the unguarded perform call then faults. */

    static const char hex[] = "0123456789ABCDEF";
    for (; *source; ++source)
    {
        unsigned char c = *source;
        if ((c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') ||
            (c >= '0' && c <= '9') || c == '-' || c == '_' || c == '.' || c == '~')
            *target++ = c;
        else
        {
            *target++ = '%';
            *target++ = hex[c >> 4];
            *target++ = hex[c & 15];
        }
    }
    *target = 0;
}

static esp_err_t fetch_weather(const tv_settings_t *s, weather_snapshot_t *out)
{
    /* Fetch the factory HTTP/Kelvin endpoint and decode its bounded response.
     * FIXED_FACTORY: 0x42010864 parses JSON even after an HTTP error such as 503.
     * Require HTTP 200 and a complete bounded body; weather_task retains the
     * last successful cache when a request for the same location fails.
     * FIXED_FACTORY: 0x42010988 passes a possibly NULL client into perform;
     * retain the initialization check so invalid URLs/allocation cannot crash. */

    char city[193], key[193], url[512];
    url_escape(s->city, city);
    url_escape(s->weather_key, key);
    snprintf(url, sizeof(url), "http://api.openweathermap.org/data/2.5/weather?q=%s,%s&appid=%s",
             city, s->country, key);
    weather_response_t response = {.body = calloc(1, 8193)};
    if (!response.body)
        return ESP_ERR_NO_MEM;
    esp_http_client_config_t config = {.url = url,
                                       .timeout_ms = 10000,
                                       .buffer_size = 1024,
                                       .buffer_size_tx = 1024,
                                       .disable_auto_redirect = true,
                                       .event_handler = weather_http_event,
                                       .user_data = &response};
    esp_http_client_handle_t client = esp_http_client_init(&config);
    esp_err_t result = client ? esp_http_client_perform(client) : ESP_ERR_NO_MEM;
    if (client && (esp_http_client_get_status_code(client) != 200 || response.overflow))
        result = ESP_FAIL;
    if (client)
        esp_http_client_cleanup(client);
    if (result == ESP_OK && !weather_parse_response(response.body, response.length, s, out))
        result = ESP_ERR_INVALID_RESPONSE;
    free(response.body);
    return result;
}

static void weather_task(void *unused)
{
    /* Execute requests scheduled by the factory main loop and reject stale results. */

    (void)unused;
    char last_city[65] = "", last_country[TV_COUNTRY_BYTES] = "", last_key[65] = "";
    for (;;)
    {
        ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
        atomic_fetch_or(&request_state, REQUEST_RUNNING);
        atomic_fetch_and(&request_state, ~REQUEST_PENDING);
        tv_settings_t s;
        settings_snapshot(&s);
        if (strcmp(last_city, s.city) || strcmp(last_country, s.country) ||
            strcmp(last_key, s.weather_key))
        {
            strcpy(last_city, s.city);
            strcpy(last_country, s.country);
            strcpy(last_key, s.weather_key);
            xSemaphoreTake(weather_mutex, portMAX_DELAY);
            cached_weather.valid = false;
            ++cached_weather.generation;
            xSemaphoreGive(weather_mutex);
        }
        if (network_connected() && s.weather_key[0])
        {
            weather_snapshot_t fresh;
            esp_err_t fetched = fetch_weather(&s, &fresh);
            if (fetched == ESP_OK)
            {
                tv_settings_t current;
                settings_snapshot(&current);
                if (!strcmp(current.city, s.city) && !strcmp(current.country, s.country) &&
                    !strcmp(current.weather_key, s.weather_key))
                {
                    xSemaphoreTake(weather_mutex, portMAX_DELAY);
                    fresh.generation = cached_weather.generation + 1;
                    cached_weather = fresh;
                    xSemaphoreGive(weather_mutex);
                }
            }
        }
        atomic_fetch_and(&request_state, ~REQUEST_RUNNING);
    }
}

void weather_start(void)
{
    /* Initialize the cache mutex and start the weather worker. */

    weather_mutex = xSemaphoreCreateMutex();
    configASSERT(weather_mutex);
    configASSERT(xTaskCreate(weather_task, "weather_http", 8192, NULL, 1, &weather_task_handle) ==
                 pdPASS);
}
