# Experimental clt_mdct_backward_c pre-rotation for Xtensa LX106 call0.
# Original96-byte frame saves a0 at sp+92 and a12..a15 at sp+88..76.
# No call inside this loop. a0/a14/a15 cache immutable bitrev/t0/t1 words.
# The standard mode has even N4 and word-aligned tables: one shared parity.
# a12=bitrev, a13=t1, sp+32=-2*N4, a3=xp1, sp+4=xp2, sp+12=yp.
# Low iteration loads words; high iteration reuses signed high halves.
# No halfword load, extra RAM, new spill, SAR change or PCM approximation.
# yr additions reassociated modulo2^32, each MULL/SRAI rounding unchanged.
# a9 is restored to yp each iteration; original tail restores a15 from a9
# before FFT CALL0. Original function epilogue restores saved ABI registers.
# All PCM reads/writes retain their order (including possible in-place data).
# C fallback and original saved GCC ASM remain unchanged.
.section .text.patch0,"ax",@progbits
.begin no-transform
.Lloop:
bbsi a12, 1, .Lhigh
l32i.n a7, a1, 32
add.n a4, a7, a13
l32i.n a14, a4, 0
l32i.n a15, a13, 0
l32i.n a0, a12, 0
slli a10, a14, 16
srai a10, a10, 16
slli a9, a15, 16
srai a9, a9, 16
slli a6, a0, 16
srai a6, a6, 16
j .Larithmetic
.Lhigh:
srai a10, a14, 16
srai a9, a15, 16
srai a6, a0, 16
.Larithmetic:
l32i a8, a1, 4
l32i a5, a3, 0
l32i a2, a8, 0
srai a4, a5, 16
srai a8, a2, 16
extui a5, a5, 0, 16
extui a2, a2, 0, 16
# yr = MULT16_32_Q15(t0,xp2) + MULT16_32_Q15(t1,xp1).
# Sequential accumulation frees a14/a15 without widening any arithmetic.
mull a7, a10, a8
slli a7, a7, 1
mull a11, a10, a2
srai a11, a11, 15
add.n a7, a7, a11
mull a11, a9, a4
slli a11, a11, 1
add.n a7, a7, a11
mull a11, a9, a5
srai a11, a11, 15
add.n a7, a7, a11
# yi = MULT16_32_Q15(t0,xp1) - MULT16_32_Q15(t1,xp2).
mull a4, a10, a4
mull a5, a10, a5
mull a8, a8, a9
mull a2, a9, a2
srai a5, a5, 15
srai a2, a2, 15
slli a4, a4, 1
slli a8, a8, 1
l32i.n a9, a1, 12
add.n a4, a4, a5
add.n a8, a8, a2
slli a6, a6, 3
add.n a6, a9, a6
sub a4, a4, a8
l32i.n a2, a1, 4
s32i.n a4, a6, 0
l32i.n a4, a1, 24
l32i.n a10, a1, 8
add.n a2, a2, a4
l32i.n a5, a1, 28
s32i.n a7, a6, 4
addi.n a12, a12, 2
s32i.n a2, a1, 4
add.n a3, a3, a10
addi.n a13, a13, 2
beq a5, a12, .Lend
j .Lloop
# Padding is unreachable: preserve every other linked byte/address.
.space 193-(.-.Lloop), 0
.Lend:
.end no-transform
