# Exact ec_dec_bits(ctx, 1) fast path at three pinned decoder sign sites.
# ABI call0: a2=48-byte DRAM ec_dec*, a3=1, result a2=0/1.
# Clobbers a4..a7 only on fast path; preserves a1, a12..a15 and SAR.
# nend_bits!=0 is the original unsigned comparison available>=1.
# Cold path changes neither arguments nor state; original GCC refills from
# the packet (including truncated-input zero padding). No UART, heap or stack.
# Fast path consumes one low bit, shifts window, decrements nend_bits and
# increments nbits_total exactly. All context access is aligned 32-bit.
# Caller argument setup/spills remain unchanged. Do not use for bits!=1.
.macro Y_OPUS_BITS1_FAST
    l32i.n a4, a2, 16
    beqz.n a4, .Lasm_bits1_cold\@
    l32i.n a5, a2, 12
    l32i.n a6, a2, 20
    addi.n a4, a4, -1
    srli a7, a5, 1
    addi.n a6, a6, 1
    s32i.n a7, a2, 12
    s32i.n a4, a2, 16
    s32i.n a6, a2, 20
    extui a2, a5, 0, 1
    j .Lasm_bits1_done\@
.Lasm_bits1_cold\@:
    call0 ec_dec_bits
.Lasm_bits1_done\@:
.endm
