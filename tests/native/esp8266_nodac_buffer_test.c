#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "nodac_buffer_state.h"

static nodac_buffer_state_t state;
static uint32_t payload[2][512];
static unsigned lengths[2];
static unsigned consumed;

static void check(void) {
    assert(state.active < 2);
    assert(state.state[state.active] == NODAC_DMA);
    assert(state.state[state.active ^ 1U] != NODAC_DMA);
}

static void eof(void) {
    check();
    unsigned old = state.active;
    if (!state.silent) {
        assert(lengths[old] == 512);
        for (unsigned i = 0; i < 512; ++i)
            assert(payload[old][i] == consumed++);
    }
    if (nodac_state_eof(&state)) memset(payload[old], 0xaa, sizeof(payload[old]));
    check();
}

int main(void) {
    nodac_state_init(&state);
    assert(nodac_state_acquire(&state) == 1);
    assert(nodac_state_acquire(&state) == -1);
    /* ISR at EVERY word of a deliberately delayed memcpy. The filling
     * buffer's prefix must survive, and DMA may only emit neutral data. */
    for (unsigned i = 0; i < 512; ++i) {
        payload[1][i] = i;
        eof();
        for (unsigned j = 0; j <= i; ++j) assert(payload[1][j] == j);
        assert(state.active == 0 && state.silent);
    }
    lengths[1] = 512;
    eof(); /* full memcpy but NOT published yet: still invisible to DMA */
    assert(state.active == 0);
    assert(nodac_state_publish(&state, 1));
    assert(!nodac_state_publish(&state, 1));
    assert(!nodac_state_publish(&state, 0));
    assert(!nodac_state_publish(&state, 2));
    eof();
    assert(state.active == 1 && !state.silent);
    eof(); /* underrun converts only the completed DMA buffer to silence */
    assert(consumed == 512 && state.silent);
    for (unsigned i = 0; i < 512; ++i)
        assert(payload[state.active][i] == 0xaaaaaaaaU); /* 1010..., not logic 0 */
    for (unsigned i = 0; i < 1000; ++i) eof();
    assert(consumed == 512); /* never replay stale audio */

    /* Random producer chunk lengths and EOF interleavings, including many
     * EOFs while partially filled. Check all output words, not just states. */
    unsigned produced = consumed;
    uint32_t rng = 0x82660001U;
    for (unsigned block = 0; block < 2000; ++block) {
        int index = nodac_state_acquire(&state);
        assert(index >= 0);
        lengths[index] = 0;
        while (lengths[index] < 512) {
            rng = rng * 1664525U + 1013904223U;
            unsigned count = 1U + (rng >> 24);
            for (unsigned j = 0; j < count && lengths[index] < 512; ++j)
                payload[index][lengths[index]++] = produced++;
            if (rng & 1U) eof();
            assert(state.state[index] == NODAC_FILLING);
        }
        assert(nodac_state_publish(&state, (unsigned)index));
        assert(nodac_state_acquire(&state) == -1);
        eof();
        assert(state.active == (unsigned)index);
    }
    eof();
    assert(produced == consumed);

    /* Stop discards partial/queued data without writing active DMA memory. */
    for (unsigned partial = 0; partial <= 512; ++partial) {
        nodac_state_init(&state);
        int index = nodac_state_acquire(&state);
        lengths[index] = partial;
        if (partial == 512) assert(nodac_state_publish(&state, (unsigned)index));
        nodac_state_silence(&state);
        assert(state.state[1] == NODAC_FREE);
        assert(nodac_state_acquire(&state) == 1);
        /* New complete block before mute EOF must remain queued. */
        assert(nodac_state_publish(&state, 1));
        assert(nodac_state_eof(&state));
        assert(state.silent && state.active == 0 && state.state[1] == NODAC_READY);
        assert(!nodac_state_eof(&state));
        assert(!state.silent && state.active == 1);
    }
    puts("NoDAC ownership tests passed: partial writes, delays, ordering, stop/restart");
    return 0;
}
