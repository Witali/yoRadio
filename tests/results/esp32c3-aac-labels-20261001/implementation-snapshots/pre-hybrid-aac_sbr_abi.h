#pragma once
// Audited views of the pinned Espressif 2.6.2 RV32 private AAC ABI.
// These describe existing storage; they never allocate another copy. Unknown
// regions remain opaque. Do not infer a lifetime or permission to shrink them
// from this header. See docs/ESP32C3_AAC_SMOOTHING_TABLES_20261001.md.
#include <stddef.h>
#include <stdint.h>

#define AAC_ABI_VIEW __attribute__((__may_alias__))
enum { AAC_SBR_ROWS=5, AAC_SBR_BANDS=64, AAC_SBR_CHANNELS=2 };
_Static_assert(sizeof(void *)==4, "AAC private ABI requires 32-bit pointers");

typedef struct AAC_ABI_VIEW {
    int32_t bands;
    int32_t *resolution;
    int32_t history_length;
    int32_t **real_history, **imag_history;
    int32_t *real_scratch, *imag_scratch;
} aac_hybrid_abi_t;

typedef struct AAC_ABI_VIEW {
    int32_t detected;
    void *right_synthesis;
    int32_t inverse_samples, force_mono;
    uint32_t samples;
    int32_t upper_subband;
    uint8_t parameters[0x190-0x18];
    int32_t delay_index;
    uint32_t serial_index[3];
    int32_t **serial_real[3], **serial_imag[3];
    int32_t **sub_serial_real[3], **sub_serial_imag[3];
    int32_t **delay_real, **delay_imag, **sub_delay_real, **sub_delay_imag;
    int32_t *peak, *previous_energy, *previous_peak_difference;
    int32_t *hybrid_left_real, *hybrid_left_imag, *hybrid_right_real, *hybrid_right_imag;
    aac_hybrid_abi_t *hybrid;
    int32_t previous_mix[4][22], mix[4][22], delta_mix[4][22];
    int32_t (*qmf_real)[64], (*qmf_imag)[64];
    int32_t long_index[41], delay_length[41];
    int32_t iid_index[6][34], icc_index[6][34];
} aac_ps_abi_t;

typedef struct AAC_ABI_VIEW {
    int32_t status, master_status, crc_enabled, sample_rate_mode;
    int32_t amplitude_resolution, start_frequency, stop_frequency, crossover_band;
    int32_t frequency_scale, alter_scale, noise_bands, noise_band_count;
    int32_t limiter_bands, limiter_gains, interpolate_frequency, smoothing_mode;
} aac_sbr_header_abi_t;

typedef struct AAC_ABI_VIEW {
    uint8_t frame_control[0xc0];
    aac_sbr_header_abi_t header;
    uint8_t domain_and_inverse_filter[0x78];
    int32_t coupling;
    uint8_t harmonics_and_envelopes[0x70c-0x17c];
    int32_t startup;
    uint8_t envelope_and_noise[0x1158-0x710];
    int32_t previous_noise[10], bandwidth[6], previous_bandwidth[6];
    int32_t low_real[40][32], low_imag[40][32];
    int32_t *high_imag;
    int32_t high_imag_history[6][48];
    int32_t *high_real;
    int32_t high_real_history[6][48];
    int16_t synthesis[1152];
    int32_t alias_degree[64];
    int32_t gain_mantissa[AAC_SBR_ROWS][AAC_SBR_BANDS];
    int32_t noise_mantissa[AAC_SBR_ROWS][AAC_SBR_BANDS];
    int32_t gain_exponent[AAC_SBR_ROWS][AAC_SBR_BANDS];
    int32_t noise_exponent[AAC_SBR_ROWS][AAC_SBR_BANDS];
} aac_sbr_frame_abi_t;

// This alternate view is valid only for the right channel while PS is active.
// Its location was checked against every PS allocator and synthesis caller.
typedef struct AAC_ABI_VIEW {
    uint8_t before_workspace[0x11b8];
    int32_t peak[20], previous_energy[20], previous_peak_difference[20];
    uint8_t hybrid_and_long_delays[0x1c00-0x12a8];
    uint8_t allpass_qmf[0x23e0-0x1c00];
    uint8_t allpass_sub_qmf[0x2800-0x23e0];
    int32_t main_delay_real[64], main_delay_imag[64];
    uint8_t before_delay_pointers[0x100];
    int32_t *delay_real[61];
    uint8_t between_delay_pointers[0x300-61*sizeof(int32_t *)];
    int32_t *delay_imag[61];
    aac_ps_abi_t relocated_ps;
} aac_sbr_ps_overlay_abi_t;

