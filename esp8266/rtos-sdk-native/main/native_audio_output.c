#include "native_audio_output.h"

#include <stdbool.h>
#include <limits.h>
#include <stdlib.h>
#include <string.h>

#include "board_config.h"
#include "spi_pdm_config.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "sdkconfig.h"
#if YORADIO_ESP8266_SPI_PDM
#include "driver/gpio.h"
#include "driver/spi.h"
#include "esp_attr.h"
#include "esp8266/spi_struct.h"
#else
#include "driver/i2s.h"
#endif
#include "esp_log.h"
#include "native_audio_normalizer.h"
#include "persistent_settings.h"

static const char *TAG = "audio_output";
#if YORADIO_ESP8266_SPI_PDM
static uint32_t s_input_sample_rate;
static uint32_t s_resample_phase;
static uint32_t s_pdm_integrator;
static bool s_spi_initialized;
static bool s_spi_pin_selected;
#else
static uint32_t s_sample_rate;
static bool s_i2s_started;
static bool s_clock_primed;
#endif
static uint8_t s_volume = 160;
static int8_t s_balance;
static bool s_normalization_enabled;
static uint8_t s_normalization_max_gain_db;
static int8_t s_normalization_target_db;
static uint16_t s_normalization_time_ms;

#define VOLUME_DENOMINATOR 254U
#define BALANCE_DENOMINATOR 16U
#define GAIN_Q15_ONE 32768U

static uint32_t channel_gain_q15(uint8_t volume, uint8_t balance_gain) {
    uint32_t denominator = VOLUME_DENOMINATOR * BALANCE_DENOMINATOR;
    uint32_t numerator = (uint32_t)volume * balance_gain;
    return (numerator * GAIN_Q15_ONE + denominator / 2U) / denominator;
}

static int16_t scale_sample(int16_t sample, uint32_t gain_q15) {
    int32_t value = (int32_t)sample * (int32_t)gain_q15;
    if (value >= 0) {
        value = (value + (int32_t)(GAIN_Q15_ONE / 2U)) >> 15;
    } else {
        value = -((-value + (int32_t)(GAIN_Q15_ONE / 2U)) >> 15);
    }
    if (value > INT16_MAX) value = INT16_MAX;
    if (value < INT16_MIN) value = INT16_MIN;
    return (int16_t)value;
}

#if YORADIO_ESP8266_SPI_PDM

#define SPI_PDM_CHUNK_BITS 512U
#define SPI_PDM_CHUNK_WORDS (SPI_PDM_CHUNK_BITS / 32U)
#define SPI_PDM_QUEUE_CHUNKS 12U
#define SPI_PDM_WAIT_MS 100U

typedef struct {
    uint32_t words[SPI_PDM_CHUNK_WORDS];
    uint16_t bit_count;
} spi_pdm_chunk_t;

static spi_pdm_chunk_t s_spi_queue[SPI_PDM_QUEUE_CHUNKS];
static volatile uint8_t s_spi_queue_head;
static volatile uint8_t s_spi_queue_tail;
static volatile uint8_t s_spi_queue_count;
static volatile bool s_spi_active;
static volatile TaskHandle_t s_spi_waiter;

#if YORADIO_ESP8266_AUDIO_PROFILE
extern void audio_profile_spi_wait_begin(void);
extern void audio_profile_spi_wait_end(void);
#elif YORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK
extern void audio_output_benchmark_spi_wait_begin(void);
extern void audio_output_benchmark_spi_wait_end(void);
#endif

static const spi_interface_t s_spi_interface = {
    .cpol = 0,
    .cpha = 0,
    .bit_tx_order = 0,
    .bit_rx_order = 0,
    .byte_tx_order = 0,
    .byte_rx_order = 0,
    .mosi_en = 1,
    .miso_en = 0,
    .cs_en = 0,
};

static void IRAM_ATTR spi_pdm_start_next_locked(void) {
    if (!s_spi_queue_count) {
        s_spi_active = false;
        return;
    }
    const spi_pdm_chunk_t *chunk = &s_spi_queue[s_spi_queue_head];
    SPI1.user.usr_mosi = 1;
    SPI1.user1.usr_mosi_bitlen = chunk->bit_count - 1U;
    for (size_t index = 0; index * 32U < chunk->bit_count; ++index)
        SPI1.data_buf[index] = chunk->words[index];
    ++s_spi_queue_head;
    if (s_spi_queue_head == SPI_PDM_QUEUE_CHUNKS) s_spi_queue_head = 0;
    --s_spi_queue_count;
    s_spi_active = true;
    SPI1.cmd.usr = 1;
}

