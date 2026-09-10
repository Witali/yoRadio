#include "native_audio_output.h"

#include <stdbool.h>
#include <limits.h>
#include <stdlib.h>
#include <string.h>

#include "board_config.h"
#include "esp_attr.h"
#include "esp8266_nodac_i2s.h"
#include "spi_pdm_config.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "sdkconfig.h"
#if CONFIG_YORADIO_STATUS_LED
#include "status_led.h"
#endif
#if YORADIO_ESP8266_SPI_PDM
#include "driver/gpio.h"
#include "driver/spi.h"
#include "esp8266/eagle_soc.h"
#include "esp8266/spi_struct.h"
#include "rom/ets_sys.h"
#else
#include "driver/i2s.h"
#endif
#include "esp_log.h"
#include "native_audio_normalizer.h"
#include "persistent_settings.h"
#if CONFIG_YORADIO_AUDIO_OUTPUT_I2S_RCPDM
#include "rc_pdm.h"
#if CONFIG_YORADIO_RCPDM_FEEDBACK
#include "rc_pdm_feedback.h"
#endif
#if YORADIO_ESP8266_OUTPUT_COMPARE
#include "rcpdm_variants.h"
#if CONFIG_YORADIO_RCPDM_FEEDBACK
#include "rcpdm_feedback_reference.h"
#endif
#if RCPDM_TEST_SIMPLE
#include "rcpdm_simple.h"
#include "rcpdm_simple_reference.h"
#define RCPDM_VERIFY_SAMPLE rcpdm_simple_reference
#define RCPDM_VERIFY_NAME "RCPDM-Simple"
#else
#define RCPDM_VERIFY_SAMPLE rc_candidate_original
#define RCPDM_VERIFY_NAME "RCPDM"
#endif
#endif
_Static_assert(BOARD_I2S_PDM_OVERSAMPLE == RC_PDM_BITS_PER_SAMPLE,
               "I2S RCPDM requires exactly 32 bits per output PCM sample");
#endif

static const char *TAG = "audio_output";

#if defined(YORADIO_ESP8266_AUDIO_TRACE)
static unsigned s_output_pcm_trace_count;

static void trace_output_pcm(const int16_t *samples, size_t frames,
                             uint8_t channels) {
    if (s_output_pcm_trace_count >= 4U || !frames) return;
    int16_t minimum = INT16_MAX;
    int16_t maximum = INT16_MIN;
    uint32_t hash = 2166136261U;
    int16_t first[8] = {0};
    for (size_t frame = 0; frame < frames; ++frame) {
        int32_t mono = samples[frame * channels];
        if (channels == 2)
            mono = (mono + samples[frame * 2U + 1U]) / 2;
        int16_t value = (int16_t)mono;
        if (value < minimum) minimum = value;
        if (value > maximum) maximum = value;
        hash = (hash ^ (uint16_t)value) * 16777619U;
        if (frame < sizeof(first) / sizeof(first[0])) first[frame] = value;
    }
    if (s_output_pcm_trace_count && minimum == 0 && maximum == 0) return;
    ESP_LOGI(TAG,
             "AUDIO_TRACE OUTPUT-PCM cb=%u frames=%u min=%d max=%d "
             "fnv=%08x first=%d,%d,%d,%d,%d,%d,%d,%d",
             s_output_pcm_trace_count++, (unsigned)frames, minimum, maximum,
             (unsigned)hash, first[0], first[1], first[2], first[3],
             first[4], first[5], first[6], first[7]);
}
#endif
#if YORADIO_ESP8266_SPI_PDM
static uint32_t s_input_sample_rate;
static uint32_t s_resample_phase;
static uint32_t s_pdm_integrator;
static bool s_spi_initialized;
static bool s_spi_pin_selected;
#elif YORADIO_ESP8266_I2S_PDM
static uint32_t s_input_sample_rate;
static uint32_t s_resample_phase;
#if CONFIG_YORADIO_AUDIO_OUTPUT_I2S_RCPDM
#if CONFIG_YORADIO_RCPDM_FEEDBACK
static rc_pdm_feedback_t s_rcpdm;
#else
static rc_pdm_t s_rcpdm;
#endif
#else
static uint32_t s_pdm_integrator;
#endif
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
/* Signed: negating 16U wraps and clamps neutral balance to -16 (mute). */
#define BALANCE_DENOMINATOR 16
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

