# LX106 decoder-only allocation-vector load: a5=byte address, a4=uint8 value.
# All other GPRs unchanged except CALL0 a0, immediately replaced by the
# existing eBands CALL0. SAR may change: every path overwrites it at the
# original SSL a14 (0x402484c0), before any variable shift or SAR read.
# That proof includes both paths of the intervening eBands leaf.
# One aligned flash L32I replaces L8UI; zero stack / DRAM growth.
# The final word ends at the existing single alignment byte, immediately
# before eband5ms. Its ignored upper byte cannot influence the uint8 result.
.section .text.patch0,"ax",@progbits
.begin no-transform
 call0 allocation_read_byte
.end no-transform
.section .text.patch1,"ax",@progbits
.begin no-transform
 ssa8l a5
 srli a4, a5, 2
 slli a4, a4, 2
 l32i.n a4, a4, 0
 srl a4, a4
 extui a4, a4, 0, 8
 ret.n
 .space 17,0
.end no-transform