static void IRAM_ATTR spi_pdm_event(int event, void *arg) {
    (void)arg;
    if (event != SPI_TRANS_DONE_EVENT) return;
    BaseType_t higher_task_woken = pdFALSE;
    spi_pdm_start_next_locked();
    TaskHandle_t waiter = s_spi_waiter;
    if (waiter) vTaskNotifyGiveFromISR(waiter, &higher_task_woken);
    if (higher_task_woken) portYIELD_FROM_ISR();
}

static uint32_t spi_pdm_wait_notification(void) {
#if YORADIO_ESP8266_AUDIO_PROFILE
    audio_profile_spi_wait_begin();
#elif YORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK
    audio_output_benchmark_spi_wait_begin();
#endif
    uint32_t notified = ulTaskNotifyTake(pdTRUE,
                                         pdMS_TO_TICKS(SPI_PDM_WAIT_MS));
#if YORADIO_ESP8266_AUDIO_PROFILE
    audio_profile_spi_wait_end();
#elif YORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK
    audio_output_benchmark_spi_wait_end();
#endif
    return notified;
}

static esp_err_t spi_pdm_select_pin(void) {
    if (s_spi_pin_selected) return ESP_OK;
    spi_interface_t interface = s_spi_interface;
    esp_err_t result = spi_set_interface(HSPI_HOST, &interface);
    if (result == ESP_OK) s_spi_pin_selected = true;
    return result;
}

static esp_err_t spi_pdm_acquire(spi_pdm_chunk_t **out) {
    if (!out) return ESP_ERR_INVALID_ARG;
    esp_err_t result = spi_pdm_select_pin();
    if (result != ESP_OK) return result;
    s_spi_waiter = xTaskGetCurrentTaskHandle();
    for (;;) {
        taskENTER_CRITICAL();
        if (s_spi_queue_count < SPI_PDM_QUEUE_CHUNKS) {
            spi_pdm_chunk_t *chunk = &s_spi_queue[s_spi_queue_tail];
            taskEXIT_CRITICAL();
            memset(chunk->words, 0, sizeof(chunk->words));
            chunk->bit_count = 0;
            *out = chunk;
            return ESP_OK;
        }
        taskEXIT_CRITICAL();
        if (!spi_pdm_wait_notification()) return ESP_ERR_TIMEOUT;
    }
}

static esp_err_t spi_pdm_commit(spi_pdm_chunk_t *chunk, size_t bit_count) {
    if (!chunk || !bit_count || bit_count > SPI_PDM_CHUNK_BITS)
        return ESP_ERR_INVALID_ARG;
    taskENTER_CRITICAL();
    if (chunk != &s_spi_queue[s_spi_queue_tail] ||
        s_spi_queue_count >= SPI_PDM_QUEUE_CHUNKS) {
        taskEXIT_CRITICAL();
        return ESP_ERR_INVALID_STATE;
    }
    chunk->bit_count = (uint16_t)bit_count;
    ++s_spi_queue_tail;
    if (s_spi_queue_tail == SPI_PDM_QUEUE_CHUNKS) s_spi_queue_tail = 0;
    ++s_spi_queue_count;
    if (!s_spi_active) spi_pdm_start_next_locked();
    taskEXIT_CRITICAL();
    return ESP_OK;
}

static esp_err_t spi_pdm_wait_idle(void) {
    s_spi_waiter = xTaskGetCurrentTaskHandle();
    for (;;) {
        taskENTER_CRITICAL();
        bool idle = !s_spi_active && !s_spi_queue_count;
        taskEXIT_CRITICAL();
        if (idle) return ESP_OK;
        if (!spi_pdm_wait_notification()) return ESP_ERR_TIMEOUT;
    }
}