#include "audio_gain_led.inc"

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
    /* Mono PDM has no independent L/R channels to balance. */
    uint8_t left_balance = channels == 2 && s_balance < 0
        ? (uint8_t)(BALANCE_DENOMINATOR + s_balance) : BALANCE_DENOMINATOR;
    uint8_t right_balance = channels == 2 && s_balance > 0
        ? (uint8_t)(BALANCE_DENOMINATOR - s_balance) : BALANCE_DENOMINATOR;
    uint32_t left_gain = channel_gain_q15(s_volume, left_balance);
    uint32_t right_gain = channel_gain_q15(s_volume, right_balance);
    output_gain_with_led(samples, frames, channels, left_gain, right_gain);
#if defined(YORADIO_ESP8266_AUDIO_TRACE)
    trace_output_pcm(samples, frames, channels);
#endif

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
#if CONFIG_YORADIO_STATUS_LED
    status_led_clear();
#endif
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

#define I2S_PDM_WRITE_TIMEOUT_MS 100U
#ifndef YORADIO_ESP8266_PDM32_LOAN_WORDS
#define YORADIO_ESP8266_PDM32_LOAN_WORDS 512
#endif
#define I2S_PDM_SILENCE_WORD 0xaaaaaaaaU
#if CONFIG_YORADIO_AUDIO_OUTPUT_I2S_RCPDM
#define I2S_PDM_LOG_NAME "I2S RCPDM"
#else
#define I2S_PDM_LOG_NAME "I2S-PDM"
#endif

typedef struct {
    uint32_t *words;
    size_t word_count;
    size_t capacity;
    TickType_t deadline;
} i2s_pdm_writer_t;

static esp_err_t i2s_pdm_reserve(i2s_pdm_writer_t *writer) {
    TickType_t now = xTaskGetTickCount();
    if ((int32_t)(writer->deadline - now) <= 0) return ESP_ERR_TIMEOUT;
    esp_err_t result = esp8266_nodac_i2s_reserve(
        &writer->words, &writer->capacity, writer->deadline - now);
#if YORADIO_ESP8266_PDM32_LOAN_WORDS < 512
    /* Diagnostic publication cadence, NOT a smaller DMA buffer. Releasing
     * this prefix lets EOF consume it between producer loans. The driver
     * retains ownership of the entire 512-word physical buffer. */
    if (result == ESP_OK && writer->capacity > YORADIO_ESP8266_PDM32_LOAN_WORDS)
        writer->capacity = YORADIO_ESP8266_PDM32_LOAN_WORDS;
#endif
    if (result != ESP_OK)
        ESP_LOGE(TAG, I2S_PDM_LOG_NAME " DMA reserve failed: %s",
                 esp_err_to_name(result));
    return result;
}

static esp_err_t i2s_pdm_flush(i2s_pdm_writer_t *writer) {
    if (!writer->words) return ESP_OK;
    esp_err_t result = esp8266_nodac_i2s_commit(writer->word_count);
    if (result != ESP_OK) {
        /* Do not leave a loan outstanding on an error return. */
        (void)esp8266_nodac_i2s_commit(0);
        ESP_LOGE(TAG, I2S_PDM_LOG_NAME " DMA commit failed: %s",
                 esp_err_to_name(result));
    }
    writer->words = NULL;
    writer->word_count = writer->capacity = 0;
    return result;
}

static esp_err_t i2s_pdm_push_word(i2s_pdm_writer_t *writer, uint32_t word) {
    if (!writer->words) {
        esp_err_t result = i2s_pdm_reserve(writer);
        if (result != ESP_OK) return result;
    }
    writer->words[writer->word_count++] = word;
    return writer->word_count == writer->capacity
        ? i2s_pdm_flush(writer) : ESP_OK;
}

#if CONFIG_YORADIO_AUDIO_OUTPUT_I2S_RCPDM || CONFIG_YORADIO_I2S_PDM_OVERSAMPLE_32
#if BOARD_I2S_PDM_OVERSAMPLE != 32U || BOARD_I2S_PDM_REPEAT != 1U
#error "The optimized PDM32 packer requires 32 genuine bits per sample"
#endif

