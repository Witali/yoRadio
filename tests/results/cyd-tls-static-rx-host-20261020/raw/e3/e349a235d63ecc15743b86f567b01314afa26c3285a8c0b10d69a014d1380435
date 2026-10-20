#include "platform.h"
#include "native_tls_rx_reserve.h"
#include "native_input_reclaim.h"
#include <stdio.h>
#include <stdatomic.h>
#include <stdlib.h>
#include <string.h>

static void check(bool condition, const char *name) {
    if (condition) return;
    fprintf(stderr, "TLS_RX_HOST_FAILURE %s\n", name);
    fflush(stderr);
    _Exit(2); /* Exact semantic controls stop before further invalid ownership. */
}
#define CHECK(condition, name) check((condition), (name))
static _Thread_local unsigned critical_depth, allocation_attempt, fail_at;
static _Thread_local bool isr;
static pthread_mutex_t ledger_lock = PTHREAD_MUTEX_INITIALIZER;
typedef struct { void *pointer; size_t bytes; } entry_t;
static entry_t ledger[1024];
static unsigned outstanding, allocations, releases, zeroize_calls;
static unsigned backend_calls, dispatch_calls;
static void *known_reserve;
static bool reclaim_enabled, fail_until_released;
static adaptive_input_t pool;
static int checksum_failure, attach_result;
static unsigned attach_calls;
static atomic_uint safe_isr_calls;
static bool attach_nested;
static pthread_mutex_t erase_lock = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t erase_cond = PTHREAD_COND_INITIALIZER;
static bool erase_gate, erase_entered, erase_continue;

void host_enter(portMUX_TYPE *lock) {
    CHECK(!isr,"task_critical_not_isr");
    CHECK(pthread_mutex_lock(lock) == 0, "critical_enter");
    ++critical_depth;
}
void host_exit(portMUX_TYPE *lock) {
    CHECK(critical_depth != 0, "critical_balanced");
    --critical_depth;
    CHECK(pthread_mutex_unlock(lock) == 0, "critical_exit");
}
void host_safe_enter(portMUX_TYPE *lock) {
    CHECK(!pthread_mutex_lock(lock),"safe_critical_enter");++critical_depth;if(isr)++safe_isr_calls;
}
void host_safe_exit(portMUX_TYPE *lock) {
    CHECK(critical_depth!=0,"safe_critical_balance");--critical_depth;CHECK(!pthread_mutex_unlock(lock),"safe_critical_exit");
}
bool xPortInIsrContext(void) { return isr; }
bool host_erase_control_active(void) { return erase_gate; }

