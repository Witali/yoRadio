#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include "stream_bitrate.h"

int main(void) {
    stream_bitrate_meter_t meter={0};
    assert(!stream_bitrate_meter_add(NULL,100,0));
    assert(!stream_bitrate_meter_add(&meter,0,0) && !meter.initialized);
    assert(!stream_bitrate_meter_add(&meter,100,-1) && !meter.initialized);
    assert(!stream_bitrate_meter_add(&meter,16000,0) && meter.initialized);
    assert(!stream_bitrate_meter_add(&meter,16000,1000000));
    assert(!stream_bitrate_meter_add(&meter,16000,2000000));
    assert(!stream_bitrate_meter_add(&meter,16000,3000000));
    assert(!stream_bitrate_meter_add(&meter,16000,4999999));
    assert(stream_bitrate_meter_add(&meter,0,5000000)==0 && meter.audio_bytes==80000);
    assert(stream_bitrate_meter_add(&meter,1,5000000)==128);
    assert(meter.started_us==5000000 && !meter.audio_bytes);
    assert(stream_bitrate_meter_add(&meter,80000,10000000)==128);
    // New transport instances never retain another generation's window.
    stream_bitrate_meter_t next={0};
    assert(!stream_bitrate_meter_add(&next,100,10000000) && next.audio_bytes==100);
    assert(!stream_bitrate_meter_add(&next,100,9000000));
    assert(next.started_us==9000000 && next.audio_bytes==100);
    assert(stream_bitrate_meter_add(&next,40000,14000000)==64);
    // Widest accepted bps and half-up kbps rounding use wide arithmetic.
    meter=(stream_bitrate_meter_t){0};
    assert(!stream_bitrate_meter_add(&meter,1,0));
    size_t bytes=(size_t)(UINT64_C(4294967295)*5/8);
    assert(stream_bitrate_meter_add(&meter,bytes-1,5000000)==4294967);
    meter=(stream_bitrate_meter_t){0};
    assert(!stream_bitrate_meter_add(&meter,1,0));
    assert(!stream_bitrate_meter_add(&meter,bytes+100,5000000));
    assert(!meter.audio_bytes && meter.started_us==5000000);
    meter=(stream_bitrate_meter_t){0};
    assert(!stream_bitrate_meter_add(&meter,1,0));
    assert(stream_bitrate_meter_add(&meter,625,5000000)==1);
    assert(!stream_bitrate_meter_add(&meter,1,10000000));
    meter=(stream_bitrate_meter_t){0};
    assert(!stream_bitrate_meter_add(&meter,100,INT64_MAX-5000000));
    assert(stream_bitrate_meter_add(&meter,79900,INT64_MAX)==128);
#if SIZE_MAX > UINT32_MAX
    meter=(stream_bitrate_meter_t){0};
    size_t maximum=(size_t)(UINT64_MAX/8000000);
    assert(!stream_bitrate_meter_add(&meter,maximum,0));
    assert(!stream_bitrate_meter_add(&meter,1,1) && !meter.audio_bytes);
    assert(!stream_bitrate_meter_add(&meter,SIZE_MAX,2) && !meter.audio_bytes);
    assert(meter.started_us==2);
#endif
    puts("PASS stream bitrate: zero epoch, exact deadline, independent windows, clock reversal, rounding and bounded counters");
    return 0;
}