/* This packer runs in the audio task, not in the DMA ISR. Keep scarce IRAM
 * for decoder word workspaces; flash execution remains cache-backed. */
#if CONFIG_YORADIO_AUDIO_OUTPUT_I2S_RCPDM && !RCPDM_DISABLE_BATCH
static inline __attribute__((always_inline)) void i2s_rcpdm_fill_channels(
    uint32_t *words, const int16_t *pcm, size_t frames, unsigned channels) {
#if CONFIG_YORADIO_RCPDM_FEEDBACK
    rc_pdm_feedback_fill(&s_rcpdm, words, pcm, frames, channels);
#elif RCPDM_TEST_SIMPLE
    rcpdm_simple_fill(&s_rcpdm, words, pcm, frames, channels);
#else
    rc_pdm_fill(&s_rcpdm, words, pcm, frames, channels);
#endif
}
static void __attribute__((noinline)) i2s_rcpdm_fill_mono(
    uint32_t *words, const int16_t *pcm, size_t frames) {
    i2s_rcpdm_fill_channels(words, pcm, frames, 1);
}
static void __attribute__((noinline)) i2s_rcpdm_fill_stereo(
    uint32_t *words, const int16_t *pcm, size_t frames) {
    i2s_rcpdm_fill_channels(words, pcm, frames, 2);
}
static inline __attribute__((always_inline)) void i2s_rcpdm_fill(
    uint32_t *words, const int16_t *pcm, size_t frames, unsigned channels) {
    if (channels == 2) i2s_rcpdm_fill_stereo(words, pcm, frames);
    else i2s_rcpdm_fill_mono(words, pcm, frames);
}
#endif
#ifndef YORADIO_ESP8266_PDM32_IRAM
#define YORADIO_ESP8266_PDM32_IRAM 0
#endif
#ifndef YORADIO_ESP8266_PDM32_BATCH
#define YORADIO_ESP8266_PDM32_BATCH 0
#endif
#if YORADIO_ESP8266_PDM32_BATCH != 0 && YORADIO_ESP8266_PDM32_BATCH != 1
#error "YORADIO_ESP8266_PDM32_BATCH must be 0 or 1"
#endif
#if YORADIO_ESP8266_PDM32_IRAM != 0 && YORADIO_ESP8266_PDM32_IRAM != 1
#error "YORADIO_ESP8266_PDM32_IRAM must be 0 or 1"
#endif
#if YORADIO_ESP8266_PDM32_IRAM
/* Experimental placement only; pdm32_iram.lf recovers space from a cold
 * task-only libgcc helper. The shared codec arena remains 16384 bytes. */
#define PDM32_CODE_ATTR IRAM_ATTR
#else
#define PDM32_CODE_ATTR
#endif
static uint32_t PDM32_CODE_ATTR __attribute__((noinline))
i2s_pdm_pack32(int16_t sample) {
#if CONFIG_YORADIO_AUDIO_OUTPUT_I2S_RCPDM
#if CONFIG_YORADIO_RCPDM_FEEDBACK
    return rc_pdm_feedback_sample(&s_rcpdm, sample);
#elif defined(RCPDM_TEST_SAMPLE)
    return RCPDM_TEST_SAMPLE(&s_rcpdm, sample);
#else
    return rc_pdm_sample(&s_rcpdm, sample);
#endif
#else
    const uint32_t target = (uint32_t)((int32_t)sample - INT16_MIN);
    uint32_t integrator = s_pdm_integrator;
    uint32_t word = 0;
#define PDM32_STEP() do { \
        uint32_t sum = integrator + target; \
        integrator = sum & 0xffffU; \
        word = (word << 1) | (sum >> 16); \
    } while (0)
    PDM32_STEP(); PDM32_STEP(); PDM32_STEP(); PDM32_STEP();
    PDM32_STEP(); PDM32_STEP(); PDM32_STEP(); PDM32_STEP();
    PDM32_STEP(); PDM32_STEP(); PDM32_STEP(); PDM32_STEP();
    PDM32_STEP(); PDM32_STEP(); PDM32_STEP(); PDM32_STEP();
    PDM32_STEP(); PDM32_STEP(); PDM32_STEP(); PDM32_STEP();
    PDM32_STEP(); PDM32_STEP(); PDM32_STEP(); PDM32_STEP();
    PDM32_STEP(); PDM32_STEP(); PDM32_STEP(); PDM32_STEP();
    PDM32_STEP(); PDM32_STEP(); PDM32_STEP(); PDM32_STEP();
