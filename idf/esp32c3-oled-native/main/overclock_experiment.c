#include <stdbool.h>
#include <stdint.h>

#include "driver/gpio.h"
#include "esp_attr.h"
#include "esp_cpu.h"
#include "esp_log.h"
#include "esp_rom_sys.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "hal/clk_tree_ll.h"
#include "hal/regi2c_ctrl_ll.h"
#include "hal/rwdt_ll.h"
#include "hal/systimer_ll.h"
#include "hal/wdt_types.h"
#include "riscv/rv_utils.h"
#include "soc/regi2c_bbpll.h"
#include "soc/soc.h"
#include "soc/system_reg.h"
#include "soc/systimer_struct.h"

#define EXPERIMENT_BOOT_BUTTON_GPIO GPIO_NUM_9
#define EXPERIMENT_MAGIC 0x4f434333U
#define EXPERIMENT_MAGIC_INVERSE (~EXPERIMENT_MAGIC)
#define EXPERIMENT_WINDOW_TICKS 1600000U
#define EXPERIMENT_SYSTIMER_TICKS_PER_US 16U
#define EXPERIMENT_WATCHDOG_TIMEOUT_TICKS 500000U

typedef enum {
    EXPERIMENT_NOT_RUN = 0,
    EXPERIMENT_RUNNING = 1,
    EXPERIMENT_PASSED = 2,
    EXPERIMENT_WATCHDOG_RESET = 3,
} experiment_phase_t;

typedef struct {
    uint32_t magic;
    uint32_t magic_inverse;
    uint32_t phase;
    uint32_t measured_khz;
    uint32_t workload;
} experiment_state_t;

typedef struct {
    uint32_t reference_ticks;
    uint32_t cpu_cycles;
    uint32_t workload;
} experiment_sample_t;

static const char *const TAG = "c3_overclock";
static RTC_NOINIT_ATTR experiment_state_t s_experiment_state;

static bool experiment_state_valid(void) {
    return s_experiment_state.magic == EXPERIMENT_MAGIC &&
           s_experiment_state.magic_inverse == EXPERIMENT_MAGIC_INVERSE &&
           s_experiment_state.phase >= EXPERIMENT_RUNNING &&
           s_experiment_state.phase <= EXPERIMENT_WATCHDOG_RESET;
}

static void experiment_state_set(experiment_phase_t phase,
                                 uint32_t measured_khz,
                                 uint32_t workload) {
    s_experiment_state.magic = EXPERIMENT_MAGIC;
    s_experiment_state.magic_inverse = EXPERIMENT_MAGIC_INVERSE;
    s_experiment_state.phase = (uint32_t)phase;
    s_experiment_state.measured_khz = measured_khz;
    s_experiment_state.workload = workload;
}

