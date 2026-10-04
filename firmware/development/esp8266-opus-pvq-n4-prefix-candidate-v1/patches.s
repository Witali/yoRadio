# Experimental exact N=4 rank/p lookup; Xtensa LX106 call0 ABI.
# Entry: a2=index, a12=K>=N, a13=N>2, a15=&row[K+1]. The existing
# sign path ensures index>=U(N,N). Keep the first U(K) fast return.
# Only N=4 after a failed probe dispatches to the helper. No bitrate cap.
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

# a3 and a11 are scratch: the unchanged continuation rewrites a9/a11,
# then a3. a0 is dead until the original decode_pulses epilogue reloads it.
# Preserve a1/a2/a4/a5/a7/a10/a13/a14/a15. Return p in a8, K in a12,
# a6=N-1. No stores, SAR writes, stack slots or additional scratch arena.
# Table words: rank[5:0], U(4,rank)[21:6], next boundary offset[30:22].
# 64..511 use 64-wide buckets; 512..65535 use 256-wide buckets.
# Each bucket has <=1 boundary. If crossed, p+=4*K*K+2; K++.
# K<=37 in this domain, so all arithmetic is exact in 32 bits.
# All other indices use the original linear search; no stream restriction.
.section .text.patch1,"ax",@progbits
.begin no-transform
.global n4_leaf
n4_leaf:
    extui a3, a2, 16, 16
    bnez a3, .Lfallback
    blti a2, 64, .Lfallback
    srli a3, a2, 9
    beqz a3, .Lsmall
    srli a3, a2, 8
    addi.n a3, a3, 5
    extui a11, a2, 0, 8
    j .Lload
.Lsmall:
    srli a3, a2, 6
    addi.n a3, a3, -1
    extui a11, a2, 0, 6
.Lload:
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

