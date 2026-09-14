# clt_mdct_backward_c post-rotation, Xtensa LX106 call0, frozen276-byte range.
# a15=yp0, sp+0=yp1, a9=&t[i], sp+4=i, sp+20=iterations=N4/2.
# a0/a11 cache forward t0/t1 words; a12/a14 cache reverse t0/t1 words.
# Standard N4=480/240/120/60: even iteration count, forwardlow/reversehigh.
# Original96-byte frame/return/callee register saves and restores unchanged.
# No CALL inside or after this loop before return; original a0 at sp+92.
# First yr uses a10/a13, second yr a7/a13: a14 stays cached, no new spill.
# Preserve each individual MULL/SRAI15/SLLI1 term; only ADD32 reassociated.
# Read BOTH yp1 samples before any yp0/yp1 store; keep four PCM stores ordered.
# C fallback and saved GCC source unchanged; no MUL16S/precision/bitrate change.
.section .text.patch0,"ax",@progbits
.begin no-transform
.Lloop:
l32i.n a4, a15, 4
l32i.n a3, a15, 0
bbsi a9, 1, .Lfhigh
l32i.n a0, a9, 0
l32i.n a7, a1, 16
add.n a2, a7, a9
l32i.n a11, a2, 0
l32i.n a7, a1, 8
sub a2, a7, a9
addi a2, a2, -2
l32i.n a12, a2, 0
l32i.n a7, a1, 12
sub a2, a7, a9
addi a2, a2, -2
l32i.n a14, a2, 0
slli a5, a0, 16
srai a5, a5, 16
slli a6, a11, 16
srai a6, a6, 16
j .Lfront
.Lfhigh:
srai a5, a0, 16
srai a6, a11, 16
.Lfront:
srai a7, a4, 16
srai a2, a3, 16
extui a4, a4, 0, 16
extui a3, a3, 0, 16
mull a10, a5, a7
slli a10, a10, 1
mull a13, a5, a4
srai a13, a13, 15
add.n a10, a10, a13
mull a13, a6, a2
slli a13, a13, 1
add.n a10, a10, a13
mull a13, a6, a3
srai a13, a13, 15
add.n a10, a10, a13
mull a2, a5, a2
mull a3, a5, a3
mull a7, a7, a6
l32i.n a8, a1, 0
mull a4, a6, a4
srai a3, a3, 15
slli a2, a2, 1
add.n a2, a2, a3
l32i.n a13, a8, 4
srai a4, a4, 15
l32i.n a3, a8, 0
slli a7, a7, 1
s32i.n a10, a15, 0
add.n a7, a7, a4
sub a7, a7, a2
s32i.n a7, a8, 4
# Reverse words use HIGH half on forwardlow and LOW half on forwardhigh.
bbsi a9, 1, .Lrlow
srai a4, a12, 16
srai a5, a14, 16
j .Lreverse
.Lrlow:
slli a4, a12, 16
srai a4, a4, 16
slli a5, a14, 16
srai a5, a5, 16
.Lreverse:
srai a8, a13, 16
extui a2, a13, 0, 16
srai a6, a3, 16
extui a3, a3, 0, 16
mull a7, a4, a8
slli a7, a7, 1
mull a13, a4, a2
srai a13, a13, 15
add.n a7, a7, a13
mull a13, a5, a6
slli a13, a13, 1
add.n a7, a7, a13
mull a13, a5, a3
srai a13, a13, 15
add.n a7, a7, a13
mull a8, a8, a5
mull a2, a5, a2
mull a6, a4, a6
mull a3, a4, a3
l32i.n a4, a1, 0
slli a8, a8, 1
srai a2, a2, 15
slli a6, a6, 1
srai a3, a3, 15
l32i.n a5, a1, 4
add.n a8, a8, a2
add.n a6, a6, a3
s32i.n a7, a4, 0
sub a6, a8, a6
s32i.n a6, a15, 4
addi.n a5, a5, 1
addi a4, a4, -8
l32i.n a6, a1, 20
s32i.n a5, a1, 4
s32i.n a4, a1, 0
addi.n a15, a15, 8
addi.n a9, a9, 2
bge a5, a6, .Lend
j .Lloop
.space 276-(.-.Lloop), 0
.Lend:
.end no-transform
