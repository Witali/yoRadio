#include "input_service.h"

#include <stdbool.h>
#include <stdint.h>

#include "board_config.h"
#include "driver/gpio.h"
#include "esp_attr.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/task.h"
#include "native_state.h"
#include "persistent_settings.h"
#include "radio_control.h"

#define INPUT_DEBOUNCE_MS 30U
#define INPUT_DOUBLE_MS 350U
#define INPUT_LONG_MS 800U
#define INPUT_MESSAGE_MS 2000U

typedef enum { INPUT_BUTTON_EDGE, INPUT_ENCODER_STEP } input_event_type_t;
typedef struct {
    input_event_type_t type;
    TickType_t tick;
    int8_t delta;
} input_event_t;

static const char *TAG = "input";
static QueueHandle_t s_events;

#if BOARD_ENCODER_A_GPIO >= 0 && BOARD_ENCODER_B_GPIO >= 0
static volatile uint8_t s_encoder_phase;
static volatile int8_t s_encoder_accumulator;
static const int8_t s_transitions[16] = {
    0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0,
};
#endif

static void IRAM_ATTR button_isr(void *argument) {
    (void)argument;
    input_event_t event = {
        .type = INPUT_BUTTON_EDGE,
        .tick = xTaskGetTickCountFromISR(),
    };
    BaseType_t wake = pdFALSE;
    xQueueSendFromISR(s_events, &event, &wake);
    if (wake) portYIELD_FROM_ISR();
}

#if BOARD_ENCODER_A_GPIO >= 0 && BOARD_ENCODER_B_GPIO >= 0
static void IRAM_ATTR encoder_isr(void *argument) {
    (void)argument;
    uint8_t phase = (gpio_get_level(BOARD_ENCODER_B_GPIO) ? 2U : 0U) |
                    (gpio_get_level(BOARD_ENCODER_A_GPIO) ? 1U : 0U);
    uint8_t transition = (uint8_t)((s_encoder_phase << 2U) | phase);
    s_encoder_phase = phase;
    int8_t accumulator =
        (int8_t)(s_encoder_accumulator + s_transitions[transition & 15U]);
    s_encoder_accumulator = accumulator;
    int8_t delta = 0;
    if (accumulator >= 4) delta = 1;
    else if (accumulator <= -4) delta = -1;
    if (!delta) return;
    s_encoder_accumulator = 0;
    input_event_t event = {
        .type = INPUT_ENCODER_STEP,
        .tick = xTaskGetTickCountFromISR(),
        .delta = delta,
    };
    BaseType_t wake = pdFALSE;
    xQueueSendFromISR(s_events, &event, &wake);
    if (wake) portYIELD_FROM_ISR();
}
#endif

static bool tick_due(TickType_t now, TickType_t deadline) {
    return (int32_t)(now - deadline) >= 0;
}

static void show_play_state(void) {
    native_state_t state;
    native_state_snapshot(&state);
    native_state_set_message(state.playing || state.connecting
                                 ? "playing" : "stopped",
                             INPUT_MESSAGE_MS);
}

static void input_task(void *argument) {
    (void)argument;
    bool raw_pressed = gpio_get_level(BOARD_BOOT_BUTTON_GPIO) == 0;
    bool stable_pressed = raw_pressed;
    TickType_t raw_changed = xTaskGetTickCount();
    TickType_t pressed_at = raw_changed;
    bool click_pending = false;
    TickType_t click_deadline = 0;

    while (true) {
        TickType_t now = xTaskGetTickCount();
        TickType_t wait = pdMS_TO_TICKS(20);
        if (click_pending && tick_due(now, click_deadline)) wait = 0;
        input_event_t event;
        if (xQueueReceive(s_events, &event, wait) == pdTRUE) {
            if (event.type == INPUT_ENCODER_STEP) {
                persistent_settings_t settings;
                persistent_settings_get(&settings);
                radio_control_adjust_volume(event.delta * settings.volume_steps);
                continue;
            }
            bool pressed = gpio_get_level(BOARD_BOOT_BUTTON_GPIO) == 0;
            if (pressed != raw_pressed) {
                raw_pressed = pressed;
                raw_changed = event.tick;
            }
        }
        now = xTaskGetTickCount();
        if (raw_pressed != stable_pressed &&
            tick_due(now, raw_changed + pdMS_TO_TICKS(INPUT_DEBOUNCE_MS))) {
            stable_pressed = raw_pressed;
            if (stable_pressed) {
                pressed_at = now;
            } else {
                uint32_t held_ms =
                    (uint32_t)((now - pressed_at) * portTICK_PERIOD_MS);
                if (held_ms >= INPUT_LONG_MS) {
                    click_pending = false;
                    radio_control_previous();
                    native_state_set_message("prev", INPUT_MESSAGE_MS);
                } else if (click_pending && !tick_due(now, click_deadline)) {
                    click_pending = false;
                    radio_control_next();
                    native_state_set_message("next", INPUT_MESSAGE_MS);
                } else {
                    click_pending = true;
                    click_deadline = now + pdMS_TO_TICKS(INPUT_DOUBLE_MS);
                }
            }
        }
        if (click_pending && tick_due(now, click_deadline)) {
            click_pending = false;
            radio_control_toggle();
            show_play_state();
        }
    }
}

esp_err_t input_service_start(void) {
    s_events = xQueueCreate(12, sizeof(input_event_t));
    if (!s_events) return ESP_ERR_NO_MEM;
    gpio_config_t button = {
        .pin_bit_mask = 1ULL << BOARD_BOOT_BUTTON_GPIO,
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_ANYEDGE,
    };
    esp_err_t result = gpio_config(&button);
    if (result != ESP_OK) return result;
    result = gpio_install_isr_service(0);
    if (result != ESP_OK && result != ESP_ERR_INVALID_STATE) return result;
    result = gpio_isr_handler_add(BOARD_BOOT_BUTTON_GPIO, button_isr, NULL);
    if (result != ESP_OK) return result;

#if BOARD_ENCODER_A_GPIO >= 0 && BOARD_ENCODER_B_GPIO >= 0
    gpio_config_t encoder = {
        .pin_bit_mask = (1ULL << BOARD_ENCODER_A_GPIO) |
                        (1ULL << BOARD_ENCODER_B_GPIO),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_ANYEDGE,
    };
    if ((result = gpio_config(&encoder)) != ESP_OK) return result;
    s_encoder_phase =
        (gpio_get_level(BOARD_ENCODER_B_GPIO) ? 2U : 0U) |
        (gpio_get_level(BOARD_ENCODER_A_GPIO) ? 1U : 0U);
    if ((result = gpio_isr_handler_add(BOARD_ENCODER_A_GPIO, encoder_isr,
                                       NULL)) != ESP_OK) return result;
    if ((result = gpio_isr_handler_add(BOARD_ENCODER_B_GPIO, encoder_isr,
                                       NULL)) != ESP_OK) return result;
    ESP_LOGI(TAG, "Encoder enabled on GPIO%d/GPIO%d",
             BOARD_ENCODER_A_GPIO, BOARD_ENCODER_B_GPIO);
#endif

    if (xTaskCreate(input_task, "input", 2048, NULL, 8, NULL) != pdPASS)
        return ESP_ERR_NO_MEM;
    ESP_LOGI(TAG, "BOOT: click play/stop, double next, long previous");
    return ESP_OK;
}
