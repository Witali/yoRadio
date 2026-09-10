#pragma once

#include <stddef.h>
#include <stdint.h>

#include "esp_err.h"

typedef struct {
    uint32_t chained_transfers;
    uint32_t gap_cycles_total;
    uint32_t gap_cycles_max;
    uint32_t queue_empty_events;
} native_audio_output_spi_stats_t;

esp_err_t native_audio_output_init(void);
esp_err_t native_audio_output_write(int16_t *samples, size_t sample_count,
                                    uint32_t sample_rate, uint8_t channels);
void native_audio_output_silence(void);
void native_audio_output_reload_settings(void);
void native_audio_output_reset_normalizer(void);
uint8_t native_audio_output_volume(void);
void native_audio_output_set_volume_runtime(uint8_t volume);
void native_audio_output_set_balance_runtime(int8_t balance);
void native_audio_output_reset_spi_stats(void);
void native_audio_output_get_spi_stats(native_audio_output_spi_stats_t *stats);
#if YORADIO_ESP8266_OPUS_BENCHMARK_OUTPUT
/* Latched hardware FIFO-empty flag. Clear only at the start of a window;
 * subsequent reads never clear it, so no event is lost between samples. */
uint32_t native_audio_output_fifo_empty(unsigned clear);
#endif
