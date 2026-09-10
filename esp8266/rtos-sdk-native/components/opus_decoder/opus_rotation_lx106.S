/* Exact CELT exp_rotation1 for ESP8266 LX106, call0 ABI.
 * a2=X (byte-addressable DRAM int16), a3=len, a4=stride, a5=c, a6=s.
 * No calls, allocation, IRQ masking, or IRAM data access. MUL16S consumes
 * the signed low halfword; rounding and 32-bit wrap match fixed-point C.
 * Forward/backward dependencies must not be reordered or vectorized.
 */
#include "opus_rotation.h"
#if YORADIO_OPUS_USE_LX106_ROTATION
    .section .text.yoradio_opus_exp_rotation1_lx106,"ax",@progbits
    .align 4
    .global yoradio_opus_exp_rotation1_lx106
    .type yoradio_opus_exp_rotation1_lx106,@function
yoradio_opus_exp_rotation1_lx106:
    bge a4, a3, .Lrotation_return
    addi a1, a1, -16
    s32i a12, a1, 12
    s32i a13, a1, 8
    s32i a15, a1, 4
    sub a3, a3, a4
    sub a15, a3, a4
    slli a4, a4, 1
    add a7, a2, a4
    neg a8, a6
.Lrotation_forward:
    l16ui a9, a2, 0
    l16ui a10, a7, 0
    mul16s a11, a9, a6
    mul16s a12, a10, a5
    add a11, a11, a12
    mul16s a12, a9, a5
    mul16s a13, a10, a8
    add a12, a12, a13
    addmi a11, a11, 0x4000
    addmi a12, a12, 0x4000
    srai a11, a11, 15
    srai a12, a12, 15
    s16i a11, a7, 0
    s16i a12, a2, 0
    addi a2, a2, 2
    addi a7, a7, 2
    addi a3, a3, -1
    bnez a3, .Lrotation_forward
    blti a15, 1, .Lrotation_restore
    addi a7, a2, -2
    sub a2, a7, a4
.Lrotation_backward:
    l16ui a9, a2, 0
    l16ui a10, a7, 0
    mul16s a11, a9, a6
    mul16s a12, a10, a5
    add a11, a11, a12
    mul16s a12, a9, a5
    mul16s a13, a10, a8
    add a12, a12, a13
    addmi a11, a11, 0x4000
    addmi a12, a12, 0x4000
    srai a11, a11, 15
    srai a12, a12, 15
    s16i a11, a7, 0
    s16i a12, a2, 0
    addi a2, a2, -2
    addi a7, a7, -2
    addi a15, a15, -1
    bnez a15, .Lrotation_backward
.Lrotation_restore:
    l32i a12, a1, 12
    l32i a13, a1, 8
    l32i a15, a1, 4
    addi a1, a1, 16
.Lrotation_return:
    ret
    .size yoradio_opus_exp_rotation1_lx106, .-yoradio_opus_exp_rotation1_lx106
#endif
