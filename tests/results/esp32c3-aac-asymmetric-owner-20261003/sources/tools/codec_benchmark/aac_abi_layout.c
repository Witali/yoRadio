// Compile for RV32, then read constants from ELF. Never execute target code on
// the host or duplicate C layout arithmetic in the binary patcher.
#include "aac_sbr_abi.h"
#define FIELD(name, member) const uint32_t aac_abi_##name[2] = { \
    offsetof(aac_sbr_owner_abi_t, member), offsetof(aac_sbr_compact_owner_abi_t, member) }
FIELD(ps_flag, initialize_ps);
FIELD(ps_pointer, ps);
FIELD(ps_data, embedded_ps);
#ifndef AAC_ABI_RIGHT_MEMBER
#define AAC_ABI_RIGHT_MEMBER(member) channel[1].member
#endif
#define RIGHT(name, member) const uint32_t aac_abi_##name[2] = { \
    offsetof(aac_sbr_owner_abi_t,channel[1].member), \
    offsetof(aac_sbr_compact_owner_abi_t,AAC_ABI_RIGHT_MEMBER(member)) }
RIGHT(right_header, frame.header);
RIGHT(right_frame, frame);
RIGHT(right_status, sync_state);
RIGHT(right_coupling, frame.coupling);
#ifdef AAC_LOW_WORKSPACE
const uint32_t aac_abi_right_synthesis[2]={
    offsetof(aac_sbr_owner_abi_t,channel[1].frame.synthesis),
    offsetof(aac_sbr_compact_owner_abi_t,AAC_ABI_RIGHT_MEMBER(ps_synthesis))};
#else
RIGHT(right_synthesis, frame.synthesis);
#endif
RIGHT(right_high_real, frame.high_real);
RIGHT(right_high_imag, frame.high_imag);
RIGHT(ps_peak, ps_overlay.peak);
RIGHT(ps_energy, ps_overlay.previous_energy);
RIGHT(ps_difference, ps_overlay.previous_peak_difference);
RIGHT(ps_hybrid, ps_overlay.hybrid_and_long_delays);
RIGHT(ps_allpass_qmf, ps_overlay.allpass_qmf);
RIGHT(ps_allpass_sub, ps_overlay.allpass_sub_qmf);
RIGHT(ps_delay_real, ps_overlay.main_delay_real);
RIGHT(ps_delay_imag, ps_overlay.main_delay_imag);
RIGHT(ps_real_pointers, ps_overlay.delay_real);
RIGHT(ps_imag_pointers, ps_overlay.delay_imag);
#undef RIGHT
#undef FIELD
const uint32_t aac_abi_channel_size[2] = {sizeof(aac_sbr_channel_abi_t), sizeof(aac_sbr_compact_channel_abi_t)};
const uint32_t aac_abi_owner_size[2] = {sizeof(aac_sbr_owner_abi_t), sizeof(aac_sbr_compact_owner_abi_t)};
const uint32_t aac_abi_table_size[2] = {sizeof(((aac_sbr_channel_abi_t *)0)->smoothing[0]), sizeof(((aac_sbr_compact_channel_abi_t *)0)->smoothing[0])};
#define TABLE(n) const uint32_t aac_abi_frame_table_##n[2] = { \
    offsetof(aac_sbr_channel_abi_t,smoothing[n])-offsetof(aac_sbr_channel_abi_t,frame), \
    offsetof(aac_sbr_compact_channel_abi_t,smoothing[n])-offsetof(aac_sbr_compact_channel_abi_t,frame) }
TABLE(1); TABLE(2); TABLE(3);
