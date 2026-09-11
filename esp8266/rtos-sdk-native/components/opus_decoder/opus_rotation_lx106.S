/* Exact CELT exp_rotation1, stride=1 only, ESP8266 LX106 call0.
 * a2=X (DRAM int16), a3=len, a4=c, a5=s. vq.c keeps C for other strides.
 * Carry the just-written neighbour in a8. MUL16S takes its signed low half:
 * do not replace it with MULL without restoring EXTRACT16 semantics.
 * No stack, calls, allocation, IRQ masking, or additional IRAM.
 */
#include "opus_rotation.h"
#if YORADIO_OPUS_USE_LX106_ROTATION
    .section .text.yoradio_opus_exp_rotation1_stride1_lx106,"ax",@progbits
    .align 4
    .global yoradio_opus_exp_rotation1_stride1_lx106
    .type yoradio_opus_exp_rotation1_stride1_lx106,@function
yoradio_opus_exp_rotation1_stride1_lx106:
    blti a3, 2, .Lrotation_return
    mov a6, a2
    addi a3, a3, -1
    slli a3, a3, 1
    add a3, a2, a3
    neg a7, a5
    l16ui a8, a2, 0
.Lrotation_forward:
    l16ui a9, a2, 2
    mul16s a10, a8, a5
    mul16s a11, a9, a4
    mul16s a8, a8, a4
    mul16s a9, a9, a7
    add a10, a10, a11
    add a9, a8, a9
    addmi a10, a10, 0x4000
    addmi a9, a9, 0x4000
    srai a8, a10, 15
    srai a9, a9, 15
    s16i a8, a2, 2
    s16i a9, a2, 0
    addi a2, a2, 2
    bne a2, a3, .Lrotation_forward
    addi a2, a2, -4
    blt a2, a6, .Lrotation_return
    l16ui a8, a2, 2
.Lrotation_backward:
    l16ui a9, a2, 0
    mul16s a10, a9, a5
    mul16s a11, a8, a4
    mul16s a9, a9, a4
    mul16s a8, a8, a7
    add a10, a10, a11
    add a9, a9, a8
    addmi a10, a10, 0x4000
    addmi a9, a9, 0x4000
    srai a10, a10, 15
    srai a8, a9, 15
    s16i a10, a2, 2
    s16i a8, a2, 0
    addi a2, a2, -2
    bge a2, a6, .Lrotation_backward
.Lrotation_return:
    ret
    .size yoradio_opus_exp_rotation1_stride1_lx106, .-yoradio_opus_exp_rotation1_stride1_lx106
#endif
