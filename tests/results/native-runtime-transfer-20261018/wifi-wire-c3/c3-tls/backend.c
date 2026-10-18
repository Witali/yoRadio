#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif
#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <netinet/in.h>
#include <signal.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/select.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>
#define MBEDTLS_DECLARE_PRIVATE_IDENTIFIERS
#include "mbedtls/net_sockets.h"
#include "mbedtls/pk.h"
#include "mbedtls/private/pk_private.h"
#include "mbedtls/ssl.h"
#include "mbedtls/x509_crt.h"
#include "mbedtls/version.h"
#include "psa/crypto.h"
#include "psa/crypto_extra.h"
#include "esp_err.h"
#define CONFIG_ESP_TLS_USING_MBEDTLS 1
#define CONFIG_MBEDTLS_TLS_SERVER 1
#include "sdk-tls-errors.h"
#ifdef HOST_ESP_TLS_UNIFIED_KEYS
#include "sdk-key-config.h"
#endif

// Host ABI field views replace SDK headers only. Their layout is deliberately
// not evidence for the ESP target ABI. Crypto and server configuration below
// are the pinned implementations, not acceptance or handshake substitutes.
typedef enum {ESP_TLS_INIT,ESP_TLS_CONNECTING,ESP_TLS_HANDSHAKE,ESP_TLS_FAIL,ESP_TLS_DONE} esp_tls_conn_state_t;
typedef enum {ESP_TLS_CLIENT,ESP_TLS_SERVER} esp_tls_role_t;
typedef enum {ESP_TLS_VER_ANY,ESP_TLS_VER_TLS_1_2,ESP_TLS_VER_TLS_1_3} esp_tls_proto_ver_t;
typedef struct {esp_tls_proto_ver_t tls_version;} esp_tls_cfg_t;
typedef struct {
    const unsigned char *servercert_buf,*serverkey_buf,*cacert_buf,*serverkey_password;
    unsigned servercert_bytes,serverkey_bytes,cacert_bytes,serverkey_password_len;
    bool use_secure_element,use_ecdsa_peripheral;
    void *userdata;
    const int *ciphersuites_list;
    esp_tls_proto_ver_t tls_version;
#ifdef HOST_ESP_TLS_UNIFIED_KEYS
    const esp_key_config_t *server_key;
#endif
} esp_tls_cfg_server_t;
typedef struct esp_tls esp_tls_t;
struct esp_tls {
    mbedtls_ssl_context ssl;mbedtls_ssl_config conf;mbedtls_net_context server_fd;
    mbedtls_x509_crt cacert,*cacert_ptr;
    union {mbedtls_x509_crt clientcert,servercert;};
    union {mbedtls_pk_context clientkey,serverkey;};
    int sockfd;
    ssize_t (*read)(esp_tls_t *,char *,size_t);
    ssize_t (*write)(esp_tls_t *,const char *,size_t);
    esp_tls_conn_state_t conn_state;esp_tls_role_t role;bool is_tls;
    bool opaque_key_is_external;
    esp_tls_error_handle_t error_handle;
};
typedef struct {
    mbedtls_x509_crt *public_cert;mbedtls_pk_context *pk_key;
    const unsigned char *publiccert_pem_buf,*privkey_pem_buf,*privkey_password;
    size_t publiccert_pem_bytes,privkey_pem_bytes,privkey_password_len;
} esp_tls_pki_t;
typedef struct {esp_err_t (*set_server_cfg)(esp_tls_cfg_server_t *,esp_tls_t *);} esp_tls_server_params_t;
typedef void *httpd_handle_t;
typedef int nvs_handle_t;
typedef int (*httpd_send_func_t)(httpd_handle_t,int,const char *,size_t,int);
typedef int (*httpd_recv_func_t)(httpd_handle_t,int,char *,size_t,int);
typedef int (*httpd_pending_func_t)(httpd_handle_t,int);
typedef struct {
    unsigned stack_size,max_open_sockets,task_priority;int core_id;unsigned server_port;
    esp_err_t (*open_fn)(httpd_handle_t,int);void (*close_fn)(httpd_handle_t,int);
} httpd_config_t;
#define HTTPD_SOCK_ERR_FAIL (-1)
#define HTTPD_SOCK_ERR_TIMEOUT (-3)
#define ESP_ERR_NVS_NOT_FOUND 0x1102
#define NVS_READWRITE 1
#define NVS_READONLY 0
#define NEWLIB_NANO_SSIZE_T_COMPAT_FORMAT "zX"
#define NEWLIB_NANO_SIZE_T_COMPAT_FORMAT "zu"
#define NEWLIB_NANO_SIZE_T_COMPAT_CAST(value) (value)
#define ESP_LOGE(...) ((void)0)
#define ESP_LOGW(...) ((void)0)
#define ESP_LOGI(...) ((void)0)
#define ESP_LOGD(...) ((void)0)
static void capture_error(esp_tls_error_handle_t handle,unsigned type,int code){if(!handle)return;if(type==ESP_TLS_ERR_TYPE_ESP)handle->last_error=code;else if(type==ESP_TLS_ERR_TYPE_MBEDTLS)handle->esp_tls_error_code=code;}
#define ESP_INT_EVENT_TRACKER_CAPTURE(handle,type,code) capture_error(handle,type,code)
static mbedtls_x509_crt *global_cacert;
static void mbedtls_print_error_msg(int error){(void)error;}
static esp_tls_error_handle_t esp_tls_internal_event_tracker_create(void){return calloc(1,sizeof(esp_tls_last_error_t));}
static void esp_tls_internal_event_tracker_destroy(esp_tls_error_handle_t handle){free(handle);}
static esp_err_t set_client_config(const char *hostname,size_t length,esp_tls_cfg_t *cfg,esp_tls_t *tls){(void)hostname;(void)length;(void)cfg;(void)tls;assert(!"Client configuration branch is outside this server test");return ESP_FAIL;}
static esp_err_t set_server_config(esp_tls_cfg_server_t *,esp_tls_t *);
void esp_mbedtls_cleanup(esp_tls_t *);
ssize_t esp_mbedtls_read(esp_tls_t *,char *,size_t);
ssize_t esp_mbedtls_write(esp_tls_t *,const char *,size_t);
#define _esp_tls_net_init esp_mbedtls_net_init
#define _esp_tls_server_session_init esp_mbedtls_server_session_init
#define _esp_tls_server_session_continue_async esp_mbedtls_server_session_continue_async
#define _esp_tls_server_session_delete esp_mbedtls_server_session_delete
#define _esp_tls_get_bytes_avail esp_mbedtls_get_bytes_avail
#define _esp_tls_get_ssl_context esp_mbedtls_get_ssl_context
// Keep the pinned SDK ternary in esp_mbedtls_write verbatim. Its signed/unsigned
// warning remains visible; the host tests verify the resulting WANT values.
#pragma GCC diagnostic push
#pragma GCC diagnostic warning "-Wsign-compare"
#include "sdk-functions.inc"
#pragma GCC diagnostic pop

