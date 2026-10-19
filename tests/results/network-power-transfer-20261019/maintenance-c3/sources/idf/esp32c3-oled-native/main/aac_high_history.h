#pragma once
#include "sdkconfig.h"
#ifdef CONFIG_YORADIO_QEMU_AAC_HIGH_HISTORY_PC16
#define AAC_HIGH_HISTORY_PC16 1
#endif
#if defined(CONFIG_YORADIO_QEMU_AAC_HIGH_HISTORY_PC19) || defined(CONFIG_YORADIO_AAC_HIGH_HISTORY_PC19)
#define AAC_HIGH_HISTORY_PC19 1
#endif
#ifdef CONFIG_YORADIO_AAC_HIGH_HISTORY_PC19
#define AAC_HIGH_HISTORY_PC19_SIDECAR 1
#endif
#if defined(AAC_HIGH_HISTORY_PC16) && defined(AAC_HIGH_HISTORY_PC19)
#error "Select only one high-QMF storage format"
#endif
#include "aac_high_history_abi.h"
#include <stdbool.h>

// Per-decoder call state. Numerical probe counters are absent from production.
typedef struct {
    aac_high_frame_t *frame;
    bool real_only;
#ifdef AAC_HIGH_HISTORY_PC19_SIDECAR
    uint8_t pc19_channel; // Fits the existing alignment gap; selected once per call.
#endif
    unsigned call_loads, call_stores;
#ifdef AAC_HIGH_HISTORY_PC19_SIDECAR
    uint32_t pc19_extra[AAC_SBR_CHANNELS][AAC_HIGH_SIDE_METADATA_WORDS];
#endif
#ifdef CONFIG_YORADIO_QEMU_AAC_HIGH_HISTORY_TEST
    unsigned loads, stores, complex_frames, real_frames;
    unsigned changed, saturations, max_shift;
#endif
} aac_high_runtime_t;

void aac_high_history_reset_counters(void);
void aac_high_history_report(const char *,unsigned,unsigned);
void aac_high_history_clear(aac_high_frame_t *,bool);
