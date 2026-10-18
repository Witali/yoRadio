#define _POSIX_C_SOURCE 200809L
#include "native_wifi_store.h"
#include "native_wifi_file.h"
#include "file_transaction.h"

#include <assert.h>
#include <errno.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

enum fault { NONE, OPEN_TEMP, SHORT_WRITE, FLUSH, CLOSE_TEMP, READ_ERROR,
             CLOSE_LIVE, REMOVE_BACKUP, RENAME_OLD, RENAME_NEW, ROLLBACK,
             ALLOCATE };
static enum fault fault;
static unsigned passed, publishes, commits, reads, allocations, erased;
static bool installed, expect_workspace;
static void *workspace;
static size_t workspace_size;
static char directory[] = "/tmp/native-wifi-store-XXXXXX";
static char live[128], temporary[128], backup[128];
static FILE *temp_file, *live_file;

FILE *__real_fopen(const char *, const char *);
size_t __real_fwrite(const void *, size_t, size_t, FILE *);
size_t __real_fread(void *, size_t, size_t, FILE *);
int __real_fflush(FILE *);
int __real_fclose(FILE *);
int __real_ferror(FILE *);
int __real_rename(const char *, const char *);
int __real_remove(const char *);
void *__real_calloc(size_t, size_t);
void __real_free(void *);

FILE *__wrap_fopen(const char *path, const char *mode) {
    if (!strcmp(path, temporary) && fault == OPEN_TEMP) { errno = EIO; return NULL; }
    FILE *file = __real_fopen(path, mode);
    if (!strcmp(path, temporary)) temp_file = file;
    if (!strcmp(path, live)) live_file = file;
    return file;
}
size_t __wrap_fwrite(const void *p, size_t size, size_t count, FILE *file) {
    if (file == temp_file && fault == SHORT_WRITE)
        return __real_fwrite(p, size, count ? count - 1U : 0, file);
    return __real_fwrite(p, size, count, file);
}
size_t __wrap_fread(void *p, size_t size, size_t count, FILE *file) {
    if (file == live_file && fault == READ_ERROR) return 0;
    return __real_fread(p, size, count, file);
}
int __wrap_ferror(FILE *file) {
    return file == live_file && fault == READ_ERROR ? 1 : __real_ferror(file);
}
int __wrap_fflush(FILE *file) {
    int result = __real_fflush(file);
    return file == temp_file && fault == FLUSH ? EOF : result;
}
int __wrap_fclose(FILE *file) {
    bool fail = (file == temp_file && fault == CLOSE_TEMP) ||
                (file == live_file && fault == CLOSE_LIVE);
    if (file == temp_file) temp_file = NULL;
    if (file == live_file) live_file = NULL;
    int result = __real_fclose(file);
    return fail ? EOF : result;
}
int __wrap_remove(const char *path) {
    if (!strcmp(path, backup) && fault == REMOVE_BACKUP && !installed) {
        errno = EIO; return -1;
    }
    return __real_remove(path);
}
int __wrap_rename(const char *from, const char *to) {
    if ((!strcmp(from, live) && fault == RENAME_OLD) ||
        (!strcmp(from, temporary) && (fault == RENAME_NEW || fault == ROLLBACK)) ||
        (!strcmp(from, backup) && fault == ROLLBACK)) { errno = EIO; return -1; }
    int result = __real_rename(from, to);
    if (!result && !strcmp(from, temporary)) installed = true;
    return result;
}
void *__wrap_calloc(size_t count, size_t size) {
    if (expect_workspace && fault == ALLOCATE) return NULL;
    void *p = __real_calloc(count, size);
    if (expect_workspace) {
        assert(!workspace); workspace = p; workspace_size = count * size;
        if (p) ++allocations;
    }
    return p;
}
void __wrap_free(void *p) {
    if (p && p == workspace) {
        const unsigned char *bytes = p;
        for (size_t i = 0; i < workspace_size; ++i) assert(!bytes[i]);
        ++erased; workspace = NULL;
    }
    __real_free(p);
}

typedef struct {
    pthread_mutex_t mutex;
    native_wifi_file_t paths;
    bool busy, held;
    pthread_t owner;
    native_wifi_store_t store;
} context_t;
static context_t ctx = {.mutex = PTHREAD_MUTEX_INITIALIZER};

