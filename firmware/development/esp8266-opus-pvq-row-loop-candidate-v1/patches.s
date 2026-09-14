# decode_pulses/cwrsi, LX106 call0: frequent many-pulses row search.
# Entry only after row[K] > unsigned entropy index; at least one more probe.
# a2=index, a6=row, a12=K, a13=N, a15=&row[K]. Frame48 and ABI unchanged.
# Reuse a15, decrement K directly; remove per-probe MOV and unconditional J.
# Probe row[K-j], j=1,... in identical order, NEVER prefetch the next value.
# At exit a3=a12=remaining K, a9=K<<16, a11=sign_extend16(K), a6=N-1.
# Other registers/SAR/memory unchanged. Old entry0x40253331, end0x40253354.
# Valid modes/bitrates unchanged; original GCC ASM and C fallback untouched.
.section .text.patch0,"ax",@progbits
.begin no-transform
addi a6, a15, -4
.Lprobe:
l32i.n a8, a6, 0
addi a6, a6, -4
addi.n a12, a12, -1
bltu a2, a8, .Lprobe
mov.n a3, a12
slli a9, a3, 16
srai a11, a9, 16
addi.n a6, a13, -1
j pvq_row_done
.space 9, 0
.end no-transform
