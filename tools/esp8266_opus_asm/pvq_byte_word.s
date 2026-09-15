# LX106 call0 leaf byte-read helper for five PVQ search probes only.
# a10: byte address -> zero-extended byte. a11 clobbered, SAR restored.
# CALL0 clobbers a0; every caller has independently proven dead a0/a11.
# No stack frame, stores, tables, MMIO, prefetch or persistent RAM.
# The 57-byte encoder-only slot is not the existing sixth-probe stub.
.section .text.patch0,"ax",@progbits
.begin no-transform
helper_start:
 rsr a11, sar
 ssa8l a10
 srli a10, a10, 2
 slli a10, a10, 2
 l32i.n a10, a10, 0
 srl a10, a10
 extui a10, a10, 0, 8
 wsr a11, sar
 ret.n
 .space 57 - (. - helper_start), 0
.end no-transform

.section .text.patch1,"ax",@progbits
.begin no-transform
 call0 pvq_read_byte
.end no-transform

.section .text.patch2,"ax",@progbits
.begin no-transform
 call0 pvq_read_byte
.end no-transform

.section .text.patch3,"ax",@progbits
.begin no-transform
 call0 pvq_read_byte
.end no-transform

.section .text.patch4,"ax",@progbits
.begin no-transform
 call0 pvq_read_byte
.end no-transform

.section .text.patch5,"ax",@progbits
.begin no-transform
 call0 pvq_read_byte
.end no-transform
