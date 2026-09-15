# LX106 call0 quant_partition: skip sixth PVQ probe when hi-lo<=1.
# Main site after five probes: a2=cache, a6=hi, a9=lo, a8=bits-1.
# Restore a4=lo for nearest-endpoint code; a10/a11 are dead at audited exits.
# No stack, table, SAR or allocation change. All outside addresses unchanged.
# Rare sixth probe uses encoder-only bytes, proven unreachable for encode=0.
.section .text.patch0,"ax",@progbits
.begin no-transform
 sub a10, a6, a9
 mov.n a4, a9
 bgei a10, 2, sixth_probe
 j nearest_endpoint
 .space 9, 0
.end no-transform
.section .text.patch1,"ax",@progbits
.begin no-transform
 add.n a4, a6, a9
 addi.n a4, a4, 1
 srai a4, a4, 1
 add.n a10, a2, a4
 l8ui a10, a10, 0
 blt a10, a8, nearest_endpoint
 mov.n a6, a4
 mov.n a4, a9
 j nearest_endpoint
 .space 6, 0
.end no-transform
