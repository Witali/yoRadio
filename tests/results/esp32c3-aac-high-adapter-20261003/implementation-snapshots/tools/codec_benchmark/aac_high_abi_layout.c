// Compile for RV32. All candidate addresses come from the C layout.
#include "aac_high_history_abi.h"
#define aac_sbr_compact_owner_abi_t aac_high_full_owner_t
#define aac_sbr_compact_channel_abi_t aac_high_channel_t
#include "aac_abi_layout.c"
#undef aac_sbr_compact_owner_abi_t
#undef aac_sbr_compact_channel_abi_t
#define FRAME(name, old_member, new_member) const uint32_t aac_abi_##name[2]={ \
    offsetof(aac_sbr_frame_abi_t,old_member),offsetof(aac_high_frame_t,new_member) }
FRAME(frame_gain,gain_mantissa,gain_mantissa);
FRAME(frame_alias,alias_degree,alias_degree);
FRAME(frame_real,high_real,high_real);
FRAME(frame_synthesis,synthesis,synthesis);
// These two addresses are distinct identity tokens consumed only by the six
// audited memmove history calls; they are not unpacked int32 arrays.
FRAME(frame_real_history,high_real_history,high_history.mantissas[0]);
FRAME(frame_imag_history,high_imag_history,high_history.mantissas[1]);
#undef FRAME
#define CHANNEL(name, member) const uint32_t aac_abi_##name[2]={ \
    offsetof(aac_sbr_channel_abi_t,member),offsetof(aac_high_channel_t,member) }
CHANNEL(left_real,frame.high_real);
#undef CHANNEL
#define FRAME_TABLE(name, member) const uint32_t aac_abi_##name[2]={ \
    offsetof(aac_sbr_channel_abi_t,member)-offsetof(aac_sbr_channel_abi_t,frame), \
    offsetof(aac_high_channel_t,member)-offsetof(aac_high_channel_t,frame) }
FRAME_TABLE(frame_table_0,smoothing[0]);
FRAME_TABLE(frame_table_end,smoothing[0][AAC_SBR_ROWS]);
#undef FRAME_TABLE
#define UPPER(type,member) ((offsetof(type,member)+0x800)>>12)
const uint32_t aac_abi_right_high_delta[2]={
    UPPER(aac_sbr_owner_abi_t,channel[1].frame.high_real)-UPPER(aac_sbr_owner_abi_t,channel[1].sync_state),
    UPPER(aac_high_full_owner_t,channel[1].frame.high_real)-UPPER(aac_high_full_owner_t,channel[1].sync_state)};
#undef UPPER
