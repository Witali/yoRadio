/* Deterministic worker ordering and async request lifetime fault controls. */
typedef struct {HANDLE entered,release;volatile LONG calls;} photo_test_gate_t;

static void photo_test_hold(void *context)
{
    /* An event freezes the queue consumer; no timing-dependent scheduling guess. */
    photo_test_gate_t *gate=context;
    SetEvent(gate->entered);assert(WaitForSingleObject(gate->release,10000)==WAIT_OBJECT_0);
}

static void photo_test_count(void *context)
{
    /* Count only accepted closures, so a rejected context remains caller-owned. */
    InterlockedIncrement((LONG *)context);
}

static LONG photo_test_begin_hold(photo_test_gate_t *gate)
{
    /* Wait for the real worker to enter an owned closure before queuing rivals. */
    *gate=(photo_test_gate_t){CreateEventW(NULL,TRUE,FALSE,NULL),CreateEventW(NULL,TRUE,FALSE,NULL),0};
    CHECK(gate->entered && gate->release);
    CHECK(photo_worker_submit(photo_test_hold,gate)==ESP_OK);
    CHECK(WaitForSingleObject(gate->entered,5000)==WAIT_OBJECT_0);
    return InterlockedCompareExchange(&photo_test_queue->receive_entered,0,0);
}

static void photo_test_drain(LONG last_receive)
{
    /* Next receive begins only after every previous closure/background job exits. */
    ULONGLONG deadline=GetTickCount64()+10000;
    while(InterlockedCompareExchange(&photo_test_queue->receive_entered,0,0)<last_receive) {
        CHECK(GetTickCount64()<deadline);
        CHECK(WaitForSingleObject(photo_test_queue->changed,1000)==WAIT_OBJECT_0 || GetTickCount64()<deadline);
    }
}

static void photo_test_end_hold(photo_test_gate_t *gate,LONG last_receive)
{
    /* Release the test gate, then observe completed jobs without another closure
     * accidentally cancelling the very background operation under examination. */
    SetEvent(gate->release);photo_test_drain(last_receive);
    CloseHandle(gate->entered);CloseHandle(gate->release);
}

static void test_photo_owner_lifetime(void)
{
    /* Failed begin, saturated queue and disconnected send must release all SDK
     * clones exactly once; rejected closures never execute or claim the source. */
    const char *start="{\"file_number\":5,\"file_size\":4096,\"total_chunks\":1}";
    InterlockedExchange(&async_begin_failure,1);post("/start_upload",start,500);
    CHECK(async_open==0 && !media_upload_active());InterlockedExchange(&async_begin_failure,0);
    photo_test_gate_t gate;LONG received=photo_test_begin_hold(&gate);
    for(unsigned i=0;i<4;++i)CHECK(photo_worker_submit(photo_test_count,(void *)&gate.calls)==ESP_OK);
    CHECK(photo_worker_submit(photo_test_count,(void *)&gate.calls)==ESP_ERR_NO_MEM);
    post("/start_upload",start,503);CHECK(async_open==0 && !media_upload_active());
    photo_test_end_hold(&gate,received+5);CHECK(gate.calls==4);
    const char *finish="{\"file_number\":5,\"file_name\":\"file5.jpg\"}";
    prepare("/finish_upload",finish,strlen(finish),"application/json");request.send_disconnected=true;
    dispatch(HTTP_POST);CHECK(async_send_failures==1 && async_open==0 && !media_upload_active());
    CHECK(get("/getclocktype")[0]!=0);
}

static int photo_test_row(void *context,uint32_t row,const uint16_t *pixels,uint32_t width)
{
    /* A stale source must never reach a consumer, including the synchronous API. */
    (void)row;(void)pixels;(void)width;++*(unsigned *)context;return 0;
}

static void test_photo_owner_stale(void)
{
    /* Queue a snapshot, replace the committed length before consumption, and
     * require zero cache writes and no ready publication for the obsolete job. */
    tv_settings_t settings;settings_snapshot(&settings);uint32_t length=settings.photo_size[0];CHECK(length>4);
    photo_test_gate_t gate;LONG received=photo_test_begin_hold(&gate);
    photo_worker_forget(0);photo_worker_request(0);
    photo_diagnostic_t diagnostic;CHECK(photo_worker_invalidate(0,&diagnostic)==ESP_OK);
    CHECK(settings_photo_size(0,length-1)==ESP_OK);
    uint64_t programs=cache_program_bytes,erases=cache_erases;
    photo_test_end_hold(&gate,received+2);
    CHECK(cache_program_bytes==programs && cache_erases==erases);
    CHECK(!(media_photo_ready_mask()&1));
    unsigned rows=0;
    CHECK(photo_worker_draw(0,length,true,photo_test_row,&rows)==ESP_ERR_INVALID_STATE);
    CHECK(rows==0 && cache_program_bytes==programs && cache_erases==erases);
    CHECK(settings_photo_size(0,length)==ESP_OK);
    CHECK(media_draw_photo(0)==ESP_OK);
    CHECK(media_photo_ready_mask()&1);
}

static void test_photo_owner_retry(void)
{
    /* A physical read error during privacy validation is temporary: the same
     * committed image must be queueable again without changing its source size. */
    photo_worker_forget(0);photo_diagnostic_t diagnostic;
    CHECK(photo_worker_invalidate(0,&diagnostic)==ESP_OK);
    photo_test_gate_t gate;LONG received=photo_test_begin_hold(&gate);
    source_read_fault_after=3;unsigned faults=source_read_faults;
    photo_worker_request(0);photo_test_end_hold(&gate,received+2);
    CHECK(source_read_faults==faults+1 && source_read_fault_after==0);
    CHECK(!(media_photo_ready_mask()&1));
    received=InterlockedCompareExchange(&photo_test_queue->receive_entered,0,0);
    photo_worker_request(0);photo_test_drain(received+1);
    CHECK(media_photo_ready_mask()&1);
}
