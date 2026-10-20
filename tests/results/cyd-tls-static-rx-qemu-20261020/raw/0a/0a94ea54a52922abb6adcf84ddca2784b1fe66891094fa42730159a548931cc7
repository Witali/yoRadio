/* Registry canonical-source fixture. Actual SDK APIs; no TCP, radio or private SSL fields. */
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "sdkconfig.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "freertos/task.h"
#include "esp_crt_bundle.h"
#include "esp_heap_caps.h"
#include "esp_system.h"
#include "esp_timer.h"
#include "mbedtls/platform.h"
#include "mbedtls/platform_util.h"
#include "mbedtls/ssl.h"
#include "ssl_misc.h"
#include "native_tls_rx_reserve.h"
#include "native_input_reclaim.h"

typedef struct {
    uintptr_t configuration_identity;
    void *pointer;
    size_t bytes;
    unsigned calls;
    int core;
} rx_trace_t;
static portMUX_TYPE s_trace_lock = portMUX_INITIALIZER_UNLOCKED;
static rx_trace_t s_traces[32];
static void *s_reserve;
static void *s_rx_by_core[2];
static bool s_injection, s_pressure, s_erase_arm;
static TaskHandle_t s_injection_task, s_pressure_task;
static unsigned s_heap_ordinal, s_inject_at, s_injected_nulls;
static unsigned s_real_nulls, s_real_recoveries;
static size_t s_last_failed_count, s_last_failed_bytes;
static SemaphoreHandle_t s_worker_start, s_worker_done, s_erase_entered, s_erase_resume;
static void *s_pressure_blocks[256];

static void require(bool condition, const char *name) {
    if (condition) return;
    printf("TLS_RX_TARGET_FAILURE %s\nTLS_RX_TARGET_CONTROLLED_STOP\n", name);
    fflush(stdout);
    esp_restart();
    for (;;) vTaskDelay(portMAX_DELAY);
}
static void integrity(const char *name) {
    require(heap_caps_check_integrity_all(true), name);
}
static bool zeroed(const void *pointer, size_t bytes) {
    const unsigned char *data = pointer;
    for (size_t index = 0; index < bytes; ++index) if (data[index]) return false;
    return true;
}
void *__real_yoradio_tls_static_rx_calloc(const mbedtls_ssl_config *, size_t, size_t);
void *__wrap_yoradio_tls_static_rx_calloc(const mbedtls_ssl_config *configuration,
                                         size_t count, size_t bytes) {
    void *result = __real_yoradio_tls_static_rx_calloc(configuration, count, bytes);
    portENTER_CRITICAL(&s_trace_lock);
    s_rx_by_core[xPortGetCoreID()] = result;
    unsigned slot;
    for (slot = 0; slot < 32; ++slot)
        if (!s_traces[slot].configuration_identity || s_traces[slot].configuration_identity == (uintptr_t)configuration) break;
    if (slot < 32) {
        s_traces[slot] = (rx_trace_t){(uintptr_t)configuration, result, bytes,
            s_traces[slot].calls + 1U, xPortGetCoreID()};
    }
    portEXIT_CRITICAL(&s_trace_lock);
    require(slot < 32, "allocation_trace_capacity");
    return result;
}
static rx_trace_t trace(const mbedtls_ssl_config *configuration) {
    rx_trace_t result = {0};
    portENTER_CRITICAL(&s_trace_lock);
    for (unsigned slot = 0; slot < 32; ++slot)
        if (s_traces[slot].configuration_identity == (uintptr_t)configuration) result = s_traces[slot];
    portEXIT_CRITICAL(&s_trace_lock);
    return result;
}
void *__real_heap_caps_calloc(size_t, size_t, uint32_t);
void *__wrap_heap_caps_calloc(size_t count, size_t bytes, uint32_t caps) {
    TaskHandle_t task = xTaskGetCurrentTaskHandle();
    portENTER_CRITICAL(&s_trace_lock);
    bool inject = s_injection && s_injection_task == task && ++s_heap_ordinal == s_inject_at;
    if (inject) ++s_injected_nulls;
    bool observing = s_pressure && s_pressure_task == task;
    portEXIT_CRITICAL(&s_trace_lock);
    /* The injected branch is explicitly NOT real allocator exhaustion proof. */
    void *result = inject ? NULL : __real_heap_caps_calloc(count, bytes, caps);
    if (observing && !inject) {
        portENTER_CRITICAL(&s_trace_lock);
        if (!result) {
            ++s_real_nulls;
            s_last_failed_count = count; s_last_failed_bytes = bytes;
        } else if (s_real_nulls && s_last_failed_count == count && s_last_failed_bytes == bytes) {
            ++s_real_recoveries;
        }
        portEXIT_CRITICAL(&s_trace_lock);
    }
    return result;
}
void __real_heap_caps_free(void *);
void __wrap_heap_caps_free(void *pointer) {
    require(!pointer || pointer != s_reserve, "reserved_pointer_never_sdk_heap_free");
    __real_heap_caps_free(pointer);
}
void __real_mbedtls_platform_zeroize(void *, size_t);
void __wrap_mbedtls_platform_zeroize(void *pointer, size_t bytes) {
    portENTER_CRITICAL(&s_trace_lock);
    bool wait = s_erase_arm && pointer == s_reserve;
    portEXIT_CRITICAL(&s_trace_lock);
    if (wait) {
        xSemaphoreGive(s_erase_entered);
        require(xSemaphoreTake(s_erase_resume, pdMS_TO_TICKS(5000)) == pdTRUE, "erase_resume_timeout");
    }
    __real_mbedtls_platform_zeroize(pointer, bytes);
}
/* Control-only candidate copies may call this phase predicate. Canonical
 * candidate never calls it. This is not a production hook. */
