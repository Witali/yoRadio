#ifndef SMALL_TV_JPEG_PROVISION_H
#define SMALL_TV_JPEG_PROVISION_H

#include "jpeg_guard.h"

#define JPEG_PROVISION_STAMP_BYTES 64u
#define JPEG_PROVISION_HEADER_BYTES 8u
#define JPEG_PROVISION_ID_BYTES 32u
#define JPEG_PROVISION_PROGRAM_BYTES (JPEG_PROVISION_HEADER_BYTES+JPEG_PROVISION_ID_BYTES)

/* Generated from the SAME authority as the immutable guard. Never supplied by
 * HTTP. resource_index identifies an existing protected-padding resource. */
typedef struct {
    unsigned resource_index;
    uint8_t bytes[JPEG_PROVISION_STAMP_BYTES];
} jpeg_provision_stamp_t;

typedef enum {
    JPEG_PROVISION_ALREADY=0, JPEG_PROVISION_INSTALLED,
    JPEG_PROVISION_ARGUMENT, JPEG_PROVISION_GUARD, JPEG_PROVISION_OCCUPIED,
    JPEG_PROVISION_STAMP, JPEG_PROVISION_IO, JPEG_PROVISION_VERIFY
} jpeg_provision_result_t;

typedef struct {
    jpeg_provision_result_t status;
    jpeg_guard_result_t guard;
    uint32_t offset;
    int io_error;
    bool program_attempted;
} jpeg_provision_diagnostic_t;

/* REQUESTED_CHANGE: preserve legacy photos/settings while claiming ONLY the
 * generated stamp. A valid physical stamp takes the ordinary read-only path,
 * even if the already-owned cache/scratch contains data.
 *
 * Legacy/torn-stamp path verifies every immutable payload against the compiled
 * guard, then requires ALL candidate sectors to be physically FF (fresh double
 * reads). Existing stamp bits must be a monotonic supermask of the exact target;
 * no erase is ever used, and no other physical byte is programmed. Write and
 * verify the32-byte identity FIRST, then the8-byte header LAST. Tail24bytes stay
 * FF. A nonerased header requires the complete expected identity: a committed
 * foreign ID is never mistaken for our interrupted body. Resume only reachable
 * torn states under those SAME preconditions, not unknown write orderings.
 *
 * Caller serializes the ENTIRE bootstrap, supplies bounded/time-limited physical
 * callbacks and revokes all old capabilities first. This function itself grants
 * NO write capabilities; the owner must still complete physical authorization.
 * These checks establish matching layout/content, not publisher authenticity. */
jpeg_provision_result_t jpeg_provision_legacy(const jpeg_guard_layout_t *layout,
    const jpeg_guard_partition_t *observed,unsigned observed_count,
    const jpeg_nor_device_t *device,const jpeg_guard_sha256_t *sha256,
    const jpeg_provision_stamp_t *stamp,jpeg_provision_diagnostic_t *diagnostic);

#endif
