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
static TaskHandle_t s_consumer_task;
static bool s_raw_pressed;
static bool s_stable_pressed;
static TickType_t s_raw_changed;
static TickType_t s_pressed_at;
static bool s_click_pending;
static TickType_t s_click_deadline;

static void IRAM_ATTR wake_consumer_from_isr(BaseType_t *wake) {
    TaskHandle_t consumer = s_consumer_task;
    if (consumer) vTaskNotifyGiveFromISR(consumer, wake);
}

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
    wake_consumer_from_isr(&wake);
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
    wake_consumer_from_isr(&wake);
    if (wake) portYIELD_FROM_ISR();
}
#endif

static bool tick_due(TickType_t now, TickType_t deadline) {
    return (int32_t)(now - deadline) >= 0;
}

static void show_play_state(void) {
    native_state_set_message(native_state_audio_active() ? "playing" : "stopped",
                             INPUT_MESSAGE_MS);
}

void input_service_poll(void) {
    if (!s_events) return;
    input_event_t event;
    while (xQueueReceive(s_events, &event, 0) == pdTRUE) {
        if (event.type == INPUT_ENCODER_STEP) {
            persistent_settings_t settings;
            persistent_settings_get(&settings);
            radio_control_adjust_volume(event.delta * settings.volume_steps);
            continue;
        }
        bool pressed = gpio_get_level(BOARD_BOOT_BUTTON_GPIO) == 0;
        if (pressed != s_raw_pressed) {
            s_raw_pressed = pressed;
            s_raw_changed = event.tick;
        }
    }

    TickType_t now = xTaskGetTickCount();
    if (s_raw_pressed != s_stable_pressed &&
        tick_due(now, s_raw_changed + pdMS_TO_TICKS(INPUT_DEBOUNCE_MS))) {
        s_stable_pressed = s_raw_pressed;
        if (s_stable_pressed) {
            s_pressed_at = now;
        } else {
            uint32_t held_ms =
                (uint32_t)((now - s_pressed_at) * portTICK_PERIOD_MS);
            if (held_ms >= INPUT_LONG_MS) {
                s_click_pending = false;
                radio_control_previous();
                native_state_set_message("prev", INPUT_MESSAGE_MS);
            } else if (s_click_pending &&
                       !tick_due(now, s_click_deadline)) {
                s_click_pending = false;
                radio_control_next();
                native_state_set_message("next", INPUT_MESSAGE_MS);
            } else {
                s_click_pending = true;
                s_click_deadline = now + pdMS_TO_TICKS(INPUT_DOUBLE_MS);
            }
        }
    }
    if (s_click_pending && tick_due(now, s_click_deadline)) {
        s_click_pending = false;
        radio_control_toggle();
        show_play_state();
    }
}

static TickType_t deadline_wait(TickType_t now, TickType_t deadline) {
    return tick_due(now, deadline) ? 0 : deadline - now;
}

TickType_t input_service_wait_ticks(TickType_t maximum_wait) {
    if (!s_events || uxQueueMessagesWaiting(s_events)) return 0;
    TickType_t now = xTaskGetTickCount();
    TickType_t wait = maximum_wait;
    if (s_raw_pressed != s_stable_pressed) {
        TickType_t debounce = deadline_wait(
            now, s_raw_changed + pdMS_TO_TICKS(INPUT_DEBOUNCE_MS));
        if (debounce < wait) wait = debounce;
    }
    if (s_click_pending) {
        TickType_t click = deadline_wait(now, s_click_deadline);
        if (click < wait) wait = click;
    }
    return wait;
}

esp_err_t input_service_start(void) {
    s_events = xQueueCreate(12, sizeof(input_event_t));
    if (!s_events) return ESP_ERR_NO_MEM;
    s_consumer_task = xTaskGetCurrentTaskHandle();
    gpio_config_t button = {
        .pin_bit_mask = 1ULL << BOARD_BOOT_BUTTON_GPIO,
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_ANYEDGE,
    };
    esp_err_t result = gpio_config(&button);
    if (result != ESP_OK) return result;
    s_raw_pressed = gpio_get_level(BOARD_BOOT_BUTTON_GPIO) == 0;
    s_stable_pressed = s_raw_pressed;
    s_raw_changed = xTaskGetTickCount();
    s_pressed_at = s_raw_changed;
    s_click_pending = false;
    s_click_deadline = 0;
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

    ESP_LOGI(TAG, "BOOT on app task: click play/stop, double next, long previous");
    return ESP_OK;
}
