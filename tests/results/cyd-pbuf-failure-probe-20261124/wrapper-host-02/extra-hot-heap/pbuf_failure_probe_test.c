#define _POSIX_C_SOURCE 200809L
#include <assert.h>
#include <pthread.h>
#include <sched.h>
#include <stdarg.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "freertos/FreeRTOS.h"
#include "lwip/mem.h"
#include "lwip/pbuf.h"
#include "esp_cpu_utils.h"

/* Scope-only trampolines forward to the actual unchanged inline record bodies. */
#define pbuf_failure_record_add actual_record_add
#define pbuf_failure_record_snapshot actual_record_snapshot
#include "pbuf_failure_record.h"
#undef pbuf_failure_record_add
#undef pbuf_failure_record_snapshot

static _Thread_local unsigned t_critical_depth, t_wrapper_depth, t_real_depth, t_dump_depth;
static _Thread_local unsigned t_real_calls_in_wrapper;
static _Thread_local pbuf_layer t_layer;
static _Thread_local u16_t t_length;
static _Thread_local pbuf_type t_type;
static _Thread_local struct pbuf *t_real_result;
static atomic_uint s_real_calls, s_record_additions, s_snapshots, s_critical_entries, s_rom_calls;
static atomic_uint s_probe_heap_calls, s_normal_lock_entries;
static char s_capture[131072];
static size_t s_capture_bytes;
static pthread_mutex_t s_capture_lock = PTHREAD_MUTEX_INITIALIZER;
static void (*s_first_print_hook)(void);

static void checked_record_add(pbuf_failure_record_t *table, const pbuf_failure_key_t *key) {
    assert(t_critical_depth == 1);
    assert(t_wrapper_depth == 1 && t_real_depth == 0 && t_real_calls_in_wrapper == 1);
    atomic_fetch_add(&s_record_additions, 1);
    actual_record_add(table, key);
}

static void checked_record_snapshot(const pbuf_failure_record_t *table, pbuf_failure_record_t *snapshot) {
    assert(t_critical_depth == 1);
    assert(t_dump_depth == 1 && t_wrapper_depth == 0 && t_real_depth == 0);
    atomic_fetch_add(&s_snapshots, 1);
    actual_record_snapshot(table, snapshot);
}

#define pbuf_failure_record_add checked_record_add
#define pbuf_failure_record_snapshot checked_record_snapshot
#include "pbuf_failure.c"
#undef pbuf_failure_record_add
#undef pbuf_failure_record_snapshot

void host_enter_critical(portMUX_TYPE *lock, unsigned isr_form) {
    assert(lock == &s_pbuf_failure_lock);
    assert(t_critical_depth == 0 && t_real_depth == 0);
    assert(pthread_mutex_lock(lock) == 0);
    t_critical_depth = 1;
    atomic_fetch_add(&s_critical_entries, 1);
    if (!isr_form) atomic_fetch_add(&s_normal_lock_entries, 1);
}

void host_exit_critical(portMUX_TYPE *lock, unsigned isr_form) {
    (void)isr_form;
    assert(lock == &s_pbuf_failure_lock && t_critical_depth == 1);
    t_critical_depth = 0;
    assert(pthread_mutex_unlock(lock) == 0);
}

struct pbuf *__real_pbuf_alloc(pbuf_layer layer, u16_t length, pbuf_type type) {
    assert(t_wrapper_depth == 1 && t_real_depth == 0 && t_critical_depth == 0);
    assert(t_real_calls_in_wrapper == 0);
    ++t_real_depth;
    ++t_real_calls_in_wrapper;
    atomic_fetch_add(&s_real_calls, 1);
    assert(layer == t_layer && length == t_length && type == t_type);
    struct pbuf *result = t_real_result;
    --t_real_depth;
    return result;
}

static void check_heap_scope(void) {
    assert(t_critical_depth == 0);
    if (t_wrapper_depth && !t_real_depth) atomic_fetch_add(&s_probe_heap_calls, 1);
    assert(!t_wrapper_depth || t_real_depth);
}

void *__real_malloc(size_t);
void *__real_calloc(size_t, size_t);
void *__real_realloc(void *, size_t);
void __real_free(void *);
void *__wrap_malloc(size_t bytes) { check_heap_scope(); return __real_malloc(bytes); }
void *__wrap_calloc(size_t count, size_t bytes) { check_heap_scope(); return __real_calloc(count, bytes); }
void *__wrap_realloc(void *pointer, size_t bytes) { check_heap_scope(); return __real_realloc(pointer, bytes); }
void __wrap_free(void *pointer) { check_heap_scope(); __real_free(pointer); }

