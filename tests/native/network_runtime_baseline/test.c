/* Historical negative evidence. Each rejected safety property has exit 42. */
#include "platform.h"
#include "policy.inc"
#include "actual.inc"

static int safety(bool condition, const char *name) {
    if (condition) { printf("SAFETY_OK:%s\n", name); return 0; }
    printf("SAFETY_FAILURE:%s\n", name);
    return 42;
}

static void reset(void) {
    memset(&state, 0, sizeof(state));
    memset(&s_station_config, 0, sizeof(s_station_config));
    memset(s_credentials, 0, sizeof(s_credentials));
    memset(&driver_config, 0, sizeof(driver_config));
    s_state = &state;
    s_wifi_events = 1;
    s_station_netif = s_ap_netif = s_softap_reboot_timer = NULL;
    s_have_credentials = true;
    s_retries = 0;
    event_bits = connects = ap_calls = delays = waits = starts = rssi_tasks = 0;
    restart_calls = timer_starts = timer_stops = power_calls = hostname_calls = 0;
    driver_mode = WIFI_MODE_NULL;
    driver_ps = WIFI_PS_MIN_MODEM;
    config_result = query_result = 0;
    configured_ap_delay = 0;
    driver_ram = time_ready = task_polling = startup_timeout = false;
    atomic_store(&s_stopping_for_sleep, false);
    s_credential_count = 2;
    s_credential_index = 0;
    memcpy(s_credentials[0].sta.ssid, "first", sizeof("first"));
    memcpy(s_credentials[1].sta.ssid, "second", sizeof("second"));
}

static void start_online(void) {
    assert(network_service_start(&state) == ESP_OK);
    /* This is the actual historical start return after actual GOT_IP handling. */
    assert(starts == 1 && waits == 1 && driver_ram);
    assert(connects == 1 && !ap_calls && driver_mode == WIFI_MODE_STA);
    assert(state.mode == NATIVE_NETWORK_CLIENT && state.ip == 0x01020304);
#ifdef TARGET_C3
    assert(rssi_tasks == 1 && hostname_calls == 1);
#else
    assert(!rssi_tasks && !hostname_calls);
#endif
}

static void disconnect(void) {
    event_handler(NULL, WIFI_EVENT, WIFI_EVENT_STA_DISCONNECTED, NULL);
}

int main(int argc, char **argv) {
    assert(argc == 2);
    reset();
    if (!strcmp(argv[1], "late-fallback")) {
        start_online();
        unsigned before = connects;
#ifdef TARGET_C3
        for (unsigned n = 0; n < 6; ++n) disconnect();
        assert(connects - before == 5);
#else
        for (unsigned n = 0; n < 9; ++n) disconnect();
        assert(connects - before == 8);
#endif
        assert(event_bits & WIFI_FAILED_BIT);
        return safety(ap_calls > 0 && driver_mode == WIFI_MODE_APSTA,
                      "late_failure_requires_portal");
    }
    if (!strcmp(argv[1], "manual-apsta")) {
        startup_timeout = true;
        assert(network_service_start(&state) == ESP_OK);
        assert(driver_mode == WIFI_MODE_APSTA && ap_calls == 1 && waits == 1);
        unsigned before = connects;
        assert(network_service_retry_client() == ESP_OK && connects == before + 1);
        /* The HTTP caller has not yet regained control to send its reply. */
        return safety(driver_mode == WIFI_MODE_APSTA,
                      "manual_retry_preserves_portal_until_reply");
    }
#ifdef TARGET_C3
    if (!strcmp(argv[1], "stale-state")) {
        start_online();
        assert(state.rssi == -55);
        disconnect();
        return safety(state.mode != NATIVE_NETWORK_CLIENT && state.ip == 0,
                      "disconnect_invalidates_client_and_ip");
    }
    if (!strcmp(argv[1], "failed-config")) {
        start_online();
        config_result = ESP_FAIL;
        assert(select_credential(1) == ESP_FAIL);
        assert(!strcmp((char *)driver_config.sta.ssid, "first"));
        return safety(s_credential_index == 0 &&
                      !strcmp((char *)s_station_config.sta.ssid, "first"),
                      "failed_config_keeps_applied_selection");
    }
    if (!strcmp(argv[1], "stale-rssi")) {
        start_online();
        state.rssi = -42;
        query_result = ESP_FAIL;
        task_polling = true;
        if (!setjmp(poll_exit)) rssi_task(NULL);
        assert(delays == 2);
        return safety(state.rssi == 0, "failed_rssi_query_invalidates_sample");
    }
    if (!strcmp(argv[1], "last-profile")) {
        start_online();
        assert(select_credential(1) == ESP_OK);
        ip_event_got_ip_t ip = {.ip_info.ip.addr = 0x05060708};
        event_handler(NULL, IP_EVENT, IP_EVENT_STA_GOT_IP, &ip);
        assert(s_credential_index == 1 && state.ip == 0x05060708);
        unsigned before = connects;
        for (unsigned n = 0; n < 3; ++n) disconnect();
        assert(connects == before + 2 && (event_bits & WIFI_FAILED_BIT));
        return safety(s_credential_index == 0, "late_cycle_wraps_to_earlier_profiles");
    }
    if (!strcmp(argv[1], "power-bool")) {
        start_online();
        assert(network_service_set_streaming(true) == ESP_OK);
        assert(driver_ps == WIFI_PS_NONE);
        assert(network_service_set_streaming(false) == ESP_OK);
        assert(driver_ps == WIFI_PS_MIN_MODEM);
        puts("CHARACTERIZATION:unowned_bool_false_replaces_true");
        puts("LIMIT:actual_audio_generation_interleaving_is_not_executed");
        return 0;
    }
#endif
    fprintf(stderr, "Unknown case: %s\n", argv[1]);
    return 2;
}
