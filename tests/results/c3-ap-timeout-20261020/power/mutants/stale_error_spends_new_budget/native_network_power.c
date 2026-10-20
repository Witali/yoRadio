#include "native_network_power.h"

#include <limits.h>
#include "freertos/FreeRTOS.h"

#define POWER_RETRY_US INT64_C(250000)
#define POWER_ATTEMPTS 3U

static portMUX_TYPE s_lock = portMUX_INITIALIZER_UNLOCKED;
static native_network_power_snapshot_t s_power;
static int64_t s_next_attempt;
static uint32_t s_driver_revision;

// All callers hold s_lock. Unsigned revisions wrap like audio generations;
// no ordering comparison or lock-free 64-bit operation is required on either CPU.
static void changed(void) {
    ++s_power.desired_revision;
    s_power.attempts = 0;
    s_power.last_error = ESP_OK;
    s_next_attempt = 0;
}

void native_network_power_accept(uint32_t generation, bool active) {
    portENTER_CRITICAL(&s_lock);
    s_power.generation = generation;
    s_power.desired_active = active;
    changed();
    portEXIT_CRITICAL(&s_lock);
}

static void receive_state(uint32_t generation, bool active) {
    portENTER_CRITICAL(&s_lock);
    if (s_power.generation == generation && s_power.desired_active != active) {
        s_power.desired_active = active;
        changed();
    }
    portEXIT_CRITICAL(&s_lock);
}

void native_network_power_receive(uint32_t generation) {
    receive_state(generation, true);
}

void native_network_power_finish(uint32_t generation) {
    receive_state(generation, false);
}

void native_network_power_invalidate(void) {
    portENTER_CRITICAL(&s_lock);
    s_power.applied_valid = false;
    ++s_driver_revision;
    changed();
    portEXIT_CRITICAL(&s_lock);
}

void native_network_power_snapshot(native_network_power_snapshot_t *out) {
    if (!out) return;
    portENTER_CRITICAL(&s_lock);
    *out = s_power;
    portEXIT_CRITICAL(&s_lock);
}

void native_network_power_poll(int64_t now_us, native_network_power_apply_t apply,
                               void *context) {
    if (!apply || now_us < 0) return;
    portENTER_CRITICAL(&s_lock);
    native_network_power_snapshot_t intent = s_power;
    uint32_t driver_revision = s_driver_revision;
    if (intent.applied_valid && intent.applied_active == intent.desired_active) {
        s_power.applied_revision = intent.desired_revision;
        s_power.last_error = ESP_OK;
        portEXIT_CRITICAL(&s_lock);
        return;
    }
    if (intent.attempts >= POWER_ATTEMPTS || now_us < s_next_attempt) {
        portEXIT_CRITICAL(&s_lock);
        return;
    }
    portEXIT_CRITICAL(&s_lock);

    esp_err_t result = apply(context, intent.desired_active);

    portENTER_CRITICAL(&s_lock);
    if (driver_revision != s_driver_revision) {
        portEXIT_CRITICAL(&s_lock);
        return;
    }
    // Even a stale successful call changed the actual driver. Record that
    // applied mode so the next step repairs it for the latest desired intent.
    if (result == ESP_OK) {
        s_power.applied_active = intent.desired_active;
        s_power.applied_valid = true;
        s_power.applied_revision = intent.desired_revision;
    }
    if (true) {
        ++s_power.attempts;
        s_power.last_error = result;
        s_next_attempt = now_us > INT64_MAX - POWER_RETRY_US
            ? INT64_MAX : now_us + POWER_RETRY_US;
    }
    portEXIT_CRITICAL(&s_lock);
}
