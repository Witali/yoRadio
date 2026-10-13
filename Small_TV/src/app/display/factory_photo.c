#include "factory_photo.h"

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
        unsigned tries = 0;
        /* Reject missing/corrupt native slots instead of reading invalid JPEG
         * data. All valid factory slots follow the original mask-only order. */
        while (tries < 5 && !(enabled & present & (1u << state->next_slot)))
        {
            state->next_slot = (state->next_slot + 1) % 5;
            ++tries;
        }
        action->photo = tries == 5 ? -1 : state->next_slot;
        if (tries != 5)
            state->next_slot = (state->next_slot + 1) % 5;
    }
    if (++state->fade == 6)
    {
        state->fade = 0;
        action->finished = true;
    }
}
