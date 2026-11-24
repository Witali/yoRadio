/* Bounded diagnostic records only. SPDX-License-Identifier: Apache-2.0 */
#pragma once

#include <stdbool.h>
#include <stdint.h>

#define PBUF_FAILURE_RECORD_SLOTS 4U

enum {
    PBUF_FAILURE_RECORD_TOTAL_SATURATED = 1U,
    PBUF_FAILURE_RECORD_OVERFLOW_SATURATED = 2U,
    PBUF_FAILURE_RECORD_ENTRY_SATURATED = 4U,
};

typedef struct {
    uint32_t layer, type, length, allocation_bytes, caller_pc;
} pbuf_failure_key_t;

typedef struct {
    pbuf_failure_key_t key;
    uint32_t count;
    uint32_t saturated; /* Boolean: an increment beyond UINT32_MAX was attempted. */
} pbuf_failure_entry_t;

typedef struct {
    pbuf_failure_entry_t entries[PBUF_FAILURE_RECORD_SLOTS];
    uint32_t total, overflow, used;
    uint32_t saturated; /* PBUF_FAILURE_RECORD_*_SATURATED bitmask. */
} pbuf_failure_record_t;

_Static_assert(sizeof(pbuf_failure_key_t) == 20, "Failure key must retain five complete 32-bit values");
_Static_assert(sizeof(pbuf_failure_entry_t) == 28, "Failure entry budget changed");
_Static_assert(sizeof(pbuf_failure_record_t) == 128, "Failure table exceeds its static budget");

static inline bool pbuf_failure_record_key_equal(const pbuf_failure_key_t *left,
                                                const pbuf_failure_key_t *right) {
    return left->layer == right->layer && (uint8_t)left->type == (uint8_t)right->type &&
           left->length == right->length && left->allocation_bytes == right->allocation_bytes &&
           left->caller_pc == right->caller_pc;
}

/* Valid zero-initialized storage and key are caller-owned. The caller MUST hold
 * the same external critical section for add and snapshot. There are no locks,
 * atomics, allocation, logging, task/phase queries, or allocator calls here.
 * Call add only after the real allocation has already returned NULL. Success
 * forwarding and the real allocation call are deliberately outside this API.
 * A full table retains its four exact tuples; further unmatched events count
 * in overflow. Existing matches continue to update even while the table is full.
 */
static inline void pbuf_failure_record_add(pbuf_failure_record_t *table,
                                         const pbuf_failure_key_t *key) {
    if (table->total == UINT32_MAX) table->saturated |= PBUF_FAILURE_RECORD_TOTAL_SATURATED;
    else ++table->total;
    for (uint32_t slot = 0; slot < table->used; ++slot) {
        pbuf_failure_entry_t *entry = &table->entries[slot];
        if (!pbuf_failure_record_key_equal(&entry->key, key)) continue;
        if (entry->count == UINT32_MAX) {
            entry->saturated = 1;
            table->saturated |= PBUF_FAILURE_RECORD_ENTRY_SATURATED;
        } else ++entry->count;
        return;
    }
    if (table->used < PBUF_FAILURE_RECORD_SLOTS) {
        pbuf_failure_entry_t *entry = &table->entries[table->used++];
        entry->key = *key;
        entry->count = 1;
        entry->saturated = 0;
    } else if (table->overflow == UINT32_MAX) {
        table->saturated |= PBUF_FAILURE_RECORD_OVERFLOW_SATURATED;
    } else ++table->overflow;
}

/* Destination storage must already exist. Copy under the same caller-held
 * critical section; formatting/draining may happen after releasing it.
 */
static inline void pbuf_failure_record_snapshot(const pbuf_failure_record_t *table,
                                              pbuf_failure_record_t *snapshot) {
    *snapshot = *table;
}
