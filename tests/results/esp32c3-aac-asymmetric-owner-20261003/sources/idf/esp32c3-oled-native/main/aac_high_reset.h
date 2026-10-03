#pragma once
#include "aac_sbr_reset.h"
#include "aac_high_history.h"
// Same repaired native reset semantics, with typed compact-history clears.
static inline void aac_high_reset_core(aac_core_abi_t *core,
                                      const aac_sbr_reset_view_t *sbr) {
    for(unsigned ch=0;ch<AAC_SBR_CHANNELS;++ch)
        memset(core->channel[ch].overlap,0,sizeof(core->channel[ch].overlap));
    if(sbr && !*sbr->initialize_ps && core->plus_enabled) {
        aac_ps_abi_t *ps=sbr->ps;
        for(unsigned ch=0;ch<AAC_SBR_CHANNELS;++ch) {
            aac_core_channel_abi_t *channel=&core->channel[ch];
            memset(channel->ltp_history,0,288*sizeof(channel->ltp_history[0]));
            memset(channel->ltp_history+1312,0,288*sizeof(channel->ltp_history[0]));
            aac_high_frame_t *frame=(void *)sbr->frame[ch];
            aac_high_channel_view_t *owner_channel=(void *)((uint8_t *)frame-offsetof(aac_high_channel_t,frame));
            int16_t *synthesis=ch && core->channels==1 && sbr->ps_initialized ?
                aac_high_ps_synthesis(owner_channel):frame->synthesis;
            memset(synthesis,0,sizeof(frame->synthesis));
            memset(frame->previous_noise,0,sizeof(frame->previous_noise));
        }
        aac_high_frame_t *left=(void *)sbr->frame[0], *right=(void *)sbr->frame[1];
        memset(left->low_real,0,8*sizeof(left->low_real[0]));
        memset(left->previous_bandwidth,0,sizeof(left->previous_bandwidth));
        memset(left->gain_mantissa,0,sizeof(left->gain_mantissa));
        memset(left->noise_mantissa,0,sizeof(left->noise_mantissa));
        aac_high_history_clear(left,true);
        aac_sbr_control_abi_t *control=core->sbr_control;
        if(control->low_complexity==1) {
            memset(right->low_real,0,8*sizeof(right->low_real[0]));
            aac_high_history_clear(right,false);
            memset(right->previous_bandwidth,0,sizeof(right->previous_bandwidth));
            memset(right->gain_mantissa,0,sizeof(right->gain_mantissa));
            memset(right->noise_mantissa,0,sizeof(right->noise_mantissa));
        } else if(core->channels==1 && sbr->ps_initialized) {
            aac_hybrid_abi_t *hybrid=ps->hybrid;
            for(unsigned row=0;row<3;++row) {
                memset(hybrid->real_history[row],0,12*sizeof(int32_t));
                memset(hybrid->imag_history[row],0,12*sizeof(int32_t));
            }
        }
        for(unsigned ch=0;ch<AAC_SBR_CHANNELS;++ch)*sbr->sync[ch]=1;
        control->output_rate=0;*sbr->initialize_ps=1;ps->detected=0;
    }
    core->frame_number=0;core->plus_enabled=core->requested_plus;
}
