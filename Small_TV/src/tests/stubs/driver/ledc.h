#pragma once
#include "esp_err.h"
enum
{
    LEDC_LOW_SPEED_MODE,
    LEDC_TIMER_0,
    LEDC_TIMER_13_BIT,
    LEDC_AUTO_CLK,
    LEDC_CHANNEL_0
};
typedef struct
{
    int speed_mode, timer_num, duty_resolution, clk_cfg;
    unsigned freq_hz;
} ledc_timer_config_t;
typedef struct
{
    int gpio_num, speed_mode, channel, timer_sel;
    unsigned duty, hpoint;
} ledc_channel_config_t;
esp_err_t ledc_timer_config(const ledc_timer_config_t *config);
esp_err_t ledc_channel_config(const ledc_channel_config_t *config);
esp_err_t ledc_set_duty(int mode, int channel, unsigned duty);
esp_err_t ledc_update_duty(int mode, int channel);
