#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define BOARD_STATUS_LED_GPIO 2
#define CONFIG_YORADIO_STATUS_LED_MAX_BRIGHTNESS 255
#define CONFIG_YORADIO_STATUS_LED_DECAY_STEP 8
#define SIGMA_DELTA_ENABLE (1U << 16)
#define SIGMA_DELTA_PRESCALAR_S 8
#define SIGMA_DELTA_TARGET_S 0
#define pdMS_TO_TICKS(x) (x)
typedef uint32_t TickType_t;
typedef int esp_err_t;
enum {ESP_OK, GPIO_MODE_OUTPUT, GPIO_PULLUP_DISABLE, GPIO_PULLDOWN_DISABLE, GPIO_INTR_DISABLE};
typedef struct { uint64_t pin_bit_mask; int mode, pull_up_en, pull_down_en, intr_type; } gpio_config_t;
static struct {
    union { struct { uint32_t source:1, other:31; }; uint32_t val; } pin[16];
    uint32_t sigma_delta;
} GPIO;
static TickType_t clock_tick;
static unsigned critical_depth, gpio_level, gpio_writes;
static int init_result;
static TickType_t xTaskGetTickCount(void) { return clock_tick; }
#define taskENTER_CRITICAL() do { assert(critical_depth == 0); ++critical_depth; } while (0)
#define taskEXIT_CRITICAL() do { assert(critical_depth == 1); --critical_depth; } while (0)
static esp_err_t gpio_set_level(int pin, int level) {
    assert(pin == 2 && critical_depth == 0);
    gpio_level = (unsigned)level; ++gpio_writes; return ESP_OK;
}
static esp_err_t gpio_config(const gpio_config_t *config) {
    assert(config->pin_bit_mask == (1ULL << 2)); return init_result;
}

/* LED_IMPLEMENTATION */

static void next_update(void) { clock_tick += STATUS_LED_UPDATE_MS; status_led_poll(); }
int main(void) {
    int16_t pcm[] = {0, -32768, 32767, -12, 3276};
    int16_t copy[5]; memcpy(copy, pcm, sizeof(pcm));
    status_led_capture_pcm(pcm, 5, 1); status_led_poll();
    assert(s_pending_peak == 0 && gpio_writes == 0);
    assert(status_led_wait_ticks(250) == 250);
    init_result = -1;
    assert(status_led_init() == -1 && !s_ready);
    init_result = ESP_OK;
    GPIO.pin[2].val = 0x240; GPIO.pin[3].val = 0xa5; GPIO.pin[15].val = 0x5a;
    assert(status_led_init() == ESP_OK);
    assert(gpio_level == BOARD_STATUS_LED_ACTIVE_LOW && GPIO.sigma_delta == 0);
    assert(status_led_wait_ticks(250) == STATUS_LED_UPDATE_MS);
    assert(status_led_wait_ticks(3) == 3);
    status_led_capture_pcm(pcm, 5, 1);
    assert(s_pending_peak == 32768 && memcmp(copy, pcm, sizeof(pcm)) == 0);
    clock_tick += STATUS_LED_UPDATE_MS - 1;
    status_led_poll(); assert(s_brightness == 0 && status_led_wait_ticks(250) == 1);
    ++clock_tick; assert(status_led_wait_ticks(250) == 0);
    status_led_poll(); assert(s_brightness == 255 && s_pending_peak == 0);
    assert(gpio_level == !BOARD_STATUS_LED_ACTIVE_LOW && GPIO.pin[2].source == 0);
    next_update(); assert(s_brightness == 255 - STATUS_LED_DECAY);
    assert(GPIO.pin[2].source == 1 && (GPIO.sigma_delta & SIGMA_DELTA_ENABLE));
    uint32_t duty = BOARD_STATUS_LED_ACTIVE_LOW ? 256U - s_brightness : s_brightness;
    assert((GPIO.sigma_delta & 255U) == duty && ((GPIO.sigma_delta >> 8) & 255U) == 255);
    assert((GPIO.pin[2].val & ~1U) == 0x240);
    assert(GPIO.pin[3].val == 0xa5 && GPIO.pin[15].val == 0x5a);
    unsigned writes = gpio_writes; status_led_poll(); assert(gpio_writes == writes);
    for (unsigned i = 0; i < 40; ++i) next_update();
    assert(s_brightness == 0 && GPIO.pin[2].source == 0 && GPIO.sigma_delta == 0);
    /* Only one snapshot per window; malformed input ignored. */
    status_led_capture_pcm(pcm + 1, 1, 1); status_led_capture_pcm(pcm, 1, 1);
    status_led_capture_pcm(NULL, 5, 1); status_led_capture_pcm(pcm, 5, 0);
    status_led_capture_pcm(pcm, 5, 3); assert(s_pending_peak == 32768);
    status_led_clear(); next_update(); assert(s_brightness == 0);
    int16_t stereo[] = {20000, -20000, -32768, 32767, 30000};
    status_led_capture_pcm(stereo, 5, 2); next_update(); assert(s_brightness == 0);
    int16_t stereo_full[] = {-32768, -32768};
    status_led_capture_pcm(stereo_full, 2, 2); next_update(); assert(s_brightness == 255);
    status_led_clear(); status_led_capture_pcm(pcm + 4, 1, 1); next_update();
    assert(s_brightness == 25); // New station after reset cannot keep old envelope.
    for (unsigned i = 0; i < 20; ++i) {
        status_led_capture_pcm(pcm + 4, 1, 1); next_update(); assert(s_brightness == 25);
    }
    status_led_clear(); next_update(); assert(s_brightness == 0);
    clock_tick = UINT32_MAX - 10; s_last_update = clock_tick;
    status_led_capture_pcm(pcm, 5, 1); next_update();
    assert(s_brightness == 255 && status_led_wait_ticks(250) == STATUS_LED_UPDATE_MS);
    for (unsigned brightness = 0; brightness <= 255; ++brightness) {
        set_brightness((uint8_t)brightness);
        if (brightness && brightness != 255) {
            duty = BOARD_STATUS_LED_ACTIVE_LOW ? 256U - brightness : brightness;
            assert((GPIO.sigma_delta & 255U) == duty && GPIO.pin[2].source == 1);
        }
    }
    status_led_clear(); next_update();
    int16_t large[128] = {0}; large[127] = INT16_MIN;
    status_led_capture_pcm(large, 128, 1);
    assert(!status_led_capture_requested && s_pending_peak == 0);
    /* No PCM walk on the remaining calls until app_main opens a new window. */
    for (unsigned i = 0; i < 10000; ++i) status_led_capture_pcm(pcm, 5, 1);
    assert(s_pending_peak == 0);
    next_update(); assert(status_led_capture_requested);
    status_led_capture_pcm(pcm, 5, 1); next_update(); assert(s_brightness == 255);
    assert(critical_depth == 0);
    puts("LED PASS: peak/mono/stereo/clear/decay/rate/wrap/polarity/256 levels, no PCM changes");
    return 0;
}