#undef PDM32_STEP
    s_pdm_integrator = integrator;
    return word;
#endif
}
#if YORADIO_ESP8266_OUTPUT_COMPARE
bool native_audio_output_benchmark_verify(void) {
#if CONFIG_YORADIO_RCPDM_FEEDBACK
    rc_pdm_feedback_t saved = s_rcpdm, expected;
    rc_pdm_feedback_init(&s_rcpdm, RC_FB_DEFAULT_SEED);
    expected = s_rcpdm;
    bool ok = true;
    for (int32_t pcm = INT16_MIN; pcm <= INT16_MAX; ++pcm) {
        uint32_t want = rc_feedback_reference_sample(&expected, (int16_t)pcm);
        if (want != i2s_pdm_pack32((int16_t)pcm) ||
            memcmp(&expected, &s_rcpdm, sizeof(expected))) { ok = false; break; }
        if (!((uint32_t)pcm & 1023U)) vTaskDelay(1);
    }
    unsigned batch_words = 0;
#if !RCPDM_DISABLE_BATCH
    int16_t pcm_batch[34];
    uint32_t words[17], random = 1;
    for (unsigned channels = 1; ok && channels <= 2; ++channels) {
        rc_pdm_feedback_init(&s_rcpdm, RC_FB_DEFAULT_SEED);
        expected = s_rcpdm;
        for (unsigned block = 0; ok && block < 128; ++block) {
            for (unsigned i = 0; i < 34; ++i) {
                random = random * 1664525U + 1013904223U;
                pcm_batch[i] = (int16_t)(random >> 16);
            }
            size_t count = block % 18U;
            i2s_rcpdm_fill(words, pcm_batch, count, channels);
            for (size_t i = 0; i < count; ++i) {
                int32_t mono = pcm_batch[i * channels];
                if (channels == 2) mono = (mono + pcm_batch[i * channels + 1]) / 2;
                if (words[i] != rc_feedback_reference_sample(&expected, (int16_t)mono)) ok = false;
                ++batch_words;
            }
            if (memcmp(&expected, &s_rcpdm, sizeof(expected))) ok = false;
        }
    }
#endif
    s_rcpdm = saved;
    if (ok) {
        ESP_LOGI(TAG, "RCPDM feedback bit/state PASS: 65536 frames");
        ESP_LOGI(TAG, "RCPDM feedback batch PASS: %u words", batch_words);
    }
    else ESP_LOGE(TAG, "RCPDM feedback bit/state FAIL");
    return ok;
#elif CONFIG_YORADIO_AUDIO_OUTPUT_I2S_RCPDM
#if RCPDM_TEST_SIMPLE
    ESP_LOGI(TAG, "RCPDM-Simple backend: %s",
             RCPDM_SIMPLE_LX106_ASM ? "Xtensa LX106 asm" : "portable C");
    ESP_LOGI(TAG, "RCPDM-Simple asm group bits: %u",
             RCPDM_SIMPLE_LX106_ASM ? (RCPDM_SIMPLE_UNROLL4 ? 4U : 1U) : 0U);
#endif
    const uint32_t seeds[] = {0, 1, 15, 0x80000000U, UINT32_MAX - 15U, UINT32_MAX};
    uint32_t saved = s_rcpdm.rc;
    unsigned cases = 0;
    rc_pdm_t expected;
#if RCPDM_TEST_SIMPLE
    /* Exercise every supported count, including unroll4 group boundaries,
     * empty input and the non-asm alpha=1/4 fallback. */
    {
        const int16_t samples[] = {INT16_MIN, -1, 0, 1, INT16_MAX};
        const unsigned shifts[] = {2, 4};
        unsigned dispatch_cases = 0;
        for (unsigned s = 0; s < sizeof(seeds) / sizeof(seeds[0]); ++s)
            for (unsigned j = 0; j < sizeof(samples) / sizeof(samples[0]); ++j)
                for (unsigned n = 0; n <= 32; ++n)
                    for (unsigned k = 0; k < sizeof(shifts) / sizeof(shifts[0]); ++k) {
                        rc_pdm_t actual = {seeds[s]}, fallback = {seeds[s]};
                        uint32_t got = rcpdm_simple_bits(&actual, samples[j], n, shifts[k]);
                        uint32_t want = rcpdm_simple_bits_c(&fallback, samples[j], n, shifts[k]);
                        if (got != want || actual.rc != fallback.rc) {
                            ESP_LOGE(TAG, "RCPDM-Simple dispatch FAIL after %u cases", dispatch_cases);
                            goto mismatch;
                        }
                        ++dispatch_cases;
                    }
        ESP_LOGI(TAG, "RCPDM-Simple dispatch PASS: %u cases", dispatch_cases);
    }
#endif
    for (unsigned s = 0; s < sizeof(seeds) / sizeof(seeds[0]); ++s) {
        for (int32_t pcm = INT16_MIN; pcm <= INT16_MAX; ++pcm) {
            s_rcpdm.rc = expected.rc = seeds[s];
            uint32_t want = RCPDM_VERIFY_SAMPLE(&expected, (int16_t)pcm);
            uint32_t got = i2s_pdm_pack32((int16_t)pcm);
            if (want != got || expected.rc != s_rcpdm.rc) goto mismatch;
            if (!(++cases & 1023U)) vTaskDelay(1);
        }
    }
    s_rcpdm.rc = expected.rc = 0x80000000U;
    uint32_t random = 1;
    for (unsigned i = 0; i < 100000; ++i) {
        random = random * 1664525U + 1013904223U;
        int16_t pcm = (int16_t)((int32_t)(random & 65535U) - 32768);
        uint32_t want = RCPDM_VERIFY_SAMPLE(&expected, pcm);
        uint32_t got = i2s_pdm_pack32(pcm);
        if (want != got || expected.rc != s_rcpdm.rc) goto mismatch;
        if (!(++cases & 1023U)) vTaskDelay(1);
    }
    s_rcpdm.rc = saved;
    ESP_LOGI(TAG, "%s bit-exact PASS: %u words and states", RCPDM_VERIFY_NAME, cases);
#if !RCPDM_DISABLE_BATCH
    // Exercise the actual machine-code batch writer before DMA/timing starts.
    int16_t pcm_batch[34];
    uint32_t words[17];
    unsigned batch_words = 0;
    for (unsigned channels = 1; channels <= 2; ++channels) {
        s_rcpdm.rc = expected.rc = 0x80000000U;
        for (unsigned block = 0; block < 128; ++block) {
            for (unsigned i = 0; i < 34; ++i) {
                random = random * 1664525U + 1013904223U;
                pcm_batch[i] = (int16_t)(random >> 16);
            }
            size_t count = block % 18U; // includes empty and partial spans
            i2s_rcpdm_fill(words, pcm_batch, count, channels);
            for (size_t i = 0; i < count; ++i) {
                int32_t mono = pcm_batch[i * channels];
                if (channels == 2) mono = (mono + pcm_batch[i * channels + 1]) / 2;
                if (words[i] != RCPDM_VERIFY_SAMPLE(&expected, (int16_t)mono)) goto mismatch;
                ++batch_words;
            }
            if (s_rcpdm.rc != expected.rc) goto mismatch;
        }
    }
    s_rcpdm.rc = saved;
    ESP_LOGI(TAG, "%s batch bit-exact PASS: %u words, mono/stereo", RCPDM_VERIFY_NAME, batch_words);
#endif
    return true;
mismatch:
    ESP_LOGE(TAG, "%s bit-exact FAIL after %u words", RCPDM_VERIFY_NAME, cases);
    s_rcpdm.rc = saved;
    return false;
#else
    return true;
#endif
}

