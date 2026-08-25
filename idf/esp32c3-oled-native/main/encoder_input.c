#include "encoder_input.h"

#include "sdkconfig.h"

#ifndef CONFIG_YORADIO_ROTARY_ENCODER

esp_err_t encoder_input_start(const encoder_input_callbacks_t *callbacks) {
    (void)callbacks;
    return ESP_ERR_NOT_SUPPORTED;
}

#else

#include "board_config.h"
#include "driver/gpio.h"
#include "esp_check.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/task.h"
#include "runtime_settings.h"

#define ENCODER_EVENT_QUEUE_LENGTH 32
#define ENCODER_TASK_PRIORITY 8
#define ENCODER_BUTTON_DEBOUNCE_MS 35U
#define ENCODER_ACCELERATION_LONG_CUTOFF_MS 200U
#define ENCODER_ACCELERATION_SHORT_CUTOFF_MS 4U

typedef enum {
    ENCODER_EVENT_ROTATE,
    ENCODER_EVENT_BUTTON_EDGE,
} encoder_event_type_t;

typedef struct {
    encoder_event_type_t type;
    TickType_t tick;
    int8_t delta;
    bool pressed;
} encoder_event_t;

typedef struct {
    bool raw_pressed;
    bool stable_pressed;
    TickType_t raw_changed_at;
} encoder_button_state_t;

static const char *const TAG = "rotary_encoder";
static const int8_t s_transition_table[16] = {
    0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0,
};
static QueueHandle_t s_event_queue;
static encoder_input_callbacks_t s_callbacks;
static volatile uint8_t s_previous_phase;
static volatile int8_t s_phase_accumulator;

static bool tick_reached(TickType_t now, TickType_t deadline) {
    return (int32_t)(now - deadline) >= 0;
}

static bool pin_is_reserved(int pin) {
    if (pin == BOARD_OLED_SDA || pin == BOARD_OLED_SCL ||
        pin == BOARD_AUDIO_LEFT_DATA || pin == BOARD_AUDIO_RIGHT_DATA ||
        pin == BOARD_BOOT_BUTTON) {
        return true;
    }
#ifdef CONFIG_YORADIO_AUDIO_LEVEL_LED
    if (pin == CONFIG_YORADIO_AUDIO_LEVEL_LED_GPIO) return true;
#endif
    return false;
}

static void IRAM_ATTR encoder_phase_isr(void *argument) {
    (void)argument;
    uint8_t phase = (gpio_get_level(CONFIG_YORADIO_ROTARY_ENCODER_GPIO_B)
                         ? 2U
                         : 0U) |
                    (gpio_get_level(CONFIG_YORADIO_ROTARY_ENCODER_GPIO_A)
                         ? 1U
                         : 0U);
    uint8_t index = (uint8_t)((s_previous_phase << 2U) | phase);
    s_previous_phase = phase;
    int8_t direction = s_transition_table[index & 0x0fU];
#ifdef CONFIG_YORADIO_ROTARY_ENCODER_REVERSE
    direction = (int8_t)-direction;
#endif
    if (!direction) return;

    int8_t accumulated = (int8_t)(s_phase_accumulator + direction);
    s_phase_accumulator = accumulated;
    int8_t detent = 0;
    if (accumulated >= CONFIG_YORADIO_ROTARY_ENCODER_STEPS) {
        detent = 1;
        s_phase_accumulator = 0;
    } else if (accumulated <= -CONFIG_YORADIO_ROTARY_ENCODER_STEPS) {
        detent = -1;
        s_phase_accumulator = 0;
    }
    if (!detent) return;

    encoder_event_t event = {
        .type = ENCODER_EVENT_ROTATE,
        .tick = xTaskGetTickCountFromISR(),
        .delta = detent,
    };
    BaseType_t higher_priority_task_woken = pdFALSE;
    xQueueSendFromISR(s_event_queue, &event, &higher_priority_task_woken);
    if (higher_priority_task_woken) portYIELD_FROM_ISR();
}

#ifdef CONFIG_YORADIO_ROTARY_ENCODER_BUTTON
static void IRAM_ATTR encoder_button_isr(void *argument) {
    (void)argument;
    encoder_event_t event = {
        .type = ENCODER_EVENT_BUTTON_EDGE,
        .tick = xTaskGetTickCountFromISR(),
        .pressed =
            gpio_get_level(CONFIG_YORADIO_ROTARY_ENCODER_BUTTON_GPIO) == 0,
    };
    BaseType_t higher_priority_task_woken = pdFALSE;
    xQueueSendFromISR(s_event_queue, &event, &higher_priority_task_woken);
    if (higher_priority_task_woken) portYIELD_FROM_ISR();
}
#endif

