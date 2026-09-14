# clt_mdct_backward_c signed16 products, Xtensa LX106 call0.
# Both operands sign-extended16 on every CFG path; product fits int32.
# MULL -> MUL16S keeps all32 result bits, same3-byte width and destination.
# No changed loads/stores/branches/SAR/ABI/frame, no new RAM or bitrate limit.
# Unsigned low16 products intentionally remain MULL. C fallback unchanged.

# 0x402472a8: mull a7, a10, a8; operand signed widths 16,16
.section .text.patch0,"ax",@progbits
.begin no-transform
mul16s a7, a10, a8
.end no-transform

# 0x402472b6: mull a11, a9, a4; operand signed widths 16,16
.section .text.patch1,"ax",@progbits
.begin no-transform
mul16s a11, a9, a4
.end no-transform

# 0x402472c6: mull a4, a10, a4; operand signed widths 16,16
.section .text.patch2,"ax",@progbits
.begin no-transform
mul16s a4, a10, a4
.end no-transform

# 0x402472cc: mull a8, a8, a9; operand signed widths 16,16
.section .text.patch3,"ax",@progbits
.begin no-transform
mul16s a8, a8, a9
.end no-transform

# 0x402473d7: mull a10, a5, a7; operand signed widths 16,16
.section .text.patch4,"ax",@progbits
.begin no-transform
mul16s a10, a5, a7
.end no-transform

# 0x402473dd: mull a13, a6, a2; operand signed widths 16,16
.section .text.patch5,"ax",@progbits
.begin no-transform
mul16s a13, a6, a2
.end no-transform

# 0x402473e3: mull a2, a5, a2; operand signed widths 16,16
.section .text.patch6,"ax",@progbits
.begin no-transform
mul16s a2, a5, a2
.end no-transform

# 0x402473f7: mull a7, a7, a6; operand signed widths 16,16
.section .text.patch7,"ax",@progbits
.begin no-transform
mul16s a7, a7, a6
.end no-transform

# 0x4024745a: mull a7, a4, a8; operand signed widths 16,16
.section .text.patch8,"ax",@progbits
.begin no-transform
mul16s a7, a4, a8
.end no-transform

# 0x40247460: mull a13, a5, a6; operand signed widths 16,16
.section .text.patch9,"ax",@progbits
.begin no-transform
mul16s a13, a5, a6
.end no-transform

# 0x40247466: mull a8, a8, a5; operand signed widths 16,16
.section .text.patch10,"ax",@progbits
.begin no-transform
mul16s a8, a8, a5
.end no-transform

# 0x4024746c: mull a6, a4, a6; operand signed widths 16,16
.section .text.patch11,"ax",@progbits
.begin no-transform
mul16s a6, a4, a6
.end no-transform

# 0x402474ef: mull a10, a8, a5; operand signed widths 16,16
.section .text.patch12,"ax",@progbits
.begin no-transform
mul16s a10, a8, a5
.end no-transform

# 0x40247502: mull a13, a7, a14; operand signed widths 16,16
.section .text.patch13,"ax",@progbits
.begin no-transform
mul16s a13, a7, a14
.end no-transform

# 0x40247508: mull a14, a14, a8; operand signed widths 16,16
.section .text.patch14,"ax",@progbits
.begin no-transform
mul16s a14, a14, a8
.end no-transform

# 0x4024750e: mull a5, a7, a5; operand signed widths 16,16
.section .text.patch15,"ax",@progbits
.begin no-transform
mul16s a5, a7, a5
.end no-transform
