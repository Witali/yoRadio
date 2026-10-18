#include <assert.h>
#include <setjmp.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include "native_state.h"
#include "audio_completion.h"
#include "stream_probe.h"
#include "stream_body.h"
#include "json_buffer.h"
#include "native_health.h"
#include "radio_control.h"

typedef enum { NATIVE_CODEC_AUTO, NATIVE_CODEC_MP3, NATIVE_CODEC_AAC,
               NATIVE_CODEC_FLAC, NATIVE_CODEC_OGG } native_codec_t;
typedef int esp_err_t;
typedef void *QueueHandle_t, *RingbufHandle_t;
typedef struct { int method; const char *query; } httpd_req_t;
enum { ESP_OK=0, ESP_FAIL=-1, ESP_ERR_TIMEOUT=0x107, ESP_ERR_HTTP_EAGAIN=0x7007,
       ESP_ERR_MBEDTLS_SSL_READ_FAILED=0x8000, HTTP_EVENT_ON_HEADER=1,
       HTTPD_500_INTERNAL_SERVER_ERROR=500, HTTPD_400_BAD_REQUEST=400,
       ESP_ERR_INVALID_ARG=-2,ESP_ERR_NOT_FOUND=-3,HTTP_GET=0,HTTP_POST=1 };
#define ESP_TLS_ERR_SSL_TIMEOUT (-0x6800)
#define ESP_TLS_ERR_SSL_WANT_READ (-0x6900)
#define ESP_TLS_ERR_SSL_WANT_WRITE (-0x6880)
#define ESP_LOGE(...) ((void)0)
#define ESP_LOGW(...) ((void)0)
typedef struct { int event_id; void *user_data; char *header_key, *header_value; } esp_http_client_event_t;
typedef struct {
    const char *url, *user_agent;
    int timeout_ms, buffer_size, buffer_size_tx, max_redirection_count;
    bool disable_auto_redirect, keep_alive_enable;
    int (*crt_bundle_attach)(void *);
    int (*event_handler)(esp_http_client_event_t *);
    void *user_data;
} esp_http_client_config_t;
typedef struct { esp_http_client_config_t config; bool open; } test_client_t;
typedef test_client_t *esp_http_client_handle_t;

