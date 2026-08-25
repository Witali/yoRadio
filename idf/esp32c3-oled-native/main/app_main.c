#include <stdio.h>
#include <stdatomic.h>
#include <string.h>

#include "audio_service.h"
#include "board_config.h"
#include "display_settings.h"
#include "driver/gpio.h"
#include "encoder_input.h"
#include "esp_check.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "esp_spiffs.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/task.h"
#include "native_state.h"
#include "native_audio_settings.h"
#include "native_audio_output.h"
#include "network_service.h"
#include "nvs_flash.h"
#include "oled_display.h"
#include "radio_control.h"
#include "runtime_settings.h"
#include "time_service.h"
#include "web_service.h"

#define BUTTON_DEBOUNCE_MS 35
#define BUTTON_CLICK_WINDOW_MS 400
#define BUTTON_HOLD_MS 800
#define BUTTON_ACTION_RETRY_MS 100
#define BUTTON_ACTION_TIMEOUT_MS 30000
#define BUTTON_STATUS_DISPLAY_MS 2000U
#define BUTTON_EDGE_QUEUE_LENGTH 32
#define BUTTON_TASK_PRIORITY 8
#define DISPLAY_SCROLL_HOLD_MS 3500U
#define DISPLAY_SCROLL_STEP_MS 35U
#define DISPLAY_SCROLL_SEPARATOR_GLYPHS 3U
#define DISPLAY_SECONDARY_PAGE_MS 5000U
#define DISPLAY_BOOT_LOGO_MS 1500U
#define DISPLAY_HARDWARE_SCROLL_RUN_MS 4000U

static const char *const TAG = "yoradio_c3";
static native_state_t s_state;
#ifndef YORADIO_CODEC_BENCHMARK
static oled_display_t s_display;
static int64_t s_boot_logo_until_us;
typedef enum {
    BUTTON_STATUS_STOPPED,
    BUTTON_STATUS_PLAYING,
    BUTTON_STATUS_NEXT,
    BUTTON_STATUS_PREVIOUS,
} button_status_t;

static atomic_uint_fast32_t s_button_status_revision;
static atomic_uint_fast32_t s_button_status_until_ms;
static atomic_uchar s_button_status;

typedef enum {
    BUTTON_ACTION_NONE,
    BUTTON_ACTION_TOGGLE,
    BUTTON_ACTION_NEXT,
    BUTTON_ACTION_PREVIOUS,
} button_action_t;

typedef struct {
    TickType_t tick;
    bool pressed;
} button_edge_event_t;

typedef struct {
    bool raw_pressed;
    bool stable_pressed;
    bool hold_handled;
    uint8_t clicks;
    TickType_t raw_changed_at;
    TickType_t pressed_at;
    TickType_t released_at;
    button_action_t pending_action;
    TickType_t action_queued_at;
    TickType_t action_retry_at;
    bool action_deferred;
} button_state_t;

static QueueHandle_t s_button_edge_queue;

static bool button_tick_reached(TickType_t now, TickType_t deadline) {
    return (int32_t)(now - deadline) >= 0;
}

static void button_gpio_isr(void *argument) {
    (void)argument;
    button_edge_event_t event = {
        .tick = xTaskGetTickCountFromISR(),
        .pressed = gpio_get_level(BOARD_BOOT_BUTTON) == 0,
    };
    BaseType_t higher_priority_task_woken = pdFALSE;
    xQueueSendFromISR(s_button_edge_queue, &event, &higher_priority_task_woken);
    if (higher_priority_task_woken) {
        portYIELD_FROM_ISR();
    }
}

static esp_err_t execute_button_action(button_action_t action) {
    switch (action) {
        case BUTTON_ACTION_TOGGLE:
            return radio_control_toggle();
        case BUTTON_ACTION_NEXT:
            return radio_control_next();
        case BUTTON_ACTION_PREVIOUS:
            return radio_control_previous();
        default:
            return ESP_ERR_INVALID_ARG;
    }
}

static void show_button_status(button_status_t status, uint32_t now_ms) {
    atomic_store(&s_button_status, (unsigned char)status);
    atomic_store(&s_button_status_until_ms,
                 now_ms + BUTTON_STATUS_DISPLAY_MS);
    atomic_fetch_add(&s_button_status_revision, 1U);
}

static void show_button_playback_status(bool playing, uint32_t now_ms) {
    show_button_status(playing ? BUTTON_STATUS_PLAYING : BUTTON_STATUS_STOPPED,
                       now_ms);
}

