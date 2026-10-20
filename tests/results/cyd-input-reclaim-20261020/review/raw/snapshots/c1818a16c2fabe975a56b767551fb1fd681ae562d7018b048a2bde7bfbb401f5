#include "web_network_settings.h"

#include <inttypes.h>
#include <stdio.h>
#include <string.h>

#include "json_buffer.h"
#include "native_web_transport.h"
#include "network_service.h"
#include "network_settings.h"

#define NETWORK_QUERY_MAX_BYTES 192U

static esp_err_t reply(httpd_req_t *request, const char *status, const char *body) {
    if (httpd_resp_set_status(request, status) != ESP_OK ||
        httpd_resp_set_type(request, "application/json; charset=utf-8") != ESP_OK ||
        httpd_resp_set_hdr(request, "Cache-Control", "no-store") != ESP_OK)
        return ESP_FAIL;
    return httpd_resp_sendstr(request, body);
}

static esp_err_t reject_body(httpd_req_t *request) {
    (void)httpd_resp_set_hdr(request, "Connection", "close");
    esp_err_t result = reply(request, "400 Bad Request",
        "{\"error\":\"Network settings requests must not contain a body\"}");
    native_web_transport_prepare_close(request->handle,
        httpd_req_to_sockfd(request), result == ESP_OK);
    // Prevent HTTPD from purging an unbounded request body after returning.
    return ESP_FAIL;
}

static int hex_value(unsigned char value) {
    if (value >= '0' && value <= '9') return value - '0';
    if (value >= 'a' && value <= 'f') return value - 'a' + 10;
    if (value >= 'A' && value <= 'F') return value - 'A' + 10;
    return -1;
}

static bool decode(const char *start, const char *end, char *output, size_t capacity) {
    size_t length = 0;
    while (start < end) {
        unsigned char value = (unsigned char)*start++;
        if (value == '%') {
            if (end - start < 2) return false;
            int high = hex_value((unsigned char)start[0]);
            int low = hex_value((unsigned char)start[1]);
            if (high < 0 || low < 0) return false;
            value = (unsigned char)(high * 16 + low);
            start += 2;
        } else if (value == '+') value = ' ';
        if (!value || value < 0x20U || value == 0x7fU || length + 1U >= capacity)
            return false;
        output[length++] = (char)value;
    }
    output[length] = '\0';
    return true;
}

static bool timeout_minutes(const char *text, uint8_t *output) {
    if (!*text || (text[0] == '0' && text[1])) return false;
    unsigned value = 0;
    for (; *text; ++text) {
        if (*text < '0' || *text > '9') return false;
        unsigned digit = (unsigned)(*text - '0');
        if (value > (NETWORK_SETTINGS_AP_TIMEOUT_MAX_MINUTES - digit) / 10U)
            return false;
        value = value * 10U + digit;
    }
    *output = (uint8_t)value;
    return true;
}

static bool parse_query(const char *query, network_settings_t *settings) {
    static const char *const keys[] = {"hostname", "ap_timeout_minutes"};
    network_settings_t candidate = {0};
    unsigned seen = 0;
    for (const char *field = query; *field;) {
        const char *end = strchr(field, '&');
        if (!end) end = field + strlen(field);
        const char *equals = memchr(field, '=', (size_t)(end - field));
        char key[24], value[NETWORK_SETTINGS_HOSTNAME_CAPACITY];
        if (!equals || !decode(field, equals, key, sizeof(key)) ||
            !decode(equals + 1, end, value, sizeof(value))) return false;
        unsigned index = 0;
        while (index < 2U && strcmp(key, keys[index])) ++index;
        if (index == 2U || (seen & (1U << index))) return false;
        seen |= 1U << index;
        if (index == 0U) memcpy(candidate.hostname, value, strlen(value) + 1U);
        else if (!timeout_minutes(value, &candidate.ap_timeout_minutes)) return false;
        if (!*end) break;
        field = end + 1;
        if (!*field) return false;
    }
    if (seen != 3U || !network_settings_valid(&candidate)) return false;
    *settings = candidate;
    return true;
}

