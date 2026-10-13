#include "factory_animation.h"

int factory_animation_next(factory_animation_t *state, unsigned frame_count)
{
    /* FIXED_RECONSTRUCTION: follow the persistent frame cursor at 0x3fcc3a24
     * in factory 0x4200b5cc, instead of an unbounded render-count modulo.
     * A shorter selected GIF reaches its terminator and restarts at zero;
     * modulo of an unbounded drawing count chooses a different frame. */
    if (!frame_count || frame_count > 126)
        return -1;
    unsigned frame = state->next_frame;
    if (frame >= frame_count)
        frame = 0;
    state->next_frame = (uint8_t)(frame + 1);
    return (int)frame;
}
