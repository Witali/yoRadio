#pragma once
#include "sdkconfig.h"
#include <stddef.h>
#include <stdint.h>

typedef enum {
    TLS_PATH_HTTP_READ,
    TLS_PATH_TLS_READ,
    TLS_PATH_POLL_READ,
    TLS_PATH_GCM_DECRYPT,
    TLS_PATH_AES_CTR,
    TLS_PATH_STAGE_COUNT
} tls_path_stage_t;

typedef enum {
    TLS_PATH_OK,
    TLS_PATH_ZERO,
    TLS_PATH_RETRY,
    TLS_PATH_ERROR
} tls_path_outcome_t;

typedef struct {
    uint64_t elapsed_us, requested_bytes, completed_bytes;
    uint32_t calls, max_us, ok, zero, retry, errors;
    uint32_t size_le_1024, size_le_4096, size_le_16384, size_larger;
} tls_path_sample_t;

#ifdef CONFIG_YORADIO_TLS_PATH_PROFILE
// Elapsed wall time includes preemption and blocking. Nested stages overlap.
// Only calls made by radio_stream are recorded; no pointers/data are retained.
int64_t tls_path_profile_begin(void);
void tls_path_profile_end(tls_path_stage_t stage, int64_t start,
                          size_t requested, size_t completed,
                          tls_path_outcome_t outcome);
void tls_path_profile_snapshot(tls_path_sample_t samples[TLS_PATH_STAGE_COUNT]);
void tls_path_profile_poll(void);
#else
static inline int64_t tls_path_profile_begin(void) { return -1; }
static inline void tls_path_profile_end(tls_path_stage_t stage, int64_t start,
                                       size_t requested, size_t completed,
                                       tls_path_outcome_t outcome) {
    (void)stage; (void)start; (void)requested; (void)completed; (void)outcome;
}
static inline void tls_path_profile_poll(void) {}
#endif
