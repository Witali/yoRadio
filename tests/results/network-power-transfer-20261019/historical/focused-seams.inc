#pragma once
// Resource-tracking boundaries, not codec/allocator/driver implementations.
typedef int esp_err_t;
enum { ESP_FAIL=-1, ESP_OK=0, ESP_ERR_INVALID_ARG, ESP_ERR_INVALID_STATE,
       ESP_ERR_TIMEOUT, ESP_ERR_NOT_SUPPORTED, ESP_ERR_NO_MEM,
       ESP_ERR_HTTP_CONNECT, ESP_ERR_HTTP_WRITE_DATA, ESP_ERR_HTTP_EAGAIN,
       ESP_ERR_MBEDTLS_SSL_READ_FAILED, ESP_ERR_HTTP_FETCH_HEADER, ESP_ERR_HTTP_MAX_REDIRECT };
#define ESP_TLS_ERR_SSL_TIMEOUT (-93)
#define ESP_TLS_ERR_SSL_WANT_READ (-94)
#define ESP_TLS_ERR_SSL_WANT_WRITE (-95)
#define ESP_RETURN_ON_ERROR(expr,...) do { int e=(expr); if(e)return e; } while(0)
#define ESP_LOGE(...) ((void)0)
#define ESP_LOGI(...) ((void)0)
#define ESP_LOGW(...) ((void)0)
static const char *esp_err_to_name(int e) {(void)e;return "host error";}
#include "audio_service.h"
#include "native_audio_output.h"
#include "cpu_profiler.h"
#include "audio_completion.h"
#include "audio_pipeline_probe.h"
#include "stream_bitrate.h"
#include "stream_probe.h"
#include "adaptive_input.h"
#include "pipeline_profile.h"
#include "rx_buffer_diagnostic.h"
#include "heap_fragment_probe.h"
#include "tls_path_profile.h"
#include "icy_title.h"
#include "decoder_arena.h"

typedef int esp_audio_err_t;
typedef unsigned esp_audio_simple_dec_type_t;
typedef void *esp_audio_simple_dec_handle_t;
typedef struct {unsigned dec_type;void *dec_cfg;unsigned cfg_size;bool use_frame_dec;} esp_audio_simple_dec_cfg_t;
typedef struct {uint8_t *buffer;size_t len,consumed;unsigned eos;} esp_audio_simple_dec_raw_t;
typedef struct {uint8_t *buffer;size_t len,needed_size,decoded_size;} esp_audio_simple_dec_out_t;
typedef struct {uint32_t sample_rate,bitrate;uint8_t bits_per_sample,channel;} esp_audio_simple_dec_info_t;
enum {ESP_AUDIO_ERR_OK=0,ESP_AUDIO_ERR_BUFF_NOT_ENOUGH=-8,ESP_AUDIO_ERR_MEM_LACK=-9,
      ESP_AUDIO_ERR_DATA_LACK=-10,ESP_AUDIO_ERR_FAIL=-11,ESP_AUDIO_SIMPLE_DEC_TYPE_MP3=1,ESP_AUDIO_SIMPLE_DEC_TYPE_AAC,
      ESP_AUDIO_SIMPLE_DEC_TYPE_FLAC,ESP_AUDIO_SIMPLE_DEC_TYPE_OGG};