/* Diagnostic only: actual production packer, before I2S/DMA is initialized.
 * Count includes the common loop/checksum overhead; no writes or allocation. */
uint32_t native_audio_output_benchmark_pack32(const int16_t *pcm,
                                             size_t samples, unsigned repeats) {
#if CONFIG_YORADIO_RCPDM_FEEDBACK
    rc_pdm_feedback_init(&s_rcpdm, RC_FB_DEFAULT_SEED);
#elif CONFIG_YORADIO_AUDIO_OUTPUT_I2S_RCPDM
    rc_pdm_init(&s_rcpdm);
#else
    s_pdm_integrator = 0;
#endif
    uint32_t checksum = 0;
    for (unsigned repeat = 0; repeat < repeats; ++repeat)
        for (size_t i = 0; i < samples; ++i)
            checksum ^= i2s_pdm_pack32(pcm[i]);
    return checksum;
}
#endif
#else
static esp_err_t i2s_pdm_push_bit(i2s_pdm_writer_t *writer, bool high) {
    s_i2s_pdm_partial_word =
        (s_i2s_pdm_partial_word << 1) | (high ? 1U : 0U);
    ++s_i2s_pdm_partial_bits;
    if (s_i2s_pdm_partial_bits != 32U) return ESP_OK;

    uint32_t word = s_i2s_pdm_partial_word;
    s_i2s_pdm_partial_word = 0;
    s_i2s_pdm_partial_bits = 0;
    return i2s_pdm_push_word(writer, word);
}
#endif

