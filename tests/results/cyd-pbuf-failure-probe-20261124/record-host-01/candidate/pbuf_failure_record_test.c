/* Portable recorder contract and real external-mutex tests.
 * SPDX-License-Identifier: Apache-2.0 */
#include <errno.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "pbuf_failure_record.h"

#define CHECK(condition) do { if (!(condition)) { \
    fprintf(stderr, "CHECK failed at line %d: %s\n", __LINE__, #condition); exit(42); \
} } while (0)

static unsigned groups;
static pbuf_failure_record_t shared;
static pthread_mutex_t external_lock = PTHREAD_MUTEX_INITIALIZER;
static atomic_uint finished;
enum { UPDATES = 20000, WRITERS = 5 };

static pbuf_failure_key_t key(uint32_t caller) {
    pbuf_failure_key_t result = {54, 0x280, 1440, 1512, caller};
    return result;
}

static void complete(const char *name) {
    ++groups;
    printf("PASS %s\n", name);
}

static void empty_and_snapshot(void) {
    pbuf_failure_record_t table = {0}, copy;
    memset(&copy, 0xa5, sizeof(copy));
    pbuf_failure_record_snapshot(&table, &copy);
    CHECK(sizeof(table) == 128 && memcmp(&table, &copy, sizeof(table)) == 0);
    CHECK(!copy.total && !copy.overflow && !copy.used && !copy.saturated);
    complete("empty 128-byte table and caller-owned snapshot");
}

static void exact_fields(void) {
    pbuf_failure_key_t original = key(0xf00d1234);
    pbuf_failure_key_t variants[] = {original, original, original, original, original};
    variants[0].layer ^= 0x10000;
    variants[1].type ^= 0x100; /* Same low byte: catches accidental enum narrowing. */
    variants[2].length ^= 0x10000;
    variants[3].allocation_bytes ^= 0x10000;
    variants[4].caller_pc ^= 0x80000000;
    for (unsigned i = 0; i < 5; ++i) {
        pbuf_failure_record_t table = {0};
        pbuf_failure_record_add(&table, &original);
        pbuf_failure_record_add(&table, &variants[i]);
        CHECK(table.used == 2 && table.total == 2 && table.overflow == 0);
        CHECK(pbuf_failure_record_key_equal(&table.entries[0].key, &original));
        CHECK(pbuf_failure_record_key_equal(&table.entries[1].key, &variants[i]));
    }
    pbuf_failure_record_t table = {0};
    pbuf_failure_record_add(&table, &original);
    original.type = 0x182;
    pbuf_failure_record_add(&table, &original);
    CHECK(table.entries[0].key.type == 0x280 && table.entries[1].key.type == 0x182);
    pbuf_failure_record_add(&table, &original);
    CHECK(table.total == 3 && table.used == 2 && table.entries[1].count == 2);
    CHECK(!table.saturated && !table.entries[1].saturated);
    complete("all five complete uint32 fields and pbuf types 0x280/0x182");
}

static void fill(pbuf_failure_record_t *table) {
    for (uint32_t i = 0; i < PBUF_FAILURE_RECORD_SLOTS; ++i) {
        pbuf_failure_key_t value = key(0x400d0000 + i);
        pbuf_failure_record_add(table, &value);
    }
}

static void full_table(void) {
    pbuf_failure_record_t table = {0}, before, snapshot;
    fill(&table);
    CHECK(table.used == 4 && table.total == 4 && !table.overflow);
    before = table;
    pbuf_failure_key_t missing = key(0x50000000);
    pbuf_failure_record_add(&table, &missing);
    pbuf_failure_record_add(&table, &missing);
    CHECK(table.used == 4 && table.total == 6 && table.overflow == 2);
    CHECK(memcmp(table.entries, before.entries, sizeof(table.entries)) == 0);
    pbuf_failure_key_t present = before.entries[3].key;
    pbuf_failure_record_add(&table, &present);
    CHECK(table.entries[3].count == 2 && table.total == 7 && table.overflow == 2);
    pbuf_failure_record_snapshot(&table, &snapshot);
    CHECK(memcmp(&table, &snapshot, sizeof(table)) == 0);
    snapshot.entries[0].count = 123;
    CHECK(table.entries[0].count == 1);
    complete("four slots, unmatched overflow, matches while full and independent snapshot");
}

static void saturation(void) {
    pbuf_failure_record_t table = {0};
    pbuf_failure_key_t value = key(0x400d0000);
    pbuf_failure_record_add(&table, &value);
    table.total = table.entries[0].count = UINT32_MAX - 1;
    pbuf_failure_record_add(&table, &value);
    CHECK(table.total == UINT32_MAX && table.entries[0].count == UINT32_MAX);
    CHECK(!table.saturated && !table.entries[0].saturated);
    pbuf_failure_record_add(&table, &value);
    CHECK(table.total == UINT32_MAX && table.entries[0].count == UINT32_MAX);
    CHECK(table.entries[0].saturated == 1);
    CHECK(table.saturated == (PBUF_FAILURE_RECORD_TOTAL_SATURATED | PBUF_FAILURE_RECORD_ENTRY_SATURATED));

    table = (pbuf_failure_record_t){0};
    fill(&table);
    value = key(0xffffffff);
    table.total = table.overflow = UINT32_MAX - 1;
    pbuf_failure_record_add(&table, &value);
    CHECK(table.total == UINT32_MAX && table.overflow == UINT32_MAX && !table.saturated);
    pbuf_failure_record_add(&table, &value);
    CHECK(table.total == UINT32_MAX && table.overflow == UINT32_MAX);
    CHECK(table.saturated == (PBUF_FAILURE_RECORD_TOTAL_SATURATED | PBUF_FAILURE_RECORD_OVERFLOW_SATURATED));

    table = (pbuf_failure_record_t){0};
    value = key(1);
    pbuf_failure_record_add(&table, &value);
    table.total = UINT32_MAX;
    pbuf_failure_record_add(&table, &value);
    CHECK(table.total == UINT32_MAX && table.entries[0].count == 2);
    CHECK(table.saturated == PBUF_FAILURE_RECORD_TOTAL_SATURATED && !table.entries[0].saturated);
    complete("independent total/entry/overflow saturation with explicit loss flags");
}

