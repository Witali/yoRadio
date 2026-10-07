#pragma once
// Analysis views of the pinned RV32 binary, not replacement decoder source.
// Native readers/initializers take precedence over PacketVideo's larger ABI.
#include "aac_analysis_regions.h"

typedef struct {
    uint8_t *buffer;
    uint32_t used_bits, available_bits, input_length;
    int32_t alignment_offset;
} aac_analysis_bits_t;

// SBR uses a different, cached bit reader. Do not confuse it with BITS above.
typedef struct {
    uint8_t *cursor;
    uint32_t cached_bits, cache, read_bits, total_bits;
} aac_analysis_sbr_bits_t;
typedef struct { uint16_t value, top_bit, polynomial; } aac_analysis_crc_t;
typedef struct { int32_t mantissa, exponent; } aac_analysis_fraction_t;
typedef struct {
    aac_analysis_fraction_t input, output;
} aac_analysis_sqrt_cache_t;
typedef struct {
    int32_t entries, dimensions, modulus, offset, signed_codebook;
} aac_analysis_codebook_t;
typedef struct { aac_analysis_codebook_t entry[13]; } aac_analysis_codebook_table_t;
typedef struct { int32_t rate, long_bands, short_bands; } aac_analysis_sample_rate_t;
typedef struct { aac_analysis_sample_rate_t entry[12]; } aac_analysis_sample_rates_t;
typedef struct {
    int32_t r11_real, r01_real, r02_real, r12_real, r22_real;
    int32_t r01_imag, r02_imag, r12_imag, determinant;
} aac_analysis_autocorrelation_t;
typedef struct { int32_t count, start_band[6]; } aac_analysis_patch_t;
typedef struct {
    int32_t estimated_mantissa[64], estimated_exponent[64];
    int32_t reference_mantissa[64], reference_exponent[64];
    int32_t gain_mantissa[64], gain_exponent[64];
    int32_t noise_mantissa[64], noise_exponent[64];
    int32_t tone_mantissa[64], tone_exponent[64], harmonics[64];
    int32_t remaining_rows[5][64];
} aac_analysis_envelope_workspace_t;

typedef struct {
    int32_t count, is_pair[16], tag[16];
} aac_analysis_elements_t;
typedef struct { int32_t present, tag, pseudo_surround; } aac_analysis_mixdown_t;
typedef struct {
    int32_t profile, sample_rate_index;
    int32_t unidentified_word; // Native offset 8: retain storage, do not infer semantics.
    aac_analysis_elements_t front, side, back, lfe, data, coupling;
    aac_analysis_mixdown_t mono, stereo, matrix;
    int32_t file_is_adts, headerless_frames, frame_length, crc_absent;
    uint32_t crc;
} aac_analysis_program_t;

typedef struct {
    int32_t is_long, windows, coefficients_per_frame, bands_per_frame;
    int32_t coefficients_per_window[8], bands_per_window[8], section_bits[8];
    int16_t *band_top[8];
    int32_t *short_band_width;
    int32_t frame_band_top[128], groups, group_length[8];
} aac_analysis_window_t;

typedef struct {
    int32_t start_band, stop_band, start_coefficient, stop_coefficient;
    uint32_t order;
    int32_t direction, lpc_q;
} aac_analysis_tns_filter_t;
typedef struct {
    int32_t present, filter_count[8];
    aac_analysis_tns_filter_t filter[8];
    int32_t lpc[60];
} aac_analysis_tns_t;
typedef struct {
    int32_t weight, window_prediction[8], band_prediction[128], present, delay[8];
} aac_analysis_ltp_t;
typedef struct {
    aac_analysis_tns_t tns;
    aac_analysis_window_t window;
    int32_t factors[128], codebook[128], groups[8], q_format[128], max_band;
    aac_analysis_ltp_t ltp;
} aac_analysis_channel_shared_t;
// This is the parsing-phase view of each 2048-word coefficient block. Later
// transforms/SBR reuse the entire block as sample storage; lifetimes are unchanged.
typedef struct {
    int32_t coefficients[1024];
    aac_analysis_channel_shared_t shared;
    int32_t mask[128];
    uint8_t unused_tail[8192 - 1024*sizeof(int32_t) - sizeof(aac_analysis_channel_shared_t) - 128*sizeof(int32_t)];
} aac_analysis_spectral_storage_t;
typedef struct {
    int32_t *coefficients;
    aac_analysis_channel_shared_t *shared;
    int32_t absolute_maximum[8], window, previous_shape, current_shape;
} aac_analysis_channel_tail_t;
typedef struct {
    int16_t ltp_history[2624];
    int32_t overlap[1024];
    aac_analysis_channel_tail_t spectrum;
} aac_analysis_core_channel_t;

