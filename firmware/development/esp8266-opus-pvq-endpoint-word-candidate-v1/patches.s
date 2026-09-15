# LX106 lower endpoint byte at a11 -> unsigned a11.
# Fixed jump continuation, not a CALL ABI: a0 saves SAR and is proven dead.
# Caller original return remains at sp+108; no RET, stack change or store.
# Upper endpoint reuses the accepted a10 CALL0 leaf after changing the ADD
# destination. Old a9 is overwritten by the very next SUB and is not read.
# Lower fragment occupies48 proven encoder-only bytes:26 live +22 padding.
.section .text.patch0,"ax",@progbits
.begin no-transform
.Lendpoint_start:
 rsr a0, sar
 ssa8l a11
 srli a11, a11, 2
 slli a11, a11, 2
 l32i.n a11, a11, 0
 srl a11, a11
 extui a11, a11, 0, 8
 wsr a0, sar
 j pvq_lower_continue
 .space 48-(.-.Lendpoint_start),0
.end no-transform

.section .text.patch1,"ax",@progbits
.begin no-transform
 add.n a10, a2, a6
.end no-transform
.section .text.patch2,"ax",@progbits
.begin no-transform
 call0 pvq_read_byte
.end no-transform
.section .text.patch3,"ax",@progbits
.begin no-transform
 j pvq_lower_word
.end no-transform
