#pragma once
#include "sdkconfig.h"

#ifdef CONFIG_YORADIO_NETWORK_HEAP_PROFILE
// Called only by the existing HTTP profiler, after lwIP/web startup.
void network_heap_profile_poll(void);
#else
static inline void network_heap_profile_poll(void) {}
#endif
