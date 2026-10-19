#define _GNU_SOURCE
#include <errno.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

#include "network_profiles.h"
#include "native_wifi_store.h"

// Deliberate failures have stable semantic markers, never secret field values.
#define CHECK(condition, marker) do { if (!(condition)) { \
    fprintf(stderr, "SEMANTIC_FAILURE:%s:%u\n", marker, __LINE__); exit(80); \
} } while (0)

static const char *const live = "/spiffs/data/wifi.csv";
static const char *const backup = "/spiffs/data/wifi.csv.bak";
static char root[1024];
static unsigned cases, opens, closes, reads, erases, line_erases, table_erases;
static bool cookie_mode, unavailable_lock, absent_lock, eof_seen;
static int open_error, stat_error, close_error, rename_error;
static const uint8_t *cookie_data;
static size_t cookie_size, cookie_position, cookie_fragment, cookie_error_at;

static void mapped_path(const char *path, char *out, size_t capacity) {
    CHECK(!strcmp(path, live) || !strcmp(path, backup), "private_path");
    int length = snprintf(out, capacity, "%s/%s", root, path + 13);
    CHECK(length > 0 && (size_t)length < capacity, "mapped_path_bounds");
}

static ssize_t cookie_read(void *context, char *out, size_t capacity) {
    (void)context;
    ++reads;
    if (cookie_position >= cookie_error_at) { errno = EIO; return -1; }
    size_t size = cookie_size - cookie_position;
    if (size > capacity) size = capacity;
    if (size > cookie_fragment) size = cookie_fragment;
    if (size > cookie_error_at - cookie_position)
        size = cookie_error_at - cookie_position;
    memcpy(out, cookie_data + cookie_position, size);
    cookie_position += size;
    if (!size) eof_seen = true;
    return (ssize_t)size;
}

static int cookie_close(void *context) {
    (void)context;
    if (close_error) { errno = EIO; return -1; }
    return 0;
}

static FILE *mapped_open(const char *path, const char *mode) {
    CHECK(!strcmp(path, live) && !strcmp(mode, "rb"), "recoverable_open_contract");
    ++opens;
    if (open_error) {
        if (open_error > 0) errno = open_error;
        return NULL;
    }
    if (cookie_mode) {
        cookie_io_functions_t io = {.read = cookie_read, .close = cookie_close};
        return fopencookie(NULL, "r", io);
    }
    char actual[1200];
    mapped_path(path, actual, sizeof(actual));
    return fopen(actual, mode);
}

static int mapped_close(FILE *file) {
    ++closes;
    int result = fclose(file);
    if (close_error) { errno = EIO; return EOF; }
    return result;
}

static int mapped_stat(const char *path, struct stat *info) {
    if (stat_error) { errno = EIO; return -1; }
    if (cookie_mode) {
        memset(info, 0, sizeof(*info));
        return 0;
    }
    char actual[1200];
    mapped_path(path, actual, sizeof(actual));
    return stat(actual, info);
}

static int mapped_rename(const char *from, const char *to) {
    if (rename_error) { errno = EIO; return -1; }
    char actual_from[1200], actual_to[1200];
    mapped_path(from, actual_from, sizeof(actual_from));
    mapped_path(to, actual_to, sizeof(actual_to));
    return rename(actual_from, actual_to);
}

typedef void *SemaphoreHandle_t;
static SemaphoreHandle_t s_storage_lock = (void *)(uintptr_t)1;
#define pdTRUE 1
#define pdMS_TO_TICKS(value) (value)
static int xSemaphoreTake(SemaphoreHandle_t lock, unsigned ticks) {
    CHECK(lock == (void *)(uintptr_t)1 && ticks == 1000U, "storage_lock_contract");
    return !unavailable_lock;
}
static void xSemaphoreGive(SemaphoreHandle_t lock) {
    CHECK(lock == (void *)(uintptr_t)1, "storage_unlock_contract");
}

#define stat(...) mapped_stat(__VA_ARGS__)
#define rename(...) mapped_rename(__VA_ARGS__)
#include "file_transaction.c"
#undef rename
#undef stat
#define fopen(...) mapped_open(__VA_ARGS__)
#include "storage-production.inc"
#undef fopen

// Use the exact production volatile erase and inspect its effect immediately;
// do not retain pointers to a returned function's stack.
#define native_wifi_erase actual_native_wifi_erase
#include "native_wifi_store.c"
#undef native_wifi_erase
void native_wifi_erase(void *data, size_t size) {
    ++erases;
    if (size == 160U) ++line_erases;
    else if (size == sizeof(network_profiles_t)) ++table_erases;
    else CHECK(false, "unexpected_secret_workspace");
    actual_native_wifi_erase(data, size);
    const uint8_t *bytes = data;
    for (size_t i = 0; i < size; ++i) CHECK(bytes[i] == 0, "whole_workspace_wiped");
}