static void wait_for_boot_press(void) {
    const gpio_config_t config = {
        .pin_bit_mask = 1ULL << EXPERIMENT_BOOT_BUTTON_GPIO,
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&config));
    while (gpio_get_level(EXPERIMENT_BOOT_BUTTON_GPIO) != 0) {
        vTaskDelay(pdMS_TO_TICKS(10));
    }
    vTaskDelay(pdMS_TO_TICKS(30));
    while (gpio_get_level(EXPERIMENT_BOOT_BUTTON_GPIO) == 0) {
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

static IRAM_ATTR __attribute__((noinline)) uint32_t systimer_counter_low(void) {
    systimer_ll_counter_snapshot(&SYSTIMER, 0);
    while (!systimer_ll_is_counter_value_valid(&SYSTIMER, 0)) {
    }
    return systimer_ll_get_counter_value_low(&SYSTIMER, 0);
}

/*
 * Espressif publishes only 320 and 480 MHz BBPLL tables for ESP32-C3. For a
 * 40 MHz crystal those tables use DIV_7_0 values 4 and 8 respectively. The
 * value 6 below is the linear midpoint used by Espressif's 400 MHz PLL table
 * on related clock hardware. It is intentionally confined to this profile.
 */
static IRAM_ATTR __attribute__((noinline)) void bbpll_program_400mhz(void) {
    const uint8_t div_ref = 0;
    const uint8_t div7_0 = 6;
    const uint8_t dr1 = 0;
    const uint8_t dr3 = 0;
    const uint8_t dchgp = 5;
    const uint8_t dcur = 3;
    const uint8_t dbias = 2;

    REGI2C_WRITE(I2C_BBPLL, I2C_BBPLL_MODE_HF, 0x6A);
    REGI2C_WRITE(I2C_BBPLL, I2C_BBPLL_OC_REF_DIV,
                 (dchgp << I2C_BBPLL_OC_DCHGP_LSB) | div_ref);
    REGI2C_WRITE(I2C_BBPLL, I2C_BBPLL_OC_DIV_7_0, div7_0);
    REGI2C_WRITE_MASK(I2C_BBPLL, I2C_BBPLL_OC_DR1, dr1);
    REGI2C_WRITE_MASK(I2C_BBPLL, I2C_BBPLL_OC_DR3, dr3);
    REGI2C_WRITE(I2C_BBPLL, I2C_BBPLL_OC_DCUR,
                 (2U << I2C_BBPLL_OC_DLREF_SEL_LSB) |
                     (1U << I2C_BBPLL_OC_DHREF_SEL_LSB) | dcur);
    REGI2C_WRITE_MASK(I2C_BBPLL, I2C_BBPLL_OC_VCO_DBIAS, dbias);
    REGI2C_WRITE_MASK(I2C_BBPLL, I2C_BBPLL_OC_DHREF_SEL, 2);
    REGI2C_WRITE_MASK(I2C_BBPLL, I2C_BBPLL_OC_DLREF_SEL, 1);
}

static IRAM_ATTR __attribute__((noinline)) void bbpll_program_official_480mhz(void) {
    clk_ll_bbpll_set_freq_mhz(480);
    regi2c_ctrl_ll_bbpll_calibration_start();
    clk_ll_bbpll_set_config(480, 40);
}

static IRAM_ATTR __attribute__((noinline)) experiment_sample_t run_200mhz_window(void) {
    experiment_sample_t sample = {0};

    rv_utils_intr_global_disable();

    /* Move the CPU away from BBPLL before changing its analog settings. */
    clk_ll_cpu_set_src(SOC_CPU_CLK_SRC_XTAL);
    clk_ll_cpu_set_divider(1);
    esp_rom_set_cpu_ticks_per_us(40);

    regi2c_ctrl_ll_bbpll_calibration_start();
    bbpll_program_400mhz();

    /* 320 MHz digital mode uses /2 for selector 1: 400 / 2 ~= 200 MHz. */
    clk_ll_bbpll_set_freq_mhz(320);
    REG_SET_FIELD(SYSTEM_CPU_PER_CONF_REG, SYSTEM_CPUPERIOD_SEL, 1);
    clk_ll_cpu_set_src(SOC_CPU_CLK_SRC_PLL);

    const uint32_t reference_start = systimer_counter_low();
    const uint32_t cycle_start = (uint32_t)esp_cpu_get_cycle_count();
    uint32_t reference_now = reference_start;
    uint32_t workload = 0x13579bdfU;
    do {
        workload ^= workload << 13;
        workload ^= workload >> 17;
        workload ^= workload << 5;
        reference_now = systimer_counter_low();
    } while ((uint32_t)(reference_now - reference_start) <
             EXPERIMENT_WINDOW_TICKS);
    const uint32_t cycle_end = (uint32_t)esp_cpu_get_cycle_count();

    /* Restore the documented 480 MHz BBPLL and 160 MHz CPU before returning. */
    clk_ll_cpu_set_src(SOC_CPU_CLK_SRC_XTAL);
    clk_ll_cpu_set_divider(1);
    esp_rom_set_cpu_ticks_per_us(40);
    bbpll_program_official_480mhz();
    REG_SET_FIELD(SYSTEM_CPU_PER_CONF_REG, SYSTEM_CPUPERIOD_SEL, 1);
    clk_ll_cpu_set_src(SOC_CPU_CLK_SRC_PLL);
    esp_rom_set_cpu_ticks_per_us(160);

    rv_utils_intr_global_enable();

    sample.reference_ticks = reference_now - reference_start;
    sample.cpu_cycles = cycle_end - cycle_start;
    sample.workload = workload;
    return sample;
}

static void watchdog_enable(void) {
    rtc_cntl_dev_t *watchdog = RWDT_DEV_GET();
    rwdt_ll_write_protect_disable(watchdog);
    rwdt_ll_disable(watchdog);
    rwdt_ll_set_flashboot_en(watchdog, false);
    rwdt_ll_disable_stage(watchdog, WDT_STAGE1);
    rwdt_ll_disable_stage(watchdog, WDT_STAGE2);
    rwdt_ll_disable_stage(watchdog, WDT_STAGE3);
    rwdt_ll_config_stage(watchdog, WDT_STAGE0,
                         EXPERIMENT_WATCHDOG_TIMEOUT_TICKS,
                         WDT_STAGE_ACTION_RESET_RTC);
    rwdt_ll_feed(watchdog);
    rwdt_ll_enable(watchdog);
    rwdt_ll_write_protect_enable(watchdog);
}

static void watchdog_disable(void) {
    rtc_cntl_dev_t *watchdog = RWDT_DEV_GET();
    rwdt_ll_write_protect_disable(watchdog);
    rwdt_ll_disable(watchdog);
    rwdt_ll_write_protect_enable(watchdog);
}

void app_main(void) {
    ESP_LOGW(TAG, "UNSUPPORTED ESP32-C3 BBPLL experiment; radio is disabled");
    ESP_LOGI(TAG, "Normal boot clock: %u MHz", esp_rom_get_cpu_ticks_per_us());

    if (experiment_state_valid()) {
        if (s_experiment_state.phase == EXPERIMENT_RUNNING) {
            experiment_state_set(EXPERIMENT_WATCHDOG_RESET, 0, 0);
            ESP_LOGE(TAG, "RTC watchdog recovered a failed 200 MHz attempt");
        } else if (s_experiment_state.phase == EXPERIMENT_PASSED) {
            ESP_LOGI(TAG, "Previous one-shot result: %lu.%03lu MHz, "
                          "workload=0x%08lx",
                     (unsigned long)(s_experiment_state.measured_khz / 1000U),
                     (unsigned long)(s_experiment_state.measured_khz % 1000U),
                     (unsigned long)s_experiment_state.workload);
        } else {
            ESP_LOGE(TAG, "Previous attempt ended in watchdog reset");
        }
        ESP_LOGW(TAG, "Press and release BOOT to clear the marker and rerun");
        wait_for_boot_press();
        s_experiment_state.magic = 0;
    } else {
        ESP_LOGW(TAG, "Press and release BOOT to start the unsupported test");
        wait_for_boot_press();
    }

    experiment_state_set(EXPERIMENT_RUNNING, 0, 0);
    ESP_LOGW(TAG, "Starting 100 ms 400 MHz BBPLL / ~200 MHz CPU window");
    watchdog_enable();
    experiment_sample_t sample = run_200mhz_window();
    watchdog_disable();

    uint32_t measured_khz = 0;
    if (sample.reference_ticks != 0) {
        measured_khz = (uint32_t)(((uint64_t)sample.cpu_cycles *
                                   EXPERIMENT_SYSTIMER_TICKS_PER_US * 1000ULL) /
                                  sample.reference_ticks);
    }
    experiment_state_set(EXPERIMENT_PASSED, measured_khz, sample.workload);
    ESP_LOGI(TAG, "Measured CPU frequency: %lu.%03lu MHz",
             (unsigned long)(measured_khz / 1000U),
             (unsigned long)(measured_khz % 1000U));
    ESP_LOGI(TAG, "Reference ticks=%lu cycles=%lu workload=0x%08lx",
             (unsigned long)sample.reference_ticks,
             (unsigned long)sample.cpu_cycles,
             (unsigned long)sample.workload);
    ESP_LOGI(TAG, "CPU and BBPLL restored to documented 160/480 MHz");
    ESP_LOGI(TAG, "Reset normally, then press BOOT to run it again");

    while (true) vTaskDelay(pdMS_TO_TICKS(1000));
}
