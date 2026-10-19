#include "platform.h"
#include "native_network_power.h"

static pthread_mutex_t driver_lock = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t driver_changed = PTHREAD_COND_INITIALIZER;
static bool driver_mode, block_apply, apply_entered, release_apply;
static unsigned calls;
static esp_err_t apply_error;
static atomic_bool stress_done;
static pthread_t rssi_thread;
static atomic_bool c3_running;
static _Thread_local bool in_rssi_thread;
static pthread_t driver_thread;
static bool driver_thread_known;

static struct timespec until_ms(unsigned ms) {
    struct timespec t; CHECK(!clock_gettime(CLOCK_REALTIME, &t), "wall_clock");
    t.tv_sec += ms / 1000; t.tv_nsec += (long)(ms % 1000) * 1000000L;
    if (t.tv_nsec >= 1000000000L) { ++t.tv_sec; t.tv_nsec -= 1000000000L; }
    return t;
}
static void changed_wait(pthread_cond_t *condition, pthread_mutex_t *mutex) {
    struct timespec end = until_ms(5000);
    CHECK(!pthread_cond_timedwait(condition, mutex, &end), "barrier_progress");
}
static esp_err_t apply(void *context, bool active) {
    CHECK(context == &calls, "apply_context_forwarded");
    pthread_mutex_lock(&driver_lock); ++calls;
    if (atomic_load(&c3_running)) {
        CHECK(in_rssi_thread, "only_rssi_task_calls_driver");
        if (driver_thread_known) CHECK(pthread_equal(pthread_self(), driver_thread), "same_rssi_driver_caller");
        else { driver_thread_known = true; driver_thread = pthread_self(); }
    }
    esp_err_t result = apply_error;
    if (block_apply) {
        block_apply = false; apply_entered = true; pthread_cond_broadcast(&driver_changed);
        while (!release_apply) changed_wait(&driver_changed, &driver_lock);
    }
    if (result == ESP_OK) driver_mode = active;
    pthread_mutex_unlock(&driver_lock); return result;
}
static void poll(int64_t now) { native_network_power_poll(now, apply, &calls); }
static native_network_power_snapshot_t snapshot(void) {
    native_network_power_snapshot_t view; native_network_power_snapshot(&view);
    CHECK(view.attempts <= 3, "bounded_attempts"); return view;
}
static unsigned call_count(void) { pthread_mutex_lock(&driver_lock); unsigned n = calls; pthread_mutex_unlock(&driver_lock); return n; }
static bool mode(void) { pthread_mutex_lock(&driver_lock); bool active = driver_mode; pthread_mutex_unlock(&driver_lock); return active; }
static void error(esp_err_t result) { pthread_mutex_lock(&driver_lock); apply_error = result; pthread_mutex_unlock(&driver_lock); }
static void arm(void) { pthread_mutex_lock(&driver_lock); block_apply = true; apply_entered = release_apply = false; pthread_mutex_unlock(&driver_lock); }
static void await_apply(void) { pthread_mutex_lock(&driver_lock); while (!apply_entered) changed_wait(&driver_changed, &driver_lock); pthread_mutex_unlock(&driver_lock); }
static void release(void) { pthread_mutex_lock(&driver_lock); release_apply = true; pthread_cond_broadcast(&driver_changed); pthread_mutex_unlock(&driver_lock); }
static void *blocked_poll(void *unused) { (void)unused; poll(1000000); return NULL; }
static void launch_poll(pthread_t *thread) { CHECK(!pthread_create(thread, NULL, blocked_poll, NULL), "poll_thread_create"); await_apply(); }

