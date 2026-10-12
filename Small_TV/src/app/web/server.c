#include "web.h"
#include "network.h"
#include <errno.h>
#include <limits.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

extern const unsigned char web_setup[], web_settings[], web_photo[];
extern const size_t web_setup_length, web_settings_length, web_photo_length;

esp_err_t web_error(httpd_req_t *req, const char *message)
{
    /* Return a bounded bad-request response for invalid input. */

    httpd_resp_set_status(req, "400 Bad Request");
    httpd_resp_set_type(req, "text/plain; charset=utf-8");
    return httpd_resp_send(req, message, HTTPD_RESP_USE_STRLEN);
}

esp_err_t web_ok(httpd_req_t *req)
{
    /* Return the original short success response. */
    return httpd_resp_send(req, "OK", 2);
}

esp_err_t web_json(httpd_req_t *req, cJSON *object)
{
    /* Serialize a JSON response and release its temporary allocation. */

    if (!object)
        return httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "Out of memory");
    char *text = cJSON_PrintUnformatted(object);
    cJSON_Delete(object);
    if (!text)
        return httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "Out of memory");
    httpd_resp_set_type(req, "application/json; charset=utf-8");
    httpd_resp_set_hdr(req, "Cache-Control", "no-store");
    esp_err_t result = httpd_resp_send(req, text, HTTPD_RESP_USE_STRLEN);
    cJSON_free(text);
    return result;
}

char *web_body(httpd_req_t *req, size_t max_length)
{
    /* Read a bounded request body, enforcing origin checks and receive timeouts. */
    /* Requests from the recovered pages are same-origin. CLI requests omit Origin. */
    size_t origin_length = httpd_req_get_hdr_value_len(req, "Origin");
    if (origin_length)
    {
        char origin[160], host[128], expected[160];
        if (origin_length >= sizeof(origin) ||
            httpd_req_get_hdr_value_str(req, "Origin", origin, sizeof(origin)) != ESP_OK ||
            httpd_req_get_hdr_value_str(req, "Host", host, sizeof(host)) != ESP_OK)
            return NULL;
        snprintf(expected, sizeof(expected), "http://%s", host);
        if (strcmp(origin, expected))
            return NULL;
    }
    if (req->content_len == 0 || req->content_len > max_length)
        return NULL;
    char *body = malloc(req->content_len + 1);
    if (!body)
        return NULL;
    size_t received = 0;
    unsigned timeouts = 0;
    while (received < req->content_len)
    {
        int bytes = httpd_req_recv(req, body + received, req->content_len - received);
        if (bytes == HTTPD_SOCK_ERR_TIMEOUT && ++timeouts < 3)
            continue;
        if (bytes <= 0)
        {
            free(body);
            return NULL;
        }
        received += bytes;
    }
    body[received] = 0;
    return body;
}

cJSON *web_parse_json(httpd_req_t *req)
{
    /* Read and parse a bounded JSON object from the HTTP request. */

    char *body = web_body(req, 4096);
    if (!body)
        return NULL;
    const char *end = NULL;
    cJSON *object = cJSON_ParseWithLengthOpts(body, req->content_len + 1, &end, true);
    free(body);
    if (!cJSON_IsObject(object))
    {
        cJSON_Delete(object);
        return NULL;
    }
    return object;
}

bool web_integer(const cJSON *object, const char *name, int minimum, int maximum, int *out)
{
    /* Accept a complete bounded integer from the original numeric/string API form. */

    const cJSON *item = cJSON_GetObjectItemCaseSensitive(object, name);
    double value;
    if (cJSON_IsNumber(item))
        value = item->valuedouble;
    else if (cJSON_IsString(item))
    {
        const char *p = item->valuestring;
        if (!*p)
            return false;
        if (*p == '-')
            ++p;
        if (!*p)
            return false;
        for (; *p; ++p)
            if (*p < '0' || *p > '9')
                return false;
        char *end;
        errno = 0;
        long parsed = strtol(item->valuestring, &end, 10);
        if (errno || *end)
            return false;
        value = parsed;
    }
    else
        return false;
    if (!isfinite(value) || value < minimum || value > maximum || floor(value) != value)
        return false;
    *out = (int)value;
    return true;
}

