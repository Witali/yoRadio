#define _GNU_SOURCE
#include <assert.h>
#include <errno.h>
#include <pthread.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
#include "native_wifi_file.h"

typedef int esp_err_t;
#define ESP_OK 0
#define ESP_FAIL (-1)
#define ESP_ERR_NO_MEM 0x101
#define ESP_ERR_INVALID_ARG 0x102
#define ESP_ERR_INVALID_STATE 0x103
#define ESP_ERR_INVALID_SIZE 0x104
#define ESP_ERR_TIMEOUT 0x107
#define ESP_RETURN_ON_FALSE(condition,error,...) do {if (!(condition)) return (error);} while (0)
#define ESP_RETURN_ON_ERROR(expression,...) do {int result_ = (expression); if (result_ != ESP_OK) return result_;} while (0)
#define pdTRUE 1
#define pdMS_TO_TICKS(ms) (ms)
#define WIFI_MAX_FILE_BYTES 800U
#define WIFI_MAX_FILE_NETWORKS 5U
typedef pthread_mutex_t *SemaphoreHandle_t;
typedef struct {struct {uint8_t ssid[32],password[64];}sta;} wifi_config_t;
static wifi_config_t s_station_config;
static SemaphoreHandle_t s_wifi_save_lock;
static pthread_mutex_t mutexes[] = {PTHREAD_MUTEX_INITIALIZER, PTHREAD_MUTEX_INITIALIZER};
static unsigned create_calls, created_mutexes, fail_create_at;
static SemaphoreHandle_t timeout_lock;
static bool pause_writer, writer_paused, release_writer;
static unsigned concurrent_save_attempts;
static pthread_mutex_t pause_mutex = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t pause_cond = PTHREAD_COND_INITIALIZER;
static bool random_zero;
static unsigned random_calls;
static void esp_fill_random(void *data, size_t size) {
    ++random_calls;
    memset(data, random_zero ? 0 : 0x39, size);
}
static SemaphoreHandle_t xSemaphoreCreateMutex(void) {
    if (++create_calls == fail_create_at) return NULL;
    assert(created_mutexes < sizeof(mutexes) / sizeof(mutexes[0]));
    return &mutexes[created_mutexes++];
}
static int xSemaphoreTake(SemaphoreHandle_t lock, unsigned timeout) {
    assert(timeout == 1000);
    if (lock == timeout_lock) return 0;
    if (pause_writer && lock == s_wifi_save_lock) {
        pthread_mutex_lock(&pause_mutex); ++concurrent_save_attempts;
        pthread_cond_broadcast(&pause_cond); pthread_mutex_unlock(&pause_mutex);
    }
    return pthread_mutex_lock(lock) == 0;
}
static void xSemaphoreGive(SemaphoreHandle_t lock) {assert(!pthread_mutex_unlock(lock));}

enum fault {NONE, OPEN_TEMP, WRITE_SHORT, FLUSH, CLOSE_FILE, LIVE_STAT, TEMP_STAT,
            BACKUP_STAT, REMOVE_BACKUP, RENAME_LIVE, RENAME_TEMP, RENAME_ROLLBACK,
            BOTH_RENAMES, CLEANUP_BACKUP};
static enum fault fault;
static char root[768];
static unsigned cases, open_calls, write_calls, flush_calls, close_calls;
static const char *live = "/spiffs/data/wifi.csv";
static const char *temporary = "/spiffs/data/wifi.csv.tmp";
static const char *backup = "/spiffs/data/wifi.csv.bak";
static const char *old_wifi = "old-fixture\told-fixture\n";
static const char *new_wifi = "new-fixture\tnew-fixture\n";

