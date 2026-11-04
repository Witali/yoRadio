// Real SDK ring operations, observed without queue mutation or fake returns.
static RingbufHandle_t runtime_pcm_ring;
static std::atomic<bool> runtime_gate_armed,runtime_gate_held,runtime_gate_release,runtime_release_on_pause;
static std::atomic<unsigned> runtime_ring_timeouts,runtime_ring_sends,runtime_ring_receives,runtime_ring_returns;
static unsigned runtime_timeout_base;
extern "C" RingbufHandle_t __real_xRingbufferCreate(size_t,RingbufferType_t);
extern "C" BaseType_t __real_xRingbufferSendAcquire(RingbufHandle_t,void **,size_t,TickType_t);
extern "C" BaseType_t __real_xRingbufferSendComplete(RingbufHandle_t,void *);
extern "C" void *__real_xRingbufferReceive(RingbufHandle_t,size_t *,TickType_t);
extern "C" void __real_vRingbufferReturnItem(RingbufHandle_t,void *);
extern "C" RingbufHandle_t __wrap_xRingbufferCreate(size_t bytes,RingbufferType_t kind) {
    RingbufHandle_t ring=__real_xRingbufferCreate(bytes,kind);
    if(bytes==8192 && kind==RINGBUF_TYPE_NOSPLIT) {
        check(ring && !runtime_pcm_ring,"one_original_8192_byte_PCM_ring");runtime_pcm_ring=ring;
        printf("CYD_RC_RING_CREATE bytes=8192 nosplit=1 max_item=%u real_returned=1\n",(unsigned)xRingbufferGetMaxItemSize(ring));
    }
    return ring;
}
extern "C" BaseType_t __wrap_xRingbufferSendAcquire(RingbufHandle_t ring,void **item,size_t bytes,TickType_t ticks) {
    const bool observed=ring==runtime_pcm_ring && runtime_pcm_ring;
    if(observed)check(bytes && bytes<=xRingbufferGetMaxItemSize(ring) && ticks==pdMS_TO_TICKS(50),"valid_real_PCM_acquire_geometry_and_original_retry");
    const size_t free_before=observed?xRingbufferGetCurFreeSize(ring):0;
    TickType_t before=xTaskGetTickCount();int64_t started=esp_timer_get_time();
    BaseType_t result=__real_xRingbufferSendAcquire(ring,item,bytes,ticks);
    if(observed && result==pdFALSE) {
        TickType_t elapsed=xTaskGetTickCount()-before;
        const int64_t elapsed_us=esp_timer_get_time()-started;
        const size_t free_after=xRingbufferGetCurFreeSize(ring);
        const bool gate_held=runtime_gate_held.load();
        check(elapsed+1>=ticks,"genuine_fifty_ms_acquire_wait_not_oversize_refusal");
        unsigned ordinal=++runtime_ring_timeouts;
        printf("CYD_RC_RING_TIMEOUT ordinal=%u generation=%u gate_held=%u bytes=%u wait_ticks=%u elapsed_ticks=%u elapsed_us=%llu free_before=%u free_after=%u max_item=%u real_result=%d core=%u priority=%u\n",
            ordinal,(unsigned)session_generation.load(),(unsigned)gate_held,(unsigned)bytes,(unsigned)ticks,(unsigned)elapsed,
            (unsigned long long)elapsed_us,(unsigned)free_before,(unsigned)free_after,(unsigned)xRingbufferGetMaxItemSize(ring),(int)result,(unsigned)xPortGetCoreID(),(unsigned)uxTaskPriorityGet(nullptr));
    }
    return result;
}
extern "C" BaseType_t __wrap_xRingbufferSendComplete(RingbufHandle_t ring,void *item) {
    BaseType_t result=__real_xRingbufferSendComplete(ring,item);
    if(ring==runtime_pcm_ring){check(result==pdTRUE,"genuine_acquired_PCM_send_complete");++runtime_ring_sends;}return result;
}
extern "C" void *__wrap_xRingbufferReceive(RingbufHandle_t ring,size_t *bytes,TickType_t ticks) {
    void *item=__real_xRingbufferReceive(ring,bytes,ticks);if(ring==runtime_pcm_ring && item)++runtime_ring_receives;return item;
}
extern "C" void __wrap_vRingbufferReturnItem(RingbufHandle_t ring,void *item) {
    __real_vRingbufferReturnItem(ring,item);if(ring==runtime_pcm_ring)++runtime_ring_returns;
}
static void runtime_output_gate() {
    if(!runtime_gate_armed.exchange(false))return;
    runtime_gate_held=true;
    printf("CYD_RC_GATE_HELD generation=%u time_us=%llu before_real_renderer=1 ring_bytes=8192 core=1 priority=6\n",(unsigned)session_generation.load(),(unsigned long long)esp_timer_get_time());
    const int64_t deadline=esp_timer_get_time()+30000000;
    while(!runtime_gate_release.load()){check(esp_timer_get_time()<deadline,"fixed_thirty_second_output_gate");vTaskDelay(1);}
    runtime_gate_held=false;
    printf("CYD_RC_GATE_RELEASE generation=%u time_us=%llu real_renderer_pending=1\n",(unsigned)session_generation.load(),(unsigned long long)esp_timer_get_time());
}
static void runtime_pause_forwarded(bool requested) {
    if(requested && runtime_release_on_pause.exchange(false)) {
        check(runtime_gate_held && runtime_ring_timeouts>=runtime_timeout_base+2,"maintenance_cancels_observed_real_ring_block");
        printf("CYD_RC_GATE_PAUSE generation=%u time_us=%llu real_pause_returned=1\n",(unsigned)session_generation.load(),(unsigned long long)esp_timer_get_time());
        runtime_gate_release=true;
    }
}
static void runtime_arm_gate(bool maintenance) {
    check(!runtime_gate_held,"prior_output_gate_quiet");runtime_timeout_base=runtime_ring_timeouts.load();
    runtime_gate_release=false;runtime_release_on_pause=maintenance;runtime_gate_armed=true;
}
