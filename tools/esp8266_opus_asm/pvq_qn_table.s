# LX106 decoder compute_qn, qb already clamped to4..64 by unchanged guards.
# Table contains (exp2[qb&7] >> (14-(qb>>3))) + 1, not just rounded qn.
# Thus a2, a3, a4 and SAR ALL match at qn_continue; all other GPRs untouched.
# 13 ->11 executed instructions including J over unreachable padding.
# No helper call, extra stack or DRAM. 260B flash replaces old decoder-dead
# encoder instructions, including the superseded32B exp2 table.
# Entries0..3 are padding; qb<4 follows unchanged low-qn path, never this one.
# C fallback remains original; speed must be measured on LX106.
.section .text.patch0,"ax",@progbits
.begin no-transform
 slli a4, a2, 2
 l32r a3, qn_pool
 add.n a3, a3, a4
 srai a2, a2, 3
 movi.n a4, 14
 sub a2, a4, a2
 ssr a2
 l32i.n a2, a3, 0
 movi.n a3, -2
 and a3, a2, a3
 j qn_continue
 .space 6,0
.end no-transform
.section .text.patch1,"ax",@progbits
 .long qn_table
.section .text.patch2,"ax",@progbits
 .long 1,1,1,1,2,2,2,2,3,3,3,3,3,4,4,4,5,5,5,6,6,7,7,8,9,9,10,11,12,13,14,15,17,18,20,21,23,25,27,30,33,35,39,42,46,50,54,59,65,70,77,83,91,99,108,118,129,140,153,166,182,198,216,235,257