#define fclose(...) mapped_close(__VA_ARGS__)
#include "network_profiles-production.c"
#undef fclose

static void reset(void) {
    opens = closes = reads = erases = line_erases = table_erases = 0;
    unavailable_lock = absent_lock = eof_seen = false;
    open_error = stat_error = close_error = rename_error = 0;
    cookie_position = 0;
    cookie_fragment = SIZE_MAX;
    cookie_error_at = SIZE_MAX;
    s_storage_lock = (void *)(uintptr_t)1;
    errno = ENOENT; // Production must clear stale errno before opening.
}

static void data(const void *bytes, size_t size) {
    reset();
    cookie_mode = true;
    cookie_data = bytes;
    cookie_size = size;
}

static void text(const char *value) { data(value, strlen(value)); }

static network_profiles_t expect(esp_err_t error, unsigned count) {
    struct {
        uint64_t before;
        network_profiles_t profiles;
        uint64_t after;
    } guarded;
    memset(&guarded, 0xa5, sizeof(guarded));
    guarded.before = UINT64_C(0x0123456789abcdef);
    guarded.after = UINT64_C(0xfedcba9876543210);
    network_profiles_t initial = guarded.profiles;
    esp_err_t actual = network_profiles_load(&guarded.profiles);
    CHECK(actual == error, "expected_error_contract");
    CHECK(guarded.before == UINT64_C(0x0123456789abcdef) &&
          guarded.after == UINT64_C(0xfedcba9876543210), "output_canaries");
    if (error == ESP_OK) {
        CHECK(guarded.profiles.count == count, "complete_profile_count");
        for (size_t i = count; i < NETWORK_PROFILES_MAX; ++i) {
            network_profile_t empty = {0};
            CHECK(!memcmp(&guarded.profiles.rows[i], &empty, sizeof(empty)),
                  "unused_profiles_zero");
        }
    } else {
        CHECK(!memcmp(&guarded.profiles, &initial, sizeof(initial)),
              "failed_io_never_publishes_partial");
    }
    CHECK(erases == 2U && line_erases == 1U && table_erases == 1U,
          "all_secret_workspaces_wiped");
    CHECK(closes == opens || (closes == 0U && error != ESP_OK), "file_closed_once");
    ++cases;
    return guarded.profiles;
}

static void row(const network_profiles_t *profiles, size_t index,
                const char *ssid, const char *password) {
    CHECK(index < profiles->count, "profile_index");
    CHECK(!strcmp(profiles->rows[index].ssid, ssid) &&
          !strcmp(profiles->rows[index].password, password), "file_order_and_bytes");
}

static void put(const char *path, const char *value) {
    char actual[1200];
    mapped_path(path, actual, sizeof(actual));
    FILE *file = fopen(actual, "wb");
    CHECK(file != NULL, "fixture_open");
    size_t size = strlen(value);
    CHECK(fwrite(value, 1, size, file) == size && fclose(file) == 0, "fixture_write");
}

static void remove_fixture(const char *path) {
    char actual[1200];
    mapped_path(path, actual, sizeof(actual));
    CHECK(remove(actual) == 0 || errno == ENOENT, "fixture_remove");
}

