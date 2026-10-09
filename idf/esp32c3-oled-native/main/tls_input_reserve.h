#pragma once

#include "adaptive_input.h"
#include "sdkconfig.h"

// Bind once before creating the stream/decoder tasks. Queue lifetime is the
// application's lifetime; this callback never deletes or replaces the queue.
void tls_input_reserve_bind(adaptive_input_t *input);
// Producer only, after closing the previous connection. A permanent TLS
// reserve starts the queue at its floor; otherwise restore its target capacity.
void tls_input_reserve_prepare_connection(void);
#if CONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS > 0
// Stream task only. Grow once after the first decoded FLAC frame; shrink
// before disposing the client. Queued/leased blocks retire on consumer return.
void tls_input_reserve_expand_flac(void);
void tls_input_reserve_finish_connection(void);
#endif
void tls_input_reserve_poll(void);