static void mapped_path(const char *name, char *path, size_t capacity) {
    assert(!strncmp(name, "/spiffs/", 8));
    int size = snprintf(path, capacity, "%s/%s", root, name + 8);
    assert(size > 0 && (size_t)size < capacity);
}
static FILE *mapped_open(const char *name, const char *mode) {
    ++open_calls;
    if (fault == OPEN_TEMP && !strcmp(name, temporary) && strchr(mode, 'w')) {
        errno = ENOSPC; return NULL;
    }
    char path[1024]; mapped_path(name, path, sizeof(path)); return fopen(path, mode);
}
static size_t mapped_write(const void *data, size_t width, size_t count, FILE *file) {
    ++write_calls;
    if (pause_writer) {
        assert(!pthread_mutex_lock(&pause_mutex)); writer_paused = true;
        pthread_cond_broadcast(&pause_cond);
        while (!release_writer) pthread_cond_wait(&pause_cond, &pause_mutex);
        pthread_mutex_unlock(&pause_mutex);
    }
    if (fault == WRITE_SHORT) return fwrite(data, width, count / 2U, file);
    return fwrite(data, width, count, file);
}
static int mapped_flush(FILE *file) {
    ++flush_calls;
    int result = fflush(file);
    if (fault == FLUSH) {errno = EIO; return EOF;}
    return result;
}
static int mapped_close(FILE *file) {
    ++close_calls;
    int result = fclose(file);
    if (fault == CLOSE_FILE) {errno = EIO; return EOF;}
    return result;
}
static int mapped_stat(const char *name, struct stat *info) {
    if ((fault == LIVE_STAT && !strcmp(name, live)) ||
        (fault == TEMP_STAT && !strcmp(name, temporary)) ||
        (fault == BACKUP_STAT && !strcmp(name, backup))) {errno = EIO; return -1;}
    char path[1024]; mapped_path(name, path, sizeof(path)); return stat(path, info);
}
static int mapped_remove(const char *name) {
    if ((fault == REMOVE_BACKUP || fault == CLEANUP_BACKUP) && !strcmp(name, backup)) {
        // Distinguish a retained backup from the absent pre-publication name.
        char path[1024]; mapped_path(name, path, sizeof(path));
        if (fault == REMOVE_BACKUP || access(path, F_OK) == 0) {errno = EIO; return -1;}
    }
    char path[1024]; mapped_path(name, path, sizeof(path)); return remove(path);
}
static int mapped_rename(const char *from, const char *to) {
    if ((fault == RENAME_LIVE && !strcmp(from, live)) ||
        ((fault == RENAME_TEMP || fault == BOTH_RENAMES) && !strcmp(from, temporary)) ||
        ((fault == RENAME_ROLLBACK || fault == BOTH_RENAMES) && !strcmp(from, backup))) {
        errno = EIO; return -1;
    }
    char source[1024], target[1024];
    mapped_path(from, source, sizeof(source)); mapped_path(to, target, sizeof(target));
    if (access(target, F_OK) == 0) {errno = EEXIST; return -1;} // Real SPIFFS rename rule.
    return rename(source, target);
}
static size_t strlcpy(char *out, const char *text, size_t cap) {
    size_t size = strlen(text);
    if (cap) {size_t count = size < cap - 1U ? size : cap - 1U; memcpy(out, text, count); out[count] = 0;}
    return size;
}

#include "credential_line.h"
#define stat(...) mapped_stat(__VA_ARGS__)
#define remove(...) mapped_remove(__VA_ARGS__)
#define rename(...) mapped_rename(__VA_ARGS__)
#include "file_transaction.c"
#define fopen(...) mapped_open(__VA_ARGS__)
#define fwrite(...) mapped_write(__VA_ARGS__)
#define fflush(...) mapped_flush(__VA_ARGS__)
#define fclose(...) mapped_close(__VA_ARGS__)
#include "native_wifi_store.c"
#include "native_wifi_file.c"
#include "cyd-storage-production.inc"
#include "cyd-wifi-production.inc"
#undef fclose
#undef fflush
#undef fwrite
#undef fopen
#undef stat
#undef remove
#undef rename

