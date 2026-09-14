# clt_mdct_backward_c bitrev pair cache, Xtensa LX106 call0.
# Original return address is saved at sp+92 in the unchanged96-byte frame.
# a0 unused until FFT CALL0: cache one immutable aligned32-bit word for two iterations.
# a2/a5/a7 old temporary values dead before any read; all other registers and SAR exact.
# Pinned standard mode tables start word aligned; a12 advances by2, first iteration loads low half.
# No custom-mode behavior is silently changed: generator validates linked tables and parent.
# No new RAM, stack or buffer, no scalar16-bit flash load. C fallback/snapshot unchanged.
.section .text.patch0,"ax",@progbits
.begin no-transform
bbsi a12, 1, .Lhigh
l32i.n a0, a12, 0
slli a6, a0, 16
srai a6, a6, 16
j .Lend
.Lhigh:
srai a6, a0, 16
j .Lend
.space 4, 0
.Lend:
.end no-transform
