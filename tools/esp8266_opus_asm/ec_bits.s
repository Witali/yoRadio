# Function: ec_dec_bits, common extraction tail from saved GCC ASM.
# ABI: LX106 call0. a2=ec_dec*, a3=bits (API0..25); return raw bits in a2.
# Entry a7=end_window, a4=nend_bits after the unchanged refill loop.
# Preserve a0/a1/a12..a15, all entropy writes and original final SAR=bits.
# a5/a9 are caller-saved scratch; other final registers remain identical.
# low = window XOR ((window >> bits) << bits), no separately built mask.
# No new RAM, stack, table, external call or bitrate/mode limitation.
# Frozen35-byte tail:33 live bytes plus2 unreachable bytes AFTER RET.
.section .text.patch0,"ax",@progbits
.begin no-transform
ec_bits_tail:
 l32i.n a6, a2, 20
 ssr a3
 srl a8, a7
 ssl a3
 sll a9, a8
 ssr a3 # Preserve original SAR before a3 becomes nbits_total.
 sub a4, a4, a3
 add.n a3, a6, a3
 s32i.n a8, a2, 12
 s32i.n a4, a2, 16
 s32i.n a3, a2, 20
 xor a2, a7, a9
 ret.n
 .space 35 - (. - ec_bits_tail), 0
.end no-transform
