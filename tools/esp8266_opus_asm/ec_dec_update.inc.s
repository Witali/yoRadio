# Optimization of GCC8.4/O3 ec_dec_update from gcc/upstream/celt/entdec.c.s.
# Purpose: commit a decoded range [fl,fh), normalize rng, refill packet bytes.
# Args: a2=ec_dec* (48-byte DRAM state), a3=fl, a4=fh, a5=ft; returns void.
# Preconditions: 0<=fl<fh<=ft; ext from ec_decode; packet does not alias state.
# Registers: a2=context, a3=rng, a4=val, a5=temp, a6=packet,
# a7=offset, a8=storage, a9=rem, a10=total bits, a11=normalization threshold.
# Changes relative to GCC: join the real-byte and zero-padding paths before
# computing val; hoist packet pointer; retain state in registers until exit;
# use only caller-saved registers (remove 16-byte frame and 8 save/restore ops).
# No allocation, narrow IRAM access, 64-bit arithmetic, new lookup table or
# interrupt masking. End-of-packet zero padding does NOT advance offs.
# Arithmetic: uint32 wrap, complement low 8 bits, mask val to 31 bits exactly.
# This is a candidate, not a measured speed improvement. See validation report.
ec_dec_update:
    l32i.n a6, a2, 36
    sub a5, a5, a4
    mull a5, a5, a6
    l32i.n a7, a2, 32
    sub a7, a7, a5
    beqz.n a3, .Lasm_update_zero
    sub a3, a4, a3
    mull a3, a3, a6
    j .Lasm_update_start
.Lasm_update_zero:
    l32i.n a3, a2, 28
    sub a3, a3, a5
.Lasm_update_start:
    mov.n a4, a7
    movi.n a11, 1
    slli a11, a11, 23
    bltu a11, a3, .Lasm_update_done
    l32i.n a6, a2, 0
    l32i.n a7, a2, 24
    l32i.n a8, a2, 4
    l32i.n a9, a2, 40
    l32i.n a10, a2, 20
.Lasm_update_loop:
    slli a5, a9, 8
    movi.n a9, 0
    bgeu a7, a8, .Lasm_update_padding
    add.n a9, a6, a7
    l8ui a9, a9, 0
    addi.n a7, a7, 1
.Lasm_update_padding:
    or a5, a5, a9
    extui a5, a5, 1, 8
    slli a4, a4, 8
    sub a4, a4, a5
    addmi a4, a4, 256
    addi.n a4, a4, -1
    slli a4, a4, 1
    srli a4, a4, 1
    slli a3, a3, 8
    addi.n a10, a10, 8
    bgeu a11, a3, .Lasm_update_loop
    s32i.n a7, a2, 24
    s32i.n a9, a2, 40
    s32i.n a10, a2, 20
.Lasm_update_done:
    s32i.n a3, a2, 28
    s32i.n a4, a2, 32
    ret.n