int tls_reserve_test_erase_phase(void) {
    portENTER_CRITICAL(&s_trace_lock);
    bool result = s_erase_arm;
    portEXIT_CRITICAL(&s_trace_lock);
    return result;
}

static void configure(mbedtls_ssl_config *configuration, bool radio) {
    mbedtls_ssl_config_init(configuration);
    require(mbedtls_ssl_config_defaults(configuration, MBEDTLS_SSL_IS_CLIENT,
        MBEDTLS_SSL_TRANSPORT_STREAM, MBEDTLS_SSL_PRESET_DEFAULT) == 0, "configuration_defaults");
    require((radio ? native_tls_rx_reserve_crt_bundle_attach(configuration) :
             esp_crt_bundle_attach(configuration)) == ESP_OK, "actual_certificate_bundle_attach");
}
static void setup(mbedtls_ssl_context *context, const mbedtls_ssl_config *configuration) {
    mbedtls_ssl_init(context);
    require(mbedtls_ssl_setup(context, configuration) == 0, "actual_sdk_setup_success");
    rx_trace_t result = trace(configuration);
    require(result.pointer && result.bytes == MBEDTLS_SSL_IN_BUFFER_LEN, "actual_sdk_full_record_capacity");
}
static void cleanup(mbedtls_ssl_context *context) {
    mbedtls_ssl_free(context);
    mbedtls_ssl_free(context);
}
/* Real public SDK configuration APIs. No private SSL/config fields are read. */
static void require_reserved_probe(const mbedtls_ssl_config *config,const char *name) {
    void *p=yoradio_tls_static_rx_calloc(config,1,MBEDTLS_SSL_IN_BUFFER_LEN);
    require(p==s_reserve,name);yoradio_tls_static_rx_free(p);
}
static void require_ordinary_probe(const mbedtls_ssl_config *config,const char *name) {
    void *p=yoradio_tls_static_rx_calloc(config,1,MBEDTLS_SSL_IN_BUFFER_LEN);
    require(p&&p!=s_reserve,name);yoradio_tls_static_rx_free(p);
}
esp_err_t __real_esp_crt_bundle_attach(void *configuration);
static bool s_attach_return_failure;
esp_err_t __wrap_esp_crt_bundle_attach(void *configuration) {
    esp_err_t result=__real_esp_crt_bundle_attach(configuration);
    /* Scoped result injection AFTER the real provider. This is not an actual
     * certificate validation failure, handshake or authentication test. */
    return result==ESP_OK&&s_attach_return_failure?ESP_FAIL:result;
}
/* Target semantic-control phase only. The canonical module never calls this. */
static bool s_forget_failure_phase;
int tls_reserve_test_forget_phase(void) {
    portENTER_CRITICAL_SAFE(&s_trace_lock);bool armed=s_forget_failure_phase;portEXIT_CRITICAL_SAFE(&s_trace_lock);return armed;
}
static void arm_forget_failure_phase(bool armed) {
    portENTER_CRITICAL_SAFE(&s_trace_lock);s_forget_failure_phase=armed;portEXIT_CRITICAL_SAFE(&s_trace_lock);
}
static void registry_userdata_lifetimes(void) {
    mbedtls_ssl_config config,secondary;mbedtls_ssl_context live,other;int cookie;
    configure(&config,false);mbedtls_ssl_conf_set_user_data_p(&config,&cookie);
    require(native_tls_rx_reserve_crt_bundle_attach(&config)==ESP_OK&&mbedtls_ssl_conf_get_user_data_p(&config)==&cookie,"pointer_radio_userdata_preserved");
    require_reserved_probe(&config,"pointer_radio_eligible");mbedtls_ssl_config_free(&config);
    const uintptr_t values[]={0,1,UINTPTR_MAX,UINTPTR_MAX-17U};
    for(unsigned i=0;i<sizeof(values)/sizeof(values[0]);++i) {
        configure(&config,false);mbedtls_ssl_conf_set_user_data_n(&config,values[i]);
        require(native_tls_rx_reserve_crt_bundle_attach(&config)==ESP_OK&&mbedtls_ssl_conf_get_user_data_n(&config)==values[i],"integer_radio_userdata_preserved");
        require_reserved_probe(&config,"integer_radio_eligible");mbedtls_ssl_config_free(&config);
        configure(&config,false);mbedtls_ssl_conf_set_user_data_n(&config,values[i]);
        require_ordinary_probe(&config,"integer_nonradio_ordinary");mbedtls_ssl_config_free(&config);
    }
    configure(&config,true);mbedtls_ssl_config_init(&config);
    require_ordinary_probe(&config,"init_revokes_stale_identity");mbedtls_ssl_config_free(&config);
    configure(&config,true);mbedtls_ssl_config_free(&config);
    require_ordinary_probe(&config,"free_revokes_stale_identity");
    configure(&config,true);setup(&live,&config);memset(s_reserve,0x67,MBEDTLS_SSL_IN_BUFFER_LEN);
    /* This is the pinned real ESP-TLS teardown order, not a mock teardown. */
    arm_forget_failure_phase(true);mbedtls_ssl_config_free(&config);arm_forget_failure_phase(false);
    require(((unsigned char *)s_reserve)[0]==0x67,"config_free_never_erases_live_rx");
    configure(&secondary,true);require_ordinary_probe(&secondary,"config_free_keeps_exclusive_loan");mbedtls_ssl_config_free(&secondary);
    configure(&config,false);mbedtls_ssl_conf_set_user_data_n(&config,UINTPTR_MAX);
    setup(&other,&config);require(trace(&config).pointer!=s_reserve,"reused_address_ordinary_while_prior_loan_live");cleanup(&other);
    cleanup(&live);setup(&other,&config);require(trace(&config).pointer!=s_reserve,"reused_unrelated_address_stays_ordinary");cleanup(&other);
    require(native_tls_rx_reserve_crt_bundle_attach(&config)==ESP_OK,"explicit_reattach_after_address_reuse");
    require_reserved_probe(&config,"reused_address_radio_eligible");
    setup(&live,&config);mbedtls_ssl_config_free(&config);configure(&config,true);
    mbedtls_ssl_conf_set_user_data_n(&config,UINTPTR_MAX);
    require_ordinary_probe(&config,"new_radio_same_address_waits_for_old_loan");
    cleanup(&live);
    require_reserved_probe(&config,"old_ssl_free_preserves_new_radio_registration");
    setup(&live,&config);memset(s_reserve,0x38,MBEDTLS_SSL_IN_BUFFER_LEN);
    s_attach_return_failure=true;
    esp_err_t failed=native_tls_rx_reserve_crt_bundle_attach(&config);
    s_attach_return_failure=false;
    require(failed==ESP_FAIL&&mbedtls_ssl_conf_get_user_data_n(&config)==UINTPTR_MAX,"injected_attach_failure_preserves_result_userdata");
    require(((unsigned char *)s_reserve)[0]==0x38,"failed_attach_never_erases_live_loan");
    cleanup(&live);require_ordinary_probe(&config,"failed_attach_revokes_eligibility");mbedtls_ssl_config_free(&config);
    /* Public valid version values in an invalid min>max combination force the
     * actual SDK pre-RX validation path, without a fake calloc result. */
    configure(&config,true);unsigned calls=trace(&config).calls;
    mbedtls_ssl_conf_min_tls_version(&config,MBEDTLS_SSL_VERSION_TLS1_3);
    mbedtls_ssl_conf_max_tls_version(&config,MBEDTLS_SSL_VERSION_TLS1_2);
    mbedtls_ssl_init(&live);int result=mbedtls_ssl_setup(&live,&config);
    require(result==MBEDTLS_ERR_SSL_BAD_CONFIG&&trace(&config).calls==calls,"actual_setup_rejects_before_rx");cleanup(&live);
    require_reserved_probe(&config,"early_setup_failure_retains_config_registration");mbedtls_ssl_config_free(&config);
    for(unsigned i=0;i<24;++i){configure(&config,true);mbedtls_ssl_config_free(&config);}
    configure(&config,true);require_reserved_probe(&config,"cancel_before_setup_registry_recycles");mbedtls_ssl_config_free(&config);
    integrity("registry_lifetimes_heap_integrity");
    puts("TLS_RX_TARGET_CASE registry_userdata_init_free_live_reuse attach_return_injection=1 early_setup_actual=1");
}
static mbedtls_ssl_config s_registry_configs[9];
static void registry_full(void) {
    for(unsigned i=0;i<9;++i) {
        configure(&s_registry_configs[i],false);mbedtls_ssl_conf_set_user_data_n(&s_registry_configs[i],i+1U);
        require(native_tls_rx_reserve_crt_bundle_attach(&s_registry_configs[i])==ESP_OK,"registry_full_attach_result_preserved");
        if(i==0)for(unsigned repeat=0;repeat<16;++repeat)require(native_tls_rx_reserve_crt_bundle_attach(&s_registry_configs[i])==ESP_OK,"duplicate_attach_idempotent");
    }
    for(unsigned i=0;i<8;++i)require_reserved_probe(&s_registry_configs[i],"full_registry_does_not_evict");
    require_ordinary_probe(&s_registry_configs[8],"full_registry_ordinary_fallback");
    mbedtls_ssl_config_free(&s_registry_configs[3]);
    require(native_tls_rx_reserve_crt_bundle_attach(&s_registry_configs[8])==ESP_OK,"registry_slot_recovery_attach");
    require_reserved_probe(&s_registry_configs[8],"registry_slot_recovery_eligible");
    for(unsigned i=0;i<9;++i)mbedtls_ssl_config_free(&s_registry_configs[i]);
    integrity("registry_full_heap_integrity");puts("TLS_RX_TARGET_CASE registry_capacity entries=8 clients=9 soft_fallback=1");
}
static mbedtls_ssl_config s_isr_config;
static SemaphoreHandle_t s_init_done;
static volatile bool s_init_seen_isr;
static void init_isr_callback(void *argument) {
    (void)argument;s_init_seen_isr=xPortInIsrContext();
    mbedtls_ssl_config_init(&s_isr_config);
    BaseType_t wake=pdFALSE;xSemaphoreGiveFromISR(s_init_done,&wake);
    if(wake)esp_timer_isr_dispatch_need_yield();
}
static void initializer_from_actual_isr(void) {
    /* Only global bundle callback/numeric userdata are attached: there are no
     * owned PSK/key allocations to abandon when exercising the pure reset. */
    mbedtls_ssl_config_init(&s_isr_config);mbedtls_ssl_conf_set_user_data_n(&s_isr_config,UINTPTR_MAX);
    require(native_tls_rx_reserve_crt_bundle_attach(&s_isr_config)==ESP_OK,"isr_reset_radio_attach");
    require_reserved_probe(&s_isr_config,"isr_reset_prior_registration");
    s_init_done=xSemaphoreCreateBinary();require(s_init_done!=NULL,"isr_done_semaphore");
    esp_timer_handle_t timer=NULL;
    esp_timer_create_args_t args={.callback=init_isr_callback,.dispatch_method=ESP_TIMER_ISR,.name="tls-config-init"};
    require(esp_timer_create(&args,&timer)==ESP_OK,"actual_isr_timer_create");
    require(esp_timer_start_once(timer,1000)==ESP_OK,"actual_isr_timer_start");
    require(xSemaphoreTake(s_init_done,pdMS_TO_TICKS(5000))==pdTRUE&&s_init_seen_isr,"actual_initializer_isr_observed");
    require(esp_timer_delete(timer)==ESP_OK,"actual_isr_timer_delete");vSemaphoreDelete(s_init_done);
    require_ordinary_probe(&s_isr_config,"actual_isr_init_revokes_eligibility");mbedtls_ssl_config_free(&s_isr_config);
    integrity("actual_isr_init_heap_integrity");puts("TLS_RX_TARGET_CASE actual_initializer_isr registry_revoked=1");
}

