#pragma once
#include "sdkconfig.h"

enum { WEB_TCP_PROBE_PORT = 80 };

#ifdef CONFIG_YORADIO_WEB_TCP_PROBE
// Single consumer: existing WebSocket status task, independent of HTTP requests.
void web_tcp_probe_poll(void);
#else
static inline void web_tcp_probe_poll(void) {}
#endif
