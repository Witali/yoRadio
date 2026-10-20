#ifndef SMALL_TV_JPEG_COEFFICIENTS_H
#define SMALL_TV_JPEG_COEFFICIENTS_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* REQUESTED_CHANGE: reversible temporary-store representation, not JPEG input
 * compression. Input/output coefficients use native signed16, storage uses LE16.
 * Each 8x8 block starts with DC. DC keeps two's-complement bits; AC uses signed
 * magnitude (negative zero encodes INT16_MIN). Complement both so zero is FF.
 * Valid progressive DC refinements OR bits; AC refinements add magnitude bits.
 * Their stored transitions can therefore program1->0, without sector erase.
 * All65536 values remain reversible, including adversarial intermediate data.
 * bytes/offset must be even and fit uint32. Buffers may be identical or disjoint;
 * invalid whole requests leave output untouched. No allocation or global state. */
bool jpeg_coefficients_pack(void *output,const void *input,size_t bytes,uint32_t offset);
bool jpeg_coefficients_unpack(void *output,const void *input,size_t bytes,uint32_t offset);

#endif