void *__real_esp_mbedtls_mem_calloc(size_t count, size_t bytes) {
    CHECK(critical_depth == 0, "allocator_outside_critical");
    ++allocation_attempt;
    CHECK(pthread_mutex_lock(&ledger_lock) == 0, "ledger_lock");
    ++backend_calls;
    bool fail = fail_at == allocation_attempt ||
        (fail_until_released && pool.released == 0);
    CHECK(pthread_mutex_unlock(&ledger_lock) == 0, "ledger_unlock");
    if (fail || !count || !bytes || bytes > SIZE_MAX / count) return NULL;
    void *result = calloc(count, bytes);
    CHECK(result != NULL, "host_heap_available");
    CHECK(pthread_mutex_lock(&ledger_lock) == 0, "ledger_lock");
    unsigned slot;
    for (slot = 0; slot < 1024 && ledger[slot].pointer; ++slot) {}
    CHECK(slot < 1024, "ledger_capacity");
    ledger[slot] = (entry_t){result, count * bytes};
    ++outstanding; ++allocations;
    CHECK(pthread_mutex_unlock(&ledger_lock) == 0, "ledger_unlock");
    return result;
}
void *mbedtls_calloc(size_t count, size_t bytes) {
    CHECK(pthread_mutex_lock(&ledger_lock) == 0, "ledger_lock");
    ++dispatch_calls;
    CHECK(pthread_mutex_unlock(&ledger_lock) == 0, "ledger_unlock");
    return reclaim_enabled ? __wrap_esp_mbedtls_mem_calloc(count, bytes) :
        __real_esp_mbedtls_mem_calloc(count, bytes);
}
void mbedtls_free(void *pointer) {
    CHECK(critical_depth == 0, "free_outside_critical");
    if (!pointer) return;
    CHECK(pointer != known_reserve, "reserved_pointer_never_sdk_heap_free");
    CHECK(pthread_mutex_lock(&ledger_lock) == 0, "ledger_lock");
    unsigned slot;
    for (slot = 0; slot < 1024 && ledger[slot].pointer != pointer; ++slot) {}
    CHECK(slot < 1024, "ordinary_free_paired");
    ledger[slot] = (entry_t){0}; --outstanding; ++releases;
    CHECK(pthread_mutex_unlock(&ledger_lock) == 0, "ledger_unlock");
    free(pointer);
}
void mbedtls_platform_zeroize(void *pointer, size_t bytes) {
    CHECK(critical_depth == 0, "zeroize_outside_critical");
    CHECK(pthread_mutex_lock(&erase_lock) == 0, "erase_lock");
    ++zeroize_calls;
    if (erase_gate && pointer == known_reserve) {
        erase_entered = true;
        CHECK(pthread_cond_broadcast(&erase_cond) == 0, "erase_enter_signal");
        while (!erase_continue)
            CHECK(pthread_cond_wait(&erase_cond, &erase_lock) == 0, "erase_wait");
    }
    CHECK(pthread_mutex_unlock(&erase_lock) == 0, "erase_unlock");
    volatile unsigned char *destination = pointer;
    for (size_t index = 0; index < bytes; ++index) destination[index] = 0;
}
adaptive_input_stats_t adaptive_input_stats(adaptive_input_t *input) {
    CHECK(input == &pool, "canonical_reclaim_bound_owner");
    return (adaptive_input_stats_t){.target = 8, .minimum = 4};
}
bool adaptive_input_release_one(adaptive_input_t *input) {
    CHECK(input == &pool && critical_depth == 0, "reclaim_outside_critical");
    if (!input->idle) return false;
    --input->idle; ++input->released;
    return true;
}

int ssl_conf_check(const mbedtls_ssl_context *ssl) {
    return ssl->conf->reject ? -777 : 0;
}
void mbedtls_ssl_transform_free(mbedtls_ssl_transform *value) { (void)value; }
void mbedtls_ssl_session_free(mbedtls_ssl_session *value) { (void)value; }
void mbedtls_ssl_handshake_free(mbedtls_ssl_context *ssl) { (void)ssl; }
void mbedtls_ssl_session_init(mbedtls_ssl_session *value) { memset(value, 0, sizeof(*value)); }
void ssl_handshake_params_init(mbedtls_ssl_handshake_params *value) { memset(value, 0, sizeof(*value)); }
void mbedtls_ssl_transform_init(mbedtls_ssl_transform *value) { memset(value, 0, sizeof(*value)); }
int mbedtls_ssl_reset_checksum(mbedtls_ssl_context *ssl) { (void)ssl; return checksum_failure; }
void mbedtls_ssl_reset_in_pointers(mbedtls_ssl_context *ssl) {
    ssl->in_hdr = ssl->in_ctr = ssl->in_len = ssl->in_iv = ssl->in_msg = ssl->in_buf;
}
void mbedtls_ssl_reset_out_pointers(mbedtls_ssl_context *ssl) {
    ssl->out_hdr = ssl->out_ctr = ssl->out_len = ssl->out_iv = ssl->out_msg = ssl->out_buf;
}
void mbedtls_ssl_set_timer(mbedtls_ssl_context *ssl, unsigned milliseconds) {
    (void)ssl; (void)milliseconds;
}

