/* Minimal ESP8266 output-only I2S/SLC ring for a software NoDAC stream.
 *
 * The ring and companion-link arrangement follows the LGPL-2.1 ESP8266
 * Arduino core I2S implementation used by ESP8266Audio. It is kept local so
 * the RTOS SDK application does not depend on Arduino. */

#include "esp8266_nodac_i2s.h"

#include <stdbool.h>
#include <string.h>

#if defined(YORADIO_ESP8266_AUDIO_TRACE)
#include "esp_log.h"
#endif
#include "esp_attr.h"
#include "esp8266/eagle_soc.h"
#include "esp8266/i2s_struct.h"
#include "esp8266/pin_mux_register.h"
#include "esp8266/slc_struct.h"
#include "freertos/task.h"
#include "rom/ets_sys.h"

#define NODAC_DMA_BUFFER_COUNT ESP8266_NODAC_DMA_BUFFER_COUNT
#define NODAC_DMA_BUFFER_WORDS ESP8266_NODAC_DMA_BUFFER_WORDS
#define NODAC_DMA_BUFFER_BYTES \
    (NODAC_DMA_BUFFER_WORDS * sizeof(uint32_t))
#define NODAC_SLC_ADDRESS_MASK 0x000fffffU

typedef struct nodac_dma_descriptor {
    uint32_t blocksize : 12;
    uint32_t datalen : 12;
    uint32_t unused : 5;
    uint32_t sub_sof : 1;
    uint32_t eof : 1;
    volatile uint32_t owner : 1;
    uint32_t *buf_ptr;
    struct nodac_dma_descriptor *next_link_ptr;
} nodac_dma_descriptor_t;

static uint32_t s_buffers[NODAC_DMA_BUFFER_COUNT][NODAC_DMA_BUFFER_WORDS];
static nodac_dma_descriptor_t s_descriptors[NODAC_DMA_BUFFER_COUNT];
static uint32_t *s_free_buffers[NODAC_DMA_BUFFER_COUNT];
static volatile uint8_t s_free_count;
static uint32_t *volatile s_current_buffer;
static volatile size_t s_current_position;
static volatile TaskHandle_t s_waiter;
static volatile bool s_waiting;
static uint32_t s_silence_word;
static volatile uint32_t s_underruns;
#if defined(YORADIO_ESP8266_AUDIO_TRACE)
static const char *TAG = "nodac_i2s";
static unsigned s_dma_trace_count;

static unsigned trace_popcount32(uint32_t word) {
    unsigned count = 0;
    while (word) {
        word &= word - 1U;
        ++count;
    }
    return count;
}
#endif

#if YORADIO_ESP8266_AUDIO_PROFILE
extern void audio_profile_spi_wait_begin(void);
extern void audio_profile_spi_wait_end(void);
#elif YORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK
extern void audio_output_benchmark_spi_wait_begin(void);
extern void audio_output_benchmark_spi_wait_end(void);
#endif

extern void rom_i2c_writeReg_Mask(int block, int host_id, int reg_add,
                                  int msb, int lsb, int value);

static uint32_t *IRAM_ATTR pop_free_buffer(void) {
    uint32_t *buffer = s_free_buffers[0];
    --s_free_count;
    for (uint8_t index = 0; index < s_free_count; ++index)
        s_free_buffers[index] = s_free_buffers[index + 1U];
    return buffer;
}

static void IRAM_ATTR nodac_slc_isr(void *arg) {
    (void)arg;
    _xt_isr_mask(1U << ETS_SLC_INUM);
    uint32_t status = SLC0.int_st.val;
    SLC0.int_clr.val = 0xffffffffU;

    if (status & (1U << 17)) {
        nodac_dma_descriptor_t *finished =
            (nodac_dma_descriptor_t *)SLC0.rx_eof_des_addr;
        nodac_dma_descriptor_t *next = finished->next_link_ptr;
        if (s_free_count >= NODAC_DMA_BUFFER_COUNT - 1U ||
            (s_current_buffer == next->buf_ptr &&
             s_current_position < NODAC_DMA_BUFFER_WORDS))
            ++s_underruns;
        for (unsigned word = 0; word < NODAC_DMA_BUFFER_WORDS; ++word)
            finished->buf_ptr[word] = s_silence_word;
        if (s_free_count >= NODAC_DMA_BUFFER_COUNT - 1U)
            (void)pop_free_buffer();
        s_free_buffers[s_free_count++] = finished->buf_ptr;

        if (s_waiting && s_waiter) {
            BaseType_t higher_task_woken = pdFALSE;
            s_waiting = false;
            vTaskNotifyGiveFromISR((TaskHandle_t)s_waiter,
                                   &higher_task_woken);
            if (higher_task_woken) portYIELD_FROM_ISR();
        }
    }

    _xt_isr_unmask(1U << ETS_SLC_INUM);
}

