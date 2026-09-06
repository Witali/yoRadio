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
#include "esp8266_nodac_i2s.h"
#include "nvs_flash.h"
#include "persistent_settings.h"

#define BENCHMARK_SAMPLE_RATE 48000U
#define BENCHMARK_FRAMES 128U
#define BENCHMARK_CHANNELS 2U
#define BENCHMARK_WARMUP_US 2000000LL
#define BENCHMARK_MEASURE_US 10000000LL

#ifndef YORADIO_ESP8266_AUDIO_OUTPUT_TONE_TEST
#define YORADIO_ESP8266_AUDIO_OUTPUT_TONE_TEST 0
#endif

#define TONE_PERIOD_FRAMES 48U
#define TONE_HALF_CYCLE_FRAMES (BENCHMARK_SAMPLE_RATE / 2U)
#define TONE_GATE_CYCLE_FRAMES BENCHMARK_SAMPLE_RATE

static const char *TAG = "audio_output_bench";
#if !YORADIO_ESP8266_AUDIO_OUTPUT_TONE_TEST
static int16_t s_template[BENCHMARK_FRAMES * BENCHMARK_CHANNELS];
#endif
static int16_t s_pcm[BENCHMARK_FRAMES * BENCHMARK_CHANNELS];
#if YORADIO_ESP8266_AUDIO_OUTPUT_TONE_TEST
static const int16_t s_sine_1khz[TONE_PERIOD_FRAMES] = {
         0,   4277,   8481,  12539,  16383,  19947,  23170,  25996,
     28377,  30273,  31650,  32487,  32767,  32487,  31650,  30273,
     28377,  25996,  23170,  19947,  16383,  12539,   8481,   4277,
         0,  -4277,  -8481, -12539, -16383, -19947, -23170, -25996,
    -28377, -30273, -31650, -32487, -32767, -32487, -31650, -30273,
    -28377, -25996, -23170, -19947, -16384, -12539,  -8481,  -4277,
};
static uint32_t s_tone_frame;
#endif
static uint64_t s_spi_wait_us;
static uint32_t s_spi_wait_max_us;
static uint32_t s_spi_wait_calls;
static uint32_t s_spi_wait_invalid;
static int64_t s_spi_wait_started;
static uint32_t s_write_invalid;

#if YORADIO_ESP8266_OUTPUT_COMPARE
extern uint32_t native_audio_output_benchmark_pack32(const int16_t *, size_t, unsigned);
#endif

static int64_t benchmark_time_us(void) {
    /* SysTick resets CCOUNT while adding it to g_esp_os_us in this SDK.
     * Protect only the timestamp read, never packing or DMA waiting. */
    taskENTER_CRITICAL();
    int64_t stamp = esp_timer_get_time();
    taskEXIT_CRITICAL();
    return stamp;
}

void audio_output_benchmark_spi_wait_begin(void) {
    s_spi_wait_started = benchmark_time_us();
}

void audio_output_benchmark_spi_wait_end(void) {
    int64_t elapsed64 = benchmark_time_us() - s_spi_wait_started;
    if (elapsed64 < 0 || elapsed64 > 200000) {
        ++s_spi_wait_invalid;
        return;
    }
    uint32_t elapsed = (uint32_t)elapsed64;
    s_spi_wait_us += elapsed;
    if (elapsed > s_spi_wait_max_us) s_spi_wait_max_us = elapsed;
    ++s_spi_wait_calls;
}

#if !YORADIO_ESP8266_AUDIO_OUTPUT_TONE_TEST
static void generate_pcm(void) {
    uint32_t left = 0x82661234U;
    uint32_t right = 0x32082667U;
    for (size_t frame = 0; frame < BENCHMARK_FRAMES; ++frame) {
        left = left * 1664525U + 1013904223U;
        right = right * 22695477U + 1U;
        s_template[frame * 2U] = (int16_t)(left >> 18);
        s_template[frame * 2U + 1U] = (int16_t)(right >> 18);
#if YORADIO_ESP8266_OUTPUT_COMPARE
        s_template[frame * 2U] = (int16_t)(left >> 16);
        s_template[frame * 2U + 1U] = (int16_t)(right >> 16);
#endif
    }
}

