#pragma once

#include "adaptive_input.h"

// Bind once before creating the stream/decoder tasks. Queue lifetime is the
// application's lifetime; this callback never deletes or replaces the queue.
void tls_input_reserve_bind(adaptive_input_t *input);
// Producer only, after closing the previous connection. A permanent TLS
// reserve keeps the queue at its floor; otherwise restore its target capacity.
void tls_input_reserve_prepare_connection(void);
void tls_input_reserve_poll(void);
