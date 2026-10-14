#pragma once
#include <stdbool.h>
#include <stdint.h>
#include <time.h>

/* Country defaults match the recovered table; an unknown key selects GB. */
bool timezone_utc_offset(const char *country, time_t utc, int32_t *offset, bool *daylight);
bool timezone_local_time(const char *country, time_t utc, struct tm *local);