int esp_rom_printf(const char *format, ...) {
    assert(t_critical_depth == 0);
    assert(t_wrapper_depth == 0 && t_real_depth == 0 && t_dump_depth == 1);
    atomic_fetch_add(&s_rom_calls, 1);
    if (s_first_print_hook) {
        void (*hook)(void) = s_first_print_hook;
        s_first_print_hook = NULL;
        hook();
    }
    char line[1024];
    va_list args;
    va_start(args, format);
    int length = vsnprintf(line, sizeof(line), format, args);
    va_end(args);
    assert(length > 0 && (size_t)length < sizeof(line));
    assert(pthread_mutex_lock(&s_capture_lock) == 0);
    assert((size_t)length < sizeof(s_capture) - s_capture_bytes);
    memcpy(s_capture + s_capture_bytes, line, (size_t)length + 1);
    s_capture_bytes += (size_t)length;
    assert(pthread_mutex_unlock(&s_capture_lock) == 0);
    return length;
}

static void begin_call(pbuf_layer layer, u16_t length, pbuf_type type, struct pbuf *result) {
    assert(t_wrapper_depth == 0 && t_real_depth == 0 && t_critical_depth == 0);
    t_layer = layer; t_length = length; t_type = type; t_real_result = result;
    t_real_calls_in_wrapper = 0;
    t_wrapper_depth = 1;
}

static void end_call(struct pbuf *result) {
    assert(result == t_real_result && t_real_calls_in_wrapper == 1);
    assert(t_real_depth == 0 && t_critical_depth == 0 && t_wrapper_depth == 1);
    t_wrapper_depth = 0;
}

__attribute__((noinline))
static struct pbuf *invoke_a(pbuf_layer layer, u16_t length, pbuf_type type, struct pbuf *expected) {
    begin_call(layer, length, type, expected);
    struct pbuf *result = __wrap_pbuf_alloc(layer, length, type);
    end_call(result);
    return result;
}

__attribute__((noinline))
static struct pbuf *invoke_b(pbuf_layer layer, u16_t length, pbuf_type type, struct pbuf *expected) {
    begin_call(layer, length, type, expected);
    struct pbuf *result = __wrap_pbuf_alloc(layer, length, type);
    end_call(result);
    return result;
}

static pbuf_failure_record_t inspect_table(void) {
    pbuf_failure_record_t result;
    portENTER_CRITICAL_ISR(&s_pbuf_failure_lock);
    actual_record_snapshot(&s_pbuf_failures, &result);
    portEXIT_CRITICAL_ISR(&s_pbuf_failure_lock);
    return result;
}

static void reset_case(void) {
    portENTER_CRITICAL_ISR(&s_pbuf_failure_lock);
    memset(&s_pbuf_failures, 0, sizeof(s_pbuf_failures));
    portEXIT_CRITICAL_ISR(&s_pbuf_failure_lock);
    atomic_store(&s_real_calls, 0); atomic_store(&s_record_additions, 0);
    atomic_store(&s_snapshots, 0); atomic_store(&s_critical_entries, 0);
    atomic_store(&s_rom_calls, 0); atomic_store(&s_probe_heap_calls, 0);
    atomic_store(&s_normal_lock_entries, 0);
    s_capture_bytes = 0; s_capture[0] = '\0'; s_first_print_hook = NULL;
}

static void dump(void) {
    assert(t_dump_depth == 0);
    ++t_dump_depth;
    cyd_openeth_pbuf_failure_dump();
    --t_dump_depth;
}

static void test_success_forwarding(void) {
    reset_case();
    struct pbuf object;
    memset(&object, 0xa5, sizeof(object));
    unsigned char original[sizeof(object)];
    memcpy(original, &object, sizeof(object));
    const pbuf_layer layers[] = {PBUF_RAW, PBUF_LINK, PBUF_IP, PBUF_TRANSPORT, (pbuf_layer)0x10003};
    const u16_t lengths[] = {0, 1, 1440, UINT16_MAX};
    const pbuf_type types[] = {PBUF_RAM, PBUF_ROM, PBUF_REF, PBUF_POOL, (pbuf_type)0x10280};
    for (size_t a = 0; a < sizeof(layers)/sizeof(layers[0]); ++a)
        for (size_t b = 0; b < sizeof(lengths)/sizeof(lengths[0]); ++b)
            for (size_t c = 0; c < sizeof(types)/sizeof(types[0]); ++c)
                assert(invoke_a(layers[a], lengths[b], types[c], &object) == &object);
    assert(memcmp(original, &object, sizeof(object)) == 0);
    assert(atomic_load(&s_real_calls) == 100);
    assert(atomic_load(&s_record_additions) == 0);
    assert(atomic_load(&s_critical_entries) == 0 && atomic_load(&s_rom_calls) == 0);
    assert(inspect_table().total == 0);
}

