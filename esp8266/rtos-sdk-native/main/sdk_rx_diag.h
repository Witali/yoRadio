#pragma once

#include <stdint.h>

#ifndef YORADIO_ESP8266_SDK_RX_DIAG
#define YORADIO_ESP8266_SDK_RX_DIAG 0
#endif

#ifdef __cplusplus
extern "C" {
#endif

/* Diagnostic lifetime counters, modulo 2^32. Exactly 32 bytes of backing RAM.
 * custom_live/peak count software custom pbuf wrappers, NOT all Wi-Fi RX
 * descriptors. Drops inside the closed Wi-Fi driver are not observable here.
 * Do not reset these counters on reconnect: RX callbacks may still own pbufs.
 * Compare snapshots instead. transform_fail also includes rejected IRAM pbufs,
 * and custom_fail includes pbuf setup failure, not only malloc failure. */
typedef struct {
    uint32_t rx_custom_fail;
    uint32_t rx_enqueue_nomem;
    uint32_t rx_enqueue_full;
    uint32_t tx_transform_fail;
    uint32_t tx_driver_fail;
    uint32_t rx_custom_live;
    uint32_t rx_custom_peak;
    uint32_t rx_custom_total;
} sdk_rx_diag_snapshot_t;

typedef enum {
    SDK_RX_DIAG_CUSTOM_FAIL,
    SDK_RX_DIAG_ENQUEUE_NOMEM,
    SDK_RX_DIAG_ENQUEUE_FULL,
    SDK_RX_DIAG_TX_TRANSFORM_FAIL,
    SDK_RX_DIAG_TX_DRIVER_FAIL
} sdk_rx_diag_event_t;

#if YORADIO_ESP8266_SDK_RX_DIAG
void sdk_rx_diag_count(sdk_rx_diag_event_t event);
void sdk_rx_diag_custom_acquire(void);
void sdk_rx_diag_custom_release(void);
/* All eight words form one consistent snapshot; NULL is ignored. */
void sdk_rx_diag_snapshot(sdk_rx_diag_snapshot_t *out);
#endif

#ifdef __cplusplus
}
#endif
