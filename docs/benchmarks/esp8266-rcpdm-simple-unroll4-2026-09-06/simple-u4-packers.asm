40215068 <i2s_pdm_pack32>:
40215068:	ed0c41        	l32r	a4, 40210498 <_stext+0x488>
4021506b:	ed0a71        	l32r	a7, 40210494 <_stext+0x484>
4021506e:	424a      	add.n	a4, a2, a4
40215070:	0738      	l32i.n	a3, a7, 0
40215072:	114400        	slli	a4, a4, 16
40215075:	020c      	movi.n	a2, 0
40215077:	850c      	movi.n	a5, 8
40215079:	ed0861        	l32r	a6, 4021049c <_stext+0x48c>
4021507c:	418430        	srli	a8, a3, 4
4021507f:	1122f0        	slli	a2, a2, 1
40215082:	03b347        	bgeu	a3, a4, 40215089 <i2s_pdm_pack32+0x21>
40215085:	336a      	add.n	a3, a3, a6
40215087:	221b      	addi.n	a2, a2, 1
40215089:	c03380        	sub	a3, a3, a8
4021508c:	418430        	srli	a8, a3, 4
4021508f:	1122f0        	slli	a2, a2, 1
40215092:	03b347        	bgeu	a3, a4, 40215099 <i2s_pdm_pack32+0x31>
40215095:	336a      	add.n	a3, a3, a6
40215097:	221b      	addi.n	a2, a2, 1
40215099:	c03380        	sub	a3, a3, a8
4021509c:	418430        	srli	a8, a3, 4
4021509f:	1122f0        	slli	a2, a2, 1
402150a2:	03b347        	bgeu	a3, a4, 402150a9 <i2s_pdm_pack32+0x41>
402150a5:	336a      	add.n	a3, a3, a6
402150a7:	221b      	addi.n	a2, a2, 1
402150a9:	c03380        	sub	a3, a3, a8
402150ac:	418430        	srli	a8, a3, 4
402150af:	1122f0        	slli	a2, a2, 1
402150b2:	03b347        	bgeu	a3, a4, 402150b9 <i2s_pdm_pack32+0x51>
402150b5:	336a      	add.n	a3, a3, a6
402150b7:	221b      	addi.n	a2, a2, 1
402150b9:	c03380        	sub	a3, a3, a8
402150bc:	550b      	addi.n	a5, a5, -1
402150be:	fba556        	bnez	a5, 4021507c <i2s_pdm_pack32+0x14>
402150c1:	0739      	s32i.n	a3, a7, 0
402150c3:	f00d      	ret.n
402150c5:	000000        	ill


