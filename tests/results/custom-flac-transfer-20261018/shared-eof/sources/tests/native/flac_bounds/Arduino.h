#pragma once
#include <algorithm>
#include <cstdint>
#include <cstdlib>
#include <cstring>
static inline bool psramFound() { return false; }
static inline void *ps_malloc(size_t size) { return malloc(size); }
#define log_i(...) ((void)0)
#define log_e(...) ((void)0)