static const char *button_status_text(button_status_t status) {
    switch (status) {
        case BUTTON_STATUS_PLAYING:
            return "playing";
        case BUTTON_STATUS_NEXT:
            return "next";
        case BUTTON_STATUS_PREVIOUS:
            return "prev";
        default:
            return "stopped";
    }
}

#ifdef CONFIG_YORADIO_ROTARY_ENCODER
static esp_err_t encoder_rotate_volume(int32_t delta, void *context) {
    (void)context;
    display_settings_note_activity();
    int32_t volume = (int32_t)native_audio_output_get_volume() + delta;
    if (volume < 0) volume = 0;
    if (volume > 254) volume = 254;
    native_audio_output_set_volume((uint8_t)volume);
    return ESP_OK;
}

static esp_err_t encoder_toggle_playback(void *context) {
    (void)context;
    display_settings_note_activity();
    native_state_t before;
    native_state_snapshot(&s_state, &before);
    esp_err_t result = radio_control_toggle();
    if (result == ESP_OK) {
        show_button_playback_status(
            !before.audio_running,
            (uint32_t)(esp_timer_get_time() / 1000U));
    }
    return result;
}
#endif

static void queue_button_action(button_state_t *button, button_action_t action) {
    TickType_t now = xTaskGetTickCount();
    button->pending_action = action;
    button->action_queued_at = now;
    button->action_retry_at = now;
    button->action_deferred = false;
}

static void apply_stable_button_level(button_state_t *button, bool pressed,
                                      TickType_t changed_at) {
    button->stable_pressed = pressed;
    if (pressed) {
        display_settings_note_activity();
        button->pressed_at = changed_at;
        button->hold_handled = false;
    } else if (!button->hold_handled) {
        if (button->clicks < UINT8_MAX) ++button->clicks;
        button->released_at = changed_at;
    }
}

static void process_button_gestures_until(button_state_t *button,
                                          TickType_t through) {
    TickType_t hold_at =
        button->pressed_at + pdMS_TO_TICKS(BUTTON_HOLD_MS);
    if (button->stable_pressed && !button->hold_handled &&
        button_tick_reached(through, hold_at)) {
        ESP_LOGI(TAG, "BOOT long press: previous station");
        queue_button_action(button, BUTTON_ACTION_PREVIOUS);
        button->hold_handled = true;
        button->clicks = 0;
    }

    TickType_t click_at =
        button->released_at + pdMS_TO_TICKS(BUTTON_CLICK_WINDOW_MS);
    if (!button->stable_pressed && button->clicks &&
        button_tick_reached(through, click_at)) {
        const bool next = button->clicks >= 2;
        ESP_LOGI(TAG, "%s", next ? "BOOT two clicks: next station"
                                  : "BOOT click: play/pause");
        queue_button_action(button,
                            next ? BUTTON_ACTION_NEXT : BUTTON_ACTION_TOGGLE);
        button->clicks = 0;
    }
}

static void execute_pending_button_action(button_state_t *button) {
    if (button->pending_action == BUTTON_ACTION_NONE) return;

    TickType_t now = xTaskGetTickCount();
    if (!button_tick_reached(now, button->action_retry_at)) return;

    native_state_t state_before_action;
    native_state_snapshot(&s_state, &state_before_action);
    button_action_t executing_action = button->pending_action;
    esp_err_t result = execute_button_action(button->pending_action);
    if (result == ESP_OK) {
        if (executing_action == BUTTON_ACTION_TOGGLE) {
            show_button_playback_status(
                !state_before_action.audio_running,
                (uint32_t)(esp_timer_get_time() / 1000U));
        } else if (executing_action == BUTTON_ACTION_NEXT) {
            show_button_status(
                BUTTON_STATUS_NEXT,
                (uint32_t)(esp_timer_get_time() / 1000U));
        } else if (executing_action == BUTTON_ACTION_PREVIOUS) {
            show_button_status(
                BUTTON_STATUS_PREVIOUS,
                (uint32_t)(esp_timer_get_time() / 1000U));
        }
        if (button->action_deferred) {
            ESP_LOGI(TAG, "Deferred BOOT action executed");
        }
        button->pending_action = BUTTON_ACTION_NONE;
    } else if (result == ESP_ERR_INVALID_STATE &&
               now - button->action_queued_at <
                   pdMS_TO_TICKS(BUTTON_ACTION_TIMEOUT_MS)) {
        if (!button->action_deferred) {
            ESP_LOGI(TAG, "Radio is starting; deferring BOOT action");
            button->action_deferred = true;
        }
        button->action_retry_at =
            now + pdMS_TO_TICKS(BUTTON_ACTION_RETRY_MS);
    } else {
        ESP_LOGW(TAG, "BOOT action failed: %s", esp_err_to_name(result));
        button->pending_action = BUTTON_ACTION_NONE;
    }
}

