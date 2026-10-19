/* Actual historical stream/decode/output loops; only call/SDK boundaries pause. */
#include "c3_maintenance_platform.h"
#include <sys/resource.h>

static atomic_bool baseline_eof_seen;
static pthread_mutex_t power_lock = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t power_changed = PTHREAD_COND_INITIALIZER;
static unsigned power_phase;
static bool release_before, release_after, boundary_claimed, boundary_disabled;
static bool late_true;
static uint32_t guarded_generation;
static atomic_int applied_power;
static atomic_uint power_calls;
static void maintenance_pause_requested(void);
static uint32_t actual_generation(void);
static void barrier_hit(const char *name) { (void)name; }
#include "focused-seams.inc"

typedef enum { WIFI_PS_NONE, WIFI_PS_MIN_MODEM } wifi_ps_type_t;
static esp_err_t esp_wifi_set_ps(wifi_ps_type_t mode) {
    atomic_store(&applied_power, mode);
    atomic_fetch_add(&power_calls, 1);
    return ESP_OK;
}
#include "network-power.inc"

// The unchanged audio body calls this boundary before the unchanged network
// body. It forwards the exact argument and result; it never assigns intent.
static esp_err_t power_call_boundary(bool active) {
    bool selected = false;
    pthread_mutex_lock(&power_lock);
    if (!boundary_disabled && !boundary_claimed && role == ROLE_STREAM &&
        (late_true ? active : !active && atomic_load(&baseline_eof_seen))) {
        boundary_claimed = selected = true;
        guarded_generation = actual_generation();
        power_phase = 1;
        pthread_cond_broadcast(&power_changed);
        while (!release_before) pthread_cond_wait(&power_changed, &power_lock);
    }
    pthread_mutex_unlock(&power_lock);
    esp_err_t result = network_service_set_streaming(active);
    if (selected) {
        pthread_mutex_lock(&power_lock);
        power_phase = 2;
        pthread_cond_broadcast(&power_changed);
        while (!release_after) pthread_cond_wait(&power_changed, &power_lock);
        pthread_mutex_unlock(&power_lock);
    }
    return result;
}

#include "adaptive.inc"
#define network_service_set_streaming power_call_boundary
#include "audio.inc"
#undef network_service_set_streaming
#undef malloc
#undef realloc
#undef free
#include "state.inc"

static uint32_t actual_generation(void) { return atomic_load(&s_generation); }
static void maintenance_pause_requested(void) { assert(maintenance_active()); }
static void await_phase(unsigned phase) {
    struct timespec end = until_ms(5000);
    pthread_mutex_lock(&power_lock);
    while (power_phase < phase) {
        int error = pthread_cond_timedwait(&power_changed, &power_lock, &end);
        assert(error == 0);
    }
    pthread_mutex_unlock(&power_lock);
}
static void release_first(void) {
    pthread_mutex_lock(&power_lock); release_before = true;
    pthread_cond_broadcast(&power_changed); pthread_mutex_unlock(&power_lock);
}
static void release_second(void) {
    pthread_mutex_lock(&power_lock); boundary_disabled = true; release_after = true;
    pthread_cond_broadcast(&power_changed); pthread_mutex_unlock(&power_lock);
}
static int safety(bool condition, const char *name) {
    if (!condition) { fprintf(stderr, "SAFETY_FAILURE:%s\n", name); return 42; }
    return 0;
}
static void cleanup(native_state_t *state) {
    audio_maintenance_token_t token = {0};
    assert(audio_service_maintenance_begin(2000, &token) == ESP_OK);
    assert(token.epoch && !http_clients && !decoder_handles && !driver.allocated);
    atomic_store(&stop_threads, true);
    for (unsigned i = 0; i < 3; ++i) {
        assert(!pthread_join(test_tasks[i]->thread, NULL));
        vSemaphoreDelete(test_tasks[i]->notify); free(test_tasks[i]);
    }
    adaptive_input_destroy(s_encoded); vRingbufferDelete(s_pcm);
    vQueueDelete(s_commands); vSemaphoreDelete(s_control_lock); vSemaphoreDelete(state->lock);
    for (unsigned i = 0; i < 64; ++i) if (allocations[i].p) {
        assert(allocations[i].owner == ROLE_STREAM); owner_free(allocations[i].p);
    }
}

int main(int argc, char **argv) {
    struct rlimit no_core = {0, 0}; assert(!setrlimit(RLIMIT_CORE, &no_core));
    assert(argc == 2);
    bool sequential = !strcmp(argv[1], "sequential");
    late_true = !strcmp(argv[1], "late-true-after-stop");
    assert(sequential || late_true || !strcmp(argv[1], "stale-finish-after-play"));
    native_state_t state;
    native_state_init(&state);
    state.web_ready = true; state.network_mode = NATIVE_NETWORK_CLIENT;
    assert(audio_service_start(&state) == ESP_OK);
    assert(audio_service_play("http://old.invalid/radio", NATIVE_CODEC_FLAC) == ESP_OK);
    await_phase(1);
    uint32_t old_generation = guarded_generation;
    assert(old_generation != 0 && actual_generation() == old_generation);
    if (!late_true) assert(atomic_load(&baseline_eof_seen) && !http_clients);
    if (sequential) {
        release_first(); await_phase(2);
        assert(actual_generation() == old_generation && atomic_load(&applied_power) == WIFI_PS_MIN_MODEM);
        release_second();
        assert(audio_service_play("http://new.invalid/radio", NATIVE_CODEC_FLAC) == ESP_OK);
        assert(actual_generation() == old_generation + 1U && atomic_load(&applied_power) == WIFI_PS_NONE);
        cleanup(&state);
        puts("PASS:sequential_old_finish_then_new_play"); return 0;
    }
    if (late_true) {
        audio_service_stop();
        assert(actual_generation() == old_generation + 1U && atomic_load(&applied_power) == WIFI_PS_MIN_MODEM);
    } else {
        assert(audio_service_play("http://new.invalid/radio", NATIVE_CODEC_FLAC) == ESP_OK);
        assert(s_last_command_valid && s_last_generation == old_generation + 1U);
        assert(actual_generation() == old_generation + 1U && atomic_load(&applied_power) == WIFI_PS_NONE);
    }
    release_first(); await_phase(2);
    fprintf(stderr, "TRACE:old_guard_generation=%u current_generation=%u driver_mode=%d power_calls=%u\n",
            old_generation, actual_generation(), atomic_load(&applied_power), atomic_load(&power_calls));
    assert(actual_generation() == old_generation + 1U);
    return late_true ? safety(atomic_load(&applied_power) == WIFI_PS_MIN_MODEM,
                             "old_stream_true_cannot_override_accepted_stop")
                     : safety(atomic_load(&applied_power) == WIFI_PS_NONE,
                              "old_stream_finish_cannot_override_new_play");
}
