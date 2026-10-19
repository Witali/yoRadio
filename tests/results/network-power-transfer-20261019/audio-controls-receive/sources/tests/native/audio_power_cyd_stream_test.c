#include <assert.h>
#include <setjmp.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include "audio_service.h"
#include "native_network_power.h"
#include "stream_probe.h"
#include "stream_body.h"
#include "stream_bitrate.h"
#include "audio_completion.h"

typedef void *QueueHandle_t,*RingbufHandle_t;
enum {ESP_ERR_HTTP_EAGAIN=0x7007,ESP_ERR_MBEDTLS_SSL_READ_FAILED=0x8000,HTTP_EVENT_ON_HEADER=1};
#define ESP_TLS_ERR_SSL_TIMEOUT (-0x6800)
#define ESP_TLS_ERR_SSL_WANT_READ (-0x6900)
#define ESP_TLS_ERR_SSL_WANT_WRITE (-0x6880)
#define ESP_LOGE(...) ((void)0)
#define ESP_LOGW(...) ((void)0)
typedef struct {int event_id;void *user_data;char *header_key,*header_value;} esp_http_client_event_t;
typedef struct {const char *url,*user_agent;int timeout_ms,buffer_size,buffer_size_tx,max_redirection_count;bool disable_auto_redirect,keep_alive_enable;int (*crt_bundle_attach)(void *);int (*event_handler)(esp_http_client_event_t *);void *user_data;} esp_http_client_config_t;
typedef struct {esp_http_client_config_t config;bool live;} test_client_t;
typedef test_client_t *esp_http_client_handle_t;
#include "stream-types.inc"
static native_state_t state,*s_state=&state;
static SemaphoreHandle_t s_control_lock;
static QueueHandle_t s_commands=(void *)2;
static RingbufHandle_t s_encoded=(void *)1;
static uint8_t buffer[STREAM_CHUNK_SIZE],*s_stream_buffer=buffer;
static atomic_uint s_generation,s_decoder_released_generation,s_failed_generation;
static atomic_uint s_start_state=AUDIO_START_READY;
static bool s_last_command_valid,s_maintenance_resume;
static play_command_t s_last_command,queued_command;
static test_client_t client;
static unsigned mode,attempts,cleanups,eos,received,groups;
static bool queued,cleanup_play;
static int64_t now_us;
static jmp_buf task_exit;
static const uint8_t aac[]={0xff,0xf1,0x4c,0x80,0x01,0x9f,0xfc,1,2,3,4,5};
static bool maintenance_active(void){return false;}
static void maintenance_ack(unsigned bits){(void)bits;assert(false);}
static void maintenance_park(uint32_t generation){(void)generation;assert(false);}
#define MAINTENANCE_STREAM 1U
static void network_service_audio_accept(uint32_t generation,bool active){native_network_power_accept(generation,active);}
static void network_service_audio_receive(uint32_t generation){native_network_power_receive(generation);}
static void network_service_audio_finish(uint32_t generation){native_network_power_finish(generation);}
static void expect_power(bool active){native_network_power_snapshot_t power;native_network_power_snapshot(&power);assert(power.generation==atomic_load(&s_generation)&&power.desired_active==active);}
static int xQueueOverwrite(void *queue,const void *data){assert(queue==s_commands);queued_command=*(const play_command_t *)data;expect_power(true);queued=true;atomic_store(&s_decoder_released_generation,queued_command.generation);return pdTRUE;}
static int xQueueReceive(void *queue,void *data,unsigned wait){
    assert(queue==s_commands&&wait==50);
    if(queued){expect_power(true);*(play_command_t *)data=queued_command;queued=false;return pdTRUE;}
    expect_power(false);assert(!client.live);
    if(eos==AUDIO_END_EOF)assert(state.audio_pending); // Receive EOF precedes the deferred PCM terminal marker.
    longjmp(task_exit,1);
}
static int64_t esp_timer_get_time(void){return now_us;}
static void vTaskDelay(unsigned ticks){now_us+=(int64_t)ticks*1000;}
static const char *esp_err_to_name(int error){(void)error;return "fixture";}
static int esp_crt_bundle_attach(void *p){(void)p;return ESP_OK;}
static int xRingbufferSendAcquire(void *ring,void **out,size_t size,unsigned wait){(void)wait;assert(ring==s_encoded);*out=malloc(size);assert(*out);return pdTRUE;}
static int xRingbufferSendComplete(void *ring,void *data){assert(ring==s_encoded);encoded_packet_t *packet=data;if(packet->end_of_stream)eos=packet->end_of_stream;free(data);return pdTRUE;}
static esp_http_client_handle_t esp_http_client_init(const esp_http_client_config_t *config){expect_power(true);++attempts;if(mode==1)return NULL;assert(!client.live);client=(test_client_t){.config=*config,.live=true};return &client;}
static int esp_http_client_set_header(void *c,const char *key,const char *value){assert(c&&key&&value);return ESP_OK;}
static int esp_http_client_set_timeout_ms(void *c,int value){assert(c&&value>0);return ESP_OK;}
static int esp_http_client_open(void *c,int length){assert(c&&length==0);if(mode==2)return ESP_FAIL;if(mode==5)audio_service_stop();return ESP_OK;}
static int64_t esp_http_client_fetch_headers(esp_http_client_handle_t c){if(mode==3){esp_http_client_event_t event={.event_id=HTTP_EVENT_ON_HEADER,.user_data=c->config.user_data,.header_key="icy-metaint",.header_value="invalid"};c->config.event_handler(&event);}return mode==4?-1:12;}
static int esp_http_client_get_status_code(void *c){assert(c);return 200;}
static int esp_http_client_set_redirection(void *c){assert(c);return ESP_OK;}
static int esp_http_client_close(void *c){assert(c);return ESP_OK;}
static int esp_http_client_cleanup(esp_http_client_handle_t c){assert(c&&c->live);c->live=false;++cleanups;if(cleanup_play){cleanup_play=false;assert(audio_service_play("http://next.invalid/audio",NATIVE_CODEC_AAC)==ESP_OK);}return ESP_OK;}
static int esp_http_client_read(void *c,char *out,int size){assert(c&&size>=12);if(mode==6){audio_service_stop();return 0;}if(mode==7)return ESP_FAIL;if(received++)return 0;memcpy(out,aac,sizeof(aac));return sizeof(aac);}
static bool esp_http_client_is_complete_data_received(void *c){assert(c);return true;}
static int esp_http_client_get_and_clear_last_tls_error(void *c,int *code,void *flags){assert(c);(void)flags;*code=0;return ESP_OK;}
void native_health_stream_failure(uint32_t generation,uint32_t completion,int32_t result){(void)generation;(void)completion;(void)result;}
size_t strlcpy(char *out,const char *text,size_t capacity){size_t size=strlen(text);if(capacity){size_t n=size<capacity-1?size:capacity-1;memcpy(out,text,n);out[n]=0;}return size;}
#define encoded_acquire xRingbufferSendAcquire
#define encoded_commit xRingbufferSendComplete
#include "stream.inc"
int main(void){
    native_state_init(&state);s_control_lock=xSemaphoreCreateMutex();
    for(mode=0;mode<9;++mode){
        attempts=cleanups=eos=received=0;now_us=0;queued=false;cleanup_play=mode==8;client.live=false;
        assert(audio_service_play("http://fixture.invalid/audio",NATIVE_CODEC_AAC)==ESP_OK);
        if(!setjmp(task_exit))stream_task(NULL);
        assert(attempts==(mode==8?2U:1U));if(mode==1)assert(!cleanups);else assert(cleanups==attempts);
        expect_power(false);++groups;
    }
    pthread_mutex_destroy(state.lock);free(state.lock);pthread_mutex_destroy(s_control_lock);free(s_control_lock);
    printf("PASS actual CYD receive/power: %u groups; allocation/open/header/read errors, cancel/open/read, EOF before PCM drain, old cleanup/new Play\n",groups);
}
