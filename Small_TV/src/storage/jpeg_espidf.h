#ifndef SMALL_TV_JPEG_ESPIDF_H
#define SMALL_TV_JPEG_ESPIDF_H

#include "jpeg_transport.h"
#include "esp_err.h"
#include "psa/crypto.h"

typedef struct {
    jpeg_transport_t transport;
    psa_hash_operation_t hash;
    uint32_t physical_bytes, configured_bytes;
    uint64_t discovery_us;
    int discovery_error;
} jpeg_espidf_t;

/* Zero-initialize once. Init only discovers geometry/initializes existing PSA
 * crypto; it does not authorize or modify flash. No private SHA implementation. */
esp_err_t jpeg_espidf_init(jpeg_espidf_t *storage);
/* Borrow the same PSA provider after initialization. Owner serialization is
 * mandatory; abort every hash/cache borrower before reusing this hash state. */
jpeg_guard_sha256_t jpeg_espidf_hash_provider(jpeg_espidf_t *storage);
/* Read/verify the complete raw partition table (including original flags and
 * MD5), cross-check ALL SDK partitions, then perform resource/stamp guard.
 * Discovery's one3072-byte read/call and elapsed time are subtracted from the
 * startup limits. Write permission remains revoked until complete success.
 * Owner must serialize with all media/resource/partition replacement. */
jpeg_transport_result_t jpeg_espidf_authorize(jpeg_espidf_t *storage,
    const jpeg_guard_layout_t *layout,const jpeg_transport_limits_t *startup_limits);

#endif
