# Generated frozen-layout Opus ASM reload experiment. Not production/default.
# LX106 call0: same destination values, a1/a12..a15/SAR and all memory preserved.
# Only private task stack reads are removed; no MMIO, shared or DMA memory.

# quant_partition: l32i a3, a1, 28 -> mov.n a3, a7 at 0x4024de5b
# Proven straight-line source: l32i a7, a1, 28; l32i a5, a1, 56; addi a3, a7, 1; slli a3, a3, 1; sub a2, a3, a2; l32i a3, a1, 28
.section .text.patch0,"ax",@progbits
.begin no-transform
mov.n a3, a7
.end no-transform

# quant_band: l32i a11, a1, 56 -> mov.n a11, a10 at 0x4024e478
# Proven straight-line source: l32i a10, a1, 56; l32i a11, a1, 56
.section .text.patch1,"ax",@progbits
.begin no-transform
mov.n a11, a10
.end no-transform

# quant_all_bands: l32i a9, a1, 280 -> or a9, a8, a8 at 0x40250897
# Proven straight-line source: l32i a8, a1, 280; slli a10, a10, 1; add a2, a2, a11; l32i a9, a1, 280
.section .text.patch2,"ax",@progbits
.begin no-transform
or a9, a8, a8
.end no-transform

# quant_all_bands: l32i a14, a1, 192 -> or a14, a12, a12 at 0x40250a98
# Proven straight-line source: l32i a12, a1, 192; l32i a14, a1, 192
.section .text.patch3,"ax",@progbits
.begin no-transform
or a14, a12, a12
.end no-transform

# opus_fft_impl: l32i a3, a1, 68 -> or a3, a11, a11 at 0x40253cda
# Proven straight-line source: l32i a11, a1, 68; l32i a3, a1, 68
.section .text.patch4,"ax",@progbits
.begin no-transform
or a3, a11, a11
.end no-transform

# opus_fft_impl: l32i a10, a1, 56 -> mov.n a10, a9 at 0x402540ab
# Proven straight-line source: l32i a9, a1, 56; l32i a10, a1, 56
.section .text.patch5,"ax",@progbits
.begin no-transform
mov.n a10, a9
.end no-transform

# opus_fft_impl: l32i a11, a1, 180 -> or a11, a10, a10 at 0x40254104
# Proven straight-line source: l32i a10, a1, 180; add a8, a8, a9; l32i a11, a1, 180
.section .text.patch6,"ax",@progbits
.begin no-transform
or a11, a10, a10
.end no-transform

# opus_fft_impl: l32i a3, a1, 32 -> mov.n a3, a2 at 0x40254128
# Proven straight-line source: l32i a2, a1, 32; l32i a3, a1, 32
.section .text.patch7,"ax",@progbits
.begin no-transform
mov.n a3, a2
.end no-transform
