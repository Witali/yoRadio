40214f48 <i2s_pdm_pack32>:
40214f48:	ed5361        	l32r	a6, 40210494 <_stext+0x484>
40214f4b:	ed5331        	l32r	a3, 40210498 <_stext+0x488>
40214f4e:	626a      	add.n	a6, a2, a6
40214f50:	116600        	slli	a6, a6, 16
40214f53:	02b637        	bgeu	a6, a3, 40214f59 <i2s_pdm_pack32+0x11>
40214f56:	206330        	or	a6, a3, a3
40214f59:	ed5191        	l32r	a9, 402104a0 <_stext+0x490>
40214f5c:	ed5021        	l32r	a2, 4021049c <_stext+0x48c>
40214f5f:	0938      	l32i.n	a3, a9, 0
40214f61:	ed5081        	l32r	a8, 402104a4 <_stext+0x494>
40214f64:	662a      	add.n	a6, a6, a2
40214f66:	042c      	movi.n	a4, 32
40214f68:	020c      	movi.n	a2, 0
40214f6a:	01a072        	movi	a7, 1
40214f6d:	415430        	srli	a5, a3, 4
40214f70:	c03350        	sub	a3, a3, a5
40214f73:	440b      	addi.n	a4, a4, -1
40214f75:	1122f0        	slli	a2, a2, 1
40214f78:	04b367        	bgeu	a3, a6, 40214f80 <i2s_pdm_pack32+0x38>
40214f7b:	338a      	add.n	a3, a3, a8
40214f7d:	202270        	or	a2, a2, a7
40214f80:	fe9456        	bnez	a4, 40214f6d <i2s_pdm_pack32+0x25>
40214f83:	0939      	s32i.n	a3, a9, 0
40214f85:	f00d      	ret.n
	...


40214f88 <i2s_rcpdm_fill>:
40214f88:	f0c112        	addi	a1, a1, -16
40214f8b:	ed4581        	l32r	a8, 402104a0 <_stext+0x490>
40214f8e:	31c9      	s32i.n	a12, a1, 12
40214f90:	21d9      	s32i.n	a13, a1, 8
40214f92:	11e9      	s32i.n	a14, a1, 4
40214f94:	01f9      	s32i.n	a15, a1, 0
40214f96:	0868      	l32i.n	a6, a8, 0
40214f98:	052526        	beqi	a5, 2, 40214fa1 <i2s_rcpdm_fill+0x19>
40214f9b:	05e456        	bnez	a4, 40214ffd <i2s_rcpdm_fill+0x75>
40214f9e:	002886        	j	40215044 <i2s_rcpdm_fill+0xbc>
40214fa1:	09f416        	beqz	a4, 40215044 <i2s_rcpdm_fill+0xbc>
40214fa4:	1144e0        	slli	a4, a4, 2
40214fa7:	ed3ba1        	l32r	a10, 40210494 <_stext+0x484>
40214faa:	ed3b71        	l32r	a7, 40210498 <_stext+0x488>
40214fad:	ed3b91        	l32r	a9, 4021049c <_stext+0x48c>
40214fb0:	ed3dc1        	l32r	a12, 402104a4 <_stext+0x494>
40214fb3:	804340        	add	a4, a3, a4
40214fb6:	1b0c      	movi.n	a11, 1
40214fb8:	019352        	l16si	a5, a3, 2
40214fbb:	0093d2        	l16si	a13, a3, 0
40214fbe:	d5da      	add.n	a13, a5, a13
40214fc0:	055fd0        	extui	a5, a13, 31, 1
40214fc3:	55da      	add.n	a5, a5, a13
40214fc5:	215150        	srai	a5, a5, 1
40214fc8:	55aa      	add.n	a5, a5, a10
40214fca:	115500        	slli	a5, a5, 16
40214fcd:	01b577        	bgeu	a5, a7, 40214fd2 <i2s_rcpdm_fill+0x4a>
40214fd0:	075d      	mov.n	a5, a7
40214fd2:	559a      	add.n	a5, a5, a9
40214fd4:	0e2c      	movi.n	a14, 32
40214fd6:	00a0d2        	movi	a13, 0
40214fd9:	41f460        	srli	a15, a6, 4
40214fdc:	c066f0        	sub	a6, a6, a15
40214fdf:	ee0b      	addi.n	a14, a14, -1
40214fe1:	11ddf0        	slli	a13, a13, 1
40214fe4:	04b657        	bgeu	a6, a5, 40214fec <i2s_rcpdm_fill+0x64>
40214fe7:	66ca      	add.n	a6, a6, a12
40214fe9:	20ddb0        	or	a13, a13, a11
40214fec:	fe9e56        	bnez	a14, 40214fd9 <i2s_rcpdm_fill+0x51>
40214fef:	02d9      	s32i.n	a13, a2, 0
40214ff1:	334b      	addi.n	a3, a3, 4
40214ff3:	224b      	addi.n	a2, a2, 4
40214ff5:	bf9437        	bne	a4, a3, 40214fb8 <i2s_rcpdm_fill+0x30>
40214ff8:	001206        	j	40215044 <i2s_rcpdm_fill+0xbc>
40214ffb:	f00000        	subx8	a0, a0, a0
40214ffe:	a11144        	excw
40215001:	71ed25        	excw
40215004:	91ed25        	excw
40215007:	c1ed25        	excw
4021500a:	4aed26        	beqi	a13, 128, 40215058 <native_audio_output_benchmark_verify+0x4>
4021500d:	a0b243        	excw
40215010:	935201        	l32r	a0, 401f9d58 <_iram_bss_end+0xf5468>
40215013:	55aa00        	extui	a10, a0, 26, 6
40215016:	115500        	slli	a5, a5, 16
40215019:	01b577        	bgeu	a5, a7, 4021501e <i2s_rcpdm_fill+0x96>
4021501c:	075d      	mov.n	a5, a7
4021501e:	559a      	add.n	a5, a5, a9
40215020:	0e2c      	movi.n	a14, 32
40215022:	00a0d2        	movi	a13, 0
40215025:	41f460        	srli	a15, a6, 4
40215028:	c066f0        	sub	a6, a6, a15
4021502b:	ee0b      	addi.n	a14, a14, -1
4021502d:	11ddf0        	slli	a13, a13, 1
40215030:	04b657        	bgeu	a6, a5, 40215038 <i2s_rcpdm_fill+0xb0>
40215033:	66ca      	add.n	a6, a6, a12
40215035:	20ddb0        	or	a13, a13, a11
40215038:	fe9e56        	bnez	a14, 40215025 <i2s_rcpdm_fill+0x9d>
4021503b:	02d9      	s32i.n	a13, a2, 0
4021503d:	332b      	addi.n	a3, a3, 2
4021503f:	224b      	addi.n	a2, a2, 4
40215041:	cc9347        	bne	a3, a4, 40215011 <i2s_rcpdm_fill+0x89>
40215044:	31c8      	l32i.n	a12, a1, 12
40215046:	21d8      	l32i.n	a13, a1, 8
40215048:	11e8      	l32i.n	a14, a1, 4
4021504a:	01f8      	l32i.n	a15, a1, 0
4021504c:	0869      	s32i.n	a6, a8, 0
4021504e:	10c112        	addi	a1, a1, 16
40215051:	f00d      	ret.n
	...
