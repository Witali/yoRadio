# ec_dec_bit_logp: delay the existing 16-byte frame until normalization.
# call0 leaf ABI: a2=ec_dec*, a3=logp; result a2. Preserve a0/a1/a12..a15.
# Fast temporaries a3..a6/a9 are caller-saved; SAR receives the original logp.
# The exact original range/value update precedes the threshold check.
# Equality rng == EC_CODE_BOT MUST normalize, including zero-padded input.
# Cold path enters the unchanged GCC normalization loop with original live
# registers: a2=ctx,a3=rng,a4=val,a9=BOT,a13=bit. No new table or allocation.
	l32i.n	a5, a2, 28
	l32i.n	a4, a2, 32
	ssr	a3
	srl	a3, a5
	movi.n	a6, 1
	bltu	a4, a3, .Llogp_value_ready
	movi.n	a6, 0
	sub	a4, a4, a3
	s32i.n	a4, a2, 32
	sub	a3, a5, a3
.Llogp_value_ready:
	l32r	a9, .LC5
	s32i.n	a3, a2, 28
	bgeu	a9, a3, .Llogp_normalize
	mov.n	a2, a6
	ret.n
.Llogp_normalize:
	addi	sp, sp, -16
	s32i.n	a13, sp, 8
	s32i.n	a12, sp, 12
	s32i.n	a14, sp, 4
	s32i.n	a15, sp, 0
	mov.n	a13, a6
