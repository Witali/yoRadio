#pragma once

// Logical PCM speaker order, independent of the physical mono CYD output.
// Legacy keeps the established first-two-channel behavior for existing callers.
typedef enum {
    PCM_CHANNEL_LAYOUT_LEGACY = 0,
    PCM_CHANNEL_LAYOUT_VORBIS = 1,
} pcm_channel_layout;