static void test_null_forwarding_and_sizes(void) {
    struct { pbuf_layer layer; u16_t length; pbuf_type type; uint32_t payload_bytes; } cases[] = {
        {PBUF_TRANSPORT, 1440, PBUF_RAM, 1496},
        {PBUF_RAW, 0, PBUF_RAM, 0},
        {(pbuf_layer)3, 1, PBUF_RAM, 8},
        {(pbuf_layer)0x10003, 3, PBUF_RAM, 8},
        {PBUF_RAW, UINT16_MAX, PBUF_RAM, 65536},
        {PBUF_TRANSPORT, 1440, PBUF_ROM, 0},
        {PBUF_TRANSPORT, UINT16_MAX, PBUF_REF, 0},
        {PBUF_TRANSPORT, 1440, PBUF_POOL, 0},
        {PBUF_TRANSPORT, 1440, (pbuf_type)0x10280, 0},
    };
    for (size_t i = 0; i < sizeof(cases)/sizeof(cases[0]); ++i) {
        reset_case();
        assert(invoke_a(cases[i].layer, cases[i].length, cases[i].type, NULL) == NULL);
        assert(atomic_load(&s_real_calls) == 1 && atomic_load(&s_record_additions) == 1);
        assert(atomic_load(&s_critical_entries) == 1 && atomic_load(&s_rom_calls) == 0);
        pbuf_failure_record_t snapshot = inspect_table();
        assert(snapshot.total == 1 && snapshot.used == 1 && snapshot.overflow == 0);
        const pbuf_failure_key_t *key = &snapshot.entries[0].key;
        assert(key->layer == (uint32_t)cases[i].layer && key->length == cases[i].length);
        assert(key->type == (uint32_t)cases[i].type && key->caller_pc != 0);
        uint32_t expected = cases[i].type == PBUF_RAM ?
            (uint32_t)LWIP_MEM_ALIGN_SIZE(sizeof(struct pbuf)) + cases[i].payload_bytes : 0;
        assert(key->allocation_bytes == expected);
    }
}

static void test_distinct_real_callers(void) {
    reset_case();
    invoke_a(PBUF_TRANSPORT, 1440, PBUF_RAM, NULL);
    invoke_b(PBUF_TRANSPORT, 1440, PBUF_RAM, NULL);
    pbuf_failure_record_t snapshot = inspect_table();
    assert(snapshot.total == 2 && snapshot.used == 2);
    assert(snapshot.entries[0].key.caller_pc != snapshot.entries[1].key.caller_pc);
}

static void inject_failure_after_snapshot(void) {
    invoke_a(PBUF_TRANSPORT, 1440, PBUF_RAM, NULL);
}

static void test_dump_and_snapshot(void) {
    reset_case();
    dump();
    assert(atomic_load(&s_snapshots) == 1 && atomic_load(&s_rom_calls) == 1);
    assert(strstr(s_capture, "SUMMARY total=0 overflow=0 used=0 saturated=0 table_bytes=128 "));
    reset_case();
    invoke_a(PBUF_TRANSPORT, 1440, PBUF_RAM, NULL);
    s_first_print_hook = inject_failure_after_snapshot;
    dump();
    assert(inspect_table().total == 2);
    assert(strstr(s_capture, "SUMMARY total=1 overflow=0 used=1 saturated=0 "));
    assert(strstr(s_capture, " count=1 saturated=0\n"));
    assert(!strstr(s_capture, " count=2 "));
    assert(atomic_load(&s_snapshots) == 1 && atomic_load(&s_rom_calls) == 2);
}

static atomic_bool s_start;
static void *worker(void *unused) {
    (void)unused;
    while (!atomic_load(&s_start)) sched_yield();
    for (unsigned i = 0; i < 1000; ++i) invoke_a(PBUF_TRANSPORT, 1440, PBUF_RAM, NULL);
    return NULL;
}

static void test_concurrent_forwarding_and_dump(void) {
    reset_case();
    pthread_t threads[2];
    atomic_store(&s_start, false);
    for (unsigned i = 0; i < 2; ++i) assert(pthread_create(&threads[i], NULL, worker, NULL) == 0);
    atomic_store(&s_start, true);
    for (unsigned i = 0; i < 20; ++i) dump();
    for (unsigned i = 0; i < 2; ++i) assert(pthread_join(threads[i], NULL) == 0);
    pbuf_failure_record_t snapshot = inspect_table();
    assert(snapshot.total == 2000 && snapshot.used == 1 && snapshot.overflow == 0);
    assert(snapshot.entries[0].count == 2000 && snapshot.saturated == 0);
    assert(atomic_load(&s_real_calls) == 2000 && atomic_load(&s_record_additions) == 2000);
    assert(atomic_load(&s_probe_heap_calls) == 0 && atomic_load(&s_normal_lock_entries) == 0);
}

int main(void) {
    _Static_assert(PBUF_RAM == 0x280 && PBUF_POOL == 0x182, "Use complete public SDK enum values");
    assert(esp_cpu_process_stack_pc(0x80001234u) == 0x40001231u);
    assert(esp_cpu_process_stack_pc(0xc0001234u) == 0x40001231u);
    assert(esp_cpu_process_stack_pc(0x40001234u) == 0x40001231u);
    test_success_forwarding();
    test_null_forwarding_and_sizes();
    test_distinct_real_callers();
    test_dump_and_snapshot();
    test_concurrent_forwarding_and_dump();
    printf("PASS pbuf wrapper: forwarding100 NULL9 caller-PC snapshot/concurrency; host_pbuf_bytes=%zu host_mem_size_bytes=%zu host_lock_bytes=%zu table_bytes=%zu\n",
           sizeof(struct pbuf), sizeof(mem_size_t), sizeof(s_pbuf_failure_lock), sizeof(s_pbuf_failures));
    return 0;
}
