# Final three adjacent eBands pairs in inlined interp_bits2pulses.
# Standard mode: p=eBands+2*j, 0<=j<21; exact SIGNED int16 results.
# No stack, no SAR access, no GPR changes except lo/hi and caller-dead a0.
# Leaf0: p=a4, lo=a10, hi=a3. Preserve the live multiplier in a2.
# Leaf1: p=a12, lo=a4, hi=a2. Leaf2: p=a6, lo=a2, hi=a7.
# Leaf2 is split across two decoder-dead areas; branch directly to cross2.
# Each path ends in RET, never falls through into another accepted helper.
.section .text.patch0,"ax",@progbits
.begin no-transform
 call0 ebands_final0
 nop
.end no-transform
.section .text.patch1,"ax",@progbits
.begin no-transform
 call0 ebands_final1
 nop
.end no-transform
.section .text.patch2,"ax",@progbits
.begin no-transform
 call0 ebands_final2
 nop
.end no-transform
.section .text.patch3,"ax",@progbits
.begin no-transform
 bbsi a4, 1, .Lcross0
 l32i.n a3, a4, 0
 slli a10, a3, 16
 srai a10, a10, 16
 srai a3, a3, 16
 ret.n
.Lcross0:
 addi a10, a4, -2
 l32i.n a10, a10, 0
 srai a10, a10, 16
 addi.n a3, a4, 2
 l32i.n a3, a3, 0
 slli a3, a3, 16
 srai a3, a3, 16
 ret.n
.end no-transform
.section .text.patch4,"ax",@progbits
.begin no-transform
 bbsi a12, 1, .Lcross1
 l32i.n a2, a12, 0
 slli a4, a2, 16
 srai a4, a4, 16
 srai a2, a2, 16
 ret.n
.Lcross1:
 addi a4, a12, -2
 l32i.n a4, a4, 0
 srai a4, a4, 16
 addi.n a2, a12, 2
 l32i.n a2, a2, 0
 slli a2, a2, 16
 srai a2, a2, 16
 ret.n
.end no-transform
.section .text.patch5,"ax",@progbits
.begin no-transform
 bbsi a6, 1, ebands_final_cross2
 l32i.n a7, a6, 0
 slli a2, a7, 16
 srai a2, a2, 16
 srai a7, a7, 16
 ret.n
.end no-transform
.section .text.patch6,"ax",@progbits
.begin no-transform
 addi a2, a6, -2
 l32i.n a2, a2, 0
 srai a2, a2, 16
 addi.n a7, a6, 2
 l32i.n a7, a7, 0
 slli a7, a7, 16
 srai a7, a7, 16
 ret.n
.end no-transform
