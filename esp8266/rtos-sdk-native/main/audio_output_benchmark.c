#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "esp_log.h"
#include "esp_system.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "native_audio_output.h"
#include "nvs_flash.h"
#include "persistent_settings.h"

#define BENCHMARK_SAMPLE_RATE 48000U
#define BENCHMARK_FRAMES 128U
#define BENCHMARK_CHANNELS 2U
#define BENCHMARK_WARMUP_US 2000000LL
#define BENCHMARK_MEASURE_US 10000000LL

static const char *TAG = "audio_output_bench";
static int16_t s_template[BENCHMARK_FRAMES * BENCHMARK_CHANNELS];
static int16_t s_pcm[BENCHMARK_FRAMES * BENCHMARK_CHANNELS];
static uint64_t s_spi_wait_us;
static uint32_t s_spi_wait_max_us;
static uint32_t s_spi_wait_calls;
static uint32_t s_spi_wait_invalid;
static int64_t s_spi_wait_started;

void audio_output_benchmark_spi_wait_begin(void) {
    s_spi_wait_started = esp_timer_get_time();
}

void audio_output_benchmark_spi_wait_end(void) {
    int64_t elapsed64 = esp_timer_get_time() - s_spi_wait_started;
    if (elapsed64 < 0 || elapsed64 > 200000) {
        ++s_spi_wait_invalid;
        return;
    }
    uint32_t elapsed = (uint32_t)elapsed64;
    s_spi_wait_us += elapsed;
    if (elapsed > s_spi_wait_max_us) s_spi_wait_max_us = elapsed;
    ++s_spi_wait_calls;
}

static void generate_pcm(void) {
    uint32_t left = 0x82661234U;
    uint32_t right = 0x32082667U;
    for (size_t frame = 0; frame < BENCHMARK_FRAMES; ++frame) {
        left = left * 1664525U + 1013904223U;
        right = right * 22695477U + 1U;
        s_template[frame * 2U] = (int16_t)(left >> 18);
        s_template[frame * 2U + 1U] = (int16_t)(right >> 18);
    }
}

#if configGENERATE_RUN_TIME_STATS == 1
static bool cpu_snapshot(uint32_t *total, uint32_t *idle) {
    static TaskStatus_t tasks[16];
    uint32_t runtime = 0;
    UBaseType_t count = uxTaskGetSystemState(
        tasks, sizeof(tasks) / sizeof(tasks[0]), &runtime);
    if (!count || !runtime) return false;
    uint32_t idle_runtime = 0;
    for (UBaseType_t index = 0; index < count; ++index) {
        if (tasks[index].pcTaskName &&
            strcmp(tasks[index].pcTaskName, "IDLE") == 0)
            idle_runtime += tasks[index].ulRunTimeCounter;
    }
    *total = runtime;
    *idle = idle_runtime;
    return true;
}
#endif

static bool run_until(int64_t deadline, uint32_t *calls,
                      uint64_t *write_us, uint32_t *maximum_us) {
    while (esp_timer_get_time() < deadline) {
        memcpy(s_pcm, s_template, sizeof(s_pcm));
        int64_t started = esp_timer_get_time();
        esp_err_t result = native_audio_output_write(
            s_pcm, sizeof(s_pcm) / sizeof(s_pcm[0]),
            BENCHMARK_SAMPLE_RATE, BENCHMARK_CHANNELS);
        uint32_t elapsed = (uint32_t)(esp_timer_get_time() - started);
        if (result != ESP_OK) {
            ESP_LOGE(TAG, "PCM write failed: %s", esp_err_to_name(result));
            return false;
        }
        if (calls) ++*calls;
        if (write_us) *write_us += elapsed;
        if (maximum_us && elapsed > *maximum_us) *maximum_us = elapsed;
    }
    return true;
}

