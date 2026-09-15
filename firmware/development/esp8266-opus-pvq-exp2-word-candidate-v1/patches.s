# LX106 exp2_table8: a3 points to aligned signed16; return sign-extended a3.
# Five helper instructions per address phase,25 live bytes, no padding.
# Every other GPR and SAR remain untouched; no stack access or allocation.
# The old encoder-only slot and falling-through predecessor must be proved
# unreachable under the private decoder contract. Disjoint from logN helper.
# Preserve the original C fallback and every unrelated linked instruction.
.section .text.patch0,"ax",@progbits
.begin no-transform
.Lexp2_start:
 bbci a3, 1, .Lexp2_low
 addi a3, a3, -2
 l32i.n a3, a3, 0
 srai a3, a3, 16
 j pvq_exp2_continue
.Lexp2_low:
 l32i.n a3, a3, 0
 slli a3, a3, 16
 srai a3, a3, 16
 j pvq_exp2_continue
 .space 25-(.-.Lexp2_start),0
.end no-transform
.section .text.patch1,"ax",@progbits
.begin no-transform
 j pvq_exp2_word
.end no-transform
