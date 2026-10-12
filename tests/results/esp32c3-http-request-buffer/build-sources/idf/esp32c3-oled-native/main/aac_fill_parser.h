#pragma once
// Checked views of the pinned RV32 AAC FIL-reader ABI. No additional storage.
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

enum {
    AAC_FIL_COUNT_BITS=4, AAC_FIL_ESCAPE_BITS=8, AAC_FIL_ESCAPE_COUNT=15,
    AAC_FIL_EXTENSION_BITS=4, AAC_FIL_SBR=13, AAC_FIL_SBR_CRC=14,
    AAC_FIL_SBR_ELEMENTS=1, AAC_FIL_SBR_PAYLOAD_BYTES=1024
};

typedef struct __attribute__((__may_alias__)) {
    uint8_t *buffer;
    uint32_t used_bits, available_bits, input_length;
    int32_t alignment_offset;
} aac_fill_bits_t;

typedef struct __attribute__((__may_alias__)) {
    int32_t element_id, extension_type, payload_bytes;
    uint8_t payload[AAC_FIL_SBR_PAYLOAD_BYTES];
} aac_fill_element_t;

typedef struct __attribute__((__may_alias__)) {
    int32_t elements, core_elements;
    aac_fill_element_t element[AAC_FIL_SBR_ELEMENTS];
} aac_fill_stream_t;

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(aac_fill_bits_t)==20, "Pinned BITS size");
_Static_assert(offsetof(aac_fill_bits_t,used_bits)==4, "Pinned BITS cursor");
_Static_assert(offsetof(aac_fill_bits_t,available_bits)==8, "Pinned BITS limit");
_Static_assert(offsetof(aac_fill_bits_t,input_length)==12, "Pinned BITS bytes");
_Static_assert(offsetof(aac_fill_bits_t,alignment_offset)==16, "Pinned BITS alignment");
#endif
_Static_assert(sizeof(aac_fill_element_t)==1036, "Pinned SBR element size");
_Static_assert(offsetof(aac_fill_element_t,payload)==12, "Pinned SBR payload");
_Static_assert(sizeof(aac_fill_stream_t)==1044, "Pinned SBR stream size");
_Static_assert(offsetof(aac_fill_stream_t,element)==8, "Pinned SBR element offset");

// Called after ID_FIL, at its count field. Invalid spans move the cursor to
// the exact byte end, where the native controller emits its normal input error.
// No part of an invalid SBR element is published. Valid data matches the SDK.
bool aac_fill_skip(aac_fill_bits_t *bits);
bool aac_fill_sbr(aac_fill_stream_t *stream,aac_fill_bits_t *bits);