static void ownership_and_rollback(void) {
    mbedtls_ssl_config radio, ordinary, occupied;
    configure(&radio, true);
    s_reserve = yoradio_tls_static_rx_calloc(&radio, 1, MBEDTLS_SSL_IN_BUFFER_LEN);
    require(s_reserve != NULL, "initial_reserved_pointer");
    yoradio_tls_static_rx_free(s_reserve);
    configure(&ordinary, false);
    mbedtls_ssl_context context, second;
    setup(&context, &ordinary);
    require(trace(&ordinary).pointer != s_reserve, "unlabelled_client_ordinary_rx");
    cleanup(&context);
    configure(&occupied, false);
    int marker;
    mbedtls_ssl_conf_set_user_data_p(&occupied, &marker);
    require(native_tls_rx_reserve_crt_bundle_attach(&occupied) == ESP_OK &&
        mbedtls_ssl_conf_get_user_data_p(&occupied) == &marker, "occupied_userdata_preserved");
    setup(&context, &occupied);
    require(trace(&occupied).pointer == s_reserve, "occupied_radio_eligible");
    cleanup(&context);
    setup(&context, &radio);
    require(trace(&radio).pointer == s_reserve, "radio_reserved_rx");
    configure(&occupied, true);
    setup(&second, &occupied);
    require(trace(&occupied).pointer != trace(&radio).pointer, "independent_context_rx_no_alias");
    cleanup(&second);
    memset(s_reserve, 0x9a, MBEDTLS_SSL_IN_BUFFER_LEN);
    require(mbedtls_ssl_session_reset(&context) == 0, "actual_sdk_session_reset");
    require(trace(&radio).pointer == s_reserve && zeroed(s_reserve, MBEDTLS_SSL_IN_BUFFER_LEN),
        "session_reset_retains_full_rx");
    cleanup(&context);
    require(zeroed(s_reserve, MBEDTLS_SSL_IN_BUFFER_LEN), "erase_complete_before_reopen");
    for (unsigned cycle = 0; cycle < 16; ++cycle) {
        setup(&context, &radio);
        require(trace(&radio).pointer == s_reserve, "reopen_reserved_rx");
        cleanup(&context);
    }
    for (unsigned ordinal = 1; ordinal <= 4; ++ordinal) {
        mbedtls_ssl_init(&context);
        portENTER_CRITICAL(&s_trace_lock);
        s_injection = true; s_injection_task = xTaskGetCurrentTaskHandle();
        s_heap_ordinal = 0; s_inject_at = ordinal;
        unsigned prior = s_injected_nulls;
        portEXIT_CRITICAL(&s_trace_lock);
        int result = mbedtls_ssl_setup(&context, &radio);
        portENTER_CRITICAL(&s_trace_lock);
        s_injection = false;
        unsigned injected = s_injected_nulls;
        portEXIT_CRITICAL(&s_trace_lock);
        require(result == MBEDTLS_ERR_SSL_ALLOC_FAILED && injected == prior + 1,
            "scoped_injection_setup_rollback");
        void *again = yoradio_tls_static_rx_calloc(&radio, 1, MBEDTLS_SSL_IN_BUFFER_LEN);
        require(again == s_reserve, "rollback_returns_slot");
        yoradio_tls_static_rx_free(again);
        cleanup(&context);
    }
    mbedtls_ssl_config_free(&occupied);
    mbedtls_ssl_config_free(&ordinary);
    mbedtls_ssl_config_free(&radio);
    integrity("ownership_rollback_heap_integrity");
    printf("TLS_RX_TARGET_CASE ownership_rollback_reopen injected_nulls=%u real_oom_claim=0\n", s_injected_nulls);
}

