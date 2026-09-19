# Experimental exact PVQ row binary search; LX106 call0 ABI, no new RAM.
# Used only after K>=N>2 and U(N,N)<=index. C/GCC fallback is unchanged.
# a2=index, a6=row, a11=U(N,N), a12=K, a13=N, a15=&row[K+1].
# a0 is dead in decode_pulses until its original SP+44 restore. No stack/SAR.
.section .text.patch0,"ax",@progbits
.begin no-transform
pvq_binary_site:
    addi a15, a15, -4
    call0 pvq_binary_leaf
    j pvq_binary_done
    .space 43 - (. - pvq_binary_site), 0
.end no-transform

# Decoder-unreachable encoder storage, proven from the native encode=0 caller.
# Invariant: row[lo]<=index<row[hi], lo>=N, hi<=original K+1.
# Never load row[hi]: hi is an exclusive bound. a11 caches row[lo].
# Outputs match original search: a12=lo, a8=row[lo], a9=lo<<16,
# a11=sign_extend16(lo), a6=N-1. a3 is dead at the shared continuation.
.section .text.patch1,"ax",@progbits
.begin no-transform
.global pvq_binary_leaf
pvq_binary_leaf:
    mov.n a3, a13
    addi.n a12, a12, 1
.Lsearch:
    sub a9, a12, a3
    blti a9, 2, .Ldone
    srli a9, a9, 1
    add.n a9, a3, a9
    addx4 a8, a9, a6
    l32i.n a8, a8, 0
    bltu a2, a8, .Lhigh
    mov.n a3, a9
    mov.n a11, a8
    j .Lsearch
.Lhigh:
    mov.n a12, a9
    j .Lsearch
.Ldone:
    mov.n a12, a3
    mov.n a8, a11
    slli a9, a3, 16
    srai a11, a9, 16
    addi.n a6, a13, -1
    ret.n
    .space 94 - (. - pvq_binary_leaf), 0
.end no-transform
