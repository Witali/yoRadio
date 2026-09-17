# LX106 call0 leaf, hot clt_compute_allocation search loop.
# Input a3 = eBands+j, j in0..20 of aligned22-int16 standard-mode table.
# Outputs a2=sign_extend(p[1]), a11=sign_extend(p[0]); all other GPRs and SAR
# unchanged except CALL0's a0 return address (proven dead in caller).
# Aligned pair needs one L32I; crossing pair needs two, still within44B.
# No DRAM, extra stack, look-up table, approximate arithmetic or bitrate cap.
# This helper replaces TWO potentially emulated flash L16SI, not a timing claim.
.section .text.patch0,"ax",@progbits
.begin no-transform
 call0 ebands_pair
 nop
.end no-transform
.section .text.patch1,"ax",@progbits
.begin no-transform
 bbsi a3, 1, .Lcross
 l32i.n a2, a3, 0
 slli a11, a2, 16
 srai a11, a11, 16
 srai a2, a2, 16
 ret.n
.Lcross:
 addi a11, a3, -2
 l32i.n a11, a11, 0
 srai a11, a11, 16
 addi.n a2, a3, 2
 l32i.n a2, a2, 0
 slli a2, a2, 16
 srai a2, a2, 16
 ret.n
 .space 6,0
.end no-transform
