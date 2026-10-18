#include "file_transaction.h"

#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>

static int file_exists(const char *path) {
    struct stat info;
    if (stat(path, &info) == 0) return 1;
    return errno == ENOENT ? 0 : -1;
}

bool native_file_recover(const char *live, const char *backup) {
    if (!live || !*live || !backup || !*backup || !strcmp(live, backup)) return false;
    int present = file_exists(live);
    if (present < 0) return false;
    if (present) return true;
    int saved = file_exists(backup);
    if (saved < 0) return false;
    return !saved || rename(backup, live) == 0;
}

bool native_file_replace(const char *temporary, const char *live, const char *backup) {
    if (!temporary || !*temporary || !live || !backup ||
        !strcmp(temporary, live) || !strcmp(temporary, backup) ||
        !native_file_recover(live, backup)) return false;
    int previous = file_exists(live);
    if (previous < 0 || file_exists(temporary) != 1) return false;
    if (previous) {
        if (remove(backup) != 0 && errno != ENOENT) return false;
        if (rename(live, backup) != 0) return false;
    }
    if (rename(temporary, live) != 0) {
        if (previous) (void)rename(backup, live);
        return false; // A failed rollback deliberately retains backup.
    }
    if (previous) (void)remove(backup); // New live is committed; cleanup may retry.
    return true;
}