# Offline generated exact single-threshold buckets in unused encoder flash.
.section .text.patch2,"ax",@progbits
.global n4_literal
n4_literal:
.word 0x40248cb8
.word 0x10000fc4
.word 0x400fc4
.word 0x9c02045
.word 0x100039c6
.word 0xe4039c6
.word 0x10005e47
.word 0x10005e47
.word 0xfc05e47
.word 0x10408fc8
.word 0x21c0d049
.word 0x400121ca
.word 0x64121ca
.word 0x3fc1864b
.word 0x4001ffcc
.word 0x4001ffcc
.word 0x1041ffcc
.word 0x4002904d
.word 0x39c2904d
.word 0x400339ce
.word 0x400339ce
.word 0x3e4339ce
.word 0x4003fe4f
.word 0x4003fe4f
.word 0x4003fe4f
.word 0x1fc3fe4f
.word 0x4004dfd0
.word 0x4004dfd0
.word 0x4004dfd0
.word 0x2044dfd0
.word 0x4005e051
.word 0x4005e051
.word 0x4005e051
.word 0x4005e051
.word 0x1c5e051
.word 0x400701d2
.word 0x400701d2
.word 0x400701d2
.word 0x400701d2
.word 0x64701d2
.word 0x40084653
.word 0x40084653
.word 0x40084653
.word 0x40084653
.word 0x2fc84653
.word 0x4009afd4
.word 0x4009afd4
.word 0x4009afd4
.word 0x4009afd4
.word 0x4009afd4
.word 0x4009afd4
.word 0x49afd4
.word 0x400b4055
.word 0x400b4055
.word 0x400b4055
.word 0x400b4055
.word 0x400b4055
.word 0x39cb4055
.word 0x400cf9d6
.word 0x400cf9d6
.word 0x400cf9d6
.word 0x400cf9d6
.word 0x400cf9d6
.word 0x400cf9d6
.word 0x400cf9d6
.word 0x1e4cf9d6
.word 0x400ede57
.word 0x400ede57
.word 0x400ede57
.word 0x400ede57
.word 0x400ede57
.word 0x400ede57
.word 0x400ede57
.word 0x2fcede57
.word 0x4010efd8
.word 0x4010efd8
.word 0x4010efd8
.word 0x4010efd8
.word 0x4010efd8
.word 0x4010efd8
.word 0x4010efd8
.word 0x4010efd8
.word 0x3050efd8
.word 0x40133059
.word 0x40133059
.word 0x40133059
.word 0x40133059
.word 0x40133059
.word 0x40133059
.word 0x40133059
.word 0x40133059
.word 0x40133059
.word 0x21d33059
.word 0x4015a1da
.word 0x4015a1da
.word 0x4015a1da
.word 0x4015a1da
.word 0x4015a1da
.word 0x4015a1da
.word 0x4015a1da
.word 0x4015a1da
.word 0x4015a1da
.word 0x4015a1da
.word 0x655a1da
.word 0x4018465b
.word 0x4018465b
.word 0x4018465b
.word 0x4018465b
.word 0x4018465b
.word 0x4018465b
.word 0x4018465b
.word 0x4018465b
.word 0x4018465b
.word 0x4018465b
.word 0x1fd8465b
.word 0x401b1fdc
.word 0x401b1fdc
.word 0x401b1fdc
.word 0x401b1fdc
.word 0x401b1fdc
.word 0x401b1fdc
.word 0x401b1fdc
.word 0x401b1fdc
.word 0x401b1fdc
.word 0x401b1fdc
.word 0x401b1fdc
.word 0x305b1fdc
.word 0x401e305d
.word 0x401e305d
.word 0x401e305d
.word 0x401e305d
.word 0x401e305d
.word 0x401e305d
.word 0x401e305d
.word 0x401e305d
.word 0x401e305d
.word 0x401e305d
.word 0x401e305d
.word 0x401e305d
.word 0x39de305d
.word 0x402179de
.word 0x402179de
.word 0x402179de
.word 0x402179de
.word 0x402179de
.word 0x402179de
.word 0x402179de
.word 0x402179de
.word 0x402179de
.word 0x402179de
.word 0x402179de
.word 0x402179de
.word 0x402179de
.word 0x3e6179de
.word 0x4024fe5f
.word 0x4024fe5f
.word 0x4024fe5f
.word 0x4024fe5f
.word 0x4024fe5f
.word 0x4024fe5f
.word 0x4024fe5f
.word 0x4024fe5f
.word 0x4024fe5f
.word 0x4024fe5f
.word 0x4024fe5f
.word 0x4024fe5f
.word 0x4024fe5f
.word 0x4024fe5f
.word 0x3fe4fe5f
.word 0x4028bfe0
.word 0x4028bfe0
.word 0x4028bfe0
.word 0x4028bfe0
.word 0x4028bfe0
.word 0x4028bfe0
.word 0x4028bfe0
.word 0x4028bfe0
.word 0x4028bfe0
.word 0x4028bfe0
.word 0x4028bfe0
.word 0x4028bfe0
.word 0x4028bfe0
.word 0x4028bfe0
.word 0x4028bfe0
.word 0x4028bfe0
.word 0x68bfe0
.word 0x402cc061
.word 0x402cc061
.word 0x402cc061
.word 0x402cc061
.word 0x402cc061
.word 0x402cc061
.word 0x402cc061
.word 0x402cc061
.word 0x402cc061
.word 0x402cc061
.word 0x402cc061
.word 0x402cc061
.word 0x402cc061
.word 0x402cc061
.word 0x402cc061
.word 0x402cc061
.word 0x1ecc061
.word 0x403101e2
.word 0x403101e2
.word 0x403101e2
.word 0x403101e2
.word 0x403101e2
.word 0x403101e2
.word 0x403101e2
.word 0x403101e2
.word 0x403101e2
.word 0x403101e2
.word 0x403101e2
.word 0x403101e2
.word 0x403101e2
.word 0x403101e2
.word 0x403101e2
.word 0x403101e2
.word 0x403101e2
.word 0x67101e2
.word 0x40358663
.word 0x40358663
.word 0x40358663
.word 0x40358663
.word 0x40358663
.word 0x40358663
.word 0x40358663
.word 0x40358663
.word 0x40358663
.word 0x40358663
.word 0x40358663
.word 0x40358663
.word 0x40358663
.word 0x40358663
.word 0x40358663
.word 0x40358663
.word 0x40358663
.word 0x40358663
.word 0xff58663
.word 0x403a4fe4
.word 0x403a4fe4
.word 0x403a4fe4
.word 0x403a4fe4
.word 0x403a4fe4
.word 0x403a4fe4
.word 0x403a4fe4
.word 0x403a4fe4
.word 0x403a4fe4
.word 0x403a4fe4
.word 0x403a4fe4
.word 0x403a4fe4
.word 0x403a4fe4
.word 0x403a4fe4
.word 0x403a4fe4
.word 0x403a4fe4
.word 0x403a4fe4
.word 0x403a4fe4
.word 0x403a4fe4
.word 0x207a4fe4
.word 0x403f6065
.word 0x403f6065
