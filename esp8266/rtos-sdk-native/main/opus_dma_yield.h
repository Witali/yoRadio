#pragma once

#include <stdbool.h>
#include <stdint.h>

#ifndef YORADIO_ESP8266_OPUS_DMA_YIELD
#define YORADIO_ESP8266_OPUS_DMA_YIELD 0
#endif

/* Single audio-task owner. A notification which returns in the same tick is
 * not evidence of time given back to the scheduler. Timeout also cannot earn
 * a yield credit. Unsigned subtraction handles the FreeRTOS tick rollover. */
static inline uint32_t opus_dma_wait_credit(uint32_t start, uint32_t end,
                                           uint32_t notified) {
    return notified ? end - start : 0U;
}

static inline bool opus_dma_needs_frame_delay(bool opus, uint32_t before,
                                             uint32_t after) {
    return !opus || before == after;
}

#if YORADIO_ESP8266_OPUS_DMA_YIELD
/* Only the audio producer calls this; ISR never touches the counter. */
uint32_t esp8266_nodac_i2s_wait_ticks(void);
#endif