esp_err_t web_network_settings_info_handler(httpd_req_t *request) {
    if (!request) return ESP_FAIL;
    if (request->content_len) return reject_body(request);
    if (request->method != HTTP_GET || httpd_req_get_url_query_len(request))
        return reply(request, "400 Bad Request", "{\"error\":\"Invalid network settings request\"}");
    network_settings_t desired;
    uint32_t revision;
    if (!network_settings_snapshot(&desired, &revision))
        return reply(request, "503 Service Unavailable", "{\"error\":\"Network settings unavailable\"}");
    network_snapshot_t snapshot;
    bool available = network_service_snapshot(&snapshot, 25U) == ESP_OK;
    char body[768], fields[384];
    json_buffer_t output;
    json_buffer_init(&output, body, sizeof(body));
    json_buffer_raw(&output, "{\"hostname\":");
    json_buffer_string(&output, desired.hostname);
    snprintf(fields, sizeof(fields), ",\"ap_timeout_minutes\":%u,\"desired_revision\":%" PRIu32
        ",\"runtime_available\":%s,\"configured_hostname\":",
        desired.ap_timeout_minutes, revision, available ? "true" : "false");
    json_buffer_raw(&output, fields);
    if (available && snapshot.settings.hostname_valid)
        json_buffer_string(&output, snapshot.settings.configured_hostname);
    else json_buffer_raw(&output, "null");
    bool pending = !available || !snapshot.settings.hostname_valid ||
        strcmp(desired.hostname, snapshot.settings.configured_hostname) != 0;
    snprintf(fields, sizeof(fields), ",\"hostname_pending\":%s,\"hostname_revision\":",
             pending ? "true" : "false");
    json_buffer_raw(&output, fields);
    if (available) {
        snprintf(fields, sizeof(fields), "%" PRIu32 ",\"last_hostname_error\":%d,"
            "\"ap_timeout_armed\":%s,\"ap_timeout_remaining_ms\":%" PRIu64 "}",
            snapshot.settings.hostname_revision, snapshot.settings.hostname_error,
            snapshot.settings.ap_timeout_armed ? "true" : "false",
            snapshot.settings.ap_timeout_remaining_ms);
        json_buffer_raw(&output, fields);
    } else json_buffer_raw(&output, "null,\"last_hostname_error\":null,"
        "\"ap_timeout_armed\":null,\"ap_timeout_remaining_ms\":null}");
    if (output.failed)
        return reply(request, "500 Internal Server Error", "{\"error\":\"Network settings response exhausted\"}");
    return reply(request, "200 OK", body);
}

esp_err_t web_network_settings_edit_handler(httpd_req_t *request) {
    if (!request) return ESP_FAIL;
    if (request->content_len) return reject_body(request);
    if (request->method != HTTP_POST)
        return reply(request, "400 Bad Request", "{\"error\":\"Invalid network settings request\"}");
    size_t size = httpd_req_get_url_query_len(request);
    char query[NETWORK_QUERY_MAX_BYTES + 1U];
    network_settings_t settings;
    if (!size || size > NETWORK_QUERY_MAX_BYTES ||
        httpd_req_get_url_query_str(request, query, sizeof(query)) != ESP_OK ||
        strlen(query) != size || !parse_query(query, &settings))
        return reply(request, "400 Bad Request", "{\"error\":\"Invalid network settings\"}");
    esp_err_t result = network_settings_save(&settings);
    if (result == ESP_ERR_INVALID_ARG)
        return reply(request, "400 Bad Request", "{\"error\":\"Invalid network settings\"}");
    if (result == ESP_ERR_INVALID_STATE || result == ESP_ERR_TIMEOUT || result == ESP_ERR_NO_MEM)
        return reply(request, "503 Service Unavailable", "{\"error\":\"Network settings unavailable\"}");
    if (result != ESP_OK)
        return reply(request, "500 Internal Server Error", "{\"error\":\"Network settings could not be saved\"}");
    return reply(request, "200 OK", "{\"saved\":true,\"application_pending\":true,\"rebooting\":false}");
}
