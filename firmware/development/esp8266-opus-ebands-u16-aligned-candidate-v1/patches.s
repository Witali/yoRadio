# Keep cross entries at parent +16 (mod4=0); three bytes after RET
# are unreachable padding, NOT executed NOPs. No new RAM or stack.
# LX106 eBands extraction only: immutable standard table contains0..100.
# NOT a generic signed16 helper. EXTUI replaces SLLI+SRAI under that proof.
# Same input/output registers, a0 return address, SAR and stack as parent.
# Callsites and inherited stack load remain byte-for-byte unchanged.
# Each path executes one fewer instruction; speed needs physical A/B/A.
# Leaf0: p=a3, low=a11, high=a2; 30 live bytes, 3 unreachable bytes before cross.
.section .text.patch0,"ax",@progbits
.begin no-transform
 bbsi a3, 1, .Lcross0
 l32i.n a2, a3, 0
 extui a11, a2, 0, 16
 srai a2, a2, 16
 ret.n
 .space 3,0
.Lcross0:
 addi a11, a3, -2
 l32i.n a11, a11, 0
 srai a11, a11, 16
 addi.n a2, a3, 2
 l32i.n a2, a2, 0
 extui a2, a2, 0, 16
 ret.n
 .space 9,0
.end no-transform
# Leaf1: p=a5, low=a2, high=a3; 30 live bytes, 3 unreachable bytes before cross.
.section .text.patch1,"ax",@progbits
.begin no-transform
 bbsi a5, 1, .Lcross1
 l32i.n a3, a5, 0
 extui a2, a3, 0, 16
 srai a3, a3, 16
 ret.n
 .space 3,0
.Lcross1:
 addi a2, a5, -2
 l32i.n a2, a2, 0
 srai a2, a2, 16
 addi.n a3, a5, 2
 l32i.n a3, a3, 0
 extui a3, a3, 0, 16
 ret.n
 .space 3,0
.end no-transform
# Leaf2: p=a5, low=a2, high=a7; 30 live bytes, 3 unreachable bytes before cross.
.section .text.patch2,"ax",@progbits
.begin no-transform
 bbsi a5, 1, .Lcross2
 l32i.n a7, a5, 0
 extui a2, a7, 0, 16
 srai a7, a7, 16
 ret.n
 .space 3,0
.Lcross2:
 addi a2, a5, -2
 l32i.n a2, a2, 0
 srai a2, a2, 16
 addi.n a7, a5, 2
 l32i.n a7, a7, 0
 extui a7, a7, 0, 16
 ret.n
 .space 3,0
.end no-transform
# Leaf3: p=a4, low=a10, high=a3; 30 live bytes, 3 unreachable bytes before cross.
.section .text.patch3,"ax",@progbits
.begin no-transform
 bbsi a4, 1, .Lcross3
 l32i.n a3, a4, 0
 extui a10, a3, 0, 16
 srai a3, a3, 16
 ret.n
 .space 3,0
.Lcross3:
 addi a10, a4, -2
 l32i.n a10, a10, 0
 srai a10, a10, 16
 addi.n a3, a4, 2
 l32i.n a3, a3, 0
 extui a3, a3, 0, 16
 ret.n
 .space 3,0
.end no-transform
# Leaf4: p=a12, low=a4, high=a2; 30 live bytes, 3 unreachable bytes before cross.
.section .text.patch4,"ax",@progbits
.begin no-transform
 bbsi a12, 1, .Lcross4
 l32i.n a2, a12, 0
 extui a4, a2, 0, 16
 srai a2, a2, 16
 ret.n
 .space 3,0
.Lcross4:
 addi a4, a12, -2
 l32i.n a4, a4, 0
 srai a4, a4, 16
 addi.n a2, a12, 2
 l32i.n a2, a2, 0
 extui a2, a2, 0, 16
 ret.n
 .space 3,0
.end no-transform
# Leaf5: p=a6, low=a2, high=a7; split13+17 live bytes.
.section .text.patch5,"ax",@progbits
.begin no-transform
 bbsi a6, 1, ebands_u16_cross
 l32i.n a7, a6, 0
 extui a2, a7, 0, 16
 srai a7, a7, 16
 ret.n
 .space 3,0
.end no-transform
.section .text.patch6,"ax",@progbits
.begin no-transform
 addi a2, a6, -2
 l32i.n a2, a2, 0
 srai a2, a2, 16
 addi.n a7, a6, 2
 l32i.n a7, a7, 0
 extui a7, a7, 0, 16
 ret.n
 .space 3,0
.end no-transform
