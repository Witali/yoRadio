#pragma once
#include "aac_sbr_abi.h"
#include <assert.h>

// QEMU-only candidate. Native QMF working rows stay int32; only the six
// inter-frame high-band rows use packed complex storage. The prefix remains
// binary compatible with every envelope/header reader in the pinned archive.
enum { AAC_HIGH_ROWS=6, AAC_HIGH_BANDS=48, AAC_HIGH_PAIRS=AAC_HIGH_ROWS*AAC_HIGH_BANDS,
       AAC_HIGH_NEW_ROWS=32 };
enum { AAC_LOW_HISTORY_ROWS=8, AAC_LOW_NEW_ROWS=32, AAC_LOW_BANDS=32,
       AAC_LOW_ROWS=AAC_LOW_HISTORY_ROWS+AAC_LOW_NEW_ROWS };
#ifdef AAC_LOW_WORKSPACE
enum { AAC_LOW_STORED_ROWS=AAC_LOW_HISTORY_ROWS };
#else
enum { AAC_LOW_STORED_ROWS=AAC_LOW_ROWS };
#endif
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
    int32_t low_real[AAC_LOW_STORED_ROWS][AAC_LOW_BANDS], low_imag[AAC_LOW_STORED_ROWS][AAC_LOW_BANDS];
    int32_t *high_imag, *high_real;
    aac_high_history_t high_history;
    int16_t synthesis[1152];
    int32_t alias_degree[64];
    int32_t gain_mantissa[AAC_SMOOTHING_PERSISTENT_ROWS][AAC_SBR_BANDS];
    int32_t noise_mantissa[AAC_SMOOTHING_PERSISTENT_ROWS][AAC_SBR_BANDS];
    int32_t gain_exponent[AAC_SMOOTHING_PERSISTENT_ROWS][AAC_SBR_BANDS];
    int32_t noise_exponent[AAC_SMOOTHING_PERSISTENT_ROWS][AAC_SBR_BANDS];
} aac_high_frame_t;

#ifdef AAC_ASYMMETRIC_OWNER
// Both channels have identical native frame-relative table addresses. Only
// the right channel reserves PS overlay/synthesis storage after this prefix.
#define AAC_HIGH_PREFIX \
    int32_t frame_size, sync_state; \
    uint32_t low_real_relative, low_imag_relative; \
    int32_t *smoothing[4][AAC_SBR_ROWS]
typedef struct AAC_ABI_VIEW {
    AAC_HIGH_PREFIX;
    aac_high_frame_t frame;
} aac_high_channel_view_t;
typedef struct AAC_ABI_VIEW {
    AAC_HIGH_PREFIX;
    union {
        aac_high_frame_t frame;
        struct { aac_sbr_ps_overlay_abi_t ps_overlay; int16_t ps_synthesis[1152]; };
        aac_sbr_packed_ps_overlay_abi_t packed_ps;
    };
} aac_high_channel_t;
#undef AAC_HIGH_PREFIX
#define AAC_HIGH_OWNER_CHANNELS aac_high_channel_view_t left; aac_high_channel_t right
#define AAC_HIGH_RIGHT_MEMBER(member) right.member
_Static_assert(offsetof(aac_high_channel_view_t,frame)==offsetof(aac_high_channel_t,frame),
               "Both channels need identical frame-relative prefixes");
_Static_assert(offsetof(aac_high_channel_t,ps_overlay)==offsetof(aac_high_channel_t,frame),
               "Right PS reuses the inactive frame, never the pointer prefix");
#elif defined(AAC_LOW_WORKSPACE)
typedef struct AAC_ABI_VIEW {
    union {
        struct {
            int32_t frame_size, sync_state;
            // RV32 frame-relative addresses, valid only during sbr_dec.
            // Kept immediately before frame so every native low-base setup
            // becomes a single signed-offset load, without adding a call.
            uint32_t low_real_relative, low_imag_relative;
            aac_high_frame_t frame;
        };
        struct {
            aac_sbr_ps_overlay_abi_t ps_overlay;
            int16_t ps_synthesis[1152];
        };
        aac_sbr_packed_ps_overlay_abi_t packed_ps;
    };
    // Outside the union: initialization must never overwrite preserved PS.
    int32_t *smoothing[4][AAC_SBR_ROWS];
} aac_high_channel_t;
#else
typedef union AAC_ABI_VIEW {
    struct {
        int32_t frame_size, sync_state;
        aac_high_frame_t frame;
        int32_t *smoothing[4][AAC_SBR_ROWS];
    };
    aac_sbr_ps_overlay_abi_t ps_overlay;
    aac_sbr_packed_ps_overlay_abi_t packed_ps;
} aac_high_channel_t;
#endif
#ifndef AAC_ASYMMETRIC_OWNER
typedef aac_high_channel_t aac_high_channel_view_t;
#define AAC_HIGH_OWNER_CHANNELS aac_high_channel_t channel[AAC_SBR_CHANNELS]
#define AAC_HIGH_RIGHT_MEMBER(member) channel[1].member
#endif
typedef struct AAC_ABI_VIEW {
    AAC_HIGH_OWNER_CHANNELS;
    int32_t initialize_ps;
    aac_ps_abi_t *ps;
#if defined(AAC_LOW_WORKSPACE) && !defined(AAC_ASYMMETRIC_OWNER)
    uint32_t frame_cursor_padding[2];
#endif
    aac_ps_abi_t embedded_ps;
} aac_high_full_owner_t;
typedef struct AAC_ABI_VIEW {
    AAC_HIGH_OWNER_CHANNELS;
    int32_t initialize_ps;
    aac_ps_abi_t *ps;
#if defined(AAC_LOW_WORKSPACE) && !defined(AAC_ASYMMETRIC_OWNER)
    uint32_t frame_cursor_padding[2];
#endif
    int32_t inactive_ps;
} aac_high_owner_t;
#undef AAC_HIGH_OWNER_CHANNELS

