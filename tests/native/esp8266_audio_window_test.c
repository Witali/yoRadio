#include <assert.h>
#include <stdio.h>
#include "audio_quiet_window.h"
int main(void) {
    _Static_assert(sizeof(audio_window_state_t) == 48, "bounded RAM");
    audio_window_state_t s = {0};
    audio_window_record(&s, 1, 1000, 100, 50);
    assert(!s.valid);
    audio_window_record(&s, 1, 25999, 1199000, 50);
    assert(!s.valid);
    audio_window_record(&s, 1, 26000, 1200100, 50);
    assert(s.valid && s.result.end.frames - s.result.start.frames == 1200000);
    assert(s.result.end.misses == s.result.start.misses);
    /* Retain a long network stall, do not start a fresh apparently-good window. */
    audio_window_record(&s, 1, 86000, 1300100, 5000);
    assert(s.valid && s.result.end.ms - s.result.start.ms == 60000);
    assert(s.result.end.misses - s.result.start.misses == 4950);
    audio_window_record(&s, 2, 87000, 1400000, 5001);
    assert(!s.valid); /* no stale previous station result */
    audio_window_record(&s, 2, 112000, 2600000, 5001);
    assert(s.valid && s.result.generation == 2);
    /* Tick, frame and miss wrap all use modulo32 deltas. */
    s = (audio_window_state_t){0};
    audio_window_record(&s, 3, UINT32_MAX - 999U, UINT32_MAX - 999U, UINT32_MAX);
    audio_window_record(&s, 3, 24000, 1199000, 0);
    assert(s.valid && (uint32_t)(s.result.end.ms - s.result.start.ms) == 25000);
    assert((uint32_t)(s.result.end.frames - s.result.start.frames) == 1200000);
    assert((uint32_t)(s.result.end.misses - s.result.start.misses) == 1);
    puts("Autonomous audio window PASS");
}
