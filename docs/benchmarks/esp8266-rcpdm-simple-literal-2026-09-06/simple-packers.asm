40214f3c <i2s_pdm_pack32>:
40214f3c:	ed57a1        	l32r	a10, 40210498 <_stext+0x488>
40214f3f:	ed5561        	l32r	a6, 40210494 <_stext+0x484>
40214f42:	0a38      	l32i.n	a3, a10, 0
40214f44:	626a      	add.n	a6, a2, a6
40214f46:	116600        	slli	a6, a6, 16
40214f49:	052c      	movi.n	a5, 32
40214f4b:	020c      	movi.n	a2, 0
40214f4d:	f87c      	movi.n	a8, -1
40214f4f:	190c      	movi.n	a9, 1
40214f51:	304830        	xor	a4, a8, a3
40214f54:	414440        	srli	a4, a4, 4
40214f57:	417430        	srli	a7, a3, 4
40214f5a:	1122f0        	slli	a2, a2, 1
40214f5d:	07b367        	bgeu	a3, a6, 40214f68 <i2s_pdm_pack32+0x2c>
40214f60:	334a      	add.n	a3, a3, a4
40214f62:	202290        	or	a2, a2, a9
40214f65:	000086        	j	40214f6b <i2s_pdm_pack32+0x2f>
40214f68:	c03370        	sub	a3, a3, a7
40214f6b:	550b      	addi.n	a5, a5, -1
40214f6d:	fe0556        	bnez	a5, 40214f51 <i2s_pdm_pack32+0x15>
40214f70:	0a39      	s32i.n	a3, a10, 0
40214f72:	f00d      	ret.n


40214f74 <i2s_rcpdm_fill>:
40214f74:	f0c112        	addi	a1, a1, -16
40214f77:	ed4871        	l32r	a7, 40210498 <_stext+0x488>
40214f7a:	31c9      	s32i.n	a12, a1, 12
40214f7c:	21d9      	s32i.n	a13, a1, 8
40214f7e:	11e9      	s32i.n	a14, a1, 4
40214f80:	0768      	l32i.n	a6, a7, 0
40214f82:	072526        	beqi	a5, 2, 40214f8d <i2s_rcpdm_fill+0x19>
40214f85:	057456        	bnez	a4, 40214fe0 <i2s_rcpdm_fill+0x6c>
40214f88:	002506        	j	40215020 <i2s_rcpdm_fill+0xac>
40214f8b:	160000        	excw
40214f8e:	e008f4        	excw
40214f91:	911144        	excw
40214f94:	4aed40        	excw
40214f97:	fb7c43        	excw
40214f9a:	1a0c      	movi.n	a10, 1
40214f9c:	019352        	l16si	a5, a3, 2
40214f9f:	0093c2        	l16si	a12, a3, 0
40214fa2:	082c      	movi.n	a8, 32
40214fa4:	c5ca      	add.n	a12, a5, a12
40214fa6:	055fc0        	extui	a5, a12, 31, 1
40214fa9:	55ca      	add.n	a5, a5, a12
40214fab:	215150        	srai	a5, a5, 1
40214fae:	559a      	add.n	a5, a5, a9
40214fb0:	115500        	slli	a5, a5, 16
40214fb3:	0c0c      	movi.n	a12, 0
40214fb5:	30db60        	xor	a13, a11, a6
40214fb8:	41e460        	srli	a14, a6, 4
40214fbb:	41d4d0        	srli	a13, a13, 4
40214fbe:	11ccf0        	slli	a12, a12, 1
40214fc1:	053657        	bltu	a6, a5, 40214fca <i2s_rcpdm_fill+0x56>
40214fc4:	c066e0        	sub	a6, a6, a14
40214fc7:	000106        	j	40214fcf <i2s_rcpdm_fill+0x5b>
40214fca:	66da      	add.n	a6, a6, a13
40214fcc:	20cca0        	or	a12, a12, a10
40214fcf:	880b      	addi.n	a8, a8, -1
40214fd1:	fe0856        	bnez	a8, 40214fb5 <i2s_rcpdm_fill+0x41>
40214fd4:	02c9      	s32i.n	a12, a2, 0
40214fd6:	334b      	addi.n	a3, a3, 4
40214fd8:	224b      	addi.n	a2, a2, 4
40214fda:	be9437        	bne	a4, a3, 40214f9c <i2s_rcpdm_fill+0x28>
40214fdd:	000fc6        	j	40215020 <i2s_rcpdm_fill+0xac>
40214fe0:	1144f0        	slli	a4, a4, 1
40214fe3:	ed2c91        	l32r	a9, 40210494 <_stext+0x484>
40214fe6:	434a      	add.n	a4, a3, a4
40214fe8:	fe7c      	movi.n	a14, -1
40214fea:	1d0c      	movi.n	a13, 1
40214fec:	009382        	l16si	a8, a3, 0
40214fef:	0b2c      	movi.n	a11, 32
40214ff1:	889a      	add.n	a8, a8, a9
40214ff3:	118800        	slli	a8, a8, 16
40214ff6:	050c      	movi.n	a5, 0
40214ff8:	30ae60        	xor	a10, a14, a6
40214ffb:	41c460        	srli	a12, a6, 4
40214ffe:	41a4a0        	srli	a10, a10, 4
40215001:	1155f0        	slli	a5, a5, 1
40215004:	053687        	bltu	a6, a8, 4021500d <i2s_rcpdm_fill+0x99>
40215007:	c066c0        	sub	a6, a6, a12
4021500a:	000106        	j	40215012 <i2s_rcpdm_fill+0x9e>
4021500d:	66aa      	add.n	a6, a6, a10
4021500f:	2055d0        	or	a5, a5, a13
40215012:	bb0b      	addi.n	a11, a11, -1
40215014:	fe0b56        	bnez	a11, 40214ff8 <i2s_rcpdm_fill+0x84>
40215017:	0259      	s32i.n	a5, a2, 0
40215019:	332b      	addi.n	a3, a3, 2
4021501b:	224b      	addi.n	a2, a2, 4
4021501d:	cb9347        	bne	a3, a4, 40214fec <i2s_rcpdm_fill+0x78>
40215020:	31c8      	l32i.n	a12, a1, 12
40215022:	21d8      	l32i.n	a13, a1, 8
40215024:	11e8      	l32i.n	a14, a1, 4
40215026:	0769      	s32i.n	a6, a7, 0
40215028:	10c112        	addi	a1, a1, 16
4021502b:	f00d      	ret.n
4021502d:	000000        	ill
