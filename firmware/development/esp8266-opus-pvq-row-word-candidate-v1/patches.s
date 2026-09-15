# LX106 private CALL0 leaf: row-length byte at a2 -> unsigned a6.
# Preserve source a2 and SAR; a11 scratch and a0 return are proven dead.
# Original quant_partition return was saved to sp+108 before the call site.
# Reuse27 bytes proven encoder-only for every valid decoder input.
# First25 bytes live, RET before2 zero padding. No RAM/table/stack growth.
.section .text.patch0,"ax",@progbits
.begin no-transform
.Lrow_start:
 rsr a11, sar
 ssa8l a2
 srli a6, a2, 2
 slli a6, a6, 2
 l32i.n a6, a6, 0
 srl a6, a6
 extui a6, a6, 0, 8
 wsr a11, sar
 ret.n
 .space 27-(.-.Lrow_start),0
.end no-transform

.section .text.patch1,"ax",@progbits
.begin no-transform
 call0 pvq_read_row
.end no-transform