static int32_t accelerated_delta(int8_t detent, TickType_t tick,
                                 TickType_t *last_tick,
                                 int8_t *last_direction) {
    uint16_t acceleration = runtime_settings_get_encoder_acceleration();
    int32_t magnitude = 1;
    if (acceleration > 1U && detent == *last_direction && *last_tick != 0) {
        uint32_t elapsed_ms =
            (uint32_t)((tick - *last_tick) * portTICK_PERIOD_MS);
        if (elapsed_ms < ENCODER_ACCELERATION_LONG_CUTOFF_MS) {
            if (elapsed_ms < ENCODER_ACCELERATION_SHORT_CUTOFF_MS) {
                elapsed_ms = ENCODER_ACCELERATION_SHORT_CUTOFF_MS;
            }
            magnitude += acceleration /
                         (elapsed_ms * CONFIG_YORADIO_ROTARY_ENCODER_STEPS);
        }
    }
    *last_tick = tick;
    *last_direction = detent;
    return detent > 0 ? magnitude : -magnitude;
}

static TickType_t button_wait_ticks(const encoder_button_state_t *button,
                                    TickType_t now) {
#ifdef CONFIG_YORADIO_ROTARY_ENCODER_BUTTON
    if (button->raw_pressed != button->stable_pressed) {
        TickType_t deadline = button->raw_changed_at +
                              pdMS_TO_TICKS(ENCODER_BUTTON_DEBOUNCE_MS);
        if (tick_reached(now, deadline)) return 0;
        return deadline - now;
    }
#else
    (void)button;
    (void)now;
#endif
    return portMAX_DELAY;
}

static void apply_button_debounce(encoder_button_state_t *button,
                                  TickType_t now) {
#ifdef CONFIG_YORADIO_ROTARY_ENCODER_BUTTON
    TickType_t deadline = button->raw_changed_at +
                          pdMS_TO_TICKS(ENCODER_BUTTON_DEBOUNCE_MS);
    if (button->raw_pressed == button->stable_pressed ||
        !tick_reached(now, deadline)) {
        return;
    }
    button->stable_pressed = button->raw_pressed;
    if (!button->stable_pressed && s_callbacks.click) {
        esp_err_t result = s_callbacks.click(s_callbacks.context);
        if (result != ESP_OK) {
            ESP_LOGW(TAG, "Encoder click failed: %s",
                     esp_err_to_name(result));
        }
    }
#else
    (void)button;
    (void)now;
#endif
}

static void encoder_task(void *argument) {
    (void)argument;
    encoder_button_state_t button = {0};
#ifdef CONFIG_YORADIO_ROTARY_ENCODER_BUTTON
    button.raw_pressed =
        gpio_get_level(CONFIG_YORADIO_ROTARY_ENCODER_BUTTON_GPIO) == 0;
    button.stable_pressed = button.raw_pressed;
#endif
    TickType_t last_rotation_tick = 0;
    int8_t last_rotation_direction = 0;

    while (true) {
        TickType_t now = xTaskGetTickCount();
        encoder_event_t event;
        TickType_t wait = button_wait_ticks(&button, now);
        if (xQueueReceive(s_event_queue, &event, wait) == pdTRUE) {
            if (event.type == ENCODER_EVENT_ROTATE && s_callbacks.rotate) {
                int32_t delta = accelerated_delta(
                    event.delta, event.tick, &last_rotation_tick,
                    &last_rotation_direction);
                esp_err_t result =
                    s_callbacks.rotate(delta, s_callbacks.context);
                if (result != ESP_OK) {
                    ESP_LOGW(TAG, "Encoder rotation failed: %s",
                             esp_err_to_name(result));
                }
#ifdef CONFIG_YORADIO_ROTARY_ENCODER_BUTTON
            } else if (event.type == ENCODER_EVENT_BUTTON_EDGE &&
                       event.pressed != button.raw_pressed) {
                apply_button_debounce(&button, event.tick);
                button.raw_pressed = event.pressed;
                button.raw_changed_at = event.tick;
#endif
            }
            continue;
        }
        apply_button_debounce(&button, xTaskGetTickCount());
    }
}