40214f58 <i2s_rcpdm_fill>:
40214f58:	f0c112        	addi	a1, a1, -16
40214f5b:	ed4e61        	l32r	a6, 40210494 <_stext+0x484>
40214f5e:	31c9      	s32i.n	a12, a1, 12
40214f60:	21d9      	s32i.n	a13, a1, 8
40214f62:	11e9      	s32i.n	a14, a1, 4
40214f64:	0678      	l32i.n	a7, a6, 0
40214f66:	062526        	beqi	a5, 2, 40214f70 <i2s_rcpdm_fill+0x18>
40214f69:	084456        	bnez	a4, 40214ff1 <i2s_rcpdm_fill+0x99>
40214f6c:	003a86        	j	4021505a <i2s_rcpdm_fill+0x102>
40214f6f:	641600        	extui	a1, a0, 6, 7
40214f72:	0e          	.byte 0xe
40214f73:	1144e0        	slli	a4, a4, 2
40214f76:	ed4891        	l32r	a9, 40210498 <_stext+0x488>
40214f79:	ed4881        	l32r	a8, 4021049c <_stext+0x48c>
40214f7c:	804340        	add	a4, a3, a4
40214f7f:	00a0b2        	movi	a11, 0
40214f82:	8a0c      	movi.n	a10, 8
40214f84:	009352        	l16si	a5, a3, 0
40214f87:	0193c2        	l16si	a12, a3, 2
40214f8a:	0add      	mov.n	a13, a10
40214f8c:	c5ca      	add.n	a12, a5, a12
40214f8e:	055fc0        	extui	a5, a12, 31, 1
40214f91:	55ca      	add.n	a5, a5, a12
40214f93:	215150        	srai	a5, a5, 1
40214f96:	559a      	add.n	a5, a5, a9
40214f98:	115500        	slli	a5, a5, 16
40214f9b:	0bcd      	mov.n	a12, a11
40214f9d:	41e470        	srli	a14, a7, 4
40214fa0:	11ccf0        	slli	a12, a12, 1
40214fa3:	05b757        	bgeu	a7, a5, 40214fac <i2s_rcpdm_fill+0x54>
40214fa6:	807780        	add	a7, a7, a8
40214fa9:	01ccc2        	addi	a12, a12, 1
40214fac:	c077e0        	sub	a7, a7, a14
40214faf:	41e470        	srli	a14, a7, 4
40214fb2:	11ccf0        	slli	a12, a12, 1
40214fb5:	03b757        	bgeu	a7, a5, 40214fbc <i2s_rcpdm_fill+0x64>
40214fb8:	778a      	add.n	a7, a7, a8
40214fba:	cc1b      	addi.n	a12, a12, 1
40214fbc:	c077e0        	sub	a7, a7, a14
40214fbf:	41e470        	srli	a14, a7, 4
40214fc2:	11ccf0        	slli	a12, a12, 1
40214fc5:	03b757        	bgeu	a7, a5, 40214fcc <i2s_rcpdm_fill+0x74>
40214fc8:	778a      	add.n	a7, a7, a8
40214fca:	cc1b      	addi.n	a12, a12, 1
40214fcc:	c077e0        	sub	a7, a7, a14
40214fcf:	41e470        	srli	a14, a7, 4
40214fd2:	11ccf0        	slli	a12, a12, 1
40214fd5:	03b757        	bgeu	a7, a5, 40214fdc <i2s_rcpdm_fill+0x84>
40214fd8:	778a      	add.n	a7, a7, a8
40214fda:	cc1b      	addi.n	a12, a12, 1
40214fdc:	c077e0        	sub	a7, a7, a14
40214fdf:	dd0b      	addi.n	a13, a13, -1
40214fe1:	fb8d56        	bnez	a13, 40214f9d <i2s_rcpdm_fill+0x45>
40214fe4:	02c9      	s32i.n	a12, a2, 0
40214fe6:	334b      	addi.n	a3, a3, 4
40214fe8:	224b      	addi.n	a2, a2, 4
40214fea:	969437        	bne	a4, a3, 40214f84 <i2s_rcpdm_fill+0x2c>
40214fed:	001a46        	j	4021505a <i2s_rcpdm_fill+0x102>
40214ff0:	44f000        	extui	a15, a0, 0, 5
40214ff3:	299111        	l32r	a1, 401df638 <_iram_bss_end+0xdad48>
40214ff6:	81ed      	excw
40214ff8:	ed29      	s32i.n	a2, a13, 56
40214ffa:	434a      	add.n	a4, a3, a4
40214ffc:	0c0c      	movi.n	a12, 0
40214ffe:	8b0c      	movi.n	a11, 8
40215000:	009352        	l16si	a5, a3, 0
40215003:	0cad      	mov.n	a10, a12
40215005:	559a      	add.n	a5, a5, a9
40215007:	115500        	slli	a5, a5, 16
4021500a:	0bdd      	mov.n	a13, a11
4021500c:	41e470        	srli	a14, a7, 4
4021500f:	11aaf0        	slli	a10, a10, 1
40215012:	03b757        	bgeu	a7, a5, 40215019 <i2s_rcpdm_fill+0xc1>
40215015:	778a      	add.n	a7, a7, a8
40215017:	aa1b      	addi.n	a10, a10, 1
40215019:	c077e0        	sub	a7, a7, a14
4021501c:	41e470        	srli	a14, a7, 4
4021501f:	11aaf0        	slli	a10, a10, 1
40215022:	03b757        	bgeu	a7, a5, 40215029 <i2s_rcpdm_fill+0xd1>
40215025:	778a      	add.n	a7, a7, a8
40215027:	aa1b      	addi.n	a10, a10, 1
40215029:	c077e0        	sub	a7, a7, a14
4021502c:	41e470        	srli	a14, a7, 4
4021502f:	11aaf0        	slli	a10, a10, 1
40215032:	03b757        	bgeu	a7, a5, 40215039 <i2s_rcpdm_fill+0xe1>
40215035:	778a      	add.n	a7, a7, a8
40215037:	aa1b      	addi.n	a10, a10, 1
40215039:	c077e0        	sub	a7, a7, a14
4021503c:	41e470        	srli	a14, a7, 4
4021503f:	11aaf0        	slli	a10, a10, 1
40215042:	03b757        	bgeu	a7, a5, 40215049 <i2s_rcpdm_fill+0xf1>
40215045:	778a      	add.n	a7, a7, a8
40215047:	aa1b      	addi.n	a10, a10, 1
40215049:	c077e0        	sub	a7, a7, a14
4021504c:	dd0b      	addi.n	a13, a13, -1
4021504e:	fbad56        	bnez	a13, 4021500c <i2s_rcpdm_fill+0xb4>
40215051:	02a9      	s32i.n	a10, a2, 0
40215053:	332b      	addi.n	a3, a3, 2
40215055:	224b      	addi.n	a2, a2, 4
40215057:	a59437        	bne	a4, a3, 40215000 <i2s_rcpdm_fill+0xa8>
4021505a:	31c8      	l32i.n	a12, a1, 12
4021505c:	21d8      	l32i.n	a13, a1, 8
4021505e:	11e8      	l32i.n	a14, a1, 4
40215060:	0679      	s32i.n	a7, a6, 0
40215062:	10c112        	addi	a1, a1, 16
40215065:	f00d      	ret.n
	...
