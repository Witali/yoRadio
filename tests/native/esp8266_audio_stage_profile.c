#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
static uint32_t now, missed, ticks, s_generation = 3;
static unsigned critical_depth;
typedef struct { uint32_t queue_empty_events; } native_audio_output_spi_stats_t;
static void native_audio_output_get_spi_stats(native_audio_output_spi_stats_t *s) { s->queue_empty_events = missed; }
static uint32_t esp_timer_get_time(void) { assert(critical_depth > 0); return now; }
static uint32_t xTaskGetTickCount(void) { return ticks; }
#define portTICK_PERIOD_MS 1
#define taskENTER_CRITICAL() (++critical_depth)
#define taskEXIT_CRITICAL() (assert(critical_depth > 0), --critical_depth)
#define YORADIO_ESP8266_OPUS_STREAM_TEST 1
#include "audio_stage_profile.inc"
int main(void) {
    AUDIO_STAGE_BEGIN(decode);
    now = 10;
    AUDIO_STAGE_BEGIN(output);
    now = 35; missed = 2;
    AUDIO_STAGE_END(AUDIO_STAGE_OUTPUT, output);
    now = 50; missed = 3;
    AUDIO_STAGE_END(AUDIO_STAGE_DECODE, decode);
    assert(s_stages[AUDIO_STAGE_DECODE].us == 25);
    assert(s_stages[AUDIO_STAGE_DECODE].misses == 1);
    assert(s_stages[AUDIO_STAGE_OUTPUT].us == 25);
    assert(s_stages[AUDIO_STAGE_OUTPUT].misses == 2);
    assert(s_stages[AUDIO_STAGE_DECODE].maximum == 25);
    now = UINT32_MAX - 10; missed = UINT32_MAX - 1;
    s_stages[AUDIO_STAGE_READ].us = UINT32_MAX - 3;
    AUDIO_STAGE_BEGIN(read);
    now = 9; missed = 2;
    AUDIO_STAGE_END(AUDIO_STAGE_READ, read);
    assert(s_stages[AUDIO_STAGE_READ].us == 16);
    assert(s_stages[AUDIO_STAGE_READ].misses == 4);
    AUDIO_STAGE_BEGIN(reset);
    missed = 0; now += 3;
    AUDIO_STAGE_END(AUDIO_STAGE_WAIT, reset);
    assert(s_stages[AUDIO_STAGE_WAIT].misses == 0);
    AUDIO_STAGE_BEGIN(input_wait);
    missed += 7; now += 123;
    AUDIO_STAGE_END(AUDIO_STAGE_INPUT_WAIT, input_wait);
    assert(s_stages[AUDIO_STAGE_INPUT_WAIT].us == 123);
    assert(s_stages[AUDIO_STAGE_INPUT_WAIT].misses == 7);
    assert(s_stages[AUDIO_STAGE_WAIT].misses == 0);
    assert(sizeof(s_stages) == 80);
    /* Worst-case values fit the shared HTTP buffer; test exact capacity. */
    memset(s_stages, 0xff, sizeof(s_stages));
    char json[1088];
    int n = audio_service_stage_json(json, sizeof(json));
    assert(n > 0 && n < (int)sizeof(json));
    assert(strstr(json, "\"profile_version\":2"));
    assert(strstr(json, "[4294967295,4294967295,4294967295,4294967295]"));
    assert(audio_service_stage_json(json, (size_t)n + 1) == n);
    assert(audio_service_stage_json(json, (size_t)n) == -1);
    assert(audio_service_stage_json(json, 0) == -1);
    assert(critical_depth == 0);
    puts("stage accounting PASS: exclusive nested output, rollover, DMA reset, bounded JSON");
}
