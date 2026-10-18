
#define TIME_QUERY_MAX_BYTES 512U

static esp_err_t reply(httpd_req_t *request, const char *status,
                       const char *body) {
    if (httpd_resp_set_status(request, status) != ESP_OK ||
        httpd_resp_set_type(request, "application/json; charset=utf-8") != ESP_OK ||
        httpd_resp_set_hdr(request, "Cache-Control", "no-store") != ESP_OK)
        return ESP_FAIL;
    return httpd_resp_sendstr(request, body);
}

static esp_err_t reject_body(httpd_req_t *request) {
    (void)httpd_resp_set_hdr(request, "Connection", "close");
    esp_err_t result = reply(request, "400 Bad Request",
                            "{\"error\":\"Time requests must not contain a body\"}");
    native_web_transport_prepare_close(request->handle,
        httpd_req_to_sockfd(request), result == ESP_OK);
    // Returning failure makes HTTPD delete the session instead of purging an
    // attacker-controlled body after this handler returns.
    return ESP_FAIL;
}

static int hex_value(unsigned char value) {
    if (value >= '0' && value <= '9') return value - '0';
    if (value >= 'a' && value <= 'f') return value - 'a' + 10;
    if (value >= 'A' && value <= 'F') return value - 'A' + 10;
    return -1;
}

static bool decode(const char *start, const char *end,
                   char *output, size_t capacity) {
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
        if (!value || value < 0x20U || value == 0x7fU ||
            length + 1U >= capacity) return false;
        output[length++] = (char)value;
    }
    output[length] = '\0';
    return true;
}

static bool number(const char *text, bool signed_value, int *output) {
    bool negative = signed_value && *text == '-';
    if (negative) ++text;
    if (!*text || (text[0] == '0' && text[1])) return false;
    unsigned value = 0;
    for (; *text; ++text) {
        if (*text < '0' || *text > '9') return false;
        value = value * 10U + (unsigned)(*text - '0');
        if (value > 1440U) return false;
    }
    *output = negative ? -(int)value : (int)value;
    return true;
}

static bool parse_query(char *query, time_settings_t *settings) {
    static const char *const keys[] = {
        "utc_offset_minutes", "sync_interval_minutes", "server1", "server2"
    };
    time_settings_t candidate = {0};
    unsigned seen = 0;
    for (const char *field = query; *field;) {
        const char *end = strchr(field, '&');
        if (!end) end = field + strlen(field);
        const char *equals = memchr(field, '=', (size_t)(end - field));
        char key[32], value[NATIVE_TIME_SNTP_NAME_CAPACITY];
        if (!equals || !decode(field, equals, key, sizeof(key)) ||
            !decode(equals + 1, end, value, sizeof(value))) return false;
        unsigned index = 0;
        while (index < 4U && strcmp(key, keys[index])) ++index;
        if (index == 4U || (seen & (1U << index))) return false;
        seen |= 1U << index;
        int parsed;
        if (index < 2U) {
            if (!number(value, index == 0U, &parsed)) return false;
            if (index == 0U) candidate.utc_offset_minutes = (int16_t)parsed;
            else candidate.sync_interval_minutes = (uint16_t)parsed;
        } else memcpy(candidate.servers[index - 2U], value, strlen(value) + 1U);
        if (!*end) break;
        field = end + 1;
        if (!*field) return false;
    }
    candidate.server_count = candidate.servers[1][0] ? 2U : 1U;
    if (seen != 15U || !time_settings_valid(&candidate)) return false;
    *settings = candidate;
    return true;
}

