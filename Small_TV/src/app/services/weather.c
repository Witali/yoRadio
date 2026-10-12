#include "services.h"
#include "settings.h"
#include "network.h"
#include "cJSON.h"
#include <ctype.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "esp_crt_bundle.h"
#include "esp_http_client.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"

static SemaphoreHandle_t weather_mutex;
static weather_snapshot_t cached_weather;
static TaskHandle_t weather_task_handle;
typedef struct {char *body; size_t length; bool overflow;} weather_response_t;

void weather_snapshot(weather_snapshot_t *out)
{
    xSemaphoreTake(weather_mutex,portMAX_DELAY); *out=cached_weather; xSemaphoreGive(weather_mutex);
}

void weather_request_update(void) {if (weather_task_handle) xTaskNotifyGive(weather_task_handle);}

static esp_err_t weather_http_event(esp_http_client_event_t *event)
{
    weather_response_t *response=event->user_data;
    if (event->event_id==HTTP_EVENT_ON_DATA && event->data_len>0) {
        if ((size_t)event->data_len>8192-response->length) {response->overflow=true; return ESP_ERR_INVALID_SIZE;}
        memcpy(response->body+response->length,event->data,event->data_len); response->length+=event->data_len;
        response->body[response->length]=0;
    }
    return ESP_OK;
}

static void url_escape(const char *source,char *target)
{
    static const char hex[]="0123456789ABCDEF";
    for (; *source; ++source) {
        unsigned char c=*source;
        if (isalnum(c) || c=='-' || c=='_' || c=='.' || c=='~') *target++=c;
        else {*target++='%'; *target++=hex[c>>4]; *target++=hex[c&15];}
    }
    *target=0;
}

static bool number(const cJSON *object,const char *name,double minimum,double maximum,double *value)
{
    const cJSON *item=cJSON_GetObjectItemCaseSensitive(object,name);
    if (!cJSON_IsNumber(item) || !isfinite(item->valuedouble) || item->valuedouble<minimum || item->valuedouble>maximum) return false;
    *value=item->valuedouble; return true;
}

static esp_err_t fetch_weather(const tv_settings_t *s,weather_snapshot_t *out)
{
    char city[193],key[193],url[512]; url_escape(s->city,city); url_escape(s->weather_key,key);
    snprintf(url,sizeof(url),"https://api.openweathermap.org/data/2.5/weather?q=%s,%s&appid=%s&units=metric",city,s->country,key);
    weather_response_t response={.body=calloc(1,8193)};
    if (!response.body) return ESP_ERR_NO_MEM;
    esp_http_client_config_t config={.url=url,.timeout_ms=15000,.buffer_size=1024,.buffer_size_tx=1024,
        .crt_bundle_attach=esp_crt_bundle_attach,.disable_auto_redirect=true,.event_handler=weather_http_event,.user_data=&response};
    esp_http_client_handle_t client=esp_http_client_init(&config);
    esp_err_t result=client?esp_http_client_perform(client):ESP_ERR_NO_MEM;
    if (client && (esp_http_client_get_status_code(client)!=200 || response.overflow)) result=ESP_FAIL;
    if (client) esp_http_client_cleanup(client);
    cJSON *root=result==ESP_OK?cJSON_ParseWithLength(response.body,response.length):NULL;
    if (root) {
        const cJSON *main=cJSON_GetObjectItemCaseSensitive(root,"main"),*wind=cJSON_GetObjectItemCaseSensitive(root,"wind");
        const cJSON *weather=cJSON_GetArrayItem(cJSON_GetObjectItemCaseSensitive(root,"weather"),0);
        const cJSON *icon=cJSON_GetObjectItemCaseSensitive(weather,"icon"),*description=cJSON_GetObjectItemCaseSensitive(weather,"description");
        double temperature,humidity,speed,zone;
        if (number(main,"temp",-100,100,&temperature) && number(main,"humidity",0,100,&humidity) && number(wind,"speed",0,150,&speed) &&
            number(root,"timezone",-50400,50400,&zone) && cJSON_IsString(icon) && strlen(icon->valuestring)==3) {
            memset(out,0,sizeof(*out)); out->valid=true; out->temperature_c=temperature; out->humidity=humidity; out->wind_mps=speed; out->timezone_seconds=zone;
            memcpy(out->icon,icon->valuestring,4);
            strcpy(out->city,s->city); strcpy(out->country,s->country);
            if (cJSON_IsString(description)) snprintf(out->description,sizeof(out->description),"%s",description->valuestring);
        } else result=ESP_ERR_INVALID_RESPONSE;
    } else if (result==ESP_OK) result=ESP_ERR_INVALID_RESPONSE;
    cJSON_Delete(root); free(response.body); return result;
}

static void weather_task(void *unused)
{
    (void)unused;
    int64_t next_fetch=0; char last_city[65]="",last_country[3]="",last_key[65]="";
    for (;;) {
        tv_settings_t s; settings_snapshot(&s);
        if (strcmp(last_city,s.city) || strcmp(last_country,s.country) || strcmp(last_key,s.weather_key)) {
            strcpy(last_city,s.city); strcpy(last_country,s.country); strcpy(last_key,s.weather_key); next_fetch=0;
            xSemaphoreTake(weather_mutex,portMAX_DELAY); cached_weather.valid=false; ++cached_weather.generation; xSemaphoreGive(weather_mutex);
        }
        struct tm local; time_t now=time(NULL); localtime_r(&now,&local);
        if (network_connected() && s.weather_key[0] && local.tm_year>=125 && esp_timer_get_time()>=next_fetch) {
            weather_snapshot_t fresh;
            if (fetch_weather(&s,&fresh)==ESP_OK) {
                tv_settings_t current; settings_snapshot(&current);
                if (!strcmp(current.city,s.city) && !strcmp(current.country,s.country) && !strcmp(current.weather_key,s.weather_key)) {
                    xSemaphoreTake(weather_mutex,portMAX_DELAY); fresh.generation=cached_weather.generation+1; cached_weather=fresh; xSemaphoreGive(weather_mutex);
                }
                next_fetch=esp_timer_get_time()+1800000000LL;
            } else next_fetch=esp_timer_get_time()+60000000;
        }
        if (ulTaskNotifyTake(pdTRUE,pdMS_TO_TICKS(1000))) next_fetch=0;
    }
}

void weather_start(void)
{
    weather_mutex=xSemaphoreCreateMutex(); configASSERT(weather_mutex);
    configASSERT(xTaskCreate(weather_task,"weather_https",8192,NULL,1,&weather_task_handle)==pdPASS);
}
