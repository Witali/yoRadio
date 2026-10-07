#pragma once
// Analysis-only names inside the ABI's opaque regions. No allocation or RAM
// reduction. Checked against the pinned binary's PS/SBR readers and setters,
// and the PacketVideo reference field order (see the symbolic audit report).
#include "aac_sbr_abi.h"

typedef struct {
    int32_t previous_upper_subband, data_available;
    uint32_t enable_iid, enable_icc, enable_extension;
    int32_t fine_iid;
    int32_t previous_iid[34], previous_icc[34];
    uint32_t iid_resolution, icc_resolution, frame_class, envelope_count;
    uint32_t envelope_borders[6], iid_time_delta[5], icc_time_delta[5];
} aac_analysis_ps_parameters_t;
typedef struct {
    int32_t scale_factor_count, noise_factor_count, crc_checksum, frame_class;
    int32_t frame_info[35], band_count[2], noise_band_count, offset;
    int32_t amplitude_resolution, noise_envelope_count, envelope_pointer;
    int32_t previous_short_envelope, reset;
} aac_analysis_frame_control_t;
typedef struct {
    int32_t envelope_domain[5], noise_domain[5];
    int32_t inverse_filter_mode[10], previous_inverse_filter_mode[10];
} aac_analysis_inverse_filter_t;
typedef struct {
    int32_t add_harmonics[290], previous_harmonics[64];
    int32_t harmonic_index, phase_index;
} aac_analysis_harmonics_t;
typedef struct {
    int32_t envelope_mantissa[290], envelope_exponent[290], previous_energy[58];
    int32_t noise_mantissa[10], noise_exponent[10];
} aac_analysis_envelope_t;
typedef struct {
    int32_t frequency_bands[2][59], noise_bands[6], master_bands[59];
    int32_t band_count[2], noise_band_count, master_band_count;
    int32_t patch_count, patch_start_band[6];
    int32_t gate_mode[4], limiter_bands[4][13], sqrt_cache[8][4];
} aac_analysis_frequency_control_t;

// The analysis ELF is the ORIGINAL decoder. Use its ordinary channel view;
// selecting a PS/PC16 overlay in Ghidra would hide ordinary frame field names.
typedef struct {
    int32_t frame_size, sync_state;
    aac_sbr_frame_abi_t frame;
    int32_t *smoothing[4][AAC_SBR_BANDS];
} aac_analysis_channel_t;
typedef struct {
    aac_analysis_channel_t channel[AAC_SBR_CHANNELS];
    aac_sbr_owner_abi_t *owner;
} aac_analysis_bindings_t;

#define AAC_REGION(view, type, member) \
    _Static_assert(sizeof(view)==sizeof(((type *)0)->member), "Analysis region: " #member)
AAC_REGION(aac_analysis_ps_parameters_t, aac_ps_abi_t, parameters);
AAC_REGION(aac_analysis_frame_control_t, aac_sbr_frame_abi_t, frame_control);
AAC_REGION(aac_analysis_inverse_filter_t, aac_sbr_frame_abi_t, domain_and_inverse_filter);
AAC_REGION(aac_analysis_harmonics_t, aac_sbr_frame_abi_t, harmonics_and_envelopes);
AAC_REGION(aac_analysis_envelope_t, aac_sbr_frame_abi_t, envelope_and_noise);
AAC_REGION(aac_analysis_frequency_control_t, aac_sbr_control_abi_t, remaining);
_Static_assert(sizeof(aac_analysis_channel_t)==sizeof(aac_sbr_channel_abi_t), "Analysis channel view");
_Static_assert(offsetof(aac_analysis_ps_parameters_t, iid_resolution)==0x128, "PS IID resolution");
_Static_assert(offsetof(aac_analysis_ps_parameters_t, envelope_count)==0x134, "PS envelope count");
_Static_assert(offsetof(aac_analysis_frame_control_t, frame_info)==0x10, "SBR frame info");
_Static_assert(offsetof(aac_analysis_frame_control_t, reset)==0xbc, "SBR reset");
#undef AAC_REGION