static int64_t esp_timer_get_time(void){struct timespec now;assert(!clock_gettime(CLOCK_MONOTONIC,&now));return (int64_t)now.tv_sec*1000000+now.tv_nsec/1000;}
static void vTaskDelay(unsigned ticks){assert(ticks==1);struct timespec delay={.tv_nsec=1000000};nanosleep(&delay,NULL);}
static ssize_t lwip_send(int fd,const void *data,size_t size,int flags){return send(fd,data,size,flags);}
static ssize_t lwip_recv(int fd,void *data,size_t size,int flags){return recv(fd,data,size,flags);}
static unsigned read_waits,write_waits,raw_closes;
static int lwip_select(int count,fd_set *reads,fd_set *writes,fd_set *errors,struct timeval *timeout){if(reads)++read_waits;if(writes)++write_waits;return select(count,reads,writes,errors,timeout);}
static int lwip_close(int fd){++raw_closes;return close(fd);}
void *httpd_sess_get_transport_ctx(httpd_handle_t,int);
void httpd_sess_set_transport_ctx(httpd_handle_t,int,void *,void (*)(void *));
esp_err_t httpd_sess_set_send_override(httpd_handle_t,int,httpd_send_func_t);
esp_err_t httpd_sess_set_recv_override(httpd_handle_t,int,httpd_recv_func_t);
esp_err_t httpd_sess_set_pending_override(httpd_handle_t,int,httpd_pending_func_t);
static uint8_t *nvs_blob;
static size_t nvs_size;
static unsigned nvs_commits;
static esp_err_t nvs_open(const char *name,int mode,nvs_handle_t *handle){assert(!strcmp(name,"web_tls"));if(mode==NVS_READONLY&&!nvs_blob)return ESP_ERR_NVS_NOT_FOUND;*handle=1;return ESP_OK;}
static void nvs_close(nvs_handle_t handle){assert(handle==1);}
static esp_err_t nvs_get_blob(nvs_handle_t handle,const char *name,void *data,size_t *size){assert(handle==1&&!strcmp(name,"bundle"));if(!nvs_blob)return ESP_ERR_NVS_NOT_FOUND;if(!data){*size=nvs_size;return ESP_OK;}assert(*size>=nvs_size);memcpy(data,nvs_blob,nvs_size);*size=nvs_size;return ESP_OK;}
static esp_err_t nvs_set_blob(nvs_handle_t handle,const char *name,const void *data,size_t size){assert(handle==1&&!strcmp(name,"bundle"));uint8_t *copy=malloc(size);assert(copy);memcpy(copy,data,size);if(nvs_blob){memset(nvs_blob,0,nvs_size);free(nvs_blob);}nvs_blob=copy;nvs_size=size;return ESP_OK;}
static esp_err_t nvs_commit(nvs_handle_t handle){assert(handle==1);++nvs_commits;return ESP_OK;}
#include "transport-production.inc"


/* Appended to the frozen ESP-TLS host fixture's platform prefix. SDK crypto,
 * ESP-TLS and native transport above are the actual tested implementations.
 * No HTTPD type crosses this module boundary: public session APIs are supplied
 * by the SDK lifecycle translation unit, and config stays private here. */
static httpd_config_t integration_tls_config;
void integration_tls_prepare(const char *path) {
    FILE *file=fopen(path,"rb");assert(file&&!fseek(file,0,SEEK_END));
    long count=ftell(file);assert(count>0&&count<32768&&!fseek(file,0,SEEK_SET));
    uint8_t *bytes=malloc((size_t)count);assert(bytes&&fread(bytes,1,(size_t)count,file)==(size_t)count&&!fclose(file));
    assert(native_web_transport_provision(bytes,(size_t)count)==ESP_OK);
    wipe(bytes,(size_t)count);free(bytes);
    integration_tls_config=(httpd_config_t){.stack_size=10240};
    assert(native_web_transport_prepare(&integration_tls_config)==ESP_OK&&native_web_transport_secure());
    assert(integration_tls_config.open_fn&&integration_tls_config.close_fn);
}
int integration_tls_open(void *server,int fd) {return integration_tls_config.open_fn(server,fd);}
void integration_tls_close(void *server,int fd) {integration_tls_config.close_fn(server,fd);}
void integration_tls_release(void) {
    assert(native_web_transport_release()==ESP_OK);
    wipe(nvs_blob,nvs_size);free(nvs_blob);nvs_blob=NULL;nvs_size=0;mbedtls_psa_crypto_free();
}
