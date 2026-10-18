/* Three unmodified production owner loops plus production adaptive FIFO.
 * HTTP, codec, RTOS and DMA drivers are explicit host seams, not real hardware. */
#include "c3_maintenance_platform.h"
#include <sys/resource.h>
static pthread_mutex_t barrier_mutex=PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t barrier_cond=PTHREAD_COND_INITIALIZER;
static const char *barrier_name;
static bool barrier_entered,barrier_released;
static void barrier_hit(const char *name) {
    pthread_mutex_lock(&barrier_mutex);
    if(barrier_name && !strcmp(name,barrier_name) && !barrier_released) {
        barrier_entered=true;pthread_cond_broadcast(&barrier_cond);
        while(!barrier_released)pthread_cond_wait(&barrier_cond,&barrier_mutex);
    }
    pthread_mutex_unlock(&barrier_mutex);
}
static void arm(const char *name) {pthread_mutex_lock(&barrier_mutex);barrier_name=name;barrier_entered=barrier_released=false;pthread_mutex_unlock(&barrier_mutex);}
static void await_barrier(void) {struct timespec end=until_ms(3000);pthread_mutex_lock(&barrier_mutex);while(!barrier_entered){int e=pthread_cond_timedwait(&barrier_cond,&barrier_mutex,&end);if(e){fprintf(stderr,"barrier missing: %s\n",barrier_name);abort();}}pthread_mutex_unlock(&barrier_mutex);}
static void release_barrier(void) {pthread_mutex_lock(&barrier_mutex);barrier_released=true;pthread_cond_broadcast(&barrier_cond);pthread_mutex_unlock(&barrier_mutex);}
static void maintenance_pause_requested(void);
#include "c3_maintenance_seams.h"
#include "adaptive.inc"
static BaseType_t tested_commit(adaptive_input_t *q,void *p,size_t n) {if(role==ROLE_STREAM)barrier_hit("encoded_commit");return adaptive_input_commit_size(q,p,n);}
static void *tested_receive(adaptive_input_t *q,size_t *n,TickType_t t) {void *p=adaptive_input_receive(q,n,t);if(role==ROLE_DECODER&&!p){if(stop_threads)pthread_exit(NULL);barrier_hit("decoder_empty");}return p;}
#define adaptive_input_commit_size tested_commit
#define adaptive_input_receive tested_receive
#include "audio.inc"
#undef malloc
#undef realloc
#undef free
#undef adaptive_input_commit_size
#undef adaptive_input_receive
#include "state.inc"
static bool display_settings_screensaver_active(bool playing,uint32_t now,bool *off) {(void)playing;(void)now;*off=false;return true;}
#define BOARD_BOOT_BUTTON 0
static int gpio_get_level(int pin) {(void)pin;return 1;}
#include "idle.inc"
static void maintenance_pause_requested(void) {assert(maintenance_active());assert(atomic_load(&s_maintenance_phase)==MAINTENANCE_REQUESTED);assert(atomic_load(&s_generation)!=0);}

