/* Unknown paths bypass the 34 registered URI contracts. Exercise that callback. */
static void test_http_captive(void)
{
    /* FIXED_TEST: factory 0x4200d4be serves root for its AP Host, including a
     * missing Host, and redirects foreign names to the absolute AP address.
     * Also prevent its substring match from accepting an AP-looking foreign host. */
    bool saved_connected = connected, saved_ap = setup_ap;
    setup_ap = true;
    connected = false;
    const char *local[] = {"192.168.43.1", "192.168.43.1:80", "192.168.43.1:18400", NULL};
    for (unsigned i = 0; i < sizeof(local)/sizeof(local[0]); ++i)
    {
        const char *target = "/generate_204?probe=1";
        prepare(target, "", 0, NULL);
        request.host = local[i];
        dispatch(HTTP_GET);
        CHECK(request.status == 200 && request.location[0] == 0);
        CHECK(request.response_length == web_setup_length);
        CHECK(!memcmp(request.response, web_setup, web_setup_length));
        CHECK(!strcmp(request.response_type, "text/html; charset=utf-8"));
        CHECK(request.uri == target && request.user_ctx == NULL);
    }
    const char *foreign[] = {"connectivity.example.invalid", "192.168.43.1.example.invalid",
                            "evil-192.168.43.1", "192.168.43.1:0", "192.168.43.1:65536",
                            "192.168.43.1:80suffix", "192.168.43.1:",
                            "192.168.43.1:+80", "192.168.43.1: 80"};
    for (unsigned i = 0; i < sizeof(foreign)/sizeof(foreign[0]); ++i)
    {
        prepare("/hotspot-detect.html", "", 0, NULL);
        request.host = foreign[i];
        dispatch(HTTP_GET);
        CHECK(request.status == 302);
        CHECK(!strcmp(request.location, "http://192.168.43.1/"));
        CHECK(request.response_length == 0);
    }
    /* Following the redirect must terminate in the setup page, not another redirect. */
    const char *html = get("/");
    CHECK(request.location[0] == 0 && request.response_length == web_setup_length);
    CHECK(!memcmp(html, web_setup, web_setup_length));
    /* A station has no setup AP: retain its local redirect rather than sending
     * a browser to an unrelated/unreachable 192.168.43.1 network. */
    setup_ap = false;
    connected = true;
    prepare("/missing-station-path", "", 0, NULL);
    request.host = "clock.example.invalid:18400";
    dispatch(HTTP_GET);
    CHECK(request.status == 302 && !strcmp(request.location, "/"));
    get("/");
    CHECK(request.response_length == web_settings_length);
    CHECK(!memcmp(request.response, web_settings, web_settings_length));
    connected = saved_connected;
    setup_ap = saved_ap;
}
