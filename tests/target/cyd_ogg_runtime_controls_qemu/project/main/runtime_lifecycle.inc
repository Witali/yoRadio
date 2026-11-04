// Typed runtime controls. Healthy EOF and allocation-error terminals have
// separate, predeclared source extents; no positive-harness guard is changed.
static const char *runtime_id,*runtime_leg;
static unsigned runtime_terminals,runtime_healthy,runtime_errors,runtime_cancelled;
static native_health_faults_t runtime_before;
static int runtime_expected_allocation_detail(runtime_mode_t mode) {
    // OFP/decoder workspace failures retain the requested byte count as their
    // detail. OGP_MEMORY is a separate status, not the recorded health result.
    return mode==RC_DUAL_OOM?15360:mode==RC_SCRATCH_OOM?23040:0;
}
template<class Predicate> static void runtime_wait(Predicate predicate,const char *reason) {
    const int64_t deadline=esp_timer_get_time()+30000000;
    while(!predicate()){check(esp_timer_get_time()<deadline,reason);vTaskDelay(1);}
}
static void runtime_begin(const char *id,const char *leg,const fixture_t &fixture,size_t prefix,runtime_mode_t mode,unsigned target_link=0) {
    active=&fixture;expected_links=prefix;runtime_id=id;runtime_leg=leg;++runtime_epoch;
    configure(false);runtime_before=native_health_snapshot().faults;runtime_arm(mode,target_link,mode==RC_DUAL_OOM?prefix:0);
    printf("CYD_RC_BEGIN epoch=%u id=%s leg=%s fixture=%s expected_links=%u actual_links=%u expected_pcm=%u expected_mono=%u mode=%u target_link=%u expected_detail=%d ordinary_deadline_ms=30000 normalizer_enabled=0\n",
        runtime_epoch.load(),id,leg,active->name,(unsigned)expected_links,(unsigned)active->count,(unsigned)full_pcm(),(unsigned)full_mono(),(unsigned)mode,target_link,runtime_expected_allocation_detail(mode));
}
static void runtime_play() {check(audio_service_play("http://fixture/runtime-control",NATIVE_CODEC_AUTO)==ESP_OK,"real_public_runtime_play");}
static void runtime_quiet() {
    runtime_wait([]{return !live_clients && !live_decoders && input_quiet() && runtime_ring_sends==runtime_ring_receives && runtime_ring_receives==runtime_ring_returns;},"bounded_real_HTTP_decoder_input_PCM_cleanup");
    check(!word_alloc_live && !word_alloc_live_bytes && !pressure_count && !pressure_bytes && heap_caps_check_integrity_all(true),"all_real_storage_owners_quiet_and_heap_intact");
}
static void runtime_terminal(bool allocation_error) {
    runtime_wait([]{return (xEventGroupGetBits(events)&ENDED)!=0;},"bounded_typed_terminal_flush");runtime_quiet();
    runtime_wait([allocation_error]{auto s=snapshot();return !s.audio_running && !s.audio_pending && !s.audio_failed &&
        !strcmp(s.stream_format,allocation_error?"decoder allocation failed":"stream ended");},"actual_public_typed_terminal_status");
    runtime_pressure_witness();runtime_trace_drain();auto faults=native_health_snapshot().faults;
    const int expected_detail=runtime_expected_allocation_detail(runtime_mode);
    printf("CYD_RC_HEALTH epoch=%u id=%s leg=%s generation=%u expected_detail=%d callbacks_seen=%u before_decoder_failures=%u before_stream_failures=%u before_output_failures=%u before_allocation_failures=%u "
        "allocation_failures=%u allocation_size=%u allocation_caps=%u decoder_failures=%u decoder_generation=%u decoder_codec=%u decoder_stage=%u decoder_result=%d decoder_completion=%u decoder_input_bytes=%u decoder_allocation_sequence=%u "
        "stream_failures=%u stream_generation=%u stream_completion=%u stream_result=%d output_failures=%u output_generation=%u output_stage=%u output_write_errors=%u output_configure_errors=%u output_flush_errors=%u output_result=%d\n",
        runtime_epoch.load(),runtime_id,runtime_leg,(unsigned)session_generation.load(),expected_detail,runtime_callback_count(),
        (unsigned)runtime_before.decoder_failures,(unsigned)runtime_before.stream_failures,(unsigned)runtime_before.output_failures,(unsigned)runtime_before.allocation_failures,
        (unsigned)faults.allocation_failures,(unsigned)faults.allocation_size,(unsigned)faults.allocation_caps,
        (unsigned)faults.decoder_failures,(unsigned)faults.decoder_generation,(unsigned)faults.decoder_codec,(unsigned)faults.decoder_stage,(int)faults.decoder_result,
        (unsigned)faults.decoder_completion,(unsigned)faults.decoder_input_bytes,(unsigned)faults.decoder_allocation_sequence,
        (unsigned)faults.stream_failures,(unsigned)faults.stream_generation,(unsigned)faults.stream_completion,(int)faults.stream_result,
        (unsigned)faults.output_failures,(unsigned)faults.output_generation,(unsigned)faults.output_stage,(unsigned)faults.output_write_errors,
        (unsigned)faults.output_configure_errors,(unsigned)faults.output_flush_errors,(int)faults.output_result);
    check(fflush(stdout)==0,"complete_health_snapshot_before_any_health_assertion");
    check((expected_detail!=0)==allocation_error,"predeclared_allocation_error_detail");
    check(faults.decoder_failures==runtime_before.decoder_failures+(allocation_error?1u:0u) &&
        faults.stream_failures==runtime_before.stream_failures && faults.output_failures==runtime_before.output_failures,
        "only_predeclared_decoder_allocation_terminal");
    if(allocation_error)check(faults.decoder_generation==session_generation && faults.decoder_completion==9 &&
        faults.decoder_stage==NATIVE_HEALTH_PROCESS && faults.decoder_result==expected_detail &&
        faults.decoder_allocation_sequence==faults.allocation_failures && faults.allocation_failures==runtime_callback_count(),
        "exact_public_allocation_failure_health_cause");
    ++runtime_terminals;if(allocation_error)++runtime_errors;else ++runtime_healthy;
    auto s=snapshot();
    printf("CYD_RC_TERMINAL epoch=%u id=%s leg=%s generation=%u allocation_error=%u links=%u pcm_bytes=%u mono_bytes=%u wire_bytes=%u padding_bytes=%u padding_blocks=%u sha256=%s render_sha256=%s running=%u pending=%u failed=%u decoder_delta=%u stream_delta=%u output_delta=%u allocation_delta=%u live_clients=%u live_decoders=%u word_live=%u pressure_live=%u ring_sends=%u ring_receives=%u ring_returns=%u heap_integrity=1\n",
        runtime_epoch.load(),runtime_id,runtime_leg,(unsigned)session_generation.load(),(unsigned)allocation_error,(unsigned)expected_links,
        (unsigned)pcm_bytes.load(),(unsigned)render_bytes,(unsigned)render_wire_bytes,(unsigned)final_padding_bytes,(unsigned)final_padding_seen,completed_sha,render_sha,
        (unsigned)s.audio_running,(unsigned)s.audio_pending,(unsigned)s.audio_failed,
        (unsigned)(faults.decoder_failures-runtime_before.decoder_failures),(unsigned)(faults.stream_failures-runtime_before.stream_failures),
        (unsigned)(faults.output_failures-runtime_before.output_failures),(unsigned)(faults.allocation_failures-runtime_before.allocation_failures),
        live_clients.load(),live_decoders.load(),word_alloc_live.load(),pressure_count,runtime_ring_sends.load(),runtime_ring_receives.load(),runtime_ring_returns.load());
    check(fflush(stdout)==0,"typed_terminal_record_retained");
}
static void runtime_blocked() {
    runtime_wait([]{return runtime_gate_held && runtime_ring_timeouts>=runtime_timeout_base+2;},"two_real_PCM_ring_timeouts_before_control");
    check(!(xEventGroupGetBits(events)&ENDED) && pcm_bytes && pcm_bytes<full_pcm(),"real_held_borrowed_write_before_eof");
    printf("CYD_RC_BLOCKED epoch=%u id=%s generation=%u timeout_base=%u timeouts=%u ring_bytes=8192 gate_held=1 before_real_renderer=1 live_decoders=%u observed_us=%llu\n",
        runtime_epoch.load(),runtime_id,(unsigned)session_generation.load(),runtime_timeout_base,runtime_ring_timeouts.load(),live_decoders.load(),(unsigned long long)esp_timer_get_time());
}
static void runtime_cancel_quiet(unsigned before_discard,uint32_t old_generation,const char *kind) {
    runtime_wait([before_discard]{return discard_calls==before_discard+1 && !runtime_gate_held;},"bounded_real_discard_after_public_cancel");runtime_quiet();
    unsigned generation=snapshot().audio_generation;check(generation==old_generation+1,"public_cancel_advances_generation_once");
    size_t source=pcm_bytes.load(),mono=render_bytes;unsigned written=writes.load(),driver_count=driver_writes.load();
    int64_t quiet_started=esp_timer_get_time();vTaskDelay(pdMS_TO_TICKS(25));
    check(discard_calls==before_discard+1 && source==pcm_bytes && mono==render_bytes && written==writes && driver_count==driver_writes &&
        !live_clients && !live_decoders && input_quiet() && !(xEventGroupGetBits(events)&ENDED),"no_stale_activity_after_real_discard_quiet_fence");
    auto faults=native_health_snapshot().faults;
    check(faults.decoder_failures==runtime_before.decoder_failures && faults.stream_failures==runtime_before.stream_failures &&
        faults.output_failures==runtime_before.output_failures,"public_cancellation_introduces_no_pipeline_failure");
    runtime_trace_drain();++runtime_cancelled;
    printf("CYD_RC_CANCEL_QUIET epoch=%u id=%s kind=%s quiet_start_us=%llu time_us=%llu old_generation=%u generation=%u discard_before=%u discard_after=%u pcm_bytes=%u mono_bytes=%u writes=%u driver_writes=%u quiet_ms=25 no_eof=1 all_owners_quiet=1 ring_sends=%u ring_receives=%u ring_returns=%u\n",
        runtime_epoch.load(),runtime_id,kind,(unsigned long long)quiet_started,(unsigned long long)esp_timer_get_time(),(unsigned)old_generation,generation,before_discard,discard_calls.load(),(unsigned)source,(unsigned)mono,written,driver_count,runtime_ring_sends.load(),runtime_ring_receives.load(),runtime_ring_returns.load());
}
static void runtime_cases() {
    runtime_begin("BYTE_FALLBACK","CONTROL",lifecycles[2],1,RC_BYTE_FALLBACK);runtime_play();runtime_terminal(false);

    runtime_begin("DUAL_OOM","CONTROL",chains[1],2,RC_DUAL_OOM,2);runtime_play();runtime_terminal(true);
    runtime_begin("DUAL_OOM","REOPEN",chains[1],chains[1].count,RC_NONE);runtime_play();runtime_terminal(false);

    runtime_begin("SCRATCH_OOM","CONTROL",lifecycles[4],0,RC_SCRATCH_OOM);runtime_play();runtime_terminal(true);
    runtime_begin("SCRATCH_OOM","REOPEN",lifecycles[4],1,RC_NONE);runtime_play();runtime_terminal(false);

    runtime_begin("RING_RELEASE","CONTROL",lifecycles[2],1,RC_NONE);runtime_arm_gate(false);runtime_play();runtime_blocked();
    runtime_gate_release=true;runtime_terminal(false);

    runtime_begin("RING_STOP","CONTROL",lifecycles[2],1,RC_NONE);runtime_arm_gate(false);runtime_play();runtime_blocked();cancelling=true;
    unsigned before_discard=discard_calls.load();uint32_t old_generation=snapshot().audio_generation;
    printf("CYD_RC_STOP_REQUEST epoch=%u generation=%u time_us=%llu\n",runtime_epoch.load(),(unsigned)old_generation,(unsigned long long)esp_timer_get_time());
    audio_service_stop();
    printf("CYD_RC_STOP_RETURN epoch=%u generation=%u time_us=%llu real_returned=1\n",runtime_epoch.load(),(unsigned)snapshot().audio_generation,(unsigned long long)esp_timer_get_time());
    runtime_gate_release=true;runtime_cancel_quiet(before_discard,old_generation,"STOP");
    check(!strcmp(snapshot().stream_format,"stopped"),"actual_stopped_state");
    runtime_begin("RING_STOP","REOPEN",lifecycles[2],1,RC_NONE);runtime_play();runtime_terminal(false);

    runtime_begin("RING_MAINTENANCE","CONTROL",lifecycles[2],1,RC_NONE);runtime_arm_gate(true);runtime_play();runtime_blocked();cancelling=true;
    before_discard=discard_calls.load();old_generation=snapshot().audio_generation;audio_maintenance_token_t token={};
    check(audio_service_maintenance_begin(10000,&token)==ESP_OK && token.epoch,"real_all_owner_maintenance_after_blocked_ring");
    runtime_cancel_quiet(before_discard,old_generation,"MAINTENANCE");
    check(!driver.live && audio_service_play("http://fixture/blocked",NATIVE_CODEC_OGG)==ESP_ERR_INVALID_STATE,"real_held_driver_and_play_guard");
    auto stale=token;
    runtime_begin("RING_MAINTENANCE","RESUME",lifecycles[2],1,RC_NONE);
    check(audio_service_maintenance_end(&token,true)==ESP_OK && !token.epoch,"real_resume_consumes_token");
    check(audio_service_maintenance_end(&stale,true)==ESP_ERR_INVALID_STATE,"stale_resume_token_rejected");runtime_terminal(false);
}
static void runtime_final() {
    auto faults=native_health_snapshot().faults;unsigned callbacks=runtime_callback_count();
    runtime_trace_drain();
    check(callbacks==faults.allocation_failures,"every_actual_failed_allocation_callback_forwarded_to_production_health");
    check(runtime_terminals==8 && runtime_healthy==6 && runtime_errors==2 && runtime_cancelled==2 && opens==closes &&
        http_opens==http_cleanup && !live_clients && !live_decoders && !driver.live && driver_created==driver_deleted &&
        runtime_ring_sends==runtime_ring_receives && runtime_ring_receives==runtime_ring_returns && total_writes==layout_stamps && total_writes==gain_stamps && total_writes==metadata_checks && input_quiet() &&
        faults.decoder_failures==2 && !faults.stream_failures && !faults.output_failures && !public_failures &&
        pressure_allocations==pressure_frees && !pressure_count && !pressure_bytes && heap_caps_check_integrity_all(true),"complete_bounded_runtime_control_owner_census");
    printf("CYD_RC_COMPLETE controls=6 source_writes=%u layout_stamps=%u gain_stamps=%u terminals=%u healthy=%u allocation_errors=%u cancelled=%u opens=%u closes=%u HTTP_opens=%u HTTP_cleanup=%u callbacks=%u decoder_failures=%u stream_failures=%u output_failures=%u allocation_failures=%u pressure_allocations=%u pressure_frees=%u pressure_peak_blocks=%u pressure_peak_bytes=%u static_pressure_bytes=%u static_callback_bytes=%u static_alloc_event_bytes=%u ring_sends=%u ring_receives=%u ring_returns=%u diagnostic_delays=1 normalizer_enabled=0 enabled_normalizer_qualified=0 private_heap=0 actual_allocators=1 hardware=0 post_output_oracle_pending=1\n",
        total_writes.load(),layout_stamps.load(),gain_stamps.load(),runtime_terminals,runtime_healthy,runtime_errors,runtime_cancelled,opens.load(),closes.load(),http_opens.load(),http_cleanup.load(),callbacks,
        (unsigned)faults.decoder_failures,(unsigned)faults.stream_failures,(unsigned)faults.output_failures,(unsigned)faults.allocation_failures,
        pressure_allocations,pressure_frees,pressure_peak,pressure_peak_bytes,(unsigned)sizeof(pressure_blocks),(unsigned)sizeof(callback_events),(unsigned)sizeof(allocation_events),
        runtime_ring_sends.load(),runtime_ring_receives.load(),runtime_ring_returns.load());
}