esp_err_t encoder_input_start(const encoder_input_callbacks_t *callbacks) {
    ESP_RETURN_ON_FALSE(callbacks && callbacks->rotate, ESP_ERR_INVALID_ARG,
                        TAG, "Encoder rotation callback is required");
    const int phase_a = CONFIG_YORADIO_ROTARY_ENCODER_GPIO_A;
    const int phase_b = CONFIG_YORADIO_ROTARY_ENCODER_GPIO_B;
    ESP_RETURN_ON_FALSE(GPIO_IS_VALID_GPIO(phase_a) &&
                            GPIO_IS_VALID_GPIO(phase_b) &&
                            phase_a != phase_b && !pin_is_reserved(phase_a) &&
                            !pin_is_reserved(phase_b),
                        ESP_ERR_INVALID_ARG, TAG,
                        "Encoder phase GPIO conflict");
#ifdef CONFIG_YORADIO_ROTARY_ENCODER_BUTTON
    const int button_pin = CONFIG_YORADIO_ROTARY_ENCODER_BUTTON_GPIO;
    ESP_RETURN_ON_FALSE(GPIO_IS_VALID_GPIO(button_pin) &&
                            button_pin != phase_a && button_pin != phase_b &&
                            !pin_is_reserved(button_pin),
                        ESP_ERR_INVALID_ARG, TAG,
                        "Encoder button GPIO conflict");
#endif

    s_callbacks = *callbacks;
    s_event_queue =
        xQueueCreate(ENCODER_EVENT_QUEUE_LENGTH, sizeof(encoder_event_t));
    ESP_RETURN_ON_FALSE(s_event_queue, ESP_ERR_NO_MEM, TAG,
                        "Encoder event queue allocation");

    gpio_config_t phase_config = {
        .pin_bit_mask = (1ULL << phase_a) | (1ULL << phase_b),
        .mode = GPIO_MODE_INPUT,
#ifdef CONFIG_YORADIO_ROTARY_ENCODER_PULLUP
        .pull_up_en = GPIO_PULLUP_ENABLE,
#else
        .pull_up_en = GPIO_PULLUP_DISABLE,
#endif
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    ESP_RETURN_ON_ERROR(gpio_config(&phase_config), TAG,
                        "Configure encoder phases");
    s_previous_phase =
        (gpio_get_level(phase_b) ? 2U : 0U) |
        (gpio_get_level(phase_a) ? 1U : 0U);

#ifdef CONFIG_YORADIO_ROTARY_ENCODER_BUTTON
    gpio_config_t button_config = {
        .pin_bit_mask = 1ULL << button_pin,
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    ESP_RETURN_ON_ERROR(gpio_config(&button_config), TAG,
                        "Configure encoder button");
#endif

    esp_err_t result = gpio_install_isr_service(0);
    ESP_RETURN_ON_FALSE(result == ESP_OK || result == ESP_ERR_INVALID_STATE,
                        result, TAG, "Install GPIO ISR service");
    ESP_RETURN_ON_ERROR(gpio_isr_handler_add(phase_a, encoder_phase_isr, NULL),
                        TAG, "Add encoder phase A ISR");
    ESP_RETURN_ON_ERROR(gpio_isr_handler_add(phase_b, encoder_phase_isr, NULL),
                        TAG, "Add encoder phase B ISR");
    ESP_RETURN_ON_ERROR(gpio_set_intr_type(phase_a, GPIO_INTR_ANYEDGE), TAG,
                        "Enable encoder phase A edges");
    ESP_RETURN_ON_ERROR(gpio_set_intr_type(phase_b, GPIO_INTR_ANYEDGE), TAG,
                        "Enable encoder phase B edges");
    ESP_RETURN_ON_ERROR(gpio_intr_enable(phase_a), TAG,
                        "Enable encoder phase A interrupt");
    ESP_RETURN_ON_ERROR(gpio_intr_enable(phase_b), TAG,
                        "Enable encoder phase B interrupt");
#ifdef CONFIG_YORADIO_ROTARY_ENCODER_BUTTON
    ESP_RETURN_ON_ERROR(
        gpio_isr_handler_add(button_pin, encoder_button_isr, NULL), TAG,
        "Add encoder button ISR");
    ESP_RETURN_ON_ERROR(gpio_set_intr_type(button_pin, GPIO_INTR_ANYEDGE), TAG,
                        "Enable encoder button edges");
    ESP_RETURN_ON_ERROR(gpio_intr_enable(button_pin), TAG,
                        "Enable encoder button interrupt");
#endif

    BaseType_t task_result =
        xTaskCreate(encoder_task, "rotary_encoder",
                    BOARD_TASK_STACK_ROTARY_ENCODER, NULL,
                    ENCODER_TASK_PRIORITY, NULL);
    ESP_RETURN_ON_FALSE(task_result == pdPASS, ESP_ERR_NO_MEM, TAG,
                        "Create encoder task");
    ESP_LOGI(TAG, "Encoder enabled: A=GPIO%d B=GPIO%d steps=%d",
             phase_a, phase_b, CONFIG_YORADIO_ROTARY_ENCODER_STEPS);
    return ESP_OK;
}

#endif
