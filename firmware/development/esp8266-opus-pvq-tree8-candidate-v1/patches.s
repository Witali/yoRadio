# Exact ordered PVQ prefix tree, LX106 internal call0 leaf; C fallback unchanged.
# Entry: a2=index, a12=K, a13=N, a15=&row[K+1], a9/a5=K<<16/sign16(K).
# Original guards guarantee K>=N>2 and index>=U(N,N). No new RAM or SAR use.
.section .text.patch0,"ax",@progbits
.begin no-transform
pvq_tree8_site:
    addi a15, a15, -4
    sub a8, a12, a13
    bgei a8, 8, .Ltree
    l32i.n a8, a15, 0
    bgeu a2, a8, pvq_tree8_fast
    addi a6, a15, -4
.Lshort:
    l32i.n a8, a6, 0
    addi a6, a6, -4
    addi.n a12, a12, -1
    bltu a2, a8, .Lshort
    addi.n a6, a13, -1
    j pvq_tree8_flags
    .space 40 - (. - pvq_tree8_site), 0
.Ltree:
    call0 pvq_tree8_leaf
# Return directly into original SLLI/SRAI/J at0x40253354 (shared column path).
.end no-transform

#123 decoder-dead bytes; the one-byte prefix aligns the internal call0 target.
.section .text.patch1,"ax",@progbits
.begin no-transform
pvq_tree8_storage:
    .byte 0
.global pvq_tree8_leaf
pvq_tree8_leaf:
# K-N>=8, so every fixed-offset probe K..K-7 is inside the valid row.
# Base=row[K-7]. Successful lower thresholds stay in a8; a3 probes above it.
# Tree leaves d=0..7 update K once; d>=8 continues the original linear loop.
# a0 is dead until original SP+44 restore, a3 is dead at shared continuation.
# Outputs: a8=U(N,new K), a12=new K, a6=N-1. Others unchanged; no stack frame.
    addi a6, a15, -28
    l32i.n a8, a6, 16
    bltu a2, a8, .Lfour
    l32i.n a3, a6, 24
    bltu a2, a3, .Ltwo_three
    l32i.n a8, a6, 28
    bgeu a2, a8, .Ldone
    mov.n a8, a3
    addi.n a12, a12, -1
    j .Ldone
.Ltwo_three:
    l32i.n a3, a6, 20
    bgeu a2, a3, .Ltwo
    addi a12, a12, -3
    j .Ldone
.Ltwo:
    mov.n a8, a3
    addi a12, a12, -2
    j .Ldone
.Lfour:
    l32i.n a8, a6, 8
    bltu a2, a8, .Lsix
    l32i.n a3, a6, 12
    bgeu a2, a3, .Lfour_leaf
    addi a12, a12, -5
    j .Ldone
.Lfour_leaf:
    mov.n a8, a3
    addi a12, a12, -4
    j .Ldone
.Lsix:
    l32i.n a8, a6, 0
    bltu a2, a8, .Leight
    l32i.n a3, a6, 4
    bgeu a2, a3, .Lsix_leaf
    addi a12, a12, -7
    j .Ldone
.Lsix_leaf:
    mov.n a8, a3
    addi a12, a12, -6
    j .Ldone
.Leight:
    addi a6, a6, -4
    addi a12, a12, -7
.Ltail:
    l32i.n a8, a6, 0
    addi a6, a6, -4
    addi.n a12, a12, -1
    bltu a2, a8, .Ltail
.Ldone:
    addi.n a6, a13, -1
    ret.n
    .space 123 - (. - pvq_tree8_storage), 0
.end no-transform
