#include "head.inc"

extern const uint8_t af_blob[] asm("_binary_fixtures_bin_start");
extern const uint8_t af_blob_end[] asm("_binary_fixtures_bin_end");
#include "asset_size.h"
struct span_t {uint32_t offset,bytes;};
struct link_t {
    const span_t *spans;size_t span_count,encoded_bytes;const char *name,*family;
    unsigned reference,channels,layout,needed,streams,coupled;
    const uint8_t *needed_ids;
    size_t frames,hold_offset,max_page;
    int16_t gain;
};
struct fixture_t {const char *name;const link_t *links[5];size_t count;uint8_t volume;unsigned schedule,page_style;};
#include "reference.h"
static const fixture_t *active;
static void check(bool,const char *);
static size_t full_pcm() {size_t n=0;for(size_t i=0;i<active->count;++i)n+=active->links[i]->frames*active->links[i]->channels*2u;return n;}
static size_t full_mono() {size_t n=0;for(size_t i=0;i<active->count;++i)n+=active->links[i]->frames*2u;return n;}
static size_t fixture_bytes() {size_t n=0;for(size_t i=0;i<active->count;++i)n+=active->links[i]->encoded_bytes;return n;}
static const char *source_sha(const link_t *link) {
    if(link->reference<13){assert(f1_references[link->reference].complete);return f1_references[link->reference].sha;}
    return link->reference==13?"b63b58b563d2a20d90a7bef235e5c1099dc52433db19083492d9c7098345469f":"e2c316f3e6b7a4a919027ab918cef54fc60a741a944aac26fc215ce33d396910";
}
static unsigned copy_encoded(uint8_t *to,size_t position,size_t bytes) {
    unsigned touched=0;
    for(size_t i=0;i<active->count && bytes;++i) {
        const link_t *link=active->links[i];size_t size=link->encoded_bytes;
        if(position>=size){position-=size;continue;}
        size_t n=std::min(bytes,size-position),remaining=n,inside=position;
        for(size_t j=0;j<link->span_count && remaining;++j) {
            const span_t &span=link->spans[j];if(inside>=span.bytes){inside-=span.bytes;continue;}
            size_t part=std::min<size_t>(remaining,span.bytes-inside);
            check((size_t)span.offset+inside+part<=F1_ASSET_BYTES,"immutable_transport_span_bounds");
            memcpy(to+(n-remaining),af_blob+span.offset+inside,part);remaining-=part;inside=0;
        }
        assert(!remaining);
        to+=n;bytes-=n;position=0;++touched;
    }
    assert(!bytes);return touched;
}
static constexpr EventBits_t TRANSPORT_HELD=1,PCM_STARTED=2,ENDED=4;
static native_state_t state;
static EventGroupHandle_t events;
static SemaphoreHandle_t output_lock,read_gate;
static TaskHandle_t stream_task_handle,decode_task_handle,output_task_handle;
static std::atomic<unsigned> profiles,opens,closes,live_decoders,http_cleanup,live_clients;
static std::atomic<unsigned> process_calls,resize_requests,resize_retry_checks,writes,metadata_checks,pauses,discard_calls;
static std::atomic<unsigned> gain_stamps,layout_stamps,driver_writes,driver_preloads,driver_created,driver_deleted;
static std::atomic<unsigned> output_flushes,cross_link_reads,discard_generation;
static std::atomic<unsigned> http_opens,total_writes;
static std::atomic<unsigned> public_state_infos;
static std::atomic<unsigned> public_failures;
static std::atomic<uint32_t> session_generation,http_generation;
static std::atomic<size_t> pcm_bytes,client_position;
static std::atomic<bool> cancelling;
static esp_http_client_handle_t current_client;
static unsigned read_index,decode_link_index;
static bool partial_transport,hold_announced;
static unsigned metadata_phase;
static unsigned ordered_layout,ordered_channels;
static size_t segment_index,segment_bytes,render_bytes,render_link_index,render_link_bytes;
static size_t render_wire_bytes,final_padding_bytes;
static bool final_padding_seen;
static unsigned total_padding_blocks;
static bool hash_finished;
static char completed_sha[65],render_sha[65];
static psa_hash_operation_t segment_hash=PSA_HASH_OPERATION_INIT,output_hash=PSA_HASH_OPERATION_INIT;
static psa_hash_operation_t render_hash=PSA_HASH_OPERATION_INIT,render_link_hash=PSA_HASH_OPERATION_INIT;
enum phase_t {INIT_PHASE,CONFIGURE_PHASE,PCM_PHASE,FLUSH_PHASE,PAUSE_PHASE,DISCARD_PHASE,IDLE_PHASE};
static phase_t phase=INIT_PHASE;
struct driver_model_t {bool live,enabled;};
static driver_model_t driver;
static i2s_chan_handle_t driver_handle(){return reinterpret_cast<i2s_chan_handle_t>(&driver);}
static void check(bool value,const char *reason) {if(!value){printf("CYD_F1_TASK_FAILURE %s\n",reason);fflush(stdout);assert(value);}}
static void owner(int core,unsigned priority){check(xPortGetCoreID()==core && uxTaskPriorityGet(nullptr)==priority,"actual_owner_profile");}
static native_state_t snapshot(){native_state_t result;native_state_snapshot(&state,&result);return result;}
static bool input_quiet(){auto h=audio_service_input_health();return h.available && h.leased && !h.ready && !h.reading && !h.writing;}
template<class Predicate> static void wait_until(Predicate predicate,const char *reason) {
    const int64_t deadline=esp_timer_get_time()+30000000;
    while(!predicate()) {
        if(snapshot().audio_failed) {
            while((live_clients || live_decoders || !input_quiet()) && esp_timer_get_time()<deadline)vTaskDelay(1);
            auto h=audio_service_input_health();auto faults=native_health_snapshot().faults;
            printf("CYD_F1_RESOURCE_FAILURE fixture=%s public_errors=%u live_clients=%u live_decoders=%u input_ready=%u input_reading=%u input_writing=%u decoder_failures=%u allocation_failures=%u output_failures=%u heap_free=%u heap_min=%u largest_internal=%u cleanup_quiet=%u\n",active->name,public_failures.load(),live_clients.load(),live_decoders.load(),(unsigned)h.ready,(unsigned)h.reading,(unsigned)h.writing,(unsigned)faults.decoder_failures,(unsigned)faults.allocation_failures,(unsigned)faults.output_failures,(unsigned)esp_get_free_heap_size(),(unsigned)esp_get_minimum_free_heap_size(),(unsigned)heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT),(unsigned)(!live_clients && !live_decoders && input_quiet()));
            check(false,"genuine_failed_generation_after_bounded_real_cleanup");
        }
        if(esp_timer_get_time()>=deadline) {
            auto h=audio_service_input_health();auto s=snapshot();
            printf("CYD_F1_CONTROL_WAIT_TIMEOUT live_clients=%u live_decoders=%u ready=%u reading=%u writing=%u generation=%u\n",live_clients.load(),live_decoders.load(),(unsigned)h.ready,(unsigned)h.reading,(unsigned)h.writing,(unsigned)s.audio_generation);
        }
        check(esp_timer_get_time()<deadline,reason);vTaskDelay(1);
    }
}
static void hex_digest(const uint8_t digest[32],char hex[65]){for(unsigned i=0;i<32;++i)snprintf(hex+2*i,3,"%02x",digest[i]);}
static void begin_hash(psa_hash_operation_t &hash){check(psa_hash_abort(&hash)==PSA_SUCCESS && psa_hash_setup(&hash,PSA_ALG_SHA_256)==PSA_SUCCESS,"fresh_complete_hash");}
static void finish_hash(psa_hash_operation_t &hash,char hex[65]){uint8_t digest[32];size_t used=0;check(psa_hash_finish(&hash,digest,32,&used)==PSA_SUCCESS && used==32,"finish_complete_hash");hex_digest(digest,hex);}
static void configure(bool hold) {
    check(!live_clients && !live_decoders,"all_old_public_owners_quiet");xSemaphoreTake(output_lock,portMAX_DELAY);
    begin_hash(output_hash);begin_hash(segment_hash);begin_hash(render_hash);begin_hash(render_link_hash);
    segment_index=segment_bytes=render_bytes=render_link_index=render_link_bytes=0;
    render_wire_bytes=final_padding_bytes=0;final_padding_seen=false;
    decode_link_index=0;pcm_bytes=0;writes=0;cross_link_reads=0;hash_finished=false;partial_transport=hold;hold_announced=false;cancelling=false;
    metadata_phase=0;
    completed_sha[0]=render_sha[0]=0;
    check(native_audio_settings_set_volume(active->volume)==ESP_OK && native_audio_settings_set_balance(0)==ESP_OK && native_audio_settings_set_normalization(false)==ESP_OK,"actual_unchanged_player_settings");
    xEventGroupClearBits(events,TRANSPORT_HELD|PCM_STARTED|ENDED);xSemaphoreGive(output_lock);
}
#include "allocation_fault_observer.inc"
#include "word_alloc_observer.inc"
#include "fairness_observer.inc"
#include "transport.inc"
#include "public_observers.inc"
#include "cancel_observer.inc"
extern "C" bool __real_native_state_set_stream_info(native_state_t *,uint32_t,const native_stream_info_t *);
extern "C" bool __wrap_native_state_set_stream_info(native_state_t *state_ptr,uint32_t generation,const native_stream_info_t *info) {
    owner(1,5);check(state_ptr==&state && info && !strcmp(info->codec,"OGG") && info->sample_rate_hz==48000 &&
        info->channels>=1 && info->channels<=8 && info->bits_per_sample==16 && !info->channels_are_core &&
        info->pcm_sample_rate_hz==48000 && info->pcm_channels==info->channels,"truthful_public_logical_PCM_geometry");
    bool accepted=__real_native_state_set_stream_info(state_ptr,generation,info);
    if(accepted) {
        ++public_state_infos;auto view=snapshot();bool current=view.audio_generation==generation && !view.audio_failed;
        if(current)check(view.sample_rate_hz==48000 && view.channels==info->channels && view.bits_per_sample==16 && !view.channels_are_core,"actual_current_state_keeps_all_logical_channels");
        static uint32_t previous_generation;static unsigned previous_channels;
        if(previous_generation!=generation || previous_channels!=info->channels) {
            printf("CYD_F1_STATE_INFO fixture=%s generation=%u rate=48000 channels=%u bits=16 current=%u channels_are_core=0\n",active->name,(unsigned)generation,(unsigned)info->channels,(unsigned)current);
            previous_generation=generation;previous_channels=info->channels;
        }
    }
    return accepted;
}
static void render(const uint8_t *data,size_t bytes) {
    xSemaphoreTake(output_lock,portMAX_DELAY);check(bytes && !(bytes%2),"actual_mono_driver_geometry");
    check(render_bytes<=full_mono(),"complete_logical_driver_extent");
    const size_t logical_before=render_bytes,wire_before=render_wire_bytes;
    const size_t logical=std::min(bytes,full_mono()-render_bytes),padding=bytes-logical;
    if(padding) {
        const size_t predicted=(1024u-full_mono()%1024u)%1024u;
        check(phase==FLUSH_PHASE && !final_padding_seen && bytes==1024 && predicted>0 && padding==predicted &&
              logical>0 && render_bytes+logical==full_mono() && wire_before==logical_before,
              "one_exact_final_PDM_DMA_padding_block");
        for(size_t i=logical;i<bytes;++i)check(data[i]==0,"every_final_padding_byte_zero");
        final_padding_seen=true;final_padding_bytes=padding;
    }
    check(psa_hash_update(&render_hash,data,logical)==PSA_SUCCESS,"complete_final_logical_driver_hash");
    size_t at=0;
    while(at<logical) {
        check(render_link_index<active->count,"driver_link_bound");const link_t *link=active->links[render_link_index];
        size_t n=std::min(logical-at,link->frames*2u-render_link_bytes);check(psa_hash_update(&render_link_hash,data+at,n)==PSA_SUCCESS,"driver_link_hash");
        at+=n;render_link_bytes+=n;
        if(render_link_bytes==link->frames*2u) {
            char hex[65];finish_hash(render_link_hash,hex);
            printf("CYD_F1_RENDER_LINK fixture=%s index=%u reference=%u channels=%u layout=%u gain_q8=%d volume=%u bytes=%u sha256=%s\n",active->name,(unsigned)render_link_index,link->reference,link->channels,link->layout,(int)link->gain,(unsigned)active->volume,(unsigned)render_link_bytes,hex);
            ++render_link_index;render_link_bytes=0;if(render_link_index<active->count)begin_hash(render_link_hash);
        }
    }
    render_bytes+=logical;render_wire_bytes+=bytes;
    if(padding)printf("CYD_F1_RENDER_PADDING fixture=%s schedule=%u page_style=%u ordinal=%u phase=FLUSH block_bytes=1024 logical_before=%u wire_before=%u logical_bytes=%u wire_bytes=%u padding_bytes=%u zero_checked=1 core=1 priority=6\n",active->name,active->schedule,active->page_style,++total_padding_blocks,(unsigned)logical_before,(unsigned)wire_before,(unsigned)logical,(unsigned)bytes,(unsigned)padding);
    xEventGroupSetBits(events,PCM_STARTED);xSemaphoreGive(output_lock);
}
#include "hardware.inc"
extern "C" esp_err_t __real_native_audio_output_configure(uint32_t);
extern "C" esp_err_t __wrap_native_audio_output_configure(uint32_t rate){owner(1,6);check(rate==48000,"actual_output_rate");phase=CONFIGURE_PHASE;auto r=__real_native_audio_output_configure(rate);phase=IDLE_PHASE;return r;}
extern "C" esp_err_t __real_native_audio_output_set_channel_layout(pcm_channel_layout,uint8_t);
extern "C" esp_err_t __wrap_native_audio_output_set_channel_layout(pcm_channel_layout layout,uint8_t channels) {
    owner(1,6);check(segment_index<active->count,"layout_metadata_link_bound");auto link=active->links[segment_index];
    check(!metadata_phase && (unsigned)layout==link->layout && channels==link->channels,"actual_queued_layout_and_logical_channels");metadata_phase=1;ordered_layout=(unsigned)layout;ordered_channels=channels;++layout_stamps;
    return __real_native_audio_output_set_channel_layout(layout,channels);
}
extern "C" esp_err_t __real_native_audio_output_set_header_gain(int16_t);
extern "C" esp_err_t __wrap_native_audio_output_set_header_gain(int16_t gain) {
    owner(1,6);check(metadata_phase==1 && segment_index<active->count && gain==active->links[segment_index]->gain,"actual_queued_header_gain");metadata_phase=2;++gain_stamps;
    if(!segment_bytes)printf("CYD_F1_METADATA fixture=%s index=%u layout=%u channels=%u gain_q8=%d core=1 priority=6 sequence=1\n",active->name,(unsigned)segment_index,ordered_layout,ordered_channels,(int)gain);
    return __real_native_audio_output_set_header_gain(gain);
}
extern "C" esp_err_t __real_native_audio_output_write_pcm(const uint8_t *,size_t,uint8_t,uint8_t);
extern "C" esp_err_t __wrap_native_audio_output_write_pcm(const uint8_t *data,size_t size,uint8_t bits,uint8_t channels) {
    owner(1,6);xSemaphoreTake(output_lock,portMAX_DELAY);check(!hash_finished && segment_index<active->count,"source_link_bound");
    check(metadata_phase==2,"actual_packet_layout_then_header_then_write_order");metadata_phase=0;
    auto link=active->links[segment_index];check(bits==16 && channels==link->channels && size && !(size%(channels*2u)),"all_logical_channel_source_geometry");
    check(pcm_bytes<=full_pcm() && size<=full_pcm()-pcm_bytes,"complete_source_extent");
    check(size<=link->frames*link->channels*2u-segment_bytes,"queue_packet_does_not_cross_logical_link");
    check(psa_hash_update(&output_hash,data,size)==PSA_SUCCESS && psa_hash_update(&segment_hash,data,size)==PSA_SUCCESS,"all_source_bytes_hashed");
    uint8_t before[32],after[32];size_t before_used=0,after_used=0;
    psa_status_t before_status=psa_hash_compute(PSA_ALG_SHA_256,data,size,before,32,&before_used);
    check(before_status==PSA_SUCCESS && before_used==32,"borrowed_source_before_hash");
    pcm_bytes+=size;segment_bytes+=size;++writes;++total_writes;++metadata_checks;
    if(segment_bytes==link->frames*link->channels*2u) {
        char hex[65];finish_hash(segment_hash,hex);check(!strcmp(hex,source_sha(link)),"whole_independent_public_mapped_trimmed_reference");
        printf("CYD_F1_LINK fixture=%s index=%u reference=%u channels=%u layout=%u gain_q8=%d bytes=%u sha256=%s\n",active->name,(unsigned)segment_index,link->reference,link->channels,link->layout,(int)link->gain,(unsigned)segment_bytes,hex);
        ++segment_index;segment_bytes=0;if(segment_index<active->count)begin_hash(segment_hash);
    }
    xSemaphoreGive(output_lock);
    unsigned acquire_at_entry=active_acquire.load();int64_t started=esp_timer_get_time();
    phase=PCM_PHASE;auto result=__real_native_audio_output_write_pcm(data,size,bits,channels);phase=IDLE_PHASE;
    int64_t returned=esp_timer_get_time();unsigned acquire_at_return=active_acquire.load();
    unsigned pause_start=last_true_pause_start.load(),pause_return=last_true_pause_return.load(),pause_acquire=true_pause_acquire.load();
    bool pause_started=true_pause_started.load(),intent=cancelling.load();
    psa_status_t after_status=psa_hash_compute(PSA_ALG_SHA_256,data,size,after,32,&after_used);
    int equal=after_status==PSA_SUCCESS && after_used==32?(memcmp(before,after,32)==0?1:0):-1;
    printf("CYD_F1_WRITE_RETURN fixture=%s call=%u source_generation=%u acquire_entry=%u acquire_return=%u pause_start=%u pause_return=%u pause_acquire=%u pause_requested=%u cancelling=%u start_us=%llu return_us=%llu result=%d data_bytes=%u before_status=%d before_bytes=%u after_status=%d after_bytes=%u equal=%d core=1 priority=6\n",
        active->name,total_writes.load(),(unsigned)session_generation.load(),acquire_at_entry,acquire_at_return,pause_start,pause_return,pause_acquire,
        (unsigned)pause_started,(unsigned)intent,(unsigned long long)started,(unsigned long long)returned,(int)result,(unsigned)size,
        (int)before_status,(unsigned)before_used,(int)after_status,(unsigned)after_used,equal);
    check(after_status==PSA_SUCCESS && after_used==32,"borrowed_source_after_hash_completed_independent_of_return");
    check(equal==1,"borrowed_source_immutable_after_actual_renderer");
    check(result==ESP_OK || (result==ESP_ERR_INVALID_STATE && intent && acquire_at_return && pause_started &&
        pause_start && pause_acquire==acquire_at_return),"actual_renderer_return_in_recorded_public_cancellation_interval");
    return result;
}
extern "C" esp_err_t __real_native_audio_output_flush_pcm(void);
extern "C" esp_err_t __wrap_native_audio_output_flush_pcm(void) {
    owner(1,6);check(!live_clients && !live_decoders,"all_public_owners_close_before_final_PCM_EOF");phase=FLUSH_PHASE;auto result=__real_native_audio_output_flush_pcm();phase=IDLE_PHASE;
    xSemaphoreTake(output_lock,portMAX_DELAY);const size_t predicted=(1024u-full_mono()%1024u)%1024u;
    check(result==ESP_OK && pcm_bytes==full_pcm() && render_bytes==full_mono() && segment_index==active->count && render_link_index==active->count &&
          final_padding_seen==(predicted!=0) && final_padding_bytes==predicted && render_wire_bytes==full_mono()+predicted,
          "one_complete_final_source_and_logical_wire_padding_terminal");
    finish_hash(output_hash,completed_sha);finish_hash(render_hash,render_sha);hash_finished=true;++output_flushes;xEventGroupSetBits(events,ENDED);xSemaphoreGive(output_lock);return result;
}
extern "C" void __real_native_audio_output_discard_pcm(void);
extern "C" void __wrap_native_audio_output_discard_pcm(void) {
    owner(1,6);phase=DISCARD_PHASE;__real_native_audio_output_discard_pcm();phase=IDLE_PHASE;
    discard_generation=snapshot().audio_generation;unsigned sequence=++discard_calls;
    printf("CYD_F1_CONTROL_DISCARD fixture=%s sequence=%u time_us=%llu snapshot_generation=%u core=1 priority=6 real_returned=1 pcm_bytes=%u mono_bytes=%u writes=%u driver_writes=%u\n",active?active->name:"INIT",sequence,(unsigned long long)esp_timer_get_time(),discard_generation.load(),(unsigned)pcm_bytes.load(),(unsigned)render_bytes,writes.load(),driver_writes.load());
}
extern "C" esp_err_t __real_native_audio_output_pause(void);
extern "C" esp_err_t __wrap_native_audio_output_pause(void){owner(1,6);check(!live_clients && !live_decoders,"all_public_owners_quiet_before_pause");phase=PAUSE_PHASE;auto r=__real_native_audio_output_pause();phase=IDLE_PHASE;++pauses;return r;}
extern "C" void __real_native_audio_output_idle(void);
extern "C" void __wrap_native_audio_output_idle(void){owner(1,6);phase=IDLE_PHASE;__real_native_audio_output_idle();}
#include "network.inc"
#include "lifecycle.inc"
extern "C" void app_main(void) {
    register_control_owner();
    check(xPortGetCoreID()==0 && af_blob_end-af_blob==F1_ASSET_BYTES,"complete_lossless_original_corpus_and_coordinator");
    printf("CYD_F1_TASK_BOOT sdk=%s actual_tasks=1 actual_output=1 public_raw=1 hardware=0\n",esp_get_idf_version());
    check(psa_crypto_init()==PSA_SUCCESS,"real_public_crypto");events=xEventGroupCreate();output_lock=xSemaphoreCreateMutex();read_gate=xSemaphoreCreateBinary();
    f1_reference_events=xEventGroupCreate();check(events && output_lock && read_gate && f1_reference_events,"reference_and_task_sync");
    TaskHandle_t reference_task=nullptr;check(xTaskCreatePinnedToCore(f1_public_reference_worker,"family1_reference",16384,nullptr,3,&reference_task,1)==pdPASS,"real_reference_worker");
    printf("CYD_F1_REFERENCE_BUDGET fixed_ms=90000 ordinary_ms=30000 whole_qemu_ms=600000 reset_on_progress=0\n");
    const int64_t deadline=esp_timer_get_time()+90000000;
    while(!(xEventGroupGetBits(f1_reference_events)&F1_REFERENCE_DONE)){check(esp_timer_get_time()<deadline,"fixed_reference_capture_deadline");vTaskDelay(1);}
    vTaskDelay(1);check(nvs_flash_init()==ESP_OK && native_audio_settings_init()==ESP_OK,"real_fresh_settings");
    check(esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(0))==ESP_OK && esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(1))==ESP_OK,"both_idle_watchdogs");
    native_state_init(&state);check(state.lock && native_health_start() && audio_service_start(&state)==ESP_OK && profiles==3,"real_complete_application_tasks");
    word_alloc_set_owner(decode_task_handle);
    allocation_fault_set_owner(decode_task_handle);
    for(unsigned i=0;i<5;++i) {
        lifecycle(lifecycles[i]);
        for(unsigned j=0;j<3;++j){active=&full_sets[i][j];configure(false);play("http://fixture/full",NATIVE_CODEC_AUTO);complete();print_full_result("CYD_F1_TASK_CASE id=FULL");}
    }
    for(unsigned i=0;i<16;++i){active=&map_cases[i];configure(false);play("http://fixture/map",NATIVE_CODEC_AUTO);complete();print_full_result("CYD_F1_TASK_CASE id=MAP");}
    for(unsigned i=0;i<2;++i) {
        active=&chains[i];unsigned clients=http_cleanup.load(),flushes=output_flushes.load();configure(false);play("http://fixture/chain",NATIVE_CODEC_AUTO);complete();
        check(http_cleanup==clients+1 && output_flushes==flushes+1 && cross_link_reads>0,"same_HTTP_generation_single_terminal_chain");print_full_result("CYD_F1_TASK_CASE id=CHAIN");
    }
    audio_maintenance_token_t final_token={};check(audio_service_maintenance_begin(10000,&final_token)==ESP_OK,"final_real_owner_quiescence");
    auto faults=native_health_snapshot().faults;record_native_fault_counters(faults);
    record_word_alloc_complete();
    record_allocation_fault_complete(faults);
    check(opens==195 && closes==195 && http_opens==58 && http_cleanup==58 && output_flushes==48 && !public_failures && !live_clients && !live_decoders && !driver.live && driver_created==driver_deleted && total_writes==gain_stamps && total_writes==layout_stamps && input_quiet() && heap_caps_check_integrity_all(true),"all_real_family1_simple_HTTP_driver_owners");
    printf("CYD_F1_ORDERED_PACKET_CENSUS packets=%u layout_stamps=%u gain_stamps=%u order=1\n",total_writes.load(),layout_stamps.load(),gain_stamps.load());
    printf("CYD_F1_TASK_COMPLETE cases=48 references=13 opens=%u closes=%u http_cleanup=%u process_calls=%u resizes=%u retries=%u output_flushes=%u gain_stamps=%u layout_stamps=%u driver_created=%u driver_deleted=%u driver_writes=%u preloads=%u stream_stack_free=%u decode_stack_free=%u output_stack_free=%u heap_free=%u heap_min=%u largest_internal=%u heap_integrity=1 private_abi=0 independent_codec_conformance=0 native_oom_injected=0 post_output_oracle_pending=1 hardware=0\n",opens.load(),closes.load(),http_cleanup.load(),process_calls.load(),resize_requests.load(),resize_retry_checks.load(),output_flushes.load(),gain_stamps.load(),layout_stamps.load(),driver_created.load(),driver_deleted.load(),driver_writes.load(),driver_preloads.load(),(unsigned)uxTaskGetStackHighWaterMark(stream_task_handle),(unsigned)uxTaskGetStackHighWaterMark(decode_task_handle),(unsigned)uxTaskGetStackHighWaterMark(output_task_handle),(unsigned)esp_get_free_heap_size(),(unsigned)esp_get_minimum_free_heap_size(),(unsigned)heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT));
    check(fflush(stdout)==0,"complete_original_records");esp_restart();
}