typedef struct {
    mbedtls_ssl_config configuration;
    mbedtls_ssl_context context;
    bool release;
    const mbedtls_ssl_config *borrowed;
} worker_t;
static worker_t s_worker;
static void core_one_worker(void *unused) {
    (void)unused;
    for (;;) {
        xSemaphoreTake(s_worker_start, portMAX_DELAY);
        require(xPortGetCoreID() == 1, "worker_core_one");
        if (s_worker.release) cleanup(&s_worker.context);
        else setup(&s_worker.context, s_worker.borrowed ? s_worker.borrowed : &s_worker.configuration);
        xSemaphoreGive(s_worker_done);
    }
}
static void wait_worker(void) {
    require(xSemaphoreTake(s_worker_done, pdMS_TO_TICKS(8000)) == pdTRUE, "worker_completion_timeout");
}
static void smp_and_erase(void) {
    mbedtls_ssl_config radio;
    configure(&radio, true);
    configure(&s_worker.configuration, true);
    mbedtls_ssl_context context;
    s_worker.release = false;
    xSemaphoreGive(s_worker_start);
    setup(&context, &radio);
    wait_worker();
    void *left = trace(&radio).pointer, *right = trace(&s_worker.configuration).pointer;
    require(left != right && ((left == s_reserve) != (right == s_reserve)),
        "parallel_configs_exactly_one_reserve");
    cleanup(&context);
    s_worker.release = true; xSemaphoreGive(s_worker_start); wait_worker();
    s_worker.release = false; xSemaphoreGive(s_worker_start); wait_worker();
    require(trace(&s_worker.configuration).pointer == s_reserve, "core_one_handover_claim");
    memset(s_reserve, 0xa6, MBEDTLS_SSL_IN_BUFFER_LEN);
    portENTER_CRITICAL(&s_trace_lock); s_erase_arm = true; portEXIT_CRITICAL(&s_trace_lock);
    s_worker.release = true; xSemaphoreGive(s_worker_start);
    require(xSemaphoreTake(s_erase_entered, pdMS_TO_TICKS(5000)) == pdTRUE, "erase_barrier_entered");
    mbedtls_ssl_config_free(&radio);configure(&radio,true);
    setup(&context, &radio);
    require(trace(&radio).pointer != s_reserve, "no_reloan_during_erase");
    cleanup(&context);
    xSemaphoreGive(s_erase_resume);
    wait_worker();
    portENTER_CRITICAL(&s_trace_lock); s_erase_arm = false; portEXIT_CRITICAL(&s_trace_lock);
    require(zeroed(s_reserve, MBEDTLS_SSL_IN_BUFFER_LEN), "erase_complete_before_reopen");
    setup(&context, &radio);
    require(trace(&radio).pointer == s_reserve, "core_zero_handover_after_erase");
    cleanup(&context);
    /* Shared immutable config, two actual pinned cores, no private SSL fields. */
    setup(&context,&radio);s_worker.borrowed=&radio;s_worker.release=false;
    xSemaphoreGive(s_worker_start);wait_worker();
    portENTER_CRITICAL(&s_trace_lock);void *core0=s_rx_by_core[0],*core1=s_rx_by_core[1];portEXIT_CRITICAL(&s_trace_lock);
    require(core0!=core1&&((core0==s_reserve)!=(core1==s_reserve)),"shared_config_two_core_exclusive_loan");
    cleanup(&context);s_worker.release=true;xSemaphoreGive(s_worker_start);wait_worker();s_worker.borrowed=NULL;
    mbedtls_ssl_config_free(&s_worker.configuration);
    mbedtls_ssl_config_free(&radio);
    integrity("smp_heap_integrity");
    puts("TLS_RX_TARGET_CASE smp_ownership_handover_erase cores=0,1");
}

