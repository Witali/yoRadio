#pragma once

#include "sdkconfig.h"

// Wemos D1 mini HSPI PDM profile. GPIO13/D7 is the filtered audio output;
// GPIO14/D5 carries the SPI clock and is not part of the analogue path.
#define BOARD_SPI_PDM_DATA_GPIO 13
#define BOARD_SPI_PDM_CLOCK_GPIO 14
#define BOARD_SPI_PDM_SAMPLE_RATE 48000U

#if CONFIG_YORADIO_SPI_PDM_OVERSAMPLE_8
#define BOARD_SPI_PDM_OVERSAMPLE 8U
#define BOARD_SPI_PDM_BIT_RATE_HZ 384615U
#define BOARD_SPI_PDM_CLOCK_PREDIV 25U
#elif CONFIG_YORADIO_SPI_PDM_OVERSAMPLE_16
#define BOARD_SPI_PDM_OVERSAMPLE 16U
#define BOARD_SPI_PDM_BIT_RATE_HZ 769231U
#define BOARD_SPI_PDM_CLOCK_PREDIV 12U
#else
#error "Select an ESP8266 SPI-PDM oversampling ratio"
#endif

// Production runs 32 genuine PDM decisions at nominally 1.536 MHz. The
// experimental PDM128 mode raises the carrier to 6.144 MHz. Integer divider
// values produce 1.538462/6.153846 MHz, both +0.16% from nominal.
#define BOARD_I2S_PDM_SAMPLE_RATE 48000U
#if CONFIG_YORADIO_I2S_PDM_OVERSAMPLE_32 || CONFIG_YORADIO_AUDIO_OUTPUT_I2S_RCPDM || !CONFIG_YORADIO_AUDIO_OUTPUT_I2S_PDM
// I2S RCPDM always uses 32 bits, independently of the delta-sigma choice.
// SPI/standard PCM do not expose the PDM choice; these unused defaults keep
// their builds independent of hidden Kconfig values.
#define BOARD_I2S_PDM_OVERSAMPLE 32U
#define BOARD_I2S_PDM_CARRIER_BITS_PER_SAMPLE 32U
#define BOARD_I2S_PDM_BCK_DIV 8U
#define BOARD_I2S_PDM_CLKM_DIV 13U
#elif CONFIG_YORADIO_I2S_PDM_OVERSAMPLE_128
#define BOARD_I2S_PDM_OVERSAMPLE 128U
#define BOARD_I2S_PDM_CARRIER_BITS_PER_SAMPLE 128U
#define BOARD_I2S_PDM_BCK_DIV 2U
#define BOARD_I2S_PDM_CLKM_DIV 13U
#else
#error "Select an ESP8266 I2S-PDM oversampling ratio"
#endif
#define BOARD_I2S_PDM_REPEAT \
    (BOARD_I2S_PDM_CARRIER_BITS_PER_SAMPLE / BOARD_I2S_PDM_OVERSAMPLE)
#define BOARD_I2S_PDM_WORDS_PER_SAMPLE \
    (BOARD_I2S_PDM_CARRIER_BITS_PER_SAMPLE / 32U)
#define BOARD_I2S_PDM_NOMINAL_HZ \
    (BOARD_I2S_PDM_SAMPLE_RATE * BOARD_I2S_PDM_CARRIER_BITS_PER_SAMPLE)
#define BOARD_I2S_PDM_EFFECTIVE_HZ \
    (BOARD_I2S_PDM_SAMPLE_RATE * BOARD_I2S_PDM_OVERSAMPLE)
#define BOARD_I2S_PDM_CARRIER_HZ \
    (160000000U / BOARD_I2S_PDM_BCK_DIV / BOARD_I2S_PDM_CLKM_DIV)
