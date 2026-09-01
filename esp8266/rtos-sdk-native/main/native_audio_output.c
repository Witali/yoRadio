#include "native_audio_output.h"

#include <stdbool.h>
#include <limits.h>
#include <stdlib.h>
#include <string.h>

#include "board_config.h"
#include "esp8266_nodac_i2s.h"
#include "spi_pdm_config.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "sdkconfig.h"
#if YORADIO_ESP8266_SPI_PDM
#include "driver/gpio.h"
#include "driver/spi.h"
#include "esp_attr.h"
#include "esp8266/eagle_soc.h"
#include "esp8266/spi_struct.h"
#include "rom/ets_sys.h"
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
#elif YORADIO_ESP8266_I2S_PDM
static uint32_t s_input_sample_rate;
static uint32_t s_resample_phase;
static uint32_t s_pdm_integrator;
static uint32_t s_i2s_pdm_partial_word;
static uint8_t s_i2s_pdm_partial_bits;
static bool s_i2s_started;
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

#if !YORADIO_ESP8266_SPI_PDM && !YORADIO_ESP8266_I2S_PDM
/* The release/v3.4 RTOS I2S driver configures I2S and SLC but omits the
 * BBPLL audio-clock gate. ESP8266Audio enables this gate before touching the
 * peripheral; without it no DMA descriptor can ever complete. */
extern void rom_i2c_writeReg_Mask(int block, int host_id, int reg_add,
                                  int msb, int lsb, int value);

static void i2s_enable_bbpll_audio_clock(void) {
    rom_i2c_writeReg_Mask(0x67, 4, 4, 7, 7, 1);
}
#endif

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
#define SPI_PDM_GAP_STATS \
    (YORADIO_ESP8266_AUDIO_PROFILE || \
     YORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK)

typedef struct {
    uint32_t words[SPI_PDM_CHUNK_WORDS];
#if SPI_PDM_GAP_STATS
    uint32_t wire_cycles;
#endif
    uint16_t bit_count;
} spi_pdm_chunk_t;

static spi_pdm_chunk_t s_spi_queue[SPI_PDM_QUEUE_CHUNKS];
static volatile uint8_t s_spi_queue_head;
static volatile uint8_t s_spi_queue_tail;
static volatile uint8_t s_spi_queue_count;
static volatile bool s_spi_active;
static volatile TaskHandle_t s_spi_waiter;
static volatile bool s_spi_waiting;
#if SPI_PDM_GAP_STATS
static volatile uint32_t s_spi_last_start_cycle;
static volatile uint32_t s_spi_last_wire_cycles;
static volatile uint32_t s_spi_gap_cycles_total;
static volatile uint32_t s_spi_gap_cycles_max;
static volatile uint32_t s_spi_chained_transfers;
static volatile uint32_t s_spi_queue_empty_events;
#endif

#define DPORT_SPI_INT_STATUS_REG 0x3ff00020U
#define DPORT_SPI_INT_STATUS_SPI0 BIT4
#define DPORT_SPI_INT_STATUS_SPI1 BIT7

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

#if SPI_PDM_GAP_STATS
extern uint64_t g_esp_os_cpu_clk;

static inline uint32_t IRAM_ATTR spi_pdm_cycle_clock(void) {
    uint32_t cycles;
    __asm__ __volatile__("rsr %0, ccount" : "=a"(cycles));
    /* ESP8266 RTOS SDK resets CCOUNT on every system tick. The accumulated
     * low word plus the live counter remains monotonic while this level-1 ISR
     * runs (and while the task-side caller holds its critical section). */
    return (uint32_t)g_esp_os_cpu_clk + cycles;
}
#endif

static inline void IRAM_ATTR spi_pdm_load_fifo(
    const spi_pdm_chunk_t *chunk) {
    if (chunk->bit_count == SPI_PDM_CHUNK_BITS) {
        for (unsigned index = 0; index < SPI_PDM_CHUNK_WORDS; ++index)
            SPI1.data_buf[index] = chunk->words[index];
        return;
    }
    unsigned words = (chunk->bit_count + 31U) / 32U;
    for (unsigned index = 0; index < words; ++index)
        SPI1.data_buf[index] = chunk->words[index];
}