static unsigned real_calls;
static void *real_result;
static pbuf_failure_key_t real_arguments;

static void *real_allocate(uint32_t layer, uint32_t length, uint32_t type) {
    ++real_calls;
    real_arguments.layer = layer;
    real_arguments.length = length;
    real_arguments.type = type;
    errno = real_result ? EAGAIN : ENOMEM;
    return real_result;
}

/* A host forwarding seam, not the production wrapper owned by integration. */
static void *forward(pbuf_failure_record_t *table, const pbuf_failure_key_t *value) {
    void *result = real_allocate(value->layer, value->length, value->type);
    if (result == NULL) {
        CHECK(pthread_mutex_lock(&external_lock) == 0);
        pbuf_failure_record_add(table, value);
        CHECK(pthread_mutex_unlock(&external_lock) == 0);
    }
    return result;
}

static void forwarding(void) {
    pbuf_failure_record_t table = {0}, before = table;
    pbuf_failure_key_t value = key(0x400d4321);
    unsigned char storage;
    real_result = &storage;
    CHECK(forward(&table, &value) == &storage && real_calls == 1 && errno == EAGAIN);
    CHECK(memcmp(&table, &before, sizeof(table)) == 0);
    CHECK(real_arguments.layer == value.layer && real_arguments.length == value.length && real_arguments.type == value.type);
    real_result = NULL;
    CHECK(forward(&table, &value) == NULL && real_calls == 2 && errno == ENOMEM);
    CHECK(table.total == 1 && table.entries[0].count == 1);
    CHECK(pbuf_failure_record_key_equal(&table.entries[0].key, &value));
    complete("real call once, unchanged arguments/result/errno and NULL-only recording");
}

static void invariant(const pbuf_failure_record_t *snapshot) {
    CHECK(snapshot->used == 4 && !snapshot->saturated);
    uint32_t sum = snapshot->overflow;
    for (unsigned i = 0; i < PBUF_FAILURE_RECORD_SLOTS; ++i) {
        CHECK(!snapshot->entries[i].saturated && snapshot->entries[i].key.caller_pc == 0x400d0000 + i);
        sum += snapshot->entries[i].count;
    }
    CHECK(sum == snapshot->total);
}

static void *update(void *argument) {
    uintptr_t index = (uintptr_t)argument;
    pbuf_failure_key_t value = key(index < 4 ? 0x400d0000 + (uint32_t)index : 0x50000000);
    for (unsigned i = 0; i < UPDATES; ++i) {
        CHECK(pthread_mutex_lock(&external_lock) == 0);
        pbuf_failure_record_add(&shared, &value);
        CHECK(pthread_mutex_unlock(&external_lock) == 0);
    }
    atomic_fetch_add_explicit(&finished, 1, memory_order_release);
    return NULL;
}

static void *observe(void *argument) {
    (void)argument;
    pbuf_failure_record_t previous = {0};
    do {
        pbuf_failure_record_t snapshot;
        CHECK(pthread_mutex_lock(&external_lock) == 0);
        pbuf_failure_record_snapshot(&shared, &snapshot);
        CHECK(pthread_mutex_unlock(&external_lock) == 0);
        invariant(&snapshot);
        CHECK(snapshot.total >= previous.total && snapshot.overflow >= previous.overflow);
        for (unsigned i = 0; i < PBUF_FAILURE_RECORD_SLOTS; ++i) CHECK(snapshot.entries[i].count >= previous.entries[i].count);
        previous = snapshot;
    } while (atomic_load_explicit(&finished, memory_order_acquire) != WRITERS);
    return NULL;
}

static void concurrency(void) {
    fill(&shared);
    pthread_t workers[WRITERS], reader;
    CHECK(pthread_create(&reader, NULL, observe, NULL) == 0);
    for (uintptr_t i = 0; i < WRITERS; ++i) CHECK(pthread_create(&workers[i], NULL, update, (void *)i) == 0);
    for (unsigned i = 0; i < WRITERS; ++i) CHECK(pthread_join(workers[i], NULL) == 0);
    CHECK(pthread_join(reader, NULL) == 0);
    invariant(&shared);
    CHECK(shared.total == 4 + WRITERS * UPDATES && shared.overflow == UPDATES);
    for (unsigned i = 0; i < PBUF_FAILURE_RECORD_SLOTS; ++i) CHECK(shared.entries[i].count == 1 + UPDATES);
    CHECK(pthread_mutex_destroy(&external_lock) == 0);
    complete("100000 updates and concurrent coherent snapshots under actual external mutex");
}

int main(void) {
    empty_and_snapshot();
    exact_fields();
    full_table();
    saturation();
    forwarding();
    concurrency();
    CHECK(groups == 6);
    printf("PASS %u pbuf recorder groups; table=%zu bytes; slots=%u\n", groups, sizeof(pbuf_failure_record_t), PBUF_FAILURE_RECORD_SLOTS);
    return 0;
}