static esp_err_t spi_pdm_emit_sample(int16_t sample, spi_pdm_chunk_t **chunk,
                                     size_t *bit_count) {
    if (!*chunk) {
        esp_err_t result = spi_pdm_acquire(chunk);
        if (result != ESP_OK) return result;
    }
    const uint32_t target = (uint32_t)((int32_t)sample - INT16_MIN);
    for (unsigned bit = 0; bit < BOARD_SPI_PDM_OVERSAMPLE; ++bit) {
        s_pdm_integrator += target;
        bool high = s_pdm_integrator >= 65536U;
        if (high) s_pdm_integrator -= 65536U;
        if (high) {
            size_t word = *bit_count / 32U;
            unsigned shift = 31U - (unsigned)(*bit_count % 32U);
            (*chunk)->words[word] |= 1UL << shift;
        }
        ++*bit_count;
        if (*bit_count == SPI_PDM_CHUNK_BITS) {
            esp_err_t result = spi_pdm_commit(*chunk, *bit_count);
            if (result != ESP_OK) return result;
            *chunk = NULL;
            *bit_count = 0;
        }
    }
    return ESP_OK;
}

esp_err_t native_audio_output_init(void) {
    spi_config_t config = {
        .interface = s_spi_interface,
        .intr_enable = {.trans_done = 1},
        .event_cb = spi_pdm_event,
        .mode = SPI_MASTER_MODE,
        /* Initialize through the public API, then use the full hardware
         * pre-divider because the public enum stops at 2 MHz. */
        .clk_div = SPI_2MHz_DIV,
    };
    esp_err_t result = spi_init(HSPI_HOST, &config);
    if (result == ESP_OK) {
        /* APB is fixed at 80 MHz. The selected integral divider produces
         * 48.077 kHz times either 8 or 16 PDM bits/sample (+0.16%). */
        SPI1.clock.clk_equ_sysclk = false;
        SPI1.clock.clkdiv_pre = BOARD_SPI_PDM_CLOCK_PREDIV;
        SPI1.clock.clkcnt_n = 7;
        SPI1.clock.clkcnt_h = 3;
        SPI1.clock.clkcnt_l = 7;
        s_spi_queue_head = 0;
        s_spi_queue_tail = 0;
        s_spi_queue_count = 0;
        s_spi_active = false;
        s_spi_waiter = NULL;
        s_spi_initialized = true;
        s_spi_pin_selected = true;
    }
    native_audio_output_reload_settings();
    if (result == ESP_OK) {
        ESP_LOGI(TAG,
                 "SPI-PDM: mono GPIO%d/D7, %u Hz, %u bits/sample; "
                 "GPIO%d/D5 clock unused",
                 BOARD_SPI_PDM_DATA_GPIO, BOARD_SPI_PDM_BIT_RATE_HZ,
                 BOARD_SPI_PDM_OVERSAMPLE,
                 BOARD_SPI_PDM_CLOCK_GPIO);
    }
    return result;
}

esp_err_t native_audio_output_write(int16_t *samples, size_t sample_count,
                                    uint32_t sample_rate, uint8_t channels) {
    if (!samples || !sample_count || !sample_rate ||
        (channels != 1 && channels != 2) || sample_count % channels)
        return ESP_ERR_INVALID_ARG;
    if (!s_spi_initialized) return ESP_ERR_INVALID_STATE;
    size_t frames = sample_count / channels;
    native_audio_normalizer_configure(
        s_normalization_enabled, s_normalization_max_gain_db,
        s_normalization_target_db, s_normalization_time_ms, sample_rate);
    native_audio_normalizer_process(samples, frames, channels);
    uint8_t left_balance = s_balance < 0
        ? (uint8_t)(BALANCE_DENOMINATOR + s_balance) : BALANCE_DENOMINATOR;
    uint8_t right_balance = s_balance > 0
        ? (uint8_t)(BALANCE_DENOMINATOR - s_balance) : BALANCE_DENOMINATOR;
    uint32_t left_gain = channel_gain_q15(s_volume, left_balance);
    uint32_t right_gain = channel_gain_q15(s_volume, right_balance);
    for (size_t frame = 0; frame < frames; ++frame) {
        samples[frame * channels] =
            scale_sample(samples[frame * channels], left_gain);
        if (channels == 2) {
            samples[frame * 2U + 1U] =
                scale_sample(samples[frame * 2U + 1U], right_gain);
        }
    }

    if (sample_rate != s_input_sample_rate) {
        s_input_sample_rate = sample_rate;
        s_resample_phase = 0;
    }
    spi_pdm_chunk_t *chunk = NULL;
    size_t bit_count = 0;
    for (size_t frame = 0; frame < frames; ++frame) {
        int32_t mono = samples[frame * channels];
        if (channels == 2)
            mono = (mono + samples[frame * 2U + 1U]) / 2;
        s_resample_phase += BOARD_SPI_PDM_SAMPLE_RATE;
        while (s_resample_phase >= sample_rate) {
            esp_err_t result = spi_pdm_emit_sample(
                (int16_t)mono, &chunk, &bit_count);
            if (result != ESP_OK) return result;
            s_resample_phase -= sample_rate;
        }
    }
    return bit_count ? spi_pdm_commit(chunk, bit_count) : ESP_OK;
}

