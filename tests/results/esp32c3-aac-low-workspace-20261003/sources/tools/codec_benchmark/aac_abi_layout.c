// Compile for RV32, then read constants from ELF. Never execute target code on
// the host or duplicate C layout arithmetic in the binary patcher.
#include "aac_sbr_abi.h"
#define FIELD(name, member) const uint32_t aac_abi_##name[2] = { \
    offsetof(aac_sbr_owner_abi_t, member), offsetof(aac_sbr_compact_owner_abi_t, member) }
FIELD(ps_flag, initialize_ps);
FIELD(ps_pointer, ps);
FIELD(ps_data, embedded_ps);
FIELD(right_header, channel[1].frame.header);
FIELD(right_frame, channel[1].frame);
FIELD(right_status, channel[1].sync_state);
FIELD(right_coupling, channel[1].frame.coupling);
#ifdef AAC_LOW_WORKSPACE
const uint32_t aac_abi_right_synthesis[2]={
    offsetof(aac_sbr_owner_abi_t,channel[1].frame.synthesis),
    offsetof(aac_sbr_compact_owner_abi_t,channel[1].ps_synthesis)};
#else
FIELD(right_synthesis, channel[1].frame.synthesis);
#endif
FIELD(right_high_real, channel[1].frame.high_real);
FIELD(right_high_imag, channel[1].frame.high_imag);
FIELD(ps_peak, channel[1].ps_overlay.peak);
FIELD(ps_energy, channel[1].ps_overlay.previous_energy);
FIELD(ps_difference, channel[1].ps_overlay.previous_peak_difference);
FIELD(ps_hybrid, channel[1].ps_overlay.hybrid_and_long_delays);
FIELD(ps_allpass_qmf, channel[1].ps_overlay.allpass_qmf);
FIELD(ps_allpass_sub, channel[1].ps_overlay.allpass_sub_qmf);
FIELD(ps_delay_real, channel[1].ps_overlay.main_delay_real);
FIELD(ps_delay_imag, channel[1].ps_overlay.main_delay_imag);
FIELD(ps_real_pointers, channel[1].ps_overlay.delay_real);
FIELD(ps_imag_pointers, channel[1].ps_overlay.delay_imag);
#undef FIELD
const uint32_t aac_abi_channel_size[2] = {sizeof(aac_sbr_channel_abi_t), sizeof(aac_sbr_compact_channel_abi_t)};
const uint32_t aac_abi_owner_size[2] = {sizeof(aac_sbr_owner_abi_t), sizeof(aac_sbr_compact_owner_abi_t)};
const uint32_t aac_abi_table_size[2] = {sizeof(((aac_sbr_channel_abi_t *)0)->smoothing[0]), sizeof(((aac_sbr_compact_channel_abi_t *)0)->smoothing[0])};
#define TABLE(n) const uint32_t aac_abi_frame_table_##n[2] = { \
    offsetof(aac_sbr_channel_abi_t,smoothing[n])-offsetof(aac_sbr_channel_abi_t,frame), \
    offsetof(aac_sbr_compact_channel_abi_t,smoothing[n])-offsetof(aac_sbr_compact_channel_abi_t,frame) }
TABLE(1); TABLE(2); TABLE(3);
