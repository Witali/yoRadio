#pragma once
#include "aac_sbr_abi.h"

// QEMU-only candidate. Native QMF working rows stay int32; only the six
// inter-frame high-band rows use packed complex storage. The prefix remains
// binary compatible with every envelope/header reader in the pinned archive.
enum { AAC_HIGH_ROWS=6, AAC_HIGH_BANDS=48, AAC_HIGH_PAIRS=AAC_HIGH_ROWS*AAC_HIGH_BANDS,
       AAC_HIGH_NEW_ROWS=32 };
enum { AAC_LOW_HISTORY_ROWS=8, AAC_LOW_NEW_ROWS=32, AAC_LOW_BANDS=32,
       AAC_LOW_ROWS=AAC_LOW_HISTORY_ROWS+AAC_LOW_NEW_ROWS };
#ifdef AAC_SMOOTHING_HISTORY_FOUR
enum { AAC_SMOOTHING_PERSISTENT_ROWS=AAC_SBR_ROWS-1 };
#else
enum { AAC_SMOOTHING_PERSISTENT_ROWS=AAC_SBR_ROWS };
#endif
#ifdef AAC_HIGH_HISTORY_PC16
enum { AAC_HIGH_METADATA_PER_WORD=8 };
#else
enum { AAC_HIGH_METADATA_PER_WORD=4 };
#endif
typedef struct {
    uint32_t mantissas[AAC_HIGH_PAIRS];
    uint32_t metadata[AAC_HIGH_PAIRS/AAC_HIGH_METADATA_PER_WORD];
} aac_high_history_t;

typedef struct AAC_ABI_VIEW {
    uint8_t frame_control[0xc0];
    aac_sbr_header_abi_t header;
    uint8_t domain_and_inverse_filter[0x78];
    int32_t coupling;
    uint8_t harmonics_and_envelopes[0x70c-0x17c];
    int32_t startup;
    uint8_t envelope_and_noise[0x1158-0x710];
    int32_t previous_noise[10], bandwidth[6], previous_bandwidth[6];
    int32_t low_real[AAC_LOW_ROWS][AAC_LOW_BANDS], low_imag[AAC_LOW_ROWS][AAC_LOW_BANDS];
    int32_t *high_imag, *high_real;
    aac_high_history_t high_history;
    int16_t synthesis[1152];
    int32_t alias_degree[64];
    int32_t gain_mantissa[AAC_SMOOTHING_PERSISTENT_ROWS][AAC_SBR_BANDS];
    int32_t noise_mantissa[AAC_SMOOTHING_PERSISTENT_ROWS][AAC_SBR_BANDS];
    int32_t gain_exponent[AAC_SMOOTHING_PERSISTENT_ROWS][AAC_SBR_BANDS];
    int32_t noise_exponent[AAC_SMOOTHING_PERSISTENT_ROWS][AAC_SBR_BANDS];
} aac_high_frame_t;

typedef union AAC_ABI_VIEW {
    struct {
        int32_t frame_size, sync_state;
        aac_high_frame_t frame;
        int32_t *smoothing[4][AAC_SBR_ROWS];
    };
    aac_sbr_ps_overlay_abi_t ps_overlay;
    aac_sbr_packed_ps_overlay_abi_t packed_ps;
} aac_high_channel_t;
typedef struct AAC_ABI_VIEW {
    aac_high_channel_t channel[AAC_SBR_CHANNELS];
    int32_t initialize_ps;
    aac_ps_abi_t *ps;
    aac_ps_abi_t embedded_ps;
} aac_high_full_owner_t;
typedef struct AAC_ABI_VIEW {
    aac_high_channel_t channel[AAC_SBR_CHANNELS];
    int32_t initialize_ps;
    aac_ps_abi_t *ps;
    int32_t inactive_ps;
} aac_high_owner_t;

_Static_assert(offsetof(aac_high_frame_t,high_imag)==offsetof(aac_sbr_frame_abi_t,high_imag),
               "Every prefix reader must retain its original ABI");
_Static_assert(sizeof(aac_sbr_ps_overlay_abi_t)<=offsetof(aac_high_channel_t,frame.synthesis),
               "Relocated PS must not overlap either synthesis history");
_Static_assert(offsetof(aac_high_owner_t,inactive_ps)==offsetof(aac_high_full_owner_t,embedded_ps),
               "Inactive PS detection word must match the native tail cursor");