static void release_pressure(unsigned count);
static unsigned heap_pressure(void) {
    unsigned count = 0;
    const size_t sizes[] = {4096, 512, 64};
    for (unsigned index = 0; index < 3; ++index) {
        while (count < 256) {
            void *block = heap_caps_malloc(sizes[index], MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT);
            if (!block) break;
            s_pressure_blocks[count++] = block;
        }
    }
    if (count == 256) {
        release_pressure(count);
        require(false, "pressure_pointer_capacity");
    }
    return count;
}
static void release_pressure(unsigned count) {
    for (unsigned index = 0; index < count; ++index) {
        heap_caps_free(s_pressure_blocks[index]); s_pressure_blocks[index] = NULL;
    }
}
static void actual_heap_cases(void) {
    mbedtls_ssl_config radio;
    configure(&radio, true);
    mbedtls_ssl_context context;
    unsigned blocks = heap_pressure();
    portENTER_CRITICAL(&s_trace_lock);
    s_pressure = true; s_pressure_task = xTaskGetCurrentTaskHandle(); s_real_nulls = 0; s_real_recoveries = 0;
    portEXIT_CRITICAL(&s_trace_lock);
    mbedtls_ssl_init(&context);
    int result = mbedtls_ssl_setup(&context, &radio);
    portENTER_CRITICAL(&s_trace_lock); s_pressure = false; unsigned nulls = s_real_nulls; portEXIT_CRITICAL(&s_trace_lock);
    const bool observed_reserved_oom = trace(&radio).pointer == s_reserve &&
        result == MBEDTLS_ERR_SSL_ALLOC_FAILED && nulls > 0;
    /* Capture the actual allocator observation BEFORE restoring memory. Release
     * only fixture-owned pressure blocks before diagnostic/restart allocations. */
    release_pressure(blocks);
    cleanup(&context);
    require(observed_reserved_oom, "real_heap_exhaustion_after_reserved_rx");
    setup(&context, &radio);
    require(trace(&radio).pointer == s_reserve, "real_oom_rollback_returns_slot");
    cleanup(&context);
    integrity("real_oom_heap_integrity");
    printf("TLS_RX_TARGET_CASE real_oom_reserved_rx blocks=%u actual_backend_nulls=%u\n", blocks, nulls);

#if CONFIG_YORADIO_TLS_INPUT_RECLAIM
    adaptive_input_t *input = adaptive_input_create(8U * 16384U, 4U * 16384U, 16384U);
    require(input && native_input_reclaim_bind(input), "actual_input_reclaim_bind");
    void *reading, *ready, *writing;
    require(adaptive_input_acquire(input, &reading, 16, 0) == pdTRUE, "input_reading_acquire");
    memset(reading, 0xa5, 16); require(adaptive_input_commit(input, reading) == pdTRUE, "input_reading_commit");
    require(adaptive_input_acquire(input, &ready, 16, 0) == pdTRUE, "input_ready_acquire");
    memset(ready, 0x5a, 16); require(adaptive_input_commit(input, ready) == pdTRUE, "input_ready_commit");
    size_t received;
    require(adaptive_input_receive(input, &received, 0) == reading && received == 16, "input_reading_receive");
    require(adaptive_input_acquire(input, &writing, 16, 0) == pdTRUE, "input_writing_acquire");
    memset(writing, 0x33, 16);
    void *held = yoradio_tls_static_rx_calloc(&radio, 1, MBEDTLS_SSL_IN_BUFFER_LEN);
    require(held == s_reserve, "reclaim_holder_reserved");
    blocks = heap_pressure();
    portENTER_CRITICAL(&s_trace_lock);
    s_pressure = true; s_pressure_task = xTaskGetCurrentTaskHandle(); s_real_nulls = 0; s_real_recoveries = 0;
    portEXIT_CRITICAL(&s_trace_lock);
    /* This call must first receive an actual unchanged heap allocator NULL,
     * then pass through canonical reclaim and recover the same request. */
    void *ordinary = yoradio_tls_static_rx_calloc(&radio, 1, MBEDTLS_SSL_IN_BUFFER_LEN);
    portENTER_CRITICAL(&s_trace_lock);
    s_pressure = false; nulls = s_real_nulls; unsigned recoveries = s_real_recoveries;
    portEXIT_CRITICAL(&s_trace_lock);
    adaptive_input_stats_t stats = adaptive_input_stats(input);
    const bool observed_reclaim = ordinary && ordinary != held && nulls > 0 &&
        recoveries > 0 && stats.released > 0;
    const bool observed_floor_and_leases = stats.resident >= stats.minimum &&
        stats.minimum == 4 && stats.target == 8 && stats.ready == 1 &&
        stats.reading == 1 && stats.writing == 1;
    bool observed_payloads = true;
    for (unsigned index = 0; index < 16; ++index)
        observed_payloads = observed_payloads && ((unsigned char *)reading)[index] == 0xa5 &&
            ((unsigned char *)ready)[index] == 0x5a && ((unsigned char *)writing)[index] == 0x33;
    /* Preserve every predicate under pressure; restore only test pressure heap
     * before require() can print/esp_restart and lazily allocate SDK locks. */
    release_pressure(blocks);
    require(observed_reclaim, "busy_slot_reclaim_retry_preserved");
    require(observed_floor_and_leases, "actual_reclaim_floor_and_leases_preserved");
    require(observed_payloads, "actual_reclaim_payloads_preserved");
    yoradio_tls_static_rx_zeroize_free(ordinary, MBEDTLS_SSL_IN_BUFFER_LEN);
    yoradio_tls_static_rx_free(held);
    require(adaptive_input_return(input, reading) && adaptive_input_cancel(input, writing), "input_lease_cleanup");
    require(adaptive_input_receive(input, &received, 0) == ready && adaptive_input_return(input, ready), "input_ready_cleanup");
    require(native_input_reclaim_detach(input) == NATIVE_INPUT_RECLAIM_DETACHED, "actual_reclaim_detach");
    adaptive_input_destroy(input);
    integrity("reclaim_coexistence_heap_integrity");
    printf("TLS_RX_TARGET_CASE actual_reclaim_recovery real_nulls=%u recoveries=%u released=%u min=4 target=8\n",
        nulls, recoveries, stats.released);
#endif
    mbedtls_ssl_config_free(&radio);
}

