#include <assert.h>
#include <inttypes.h>
#include <stdbool.h>
#include <stdio.h>
#include "adaptive_input.h"

static adaptive_input_t *s_encoded=(adaptive_input_t *)1;
static adaptive_input_stats_t capacity;
static int64_t clock_us;
static unsigned active_generation,tick_ms,delays,queries,fill_after,cancel_after,fail_after;
static bool failed;
#define STREAM_INPUT_ACTIVE(g) ((g)==active_generation && !failed)
#define pdMS_TO_TICKS(ms) ((ms)/tick_ms)
static int64_t esp_timer_get_time(void) {return clock_us;}
adaptive_input_stats_t adaptive_input_stats(adaptive_input_t *q) {
    assert(q==s_encoded);++queries;return capacity;
}
static void vTaskDelay(TickType_t ticks) {
    assert(ticks);clock_us+=(int64_t)ticks*tick_ms*1000;++delays;
    if (fill_after && delays==fill_after)capacity.occupied=capacity.resident;
    if (cancel_after && delays==cancel_after)++active_generation;
    if (fail_after && delays==fail_after)failed=true;
}
#include "input_prefill.h"

static void begin(void) {
    capacity=(adaptive_input_stats_t){.resident=8,.occupied=2};
    clock_us=0;active_generation=42;tick_ms=1;delays=queries=fill_after=cancel_after=fail_after=0;
    failed=false;
}
int main(void) {
    begin();assert(prefill_encoded_input(42,0) && !delays && !queries);
    begin();assert(!prefill_encoded_input(41,0) && !delays && !queries);
    begin();capacity.occupied=8;assert(prefill_encoded_input(42,250) && !delays && queries==1);
    begin();capacity.resident=0;assert(!prefill_encoded_input(42,250) && !delays);
    begin();fill_after=2;assert(prefill_encoded_input(42,250) && delays==2 && clock_us==10000);
    begin();assert(prefill_encoded_input(42,25) && clock_us==25000);
    begin();clock_us=UINT32_MAX-1000LL;
    assert(prefill_encoded_input(42,25) && clock_us==UINT32_MAX-1000LL+25000);
    begin();tick_ms=20;assert(prefill_encoded_input(42,25) && delays==2 && clock_us==40000);
    begin();cancel_after=2;assert(!prefill_encoded_input(42,250) && delays==2);
    begin();fail_after=2;assert(!prefill_encoded_input(42,250) && delays==2);
    begin();failed=true;assert(!prefill_encoded_input(42,250) && !delays && !queries);
    begin();capacity.occupied=8;capacity.writing=4;capacity.reading=4;capacity.ready=0;
    assert(prefill_encoded_input(42,250) && !delays);
    puts("PASS CYD prefill: disabled/empty/full/fill/deadline, generation/output cancellation, coarse tick clamp, 64-bit clock and retained producer leases; ASan/UBSan");
    return 0;
}