/* New identity registry API regressions. Config objects are initialized and
 * attached IN PLACE: a registry identity must never be returned by value. */
static void configuration(mbedtls_ssl_config *conf, bool radio) {
    mbedtls_ssl_config_init(conf);conf->max_tls_version=0x303;
    if(radio)CHECK(native_tls_rx_reserve_crt_bundle_attach(conf)==ESP_OK,"radio_attach_success");
}
esp_err_t esp_crt_bundle_attach(void *value) {
    mbedtls_ssl_config *conf=value;
    CHECK(conf!=NULL&&critical_depth==0,"original_attach_outside_critical");
    pthread_mutex_lock(&ledger_lock);++attach_calls;++conf->attached;pthread_mutex_unlock(&ledger_lock);
    if(attach_nested) {
        mbedtls_ssl_config other;configuration(&other,false);mbedtls_ssl_context ssl;
        mbedtls_ssl_init(&ssl);CHECK(mbedtls_ssl_setup(&ssl,&other)==0,"nested_setup_success");
        CHECK(ssl.in_buf!=known_reserve,"nested_client_ordinary_rx");
        mbedtls_ssl_free(&ssl);mbedtls_ssl_config_free(&other);
    }
    return attach_result;
}
static bool all_zero(const void *p,size_t bytes) {
    const unsigned char *data=p;for(size_t n=0;n<bytes;++n)if(data[n])return false;return true;
}
static void setup(mbedtls_ssl_context *ssl,const mbedtls_ssl_config *conf) {
    mbedtls_ssl_init(ssl);allocation_attempt=0;CHECK(mbedtls_ssl_setup(ssl,conf)==0,"setup_success");
}
static void clean(mbedtls_ssl_context *ssl) {
    mbedtls_ssl_free(ssl);CHECK(all_zero(ssl,sizeof(*ssl)),"ssl_free_clears_context");mbedtls_ssl_free(ssl);
}
static void expect_reserve(mbedtls_ssl_config *conf,const char *name) {
    void *p=yoradio_tls_static_rx_calloc(conf,1,MBEDTLS_SSL_IN_BUFFER_LEN);CHECK(p==known_reserve,name);yoradio_tls_static_rx_free(p);
}
static void expect_ordinary(mbedtls_ssl_config *conf,const char *name) {
    void *p=yoradio_tls_static_rx_calloc(conf,1,MBEDTLS_SSL_IN_BUFFER_LEN);CHECK(p&&p!=known_reserve,name);yoradio_tls_static_rx_free(p);
}
static void userdata(void) {
    mbedtls_ssl_config conf;mbedtls_ssl_context ssl;int cookie;
    configuration(&conf,false);mbedtls_ssl_conf_set_user_data_p(&conf,&cookie);
    CHECK(native_tls_rx_reserve_crt_bundle_attach(&conf)==0,"pointer_radio_attach");
    CHECK(mbedtls_ssl_conf_get_user_data_p(&conf)==&cookie,"pointer_radio_userdata_preserved");
    setup(&ssl,&conf);CHECK(ssl.in_buf==known_reserve,"pointer_radio_eligible");clean(&ssl);mbedtls_ssl_config_free(&conf);
    uintptr_t values[]={0,1,UINTPTR_MAX,UINTPTR_MAX-17};
    for(unsigned index=0;index<sizeof(values)/sizeof(values[0]);++index) {
        configuration(&conf,false);mbedtls_ssl_conf_set_user_data_n(&conf,values[index]);
        unsigned char before[sizeof(conf.user_data)];memcpy(before,&conf.user_data,sizeof(before));
        CHECK(native_tls_rx_reserve_crt_bundle_attach(&conf)==0,"integer_radio_attach");
        CHECK(mbedtls_ssl_conf_get_user_data_n(&conf)==values[index]&&!memcmp(before,&conf.user_data,sizeof(before)),"integer_radio_userdata_preserved");
        setup(&ssl,&conf);CHECK(ssl.in_buf==known_reserve,"integer_radio_eligible");clean(&ssl);mbedtls_ssl_config_free(&conf);
        configuration(&conf,false);mbedtls_ssl_conf_set_user_data_n(&conf,values[index]);
        CHECK(esp_crt_bundle_attach(&conf)==0,"integer_nonradio_original_attach");
        setup(&ssl,&conf);CHECK(ssl.in_buf!=known_reserve,"integer_nonradio_ordinary");clean(&ssl);mbedtls_ssl_config_free(&conf);
    }
    configuration(&conf,false);mbedtls_ssl_conf_set_user_data_p(&conf,&cookie);
    setup(&ssl,&conf);CHECK(ssl.in_buf!=known_reserve,"pointer_nonradio_ordinary");clean(&ssl);mbedtls_ssl_config_free(&conf);
    puts("TLS_RX_HOST_CASE userdata_both_kinds_untouched");
}
static void lifetime(void) {
    mbedtls_ssl_config conf;mbedtls_ssl_context ssl,other;
    configuration(&conf,true);expect_reserve(&conf,"initial_registration");
    mbedtls_ssl_config_init(&conf);conf.max_tls_version=0x303;
    expect_ordinary(&conf,"init_revokes_stale_identity");
    CHECK(native_tls_rx_reserve_crt_bundle_attach(&conf)==0,"reattach_after_init");
    mbedtls_ssl_config_free(&conf);expect_ordinary(&conf,"free_revokes_stale_identity");
    configuration(&conf,true);setup(&ssl,&conf);CHECK(ssl.in_buf==known_reserve,"teardown_live_loan");
    memset(ssl.in_buf,0x67,MBEDTLS_SSL_IN_BUFFER_LEN);
    /* The actual ESP-TLS order is config-free before ssl-free. */
    mbedtls_ssl_config_free(&conf);
    CHECK(ssl.in_buf==known_reserve&&ssl.in_buf[0]==0x67,"config_free_never_erases_live_rx");
    mbedtls_ssl_config secondary;configuration(&secondary,true);
    expect_ordinary(&secondary,"config_free_keeps_exclusive_loan");mbedtls_ssl_config_free(&secondary);
    configuration(&conf,false);mbedtls_ssl_conf_set_user_data_n(&conf,UINTPTR_MAX);
    setup(&other,&conf);CHECK(other.in_buf!=known_reserve,"reused_unrelated_address_ordinary_while_loan_live");clean(&other);
    clean(&ssl);setup(&other,&conf);CHECK(other.in_buf!=known_reserve,"reused_unrelated_address_stays_ordinary");clean(&other);
    CHECK(native_tls_rx_reserve_crt_bundle_attach(&conf)==0,"reused_numeric_radio_reattach");
    setup(&ssl,&conf);CHECK(ssl.in_buf==known_reserve&&all_zero(ssl.in_buf,MBEDTLS_SSL_IN_BUFFER_LEN),"reused_address_explicit_reattach");clean(&ssl);mbedtls_ssl_config_free(&conf);
    /* NEW radio at the same address while OLD SSL still owns the loan. */
    configuration(&conf,true);setup(&ssl,&conf);mbedtls_ssl_config_free(&conf);
    configuration(&conf,true);setup(&other,&conf);
    CHECK(other.in_buf!=known_reserve,"new_radio_same_address_waits_for_old_loan");clean(&other);
    clean(&ssl);expect_reserve(&conf,"old_ssl_free_preserves_new_radio_registration");mbedtls_ssl_config_free(&conf);
    /* Cancellation after callback but before setup must not fill the registry. */
    mbedtls_ssl_config canceled[24];
    for(unsigned i=0;i<24;++i){configuration(&canceled[i],true);mbedtls_ssl_config_free(&canceled[i]);}
    configuration(&conf,true);expect_reserve(&conf,"cancel_before_setup_registry_recycled");mbedtls_ssl_config_free(&conf);
    /* Do not add task-only requirements to the originally pure initializer. */
    configuration(&conf,true);unsigned before=atomic_load(&safe_isr_calls);isr=true;mbedtls_ssl_config_init(&conf);isr=false;conf.max_tls_version=0x303;
    CHECK(atomic_load(&safe_isr_calls)>before,"init_uses_safe_isr_critical");expect_ordinary(&conf,"isr_init_revokes_stale_identity");mbedtls_ssl_config_free(&conf);
    mbedtls_ssl_config_free(NULL);
    puts("TLS_RX_HOST_CASE config_init_free_cancel_address_reuse");
}
static void registry_full(void) {
    enum {CAPACITY=8};mbedtls_ssl_config configs[CAPACITY+1];
    for(unsigned index=0;index<CAPACITY+1;++index) {
        configuration(&configs[index],false);mbedtls_ssl_conf_set_user_data_n(&configs[index],(uintptr_t)index+1);
        CHECK(native_tls_rx_reserve_crt_bundle_attach(&configs[index])==0,"full_registry_attach_result_preserved");
        CHECK(mbedtls_ssl_conf_get_user_data_n(&configs[index])==(uintptr_t)index+1,"full_registry_userdata_preserved");
        if(index==0)for(unsigned duplicate=0;duplicate<16;++duplicate)CHECK(native_tls_rx_reserve_crt_bundle_attach(&configs[index])==0,"duplicate_attach_idempotent");
    }
    for(unsigned i=0;i<CAPACITY;++i)expect_reserve(&configs[i],"full_registry_does_not_evict");
    expect_ordinary(&configs[CAPACITY],"full_registry_falls_back_ordinary");
    mbedtls_ssl_config_free(&configs[3]);
    CHECK(native_tls_rx_reserve_crt_bundle_attach(&configs[CAPACITY])==0,"capacity_recovery_attach");
    expect_reserve(&configs[CAPACITY],"released_registry_slot_reusable");
    for(unsigned i=0;i<CAPACITY+1;++i)mbedtls_ssl_config_free(&configs[i]);
    puts("TLS_RX_HOST_CASE bounded_registry_soft_fallback_no_eviction");
}
static void attach_failure(void) {
    mbedtls_ssl_config conf;configuration(&conf,false);mbedtls_ssl_conf_set_user_data_n(&conf,UINTPTR_MAX);
    attach_result=-42;CHECK(native_tls_rx_reserve_crt_bundle_attach(&conf)==-42,"failed_attach_result_preserved");
    expect_ordinary(&conf,"failed_attach_not_registered");attach_result=0;
    attach_nested=true;CHECK(native_tls_rx_reserve_crt_bundle_attach(&conf)==0,"nested_original_attach");attach_nested=false;
    mbedtls_ssl_context ssl;setup(&ssl,&conf);CHECK(ssl.in_buf==known_reserve,"attach_success_registered_after_callback");memset(ssl.in_buf,0x38,MBEDTLS_SSL_IN_BUFFER_LEN);
    attach_result=-42;CHECK(native_tls_rx_reserve_crt_bundle_attach(&conf)==-42,"repeated_attach_failure_preserved");attach_result=0;
    CHECK(ssl.in_buf[0]==0x38,"attach_failure_never_erases_live_rx");clean(&ssl);
    expect_ordinary(&conf,"attach_failure_revokes_after_live_return");
    CHECK(mbedtls_ssl_conf_get_user_data_n(&conf)==UINTPTR_MAX,"attach_failure_numeric_data_preserved");mbedtls_ssl_config_free(&conf);
    puts("TLS_RX_HOST_CASE original_attach_failure_revocation_nested");
}
static void rollback(void) {
    mbedtls_ssl_config conf;configuration(&conf,true);
    for(unsigned allocation=1;allocation<=4;++allocation) {
        mbedtls_ssl_context ssl;mbedtls_ssl_init(&ssl);allocation_attempt=0;fail_at=allocation;
        CHECK(mbedtls_ssl_setup(&ssl,&conf)==MBEDTLS_ERR_SSL_ALLOC_FAILED,"setup_failure_original_error");fail_at=0;
        CHECK(!ssl.in_buf&&!ssl.out_buf&&!ssl.conf,"setup_rollback_clears_rx_tx_conf");
        expect_reserve(&conf,"rollback_returns_slot");clean(&ssl);CHECK(!outstanding,"rollback_no_heap_leaks");
    }
    conf.reject=true;mbedtls_ssl_context ssl;mbedtls_ssl_init(&ssl);unsigned before=allocations;
    CHECK(mbedtls_ssl_setup(&ssl,&conf)==-777&&allocations==before,"config_failure_before_rx_no_allocation");
    clean(&ssl);conf.reject=false;expect_reserve(&conf,"early_failure_registration_retained_until_config_free");mbedtls_ssl_config_free(&conf);
    puts("TLS_RX_HOST_CASE setup_failure_before_rx_and_four_rollbacks");
}
static void fallback(void) {
    mbedtls_ssl_config conf;configuration(&conf,true);void *held=yoradio_tls_static_rx_calloc(&conf,1,MBEDTLS_SSL_IN_BUFFER_LEN);
    CHECK(held==known_reserve,"fallback_holder_reserved");CHECK(native_input_reclaim_bind(&pool),"canonical_reclaim_bind");
    pool=(adaptive_input_t){.idle=4};reclaim_enabled=true;fail_until_released=true;unsigned before=backend_calls;
    void *ordinary=yoradio_tls_static_rx_calloc(&conf,1,MBEDTLS_SSL_IN_BUFFER_LEN);
    CHECK(ordinary&&ordinary!=held&&pool.released==1&&backend_calls==before+2,"busy_slot_reclaim_retry_preserved");
    fail_until_released=false;yoradio_tls_static_rx_zeroize_free(ordinary,MBEDTLS_SSL_IN_BUFFER_LEN);
    isr=true;ordinary=yoradio_tls_static_rx_calloc(&conf,1,MBEDTLS_SSL_IN_BUFFER_LEN);isr=false;
    CHECK(ordinary&&ordinary!=held,"isr_never_loans_reserve");yoradio_tls_static_rx_free(ordinary);
    CHECK(native_input_reclaim_detach(&pool)==NATIVE_INPUT_RECLAIM_DETACHED,"reclaim_detach");reclaim_enabled=false;
    mbedtls_ssl_config_free(&conf);CHECK(((unsigned char *)held)[0]==0,"config_free_keeps_loan_pointer_valid");yoradio_tls_static_rx_free(held);
    puts("TLS_RX_HOST_CASE canonical_reclaim_fallback_preserved");
}
typedef struct {const mbedtls_ssl_config *conf;mbedtls_ssl_context context;pthread_barrier_t *barrier;} worker_t;
static void *parallel_setup(void *p) {worker_t *w=p;int r=pthread_barrier_wait(w->barrier);CHECK(r==0||r==PTHREAD_BARRIER_SERIAL_THREAD,"parallel_barrier");setup(&w->context,w->conf);return NULL;}
static void *release_worker(void *p) {clean(p);return NULL;}
static void concurrent(void) {
    mbedtls_ssl_config configs[2];configuration(&configs[0],true);configuration(&configs[1],true);
    for(unsigned shared=0;shared<2;++shared) {
        pthread_barrier_t barrier;CHECK(!pthread_barrier_init(&barrier,NULL,3),"parallel_barrier_init");
        worker_t workers[2]={{.conf=&configs[0],.barrier=&barrier},{.conf=&configs[shared?0:1],.barrier=&barrier}};pthread_t threads[2];
        for(unsigned i=0;i<2;++i)CHECK(!pthread_create(&threads[i],NULL,parallel_setup,&workers[i]),"parallel_create");
        int r=pthread_barrier_wait(&barrier);CHECK(r==0||r==PTHREAD_BARRIER_SERIAL_THREAD,"parallel_main_barrier");
        for(unsigned i=0;i<2;++i)CHECK(!pthread_join(threads[i],NULL),"parallel_join");
        CHECK(workers[0].context.in_buf!=workers[1].context.in_buf&&((workers[0].context.in_buf==known_reserve)!=(workers[1].context.in_buf==known_reserve)),"parallel_shared_or_distinct_exactly_one_loan");
        clean(&workers[0].context);clean(&workers[1].context);CHECK(!pthread_barrier_destroy(&barrier),"parallel_destroy");
    }
    mbedtls_ssl_context releasing,during;setup(&releasing,&configs[0]);memset(known_reserve,0x7a,MBEDTLS_SSL_IN_BUFFER_LEN);
    pthread_mutex_lock(&erase_lock);erase_gate=true;erase_entered=false;erase_continue=false;pthread_mutex_unlock(&erase_lock);
    pthread_t thread;CHECK(!pthread_create(&thread,NULL,release_worker,&releasing),"erase_create");
    pthread_mutex_lock(&erase_lock);while(!erase_entered)pthread_cond_wait(&erase_cond,&erase_lock);pthread_mutex_unlock(&erase_lock);
    mbedtls_ssl_config_free(&configs[0]);configuration(&configs[0],true);
    setup(&during,&configs[0]);CHECK(during.in_buf!=known_reserve,"no_reloan_during_erase_after_config_reuse");clean(&during);
    pthread_mutex_lock(&erase_lock);erase_continue=true;pthread_cond_broadcast(&erase_cond);pthread_mutex_unlock(&erase_lock);
    CHECK(!pthread_join(thread,NULL),"erase_join");erase_gate=false;
    CHECK(all_zero(known_reserve,MBEDTLS_SSL_IN_BUFFER_LEN),"full_erase_before_reloan");expect_reserve(&configs[0],"erase_handover_reopens");
    mbedtls_ssl_config_free(&configs[0]);mbedtls_ssl_config_free(&configs[1]);
    puts("TLS_RX_HOST_CASE parallel_shared_distinct_config_lifetime_and_erase");
}
void registry_host_check(bool condition,const char *name) {check(condition,name);}
void registry_stale_storage_case(void *reserve);
int main(int argc,char **argv) {
    CHECK(argc==2,"case_argument");mbedtls_ssl_config prime;configuration(&prime,true);
    known_reserve=yoradio_tls_static_rx_calloc(&prime,1,MBEDTLS_SSL_IN_BUFFER_LEN);CHECK(known_reserve!=NULL,"initial_reserve");yoradio_tls_static_rx_free(known_reserve);mbedtls_ssl_config_free(&prime);
    if(!strcmp(argv[1],"stale_storage"))registry_stale_storage_case(known_reserve);else if(!strcmp(argv[1],"userdata"))userdata();else if(!strcmp(argv[1],"lifetime"))lifetime();else if(!strcmp(argv[1],"registry_full"))registry_full();else if(!strcmp(argv[1],"attach_failure"))attach_failure();else if(!strcmp(argv[1],"rollback"))rollback();else if(!strcmp(argv[1],"fallback"))fallback();else if(!strcmp(argv[1],"concurrent"))concurrent();else CHECK(false,"known_case");
    CHECK(!outstanding&&allocations==releases,"allocator_ledger_balanced");printf("TLS_RX_HOST_COMPLETE case=%s allocations=%u releases=%u\n",argv[1],allocations,releases);return 0;
}
