#pragma once
#include <stdbool.h>
#include <stdint.h>

// Fits existing adapter/reservation/owner padding; no PCM channel inference.
typedef uint8_t aac_profile_state_t;
enum { AAC_PROFILE_UNKNOWN, AAC_PROFILE_BASE, AAC_PROFILE_SBR, AAC_PROFILE_PS };
enum { AAC_PROFILE_KIND_MASK=3, AAC_PROFILE_CHANNEL_SHIFT=2 };

static inline unsigned aac_profile_channels(aac_profile_state_t profile) {
    return profile >> AAC_PROFILE_CHANNEL_SHIFT;
}

static inline const char *aac_profile_label(aac_profile_state_t profile,bool *pcm_only) {
    unsigned channels=aac_profile_channels(profile);
    profile &= AAC_PROFILE_KIND_MASK;
    *pcm_only=profile!=AAC_PROFILE_SBR && profile!=AAC_PROFILE_PS;
    if(!channels)*pcm_only=true;
    if(profile==AAC_PROFILE_PS)return "HE-AACv2";
    if(profile==AAC_PROFILE_SBR)return "HE-AAC";
    return "AAC"; // Base object type is not inferred from SBR being absent.
}

#ifdef YORADIO_AAC_PROFILE_METADATA
void aac_profile_enter(aac_profile_state_t *);
void aac_profile_leave(void);
void aac_profile_observe(const void *core,int result);
#else
static inline void aac_profile_observe(const void *core,int result) {(void)core;(void)result;}
#endif