enum { AAC_PS_PACKED_PAIRS=617 };
typedef struct AAC_ABI_VIEW {
    uint8_t before_mantissas[0x1664];
    uint32_t mantissas[AAC_PS_PACKED_PAIRS];
    uint32_t exponents[(AAC_PS_PACKED_PAIRS+7)/8];
} aac_sbr_packed_ps_overlay_abi_t;

#define AAC_SBR_CHANNEL_TYPE(name, entries) \
    typedef union AAC_ABI_VIEW { \
        struct { \
            int32_t frame_size, sync_state; \
            aac_sbr_frame_abi_t frame; \
            int32_t *smoothing[4][entries]; \
        }; \
        aac_sbr_ps_overlay_abi_t ps_overlay; \
        aac_sbr_packed_ps_overlay_abi_t packed_ps; \
    } name
AAC_SBR_CHANNEL_TYPE(aac_sbr_channel_abi_t, AAC_SBR_BANDS);
AAC_SBR_CHANNEL_TYPE(aac_sbr_compact_channel_abi_t, AAC_SBR_ROWS);
#undef AAC_SBR_CHANNEL_TYPE

#define AAC_SBR_OWNER_TYPE(name, channel_type, tail_type, tail_name) \
    typedef struct AAC_ABI_VIEW { \
        channel_type channel[AAC_SBR_CHANNELS]; \
        int32_t initialize_ps; \
        aac_ps_abi_t *ps; \
        tail_type tail_name; \
    } name
AAC_SBR_OWNER_TYPE(aac_sbr_owner_abi_t, aac_sbr_channel_abi_t, aac_ps_abi_t, embedded_ps);
AAC_SBR_OWNER_TYPE(aac_sbr_compact_owner_abi_t, aac_sbr_compact_channel_abi_t, aac_ps_abi_t, embedded_ps);
AAC_SBR_OWNER_TYPE(aac_sbr_relocated_owner_abi_t, aac_sbr_channel_abi_t, int32_t, inactive_ps);
#undef AAC_SBR_OWNER_TYPE

typedef struct AAC_ABI_VIEW {
    int32_t output_rate, low_complexity;
    int32_t start_index, low_band_samples, columns, qmf_buffer_length;
    int32_t write_offset, read_offset, stop_codec;
    int32_t low_subband, previous_low_subband, high_subband, subband_count;
    uint8_t remaining[1180-13*sizeof(int32_t)];
} aac_sbr_control_abi_t;

typedef struct AAC_ABI_VIEW {
    int16_t ltp_history[2624];
    int32_t overlap[1024];
    uint8_t spectrum_and_window[0x34];
} aac_core_channel_abi_t;

typedef struct AAC_ABI_VIEW {
    uint32_t frame_number;
    int32_t status;
    uint8_t plus_enabled;
    uint8_t configuration[0xc0-9];
    int32_t channels;
    uint8_t channel_configuration[0xf0-0xc4];
    aac_core_channel_abi_t channel[AAC_SBR_CHANNELS];
    uint8_t spectrum_and_scratch[0x8a58-0xf0-2*sizeof(aac_core_channel_abi_t)];
    void *sbr; // Original or compact owner, selected by the calling adapter.
    aac_sbr_control_abi_t *sbr_control;
    uint8_t stream_state[0x8a80-0x8a60];
    uint8_t requested_plus;
    uint8_t tail[3];
} aac_core_abi_t;