// Actual C3 function bodies below use SDK field models and a clock/delay seam.
typedef enum { WIFI_PS_NONE, WIFI_PS_MIN_MODEM } wifi_ps_type_t;
typedef struct { int8_t rssi; } wifi_ap_record_t;
typedef struct { int8_t rssi; } native_state_t;
static native_state_t state, *s_state = &state;
static atomic_bool s_stopping_for_sleep;
static pthread_mutex_t clock_lock = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t clock_changed = PTHREAD_COND_INITIALIZER;
static atomic_int_fast64_t now_us;
static bool task_parked, task_exit;
static unsigned lap, awaited_lap, permits, rssi_queries, rssi_publications;
static esp_err_t stop_error;
#define WIFI_RSSI_INTERVAL_MS 2000
static int64_t esp_timer_get_time(void) { return atomic_load(&now_us); }
static esp_err_t esp_wifi_set_ps(wifi_ps_type_t policy) { return apply(&calls, policy == WIFI_PS_NONE); }
static esp_err_t esp_wifi_stop(void) { return stop_error; }
static esp_err_t esp_wifi_sta_get_ap_info(wifi_ap_record_t *ap) { ++rssi_queries; ap->rssi = -55; return ESP_OK; }
static void native_state_set_wifi_rssi(native_state_t *out, int8_t rssi) { ++rssi_publications; out->rssi = rssi; }
static void vTaskDelay(unsigned ticks) {
    CHECK(ticks == 100 && in_rssi_thread, "c3_policy_poll_period");
    pthread_mutex_lock(&clock_lock); task_parked = true; ++lap; pthread_cond_broadcast(&clock_changed);
    while (!permits && !task_exit) changed_wait(&clock_changed, &clock_lock);
    bool exit = task_exit; if (permits) --permits; task_parked = false;
    pthread_mutex_unlock(&clock_lock); if (exit) pthread_exit(NULL);
}
#include "c3-power.inc"
static void *run_rssi(void *unused) { in_rssi_thread = true; rssi_task(unused); return NULL; }
static void await_park(void) {
    pthread_mutex_lock(&clock_lock);
    while (!(task_parked && lap >= awaited_lap)) changed_wait(&clock_changed, &clock_lock);
    pthread_mutex_unlock(&clock_lock);
}
static void start_rssi(bool wait) {
    atomic_store(&c3_running, true); awaited_lap = 1;
    CHECK(!pthread_create(&rssi_thread, NULL, run_rssi, NULL), "actual_rssi_task_thread");
    if (wait) await_park();
}
static void tick(int64_t delta) {
    await_park(); pthread_mutex_lock(&clock_lock); awaited_lap = lap + 1;
    int64_t old = atomic_load(&now_us); CHECK(delta >= 0 && old <= INT64_MAX - delta, "clock_step_bounds");
    atomic_store(&now_us, old + delta); ++permits; pthread_cond_broadcast(&clock_changed);
    pthread_mutex_unlock(&clock_lock); await_park();
}
static void stop_rssi(void) {
    pthread_mutex_lock(&clock_lock); task_exit = true; pthread_cond_broadcast(&clock_changed); pthread_mutex_unlock(&clock_lock);
    CHECK(!pthread_join(rssi_thread, NULL), "rssi_task_join"); atomic_store(&c3_running, false);
}
static void *stress_publisher(void *argument) {
    uintptr_t publisher = (uintptr_t)argument;
    for (unsigned i = 0; i < 2000; ++i) {
        native_network_power_accept((uint32_t)(publisher * 10000 + i), (i & 1) != 0);
        native_network_power_snapshot_t view = snapshot();
        native_network_power_receive(view.generation);
        native_network_power_finish(view.generation - 1U);
    }
    return NULL;
}
static void *stress_snapshot(void *unused) { (void)unused; for (unsigned i = 0; i < 5000; ++i) (void)snapshot(); return NULL; }
static void *stress_owner(void *unused) {
    (void)unused; int64_t now = 0;
    while (!atomic_load(&stress_done)) { poll(now); now += 100000; }
    for (unsigned i = 0; i < 3; ++i) poll(now + (int64_t)i * 250000);
    return NULL;
}