static void IRAM_ATTR __attribute__((noinline)) spi_pdm_start_next_locked(void) {
    if (!s_spi_queue_count) {
#if SPI_PDM_GAP_STATS
        if (s_spi_active) ++s_spi_queue_empty_events;
#endif
        s_spi_active = false;
#if SPI_PDM_GAP_STATS
        s_spi_last_start_cycle = 0;
#endif
        return;
    }
#if SPI_PDM_GAP_STATS
    bool chained = s_spi_active && s_spi_last_start_cycle;
#endif
    const spi_pdm_chunk_t *chunk = &s_spi_queue[s_spi_queue_head];
    SPI1.user.usr_mosi = 1;
    SPI1.user.usr_mosi_highpart = 0;
    SPI1.user1.usr_mosi_bitlen = chunk->bit_count - 1U;
    spi_pdm_load_fifo(chunk);
    ++s_spi_queue_head;
    if (s_spi_queue_head == SPI_PDM_QUEUE_CHUNKS) s_spi_queue_head = 0;
    --s_spi_queue_count;
    s_spi_active = true;
#if SPI_PDM_GAP_STATS
    uint32_t now = spi_pdm_cycle_clock();
    if (chained) {
        uint32_t elapsed = now - s_spi_last_start_cycle;
        uint32_t gap = elapsed > s_spi_last_wire_cycles
            ? elapsed - s_spi_last_wire_cycles : 0;
        s_spi_gap_cycles_total += gap;
        if (gap > s_spi_gap_cycles_max) s_spi_gap_cycles_max = gap;
        ++s_spi_chained_transfers;
    }
    s_spi_last_start_cycle = now;
    s_spi_last_wire_cycles = chunk->wire_cycles;
#endif
    SPI1.cmd.usr = 1;
}

static void IRAM_ATTR __attribute__((noinline)) spi_pdm_wake_waiter(void) {
    BaseType_t higher_task_woken = pdFALSE;
    s_spi_waiting = false;
    TaskHandle_t waiter = s_spi_waiter;
    if (waiter) vTaskNotifyGiveFromISR(waiter, &higher_task_woken);
    if (higher_task_woken) portYIELD_FROM_ISR();
}

static void IRAM_ATTR spi_pdm_complete(void) {
    spi_pdm_start_next_locked();
    if (s_spi_waiting) spi_pdm_wake_waiter();
}

#if YORADIO_ESP8266_SPI_PDM_FAST_ISR
static void IRAM_ATTR spi_pdm_isr(void *arg) {
    (void)arg;
    uint32_t status = READ_PERI_REG(DPORT_SPI_INT_STATUS_REG);
    if (!(status & DPORT_SPI_INT_STATUS_SPI1)) {
        /* The vector is shared. Preserve the SDK driver's SPI0 acknowledgement
         * in the exceptional case that its transfer-done interrupt is enabled. */
        if (status & DPORT_SPI_INT_STATUS_SPI0) SPI0.slave.val &= ~0x1fU;
        return;
    }
    /* The SDK repeats this write because early silicon can leave a transfer
     * flag asserted for one APB cycle. This loop normally runs once. */
    do {
        SPI1.slave.val &= ~0x1fU;
    } while (SPI1.slave.val & 0x1fU);
    spi_pdm_complete();
}
#else
static void IRAM_ATTR spi_pdm_event(int event, void *arg) {
    (void)arg;
    if (event == SPI_TRANS_DONE_EVENT) spi_pdm_complete();
}
#endif

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
    for (;;) {
        taskENTER_CRITICAL();
        if (s_spi_queue_count < SPI_PDM_QUEUE_CHUNKS) {
            s_spi_waiting = false;
            spi_pdm_chunk_t *chunk = &s_spi_queue[s_spi_queue_tail];
            taskEXIT_CRITICAL();
            memset(chunk->words, 0, sizeof(chunk->words));
            chunk->bit_count = 0;
            *out = chunk;
            return ESP_OK;
        }
        s_spi_waiter = xTaskGetCurrentTaskHandle();
        s_spi_waiting = true;
        taskEXIT_CRITICAL();
        if (!spi_pdm_wait_notification()) {
            taskENTER_CRITICAL();
            s_spi_waiting = false;
            taskEXIT_CRITICAL();
            return ESP_ERR_TIMEOUT;
        }
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
#if SPI_PDM_GAP_STATS
    chunk->wire_cycles = (uint32_t)(
        ((uint64_t)CONFIG_ESP8266_DEFAULT_CPU_FREQ_MHZ * 1000000ULL *
         bit_count + BOARD_SPI_PDM_BIT_RATE_HZ / 2U) /
        BOARD_SPI_PDM_BIT_RATE_HZ);
#endif
    ++s_spi_queue_tail;
    if (s_spi_queue_tail == SPI_PDM_QUEUE_CHUNKS) s_spi_queue_tail = 0;
    ++s_spi_queue_count;
    if (!s_spi_active) spi_pdm_start_next_locked();
    taskEXIT_CRITICAL();
    return ESP_OK;
}