static native_state_t state;
static test_client_t client;
static jmp_buf task_exit;
static uint64_t clock_us;
static unsigned queued, opens, fetches, redirects, reads, cleanups, closes, deletes;
static unsigned encoded_bytes, terminal, packets, selected_codec, cases;
static unsigned eagain, chunk_size, open_delay_ms, header_delay_ms;
static int statuses[8], open_error, header_error, redirect_error;
static const uint8_t *body_data;
static size_t body_size, body_offset;
static const char *interval_text, *second_interval;
static bool cancel_read, fail_client, fail_buffer, stall_body, fatal_tls, retry_tls;
static bool icy_first_response_only;
static void *task_buffer;
static uint8_t captured[8192];
static char response[4096];
static int response_status;
static unsigned last_timeout;
static int tls_error, tls_code;
static atomic_uint s_generation;
static uint64_t s_health_boot_id=UINT64_C(0x0123456789abcdef);
static native_health_snapshot_t health_snapshot;
static unsigned health_track_calls;
static bool fail_health_format;
static unsigned radio_actions;
static uint16_t radio_station;
static bool radio_enabled,radio_unavailable;
static int radio_result;
static unsigned direct_stops;
static void audio_service_stop(void) {++direct_stops;}
bool radio_control_snapshot(radio_control_snapshot_t *out) {
    if(radio_unavailable)return false;
    memset(out,0,sizeof(*out));out->item=out->count=UINT16_MAX;out->smartstart=true;
    memset(out->name,1,sizeof(out->name)-1);return true;
}
int radio_control_next(void) {++radio_actions;return radio_result;}
int radio_control_previous(void) {++radio_actions;return radio_result;}
int radio_control_toggle(void) {++radio_actions;return radio_result;}
int radio_control_stop(void) {++radio_actions;return radio_result;}
int radio_control_play(uint16_t item) {++radio_actions;radio_station=item;return radio_result;}
int radio_control_set_smartstart_enabled(bool enabled) {++radio_actions;radio_enabled=enabled;return radio_result;}
static int httpd_req_get_url_query_str(httpd_req_t *request,char *out,size_t capacity) {
    if(!request->query || strlen(request->query)>=capacity)return ESP_FAIL;
    strcpy(out,request->query);return ESP_OK;
}
static int httpd_query_key_value(const char *query,const char *key,char *out,size_t capacity) {
    size_t length=strlen(key);
    for (const char *p=query; p && *p; p=strchr(p,'&'),p=p ? p+1 : NULL) {
        if(!strncmp(p,key,length) && p[length]=='=') {
            p+=length+1;size_t size=strcspn(p,"&");if(size>=capacity)return ESP_FAIL;
            memcpy(out,p,size);out[size]=0;return ESP_OK;
        }
    }
    return ESP_FAIL;
}
#define configNUMBER_OF_CORES 2
#define MALLOC_CAP_8BIT 1
#define MALLOC_CAP_INTERNAL 2
#define MALLOC_CAP_DMA 4
typedef struct { size_t total_free_bytes,largest_free_block,minimum_free_bytes; } multi_heap_info_t;
static void *xTaskGetCurrentTaskHandle(void) {return (void *)1234;}
static unsigned uxTaskGetNumberOfTasks(void) {return 7;}
static unsigned esp_reset_reason(void) {return 1;}
static void heap_caps_get_info(multi_heap_info_t *info,unsigned caps) {
    assert(caps==MALLOC_CAP_8BIT);*info=(multi_heap_info_t){10000,9000,8000};
}
static size_t heap_caps_get_free_size(unsigned caps) {
    if(caps==MALLOC_CAP_DMA)return 4000;
    assert(caps==(MALLOC_CAP_8BIT|MALLOC_CAP_INTERNAL));return 8000;
}
static size_t heap_caps_get_largest_free_block(unsigned caps) {
    if(caps==MALLOC_CAP_DMA)return 3000;
    assert(caps==(MALLOC_CAP_8BIT|MALLOC_CAP_INTERNAL));return 7000;
}
void native_health_track_task(native_health_task_t role,void *task) {
    assert(role==NATIVE_HEALTH_HTTP && task==(void *)1234);++health_track_calls;
}
native_health_snapshot_t native_health_snapshot(void) {return health_snapshot;}
static bool format_health_for_test(char *body,size_t capacity,const native_health_snapshot_t *health,
                                   const native_health_runtime_t *runtime) {
    return !fail_health_format && native_health_format_json(body,capacity,health,runtime);
}
static unsigned health_stream_failures;
void native_health_stream_failure(uint32_t generation,uint32_t completion,int32_t result) {
    (void)result;assert(generation==atomic_load(&s_generation) && completion!=AUDIO_END_EOF);
    ++health_stream_failures;
}

