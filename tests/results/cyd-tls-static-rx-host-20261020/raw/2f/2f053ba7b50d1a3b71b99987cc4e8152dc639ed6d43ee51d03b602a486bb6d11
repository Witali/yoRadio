/* Host allocator/crypto API seam; exact SDK lifetime bodies live separately.
 * No transport, handshake, hardware, target ABI or real OOM claim. */
#include "platform.h"
#include "tls_bridge.h"
#include "native_tls_rx_reserve.h"
#if CONFIG_YORADIO_TLS_INPUT_RECLAIM
#include "native_input_reclaim.h"
#endif
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>

void tls_check(bool condition, const char *name) {
    if (condition) return;
    fprintf(stderr, "TLS_SERVICE_FAILURE %s\n", name);
    fflush(stderr);
    _Exit(2);
}
static pthread_mutex_t ledger_lock = PTHREAD_MUTEX_INITIALIZER;
static void *ledger[1024];
static unsigned outstanding;
static _Thread_local unsigned critical_depth, fail_next;
static atomic_uint attach_calls, setup_calls, closed_calls, loans, loan_count;
static atomic_uint zeroizes, ordinary_setups, allocator_calls;
static atomic_int attach_result;
static atomic_bool nested_attach;
static void *reserved;

void host_enter(portMUX_TYPE *lock) {tls_check(!pthread_mutex_lock(lock), "critical_enter");++critical_depth;}
void host_exit(portMUX_TYPE *lock) {tls_check(critical_depth!=0,"critical_balanced");--critical_depth;tls_check(!pthread_mutex_unlock(lock),"critical_exit");}
bool xPortInIsrContext(void) {return false;}
void tls_fail_next_allocation(void) {fail_next=1;}
void *__real_esp_mbedtls_mem_calloc(size_t count,size_t bytes) {
    tls_check(!critical_depth,"allocator_outside_critical");
    ++allocator_calls;
    if(fail_next){--fail_next;return NULL;}
    if(!count||!bytes||bytes>SIZE_MAX/count)return NULL;
    void *p=calloc(count,bytes);tls_check(p!=NULL,"host_heap_available");
    pthread_mutex_lock(&ledger_lock);
    unsigned i=0;while(i<1024&&ledger[i])++i;
    tls_check(i<1024,"ledger_capacity");ledger[i]=p;++outstanding;
    pthread_mutex_unlock(&ledger_lock);return p;
}
bool tls_is_ordinary(void *p) {
    bool found=false;pthread_mutex_lock(&ledger_lock);
    for(unsigned i=0;i<1024;++i)if(ledger[i]==p&&p){found=true;break;}
    pthread_mutex_unlock(&ledger_lock);return found;
}
void *mbedtls_calloc(size_t count,size_t bytes) {
#if CONFIG_YORADIO_TLS_INPUT_RECLAIM
    return __wrap_esp_mbedtls_mem_calloc(count,bytes);
#else
    return __real_esp_mbedtls_mem_calloc(count,bytes);
#endif
}
void mbedtls_free(void *p) {
    tls_check(!critical_depth,"free_outside_critical");if(!p)return;
    pthread_mutex_lock(&ledger_lock);unsigned i=0;while(i<1024&&ledger[i]!=p)++i;
    tls_check(i<1024,"ordinary_free_paired");ledger[i]=NULL;--outstanding;
    pthread_mutex_unlock(&ledger_lock);free(p);
}
void mbedtls_platform_zeroize(void *p,size_t n) {
    tls_check(!critical_depth,"zeroize_outside_critical");++zeroizes;
    volatile unsigned char *d=p;while(n--)*d++=0;
}
int ssl_conf_check(const mbedtls_ssl_context *ssl) {return ssl->conf->reject?-777:0;}
void mbedtls_ssl_transform_free(mbedtls_ssl_transform *v) {(void)v;}
void mbedtls_ssl_session_free(mbedtls_ssl_session *v) {(void)v;}
void mbedtls_ssl_handshake_free(mbedtls_ssl_context *s) {(void)s;}
void mbedtls_ssl_session_init(mbedtls_ssl_session *v) {memset(v,0,sizeof(*v));}
void ssl_handshake_params_init(mbedtls_ssl_handshake_params *v) {memset(v,0,sizeof(*v));}
void mbedtls_ssl_transform_init(mbedtls_ssl_transform *v) {memset(v,0,sizeof(*v));}
int mbedtls_ssl_reset_checksum(mbedtls_ssl_context *s) {(void)s;return 0;}
void mbedtls_ssl_reset_in_pointers(mbedtls_ssl_context *s) {s->in_hdr=s->in_ctr=s->in_len=s->in_iv=s->in_msg=s->in_buf;}
void mbedtls_ssl_reset_out_pointers(mbedtls_ssl_context *s) {s->out_hdr=s->out_ctr=s->out_len=s->out_iv=s->out_msg=s->out_buf;}
void mbedtls_ssl_set_timer(mbedtls_ssl_context *s,unsigned n) {(void)s;(void)n;}

