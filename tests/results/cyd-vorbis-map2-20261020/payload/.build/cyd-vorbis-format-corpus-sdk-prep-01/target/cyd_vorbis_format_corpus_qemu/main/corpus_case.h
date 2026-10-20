#pragma once
#include <stddef.h>
#include <stdint.h>

typedef struct {
    const char *id;
    const uint8_t *identification;
    size_t identification_size;
    const uint8_t *setup;
    size_t setup_size;
    const uint8_t *audio;
    size_t audio_size;
    const uint32_t *offsets;
    size_t offset_count;
    const uint8_t *modes;
    size_t mode_count;
    uint32_t rate;
    uint16_t channels, short_block, long_block;
    uint32_t expected_pcm_bytes;
} corpus_case_t;