void native_audio_output_silence(void) {
    if (!s_spi_initialized) return;
    esp_err_t result = spi_pdm_wait_idle();
    spi_pdm_chunk_t *silence = NULL;
    if (result == ESP_OK) result = spi_pdm_acquire(&silence);
    if (result == ESP_OK) {
        for (size_t index = 0; index < SPI_PDM_CHUNK_WORDS; ++index)
            silence->words[index] = 0xaaaaaaaaU;
        result = spi_pdm_commit(silence, SPI_PDM_CHUNK_BITS);
    }
    if (result == ESP_OK) result = spi_pdm_wait_idle();
    if (result != ESP_OK)
        ESP_LOGE(TAG, "SPI-PDM drain failed: %s", esp_err_to_name(result));
    taskENTER_CRITICAL();
    s_spi_queue_head = 0;
    s_spi_queue_tail = 0;
    s_spi_queue_count = 0;
    s_spi_active = false;
    taskEXIT_CRITICAL();
    gpio_set_direction(BOARD_SPI_PDM_DATA_GPIO, GPIO_MODE_OUTPUT);
    gpio_set_level(BOARD_SPI_PDM_DATA_GPIO, 0);
    s_spi_pin_selected = false;
    s_input_sample_rate = 0;
    s_resample_phase = 0;
    s_pdm_integrator = 0;
}
#else

esp_err_t native_audio_output_init(void) {
    const i2s_config_t config = {
        .mode = I2S_MODE_MASTER | I2S_MODE_TX,
        .sample_rate = 44100,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT,
        .communication_format = I2S_COMM_FORMAT_I2S | I2S_COMM_FORMAT_I2S_MSB,
        .dma_buf_count = 4,
        .dma_buf_len = 128,
        .tx_desc_auto_clear = true,
    };
    const i2s_pin_config_t pins = {
        .bck_o_en = 1,
        .ws_o_en = 1,
        .data_out_en = 1,
        .data_in_en = 0,
    };
    esp_err_t result = i2s_driver_install(I2S_NUM_0, &config, 0, NULL);
    if (result == ESP_OK) result = i2s_set_pin(I2S_NUM_0, &pins);
    if (result == ESP_OK)
        result = i2s_set_clk(I2S_NUM_0, 44100,
                             I2S_BITS_PER_SAMPLE_16BIT,
                             I2S_CHANNEL_STEREO);
    if (result == ESP_OK) {
        /* Keep SLC DMA active between streams. The legacy ESP8266 driver
         * reports a stopped-DMA write timeout as ESP_OK with zero bytes, so
         * silence is written into the existing descriptors instead. */
        s_sample_rate = 44100;
        s_i2s_started = true;
        s_clock_primed = false;
        result = i2s_zero_dma_buffer(I2S_NUM_0);
    }
    native_audio_output_reload_settings();
    ESP_LOGI(TAG, "I2S DMA: 4 x 128 stereo frames");
    return result;
}

