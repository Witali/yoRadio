#include <assert.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "native_state.h"

#ifndef C3_HAS_PRIORITY
// Keep the old public API executable for negative controls. This adapter adds
// no ordering: the old implementation unconditionally assigns the bitrate.
typedef enum {
    NATIVE_BITRATE_NONE, NATIVE_BITRATE_ICY, NATIVE_BITRATE_DECODER, NATIVE_BITRATE_MEASURED
} native_bitrate_source_t;
static void native_state_publish_bitrate(native_state_t *state, uint32_t generation,
                                         uint32_t kbps, native_bitrate_source_t source) {
    (void)source;native_state_set_bitrate(state,generation,kbps);
}
#endif

static native_state_t state;
static native_state_t *s_state=&state;
static atomic_uint s_generation;
static int64_t now_us;
static void (*before_take)(void), (*after_generation_load)(void), (*after_ready_load)(void);
static int64_t esp_timer_get_time(void) {return now_us;}
static void invoke_once(void (**slot)(void)) {
    if (*slot) {void (*hook)(void)=*slot;*slot=NULL;hook();}
}
static unsigned load_generation(const atomic_uint *value) {
    unsigned result=atomic_load_explicit(value,memory_order_seq_cst);
    invoke_once(&after_generation_load);return result;
}
static bool load_ready(const atomic_bool *value) {
    bool result=atomic_load_explicit(value,memory_order_seq_cst);
    invoke_once(&after_ready_load);return result;
}
#undef atomic_load
#define atomic_load(p) _Generic((p), atomic_uint *:load_generation, atomic_bool *:load_ready)(p)
#define ESP_LOGI(...) ((void)0)
#include "production.inc"

