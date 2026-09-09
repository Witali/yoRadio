#include <assert.h>
#include <limits.h>
#include <stdbool.h>
#include "volume_scale.h"

typedef int esp_err_t;
#define ESP_OK 0
#define ESP_ERR_INVALID_STATE -1
#define ESP_ERR_TIMEOUT -2
#define pdTRUE 1
#define pdMS_TO_TICKS(ms) (ms)
static int s_lock = 1, lock_available = 1, locked;
static unsigned raw_volume, saved_volume, state_volume, dirty;
static int xSemaphoreTake(int lock, int wait) {
    assert(lock && wait == 100 && !locked);
    if (!lock_available) return 0;
    locked = 1; return pdTRUE;
}
static void xSemaphoreGive(int lock) { assert(lock && locked); locked = 0; }
static uint8_t native_audio_output_volume(void) { return raw_volume; }
static void native_audio_output_set_volume_runtime(uint8_t raw) {
    assert(locked); raw_volume = raw;
}
static void native_state_set_volume(uint8_t raw) { assert(locked); state_volume = raw; }
static void persistent_settings_set_volume_runtime(uint8_t raw) {
    assert(locked); saved_volume = raw;
}
static void mark_settings_dirty(void) { assert(locked); dirty++; }

/* REAL_CONTROLS */

int main(void) {
    assert(volume_from_percent(INT_MIN) == 0);
    assert(volume_from_percent(INT_MAX) == 254);
    assert(volume_to_percent(UINT_MAX) == 100);
    assert(volume_to_percent(160) == 63);
    assert(volume_to_percent(128) == 50);
    assert(volume_from_percent(50) == 127);
    unsigned previous = 0;
    for (int p = 0; p <= 100; ++p) {
        assert(volume_to_percent(volume_from_percent(p)) == p);
        assert(radio_control_set_volume(p) == ESP_OK);
        assert(radio_control_volume() == p);
        assert(raw_volume == volume_from_percent(p));
        assert(raw_volume == state_volume && raw_volume == saved_volume);
        assert(p == 0 || raw_volume > previous);
        previous = raw_volume;
        /* Reboot/read-back: storage remains raw and conversion is exact. */
        raw_volume = saved_volume;
        assert(radio_control_volume() == p);
        unsigned before = dirty;
        assert(radio_control_set_volume(p) == ESP_OK && dirty == before);
    }
    /* All pre-update NVS volume values must retain their exact gain until
     * a user changes the control. No eager migration or repeated rounding. */
    for (unsigned raw = 0; raw <= 254; ++raw) {
        raw_volume = saved_volume = raw;
        unsigned before = dirty;
        assert(radio_control_volume() == (raw * 100U + 127U) / 254U);
        assert(raw_volume == raw && saved_volume == raw && dirty == before);
    }
    radio_control_set_volume(0);
    for (int p = 1; p <= 100; ++p) {
        radio_control_adjust_volume(1); assert(radio_control_volume() == p);
    }
    radio_control_adjust_volume(INT_MAX); assert(radio_control_volume() == 100);
    for (int p = 99; p >= 0; --p) {
        radio_control_adjust_volume(-1); assert(radio_control_volume() == p);
    }
    radio_control_adjust_volume(INT_MIN); assert(radio_control_volume() == 0);
    radio_control_set_volume(99);
    radio_control_adjust_volume(2); assert(radio_control_volume() == 100);
    radio_control_set_volume(1);
    radio_control_adjust_volume(-2); assert(radio_control_volume() == 0);
    unsigned before = dirty;
    lock_available = 0;
    assert(radio_control_set_volume(50) == ESP_ERR_TIMEOUT);
    assert(radio_control_adjust_volume(1) == ESP_ERR_TIMEOUT);
    assert(raw_volume == 0 && dirty == before);
    s_lock = 0;
    assert(radio_control_set_volume(50) == ESP_ERR_INVALID_STATE);
    assert(radio_control_adjust_volume(1) == ESP_ERR_INVALID_STATE);
    assert(!locked);
}
