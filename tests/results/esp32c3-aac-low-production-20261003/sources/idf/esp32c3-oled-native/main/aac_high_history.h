#pragma once
#include "sdkconfig.h"
#ifdef CONFIG_YORADIO_QEMU_AAC_HIGH_HISTORY_PC16
#define AAC_HIGH_HISTORY_PC16 1
#endif
#include "aac_high_history_abi.h"
#include <stdbool.h>

// Per-decoder call state. Numerical probe counters are absent from production.
typedef struct {
    aac_high_frame_t *frame;
    bool real_only;
    unsigned call_loads, call_stores;
#ifdef CONFIG_YORADIO_QEMU_AAC_HIGH_HISTORY_TEST
    unsigned loads, stores, complex_frames, real_frames;
    unsigned changed, saturations, max_shift;
#endif
} aac_high_runtime_t;

void aac_high_history_reset_counters(void);
void aac_high_history_report(const char *,unsigned,unsigned);
void aac_high_history_clear(aac_high_frame_t *,bool);