int main(int argc, char **argv) {
    CHECK(argc == 2, "case_argument"); const char *name = argv[1];
    if (!strcmp(name, "idle-known")) {
        poll(0); CHECK(call_count() == 1 && !mode() && snapshot().applied_valid, "initial_idle_policy_known");
        native_network_power_accept(1, false); poll(100000);
        CHECK(call_count() == 1 && snapshot().applied_revision == snapshot().desired_revision, "known_idle_no_redundant_call");
    } else if (!strcmp(name, "generation-equality") || !strcmp(name, "generation-wrap")) {
        bool wrap = !strcmp(name, "generation-wrap"); uint32_t old = wrap ? UINT32_MAX : 10, current = old + 1U;
        native_network_power_accept(old, true); poll(0); native_network_power_accept(current, true);
        native_network_power_snapshot_t before = snapshot(); native_network_power_finish(old);
        CHECK(snapshot().desired_active && snapshot().desired_revision == before.desired_revision, "stale_finish_ignored");
        native_network_power_accept(current, false); before = snapshot(); native_network_power_receive(old);
        CHECK(!snapshot().desired_active && snapshot().generation == current && snapshot().desired_revision == before.desired_revision, "stale_receive_ignored");
        native_network_power_receive(current); CHECK(snapshot().desired_active, "current_receive_accepted");
        native_network_power_finish(current); CHECK(!snapshot().desired_active, "current_finish_accepted");
    } else if (!strcmp(name, "same-generation-retry")) {
        native_network_power_accept(7, true); poll(0); native_network_power_finish(7); poll(100000);
        CHECK(!mode(), "same_generation_backoff_idle"); native_network_power_receive(7); poll(200000);
        CHECK(mode() && call_count() == 3, "same_generation_receive_reactivates");
        unsigned revision = snapshot().desired_revision; native_network_power_receive(7); poll(300000);
        CHECK(call_count() == 3 && snapshot().desired_revision == revision, "duplicate_receive_no_extra_revision");
    } else if (!strcmp(name, "failure-budget")) {
        native_network_power_accept(1, true); error(ESP_FAIL); poll(0);
        CHECK(snapshot().attempts == 1 && snapshot().last_error == ESP_FAIL, "first_failure_recorded");
        poll(249999); CHECK(call_count() == 1, "retry_waits_250ms"); poll(250000); poll(499999);
        CHECK(call_count() == 2, "second_retry_wait"); poll(500000); poll(1000000); poll(INT64_MAX);
        CHECK(call_count() == 3 && snapshot().attempts == 3, "three_attempts_per_revision");
        native_network_power_accept(2, true); error(ESP_OK); poll(1000001);
        CHECK(call_count() == 4 && mode() && snapshot().last_error == ESP_OK, "new_revision_gets_new_budget");
    } else if (!strcmp(name, "blocked-success") || !strcmp(name, "blocked-error") || !strcmp(name, "stale-error-budget")) {
        bool success = !strcmp(name, "blocked-success"), same = !strcmp(name, "stale-error-budget");
        poll(0); native_network_power_accept(1, true); error(success ? ESP_OK : ESP_FAIL); arm(); pthread_t thread; launch_poll(&thread);
        native_network_power_accept(2, same); native_network_power_finish(0);
        CHECK(snapshot().generation == 2 && snapshot().attempts == 0, "control_snapshot_unblocked_during_driver_call");
        release(); CHECK(!pthread_join(thread, NULL), "blocked_poll_join");
        CHECK(snapshot().attempts == 0 && snapshot().last_error == ESP_OK, "stale_error_preserves_new_budget");
        if (success) CHECK(snapshot().applied_active && mode(), "stale_success_recorded_for_repair");
        error(ESP_OK); unsigned previous = call_count(); poll(1000001);
        CHECK(mode() == same && snapshot().applied_active == same && snapshot().applied_revision == snapshot().desired_revision, "latest_intent_repaired");
        CHECK(call_count() == previous + (success || same ? 1U : 0U), "stale_result_does_not_delay_new_policy");
    } else if (!strcmp(name, "invalidate-success") || !strcmp(name, "invalidate-error")) {
        bool success = !strcmp(name, "invalidate-success"); native_network_power_accept(UINT32_MAX, true);
        error(success ? ESP_OK : ESP_FAIL); arm(); pthread_t thread; launch_poll(&thread);
        native_network_power_invalidate(); CHECK(snapshot().desired_active && snapshot().generation == UINT32_MAX, "invalidate_preserves_intent");
        release(); CHECK(!pthread_join(thread, NULL), "invalidated_poll_join");
        CHECK(!snapshot().applied_valid && snapshot().attempts == 0, "invalidated_driver_result_ignored");
        error(ESP_OK); poll(1000001); CHECK(mode() && snapshot().applied_valid && call_count() == 2, "new_driver_policy_reapplied");
    } else if (!strcmp(name, "clock-limit")) {
        native_network_power_accept(1, true); error(ESP_FAIL); poll(INT64_MAX - 100);
        poll(INT64_MAX - 1); CHECK(call_count() == 1, "saturated_retry_deadline_no_wrap");
        poll(INT64_MAX); poll(INT64_MAX); poll(INT64_MAX);
        CHECK(call_count() == 3 && snapshot().attempts == 3, "saturated_clock_retry_budget_finite");
    } else if (!strcmp(name, "invalid-poll")) {
        native_network_power_accept(1, true); poll(-1); native_network_power_poll(0, NULL, NULL); native_network_power_snapshot(NULL);
        CHECK(!call_count() && snapshot().attempts == 0, "invalid_poll_has_no_effect");
    } else if (!strcmp(name, "concurrent")) {
        pthread_t owner, publishers[4], observer;
        CHECK(!pthread_create(&owner, NULL, stress_owner, NULL), "stress_owner_create");
        for (uintptr_t i = 0; i < 4; ++i) CHECK(!pthread_create(&publishers[i], NULL, stress_publisher, (void *)i), "publisher_create");
        CHECK(!pthread_create(&observer, NULL, stress_snapshot, NULL), "observer_create");
        for (unsigned i = 0; i < 4; ++i) CHECK(!pthread_join(publishers[i], NULL), "publisher_join");
        CHECK(!pthread_join(observer, NULL), "observer_join"); native_network_power_accept(0xabcdef01, true);
        atomic_store(&stress_done, true); CHECK(!pthread_join(owner, NULL), "stress_owner_join");
        CHECK(mode() && snapshot().generation == 0xabcdef01 && snapshot().applied_active &&
              snapshot().applied_revision == snapshot().desired_revision, "concurrent_publishers_converge");
    } else if (!strcmp(name, "c3-periods") || !strcmp(name, "c3-sleep-error")) {
        bool sleep_error = !strcmp(name, "c3-sleep-error"); network_service_audio_accept(1, true);
        CHECK(!call_count(), "c3_intent_does_not_call_driver"); start_rssi(true);
        CHECK(call_count() == 1 && mode() && rssi_queries == 1, "actual_c3_owner_first_poll");
        network_service_audio_finish(1); tick(100000);
        CHECK(!mode() && call_count() == 2 && rssi_queries == 1, "c3_100ms_power_independent_of_rssi");
        tick(1900000); CHECK(rssi_queries == 2 && rssi_publications == 2, "c3_rssi_2s_period");
        stop_error = sleep_error ? ESP_FAIL : ESP_OK;
        CHECK(network_service_prepare_sleep() == stop_error, "actual_prepare_sleep_result");
        network_service_audio_accept(2, true); unsigned previous = call_count(); tick(100000);
        CHECK(call_count() == previous + (sleep_error ? 1U : 0U), "sleep_guard_skips_new_driver_calls");
        if (!sleep_error) { tick(2000000); CHECK(rssi_queries == 2, "sleep_guard_skips_rssi"); }
        stop_rssi();
    } else if (!strcmp(name, "c3-blocked")) {
        network_service_audio_accept(1, true); arm(); start_rssi(false); await_apply();
        network_service_audio_accept(2, false); CHECK(call_count() == 1, "c3_new_intent_no_direct_sdk_call");
        release(); await_park(); CHECK(mode(), "c3_stale_sdk_call_observed"); tick(100000);
        CHECK(!mode() && snapshot().generation == 2 && snapshot().applied_revision == snapshot().desired_revision, "c3_next_owner_step_repairs_latest_intent");
        stop_rssi();
    } else CHECK(false, "known_case");
    printf("PASS:%s\n", name); return 0;
}
