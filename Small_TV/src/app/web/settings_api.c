#include "web.h"
#include "settings.h"
#include "network.h"
#include "services.h"
#include <ctype.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct
{
    const char *get, *post, *key;
    size_t offset;
    int min, max;
} integer_route_t;
#define FIELD(get, post, key, field, min, max)                                                     \
    {get, post, key, offsetof(tv_settings_t, field), min, max}
static const integer_route_t integers[] = {
    FIELD("/getclocktype", "/setclocktype", "clocktype", theme, 0, 3),
    FIELD("/getgifvalue", "/setgifvalue", "gif", animation, 0, 4),
    FIELD("/GetTimeModeValue", "/SetTimeModeValue", "timemode", date_format, 0, 2),
    FIELD("/GetNightStartTime", "/SetNightStartTime", "StartTime", night_start, 18, 23),
    FIELD("/GetNightStopTime", "/SetNightStopTime", "StopTime", night_stop, 5, 12),
    FIELD("/get_display_time", "/set_display_time", "display_time", photo_seconds, 3, 60),
};
static const struct
{
    const char *key;
    size_t offset;
} switches[] = {{"tempUnit", offsetof(tv_settings_t, fahrenheit)},
                {"hourFormat", offsetof(tv_settings_t, hour12)},
                {"mileDisplay", offsetof(tv_settings_t, miles)},
                {"timeSync", offsetof(tv_settings_t, browser_time)},
                {"nightmode", offsetof(tv_settings_t, night_mode)}};

esp_err_t web_settings_get(httpd_req_t *req)
{
    /* Return the requested setting using its original response shape.
     * FIXED_RECONSTRUCTION: /get_display_time must return the displaytime JSON
     * field, as in 0x4200e7b6, rather than a scalar that breaks the stock page. */

    tv_settings_t s;
    settings_snapshot(&s);
    cJSON *result = NULL;
    for (unsigned i = 0; i < sizeof(integers) / sizeof(integers[0]); ++i)
        if (!strcmp(req->uri, integers[i].get))
        {
            unsigned value = *((const uint8_t *)&s + integers[i].offset);
            if (!strcmp(req->uri, "/get_display_time"))
            {
                result = cJSON_CreateObject();
                cJSON_AddNumberToObject(result, "displaytime", value);
                return web_json(req, result);
            }
            char text[16];
            snprintf(text, sizeof(text), "%u", value);
            return httpd_resp_send(req, text, HTTPD_RESP_USE_STRLEN);
        }
    result = cJSON_CreateObject();
    if (!strcmp(req->uri, "/getsettings"))
    {
        for (unsigned i = 0; i < sizeof(switches) / sizeof(switches[0]); ++i)
            cJSON_AddNumberToObject(result, switches[i].key,
                                    *((const uint8_t *)&s + switches[i].offset));
    }
    else if (!strcmp(req->uri, "/get_clock_colors"))
    {
        for (unsigned i = 0; i < 3; ++i)
        {
            char name[8], color[8];
            snprintf(name, sizeof(name), "color%u", i);
            snprintf(color, sizeof(color), "#%06lx",
                     (unsigned long)rgb888_from_rgb565(s.colors[i]));
            cJSON_AddStringToObject(result, name, color);
        }
    }
    else if (!strcmp(req->uri, "/get_checkbox_state"))
    {
        for (unsigned i = 0; i < PHOTO_COUNT; ++i)
        {
            char name[20];
            snprintf(name, sizeof(name), "file%u_switch", i + 1);
            cJSON_AddBoolToObject(result, name, s.photo_mask & (1u << i));
        }
    }
    else if (!strcmp(req->uri, "/get_led_brightness") || !strcmp(req->uri, "/get_night_brightness"))
    {
        unsigned level = !strcmp(req->uri, "/get_led_brightness") ? s.day_level : s.night_level;
        cJSON_AddNumberToObject(result, "brightness", 100 - level / 10);
    }
    else
    {
        cJSON_Delete(result);
        return web_error(req, "Unknown setting");
    }
    return web_json(req, result);
}

static bool copy_string(const cJSON *object, const char *key, char *out, size_t capacity)
{
    /* Copy a JSON string only if it fits the destination including its terminator. */

    const cJSON *value = cJSON_GetObjectItemCaseSensitive(object, key);
    if (!cJSON_IsString(value) || strlen(value->valuestring) >= capacity)
        return false;
    strcpy(out, value->valuestring);
    return true;
}

