# Two additional clt_compute_allocation loops, standard eBands (22 int16).
# Input a5=p, p=eBands+j, j=0..20. No stack or SAR access.
# First leaf: a2=sign16(p[0]), a3=sign16(p[1]).
# Second leaf: a2=sign16(p[0]), a7=sign16(p[1]).
# Other registers unchanged except caller-dead a0 written by CALL0.
# The intervening stack load at the second site is preserved after the leaf.
# Existing search-loop helper and exp2 table remain byte-for-byte intact.
.section .text.patch0,"ax",@progbits
.begin no-transform
 call0 ebands_init
 nop
.end no-transform
.section .text.patch1,"ax",@progbits
.begin no-transform
 call0 ebands_interp
 l32i a14, a1, 68
 nop
.end no-transform
.section .text.patch2,"ax",@progbits
.begin no-transform
 bbsi a5, 1, .Linit_cross
 l32i.n a3, a5, 0
 slli a2, a3, 16
 srai a2, a2, 16
 srai a3, a3, 16
 ret.n
.Linit_cross:
 addi a2, a5, -2
 l32i.n a2, a2, 0
 srai a2, a2, 16
 addi.n a3, a5, 2
 l32i.n a3, a3, 0
 slli a3, a3, 16
 srai a3, a3, 16
 ret.n
.end no-transform
.section .text.patch3,"ax",@progbits
.begin no-transform
 bbsi a5, 1, .Linterp_cross
 l32i.n a7, a5, 0
 slli a2, a7, 16
 srai a2, a2, 16
 srai a7, a7, 16
 ret.n
.Linterp_cross:
 addi a2, a5, -2
 l32i.n a2, a2, 0
 srai a2, a2, 16
 addi.n a7, a5, 2
 l32i.n a7, a7, 0
 slli a7, a7, 16
 srai a7, a7, 16
 ret.n
.end no-transform
