/* Three unmodified production owner loops plus production adaptive FIFO.
 * HTTP, codec, RTOS and DMA drivers are explicit host seams, not real hardware. */
#include "cyd_maintenance_platform.h"
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
static void driver_hook(const char *name) {assert(role==ROLE_OUTPUT);barrier_hit(name);}
#define CYD_MAINTENANCE_HOST 1
#define MAINTENANCE_DRIVER_HOOK(name) driver_hook(name)
#define TAG OUTPUT_TAG
#include "cyd_output_pause_test.c"
#undef TAG
#define ESP_LOGE(...) ((void)0)
#define ESP_ERR_HTTP_EAGAIN 91
#define ESP_ERR_MBEDTLS_SSL_READ_FAILED 92
#define ESP_TLS_ERR_SSL_TIMEOUT (-93)
#define ESP_TLS_ERR_SSL_WANT_READ (-94)
#define ESP_TLS_ERR_SSL_WANT_WRITE (-95)
static const char *esp_err_to_name(int e) {(void)e;return "host error";}
#include "audio_service.h"
#include "native_audio_output.h"
#include "native_health.h"
#include "audio_completion.h"
#include "stream_body.h"
#include "stream_bitrate.h"
#include "stream_probe.h"
#include "adaptive_input.h"
#include "audio_power_seam.h"

typedef int esp_audio_err_t;
typedef unsigned esp_audio_simple_dec_type_t;
typedef void *esp_audio_simple_dec_handle_t;
typedef struct {unsigned dec_type;void *dec_cfg;unsigned cfg_size;bool use_frame_dec;} esp_audio_simple_dec_cfg_t;
typedef struct {uint8_t *buffer;size_t len,consumed;unsigned eos;} esp_audio_simple_dec_raw_t;
typedef struct {uint8_t *buffer;size_t len,needed_size,decoded_size;} esp_audio_simple_dec_out_t;
typedef struct {uint32_t sample_rate,bitrate;uint8_t bits_per_sample,channel;} esp_audio_simple_dec_info_t;
enum {ESP_AUDIO_ERR_OK=0,ESP_AUDIO_ERR_BUFF_NOT_ENOUGH=-8,ESP_AUDIO_ERR_MEM_LACK=-9,ESP_AUDIO_SIMPLE_DEC_TYPE_MP3=1,ESP_AUDIO_SIMPLE_DEC_TYPE_AAC,ESP_AUDIO_SIMPLE_DEC_TYPE_FLAC,ESP_AUDIO_SIMPLE_DEC_TYPE_OGG};
static atomic_uint decoder_handles,codec_type;
static atomic_bool hold_codec_close,codec_close_entered;
static int decoder_register_codecs(void) {return ESP_OK;}
static void decoder_unregister_codecs(void) {}
static int esp_audio_simple_dec_open(const esp_audio_simple_dec_cfg_t *cfg,void **out) {assert(role==ROLE_DECODER);*out=malloc(8);assert(*out);++decoder_handles;codec_type=cfg->dec_type;return ESP_OK;}
static void esp_audio_simple_dec_close(void *p) {assert(role==ROLE_DECODER && p && decoder_handles);codec_close_entered=true;while(hold_codec_close)vTaskDelay(1);--decoder_handles;free(p);}
static int esp_audio_simple_dec_process(void *p,esp_audio_simple_dec_raw_t *raw,esp_audio_simple_dec_out_t *out) {assert(role==ROLE_DECODER && p);barrier_hit("codec");raw->consumed=raw->len;out->decoded_size=raw->len?3072:0;assert(out->len>=out->decoded_size);memset(out->buffer,0x11,out->decoded_size);return ESP_OK;}
static int esp_audio_simple_dec_get_info(void *p,esp_audio_simple_dec_info_t *out) {assert(role==ROLE_DECODER && p);*out=(esp_audio_simple_dec_info_t){16000,128000,16,1};return ESP_OK;}
static int audio_level_led_init(void) {return ESP_OK;}
static void audio_level_led_update_peak(unsigned p) {(void)p;}
static void audio_level_led_update_pcm(const uint8_t *p,size_t n,uint8_t b,uint8_t c) {(void)p;(void)n;(void)b;(void)c;}
static atomic_uint health_faults;
void native_health_track_task(native_health_task_t r,void *p) {(void)r;(void)p;}
void native_health_decoder_failure(uint32_t g,uint32_t c,native_health_decoder_stage_t s,int32_t r,uint32_t e,uint32_t n) {(void)g;(void)c;(void)s;(void)r;(void)e;(void)n;++health_faults;}
void native_health_stream_failure(uint32_t g,uint32_t e,int32_t r) {(void)g;(void)e;(void)r;++health_faults;}
void native_health_output_failure(uint32_t g,native_health_output_stage_t s,int32_t r) {(void)g;(void)s;(void)r;++health_faults;}

