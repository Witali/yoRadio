# LX106 signed PVQ index: a2 points to int16 -> a2 is sign-extended int32.
# Fixed J continuation, no CALL/RET and no additional frame or allocation.
# Save the original a0 return to its existing sp+108 slot before reusing a0
# for SAR. Intervening instructions neither use a2/a0 nor alias flash.
# Restore SAR; original return remains in sp+108 and is restored by caller.
# LX106 assembler has no SEXT: exact sign extension uses SLLI16/SRAI16.
# Reuse29 encoder-only bytes, all live; all other addresses stay frozen.
.section .text.patch0,"ax",@progbits
.begin no-transform
.Lindex_start:
 rsr a0, sar
 ssa8l a2
 srli a2, a2, 2
 slli a2, a2, 2
 l32i.n a2, a2, 0
 srl a2, a2
 slli a2, a2, 16
 srai a2, a2, 16
 wsr a0, sar
 j pvq_index_continue
 .space 29-(.-.Lindex_start),0
.end no-transform
.section .text.patch1,"ax",@progbits
.begin no-transform
 s32i a0, a1, 108
.end no-transform
.section .text.patch2,"ax",@progbits
.begin no-transform
 j pvq_index_word
.end no-transform
