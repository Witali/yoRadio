#include <assert.h>
#include <errno.h>
#include <setjmp.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>

static const char *files[4];
static unsigned operations, failure_at, second_failure_at, crash_at;
static jmp_buf power_loss;
static int slot(const char *path) {
    const char *const names[]={"temporary","live","backup","unrelated"};
    for (unsigned i=0;i<4;++i) if (!strcmp(path,names[i])) return (int)i;
    assert(false);return 0;
}
static bool fail_operation(void) {
    ++operations;
    if (operations==failure_at || operations==second_failure_at) {errno=EIO;return true;}
    return false;
}
static void maybe_crash(void) {if (operations==crash_at) longjmp(power_loss,1);}
static int test_stat(const char *path,struct stat *out) {
    if (fail_operation()) return -1;
    if (!files[slot(path)]) {errno=ENOENT;return -1;}
    memset(out,0,sizeof(*out));maybe_crash();return 0;
}
static int test_remove(const char *path) {
    if (fail_operation()) return -1;
    int i=slot(path);
    if (!files[i]) {errno=ENOENT;return -1;}
    files[i]=NULL;maybe_crash();return 0;
}
static int test_rename(const char *from,const char *to) {
    if (fail_operation()) return -1;
    int a=slot(from), b=slot(to);
    // Match SPIFFS: rename must not rely on POSIX replacement of an existing name.
    if (!files[a]) {errno=ENOENT;return -1;}
    if (files[b]) {errno=EEXIST;return -1;}
    files[b]=files[a];files[a]=NULL;maybe_crash();return 0;
}
#define stat(...) test_stat(__VA_ARGS__)
#define remove(...) test_remove(__VA_ARGS__)
#define rename(...) test_rename(__VA_ARGS__)
#include "file_transaction.c"

static void reset(bool live,bool backup) {
    files[0]="new";files[1]=live ? "old" : NULL;
    files[2]=backup ? "old" : NULL;files[3]="unrelated";
    operations=failure_at=second_failure_at=crash_at=0;
}
static void check(bool had_old) {
    assert(files[3] && !strcmp(files[3],"unrelated"));
    if (had_old) assert((files[1] && (!strcmp(files[1],"old") || !strcmp(files[1],"new"))) ||
                       (files[2] && !strcmp(files[2],"old")));
    else assert(files[0] || files[1]);
}
int main(void) {
    unsigned cases=0;
    for (unsigned state=0;state<4;++state) {
        bool live=state&1, backup=state&2;
        reset(live,backup);assert(native_file_replace("temporary","live","backup"));
        assert(files[1] && !strcmp(files[1],"new") && !files[0]);
        unsigned maximum=operations;
        for (unsigned failure=1;failure<=maximum+1;++failure) {
            for (unsigned second=0;second<=maximum+2;++second) {
                reset(live,backup); failure_at=failure;second_failure_at=second;
                bool replaced=native_file_replace("temporary","live","backup");
                check(live||backup);
                if (replaced) assert(files[1] && !strcmp(files[1],"new"));
                failure_at=second_failure_at=0;
                assert(native_file_recover("live","backup"));check(live||backup);++cases;
            }
        }
        for (unsigned cut=1;cut<=maximum;++cut) {
            reset(live,backup);crash_at=cut;
            if (!setjmp(power_loss)) (void)native_file_replace("temporary","live","backup");
            crash_at=0;assert(native_file_recover("live","backup"));check(live||backup);++cases;
        }
    }
    reset(true,true);assert(!native_file_replace(NULL,"live","backup"));
    assert(!native_file_replace("live","live","backup"));
    assert(!native_file_replace("backup","live","backup"));
    assert(!native_file_recover("live","live"));assert(!native_file_recover("","backup"));
    assert(!native_file_recover(NULL,"backup"));check(true);
    printf("PASS file transaction: %u failure/rollback/power-cut cases; original contents retained; SPIFFS no-overwrite rename; ASan/UBSan\n",cases);
    return 0;
}