static native_state_t state;
static const char test_url[]="https://radio.example.invalid:8443/direct?fixture=maintenance";
static pthread_t begin_thread;
static atomic_bool begin_done;
static unsigned begin_timeout;
static int begin_result;
static audio_maintenance_token_t begin_token;
static void assert_metadata_cleared(const native_state_t *snapshot) {
    assert(!idle_clock(&state));
    assert(!snapshot->title[0]);
    assert(!snapshot->codec[0] && !snapshot->bitrate_kbps && !snapshot->sample_rate_hz &&
           !snapshot->pcm_sample_rate_hz && !snapshot->channels && !snapshot->bits_per_sample &&
           !snapshot->pcm_channels && !snapshot->channels_are_core && !snapshot->format_is_pcm &&
           snapshot->bitrate_source==NATIVE_BITRATE_NONE);
}
static void *call_begin(void *unused) {(void)unused;budget_call=true;begin_result=audio_service_maintenance_begin(begin_timeout,&begin_token);budget_call=false;atomic_store(&begin_done,true);return NULL;}
static void begin_async(unsigned timeout) {begin_timeout=timeout;begin_token=(audio_maintenance_token_t){0};begin_done=false;assert(!pthread_create(&begin_thread,NULL,call_begin,NULL));}
static void join_begin(int expected) {assert(!pthread_join(begin_thread,NULL));if(begin_result!=expected)fprintf(stderr,"begin result=%d expected=%d phase=%u acks=%u error=%d\n",begin_result,expected,atomic_load(&s_maintenance_phase),atomic_load(&s_maintenance_acks),atomic_load(&s_maintenance_error));assert(begin_result==expected);assert((begin_result==ESP_OK)==(begin_token.epoch!=0));}
static void await_phase(unsigned phase) {int64_t end=esp_timer_get_time()+3000000;while(atomic_load(&s_maintenance_phase)!=phase){assert(esp_timer_get_time()<end);vTaskDelay(1);}}
static void await_acks(unsigned bits) {int64_t end=esp_timer_get_time()+3000000;while(!maintenance_acked(bits)){assert(esp_timer_get_time()<end);vTaskDelay(1);}}
static void begin_ok(void) {budget_call=true;int result=audio_service_maintenance_begin(2000,&begin_token);budget_call=false;if(result!=ESP_OK)fprintf(stderr,"begin=%d phase=%u acks=%u error=%d gen=%u decoder_release=%u\n",result,atomic_load(&s_maintenance_phase),atomic_load(&s_maintenance_acks),atomic_load(&s_maintenance_error),atomic_load(&s_generation),atomic_load(&s_decoder_released_generation));assert(result==ESP_OK);assert(begin_token.epoch && maintenance_acked(MAINTENANCE_ALL));assert(!http_clients && !decoder_handles && !driver.running && !driver.allocated);assert(!owner_allocations(ROLE_DECODER)&&!arena_live&&!arena_blocks&&!legacy_arena&&!driver.retained);adaptive_input_stats_t stats=adaptive_input_stats(s_encoded);assert(!stats.ready&&!stats.reading&&!stats.writing);assert(s_encoded->control.state!=READING&&s_encoded->control.state!=READY&&s_encoded->control.state!=WRITING);pthread_mutex_lock(&s_pcm->mutex);assert(!s_pcm->used&&!s_pcm->reading&&!s_pcm->writing&&!s_pcm->ready);pthread_mutex_unlock(&s_pcm->mutex);native_state_t snap;native_state_snapshot(&state,&snap);assert_metadata_cleared(&snap);assert(!snap.audio_running&&!snap.audio_pending&&!strcmp(snap.stream_format,"maintenance paused"));}
static void end_ok(bool resume) {assert(audio_service_maintenance_end(&begin_token,resume)==ESP_OK);assert(!begin_token.epoch);await_phase(MAINTENANCE_OFF);}
static void start_play(native_codec_t codec) {assert(audio_service_play(test_url,codec)==ESP_OK);native_state_set_station(&state,"fixture station label");native_state_set_stream_title(&state,atomic_load(&s_generation),"old stream title");}
static void await_play(unsigned previous) {int64_t end=esp_timer_get_time()+3000000;while(http_inits<=previous){assert(esp_timer_get_time()<end);vTaskDelay(1);}}
static void await_driver(void) {int64_t end=esp_timer_get_time()+3000000;while(!driver.running){assert(esp_timer_get_time()<end);vTaskDelay(1);}}
static void shutdown_test(void) {
    if(atomic_load(&s_maintenance_phase)!=MAINTENANCE_HELD&&!fail_stream_buffer)begin_ok();
    assert(!http_clients&&!decoder_handles&&!driver.allocated);
    stop_threads=true;
    for(unsigned i=0;i<3;++i){assert(!pthread_join(test_tasks[i]->thread,NULL));vSemaphoreDelete(test_tasks[i]->notify);free(test_tasks[i]);}
    adaptive_input_destroy(s_encoded);vRingbufferDelete(s_pcm);vQueueDelete(s_commands);vSemaphoreDelete(s_control_lock);vSemaphoreDelete(state.lock);
    for(unsigned i=0;i<64;++i)if(allocations[i].p){assert(allocations[i].owner==ROLE_STREAM);owner_free(allocations[i].p);}

}

