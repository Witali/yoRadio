# LX106 call0 quant_partition nearest-endpoint tail.
# Keep upper cost in a10, lower cost in a11, and publish selected cost in a8.
# a4 still holds selected q; a9 holds the unchanged upper distance.
# a10/a11 are proven dead at both continuation points. No SRAM, SAR or ABI change.
# Each point retains the exact instruction address/width. Register self-copies
# preserve slots, avoiding a relink or movement of any subsequent instruction.
.section .text.patch0,"ax",@progbits
.begin no-transform
 l8ui a10, a9, 0
.end no-transform
.section .text.patch1,"ax",@progbits
.begin no-transform
 sub a9, a10, a8
.end no-transform
.section .text.patch2,"ax",@progbits
.begin no-transform
 add.n a11, a2, a4
.end no-transform
.section .text.patch3,"ax",@progbits
.begin no-transform
 l8ui a11, a11, 0
.end no-transform
.section .text.patch4,"ax",@progbits
.begin no-transform
 mov.n a10, a10
.end no-transform
.section .text.patch5,"ax",@progbits
.begin no-transform
 mov.n a11, a10
.end no-transform
.section .text.patch6,"ax",@progbits
.begin no-transform
 mov.n a8, a11
.end no-transform
.section .text.patch7,"ax",@progbits
.begin no-transform
 or a10, a10, a10
.end no-transform