static void put(const char *name, const void *data, size_t size) {
    char path[1024]; mapped_path(name, path, sizeof(path)); FILE *file = fopen(path, "wb");
    assert(file && fwrite(data, 1, size, file) == size && !fclose(file));
}
static void text(const char *name, const char *data) {put(name, data, strlen(data));}
static bool equals(const char *name, const char *expected) {
    char path[1024], data[1024]; mapped_path(name, path, sizeof(path)); FILE *file = fopen(path, "rb");
    if (!file) return false;
    size_t count = fread(data, 1, sizeof(data), file); assert(!ferror(file) && !fclose(file));
    return count == strlen(expected) && !memcmp(data, expected, count);
}
static bool exists(const char *name) {char path[1024]; mapped_path(name, path, sizeof(path)); return !access(path, F_OK);}
static void clear(void) {
    fault = NONE; timeout_lock = NULL; pause_writer = writer_paused = release_writer = false;
    const char *names[] = {live, temporary, backup};
    for (size_t index = 0; index < sizeof(names) / sizeof(names[0]); ++index) {
        char path[1024]; mapped_path(names[index], path, sizeof(path)); remove(path);
    }
    ++cases;
}
static void expect_read(bool accepted, const char *ssid, const char *password) {
    struct {uint64_t before; wifi_config_t config; uint64_t after;} guarded = {
        .before = UINT64_C(0x123456789abcdef0), .after = UINT64_C(0xfedcba9876543210)};
    memset(&guarded.config, 0xa5, sizeof(guarded.config)); wifi_config_t initial = guarded.config;
    assert(read_credentials(&guarded.config) == accepted);
    assert(guarded.before == UINT64_C(0x123456789abcdef0) && guarded.after == UINT64_C(0xfedcba9876543210));
    if (accepted) assert(!strcmp((char *)guarded.config.sta.ssid, ssid) && !strcmp((char *)guarded.config.sta.password, password));
    else assert(!memcmp(&guarded.config, &initial, sizeof(initial)));
}
static void reject(const void *data, size_t size) {
    clear(); text(live, old_wifi); unsigned before_open = open_calls, before_write = write_calls;
    assert(network_service_validate_credentials_file(data, size) != ESP_OK);
    assert(network_service_save_credentials_file(data, size) != ESP_OK);
    assert(equals(live, old_wifi) && open_calls == before_open && write_calls == before_write);
}
static void accept(const char *data, const char *ssid, const char *password) {
    clear(); text(live, old_wifi); wifi_config_t active = s_station_config;
    assert(network_service_validate_credentials_file((const uint8_t *)data, strlen(data)) == ESP_OK);
    assert(network_service_save_credentials_file((const uint8_t *)data, strlen(data)) == ESP_OK);
    assert(equals(live, data) && !exists(backup) && !exists(temporary));
    assert(!memcmp(&active, &s_station_config, sizeof(active))); expect_read(true, ssid, password);
}
static void *save_thread(void *argument) {
    const char *data = argument;
    assert(network_service_save_credentials_file((const uint8_t *)data, strlen(data)) == ESP_OK);
    return NULL;
}

static native_wifi_edit_t keep_profiles(const native_wifi_metadata_t *metadata) {
    native_wifi_edit_t edit = {0};
    memcpy(edit.revision, metadata->revision, sizeof(edit.revision));
    edit.count = metadata->count;
    for (size_t i = 0; i < edit.count; ++i)
        memcpy(edit.profiles[i].id, metadata->profiles[i].id, sizeof(edit.profiles[i].id));
    return edit;
}

static void metadata_cleared(const native_wifi_metadata_t *metadata) {
    const uint8_t zero[sizeof(*metadata)] = {0};
    assert(!memcmp(metadata, zero, sizeof(*metadata)));
}