static void configure_descriptors(uint32_t silence_word) {
    s_silence_word = silence_word;
    s_free_count = 0;
    s_current_buffer = NULL;
    s_current_position = 0;
    s_waiter = NULL;
    s_waiting = false;
    s_underruns = 0;
#if defined(YORADIO_ESP8266_AUDIO_TRACE)
    s_dma_trace_count = 0;
#endif
    for (unsigned index = 0; index < NODAC_DMA_BUFFER_COUNT; ++index) {
        for (unsigned word = 0; word < NODAC_DMA_BUFFER_WORDS; ++word)
            s_buffers[index][word] = silence_word;
        nodac_dma_descriptor_t *descriptor = &s_descriptors[index];
        memset(descriptor, 0, sizeof(*descriptor));
        descriptor->owner = 1;
        descriptor->eof = 1;
        descriptor->datalen = NODAC_DMA_BUFFER_BYTES;
        descriptor->blocksize = NODAC_DMA_BUFFER_BYTES;
        descriptor->buf_ptr = s_buffers[index];
        descriptor->next_link_ptr =
            &s_descriptors[(index + 1U) % NODAC_DMA_BUFFER_COUNT];
    }
}

static void configure_slc(void) {
    _xt_isr_mask(1U << ETS_SLC_INUM);
    SLC0.conf0.rx_rst = 1;
    SLC0.conf0.tx_rst = 1;
    SLC0.conf0.rx_rst = 0;
    SLC0.conf0.tx_rst = 0;
    SLC0.int_clr.val = 0xffffffffU;
    SLC0.int_ena.val = 0;
    /* The RTOS SDK names bits 12..13 as TX burst controls, but on ESP8266
     * they are SLC_MODE. Match the Arduino core/ESP8266Audio DMA mode 1. */
    SLC0.conf0.val = (SLC0.conf0.val & ~(3U << 12)) | (1U << 12);
    SLC0.rx_dscr_conf.rx_fill_mode = 0;
    SLC0.rx_dscr_conf.rx_eof_mode = 0;
    SLC0.rx_dscr_conf.rx_fill_en = 0;
    SLC0.rx_dscr_conf.token_no_replace = 1;
    SLC0.rx_dscr_conf.infor_no_replace = 1;
    SLC0.tx_link.val =
        (uint32_t)&s_descriptors[1] & NODAC_SLC_ADDRESS_MASK;
    SLC0.rx_link.val =
        (uint32_t)&s_descriptors[0] & NODAC_SLC_ADDRESS_MASK;
    _xt_isr_attach(ETS_SLC_INUM, nodac_slc_isr, NULL);
    SLC0.int_ena.rx_eof = 1;
    /* The companion TX link intentionally has no payload owner. Enabling its
     * descriptor-error source can create an ISR storm at low I2S rates; EOF
     * is the only event needed to recycle the output ring. */
    SLC0.int_ena.rx_dscr_err = 0;
    _xt_isr_unmask(1U << ETS_SLC_INUM);
    SLC0.tx_link.start = 1;
    SLC0.rx_link.start = 1;
}

static void configure_i2s(uint8_t bck_div, uint8_t clkm_div) {
    rom_i2c_writeReg_Mask(0x67, 4, 4, 7, 7, 1);
    PIN_FUNC_SELECT(PERIPHS_IO_MUX_U0RXD_U, FUNC_I2SO_DATA);
    PIN_FUNC_SELECT(PERIPHS_IO_MUX_MTDO_U, FUNC_I2SO_BCK);
    PIN_FUNC_SELECT(PERIPHS_IO_MUX_GPIO2_U, FUNC_I2SO_WS);

    I2S0.int_clr.val = 0x3fU;
    I2S0.int_ena.val = 0;
    I2S0.conf.val &= ~0x0fU;
    I2S0.conf.val |= 0x0fU;
    I2S0.conf.val &= ~0x0fU;
    I2S0.fifo_conf.dscr_en = 0;
    I2S0.fifo_conf.tx_fifo_mod = 0;
    I2S0.fifo_conf.rx_fifo_mod = 0;
    I2S0.fifo_conf.dscr_en = 1;
    I2S0.conf_chan.tx_chan_mod = 0;
    I2S0.conf_chan.rx_chan_mod = 0;
    I2S0.conf.tx_slave_mod = 0;
    I2S0.conf.rx_slave_mod = 0;
    I2S0.conf.right_first = 1;
    I2S0.conf.msb_right = 1;
    I2S0.conf.tx_msb_shift = 1;
    I2S0.conf.rx_msb_shift = 1;
    I2S0.conf.bits_mod = 0;
    I2S0.conf.bck_div_num = bck_div;
    I2S0.conf.clkm_div_num = clkm_div;
    I2S0.conf.tx_start = 1;
}

