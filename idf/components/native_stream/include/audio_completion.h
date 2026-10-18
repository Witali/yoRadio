#pragma once

#define AUDIO_STATUS_STATION_UNAVAILABLE "station unavailable"

// Encoded completion follows input bytes; PCM completion follows decoded audio.
// A codec drain ends a segment without stopping the current connection.
enum {
    AUDIO_CONTINUE = 0,
    AUDIO_END_EOF,
    AUDIO_END_READ_FAILED,
    AUDIO_END_BUFFER_STALLED,
    AUDIO_END_UNAVAILABLE,
    AUDIO_END_FORMAT_UNKNOWN,
    AUDIO_END_FRAME_TRUNCATED,
    AUDIO_DRAIN_CODEC,
    AUDIO_END_DECODE_FAILED,
    AUDIO_END_ALLOCATION_FAILED,
    AUDIO_END_OUTPUT_FAILED,
};

static inline int audio_completion_is_terminal(unsigned reason) {
    return reason != AUDIO_CONTINUE && reason != AUDIO_DRAIN_CODEC;
}

static inline const char *audio_completion_status(unsigned reason) {
    switch (reason) {
        case AUDIO_END_FRAME_TRUNCATED: return "truncated audio frame";
        case AUDIO_END_FORMAT_UNKNOWN: return "unknown audio format";
        case AUDIO_END_READ_FAILED: return "stream read failed";
        case AUDIO_END_BUFFER_STALLED: return "buffer stalled";
        case AUDIO_END_UNAVAILABLE: return AUDIO_STATUS_STATION_UNAVAILABLE;
        case AUDIO_END_DECODE_FAILED: return "decode failed";
        case AUDIO_END_ALLOCATION_FAILED: return "decoder allocation failed";
        case AUDIO_END_OUTPUT_FAILED: return "audio output failed";
        default: return "stream ended";
    }
}