#include "native_aac_decoder.h"
#include "custom_flac_adapter.h"
#include "custom_legacy_adapter.h"
static atomic_uint decoder_handles,codec_type,decoder_faults;
static atomic_bool hold_codec_close,codec_close_entered,arena_reject_discard;
static atomic_bool defer_codec_tail;
static _Atomic(void *) deferred_codec;
static atomic_uint arena_live,arena_blocks;
static void *legacy_arena;
struct native_aac_decoder {unsigned marker;};
struct custom_flac_decoder {unsigned marker;};
struct custom_legacy_decoder {unsigned marker;};
static void *codec_create(unsigned type) {assert(role==ROLE_DECODER);void *p=malloc(32);assert(p);++decoder_handles;++arena_blocks;arena_live+=32;codec_type=type;return p;}
static void codec_destroy(void *p) {if(!p)return;assert(role==ROLE_DECODER&&decoder_handles);codec_close_entered=true;while(hold_codec_close)vTaskDelay(1);--decoder_handles;if(defer_codec_tail){assert(!deferred_codec);deferred_codec=p;return;}--arena_blocks;arena_live-=32;free(p);}
int decoder_register_codecs(void) {return ESP_OK;}
static int esp_audio_simple_dec_open(const esp_audio_simple_dec_cfg_t *cfg,void **out) {*out=codec_create(cfg->dec_type);return ESP_OK;}
static void esp_audio_simple_dec_close(void *p) {codec_destroy(p);}
static int esp_audio_simple_dec_process(void *p,esp_audio_simple_dec_raw_t *raw,esp_audio_simple_dec_out_t *out) {assert(role==ROLE_DECODER&&p);barrier_hit("codec");raw->consumed=raw->len;out->decoded_size=raw->len?3072:0;assert(out->len>=out->decoded_size);memset(out->buffer,0x11,out->decoded_size);return ESP_OK;}
static int esp_audio_simple_dec_get_info(void *p,esp_audio_simple_dec_info_t *out) {assert(role==ROLE_DECODER&&p);*out=(esp_audio_simple_dec_info_t){16000,128000,16,1};return ESP_OK;}
native_aac_decoder_t *native_aac_decoder_create(void) {return codec_create(ESP_AUDIO_SIMPLE_DEC_TYPE_AAC);}
void native_aac_decoder_destroy(native_aac_decoder_t *p) {codec_destroy(p);}
int native_aac_decoder_process(native_aac_decoder_t *p,esp_audio_simple_dec_raw_t *raw,esp_audio_simple_dec_out_t *out) {return esp_audio_simple_dec_process(p,raw,out);}
int native_aac_decoder_get_info(native_aac_decoder_t *p,esp_audio_simple_dec_info_t *out) {return esp_audio_simple_dec_get_info(p,out);}
const char *native_aac_decoder_label(native_aac_decoder_t *p,const esp_audio_simple_dec_info_t *i,bool *pcm) {(void)p;(void)i;*pcm=true;return "AAC PCM";}
unsigned native_aac_decoder_source_channels(native_aac_decoder_t *p) {(void)p;return 1;}
custom_flac_decoder_t *custom_flac_decoder_create(void) {return codec_create(ESP_AUDIO_SIMPLE_DEC_TYPE_FLAC);}
void custom_flac_decoder_destroy(custom_flac_decoder_t *p) {codec_destroy(p);}
size_t custom_flac_decoder_memory_used(const custom_flac_decoder_t *p) {return p?32:0;}
int custom_flac_decoder_feed(custom_flac_decoder_t *p,const uint8_t *data,size_t size,bool eos,custom_flac_pcm_callback_t cb,void *ctx,custom_flac_feed_stats_t *stats) {(void)data;(void)eos;assert(role==ROLE_DECODER&&p);barrier_hit("codec");uint8_t pcm[3072]={0};custom_flac_info_t info={16000,24,1,16,128000};*stats=(custom_flac_feed_stats_t){1,1,1,(uint32_t)size};return size&&!cb(ctx,&info,pcm,sizeof(pcm))?-8:0;}
custom_legacy_decoder_t *custom_legacy_decoder_create(custom_legacy_kind_t kind) {if(!legacy_arena){legacy_arena=malloc(512);assert(legacy_arena);}return codec_create(kind==CUSTOM_LEGACY_AAC?ESP_AUDIO_SIMPLE_DEC_TYPE_AAC:ESP_AUDIO_SIMPLE_DEC_TYPE_MP3);}
void custom_legacy_decoder_destroy(custom_legacy_decoder_t *p) {codec_destroy(p);}
bool custom_legacy_decoder_discard_arena(void) {assert(role==ROLE_DECODER);barrier_hit("arena_discard");if(arena_reject_discard)return false;assert(!decoder_handles);free(legacy_arena);legacy_arena=NULL;return true;}
size_t custom_legacy_decoder_memory_used(const custom_legacy_decoder_t *p) {return p?544:0;}
int custom_legacy_decoder_feed(custom_legacy_decoder_t *p,const uint8_t *data,size_t size,bool eos,custom_legacy_pcm_callback_t cb,void *ctx,custom_legacy_feed_stats_t *stats) {(void)data;(void)eos;assert(role==ROLE_DECODER&&p);barrier_hit("codec");uint8_t pcm[3072]={0};custom_legacy_info_t info={.sample_rate=16000,.bits_per_sample=16,.channels=1,.bitrate=128000,.stream_sample_rate=16000,.stream_channels=1};*stats=(custom_legacy_feed_stats_t){1,1,1,(uint32_t)size};return size&&!cb(ctx,&info,pcm,sizeof(pcm))?-8:0;}
bool decoder_arena_init(void) {return true;}
bool decoder_arena_select(bool value) {static _Thread_local bool selected;bool old=selected;selected=value;return old;}
decoder_arena_stats_t decoder_arena_stats(void) {return (decoder_arena_stats_t){.live=arena_live,.blocks=arena_blocks};}
void cpu_profiler_decoder_failure(uint32_t c,decoder_failure_stage_t s,int32_t r,uint32_t e,uint32_t n) {(void)c;(void)s;(void)r;(void)e;(void)n;++decoder_faults;}
static int audio_level_led_init(void) {return ESP_OK;}
static void audio_level_led_update_pcm(const uint8_t *p,size_t n,uint8_t b,uint8_t c) {(void)p;(void)n;(void)b;(void)c;}
static atomic_bool watchdog_enabled=true;
static bool runtime_settings_get_watchdog(void) {return watchdog_enabled;}
static uint8_t runtime_settings_get_station_timeout_sec(void) {return 10;}
static uint8_t runtime_settings_get_audio_buffer_blocks(void) {return 10;}
/* Actual historical network power function is linked by focused test. */
static void tls_input_reserve_bind(adaptive_input_t *q) {(void)q;}
static void tls_input_reserve_prepare_connection(void) {}
static void tls_input_reserve_poll(void) {}

