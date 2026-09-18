# Experimental branchless signed pair at the existing ebands_init entry.
# LX106 call0 leaf: a5 = eBands+2*j, j=0..20; a2=p[0], a3=p[1].
# Other GPRs unchanged, no stack. SAR is dead until caller SSL a4.
# Load align(p) and align(p+2), NOT align(p)+4: the last pair must
# remain within the 44-byte table. An even pair reads one word twice.
# SSA8L sets SAR=8*(p&3); SRC concatenates high||low and shifts right.
# Both outputs remain signed16, not just the currently positive table.
.section .text.patch0,"ax",@progbits
.begin no-transform
ebands_src_start:
 ssa8l a5
 movi.n a2, -4
 addi.n a3, a5, 2
 and a3, a3, a2
 and a2, a5, a2
 l32i.n a3, a3, 0
 l32i.n a2, a2, 0
 src a3, a3, a2
 slli a2, a3, 16
 srai a2, a2, 16
 srai a3, a3, 16
 ret.n
 .space 36 - (. - ebands_src_start), 0
.end no-transform
