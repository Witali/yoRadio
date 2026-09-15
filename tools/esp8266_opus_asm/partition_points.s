# quant_partition: precise decoder-only constant propagation, LX106 call0.
# ctx.encode is immutable0 throughout the proven private decoder call chain.
# Keep a7 exactly0; original C/GCC snapshot and all audio decisions unchanged.
# All other internal/external addresses, literals, stack112 and RAM unchanged.
# Two nonvolatile private reads become immediate writes of identical value.
.section .text.patch0,"ax",@progbits
.begin no-transform
 movi.n a7, 0
.end no-transform
.section .text.patch1,"ax",@progbits
.begin no-transform
 movi a7, 0
.end no-transform
# Original BEQZ.N taken over an unreachable encoder J. Preserve its5-byte range.
# Only2 bytes of padding after our unconditional J; these are never executed.
.section .text.patch2,"ax",@progbits
.begin no-transform
 j point_4024dbd8
 .space 2, 0
.end no-transform
.section .text.patch3,"ax",@progbits
.begin no-transform
 j point_4024e36e
.end no-transform
.section .text.patch4,"ax",@progbits
.begin no-transform
 j point_4024e297
.end no-transform