static void private_metadata_cases(void) {
    clear();
    native_wifi_metadata_t metadata;
    assert(network_service_wifi_metadata(&metadata) == NATIVE_WIFI_OK && !metadata.count);
    const char *duplicates = "duplicate\tunique-secret-one\nduplicate\tunique-secret-two\n";
    assert(network_service_save_credentials_file((const uint8_t *)duplicates, strlen(duplicates)) == ESP_OK);
    wifi_config_t active = s_station_config;
    assert(network_service_wifi_metadata(&metadata) == NATIVE_WIFI_OK && metadata.count == 2);
    assert(!strcmp(metadata.profiles[0].ssid, "duplicate") && metadata.profiles[0].ssid_utf8);
    assert(strcmp(metadata.profiles[0].id, metadata.profiles[1].id));
    assert(!memmem(&metadata, sizeof(metadata), "unique-secret", strlen("unique-secret")));
    native_wifi_edit_t stale = keep_profiles(&metadata), edit = stale;
    edit.profiles[0] = stale.profiles[1];
    edit.profiles[1] = stale.profiles[0];
    edit.profiles[1].password_action = NATIVE_WIFI_PASSWORD_SET;
    edit.profiles[1].password_present = true; // Explicit empty means open.
    assert(network_service_wifi_edit(&edit) == NATIVE_WIFI_OK);
    assert(equals(live, "duplicate\tunique-secret-two\nduplicate\t\n"));
    assert(!memcmp(&active, &s_station_config, sizeof(active)));
    assert(network_service_wifi_edit(&stale) == NATIVE_WIFI_CONFLICT);
    assert(network_service_wifi_metadata(&metadata) == NATIVE_WIFI_OK);
    edit = keep_profiles(&metadata);
    edit.profiles[0].id[0] = 0; // A new row cannot KEEP a stored password.
    assert(network_service_wifi_edit(&edit) == NATIVE_WIFI_INVALID);
    edit = keep_profiles(&metadata);
    native_wifi_metadata_t before = metadata;
    fault = CLOSE_FILE;
    assert(network_service_wifi_metadata(&metadata) == NATIVE_WIFI_IO);
    metadata_cleared(&metadata);
    fault = NONE; timeout_lock = s_wifi_save_lock;
    assert(network_service_wifi_metadata(&metadata) == NATIVE_WIFI_BUSY);
    assert(network_service_wifi_edit(&edit) == NATIVE_WIFI_BUSY);
    metadata_cleared(&metadata);
    timeout_lock = NULL;
    edit.profiles[0].password_action = NATIVE_WIFI_PASSWORD_SET;
    edit.profiles[0].password_present = true;
    strcpy(edit.profiles[0].password, "new-request-key");
    fault = RENAME_TEMP;
    assert(network_service_wifi_edit(&edit) == NATIVE_WIFI_IO);
    fault = NONE;
    assert(network_service_wifi_metadata(&metadata) == NATIVE_WIFI_OK);
    assert(!strcmp(metadata.revision, before.revision));
    edit = keep_profiles(&metadata); edit.count = 0;
    fault = CLEANUP_BACKUP;
    assert(network_service_wifi_edit(&edit) == NATIVE_WIFI_OK);
    assert(equals(live, "") && exists(backup));
    fault = NONE;
    assert(network_service_wifi_metadata(&metadata) == NATIVE_WIFI_OK && !metadata.count);
    expect_read(false, NULL, NULL);
    assert(equals(live, "")); // Recovery must not resurrect the retained backup.
    clear(); text(live, "corrupt private file");
    assert(network_service_wifi_metadata(&metadata) == NATIVE_WIFI_INVALID_STORAGE);
    metadata_cleared(&metadata);
    const char legacy[] = "b\xff\tlegacy-key\n";
    assert(network_service_save_credentials_file((const uint8_t *)legacy, sizeof(legacy) - 1U) == ESP_OK);
    assert(network_service_wifi_metadata(&metadata) == NATIVE_WIFI_OK && metadata.count == 1 && !metadata.profiles[0].ssid_utf8);
    edit = keep_profiles(&metadata);
    assert(network_service_wifi_edit(&edit) == NATIVE_WIFI_OK && equals(live, legacy));
    native_wifi_erase(&edit, sizeof(edit));
    native_wifi_erase(&stale, sizeof(stale));
}

