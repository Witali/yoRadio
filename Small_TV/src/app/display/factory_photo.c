#include "factory_photo.h"

static int next_photo(unsigned start,uint32_t available)
{
    /* Share the original five-slot round-robin order between cache preparation
     * and actual selection. Bound even a damaged RAM cursor before shifting. */
    unsigned slot=start%5;
    for(unsigned tries=0;tries<5;++tries) {
        if(available&(1u<<slot))return (int)slot;
        slot=(slot+1)%5;
    }
    return -1;
}

int factory_photo_prefetch(const factory_photo_t *state,uint32_t enabled,
                           uint32_t configured,uint32_t ready,uint32_t failed)
{
    /* FIXED_RECONSTRUCTION: warming all five caches held the first usable photo
     * behind unrelated jobs. Prepare only the next eligible source between
     * fades (or repair readiness at selection), never during phases1/3/4/5.
     * A stable rejected source is skipped; a transient failure remains retryable.
     * A returned slot also means the selector must wait, not skip that valid
     * source just because some later/previous photo happens to be cached. */
    if(state->fade!=0 && state->fade!=2)return -1;
    int slot=next_photo(state->next_slot,enabled&configured&~failed);
    return slot>=0 && !(ready&(1u<<slot)) ? slot:-1;
}

void factory_photo_step(factory_photo_t *state, uint32_t enabled, uint32_t present,
                        bool photo_event, bool blocked, factory_photo_action_t *action)
{
    /* Advance one 0x4200bc36 fade step and the 0x4200bb4c round-robin selector. */
    *action = (factory_photo_action_t){.photo = -2};
    if (!photo_event || blocked)
        return;
    static const uint16_t levels[] = {300, 600, 1000, 600, 300, 0};
    if (state->fade >= sizeof(levels) / sizeof(levels[0]))
        state->fade = 0;
    action->set_duty = true;
    action->duty = levels[state->fade];
    if (state->fade == 2)
    {
        /* Reject missing/corrupt native slots instead of reading invalid JPEG
         * data. All valid factory slots follow the original mask-only order. */
        action->photo = (int8_t)next_photo(state->next_slot,enabled&present);
        state->next_slot = action->photo>=0 ? (action->photo+1)%5:state->next_slot%5;
    }
    if (++state->fade == 6)
    {
        state->fade = 0;
        action->finished = true;
    }
}
