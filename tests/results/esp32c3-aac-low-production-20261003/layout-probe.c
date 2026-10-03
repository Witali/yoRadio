#include "aac_high_history_abi.h"
const uint32_t low_production_layout[]={
    sizeof(aac_high_frame_t),sizeof(aac_high_channel_t),sizeof(aac_high_owner_t),
    offsetof(aac_high_channel_t,frame),offsetof(aac_high_channel_t,smoothing),
    sizeof(((aac_high_channel_t *)0)->smoothing),sizeof(aac_sbr_ps_overlay_abi_t),
    sizeof(((aac_high_channel_t *)0)->ps_synthesis)
};