#endif

#if YORADIO_ESP8266_AUDIO_OUTPUT_TONE_TEST
static void generate_tone_pcm(void) {
    for (size_t frame = 0; frame < BENCHMARK_FRAMES; ++frame) {
        int16_t sample = s_tone_frame < TONE_HALF_CYCLE_FRAMES
            ? s_sine_1khz[s_tone_frame % TONE_PERIOD_FRAMES] : 0;
        s_pcm[frame * 2U] = sample;
        s_pcm[frame * 2U + 1U] = sample;
        if (++s_tone_frame == TONE_GATE_CYCLE_FRAMES) s_tone_frame = 0;
    }
}
#endif
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
    while (benchmark_time_us() < deadline) {
#if YORADIO_ESP8266_AUDIO_OUTPUT_TONE_TEST
        generate_tone_pcm();
#else
        memcpy(s_pcm, s_template, sizeof(s_pcm));
#endif
        int64_t started = benchmark_time_us();
        esp_err_t result = native_audio_output_write(
            s_pcm, sizeof(s_pcm) / sizeof(s_pcm[0]),
            BENCHMARK_SAMPLE_RATE, BENCHMARK_CHANNELS);
        int64_t elapsed64 = benchmark_time_us() - started;
        uint32_t elapsed = 0;
        if (elapsed64 < 0 || elapsed64 > 200000) {
            ++s_write_invalid;
        } else {
            elapsed = (uint32_t)elapsed64;
        }
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
#if YORADIO_ESP8266_AUDIO_OUTPUT_TONE_TEST || YORADIO_ESP8266_OUTPUT_COMPARE
    settings.volume = 254;
    settings.balance = 0;
    settings.normalization_enabled = false;
#if YORADIO_ESP8266_OUTPUT_COMPARE
    settings.volume = 64; // keep physical generated noise below full amplitude
#endif
    result = persistent_settings_update_runtime(&settings);
    if (result != ESP_OK) {
        ESP_LOGE(TAG, "Tone settings failed: %s", esp_err_to_name(result));
        return;
    }
#endif
#if YORADIO_ESP8266_OUTPUT_COMPARE && !YORADIO_ESP8266_AUDIO_OUTPUT_TONE_TEST
    generate_pcm();
    for (unsigned round = 0; round < 3; ++round) {
        int64_t started = benchmark_time_us();
        uint32_t checksum = native_audio_output_benchmark_pack32(s_template, 128, 375);
        uint32_t elapsed = (uint32_t)(benchmark_time_us() - started);
        ESP_LOGI(TAG, "pack_only round=%u samples=48000 elapsed=%u us checksum=%08x DMA=off", round, elapsed, checksum);
        vTaskDelay(1);
    }
#endif
    result = native_audio_output_init();
    if (result != ESP_OK) {
        ESP_LOGE(TAG, "Output init failed: %s", esp_err_to_name(result));
        return;
    }
    native_audio_output_set_volume_runtime(254);
#if YORADIO_ESP8266_OUTPUT_COMPARE
    native_audio_output_set_volume_runtime(64);
#endif
    native_audio_output_set_balance_runtime(0);
    native_audio_output_reset_normalizer();
#if YORADIO_ESP8266_AUDIO_OUTPUT_TONE_TEST
    s_tone_frame = 0;
    ESP_LOGI(TAG,
             "tone test: 1000 Hz full-scale stereo PCM at 48 kHz, "
             "500 ms on / 500 ms silence; normalization=off, "
             "Wi-Fi=off, codec=off");
    for (;;) {
        if (!run_until(benchmark_time_us() + 1000000LL,
                       NULL, NULL, NULL)) return;
    }
#else
    generate_pcm();
    ESP_LOGI(TAG,
             "generated PCM: stereo 48 kHz, 128 frames/512 bytes; "
             "normalization=%u, Wi-Fi=off, codec=off",
             settings.normalization_enabled ? 1U : 0U);

    if (!run_until(benchmark_time_us() + BENCHMARK_WARMUP_US,
                   NULL, NULL, NULL)) return;
    native_audio_output_reset_spi_stats();
    s_spi_wait_us = 0;
    s_spi_wait_max_us = 0;
    s_spi_wait_calls = 0;
    s_spi_wait_invalid = 0;
    s_write_invalid = 0;
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
#if YORADIO_ESP8266_I2S_PDM
    esp8266_nodac_profile_t dma_before;
    esp8266_nodac_i2s_profile(&dma_before);
#endif
    uint64_t write_us = 0;
    uint32_t maximum_us = 0;
    int64_t started = benchmark_time_us();
    if (!run_until(started + BENCHMARK_MEASURE_US,
                   &calls, &write_us, &maximum_us)) return;
    uint64_t wall_us = (uint64_t)(benchmark_time_us() - started);
    native_audio_output_spi_stats_t spi_stats;
    native_audio_output_get_spi_stats(&spi_stats);
#if YORADIO_ESP8266_I2S_PDM
    esp8266_nodac_profile_t dma_after;
    esp8266_nodac_i2s_profile(&dma_after);
#endif
    native_audio_output_silence();
#if configGENERATE_RUN_TIME_STATS == 1
    have_cpu = have_cpu && cpu_snapshot(&cpu_total_after, &cpu_idle_after);
#endif
    uint64_t audio_us = (uint64_t)calls * BENCHMARK_FRAMES * 1000000ULL /
                        BENCHMARK_SAMPLE_RATE;
    uint32_t realtime_x10 = wall_us
        ? (uint32_t)(audio_us * 1000ULL / wall_us) : 0;
    ESP_LOGI(TAG,
             "result calls=%u wall=%u us audio=%u us realtime=%u.%u%% "
             "write=%u us avg=%u us max=%u us invalid=%u",
             calls, (unsigned)wall_us, (unsigned)audio_us,
             realtime_x10 / 10U, realtime_x10 % 10U,
             (unsigned)write_us, calls ? (unsigned)(write_us / calls) : 0U,
             maximum_us, s_write_invalid);
    ESP_LOGI(TAG,
             "spi_wait=%u us calls=%u avg=%u us max=%u us invalid=%u",
             (unsigned)s_spi_wait_us, s_spi_wait_calls,
             s_spi_wait_calls
                 ? (unsigned)(s_spi_wait_us / s_spi_wait_calls) : 0U,
             s_spi_wait_max_us, s_spi_wait_invalid);
    if (write_us >= s_spi_wait_us) {
        uint64_t active = write_us - s_spi_wait_us;
        ESP_LOGI(TAG, "producer_nonwait=%u us avg=%u us per_audio_second=%u us; wall-time estimate, not total CPU load",
                 (unsigned)active, calls ? (unsigned)(active / calls) : 0U,
                 audio_us ? (unsigned)(active * 1000000ULL / audio_us) : 0U);
    }
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
#if YORADIO_ESP8266_I2S_PDM
    ESP_LOGI(TAG, "dma eof=%u partial_start=%u blocked_partial=%u fifo_empty=%u",
             (unsigned)(dma_after.eof_count - dma_before.eof_count),
             (unsigned)(dma_after.partial_starts - dma_before.partial_starts),
             (unsigned)(dma_after.blocked_partial - dma_before.blocked_partial),
             (unsigned)(dma_after.fifo_empty - dma_before.fifo_empty));
    ESP_LOGI(TAG, "stalled producer (65 ms): %s",
             esp8266_nodac_i2s_test_stalled_producer() ? "PASS" : "FAIL");
#endif
    ESP_LOGI(TAG, "complete");
#endif
}
