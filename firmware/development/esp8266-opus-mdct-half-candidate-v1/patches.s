# MDCT signed-half selection, saved GCC ASM / Xtensa LX106 call0.
# Same17-byte slots; registers, SAR, aligned L32I accesses, stack96 and all other code unchanged.
# Preserve mask=2. High half:3 instructions instead of6; low:5 instead of4.
# No new alignment/size assumptions; works for either half including signed extremes.
# Baseline C and GCC snapshot unchanged; this post-link diagnostic is OFF by default.

# clt_mdct_backward_c: pointer a4, loaded word a2, result a10.
.section .text.patch0,"ax",@progbits
.begin no-transform
movi.n a9, 2
bbsi a4, 1, .Lhigh0
slli a10, a2, 16
srai a10, a10, 16
j .Lend0
.Lhigh0:
srai a10, a2, 16
.Lend0:
.end no-transform

# clt_mdct_backward_c: pointer a13, loaded word a2, result a9.
.section .text.patch1,"ax",@progbits
.begin no-transform
movi.n a4, 2
bbsi a13, 1, .Lhigh1
slli a9, a2, 16
srai a9, a9, 16
j .Lend1
.Lhigh1:
srai a9, a2, 16
.Lend1:
.end no-transform

# clt_mdct_backward_c: pointer a12, loaded word a2, result a6.
.section .text.patch2,"ax",@progbits
.begin no-transform
movi.n a7, 2
bbsi a12, 1, .Lhigh2
slli a6, a2, 16
srai a6, a6, 16
j .Lend2
.Lhigh2:
srai a6, a2, 16
.Lend2:
.end no-transform

# clt_mdct_backward_c: pointer a9, loaded word a5, result a8.
.section .text.patch3,"ax",@progbits
.begin no-transform
movi.n a10, 2
bbsi a9, 1, .Lhigh3
slli a8, a5, 16
srai a8, a8, 16
j .Lend3
.Lhigh3:
srai a8, a5, 16
.Lend3:
.end no-transform

# clt_mdct_backward_c: pointer a11, loaded word a5, result a7.
.section .text.patch4,"ax",@progbits
.begin no-transform
movi.n a6, 2
bbsi a11, 1, .Lhigh4
slli a7, a5, 16
srai a7, a7, 16
j .Lend4
.Lhigh4:
srai a7, a5, 16
.Lend4:
.end no-transform