enum {HTTP_EVENT_ON_HEADER=1};
typedef struct {int event_id;void *user_data;const char *header_key,*header_value;} esp_http_client_event_t;
typedef struct {const char *url,*user_agent;int timeout_ms,buffer_size,buffer_size_tx,max_redirection_count;void *crt_bundle_attach;bool disable_auto_redirect,keep_alive_enable;int (*event_handler)(esp_http_client_event_t *);void *user_data;} esp_http_client_config_t;
typedef struct {bool closed;unsigned reads;char url[512];} *esp_http_client_handle_t;
static void *esp_crt_bundle_attach;
static atomic_uint http_clients,http_inits,http_closes;
static atomic_bool no_body,mp3_start,tls_error,redirect_once;
static pthread_mutex_t url_mutex=PTHREAD_MUTEX_INITIALIZER;
static char observed_url[512];
static esp_http_client_handle_t esp_http_client_init(const esp_http_client_config_t *cfg) {assert(role==ROLE_STREAM);esp_http_client_handle_t c=calloc(1,sizeof(*c));assert(c);strlcpy(c->url,cfg->url,sizeof(c->url));pthread_mutex_lock(&url_mutex);strlcpy(observed_url,cfg->url,sizeof(observed_url));pthread_mutex_unlock(&url_mutex);++http_inits;++http_clients;return c;}
static int esp_http_client_set_header(void *c,const char *k,const char *v) {assert(role==ROLE_STREAM && c && k && v);return ESP_OK;}
static int esp_http_client_set_timeout_ms(void *c,int t) {assert(role==ROLE_STREAM && c && t>0);return ESP_OK;}
static int esp_http_client_open(esp_http_client_handle_t c,int n) {assert(role==ROLE_STREAM && c && !n);barrier_hit("open");c->closed=false;return ESP_OK;}
static int64_t esp_http_client_fetch_headers(void *c) {assert(role==ROLE_STREAM && c);barrier_hit("headers");return 0;}
static int esp_http_client_get_status_code(void *c) {assert(c);return atomic_load(&redirect_once)?302:200;}
static int esp_http_client_set_redirection(void *c) {assert(role==ROLE_STREAM && c);redirect_once=false;return ESP_OK;}
static int esp_http_client_close(esp_http_client_handle_t c) {assert(role==ROLE_STREAM);if(!c->closed){barrier_hit("close");c->closed=true;++http_closes;}return ESP_OK;}
static int esp_http_client_cleanup(esp_http_client_handle_t c) {assert(role==ROLE_STREAM && c && http_clients);barrier_hit("cleanup");esp_http_client_close(c);--http_clients;free(c);return ESP_OK;}
static int esp_http_client_read(esp_http_client_handle_t c,char *p,int n) {assert(role==ROLE_STREAM && c && !c->closed);barrier_hit("read");vTaskDelay(1);if(atomic_load(&tls_error))return ESP_FAIL;if(atomic_load(&no_body))return -ESP_ERR_HTTP_EAGAIN;if(atomic_load(&mp3_start)){if(c->reads++){barrier_hit("staging");return -ESP_ERR_HTTP_EAGAIN;}assert(n>=100);memset(p,0,100);p[0]=(char)0xff;p[1]=(char)0xfb;p[2]=(char)0x90;return 100;}memset(p,0,(size_t)n);memcpy(p,"fLaC\0\0\0\42",8);++c->reads;return n;}
static int esp_http_client_get_and_clear_last_tls_error(void *c,int *code,void *flags) {(void)c;(void)flags;*code=0;return atomic_load(&tls_error)?ESP_ERR_MBEDTLS_SSL_READ_FAILED:ESP_OK;}
static bool esp_http_client_is_complete_data_received(void *c) {(void)c;return false;}

#include "adaptive.inc"
static BaseType_t tested_commit(adaptive_input_t *q,void *p,size_t n) {if(role==ROLE_STREAM)barrier_hit("encoded_commit");return adaptive_input_commit_size(q,p,n);}
static void *tested_receive(adaptive_input_t *q,size_t *n,TickType_t t) {void *p=adaptive_input_receive(q,n,t);if(role==ROLE_DECODER&&!p)barrier_hit("decoder_empty");return p;}
#define adaptive_input_commit_size tested_commit
#define adaptive_input_receive tested_receive
static bool maintenance_active(void);
static void observe_pause_publication(bool requested) {
    native_audio_output_request_pause(requested);
    if (requested) {
        // A canceled write must be recognized by the actual output owner as
        // maintenance, rather than becoming a health/output failure.
        assert(maintenance_active());
        barrier_hit("pause_publish");
    }
}
#define native_audio_output_request_pause observe_pause_publication
#include "audio.inc"
#undef native_audio_output_request_pause
#undef adaptive_input_commit_size
#undef adaptive_input_receive
#include "state.inc"

