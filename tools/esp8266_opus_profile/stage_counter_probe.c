#include <assert.h>
#include <stdint.h>
#include "opus_stage_profile.h"
static uint32_t tick;
static unsigned reads;
uint32_t opus_stage_profile_clock(void) { ++reads; return tick; }
int main(void) {
    /* Selected scopes only; natural timer wrap subtracts modulo 2^32. */
    opus_stage_profile_reset();
    tick = UINT32_MAX - 10;
    OPUS_STAGE_BEGIN(OPUS_STAGE_CELT_BANDS)
    tick = 25;
    OPUS_STAGE_END(OPUS_STAGE_CELT_BANDS)
    OPUS_STAGE_BEGIN(OPUS_STAGE_SILK_CORE)
    tick = 1000;
    OPUS_STAGE_END(OPUS_STAGE_SILK_CORE)
    opus_stage_profile_t s = opus_stage_profile_snapshot();
    assert(reads == 2 && s.calls == 1 && s.ticks == 36 && s.max_ticks == 36);
    opus_stage_profile_record(UINT32_MAX);
    opus_stage_profile_record(UINT32_MAX);
    s = opus_stage_profile_snapshot();
    assert(s.calls == 3 && s.ticks == 36 + UINT64_C(2)*UINT32_MAX && s.max_ticks == UINT32_MAX);
    opus_stage_profile_reset(); s = opus_stage_profile_snapshot();
    assert(s.calls == 0 && s.ticks == 0 && s.max_ticks == 0);
    return 0;
}
