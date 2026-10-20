#pragma once
#ifndef _POSIX_C_SOURCE
#define _POSIX_C_SOURCE 200809L
#endif
#include <pthread.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define CHECK(value, marker) do { if (!(value)) { \
    fprintf(stderr, "SEMANTIC_FAILURE:%s:%u\n", marker, __LINE__); exit(80); \
} } while (0)
/* ESP-IDF esp_err.h values, shared by both production translation units. */
typedef int esp_err_t;
#define ESP_OK 0
#define ESP_FAIL (-1)
#define ESP_ERR_NO_MEM 0x101
#define ESP_ERR_INVALID_ARG 0x102
#define ESP_ERR_INVALID_STATE 0x103
#define ESP_ERR_NOT_SUPPORTED 0x106
#define ESP_ERR_TIMEOUT 0x107
#define IRAM_ATTR
#define DRAM_ATTR
#define ESP_RETURN_ON_ERROR(expr, ...) do { esp_err_t e_=(expr); if(e_!=ESP_OK) return e_; } while(0)
#define ESP_LOGI(...) ((void)0)
#define ESP_LOGW(...) ((void)0)
#define pdMS_TO_TICKS(value) (value)

typedef pthread_mutex_t portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED PTHREAD_MUTEX_INITIALIZER
extern _Thread_local unsigned critical_depth;
extern _Thread_local bool in_isr;
static inline void enter(portMUX_TYPE *lock, bool isr) {
    CHECK(isr==in_isr && !critical_depth, "critical_context");
    CHECK(!pthread_mutex_lock(lock), "lock_enter"); ++critical_depth;
}
static inline void leave(portMUX_TYPE *lock, bool isr) {
    CHECK(isr==in_isr && critical_depth==1, "critical_balance");
    --critical_depth; CHECK(!pthread_mutex_unlock(lock), "lock_leave");
}
#define portENTER_CRITICAL(lock) enter(lock, false)
#define portEXIT_CRITICAL(lock) leave(lock, false)
#define portENTER_CRITICAL_ISR(lock) enter(lock, true)
#define portEXIT_CRITICAL_ISR(lock) leave(lock, true)
int64_t esp_timer_get_time(void);
static inline const char *esp_err_to_name(esp_err_t value) { (void)value; return "host seam"; }

#define GPIO_NUM_0 0
#define GPIO_NUM_2 2
#define GPIO_NUM_12 12
#define GPIO_NUM_13 13
#define GPIO_NUM_14 14
#define GPIO_NUM_15 15
#define GPIO_NUM_21 21
#define GPIO_NUM_25 25
#define GPIO_NUM_26 26
#define GPIO_NUM_32 32
#define GPIO_NUM_33 33
#define GPIO_NUM_39 39
#define GPIO_MODE_OUTPUT 1
void gpio_reset_pin(int pin);
void gpio_set_direction(int pin, int mode);
void gpio_set_level(int pin, int level);
void vTaskDelay(unsigned ticks);

bool native_audio_settings_get_normalization(void);
uint8_t native_audio_settings_get_normalization_gain_db(void);
int8_t native_audio_settings_get_normalization_target_dbfs(void);
uint16_t native_audio_settings_get_normalization_time_ms(void);
uint8_t native_audio_settings_get_volume(void);
int8_t native_audio_settings_get_balance(void);
esp_err_t native_audio_settings_set_volume(uint8_t value);
esp_err_t native_audio_settings_set_balance(int8_t value);
void native_audio_normalizer_configure(bool, uint8_t, int8_t, uint16_t, uint32_t);
void native_audio_normalizer_reset(void);
void native_audio_normalizer_process_block(int16_t *, size_t, uint8_t);

