#include "status_led.h"

#include <stdbool.h>
#include <stdint.h>

#include "board_config.h"
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "native_state.h"
#include "network_service.h"

#define STATUS_LED_HALF_PERIOD_MS 500U

static bool s_output_on;
static bool s_was_playing;
static TickType_t s_blink_started;

static void set_output(bool on) {
    if (on == s_output_on) return;
    s_output_on = on;
    gpio_set_level(BOARD_STATUS_LED_GPIO,
                   BOARD_STATUS_LED_ACTIVE_LOW ? !on : on);
}

esp_err_t status_led_init(void) {
    gpio_config_t led = {
        .pin_bit_mask = 1ULL << BOARD_STATUS_LED_GPIO,
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    esp_err_t result = gpio_config(&led);
    if (result != ESP_OK) return result;
    s_output_on = true;
    set_output(false);
    s_was_playing = false;
    s_blink_started = xTaskGetTickCount();
    return ESP_OK;
}

void status_led_poll(void) {
    native_state_t state;
    native_state_snapshot(&state);
    bool connected = network_service_connected();
    if (!connected) {
        s_was_playing = false;
        set_output(false);
        return;
    }
    if (!state.playing) {
        s_was_playing = false;
        set_output(true);
        return;
    }

    TickType_t now = xTaskGetTickCount();
    if (!s_was_playing) {
        s_was_playing = true;
        s_blink_started = now;
    }
    TickType_t half_period = pdMS_TO_TICKS(STATUS_LED_HALF_PERIOD_MS);
    bool on = ((now - s_blink_started) / half_period & 1U) != 0;
    set_output(on);
}
