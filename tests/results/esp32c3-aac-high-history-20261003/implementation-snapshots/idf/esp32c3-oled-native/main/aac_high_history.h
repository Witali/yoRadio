#pragma once
#include "sdkconfig.h"
#ifdef CONFIG_YORADIO_QEMU_AAC_HIGH_HISTORY_PC16
#define AAC_HIGH_HISTORY_PC16 1
#endif
#include "aac_high_history_abi.h"
#include <stdbool.h>

void aac_high_history_reset_counters(void);
void aac_high_history_report(const char *,unsigned,unsigned);
void aac_high_history_clear(aac_high_frame_t *,bool);