typedef struct {
    int32_t tag, is_pair, intensity_present, coupling_channels;
    char *extension;
} aac_analysis_channel_info_t;
typedef struct {
    int32_t channels, front_single_channels, front_channels, side_channels;
    int32_t back_channels, lfe_channels, object_type, sample_rate_index;
    int32_t implicit_channels, upsampling;
    uint8_t downsampled_sbr, alignment[3];
    int32_t he_level, sbr_present, ps_present;
    aac_analysis_channel_info_t channel[2];
} aac_analysis_mc_t;

typedef struct {
    int32_t element_id, extension_type, payload_bytes;
    uint8_t payload[1024];
} aac_analysis_sbr_element_t;
typedef struct {
    int32_t elements, core_elements;
    aac_analysis_sbr_element_t element[1];
} aac_analysis_sbr_stream_t;
typedef struct { int32_t codebook, end; } aac_analysis_section_t;
typedef struct {
    int32_t present, count, start_band, offset[4], amplitude[4];
} aac_analysis_pulse_t;
typedef struct {
    char id[5];
    int32_t copyright_present;
    char copyright_id[10];
    int32_t original, home, bitstream_type, bitrate, programs, tags[16];
} aac_analysis_adif_t;
typedef union {
    int32_t words[1024];
    aac_analysis_program_t program;
    aac_analysis_adif_t adif;
} aac_analysis_scratch_t;
typedef union {
    int32_t predicted_samples[2048];
    uint8_t data_stream[512];
    struct {
        int16_t quantized[1024];
        aac_analysis_section_t sections[129];
        aac_analysis_pulse_t pulse;
    } spectral;
} aac_analysis_shared_t;
typedef struct {
    aac_analysis_scratch_t scratch;
    aac_analysis_shared_t shared;
} aac_analysis_workspace_t;

typedef struct {
    uint32_t frame_number;
    int32_t status;
    uint8_t plus_enabled, config_utility_enabled, alignment[2];
    int32_t current_program, frame_length, adif_test;
    aac_analysis_bits_t input;
    aac_analysis_program_t *program;
    int32_t short_band_width[16];
    aac_analysis_window_t *long_window, *short_window, *window_map[4];
    int32_t noise_state;
    aac_analysis_mc_t mc;
    int32_t ltp_buffer_state;
    aac_analysis_core_channel_t channel[2];
    aac_analysis_spectral_storage_t spectral[2];
    aac_sbr_owner_abi_t *sbr;
    aac_sbr_control_abi_t *sbr_control;
    aac_analysis_sbr_stream_t *sbr_stream;
    uint32_t syncword;
    int32_t invoke, *mask, has_mask;
    aac_analysis_scratch_t *scratch;
    aac_analysis_shared_t *shared;
    aac_analysis_workspace_t *workspace;
    uint8_t requested_plus, tail[3];
} aac_analysis_core_t;

typedef struct {
    uint8_t *input;
    uint32_t input_length, input_capacity;
    int32_t output_format;
    int16_t *output, *output_plus;
    int32_t reposition, plus_enabled, requested_he_level, requested_channels;
    uint32_t consumed_bytes, remainder_bits, sample_rate;
    uint32_t bitrate;
    int32_t encoded_channels, frame_length;
} aac_analysis_external_t;
typedef struct {
    aac_analysis_core_t *core;
    int16_t *extra_output;
    uint32_t pending_output_bytes, output_block_bytes;
    aac_analysis_external_t external;
    uint8_t saved_plus_enabled, alignment[3];
} aac_analysis_decoder_t;
typedef struct {
    uint32_t sample_rate;
    uint8_t channels, bits_per_sample, no_adts_header, plus_enabled;
} aac_analysis_config_t;
typedef struct {
    uint8_t *buffer;
    uint32_t length, consumed;
    int32_t frame_recovery;
} aac_analysis_raw_t;
typedef struct {
    uint8_t *buffer;
    uint32_t length, needed, decoded;
} aac_analysis_output_t;
typedef struct {
    uint32_t sample_rate;
    uint8_t bits_per_sample, channels, alignment[2];
    uint32_t bitrate, frame_size;
} aac_analysis_info_t;

