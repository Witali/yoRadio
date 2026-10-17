/* Request-target regressions share native_test.c's registered HTTP adapter. */
static const char *http_target(char *out, size_t capacity, const char *path, unsigned form)
{
    /* Four valid target forms must select the same registered application action. */
    int length = snprintf(out, capacity, "%s%s%s", form >= 2 ? "http://clock.example.invalid" : "",
                          path, form % 2 ? (strchr(path, '?') ? "&probe=%2Fphoto" : "?probe=%2Fphoto") : "");
    CHECK(length > 0 && (size_t)length < capacity);
    return out;
}

static void test_http_uri_targets(void)
{
    /* Exercise every GET, both root-page modes and each settings POST through
     * the actual handlers. Query values must not replace the selected path. */
    char target[256];
    for (unsigned mode = 0; mode < 2; ++mode)
    {
        connected = mode != 0;
        for (unsigned i = 0; i < registered_routes; ++i)
        {
            if (route_table[i]->method != HTTP_GET)
                continue;
            const char *path = !strcmp(route_table[i]->uri, "/get_Photo_File")
                                   ? "/get_Photo_File?file=1&chunk=0&size=0" : route_table[i]->uri;
            get(path);
            size_t length = request.response_length;
            char *expected = malloc(length + 1);
            CHECK(expected != NULL);
            memcpy(expected, request.response, length + 1);
            char type[64];
            strcpy(type, request.response_type);
            for (unsigned form = 1; form < 4; ++form)
            {
                get(http_target(target, sizeof(target), path, form));
                CHECK(request.response_length == length && !memcmp(request.response, expected, length));
                CHECK(!strcmp(request.response_type, type));
                CHECK(request.uri == target);
            }
            free(expected);
        }
    }
    const struct { const char *path, *body; } posts[] = {
        {"/setclocktype", "{\"clocktype\":2}"}, {"/setgifvalue", "{\"gif\":3}"},
        {"/SetTimeModeValue", "{\"timemode\":1}"}, {"/SetNightStartTime", "{\"StartTime\":19}"},
        {"/SetNightStopTime", "{\"StopTime\":8}"}, {"/set_display_time", "{\"display_time\":10}"},
        {"/settings", "{\"hourFormat\":1,\"nightmode\":0}"},
        {"/set_clock_color", "{\"index\":1,\"color\":\"#12ab34\"}"},
        {"/set_checkbox_state", "{\"checkbox_id\":\"file2-switch\",\"checked\":true}"},
        {"/set_led_brightness", "ledBrightness=63"}, {"/set_night_brightness", "NightBrightness=12"},
        {"/updateCity", "{\"city\":\"London,GB\"}"},
        {"/advancedset", "{\"ntp\":\"test.invalid\",\"openweathermapKey\":\"\",\"clickCount\":0}"},
        {"/configure", "{\"ssid\":\"synthetic\",\"password\":\"\"}"},
        {"/wifireset", "{\"ssid\":\"synthetic\",\"password\":\"\"}"}, {"/restart", ""}
    };
    tv_settings_t saved;
    settings_snapshot(&saved);
    for (unsigned i = 0; i < sizeof(posts) / sizeof(posts[0]); ++i)
    {
        tv_settings_t expected, actual;
        unsigned restarts = restart_requests, updates = weather_requests;
        post(posts[i].path, posts[i].body, 200);
        settings_snapshot(&expected);
        unsigned restart_delta = restart_requests - restarts, update_delta = weather_requests - updates;
        char response[32];
        CHECK(request.response_length < sizeof(response));
        strcpy(response, request.response);
        for (unsigned form = 1; form < 4; ++form)
        {
            restarts = restart_requests; updates = weather_requests;
            post(http_target(target, sizeof(target), posts[i].path, form), posts[i].body, 200);
            settings_snapshot(&actual);
            CHECK(!memcmp(&expected, &actual, sizeof(expected)));
            CHECK(restart_requests - restarts == restart_delta && weather_requests - updates == update_delta);
            CHECK(!strcmp(request.response, response));
        }
    }
    CHECK(settings_replace(&saved) == ESP_OK);
    rejected_setting("/setgifvalue?probe=1", "{\"gif\":5}");
    const char *unknown[] = {"/getclocktype/", "/getclocktypeX", "/GETCLOCKTYPE",
                            "/getclocktype%3Fprobe=1", "/missing?path=/getclocktype"};
    for (unsigned i = 0; i < sizeof(unknown) / sizeof(unknown[0]); ++i)
    {
        prepare(unknown[i], "", 0, NULL);
        dispatch(HTTP_GET);
        CHECK(request.status == 302 && !strcmp(request.location, "/"));
    }
}
