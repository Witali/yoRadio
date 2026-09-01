#pragma once

enum HelixStageProfileId {
    HELIX_STAGE_HUFFMAN = 0,
    HELIX_STAGE_DEQUANT,
    HELIX_STAGE_STEREO_FILTER,
    HELIX_STAGE_IMDCT,
    HELIX_STAGE_SYNTHESIS,
    HELIX_STAGE_SBR,
    HELIX_STAGE_COUNT
};

#if defined(YORADIO_ESP8266_HELIX_STAGE_PROFILE)
#ifdef __cplusplus
extern "C" {
#endif
void helix_stage_profile_begin(int stage);
void helix_stage_profile_end(int stage);
#ifdef __cplusplus
}
#endif
#define HELIX_PROFILE_BEGIN(stage) helix_stage_profile_begin(stage)
#define HELIX_PROFILE_END(stage) helix_stage_profile_end(stage)
#else
#define HELIX_PROFILE_BEGIN(stage) do { } while (0)
#define HELIX_PROFILE_END(stage) do { } while (0)
#endif
