#include "display.h"
#include "media.h"
#include "network.h"
#include "services.h"
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <math.h>
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static void time_labels(const tv_settings_t *s,const struct tm *local,bool valid,char *clock,char *date)
{
    if (!valid) {strcpy(clock,"--:--:--"); strcpy(date,"Waiting for time sync"); return;}
    int hour=local->tm_hour; if (s->hour12) {hour%=12; if (!hour) hour=12;}
    snprintf(clock,16,"%02d:%02d:%02d",hour,local->tm_min,local->tm_sec);
    static const char *const formats[]={"%m/%d/%Y","%d/%m/%Y","%Y/%m/%d"};
    strftime(date,32,formats[s->date_format],local);
}

static void weather_labels(const tv_settings_t *s,const weather_snapshot_t *weather)
{
    char value[32];
    if (!weather->valid) {display_text(6,120,"Set city and weather key",1,0x8410,0); return;}
    float temperature=s->fahrenheit?weather->temperature_c*1.8f+32:weather->temperature_c;
    float wind=weather->wind_mps*(s->miles?2.236936f:3.6f);
    snprintf(value,sizeof(value),"%.1f %c  %d%%",temperature,s->fahrenheit?'F':'C',weather->humidity);
    display_text(6,120,value,2,s->colors[1],0);
    snprintf(value,sizeof(value),"%.1f %s",wind,s->miles?"mph":"km/h");
    display_text(6,218,value,1,s->colors[2],0);
    media_draw_weather(weather->icon,178,155);
}

static void dial(const struct tm *local,bool valid,const tv_settings_t *s)
{
    for (int i=0; i<60; ++i) {
        float angle=i*0.104719755f;
        int inner=i%5?65:59;
        display_line(120+inner*sinf(angle),86-inner*cosf(angle),120+69*sinf(angle),86-69*cosf(angle),s->colors[2]);
    }
    if (!valid) return;
    float seconds=local->tm_sec*0.104719755f;
    float minutes=(local->tm_min+local->tm_sec/60.0f)*0.104719755f;
    float hours=((local->tm_hour%12)+local->tm_min/60.0f)*0.523598776f;
    display_line(120,86,120+37*sinf(hours),86-37*cosf(hours),s->colors[1]);
    display_line(120,86,120+53*sinf(minutes),86-53*cosf(minutes),s->colors[2]);
    display_line(120,86,120+59*sinf(seconds),86-59*cosf(seconds),s->colors[0]);
}

static void clock_task(void *unused)
{
    (void)unused;
    unsigned animation_frame=0,photo=0;
    uint32_t previous_generation=0,previous_weather=0;
    time_t previous_second=0;
    int64_t next_photo=0;
    bool first=true,previous_online=false;
    for (;;) {
        tv_settings_t s; weather_snapshot_t weather; settings_snapshot(&s); weather_snapshot(&weather);
        time_t now=time(NULL); struct tm local; localtime_r(&now,&local); bool valid=local.tm_year>=125;
        uint32_t generation=settings_generation(); bool online=network_connected();
        bool changed=first || previous_generation!=generation || previous_weather!=weather.generation || previous_online!=online;
        backlight_update(&s,local.tm_hour,valid);
        if (media_upload_active()) {vTaskDelay(pdMS_TO_TICKS(100)); continue;}
        char clock[16],date[32]; time_labels(&s,&local,valid,clock,date);
        if (s.theme==2) {
            int64_t monotonic=esp_timer_get_time();
            if (changed || monotonic>=next_photo) {
                if (!changed) photo=(photo+1)%PHOTO_COUNT;
                unsigned tries=0;
                while (tries<PHOTO_COUNT && (!(s.photo_mask&(1u<<photo)) || !s.photo_size[photo])) {photo=(photo+1)%PHOTO_COUNT; ++tries;}
                display_fill(0,0,240,240,0);
                if (tries==PHOTO_COUNT) display_text(30,90,"No enabled photos",1,0xffff,0);
                else if (media_draw_photo(photo)!=ESP_OK) display_text(24,90,"Photo decode failed",1,0xf800,0);
                next_photo=monotonic+(int64_t)s.photo_seconds*1000000;
            }
            if (changed || now!=previous_second) {
                display_fill(0,192,240,48,0); display_text(24,194,clock,3,s.colors[2],0);
            }
        } else {
            if (changed || now!=previous_second) {
                display_fill(0,0,240,240,0);
                if (s.theme==0) {
                    display_text(6,14,s.city,1,s.colors[2],0);
                    char hours[6]; memcpy(hours,clock,5); hours[5]=0;
                    display_text(18,28,hours,5,s.colors[0],0); display_text(186,52,clock+6,2,s.colors[1],0);
                    display_text(18,98,date,1,s.colors[2],0); weather_labels(&s,&weather);
                } else if (s.theme==1) {
                    display_text(24,45,clock,4,s.colors[0],0); display_text(60,110,date,1,s.colors[2],0);
                } else {
                    dial(&local,valid,&s); display_text(72,164,clock,2,s.colors[0],0);
                    display_text(60,192,date,1,s.colors[2],0);
                }
                if (!online) display_text(6,0,network_ap_active()?"Setup: 192.168.43.1":"Connecting to Wi-Fi",1,0x07ff,0);
                else {char address[20]; network_address(address,sizeof(address)); display_text(6,0,address,1,0x8410,0);}
            }
            if (s.theme<2) {
                unsigned frames=media_animation_frames(s.animation);
                if (frames) media_draw_animation(s.animation,(animation_frame++)%frames,83,143);
            }
        }
        first=false; previous_generation=generation; previous_weather=weather.generation; previous_online=online; previous_second=now;
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

void clock_ui_start(void) {configASSERT(xTaskCreate(clock_task,"clock_display",4096,NULL,2,NULL)==pdPASS);}
