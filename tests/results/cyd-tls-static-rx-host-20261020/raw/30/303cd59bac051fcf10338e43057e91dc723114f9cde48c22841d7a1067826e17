#pragma once
#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include <pthread.h>

/* Explicit HOST types/RTOS/crypto seam, not an ESP32 layout declaration. Exact
 * public inline getter/setter and SDK lifetime bodies are separately extracted. */
#define MBEDTLS_PRIVATE(value) value
#define MBEDTLS_SSL_PROTO_TLS1_2
#define MBEDTLS_SSL_DEBUG_MSG(level, args) ((void)0)
#define MBEDTLS_SSL_DEBUG_RET(level, label, result) ((void)0)
#define MBEDTLS_CHECK_RETURN_CRITICAL
#define MBEDTLS_ERR_ERROR_CORRUPTION_DETECTED (-1000)
#define MBEDTLS_ERR_SSL_ALLOC_FAILED (-1001)
typedef int esp_err_t;
enum { ESP_OK = 0 };
typedef pthread_mutex_t portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED PTHREAD_MUTEX_INITIALIZER
void host_enter(portMUX_TYPE *lock);
void host_exit(portMUX_TYPE *lock);
void host_safe_enter(portMUX_TYPE *lock);
void host_safe_exit(portMUX_TYPE *lock);
#define portENTER_CRITICAL_SAFE(lock) host_safe_enter(lock)
#define portEXIT_CRITICAL_SAFE(lock) host_safe_exit(lock)
#define portENTER_CRITICAL(lock) host_enter(lock)
#define portEXIT_CRITICAL(lock) host_exit(lock)
bool xPortInIsrContext(void);
bool host_erase_control_active(void); /* Semantic-control copy only. */
typedef struct { unsigned char contents[32]; } mbedtls_ssl_transform;
typedef struct { unsigned char contents[24]; } mbedtls_ssl_session;
typedef struct { unsigned char contents[64]; } mbedtls_ssl_handshake_params;
typedef struct {
    union { void *p; uintptr_t n; } user_data;
    int max_tls_version;
    bool reject;
    int attached;
} mbedtls_ssl_config;
typedef struct {
    const mbedtls_ssl_config *conf;
    int tls_version;
    unsigned char *in_buf, *out_buf;
    unsigned char *in_hdr, *in_ctr, *in_len, *in_iv, *in_msg;
    unsigned char *out_hdr, *out_ctr, *out_len, *out_iv, *out_msg;
    unsigned char *in_offt;
    unsigned nb_zero, in_msgtype, in_msglen, in_hslen, in_hsfraglen;
    unsigned keep_current_message, in_left;
    unsigned in_fatal_alert_recv, in_fatal_alert_type, send_alert;
    unsigned out_msgtype, out_msglen, out_left;
    unsigned char cur_out_ctr[8];
    mbedtls_ssl_transform *transform, *transform_in, *transform_out, *transform_negotiate;
    mbedtls_ssl_session *session, *session_negotiate;
    mbedtls_ssl_handshake_params *handshake;
} mbedtls_ssl_context;

/* The arithmetic is an explicitly labelled HOST seam. The actual full buffer
 * macro definitions are extracted verbatim from ssl_misc.h into capacity.h.
 * Maximum IV/MAC/padding values here exercise overhead; target values pending. */
#define MBEDTLS_SSL_IN_CONTENT_LEN 16384
#define MBEDTLS_SSL_OUT_CONTENT_LEN 4096
#define MBEDTLS_MAX_IV_LENGTH 16
#define MBEDTLS_SSL_MAC_ADD 32
#define MBEDTLS_SSL_PADDING_ADD 256
#define MBEDTLS_SSL_MAX_CID_EXPANSION 0
#include "capacity.h"
#include "public_user_data.h"

void *mbedtls_calloc(size_t count, size_t bytes);
void *__real_esp_mbedtls_mem_calloc(size_t count, size_t bytes);
void mbedtls_free(void *pointer);
void mbedtls_platform_zeroize(void *pointer, size_t bytes);
void mbedtls_zeroize_and_free(void *pointer, size_t bytes);
esp_err_t esp_crt_bundle_attach(void *conf);
void mbedtls_ssl_init(mbedtls_ssl_context *ssl);
int mbedtls_ssl_setup(mbedtls_ssl_context *ssl, const mbedtls_ssl_config *conf);
void mbedtls_ssl_free(mbedtls_ssl_context *ssl);
void mbedtls_ssl_session_reset_msg_layer(mbedtls_ssl_context *ssl, int partial);
int ssl_conf_check(const mbedtls_ssl_context *ssl);
void mbedtls_ssl_transform_free(mbedtls_ssl_transform *value);
void mbedtls_ssl_session_free(mbedtls_ssl_session *value);
void mbedtls_ssl_handshake_free(mbedtls_ssl_context *ssl);
void mbedtls_ssl_session_init(mbedtls_ssl_session *value);
void ssl_handshake_params_init(mbedtls_ssl_handshake_params *value);
void mbedtls_ssl_transform_init(mbedtls_ssl_transform *value);
int mbedtls_ssl_reset_checksum(mbedtls_ssl_context *ssl);
void mbedtls_ssl_reset_in_pointers(mbedtls_ssl_context *ssl);
void mbedtls_ssl_reset_out_pointers(mbedtls_ssl_context *ssl);
void mbedtls_ssl_set_timer(mbedtls_ssl_context *ssl, unsigned milliseconds);

typedef struct { unsigned target, minimum; } adaptive_input_stats_t;
typedef struct { unsigned idle, released; } adaptive_input_t;
adaptive_input_stats_t adaptive_input_stats(adaptive_input_t *input);
bool adaptive_input_release_one(adaptive_input_t *input);

void mbedtls_ssl_config_init(mbedtls_ssl_config *conf);
void mbedtls_ssl_config_free(mbedtls_ssl_config *conf);
