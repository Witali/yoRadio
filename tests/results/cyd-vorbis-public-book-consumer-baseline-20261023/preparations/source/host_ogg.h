/* Owned host bitreader types only. No target or external decoder ABI claim. */
#pragma once
#include <stdint.h>
#include <limits.h>
typedef int32_t ogg_int32_t;
typedef uint32_t ogg_uint32_t;
typedef uint16_t ogg_uint16_t;
typedef struct { unsigned owned_tag; } oggpack_buffer;
_Static_assert(CHAR_BIT == 8 && sizeof(int) == 4 && sizeof(ogg_int32_t) == 4, "host 32-bit public arithmetic");
