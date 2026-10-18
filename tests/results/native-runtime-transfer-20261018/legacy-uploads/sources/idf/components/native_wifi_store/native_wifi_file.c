#include "native_wifi_file.h"

#include <errno.h>
#include <stdio.h>
#include <string.h>

#include "file_transaction.h"

static bool paths_valid(const native_wifi_file_t *paths) {
    return paths && paths->live && paths->temporary && paths->backup &&
           paths->live[0] && paths->temporary[0] && paths->backup[0] &&
           strcmp(paths->live, paths->temporary) &&
           strcmp(paths->live, paths->backup) &&
           strcmp(paths->temporary, paths->backup);
}

native_wifi_result_t native_wifi_file_read(const native_wifi_file_t *paths,
                                          uint8_t *data, size_t capacity,
                                          size_t *size) {
    if (!paths_valid(paths) || !data || !size || capacity < NATIVE_WIFI_FILE_BYTES)
        return NATIVE_WIFI_INVALID;
    *size = 0;
    if (!native_file_recover(paths->live, paths->backup)) return NATIVE_WIFI_IO;
    FILE *file = fopen(paths->live, "rb");
    if (!file) return errno == ENOENT ? NATIVE_WIFI_ABSENT : NATIVE_WIFI_IO;
    size_t received = fread(data, 1, NATIVE_WIFI_FILE_BYTES, file);
    bool healthy = !ferror(file);
    bool closed = fclose(file) == 0;
    if (!healthy || !closed) return NATIVE_WIFI_IO;
    if (received >= NATIVE_WIFI_FILE_BYTES) return NATIVE_WIFI_INVALID_STORAGE;
    *size = received;
    return NATIVE_WIFI_OK;
}

native_wifi_result_t native_wifi_file_publish(const native_wifi_file_t *paths,
                                             const uint8_t *data, size_t size) {
    if (!paths_valid(paths) || !data || size >= NATIVE_WIFI_FILE_BYTES)
        return NATIVE_WIFI_INVALID;
    FILE *file = fopen(paths->temporary, "wb");
    if (!file) return NATIVE_WIFI_IO;
    bool written = fwrite(data, 1, size, file) == size;
    bool flushed = fflush(file) == 0;
    bool closed = fclose(file) == 0;
    if (written && flushed && closed &&
        native_file_replace(paths->temporary, paths->live, paths->backup))
        return NATIVE_WIFI_OK;
    (void)remove(paths->temporary);
    return NATIVE_WIFI_IO;
}
