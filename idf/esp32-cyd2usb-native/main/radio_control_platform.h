#pragma once
// CYD has no normalizer yet. Its existing output owner resets PCM/resampler
// history on every generation; stage 10 will add the DSP reset request here.
static inline void radio_control_reset_normalizer(void) {}
