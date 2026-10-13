#pragma once
#include "sdkconfig.h"
#include <stdint.h>

enum { WEB_TCP_PROBE_PORT = 80 };
typedef enum {
    WEB_TCP_WIFI_CONNECTED = 1,
    WEB_TCP_WIFI_DISCONNECTED = 2,
    WEB_TCP_WIFI_GOT_IP = 3,
} web_tcp_wifi_event_t;

#ifdef CONFIG_YORADIO_WEB_TCP_PROBE
// Single consumer: existing WebSocket status task, independent of HTTP requests.
void web_tcp_probe_poll(void);
// Record only an event code/reason; never retain SSID, addresses or credentials.
void web_tcp_probe_record_wifi(web_tcp_wifi_event_t event, uint16_t reason);
void web_tcp_probe_log_listener(uint32_t sequence, uint32_t age_ms,
                                uint32_t syn_received, uint32_t established,
                                uint32_t listeners, uint32_t backlog,
                                uint32_t pending, uint32_t backlog_supported);
#else
static inline void web_tcp_probe_poll(void) {}
static inline void web_tcp_probe_record_wifi(web_tcp_wifi_event_t event,
                                             uint16_t reason) {
    (void)event;
    (void)reason;
}
#endif