static int64_t esp_timer_get_time(void) { return (int64_t)clock_us; }
static void vTaskDelay(unsigned ticks) { clock_us+=(uint64_t)ticks*1000; }
static void vTaskDelete(void *task) { assert(!task); ++deletes; }
static int esp_crt_bundle_attach(void *p) { (void)p; return ESP_OK; }
static const char *esp_err_to_name(int error) { (void)error; return "test"; }
static void *buffer_malloc(size_t size) {
    if (fail_buffer) return NULL;
    assert(!task_buffer); task_buffer=malloc(size); assert(task_buffer); return task_buffer;
}
static int xQueueReceive(void *,void *,unsigned);
static int xRingbufferSendAcquire(void *ring,void **p,size_t size,unsigned wait) {
    (void)wait; assert(ring==(void *)1); *p=malloc(size); assert(*p); return pdTRUE;
}
static int xRingbufferSendComplete(void *,void *);
static int native_audio_output_get_volume(void) { return 123; }
static int native_audio_output_get_balance(void) { return -4; }
static int httpd_resp_set_type(httpd_req_t *r,const char *type) {
    (void)r; assert(!strcmp(type,"application/json; charset=utf-8")); return ESP_OK;
}
static int httpd_resp_set_hdr(httpd_req_t *r,const char *key,const char *value) {
    (void)r; assert(!strcmp(key,"Cache-Control") && !strcmp(value,"no-store")); return ESP_OK;
}
static int httpd_resp_sendstr(httpd_req_t *r,const char *text) {
    (void)r; assert(strlen(text)<sizeof(response)); strcpy(response,text); response_status=200; return ESP_OK;
}
static int httpd_resp_send_err(httpd_req_t *r,int status,const char *text) {
    (void)r; (void)text; response_status=status; return ESP_FAIL;
}
static esp_http_client_handle_t esp_http_client_init(const esp_http_client_config_t *config) {
    assert(config->disable_auto_redirect && config->max_redirection_count==5);
    assert(config->crt_bundle_attach==esp_crt_bundle_attach);
    if (fail_client) return NULL;
    client=(test_client_t){.config=*config};return &client;
}
static int esp_http_client_set_header(esp_http_client_handle_t c,const char *key,const char *value) {
    assert(c==&client && !strcmp(key,"Icy-MetaData") && !strcmp(value,"1"));return ESP_OK;
}
static int esp_http_client_set_timeout_ms(esp_http_client_handle_t c,int timeout) {
    assert(c==&client && timeout>0 && timeout<=10000);last_timeout=(unsigned)timeout;return ESP_OK;
}
static int esp_http_client_open(esp_http_client_handle_t c,int write_length) {
    assert(c==&client && !write_length && opens<8);++opens;
    clock_us+=(uint64_t)open_delay_ms*1000;
    if(open_error)return open_error;
    c->open=true;return ESP_OK;
}
static void header(const char *key,const char *value) {
    esp_http_client_event_t event={HTTP_EVENT_ON_HEADER,client.config.user_data,(char *)key,(char *)value};
    assert(client.config.event_handler(&event)==ESP_OK);
}
static int64_t esp_http_client_fetch_headers(esp_http_client_handle_t c) {
    assert(c==&client);++fetches;clock_us+=(uint64_t)header_delay_ms*1000;
    if(header_error)return -1;
    // ICY must not depend on the first eight saved SDK header slots.
    for(unsigned i=0;i<32;++i)header("X-Test","value");
    header("Content-Type","audio/mpeg"); // Deliberately wrong for AAC fixtures.
    if(interval_text && (!icy_first_response_only || opens==1))header("IcY-MeTaInT",interval_text);
    if(second_interval)header("icy-metaint",second_interval);
    return (int64_t)body_size;
}
static int esp_http_client_get_status_code(esp_http_client_handle_t c) {
    assert(c==&client && opens);return statuses[opens-1];
}
static int esp_http_client_set_redirection(esp_http_client_handle_t c) {
    assert(c==&client);++redirects;return redirect_error;
}
static int esp_http_client_close(esp_http_client_handle_t c) {
    assert(c==&client);if(c->open){++closes;c->open=false;}return ESP_OK;
}
static int esp_http_client_cleanup(esp_http_client_handle_t c) {
    assert(c==&client);++cleanups;return esp_http_client_close(c);
}
static int esp_http_client_read(esp_http_client_handle_t c,char *buffer,int size) {
    assert(c==&client && c->open && last_timeout==250);++reads;
    if(eagain){--eagain;clock_us+=250000;tls_error=ESP_ERR_MBEDTLS_SSL_READ_FAILED;tls_code=-ESP_TLS_ERR_SSL_TIMEOUT;return -ESP_ERR_HTTP_EAGAIN;}
    if(cancel_read){cancel_read=false;unsigned gen=atomic_fetch_add(&s_generation,1)+1;native_state_begin_audio(&state,gen,NULL,"stopped");}
    size_t left=body_size-body_offset;
    if(!left){if(stall_body)clock_us+=250000;return 0;}
    size_t n=left<chunk_size?left:chunk_size;if(n>(size_t)size)n=(size_t)size;
    memcpy(buffer,body_data+body_offset,n);body_offset+=n;
    if(fatal_tls||retry_tls){tls_error=ESP_ERR_MBEDTLS_SSL_READ_FAILED;tls_code=fatal_tls?12345:-ESP_TLS_ERR_SSL_WANT_READ;fatal_tls=retry_tls=false;}
    return (int)n;
}
static int esp_http_client_get_and_clear_last_tls_error(esp_http_client_handle_t c,int *code,void *flags) {
    (void)flags;assert(c==&client);*code=tls_code;int result=tls_error;tls_code=tls_error=0;return result;
}
static bool esp_http_client_is_complete_data_received(esp_http_client_handle_t c) {
    assert(c==&client);return !stall_body && body_offset==body_size;
}
size_t strlcpy(char *to,const char *from,size_t capacity) {
    size_t n=strlen(from);if(capacity){size_t copy=n<capacity-1?n:capacity-1;memcpy(to,from,copy);to[copy]=0;}return n;
}
#define malloc buffer_malloc
#define native_health_format_json format_health_for_test
#include "production.inc"
#undef native_health_format_json
#undef malloc

