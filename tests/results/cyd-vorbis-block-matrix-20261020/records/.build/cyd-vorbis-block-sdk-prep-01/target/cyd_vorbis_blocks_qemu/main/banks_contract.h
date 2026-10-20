#pragma once
#include <stddef.h>
#include <stdint.h>
// Encoded public payloads only; info[23] and setup exclude the 7-byte packet prefix.
typedef struct {
    const char *name;
    uint32_t source_rate;
    const uint8_t *info, *setup, *audio, *modes;
    size_t info_size, setup_size, audio_size, modes_count;
    const uint32_t *offsets;
    size_t offsets_count;
    uint32_t packet_count;
} block_bank_t;
// Root's future frozen banks_data.h defines block_banks[3] and
// BLOCK_MATRIX_DATA_MANIFEST_SHA256 after independent input qualification.
