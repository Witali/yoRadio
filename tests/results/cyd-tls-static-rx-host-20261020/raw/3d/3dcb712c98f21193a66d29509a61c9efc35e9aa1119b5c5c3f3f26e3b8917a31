/* Typed callback + public lifetime API HOST seam, replacing only the existing
 * maintenance harness HTTP seam. Production audio_service is whole/unmodified
 * apart from its two reviewed include/callback integration changes. */
#include "tls_bridge.h"
#include "native_tls_rx_reserve.h"
enum {HTTP_EVENT_ON_HEADER=1};
typedef struct {int event_id;void *user_data;const char *header_key,*header_value;} esp_http_client_event_t;
typedef struct {const char *url,*user_agent;int timeout_ms,buffer_size,buffer_size_tx,max_redirection_count;int (*crt_bundle_attach)(void *);bool disable_auto_redirect,keep_alive_enable;int (*event_handler)(esp_http_client_event_t *);void *user_data;} esp_http_client_config_t;
typedef struct {bool closed,tls_initialized;unsigned reads;char url[512];esp_http_client_config_t config;mbedtls_ssl_config tls_config;mbedtls_ssl_context tls;} *esp_http_client_handle_t;
static atomic_uint http_clients,http_inits,http_closes;
static atomic_bool no_body,mp3_start,tls_error,redirect_once;
static atomic_bool fail_init,fail_open_before,fail_open_after,fail_headers,fail_redirect,occupy_userdata;
static atomic_bool fail_tls_setup,numeric_userdata;
static const char *redirect_destination;
static int occupied_cookie;
static pthread_mutex_t url_mutex=PTHREAD_MUTEX_INITIALIZER;
static char observed_url[512];
static esp_http_client_handle_t esp_http_client_init(const esp_http_client_config_t *cfg) {
    assert(role==ROLE_STREAM);
    tls_check(cfg->crt_bundle_attach==native_tls_rx_reserve_crt_bundle_attach,"actual_radio_callback_selection");
    tls_check(cfg->buffer_size==2048&&cfg->buffer_size_tx==4096,"http_buffer_profile_preserved");
    tls_check(cfg->disable_auto_redirect&&cfg->keep_alive_enable,"http_redirect_auth_profile_preserved");
    if(atomic_load(&fail_init)){++http_inits;return NULL;}
    esp_http_client_handle_t c=calloc(1,sizeof(*c));assert(c);c->config=*cfg;
    strlcpy(c->url,cfg->url,sizeof(c->url));
    pthread_mutex_lock(&url_mutex);strlcpy(observed_url,cfg->url,sizeof(observed_url));pthread_mutex_unlock(&url_mutex);
    ++http_inits;++http_clients;return c;
}
static int esp_http_client_set_header(void *c,const char *k,const char *v) {assert(role==ROLE_STREAM&&c&&k&&v);return ESP_OK;}
static int esp_http_client_set_timeout_ms(void *c,int t) {assert(role==ROLE_STREAM&&c&&t>0);return ESP_OK;}
static int esp_http_client_open(esp_http_client_handle_t c,int n) {
    assert(role==ROLE_STREAM&&c&&!n);barrier_hit("open");c->closed=false;
    if(fail_open_before)return ESP_FAIL;
    if(!strncmp(c->url,"https://",8)) {
        tls_check(!c->tls_initialized,"close_before_tls_reopen");
        mbedtls_ssl_config_init(&c->tls_config);c->tls_config.max_tls_version=0x303;
        if(occupy_userdata)mbedtls_ssl_conf_set_user_data_p(&c->tls_config,&occupied_cookie);
        if(numeric_userdata)mbedtls_ssl_conf_set_user_data_n(&c->tls_config,UINTPTR_MAX);
        /* Actual pinned esp_tls_mbedtls.c invokes this callback and ignores its
         * return. This seam deliberately preserves that observed behavior. */
        (void)c->config.crt_bundle_attach(&c->tls_config);
        if(occupy_userdata)tls_check(mbedtls_ssl_conf_get_user_data_p(&c->tls_config)==&occupied_cookie,"occupied_public_userdata_preserved");
        if(numeric_userdata)tls_check(mbedtls_ssl_conf_get_user_data_n(&c->tls_config)==UINTPTR_MAX,"numeric_radio_data_preserved");
        c->tls_initialized=true;
        if(fail_tls_setup)c->tls_config.reject=true;
        int result=tls_open(&c->tls,&c->tls_config);
        if(result)return ESP_FAIL;
    }
    barrier_hit("tls_open");
    return fail_open_after?ESP_FAIL:ESP_OK;
}
static int64_t esp_http_client_fetch_headers(void *c) {assert(role==ROLE_STREAM&&c);barrier_hit("headers");return fail_headers?-1:0;}
static int esp_http_client_get_status_code(void *c) {assert(c);return atomic_load(&redirect_once)?302:200;}
static int esp_http_client_set_redirection(esp_http_client_handle_t c) {
    assert(role==ROLE_STREAM&&c);redirect_once=false;
    if(redirect_destination)strlcpy(c->url,redirect_destination,sizeof(c->url));
    return fail_redirect?ESP_FAIL:ESP_OK;
}
static int esp_http_client_close(esp_http_client_handle_t c) {
    assert(role==ROLE_STREAM);
    if(!c->closed){barrier_hit("close");if(c->tls_initialized){mbedtls_ssl_config_free(&c->tls_config);tls_close(&c->tls);c->tls_initialized=false;}c->closed=true;++http_closes;}
    return ESP_OK;
}
static int esp_http_client_cleanup(esp_http_client_handle_t c) {
    assert(role==ROLE_STREAM&&c&&http_clients);barrier_hit("cleanup");esp_http_client_close(c);--http_clients;free(c);return ESP_OK;
}
static int esp_http_client_read(esp_http_client_handle_t c,char *p,int n) {assert(role==ROLE_STREAM&&c&&!c->closed);barrier_hit("read");vTaskDelay(1);if(atomic_load(&tls_error))return ESP_FAIL;if(atomic_load(&no_body))return -ESP_ERR_HTTP_EAGAIN;if(atomic_load(&mp3_start)){if(c->reads++){barrier_hit("staging");return -ESP_ERR_HTTP_EAGAIN;}assert(n>=100);memset(p,0,100);p[0]=(char)0xff;p[1]=(char)0xfb;p[2]=(char)0x90;return 100;}memset(p,0,(size_t)n);memcpy(p,"fLaC\0\0\0\42",8);++c->reads;return n;}
static int esp_http_client_get_and_clear_last_tls_error(void *c,int *code,void *flags) {(void)c;(void)flags;*code=0;return atomic_load(&tls_error)?ESP_ERR_MBEDTLS_SSL_READ_FAILED:ESP_OK;}
static bool esp_http_client_is_complete_data_received(void *c) {(void)c;return false;}