int main(int argc,char **argv) {
    struct rlimit no_core={0,0};assert(!setrlimit(RLIMIT_CORE,&no_core));
#ifdef TEST_TSAN
    fputs("HOST_MAIN_ENTERED\n",stderr);
#endif
    assert(argc==2);const char *scenario=argv[1];
    if(!strcmp(scenario,"stream_alloc_failure"))fail_stream_buffer=true;
    if(!strcmp(scenario,"wide_epoch"))s_maintenance_epoch=UINT32_MAX;
    native_state_init(&state);state.web_ready=true;state.network_mode=NATIVE_NETWORK_CLIENT;
    assert(audio_service_start(&state)==ESP_OK);
    if(!strcmp(scenario,"idle")){assert(idle_clock(&state));begin_ok();end_ok(false);assert(idle_clock(&state));}
    else if(!strcmp(scenario,"stream_alloc_failure")) {
        begin_async(60);join_begin(ESP_ERR_TIMEOUT);
        assert(!begin_token.epoch&&!maintenance_acked(MAINTENANCE_STREAM));
        assert(!http_clients&&!decoder_handles&&!driver.allocated);
    }
    else if(!strcmp(scenario,"native_aac")||!strcmp(scenario,"legacy_arena")) {
        bool aac=!strcmp(scenario,"native_aac");aac_start=aac;mp3_full=!aac;
        start_play(aac?NATIVE_CODEC_AAC:NATIVE_CODEC_MP3);await_driver();
        assert(decoder_handles==1&&arena_live&&arena_blocks);
        if(!aac)assert(legacy_arena);
        begin_ok();end_ok(true);
    }
    else if(!strcmp(scenario,"retry_cleanup")||!strcmp(scenario,"terminal_cleanup")||!strcmp(scenario,"retry_watchdog_off")) {
        bool retry=!strcmp(scenario,"retry_cleanup");watchdog_enabled=strcmp(scenario,"retry_watchdog_off")!=0;
        connect_error=retry||!watchdog_enabled;terminal_response=watchdog_enabled&&!retry;
        arm("cleanup");start_play(NATIVE_CODEC_FLAC);await_barrier();
        assert(atomic_load(&s_stream_retry_pending)==retry);
        unsigned previous=http_inits;begin_async(1500);await_phase(MAINTENANCE_REQUESTED);
        vTaskDelay(35);assert(!begin_done&&!maintenance_acked(MAINTENANCE_STREAM));
        connect_error=terminal_response=false;release_barrier();join_begin(ESP_OK);end_ok(true);
        if(retry)await_play(previous);else {vTaskDelay(60);assert(http_inits==previous);}
    }
    else if(!strcmp(scenario,"retry_backoff")) {
        connect_error=true;start_play(NATIVE_CODEC_FLAC);
        int64_t end=esp_timer_get_time()+2000000;while(!s_stream_retry_pending||http_clients){assert(esp_timer_get_time()<end);vTaskDelay(1);}
        unsigned previous=http_inits;begin_ok();connect_error=false;end_ok(true);await_play(previous);
    }
    else if(!strcmp(scenario,"shared_arena_tail")) {
        start_play(NATIVE_CODEC_FLAC);await_driver();defer_codec_tail=true;
        begin_async(1500);join_begin(ESP_ERR_INVALID_STATE);
        assert(!decoder_handles&&arena_live&&arena_blocks&&!maintenance_acked(MAINTENANCE_DECODER));
        void *p=atomic_exchange(&deferred_codec,NULL);assert(p);defer_codec_tail=false;free(p);--arena_blocks;arena_live-=32;
        await_phase(MAINTENANCE_OFF);
    }
    else if(!strcmp(scenario,"legacy_discard_fail")) {
        mp3_full=true;start_play(NATIVE_CODEC_MP3);await_driver();arena_reject_discard=true;
        begin_async(1500);join_begin(ESP_ERR_INVALID_STATE);
        assert(legacy_arena&&!decoder_handles&&!maintenance_acked(MAINTENANCE_DECODER));
        arena_reject_discard=false;await_phase(MAINTENANCE_OFF);
    }
#ifdef CONFIG_YORADIO_DIRECT_DMA_PCM
    else if(!strcmp(scenario,"retained_dma")||!strcmp(scenario,"retained_pause_failure")) {
        start_play(NATIVE_CODEC_FLAC);await_driver();
        int64_t end=esp_timer_get_time()+2000000;while(!driver.retained){assert(esp_timer_get_time()<end);vTaskDelay(1);}no_body=true;
        if(!strcmp(scenario,"retained_pause_failure")) {
            fail_disable=true;begin_async(1500);join_begin(ESP_FAIL);
            assert(!driver.retained&&driver.discarded&&driver.running&&driver.allocated&&!maintenance_acked(MAINTENANCE_OUTPUT));
            fail_disable=false;await_phase(MAINTENANCE_OFF);
        } else {
            arm("disable");begin_async(1500);await_barrier();vTaskDelay(25);
            assert(!driver.retained&&driver.discarded&&!begin_done&&!maintenance_acked(MAINTENANCE_OUTPUT));
            release_barrier();join_begin(ESP_OK);
        }
    }
#endif
    else if(!strcmp(scenario,"empty_receive_epoch")) {
        start_play(NATIVE_CODEC_FLAC);await_driver();no_body=true;arm("decoder_empty");await_barrier();
        assert(decoder_handles==1);hold_codec_close=true;codec_close_entered=false;
        begin_async(1500);await_acks(MAINTENANCE_STREAM);release_barrier();
        int64_t end=esp_timer_get_time()+1000000;while(!codec_close_entered){assert(esp_timer_get_time()<end);vTaskDelay(1);}
        vTaskDelay(35);assert(!begin_done && !maintenance_acked(MAINTENANCE_DECODER) && !maintenance_acked(MAINTENANCE_OUTPUT));
        hold_codec_close=false;join_begin(ESP_OK);assert(!decoder_handles);
    }
    else if(!strcmp(scenario,"back_to_back")) {
        arm("park");begin_ok();await_barrier();end_ok(false);begin_async(1000);
        await_phase(MAINTENANCE_REQUESTED);vTaskDelay(35);assert(!begin_done);
        release_barrier();join_begin(ESP_OK);
    }
    else if(!strcmp(scenario,"pending_resume")) {
        start_play(NATIVE_CODEC_FLAC);await_driver();arm("stream_park");begin_ok();await_barrier();
        end_ok(true);unsigned previous=http_inits;begin_async(1500);await_phase(MAINTENANCE_REQUESTED);
        release_barrier();join_begin(ESP_OK);end_ok(true);await_play(previous);
    }
    else if(!strcmp(scenario,"state_lock")||!strcmp(scenario,"control_lock")) {
        SemaphoreHandle_t lock=!strcmp(scenario,"state_lock")?state.lock:s_control_lock;
        assert(xSemaphoreTake(lock,0));int64_t start=esp_timer_get_time();begin_async(25);join_begin(ESP_ERR_TIMEOUT);assert(esp_timer_get_time()-start<300000);assert(!maintenance_active());xSemaphoreGive(lock);
    }
    else if(!strcmp(scenario,"queue_failure")) {reject_queue=true;budget_call=true;assert(audio_service_maintenance_begin(500,&begin_token)==ESP_FAIL);budget_call=false;assert(!begin_token.epoch);await_phase(MAINTENANCE_OFF);}
    else if(!strcmp(scenario,"pause_failure")) {
        start_play(NATIVE_CODEC_FLAC);await_driver();fail_disable=true;
        begin_async(1500);join_begin(ESP_FAIL);assert(maintenance_active() && !begin_token.epoch);
        assert(driver.running && driver.allocated && !maintenance_acked(MAINTENANCE_OUTPUT));
        native_state_t snap;native_state_snapshot(&state,&snap);assert_metadata_cleared(&snap);assert(!snap.audio_running&&snap.audio_pending&&strstr(snap.stream_format,"failed; cleanup pending"));
        unsigned previous=http_inits;fail_disable=false;await_phase(MAINTENANCE_OFF);await_play(previous);
    }
    else if(!strcmp(scenario,"delete_failure")) {
        start_play(NATIVE_CODEC_FLAC);await_driver();fail_delete=true;
        begin_async(1500);join_begin(ESP_FAIL);assert(maintenance_active() && !begin_token.epoch);
        assert(!driver.running && driver.allocated && !maintenance_acked(MAINTENANCE_OUTPUT));
        native_state_t snap;native_state_snapshot(&state,&snap);assert_metadata_cleared(&snap);assert(!snap.audio_running&&snap.audio_pending&&strstr(snap.stream_format,"failed; cleanup pending"));
        unsigned previous=http_inits;fail_delete=false;await_phase(MAINTENANCE_OFF);await_play(previous);
    }
    else if(!strcmp(scenario,"stopped_no_resume")) {
        start_play(NATIVE_CODEC_FLAC);await_play(0);audio_service_stop();begin_ok();
        unsigned previous=http_inits;end_ok(true);vTaskDelay(60);assert(http_inits==previous);
    }
    else if(!strcmp(scenario,"resume_queue_failure")) {
        start_play(NATIVE_CODEC_FLAC);await_play(0);begin_ok();unsigned previous=http_inits;
        reject_queue=true;assert(audio_service_maintenance_end(&begin_token,true)==ESP_OK);
        assert(!begin_token.epoch);await_phase(MAINTENANCE_OFF);await_play(previous);
    }
    else if(!strcmp(scenario,"wide_epoch")){begin_ok();assert(begin_token.epoch>UINT32_MAX);audio_maintenance_token_t stale=begin_token;end_ok(false);begin_ok();assert(audio_service_maintenance_end(&stale,true)==ESP_ERR_INVALID_STATE);assert(begin_token.epoch);}
    else if(!strcmp(scenario,"resume")||!strcmp(scenario,"stop_cancels")||!strcmp(scenario,"end_no_resume")||!strcmp(scenario,"end_busy")) {
        start_play(NATIVE_CODEC_FLAC);await_play(0);begin_ok();unsigned previous=http_inits;
        assert(audio_service_play("http://other.invalid/",NATIVE_CODEC_MP3)==ESP_ERR_INVALID_STATE);
        if(!strcmp(scenario,"stop_cancels"))audio_service_stop();
        bool resume=strcmp(scenario,"end_no_resume")!=0;
        if(!strcmp(scenario,"end_busy"))assert(xSemaphoreTake(s_control_lock,0));
        audio_maintenance_token_t stale=begin_token;
        assert(audio_service_maintenance_end(&begin_token,resume)==ESP_OK);assert(!begin_token.epoch);
        assert(audio_service_maintenance_end(&stale,resume)==ESP_ERR_INVALID_STATE);
        if(!strcmp(scenario,"end_busy")){assert(maintenance_active());assert(!idle_clock(&state));vTaskDelay(25);assert(http_inits==previous);xSemaphoreGive(s_control_lock);}
        await_phase(MAINTENANCE_OFF);
        if(resume && strcmp(scenario,"stop_cancels")){await_play(previous);pthread_mutex_lock(&url_mutex);assert(!strcmp(observed_url,test_url));pthread_mutex_unlock(&url_mutex);native_state_t snapshot;native_state_snapshot(&state,&snapshot);assert(!strcmp(snapshot.station,"fixture station label"));assert(s_last_codec==NATIVE_CODEC_FLAC);}
        else {vTaskDelay(60);assert(http_inits==previous);}
    }
    else {
        const char *tag=scenario;bool timeout=!strncmp(scenario,"timeout_",8);
        if(timeout)tag=scenario+8;
        if(!strcmp(scenario,"late_encoded"))tag="encoded_commit";
        if(!strcmp(scenario,"late_pcm"))tag="pcm_acquire";
        if(!strcmp(scenario,"output_write"))tag="write";
        if(!strcmp(scenario,"output_disable"))tag="disable";
        if(!strcmp(scenario,"control_reading"))tag="codec";
        if(!strcmp(scenario,"staging"))mp3_start=true;
        if(!strcmp(scenario,"timeout_close")){tls_error=true;}
        if(!strcmp(scenario,"timeout_cleanup"))tls_error=true;
        arm(tag);
        if(!strcmp(scenario,"control_reading"))no_body=true;
        start_play(mp3_start?NATIVE_CODEC_MP3:NATIVE_CODEC_FLAC);
        if(!strcmp(scenario,"control_reading")) {
            static _Alignas(encoded_packet_t) uint8_t control[sizeof(encoded_packet_t)+1];
            await_play(0);assert(adaptive_input_attach_control(s_encoded,control,sizeof(control)));
            void *p=NULL;assert(adaptive_input_acquire_control(s_encoded,&p,sizeof(encoded_packet_t)+1,100)==pdTRUE);encoded_packet_t *packet=p;packet->generation=atomic_load(&s_generation);packet->codec=NATIVE_CODEC_FLAC;packet->data_size=1;packet->end_of_stream=0;packet->data[0]=1;assert(adaptive_input_commit_size(s_encoded,p,sizeof(encoded_packet_t)+1));
        }
        if(!strcmp(scenario,"output_disable")) {await_driver();begin_async(1500);await_barrier();}
        else {await_barrier();begin_async(timeout?35:1500);}
        if(timeout) {
            join_begin(ESP_ERR_TIMEOUT);assert(!begin_token.epoch && maintenance_active());assert(!maintenance_acked(MAINTENANCE_STREAM));assert(audio_service_play(test_url,NATIVE_CODEC_FLAC)==ESP_ERR_INVALID_STATE);
            native_state_t snap;native_state_snapshot(&state,&snap);assert_metadata_cleared(&snap);assert(!snap.audio_running&&snap.audio_pending&&strstr(snap.stream_format,"timeout; cleanup pending"));
            begin_token.epoch=UINT64_C(0xfeedfaceabcdef01); // HTTP stack can disappear now.
            release_barrier();await_phase(MAINTENANCE_OFF);assert(!decoder_handles);
        } else {
            vTaskDelay(45);assert(!begin_done);
            if(!strcmp(scenario,"late_encoded")||!strcmp(scenario,"staging")){assert(!maintenance_acked(MAINTENANCE_STREAM));assert(!maintenance_acked(MAINTENANCE_DECODER));}
            if(!strcmp(scenario,"late_pcm")||!strcmp(scenario,"control_reading")){await_acks(MAINTENANCE_STREAM);assert(!maintenance_acked(MAINTENANCE_DECODER));assert(!maintenance_acked(MAINTENANCE_OUTPUT));}
            if(!strcmp(scenario,"output_write")||!strcmp(scenario,"output_disable")){assert(!maintenance_acked(MAINTENANCE_OUTPUT));assert(driver.running);}
            if(!strcmp(scenario,"staging")){adaptive_input_stats_t st=adaptive_input_stats(s_encoded);assert(st.writing);}
            // C3 may queue an old-generation terminal behind the held control
            // lease; its decoder must drain both before acknowledging.
            if(!strcmp(scenario,"control_reading")){adaptive_input_stats_t st=adaptive_input_stats(s_encoded);assert(!st.reading&&!st.writing);assert(s_encoded->control.state==READING);}
            native_state_t snap;native_state_snapshot(&state,&snap);assert_metadata_cleared(&snap);assert(!snap.audio_running&&snap.audio_pending&&strstr(snap.stream_format,"cleanup pending"));
            release_barrier();join_begin(ESP_OK);assert(!http_clients&&!decoder_handles&&!driver.allocated);
        }
    }
    shutdown_test();printf("PASS %s; actual owners/FIFO/reader; command=%zu token=%zu maintenance_fields=%zu token_lock=%zu host bytes; priorities=5/7/8\n",scenario,sizeof(play_command_t),sizeof(audio_maintenance_token_t),sizeof(s_maintenance_phase)+sizeof(s_maintenance_acks)+sizeof(s_maintenance_error)+sizeof(s_maintenance_waiter)+sizeof(s_maintenance_epoch)+sizeof(s_last_generation)+sizeof(s_stream_retry_pending)+sizeof(s_last_command_valid)+sizeof(s_maintenance_resume),sizeof(s_maintenance_token_lock));return 0;
}
