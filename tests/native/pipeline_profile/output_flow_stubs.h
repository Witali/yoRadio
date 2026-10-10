#include <assert.h>
#include <stdint.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>
#include "pipeline_wait.h"

#define DECODE_STATS_INTERVAL_US 5000000LL
static int64_t test_now;
static uint32_t test_overruns;
static unsigned test_logs, test_dma_reads;
static char test_log[512];
static pipeline_wait_t test_dma;
static int64_t esp_timer_get_time(void) { return test_now; }
static uint32_t native_audio_output_dma_overruns(void) { return test_overruns; }
static pipeline_wait_t native_i2s_take_wait_profile(void) {
    ++test_dma_reads;
    pipeline_wait_t result = test_dma;
    test_dma = (pipeline_wait_t){0};
    return result;
}
static void test_capture_log(const char *format, ...) {
    va_list args;
    va_start(args, format);
    int length = vsnprintf(test_log, sizeof(test_log), format, args);
    va_end(args);
    assert(length > 0 && length < (int)sizeof(test_log));
    ++test_logs;
    ++test_overruns; // ISR between the counter read and stats reset.
}
#define ESP_LOGI(tag, ...) test_capture_log(__VA_ARGS__)