static esp_err_t i2s_pdm_emit_sample(int16_t sample,
                                     i2s_pdm_writer_t *writer) {
#if CONFIG_YORADIO_AUDIO_OUTPUT_I2S_RCPDM || CONFIG_YORADIO_I2S_PDM_OVERSAMPLE_32
    return i2s_pdm_push_word(writer, i2s_pdm_pack32(sample));
#else
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
#endif
}

static esp_err_t i2s_pdm_finish_partial_word(i2s_pdm_writer_t *writer) {
#if !CONFIG_YORADIO_AUDIO_OUTPUT_I2S_RCPDM && !CONFIG_YORADIO_I2S_PDM_OVERSAMPLE_32
    while (s_i2s_pdm_partial_bits) {
        esp_err_t result = i2s_pdm_emit_sample(0, writer);
        if (result != ESP_OK) return result;
    }
#endif
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
#if CONFIG_YORADIO_RCPDM_FEEDBACK
        rc_pdm_feedback_init(&s_rcpdm, RC_FB_DEFAULT_SEED);
#elif CONFIG_YORADIO_AUDIO_OUTPUT_I2S_RCPDM
        rc_pdm_init(&s_rcpdm);
#else
        s_pdm_integrator = 0;
#endif
        s_i2s_pdm_partial_word = 0;
        s_i2s_pdm_partial_bits = 0;
    }
    native_audio_output_reload_settings();
    if (result == ESP_OK) {
#if CONFIG_YORADIO_AUDIO_OUTPUT_I2S_RCPDM
#if CONFIG_YORADIO_RCPDM_FEEDBACK
        ESP_LOGI(TAG, "RC-PDM feedback: unity error, interpolation, TPDF dither; state=16 bytes");
#endif
        ESP_LOGI(TAG,
                 "I2S RCPDM DMA: mono GPIO%d/RX, carrier %u Hz, alpha=1/16; "
                 "%u x %u words; UART RX ignored",
                 BOARD_I2S_DATA_GPIO, BOARD_I2S_PDM_CARRIER_HZ,
                 ESP8266_NODAC_DMA_BUFFER_COUNT,
                 ESP8266_NODAC_DMA_BUFFER_WORDS);
#else
        ESP_LOGI(TAG,
                 "I2S-PDM DMA: mono GPIO%d/RX, carrier %u Hz, "
                 "PDM%u x%u effective %u Hz, nominal carrier %u Hz, "
                 "%u x %u words; UART RX ignored",
                 BOARD_I2S_DATA_GPIO, BOARD_I2S_PDM_CARRIER_HZ,
                 BOARD_I2S_PDM_OVERSAMPLE, BOARD_I2S_PDM_REPEAT,
                 BOARD_I2S_PDM_EFFECTIVE_HZ, BOARD_I2S_PDM_NOMINAL_HZ,
                 ESP8266_NODAC_DMA_BUFFER_COUNT,
                 ESP8266_NODAC_DMA_BUFFER_WORDS);
#endif
    }
    return result;
}

