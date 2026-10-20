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

static void restore_pair_file(const char *live, const char *backup,
                              bool retained, bool installed) {
    if (installed && remove(live) != 0 && errno != ENOENT) return;
    if (retained) (void)rename(backup, live);
}

bool native_file_replace_pair(const char *temporary_a, const char *live_a,
                              const char *backup_a, const char *temporary_b,
                              const char *live_b, const char *backup_b) {
    const char *paths[] = {temporary_a, live_a, backup_a,
                          temporary_b, live_b, backup_b};
    for (size_t i = 0; i < sizeof(paths) / sizeof(paths[0]); ++i) {
        if (!paths[i] || !paths[i][0]) return false;
        for (size_t j = 0; j < i; ++j)
            if (!strcmp(paths[i], paths[j])) return false;
    }
    if (!native_file_recover(live_a, backup_a) ||
        !native_file_recover(live_b, backup_b)) return false;
    int previous_a = file_exists(live_a);
    int previous_b = file_exists(live_b);
    if (previous_a < 0 || previous_b < 0 ||
        file_exists(temporary_a) != 1 || file_exists(temporary_b) != 1) return false;
    if ((previous_a && remove(backup_a) != 0 && errno != ENOENT) ||
        (previous_b && remove(backup_b) != 0 && errno != ENOENT)) return false;
    bool retained_a = false, retained_b = false, installed_a = false;
    if (previous_a) {
        if (rename(live_a, backup_a) != 0) return false;
        retained_a = true;
    }
    if (previous_b) {
        if (rename(live_b, backup_b) != 0) goto rollback;
        retained_b = true;
    }
    if (rename(temporary_a, live_a) != 0) goto rollback;
    installed_a = true;
    if (rename(temporary_b, live_b) != 0) goto rollback;
    // Both new files are committed. Cleanup failure keeps an old backup but
    // does not turn an installed, validated pair into a failed publication.
    if (retained_a) (void)remove(backup_a);
    if (retained_b) (void)remove(backup_b);
    return true;

rollback:
    restore_pair_file(live_b, backup_b, retained_b, false);
    restore_pair_file(live_a, backup_a, retained_a, installed_a);
    return false;
}
