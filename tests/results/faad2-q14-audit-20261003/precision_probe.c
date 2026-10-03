// Compile-time/assembly audit only; not a decoder or a firmware build.
#include <stdint.h>
#define INLINE inline
#include "fixed.h"
_Static_assert(sizeof(real_t)==4, "Q14 retains int32 storage");
_Static_assert(sizeof(float)==4, "float32 also occupies four bytes");
const uint32_t faad_precision_layout[]={REAL_BITS,COEF_BITS,FRAC_BITS,Q2_BITS,sizeof(real_t),2*sizeof(real_t),sizeof(float)};
real_t faad_q14_multiply(real_t a,real_t b) { return MUL_R(a,b); }
// Diagnostic only: demonstrate that a different constant shift does not
// select a narrower multiply. This is not a complete Q12 decoder build.
#undef REAL_BITS
#define REAL_BITS 12
real_t isolated_q12_multiply(real_t a,real_t b) { return MUL_R(a,b); }