// Literal offsets belong only at this ABI boundary, as checks against the
// audited binary. All live access and allocation calculations use fields.
#define AAC_ABI_OFFSET(type, member, expected) \
    _Static_assert(offsetof(type, member)==expected, #type "." #member " ABI changed")
AAC_ABI_OFFSET(aac_ps_abi_t, serial_real, 0x1a0);
AAC_ABI_OFFSET(aac_ps_abi_t, upper_subband, 0x14);
AAC_ABI_OFFSET(aac_ps_abi_t, delay_real, 0x1d0);
AAC_ABI_OFFSET(aac_ps_abi_t, hybrid, 0x1fc);
AAC_ABI_OFFSET(aac_ps_abi_t, previous_mix, 0x200);
AAC_ABI_OFFSET(aac_ps_abi_t, long_index, 0x628);
AAC_ABI_OFFSET(aac_ps_abi_t, delay_length, 0x6cc);
_Static_assert(sizeof(aac_ps_abi_t)==3536, "PS ABI size");
AAC_ABI_OFFSET(aac_sbr_channel_abi_t, frame, 8);
AAC_ABI_OFFSET(aac_sbr_channel_abi_t, frame.header, 0xc8);
AAC_ABI_OFFSET(aac_sbr_channel_abi_t, frame.header.smoothing_mode, 0x104);
AAC_ABI_OFFSET(aac_sbr_channel_abi_t, frame.coupling, 0x180);
AAC_ABI_OFFSET(aac_sbr_channel_abi_t, frame.startup, 0x714);
AAC_ABI_OFFSET(aac_sbr_channel_abi_t, frame.previous_noise, 0x1160);
AAC_ABI_OFFSET(aac_sbr_channel_abi_t, frame.previous_bandwidth, 0x11a0);
AAC_ABI_OFFSET(aac_sbr_channel_abi_t, frame.low_real, 0x11b8);
AAC_ABI_OFFSET(aac_sbr_channel_abi_t, frame.high_imag, 0x39b8);
AAC_ABI_OFFSET(aac_sbr_channel_abi_t, frame.high_real, 0x3e3c);
AAC_ABI_OFFSET(aac_sbr_channel_abi_t, frame.synthesis, 0x42c0);
AAC_ABI_OFFSET(aac_sbr_channel_abi_t, frame.gain_mantissa, 0x4cc0);
AAC_ABI_OFFSET(aac_sbr_channel_abi_t, smoothing, 0x60c0);
_Static_assert(sizeof(aac_sbr_channel_abi_t)==25792, "Original channel ABI");
_Static_assert(sizeof(aac_sbr_compact_channel_abi_t)==24848, "Compact channel ABI");
AAC_ABI_OFFSET(aac_sbr_owner_abi_t, ps, 0xc984);
AAC_ABI_OFFSET(aac_sbr_compact_owner_abi_t, ps, 0xc224);
AAC_ABI_OFFSET(aac_sbr_relocated_owner_abi_t, channel[1].ps_overlay.relocated_ps, 0x93b4);
AAC_ABI_OFFSET(aac_sbr_relocated_owner_abi_t, channel[1].packed_ps.mantissas, 0x7b24);
AAC_ABI_OFFSET(aac_sbr_relocated_owner_abi_t, channel[1].packed_ps.exponents, 0x84c8);
_Static_assert(sizeof(aac_sbr_owner_abi_t)==55128, "Original SBR ABI");
_Static_assert(sizeof(aac_sbr_compact_owner_abi_t)==53240, "Compact SBR ABI");
_Static_assert(sizeof(aac_sbr_relocated_owner_abi_t)==51596, "Relocated SBR ABI");
AAC_ABI_OFFSET(aac_sbr_control_abi_t, columns, 0x10);
AAC_ABI_OFFSET(aac_sbr_control_abi_t, write_offset, 0x18);
_Static_assert(sizeof(aac_sbr_control_abi_t)==1180, "SBR control ABI");
_Static_assert(sizeof(aac_sbr_ps_overlay_abi_t)<=offsetof(aac_sbr_channel_abi_t,frame.synthesis),
               "PS overlay must precede synthesis history");
AAC_ABI_OFFSET(aac_core_abi_t, channel[0].overlap, 0x1570);
AAC_ABI_OFFSET(aac_core_abi_t, channel[1].overlap, 0x3a24);
AAC_ABI_OFFSET(aac_core_abi_t, sbr, 0x8a58);
AAC_ABI_OFFSET(aac_core_abi_t, sbr_control, 0x8a5c);
AAC_ABI_OFFSET(aac_core_abi_t, requested_plus, 0x8a80);
_Static_assert(sizeof(aac_core_abi_t)==35460, "Core ABI size");
#undef AAC_ABI_OFFSET
