#pragma once
#include <stdbool.h>
#include <stdint.h>
#define CONFIG_YORADIO_DEEP_SLEEP_CLOCK 1
#define GPIO_NUM_3 3
#define GPIO_NUM_5 5
#define GPIO_NUM_6 6
#define GPIO_NUM_9 9
#define GPIO_NUM_10 10
#define IO_MUX_GPIO0_REG 0
#define FUN_IE 1
#define FUN_PU 2
#define FUN_PD 4
#define RTC_CNTL_DIG_ISO_REG 4
#define RTC_CNTL_CLR_DG_PAD_AUTOHOLD 8
#define SIG_GPIO_OUT_IDX 256
#define REG_SET_BIT(reg, bits) ((void)(reg), (void)(bits))
#define REG_CLR_BIT(reg, bits) ((void)(reg), (void)(bits))
typedef struct { int unused; } gpio_dev_t;
extern gpio_dev_t GPIO;
void esp_rom_gpio_pad_select_gpio(unsigned pin);
void esp_rom_gpio_connect_out_signal(unsigned pin, unsigned signal, bool inv, bool oen);
void gpio_ll_output_disable(gpio_dev_t *gpio, unsigned pin);
void gpio_ll_output_enable(gpio_dev_t *gpio, unsigned pin);
void gpio_ll_od_enable(gpio_dev_t *gpio, unsigned pin);
void gpio_ll_set_level(gpio_dev_t *gpio, unsigned pin, unsigned level);
unsigned gpio_ll_get_level(gpio_dev_t *gpio, unsigned pin);
void esp_rom_delay_us(unsigned us);
uint64_t rtc_timer_ll_get_cycle_count(unsigned id);
void esp_default_wake_deep_sleep(void);
void esp_wake_stub_set_wakeup_time(uint64_t us);
void esp_wake_stub_sleep(void (*stub)(void));
