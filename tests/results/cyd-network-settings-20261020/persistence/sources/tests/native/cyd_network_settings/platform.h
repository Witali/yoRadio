#pragma once
#define _GNU_SOURCE
#include <assert.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define CHECK(condition, marker) do { if (!(condition)) { \
    fprintf(stderr, "SEMANTIC_FAILURE:%s:%u\n", marker, __LINE__); exit(80); \
} } while (0)
typedef int esp_err_t;
#define ESP_OK 0
#define ESP_FAIL (-1)
#define ESP_ERR_NO_MEM 0x101
#define ESP_ERR_INVALID_ARG 0x102
#define ESP_ERR_INVALID_STATE 0x103
#define ESP_ERR_TIMEOUT 0x107
#define ESP_ERR_NVS_NOT_FOUND 0x1102
#define ESP_ERR_NVS_TYPE_MISMATCH 0x1103
#define ESP_ERR_NVS_INVALID_LENGTH 0x110c
#define pdTRUE 1
#define pdFALSE 0
#define pdMS_TO_TICKS(value) (value)
typedef pthread_mutex_t portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED PTHREAD_MUTEX_INITIALIZER
#define portENTER_CRITICAL(lock) CHECK(!pthread_mutex_lock(lock), "snapshot_lock")
#define portEXIT_CRITICAL(lock) CHECK(!pthread_mutex_unlock(lock), "snapshot_unlock")
typedef struct host_semaphore { pthread_mutex_t mutex; atomic_bool held; } *SemaphoreHandle_t;
static pthread_mutex_t registry_lock = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t registry_cond = PTHREAD_COND_INITIALIZER;
static SemaphoreHandle_t semaphores[16];
static unsigned semaphore_count;
static atomic_uint semaphore_creates, semaphore_deletes, semaphore_takes;
static atomic_bool fail_mutex;
static _Atomic(SemaphoreHandle_t) forced_timeout;
static bool barrier_creation;
static pthread_barrier_t creation_barrier;

static SemaphoreHandle_t xSemaphoreCreateMutex(void) {
    atomic_fetch_add(&semaphore_creates, 1);
    if (atomic_load(&fail_mutex)) return NULL;
    SemaphoreHandle_t lock = calloc(1, sizeof(*lock));
    CHECK(lock && !pthread_mutex_init(&lock->mutex, NULL), "fixture_mutex_create");
    atomic_init(&lock->held, false);
    CHECK(!pthread_mutex_lock(&registry_lock), "registry_lock");
    CHECK(semaphore_count < 16, "fixture_mutex_capacity");
    semaphores[semaphore_count++] = lock;
    CHECK(!pthread_mutex_unlock(&registry_lock), "registry_unlock");
    if (barrier_creation) {
        int result = pthread_barrier_wait(&creation_barrier);
        CHECK(result == 0 || result == PTHREAD_BARRIER_SERIAL_THREAD, "creation_barrier");
    }
    return lock;
}
static int xSemaphoreTake(SemaphoreHandle_t lock, unsigned ticks) {
    CHECK(lock && ticks == 100U, "finite_writer_admission_budget");
    CHECK(!pthread_mutex_lock(&registry_lock), "registry_lock");
    atomic_fetch_add(&semaphore_takes, 1);
    pthread_cond_broadcast(&registry_cond);
    CHECK(!pthread_mutex_unlock(&registry_lock), "registry_unlock");
    if (lock == atomic_load(&forced_timeout)) return pdFALSE;
    CHECK(!pthread_mutex_lock(&lock->mutex), "writer_lock");
    CHECK(!atomic_exchange(&lock->held, true), "writer_lock_exclusive");
    return pdTRUE;
}
static void xSemaphoreGive(SemaphoreHandle_t lock) {
    CHECK(atomic_exchange(&lock->held, false), "writer_admission_required");
    CHECK(!pthread_mutex_unlock(&lock->mutex), "writer_unlock");
}
static void vSemaphoreDelete(SemaphoreHandle_t lock) {
    CHECK(!atomic_load(&lock->held), "never_delete_held_mutex");
    CHECK(!pthread_mutex_lock(&registry_lock), "registry_lock");
    for (unsigned index = 0; index < semaphore_count; ++index)
        if (semaphores[index] == lock) semaphores[index] = NULL;
    CHECK(!pthread_mutex_unlock(&registry_lock), "registry_unlock");
    CHECK(!pthread_mutex_destroy(&lock->mutex), "fixture_mutex_destroy");
    atomic_fetch_add(&semaphore_deletes, 1);
    free(lock);
}
static void cleanup_semaphores(void) {
    for (unsigned index = 0; index < semaphore_count; ++index)
        if (semaphores[index]) vSemaphoreDelete(semaphores[index]);
}