static bool read_brightness(httpd_req_t *req, const char *key, unsigned *out)
{
    /* Parse the original form-encoded brightness percentage.
     * FIXED_RECONSTRUCTION: accept both 0 and 100 percent; rejecting the upper
     * endpoint made the web slider unable to select full brightness. */

    char *body = web_body(req, 128);
    if (!body)
        return false;
    char value[8];
    bool valid = false;
    if (!memchr(body, 0, req->content_len) &&
        httpd_query_key_value(body, key, value, sizeof(value)) == ESP_OK && *value)
    {
        valid = true;
        for (const char *p = value; *p; ++p)
            if (*p < '0' || *p > '9')
                valid = false;
        unsigned number = strtoul(value, NULL, 10);
        if (number > 100)
            valid = false;
        *out = number;
    }
    free(body);
    return valid;
}

static bool update_city(tv_settings_t *s, const cJSON *object)
{
    /* Split and validate the city/country pair supplied by the original web page.
     * FIXED_RECONSTRUCTION: 0x4200f2c0 copies the complete regional suffix into
     * a 20-byte field; accept AU-W/US-H rather than requiring exactly two letters. */

    char value[sizeof(s->city) + 3 + sizeof(s->country) - 1];
    if (!copy_string(object, "city", value, sizeof(value)))
        return false;
    char *separator = strrchr(value, ',');
    size_t comma_bytes = 1;
    if (!separator)
    {
        separator = strstr(value, "\xef\xbc\x8c");
        comma_bytes = 3;
    }
    if (!separator)
        return false;
    char *country = separator + comma_bytes;
    if (strlen(country) >= sizeof(s->country) || !settings_country_valid(country))
        return false;
    *separator = 0;
    size_t length = strlen(value);
    if (!length || length >= sizeof(s->city))
        return false;
    strcpy(s->city, value);
    size_t country_length = strlen(country);
    for (size_t i = 0; i <= country_length; ++i)
        s->country[i] = toupper((unsigned char)country[i]);
    return true;
}

