# Independent N=4 uniform-256 prefix search, LX106 call0 ABI.
# Entry: a2=index, a12=K>=N, a13=N>2, a15=&row[K+1]. The original
# sign path proves index>=U(N,N). Keep the first U(K) fast return.
# Other N retain the old linear loop; this is not a bitrate restriction.
.section .text.patch0,"ax",@progbits
.begin no-transform
n4_site:
    addi a15, a15, -4
    l32i.n a8, a15, 0
    bgeu a2, a8, n4_fast
    beqi a13, 4, .Llookup
    addi a6, a15, -4
.Llinear:
    l32i.n a8, a6, 0
    addi a6, a6, -4
    addi.n a12, a12, -1
    bltu a2, a8, .Llinear
    addi.n a6, a13, -1
    j n4_flags
    .space 40 - (. - n4_site), 0
.Llookup:
    call0 n4_leaf
.end no-transform

# Domain 256<=index<65536. The bucket is index>>8 (1..255), with no
# runtime bucket-width selection or index adjustment. The table literal
# points one word BEFORE the actual table, so ADDX4 selects bucket-1.
# The zero bucket is rejected BEFORE the load: never read the literal as data.
# Words: rank[5:0], U(4,rank)[21:6], next-boundary offset[30:22].
# Every 256-wide bucket in this domain has at most one boundary. If crossed,
# p+=4*K*K+2; K++. K<=37, hence exact 32-bit arithmetic, no division or SAR.
# Outside the domain use the original loop. No new RAM, stores or stack slots.
# a0 is dead until original epilogue; a3/a11 overwritten by the continuation.
# Preserve a1/a2/a4/a5/a7/a10/a13/a14/a15. Return p=a8, K=a12, a6=N-1.
.section .text.patch1,"ax",@progbits
.begin no-transform
.global n4_leaf
n4_leaf:
    extui a3, a2, 16, 16
    bnez a3, .Lfallback
    srli a3, a2, 8
    beqz a3, .Lfallback
    extui a11, a2, 0, 8
    l32r a6, n4_literal
    addx4 a3, a3, a6
    l32i.n a8, a3, 0
    extui a12, a8, 0, 6
    extui a3, a8, 22, 10
    extui a8, a8, 6, 16
    bltu a11, a3, .Ldone
    mull a3, a12, a12
    slli a3, a3, 2
    addi.n a3, a3, 2
    add.n a8, a8, a3
    addi.n a12, a12, 1
.Ldone:
    addi.n a6, a13, -1
    ret.n
.Lfallback:
    addi a6, a15, -4
.Lfallback_loop:
    l32i.n a8, a6, 0
    addi a6, a6, -4
    addi.n a12, a12, -1
    bltu a2, a8, .Lfallback_loop
    j .Ldone
.global n4_helper_end
n4_helper_end:
    .space 94 - (. - n4_leaf), 0
.end no-transform