static inline aac_high_channel_view_t *aac_high_owner_channel(aac_high_owner_t *owner,unsigned ch) {
    assert(ch<AAC_SBR_CHANNELS);
#ifdef AAC_ASYMMETRIC_OWNER
    return ch ? (void *)&owner->right : &owner->left;
#else
    return &owner->channel[ch];
#endif
}
static inline aac_high_channel_t *aac_high_owner_right(aac_high_owner_t *owner) {
#ifdef AAC_ASYMMETRIC_OWNER
    return &owner->right;
#else
    return &owner->channel[1];
#endif
}

#ifndef AAC_LOW_WORKSPACE
_Static_assert(offsetof(aac_high_frame_t,high_imag)==offsetof(aac_sbr_frame_abi_t,high_imag),
               "Every prefix reader must retain its original ABI");
_Static_assert(sizeof(aac_sbr_ps_overlay_abi_t)<=offsetof(aac_high_channel_t,frame.synthesis),
               "Relocated PS must not overlap either synthesis history");
#else
_Static_assert(offsetof(aac_high_channel_t,frame.previous_noise)+sizeof(((aac_high_frame_t *)0)->previous_noise)
               <=offsetof(aac_high_channel_t,ps_overlay.peak),"Right reset must not touch PS workspace");
#ifdef AAC_ASYMMETRIC_OWNER
_Static_assert(offsetof(aac_high_channel_t,smoothing)+sizeof(((aac_high_channel_t *)0)->smoothing)
               <=offsetof(aac_high_channel_t,ps_overlay),
               "Pointer tables must remain outside the PS union");
#else
_Static_assert(offsetof(aac_high_channel_t,smoothing)>=sizeof(aac_sbr_ps_overlay_abi_t),
               "Smoothing-table initialization must not touch relocated PS");
#endif
#endif
_Static_assert(offsetof(aac_high_owner_t,inactive_ps)==offsetof(aac_high_full_owner_t,embedded_ps),
               "Inactive PS detection word must match the native tail cursor");

static inline int16_t *aac_high_ps_synthesis(aac_high_channel_view_t *channel) {
#ifdef AAC_LOW_WORKSPACE
    return ((aac_high_channel_t *)(void *)channel)->ps_synthesis;
#else
    return channel->frame.synthesis;
#endif
}

#ifdef AAC_LOW_WORKSPACE
typedef struct {
    int32_t real[AAC_LOW_ROWS][AAC_LOW_BANDS], imag[AAC_LOW_ROWS][AAC_LOW_BANDS];
} aac_low_workspace_t;
_Static_assert(offsetof(aac_low_workspace_t,imag)==AAC_LOW_ROWS*AAC_LOW_BANDS*sizeof(int32_t),
               "Native PS real-to-imaginary plane stride is retained");
#ifndef AAC_ASYMMETRIC_OWNER
_Static_assert(offsetof(aac_high_owner_t,inactive_ps)==
               2*sizeof(aac_high_channel_t)+offsetof(aac_high_channel_t,frame),
               "Native frame loop ends at the inactive PS word");
#endif
static inline aac_high_channel_view_t *aac_high_frame_channel(aac_high_frame_t *frame) {
    return (void *)((uint8_t *)frame - offsetof(aac_high_channel_t,frame));
}
static inline int32_t (*aac_low_real(aac_high_frame_t *frame))[AAC_LOW_BANDS] {
    return (void *)((uintptr_t)frame+aac_high_frame_channel(frame)->low_real_relative);
}
static inline int32_t (*aac_low_imag(aac_high_frame_t *frame))[AAC_LOW_BANDS] {
    return (void *)((uintptr_t)frame+aac_high_frame_channel(frame)->low_imag_relative);
}
#else
static inline int32_t (*aac_low_real(aac_high_frame_t *frame))[AAC_LOW_BANDS] { return frame->low_real; }
static inline int32_t (*aac_low_imag(aac_high_frame_t *frame))[AAC_LOW_BANDS] { return frame->low_imag; }
#endif