void app_main(void) {
    puts("TLS_RX_TARGET_ENTRY registry_fixture=1");
    s_worker_start = xSemaphoreCreateBinary(); s_worker_done = xSemaphoreCreateBinary();
    s_erase_entered = xSemaphoreCreateBinary(); s_erase_resume = xSemaphoreCreateBinary();
    require(s_worker_start && s_worker_done && s_erase_entered && s_erase_resume, "fixture_semaphore_creation");
    require(xTaskCreatePinnedToCore(core_one_worker, "tls_rx_worker", 6144, NULL, 3, NULL, 1) == pdPASS,
        "fixture_core_one_task_creation");
    require(xPortGetCoreID() == 0, "coordinator_core_zero");
    printf("TLS_RX_TARGET_CAPACITY content=%u storage=%u pointer_alignment=%u\n",
        (unsigned)MBEDTLS_SSL_IN_CONTENT_LEN, (unsigned)MBEDTLS_SSL_IN_BUFFER_LEN, (unsigned)_Alignof(max_align_t));
    ownership_and_rollback();
    registry_userdata_lifetimes();registry_full();initializer_from_actual_isr();
    smp_and_erase();
    actual_heap_cases();
    integrity("final_heap_integrity");
    puts("TLS_RX_TARGET_COMPLETE registry_fixture=1 production_radio=0 physical_benefit=0");
    fflush(stdout);
    esp_restart();
}