/* Instantiate this single implementation with constant channel counts below.
 * always_inline is intentional: optimized builds must not dispatch mono/stereo
 * inside the gain, downmix, resampler or modulator loops. */
static inline __attribute__((always_inline)) esp_err_t i2s_pdm_write_channels(
    int16_t *samples, size_t sample_count, uint32_t sample_rate,
    const uint8_t channels) {
    size_t frames = sample_count / channels;
    native_audio_normalizer_configure(
        s_normalization_enabled, s_normalization_max_gain_db,
        s_normalization_target_db, s_normalization_time_ms, sample_rate);
    native_audio_normalizer_process(samples, frames, channels);
    /* Mono PDM has no independent L/R channels to balance. */
    uint8_t left_balance = channels == 2 && s_balance < 0
        ? (uint8_t)(BALANCE_DENOMINATOR + s_balance) : BALANCE_DENOMINATOR;
    uint8_t right_balance = channels == 2 && s_balance > 0
        ? (uint8_t)(BALANCE_DENOMINATOR - s_balance) : BALANCE_DENOMINATOR;
    uint32_t left_gain = channel_gain_q15(s_volume, left_balance);
    uint32_t right_gain = channel_gain_q15(s_volume, right_balance);
    output_gain_with_led(samples, frames, channels, left_gain, right_gain);
#if defined(YORADIO_ESP8266_AUDIO_TRACE)
    trace_output_pcm(samples, frames, channels);
#endif

    if (sample_rate != s_input_sample_rate) {
        s_input_sample_rate = sample_rate;
        s_resample_phase = 0;
    }
    i2s_pdm_writer_t writer = {
        .deadline = xTaskGetTickCount() +
                    pdMS_TO_TICKS(I2S_PDM_WRITE_TIMEOUT_MS),
    };
#if CONFIG_YORADIO_AUDIO_OUTPUT_I2S_RCPDM && !RCPDM_DISABLE_BATCH
    if (sample_rate == BOARD_I2S_PDM_SAMPLE_RATE && s_resample_phase == 0) {
        size_t frame = 0;
        while (frame < frames) {
            esp_err_t result = i2s_pdm_reserve(&writer);
            if (result != ESP_OK) {
                // Match the scalar path: it advances one sample before a
                // failed reserve and leaves the resampler subtraction pending.
                int32_t mono = samples[frame * channels];
                if (channels == 2) mono = (mono + samples[frame * 2U + 1U]) / 2;
                (void)i2s_pdm_pack32((int16_t)mono);
                s_resample_phase = BOARD_I2S_PDM_SAMPLE_RATE;
                return result;
            }
            size_t count = frames - frame;
            if (count > writer.capacity) count = writer.capacity;
            i2s_rcpdm_fill(writer.words, samples + frame * channels, count, channels);
            writer.word_count = count;
            frame += count;
            bool full = count == writer.capacity;
            result = i2s_pdm_flush(&writer);
            if (result != ESP_OK) {
                if (full) s_resample_phase = BOARD_I2S_PDM_SAMPLE_RATE;
                return result;
            }
        }
        return ESP_OK;
    }
#endif
#if YORADIO_ESP8266_PDM32_BATCH && CONFIG_YORADIO_AUDIO_OUTPUT_I2S_PDM && CONFIG_YORADIO_I2S_PDM_OVERSAMPLE_32
    /* At 48 kHz one PCM frame produces exactly one DMA word. Fill the
     * existing loan directly; keep gain/LED/normalization above and the
     * scalar resampler below unchanged. No additional PCM or word buffer. */
    if (sample_rate == BOARD_I2S_PDM_SAMPLE_RATE && s_resample_phase == 0) {
        size_t frame = 0;
        while (frame < frames) {
            esp_err_t result = i2s_pdm_reserve(&writer);
            if (result != ESP_OK) {
                /* Scalar emit packs before reserving: preserve its one
                 * advanced sample and unconsumed resampler phase on error. */
                int32_t mono = samples[frame * channels];
                if (channels == 2) mono = (mono + samples[frame * 2U + 1U]) / 2;
                (void)i2s_pdm_pack32((int16_t)mono);
                s_resample_phase = BOARD_I2S_PDM_SAMPLE_RATE;
                return result;
            }
            size_t count = frames - frame;
            if (count > writer.capacity) count = writer.capacity;
            for (size_t i = 0; i < count; ++i) {
                int32_t mono = samples[(frame + i) * channels];
                if (channels == 2)
                    mono = (mono + samples[(frame + i) * 2U + 1U]) / 2;
                writer.words[i] = i2s_pdm_pack32((int16_t)mono);
            }
            writer.word_count = count;
            frame += count;
            bool full = count == writer.capacity;
            result = i2s_pdm_flush(&writer);
            if (result != ESP_OK) {
                if (full) s_resample_phase = BOARD_I2S_PDM_SAMPLE_RATE;
                return result;
            }
        }
        return ESP_OK;
    }
#endif
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

static esp_err_t i2s_pdm_write_mono(int16_t *samples, size_t sample_count,
                                    uint32_t sample_rate) {
    return i2s_pdm_write_channels(samples, sample_count, sample_rate, 1);
}

static esp_err_t i2s_pdm_write_stereo(int16_t *samples, size_t sample_count,
                                      uint32_t sample_rate) {
    return i2s_pdm_write_channels(samples, sample_count, sample_rate, 2);
}

typedef esp_err_t (*i2s_pdm_write_fn)(int16_t *, size_t, uint32_t);
static i2s_pdm_write_fn s_i2s_pdm_write;
static uint8_t s_i2s_pdm_channels;

esp_err_t native_audio_output_write(int16_t *samples, size_t sample_count,
                                    uint32_t sample_rate, uint8_t channels) {
    if (!samples || !sample_count || !sample_rate ||
        (channels != 1 && channels != 2) ||
        (channels == 2 && (sample_count & 1U)))
        return ESP_ERR_INVALID_ARG;
    if (!s_i2s_started) return ESP_ERR_INVALID_STATE;

    /* Only the audio producer owns this dispatch state. Preserve RC/PDM and
     * resampler history across channel-only changes; silence resets them. */
    if (channels != s_i2s_pdm_channels) {
        s_i2s_pdm_write = channels == 2
            ? i2s_pdm_write_stereo : i2s_pdm_write_mono;
        s_i2s_pdm_channels = channels;
    }
    return s_i2s_pdm_write(samples, sample_count, sample_rate);
}

void native_audio_output_silence(void) {
#if CONFIG_YORADIO_STATUS_LED
    status_led_clear();
#endif
    if (!s_i2s_started) return;
    i2s_pdm_writer_t writer = {
        .deadline = xTaskGetTickCount() +
                    pdMS_TO_TICKS(I2S_PDM_WRITE_TIMEOUT_MS),
    };
    esp_err_t result = i2s_pdm_finish_partial_word(&writer);
    if (result == ESP_OK) result = i2s_pdm_fill_dma_silence();
    if (result != ESP_OK)
        ESP_LOGE(TAG, I2S_PDM_LOG_NAME " silence failed: %s", esp_err_to_name(result));
    s_input_sample_rate = 0;
    s_resample_phase = 0;
#if CONFIG_YORADIO_RCPDM_FEEDBACK
    rc_pdm_feedback_init(&s_rcpdm, RC_FB_DEFAULT_SEED);
#elif CONFIG_YORADIO_AUDIO_OUTPUT_I2S_RCPDM
    rc_pdm_init(&s_rcpdm);
#else
    s_pdm_integrator = 0;
#endif
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
    /* Balance only applies when the decoder supplies independent L/R. */
    uint8_t left_balance = channels == 2 && s_balance < 0
        ? (uint8_t)(BALANCE_DENOMINATOR + s_balance) : BALANCE_DENOMINATOR;
    uint8_t right_balance = channels == 2 && s_balance > 0
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
    stats->chained_transfers = esp8266_nodac_i2s_eofs();
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
