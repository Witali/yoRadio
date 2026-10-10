#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "driver/i2s_common.h"
#include "sdkconfig.h"

#ifdef CONFIG_YORADIO_PIPELINE_PROFILE
#include "pipeline_wait.h"
// Read/reset only in the output task, outside a fill call.
pipeline_wait_t native_i2s_take_wait_profile(void);
#endif

// Runs in the output task, under the driver's write lock, never in an ISR.
// Fill exactly `frames` stereo s16 frames. Do not block, allocate, or decode
// compressed audio here. The pointer is valid only for this callback.
typedef void (*native_i2s_fill_t)(void *context, int16_t *dma, size_t frames);
esp_err_t native_i2s_write_generated(i2s_chan_handle_t channel, size_t frames,
    native_i2s_fill_t fill, void *context, bool preload, size_t *written);
// Acquire a fresh descriptor and fill it completely in one callback. Audio
// packets must be gathered before this call; never wait for input inside fill.
esp_err_t native_i2s_write_full_block(i2s_chan_handle_t channel,
    native_i2s_fill_t fill, void *context);
