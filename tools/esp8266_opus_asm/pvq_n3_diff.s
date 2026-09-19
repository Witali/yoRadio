# Exact N=3 finite-difference PVQ search, Xtensa LX106 call0 ABI.
# Entry: a2=index, a12=K, a13=N, a15=&row[K+1]. Original guards ensure
# K>=N>2 and index>=U(N,N). First U(K) probe / fast exit is unchanged.
# Other dimensions retain the old linear search. No bitrate cap or new table.
.section .text.patch0,"ax",@progbits
.begin no-transform
pvq_n3_diff_site:
    addi a15, a15, -4
    l32i.n a8, a15, 0
    bgeu a2, a8, pvq_n3_diff_fast
    beqi a13, 3, .Larithmetic
    addi a6, a15, -4
.Llinear:
    l32i.n a8, a6, 0
    addi a6, a6, -4
    addi.n a12, a12, -1
    bltu a2, a8, .Llinear
    addi.n a6, a13, -1
    j pvq_n3_diff_flags
    .space 40 - (. - pvq_n3_diff_site), 0
.Larithmetic:
    call0 pvq_n3_diff_leaf
# Return into unchanged SLLI/SRAI/J at0x40253354.
.end no-transform

# Replace94 proved decoder-dead encoder bytes without moving any function.
# Input: N=3, p=a8=U(3,K)>index. Use obsolete row-base a6 for delta;
# restore a6=N-1 as expected by the shared continuation. a0 is dead until
# the original epilogue reloads it. No stack slots, stores or SAR writes.
# U(3,k)-U(3,k-1)=4*(k-1). In our full stored domain K<=175,
# p<=60901, delta<=696. The original index>=13 guard prevents underflow.
.section .text.patch1,"ax",@progbits
.begin no-transform
.global pvq_n3_diff_leaf
pvq_n3_diff_leaf:
    slli a6, a12, 2
    addi a6, a6, -4
.Ldifference:
    sub a8, a8, a6
    addi a6, a6, -4
    addi.n a12, a12, -1
    bltu a2, a8, .Ldifference
    addi.n a6, a13, -1
    ret.n
    .space 94 - (. - pvq_n3_diff_leaf), 0
.end no-transform
