#pragma once

#include "esp_audio_dec.h"

// Called by startup while all pipeline tasks are blocked. Failure rolls back
// partial registration; retry is safe after the allocation pressure is gone.
esp_audio_err_t decoder_register_codecs(void);
// Only while no decoder task can use the registry (failed startup cleanup).
void decoder_unregister_codecs(void);
