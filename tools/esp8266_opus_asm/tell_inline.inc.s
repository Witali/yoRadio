# Selective inline expansion of GCC's exact ec_tell_frac body.
# Derived from upstream/celt/entcode.c; upstream/COPYING and its license apply.
# Input a2=ec_ctx; output a2=bit usage in eighth-bits. Clobbers a3..a6, SAR.
# Preserves a0/a1/a7..a15 and all memory. No stack slots or extra table copy.
# .Lasm_tell_table references an alias of the ORIGINAL correction[8].
# The original function remains available to every other call site.
# Unique GAS labels allow repeated expansion in one function. Caller spills
# are intentionally unchanged: there is no new compiler register allocation.
	.macro Y_OPUS_TELL_FRAC
	l32i.n	a5, a2, 28
	movi.n	a4, 0x10
	nsau	a3, a5
	sub	a4, a4, a3
	l32i.n	a2, a2, 20
	ssr	a4
	srl	a4, a5
	srli	a5, a4, 12
	addi	a5, a5, -8
	add.n	a3, a3, a2
	l32r	a2, .Lasm_tell_table
	slli	a6, a5, 2
	add.n	a2, a2, a6
	addi	a3, a3, -32
	l32i.n	a6, a2, 0
	slli	a3, a3, 3
	sub	a3, a3, a5
	movi.n	a2, 1
	bltu	a6, a4, .Lasm_tell_done\@
	movi.n	a2, 0
.Lasm_tell_done\@:
	sub	a2, a3, a2
	.endm
