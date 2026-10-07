#pragma once
#include "esp_audio_dec.h"

// This task owns codec registration. On failure, roll back its registry before
// admitting a stream; a later Play can retry after memory becomes available.
esp_audio_err_t decoder_register_codecs(void);
