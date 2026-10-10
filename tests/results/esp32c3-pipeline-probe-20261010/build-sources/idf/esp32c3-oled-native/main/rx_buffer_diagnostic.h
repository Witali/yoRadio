#pragma once
#include "sdkconfig.h"
#ifdef CONFIG_YORADIO_RX_BUFFER_DIAGNOSTICS
// Called only between decoder calls, including while the decoder is idle.
void rx_buffer_diagnostic_poll(void);
#else
static inline void rx_buffer_diagnostic_poll(void) {}
#endif
