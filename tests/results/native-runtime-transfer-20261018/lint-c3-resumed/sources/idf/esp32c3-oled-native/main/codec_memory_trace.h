#pragma once

#include "sdkconfig.h"

#if CONFIG_YORADIO_CODEC_MEMORY_TRACE
void codec_memory_trace_dump(const char *phase);
#else
static inline void codec_memory_trace_dump(const char *phase) { (void)phase; }
#endif
