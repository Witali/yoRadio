#pragma once

#define AUDIO_STATUS_STATION_UNAVAILABLE "station unavailable"

// A terminal marker travels after all encoded data and then after all PCM.
// Zero is reserved for ordinary data packets.
enum {
    AUDIO_CONTINUE = 0,
    AUDIO_END_EOF,
    AUDIO_END_READ_FAILED,
    AUDIO_END_BUFFER_STALLED,
    AUDIO_END_UNAVAILABLE,
};

static inline const char *audio_completion_status(unsigned reason) {
    switch (reason) {
        case AUDIO_END_READ_FAILED: return "stream read failed";
        case AUDIO_END_BUFFER_STALLED: return "buffer stalled";
        case AUDIO_END_UNAVAILABLE: return AUDIO_STATUS_STATION_UNAVAILABLE;
        default: return "stream ended";
    }
}