static native_wifi_result_t owner_lock(void *opaque) {
    context_t *c = opaque;
    if (c->busy) return NATIVE_WIFI_BUSY;
    assert(!pthread_mutex_lock(&c->mutex));
    c->held = true; c->owner = pthread_self();
    return NATIVE_WIFI_OK;
}
static void owner_unlock(void *opaque) {
    context_t *c = opaque;
    assert(c->held && pthread_equal(c->owner, pthread_self()));
    c->held = false; assert(!pthread_mutex_unlock(&c->mutex));
}
static void locked(context_t *c) {
    assert(c->held && pthread_equal(c->owner, pthread_self()));
}
static native_wifi_result_t read_live(void *opaque, uint8_t *data,
                                     size_t capacity, size_t *size) {
    context_t *c = opaque; locked(c); ++reads;
    return native_wifi_file_read(&c->paths, data, capacity, size);
}
static native_wifi_result_t publish_csv(void *opaque, const uint8_t *data, size_t size) {
    context_t *c = opaque; locked(c); ++publishes;
    return native_wifi_file_publish(&c->paths, data, size);
}
static void committed_csv(void *opaque, const uint8_t *data, size_t size) {
    context_t *c = opaque; locked(c); assert(data && size < 800); ++commits;
}
static const native_wifi_store_ops_t ops = {
    owner_lock, owner_unlock, read_live, publish_csv, committed_csv,
};
static void text(const char *path, const void *data, size_t size) {
    FILE *file = __real_fopen(path, "wb"); assert(file);
    assert(__real_fwrite(data, 1, size, file) == size); assert(!__real_fclose(file));
}
static void check_live(const void *data, size_t size) {
    uint8_t buffer[801]; FILE *file = __real_fopen(live, "rb"); assert(file);
    assert(__real_fread(buffer, 1, sizeof(buffer), file) == size);
    assert(!memcmp(buffer, data, size)); assert(!__real_fclose(file));
}
static void reset(const char *csv) {
    fault = NONE; installed = false; expect_workspace = false;
    assert(!workspace); temp_file = live_file = NULL;
    (void)__real_remove(live); (void)__real_remove(temporary); (void)__real_remove(backup);
    if (csv) text(live, csv, strlen(csv));
    ctx.busy = false;
    assert(native_wifi_store_init(&ctx.store, &ops, &ctx, UINT64_C(0x123456789abcdef)));
    publishes = commits = reads = 0;
}
static native_wifi_result_t metadata(native_wifi_metadata_t *out) {
    expect_workspace = true;
    native_wifi_result_t result = native_wifi_store_metadata(&ctx.store, out);
    expect_workspace = false; assert(!workspace); return result;
}
static native_wifi_result_t edit(native_wifi_edit_t *value) {
    expect_workspace = true;
    native_wifi_result_t result = native_wifi_store_edit(&ctx.store, value);
    expect_workspace = false; assert(!workspace); return result;
}
static native_wifi_edit_t existing(const native_wifi_metadata_t *meta) {
    native_wifi_edit_t value = {0};
    strcpy(value.revision, meta->revision); value.count = meta->count;
    for (size_t i = 0; i < meta->count; ++i) strcpy(value.profiles[i].id, meta->profiles[i].id);
    return value;
}
static bool contains(const void *data, size_t size, const char *needle) {
    size_t length = strlen(needle);
    for (size_t i = 0; i + length <= size; ++i)
        if (!memcmp((const char *)data + i, needle, length)) return true;
    return false;
}
static void csv_cases(void) {
    uint8_t csv[801];
    assert(native_wifi_validate_csv(NULL, 0) == NATIVE_WIFI_INVALID);
    for (size_t ssid = 0; ssid <= 33; ++ssid) {
        for (size_t password = 0; password <= 65; ++password) {
            memset(csv, 's', ssid); csv[ssid] = '\t';
            memset(csv + ssid + 1, 'p', password); csv[ssid + 1 + password] = '\n';
            bool valid = ssid > 0 && ssid < 32 && password < 64;
            assert((native_wifi_validate_csv(csv, ssid + password + 2) == NATIVE_WIFI_OK) == valid);
            ++passed;
        }
    }
    for (size_t count = 0; count <= 6; ++count) {
        for (size_t i = 0; i < count; ++i) memcpy(csv + i * 4, "s\tp\n", 4);
        assert((native_wifi_validate_csv(csv, count * 4) == NATIVE_WIFI_OK) ==
               (count > 0 && count <= 5)); ++passed;
    }
    const char *valid[] = {" s \t p \r\n", "a\t", "\na\tp\n\r\n", "a\tp\r\nb\t\n"};
    const char *invalid[] = {"", "\n", "\tpass\n", "ssid\n", "s\tp\tq\n", "s\tp\rq\n", "s\rp\tq\n"};
    for (size_t i = 0; i < sizeof(valid) / sizeof(*valid); ++i) {
        assert(native_wifi_validate_csv((const uint8_t *)valid[i], strlen(valid[i])) == NATIVE_WIFI_OK); ++passed;
    }
    for (size_t i = 0; i < sizeof(invalid) / sizeof(*invalid); ++i) {
        assert(native_wifi_validate_csv((const uint8_t *)invalid[i], strlen(invalid[i])) == NATIVE_WIFI_INVALID); ++passed;
    }
    const uint8_t nul[] = {'s','\t','p',0,'q','\n'};
    assert(native_wifi_validate_csv(nul, sizeof(nul)) == NATIVE_WIFI_INVALID); ++passed;
}
static void typed_cases(void) {
    const char *base = " duplicate \tOLD_SECRET_CANARY_A\r\n duplicate \tOLD_SECRET_CANARY_B\n";
    native_wifi_metadata_t meta, next;
    reset(base); assert(metadata(&meta) == NATIVE_WIFI_OK && meta.count == 2);
    assert(!contains(&meta, sizeof(meta), "OLD_SECRET_CANARY"));
    assert(!strcmp(meta.profiles[0].ssid, " duplicate ") && meta.profiles[0].ssid_utf8);
    native_wifi_edit_t value = existing(&meta);
    native_wifi_edit_profile_t swap = value.profiles[0];
    value.profiles[0] = value.profiles[1]; value.profiles[1] = swap;
    assert(edit(&value) == NATIVE_WIFI_OK && publishes == 1 && commits == 1 && reads == 2);
    check_live(" duplicate \tOLD_SECRET_CANARY_B\n duplicate \tOLD_SECRET_CANARY_A\n", 64);
    assert(metadata(&next) == NATIVE_WIFI_OK && strcmp(meta.revision, next.revision));
    unsigned before = reads;
    assert(edit(&value) == NATIVE_WIFI_CONFLICT && reads == before && publishes == 1);
    passed += 4;
    value = existing(&next); value.count = 1;
    value.profiles[0].password_action = NATIVE_WIFI_PASSWORD_SET;
    value.profiles[0].password_present = true; // Deliberate open network.
    assert(edit(&value) == NATIVE_WIFI_OK); check_live(" duplicate \t\n", 13); ++passed;
    assert(metadata(&meta) == NATIVE_WIFI_OK);
    value = existing(&meta); value.count = 2;
    value.profiles[1] = (native_wifi_edit_profile_t){.ssid_present=true,
        .password_action=NATIVE_WIFI_PASSWORD_SET, .password_present=true};
    strcpy(value.profiles[1].ssid, " new "); strcpy(value.profiles[1].password, "********");
    assert(edit(&value) == NATIVE_WIFI_OK);
    const char *with_new = " duplicate \t\n new \t********\n";
    check_live(with_new, strlen(with_new)); ++passed;
    for (unsigned mode = 0; mode < 10; ++mode) {
        reset(base); assert(metadata(&meta) == NATIVE_WIFI_OK); value = existing(&meta);
        switch (mode) {
        case 0: value.profiles[0].password_present = true; break;
        case 1: value.profiles[0].password_action = NATIVE_WIFI_PASSWORD_SET; break;
        case 2: value.profiles[0].password_action = (native_wifi_password_action_t)9; break;
        case 3: strcpy(value.profiles[0].id, "r5"); break;
        case 4: strcpy(value.profiles[1].id, "r1"); break;
        case 5: value.profiles[0].id[0] = 0; break;
        case 6: value.profiles[0].ssid_present = true; strcpy(value.profiles[0].ssid, "bad\nrow"); break;
        case 7: memset(value.profiles[0].id, 'r', sizeof(value.profiles[0].id)); break;
        case 8: value.count = 6; break;
        default: value.profiles[0].password_action = NATIVE_WIFI_PASSWORD_SET;
                 value.profiles[0].password_present = true;
                 memset(value.profiles[0].password, 'x', sizeof(value.profiles[0].password)); break;
        }
        assert(edit(&value) == NATIVE_WIFI_INVALID && !publishes && !commits);
        check_live(base, strlen(base)); ++passed;
    }
    reset("bad storage"); assert(metadata(&meta) == NATIVE_WIFI_INVALID_STORAGE && !meta.count && !meta.revision[0]);
    assert(native_wifi_store_import(&ctx.store, (const uint8_t *)"fixed\tp\n", 8) == NATIVE_WIFI_OK);
    assert(metadata(&meta) == NATIVE_WIFI_OK && meta.count == 1); ++passed;
    reset(NULL); assert(metadata(&meta) == NATIVE_WIFI_OK && !meta.count);
    value = existing(&meta); value.count = 1;
    value.profiles[0] = (native_wifi_edit_profile_t){.ssid_present=true,
        .password_present=true,.password_action=NATIVE_WIFI_PASSWORD_SET};
    strcpy(value.profiles[0].ssid, "first"); assert(edit(&value) == NATIVE_WIFI_OK); ++passed;
    assert(metadata(&meta) == NATIVE_WIFI_OK); value = existing(&meta); value.count = 0;
    assert(edit(&value) == NATIVE_WIFI_OK); check_live("", 0);
    text(backup, "old\tDO_NOT_RESURRECT\n", 21);
    assert(native_file_recover(live, backup)); check_live("", 0);
    assert(metadata(&next) == NATIVE_WIFI_OK && !next.count);
    assert(native_wifi_store_import(&ctx.store, (const uint8_t *)"", 0) == NATIVE_WIFI_INVALID); ++passed;
    reset("a\tp\n"); ctx.store.generation = UINT64_MAX;
    assert(metadata(&meta) == NATIVE_WIFI_OK); value = existing(&meta);
    assert(edit(&value) == NATIVE_WIFI_EXHAUSTED && !publishes && !commits);
    assert(native_wifi_store_import(&ctx.store, (const uint8_t *)"b\tq\n", 4) == NATIVE_WIFI_EXHAUSTED); ++passed;
    reset("a\tp\n"); assert(metadata(&meta) == NATIVE_WIFI_OK); value = existing(&meta); ctx.busy = true;
    assert(metadata(&next) == NATIVE_WIFI_BUSY && edit(&value) == NATIVE_WIFI_BUSY && !publishes); ++passed;
    ctx.busy = false;
}
static void legacy_cases(void) {
    const char legacy[] = {'s',(char)0xff,'\t','p',(char)0x80,'\n',0};
    reset(legacy); native_wifi_metadata_t meta; assert(metadata(&meta) == NATIVE_WIFI_OK);
    assert(!meta.profiles[0].ssid_utf8); native_wifi_edit_t value = existing(&meta);
    assert(edit(&value) == NATIVE_WIFI_OK); check_live(legacy, strlen(legacy)); ++passed;
    assert(metadata(&meta) == NATIVE_WIFI_OK); value = existing(&meta);
    value.profiles[0].ssid_present = true; memcpy(value.profiles[0].ssid, legacy, 2);
    assert(edit(&value) == NATIVE_WIFI_INVALID); ++passed;
    strcpy(value.profiles[0].ssid, "\xc3\xa9\xf0\x9f\x98\x80");
    assert(edit(&value) == NATIVE_WIFI_OK); assert(metadata(&meta) == NATIVE_WIFI_OK && meta.profiles[0].ssid_utf8); ++passed;
    const unsigned char *bad[] = {(const unsigned char *)"\xc0\x80",(const unsigned char *)"\xed\xa0\x80",(const unsigned char *)"\xf4\x90\x80\x80",(const unsigned char *)"\xe2\x82"};
    for (size_t i = 0; i < sizeof(bad)/sizeof(*bad); ++i) {
        assert(metadata(&meta) == NATIVE_WIFI_OK); value = existing(&meta);
        value.profiles[0].ssid_present = true; strcpy(value.profiles[0].ssid, (const char *)bad[i]);
        assert(edit(&value) == NATIVE_WIFI_INVALID); ++passed;
    }
}
static void fault_cases(void) {
    const char *old = "old\tPRIVATE_CANARY\n", *new_csv = "new\tNEW_CANARY\n";
    for (enum fault f = OPEN_TEMP; f <= ROLLBACK; ++f) {
        reset(old); native_wifi_metadata_t meta; assert(metadata(&meta) == NATIVE_WIFI_OK);
        uint64_t generation = ctx.store.generation; fault = f;
        if (f == READ_ERROR || f == CLOSE_LIVE) {
            assert(metadata(&meta) == NATIVE_WIFI_IO && !publishes);
        } else {
            assert(native_wifi_store_import(&ctx.store, (const uint8_t *)new_csv, strlen(new_csv)) == NATIVE_WIFI_IO);
            assert(!commits && generation == ctx.store.generation);
        }
        fault = NONE; assert(native_file_recover(live, backup)); check_live(old, strlen(old)); ++passed;
    }
    reset(old); native_wifi_metadata_t meta; assert(metadata(&meta) == NATIVE_WIFI_OK);
    native_wifi_edit_t value = existing(&meta); fault = ALLOCATE;
    assert(edit(&value) == NATIVE_WIFI_NO_MEMORY && metadata(&meta) == NATIVE_WIFI_NO_MEMORY && !publishes); ++passed;
    reset(old); uint8_t huge[800]; memset(huge, 'x', sizeof(huge)); text(live, huge, sizeof(huge));
    assert(metadata(&meta) == NATIVE_WIFI_INVALID_STORAGE); ++passed;
    reset(old); assert(!__real_rename(live, backup));
    assert(metadata(&meta) == NATIVE_WIFI_OK && meta.count == 1); check_live(old, strlen(old)); ++passed;
}

