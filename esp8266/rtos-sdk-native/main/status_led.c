#include "status_led.h"
#include "sdkconfig.h"

#if CONFIG_YORADIO_STATUS_LED
#include <stdbool.h>
#include "board_config.h"
#include "driver/gpio.h"
#include "esp8266/gpio_struct.h"
#include "esp8266/gpio_register.h"
#include "freertos/task.h"

#define STATUS_LED_UPDATE_MS (1000U / CONFIG_YORADIO_STATUS_LED_UPDATE_HZ)
#define STATUS_LED_DECAY ((CONFIG_YORADIO_STATUS_LED_DECAY_STEP * 20U) / \
                         CONFIG_YORADIO_STATUS_LED_UPDATE_HZ)
#define STATUS_LED_SD_PRESCALE 255U

_Static_assert(BOARD_STATUS_LED_GPIO >= 0 && BOARD_STATUS_LED_GPIO < 16,
               "GPIO sigma-delta is not available on GPIO16");
/* One producer (audio task), one consumer (app task). No PCM queue/copy,
 * worker stack, heap allocation, software PWM timer or extra interrupt. */
static volatile uint16_t s_pending_peak;
static volatile bool s_reset_envelope;
volatile bool status_led_capture_requested;
static bool s_ready;
static uint8_t s_envelope;
static uint8_t s_brightness;
static TickType_t s_last_update;

static void set_brightness(uint8_t brightness) {
    if (brightness == s_brightness) return;
    s_brightness = brightness;
    if (brightness == 0 || brightness == 255) {
        /* GPIO bypass gives exact dark/full endpoints (SD is n/256). */
        bool on = brightness != 0;
        gpio_set_level(BOARD_STATUS_LED_GPIO, BOARD_STATUS_LED_ACTIVE_LOW ? !on : on);
        GPIO.pin[BOARD_STATUS_LED_GPIO].source = 0;
        GPIO.sigma_delta = 0;
    } else {
        uint8_t high_density = BOARD_STATUS_LED_ACTIVE_LOW
            ? (uint8_t)(256U - brightness) : brightness;
        /* Raw 0..255 target follows the ESP8266/NodeMCU sigma-delta driver.
         * This peripheral is independent of the I2S DMA audio modulator. */
        GPIO.sigma_delta = SIGMA_DELTA_ENABLE |
            (STATUS_LED_SD_PRESCALE << SIGMA_DELTA_PRESCALAR_S) |
            ((uint32_t)high_density << SIGMA_DELTA_TARGET_S);
        GPIO.pin[BOARD_STATUS_LED_GPIO].source = 1;
    }
}

esp_err_t status_led_init(void) {
    gpio_config_t led = {
        .pin_bit_mask = 1ULL << BOARD_STATUS_LED_GPIO,
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    /* Preload the inactive level before enabling GPIO output. */
    gpio_set_level(BOARD_STATUS_LED_GPIO, BOARD_STATUS_LED_ACTIVE_LOW ? 1 : 0);
    esp_err_t result = gpio_config(&led);
    if (result != ESP_OK) return result;
    s_pending_peak = 0;
    s_reset_envelope = false;
    s_envelope = 0;
    s_brightness = 255;
    set_brightness(0);
    s_last_update = xTaskGetTickCount();
    s_ready = true;
    status_led_capture_requested = CONFIG_YORADIO_STATUS_LED_MAX_BRIGHTNESS != 0;
    return ESP_OK;
}

void status_led_publish_peak(uint16_t peak) {
    if (!status_led_capture_requested) return;
    taskENTER_CRITICAL();
    if (peak > s_pending_peak) s_pending_peak = peak;
    status_led_capture_requested = false;
    taskEXIT_CRITICAL();
}

void status_led_clear(void) {
    taskENTER_CRITICAL();
    s_pending_peak = 0;
    s_reset_envelope = true;
    taskEXIT_CRITICAL();
}

TickType_t status_led_wait_ticks(TickType_t maximum) {
    if (!s_ready) return maximum;
    TickType_t elapsed = xTaskGetTickCount() - s_last_update;
    TickType_t period = pdMS_TO_TICKS(STATUS_LED_UPDATE_MS);
    TickType_t remaining = elapsed >= period ? 0 : period - elapsed;
    return remaining < maximum ? remaining : maximum;
}

void status_led_poll(void) {
    if (!s_ready) return;
    TickType_t now = xTaskGetTickCount();
    if ((TickType_t)(now - s_last_update) < pdMS_TO_TICKS(STATUS_LED_UPDATE_MS))
        return;
    s_last_update = now;
    taskENTER_CRITICAL();
    uint16_t peak = s_pending_peak;
    s_pending_peak = 0;
    bool reset = s_reset_envelope;
    s_reset_envelope = false;
    status_led_capture_requested = CONFIG_YORADIO_STATUS_LED_MAX_BRIGHTNESS != 0;
    taskEXIT_CRITICAL();
    if (reset) s_envelope = 0;
    uint8_t target = (uint8_t)(((uint32_t)peak * 255U + 16384U) >> 15);
    if (target >= s_envelope) s_envelope = target;
    else {
        /* Do not release below a still-present signal. */
        uint32_t released = s_envelope > STATUS_LED_DECAY
            ? s_envelope - STATUS_LED_DECAY : 0;
        s_envelope = (uint8_t)(released > target ? released : target);
    }
#if CONFIG_YORADIO_STATUS_LED_MAX_BRIGHTNESS == 255
    set_brightness(s_envelope); /* No multiply/divide in the default profile. */
#else
    uint32_t product = (uint32_t)s_envelope * CONFIG_YORADIO_STATUS_LED_MAX_BRIGHTNESS + 127U;
    /* Exact rounded /255 for the entire 0..65152 product range. */
    set_brightness((uint8_t)((product + 1U + (product >> 8)) >> 8));
#endif
}
#endif
