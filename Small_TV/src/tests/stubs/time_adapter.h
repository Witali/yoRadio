#pragma once
#include <time.h>
/* Explicit declaration for the POSIX environment call absent from MSVC's stdlib. */
int test_setenv(const char *name, const char *value, int overwrite);
struct tm *test_localtime_r(const time_t *now, struct tm *local);
struct tm *test_gmtime_r(const time_t *now, struct tm *local);
time_t test_time(time_t *out);
#define time test_time
#define localtime_r test_localtime_r
#define gmtime_r test_gmtime_r
