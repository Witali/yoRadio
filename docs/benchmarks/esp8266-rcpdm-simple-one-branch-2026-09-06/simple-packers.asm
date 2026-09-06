40214f40 <i2s_pdm_pack32>:
40214f40:	ed5691        	l32r	a9, 40210498 <_stext+0x488>
40214f43:	ed5461        	l32r	a6, 40210494 <_stext+0x484>
40214f46:	0938      	l32i.n	a3, a9, 0
40214f48:	626a      	add.n	a6, a2, a6
40214f4a:	ed5481        	l32r	a8, 4021049c <_stext+0x48c>
40214f4d:	116600        	slli	a6, a6, 16
40214f50:	052c      	movi.n	a5, 32
40214f52:	00a022        	movi	a2, 0
40214f55:	01a072        	movi	a7, 1
40214f58:	414430        	srli	a4, a3, 4
40214f5b:	c04340        	sub	a4, a3, a4
40214f5e:	1122f0        	slli	a2, a2, 1
40214f61:	07b367        	bgeu	a3, a6, 40214f6c <i2s_pdm_pack32+0x2c>
40214f64:	348a      	add.n	a3, a4, a8
40214f66:	202270        	or	a2, a2, a7
40214f69:	000046        	j	40214f6e <i2s_pdm_pack32+0x2e>
40214f6c:	043d      	mov.n	a3, a4
40214f6e:	550b      	addi.n	a5, a5, -1
40214f70:	fe4556        	bnez	a5, 40214f58 <i2s_pdm_pack32+0x18>
40214f73:	0939      	s32i.n	a3, a9, 0
40214f75:	f00d      	ret.n
	...


40214f78 <i2s_rcpdm_fill>:
40214f78:	f0c112        	addi	a1, a1, -16
40214f7b:	ed4771        	l32r	a7, 40210498 <_stext+0x488>
40214f7e:	31c9      	s32i.n	a12, a1, 12
40214f80:	21d9      	s32i.n	a13, a1, 8
40214f82:	11e9      	s32i.n	a14, a1, 4
40214f84:	0768      	l32i.n	a6, a7, 0
40214f86:	072526        	beqi	a5, 2, 40214f91 <i2s_rcpdm_fill+0x19>
40214f89:	054456        	bnez	a4, 40214fe1 <i2s_rcpdm_fill+0x69>
40214f8c:	002486        	j	40215022 <i2s_rcpdm_fill+0xaa>
40214f8f:	160000        	excw
40214f92:	e008d4        	excw
40214f95:	911144        	excw
40214f98:	3f          	.byte 0x3f
40214f99:	b1ed      	excw
40214f9b:	4aed40        	excw
40214f9e:	1a0c43        	excw
40214fa1:	019352        	l16si	a5, a3, 2
40214fa4:	0093c2        	l16si	a12, a3, 0
40214fa7:	068d      	mov.n	a8, a6
40214fa9:	c5ca      	add.n	a12, a5, a12
40214fab:	055fc0        	extui	a5, a12, 31, 1
40214fae:	55ca      	add.n	a5, a5, a12
40214fb0:	215150        	srai	a5, a5, 1
40214fb3:	559a      	add.n	a5, a5, a9
40214fb5:	115500        	slli	a5, a5, 16
40214fb8:	0d2c      	movi.n	a13, 32
40214fba:	00a0c2        	movi	a12, 0
40214fbd:	41e460        	srli	a14, a6, 4
40214fc0:	dd0b      	addi.n	a13, a13, -1
40214fc2:	c066e0        	sub	a6, a6, a14
40214fc5:	11ccf0        	slli	a12, a12, 1
40214fc8:	04b857        	bgeu	a8, a5, 40214fd0 <i2s_rcpdm_fill+0x58>
40214fcb:	66ba      	add.n	a6, a6, a11
40214fcd:	20cca0        	or	a12, a12, a10
40214fd0:	068d      	mov.n	a8, a6
40214fd2:	fe7d56        	bnez	a13, 40214fbd <i2s_rcpdm_fill+0x45>
40214fd5:	02c9      	s32i.n	a12, a2, 0
40214fd7:	334b      	addi.n	a3, a3, 4
40214fd9:	224b      	addi.n	a2, a2, 4
40214fdb:	c29437        	bne	a4, a3, 40214fa1 <i2s_rcpdm_fill+0x29>
40214fde:	001006        	j	40215022 <i2s_rcpdm_fill+0xaa>
40214fe1:	1144f0        	slli	a4, a4, 1
40214fe4:	ed2c91        	l32r	a9, 40210494 <_stext+0x484>
40214fe7:	ed2db1        	l32r	a11, 4021049c <_stext+0x48c>
40214fea:	804340        	add	a4, a3, a4
40214fed:	01a0d2        	movi	a13, 1
40214ff0:	009382        	l16si	a8, a3, 0
40214ff3:	06cd      	mov.n	a12, a6
40214ff5:	808890        	add	a8, a8, a9
40214ff8:	118800        	slli	a8, a8, 16
40214ffb:	20a0a2        	movi	a10, 32
40214ffe:	00a052        	movi	a5, 0
40215001:	41e460        	srli	a14, a6, 4
40215004:	aa0b      	addi.n	a10, a10, -1
40215006:	c066e0        	sub	a6, a6, a14
40215009:	1155f0        	slli	a5, a5, 1
4021500c:	04bc87        	bgeu	a12, a8, 40215014 <i2s_rcpdm_fill+0x9c>
4021500f:	66ba      	add.n	a6, a6, a11
40215011:	2055d0        	or	a5, a5, a13
40215014:	06cd      	mov.n	a12, a6
40215016:	fe7a56        	bnez	a10, 40215001 <i2s_rcpdm_fill+0x89>
40215019:	0259      	s32i.n	a5, a2, 0
4021501b:	332b      	addi.n	a3, a3, 2
4021501d:	224b      	addi.n	a2, a2, 4
4021501f:	cd9347        	bne	a3, a4, 40214ff0 <i2s_rcpdm_fill+0x78>
40215022:	31c8      	l32i.n	a12, a1, 12
40215024:	21d8      	l32i.n	a13, a1, 8
40215026:	11e8      	l32i.n	a14, a1, 4
40215028:	0769      	s32i.n	a6, a7, 0
4021502a:	10c112        	addi	a1, a1, 16
4021502d:	f00d      	ret.n
	...