static atomic_uint stale_conflicts, successful_edits;
static void *race_writer(void *argument) {
    unsigned thread = (unsigned)(uintptr_t)argument;
    for (unsigned i = 0; i < 80; ++i) {
        native_wifi_metadata_t meta;
        assert(native_wifi_store_metadata(&ctx.store, &meta) == NATIVE_WIFI_OK && meta.count == 2);
        native_wifi_edit_t value = existing(&meta);
        value.profiles[0].ssid_present = true;
        (void)snprintf(value.profiles[0].ssid, sizeof(value.profiles[0].ssid), "t%u-%u", thread, i);
        native_wifi_result_t result = native_wifi_store_edit(&ctx.store, &value);
        assert(result == NATIVE_WIFI_OK || result == NATIVE_WIFI_CONFLICT);
        if (result == NATIVE_WIFI_OK) atomic_fetch_add(&successful_edits, 1);
        else atomic_fetch_add(&stale_conflicts, 1);
    }
    return NULL;
}
static void concurrency_cases(void) {
    reset("same\tKEY_A\nsame\tKEY_B\n");
    // Real threads intentionally bypass single-thread workspace instrumentation.
    pthread_t threads[4];
    for (unsigned i = 0; i < 4; ++i) assert(!pthread_create(&threads[i], NULL, race_writer, (void *)(uintptr_t)i));
    for (unsigned i = 0; i < 4; ++i) assert(!pthread_join(threads[i], NULL));
    assert(successful_edits + stale_conflicts == 320 && successful_edits == commits && publishes == commits);
    native_wifi_metadata_t meta; assert(metadata(&meta) == NATIVE_WIFI_OK && meta.count == 2);
    uint8_t csv[800]; size_t size; assert(native_wifi_file_read(&ctx.paths, csv, sizeof(csv), &size) == NATIVE_WIFI_OK);
    assert(contains(csv, size, "\tKEY_A\n") && contains(csv, size, "\tKEY_B\n"));
    assert(ctx.store.generation == 1U + successful_edits); passed += 320;
}
int main(void) {
    assert(mkdtemp(directory));
    (void)snprintf(live, sizeof(live), "%s/wifi.csv", directory);
    (void)snprintf(temporary, sizeof(temporary), "%s/wifi.csv.tmp", directory);
    (void)snprintf(backup, sizeof(backup), "%s/wifi.csv.bak", directory);
    ctx.paths = (native_wifi_file_t){live, temporary, backup};
    csv_cases(); typed_cases(); legacy_cases(); fault_cases(); concurrency_cases();
    assert(allocations == erased && !workspace);
    fault = NONE; (void)__real_remove(live); (void)__real_remove(temporary); (void)__real_remove(backup);
    assert(!rmdir(directory));
    printf("%u groups passed; %u private workspaces erased; 320 real-thread edits (%u conflicts)\n", passed, erased, stale_conflicts);
    return 0;
}
