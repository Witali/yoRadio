# Combined exact LX106 call0 micro-optimizations; C fallback unchanged.
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

# opus_fft_impl: load a complex PCM value using a single private-stack pointer.
# LX106 call0 ABI: a2/a3 receive exactly the original r/i words; all other
# registers, a1, SAR and memory remain unchanged. No call, spill or new buffer.
# Original: four narrow loads (8 bytes), two reading the same private sp+32.
# New: three loads (3+2+3 bytes), keeping all later code/literal addresses fixed.
# The data reads remain in r-then-i order. No padding is executed.
.section .text.patch1,"ax",@progbits
.begin no-transform
    l32i a3, a1, 32
    l32i.n a2, a3, 0
    l32i a3, a3, 4
.end no-transform

# clt_mdct_backward_c: both operands sign-extended16 on every CFG path.
# MULL -> MUL16S: same exact int32 product, destination, 3-byte width and SAR.
# No extra register, call, spill, buffer or stack. Unsigned low16 stays MULL.

# 0x402472a8: mull a7, a10, a8; signed widths 16,16
.section .text.patch2,"ax",@progbits
.begin no-transform
 mul16s a7, a10, a8
.end no-transform

# 0x402472b6: mull a11, a9, a4; signed widths 16,16
.section .text.patch3,"ax",@progbits
.begin no-transform
 mul16s a11, a9, a4
.end no-transform

# 0x402472c6: mull a4, a10, a4; signed widths 16,16
.section .text.patch4,"ax",@progbits
.begin no-transform
 mul16s a4, a10, a4
.end no-transform

# 0x402472cc: mull a8, a8, a9; signed widths 16,16
.section .text.patch5,"ax",@progbits
.begin no-transform
 mul16s a8, a8, a9
.end no-transform

# 0x402473e4: mull a10, a5, a7; signed widths 16,16
.section .text.patch6,"ax",@progbits
.begin no-transform
 mul16s a10, a5, a7
.end no-transform

# 0x402473f2: mull a13, a6, a2; signed widths 16,16
.section .text.patch7,"ax",@progbits
.begin no-transform
 mul16s a13, a6, a2
.end no-transform

# 0x40247402: mull a2, a5, a2; signed widths 16,16
.section .text.patch8,"ax",@progbits
.begin no-transform
 mul16s a2, a5, a2
.end no-transform

# 0x40247408: mull a7, a7, a6; signed widths 16,16
.section .text.patch9,"ax",@progbits
.begin no-transform
 mul16s a7, a7, a6
.end no-transform

# 0x4024744f: mull a7, a4, a8; signed widths 16,16
.section .text.patch10,"ax",@progbits
.begin no-transform
 mul16s a7, a4, a8
.end no-transform

# 0x4024745d: mull a13, a5, a6; signed widths 16,16
.section .text.patch11,"ax",@progbits
.begin no-transform
 mul16s a13, a5, a6
.end no-transform

# 0x4024746d: mull a8, a8, a5; signed widths 16,16
.section .text.patch12,"ax",@progbits
.begin no-transform
 mul16s a8, a8, a5
.end no-transform

# 0x40247473: mull a6, a4, a6; signed widths 16,16
.section .text.patch13,"ax",@progbits
.begin no-transform
 mul16s a6, a4, a6
.end no-transform

# 0x402474ef: mull a10, a8, a5; signed widths 16,16
.section .text.patch14,"ax",@progbits
.begin no-transform
 mul16s a10, a8, a5
.end no-transform

# 0x40247502: mull a13, a7, a14; signed widths 16,16
.section .text.patch15,"ax",@progbits
.begin no-transform
 mul16s a13, a7, a14
.end no-transform

# 0x40247508: mull a14, a14, a8; signed widths 16,16
.section .text.patch16,"ax",@progbits
.begin no-transform
 mul16s a14, a14, a8
.end no-transform

# 0x4024750e: mull a5, a7, a5; signed widths 16,16
.section .text.patch17,"ax",@progbits
.begin no-transform
 mul16s a5, a7, a5
.end no-transform
