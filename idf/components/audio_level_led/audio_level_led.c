#include "audio_level_led.h"

#include "sdkconfig.h"

#if CONFIG_YORADIO_AUDIO_LEVEL_LED

#include <limits.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "driver/gpio.h"
#include "driver/ledc.h"
#include "esp_check.h"
#include "esp_log.h"
#include "esp_timer.h"

static const char *const TAG = "audio_level_led";
static uint32_t s_last_update_ms;
static uint8_t s_envelope;
static uint8_t s_last_brightness = UINT8_MAX;
static bool s_ready;

static bool update_due(void) {
    uint32_t now_ms = (uint32_t)(esp_timer_get_time() / 1000U);
    if (now_ms - s_last_update_ms < CONFIG_YORADIO_AUDIO_LEVEL_LED_UPDATE_MS) {
        return false;
    }
    s_last_update_ms = now_ms;
    return true;
}

static void apply_peak(uint16_t peak) {
    uint8_t target =
        (uint8_t)(((uint32_t)peak * 255U + 16384U) / 32768U);
    if (target >= s_envelope) {
        s_envelope = target;
    } else if (s_envelope > CONFIG_YORADIO_AUDIO_LEVEL_LED_DECAY_STEP) {
        s_envelope -= CONFIG_YORADIO_AUDIO_LEVEL_LED_DECAY_STEP;
    } else {
        s_envelope = 0;
    }

    uint8_t brightness = (uint8_t)(
        ((uint32_t)s_envelope *
             CONFIG_YORADIO_AUDIO_LEVEL_LED_MAX_BRIGHTNESS +
         127U) /
        255U);
    if (!s_ready || brightness == s_last_brightness) return;
    s_last_brightness = brightness;
    uint32_t duty = CONFIG_YORADIO_AUDIO_LEVEL_LED_ACTIVE_LOW
                        ? 255U - brightness
                        : brightness;
    ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, duty);
    ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
}

esp_err_t audio_level_led_init(void) {
    gpio_num_t gpio = (gpio_num_t)CONFIG_YORADIO_AUDIO_LEVEL_LED_GPIO;
    ESP_RETURN_ON_FALSE(GPIO_IS_VALID_OUTPUT_GPIO(gpio), ESP_ERR_INVALID_ARG,
                        TAG, "GPIO%d is not a valid LED output", gpio);
    ledc_timer_config_t timer = {
        .speed_mode = LEDC_LOW_SPEED_MODE,
        .duty_resolution = LEDC_TIMER_8_BIT,
        .timer_num = LEDC_TIMER_0,
        .freq_hz = CONFIG_YORADIO_AUDIO_LEVEL_LED_PWM_HZ,
        .clk_cfg = LEDC_AUTO_CLK,
    };
    ESP_RETURN_ON_ERROR(ledc_timer_config(&timer), TAG, "PWM timer setup");
    ledc_channel_config_t channel = {
        .gpio_num = gpio,
        .speed_mode = LEDC_LOW_SPEED_MODE,
        .channel = LEDC_CHANNEL_0,
        .intr_type = LEDC_INTR_DISABLE,
        .timer_sel = LEDC_TIMER_0,
        .duty = CONFIG_YORADIO_AUDIO_LEVEL_LED_ACTIVE_LOW ? 255 : 0,
        .hpoint = 0,
    };
    ESP_RETURN_ON_ERROR(ledc_channel_config(&channel), TAG,
                        "PWM channel setup");
    s_last_update_ms = 0;
    s_envelope = 0;
    s_last_brightness = UINT8_MAX;
    s_ready = true;
    apply_peak(0);
    ESP_LOGI(TAG, "GPIO%d, %s, %d Hz, max %d/255", gpio,
             CONFIG_YORADIO_AUDIO_LEVEL_LED_ACTIVE_LOW ? "active low"
                                                       : "active high",
             CONFIG_YORADIO_AUDIO_LEVEL_LED_PWM_HZ,
             CONFIG_YORADIO_AUDIO_LEVEL_LED_MAX_BRIGHTNESS);
    return ESP_OK;
}

void audio_level_led_update_peak(uint16_t peak) {
    if (!s_ready || !update_due()) return;
    if (peak > 32768U) peak = 32768U;
    apply_peak(peak);
}

void audio_level_led_update_pcm(const uint8_t *data, size_t size,
                                uint8_t bits_per_sample, uint8_t channels) {
    if (!s_ready || !update_due()) return;
    if (!data || bits_per_sample != 16 || channels == 0) {
        apply_peak(0);
        return;
    }
    uint16_t peak = 0;
    for (size_t offset = 0; offset + sizeof(int16_t) <= size;
         offset += sizeof(int16_t)) {
        int16_t sample;
        memcpy(&sample, data + offset, sizeof(sample));
        uint16_t magnitude = sample == INT16_MIN ? 32768U
                                                  : (uint16_t)abs(sample);
        if (magnitude > peak) peak = magnitude;
    }
    apply_peak(peak);
}

#else

esp_err_t audio_level_led_init(void) { return ESP_OK; }

void audio_level_led_update_peak(uint16_t peak) { (void)peak; }

void audio_level_led_update_pcm(const uint8_t *data, size_t size,
                                uint8_t bits_per_sample, uint8_t channels) {
    (void)data;
    (void)size;
    (void)bits_per_sample;
    (void)channels;
}

#endif
