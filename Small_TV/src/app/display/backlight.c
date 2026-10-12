#include "display.h"
#include "board.h"
#include "driver/ledc.h"

esp_err_t backlight_init(void)
{
    ledc_timer_config_t timer = {.speed_mode=LEDC_LOW_SPEED_MODE,.timer_num=LEDC_TIMER_0,
        .duty_resolution=LEDC_TIMER_13_BIT,.freq_hz=1000,.clk_cfg=LEDC_AUTO_CLK};
    esp_err_t result=ledc_timer_config(&timer);
    if (result!=ESP_OK) return result;
    ledc_channel_config_t channel = {.gpio_num=LCD_GPIO_BACKLIGHT,.speed_mode=LEDC_LOW_SPEED_MODE,
        .channel=LEDC_CHANNEL_0,.timer_sel=LEDC_TIMER_0,.duty=819,.hpoint=0};
    return ledc_channel_config(&channel);
}

void backlight_set_level(unsigned per_mille)
{
    if (per_mille>1000) per_mille=1000;
    ESP_ERROR_CHECK(ledc_set_duty(LEDC_LOW_SPEED_MODE,LEDC_CHANNEL_0,per_mille*8191/1000));
    ESP_ERROR_CHECK(ledc_update_duty(LEDC_LOW_SPEED_MODE,LEDC_CHANNEL_0));
}

void backlight_update(const tv_settings_t *s,int local_hour,bool clock_valid)
{
    bool night=clock_valid && s->night_mode && (local_hour>=s->night_start || local_hour<s->night_stop);
    backlight_set_level(night?s->night_level:s->day_level);
}
