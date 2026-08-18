#pragma once

// ESP-IDF 6 removed the legacy built-in-DAC I2S path. Keep the same adapter
// API as the existing esp32-cyd2usb-minimal firmware so native code can select
// either the supported DAC driver or the vendored IDF 5.5 implementation.

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "esp_err.h"
#include "freertos/FreeRTOS.h"

#if defined(YORADIO_DAC_BACKEND_LEGACY)
#include "driver/i2s.h"
#else

typedef int i2s_port_t;
typedef int i2s_mode_t;
typedef int i2s_bits_per_sample_t;
typedef int i2s_channel_fmt_t;
typedef int i2s_comm_format_t;
typedef int i2s_dac_mode_t;

#define I2S_NUM_0 0
#define I2S_NUM_1 1
#define I2S_PIN_NO_CHANGE (-1)
#define I2S_MODE_MASTER (1 << 0)
#define I2S_MODE_TX (1 << 1)
#define I2S_MODE_DAC_BUILT_IN (1 << 2)
#define I2S_BITS_PER_SAMPLE_16BIT 16
#define I2S_CHANNEL_FMT_RIGHT_LEFT 0
#define I2S_COMM_FORMAT_STAND_I2S 0
#define I2S_COMM_FORMAT_STAND_MSB 1
#define I2S_COMM_FORMAT_I2S 0
#define I2S_COMM_FORMAT_I2S_MSB 1
#define I2S_COMM_FORMAT_I2S_LSB 2
#define I2S_DAC_CHANNEL_DISABLE 0
#define I2S_DAC_CHANNEL_RIGHT_EN 1
#define I2S_DAC_CHANNEL_LEFT_EN 2
#define I2S_DAC_CHANNEL_BOTH_EN 3

typedef struct {
    i2s_mode_t mode;
    uint32_t sample_rate;
    i2s_bits_per_sample_t bits_per_sample;
    i2s_channel_fmt_t channel_format;
    i2s_comm_format_t communication_format;
    int intr_alloc_flags;
    int dma_buf_count;
    int dma_buf_len;
    bool use_apll;
    bool tx_desc_auto_clear;
    int fixed_mclk;
} i2s_config_t;

typedef struct {
    int bck_io_num;
    int ws_io_num;
    int data_out_num;
    int data_in_num;
    int mck_io_num;
} i2s_pin_config_t;
#endif

#ifdef __cplusplus
extern "C" {
#endif

esp_err_t idf6_dac_output_configure(const i2s_config_t *config,
                                    i2s_dac_mode_t mode);
esp_err_t idf6_dac_output_begin(void);
esp_err_t idf6_dac_output_end(void);
esp_err_t idf6_dac_output_start(void);
esp_err_t idf6_dac_output_stop(void);
esp_err_t idf6_dac_output_clear(void);
esp_err_t idf6_dac_output_set_sample_rate(uint32_t sample_rate);
esp_err_t idf6_dac_output_write(const void *source, size_t size,
                                size_t *bytes_written,
                                TickType_t timeout_ticks);

#ifdef __cplusplus
}
#endif