static TickType_t button_wait_ticks(const button_state_t *button,
                                    TickType_t now) {
    TickType_t deadline = 0;
    bool has_deadline = false;
#define KEEP_EARLIEST_BUTTON_DEADLINE(candidate)                         \
    do {                                                                 \
        TickType_t value = (candidate);                                  \
        if (!has_deadline || (int32_t)(value - deadline) < 0) {         \
            deadline = value;                                            \
            has_deadline = true;                                         \
        }                                                                \
    } while (0)

    if (button->raw_pressed != button->stable_pressed) {
        KEEP_EARLIEST_BUTTON_DEADLINE(
            button->raw_changed_at + pdMS_TO_TICKS(BUTTON_DEBOUNCE_MS));
    }
    if (button->stable_pressed && !button->hold_handled) {
        KEEP_EARLIEST_BUTTON_DEADLINE(
            button->pressed_at + pdMS_TO_TICKS(BUTTON_HOLD_MS));
    }
    if (!button->stable_pressed && button->clicks) {
        KEEP_EARLIEST_BUTTON_DEADLINE(
            button->released_at + pdMS_TO_TICKS(BUTTON_CLICK_WINDOW_MS));
    }
    if (button->pending_action != BUTTON_ACTION_NONE) {
        KEEP_EARLIEST_BUTTON_DEADLINE(button->action_retry_at);
    }
#undef KEEP_EARLIEST_BUTTON_DEADLINE

    if (!has_deadline) return portMAX_DELAY;
    if (button_tick_reached(now, deadline)) return 0;
    return deadline - now;
}

typedef struct {
    size_t glyph_count;
    size_t pixel_offset;
    uint32_t wait_started_ms;
    uint32_t last_step_ms;
    bool enabled;
} display_scroll_t;

typedef enum {
    DISPLAY_SCROLL_NONE,
    DISPLAY_SCROLL_STATION,
    DISPLAY_SCROLL_TITLE,
} display_scroll_owner_t;

#if CONFIG_YORADIO_OLED_HW_SCROLL
typedef struct {
    display_scroll_owner_t owner;
    uint32_t started_ms;
    bool active;
    bool available;
} display_hardware_scroll_t;
#endif

static esp_err_t mount_spiffs(void) {
    esp_vfs_spiffs_conf_t config = {
        .base_path = "/spiffs",
        .partition_label = "spiffs",
        .max_files = 8,
        // Never format automatically: preserve Wi-Fi, playlist and WebUI.
        .format_if_mount_failed = false,
    };
    return esp_vfs_spiffs_register(&config);
}

static void reset_scroll(display_scroll_t *scroll, const char *text,
                         uint32_t now_ms) {
    scroll->glyph_count = oled_display_large_text_length(text);
    scroll->pixel_offset = 0;
    scroll->wait_started_ms = now_ms;
    scroll->last_step_ms = now_ms;
    scroll->enabled =
        scroll->glyph_count * OLED_LARGE_GLYPH_WIDTH > OLED_DISPLAY_WIDTH;
}

static bool advance_scroll(display_scroll_t *station,
                           display_scroll_t *title,
                           display_scroll_owner_t *owner,
                           uint32_t now_ms,
                           display_scroll_owner_t *completed) {
    *completed = DISPLAY_SCROLL_NONE;
    display_scroll_t *active = NULL;
    if (*owner == DISPLAY_SCROLL_STATION && station->enabled) active = station;
    if (*owner == DISPLAY_SCROLL_TITLE && title->enabled) active = title;
    if (!active) {
        *owner = DISPLAY_SCROLL_NONE;
        if (station->enabled &&
            now_ms - station->wait_started_ms >= DISPLAY_SCROLL_HOLD_MS) {
            *owner = DISPLAY_SCROLL_STATION;
            active = station;
        } else if (title->enabled &&
                   now_ms - title->wait_started_ms >= DISPLAY_SCROLL_HOLD_MS) {
            *owner = DISPLAY_SCROLL_TITLE;
            active = title;
        }
        if (!active) return false;
        active->last_step_ms = now_ms;
    }

    uint32_t elapsed = now_ms - active->last_step_ms;
    size_t steps = elapsed / DISPLAY_SCROLL_STEP_MS;
    if (!steps) return false;
    active->last_step_ms += (uint32_t)(steps * DISPLAY_SCROLL_STEP_MS);
    active->pixel_offset += steps;
    size_t cycle_pixels =
        (active->glyph_count + DISPLAY_SCROLL_SEPARATOR_GLYPHS) *
        OLED_LARGE_GLYPH_WIDTH;
    if (active->pixel_offset >= cycle_pixels) {
        active->pixel_offset = 0;
        active->wait_started_ms = now_ms;
        active->last_step_ms = now_ms;
        *completed = *owner;
        *owner = DISPLAY_SCROLL_NONE;
    }
    return true;
}

