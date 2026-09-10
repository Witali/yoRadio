#ifndef YORADIO_OPUS_ROTATION_H
#define YORADIO_OPUS_ROTATION_H
#ifndef YORADIO_OPUS_ROTATION_LX106
#define YORADIO_OPUS_ROTATION_LX106 0
#endif
#if YORADIO_OPUS_ROTATION_LX106 != 0 && YORADIO_OPUS_ROTATION_LX106 != 1
#error "YORADIO_OPUS_ROTATION_LX106 must be 0 or 1"
#endif
#if YORADIO_OPUS_ROTATION_LX106 && defined(__XTENSA__)
#include <xtensa/config/core-isa.h>
#if XCHAL_HAVE_MUL16 && !XCHAL_HAVE_WINDOWED && XCHAL_NUM_AREGS == 16
#define YORADIO_OPUS_USE_LX106_ROTATION 1
#endif
#endif
#ifndef YORADIO_OPUS_USE_LX106_ROTATION
#define YORADIO_OPUS_USE_LX106_ROTATION 0
#endif
#if YORADIO_OPUS_USE_LX106_ROTATION && !defined(__ASSEMBLER__) && defined(YORADIO_OPUS_BOUNDED) && defined(FIXED_POINT)
/* Enabled only by the ESP8266 component. Other architectures keep C even
 * when the experiment flag is supplied to a portable host build. */
#define OVERRIDE_vq_exp_rotation1
void yoradio_opus_exp_rotation1_lx106(celt_norm *X, int len, int stride,
                                     opus_val16 c, opus_val16 s);
#define exp_rotation1 yoradio_opus_exp_rotation1_lx106
#endif
#endif
