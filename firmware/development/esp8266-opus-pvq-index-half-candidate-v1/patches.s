# LX106 signed PVQ index: a2 points to aligned int16; result sign-extended a2.
# Branch once on halfword phase. Do not touch SAR, a0, or any other register.
# Restore the parent's original ordering: load first, save return at sp+108
# at its original address. Fixed J continuation; no CALL, RET or new stack.
# Five executed helper instructions per phase;25 live bytes in the proven
#29-byte encoder-only slot. Preserve C fallback and all other linked addresses.
.section .text.patch0,"ax",@progbits
.begin no-transform
.Lindex_start:
 bbci a2, 1, .Lindex_low
 addi a2, a2, -2
 l32i.n a2, a2, 0
 srai a2, a2, 16
 j pvq_index_continue
.Lindex_low:
 l32i.n a2, a2, 0
 slli a2, a2, 16
 srai a2, a2, 16
 j pvq_index_continue
 .space 29-(.-.Lindex_start),0
.end no-transform
.section .text.patch1,"ax",@progbits
.begin no-transform
 j pvq_index_half
.end no-transform
.section .text.patch2,"ax",@progbits
.begin no-transform
 s32i a0, a1, 108
.end no-transform
