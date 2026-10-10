#pragma once
#include "sdkconfig.h"

#ifdef CONFIG_YORADIO_NETWORK_HEAP_PROFILE
// One caller after lwIP/web startup: CPU profiler, or the WebSocket task when
// the independent WebUI TCP diagnostic is enabled.
void network_heap_profile_poll(void);
#else
static inline void network_heap_profile_poll(void) {}
#endif