SemaphoreHandle_t xSemaphoreCreateMutex(void) {
    SemaphoreHandle_t mutex=malloc(sizeof(*mutex));
    assert(mutex && !pthread_mutex_init(mutex,NULL));return mutex;
}
int xSemaphoreTake(SemaphoreHandle_t mutex,unsigned timeout) {
    (void)timeout;invoke_once(&before_take);
    assert(!pthread_mutex_lock(mutex));return pdTRUE;
}
void xSemaphoreGive(SemaphoreHandle_t mutex) {assert(!pthread_mutex_unlock(mutex));}
size_t strlcpy(char *to,const char *from,size_t capacity) {
    size_t size=strlen(from);
    if (capacity) {size_t copy=size<capacity ? size : capacity-1;memcpy(to,from,copy);to[copy]=0;}
    return size;
}
static void init(void) {
    native_state_init(&state);atomic_init(&s_generation,1);
    native_state_begin_stream(&state,1);reset_decoder_bitrate_tracking();
    now_us=1;
#ifndef C3_HAS_PRIORITY
    atomic_store(&s_measured_bitrate_ready,false);
#endif
}
static void finish(void) {assert(!pthread_mutex_destroy(state.lock));free(state.lock);}
static void begin_next_generation(void) {
    atomic_store(&s_generation,2);native_state_begin_stream(&state,2);
#ifndef C3_HAS_PRIORITY
    // This is the readiness reset performed by the actual old Play path.
    atomic_store(&s_measured_bitrate_ready,false);
#endif
}
static void old_meter_generation(void) {
    stream_bitrate_meter_t meter={0};
    stream_bitrate_add(1,&meter,40000);now_us=5000001;
#ifdef C3_HAS_PRIORITY
    before_take=begin_next_generation;
#else
    after_generation_load=begin_next_generation;
#endif
    // The old stream was current at its precheck, then a new Play starts.
    stream_bitrate_add(1,&meter,40000);
    state_set_decoder_bitrate(2,64000);
    assert(state.audio_generation==2 && state.bitrate_kbps==64);
}
static stream_bitrate_meter_t pending_meter;
static void publish_measured(void) {stream_bitrate_add(1,&pending_meter,50000);}
static void decoder_measured_preemption(void) {
    stream_bitrate_add(1,&pending_meter,50000);now_us=5000001;
#ifdef C3_HAS_PRIORITY
    before_take=publish_measured;
#else
    after_ready_load=publish_measured;
#endif
    // A measured result arrives after the decoder's earlier readiness test.
    state_set_decoder_bitrate(1,128000);
    assert(state.bitrate_kbps==160);
}
static void decoder_rounding(void) {
    state_set_decoder_bitrate(1,UINT32_MAX);
    assert(state.bitrate_kbps==4294967);
}
static void meter_rounding(void) {
    stream_bitrate_meter_t meter={0};
    stream_bitrate_add(1,&meter,1);now_us=5000001;
    stream_bitrate_add(1,&meter,2684354399U);
    assert(state.bitrate_kbps==4294967);
}
static void meter_clock_zero(void) {
    stream_bitrate_meter_t meter={0};now_us=0;
    stream_bitrate_add(1,&meter,40000);now_us=5000000;
    stream_bitrate_add(1,&meter,40000);
    assert(state.bitrate_kbps==128);
}
static void decoder_clock_zero(void) {
    now_us=0;state_set_decoder_bitrate(1,128000);
    now_us=1;state_set_decoder_bitrate(1,64000);
    assert(state.bitrate_kbps==128);
    now_us=1000000;state_set_decoder_bitrate(1,64000);
    assert(state.bitrate_kbps==64);
}
static void priority_and_generation(void) {
    native_state_publish_bitrate(&state,1,96,NATIVE_BITRATE_ICY);
    assert(state.bitrate_kbps==96);
    state_set_decoder_bitrate(1,128000);assert(state.bitrate_kbps==128);
    native_state_publish_bitrate(&state,1,80,NATIVE_BITRATE_ICY);
    assert(state.bitrate_kbps==128);
    native_state_publish_bitrate(&state,1,160,NATIVE_BITRATE_MEASURED);
    now_us+=2000000;state_set_decoder_bitrate(1,192000);
    assert(state.bitrate_kbps==160);
    native_state_publish_bitrate(&state,1,176,NATIVE_BITRATE_MEASURED);
    assert(state.bitrate_kbps==176);
    native_state_publish_bitrate(&state,1,0,NATIVE_BITRATE_MEASURED);
    native_state_publish_bitrate(&state,1,999,(native_bitrate_source_t)99);
    assert(state.bitrate_kbps==176);
    begin_next_generation();assert(!state.bitrate_kbps);
    state_set_decoder_bitrate(2,192000);assert(state.bitrate_kbps==192);
    native_state_publish_bitrate(&state,1,999,NATIVE_BITRATE_MEASURED);
    assert(state.bitrate_kbps==192);
    state.audio_generation=UINT32_MAX;atomic_store(&s_generation,0);
    native_state_begin_stream(&state,0);
    state_set_decoder_bitrate(0,192000);
    assert(state.audio_generation==0 && state.bitrate_kbps==192);
    native_state_set_audio(&state,0,false,"stopped");
    assert(!state.bitrate_kbps);
#ifdef C3_HAS_PRIORITY
    assert(state.bitrate_source==NATIVE_BITRATE_NONE);
#endif
}
static void *writer(void *identity) {
    native_bitrate_source_t source=(native_bitrate_source_t)(uintptr_t)identity;
    uint32_t bitrate=source==NATIVE_BITRATE_MEASURED ? 96 : 999;
    for (unsigned i=0;i<10000;++i) {
        native_state_publish_bitrate(&state,1,bitrate,source);
        native_state_publish_bitrate(&state,0,888,NATIVE_BITRATE_MEASURED);
        native_state_t snapshot;native_state_snapshot(&state,&snapshot);
        assert(snapshot.audio_generation==1 && snapshot.bitrate_kbps==96);
    }
    return NULL;
}
static void concurrent_priority(void) {
    native_state_publish_bitrate(&state,1,96,NATIVE_BITRATE_MEASURED);
    pthread_t writers[3];
    for (uintptr_t i=0;i<3;++i)
        assert(!pthread_create(&writers[i],NULL,writer,(void *)(i+1)));
    for (unsigned i=0;i<3;++i)assert(!pthread_join(writers[i],NULL));
}
int main(int argc,char **argv) {
    assert(argc==2);init();
    if (!strcmp(argv[1],"old-meter-generation"))old_meter_generation();
    else if (!strcmp(argv[1],"decoder-measured-preemption"))decoder_measured_preemption();
    else if (!strcmp(argv[1],"decoder-rounding"))decoder_rounding();
    else if (!strcmp(argv[1],"meter-rounding"))meter_rounding();
    else if (!strcmp(argv[1],"meter-clock-zero"))meter_clock_zero();
    else if (!strcmp(argv[1],"decoder-clock-zero"))decoder_clock_zero();
    else if (!strcmp(argv[1],"priority-and-generation"))priority_and_generation();
    else if (!strcmp(argv[1],"concurrent-priority"))concurrent_priority();
    else assert(!"unknown case");
    finish();printf("PASS C3 bitrate %s; ASan/UBSan\n",argv[1]);return 0;
}
