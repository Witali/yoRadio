/* Real selector/planner contracts and current-source worker failure publication. */
static void test_photo_prefetch_policy(void)
{
    /* A ready first photo must not wait for four unrelated missing caches.
     * Later missing sources remain in round-robin order, never skipped toward
     * an already cached later slot. No new producer starts during a fade. */
    factory_photo_t state={0};factory_photo_action_t action;
    CHECK(factory_photo_prefetch(&state,31,31,0,0)==0);
    CHECK(factory_photo_prefetch(&state,31,31,1,0)==-1);
    for(unsigned phase=0;phase<6;++phase) {
        CHECK(state.fade==phase);
        CHECK(factory_photo_prefetch(&state,31,31,1,0)==-1);
        factory_photo_step(&state,31,1,true,false,&action);
        CHECK(action.set_duty);
        CHECK(action.photo==(phase==2 ? 0:-2));
    }
    CHECK(state.fade==0 && state.next_slot==1 && action.finished);
    CHECK(factory_photo_prefetch(&state,31,31,1,0)==1);
    CHECK(factory_photo_prefetch(&state,31,31,9,0)==1); /* Do not jump to ready slot3. */
    factory_photo_step(&state,31,9,true,true,&action);
    CHECK(state.fade==0 && state.next_slot==1 && !action.set_duty && action.photo==-2);
    CHECK(factory_photo_prefetch(&state,31,31,9,2)==2); /* Stable rejection of slot1. */
    CHECK(factory_photo_prefetch(&state,31,29,9,0)==2); /* Empty source slot1. */
    CHECK(factory_photo_prefetch(&state,10,31,1,0)==1);
    CHECK(factory_photo_prefetch(&state,10,31,1,2)==3);
    CHECK(factory_photo_prefetch(&state,10,31,8,2)==-1);
    CHECK(factory_photo_prefetch(&state,0,31,0,0)==-1);
    CHECK(factory_photo_prefetch(&state,31,0,0,0)==-1);
    CHECK(factory_photo_prefetch(&state,31,31,0,31)==-1);
    state=(factory_photo_t){.fade=2,.next_slot=4};
    CHECK(factory_photo_prefetch(&state,3,31,2,0)==0); /* Wrap without skipping slot0. */
    CHECK(factory_photo_prefetch(&state,3,31,1,0)==-1);
    factory_photo_step(&state,3,1,true,false,&action);
    CHECK(action.photo==0 && state.next_slot==1 && state.fade==3);
    for(unsigned phase=1;phase<6;++phase)if(phase!=2) {
        state=(factory_photo_t){.fade=(uint8_t)phase,.next_slot=1};
        CHECK(factory_photo_prefetch(&state,31,31,0,0)==-1);
    }
    state=(factory_photo_t){.fade=2,.next_slot=3};
    CHECK(factory_photo_prefetch(&state,31,31,0,31)==-1);
    factory_photo_step(&state,31,0,true,false,&action);
    CHECK(action.photo==-1 && state.next_slot==3 && state.fade==3);
}

static void test_photo_prefetch_failed_source(void)
{
    /* The scheduler can skip a stable damaged source, while source replacement,
     * transient faults and cancellation must not permanently hide a valid one. */
    tv_settings_t settings;settings_snapshot(&settings);uint32_t length=settings.photo_size[0];
    uint8_t saved[2];memcpy(saved,flash_bytes,sizeof(saved));CHECK(length>4);
    photo_worker_forget(0);photo_diagnostic_t diagnostic;
    CHECK(photo_worker_invalidate(0,&diagnostic)==ESP_OK);
    flash_bytes[0]=0; /* Deliberate source-corruption fixture, not production I/O. */
    photo_test_gate_t gate;LONG received=photo_test_begin_hold(&gate);
    photo_worker_request(0);photo_test_end_hold(&gate,received+2);
    CHECK(!(media_photo_ready_mask()&1));CHECK(media_photo_failed_mask()&1);
    factory_photo_t next={0};
    CHECK(factory_photo_prefetch(&next,31,31,0,media_photo_failed_mask())==1);
    CHECK(settings_photo_size(0,length-1)==ESP_OK);
    CHECK(!(media_photo_failed_mask()&1)); /* An obsolete failed length is not current. */
    CHECK(settings_photo_size(0,length)==ESP_OK);
    memcpy(flash_bytes,saved,sizeof(saved));photo_worker_forget(0);
    CHECK(!(media_photo_failed_mask()&1));
    received=InterlockedCompareExchange(&photo_test_queue->receive_entered,0,0);
    photo_worker_request(0);photo_test_drain(received+1);
    CHECK(media_photo_ready_mask()&1);CHECK(!(media_photo_failed_mask()&1));
}

static void test_photo_prefetch_cancel_retry(void)
{
    /* A queued foreground request cancels an earlier background warm-up, but
     * must neither publish stale readiness nor permanently reject that source. */
    photo_worker_forget(0);photo_diagnostic_t diagnostic;
    CHECK(photo_worker_invalidate(0,&diagnostic)==ESP_OK);
    photo_test_gate_t gate;LONG received=photo_test_begin_hold(&gate);
    photo_worker_request(0);
    CHECK(photo_worker_submit(photo_test_count,(void *)&gate.calls)==ESP_OK);
    uint64_t programs=cache_program_bytes,erases=cache_erases;
    photo_test_end_hold(&gate,received+3);
    CHECK(gate.calls==1 && !(media_photo_ready_mask()&1) && !(media_photo_failed_mask()&1));
    CHECK(cache_program_bytes==programs && cache_erases==erases);
    received=InterlockedCompareExchange(&photo_test_queue->receive_entered,0,0);
    photo_worker_request(0);photo_test_drain(received+1);
    CHECK(media_photo_ready_mask()&1);
}
