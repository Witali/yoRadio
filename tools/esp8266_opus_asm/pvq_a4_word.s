# LX106 call0 leaf for the two remaining a4 PVQ byte probes.
# a4 byte address -> zero-extended byte; a11 clobbered, SAR restored.
# a0 is dead at both continuations and original return lives at sp+108.
# Reuse25 bytes of existing unreachable padding after the first helper's RET.
# No stack, stores, new table/RAM or movement of any outside instruction.
.section .text.patch0,"ax",@progbits
.begin no-transform
 rsr a11, sar
 ssa8l a4
 srli a4, a4, 2
 slli a4, a4, 2
 l32i.n a4, a4, 0
 srl a4, a4
 extui a4, a4, 0, 8
 wsr a11, sar
 ret.n
.end no-transform

.section .text.patch1,"ax",@progbits
.begin no-transform
 call0 pvq_read_a4
.end no-transform
.section .text.patch2,"ax",@progbits
.begin no-transform
 call0 pvq_read_a4
.end no-transform
