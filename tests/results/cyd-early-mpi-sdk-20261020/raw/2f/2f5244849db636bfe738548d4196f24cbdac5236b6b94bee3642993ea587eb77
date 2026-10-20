#pragma once

#include "sdkconfig.h"

#ifdef __cplusplus
extern "C" {
#endif

// Call once in normal app_main task context, before application services.
// This uses the SDK-owned lifetime mutex. Its void API aborts on lazy-init OOM;
// there is no recoverable allocation-error result or heap-benefit guarantee.
#if defined(CONFIG_YORADIO_TLS_EARLY_MPI_LOCK) && CONFIG_YORADIO_TLS_EARLY_MPI_LOCK
void native_tls_early_mpi_prepare(void);
#else
static inline void native_tls_early_mpi_prepare(void) {}
#endif

#ifdef __cplusplus
}
#endif
