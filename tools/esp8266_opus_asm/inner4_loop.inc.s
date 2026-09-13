# renormalise_vector's inlined celt_inner_prod(X,X,N), N >= 8.
# Entry: a6=X, a3=X+2*N, a14=2*N, a2=0. The original N<=0 guard stays.
# a4/a7 are dead at the join (caller-saved, not read before redefinition/call).
# Preserve the scalar order and every MUL/ADD low bit. No new stack or table.
# Paired loads separate L16SI from its dependent MUL, without reading past N.
# a7 is the end of complete four-element groups, calculated once per vector.
	blti	a14, 16, .L182
	srli	a7, a14, 3
	slli	a7, a7, 3
	add.n	a7, a6, a7
.Linner4_bulk:
	l16si	a4, a6, 0
	l16si	a5, a6, 2
	mull	a4, a4, a4
	add.n	a2, a2, a4
	mull	a5, a5, a5
	add.n	a2, a2, a5
	l16si	a4, a6, 4
	l16si	a5, a6, 6
	mull	a4, a4, a4
	add.n	a2, a2, a4
	mull	a5, a5, a5
	add.n	a2, a2, a5
	addi.n	a6, a6, 8
	bne	a7, a6, .Linner4_bulk
	beq	a3, a6, .Linner4_done
# One to three remaining elements use the unchanged scalar loop below.
