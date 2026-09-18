# Experimental quant_all_bands private flag loads, native decoder only.
# LX106 call0 ABI: original384-byte frame, every instruction address retained.
# ctx.encode=0 / ctx.resynth=1 proven at each reachable read after initialization.
# MOVI writes the same destination; no SAR, memory write, branch or call changes.
# Original GCC snapshot and C fallback are unchanged. No added RAM or scratch.

# 0x40250e92: l32i a10, a1, 32; private SP+32, immutable 0
.section .text.patch0,"ax",@progbits
.begin no-transform
movi.n a10, 0
.end no-transform

# 0x40250ede: l32i a4, a1, 36; private SP+36, immutable 1
.section .text.patch1,"ax",@progbits
.begin no-transform
movi a4, 1
.end no-transform

# 0x40250ef3: l32i a2, a1, 36; private SP+36, immutable 1
.section .text.patch2,"ax",@progbits
.begin no-transform
movi.n a2, 1
.end no-transform

# 0x4025146c: l32i a10, a1, 32; private SP+32, immutable 0
.section .text.patch3,"ax",@progbits
.begin no-transform
movi.n a10, 0
.end no-transform

# 0x4025176e: l32i a6, a1, 32; private SP+32, immutable 0
.section .text.patch4,"ax",@progbits
.begin no-transform
movi.n a6, 0
.end no-transform

# 0x402517b6: l32i a12, a1, 32; private SP+32, immutable 0
.section .text.patch5,"ax",@progbits
.begin no-transform
movi.n a12, 0
.end no-transform

# 0x402517db: l32i a10, a1, 32; private SP+32, immutable 0
.section .text.patch6,"ax",@progbits
.begin no-transform
movi.n a10, 0
.end no-transform

# 0x4025191e: l32i a2, a1, 36; private SP+36, immutable 1
.section .text.patch7,"ax",@progbits
.begin no-transform
movi.n a2, 1
.end no-transform

# 0x402519b6: l32i a2, a1, 36; private SP+36, immutable 1
.section .text.patch8,"ax",@progbits
.begin no-transform
movi.n a2, 1
.end no-transform

# 0x40251c44: l32i a2, a1, 36; private SP+36, immutable 1
.section .text.patch9,"ax",@progbits
.begin no-transform
movi.n a2, 1
.end no-transform

# 0x40251d9c: l32i a2, a1, 32; private SP+32, immutable 0
.section .text.patch10,"ax",@progbits
.begin no-transform
movi.n a2, 0
.end no-transform

# 0x40252030: l32i a10, a1, 36; private SP+36, immutable 1
.section .text.patch11,"ax",@progbits
.begin no-transform
movi.n a10, 1
.end no-transform

# 0x402521a8: l32i a9, a1, 32; private SP+32, immutable 0
.section .text.patch12,"ax",@progbits
.begin no-transform
movi.n a9, 0
.end no-transform

# 0x402525f4: l32i a11, a1, 36; private SP+36, immutable 1
.section .text.patch13,"ax",@progbits
.begin no-transform
movi.n a11, 1
.end no-transform

# 0x4025289c: l32i a2, a1, 36; private SP+36, immutable 1
.section .text.patch14,"ax",@progbits
.begin no-transform
movi.n a2, 1
.end no-transform

# 0x402528d0: l32i a9, a1, 36; private SP+36, immutable 1
.section .text.patch15,"ax",@progbits
.begin no-transform
movi.n a9, 1
.end no-transform

# 0x40252913: l32i a2, a1, 36; private SP+36, immutable 1
.section .text.patch16,"ax",@progbits
.begin no-transform
movi.n a2, 1
.end no-transform

# 0x40252943: l32i a2, a1, 36; private SP+36, immutable 1
.section .text.patch17,"ax",@progbits
.begin no-transform
movi.n a2, 1
.end no-transform