typedef void *i2s_chan_handle_t;
typedef struct { unsigned size; } i2s_event_data_t;
typedef bool (*i2s_callback_t)(i2s_chan_handle_t, i2s_event_data_t *, void *);
typedef struct { i2s_callback_t on_sent, on_send_q_ovf, on_recv, on_recv_q_ovf; } i2s_event_callbacks_t;
typedef struct {
    int id, role; unsigned dma_desc_num, dma_frame_num;
    bool auto_clear_after_cb, auto_clear_before_cb;
} i2s_chan_config_t;
typedef struct { uint32_t sample_rate_hz; } pdm_clock_t;
typedef struct { unsigned data_bit_width; int slot_mode; } pdm_slot_t;
typedef struct {
    pdm_clock_t clk_cfg; pdm_slot_t slot_cfg;
    struct { int clk, dout; struct { bool clk_inv; } invert_flags; } gpio_cfg;
} i2s_pdm_tx_config_t;
typedef struct { unsigned bclk_hz; } i2s_chan_info_t;
enum { I2S_NUM_0=0, I2S_ROLE_MASTER=1, I2S_GPIO_UNUSED=-1,
       I2S_SLOT_MODE_MONO=1, I2S_DATA_BIT_WIDTH_16BIT=16 };
#define I2S_CHANNEL_DEFAULT_CONFIG(port,mode) ((i2s_chan_config_t){.id=(port),.role=(mode)})
#define I2S_PDM_TX_CLK_DAC_DEFAULT_CONFIG(rate) ((pdm_clock_t){.sample_rate_hz=(rate)})
#define I2S_PDM_TX_SLOT_DEFAULT_CONFIG(bits,mode) ((pdm_slot_t){.data_bit_width=(bits),.slot_mode=(mode)})
esp_err_t i2s_new_channel(const i2s_chan_config_t *, i2s_chan_handle_t *, void *);
esp_err_t i2s_channel_init_pdm_tx_mode(i2s_chan_handle_t, const i2s_pdm_tx_config_t *);
esp_err_t i2s_channel_register_event_callback(i2s_chan_handle_t, const i2s_event_callbacks_t *, void *);
esp_err_t i2s_channel_preload_data(i2s_chan_handle_t, const void *, size_t, size_t *);
esp_err_t i2s_channel_enable(i2s_chan_handle_t);
esp_err_t i2s_channel_disable(i2s_chan_handle_t);
esp_err_t i2s_del_channel(i2s_chan_handle_t);
esp_err_t i2s_channel_get_info(i2s_chan_handle_t, i2s_chan_info_t *);
esp_err_t i2s_channel_write(i2s_chan_handle_t, const void *, size_t, size_t *, unsigned);

typedef void *dac_continuous_handle_t;
typedef struct { unsigned chan_mask, desc_num, buf_size, freq_hz; int offset, clk_src, chan_mode; } dac_continuous_config_t;
enum { DAC_CHANNEL_MASK_CH1=1, DAC_DIGI_CLK_SRC_APLL=2, DAC_CHANNEL_MODE_SIMUL=3 };
esp_err_t dac_continuous_new_channels(const dac_continuous_config_t *, dac_continuous_handle_t *);
esp_err_t dac_continuous_enable(dac_continuous_handle_t);
esp_err_t dac_continuous_disable(dac_continuous_handle_t);
esp_err_t dac_continuous_del_channels(dac_continuous_handle_t);
esp_err_t dac_continuous_write(dac_continuous_handle_t, const void *, size_t, size_t *, int);

typedef struct {
    unsigned mode, sample_rate, bits_per_sample, channel_format, communication_format,
        intr_alloc_flags, dma_buf_count, dma_buf_len;
    bool use_apll, tx_desc_auto_clear; int fixed_mclk;
} i2s_config_t;
enum { I2S_MODE_MASTER=1, I2S_MODE_TX=2, I2S_MODE_DAC_BUILT_IN=4,
       I2S_BITS_PER_SAMPLE_16BIT=16, I2S_CHANNEL_FMT_RIGHT_LEFT=17,
       I2S_COMM_FORMAT_STAND_MSB=18, ESP_INTR_FLAG_LEVEL1=19,
       I2S_PIN_NO_CHANGE=-1, I2S_DAC_CHANNEL_LEFT_EN=20 };
esp_err_t idf6_dac_output_configure(const i2s_config_t *, int);
esp_err_t idf6_dac_output_begin(void);
esp_err_t idf6_dac_output_end(void);
esp_err_t idf6_dac_output_set_sample_rate(unsigned);
esp_err_t idf6_dac_output_write(const void *, size_t, size_t *, unsigned);
