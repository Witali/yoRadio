# LX106 compute_qn: duplicate eight signed constants as aligned words in flash.
# Keep every instruction address/width. No helper, call, stack or RAM allocation.
# a4 temporarily contains four times the index instead of twice, then the
# original MOVI at0x4024dc79 overwrites it before any observer can use it.
# a3, all other GPRs and SAR match at0x4024dc7b. C fallback is unchanged.
# The original int16 table remains intact for other clones. Authenticate the
# literal's sole instruction reader and the decoder-inaccessible table slot.
.section .text.patch0,"ax",@progbits
.begin no-transform
 slli a4, a3, 2
.end no-transform
.section .text.patch1,"ax",@progbits
.begin no-transform
 l32i a3, a3, 0
.end no-transform
.section .text.patch2,"ax",@progbits
 .long pvq_exp2_table32
.section .text.patch3,"ax",@progbits
 .long 16384,17866,19483,21247,23170,25267,27554,30048
