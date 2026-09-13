# Fuse normalise_residual + extract_collapse_mask in alg_unquant only.
# Entry: a4=iy (aligned words), a5=X (int16), a6=k+1, a8=N, a9=B,
# a10=g, a11=rounding bias, a12=X base, a13=iy base, a14=K.
# Preserve a1/a4..a6/a9..a14 as needed by the original continuation;
# a4/a5 advance, a7 restored to X. a0 is scratch: return address is already
# saved at sp+108. a15=k is dead after normalization. No calls/IRQ masking.
# sp+72 is UNUSED in the pinned 112-byte frame, proven by the generator.
# Store -1 for original fallback or a 0..255 mask for B=2/4/8, N%B=0.
# Every iy is loaded ONCE, ORed BEFORE mul16s truncation/PCM rounding.
# B<=1 retains the original no-mask loop; custom shapes retain the late pass.
	blti	a9, 2, .Lasm_fused_fallback
	bgei	a9, 16, .Lasm_fused_fallback
	blt	a8, a9, .Lasm_fused_fallback
	addi	a2, a9, -1
	and	a0, a9, a2
	bnez	a0, .Lasm_fused_fallback
	and	a0, a8, a2
	bnez	a0, .Lasm_fused_fallback
	nsau	a2, a9
	movi	a0, 31
	sub	a2, a0, a2
	ssr	a2
	srl	a15, a8
	movi	a7, 1
	movi	a3, 0
.Lasm_fused_block:
	movi	a0, 0
	mov	a8, a15
.Lasm_fused_sample:
	l32i	a2, a4, 0
	or	a0, a0, a2
	mul16s	a2, a2, a10
	addi	a4, a4, 4
	add	a2, a2, a11
	ssr	a6
	sra	a2, a2
	s16i	a2, a5, 0
	addi	a5, a5, 2
	addi	a8, a8, -1
	bnez	a8, .Lasm_fused_sample
	movi	a2, 0
	movnez	a2, a7, a0
	or	a3, a3, a2
	slli	a7, a7, 1
	addi	a9, a9, -1
	bnez	a9, .Lasm_fused_block
	s32i	a3, sp, 72
	l32i	a9, sp, 68
	mov	a7, a12
	j	.Lasm_fused_after_normalize
.Lasm_fused_fallback:
	movi	a2, -1
	s32i	a2, sp, 72
