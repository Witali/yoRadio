40214f58 <i2s_pdm_pack32>:
40214f58:	ed5041        	l32r	a4, 40210498 <_stext+0x488>
40214f5b:	ed4e71        	l32r	a7, 40210494 <_stext+0x484>
40214f5e:	424a      	add.n	a4, a2, a4
40214f60:	0738      	l32i.n	a3, a7, 0
40214f62:	114400        	slli	a4, a4, 16
40214f65:	020c      	movi.n	a2, 0
40214f67:	052c      	movi.n	a5, 32
40214f69:	ed4c61        	l32r	a6, 4021049c <_stext+0x48c>
40214f6c:	418430        	srli	a8, a3, 4
40214f6f:	1122f0        	slli	a2, a2, 1
40214f72:	03b347        	bgeu	a3, a4, 40214f79 <i2s_pdm_pack32+0x21>
40214f75:	336a      	add.n	a3, a3, a6
40214f77:	221b      	addi.n	a2, a2, 1
40214f79:	c03380        	sub	a3, a3, a8
40214f7c:	550b      	addi.n	a5, a5, -1
40214f7e:	fea556        	bnez	a5, 40214f6c <i2s_pdm_pack32+0x14>
40214f81:	0739      	s32i.n	a3, a7, 0
40214f83:	f00d      	ret.n
40214f85:	000000        	ill


40214f88 <i2s_rcpdm_fill>:
40214f88:	f0c112        	addi	a1, a1, -16
40214f8b:	ed4261        	l32r	a6, 40210494 <_stext+0x484>
40214f8e:	31c9      	s32i.n	a12, a1, 12
40214f90:	21d9      	s32i.n	a13, a1, 8
40214f92:	11e9      	s32i.n	a14, a1, 4
40214f94:	0678      	l32i.n	a7, a6, 0
40214f96:	062526        	beqi	a5, 2, 40214fa0 <i2s_rcpdm_fill+0x18>
40214f99:	054456        	bnez	a4, 40214ff1 <i2s_rcpdm_fill+0x69>
40214f9c:	002286        	j	4021502a <i2s_rcpdm_fill+0xa2>
40214f9f:	641600        	extui	a1, a0, 6, 7
40214fa2:	e008      	l32i.n	a0, a0, 56
40214fa4:	911144        	excw
40214fa7:	ed3c      	movi.n	a13, 62
40214fa9:	ed3c81        	l32r	a8, 4021049c <_stext+0x48c>
40214fac:	804340        	add	a4, a3, a4
40214faf:	00a0b2        	movi	a11, 0
40214fb2:	0a2c      	movi.n	a10, 32
40214fb4:	009352        	l16si	a5, a3, 0
40214fb7:	0193c2        	l16si	a12, a3, 2
40214fba:	0add      	mov.n	a13, a10
40214fbc:	c5ca      	add.n	a12, a5, a12
40214fbe:	055fc0        	extui	a5, a12, 31, 1
40214fc1:	55ca      	add.n	a5, a5, a12
40214fc3:	215150        	srai	a5, a5, 1
40214fc6:	559a      	add.n	a5, a5, a9
40214fc8:	115500        	slli	a5, a5, 16
40214fcb:	0bcd      	mov.n	a12, a11
40214fcd:	41e470        	srli	a14, a7, 4
40214fd0:	11ccf0        	slli	a12, a12, 1
40214fd3:	05b757        	bgeu	a7, a5, 40214fdc <i2s_rcpdm_fill+0x54>
40214fd6:	807780        	add	a7, a7, a8
40214fd9:	01ccc2        	addi	a12, a12, 1
40214fdc:	c077e0        	sub	a7, a7, a14
40214fdf:	dd0b      	addi.n	a13, a13, -1
40214fe1:	fe8d56        	bnez	a13, 40214fcd <i2s_rcpdm_fill+0x45>
40214fe4:	02c9      	s32i.n	a12, a2, 0
40214fe6:	334b      	addi.n	a3, a3, 4
40214fe8:	224b      	addi.n	a2, a2, 4
40214fea:	c69437        	bne	a4, a3, 40214fb4 <i2s_rcpdm_fill+0x2c>
40214fed:	000e46        	j	4021502a <i2s_rcpdm_fill+0xa2>
40214ff0:	44f000        	extui	a15, a0, 0, 5
40214ff3:	299111        	l32r	a1, 401df638 <_iram_bss_end+0xdad48>
40214ff6:	81ed      	excw
40214ff8:	ed29      	s32i.n	a2, a13, 56
40214ffa:	434a      	add.n	a4, a3, a4
40214ffc:	0c0c      	movi.n	a12, 0
40214ffe:	0b2c      	movi.n	a11, 32
40215000:	009352        	l16si	a5, a3, 0
40215003:	0cad      	mov.n	a10, a12
40215005:	559a      	add.n	a5, a5, a9
40215007:	115500        	slli	a5, a5, 16
4021500a:	0bdd      	mov.n	a13, a11
4021500c:	41e470        	srli	a14, a7, 4
4021500f:	11aaf0        	slli	a10, a10, 1
40215012:	03b757        	bgeu	a7, a5, 40215019 <i2s_rcpdm_fill+0x91>
40215015:	778a      	add.n	a7, a7, a8
40215017:	aa1b      	addi.n	a10, a10, 1
40215019:	c077e0        	sub	a7, a7, a14
4021501c:	dd0b      	addi.n	a13, a13, -1
4021501e:	fead56        	bnez	a13, 4021500c <i2s_rcpdm_fill+0x84>
40215021:	02a9      	s32i.n	a10, a2, 0
40215023:	332b      	addi.n	a3, a3, 2
40215025:	224b      	addi.n	a2, a2, 4
40215027:	d59437        	bne	a4, a3, 40215000 <i2s_rcpdm_fill+0x78>
4021502a:	31c8      	l32i.n	a12, a1, 12
4021502c:	21d8      	l32i.n	a13, a1, 8
4021502e:	11e8      	l32i.n	a14, a1, 4
40215030:	0679      	s32i.n	a7, a6, 0
40215032:	10c112        	addi	a1, a1, 16
40215035:	f00d      	ret.n
	...