static esp_err_t page(httpd_req_t *req)
{
    /* Serve the recovered setup, settings or photo page for the current URI/mode. */

    const unsigned char *data = web_settings;
    size_t length = web_settings_length;
    if (!strcmp(req->uri, "/photo") || !strcmp(req->uri, "/photo.html"))
    {
        data = web_photo;
        length = web_photo_length;
    }
    else if (!strcmp(req->uri, "/setup") || !strcmp(req->uri, "/setup.html") ||
             (!strcmp(req->uri, "/") && !network_connected()))
    {
        data = web_setup;
        length = web_setup_length;
    }
    httpd_resp_set_type(req, "text/html; charset=utf-8");
    return httpd_resp_send(req, (const char *)data, (int)length);
}

static esp_err_t advanced_page(httpd_req_t *req)
{
    /* Serve the retained optional editor for weather, NTP and night settings. */

    static const char html[] =
        "<!doctype html><html lang=en><meta charset=utf-8><meta name=viewport "
        "content='width=device-width,initial-scale=1'><title>Small TV advanced settings</title>"
        "<body style='font:18px sans-serif;max-width:600px;margin:2rem auto;padding:1rem'><a "
        "href=/settings>Clock settings</a> | <a href=/photo>Photos</a>"
        "<h1>Advanced settings</h1><form id=f><p><label>NTP server <input id=ntp "
        "value=pool.ntp.org maxlength=64 required></label></p>"
        "<p><label>OpenWeatherMap API key <input id=key type=password maxlength=64 "
        "autocomplete=off></label></p>"
        "<p>The key is stored on this device and sent to OpenWeatherMap using the factory HTTP API. Saving an "
        "empty key disables weather updates.</p><button>Save</button></form>"
        "<p><label><input id=night type=checkbox> Night brightness "
        "schedule</label></p><p><label>Start hour <input id=start type=number min=18 "
        "max=23></label></p>"
        "<p><label>Stop hour <input id=stop type=number min=5 max=12></label></p>"
        "<p><label>Night brightness <input id=brightness type=range min=2 max=99></label></p><p "
        "id=status></p>"
        "<script>const $=id=>document.getElementById(id);async function post(url,body){const "
        "r=await "
        "fetch(url,{method:'POST',headers:{'Content-Type':'application/"
        "json'},body:JSON.stringify(body)});if(!r.ok)throw Error(await "
        "r.text());$('status').textContent=await r.text()}"
        "$('f').onsubmit=async e=>{e.preventDefault();try{await "
        "post('/"
        "advancedset',{ntp:$('ntp').value,openweathermapKey:$('key').value,clickCount:0})}catch(e){"
        "$('status').textContent=e.message}};"
        "fetch('/"
        "getsettings').then(r=>r.json()).then(s=>$('night').checked=!!s.nightmode);$('night')."
        "onchange=()=>post('/settings',{nightmode:+$('night').checked});"
        "fetch('/"
        "get_night_brightness').then(r=>r.json()).then(s=>$('brightness').value=s.brightness);$('"
        "brightness').onchange=async()=>{const r=await "
        "fetch('/set_night_brightness',{method:'POST',body:new "
        "URLSearchParams({NightBrightness:$('brightness').value})});$('status').textContent=await "
        "r.text()};"
        "for(const [id,get,set,key] of "
        "[['start','/GetNightStartTime','/SetNightStartTime','StartTime'],['stop','/"
        "GetNightStopTime','/"
        "SetNightStopTime','StopTime']]){fetch(get).then(r=>r.text()).then(v=>$(id).value=v);$(id)."
        "onchange=()=>post(set,{[key]:$(id).value})}</script></body></html>";
    httpd_resp_set_type(req, "text/html; charset=utf-8");
    return httpd_resp_send(req, html, sizeof(html) - 1);
}

static esp_err_t captive_redirect(httpd_req_t *req, httpd_err_code_t error)
{
    /* Redirect unknown setup-network paths to the captive configuration page. */

    (void)error;
    httpd_resp_set_status(req, "302 Found");
    httpd_resp_set_hdr(req, "Location", "/");
    return httpd_resp_send(req, "", 0);
}

