// Verify the extra metadata's decoder ownership and both reset semantics.
#include "aac_compact_owner.h"
#include "packed_complex_storage.h"
#include "esp_heap_caps.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void *__wrap_media_lib_module_calloc(const char *,size_t,size_t);
void __wrap_media_lib_free(void *);
void __wrap_compact5_sbr_open(int,void *,void *,int);
void aac_compact_owner_test_assert_idle(void);

static void get(aac_compact_owner_t *state,unsigned ch,unsigned index,int32_t *r,int32_t *im) {
    aac_high_history_t *h=&aac_high_owner_channel(state->owner,ch)->frame.high_history;
    pc19_unpack(h->mantissas[index],pc19_split_metadata_load(h->metadata,state->high_history.pc19_extra[ch],index),r,im);
}
void qemu_aac_pc19_metadata_test(void) {
    aac_compact_owner_t state={0};aac_compact_owner_enter(&state);
    aac_high_owner_t *owner=__wrap_media_lib_module_calloc("AAC",1,sizeof(aac_sbr_owner_abi_t));
    assert(owner && state.owner==owner);
    for(unsigned ch=0;ch<AAC_SBR_CHANNELS;++ch)for(unsigned i=0;i<AAC_HIGH_PAIRS;++i) {
        int32_t r=(int32_t)(i+1)*(1<<17),im=-(int32_t)(i+1)*(1<<15);
        if(ch){r=-r;im=-im;} // Opposite metadata signs expose cross-channel access.
        unsigned metadata,clipped;aac_high_history_t *h=&aac_high_owner_channel(owner,ch)->frame.high_history;
        h->mantissas[i]=pc19_pack(r,im,&metadata,&clipped);assert(!clipped);
        pc19_split_metadata_store(h->metadata,state.high_history.pc19_extra[ch],i,metadata);
    }
    // Repacking a real-only clear must retain the represented imaginary part.
    aac_high_history_clear(&aac_high_owner_channel(owner,1)->frame,false);
    for(unsigned i=0;i<AAC_HIGH_PAIRS;++i) {
        int32_t lr,li,rr,ri;get(&state,0,i,&lr,&li);get(&state,1,i,&rr,&ri);
        assert(lr==(int32_t)(i+1)*(1<<17) && rr==0);
        assert(li==-(int32_t)(i+1)*(1<<15) && ri==-li);
    }
    state.high_history.pc19_channel=1;
    aac_high_history_clear(&aac_high_owner_channel(owner,0)->frame,true);
    assert(state.high_history.pc19_channel==1);
    for(unsigned i=0;i<AAC_HIGH_PAIRS;++i) {
        int32_t lr,li,rr,ri;get(&state,0,i,&lr,&li);get(&state,1,i,&rr,&ri);
        assert(!lr && !li && !rr && ri!=0);
    }
    // Opening SBR again must clear extra bits even when the PS overlay survives.
    aac_sbr_control_abi_t *control=calloc(1,sizeof(*control));assert(control);
    aac_ps_abi_t *ps=&aac_high_owner_right(owner)->ps_overlay.relocated_ps;
    state.ps_initialized=true;owner->ps=ps;ps->detected=1;
    ps->previous_mix[0][0]=0x12345678;
    memset(state.high_history.pc19_extra,0xff,sizeof(state.high_history.pc19_extra));
    __wrap_compact5_sbr_open(22050,control,owner,0);
    assert(ps->detected==1 && ps->previous_mix[0][0]==0x12345678);
    for(unsigned ch=0;ch<AAC_SBR_CHANNELS;++ch)for(unsigned i=0;i<AAC_HIGH_SIDE_METADATA_WORDS;++i)
        assert(!state.high_history.pc19_extra[ch][i]);
    free(control);
    __wrap_media_lib_free(owner);assert(!state.owner);
    // Simulate stale auxiliary bits after a previous owner, then reopen.
    memset(state.high_history.pc19_extra,0xff,sizeof(state.high_history.pc19_extra));
    owner=__wrap_media_lib_module_calloc("AAC",1,sizeof(aac_sbr_owner_abi_t));assert(owner);
    for(unsigned ch=0;ch<AAC_SBR_CHANNELS;++ch)for(unsigned i=0;i<AAC_HIGH_SIDE_METADATA_WORDS;++i)
        assert(!state.high_history.pc19_extra[ch][i]);
    __wrap_media_lib_free(owner);aac_compact_owner_leave();aac_compact_owner_test_assert_idle();
    assert(heap_caps_check_integrity_all(true));
    printf("AAC_PC19_METADATA_PASS pairs_per_channel=%u channels=2 real_clear=exact full_clear=exact reopen=zero side_bytes=%u\n",
           AAC_HIGH_PAIRS,(unsigned)sizeof(state.high_history.pc19_extra));
    puts("AAC_PC19_REOPEN_PASS channels=distinct channel_cursor=preserved sbr_open=zero ps_overlay=preserved");
}