esp_err_t web_settings_post(httpd_req_t *req)
{
    /* Validate and apply one original settings request and its follow-up action.
     * FIXED_FACTORY: /wifireset at 0x4200e84c overwrites the supplied credentials
     * with unrelated scratch buffers. Persist the validated JSON SSID/password.
     * Both credential routes accept normal JSON whitespace instead of relying
     * on the factory handlers' literal substring parsing. */

    tv_settings_t s;
    settings_snapshot(&s);
    bool valid = false, restart = false, weather = false;
    if (!strcmp(req->uri, "/restart"))
    {
        if (req->content_len)
        {
            char *body = web_body(req, 128);
            if (!body)
                return web_error(req, "Invalid body");
            free(body);
        }
        network_restart_later();
        return web_ok(req);
    }
    if (!strcmp(req->uri, "/set_led_brightness") || !strcmp(req->uri, "/set_night_brightness"))
    {
        bool day = !strcmp(req->uri, "/set_led_brightness");
        unsigned percent;
        valid = read_brightness(req, day ? "ledBrightness" : "NightBrightness", &percent);
        if (valid)
        {
            if (day)
                s.day_level = 1000 - percent * 10;
            else
                s.night_level = 1000 - percent * 10;
        }
    }
    else
    {
        cJSON *object = web_parse_json(req);
        if (!object)
            return web_error(req, "Expected a bounded JSON object");
        for (unsigned i = 0; i < sizeof(integers) / sizeof(integers[0]); ++i)
            if (!strcmp(req->uri, integers[i].post))
            {
                int value;
                valid =
                    web_integer(object, integers[i].key, integers[i].min, integers[i].max, &value);
                if (valid)
                    *((uint8_t *)&s + integers[i].offset) = value;
            }
        if (!strcmp(req->uri, "/settings"))
        {
            valid = true;
            bool any = false;
            for (unsigned i = 0; i < sizeof(switches) / sizeof(switches[0]); ++i)
                if (cJSON_HasObjectItem(object, switches[i].key))
                {
                    int value;
                    any = true;
                    if (!web_integer(object, switches[i].key, 0, 1, &value))
                    {
                        valid = false;
                        break;
                    }
                    *((uint8_t *)&s + switches[i].offset) = value;
                }
            valid = valid && any;
        }
        else if (!strcmp(req->uri, "/configure") || !strcmp(req->uri, "/wifireset"))
        {
            valid = copy_string(object, "ssid", s.ssid, sizeof(s.ssid)) && s.ssid[0] &&
                    copy_string(object, "password", s.password, sizeof(s.password));
            size_t password_length = strlen(s.password);
            valid = valid && (!password_length || password_length >= 8);
            restart = valid;
            if (valid)
                s.wifi_mode = 1;
        }
        else if (!strcmp(req->uri, "/advancedset"))
        {
            int clicks;
            valid =
                copy_string(object, "ntp", s.ntp, sizeof(s.ntp)) &&
                copy_string(object, "openweathermapKey", s.weather_key, sizeof(s.weather_key)) &&
                web_integer(object, "clickCount", 0, 10, &clicks);
            if (valid)
            {
                s.click_count = clicks;
                weather = true;
            }
        }
        else if (!strcmp(req->uri, "/updateCity"))
        {
            valid = update_city(&s, object);
            weather = valid;
        }
        else if (!strcmp(req->uri, "/set_clock_color"))
        {
            int index;
            const cJSON *color = cJSON_GetObjectItemCaseSensitive(object, "color");
            valid = web_integer(object, "index", 0, 2, &index) && cJSON_IsString(color) &&
                    strlen(color->valuestring) == 7 && color->valuestring[0] == '#';
            if (valid)
            {
                for (unsigned i = 1; i < 7; ++i)
                    if (!isxdigit((unsigned char)color->valuestring[i]))
                        valid = false;
                if (valid)
                    s.colors[index] = rgb565_from_rgb888(strtoul(color->valuestring + 1, NULL, 16));
            }
        }
        else if (!strcmp(req->uri, "/set_checkbox_state"))
        {
            const cJSON *id = cJSON_GetObjectItemCaseSensitive(object, "checkbox_id"),
                        *checked = cJSON_GetObjectItemCaseSensitive(object, "checked");
            valid = cJSON_IsString(id) && cJSON_IsBool(checked) && strlen(id->valuestring) == 12 &&
                    !memcmp(id->valuestring, "file", 4) &&
                    !strcmp(id->valuestring + 5, "-switch") && id->valuestring[4] >= '1' &&
                    id->valuestring[4] <= '5';
            if (valid)
            {
                unsigned mask = 1u << (id->valuestring[4] - '1');
                if (cJSON_IsTrue(checked))
                    s.photo_mask |= mask;
                else
                    s.photo_mask &= ~mask;
            }
        }
        cJSON_Delete(object);
    }
    if (!valid || settings_replace(&s) != ESP_OK)
        return web_error(req, "Invalid setting or value");
    if (weather)
        weather_request_update();
    if (restart)
        network_restart_later();
    if (!strcmp(req->uri, "/advancedset"))
        return httpd_resp_send(req, "Settings saved", HTTPD_RESP_USE_STRLEN);
    return web_ok(req);
}

esp_err_t web_scan(httpd_req_t *req)
{
    /* Return real scan results or a retryable error when Wi-Fi cannot scan.
     * FIXED_FACTORY: /scan at 0x4200f440 dereferences its null output buffer when
     * there are no networks. Return a valid empty JSON array for zero results. */

    wifi_ap_record_t *records = calloc(20, sizeof(*records));
    if (!records)
        return httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "Out of memory");
    uint16_t count = 20;
    esp_err_t result = network_scan(records, &count);
    cJSON *list = cJSON_CreateArray();
    if (result == ESP_OK)
        for (unsigned i = 0; i < count; ++i)
        {
            records[i].ssid[32] = 0;
            cJSON *entry = cJSON_CreateObject();
            cJSON_AddStringToObject(entry, "ssid", (const char *)records[i].ssid);
            cJSON_AddNumberToObject(entry, "rssi", records[i].rssi);
            cJSON_AddItemToArray(list, entry);
        }
    free(records);
    if (result != ESP_OK)
    {
        cJSON_Delete(list);
        httpd_resp_set_status(req, "503 Service Unavailable");
        return httpd_resp_send(req, "Wi-Fi scan busy; retry", HTTPD_RESP_USE_STRLEN);
    }
    return web_json(req, list);
}
