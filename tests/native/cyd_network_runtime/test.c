#include "platform.h"
#include <limits.h>
#include "network_runtime.h"

static native_state_t state;
static esp_netif_t station = {.identity = 1}, foreign = {.identity = 2};
static network_profiles_t profiles;

static network_snapshot_t snapshot(void) {
    network_snapshot_t view;
    CHECK(network_runtime_snapshot(&view, 10) == ESP_OK, "checked_snapshot_available");
    CHECK(view.profile_count <= 5 &&
          (view.profile_index < view.profile_count || view.profile_index == NETWORK_NO_PROFILE), "snapshot_profile_bounds");
    CHECK(!view.online || view.ipv4, "online_snapshot_coherent");
    CHECK(!view.rssi_valid || view.online, "rssi_requires_online_link");
    CHECK(view.rssi_valid || view.rssi == 0, "invalid_rssi_zero");
    return view;
}
static void make_profiles(unsigned count) {
    memset(&profiles, 0, sizeof(profiles)); profiles.count = (uint8_t)count;
    for (unsigned i = 0; i < count; ++i) {
        snprintf(profiles.rows[i].ssid, sizeof(profiles.rows[i].ssid), "network-%u", i);
        snprintf(profiles.rows[i].password, sizeof(profiles.rows[i].password), "pw-%u", i);
    }
}
static void start(unsigned count) {
    make_profiles(count);
    CHECK(network_runtime_start(&state, &station, &profiles) == ESP_OK, "runtime_start");
    fixture_wait_parked();
    CHECK(snapshot().phase == NETWORK_WAIT_START, "wait_for_actual_start_event");
    CHECK(!fixture_stats().api_calls[API_POWER], "no_power_call_before_driver_start");
    fixture_emit(WIFI_EVENT, WIFI_EVENT_STA_START, NULL, 0); fixture_step(0);
}
static void next_connect(unsigned previous) {
    for (unsigned i = 0; i < 50 && fixture_stats().connects == previous; ++i) fixture_step(100000);
    CHECK(fixture_stats().connects == previous + 1 && snapshot().phase == NETWORK_CONNECTING, "owner_made_next_attempt");
}
static void first_connect(void) { next_connect(0); }
static void online_current(uint32_t ip) {
    network_snapshot_t before = snapshot();
    CHECK(before.phase == NETWORK_CONNECTING, "online_requires_real_connect");
    fixture_observe(true, true, ip, -55, before.profile_index);
    fixture_emit(WIFI_EVENT, WIFI_EVENT_STA_CONNECTED, NULL, 0);
    fixture_emit(IP_EVENT, IP_EVENT_STA_GOT_IP, &station, ip); fixture_step(0);
    network_snapshot_t view = snapshot();
    CHECK(view.online && view.ipv4 == ip && view.phase == NETWORK_ONLINE, "actual_owner_accepts_observed_ip");
}
static void fail_attempt(void) {
    network_snapshot_t view = snapshot();
    CHECK(view.phase == NETWORK_CONNECTING, "failure_requires_real_attempt");
    fixture_observe(true, false, 0, -55, view.profile_index);
    fixture_emit(WIFI_EVENT, WIFI_EVENT_STA_CONNECTED, NULL, 0); fixture_step(0);
    fixture_observe(false, false, 0, 0, 0);
    fixture_emit(WIFI_EVENT, WIFI_EVENT_STA_DISCONNECTED, NULL, 0); fixture_step(0);
}
static void stopped(void) {
    fixture_driver_stopped();
    CHECK(network_runtime_stop(1000) == ESP_OK, "runtime_stop"); fixture_join();
    fixture_stats_t s = fixture_stats();
    CHECK(!s.queues && s.semaphores == 1 && !s.events && !s.ap_netifs && !s.registrations, "all_runtime_resources_released");
    network_snapshot_t view, unchanged; memset(&view, 0xa5, sizeof(view)); unchanged = view;
    CHECK(network_runtime_snapshot(&view, 0) == ESP_ERR_INVALID_STATE &&
          !memcmp(&view, &unchanged, sizeof(view)), "stopped_snapshot_unchanged");
    CHECK(network_runtime_retry() == ESP_ERR_INVALID_STATE &&
          network_runtime_wait_initial(0) == ESP_ERR_INVALID_STATE, "stopped_admission_rejected");
    CHECK(network_runtime_stop(0) == ESP_OK, "stop_idempotent");
    vSemaphoreDelete(state.lock);
}
static void *blocked_callback(void *unused) {
    (void)unused; fixture_emit(WIFI_EVENT, WIFI_EVENT_STA_DISCONNECTED, NULL, 0); return NULL;
}
static atomic_int stop_result;
static void *concurrent_stop(void *unused) {
    (void)unused; atomic_store(&stop_result, network_runtime_stop(1000)); return NULL;
}
static void *publisher(void *argument) {
    uintptr_t kind = (uintptr_t)argument;
    for (unsigned i = 0; i < 2000; ++i) {
        if (kind < 3) fixture_emit(WIFI_EVENT, WIFI_EVENT_STA_CONNECTED, NULL, 0);
        else if (kind == 3) {
            esp_err_t result = network_runtime_retry();
            CHECK(result == ESP_OK || result == ESP_ERR_TIMEOUT, "concurrent_retry_admission");
        } else {
            network_snapshot_t view, old; memset(&view, 0xa5, sizeof(view)); old = view;
            esp_err_t result = network_runtime_snapshot(&view, 0);
            CHECK(result == ESP_OK || result == ESP_ERR_TIMEOUT, "concurrent_snapshot_result");
            if (result == ESP_OK) {
                CHECK(!view.online || view.ipv4, "concurrent_snapshot_coherent");
                CHECK(view.profile_count == 1 &&
                      (view.profile_index == 0 || view.profile_index == NETWORK_NO_PROFILE), "concurrent_profile_coherent");
            } else CHECK(!memcmp(&view, &old, sizeof(view)), "concurrent_failed_snapshot_unchanged");
        }
    }
    return NULL;
}

