#pragma once
#include <stdbool.h>
#include "sdkconfig.h"
#ifdef CONFIG_YORADIO_HEAP_FRAGMENT_PROBE
void heap_fragment_probe_poll(bool idle);
#else
static inline void heap_fragment_probe_poll(bool idle) { (void)idle; }
#endif