int main(int argc, char **argv) {
    assert(argc == 2); assert(strlen(argv[1]) < sizeof(root)); strcpy(root, argv[1]);
    char directory[1024]; snprintf(directory, sizeof(directory), "%s/data", root); assert(!mkdir(directory, 0700) || errno == EEXIST);
    memset(&s_station_config, 0x5a, sizeof(s_station_config));
    native_wifi_metadata_t unavailable;
    memset(&unavailable, 0xa6, sizeof(unavailable));
    assert(network_service_wifi_metadata(&unavailable) == NATIVE_WIFI_NOT_READY);
    metadata_cleared(&unavailable);
    assert(network_service_save_credentials_file((const uint8_t *)new_wifi, strlen(new_wifi)) == ESP_ERR_INVALID_STATE);
    fail_create_at = 1; assert(network_service_storage_init() == ESP_ERR_NO_MEM && !s_wifi_save_lock);
    fail_create_at = 3; assert(network_service_storage_init() == ESP_ERR_NO_MEM && !s_wifi_save_lock);
    fail_create_at = 0; random_zero = true;
    assert(network_service_storage_init() == ESP_FAIL && s_wifi_save_lock && !s_wifi_store.ready);
    random_zero = false; assert(network_service_storage_init() == ESP_OK && s_wifi_save_lock);
    unsigned allocated = create_calls; assert(network_service_storage_init() == ESP_OK && create_calls == allocated);
    assert(random_calls == 2);
    unsigned before_lock_open = open_calls;
    timeout_lock = s_wifi_save_lock;
    assert(network_service_wifi_metadata(&unavailable) == NATIVE_WIFI_BUSY);
    metadata_cleared(&unavailable);
    assert(open_calls == before_lock_open);
    timeout_lock = NULL;
    ++cases;

    accept(" allowed \t pass \r\nsecond\tsecond\n", " allowed ", " pass ");
    accept("\r\n\nfirst\t\r\nsecond\tsecond", "first", "");
    accept("last\tpassword", "last", "password");
    accept("last\tpassword\r", "last", "password");
    accept("a\t1\nb\t2\nc\t3\nd\t4\ne\t5\n", "a", "1");
    char ssid31[32], ssid32[33], pass63[64], pass64[65], row[256];
    memset(ssid31, 's', 31); ssid31[31] = 0; memset(ssid32, 's', 32); ssid32[32] = 0;
    memset(pass63, 'p', 63); pass63[63] = 0; memset(pass64, 'p', 64); pass64[64] = 0;
    snprintf(row, sizeof(row), "%s\t%s\n", ssid31, pass63); accept(row, ssid31, pass63);
    snprintf(row, sizeof(row), "%s\tpassword\n", ssid32); reject(row, strlen(row));
    snprintf(row, sizeof(row), "first\t%s\n", pass64); reject(row, strlen(row));
    const char *invalid[] = {"", "\n\r\n", "first", "\tpassword\n", "first\tpass\textra\n",
        "fir\rst\tpass\n", "first\tpa\rss\n", "first\tpass\rsecond\tpass\n",
        "a\t1\nb\t2\nc\t3\nd\t4\ne\t5\nf\t6\n", "valid\tpass\ninvalid\n"};
    for (size_t index = 0; index < sizeof(invalid) / sizeof(invalid[0]); ++index) reject(invalid[index], strlen(invalid[index]));
    const char nul[] = "valid\tpass\ninvalid\tpa\0ss\n"; reject(nul, sizeof(nul) - 1U);
    reject(NULL, 10); reject(new_wifi, 0); char oversized[801]; memset(oversized, 'x', sizeof(oversized));
    reject(oversized, 800); reject(oversized, 801); reject(oversized, SIZE_MAX);
    memset(oversized, '\n', 799); memcpy(oversized, "a\t1\n", 4); oversized[799] = 0; accept(oversized, "a", "1");

    clear(); text(live, old_wifi); assert(network_service_save_credentials("", "pass") == ESP_ERR_INVALID_ARG);
    assert(network_service_save_credentials(NULL, "pass") == ESP_ERR_INVALID_ARG);
    assert(network_service_save_credentials("ssid", NULL) == ESP_ERR_INVALID_ARG);
    assert(network_service_save_credentials(ssid32, "pass") == ESP_ERR_INVALID_ARG);
    assert(network_service_save_credentials("ssid", pass64) == ESP_ERR_INVALID_ARG);
    assert(network_service_save_credentials("first\nsecond\tpass", "pass") == ESP_ERR_INVALID_ARG);
    assert(network_service_save_credentials("ssid", "pass\nsecond\tpass") == ESP_ERR_INVALID_ARG);
    assert(equals(live, old_wifi));
    assert(network_service_save_credentials(ssid31, pass63) == ESP_OK);
    expect_read(true, ssid31, pass63);
    assert(network_service_save_credentials(" open ", "") == ESP_OK); expect_read(true, " open ", "");

    const enum fault failures[] = {OPEN_TEMP, WRITE_SHORT, FLUSH, CLOSE_FILE, LIVE_STAT,
        TEMP_STAT, REMOVE_BACKUP, RENAME_LIVE, RENAME_TEMP};
    for (size_t index = 0; index < sizeof(failures) / sizeof(failures[0]); ++index) {
        clear(); text(live, old_wifi); wifi_config_t active = s_station_config; fault = failures[index];
        assert(network_service_save_credentials_file((const uint8_t *)new_wifi, strlen(new_wifi)) == ESP_FAIL);
        assert(!memcmp(&active, &s_station_config, sizeof(active)) && equals(live, old_wifi));
        fault = NONE; expect_read(true, "old-fixture", "old-fixture");
        assert(network_service_save_credentials_file((const uint8_t *)new_wifi, strlen(new_wifi)) == ESP_OK);
    }
    clear(); text(live, old_wifi); timeout_lock = s_wifi_save_lock;
    assert(network_service_save_credentials_file((const uint8_t *)new_wifi, strlen(new_wifi)) == ESP_ERR_TIMEOUT && equals(live, old_wifi));
    timeout_lock = s_storage_lock;
    // Credential names now have their own owner; unrelated static/public file
    // contention cannot admit an interleaved credential transaction.
    assert(network_service_save_credentials_file((const uint8_t *)new_wifi, strlen(new_wifi)) == ESP_OK && equals(live, new_wifi));
    timeout_lock = NULL;

    clear(); text(live, old_wifi); fault = BOTH_RENAMES;
    assert(network_service_save_credentials_file((const uint8_t *)new_wifi, strlen(new_wifi)) == ESP_FAIL);
    assert(!exists(live) && equals(backup, old_wifi));
    expect_read(false, NULL, NULL); fault = NONE; expect_read(true, "old-fixture", "old-fixture");
    assert(equals(live, old_wifi) && !exists(backup));
    clear(); text(backup, old_wifi); fault = BACKUP_STAT; expect_read(false, NULL, NULL);
    assert(equals(backup, old_wifi)); fault = NONE; expect_read(true, "old-fixture", "old-fixture");
    clear(); text(backup, old_wifi); fault = RENAME_ROLLBACK; expect_read(false, NULL, NULL);
    fault = NONE; expect_read(true, "old-fixture", "old-fixture");
    clear(); text(live, old_wifi); fault = CLEANUP_BACKUP;
    assert(network_service_save_credentials_file((const uint8_t *)new_wifi, strlen(new_wifi)) == ESP_OK);
    assert(equals(live, new_wifi) && equals(backup, old_wifi)); fault = NONE; expect_read(true, "new-fixture", "new-fixture");
    assert(network_service_save_credentials("third", "pass") == ESP_OK && !exists(backup));
    clear(); text(live, old_wifi); text(backup, new_wifi); expect_read(true, "old-fixture", "old-fixture");
    clear(); text(live, old_wifi); fault = CLOSE_FILE; expect_read(false, NULL, NULL);
    fault = NONE; expect_read(true, "old-fixture", "old-fixture");

    clear(); text(live, old_wifi); pause_writer = true;
    pthread_t first, second;
    assert(!pthread_create(&first, NULL, save_thread, (void *)new_wifi));
    pthread_mutex_lock(&pause_mutex); while (!writer_paused) pthread_cond_wait(&pause_cond, &pause_mutex);
    pthread_mutex_unlock(&pause_mutex);
    assert(!pthread_create(&second, NULL, save_thread, (void *)"second-fixture\tsecond-fixture\n"));
    pthread_mutex_lock(&pause_mutex);
    while (concurrent_save_attempts < 2U) pthread_cond_wait(&pause_cond, &pause_mutex);
    release_writer = true; pthread_cond_broadcast(&pause_cond); pthread_mutex_unlock(&pause_mutex);
    assert(!pthread_join(first, NULL) && !pthread_join(second, NULL));
    assert(equals(live, "second-fixture\tsecond-fixture\n") && !exists(backup) && !exists(temporary));
    assert(write_calls && flush_calls && close_calls);
    private_metadata_cases();
    printf("PASS CYD Wi-Fi storage: %u fixture groups; bounded full-file/field validation, first-valid/whitespace, preserved active config, OOM/locks, stdio/rename/rollback/recovery faults, serialized concurrent saves\n", cases);
    return 0;
}
