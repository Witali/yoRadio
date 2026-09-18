# Experimental quant_all_bands local scalar loads, native decoder only.
# LX106 call0 ABI; original384-byte frame and every instruction PC retained.
#23 local L32I -> MOVI, values proven at each use; slots may change elsewhere.
# No ctx SP32/36 load replacement from the unaccepted flags experiment.
# Same destination/width, no SAR, memory writes, branches, calls or RAM changes.
# Original GCC snapshot and C fallback unchanged. Proof: quant_locals_proof.cjs.

# 0x40250902: l32i a9, a1, 220; SP+220 is 1 HERE
.section .text.patch0,"ax",@progbits
.begin no-transform
movi a9, 1
.end no-transform

# 0x402509d1: l32i a8, a1, 220; SP+220 is 1 HERE
.section .text.patch1,"ax",@progbits
.begin no-transform
movi a8, 1
.end no-transform

# 0x40250a95: l32i a12, a1, 192; SP+192 is 0 HERE
.section .text.patch2,"ax",@progbits
.begin no-transform
movi a12, 0
.end no-transform

# 0x40250a98: l32i a14, a1, 192; SP+192 is 0 HERE
.section .text.patch3,"ax",@progbits
.begin no-transform
movi a14, 0
.end no-transform

# 0x40250b70: l32i a11, a1, 220; SP+220 is 1 HERE
.section .text.patch4,"ax",@progbits
.begin no-transform
movi a11, 1
.end no-transform

# 0x40250d32: l32i a9, a1, 220; SP+220 is 1 HERE
.section .text.patch5,"ax",@progbits
.begin no-transform
movi a9, 1
.end no-transform

# 0x40250fc5: l32i a8, a1, 240; SP+240 is 0 HERE
.section .text.patch6,"ax",@progbits
.begin no-transform
movi a8, 0
.end no-transform

# 0x40251007: l32i a10, a1, 240; SP+240 is 0 HERE
.section .text.patch7,"ax",@progbits
.begin no-transform
movi a10, 0
.end no-transform

# 0x402511d6: l32i a11, a1, 240; SP+240 is 0 HERE
.section .text.patch8,"ax",@progbits
.begin no-transform
movi a11, 0
.end no-transform

# 0x402513d2: l32i a11, a1, 240; SP+240 is 0 HERE
.section .text.patch9,"ax",@progbits
.begin no-transform
movi a11, 0
.end no-transform

# 0x402514c0: l32i a11, a1, 140; SP+140 is 0 HERE
.section .text.patch10,"ax",@progbits
.begin no-transform
movi a11, 0
.end no-transform

# 0x40251518: l32i a12, a1, 140; SP+140 is 0 HERE
.section .text.patch11,"ax",@progbits
.begin no-transform
movi a12, 0
.end no-transform

# 0x40251681: l32i a6, a1, 140; SP+140 is 0 HERE
.section .text.patch12,"ax",@progbits
.begin no-transform
movi a6, 0
.end no-transform

# 0x40251781: l32i a8, a1, 140; SP+140 is 0 HERE
.section .text.patch13,"ax",@progbits
.begin no-transform
movi a8, 0
.end no-transform

# 0x402518d9: l32i a14, a1, 140; SP+140 is 0 HERE
.section .text.patch14,"ax",@progbits
.begin no-transform
movi a14, 0
.end no-transform

# 0x40251db8: l32i a10, a1, 124; SP+124 is 0 HERE
.section .text.patch15,"ax",@progbits
.begin no-transform
movi a10, 0
.end no-transform

# 0x40251e90: l32i a2, a1, 124; SP+124 is 0 HERE
.section .text.patch16,"ax",@progbits
.begin no-transform
movi a2, 0
.end no-transform

# 0x40251f27: l32i a9, a1, 124; SP+124 is 0 HERE
.section .text.patch17,"ax",@progbits
.begin no-transform
movi a9, 0
.end no-transform

# 0x402521c5: l32i a2, a1, 132; SP+132 is 0 HERE
.section .text.patch18,"ax",@progbits
.begin no-transform
movi a2, 0
.end no-transform

# 0x4025229c: l32i a2, a1, 132; SP+132 is 0 HERE
.section .text.patch19,"ax",@progbits
.begin no-transform
movi a2, 0
.end no-transform

# 0x40252334: l32i a9, a1, 132; SP+132 is 0 HERE
.section .text.patch20,"ax",@progbits
.begin no-transform
movi a9, 0
.end no-transform

# 0x402529f4: l32i a9, a1, 240; SP+240 is 0 HERE
.section .text.patch21,"ax",@progbits
.begin no-transform
movi a9, 0
.end no-transform

# 0x40252a20: l32i a10, a1, 132; SP+132 is 1 HERE
.section .text.patch22,"ax",@progbits
.begin no-transform
movi a10, 1
.end no-transform