esp_err_t native_audio_output_write(int16_t *samples, size_t sample_count,
                                    uint32_t sample_rate, uint8_t channels) {
    if (!samples || !sample_count || !sample_rate ||
        (channels != 1 && channels != 2)) return ESP_ERR_INVALID_ARG;
    size_t frames = sample_count / channels;
    native_audio_normalizer_configure(
        s_normalization_enabled, s_normalization_max_gain_db,
        s_normalization_target_db, s_normalization_time_ms, sample_rate);
    native_audio_normalizer_process(samples, frames, channels);
    uint8_t left_balance = s_balance < 0
        ? (uint8_t)(BALANCE_DENOMINATOR + s_balance) : BALANCE_DENOMINATOR;
    uint8_t right_balance = s_balance > 0
        ? (uint8_t)(BALANCE_DENOMINATOR - s_balance) : BALANCE_DENOMINATOR;
    uint32_t left_gain = channel_gain_q15(s_volume, left_balance);
    uint32_t right_gain = channel_gain_q15(s_volume, right_balance);
    for (size_t frame = 0; frame < frames; ++frame) {
        samples[frame * channels] =
            scale_sample(samples[frame * channels], left_gain);
        if (channels == 2) {
            samples[frame * 2U + 1U] =
                scale_sample(samples[frame * 2U + 1U], right_gain);
        }
    }
    if (channels == 1) {
        if (sample_count > 1152) return ESP_ERR_INVALID_SIZE;
        for (size_t index = sample_count; index-- > 0;) {
            int16_t value = samples[index];
            samples[index * 2] = value;
            samples[index * 2 + 1] = value;
        }
        sample_count *= 2;
    }
    if (!s_clock_primed || sample_rate != s_sample_rate) {
        esp_err_t result = i2s_set_clk(I2S_NUM_0, sample_rate,
                                       I2S_BITS_PER_SAMPLE_16BIT,
                                       I2S_CHANNEL_STEREO);
        if (result != ESP_OK) return result;
        s_sample_rate = sample_rate;
        s_clock_primed = true;
    }
    size_t bytes = sample_count * sizeof(*samples);
    if (!s_i2s_started) {
        esp_err_t result = i2s_start(I2S_NUM_0);
        if (result != ESP_OK) return result;
        s_i2s_started = true;
    }

    size_t offset = 0;
    while (offset < bytes) {
        size_t bytes_written = 0;
        esp_err_t result = i2s_write(
            I2S_NUM_0, (uint8_t *)samples + offset, bytes - offset,
            &bytes_written, pdMS_TO_TICKS(1000));
        if (result != ESP_OK || !bytes_written) {
            ESP_LOGE(TAG, "I2S write failed: %s, %u/%u bytes",
                     esp_err_to_name(result), (unsigned)offset,
                     (unsigned)bytes);
            return result == ESP_OK ? ESP_FAIL : result;
        }
        offset += bytes_written;
    }
    return ESP_OK;
}

void native_audio_output_silence(void) {
    if (!s_i2s_started) return;
    esp_err_t result = i2s_zero_dma_buffer(I2S_NUM_0);
    if (result != ESP_OK)
        ESP_LOGE(TAG, "I2S silence failed: %s", esp_err_to_name(result));
    s_clock_primed = false;
}

#endif

void native_audio_output_reload_settings(void) {
    persistent_settings_t settings;
    persistent_settings_get(&settings);
    s_volume = settings.volume > VOLUME_DENOMINATOR
                   ? VOLUME_DENOMINATOR : settings.volume;
    s_balance = settings.balance < -BALANCE_DENOMINATOR
                    ? -BALANCE_DENOMINATOR
                    : (settings.balance > BALANCE_DENOMINATOR
                           ? BALANCE_DENOMINATOR : settings.balance);
    s_normalization_enabled = settings.normalization_enabled;
    s_normalization_max_gain_db = settings.normalization_max_gain_db;
    s_normalization_target_db = settings.normalization_target_db;
    s_normalization_time_ms = settings.normalization_time_ms;
}

void native_audio_output_reset_normalizer(void) {
    native_audio_normalizer_reset();
}

uint8_t native_audio_output_volume(void) { return s_volume; }

void native_audio_output_set_volume_runtime(uint8_t volume) {
    s_volume = volume > VOLUME_DENOMINATOR ? VOLUME_DENOMINATOR : volume;
}

void native_audio_output_set_balance_runtime(int8_t balance) {
    s_balance = balance < -BALANCE_DENOMINATOR
                    ? -BALANCE_DENOMINATOR
                    : (balance > BALANCE_DENOMINATOR
                           ? BALANCE_DENOMINATOR : balance);
}