void tls_set_attach_result(int result) {attach_result=result;}
void tls_set_nested_attach(bool enabled) {nested_attach=enabled;}
esp_err_t esp_crt_bundle_attach(void *value) {
    mbedtls_ssl_config *conf=value;++attach_calls;
    tls_check(conf!=NULL,"original_attach_configuration");++conf->attached;
    if(nested_attach) {
        mbedtls_ssl_config nested;mbedtls_ssl_config_init(&nested);nested.max_tls_version=0x303;mbedtls_ssl_context ssl;
        mbedtls_ssl_init(&ssl);
        tls_check(mbedtls_ssl_setup(&ssl,&nested)==0,"nested_setup_success");
        tls_check(tls_is_ordinary(ssl.in_buf),"nested_attach_ordinary_rx");
        mbedtls_ssl_config_free(&nested);mbedtls_ssl_free(&ssl);
    }
    return attach_result;
}
int tls_open(mbedtls_ssl_context *ssl,mbedtls_ssl_config *conf) {
    mbedtls_ssl_init(ssl);int result=mbedtls_ssl_setup(ssl,conf);++setup_calls;
    if(result)return result;
    if(tls_is_ordinary(ssl->in_buf))++ordinary_setups;
    else {
#if CONFIG_YORADIO_TLS_STATIC_RX_RESERVE
        tls_check(!reserved||reserved==ssl->in_buf,"same_reserved_address");reserved=ssl->in_buf;
        tls_check(atomic_fetch_add(&loans,1)==0,"single_live_radio_loan");++loan_count;
#else
        tls_check(false,"disabled_all_ordinary");
#endif
    }
    return 0;
}
void tls_close(mbedtls_ssl_context *ssl) {
    bool loan=ssl->in_buf&&ssl->in_buf==reserved;
    mbedtls_ssl_free(ssl);++closed_calls;
    if(loan) {
        tls_check(atomic_fetch_sub(&loans,1)==1,"loan_return_once");
        const unsigned char *bytes=reserved;
        for(size_t n=0;n<MBEDTLS_SSL_IN_BUFFER_LEN;++n)tls_check(!bytes[n],"returned_full_slot_erased");
    }
}
void tls_independent_client(void) {
    mbedtls_ssl_config conf;mbedtls_ssl_config_init(&conf);conf.max_tls_version=0x303;mbedtls_ssl_context ssl;
    tls_check(esp_crt_bundle_attach(&conf)==attach_result,"unrelated_original_attach");
    tls_check(mbedtls_ssl_conf_get_user_data_p(&conf)==NULL,"unrelated_config_unlabelled");
    tls_check(tls_open(&ssl,&conf)==0,"unrelated_setup_success");
    tls_check(tls_is_ordinary(ssl.in_buf),"unrelated_client_ordinary_rx");mbedtls_ssl_config_free(&conf);tls_close(&ssl);
}
unsigned tls_loans(void) {return loans;}
unsigned tls_loan_count(void) {return loan_count;}
unsigned tls_setups(void) {return setup_calls;}
unsigned tls_attaches(void) {return attach_calls;}
unsigned tls_ordinary_setups(void) {return ordinary_setups;}
unsigned tls_allocator_calls(void) {return allocator_calls;}
void tls_assert_drained(void) {
    tls_check(!loans,"no_radio_loan_after_shutdown");
    pthread_mutex_lock(&ledger_lock);tls_check(!outstanding,"no_tls_heap_leaks");pthread_mutex_unlock(&ledger_lock);
}