int main(int argc, char **argv) {
    CHECK(argc == 2, "fixture_directory_argument");
    CHECK(strlen(argv[1]) < sizeof(root), "fixture_directory_bounds");
    strcpy(root, argv[1]);
    reset();
    CHECK(network_profiles_load(NULL) == ESP_ERR_INVALID_ARG && !erases && !opens,
          "null_argument");
    ++cases;

    text("");
    expect(ESP_OK, 0);
    text("first\t\n");
    network_profiles_t profiles = expect(ESP_OK, 1);
    row(&profiles, 0, "first", "");
    const char *five = "first\tone\nsecond\ttwo\nthird\tthree\nfourth\tfour\nfifth\tfive\n";
    text(five);
    profiles = expect(ESP_OK, 5);
    row(&profiles, 0, "first", "one");
    row(&profiles, 1, "second", "two");
    row(&profiles, 2, "third", "three");
    row(&profiles, 3, "fourth", "four");
    row(&profiles, 4, "fifth", "five");
    const char *six = "first\tone\nsecond\ttwo\nthird\tthree\nfourth\tfour\nfifth\tfive\nsixth\tsix\n";
    text(six);
    profiles = expect(ESP_OK, 5);
    CHECK(cookie_position == cookie_size && eof_seen, "whole_file_read_after_five");
    row(&profiles, 4, "fifth", "five");

    char ssid31[32], ssid32[33], pass63[64], pass64[65], buffer[1024];
    memset(ssid31, 's', 31); ssid31[31] = 0;
    memset(ssid32, 's', 32); ssid32[32] = 0;
    memset(pass63, 'p', 63); pass63[63] = 0;
    memset(pass64, 'p', 64); pass64[64] = 0;
    snprintf(buffer, sizeof(buffer), "%s\t%s\r\n", ssid31, pass63);
    text(buffer);
    profiles = expect(ESP_OK, 1);
    row(&profiles, 0, ssid31, pass63);
    snprintf(buffer, sizeof(buffer), "%s\tvalue\nbad\t%s\nvalid\tvalue\n", ssid32, pass64);
    text(buffer);
    profiles = expect(ESP_OK, 1);
    row(&profiles, 0, "valid", "value");
    text("\n\r\nmissing-tab\n\tignored\nbad\rssid\tvalue\nbad\tval\rue\nbad\tvalue\textra\nvalid\tvalue\r\n");
    profiles = expect(ESP_OK, 1);
    row(&profiles, 0, "valid", "value");
    text("missing-tab\n\tignored\n");
    expect(ESP_OK, 0);
    const char nul[] = "before\tvalue\0phantom\tvalue\nvalid\tvalue\n";
    data(nul, sizeof(nul) - 1U);
    profiles = expect(ESP_OK, 1);
    row(&profiles, 0, "valid", "value");
    memset(buffer, 'x', 159);
    strcpy(buffer + 159, "phantom\tvalue\nvalid\tvalue\n");
    text(buffer);
    profiles = expect(ESP_OK, 1);
    row(&profiles, 0, "valid", "value");
    memset(buffer, 'x', 510);
    strcpy(buffer + 510, "\nvalid\tvalue");
    const size_t fragments[] = {1, 2, 3, 7, 31, 159, 512};
    for (size_t i = 0; i < sizeof(fragments) / sizeof(fragments[0]); ++i) {
        text(buffer);
        cookie_fragment = fragments[i];
        profiles = expect(ESP_OK, 1);
        row(&profiles, 0, "valid", "value");
    }
    text(" first \t value \r\nduplicate\tone\nduplicate\ttwo");
    profiles = expect(ESP_OK, 3);
    row(&profiles, 0, " first ", " value ");
    row(&profiles, 1, "duplicate", "one");
    row(&profiles, 2, "duplicate", "two");
    const char arbitrary_bytes[] = "\xffssid\t\xfepass\n";
    data(arbitrary_bytes, sizeof(arbitrary_bytes) - 1U);
    profiles = expect(ESP_OK, 1);
    row(&profiles, 0, "\xffssid", "\xfepass");

    const size_t failures[] = {0, 1, 4, 9, 10, 20};
    for (size_t i = 0; i < sizeof(failures) / sizeof(failures[0]); ++i) {
        text(six);
        cookie_fragment = 1;
        cookie_error_at = failures[i];
        expect(ESP_FAIL, 0);
    }
    text(six);
    cookie_error_at = strlen(five);
    expect(ESP_FAIL, 0);
    text(six);
    cookie_error_at = cookie_size;
    expect(ESP_FAIL, 0);
    text("last\tvalue");
    cookie_error_at = cookie_size;
    expect(ESP_FAIL, 0);
    text(""); close_error = 1;
    expect(ESP_FAIL, 0);
    text(five); close_error = 1;
    expect(ESP_FAIL, 0);
    text(five); cookie_error_at = 5; close_error = 1;
    expect(ESP_FAIL, 0);
    const int open_failures[] = {ENOENT, EACCES, EIO, ENOSPC, -1};
    for (size_t i = 0; i < sizeof(open_failures) / sizeof(open_failures[0]); ++i) {
        text(five);
        open_error = open_failures[i];
        expect(open_error == ENOENT ? ESP_ERR_NOT_FOUND : ESP_FAIL, 0);
    }
    text(five); stat_error = 1;
    expect(ESP_FAIL, 0);
    text(five); unavailable_lock = true;
    expect(ESP_FAIL, 0);
    text(five); s_storage_lock = NULL;
    expect(ESP_FAIL, 0);

    // The actual existing open/recovery functions run over real mapped files.
    // A present empty live file must suppress a stale nonempty backup.
    reset(); cookie_mode = false;
    put(live, ""); put(backup, "stale\tvalue\n");
    expect(ESP_OK, 0);
    remove_fixture(live);
    reset();
    profiles = expect(ESP_OK, 1);
    row(&profiles, 0, "stale", "value");
    char actual_backup[1200]; mapped_path(backup, actual_backup, sizeof(actual_backup));
    CHECK(access(actual_backup, F_OK) != 0 && errno == ENOENT, "backup_recovered_once");
    remove_fixture(live);
    reset();
    expect(ESP_ERR_NOT_FOUND, 0);
    put(backup, "stale\tvalue\n");
    reset(); rename_error = 1;
    expect(ESP_FAIL, 0);
    remove_fixture(backup);
    printf("PASS CYD boot profiles: %u cases; first-five ordered rows, legacy bounds, fragmented stdio, whole-file errors, unchanged output, checked close, full secret wipes, real recovery/empty-live semantics\n", cases);
    return 0;
}