static int xQueueReceive(void *queue,void *destination,unsigned wait) {
    assert(queue==(void *)2 && wait==portMAX_DELAY);
    if(queued++)longjmp(task_exit,1);
    play_command_t *command=destination;memset(command,0,sizeof(*command));
    command->generation=atomic_load(&s_generation);command->requested_codec=(native_codec_t)selected_codec;
    strcpy(command->url,"https://fixture.example/audio");return pdTRUE;
}
static int xRingbufferSendComplete(void *ring,void *data) {
    assert(ring==(void *)1);encoded_packet_t *p=data;++packets;
    assert(p->generation==atomic_load(&s_generation));
    if(p->end_of_stream){assert(!p->data_size && !terminal);terminal=p->end_of_stream;}
    else {
        assert(!terminal && p->codec!=NATIVE_CODEC_AUTO);
        assert(encoded_bytes+p->data_size<=sizeof(captured));
        memcpy(captured+encoded_bytes,p->data,p->data_size);encoded_bytes+=p->data_size;
        assert(!state.audio_running); // Probe success is not decoded PCM progress.
        selected_codec=(unsigned)p->codec;
    }
    free(p);return pdTRUE;
}
static void setup(const uint8_t *data,size_t size,unsigned chunk) {
    assert(!task_buffer);++cases;memset(&client,0,sizeof(client));
    clock_us=0;queued=opens=fetches=redirects=reads=cleanups=closes=deletes=0;
    encoded_bytes=terminal=packets=0;selected_codec=NATIVE_CODEC_AUTO;
    health_stream_failures=0;
    eagain=open_delay_ms=header_delay_ms=0;chunk_size=chunk;
    open_error=header_error=redirect_error=tls_error=tls_code=0;
    for(unsigned i=0;i<8;++i)statuses[i]=200;
    interval_text=second_interval=NULL;
    cancel_read=fail_client=fail_buffer=stall_body=fatal_tls=retry_tls=false;
    icy_first_response_only=false;
    body_data=data;body_size=size;body_offset=0;
    s_state=&state;s_commands=(void *)2;s_encoded=(void *)1;
    atomic_store(&s_generation,cases);atomic_store(&s_decoder_released_generation,cases);
    atomic_store(&s_failed_generation,0);
    native_state_begin_audio(&state,cases,"fixture","connecting");
}
static void play(void) {
    if(!setjmp(task_exit))stream_task(NULL);
    free(task_buffer);task_buffer=NULL;
}
static void exact(const uint8_t *expected,size_t size,unsigned codec,unsigned reason) {
    assert(encoded_bytes==size && !memcmp(captured,expected,size));
    assert(selected_codec==codec && terminal==reason && cleanups==1 && !client.open);
}

