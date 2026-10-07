#pragma once
#include "sdkconfig.h"
#ifdef CONFIG_YORADIO_RX_COPY_PROFILE
void rx_copy_profile_poll(void);
#else
static inline void rx_copy_profile_poll(void) {}
#endif
