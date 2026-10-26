// Exclusive ownership of an immutable, exact Vorbis setup view.
#pragma once
#include "native_vorbis_setup.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct native_vorbis_setup_owner native_vorbis_setup_owner_t;

typedef struct {
    void *context;
    void *(*allocate)(void *context, size_t bytes);
    void (*release)(void *context, void *allocation);
} native_vorbis_setup_allocator_t;

typedef enum {
    NATIVE_VORBIS_SETUP_OWNER_OK = 0,
    NATIVE_VORBIS_SETUP_OWNER_INVALID = -1,
    NATIVE_VORBIS_SETUP_OWNER_RANGE = -2,
    NATIVE_VORBIS_SETUP_OWNER_TRUNCATED = -3,
    NATIVE_VORBIS_SETUP_OWNER_NO_MEMORY = -4
} native_vorbis_setup_owner_status_t;

// *owner starts NULL or is an exclusively owned live handle from this API.
// Parse complete type1/type5 packets and validate each object's byte size before
// allocation. Reuse the exact setup parser; header ordering, comments and BOS
// remain the caller's responsibility. Explicit bit extents use its packet rules.
// No input packet pointer is retained after success.
//
// On failure preserve *owner, all prior borrowed pointers and bytes. On success
// publish the new owner and release the previous one through its saved allocator;
// all previous borrows then expire. Replacement temporarily needs both owners.
// Allocate a control object and up to four actual-size arrays; skip empty arrays.
// No floating value table, expanded declared-entry table or format cap is added.
//
// The allocator is copied by value. Both callbacks are required; its context
// must outlive its owners. allocate returns NULL or fresh suitably aligned,
// disjoint storage, as malloc does. No callback receives a zero-size allocation
// or a NULL release. All input bytes stay immutable throughout the call.
// Inputs/allocator/handle storage must be disjoint from candidate allocations.
// Writable handle storage is also disjoint from both input packets, the
// allocator descriptor and existing owner allocations. Callbacks must not
// modify the handle directly.
// Callers serialize reads against replace/clear; callbacks cannot reenter these
// operations on the same handle. This is failure atomicity, not thread locking.
native_vorbis_setup_owner_status_t native_vorbis_setup_owner_replace(
    native_vorbis_setup_owner_t **owner,
    const uint8_t *identification, size_t identification_bytes, uint64_t identification_bits,
    const uint8_t *setup, size_t setup_bytes, uint64_t setup_bits,
    const native_vorbis_setup_allocator_t *allocator);

// Borrowed immutable view, valid until successful replacement or clear. NULL
// owner returns NULL. No packet storage or allocator descriptor is borrowed.
const native_vorbis_setup_t *native_vorbis_setup_owner_view(
    const native_vorbis_setup_owner_t *owner);

// End all borrows, clear the handle before callbacks, then release its arrays
// and control object through the original allocator. NULL arguments are no-ops.
void native_vorbis_setup_owner_clear(native_vorbis_setup_owner_t **owner);

#ifdef __cplusplus
}
#endif