int main(void) {
    native_state_init(&state);
    const uint8_t aac[]={0xff,0xf1,0x4c,0x80,0x01,0x9f,0xfc,1,2,3,4,5};
    const uint8_t mp3[]={0xff,0xfb,0x90,0,1,2,3,4};
    const uint8_t flac[]={'f','L','a','C',0,0,0,34,1,2};
    const uint8_t ogg[]={'O','g','g','S',0,1,2,3};
    const uint8_t *fixtures[]={aac,mp3,flac,ogg};const size_t sizes[]={sizeof(aac),sizeof(mp3),sizeof(flac),sizeof(ogg)};
    const unsigned codecs[]={NATIVE_CODEC_AAC,NATIVE_CODEC_MP3,NATIVE_CODEC_FLAC,NATIVE_CODEC_OGG};
    for(unsigned f=0;f<4;++f)for(unsigned chunk=1;chunk<=2048;chunk=chunk==1?7:chunk==7?2048:2049) {
        setup(fixtures[f],sizes[f],chunk);play();exact(fixtures[f],sizes[f],codecs[f],AUDIO_END_EOF);
    }
    setup(aac,sizeof(aac),2048);eagain=2;retry_tls=true;play();exact(aac,sizeof(aac),NATIVE_CODEC_AAC,AUDIO_END_EOF);
    assert(reads==4 && clock_us>=500000);
    setup(aac,sizeof(aac),2048);fatal_tls=true;play();exact(aac,sizeof(aac),NATIVE_CODEC_AAC,AUDIO_END_READ_FAILED);
    assert(reads==1 && closes==1 && health_stream_failures==1);
    setup(aac,sizeof(aac),2048);cancel_read=true;play();
    assert(!encoded_bytes && !terminal && cleanups==1 && !strcmp(state.stream_format,"stopped"));
    assert(!health_stream_failures);
    setup(aac,sizeof(aac),2048);statuses[0]=302;statuses[1]=200;play();
    exact(aac,sizeof(aac),NATIVE_CODEC_AAC,AUDIO_END_EOF);assert(opens==2 && redirects==1);
    const char *redirect_icy[]={"5","-1"};
    for(unsigned i=0;i<2;++i) {
        setup(aac,sizeof(aac),1);statuses[0]=302;interval_text=redirect_icy[i];icy_first_response_only=true;
        play();exact(aac,sizeof(aac),NATIVE_CODEC_AAC,AUDIO_END_EOF);
    }
    setup(aac,sizeof(aac),2048);for(unsigned i=0;i<8;++i)statuses[i]=301;play();
    assert(opens==6 && redirects==5 && !packets && cleanups==1);
    const int errors[]={401,404,429,500};
    for(unsigned i=0;i<4;++i){setup(aac,sizeof(aac),2048);statuses[0]=errors[i];play();assert(!packets && !reads && cleanups==1 && !strcmp(state.stream_format,"connection failed"));}
    setup(aac,sizeof(aac),2048);open_error=ESP_FAIL;play();assert(!packets && !fetches && cleanups==1);
    setup(aac,sizeof(aac),2048);header_error=1;play();assert(!packets && !reads && cleanups==1);
    setup(aac,sizeof(aac),2048);statuses[0]=302;redirect_error=ESP_FAIL;play();assert(!packets && opens==1 && cleanups==1);
    setup(aac,sizeof(aac),2048);open_delay_ms=5000;header_delay_ms=5001;play();assert(!packets && !reads && cleanups==1 && clock_us==10001000);
    setup(aac,sizeof(aac),2048);fail_client=true;play();assert(!opens && !cleanups && !strcmp(state.stream_format,"HTTP allocation failed"));
    setup(aac,sizeof(aac),2048);fail_buffer=true;play();assert(deletes==1 && !queued && !opens);
    setup(aac,2,1);stall_body=true;play();assert(!encoded_bytes && terminal==AUDIO_END_FORMAT_UNKNOWN && clock_us>=10000000);
    setup(NULL,0,1);play();assert(!encoded_bytes && terminal==AUDIO_END_FORMAT_UNKNOWN);
    uint8_t junk[5000]={0};setup(junk,sizeof(junk),2048);play();assert(!encoded_bytes && terminal==AUDIO_END_FORMAT_UNKNOWN && reads<=3);
    setup(junk,12,2048);selected_codec=NATIVE_CODEC_AAC;play();exact(junk,12,NATIVE_CODEC_AAC,AUDIO_END_EOF);

    uint8_t wire[64]={0};memcpy(wire,aac,5);wire[5]=2;
    memcpy(wire+6,"StreamTitle='quote \" \\';",24);memcpy(wire+38,aac+5,5);wire[43]=0;memcpy(wire+44,aac+10,2);
    for(unsigned chunk=1;chunk<=2048;chunk=chunk==1?7:chunk==7?2048:2049) {
        setup(wire,46,chunk);interval_text="5";second_interval=" 5 ";play();
        exact(aac,sizeof(aac),NATIVE_CODEC_AAC,AUDIO_END_EOF);assert(!strcmp(state.title,"quote \" \\"));
    }
    setup(wire,20,1);interval_text="5";play();assert(terminal==AUDIO_END_METADATA_TRUNCATED && !state.title[0]);
    const char *bad[]={"-1","0x10","4294967296","1x"};
    for(unsigned i=0;i<4;++i){setup(aac,sizeof(aac),2048);interval_text=bad[i];play();assert(!reads && !packets && !strcmp(state.stream_format,"invalid ICY interval"));}
    setup(aac,sizeof(aac),2048);interval_text="5";second_interval="6";play();assert(!reads && !packets);

    httpd_req_t request={0};native_state_begin_audio(&state,1000,"station \" \\","format\nline");
    native_state_set_audio(&state,1000,true,NULL);
    native_state_set_title(&state,1000,"title \" \\ Привет 🌍\n");
    native_state_set_title(&state,999,"old title");assert(status_handler(&request)==ESP_OK && response_status==200);
    printf("STATUS=%s\n",response);
    memset(state.station,1,sizeof(state.station)-1);state.station[sizeof(state.station)-1]=0;
    memset(state.title,1,sizeof(state.title)-1);state.title[sizeof(state.title)-1]=0;
    memset(state.stream_format,1,sizeof(state.stream_format)-1);state.stream_format[sizeof(state.stream_format)-1]=0;
    assert(status_handler(&request)==ESP_OK && response_status==200);printf("MAX_STATUS=%s\n",response);
    char long_title[201];for(unsigned i=0;i<100;++i){long_title[i*2]=(char)0xd0;long_title[i*2+1]=(char)0xb0;}long_title[200]=0;
    native_state_set_title(&state,1000,long_title);
    assert(status_handler(&request)==ESP_OK && response_status==200);printf("UTF8_STATUS=%s\n",response);
    native_state_begin_audio(&state,1001,NULL,"connecting");native_state_set_title(&state,1000,"obsolete");
    assert(!state.title[0]);
    clock_us=12345000;
    health_snapshot=(native_health_snapshot_t){.faults={.allocation_failures=3,.decoder_failures=2}};
    assert(health_handler(&request)==ESP_OK && response_status==200);printf("HEALTH=%s\n",response);
    assert(health_track_calls==1 && health_snapshot.faults.allocation_failures==3);
    fail_health_format=true;
    assert(health_handler(&request)==ESP_FAIL && response_status==500 && health_track_calls==2);
    assert(health_snapshot.faults.decoder_failures==2 && state.audio_generation==1001);
    native_state_set_pending(&state,1001,true);
    assert(radio_handler(&request)==ESP_OK && !radio_actions);printf("RADIO=%s\n",response);
    request.method=HTTP_POST;
    const char *actions[]={"action=next","action=previous","action=toggle","action=stop","action=play&station=65535",
        "action=smartstart&enabled=1","action=smartstart&enabled=0"};
    for(unsigned i=0;i<sizeof(actions)/sizeof(actions[0]);++i) {
        request.query=actions[i];assert(radio_handler(&request)==ESP_OK && radio_actions==i+1);
    }
    assert(radio_station==65535 && !radio_enabled);
    const char *bad_actions[]={NULL,"","action=","action=unknown","action=play","action=play&station=0",
        "action=play&station=-1","action=play&station=+1","action=play&station=1junk","action=play&station=65536",
        "action=play&station=99999999999999999999999","action=play&station= 1","action=smartstart",
        "action=smartstart&enabled=2","action=smartstart&enabled=01"};
    unsigned count=radio_actions;
    for(unsigned i=0;i<sizeof(bad_actions)/sizeof(bad_actions[0]);++i) {
        request.query=bad_actions[i];assert(radio_handler(&request)==ESP_FAIL && response_status==400 && radio_actions==count);
    }
    request.query="action=next";radio_result=ESP_FAIL;
    assert(radio_handler(&request)==ESP_FAIL && response_status==500);
    radio_result=ESP_OK;assert(stop_handler(&request)==ESP_OK && !direct_stops);
    radio_result=ESP_FAIL;assert(stop_handler(&request)==ESP_OK && direct_stops==1);
    radio_result=ESP_ERR_NOT_FOUND;assert(radio_handler(&request)==ESP_FAIL && response_status==400);
    request.method=HTTP_GET;radio_unavailable=true;
    assert(radio_handler(&request)==ESP_FAIL && response_status==500);
    printf("PASS CYD stream cases=%u: actual HTTP/ICY/probe task, MIME mismatch, redirects/status/deadline, retry/fatal TLS, cancellation/OOM, exact replay and status JSON\n",cases);
    return 0;
}
