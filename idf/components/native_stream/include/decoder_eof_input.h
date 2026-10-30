#pragma once

#include <stdbool.h>
#include <stdint.h>

// One-byte lookahead lets a producer which reports EOF in a later control
// packet mark the actual final encoded byte as EOS. Packet bodies stay borrowed.
typedef struct {
    bool present;
    uint8_t byte;
} decoder_eof_input_t;

typedef struct {
    uint8_t *data;
    uint32_t size;
    bool eos;
} decoder_eof_segment_t;

static inline void decoder_eof_input_clear(decoder_eof_input_t *input) {
    input->present = false;
    input->byte = 0;
}

// previous is caller-owned storage, distinct from input and data, which stays
// alive until both returned segments have been processed. Copy the old byte
// there before replacing the task's lookahead with the current packet's tail.
static inline unsigned decoder_eof_input_prepare(decoder_eof_input_t *input,
        bool enabled, uint8_t *data, uint32_t size, bool eos, uint8_t *previous,
        decoder_eof_segment_t segments[2]) {
    if (!enabled) {
        decoder_eof_input_clear(input);
        segments[0] = (decoder_eof_segment_t){.data=data, .size=size, .eos=eos};
        return 1;
    }
    if (!size && !eos) return 0;
    bool had_previous = input->present;
    if (had_previous) *previous = input->byte;
    if (eos) decoder_eof_input_clear(input);
    else {
        input->byte = data[size-1U];
        input->present = true;
    }
    unsigned count = 0;
    if (had_previous) segments[count++] = (decoder_eof_segment_t){
        .data=previous, .size=1, .eos=eos && !size};
    uint32_t body_size = eos ? size : size-1U;
    if (body_size || (eos && !count)) segments[count++] = (decoder_eof_segment_t){
        .data=data, .size=body_size, .eos=eos};
    return count;
}
