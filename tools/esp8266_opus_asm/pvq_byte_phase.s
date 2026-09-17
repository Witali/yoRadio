# LX106 call0: a10 byte address -> unsigned byte, dead a11 is scratch.
# Preserve a0 (the CALL0 return), all other GPRs, memory, and SAR without
# reading/writing SAR. One aligned word load, two phase decisions.
# Seven executed instructions vs nine in the accepted a10 SAR helper.
# Six authenticated callers, including the upper endpoint, not all L8UI.
# New helper occupies 42 proven encoder-only bytes; original helper remains
# unchanged but unreachable. C fallback and all other addresses are intact.
.section .text.patch0,"ax",@progbits
.begin no-transform
.Lphase_start:
 extui a11, a10, 0, 2
 sub a10, a10, a11
 l32i.n a10, a10, 0
 bbci a11, 1, .Lphase_low
 bbci a11, 0, .Lphase_two
 extui a10, a10, 24, 8
 ret.n
.Lphase_two:
 extui a10, a10, 16, 8
 ret.n
.Lphase_low:
 bbci a11, 0, .Lphase_zero
 extui a10, a10, 8, 8
 ret.n
.Lphase_zero:
 extui a10, a10, 0, 8
 ret.n
 .space 42-(.-.Lphase_start),0
.end no-transform
.section .text.patch1,"ax",@progbits
.begin no-transform
 call0 pvq_byte_phase
.end no-transform
.section .text.patch2,"ax",@progbits
.begin no-transform
 call0 pvq_byte_phase
.end no-transform
.section .text.patch3,"ax",@progbits
.begin no-transform
 call0 pvq_byte_phase
.end no-transform
.section .text.patch4,"ax",@progbits
.begin no-transform
 call0 pvq_byte_phase
.end no-transform
.section .text.patch5,"ax",@progbits
.begin no-transform
 call0 pvq_byte_phase
.end no-transform
.section .text.patch6,"ax",@progbits
.begin no-transform
 call0 pvq_byte_phase
.end no-transform