void audio_output_benchmark_run(void) {
    esp_err_t result = nvs_flash_init();
    if (result != ESP_OK) {
        ESP_LOGE(TAG, "NVS init failed: %s", esp_err_to_name(result));
        return;
    }
    result = persistent_settings_init();
    if (result != ESP_OK) {
        ESP_LOGE(TAG, "Settings init failed: %s", esp_err_to_name(result));
        return;
    }
    persistent_settings_t settings;
    persistent_settings_get(&settings);
    result = native_audio_output_init();
    if (result != ESP_OK) {
        ESP_LOGE(TAG, "Output init failed: %s", esp_err_to_name(result));
        return;
    }
    native_audio_output_set_volume_runtime(254);
    native_audio_output_set_balance_runtime(0);
    native_audio_output_reset_normalizer();
    generate_pcm();
    ESP_LOGI(TAG,
             "generated PCM: stereo 48 kHz, 128 frames/512 bytes; "
             "normalization=%u, Wi-Fi=off, codec=off",
             settings.normalization_enabled ? 1U : 0U);

    if (!run_until(esp_timer_get_time() + BENCHMARK_WARMUP_US,
                   NULL, NULL, NULL)) return;
    native_audio_output_reset_spi_stats();
    s_spi_wait_us = 0;
    s_spi_wait_max_us = 0;
    s_spi_wait_calls = 0;
    s_spi_wait_invalid = 0;
    uint32_t cpu_total_before = 0;
    uint32_t cpu_idle_before = 0;
    uint32_t cpu_total_after = 0;
    uint32_t cpu_idle_after = 0;
#if configGENERATE_RUN_TIME_STATS == 1
    bool have_cpu = cpu_snapshot(&cpu_total_before, &cpu_idle_before);
#else
    bool have_cpu = false;
#endif
    uint32_t calls = 0;
    uint64_t write_us = 0;
    uint32_t maximum_us = 0;
    int64_t started = esp_timer_get_time();
    if (!run_until(started + BENCHMARK_MEASURE_US,
                   &calls, &write_us, &maximum_us)) return;
    uint64_t wall_us = (uint64_t)(esp_timer_get_time() - started);
#if configGENERATE_RUN_TIME_STATS == 1
    have_cpu = have_cpu && cpu_snapshot(&cpu_total_after, &cpu_idle_after);
#endif
    uint64_t audio_us = (uint64_t)calls * BENCHMARK_FRAMES * 1000000ULL /
                        BENCHMARK_SAMPLE_RATE;
    uint32_t realtime_x10 = wall_us
        ? (uint32_t)(audio_us * 1000ULL / wall_us) : 0;
    ESP_LOGI(TAG,
             "result calls=%u wall=%u us audio=%u us realtime=%u.%u%% "
             "write=%u us avg=%u us max=%u us",
             calls, (unsigned)wall_us, (unsigned)audio_us,
             realtime_x10 / 10U, realtime_x10 % 10U,
             (unsigned)write_us, calls ? (unsigned)(write_us / calls) : 0U,
             maximum_us);
    ESP_LOGI(TAG,
             "spi_wait=%u us calls=%u avg=%u us max=%u us invalid=%u",
             (unsigned)s_spi_wait_us, s_spi_wait_calls,
             s_spi_wait_calls
                 ? (unsigned)(s_spi_wait_us / s_spi_wait_calls) : 0U,
             s_spi_wait_max_us, s_spi_wait_invalid);
    native_audio_output_spi_stats_t spi_stats;
    native_audio_output_get_spi_stats(&spi_stats);
    ESP_LOGI(TAG,
             "spi_gap cycles=%u calls=%u avg=%u max=%u empty=%u",
             spi_stats.gap_cycles_total, spi_stats.chained_transfers,
             spi_stats.chained_transfers
                 ? spi_stats.gap_cycles_total / spi_stats.chained_transfers : 0U,
             spi_stats.gap_cycles_max, spi_stats.queue_empty_events);
    if (have_cpu) {
        uint32_t total = cpu_total_after - cpu_total_before;
        uint32_t idle = cpu_idle_after - cpu_idle_before;
        uint32_t idle_x10 = total ? idle * 1000U / total : 0U;
        if (idle_x10 > 1000U) idle_x10 = 1000U;
        ESP_LOGI(TAG, "cpu busy=%u.%u%% idle=%u.%u%%",
                 (1000U - idle_x10) / 10U, (1000U - idle_x10) % 10U,
                 idle_x10 / 10U, idle_x10 % 10U);
    }
    ESP_LOGI(TAG, "heap free=%u min_free=%u",
             (unsigned)esp_get_free_heap_size(),
             (unsigned)esp_get_minimum_free_heap_size());
    native_audio_output_silence();
    ESP_LOGI(TAG, "complete");
}