// Numeric values are assertions against the native ABI, never live accesses.
#define AAC_ANALYSIS_OFFSET(type, member, value) \
    _Static_assert(offsetof(type, member)==value, #type "." #member)
_Static_assert(sizeof(aac_analysis_bits_t)==20, "BITS ABI");
_Static_assert(sizeof(aac_analysis_sbr_bits_t)==20, "SBR bit cache ABI");
AAC_ANALYSIS_OFFSET(aac_analysis_sbr_bits_t, total_bits, 0x10);
_Static_assert(sizeof(aac_analysis_program_t)==0x35c, "Native program allocation");
AAC_ANALYSIS_OFFSET(aac_analysis_program_t, front, 0xc);
AAC_ANALYSIS_OFFSET(aac_analysis_program_t, file_is_adts, 0x348);
_Static_assert(sizeof(aac_analysis_window_t)==0x2b8, "Native window allocation");
_Static_assert(sizeof(aac_analysis_tns_t)==0x1f4, "TNS region");
AAC_ANALYSIS_OFFSET(aac_analysis_ltp_t, present, 0x224);
AAC_ANALYSIS_OFFSET(aac_analysis_ltp_t, delay, 0x228);
AAC_ANALYSIS_OFFSET(aac_analysis_channel_shared_t, window, 0x1f4);
AAC_ANALYSIS_OFFSET(aac_analysis_channel_shared_t, factors, 0x4ac);
AAC_ANALYSIS_OFFSET(aac_analysis_channel_shared_t, codebook, 0x6ac);
AAC_ANALYSIS_OFFSET(aac_analysis_channel_shared_t, groups, 0x8ac);
AAC_ANALYSIS_OFFSET(aac_analysis_channel_shared_t, q_format, 0x8cc);
AAC_ANALYSIS_OFFSET(aac_analysis_channel_shared_t, max_band, 0xacc);
AAC_ANALYSIS_OFFSET(aac_analysis_channel_shared_t, ltp, 0xad0);
_Static_assert(sizeof(aac_analysis_channel_shared_t)==0xd18, "Shared channel region");
_Static_assert(sizeof(aac_analysis_spectral_storage_t)==8192, "Coefficient block");
AAC_ANALYSIS_OFFSET(aac_analysis_spectral_storage_t, shared, 0x1000);
AAC_ANALYSIS_OFFSET(aac_analysis_spectral_storage_t, mask, 0x1d18);
_Static_assert(sizeof(aac_analysis_core_channel_t)==sizeof(aac_core_channel_abi_t), "Channel ABI");
AAC_ANALYSIS_OFFSET(aac_analysis_core_channel_t, spectrum, 0x2480);
_Static_assert(sizeof(aac_analysis_sbr_stream_t)==0x414, "SBR stream allocation");
_Static_assert(sizeof(aac_analysis_workspace_t)==0x3000, "Shared workspace allocation");
_Static_assert(sizeof(aac_analysis_core_t)==sizeof(aac_core_abi_t), "Core ABI");
AAC_ANALYSIS_OFFSET(aac_analysis_core_t, input, 0x18);
AAC_ANALYSIS_OFFSET(aac_analysis_core_t, program, 0x2c);
AAC_ANALYSIS_OFFSET(aac_analysis_core_t, long_window, 0x70);
AAC_ANALYSIS_OFFSET(aac_analysis_core_t, window_map, 0x78);
AAC_ANALYSIS_OFFSET(aac_analysis_core_t, mc, 0x8c);
AAC_ANALYSIS_OFFSET(aac_analysis_core_t, mc.ps_present, 0xc0);
AAC_ANALYSIS_OFFSET(aac_analysis_core_t, channel, 0xf0);
AAC_ANALYSIS_OFFSET(aac_analysis_core_t, spectral, 0x4a58);
AAC_ANALYSIS_OFFSET(aac_analysis_core_t, sbr, 0x8a58);
AAC_ANALYSIS_OFFSET(aac_analysis_core_t, workspace, 0x8a7c);
_Static_assert(sizeof(aac_analysis_external_t)==64, "Native external API");
_Static_assert(sizeof(aac_analysis_decoder_t)==84, "Native wrapper allocation");
_Static_assert(sizeof(aac_analysis_config_t)==8, "Public config ABI");
_Static_assert(sizeof(aac_analysis_raw_t)==16, "Public input ABI");
_Static_assert(sizeof(aac_analysis_output_t)==16, "Public output ABI");
_Static_assert(sizeof(aac_analysis_info_t)==16, "Public info ABI");
AAC_ANALYSIS_OFFSET(aac_analysis_decoder_t, external, 0x10);
AAC_ANALYSIS_OFFSET(aac_analysis_decoder_t, saved_plus_enabled, 0x50);
_Static_assert(sizeof(aac_analysis_codebook_table_t)==260, "Native hcbbook_binary symbol");
_Static_assert(sizeof(aac_analysis_sample_rates_t)==144, "Native samp_rate_info symbol");
_Static_assert(sizeof(aac_analysis_autocorrelation_t)==36, "Native correlation result");
_Static_assert(sizeof(aac_analysis_patch_t)==28, "Native patch descriptor");
_Static_assert(sizeof(aac_analysis_envelope_workspace_t)==4096, "Full scratch workspace retained");
AAC_ANALYSIS_OFFSET(aac_analysis_envelope_workspace_t, gain_mantissa, 0x400);
AAC_ANALYSIS_OFFSET(aac_analysis_envelope_workspace_t, harmonics, 0xa00);
#undef AAC_ANALYSIS_OFFSET
