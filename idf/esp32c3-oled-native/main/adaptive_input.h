#pragma once

#include <stdbool.h>
#include <stddef.h>
#include "freertos/FreeRTOS.h"

typedef struct adaptive_input adaptive_input_t;
typedef struct {
    size_t packet_capacity;
    unsigned resident, minimum, target, occupied, limit;
    unsigned released;
    // Data slots only; unpublished WRITING/control storage is not ready audio.
    // Byte counts include the caller's packet header. READING counts the whole
    // retained packet, not the decoder's unconsumed suffix.
    unsigned ready, reading, writing;
    size_t ready_bytes, reading_bytes;
} adaptive_input_stats_t;

// One producer, one consumer. Each acquired pointer is a lease: reclaim never
// touches WRITING, READY or READING slots. The object lives until task teardown.
adaptive_input_t *adaptive_input_create(size_t budget, size_t minimum_bytes,
                                        size_t packet_capacity);
void adaptive_input_destroy(adaptive_input_t *input); // Quiescent callers only.
BaseType_t adaptive_input_acquire(adaptive_input_t *input, void **packet,
                                  size_t size, TickType_t timeout);
BaseType_t adaptive_input_commit(adaptive_input_t *input, void *packet);
// Publish a nonempty prefix of the acquired lease. Never extend its requested
// size. Failure preserves the WRITING lease for correction or cancellation.
BaseType_t adaptive_input_commit_size(adaptive_input_t *input, void *packet,
                                      size_t used);
// Single producer only: temporarily take the partial READY data tail back as
// a full-capacity WRITING lease. Never take the sole queued node, a control
// tail, a full packet or a READING lease. Returns its previous committed size.
// Copy outside the lock, then republish before any other producer commit or
// blocking operation. Preserve the original prefix on rejection/cancellation.
BaseType_t adaptive_input_reopen_tail(adaptive_input_t *input, void **packet,
                                      size_t *used);
// Optional caller-owned small control storage, attached once before use.
// It joins the same FIFO, independently of the data slots. Never reclaimed,
// counted as audio prefill, or freed by this queue. Storage must outlive input.
// Commit/cancel/receive/return have the same lease rules as normal packets.
bool adaptive_input_attach_control(adaptive_input_t *input, void *storage,
                                    size_t capacity);
BaseType_t adaptive_input_acquire_control(adaptive_input_t *input, void **packet,
                                          size_t size, TickType_t timeout);
// Producer only: give up an uncommitted WRITING lease. Queued/READING pointers
// cannot be cancelled. The pointer is invalid after a successful cancellation.
bool adaptive_input_cancel(adaptive_input_t *input, void *packet);
void *adaptive_input_receive(adaptive_input_t *input, size_t *size,
                             TickType_t timeout);
bool adaptive_input_return(adaptive_input_t *input, void *packet);
bool adaptive_input_release_one(adaptive_input_t *input);
// Only the producer calls restore, between connections after old TLS closes.
// Does not change queued data or leases and never waits for consumers.
void adaptive_input_restore(adaptive_input_t *input);
// Producer only. Best-effort allocation of one absent slot, up to the current
// limit. Existing leases/queued bytes are untouched; allocation stays unlocked.
bool adaptive_input_restore_one(adaptive_input_t *input);
// Bound resident storage between minimum and configured target. Shrink idle
// excess slots immediately and busy excess slots on consumer return, keeping
// the earliest resident buffers. Real allocation-pressure reclamation can
// still free any idle slot above the minimum resident count.
// May overlap reclamation/consumer return and a producer allocation in flight.
void adaptive_input_set_limit(adaptive_input_t *input, unsigned slots);
adaptive_input_stats_t adaptive_input_stats(adaptive_input_t *input);
