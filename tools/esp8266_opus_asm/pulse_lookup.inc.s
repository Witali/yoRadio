# ASM pulse lookup: inline shortcut at quant_partition .L22.
# Inputs: a2=cache row, a6=cache[0], a14=bits BEFORE original bits--.
# Scratch: a4,a8,a9,a10,SAR. Preserve a2,a3=N,a5=spread,a6,a7=encode,
# a0,a1,a12=ctx,a13=B,a14=bits,a15=X and every stack slot.
# Only original static cache row starts and bits 0..256 use the table.
# Every other pointer/budget retains the exact GCC search (including custom modes).
# Packed table accesses are aligned L32I; no byte IRAM loads, calls or stores.
# Exit .L60: nonzero q in a4/a10. Exit .L61: q=0, no bits consumed.
	l32r	a8, .Lasm_pulse_base
	sub	a9, a2, a8
	movi	a10, 392
	bgeu	a9, a10, .Lasm_pulse_fallback
	movi	a8, 256
	bltu	a8, a14, .Lasm_pulse_fallback
	l32r	a8, .Lasm_pulse_map
	movi	a10, -4
	and	a10, a9, a10
	add	a8, a8, a10
	l32i	a8, a8, 0
	extui	a9, a9, 0, 2
	slli	a9, a9, 3
	ssr	a9
	srl	a8, a8
	extui	a8, a8, 0, 8
	movi	a9, 255
	beq	a8, a9, .Lasm_pulse_fallback
# 260 bytes per row = 256*r + 4*r; last word contains b=256 and padding.
	slli	a9, a8, 8
	addx4	a9, a8, a9
	extui	a10, a14, 0, 2
	slli	a10, a10, 3
	movi	a8, -4
	and	a8, a14, a8
	add	a9, a9, a8
	l32r	a8, .Lasm_pulse_inverse
	add	a8, a8, a9
	l32i	a4, a8, 0
	ssr	a10
	srl	a4, a4
	extui	a4, a4, 0, 8
	beqz	a4, .L61
	mov	a10, a4
	j	.L60
.Lasm_pulse_fallback:
