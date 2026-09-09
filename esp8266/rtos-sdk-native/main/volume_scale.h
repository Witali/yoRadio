#pragma once

#include <stdint.h>

/* Public controls use percent; audio gain and the version-1 NVS blob keep
 * their legacy 0..254 units. Convert only at control/status boundaries,
 * never in the PCM loop. Existing saved loudness therefore stays intact. */
#define RADIO_VOLUME_MAX 100U
#define RADIO_VOLUME_RAW_MAX 254U

static inline uint8_t volume_to_percent(unsigned raw) {
    if (raw > RADIO_VOLUME_RAW_MAX) raw = RADIO_VOLUME_RAW_MAX;
    return (uint8_t)((raw * RADIO_VOLUME_MAX + RADIO_VOLUME_RAW_MAX / 2U) /
                     RADIO_VOLUME_RAW_MAX);
}

static inline uint8_t volume_from_percent(int percent) {
    if (percent < 0) percent = 0;
    if (percent > (int)RADIO_VOLUME_MAX) percent = RADIO_VOLUME_MAX;
    return (uint8_t)(((unsigned)percent * RADIO_VOLUME_RAW_MAX +
                      RADIO_VOLUME_MAX / 2U) / RADIO_VOLUME_MAX);
}
