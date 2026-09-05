#pragma once
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>

/* SPIFFS cannot rename over an existing destination. Keep the previous file
 * until the new name exists, and recover an interrupted rename on boot. */
static inline bool file_exists(const char *path) {
    struct stat st;
    return stat(path, &st) == 0;
}
static inline bool file_recover(const char *path) {
    char backup[96];
    snprintf(backup, sizeof(backup), "%s.bak", path);
    if (!file_exists(backup)) return true;
    if (!file_exists(path)) return rename(backup, path) == 0;
    return remove(backup) == 0;
}
static inline bool file_replace(const char *temporary, const char *path) {
    char backup[96];
    snprintf(backup, sizeof(backup), "%s.bak", path);
    if (!file_recover(path)) return false;
    bool previous = file_exists(path);
    if (previous && rename(path, backup) != 0) return false;
    if (rename(temporary, path) != 0) {
        if (previous) (void)rename(backup, path);
        return false;
    }
    if (previous) (void)remove(backup);
    return true;
}