static struct {atomic_bool allocated,running;atomic_uint retained,discarded;} driver;
static atomic_bool fail_disable,fail_delete,pause_requested;
#ifdef CONFIG_YORADIO_DIRECT_DMA_PCM
static native_audio_pcm_lease_t *retained_head;
static void release_retained(void) {while(retained_head){native_audio_pcm_lease_t *p=retained_head;retained_head=p->next;assert(driver.retained);--driver.retained;p->release(p);++driver.discarded;}}
#endif
int native_audio_output_init(void) {return ESP_OK;}
void native_audio_output_request_pause(bool value) {if(value)maintenance_pause_requested();pause_requested=value;}
void native_audio_output_discard_pcm(void) {assert(role==ROLE_OUTPUT);
#ifdef CONFIG_YORADIO_DIRECT_DMA_PCM
release_retained();
#endif
}
int native_audio_output_pause(void) {assert(role==ROLE_OUTPUT);native_audio_output_discard_pcm();barrier_hit("disable");if(fail_disable)return ESP_FAIL;driver.running=false;if(fail_delete)return ESP_FAIL;driver.allocated=false;return ESP_OK;}
int native_audio_output_configure(uint32_t rate) {assert(role==ROLE_OUTPUT&&rate);if(pause_requested)return ESP_ERR_INVALID_STATE;driver.allocated=driver.running=true;return ESP_OK;}
int native_audio_output_write_pcm(uint8_t *p,size_t n,uint8_t b,uint8_t c) {assert(role==ROLE_OUTPUT&&p&&n&&b&&c);barrier_hit("write");return pause_requested?ESP_ERR_INVALID_STATE:ESP_OK;}
int native_audio_output_flush_pcm(void) {native_audio_output_discard_pcm();return ESP_OK;}
void native_audio_output_idle(void) {vTaskDelay(1);}
const char *native_audio_output_name(void) {return "resource boundary";}
#ifdef CONFIG_YORADIO_DIRECT_DMA_PCM
int native_audio_output_submit_pcm(native_audio_pcm_lease_t *lease,uint8_t *p,size_t n,uint8_t b,uint8_t c,void (*release)(native_audio_pcm_lease_t *)) {assert(role==ROLE_OUTPUT&&p&&n&&b&&c);lease->release=release;lease->next=retained_head;retained_head=lease;++driver.retained;barrier_hit("write");if(pause_requested){release_retained();return ESP_ERR_INVALID_STATE;}if(driver.retained>1){native_audio_pcm_lease_t *old=lease->next;lease->next=old->next;--driver.retained;old->release(old);}return ESP_OK;}
#endif