esp_err_t esp8266_nodac_i2s_init(uint32_t silence_word,
                                 uint8_t bck_div, uint8_t clkm_div) {
    if (!bck_div || bck_div > 63U || !clkm_div || clkm_div > 63U)
        return ESP_ERR_INVALID_ARG;
    configure_descriptors(silence_word);
    configure_slc();
    configure_i2s(bck_div, clkm_div);
    const TickType_t timeout = pdMS_TO_TICKS(100);
    const TickType_t started = xTaskGetTickCount();
    while (!s_free_count && xTaskGetTickCount() - started < timeout)
        vTaskDelay(1);
    return s_free_count ? ESP_OK : ESP_ERR_TIMEOUT;
}

static bool acquire_free_buffer(TickType_t ticks_to_wait) {
    const TickType_t started = xTaskGetTickCount();
    TaskHandle_t current = xTaskGetCurrentTaskHandle();
    for (;;) {
        taskENTER_CRITICAL();
        if (s_free_count) {
            s_waiting = false;
            s_current_buffer = pop_free_buffer();
            s_current_position = 0;
            taskEXIT_CRITICAL();
            return true;
        }
        TickType_t elapsed = xTaskGetTickCount() - started;
        if (elapsed >= ticks_to_wait) {
            s_waiting = false;
            taskEXIT_CRITICAL();
            return false;
        }
        s_waiter = current;
        s_waiting = true;
        taskEXIT_CRITICAL();
#if YORADIO_ESP8266_AUDIO_PROFILE
        audio_profile_spi_wait_begin();
#elif YORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK
        audio_output_benchmark_spi_wait_begin();
#endif
        uint32_t notified = ulTaskNotifyTake(
            pdTRUE, ticks_to_wait - elapsed);
#if YORADIO_ESP8266_AUDIO_PROFILE
        audio_profile_spi_wait_end();
#elif YORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK
        audio_output_benchmark_spi_wait_end();
#endif
        if (!notified) {
            taskENTER_CRITICAL();
            s_waiting = false;
            taskEXIT_CRITICAL();
            return false;
        }
    }
}

esp_err_t esp8266_nodac_i2s_write(const uint32_t *words, size_t word_count,
                                  TickType_t ticks_to_wait) {
    if (!words && word_count) return ESP_ERR_INVALID_ARG;
    while (word_count) {
        if (!s_current_buffer ||
            s_current_position == NODAC_DMA_BUFFER_WORDS) {
            if (!acquire_free_buffer(ticks_to_wait)) return ESP_ERR_TIMEOUT;
        }
        size_t available = NODAC_DMA_BUFFER_WORDS - s_current_position;
        size_t count = word_count < available ? word_count : available;
        memcpy(s_current_buffer + s_current_position, words,
               count * sizeof(*words));
#if defined(YORADIO_ESP8266_AUDIO_TRACE)
        if (s_dma_trace_count < 4U && count) {
            const uint32_t *copied =
                s_current_buffer + s_current_position;
            unsigned ones = 0;
            uint32_t hash = 2166136261U;
            for (size_t index = 0; index < count; ++index) {
                ones += trace_popcount32(copied[index]);
                hash = (hash ^ copied[index]) * 16777619U;
            }
            ESP_LOGI(TAG,
                     "AUDIO_TRACE DMA-PDM copy=%u words=%u ones=%u/%u "
                     "fnv=%08x first=%08x,%08x,%08x,%08x",
                     s_dma_trace_count++, (unsigned)count, ones,
                     (unsigned)(count * 32U), (unsigned)hash, copied[0],
                     count > 1U ? copied[1] : 0U,
                     count > 2U ? copied[2] : 0U,
                     count > 3U ? copied[3] : 0U);
        }
#endif
        s_current_position += count;
        words += count;
        word_count -= count;
    }
    return ESP_OK;
}

void esp8266_nodac_i2s_silence(uint32_t silence_word) {
    taskENTER_CRITICAL();
    s_silence_word = silence_word;
    for (unsigned index = 0; index < NODAC_DMA_BUFFER_COUNT; ++index)
        for (unsigned word = 0; word < NODAC_DMA_BUFFER_WORDS; ++word)
            s_buffers[index][word] = silence_word;
    s_current_buffer = NULL;
    s_current_position = 0;
    taskEXIT_CRITICAL();
}

void esp8266_nodac_i2s_reset_underruns(void) {
    taskENTER_CRITICAL();
    s_underruns = 0;
    taskEXIT_CRITICAL();
}

uint32_t esp8266_nodac_i2s_underruns(void) {
    taskENTER_CRITICAL();
    uint32_t underruns = s_underruns;
    taskEXIT_CRITICAL();
    return underruns;
}