static native_state_t state;
static const char test_url[]="https://radio.example.invalid:8443/direct?fixture=maintenance";
static pthread_t begin_thread;
static atomic_bool begin_done;
static unsigned begin_timeout;
static int begin_result;
static audio_maintenance_token_t begin_token;
static void assert_metadata_cleared(const native_state_t *snapshot) {
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
static void begin_ok(void) {budget_call=true;int result=audio_service_maintenance_begin(2000,&begin_token);budget_call=false;if(result!=ESP_OK)fprintf(stderr,"begin=%d phase=%u acks=%u error=%d gen=%u decoder_release=%u\n",result,atomic_load(&s_maintenance_phase),atomic_load(&s_maintenance_acks),atomic_load(&s_maintenance_error),atomic_load(&s_generation),atomic_load(&s_decoder_released_generation));assert(result==ESP_OK);assert(begin_token.epoch && maintenance_acked(MAINTENANCE_ALL));audio_power_assert_quiet(atomic_load(&s_generation));assert(!http_clients && !decoder_handles && !driver.running && !driver.allocated);adaptive_input_stats_t stats=adaptive_input_stats(s_encoded);assert(!stats.ready&&!stats.reading&&!stats.writing);pthread_mutex_lock(&s_pcm->mutex);assert(!s_pcm->used&&!s_pcm->reading&&!s_pcm->writing&&!s_pcm->ready);pthread_mutex_unlock(&s_pcm->mutex);native_state_t snap;native_state_snapshot(&state,&snap);assert_metadata_cleared(&snap);assert(!snap.audio_running&&!snap.audio_pending&&!snap.audio_failed&&!strcmp(snap.stream_format,"maintenance paused"));}
static void end_ok(bool resume) {bool expected=resume&&s_maintenance_resume&&s_last_command_valid;assert(audio_service_maintenance_end(&begin_token,resume)==ESP_OK);assert(!begin_token.epoch);await_phase(MAINTENANCE_OFF);audio_power_assert_accepted(atomic_load(&s_generation),expected);if(!expected)audio_power_assert_quiet(atomic_load(&s_generation));}
static void start_play(native_codec_t codec) {assert(audio_service_play(test_url,codec)==ESP_OK);native_state_set_station(&state,"fixture station label");native_state_set_title(&state,atomic_load(&s_generation),"old stream title");}
static void await_play(unsigned previous) {int64_t end=esp_timer_get_time()+3000000;while(http_inits<=previous){assert(esp_timer_get_time()<end);vTaskDelay(1);}}
static void await_driver(void) {int64_t end=esp_timer_get_time()+3000000;while(!driver.running){assert(esp_timer_get_time()<end);vTaskDelay(1);}}
static void shutdown_test(void) {
    if(atomic_load(&s_maintenance_phase)!=MAINTENANCE_HELD)begin_ok();
    assert(!http_clients&&!decoder_handles&&!driver.allocated);
    stop_threads=true;
    for(unsigned i=0;i<3;++i){assert(!pthread_join(test_tasks[i]->thread,NULL));vSemaphoreDelete(test_tasks[i]->notify);free(test_tasks[i]);}
    TaskHandle_t none[3]={0};discard_pipeline_startup(none,false);vSemaphoreDelete(state.lock);
#if CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_DAC
    free(s_dac_data);
#elif CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_LEGACY_DAC
    free(s_legacy_frames);
#endif
}

int main(int argc,char **argv) {
#ifdef TEST_TSAN
    fputs("HOST_MAIN_ENTERED\n",stderr);
#endif
    assert(argc==2);const char *scenario=argv[1];
    if(!strcmp(scenario,"wide_epoch"))s_maintenance_epoch=UINT32_MAX;
    native_state_init(&state);assert(audio_service_start(&state)==ESP_OK);
    if(!strcmp(scenario,"idle")){begin_ok();end_ok(false);}
    else if(!strcmp(scenario,"pause_publish")) {
        start_play(NATIVE_CODEC_FLAC);await_driver();arm("pause_publish");
        unsigned faults=health_faults;begin_async(1500);await_barrier();
        vTaskDelay(35);assert(!begin_done && health_faults==faults);
        release_barrier();join_begin(ESP_OK);assert(health_faults==faults);
    }
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
        native_state_t snap;native_state_snapshot(&state,&snap);assert_metadata_cleared(&snap);assert(!snap.audio_running&&snap.audio_pending&&snap.audio_failed&&strstr(snap.stream_format,"failed; cleanup pending"));
        unsigned previous=http_inits;fail_disable=false;await_phase(MAINTENANCE_OFF);await_play(previous);
    }
    else if(!strcmp(scenario,"delete_failure")) {
        start_play(NATIVE_CODEC_FLAC);await_driver();fail_delete=true;
        begin_async(1500);join_begin(ESP_FAIL);assert(maintenance_active() && !begin_token.epoch);
        assert(!driver.running && driver.allocated && !maintenance_acked(MAINTENANCE_OUTPUT));
        native_state_t snap;native_state_snapshot(&state,&snap);assert_metadata_cleared(&snap);assert(!snap.audio_running&&snap.audio_pending&&snap.audio_failed&&strstr(snap.stream_format,"failed; cleanup pending"));
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
        if(!strcmp(scenario,"end_busy")){assert(maintenance_active());vTaskDelay(25);assert(http_inits==previous);xSemaphoreGive(s_control_lock);}
        await_phase(MAINTENANCE_OFF);
        if(resume && strcmp(scenario,"stop_cancels")){await_play(previous);pthread_mutex_lock(&url_mutex);assert(!strcmp(observed_url,test_url));pthread_mutex_unlock(&url_mutex);native_state_t snapshot;native_state_snapshot(&state,&snapshot);assert(!strcmp(snapshot.station,"fixture station label"));assert(s_last_command.requested_codec==NATIVE_CODEC_FLAC);}
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
            await_play(0);void *p=NULL;assert(adaptive_input_acquire_control(s_encoded,&p,sizeof(encoded_packet_t)+1,100)==pdTRUE);encoded_packet_t *packet=p;packet->generation=atomic_load(&s_generation);packet->codec=NATIVE_CODEC_FLAC;packet->data_size=1;packet->end_of_stream=0;packet->data[0]=1;assert(adaptive_input_commit_size(s_encoded,p,sizeof(encoded_packet_t)+1));
        }
        if(!strcmp(scenario,"output_disable")) {await_driver();begin_async(1500);await_barrier();}
        else {await_barrier();begin_async(timeout?35:1500);}
        if(timeout) {
            join_begin(ESP_ERR_TIMEOUT);assert(!begin_token.epoch && maintenance_active());assert(!maintenance_acked(MAINTENANCE_STREAM));assert(audio_service_play(test_url,NATIVE_CODEC_FLAC)==ESP_ERR_INVALID_STATE);
            native_state_t snap;native_state_snapshot(&state,&snap);assert_metadata_cleared(&snap);assert(!snap.audio_running&&snap.audio_pending&&snap.audio_failed&&strstr(snap.stream_format,"timeout; cleanup pending"));
            begin_token.epoch=UINT64_C(0xfeedfaceabcdef01); // HTTP stack can disappear now.
            release_barrier();await_phase(MAINTENANCE_OFF);assert(!decoder_handles);
        } else {
            vTaskDelay(45);assert(!begin_done);
            if(!strcmp(scenario,"late_encoded")||!strcmp(scenario,"staging")){assert(!maintenance_acked(MAINTENANCE_STREAM));assert(!maintenance_acked(MAINTENANCE_DECODER));}
            if(!strcmp(scenario,"late_pcm")||!strcmp(scenario,"control_reading")){await_acks(MAINTENANCE_STREAM);assert(!maintenance_acked(MAINTENANCE_DECODER));assert(!maintenance_acked(MAINTENANCE_OUTPUT));}
            if(!strcmp(scenario,"output_write")||!strcmp(scenario,"output_disable")){assert(!maintenance_acked(MAINTENANCE_OUTPUT));assert(driver.running);}
            if(!strcmp(scenario,"staging")){adaptive_input_stats_t st=adaptive_input_stats(s_encoded);assert(st.writing);}
            if(!strcmp(scenario,"control_reading")){adaptive_input_stats_t st=adaptive_input_stats(s_encoded);assert(!st.ready&&!st.reading&&!st.writing);assert(s_encoded->control.state==READING);}
            native_state_t snap;native_state_snapshot(&state,&snap);assert_metadata_cleared(&snap);assert(!snap.audio_running&&snap.audio_pending&&!snap.audio_failed&&strstr(snap.stream_format,"cleanup pending"));
            release_barrier();join_begin(ESP_OK);assert(!http_clients&&!decoder_handles&&!driver.allocated);
        }
    }
    shutdown_test();printf("PASS %s; actual stream/decode/output owners + production adaptive FIFO; command=%zu token=%zu bytes\n",scenario,sizeof(play_command_t),sizeof(audio_maintenance_token_t));return 0;
}
