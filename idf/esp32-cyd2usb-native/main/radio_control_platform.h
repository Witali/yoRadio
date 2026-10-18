#pragma once
#include "native_audio_output.h"

static inline void radio_control_reset_normalizer(void) {
    native_audio_output_request_normalizer_reset();
}
