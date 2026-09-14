# opus_fft_impl radix-5: schedule an independent stack load between loading
# Fout0 and dereferencing it. Experimental LX106 call0; no latency assumption.
# a2/a3 = identical PCM r/i, a4 = same twiddle pointer, a6 = same packed word.
# Private sp+100 differs from the two written words sp+156/sp+164. Twiddle data
# is still read AFTER both stores: it may alias those addresses in the proof.
# All other registers, a1, SAR and memory are preserved. No calls/new scratch.
# 8 -> 7 instructions, widths 3+3+2+3+3+3+2 = original 19 bytes, no NOP.
.section .text.patch0,"ax",@progbits
.begin no-transform
    l32i a3, a1, 32
    l32i a4, a1, 100
    l32i.n a2, a3, 0
    l32i a3, a3, 4
    s32i a2, a1, 156
    s32i a3, a1, 164
    l32i.n a6, a4, 0
.end no-transform
