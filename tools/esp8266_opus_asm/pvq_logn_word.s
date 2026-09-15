# LX106 decoder logN: a10 points at aligned int16; return signed a4.
# Five helper instructions per phase. Preserve a10, every other GPR and SAR.
# No call, return-register use, stack access, allocation or table expansion.
# Storage is an independently proven encoder-only island; the old predecessor
# falls through, so its reachability must also be proved (not assumed dead).
# C fallback and all other linked instruction addresses are unchanged.
.section .text.patch0,"ax",@progbits
.begin no-transform
.Llogn_start:
 bbci a10, 1, .Llogn_low
 addi a4, a10, -2
 l32i.n a4, a4, 0
 srai a4, a4, 16
 j pvq_logn_continue
.Llogn_low:
 l32i.n a4, a10, 0
 slli a4, a4, 16
 srai a4, a4, 16
 j pvq_logn_continue
 .space 42-(.-.Llogn_start),0
.end no-transform
.section .text.patch1,"ax",@progbits
.begin no-transform
 j pvq_logn_word
.end no-transform