static bool display_state_changed(const native_state_t *current,
                                  const native_state_t *previous) {
    // Stream parameters are deliberately frozen for one complete secondary
    // page. They are sampled again when that page changes, so live bitrate
    // updates do not interrupt an autonomous station-title scroll.
    return strcmp(current->station, previous->station) != 0 ||
           strcmp(current->title, previous->title) != 0 ||
           current->network_mode != previous->network_mode ||
           current->ipv4 != previous->ipv4;
}

#if CONFIG_YORADIO_OLED_HW_SCROLL
static bool hardware_scroll_candidate(const display_scroll_t *scroll,
                                      uint32_t now_ms) {
    return scroll->enabled &&
           scroll->glyph_count <= OLED_HARDWARE_SCROLL_MAX_GLYPHS &&
           now_ms - scroll->wait_started_ms >= DISPLAY_SCROLL_HOLD_MS;
}

static display_scroll_t *scroll_for_owner(display_scroll_owner_t owner,
                                          display_scroll_t *station,
                                          display_scroll_t *title) {
    if (owner == DISPLAY_SCROLL_STATION) return station;
    if (owner == DISPLAY_SCROLL_TITLE) return title;
    return NULL;
}
#endif

static void format_stream_details(const native_state_t *state, char *output,
                                  size_t output_size) {
    char bitrate[20] = "";
    char sample_rate[20] = "";
    char channels[16] = "";
    if (state->bitrate_kbps) {
        snprintf(bitrate, sizeof(bitrate), "%lu kbps",
                 (unsigned long)state->bitrate_kbps);
    }
    if (state->sample_rate_hz) {
        uint32_t tenths_khz = (state->sample_rate_hz + 50U) / 100U;
        if (tenths_khz % 10U) {
            snprintf(sample_rate, sizeof(sample_rate), "%lu.%lu kHz",
                     (unsigned long)(tenths_khz / 10U),
                     (unsigned long)(tenths_khz % 10U));
        } else {
            snprintf(sample_rate, sizeof(sample_rate), "%lu kHz",
                     (unsigned long)(tenths_khz / 10U));
        }
    }
    if (state->channels == 1) {
        strcpy(channels, "mono");
    } else if (state->channels == 2) {
        strcpy(channels, "stereo");
    } else if (state->channels) {
        snprintf(channels, sizeof(channels), "%u channels", state->channels);
    }

    const char *parts[] = {state->codec, bitrate, sample_rate, channels};
    size_t written = 0;
    output[0] = '\0';
    for (size_t index = 0; index < sizeof(parts) / sizeof(parts[0]); ++index) {
        if (!parts[index][0] || written + 1 >= output_size) continue;
        int result = snprintf(output + written, output_size - written,
                              "%s%s", written ? " " : "", parts[index]);
        if (result < 0) break;
        size_t added = (size_t)result;
        written += added < output_size - written
                       ? added
                       : output_size - written - 1;
    }
}

static void draw_status(const native_state_t *state,
                        const char *station_text,
                        const char *secondary_text,
                        const display_scroll_t *station_scroll,
                        const display_scroll_t *title_scroll,
                        bool station_uppercase) {
    char line[24] = {0};
    oled_display_clear(&s_display);
    oled_display_draw_large_text(
        &s_display, 0, 0, station_text,
        station_scroll->pixel_offset, station_scroll->enabled, true,
        station_uppercase);
    oled_display_draw_large_text(
        &s_display, 0, 16, secondary_text,
        title_scroll->pixel_offset, title_scroll->enabled, false, false);

    if (state->network_mode == NATIVE_NETWORK_CLIENT && state->ipv4) {
        esp_ip4_addr_t address = {.addr = state->ipv4};
        snprintf(line, sizeof(line), IPSTR, IP2STR(&address));
    } else if (state->network_mode == NATIVE_NETWORK_ACCESS_POINT) {
        strcpy(line, "AP mode");
    } else if (state->network_mode == NATIVE_NETWORK_ERROR) {
        strcpy(line, "WiFi error");
    } else {
        strcpy(line, "WiFi start");
    }
    size_t width = strlen(line) * 5U;
    int left = width < OLED_DISPLAY_WIDTH
                   ? (OLED_DISPLAY_WIDTH - (int)width) / 2
                   : 0;
    oled_display_draw_compact_text(&s_display, left, 33, line);
    ESP_ERROR_CHECK_WITHOUT_ABORT(oled_display_present(&s_display));
}

