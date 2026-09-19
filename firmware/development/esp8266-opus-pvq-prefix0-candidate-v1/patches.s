# Exact exponent-bound PVQ search, LX106 call0 leaf; C fallback unchanged.
# Entry: a2=index, a12=K, a13=N, a15=&row[K+1], a9/a5=K<<16/sign16(K).
# Original guards guarantee K>=N>2 and index>=U(N,N). No new RAM or SAR use.
.section .text.patch0,"ax",@progbits
.begin no-transform
pvq_prefix0_site:
    addi a15, a15, -4
    sub a8, a12, a13
    bgei a8, 8, .Ltree
    l32i.n a8, a15, 0
    bgeu a2, a8, pvq_prefix0_fast
    addi a6, a15, -4
.Lshort:
    l32i.n a8, a6, 0
    addi a6, a6, -4
    addi.n a12, a12, -1
    bltu a2, a8, .Lshort
    addi.n a6, a13, -1
    j pvq_prefix0_flags
    .space 40 - (. - pvq_prefix0_site), 0
.Ltree:
    call0 pvq_prefix0_leaf
# Return directly into original SLLI/SRAI/J at0x40253354 (shared column path).
.end no-transform

#94 decoder-dead bytes inside quant_all_bands; entry is already word aligned.
.section .text.patch1,"ax",@progbits
.begin no-transform
.global pvq_prefix0_leaf
pvq_prefix0_leaf:
# K-N>=8. a2>=U(N,N)>0; NSAU yields0..31.
# Prefix keys are (N-3)*32+clz(index), packed four bounds per aligned word.
# Table values bound the answer from above; MIN with original K preserves it.
# a9 temporarily saves SAR; a3 is dead at the original join. No stack or stores.
    nsau a8, a2
    slli a3, a13, 5
    add.n a8, a8, a3
    extui a3, a8, 0, 2
    srli a8, a8, 2
    l32r a11, pvq_prefix0_literal
    addx4 a8, a8, a11
    l32i.n a8, a8, 0
    rsr a9, SAR
    slli a3, a3, 3
    ssr a3
    srl a8, a8
    wsr a9, SAR
    extui a8, a8, 0, 8
    bltu a12, a8, .Lbounded
    mov.n a12, a8
.Lbounded:
    addx4 a6, a12, a6
    l32i.n a8, a6, 0
    bgeu a2, a8, .Ldone
    addi a6, a6, -4
.Llinear:
    l32i.n a8, a6, 0
    addi a6, a6, -4
    addi.n a12, a12, -1
    bltu a2, a8, .Llinear
.Ldone:
    addi.n a6, a13, -1
    ret.n
    .space 94 - (. - pvq_prefix0_leaf), 0
.end no-transform

# Audited unused alg_quant encoder storage. Read-only bytes; never executed.
.section .text.patch2,"ax",@progbits
.global pvq_prefix0_literal
pvq_prefix0_literal:
    .long pvq_prefix0_table - 96
pvq_prefix0_table:
    .byte 176,176,176,176,176,176,176,176,176,176,176,176,176,176,176,176,176,128,91,64,45,32,23,16,11,8,6,4,3,3,3,3
    .byte 176,176,176,176,176,176,176,176,176,176,147,116,92,73,58,46,37,29,23,18,15,12,9,7,6,4,4,4,4,4,4,4
    .byte 176,176,176,168,142,119,100,84,71,60,50,42,35,30,25,21,18,15,12,10,9,7,6,5,5,5,5,5,5,5,5,5
    .byte 96,96,83,73,63,55,48,42,36,32,27,24,21,18,16,14,12,10,9,8,7,6,6,6,6,6,6,6,6,6,6,6
    .byte 54,54,48,43,38,34,30,27,24,21,19,17,15,13,12,10,9,8,7,7,7,7,7,7,7,7,7,7,7,7,7,7
    .byte 37,36,33,30,27,24,22,20,18,16,15,13,12,11,10,9,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8
    .byte 28,27,25,23,21,19,18,16,15,13,12,11,10,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9
    .byte 24,22,21,19,18,16,15,14,13,12,11,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10
    .byte 19,19,18,16,15,14,13,12,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11
    .byte 18,17,16,15,14,13,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12
    .byte 16,15,14,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13

