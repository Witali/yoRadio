/* Deterministic host regression clock; NOT a performance measurement. */
#include <assert.h>
#include "opus_function_profile.h"
static uint32_t tick;
void yoradio_opus_function_clock(uint32_t *wall, uint32_t *cpu) { *wall=*cpu=++tick; }
__attribute__((constructor)) static void start_profile(void) {
    opus_function_profile_reset(); opus_function_profile_enable(1);
}
__attribute__((destructor)) static void check_used(void) {
    assert(opus_function_profile_row(0).calls > 0);
}
