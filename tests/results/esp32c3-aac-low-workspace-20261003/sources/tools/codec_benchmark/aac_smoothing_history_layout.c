// Compile for RV32, with AAC_SMOOTHING_HISTORY_FOUR defined.
#include "aac_high_abi_layout.c"
enum { AAC_RV32_POSITIVE_IMM_MAX=2047 };
#define MATRIX(name, expression) const uint32_t aac_abi_##name[2]={ \
    expression(aac_sbr_frame_abi_t),expression(aac_high_frame_t) }
#define MATRIX_SIZE(type) sizeof(((type *)0)->gain_mantissa)
#define GAIN_EXP_TAIL(type) (offsetof(type,gain_exponent)-offsetof(type,gain_mantissa)-AAC_RV32_POSITIVE_IMM_MAX)
#define NOISE_EXP_TAIL(type) (offsetof(type,noise_exponent)-offsetof(type,gain_mantissa)-AAC_RV32_POSITIVE_IMM_MAX)
MATRIX(matrix_size,MATRIX_SIZE);
MATRIX(gain_exponent_tail,GAIN_EXP_TAIL);
MATRIX(noise_exponent_tail,NOISE_EXP_TAIL);
