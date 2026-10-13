#pragma once
#include <stddef.h>
#include "esp_err.h"
enum
{
    SPI2_HOST = 2,
    SPI_DMA_CH_AUTO = 3
};
typedef void *spi_device_handle_t;
typedef struct
{
    int mosi_io_num, miso_io_num, sclk_io_num, quadwp_io_num, quadhd_io_num;
    size_t max_transfer_sz;
} spi_bus_config_t;
typedef struct
{
    int clock_speed_hz, mode, spics_io_num, queue_size;
} spi_device_interface_config_t;
typedef struct
{
    size_t length;
    const void *tx_buffer;
} spi_transaction_t;
esp_err_t spi_bus_initialize(int host, const spi_bus_config_t *config, int dma);
esp_err_t spi_bus_add_device(int host, const spi_device_interface_config_t *config,
                             spi_device_handle_t *device);
esp_err_t spi_device_polling_transmit(spi_device_handle_t device, spi_transaction_t *transaction);
