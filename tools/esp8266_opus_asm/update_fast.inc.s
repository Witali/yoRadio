# Exact decoder-only fast path for ec_dec_update at two CELT bands call sites.
# ABI: a2=48-byte DRAM ec_dec*, a3=fl, a4=fh, a5=ft; returns void.
# Scratch: a6=ext, a7=s, a8=new_rng, a9=threshold/val. No stack or literal pool.
# Preserve a2..a5 until the fallback call, all a12..a15, a1 and SAR.
# Fast path writes only rng/val. Cold path writes NOTHING before calling the
# original GCC function with original arguments, so it cannot update twice.
# Exact uint32 arithmetic: s=ext*(ft-fh); rng=fl?ext*(fh-fl):old_rng-s.
# EC_CODE_BOT is 1<<23; equality MUST normalize and use the original function.
# Leave caller spills, encoder code and the original shared function untouched.
# No speed claim until raw physical A/B; cold paths duplicate this small guard.
.macro Y_OPUS_UPDATE_FAST
    l32i.n a6, a2, 36
    sub a7, a5, a4
    mull a7, a7, a6
    beqz.n a3, .Lasm_update_fast_zero\@
    sub a8, a4, a3
    mull a8, a8, a6
    j .Lasm_update_fast_check\@
.Lasm_update_fast_zero\@:
    l32i.n a8, a2, 28
    sub a8, a8, a7
.Lasm_update_fast_check\@:
    movi.n a9, 1
    slli a9, a9, 23
    bgeu a9, a8, .Lasm_update_fast_cold\@
    l32i.n a9, a2, 32
    sub a9, a9, a7
    s32i.n a8, a2, 28
    s32i.n a9, a2, 32
    j .Lasm_update_fast_done\@
.Lasm_update_fast_cold\@:
    call0 ec_dec_update
.Lasm_update_fast_done\@:
.endm
