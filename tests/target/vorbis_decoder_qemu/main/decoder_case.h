// Literal raw-fixture transport metadata; no EOF or loop-index EOS inference.
#pragma once
#include <stddef.h>
#include <stdint.h>

typedef struct {
    const uint8_t *identification, *setup, *audio;
    size_t identification_bytes, setup_bytes, audio_bytes;
    const uint32_t *offsets;
    const uint64_t *bits;
    const int64_t *granules;
    const uint8_t *eos, *gaps;
    uint32_t packets;
} decoder_case_t;