typedef unsigned nvs_handle_t;
#define NVS_READONLY 0
#define NVS_READWRITE 1
static uint8_t flash_record[64], staged_record[64];
static size_t flash_size, staged_size;
static bool flash_present, wrong_type, successful_short_read;
static unsigned fail_get_at;
static esp_err_t fail_open, fail_set, fail_commit;
static atomic_uint nvs_opens, nvs_closes, nvs_reads, nvs_sets, nvs_commits, nvs_live;
static pthread_mutex_t commit_lock = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t commit_cond = PTHREAD_COND_INITIALIZER;
static bool hold_commit, commit_waiting, release_commit;

static esp_err_t nvs_open(const char *name, int mode, nvs_handle_t *out) {
    CHECK(!strcmp(name, "native_network") && (mode == NVS_READONLY || mode == NVS_READWRITE),
          "dedicated_namespace");
    atomic_fetch_add(&nvs_opens, 1);
    if (fail_open) return fail_open;
    if (mode == NVS_READONLY && !flash_present) return ESP_ERR_NVS_NOT_FOUND;
    CHECK(atomic_fetch_add(&nvs_live, 1) == 0, "nvs_writers_serialized");
    *out = 42;
    staged_size = 0;
    return ESP_OK;
}
static void nvs_close(nvs_handle_t handle) {
    CHECK(handle == 42 && atomic_fetch_sub(&nvs_live, 1) == 1, "nvs_handle_closed_once");
    atomic_fetch_add(&nvs_closes, 1);
    staged_size = 0;
}
static esp_err_t nvs_get_blob(nvs_handle_t handle, const char *key, void *out, size_t *size) {
    CHECK(handle == 42 && !strcmp(key, "cfg") && atomic_load(&nvs_live) == 1,
          "nvs_blob_read_contract");
    unsigned call = atomic_fetch_add(&nvs_reads, 1) + 1U;
    if (call == fail_get_at) return ESP_FAIL;
    if (!flash_present) return ESP_ERR_NVS_NOT_FOUND;
    if (wrong_type) return ESP_ERR_NVS_TYPE_MISMATCH;
    if (!out) { *size = flash_size; return ESP_OK; }
    if (*size < flash_size) { *size = flash_size; return ESP_ERR_NVS_INVALID_LENGTH; }
    size_t bytes = successful_short_read ? flash_size - 1U : flash_size;
    memcpy(out, flash_record, bytes); *size = bytes;
    return ESP_OK;
}
static esp_err_t nvs_set_blob(nvs_handle_t handle, const char *key, const void *data, size_t size) {
    CHECK(handle == 42 && !strcmp(key, "cfg") && size <= sizeof(staged_record) &&
          atomic_load(&nvs_live) == 1, "nvs_blob_set_contract");
    atomic_fetch_add(&nvs_sets, 1);
    if (fail_set) return fail_set;
    memcpy(staged_record, data, size); staged_size = size;
    return ESP_OK;
}
static esp_err_t nvs_commit(nvs_handle_t handle) {
    CHECK(handle == 42 && staged_size && atomic_load(&nvs_live) == 1, "nvs_commit_contract");
    atomic_fetch_add(&nvs_commits, 1);
    CHECK(!pthread_mutex_lock(&commit_lock), "commit_barrier_lock");
    if (hold_commit) {
        commit_waiting = true;
        pthread_cond_broadcast(&commit_cond);
        while (!release_commit) pthread_cond_wait(&commit_cond, &commit_lock);
    }
    CHECK(!pthread_mutex_unlock(&commit_lock), "commit_barrier_unlock");
    if (fail_commit) return fail_commit;
    memcpy(flash_record, staged_record, staged_size);
    flash_size = staged_size; flash_present = true;
    return ESP_OK;
}
