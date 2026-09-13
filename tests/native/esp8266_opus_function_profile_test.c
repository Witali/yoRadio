#include <assert.h>
#include <stdint.h>
#include "opus_function_profile.h"
static uint32_t wall, cpu;
void yoradio_opus_function_clock(uint32_t *w, uint32_t *c) { *w=wall; *c=cpu; }
int main(void) {
    opus_function_scope_t root, a, b;
    opus_function_profile_reset(); opus_function_profile_enable(1);
    wall=cpu=0; opus_function_enter(&root,0);
    wall=cpu=10; opus_function_enter(&a,1);
    wall=40;cpu=20;opus_function_enter(&b,2);
    wall=80;cpu=30;opus_function_leave(&b);
    wall=100;cpu=50;opus_function_leave(&a);
    wall=120;cpu=70;opus_function_leave(&root);
    opus_function_row_t r=opus_function_profile_row(0),s=opus_function_profile_row(1),t=opus_function_profile_row(2);
    assert(r.calls==1&&r.cpu_us==70&&r.wall_us==120&&r.self_cpu_us==30&&r.self_wall_us==30);
    assert(s.cpu_us==40&&s.self_cpu_us==30&&s.wall_us==90&&s.self_wall_us==50);
    assert(t.cpu_us==10&&t.wall_us==40&&t.max_cpu_us==10);
    assert(r.self_cpu_us+s.self_cpu_us+t.self_cpu_us==r.cpu_us);
    assert(!opus_function_profile_error());
    opus_function_profile_enable(0);opus_function_enter(&a,1);opus_function_leave(&a);
    assert(opus_function_profile_row(1).calls==1);
    opus_function_profile_reset();opus_function_profile_enable(1);
    wall=cpu=UINT32_MAX-10;opus_function_enter(&a,0);
    wall=cpu=9;opus_function_leave(&a);
    assert(opus_function_profile_row(0).cpu_us==20&&!opus_function_profile_error());
    opus_function_enter(&root,0);opus_function_enter(&a,1);
    opus_function_leave(&root); /* Simulated OOM longjmp past inner scope. */
    assert(opus_function_profile_error()&2);opus_function_profile_enable(0);
    opus_function_profile_reset();assert(!opus_function_profile_error());
    opus_function_profile_enable(1);wall=cpu=0;opus_function_enter(&root,0);
    wall=10;cpu=20;opus_function_leave(&root);assert(opus_function_profile_error()&4);
    opus_function_profile_reset();opus_function_profile_enable(1);
    wall=cpu=0;opus_function_enter(&root,0);wall=cpu=0x80000000u;opus_function_leave(&root);
    wall=cpu=0;opus_function_enter(&root,0);wall=cpu=0x80000000u;opus_function_leave(&root);
    assert(opus_function_profile_error()&1);
    return 0;
}
