static void play(const char *url, native_codec_t codec = NATIVE_CODEC_OGG) {
    check(audio_service_play(url, codec) == ESP_OK, "actual_public_play");
}
static void complete() {
    wait_until([] { return (xEventGroupGetBits(events) & ENDED) != 0; }, "bounded_full_output_eof");
    wait_until([] { return !live_clients && !live_decoders && input_quiet(); }, "bounded_public_cleanup");
    wait_until([] {
        auto info = snapshot();
        return !info.audio_running && !info.audio_pending && !info.audio_failed && !strcmp(info.stream_format, "stream ended");
    }, "public_final_eof_state");
    check(heap_caps_check_integrity_all(true), "complete_heap_integrity");
}
static void held() {
    wait_until([] { return (xEventGroupGetBits(events) & (TRANSPORT_HELD | PCM_STARTED)) ==
                              (TRANSPORT_HELD | PCM_STARTED); }, "hold_after_actual_pcm");
    check(live_clients == 1 && live_decoders > 0 && pcm_bytes > 0 && pcm_bytes < full_pcm() &&
          client_position < (size_t)(fixture_bytes()), "genuine_partial_stream");
    check(!(xEventGroupGetBits(events) & ENDED), "partial_stream_not_flushed");
}
static void memory_record(const char *stage) {
    printf("CYD_F1_MEMORY fixture=%s stage=%s heap_free=%u heap_min=%u largest_internal=%u\n",
           active->name,stage,(unsigned)esp_get_free_heap_size(),(unsigned)esp_get_minimum_free_heap_size(),
           (unsigned)heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT));
}
static void print_full_result(const char *prefix) {
    printf("%s fixture=%s schedule=%u page_style=%u pcm_bytes=%u sha256=%s opens=%u closes=%u http_cleanup=%u writes=%u metadata=1\n",
           prefix,active->name,active->schedule,active->page_style,(unsigned)pcm_bytes.load(),completed_sha,opens.load(),closes.load(),http_cleanup.load(),writes.load());
    printf("CYD_F1_RENDER_CASE fixture=%s mono_bytes=%u wire_bytes=%u padding_bytes=%u padding_blocks=%u sha256=%s volume=%u\n",active->name,(unsigned)render_bytes,(unsigned)render_wire_bytes,(unsigned)final_padding_bytes,(unsigned)final_padding_seen,render_sha,(unsigned)active->volume);
    check(fflush(stdout)==0,"flush_case_record");memory_record("EOF_DONE");
}
static void lifecycle(const fixture_t &fixture) {
    active=&fixture;unsigned clients=http_cleanup.load();
    size_t maximum_page=active->links[0]->max_page;
    printf("CYD_F1_TASK_FIXTURE fixture=%s encoded=%u max_page=%u\n",
           active->name,(unsigned)fixture_bytes(),(unsigned)maximum_page);
    configure(false);play("http://fixture/T0",NATIVE_CODEC_AUTO);complete();
    check(closes==opens && http_cleanup==clients+1,"first_instance_cleanup");
    print_full_result("CYD_F1_TASK_CASE id=T0 ordered_eof=1");

    configure(true);play("http://fixture/T1-old");held();cancelling=true;
    unsigned before_discard=discard_calls.load();
    uint32_t before_generation=snapshot().audio_generation;
    int64_t stop_request_us=esp_timer_get_time();
    printf("CYD_F1_CONTROL_STOP_REQUEST fixture=%s time_us=%llu before_sequence=%u before_generation=%u core=0\n",
           active->name,(unsigned long long)stop_request_us,before_discard,(unsigned)before_generation);
    audio_service_stop();
    uint32_t stopped_generation=snapshot().audio_generation;
    printf("CYD_F1_CONTROL_STOP_RETURN fixture=%s time_us=%llu stop_generation=%u before_sequence=%u current_sequence=%u\n",
           active->name,(unsigned long long)esp_timer_get_time(),(unsigned)stopped_generation,before_discard,discard_calls.load());
    // Real discard has no generation parameter. Its contemporaneous public
    // snapshot may precede Stop's separate state publication. Correlate the
    // actual output-owner completion event to this request sequence instead.
    wait_until([before_discard] {return !live_clients && !live_decoders && discard_calls==before_discard+1 && input_quiet();},"stop_output_owner_and_public_cleanup");
    uint32_t discarded_generation=discard_generation.load();size_t stopped_pcm=pcm_bytes.load();
    check(stopped_generation==before_generation+1 && stopped_pcm>0 && stopped_pcm<full_pcm() &&
          !strcmp(snapshot().stream_format,"stopped") && !(xEventGroupGetBits(events)&ENDED),"stopped_partial_output");
    unsigned stopped_writes=writes.load(),stopped_driver=driver_writes.load();size_t stopped_mono=render_bytes;
    vTaskDelay(pdMS_TO_TICKS(25));
    auto stop_health=audio_service_input_health();auto stopped_state=snapshot();
    check(discard_calls==before_discard+1 && !live_clients && !live_decoders && input_quiet() &&
          pcm_bytes==stopped_pcm && render_bytes==stopped_mono && writes==stopped_writes && driver_writes==stopped_driver &&
          !(xEventGroupGetBits(events)&ENDED) && stopped_state.audio_generation==stopped_generation &&
          !stopped_state.audio_running && !stopped_state.audio_pending && !stopped_state.audio_failed &&
          !strcmp(stopped_state.stream_format,"stopped"),"real_stop_discard_and_all_owners_stay_quiet");
    printf("CYD_F1_CONTROL_STOP_QUIET fixture=%s time_us=%llu stop_generation=%u discard_sequence=%u discard_snapshot_generation=%u live_decoders=%u live_clients=%u input_available=%u input_leased=%u input_ready=%u input_reading=%u input_writing=%u pcm_bytes=%u mono_bytes=%u writes=%u driver_writes=%u quiet_ticks=25 no_eof=1\n",
           active->name,(unsigned long long)esp_timer_get_time(),(unsigned)stopped_generation,discard_calls.load(),(unsigned)discarded_generation,
           live_decoders.load(),live_clients.load(),(unsigned)stop_health.available,(unsigned)stop_health.leased,(unsigned)stop_health.ready,(unsigned)stop_health.reading,(unsigned)stop_health.writing,
           (unsigned)stopped_pcm,(unsigned)stopped_mono,stopped_writes,stopped_driver);
    memory_record("STOP_QUIET");configure(false);play("http://fixture/T1-reopen");complete();
    check(closes==opens && http_cleanup==clients+3,"stop_reopen_instance_cleanup");
    char prefix[256];
    snprintf(prefix,sizeof(prefix),"CYD_F1_TASK_CASE id=T1 stop_reopen=1 partial_pcm=%u stop_generation=%u discard_snapshot_generation=%u discard_after_request=1 stop_quiet=1",(unsigned)stopped_pcm,(unsigned)stopped_generation,(unsigned)discarded_generation);
    print_full_result(prefix);

    configure(true);play("http://fixture/T2");held();cancelling=true;unsigned previous_pauses=pauses.load();
    audio_maintenance_token_t token={};
    check(audio_service_maintenance_begin(10000,&token)==ESP_OK && token.epoch,"actual_three_owner_maintenance");
    check(!live_clients && !live_decoders && pauses>previous_pauses && input_quiet(),"maintenance_all_owners_quiet");
    size_t held_pcm=pcm_bytes.load();check(held_pcm>0 && held_pcm<full_pcm() && !(xEventGroupGetBits(events)&ENDED),"maintenance_partial_output");
    memory_record("MAINTENANCE_HELD");
    check(audio_service_play("http://fixture/blocked",NATIVE_CODEC_OGG)==ESP_ERR_INVALID_STATE,"play_blocked_while_held");
    auto stale=token;configure(false);
    check(audio_service_maintenance_end(&token,true)==ESP_OK && !token.epoch,"valid_resume_token_consumed");
    check(audio_service_maintenance_end(&stale,true)==ESP_ERR_INVALID_STATE,"stale_resume_token_rejected");complete();
    check(closes==opens && http_cleanup==clients+5,"resume_instance_cleanup");
    snprintf(prefix,sizeof(prefix),"CYD_F1_TASK_CASE id=T2 maintenance_resume=1 partial_pcm=%u held_quiet=1 play_blocked=1 token_consumed=1 stale_rejected=1",(unsigned)held_pcm);
    print_full_result(prefix);
}