static esp_err_t spi_pdm_wait_idle(void) {
    for (;;) {
        taskENTER_CRITICAL();
        bool idle = !s_spi_active && !s_spi_queue_count;
        if (idle) {
            s_spi_waiting = false;
        } else {
            s_spi_waiter = xTaskGetCurrentTaskHandle();
            s_spi_waiting = true;
        }
        taskEXIT_CRITICAL();
        if (idle) return ESP_OK;
        if (!spi_pdm_wait_notification()) {
            taskENTER_CRITICAL();
            s_spi_waiting = false;
            taskEXIT_CRITICAL();
            return ESP_ERR_TIMEOUT;
        }
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
#if YORADIO_ESP8266_SPI_PDM_FAST_ISR
        .event_cb = NULL,
#else
        .event_cb = spi_pdm_event,
#endif
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
        s_spi_waiting = false;
#if SPI_PDM_GAP_STATS
        s_spi_last_start_cycle = 0;
#endif
        native_audio_output_reset_spi_stats();
#if YORADIO_ESP8266_SPI_PDM_FAST_ISR
        _xt_isr_mask(1U << ETS_SPI_INUM);
        _xt_isr_attach(ETS_SPI_INUM, spi_pdm_isr, NULL);
        _xt_isr_unmask(1U << ETS_SPI_INUM);
#endif
        s_spi_initialized = true;
        s_spi_pin_selected = true;
    }
    native_audio_output_reload_settings();
    if (result == ESP_OK) {
        ESP_LOGI(TAG,
                 "SPI-PDM: mono GPIO%d/D7, %u Hz, %u bits/sample; "
                 "GPIO%d/D5 clock unused; fast_isr=%u",
                 BOARD_SPI_PDM_DATA_GPIO, BOARD_SPI_PDM_BIT_RATE_HZ,
                 BOARD_SPI_PDM_OVERSAMPLE,
                 BOARD_SPI_PDM_CLOCK_GPIO,
                 (unsigned)YORADIO_ESP8266_SPI_PDM_FAST_ISR);
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
    s_spi_waiting = false;
    taskEXIT_CRITICAL();
    gpio_set_direction(BOARD_SPI_PDM_DATA_GPIO, GPIO_MODE_OUTPUT);
    gpio_set_level(BOARD_SPI_PDM_DATA_GPIO, 0);
    s_spi_pin_selected = false;
    s_input_sample_rate = 0;
    s_resample_phase = 0;
    s_pdm_integrator = 0;
}
#elif YORADIO_ESP8266_I2S_PDM

#define I2S_PDM_BATCH_WORDS 64U
#define I2S_PDM_WRITE_TIMEOUT_MS 1000U
#define I2S_PDM_SILENCE_WORD 0xaaaaaaaaU

typedef struct {
    uint32_t words[I2S_PDM_BATCH_WORDS];
    size_t word_count;
} i2s_pdm_writer_t;

static esp_err_t i2s_pdm_write_words(const uint32_t *words,
                                     size_t word_count) {
    esp_err_t result = esp8266_nodac_i2s_write(
        words, word_count, pdMS_TO_TICKS(I2S_PDM_WRITE_TIMEOUT_MS));
    if (result != ESP_OK)
        ESP_LOGE(TAG, "I2S-PDM DMA write failed: %s",
                 esp_err_to_name(result));
    return result;
}

static esp_err_t i2s_pdm_flush(i2s_pdm_writer_t *writer) {
    if (!writer->word_count) return ESP_OK;
    esp_err_t result =
        i2s_pdm_write_words(writer->words, writer->word_count);
    if (result == ESP_OK) writer->word_count = 0;
    return result;
}

static esp_err_t i2s_pdm_push_bit(i2s_pdm_writer_t *writer, bool high) {
    s_i2s_pdm_partial_word =
        (s_i2s_pdm_partial_word << 1) | (high ? 1U : 0U);
    ++s_i2s_pdm_partial_bits;
    if (s_i2s_pdm_partial_bits != 32U) return ESP_OK;

    writer->words[writer->word_count++] = s_i2s_pdm_partial_word;
    s_i2s_pdm_partial_word = 0;
    s_i2s_pdm_partial_bits = 0;
    return writer->word_count == I2S_PDM_BATCH_WORDS
        ? i2s_pdm_flush(writer) : ESP_OK;
}

static esp_err_t i2s_pdm_emit_sample(int16_t sample,
                                     i2s_pdm_writer_t *writer) {
    const uint32_t target = (uint32_t)((int32_t)sample - INT16_MIN);
    for (unsigned bit = 0; bit < BOARD_I2S_PDM_OVERSAMPLE; ++bit) {
        s_pdm_integrator += target;
        bool high = s_pdm_integrator >= 65536U;
        if (high) s_pdm_integrator -= 65536U;
        for (unsigned repeat = 0; repeat < BOARD_I2S_PDM_REPEAT; ++repeat) {
            esp_err_t result = i2s_pdm_push_bit(writer, high);
            if (result != ESP_OK) return result;
        }
    }
    return ESP_OK;
}

static esp_err_t i2s_pdm_finish_partial_word(i2s_pdm_writer_t *writer) {
    while (s_i2s_pdm_partial_bits) {
        esp_err_t result = i2s_pdm_emit_sample(0, writer);
        if (result != ESP_OK) return result;
    }
    return i2s_pdm_flush(writer);
}

static esp_err_t i2s_pdm_fill_dma_silence(void) {
    esp8266_nodac_i2s_silence(I2S_PDM_SILENCE_WORD);
    return ESP_OK;
}

esp_err_t native_audio_output_init(void) {
    esp_err_t result = esp8266_nodac_i2s_init(
        I2S_PDM_SILENCE_WORD, BOARD_I2S_PDM_BCK_DIV,
        BOARD_I2S_PDM_CLKM_DIV);
    if (result == ESP_OK) {
        s_i2s_started = true;
        s_input_sample_rate = 0;
        s_resample_phase = 0;
        s_pdm_integrator = 0;
        s_i2s_pdm_partial_word = 0;
        s_i2s_pdm_partial_bits = 0;
    }
    native_audio_output_reload_settings();
    if (result == ESP_OK) {
        ESP_LOGI(TAG,
                 "I2S-PDM DMA: mono GPIO%d/RX, carrier %u Hz, "
                 "PDM%u x%u effective %u Hz, nominal carrier %u Hz, "
                 "%u x %u words; UART RX ignored",
                 BOARD_I2S_DATA_GPIO, BOARD_I2S_PDM_CARRIER_HZ,
                 BOARD_I2S_PDM_OVERSAMPLE, BOARD_I2S_PDM_REPEAT,
                 BOARD_I2S_PDM_EFFECTIVE_HZ, BOARD_I2S_PDM_NOMINAL_HZ,
                 ESP8266_NODAC_DMA_BUFFER_COUNT,
                 ESP8266_NODAC_DMA_BUFFER_WORDS);
    }
    return result;
}

esp_err_t native_audio_output_write(int16_t *samples, size_t sample_count,
                                    uint32_t sample_rate, uint8_t channels) {
    if (!samples || !sample_count || !sample_rate ||
        (channels != 1 && channels != 2) || sample_count % channels)
        return ESP_ERR_INVALID_ARG;
    if (!s_i2s_started) return ESP_ERR_INVALID_STATE;

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
    i2s_pdm_writer_t writer = {0};
    for (size_t frame = 0; frame < frames; ++frame) {
        int32_t mono = samples[frame * channels];
        if (channels == 2)
            mono = (mono + samples[frame * 2U + 1U]) / 2;
        s_resample_phase += BOARD_I2S_PDM_SAMPLE_RATE;
        while (s_resample_phase >= sample_rate) {
            esp_err_t result =
                i2s_pdm_emit_sample((int16_t)mono, &writer);
            if (result != ESP_OK) return result;
            s_resample_phase -= sample_rate;
        }
    }
    return i2s_pdm_flush(&writer);
}

void native_audio_output_silence(void) {
    if (!s_i2s_started) return;
    i2s_pdm_writer_t writer = {0};
    esp_err_t result = i2s_pdm_finish_partial_word(&writer);
    if (result == ESP_OK) result = i2s_pdm_fill_dma_silence();
    if (result != ESP_OK)
        ESP_LOGE(TAG, "I2S-PDM silence failed: %s", esp_err_to_name(result));
    s_input_sample_rate = 0;
    s_resample_phase = 0;
    s_pdm_integrator = 0;
    s_i2s_pdm_partial_word = 0;
    s_i2s_pdm_partial_bits = 0;
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
    i2s_enable_bbpll_audio_clock();
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

void native_audio_output_reset_spi_stats(void) {
#if YORADIO_ESP8266_SPI_PDM && SPI_PDM_GAP_STATS
    taskENTER_CRITICAL();
    s_spi_gap_cycles_total = 0;
    s_spi_gap_cycles_max = 0;
    s_spi_chained_transfers = 0;
    s_spi_queue_empty_events = 0;
    taskEXIT_CRITICAL();
#elif YORADIO_ESP8266_I2S_PDM
    esp8266_nodac_i2s_reset_underruns();
#endif
}

void native_audio_output_get_spi_stats(native_audio_output_spi_stats_t *stats) {
    if (!stats) return;
    memset(stats, 0, sizeof(*stats));
#if YORADIO_ESP8266_SPI_PDM && SPI_PDM_GAP_STATS
    taskENTER_CRITICAL();
    stats->chained_transfers = s_spi_chained_transfers;
    stats->gap_cycles_total = s_spi_gap_cycles_total;
    stats->gap_cycles_max = s_spi_gap_cycles_max;
    stats->queue_empty_events = s_spi_queue_empty_events;
    taskEXIT_CRITICAL();
#elif YORADIO_ESP8266_I2S_PDM
    stats->queue_empty_events = esp8266_nodac_i2s_underruns();
#endif
}

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
