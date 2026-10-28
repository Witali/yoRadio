#ifndef SMALL_TV_JPEG_GUARD_H
#define SMALL_TV_JPEG_GUARD_H

#include "jpeg_nor.h"

#define JPEG_GUARD_MAX_PARTITIONS 8u
#define JPEG_GUARD_MAX_RESOURCES 32u
#define JPEG_GUARD_READ_BYTES 256u

typedef struct {
    char label[16];
    uint32_t offset, bytes, flags;
    uint8_t type, subtype;
} jpeg_guard_partition_t;

typedef struct {
    uint32_t offset, bytes;
    uint8_t sha256[32];
} jpeg_guard_resource_t;

/* Generated, const build inputs, never descriptors received from HTTP.
 * The planner proves which payloads are immutable and which full sectors it
 * owns. The guard checks the actual boot partition map and those payloads.
 * The generated resource list includes an ownership stamp in protected padding;
 * the matching prepared assets.bin must ship together with these descriptors.
 * layout_id is also the future cache journal's build/layout identity. */
typedef struct {
    uint32_t flash_bytes;
    const jpeg_guard_partition_t *partitions;
    unsigned partition_count, assets_partition;
    const jpeg_nor_extent_t *allowed, *protected_ranges;
    unsigned allowed_count, protected_count;
    const jpeg_guard_resource_t *resources;
    unsigned resource_count;
    uint8_t layout_id[32];
} jpeg_guard_layout_t;

/* Streaming SHA-256 provider, e.g. ESP-IDF mbedTLS. No new cryptographic
 * implementation is needed here. reset releases provider state after EVERY
 * begin attempt, including success and partial begin/update/finish failures.
 * Each callback returns 0 on success. Hash state is owned by the caller. */
typedef struct {
    void *context;
    int (*begin)(void *context);
    int (*update)(void *context, const void *data, size_t bytes);
    int (*finish)(void *context, uint8_t digest[32]);
    void (*reset)(void *context);
} jpeg_guard_sha256_t;

typedef enum {
    JPEG_GUARD_OK = 0,
    JPEG_GUARD_ARGUMENT,
    JPEG_GUARD_LAYOUT,
    JPEG_GUARD_RESOURCE,
    JPEG_GUARD_IO,
    JPEG_GUARD_HASH
} jpeg_guard_result_t;

/* Read-only, fail-closed verification before granting any NOR write capability.
 * No partial success or cached authorization escapes a failed call. The owner
 * serializes verification with all media writes and authorizes a boot session
 * only after OK. Reverify after resource/partition replacement; close all old
 * handles first. This detects build/layout mismatch, not hostile firmware or
 * authenticated assets. The observed table must enumerate ALL boot partitions,
 * sorted by offset, with label/type/subtype/offset/size/flags preserved.
 * Guard reads only immutable payloads, never user photos, scratch or settings.
 * No program/erase callback is called, even on failure. */
jpeg_guard_result_t jpeg_guard_verify(const jpeg_guard_layout_t *layout,
    const jpeg_guard_partition_t *observed, unsigned observed_count,
    const jpeg_nor_device_t *device, const jpeg_guard_sha256_t *sha256);

#endif
