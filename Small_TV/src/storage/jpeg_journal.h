#ifndef SMALL_TV_JPEG_JOURNAL_H
#define SMALL_TV_JPEG_JOURNAL_H

#include "jpeg_nor.h"

#define JPEG_JOURNAL_SLOTS 5u
#define JPEG_JOURNAL_BODY_BYTES 512u

typedef enum {
    JPEG_JOURNAL_OK = 0,
    JPEG_JOURNAL_MISS,
    JPEG_JOURNAL_ARGUMENT,
    JPEG_JOURNAL_STATE,
    JPEG_JOURNAL_IO,
    JPEG_JOURNAL_VERIFY,
    JPEG_JOURNAL_AMBIGUOUS,
    JPEG_JOURNAL_LIMIT
} jpeg_journal_result_t;

typedef struct {
    uint32_t banks[2], frame_bytes, source_limit;
    uint8_t layout_id[32], codec_id[32];
} jpeg_journal_config_t;

typedef struct {
    bool ready;
    uint32_t source_bytes;
    uint8_t source_sha256[32], frame_sha256[32];
} jpeg_journal_entry_t;

/* Trusted adapter: finish any dirty cache writes, then hash the ENTIRE physical
 * frame (not a RAM copy) and compare the expected SHA-256. Used on every hit and
 * before publication. Return 0 only after complete verification. Non-reentrant;
 * owner serializes media I/O. Current source identity must also describe actual
 * persistent JPEG bytes, not a stale HTTP/settings snapshot. */
typedef struct {
    void *context;
    int (*verify)(void *context, unsigned slot, uint32_t frame_bytes, const uint8_t expected[32]);
} jpeg_journal_verifier_t;

typedef struct {
    jpeg_nor_device_t device;
    jpeg_journal_config_t config;
    jpeg_journal_entry_t entries[JPEG_JOURNAL_SLOTS];
    uint64_t generation;
    uint64_t read_calls, program_calls, erase_calls;
    unsigned bank, pending_slot;
    int last_io_error;
    bool open, failed, have_head, matching, pending;
    uint8_t body[JPEG_JOURNAL_BODY_BYTES];
} jpeg_journal_t;

/* Owner zero-initializes the handle. Guard authorization is mandatory BEFORE
 * calling this API; allowed is a trusted, sorted, disjoint full-sector list.
 * Open is read-only. Foreign layout/codec snapshots are not fallback candidates:
 * retain the newest generation but expose no ready entries. A metadata I/O error
 * poisons the handle until abort/reopen; invalid arguments do no I/O.
 * No heap, hardware dependencies, C-struct serialization or implicit writes. */
jpeg_journal_result_t jpeg_journal_open(jpeg_journal_t *journal,
    const jpeg_nor_device_t *device, const jpeg_journal_config_t *config,
    const jpeg_nor_extent_t *allowed, unsigned allowed_count);
/* OK means durable invalidation; ONLY THEN may the owner overwrite the slot's
 * source or frame. One pending transaction. An already durably invalid entry
 * avoids a redundant metadata erase, but a fresh/foreign journal is published. */
jpeg_journal_result_t jpeg_journal_begin(jpeg_journal_t *journal, unsigned slot);
/* Ready metadata is committed only after adapter flush/physical-hash success.
 * A verify failure leaves the slot invalid and pending; abort or repair/retry.
 * On transport failure do not retry with old RAM state: reopen from actual flash. */
jpeg_journal_result_t jpeg_journal_publish(jpeg_journal_t *journal,
    uint32_t source_bytes, const uint8_t source_sha256[32], const uint8_t frame_sha256[32],
    const jpeg_journal_verifier_t *verifier);
/* OK authorizes use of a matching, physically verified cached frame. Metadata
 * alone never authorizes a hit, including when a damaged newest bank made boot
 * fall back to an older snapshot. A verify failure does not silently invalidate
 * RAM metadata: begin must still durably invalidate before overwriting anything. */
jpeg_journal_result_t jpeg_journal_lookup(jpeg_journal_t *journal, unsigned slot,
    uint32_t source_bytes, const uint8_t source_sha256[32],
    const jpeg_journal_verifier_t *verifier);
/* Cancel the transaction without I/O; its durable invalidation remains. */
void jpeg_journal_cancel(jpeg_journal_t *journal);
/* Close/discard RAM without I/O, including a failed/partly committed operation. */
void jpeg_journal_abort(jpeg_journal_t *journal);

#endif
