#pragma once

#include "native_time_sntp.h"

// All three functions execute exclusively via checked esp_netif_tcpip_exec.
esp_err_t native_time_sntp_context_unused(void *context);
esp_err_t native_time_sntp_context_apply(void *context);
esp_err_t native_time_sntp_context_restart(void *context);

// The context TU has only the raw public lwIP header. Keep the public ESP
// extension declarations in the lifecycle TU to avoid legacy-inline aliases.
// Called only by native_time_sntp_context_apply in TCP/IP context.
void native_time_sntp_context_interval(uint32_t interval_ms);
