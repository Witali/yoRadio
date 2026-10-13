#pragma once

#include "esp_audio_simple_dec.h"

typedef struct native_aac_decoder native_aac_decoder_t;

native_aac_decoder_t *native_aac_decoder_create(void);
void native_aac_decoder_destroy(native_aac_decoder_t *decoder);
#ifdef CONFIG_YORADIO_QEMU_AAC_LATE_SBR_TEST
// Select the unmodified native controller before opening a QEMU test decoder.
void native_aac_decoder_test_disable_late_sbr(native_aac_decoder_t *decoder);
void native_aac_decoder_test_footprint(native_aac_decoder_t *decoder,
                                     size_t *requested,size_t *allocated);
#endif
esp_audio_err_t native_aac_decoder_process(native_aac_decoder_t *decoder,
    esp_audio_simple_dec_raw_t *raw, esp_audio_simple_dec_out_t *output);
esp_audio_err_t native_aac_decoder_get_info(native_aac_decoder_t *decoder,
    esp_audio_simple_dec_info_t *info);
// Extensions come from the pinned native core's decoded SBR/PS flags. Output
// channel duplication is not PS evidence. Generic AAC remains PCM-labelled.
const char *native_aac_decoder_label(native_aac_decoder_t *decoder,
    const esp_audio_simple_dec_info_t *info, bool *format_is_pcm);
// Zero when unknown. HE mono can have one source channel and two PCM channels.
unsigned native_aac_decoder_source_channels(native_aac_decoder_t *decoder);
