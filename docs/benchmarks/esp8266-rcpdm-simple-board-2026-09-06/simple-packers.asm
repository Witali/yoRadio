40214f40 <i2s_pdm_pack32>:
40214f40:	ed56a1        	l32r	a10, 40210498 <_stext+0x488>
40214f43:	ed5461        	l32r	a6, 40210494 <_stext+0x484>
40214f46:	0a38      	l32i.n	a3, a10, 0
40214f48:	626a      	add.n	a6, a2, a6
40214f4a:	ed54b1        	l32r	a11, 4021049c <_stext+0x48c>
40214f4d:	020c      	movi.n	a2, 0
40214f4f:	116600        	slli	a6, a6, 16
40214f52:	052c      	movi.n	a5, 32
40214f54:	180c      	movi.n	a8, 1
40214f56:	029d      	mov.n	a9, a2
40214f58:	414430        	srli	a4, a3, 4
40214f5b:	207880        	or	a7, a8, a8
40214f5e:	023367        	bltu	a3, a6, 40214f64 <i2s_pdm_pack32+0x24>
40214f61:	207990        	or	a7, a9, a9
40214f64:	c04340        	sub	a4, a3, a4
40214f67:	05b367        	bgeu	a3, a6, 40214f70 <i2s_pdm_pack32+0x30>
40214f6a:	34ba      	add.n	a3, a4, a11
40214f6c:	000086        	j	40214f72 <i2s_pdm_pack32+0x32>
40214f6f:	043d00        	extui	a3, a0, 13, 1
40214f72:	1122f0        	slli	a2, a2, 1
40214f75:	550b      	addi.n	a5, a5, -1
40214f77:	202720        	or	a2, a7, a2
40214f7a:	fda556        	bnez	a5, 40214f58 <i2s_pdm_pack32+0x18>
40214f7d:	0a39      	s32i.n	a3, a10, 0
40214f7f:	f00d      	ret.n
40214f81:	000000        	ill


40214f84 <i2s_rcpdm_fill>:
40214f84:	f0c112        	addi	a1, a1, -16
40214f87:	ed4471        	l32r	a7, 40210498 <_stext+0x488>
40214f8a:	31c9      	s32i.n	a12, a1, 12
40214f8c:	21d9      	s32i.n	a13, a1, 8
40214f8e:	11e9      	s32i.n	a14, a1, 4
40214f90:	01f9      	s32i.n	a15, a1, 0
40214f92:	0768      	l32i.n	a6, a7, 0
40214f94:	052526        	beqi	a5, 2, 40214f9d <i2s_rcpdm_fill+0x19>
40214f97:	05e456        	bnez	a4, 40214ff9 <i2s_rcpdm_fill+0x75>
40214f9a:	002906        	j	40215042 <i2s_rcpdm_fill+0xbe>
40214f9d:	0a1416        	beqz	a4, 40215042 <i2s_rcpdm_fill+0xbe>
40214fa0:	1144e0        	slli	a4, a4, 2
40214fa3:	ed3c91        	l32r	a9, 40210494 <_stext+0x484>
40214fa6:	ed3dc1        	l32r	a12, 4021049c <_stext+0x48c>
40214fa9:	434a      	add.n	a4, a3, a4
40214fab:	0a0c      	movi.n	a10, 0
40214fad:	01a0b2        	movi	a11, 1
40214fb0:	019352        	l16si	a5, a3, 2
40214fb3:	0093d2        	l16si	a13, a3, 0
40214fb6:	082c      	movi.n	a8, 32
40214fb8:	d5da      	add.n	a13, a5, a13
40214fba:	055fd0        	extui	a5, a13, 31, 1
40214fbd:	55da      	add.n	a5, a5, a13
40214fbf:	215150        	srai	a5, a5, 1
40214fc2:	559a      	add.n	a5, a5, a9
40214fc4:	115500        	slli	a5, a5, 16
40214fc7:	0add      	mov.n	a13, a10
40214fc9:	41e460        	srli	a14, a6, 4
40214fcc:	0bfd      	mov.n	a15, a11
40214fce:	023657        	bltu	a6, a5, 40214fd4 <i2s_rcpdm_fill+0x50>
40214fd1:	20faa0        	or	a15, a10, a10
40214fd4:	c0e6e0        	sub	a14, a6, a14
40214fd7:	05b657        	bgeu	a6, a5, 40214fe0 <i2s_rcpdm_fill+0x5c>
40214fda:	6eca      	add.n	a6, a14, a12
40214fdc:	000086        	j	40214fe2 <i2s_rcpdm_fill+0x5e>
40214fdf:	0e6d00        	excw
40214fe2:	11ddf0        	slli	a13, a13, 1
40214fe5:	880b      	addi.n	a8, a8, -1
40214fe7:	20ddf0        	or	a13, a13, a15
40214fea:	fdb856        	bnez	a8, 40214fc9 <i2s_rcpdm_fill+0x45>
40214fed:	02d9      	s32i.n	a13, a2, 0
40214fef:	334b      	addi.n	a3, a3, 4
40214ff1:	224b      	addi.n	a2, a2, 4
40214ff3:	b99437        	bne	a4, a3, 40214fb0 <i2s_rcpdm_fill+0x2c>
40214ff6:	001206        	j	40215042 <i2s_rcpdm_fill+0xbe>
40214ff9:	1144f0        	slli	a4, a4, 1
40214ffc:	ed2691        	l32r	a9, 40210494 <_stext+0x484>
40214fff:	ed27f1        	l32r	a15, 4021049c <_stext+0x48c>
40215002:	434a      	add.n	a4, a3, a4
40215004:	0d0c      	movi.n	a13, 0
40215006:	1e0c      	movi.n	a14, 1
40215008:	009352        	l16si	a5, a3, 0
4021500b:	0b2c      	movi.n	a11, 32
4021500d:	559a      	add.n	a5, a5, a9
4021500f:	115500        	slli	a5, a5, 16
40215012:	0d8d      	mov.n	a8, a13
40215014:	41a460        	srli	a10, a6, 4
40215017:	20cee0        	or	a12, a14, a14
4021501a:	023657        	bltu	a6, a5, 40215020 <i2s_rcpdm_fill+0x9c>
4021501d:	20cdd0        	or	a12, a13, a13
40215020:	c0a6a0        	sub	a10, a6, a10
40215023:	05b657        	bgeu	a6, a5, 4021502c <i2s_rcpdm_fill+0xa8>
40215026:	6afa      	add.n	a6, a10, a15
40215028:	000086        	j	4021502e <i2s_rcpdm_fill+0xaa>
4021502b:	0a6d00        	excw
4021502e:	1188f0        	slli	a8, a8, 1
40215031:	bb0b      	addi.n	a11, a11, -1
40215033:	208c80        	or	a8, a12, a8
40215036:	fdab56        	bnez	a11, 40215014 <i2s_rcpdm_fill+0x90>
40215039:	0289      	s32i.n	a8, a2, 0
4021503b:	332b      	addi.n	a3, a3, 2
4021503d:	224b      	addi.n	a2, a2, 4
4021503f:	c59347        	bne	a3, a4, 40215008 <i2s_rcpdm_fill+0x84>
40215042:	31c8      	l32i.n	a12, a1, 12
40215044:	21d8      	l32i.n	a13, a1, 8
40215046:	11e8      	l32i.n	a14, a1, 4
40215048:	01f8      	l32i.n	a15, a1, 0
4021504a:	0769      	s32i.n	a6, a7, 0
4021504c:	10c112        	addi	a1, a1, 16
4021504f:	f00d      	ret.n
40215051:	000000        	ill
