# LX106 call0 quant_partition: early exit after four PVQ probes.
# Entry: a2=cache, a4=lo, a6=hi, a8=bits-1; a10/a11 dead at audited joins.
# lo-hi >= -1 is equivalent to hi-lo<=1 for bounded cache indices.
# This SUB/BGEI needs no constant register, SAR change or temporary memory.
# Retain the accepted fifth-step shortcut and the existing sixth_probe stub.
# The whole40-byte range is fixed; all outside instructions/tables unchanged.
.section .text.patch0,"ax",@progbits
.begin no-transform
 sub a10, a4, a6
 bgei a10, -1, nearest_endpoint
# Unchanged fifth probe, with identical MOV in place of three-byte OR.
 add.n a9, a6, a4
 addi.n a9, a9, 1
 srai a9, a9, 1
 add.n a10, a2, a9
 l8ui a10, a10, 0
 blt a10, a8, fifth_done
 mov.n a6, a9
 mov.n a9, a4
fifth_done:
 sub a10, a6, a9
 mov.n a4, a9
 bgei a10, 2, sixth_probe
 j nearest_endpoint
 .space 4, 0
.end no-transform
