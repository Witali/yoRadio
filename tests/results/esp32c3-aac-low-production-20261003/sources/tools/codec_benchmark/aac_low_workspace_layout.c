// Compile for RV32; no duplicated host-side layout arithmetic.
#include "aac_smoothing_history_layout.c"
#define CHANNEL(name,member) const uint32_t aac_abi_##name[2]={ \
    offsetof(aac_sbr_channel_abi_t,member),offsetof(aac_high_channel_t,member) }
CHANNEL(left_frame,frame);
CHANNEL(left_header,frame.header);
CHANNEL(left_header_end,frame.domain_and_inverse_filter);
CHANNEL(left_sample_mode,frame.header.sample_rate_mode);
CHANNEL(left_startup,frame.startup);
CHANNEL(left_coupling,frame.coupling);
CHANNEL(left_imag,frame.high_imag);
#undef CHANNEL
const uint32_t aac_abi_frame_imag[2]={offsetof(aac_sbr_frame_abi_t,high_imag),offsetof(aac_high_frame_t,high_imag)};
const uint32_t aac_abi_frame_sync[2]={
    offsetof(aac_sbr_channel_abi_t,sync_state)-offsetof(aac_sbr_channel_abi_t,frame),
    offsetof(aac_high_channel_t,sync_state)-offsetof(aac_high_channel_t,frame)};
// Separate descriptor for the two opcode replacements (ADDI -> LW).
const uint32_t aac_low_slots[4]={
    offsetof(aac_sbr_frame_abi_t,low_real),
    offsetof(aac_high_channel_t,low_real_relative)-offsetof(aac_high_channel_t,frame),
    offsetof(aac_sbr_frame_abi_t,low_imag),
    offsetof(aac_high_channel_t,low_imag_relative)-offsetof(aac_high_channel_t,frame)};