/* All 34 recovered method/URI pairs. Additions are page aliases and /advanced. */
static const httpd_uri_t routes[] = {
    {.uri = "/get_Photo_File", .method = HTTP_GET, .handler = web_photo_get},
    {.uri = "/set_checkbox_state", .method = HTTP_POST, .handler = web_settings_post},
    {.uri = "/get_checkbox_state", .method = HTTP_GET, .handler = web_settings_get},
    {.uri = "/set_display_time", .method = HTTP_POST, .handler = web_settings_post},
    {.uri = "/get_display_time", .method = HTTP_GET, .handler = web_settings_get},
    {.uri = "/photo", .method = HTTP_GET, .handler = page},
    {.uri = "/wifireset", .method = HTTP_POST, .handler = web_settings_post},
    {.uri = "/advancedset", .method = HTTP_POST, .handler = web_settings_post},
    {.uri = "/restart", .method = HTTP_POST, .handler = web_settings_post},
    {.uri = "/GetNightStopTime", .method = HTTP_GET, .handler = web_settings_get},
    {.uri = "/SetNightStopTime", .method = HTTP_POST, .handler = web_settings_post},
    {.uri = "/GetNightStartTime", .method = HTTP_GET, .handler = web_settings_get},
    {.uri = "/SetNightStartTime", .method = HTTP_POST, .handler = web_settings_post},
    {.uri = "/set_night_brightness", .method = HTTP_POST, .handler = web_settings_post},
    {.uri = "/get_night_brightness", .method = HTTP_GET, .handler = web_settings_get},
    {.uri = "/set_clock_color", .method = HTTP_POST, .handler = web_settings_post},
    {.uri = "/get_clock_colors", .method = HTTP_GET, .handler = web_settings_get},
    {.uri = "/set_led_brightness", .method = HTTP_POST, .handler = web_settings_post},
    {.uri = "/get_led_brightness", .method = HTTP_GET, .handler = web_settings_get},
    {.uri = "/updateCity", .method = HTTP_POST, .handler = web_settings_post},
    {.uri = "/GetTimeModeValue", .method = HTTP_GET, .handler = web_settings_get},
    {.uri = "/SetTimeModeValue", .method = HTTP_POST, .handler = web_settings_post},
    {.uri = "/getsettings", .method = HTTP_GET, .handler = web_settings_get},
    {.uri = "/settings", .method = HTTP_POST, .handler = web_settings_post},
    {.uri = "/getclocktype", .method = HTTP_GET, .handler = web_settings_get},
    {.uri = "/setclocktype", .method = HTTP_POST, .handler = web_settings_post},
    {.uri = "/getgifvalue", .method = HTTP_GET, .handler = web_settings_get},
    {.uri = "/setgifvalue", .method = HTTP_POST, .handler = web_settings_post},
    {.uri = "/scan", .method = HTTP_GET, .handler = web_scan},
    {.uri = "/configure", .method = HTTP_POST, .handler = web_settings_post},
    {.uri = "/", .method = HTTP_GET, .handler = page},
    {.uri = "/finish_upload", .method = HTTP_POST, .handler = web_photo_post},
    {.uri = "/upload_chunk", .method = HTTP_POST, .handler = web_photo_post},
    {.uri = "/start_upload", .method = HTTP_POST, .handler = web_photo_post},
    {.uri = "/setup", .method = HTTP_GET, .handler = page},
    {.uri = "/setup.html", .method = HTTP_GET, .handler = page},
    {.uri = "/settings", .method = HTTP_GET, .handler = page},
    {.uri = "/settings.html", .method = HTTP_GET, .handler = page},
    {.uri = "/photo.html", .method = HTTP_GET, .handler = page},
    {.uri = "/advanced", .method = HTTP_GET, .handler = advanced_page},
};

esp_err_t web_start(void)
{
    /* Start HTTP and register the recovered routes plus compatibility aliases. */

    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.max_uri_handlers = 48;
    config.stack_size = 6144;
    config.lru_purge_enable = true;
    config.max_open_sockets = 4;
    config.recv_wait_timeout = 5;
    config.send_wait_timeout = 5;
    httpd_handle_t server;
    esp_err_t result = httpd_start(&server, &config);
    if (result != ESP_OK)
        return result;
    for (unsigned i = 0; i < sizeof(routes) / sizeof(routes[0]); ++i)
    {
        result = httpd_register_uri_handler(server, &routes[i]);
        if (result != ESP_OK)
        {
            httpd_stop(server);
            return result;
        }
    }
    return httpd_register_err_handler(server, HTTPD_404_NOT_FOUND, captive_redirect);
}