int main(int argc, char **argv) {
    CHECK(argc == 2, "case_argument"); const char *name = argv[1];
    fixture_init(); native_state_init(&state); CHECK(state.lock, "state_mutex");
    if (!strcmp(name, "no-profiles")) {
        start(0); network_snapshot_t view = snapshot();
        CHECK(view.phase == NETWORK_AP_IDLE && view.ap_enabled && !view.online && !fixture_stats().connects, "no_profiles_portal_without_connect");
        CHECK(network_runtime_retry() == ESP_ERR_NOT_FOUND && network_runtime_wait_initial(0) == ESP_OK, "empty_profile_admission");
    } else if (!strcmp(name, "one-immutable")) {
        start(1); memset(&profiles, 0, sizeof(profiles)); first_connect(); online_current(0x01020304);
        CHECK(fixture_stats().config_rows[0] == 0 && snapshot().profile_count == 1, "immutable_boot_cache");
        CHECK(network_runtime_wait_initial(0) == ESP_OK, "online_initial_ready");
        fixture_stats_t before = fixture_stats();
        CHECK(network_runtime_start(&state, &station, &profiles) == ESP_ERR_INVALID_STATE &&
              fixture_stats().tasks == before.tasks, "no_duplicate_owner");
    } else if (!strcmp(name, "five-attempts") || !strcmp(name, "late-wrap")) {
        bool wrap = !strcmp(name, "late-wrap"); start(5); first_connect();
        if (wrap) {
            for (unsigned i = 0; i < 9; ++i) { unsigned count = fixture_stats().connects; fail_attempt(); next_connect(count); }
            CHECK(snapshot().profile_index == 3, "selected_later_profile"); online_current(0x01020304);
            uint32_t epoch = snapshot().epoch;
            fixture_observe(false, false, 0, 0, 0); fixture_emit(WIFI_EVENT, WIFI_EVENT_STA_DISCONNECTED, NULL, 0);
            network_snapshot_t pending;
            CHECK(network_runtime_snapshot(&pending, 0) == ESP_OK, "pending_snapshot_available");
            CHECK(!pending.online && !pending.ipv4 && !pending.rssi_valid && pending.reconciling, "pending_loss_masks_old_status");
            unsigned before = fixture_stats().connects; fixture_step(0); next_connect(before);
            CHECK(snapshot().epoch == epoch + 1 && snapshot().profile_index == 3, "late_cycle_starts_last_success");
        }
        unsigned first = fixture_stats().configs - 1;
        for (unsigned i = 0; i < 15; ++i) {
            unsigned previous = fixture_stats().connects; fail_attempt();
            if (i != 14) next_connect(previous);
        }
        fixture_stats_t s = fixture_stats(); network_snapshot_t view = snapshot();
        CHECK(view.phase == NETWORK_AP_IDLE && view.ap_enabled && !view.online && s.mode == WIFI_MODE_APSTA, "late_exhaustion_keeps_live_portal");
        for (unsigned i = 0; i < 15; ++i) CHECK(s.config_rows[first + i] == ((wrap ? 3 : 0) + i / 3) % 5, "ordered_three_attempts_each_with_wrap");
        unsigned previous = s.connects; fixture_step(100000000);
        CHECK(fixture_stats().connects == previous, "exhaustion_has_no_infinite_retry");
    } else if (!strcmp(name, "startup-deadline")) {
        start(1); CHECK(network_runtime_wait_initial(0) == ESP_ERR_TIMEOUT, "startup_not_ready_early"); first_connect();
        fixture_step(20000000); network_snapshot_t view = snapshot();
        CHECK(view.ap_enabled && !view.online && network_runtime_wait_initial(0) == ESP_OK, "portal_after_startup_budget");
        unsigned previous = fixture_stats().connects; next_connect(previous); online_current(0x01020304);
        CHECK(snapshot().ap_enabled && fixture_stats().mode == WIFI_MODE_APSTA, "late_ip_keeps_apsta");
    } else if (!strcmp(name, "cycle-deadline")) {
        start(5); int64_t begin = esp_timer_get_time();
        for (unsigned i = 0; i < 3100 && snapshot().phase != NETWORK_AP_IDLE; ++i) fixture_step(100000);
        fixture_stats_t s = fixture_stats(); network_snapshot_t view = snapshot();
        CHECK(view.phase == NETWORK_AP_IDLE && view.ap_enabled && view.last_error == ESP_ERR_TIMEOUT, "whole_cycle_deadline");
        CHECK(esp_timer_get_time() - begin <= 300000000 && s.connects <= 15 && s.connects >= 10, "bounded_cycle_attempt_count");
    } else if (!strcmp(name, "manual-admission")) {
        start(1); first_connect(); fixture_step(20000000); CHECK(snapshot().ap_enabled, "manual_portal_precondition");
        fixture_stats_t before = fixture_stats();
        CHECK(network_runtime_retry() == ESP_OK && network_runtime_retry() == ESP_ERR_TIMEOUT, "one_pending_manual_request");
        fixture_stats_t admitted = fixture_stats();
        CHECK(admitted.connects == before.connects && admitted.api_calls[API_MODE] == before.api_calls[API_MODE] &&
              admitted.api_calls[API_DISCONNECT] == before.api_calls[API_DISCONNECT], "admission_calls_no_driver_api");
        fixture_step(0); next_connect(before.connects);
        CHECK(snapshot().ap_enabled && fixture_stats().mode == WIFI_MODE_APSTA && fixture_stats().api_calls[API_AP_CONFIG] == 1, "manual_retry_retains_preconfigured_apsta");
        CHECK(network_runtime_retry() == ESP_ERR_TIMEOUT, "manual_busy_until_cycle_completion");
        online_current(0x01020304);
        CHECK(network_runtime_retry() == ESP_OK, "manual_admission_reopens_after_online");
    } else if (!strcmp(name, "manual-before-start")) {
        make_profiles(1); CHECK(network_runtime_start(&state, &station, &profiles) == ESP_OK, "manual_before_start_owner"); fixture_wait_parked();
        CHECK(network_runtime_retry() == ESP_OK, "manual_before_start_admitted"); fixture_step(0);
        CHECK(snapshot().phase == NETWORK_WAIT_START && !fixture_stats().connects &&
              network_runtime_retry() == ESP_ERR_TIMEOUT, "manual_before_start_retained");
        fixture_emit(WIFI_EVENT, WIFI_EVENT_STA_START, NULL, 0); fixture_step(0); first_connect();
        CHECK(network_runtime_retry() == ESP_ERR_TIMEOUT, "prestart_manual_busy_during_cycle"); online_current(0x01020304);
        CHECK(network_runtime_retry() == ESP_OK, "prestart_manual_completion_releases_admission");
    } else if (!strcmp(name, "manual-exhaustion")) {
        start(1); first_connect(); unsigned before = fixture_stats().connects;
        CHECK(network_runtime_retry() == ESP_OK, "manual_exhaustion_admitted"); fixture_step(0); next_connect(before);
        for (unsigned i = 0; i < 3; ++i) {
            CHECK(network_runtime_retry() == ESP_ERR_TIMEOUT, "manual_exhaustion_busy_during_attempt");
            before = fixture_stats().connects; fail_attempt(); if (i < 2) next_connect(before);
        }
        CHECK(snapshot().phase == NETWORK_AP_IDLE && network_runtime_retry() == ESP_OK, "manual_exhaustion_reopens_admission");
    } else if (!strcmp(name, "config-failure") || !strcmp(name, "connect-failure")) {
        bool config = !strcmp(name, "config-failure");
        fixture_fail_api(config ? API_STA_CONFIG : API_CONNECT, UINT_MAX, ESP_FAIL); start(1);
        for (unsigned i = 0; i < 50 && snapshot().phase != NETWORK_AP_IDLE; ++i) fixture_step(100000);
        network_snapshot_t view = snapshot(); fixture_stats_t s = fixture_stats();
        CHECK(view.phase == NETWORK_AP_IDLE && view.ap_enabled && view.last_error == ESP_FAIL, "sdk_error_exhaustion");
        CHECK(s.api_calls[API_STA_CONFIG] == 3 && s.connects == (config ? 0 : 3), "sdk_error_finite_attempts");
        if (config) CHECK(view.profile_index == NETWORK_NO_PROFILE, "failed_set_config_not_published");
    } else if (!strcmp(name, "disconnect-error")) {
        fixture_fail_api(API_DISCONNECT, 1, ESP_FAIL); start(1);
        CHECK(snapshot().last_error == ESP_FAIL, "disconnect_error_visible"); first_connect();
    } else if (!strcmp(name, "config-busy")) {
        fixture_fail_api(API_STA_CONFIG, UINT_MAX, ESP_ERR_WIFI_STATE); start(1);
        for (unsigned i = 0; i < 100 && snapshot().phase != NETWORK_AP_IDLE; ++i) fixture_step(100000);
        CHECK(snapshot().phase == NETWORK_AP_IDLE && snapshot().last_error == ESP_ERR_WIFI_STATE &&
              snapshot().profile_index == NETWORK_NO_PROFILE && !fixture_stats().connects, "driver_config_busy_bounded_by_disconnect_deadline");
    } else if (!strcmp(name, "disconnect-stuck")) {
        start(1); first_connect(); online_current(0x01020304); fixture_hold_disconnect(true);
        CHECK(network_runtime_retry() == ESP_OK, "stuck_retry_admitted"); fixture_step(0);
        unsigned configs = fixture_stats().api_calls[API_STA_CONFIG]; fixture_step(100000);
        CHECK(fixture_stats().api_calls[API_STA_CONFIG] == configs && snapshot().phase == NETWORK_WAIT_DISCONNECT, "no_config_while_associated");
        for (unsigned i = 0; i < 100 && snapshot().phase != NETWORK_AP_IDLE; ++i) fixture_step(100000);
        CHECK(snapshot().phase == NETWORK_AP_IDLE && fixture_stats().api_calls[API_STA_CONFIG] == configs, "stuck_disconnect_bounded");
    } else if (!strcmp(name, "ap-enable-errors")) {
        make_profiles(0); CHECK(network_runtime_start(&state, &station, &profiles) == ESP_OK, "ap_error_start"); fixture_wait_parked();
        fixture_fail_api(API_MODE, UINT_MAX, ESP_FAIL);
        fixture_emit(WIFI_EVENT, WIFI_EVENT_STA_START, NULL, 0); fixture_step(0);
        fixture_step(250000); fixture_step(250000);
        CHECK(!snapshot().ap_enabled && snapshot().last_error == ESP_FAIL &&
              network_runtime_wait_initial(0) == ESP_FAIL, "three_portal_enable_errors_fail_initial_ready");
        unsigned calls = fixture_stats().api_calls[API_MODE]; fixture_step(100000000);
        CHECK(fixture_stats().api_calls[API_MODE] == calls, "portal_error_retry_budget_finite");
    } else if (!strcmp(name, "queue-overflow") || !strcmp(name, "start-overflow")) {
        bool initial = !strcmp(name, "start-overflow");
        if (initial) {
            make_profiles(1); CHECK(network_runtime_start(&state, &station, &profiles) == ESP_OK, "overflow_start"); fixture_wait_parked();
            for (unsigned i = 0; i < 16; ++i) fixture_emit(WIFI_EVENT, WIFI_EVENT_STA_CONNECTED, NULL, 0);
            fixture_emit(WIFI_EVENT, WIFI_EVENT_STA_START, NULL, 0); fixture_step(0);
            first_connect(); CHECK(snapshot().event_overflows == 1, "overflowed_start_reconciles");
        } else {
            start(1); first_connect(); online_current(0x01020304); fixture_observe(false, false, 0, 0, 0);
            for (unsigned i = 0; i < 32; ++i) fixture_emit(WIFI_EVENT, WIFI_EVENT_STA_DISCONNECTED, NULL, 0);
            CHECK(snapshot().reconciling && !snapshot().online, "overflow_masks_old_online"); fixture_step(0);
            CHECK(snapshot().event_overflows == 16 && !snapshot().online && !snapshot().ipv4, "overflow_reconciles_terminal_loss");
        }
    } else if (!strcmp(name, "stale-events") || !strcmp(name, "same-ssid")) {
        bool same = !strcmp(name, "same-ssid");
        if (same) {
            make_profiles(5); for (unsigned i = 0; i < 5; ++i) strcpy(profiles.rows[i].ssid, "same");
            CHECK(network_runtime_start(&state, &station, &profiles) == ESP_OK, "same_ssid_start"); fixture_wait_parked();
            fixture_emit(WIFI_EVENT, WIFI_EVENT_STA_START, NULL, 0); fixture_step(0);
        } else start(1);
        first_connect();
        if (same) for (unsigned i = 0; i < 3; ++i) { unsigned before = fixture_stats().connects; fail_attempt(); next_connect(before); }
        uint8_t profile = snapshot().profile_index;
        fixture_emit(IP_EVENT, IP_EVENT_STA_GOT_IP, &station, 0x01020304); fixture_step(0);
        CHECK(!snapshot().online && snapshot().attempt == 1, "stale_ip_without_live_association_ignored");
        fixture_emit(WIFI_EVENT, WIFI_EVENT_STA_DISCONNECTED, NULL, 0); fixture_step(0);
        CHECK(snapshot().phase == NETWORK_CONNECTING && snapshot().attempt == 1, "ambiguous_loss_not_charged_to_new_attempt");
        fixture_observe(true, false, 0, -60, profile);
        fixture_emit(WIFI_EVENT, WIFI_EVENT_STA_CONNECTED, NULL, 0); fixture_step(0);
        fixture_emit(WIFI_EVENT, WIFI_EVENT_STA_DISCONNECTED, NULL, 0); fixture_step(0);
        CHECK(snapshot().phase == NETWORK_CONNECTING && snapshot().attempt == 1, "old_loss_during_current_dhcp_does_not_charge_attempt");
        fixture_observe(true, true, 0x05060708, -60, profile);
        fixture_emit(IP_EVENT, IP_EVENT_STA_GOT_IP, &foreign, 0x05060708); fixture_step(0); CHECK(!snapshot().online, "foreign_netif_ip_ignored");
        fixture_emit(IP_EVENT, IP_EVENT_STA_GOT_IP, &station, 0x01020304); fixture_step(0); CHECK(!snapshot().online, "old_ip_payload_ignored");
        online_current(0x05060708);
        fixture_emit(IP_EVENT, IP_EVENT_STA_LOST_IP, NULL, 0); fixture_step(0);
        CHECK(snapshot().online && snapshot().ipv4 == 0x05060708 && snapshot().profile_index == profile, "queued_loss_does_not_destroy_live_current_link");
    } else if (!strcmp(name, "snapshot-lock")) {
        start(1); first_connect(); online_current(0x01020304);
        network_snapshot_t view, old; memset(&view, 0xa5, sizeof(view)); old = view;
        fixture_lock_snapshot(true);
        CHECK(network_runtime_snapshot(&view, 1) == ESP_ERR_TIMEOUT && !memcmp(&view, &old, sizeof(view)), "timed_out_snapshot_unchanged");
        fixture_lock_snapshot(false); CHECK(snapshot().online, "snapshot_lock_recovery");
    } else if (!strcmp(name, "rssi") || !strcmp(name, "rssi-late")) {
        bool late = !strcmp(name, "rssi-late"); start(1); first_connect(); online_current(0x01020304);
        fixture_step(1000000); CHECK(snapshot().rssi_age_ms == 1000, "rssi_age_from_actual_clock");
        if (late) {
            fixture_block_ap_info(); fixture_release_step(1000000); fixture_wait_ap_info();
            fixture_observe(false, false, 0, 0, 0); fixture_emit(WIFI_EVENT, WIFI_EVENT_STA_DISCONNECTED, NULL, 0);
            CHECK(!snapshot().online && !snapshot().rssi_valid && !snapshot().ipv4, "pending_loss_masks_inflight_rssi");
            fixture_release_ap_info(); fixture_wait_parked();
        } else {
            fixture_observe(true, true, 0x01020304, -72, 0); fixture_step(1000000);
            CHECK(snapshot().rssi == -72 && snapshot().rssi_age_ms == 0, "actual_periodic_rssi_update");
            fixture_fail_api(API_AP_INFO, 1, ESP_FAIL); fixture_step(2000000);
        }
        CHECK(!snapshot().rssi_valid && !snapshot().rssi, "failed_or_late_rssi_invalidated");
        if (late) CHECK(!snapshot().online && !snapshot().ipv4, "late_rssi_does_not_restore_lost_link");
        else {
            CHECK(snapshot().online && snapshot().ipv4 == 0x01020304, "transient_rssi_error_preserves_observed_link");
            fixture_step(2000000); CHECK(snapshot().rssi_valid && snapshot().rssi == -72, "rssi_recovers_after_transient_query_error");
        }
    } else if (!strcmp(name, "projection-lock")) {
        start(1); first_connect(); CHECK(xSemaphoreTake(state.lock, 0), "hold_native_state_lock");
        online_current(0x01020304); CHECK(snapshot().online, "authoritative_view_survives_projection_failure");
        xSemaphoreGive(state.lock); fixture_step(0);
        native_state_t projected; native_state_snapshot(&state, &projected);
        CHECK(projected.ipv4 == 0x01020304 && projected.wifi_rssi_valid, "failed_projection_retried");
    } else if (!strcmp(name, "pending-publisher-stop")) {
        start(1); fixture_block_send(); pthread_t callback;
        CHECK(!pthread_create(&callback, NULL, blocked_callback, NULL), "publisher_thread"); fixture_wait_send();
        fixture_driver_stopped();
        CHECK(network_runtime_stop(2) == ESP_ERR_TIMEOUT && fixture_stats().queues == 1, "inflight_callback_retains_objects");
        fixture_release_send(); CHECK(!pthread_join(callback, NULL), "publisher_join");
    } else if (!strcmp(name, "unregister-running")) {
        start(1); first_connect(); fixture_driver_stopped(); fixture_fail_api(API_UNREGISTER, 1, ESP_FAIL);
        CHECK(network_runtime_stop(1000) == ESP_FAIL, "unregister_failure_returned"); fixture_join();
        fixture_stats_t s = fixture_stats();
        CHECK(s.queues == 1 && s.events == 1 && s.ap_netifs == 1 && s.registrations == 1, "failed_unregister_retains_callback_objects");
        fixture_emit(WIFI_EVENT, WIFI_EVENT_STA_DISCONNECTED, NULL, 0);
        CHECK(network_runtime_start(&state, &station, &profiles) == ESP_ERR_INVALID_STATE, "retained_owner_cannot_restart");
    } else if (!strcmp(name, "concurrent-stop")) {
        start(1); first_connect(); fixture_driver_stopped(); fixture_block_unregister(); pthread_t stopping;
        CHECK(!pthread_create(&stopping, NULL, concurrent_stop, NULL), "stop_thread_create"); fixture_wait_unregister();
        CHECK(network_runtime_stop(1000) == ESP_ERR_INVALID_STATE, "concurrent_stop_excluded");
        network_snapshot_t view, old; memset(&view, 0xa5, sizeof(view)); old = view;
        CHECK(network_runtime_snapshot(&view, 0) == ESP_ERR_INVALID_STATE && !memcmp(&view, &old, sizeof(view)), "closed_gate_rejects_new_snapshot");
        fixture_emit(WIFI_EVENT, WIFI_EVENT_STA_DISCONNECTED, NULL, 0);
        fixture_release_unregister(); CHECK(!pthread_join(stopping, NULL) && atomic_load(&stop_result) == ESP_OK, "first_stop_finishes_once");
    } else if (!strcmp(name, "cleanup-poison")) {
        start(1); first_connect(); fixture_driver_stopped(); fixture_fail_api(API_CLEAR, 1, ESP_FAIL);
        CHECK(network_runtime_stop(1000) == ESP_FAIL, "netif_cleanup_error_reported"); fixture_join();
        fixture_stats_t retained = fixture_stats();
        CHECK(retained.queues == 1 && retained.events == 1 && retained.ap_netifs == 1 && !retained.registrations, "poisoned_netif_retains_owner_storage");
        CHECK(network_runtime_stop(1000) == ESP_ERR_INVALID_STATE &&
              fixture_stats().api_calls[API_CLEAR] == retained.api_calls[API_CLEAR], "poisoned_cleanup_never_retried");
        CHECK(network_runtime_start(&state, &station, &profiles) == ESP_ERR_INVALID_STATE, "poisoned_owner_not_reinitialized");
        vSemaphoreDelete(state.lock); printf("PASS:%s\n", name); return 0;
    } else if (!strcmp(name, "concurrent")) {
        start(1); first_connect(); online_current(0x01020304); pthread_t threads[6];
        for (uintptr_t i = 0; i < 6; ++i) CHECK(!pthread_create(&threads[i], NULL, publisher, (void *)i), "concurrent_publisher_create");
        for (unsigned i = 0; i < 200; ++i) fixture_step(100000);
        for (unsigned i = 0; i < 6; ++i) CHECK(!pthread_join(threads[i], NULL), "concurrent_publisher_join");
        fixture_step(0); (void)snapshot();
    } else if (!strcmp(name, "power-intent")) {
        native_network_power_accept(UINT32_MAX, true); start(0);
        network_snapshot_t view = snapshot();
        CHECK(view.power.generation == UINT32_MAX && view.power.desired_active &&
            view.power.applied_valid && view.power.applied_active && fixture_stats().power_active,
            "prestartup_audio_intent_preserved");
        native_network_power_finish(UINT32_MAX);
        CHECK(!snapshot().power.desired_active && fixture_stats().power_active, "intent_does_not_call_driver");
        fixture_step(0); CHECK(!fixture_stats().power_active, "finish_returns_modem_sleep");
        native_network_power_accept(0, true);
        native_network_power_finish(UINT32_MAX); native_network_power_receive(UINT32_MAX);
        fixture_step(0); CHECK(fixture_stats().power_active && snapshot().power.generation == 0,
            "stale_finish_and_begin_cannot_replace_wrap_generation");
        native_network_power_finish(0); fixture_step(0);
        native_network_power_receive(0); fixture_step(0);
        CHECK(fixture_stats().power_active, "same_generation_receive_retry_reactivates");
        native_network_power_accept(1, false); native_network_power_receive(0); fixture_step(0);
        CHECK(!fixture_stats().power_active && !snapshot().power.desired_active, "late_receive_cannot_override_stop");
    } else if (!strcmp(name, "power-errors")) {
        start(0); fixture_fail_api(API_POWER, UINT_MAX, ESP_FAIL);
        unsigned before = fixture_stats().api_calls[API_POWER];
        native_network_power_accept(1, true); fixture_step(0);
        CHECK(snapshot().power.attempts == 1, "power_failure_attempt_count");
        fixture_step(249999); CHECK(fixture_stats().api_calls[API_POWER] == before + 1, "power_retry_delay");
        fixture_step(1); fixture_step(250000); fixture_step(5000000);
        network_snapshot_t view = snapshot();
        CHECK(fixture_stats().api_calls[API_POWER] == before + 3 && view.power.attempts == 3 &&
            view.power.last_error == ESP_FAIL && view.power.desired_active && !view.power.applied_active,
            "power_failures_bounded_and_visible");
        fixture_fail_api(API_POWER, 0, ESP_OK); native_network_power_accept(2, true); fixture_step(0);
        view = snapshot();
        CHECK(view.power.applied_valid && view.power.applied_active && view.power.last_error == ESP_OK &&
            view.power.applied_revision == view.power.desired_revision, "new_command_rearms_failed_policy");
    } else if (!strcmp(name, "power-call-race") || !strcmp(name, "power-stale-error")) {
        bool fail = !strcmp(name, "power-stale-error");
        start(0); native_network_power_accept(1, true);
        if (fail) fixture_fail_api(API_POWER, 1, ESP_FAIL);
        fixture_block_power(); fixture_release_step(0); fixture_wait_power();
        native_network_power_accept(2, fail);
        native_network_power_finish(1);
        CHECK(snapshot().power.generation == 2 && snapshot().power.desired_active == fail,
            "new_intent_not_blocked_by_driver_call");
        fixture_release_power(); fixture_wait_parked();
        CHECK(snapshot().power.attempts == 0 && snapshot().power.last_error == ESP_OK,
            "stale_result_does_not_charge_new_revision");
        fixture_step(0); network_snapshot_t view = snapshot();
        CHECK(view.power.applied_valid && view.power.applied_active == fail &&
            view.power.applied_revision == view.power.desired_revision && fixture_stats().power_active == fail,
            "next_owner_step_reconciles_latest_power");
    } else if (!strcmp(name, "clock-limit")) {
        fixture_set_clock(INT64_MAX - 500000); start(5); first_connect(); fixture_step(400000);
        CHECK(esp_timer_get_time() == INT64_MAX && snapshot().phase == NETWORK_AP_IDLE && snapshot().ap_enabled, "saturated_deadlines_do_not_wrap");
        fixture_driver_stopped();
        CHECK(network_runtime_stop(1000) == ESP_ERR_TIMEOUT && fixture_stats().queues == 1, "saturated_cleanup_retains_until_owner_exits");
        fixture_step(0);
    } else if (!strcmp(name, "invalid-input")) {
        make_profiles(1); fixture_stats_t before = fixture_stats();
        CHECK(network_runtime_start(NULL, &station, &profiles) == ESP_ERR_INVALID_ARG, "null_state_rejected");
        CHECK(network_runtime_start(&state, NULL, &profiles) == ESP_ERR_INVALID_ARG, "null_station_rejected");
        CHECK(network_runtime_start(&state, &station, NULL) == ESP_ERR_INVALID_ARG, "null_table_rejected");
        profiles.count = 6; CHECK(network_runtime_start(&state, &station, &profiles) == ESP_ERR_INVALID_ARG, "six_profiles_rejected");
        make_profiles(1); memset(profiles.rows[0].ssid, 'x', sizeof(profiles.rows[0].ssid));
        CHECK(network_runtime_start(&state, &station, &profiles) == ESP_ERR_INVALID_ARG, "unterminated_ssid_rejected");
        make_profiles(1); memset(profiles.rows[0].password, 'x', sizeof(profiles.rows[0].password));
        CHECK(network_runtime_start(&state, &station, &profiles) == ESP_ERR_INVALID_ARG && !fixture_stats().tasks &&
              fixture_stats().semaphores == before.semaphores, "invalid_input_has_no_lifecycle_side_effects");
    } else if (!strncmp(name, "rollback-", 9)) {
        const char *kind = name + 9; make_profiles(1);
        if (!strcmp(kind, "queue")) fixture_fail_alloc(1);
        else if (!strcmp(kind, "mutex")) fixture_fail_alloc(2);
        else if (!strcmp(kind, "event")) fixture_fail_alloc(3);
        else if (!strcmp(kind, "ap-netif")) fixture_fail_alloc(4);
        else if (!strcmp(kind, "mac")) fixture_fail_api(API_MAC, 1, ESP_FAIL);
        else if (!strcmp(kind, "mode-ap")) fixture_fail_api(API_MODE, 1, ESP_FAIL);
        else if (!strcmp(kind, "mode-sta")) fixture_fail_api(API_MODE, 2, ESP_FAIL);
        else if (!strcmp(kind, "ap-config")) fixture_fail_api(API_AP_CONFIG, 1, ESP_FAIL);
        else if (!strcmp(kind, "ap-attach")) fixture_fail_api(API_ATTACH, 1, ESP_FAIL);
        else if (!strcmp(kind, "ap-handlers")) fixture_fail_api(API_DEFAULT_HANDLERS, 1, ESP_FAIL);
        else if (!strcmp(kind, "wifi-handler")) fixture_fail_api(API_REGISTER, 1, ESP_FAIL);
        else if (!strcmp(kind, "ip-handler")) fixture_fail_api(API_REGISTER, 2, ESP_FAIL);
        else if (!strcmp(kind, "task")) fixture_fail_task(true);
        else if (!strcmp(kind, "unregister")) { fixture_fail_task(true); fixture_fail_api(API_UNREGISTER, 1, ESP_FAIL); }
        else CHECK(false, "known_rollback_case");
        esp_err_t result = network_runtime_start(&state, &station, &profiles);
        CHECK(result != ESP_OK, "startup_failure_reported");
        fixture_stats_t s = fixture_stats();
        if (!strcmp(kind, "unregister")) {
            CHECK(s.queues == 1 && s.events == 1 && s.registrations == 1 && s.ap_netifs == 1, "startup_unregister_failure_retains_objects");
            fixture_emit(WIFI_EVENT, WIFI_EVENT_STA_DISCONNECTED, NULL, 0);
            CHECK(network_runtime_start(&state, &station, &profiles) == ESP_ERR_INVALID_STATE, "retained_start_failure_not_recreated");
        } else CHECK(!s.queues && s.semaphores == 1 && !s.events && !s.ap_netifs && !s.registrations, "failed_start_rolls_back_owned_resources");
    } else CHECK(false, "known_case");
    stopped(); printf("PASS:%s\n", name); return 0;
}
