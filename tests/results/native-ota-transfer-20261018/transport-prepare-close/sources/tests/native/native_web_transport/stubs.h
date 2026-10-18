#pragma once
#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdatomic.h>
#include <sys/select.h>
#include <sys/socket.h>
#include <sys/types.h>
typedef int esp_err_t;
typedef void *httpd_handle_t;
typedef int nvs_handle_t;
#define ESP_OK 0
#define ESP_FAIL (-1)
#define ESP_ERR_NO_MEM 0x101
#define ESP_ERR_INVALID_ARG 0x102
#define ESP_ERR_INVALID_STATE 0x103
#define ESP_ERR_INVALID_SIZE 0x104
#define ESP_ERR_TIMEOUT 0x107
#define ESP_ERR_NVS_NOT_FOUND 0x1102
#define HTTPD_SOCK_ERR_FAIL (-1)
#define HTTPD_SOCK_ERR_TIMEOUT (-3)
#define NVS_READWRITE 1
#define NVS_READONLY 0
#define ESP_TLS_VER_TLS_1_2 1
#define ESP_TLS_DONE 4
#define ESP_TLS_ERR_SSL_WANT_READ (-0x6900)
#define ESP_TLS_ERR_SSL_WANT_WRITE (-0x6880)
#define PSA_SUCCESS 0
#define CONFIG_ESP_TLS_USING_MBEDTLS 1
#define CONFIG_MBEDTLS_TLS_SERVER 1
typedef struct { unsigned unused; } mbedtls_pk_context;
typedef struct { mbedtls_pk_context pk; } mbedtls_x509_crt;
typedef struct { unsigned unused; } mbedtls_ssl_context;
typedef struct { const unsigned char *servercert_buf,*serverkey_buf;
    unsigned servercert_bytes,serverkey_bytes;int tls_version; } esp_tls_cfg_server_t;
typedef struct { int socket;mbedtls_ssl_context ssl; } esp_tls_t;
typedef int (*httpd_send_func_t)(httpd_handle_t,int,const char *,size_t,int);
typedef int (*httpd_recv_func_t)(httpd_handle_t,int,char *,size_t,int);
typedef int (*httpd_pending_func_t)(httpd_handle_t,int);
typedef struct { unsigned stack_size,max_open_sockets,task_priority;int core_id;
    unsigned server_port;esp_err_t (*open_fn)(httpd_handle_t,int);
    void (*close_fn)(httpd_handle_t,int); } httpd_config_t;

void *tracked_malloc(size_t);
void *tracked_calloc(size_t,size_t);
void tracked_free(void *);
int mock_fcntl(int,int,...);
#define malloc tracked_malloc
#define calloc tracked_calloc
#define free tracked_free
#define fcntl mock_fcntl
int64_t esp_timer_get_time(void);
void vTaskDelay(unsigned);
ssize_t lwip_send(int,const void *,size_t,int);
ssize_t lwip_recv(int,void *,size_t,int);
int lwip_select(int,fd_set *,fd_set *,fd_set *,struct timeval *);
int lwip_close(int);
int shutdown(int,int);
void *httpd_sess_get_transport_ctx(httpd_handle_t,int);
void httpd_sess_set_transport_ctx(httpd_handle_t,int,void *,void (*)(void *));
esp_err_t httpd_sess_set_send_override(httpd_handle_t,int,httpd_send_func_t);
esp_err_t httpd_sess_set_recv_override(httpd_handle_t,int,httpd_recv_func_t);
esp_err_t httpd_sess_set_pending_override(httpd_handle_t,int,httpd_pending_func_t);
esp_err_t nvs_open(const char *,int,nvs_handle_t *);
void nvs_close(nvs_handle_t);
esp_err_t nvs_get_blob(nvs_handle_t,const char *,void *,size_t *);
esp_err_t nvs_set_blob(nvs_handle_t,const char *,const void *,size_t);
esp_err_t nvs_commit(nvs_handle_t);
int psa_crypto_init(void);
void mbedtls_x509_crt_init(mbedtls_x509_crt *);
int mbedtls_x509_crt_parse(mbedtls_x509_crt *,const unsigned char *,size_t);
void mbedtls_x509_crt_free(mbedtls_x509_crt *);
void mbedtls_pk_init(mbedtls_pk_context *);
int mbedtls_pk_parse_key(mbedtls_pk_context *,const unsigned char *,size_t,const unsigned char *,size_t);
int mbedtls_pk_check_pair(const mbedtls_pk_context *,const mbedtls_pk_context *);
void mbedtls_pk_free(mbedtls_pk_context *);
int mbedtls_ssl_close_notify(mbedtls_ssl_context *);
esp_tls_t *esp_tls_init(void);
esp_err_t esp_tls_server_session_init(esp_tls_cfg_server_t *,int,esp_tls_t *);
int esp_tls_server_session_continue_async(esp_tls_t *);
esp_err_t esp_tls_set_conn_state(esp_tls_t *,int);
void esp_tls_server_session_delete(esp_tls_t *);
ssize_t esp_tls_conn_write(esp_tls_t *,const void *,size_t);
ssize_t esp_tls_conn_read(esp_tls_t *,void *,size_t);
ssize_t esp_tls_get_bytes_avail(esp_tls_t *);
void *esp_tls_get_ssl_context(esp_tls_t *);
