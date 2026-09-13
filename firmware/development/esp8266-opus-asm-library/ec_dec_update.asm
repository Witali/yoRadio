
C:\Work\yoRadio\.worktree\esp8266-opus-asm\.build\opus-asm-export\optimized-entdec.o:     file format elf32-xtensa-le


Disassembly of section .text.ec_dec_update:

00000000 <ec_dec_update>:
   0:	9268      	l32i.n	a6, a2, 36
   2:	c05540        	sub	a5, a5, a4
   5:	825560        	mull	a5, a5, a6
   8:	8278      	l32i.n	a7, a2, 32
   a:	c07750        	sub	a7, a7, a5
   d:	738c      	beqz.n	a3, 18 <ec_dec_update+0x18>
			d: R_XTENSA_SLOT0_OP	.text.ec_dec_update+0x18
   f:	c03430        	sub	a3, a4, a3
  12:	823360        	mull	a3, a3, a6
  15:	000106        	j	1d <ec_dec_update+0x1d>
			15: R_XTENSA_SLOT0_OP	.text.ec_dec_update+0x1d
  18:	7238      	l32i.n	a3, a2, 28
  1a:	c03350        	sub	a3, a3, a5
  1d:	074d      	mov.n	a4, a7
  1f:	1b0c      	movi.n	a11, 1
  21:	01bb90        	slli	a11, a11, 23
  24:	3d3b37        	bltu	a11, a3, 65 <ec_dec_update+0x65>
			24: R_XTENSA_SLOT0_OP	.text.ec_dec_update+0x65
  27:	0268      	l32i.n	a6, a2, 0
  29:	6278      	l32i.n	a7, a2, 24
  2b:	1288      	l32i.n	a8, a2, 4
  2d:	a298      	l32i.n	a9, a2, 40
  2f:	52a8      	l32i.n	a10, a2, 20
  31:	115980        	slli	a5, a9, 8
  34:	090c      	movi.n	a9, 0
  36:	06b787        	bgeu	a7, a8, 40 <ec_dec_update+0x40>
			36: R_XTENSA_SLOT0_OP	.text.ec_dec_update+0x40
  39:	967a      	add.n	a9, a6, a7
  3b:	000992        	l8ui	a9, a9, 0
  3e:	771b      	addi.n	a7, a7, 1
  40:	205590        	or	a5, a5, a9
  43:	745150        	extui	a5, a5, 1, 8
  46:	114480        	slli	a4, a4, 8
  49:	c04450        	sub	a4, a4, a5
  4c:	01d442        	addmi	a4, a4, 0x100
  4f:	440b      	addi.n	a4, a4, -1
  51:	1144f0        	slli	a4, a4, 1
  54:	414140        	srli	a4, a4, 1
  57:	113380        	slli	a3, a3, 8
  5a:	aa8b      	addi.n	a10, a10, 8
  5c:	d1bb37        	bgeu	a11, a3, 31 <ec_dec_update+0x31>
			5c: R_XTENSA_SLOT0_OP	.text.ec_dec_update+0x31
  5f:	6279      	s32i.n	a7, a2, 24
  61:	a299      	s32i.n	a9, a2, 40
  63:	52a9      	s32i.n	a10, a2, 20
  65:	7239      	s32i.n	a3, a2, 28
  67:	8249      	s32i.n	a4, a2, 32
  69:	f00d      	ret.n
