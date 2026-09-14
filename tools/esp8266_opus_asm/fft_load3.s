# opus_fft_impl: load a complex PCM value using a single private-stack pointer.
# LX106 call0 ABI: a2/a3 receive exactly the original r/i words; all other
# registers, a1, SAR and memory remain unchanged. No call, spill or new buffer.
# Original: four narrow loads (8 bytes), two reading the same private sp+32.
# New: three loads (3+2+3 bytes), keeping all later code/literal addresses fixed.
# The data reads remain in r-then-i order. No padding is executed.
.section .text.patch0,"ax",@progbits
.begin no-transform
    l32i a3, a1, 32
    l32i.n a2, a3, 0
    l32i a3, a3, 4
.end no-transform