typedef struct {const char *url,*user_agent;int timeout_ms,buffer_size,buffer_size_tx,max_redirection_count;void *crt_bundle_attach;bool disable_auto_redirect,keep_alive_enable;} esp_http_client_config_t;
typedef struct {bool closed;unsigned reads;char url[512];} *esp_http_client_handle_t;
static void *esp_crt_bundle_attach;
static atomic_uint http_clients,http_inits,http_closes;
static atomic_bool no_body,mp3_start,mp3_full,aac_start,tls_error,redirect_once,connect_error,terminal_response;
static pthread_mutex_t url_mutex=PTHREAD_MUTEX_INITIALIZER;
static char observed_url[512];
static esp_http_client_handle_t esp_http_client_init(const esp_http_client_config_t *cfg) {assert(role==ROLE_STREAM);esp_http_client_handle_t c=calloc(1,sizeof(*c));assert(c);strlcpy(c->url,cfg->url,sizeof(c->url));pthread_mutex_lock(&url_mutex);strlcpy(observed_url,cfg->url,sizeof(observed_url));pthread_mutex_unlock(&url_mutex);++http_inits;++http_clients;return c;}
static int esp_http_client_set_header(void *c,const char *k,const char *v) {assert(role==ROLE_STREAM&&c&&k&&v);return ESP_OK;}
static int esp_http_client_set_timeout_ms(void *c,int t) {assert(role==ROLE_STREAM&&c&&t>0);return ESP_OK;}
static int esp_http_client_open(esp_http_client_handle_t c,int n) {assert(role==ROLE_STREAM&&c&&!n);barrier_hit("open");c->closed=false;return connect_error?ESP_ERR_HTTP_CONNECT:ESP_OK;}
static int64_t esp_http_client_fetch_headers(void *c) {assert(role==ROLE_STREAM&&c);barrier_hit("headers");return 0;}
static int esp_http_client_get_status_code(void *c) {assert(c);return redirect_once?302:terminal_response?404:200;}
static int esp_http_client_set_redirection(void *c) {assert(role==ROLE_STREAM&&c);redirect_once=false;return ESP_OK;}
static int esp_http_client_get_response_header(void *c,const char *key,char **out) {assert(c&&key&&out);*out=NULL;return ESP_FAIL;}
static int esp_http_client_close(esp_http_client_handle_t c) {assert(role==ROLE_STREAM);if(!c->closed){barrier_hit("close");c->closed=true;++http_closes;}return ESP_OK;}
static int esp_http_client_cleanup(esp_http_client_handle_t c) {assert(role==ROLE_STREAM&&c&&http_clients);barrier_hit("cleanup");esp_http_client_close(c);--http_clients;free(c);return ESP_OK;}
static int esp_http_client_read(esp_http_client_handle_t c,char *p,int n) {assert(role==ROLE_STREAM&&c&&!c->closed);barrier_hit("read");vTaskDelay(1);if(strstr(c->url,"old.invalid")&&c->reads){atomic_store(&baseline_eof_seen,true);return 0;}if(strstr(c->url,"new.invalid"))return -ESP_ERR_HTTP_EAGAIN;if(tls_error)return ESP_FAIL;if(no_body)return -ESP_ERR_HTTP_EAGAIN;if(mp3_start){if(c->reads++){barrier_hit("staging");return -ESP_ERR_HTTP_EAGAIN;}assert(n>=100);memset(p,0,100);p[0]=(char)0xff;p[1]=(char)0xfb;p[2]=(char)0x90;return 100;}memset(p,0,(size_t)n);if(aac_start){int count=n/256;for(int i=0;i<count;++i)memcpy(p+i*256,"\xff\xf1\x50\x80\x20\x1f\xfc",7);return count*256;}if(mp3_full){int count=n/417;for(int i=0;i<count;++i)memcpy(p+i*417,"\xff\xfb\x90\x64",4);return count*417;}memcpy(p,"fLaC\0\0\0\42",8);++c->reads;return n;}
static int esp_http_client_get_and_clear_last_tls_error(void *c,int *code,void *flags) {(void)c;(void)flags;*code=0;return tls_error?ESP_ERR_MBEDTLS_SSL_READ_FAILED:ESP_OK;}
static bool esp_http_client_is_complete_data_received(void *c) {return strstr(((esp_http_client_handle_t)c)->url,"old.invalid")&&atomic_load(&baseline_eof_seen);}
#include "stream_http_reader.h"
#include "reader.inc"

// Track the actual module's malloc/realloc/free, especially its reusable PCM.
typedef struct {void *p;unsigned owner;} tracked_allocation_t;
static tracked_allocation_t allocations[64];
static atomic_bool fail_stream_buffer;
static pthread_mutex_t allocation_mutex=PTHREAD_MUTEX_INITIALIZER;
static void track_remove(void *p) {for(unsigned i=0;i<64;++i)if(allocations[i].p==p){allocations[i]=(tracked_allocation_t){0};return;}}
static void track_add(void *p) {if(!p)return;for(unsigned i=0;i<64;++i)if(!allocations[i].p){allocations[i]=(tracked_allocation_t){p,role};return;}assert(false);}
static void *owner_malloc(size_t n) {if(role==ROLE_STREAM&&n==2048&&fail_stream_buffer)return NULL;void *p=malloc(n);pthread_mutex_lock(&allocation_mutex);track_add(p);pthread_mutex_unlock(&allocation_mutex);return p;}
static void *owner_realloc(void *old,size_t n) {assert(n);pthread_mutex_lock(&allocation_mutex);track_remove(old);void *p=realloc(old,n);track_add(p?p:old);pthread_mutex_unlock(&allocation_mutex);return p;}
static void owner_free(void *p) {pthread_mutex_lock(&allocation_mutex);track_remove(p);pthread_mutex_unlock(&allocation_mutex);free(p);}
static unsigned owner_allocations(unsigned owner) {unsigned count=0;pthread_mutex_lock(&allocation_mutex);for(unsigned i=0;i<64;++i)count+=allocations[i].p&&allocations[i].owner==owner;pthread_mutex_unlock(&allocation_mutex);return count;}
#define malloc owner_malloc
#define realloc owner_realloc
#define free owner_free
#include "decoder_pcm.h"
#include "decoder_resources.h"