static void display_task(void *argument) {
    (void)argument;
    while (esp_timer_get_time() < s_boot_logo_until_us) {
        vTaskDelay(pdMS_TO_TICKS(20));
    }
    native_state_t previous = {0};
    previous.network_mode = (native_network_mode_t)-1;
    display_scroll_t station_scroll = {0};
    display_scroll_t title_scroll = {0};
    display_scroll_owner_t scroll_owner = DISPLAY_SCROLL_NONE;
#if CONFIG_YORADIO_OLED_HW_SCROLL
    display_hardware_scroll_t hardware_scroll = {.available = true};
    bool hardware_scroll_reported = false;
    ESP_LOGI(TAG, "SSD1306 hardware text scroll enabled (up to %u glyphs)",
             OLED_HARDWARE_SCROLL_MAX_GLYPHS);
#endif
    bool show_stream_info = true;
    uint32_t secondary_started_ms = 0;
    char secondary_text[192] = "";
    bool secondary_initialized = false;
    bool previous_station_uppercase =
        display_settings_get_station_uppercase();
    bool previous_numbered = display_settings_get_numbered_playlist();
    bool previous_audio_info = runtime_settings_get_audio_info();
    uint16_t previous_item = 0;
    bool screensaver_was_active = false;
    char station_text[176] = "";
    uint32_t button_status_revision =
        (uint32_t)atomic_load(&s_button_status_revision);
    uint32_t button_status_until_ms = 0;
    button_status_t button_status = BUTTON_STATUS_STOPPED;
    bool button_status_was_visible = false;
    const display_scroll_t button_status_scroll = {0};
    while (true) {
        native_state_t state;
        native_state_snapshot(&s_state, &state);
        uint32_t now_ms = (uint32_t)(esp_timer_get_time() / 1000U);
        bool redraw = display_state_changed(&state, &previous);
        bool screensaver_power_off = false;
        bool screensaver_active = display_settings_screensaver_active(
            state.audio_running, now_ms, &screensaver_power_off);
        if (screensaver_active) {
            if (!screensaver_was_active) {
                ESP_ERROR_CHECK_WITHOUT_ABORT(
                    oled_display_stop_scroll(&s_display));
                oled_display_clear(&s_display);
                ESP_ERROR_CHECK_WITHOUT_ABORT(
                    oled_display_present(&s_display));
                if (screensaver_power_off) {
                    ESP_ERROR_CHECK_WITHOUT_ABORT(
                        oled_display_set_power(&s_display, false));
                }
                screensaver_was_active = true;
            }
            previous = state;
            vTaskDelay(pdMS_TO_TICKS(50));
            continue;
        }
        if (screensaver_was_active) {
            ESP_ERROR_CHECK_WITHOUT_ABORT(
                oled_display_set_power(&s_display, true));
            screensaver_was_active = false;
            previous.network_mode = (native_network_mode_t)-1;
            redraw = true;
        }
        uint32_t current_button_status_revision =
            (uint32_t)atomic_load(&s_button_status_revision);
        if (current_button_status_revision != button_status_revision) {
            button_status_revision = current_button_status_revision;
            button_status_until_ms =
                (uint32_t)atomic_load(&s_button_status_until_ms);
            button_status =
                (button_status_t)atomic_load(&s_button_status);
            redraw = true;
        }
        bool button_status_visible =
            (int32_t)(button_status_until_ms - now_ms) > 0;
        if (button_status_visible != button_status_was_visible) redraw = true;
        bool station_uppercase = display_settings_get_station_uppercase();
        if (station_uppercase != previous_station_uppercase) redraw = true;
        bool numbered = display_settings_get_numbered_playlist();
        bool audio_info = runtime_settings_get_audio_info();
        uint16_t current_item = radio_control_current_item();
        if (numbered) {
            snprintf(station_text, sizeof(station_text), "%u %s", current_item,
                     state.station);
        } else {
            strlcpy(station_text, state.station, sizeof(station_text));
        }
        bool station_changed = strcmp(state.station, previous.station) != 0 ||
                               numbered != previous_numbered ||
                               current_item != previous_item;
        bool audio_info_changed = audio_info != previous_audio_info;
        if (station_changed || audio_info_changed) redraw = true;
        char stream_details[96];
        format_stream_details(&state, stream_details, sizeof(stream_details));
        if (station_changed) {
            reset_scroll(&station_scroll, station_text, now_ms);
            if (scroll_owner == DISPLAY_SCROLL_STATION) {
                scroll_owner = DISPLAY_SCROLL_NONE;
            }
        }
        bool title_changed = strcmp(state.title, previous.title) != 0 ||
                             audio_info_changed;
        if (title_changed) {
            show_stream_info = audio_info && !state.title[0];
            secondary_started_ms = now_ms;
            if (scroll_owner == DISPLAY_SCROLL_TITLE) {
                scroll_owner = DISPLAY_SCROLL_NONE;
            }
            const char *wanted_secondary =
                show_stream_info ? stream_details : state.title;
            strlcpy(secondary_text, wanted_secondary, sizeof(secondary_text));
            reset_scroll(&title_scroll, secondary_text, now_ms);
            secondary_initialized = true;
            redraw = true;
        } else if (!secondary_initialized) {
            const char *wanted_secondary =
                show_stream_info ? stream_details : state.title;
            strlcpy(secondary_text, wanted_secondary, sizeof(secondary_text));
            reset_scroll(&title_scroll, secondary_text, now_ms);
            secondary_started_ms = now_ms;
            secondary_initialized = true;
            redraw = true;
        }
        display_scroll_owner_t completed = DISPLAY_SCROLL_NONE;
#if CONFIG_YORADIO_OLED_HW_SCROLL
        bool start_hardware_scroll = false;
        if (hardware_scroll.active) {
            display_scroll_t *active = scroll_for_owner(
                hardware_scroll.owner, &station_scroll, &title_scroll);
            if (redraw) {
                ESP_ERROR_CHECK_WITHOUT_ABORT(
                    oled_display_stop_scroll(&s_display));
                hardware_scroll.active = false;
                scroll_owner = DISPLAY_SCROLL_NONE;
                if (active) {
                    active->pixel_offset = 0;
                    active->wait_started_ms = now_ms;
                    active->last_step_ms = now_ms;
                }
            } else if (now_ms - hardware_scroll.started_ms >=
                       DISPLAY_HARDWARE_SCROLL_RUN_MS) {
                ESP_ERROR_CHECK_WITHOUT_ABORT(
                    oled_display_stop_scroll(&s_display));
                hardware_scroll.active = false;
                completed = hardware_scroll.owner;
                scroll_owner = DISPLAY_SCROLL_NONE;
                if (active) {
                    active->pixel_offset = 0;
                    active->wait_started_ms = now_ms;
                    active->last_step_ms = now_ms;
                }
                redraw = true;
            }
        }
        if (!hardware_scroll.active && hardware_scroll.available &&
            completed == DISPLAY_SCROLL_NONE &&
            scroll_owner == DISPLAY_SCROLL_NONE) {
            if (hardware_scroll_candidate(&station_scroll, now_ms)) {
                scroll_owner = DISPLAY_SCROLL_STATION;
                start_hardware_scroll = true;
            } else if (hardware_scroll_candidate(&title_scroll, now_ms)) {
                scroll_owner = DISPLAY_SCROLL_TITLE;
                start_hardware_scroll = true;
            }
        }
#endif
        if (
#if CONFIG_YORADIO_OLED_HW_SCROLL
            !hardware_scroll.active && !start_hardware_scroll &&
#endif
            completed == DISPLAY_SCROLL_NONE &&
            advance_scroll(&station_scroll, &title_scroll, &scroll_owner,
                           now_ms, &completed)) {
            redraw = true;
        }
        if (audio_info && state.title[0] &&
            (completed == DISPLAY_SCROLL_TITLE ||
             (!title_scroll.enabled &&
              now_ms - secondary_started_ms >= DISPLAY_SECONDARY_PAGE_MS))) {
            show_stream_info = !show_stream_info;
            secondary_started_ms = now_ms;
            const char *wanted_secondary =
                show_stream_info ? stream_details : state.title;
            strlcpy(secondary_text, wanted_secondary, sizeof(secondary_text));
            reset_scroll(&title_scroll, secondary_text, now_ms);
            if (scroll_owner == DISPLAY_SCROLL_TITLE) {
                scroll_owner = DISPLAY_SCROLL_NONE;
            }
            redraw = true;
        } else if (audio_info && !state.title[0] &&
                   (completed == DISPLAY_SCROLL_TITLE ||
                    (!title_scroll.enabled &&
                     now_ms - secondary_started_ms >=
                         DISPLAY_SECONDARY_PAGE_MS))) {
            // Freeze one stream-details snapshot for a complete display pass.
            // Live bitrate updates remain available to WebUI in native_state.
            secondary_started_ms = now_ms;
            strlcpy(secondary_text, stream_details, sizeof(secondary_text));
            reset_scroll(&title_scroll, secondary_text, now_ms);
            redraw = true;
        }
        if (redraw) {
            const char *display_secondary =
                button_status_visible
                    ? button_status_text(button_status)
                    : (state.audio_running ? secondary_text : "");
            draw_status(&state, station_text, display_secondary, &station_scroll,
                        button_status_visible ? &button_status_scroll
                                              : &title_scroll,
                        station_uppercase);
            previous = state;
            previous_station_uppercase = station_uppercase;
            previous_numbered = numbered;
            previous_audio_info = audio_info;
            previous_item = current_item;
            button_status_was_visible = button_status_visible;
        }
#if CONFIG_YORADIO_OLED_HW_SCROLL
        if (start_hardware_scroll) {
            const bool station =
                scroll_owner == DISPLAY_SCROLL_STATION;
            esp_err_t result = oled_display_start_text_scroll(
                &s_display, station ? 0 : 2,
                station ? station_text : secondary_text, station,
                station && station_uppercase);
            if (result == ESP_OK) {
                hardware_scroll.active = true;
                hardware_scroll.owner = scroll_owner;
                hardware_scroll.started_ms = now_ms;
                if (!hardware_scroll_reported) {
                    display_scroll_t *active = scroll_for_owner(
                        scroll_owner, &station_scroll, &title_scroll);
                    ESP_LOGI(TAG,
                             "SSD1306 hardware scroll started for %s (%u glyphs)",
                             station ? "station" : "title",
                             active ? (unsigned)active->glyph_count : 0U);
                    hardware_scroll_reported = true;
                }
            } else {
                ESP_LOGW(TAG,
                         "Hardware text scroll failed, using software: %s",
                         esp_err_to_name(result));
                hardware_scroll.available = false;
                scroll_owner = DISPLAY_SCROLL_NONE;
            }
        }
#endif
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

static void button_task(void *argument) {
    (void)argument;
    s_button_edge_queue =
        xQueueCreate(BUTTON_EDGE_QUEUE_LENGTH, sizeof(button_edge_event_t));
    ESP_ERROR_CHECK(s_button_edge_queue != NULL ? ESP_OK : ESP_ERR_NO_MEM);

    gpio_config_t config = {
        .pin_bit_mask = 1ULL << BOARD_BOOT_BUTTON,
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&config));
    esp_err_t isr_result = gpio_install_isr_service(0);
    ESP_ERROR_CHECK(isr_result == ESP_OK || isr_result == ESP_ERR_INVALID_STATE
                        ? ESP_OK
                        : isr_result);
    ESP_ERROR_CHECK(gpio_isr_handler_add(BOARD_BOOT_BUTTON, button_gpio_isr,
                                         NULL));

    TickType_t now = xTaskGetTickCount();
    bool initially_pressed = gpio_get_level(BOARD_BOOT_BUTTON) == 0;
    button_state_t button = {
        .raw_pressed = initially_pressed,
        .stable_pressed = initially_pressed,
        .raw_changed_at = now,
        .pending_action = BUTTON_ACTION_NONE,
    };
    ESP_ERROR_CHECK(gpio_set_intr_type(BOARD_BOOT_BUTTON, GPIO_INTR_ANYEDGE));
    ESP_ERROR_CHECK(gpio_intr_enable(BOARD_BOOT_BUTTON));

    while (true) {
        now = xTaskGetTickCount();
        button_edge_event_t event;
        TickType_t wait = button_wait_ticks(&button, now);
        if (xQueueReceive(s_button_edge_queue, &event, wait) == pdTRUE) {
            if (event.pressed != button.raw_pressed) {
                TickType_t debounce_at =
                    button.raw_changed_at +
                    pdMS_TO_TICKS(BUTTON_DEBOUNCE_MS);
                if (button.raw_pressed != button.stable_pressed &&
                    button_tick_reached(event.tick, debounce_at)) {
                    apply_stable_button_level(&button, button.raw_pressed,
                                              debounce_at);
                }
                process_button_gestures_until(&button, event.tick);
                button.raw_pressed = event.pressed;
                button.raw_changed_at = event.tick;
            }
            execute_pending_button_action(&button);
            continue;
        }

        now = xTaskGetTickCount();
        TickType_t debounce_at =
            button.raw_changed_at + pdMS_TO_TICKS(BUTTON_DEBOUNCE_MS);
        if (button.raw_pressed != button.stable_pressed &&
            button_tick_reached(now, debounce_at)) {
            apply_stable_button_level(&button, button.raw_pressed, debounce_at);
        }
        process_button_gestures_until(&button, now);
        execute_pending_button_action(&button);
    }
}

static void services_task(void *argument) {
    (void)argument;
    esp_err_t result = network_service_start(&s_state);
    if (result != ESP_OK) {
        ESP_LOGE(TAG, "Network failed: %s", esp_err_to_name(result));
        native_state_set_network(&s_state, NATIVE_NETWORK_ERROR, 0);
    }
    result = time_service_apply();
    if (result != ESP_OK) {
        ESP_LOGE(TAG, "Time service failed: %s", esp_err_to_name(result));
    }
    result = audio_service_start(&s_state);
    if (result != ESP_OK) {
        ESP_LOGE(TAG, "Audio service failed: %s", esp_err_to_name(result));
    }
    result = radio_control_init(&s_state);
    if (result != ESP_OK) {
        ESP_LOGE(TAG, "Radio control failed: %s", esp_err_to_name(result));
    }
#ifdef CONFIG_YORADIO_ROTARY_ENCODER
    if (result == ESP_OK) {
        const encoder_input_callbacks_t encoder_callbacks = {
            .rotate = encoder_rotate_volume,
            .click = encoder_toggle_playback,
        };
        result = encoder_input_start(&encoder_callbacks);
        if (result != ESP_OK) {
            ESP_LOGE(TAG, "Encoder input failed: %s", esp_err_to_name(result));
        }
    }
#endif
    result = web_service_start(&s_state);
    if (result != ESP_OK) {
        ESP_LOGE(TAG, "Web server failed: %s", esp_err_to_name(result));
    }
    vTaskDelete(NULL);
}
#endif

void app_main(void) {
    ESP_LOGI(TAG, "Starting pure ESP-IDF ESP32-C3 OLED yoRadio");
    native_state_init(&s_state);

#ifdef YORADIO_CODEC_BENCHMARK
    ESP_LOGI(TAG, "Codec benchmark mode: network, WebUI and display disabled");
    ESP_ERROR_CHECK(audio_service_start(&s_state));
#else
    esp_err_t result = nvs_flash_init();
    if (result != ESP_OK) {
        // Existing settings are more important than automatic recovery.
        ESP_LOGE(TAG, "NVS init failed without erase: %s",
                 esp_err_to_name(result));
    }
    ESP_ERROR_CHECK(native_audio_settings_init());
    ESP_ERROR_CHECK(runtime_settings_init());
    result = mount_spiffs();
    if (result != ESP_OK) {
        ESP_LOGE(TAG, "SPIFFS mount failed without format: %s",
                 esp_err_to_name(result));
    }
    ESP_ERROR_CHECK(oled_display_init(&s_display));
    ESP_ERROR_CHECK(oled_display_show_boot_logo(&s_display));
    s_boot_logo_until_us =
        esp_timer_get_time() + (int64_t)DISPLAY_BOOT_LOGO_MS * 1000LL;
    ESP_ERROR_CHECK(display_settings_init(&s_display));

    ESP_ERROR_CHECK(xTaskCreate(display_task, "display",
                                BOARD_TASK_STACK_DISPLAY, NULL, 1, NULL) ==
                            pdPASS
                        ? ESP_OK
                        : ESP_ERR_NO_MEM);
    ESP_ERROR_CHECK(xTaskCreate(button_task, "boot_button",
                                BOARD_TASK_STACK_BOOT_BUTTON, NULL,
                                BUTTON_TASK_PRIORITY,
                                NULL) == pdPASS
                        ? ESP_OK
                        : ESP_ERR_NO_MEM);
    ESP_ERROR_CHECK(xTaskCreate(services_task, "services",
                                BOARD_TASK_STACK_SERVICES, NULL, 3,
                                NULL) == pdPASS
                        ? ESP_OK
                        : ESP_ERR_NO_MEM);
#endif
}