esp_err_t web_time_info_handler(httpd_req_t *request) {
    if (!request) return ESP_FAIL;
    if (request->content_len) return reject_body(request);
    if (request->method != HTTP_GET || httpd_req_get_url_query_len(request))
        return reply(request, "400 Bad Request", "{\"error\":\"Invalid time request\"}");
    time_snapshot_t snapshot;
    if (!time_service_snapshot(&snapshot))
        return reply(request, "503 Service Unavailable", "{\"error\":\"Time service unavailable\"}");
    char body[1024], fields[448];
    json_buffer_t output;
    json_buffer_init(&output, body, sizeof(body));
    snprintf(fields, sizeof(fields),
        "{\"utc_offset_minutes\":%d,\"sync_interval_minutes\":%u,\"server1\":",
        snapshot.settings.utc_offset_minutes, snapshot.settings.sync_interval_minutes);
    json_buffer_raw(&output, fields);
    json_buffer_string(&output, snapshot.settings.servers[0]);
    json_buffer_raw(&output, ",\"server2\":");
    json_buffer_string(&output, snapshot.settings.server_count > 1U
                                   ? snapshot.settings.servers[1] : "");
    snprintf(fields, sizeof(fields),
        ",\"available\":%s,\"network_ready\":%s,\"clock_valid\":%s,"
        "\"synchronized_this_boot\":%s,\"desired_revision\":%" PRIu32 ","
        "\"applied_revision\":%" PRIu32 ",\"last_apply_error\":%d,\"utc_epoch\":",
        snapshot.available ? "true" : "false", snapshot.network_ready ? "true" : "false",
        snapshot.clock_valid ? "true" : "false",
        snapshot.synchronized_this_boot ? "true" : "false",
        snapshot.desired_revision, snapshot.applied_revision, snapshot.last_apply_error);
    json_buffer_raw(&output, fields);
    if (snapshot.clock_valid) {
        snprintf(fields, sizeof(fields), "%" PRId64 ",\"local_time\":", (int64_t)snapshot.utc_epoch);
        json_buffer_raw(&output, fields);
        if (!strftime(fields, sizeof(fields), "%Y-%m-%dT%H:%M:%S", &snapshot.local_time))
            return reply(request, "500 Internal Server Error", "{\"error\":\"Time formatting failed\"}");
        json_buffer_string(&output, fields);
    } else json_buffer_raw(&output, "null,\"local_time\":null");
    if (snapshot.synchronized_this_boot) {
        snprintf(fields, sizeof(fields), ",\"last_sync_epoch\":%" PRId64
                 ",\"last_sync_age_ms\":%" PRId64 "}",
                 (int64_t)snapshot.last_sync_epoch, snapshot.last_sync_age_ms);
        json_buffer_raw(&output, fields);
    } else json_buffer_raw(&output, ",\"last_sync_epoch\":null,\"last_sync_age_ms\":null}");
    if (output.failed)
        return reply(request, "500 Internal Server Error", "{\"error\":\"Time response exhausted\"}");
    return reply(request, "200 OK", body);
}

esp_err_t web_time_edit_handler(httpd_req_t *request) {
    if (!request) return ESP_FAIL;
    if (request->content_len) return reject_body(request);
    if (request->method != HTTP_POST)
        return reply(request, "400 Bad Request", "{\"error\":\"Invalid time request\"}");
    size_t size = httpd_req_get_url_query_len(request);
    char query[TIME_QUERY_MAX_BYTES + 1U];
    time_settings_t settings;
    if (!size || size > TIME_QUERY_MAX_BYTES ||
        httpd_req_get_url_query_str(request, query, sizeof(query)) != ESP_OK ||
        strlen(query) != size || !parse_query(query, &settings))
        return reply(request, "400 Bad Request", "{\"error\":\"Invalid time settings\"}");
    esp_err_t result = time_service_save_settings(&settings);
    if (result == ESP_ERR_INVALID_ARG)
        return reply(request, "400 Bad Request", "{\"error\":\"Invalid time settings\"}");
    if (result == ESP_ERR_INVALID_STATE || result == ESP_ERR_TIMEOUT || result == ESP_ERR_NO_MEM)
        return reply(request, "503 Service Unavailable", "{\"error\":\"Time settings unavailable\"}");
    if (result != ESP_OK)
        return reply(request, "500 Internal Server Error", "{\"error\":\"Time settings could not be saved\"}");
    return reply(request, "200 OK", "{\"saved\":true,\"application_pending\":true}");
}
