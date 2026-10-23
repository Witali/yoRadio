#ifndef SMALL_TV_JPEG_TRANSPORT_H
#define SMALL_TV_JPEG_TRANSPORT_H

#include "jpeg_guard.h"
#include "jpeg_provision.h"

typedef enum {
    JPEG_TRANSPORT_OK=0, JPEG_TRANSPORT_STATE, JPEG_TRANSPORT_ARGUMENT,
    JPEG_TRANSPORT_RANGE, JPEG_TRANSPORT_LIMIT, JPEG_TRANSPORT_TIME,
    JPEG_TRANSPORT_CLOCK, JPEG_TRANSPORT_IO, JPEG_TRANSPORT_GUARD
} jpeg_transport_result_t;

typedef struct {
    uint64_t calls, read_bytes, program_bytes, erase_calls, duration_us;
} jpeg_transport_limits_t;

typedef struct {
    uint64_t calls, read_bytes, program_bytes, erase_calls;
} jpeg_transport_usage_t;

typedef struct {
    jpeg_nor_device_t raw;
    void *clock_context;
    uint64_t (*now_us)(void *context);
    jpeg_nor_extent_t allowed[JPEG_NOR_MAX_EXTENTS], readable;
    unsigned allowed_count;
    jpeg_transport_limits_t limits;
    jpeg_transport_usage_t usage;
    uint64_t epoch, started_us;
    const jpeg_guard_layout_t *verifying;
    jpeg_transport_result_t last_error;
    int last_io_error;
    bool initialized, authorized, active;
} jpeg_transport_t;

typedef struct {
    jpeg_transport_t *owner;
    jpeg_nor_extent_t extents[JPEG_NOR_MAX_EXTENTS];
    unsigned count;
    uint64_t epoch;
    bool writable;
} jpeg_transport_port_t;

/* Caller zero-initializes context once; all operations are owner-serialized.
 * Raw device and monotonic clock are trusted platform callbacks. Counts are
 * issued API requests/bytes, not chip bus commands or an endurance guarantee. */
jpeg_transport_result_t jpeg_transport_init(jpeg_transport_t *transport,
    const jpeg_nor_device_t *raw, uint64_t (*now_us)(void *), void *clock_context);
/* Revokes ALL old ports before even attempting verification. Startup guard is
 * readonly, separately budgeted; no port/job survives success OR failure.
 * SHA provider/observed map must be captured from this exact device/build. */
jpeg_transport_result_t jpeg_transport_authorize(jpeg_transport_t *transport,
    const jpeg_guard_layout_t *layout,const jpeg_guard_partition_t *observed,unsigned count,
    const jpeg_guard_sha256_t *sha256,const jpeg_transport_limits_t *limits);
/* Startup-only legacy adoption under ONE budget/epoch, followed by the full
 * physical guard. Only the generated32-byte identity and8-byte header within
 * the64-byte stamp may be programmed; erases/ordinary ports remain forbidden. Existing stamps take
 * the same read-only guard path. Old ports are revoked on every outcome. */
jpeg_transport_result_t jpeg_transport_provision(jpeg_transport_t *transport,
    const jpeg_guard_layout_t *layout,const jpeg_guard_partition_t *observed,unsigned count,
    const jpeg_guard_sha256_t *sha256,const jpeg_provision_stamp_t *stamp,
    jpeg_provision_diagnostic_t *diagnostic,const jpeg_transport_limits_t *limits);
/* One shared budget for every scratch/cache/journal/source port of one decode.
 * Every begin invalidates prior handles; owner aborts/reopens NOR/journal state.
 * Limits are inclusive counts; zero denies that operation, duration must be>0.
 * Deadline is checked before/after synchronous callbacks: it cannot interrupt
 * a chip operation already executing, but no subsequent callback is issued. */
jpeg_transport_result_t jpeg_transport_begin(jpeg_transport_t *transport,const jpeg_transport_limits_t *limits);
/* Cooperative deadline checkpoint for buffered RAM operations/decoder rows too. */
jpeg_transport_result_t jpeg_transport_check(jpeg_transport_t *transport);
void jpeg_transport_end(jpeg_transport_t *transport);
void jpeg_transport_revoke(jpeg_transport_t *transport);
/* Writable full-sector ports are restricted to verified ownership capabilities.
 * Readonly subfiles may also cover bounded asset payloads. Descriptors are copied.
 * Ports cannot be forged from HTTP addresses. Returned device is valid only for
 * this owner epoch; any failure/deadline invalidates ALL concurrent ports.
 * Device context borrows the port object: discard every old NOR/journal/device
 * borrower before reusing that object's memory. RAM caches also require the
 * owner's check/abort protocol; callback revocation only governs actual I/O. */
jpeg_transport_result_t jpeg_transport_port(jpeg_transport_t *transport,jpeg_transport_port_t *port,
    const jpeg_nor_extent_t *extents,unsigned count,bool writable,jpeg_nor_device_t *device);

#endif
