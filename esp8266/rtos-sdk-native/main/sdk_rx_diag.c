#include "sdk_rx_diag.h"

#if YORADIO_ESP8266_SDK_RX_DIAG
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

typedef char sdk_rx_diag_is_32_bytes[(sizeof(sdk_rx_diag_snapshot_t) == 32) ? 1 : -1];
static sdk_rx_diag_snapshot_t s_sdk_rx_diag;

/* These SDK callbacks run in task context. The ESP8266 port critical section
 * masks interrupts without allocating or blocking. Do not use SYS_ARCH_PROTECT:
 * this SDK implements it with a lazily allocated mutex. No external call or
 * pbuf operation belongs inside any of these short critical sections. */
void sdk_rx_diag_count(sdk_rx_diag_event_t event)
{
    taskENTER_CRITICAL();
    switch (event) {
    case SDK_RX_DIAG_CUSTOM_FAIL: ++s_sdk_rx_diag.rx_custom_fail; break;
    case SDK_RX_DIAG_ENQUEUE_NOMEM: ++s_sdk_rx_diag.rx_enqueue_nomem; break;
    case SDK_RX_DIAG_ENQUEUE_FULL: ++s_sdk_rx_diag.rx_enqueue_full; break;
    case SDK_RX_DIAG_TX_TRANSFORM_FAIL: ++s_sdk_rx_diag.tx_transform_fail; break;
    case SDK_RX_DIAG_TX_DRIVER_FAIL: ++s_sdk_rx_diag.tx_driver_fail; break;
    default: break;
    }
    taskEXIT_CRITICAL();
}

void sdk_rx_diag_custom_acquire(void)
{
    taskENTER_CRITICAL();
    ++s_sdk_rx_diag.rx_custom_total;
    ++s_sdk_rx_diag.rx_custom_live;
    if (s_sdk_rx_diag.rx_custom_live > s_sdk_rx_diag.rx_custom_peak)
        s_sdk_rx_diag.rx_custom_peak = s_sdk_rx_diag.rx_custom_live;
    taskEXIT_CRITICAL();
}

void sdk_rx_diag_custom_release(void)
{
    taskENTER_CRITICAL();
    --s_sdk_rx_diag.rx_custom_live;
    taskEXIT_CRITICAL();
}

void sdk_rx_diag_snapshot(sdk_rx_diag_snapshot_t *out)
{
    if (!out) return;
    taskENTER_CRITICAL();
    *out = s_sdk_rx_diag;
    taskEXIT_CRITICAL();
}
#endif
