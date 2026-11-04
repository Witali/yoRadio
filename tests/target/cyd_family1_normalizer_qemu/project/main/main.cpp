// Thin coordinator over the complete frozen family1 observer/transport graph.
// Both original target and all production translation units remain unchanged.
#define app_main family1_disabled_matrix_entry
#define __wrap_native_audio_output_write_pcm norm_base_write_pcm
#include "../../../shared-family1/project/main/main.cpp"
#undef __wrap_native_audio_output_write_pcm
#undef app_main
#include "native_audio_normalizer.h"

static std::atomic<unsigned> norm_case, norm_frames, norm_resets, norm_configs;
static std::atomic<unsigned> norm_inflight, norm_calls, norm_wrong_calls;

extern "C" void __real_native_audio_normalizer_configure(bool,uint8_t,int8_t,uint16_t,uint32_t);
extern "C" void __real_native_audio_normalizer_reset(void);
extern "C" void __real_native_audio_normalizer_process_multichannel_block(int16_t *,size_t,uint8_t);
extern "C" void __real_native_audio_normalizer_process_block(int16_t *,size_t,uint8_t);
extern "C" void __wrap_native_audio_normalizer_configure(bool enabled,uint8_t gain,int8_t target,uint16_t time,uint32_t rate) {
    owner(1,6);check(enabled && gain==20 && target==-20 && time==100 && rate==48000,"fixed_enabled_normalizer_profile");
    ++norm_configs;
    printf("CYD_NORM_CONFIG case=%u enabled=1 gain_db=20 target_dbfs=-20 time_ms=100 rate=48000 frames=%u core=1 priority=6\n",norm_case.load(),norm_frames.load());
    __real_native_audio_normalizer_configure(enabled,gain,target,time,rate);
}
extern "C" void __wrap_native_audio_normalizer_reset(void) {
    owner(1,6);++norm_resets;
    if(norm_case && (phase==PCM_PHASE || phase==FLUSH_PHASE))
        printf("CYD_NORM_RESET case=%u frames=%u phase=%u core=1 priority=6\n",norm_case.load(),norm_frames.load(),(unsigned)phase);
    __real_native_audio_normalizer_reset();
}
extern "C" void __wrap_native_audio_normalizer_process_multichannel_block(int16_t *pcm,size_t frames,uint8_t channels) {
    owner(1,6);check(norm_case && phase==PCM_PHASE && pcm && channels==8 && frames>0 && frames<=32,"actual_all_channel_scratch_dispatch");
    __real_native_audio_normalizer_process_multichannel_block(pcm,frames,channels);
    norm_frames+=(unsigned)frames;++norm_calls;
}
extern "C" void __wrap_native_audio_normalizer_process_block(int16_t *pcm,size_t frames,uint8_t channels) {
    owner(1,6);++norm_wrong_calls;
    __real_native_audio_normalizer_process_block(pcm,frames,channels);
}
extern "C" esp_err_t __wrap_native_audio_output_write_pcm(const uint8_t *pcm,size_t bytes,uint8_t bits,uint8_t channels) {
    ++norm_inflight;auto result=norm_base_write_pcm(pcm,bytes,bits,channels);--norm_inflight;return result;
}
static void norm_settings() {
    check(native_audio_settings_set_normalization_gain_db(20)==ESP_OK &&
          native_audio_settings_set_normalization_target_dbfs(-20)==ESP_OK &&
          native_audio_settings_set_normalization_time_ms(100)==ESP_OK &&
          native_audio_settings_set_normalization(true)==ESP_OK &&
          native_audio_settings_get_volume()==127 && native_audio_settings_get_balance()==0 &&
          native_audio_settings_get_normalization() && native_audio_settings_get_normalization_gain_db()==20 &&
          native_audio_settings_get_normalization_target_dbfs()==-20 && native_audio_settings_get_normalization_time_ms()==100,
          "actual_public_enabled_settings");
}
extern "C" void app_main(void) {
    register_control_owner();
    check(xPortGetCoreID()==0 && af_blob_end-af_blob==F1_ASSET_BYTES,"whole_original_creator_asset_blob");
    printf("CYD_NORM_BOOT cases=2 enabled=1 hardware=0 release=UNRELEASED\n");
    check(psa_crypto_init()==PSA_SUCCESS,"real_public_crypto");events=xEventGroupCreate();output_lock=xSemaphoreCreateMutex();read_gate=xSemaphoreCreateBinary();
    f1_reference_events=xEventGroupCreate();check(events && output_lock && read_gate && f1_reference_events,"normalizer_sync_objects");
    TaskHandle_t reference_task=nullptr;
    check(xTaskCreatePinnedToCore(f1_public_reference_worker,"family1_reference",16384,nullptr,3,&reference_task,1)==pdPASS,"independent_reference_task");
    const int64_t deadline=esp_timer_get_time()+90000000;
    while(!(xEventGroupGetBits(f1_reference_events)&F1_REFERENCE_DONE)){check(esp_timer_get_time()<deadline,"fixed_reference_deadline");vTaskDelay(1);}
    vTaskDelay(1);check(nvs_flash_init()==ESP_OK && native_audio_settings_init()==ESP_OK,"real_fresh_settings");
    check(esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(0))==ESP_OK && esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(1))==ESP_OK,"both_original_idle_watchdogs");
    native_state_init(&state);check(state.lock && native_health_start() && audio_service_start(&state)==ESP_OK && profiles==3,"actual_original_application_tasks");
    word_alloc_set_owner(decode_task_handle);allocation_fault_set_owner(decode_task_handle);
    // Cancel/maintenance observers retain active until final quiescence.
    fixture_t plans[2]={full_sets[4][0],full_sets[4][1]};
    for(unsigned i=1;i<=2;++i) {
        // Existing complete F12 plans: whole pages/1-byte reads, then continued
        // pages/257-byte reads. Only public player settings change.
        fixture_t &plan=plans[i-1];plan.volume=127;active=&plan;
        check(plan.count==1 && plan.links[0]->reference==12 && plan.links[0]->channels==8 && plan.links[0]->frames==9600 &&
              plan.schedule==i && plan.page_style==i-1 && plan.links[0]->gain==1536,"exact_complete_F12_transport_plan");
        configure(i==1);norm_case=i;norm_frames=0;norm_calls=0;norm_wrong_calls=0;norm_settings();
        printf("CYD_NORM_BEGIN case=%u enabled=1 gain_db=20 target_dbfs=-20 time_ms=100 rate=48000 channels=8 volume=127 balance=0 schedule=%u page_style=%u\n",i,plan.schedule,plan.page_style);
        play("http://fixture/normalizer",NATIVE_CODEC_AUTO);
        if(i==1) {
            held();
            // HTTP read clamps every returned byte at the predeclared complete
            // first-audio-page boundary. Even a16KiB encoded ring cannot prefetch
            // packet2. Complete first-packet PCM is5760-312=5448 frames.
            wait_until([]{return client_position==active->links[0]->hold_offset && norm_frames==5448 &&
                pcm_bytes==5448u*8u*2u && norm_inflight==0;},"first_complete_packet_rendered_before_reset");
            unsigned resets=norm_resets.load(),configs=norm_configs.load();
            // PDM idle() does not inspect settings or consume pending reset.
            // No next PCM can arrive until the transport gate below is released.
            native_audio_output_request_normalizer_reset();native_audio_output_request_normalizer_reset();
            check(norm_resets==resets && norm_configs==configs && norm_inflight==0 && norm_frames==5448,"reset_requests_deferred_at_stable_format_boundary");
            printf("CYD_NORM_REQUEST case=1 frames=5448 requests=2 immediate_resets=0 config_unchanged=1 geometry_unchanged=1\n");
            partial_transport=false;xSemaphoreGive(read_gate);
        }
        complete();check(norm_frames==9600 && norm_calls>0 && !norm_wrong_calls && !norm_inflight,"all_complete_actual_normalizer_frames");
        printf("CYD_NORM_CASE case=%u frames=9600 mono_bytes=%u wire_bytes=%u padding_bytes=%u sha256=%s normalizer_frames=%u wrong_api_calls=%u\n",i,(unsigned)render_bytes,(unsigned)render_wire_bytes,(unsigned)final_padding_bytes,render_sha,norm_frames.load(),norm_wrong_calls.load());
        norm_case=0;
    }
    audio_maintenance_token_t token={};check(audio_service_maintenance_begin(10000,&token)==ESP_OK,"final_public_quiescence");
    check(opens==10 && closes==10 && http_cleanup==2 && output_flushes==2 && !public_failures && !live_clients && !live_decoders &&
          !driver.live && driver_created==driver_deleted && total_writes==gain_stamps && total_writes==layout_stamps &&
          input_quiet() && heap_caps_check_integrity_all(true),"complete_enabled_owner_and_metadata_census");
    printf("CYD_NORM_COMPLETE cases=2 opens=10 closes=10 http_cleanup=2 flushes=2 heap_integrity=1 hardware=0\n");
    check(fflush(stdout)==0,"flush_original_normalizer_records");esp_restart();
}
