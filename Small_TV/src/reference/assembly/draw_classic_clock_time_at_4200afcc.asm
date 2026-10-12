
factory-irom.bin:     file format binary


Disassembly of section .data:

4200afcc <.data+0xafac>:
4200afcc:	1141                	addi	sp,sp,-16
4200afce:	c606                	sw	ra,12(sp)
4200afd0:	c422                	sw	s0,8(sp)
4200afd2:	c226                	sw	s1,4(sp)
4200afd4:	3fcbb7b7          	lui	a5,0x3fcbb
4200afd8:	9a878793          	addi	a5,a5,-1624 # 0x3fcba9a8
4200afdc:	0007a023          	sw	zero,0(a5)
4200afe0:	0007a223          	sw	zero,4(a5)
4200afe4:	0007a423          	sw	zero,8(a5)
4200afe8:	00079623          	sh	zero,12(a5)
4200afec:	00078723          	sb	zero,14(a5)
4200aff0:	3fcc07b7          	lui	a5,0x3fcc0
4200aff4:	fc878793          	addi	a5,a5,-56 # 0x3fcbffc8
4200aff8:	0067c703          	lbu	a4,6(a5)
4200affc:	3fcb87b7          	lui	a5,0x3fcb8
4200b000:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200b004:	1707a683          	lw	a3,368(a5)
4200b008:	4785                	li	a5,1
4200b00a:	18f68a63          	beq	a3,a5,0x4200b19e
4200b00e:	ccccd7b7          	lui	a5,0xccccd
4200b012:	ccd78793          	addi	a5,a5,-819 # 0xcccccccd
4200b016:	02f737b3          	mulhu	a5,a4,a5
4200b01a:	838d                	srli	a5,a5,0x3
4200b01c:	03078693          	addi	a3,a5,48
4200b020:	3fcbb637          	lui	a2,0x3fcbb
4200b024:	9a860413          	addi	s0,a2,-1624 # 0x3fcba9a8
4200b028:	00d40023          	sb	a3,0(s0)
4200b02c:	00279693          	slli	a3,a5,0x2
4200b030:	97b6                	add	a5,a5,a3
4200b032:	00179693          	slli	a3,a5,0x1
4200b036:	8f15                	sub	a4,a4,a3
4200b038:	03070713          	addi	a4,a4,48
4200b03c:	00e400a3          	sb	a4,1(s0)
4200b040:	3fcb8737          	lui	a4,0x3fcb8
4200b044:	4781                	li	a5,0
4200b046:	b9c70713          	addi	a4,a4,-1124 # 0x3fcb7b9c
4200b04a:	18475703          	lhu	a4,388(a4)
4200b04e:	04000693          	li	a3,64
4200b052:	9a860613          	addi	a2,a2,-1624
4200b056:	05000593          	li	a1,80
4200b05a:	4501                	li	a0,0
4200b05c:	b93ff0ef          	jal	0x4200abee
4200b060:	00042023          	sw	zero,0(s0)
4200b064:	00042223          	sw	zero,4(s0)
4200b068:	00042423          	sw	zero,8(s0)
4200b06c:	00041623          	sh	zero,12(s0)
4200b070:	00040723          	sb	zero,14(s0)
4200b074:	3fcc07b7          	lui	a5,0x3fcc0
4200b078:	fc878793          	addi	a5,a5,-56 # 0x3fcbffc8
4200b07c:	0087c783          	lbu	a5,8(a5)
4200b080:	8b85                	andi	a5,a5,1
4200b082:	12079563          	bnez	a5,0x4200b1ac
4200b086:	3fcbb637          	lui	a2,0x3fcbb
4200b08a:	03a00793          	li	a5,58
4200b08e:	9af60423          	sb	a5,-1624(a2) # 0x3fcba9a8
4200b092:	4781                	li	a5,0
4200b094:	6741                	lui	a4,0x10
4200b096:	177d                	addi	a4,a4,-1 # 0xffff
4200b098:	04000693          	li	a3,64
4200b09c:	9a860613          	addi	a2,a2,-1624
4200b0a0:	05000593          	li	a1,80
4200b0a4:	8536                	mv	a0,a3
4200b0a6:	b49ff0ef          	jal	0x4200abee
4200b0aa:	3fcc07b7          	lui	a5,0x3fcc0
4200b0ae:	fc878793          	addi	a5,a5,-56 # 0x3fcbffc8
4200b0b2:	0077c703          	lbu	a4,7(a5)
4200b0b6:	3fcc47b7          	lui	a5,0x3fcc4
4200b0ba:	a287c783          	lbu	a5,-1496(a5) # 0x3fcc3a28
4200b0be:	00f71863          	bne	a4,a5,0x4200b0ce
4200b0c2:	3fcc47b7          	lui	a5,0x3fcc4
4200b0c6:	a267c783          	lbu	a5,-1498(a5) # 0x3fcc3a26
4200b0ca:	18078963          	beqz	a5,0x4200b25c
4200b0ce:	4485                	li	s1,1
4200b0d0:	3fcc47b7          	lui	a5,0x3fcc4
4200b0d4:	9e978aa3          	sb	s1,-1547(a5) # 0x3fcc39f5
4200b0d8:	3fcc47b7          	lui	a5,0x3fcc4
4200b0dc:	a2078323          	sb	zero,-1498(a5) # 0x3fcc3a26
4200b0e0:	3fcbb637          	lui	a2,0x3fcbb
4200b0e4:	9a860413          	addi	s0,a2,-1624 # 0x3fcba9a8
4200b0e8:	00042023          	sw	zero,0(s0)
4200b0ec:	00042223          	sw	zero,4(s0)
4200b0f0:	00042423          	sw	zero,8(s0)
4200b0f4:	00041623          	sh	zero,12(s0)
4200b0f8:	00040723          	sb	zero,14(s0)
4200b0fc:	ccccd7b7          	lui	a5,0xccccd
4200b100:	ccd78793          	addi	a5,a5,-819 # 0xcccccccd
4200b104:	02f737b3          	mulhu	a5,a4,a5
4200b108:	838d                	srli	a5,a5,0x3
4200b10a:	03078693          	addi	a3,a5,48
4200b10e:	00d40023          	sb	a3,0(s0)
4200b112:	00279693          	slli	a3,a5,0x2
4200b116:	97b6                	add	a5,a5,a3
4200b118:	00179693          	slli	a3,a5,0x1
4200b11c:	8f15                	sub	a4,a4,a3
4200b11e:	03070713          	addi	a4,a4,48
4200b122:	00e400a3          	sb	a4,1(s0)
4200b126:	3fcb8737          	lui	a4,0x3fcb8
4200b12a:	4781                	li	a5,0
4200b12c:	b9c70713          	addi	a4,a4,-1124 # 0x3fcb7b9c
4200b130:	18875703          	lhu	a4,392(a4)
4200b134:	04000693          	li	a3,64
4200b138:	9a860613          	addi	a2,a2,-1624
4200b13c:	05000593          	li	a1,80
4200b140:	06000513          	li	a0,96
4200b144:	aabff0ef          	jal	0x4200abee
4200b148:	00042023          	sw	zero,0(s0)
4200b14c:	00042223          	sw	zero,4(s0)
4200b150:	00042423          	sw	zero,8(s0)
4200b154:	00041623          	sh	zero,12(s0)
4200b158:	00040723          	sb	zero,14(s0)
4200b15c:	3fcc07b7          	lui	a5,0x3fcc0
4200b160:	fc878793          	addi	a5,a5,-56 # 0x3fcbffc8
4200b164:	0097c783          	lbu	a5,9(a5)
4200b168:	06978463          	beq	a5,s1,0x4200b1d0
4200b16c:	4709                	li	a4,2
4200b16e:	0ee78c63          	beq	a5,a4,0x4200b266
4200b172:	470d                	li	a4,3
4200b174:	10e78263          	beq	a5,a4,0x4200b278
4200b178:	4711                	li	a4,4
4200b17a:	10e78863          	beq	a5,a4,0x4200b28a
4200b17e:	4715                	li	a4,5
4200b180:	10e78e63          	beq	a5,a4,0x4200b29c
4200b184:	4719                	li	a4,6
4200b186:	12e78463          	beq	a5,a4,0x4200b2ae
4200b18a:	ebb9                	bnez	a5,0x4200b1e0
4200b18c:	3fcbb737          	lui	a4,0x3fcbb
4200b190:	006e77b7          	lui	a5,0x6e7
4200b194:	55378793          	addi	a5,a5,1363 # 0x6e7553
4200b198:	9af72423          	sw	a5,-1624(a4) # 0x3fcba9a8
4200b19c:	a091                	j	0x4200b1e0
4200b19e:	47b1                	li	a5,12
4200b1a0:	e6e7f7e3          	bgeu	a5,a4,0x4200b00e
4200b1a4:	1751                	addi	a4,a4,-12
4200b1a6:	0ff77713          	zext.b	a4,a4
4200b1aa:	b595                	j	0x4200b00e
4200b1ac:	3fcbb637          	lui	a2,0x3fcbb
4200b1b0:	02000793          	li	a5,32
4200b1b4:	9af60423          	sb	a5,-1624(a2) # 0x3fcba9a8
4200b1b8:	4781                	li	a5,0
4200b1ba:	4701                	li	a4,0
4200b1bc:	04000693          	li	a3,64
4200b1c0:	9a860613          	addi	a2,a2,-1624
4200b1c4:	05000593          	li	a1,80
4200b1c8:	8536                	mv	a0,a3
4200b1ca:	a25ff0ef          	jal	0x4200abee
4200b1ce:	bdf1                	j	0x4200b0aa
4200b1d0:	3fcbb737          	lui	a4,0x3fcbb
4200b1d4:	006e77b7          	lui	a5,0x6e7
4200b1d8:	f4d78793          	addi	a5,a5,-179 # 0x6e6f4d
4200b1dc:	9af72423          	sw	a5,-1624(a4) # 0x3fcba9a8
4200b1e0:	3fcb84b7          	lui	s1,0x3fcb8
4200b1e4:	b9c48493          	addi	s1,s1,-1124 # 0x3fcb7b9c
4200b1e8:	4781                	li	a5,0
4200b1ea:	18c4d703          	lhu	a4,396(s1)
4200b1ee:	02000693          	li	a3,32
4200b1f2:	3fcbb437          	lui	s0,0x3fcbb
4200b1f6:	9a840613          	addi	a2,s0,-1624 # 0x3fcba9a8
4200b1fa:	06e00593          	li	a1,110
4200b1fe:	0b000513          	li	a0,176
4200b202:	9edff0ef          	jal	0x4200abee
4200b206:	9a840793          	addi	a5,s0,-1624
4200b20a:	0007a023          	sw	zero,0(a5)
4200b20e:	0007a223          	sw	zero,4(a5)
4200b212:	0007a423          	sw	zero,8(a5)
4200b216:	00079623          	sh	zero,12(a5)
4200b21a:	00078723          	sb	zero,14(a5)
4200b21e:	4701                	li	a4,0
4200b220:	46e1                	li	a3,24
4200b222:	07800613          	li	a2,120
4200b226:	09600593          	li	a1,150
4200b22a:	4501                	li	a0,0
4200b22c:	f0afe0ef          	jal	0x42009936
4200b230:	17c4a783          	lw	a5,380(s1)
4200b234:	c7d1                	beqz	a5,0x4200b2c0
4200b236:	4705                	li	a4,1
4200b238:	0ae78863          	beq	a5,a4,0x4200b2e8
4200b23c:	4709                	li	a4,2
4200b23e:	0ce78b63          	beq	a5,a4,0x4200b314
4200b242:	4781                	li	a5,0
4200b244:	6741                	lui	a4,0x10
4200b246:	177d                	addi	a4,a4,-1 # 0xffff
4200b248:	46e1                	li	a3,24
4200b24a:	3fcbb637          	lui	a2,0x3fcbb
4200b24e:	9a860613          	addi	a2,a2,-1624 # 0x3fcba9a8
4200b252:	09600593          	li	a1,150
4200b256:	4501                	li	a0,0
4200b258:	997ff0ef          	jal	0x4200abee
4200b25c:	40b2                	lw	ra,12(sp)
4200b25e:	4422                	lw	s0,8(sp)
4200b260:	4492                	lw	s1,4(sp)
4200b262:	0141                	addi	sp,sp,16
4200b264:	8082                	ret
4200b266:	3fcbb737          	lui	a4,0x3fcbb
4200b26a:	006577b7          	lui	a5,0x657
4200b26e:	55478793          	addi	a5,a5,1364 # 0x657554
4200b272:	9af72423          	sw	a5,-1624(a4) # 0x3fcba9a8
4200b276:	b7ad                	j	0x4200b1e0
4200b278:	3fcbb737          	lui	a4,0x3fcbb
4200b27c:	006467b7          	lui	a5,0x646
4200b280:	55778793          	addi	a5,a5,1367 # 0x646557
4200b284:	9af72423          	sw	a5,-1624(a4) # 0x3fcba9a8
4200b288:	bfa1                	j	0x4200b1e0
4200b28a:	3fcbb737          	lui	a4,0x3fcbb
4200b28e:	007577b7          	lui	a5,0x757
4200b292:	85478793          	addi	a5,a5,-1964 # 0x756854
4200b296:	9af72423          	sw	a5,-1624(a4) # 0x3fcba9a8
4200b29a:	b799                	j	0x4200b1e0
4200b29c:	3fcbb737          	lui	a4,0x3fcbb
4200b2a0:	006977b7          	lui	a5,0x697
4200b2a4:	24678793          	addi	a5,a5,582 # 0x697246
4200b2a8:	9af72423          	sw	a5,-1624(a4) # 0x3fcba9a8
4200b2ac:	bf15                	j	0x4200b1e0
4200b2ae:	3fcbb737          	lui	a4,0x3fcbb
4200b2b2:	007467b7          	lui	a5,0x746
4200b2b6:	15378793          	addi	a5,a5,339 # 0x746153
4200b2ba:	9af72423          	sw	a5,-1624(a4) # 0x3fcba9a8
4200b2be:	b70d                	j	0x4200b1e0
4200b2c0:	3fcc07b7          	lui	a5,0x3fcc0
4200b2c4:	fc878793          	addi	a5,a5,-56 # 0x3fcbffc8
4200b2c8:	4398                	lw	a4,0(a5)
4200b2ca:	0057c683          	lbu	a3,5(a5)
4200b2ce:	0047c603          	lbu	a2,4(a5)
4200b2d2:	3c0c35b7          	lui	a1,0x3c0c3
4200b2d6:	b3458593          	addi	a1,a1,-1228 # 0x3c0c2b34
4200b2da:	9a840513          	addi	a0,s0,-1624
4200b2de:	fdff5097          	auipc	ra,0xfdff5
4200b2e2:	3ca080e7          	jalr	970(ra) # 0x400006a8
4200b2e6:	bfb1                	j	0x4200b242
4200b2e8:	3fcc07b7          	lui	a5,0x3fcc0
4200b2ec:	fc878793          	addi	a5,a5,-56 # 0x3fcbffc8
4200b2f0:	4398                	lw	a4,0(a5)
4200b2f2:	0047c683          	lbu	a3,4(a5)
4200b2f6:	0057c603          	lbu	a2,5(a5)
4200b2fa:	3c0c35b7          	lui	a1,0x3c0c3
4200b2fe:	b3458593          	addi	a1,a1,-1228 # 0x3c0c2b34
4200b302:	3fcbb537          	lui	a0,0x3fcbb
4200b306:	9a850513          	addi	a0,a0,-1624 # 0x3fcba9a8
4200b30a:	fdff5097          	auipc	ra,0xfdff5
4200b30e:	39e080e7          	jalr	926(ra) # 0x400006a8
4200b312:	bf05                	j	0x4200b242
4200b314:	3fcc07b7          	lui	a5,0x3fcc0
4200b318:	fc878793          	addi	a5,a5,-56 # 0x3fcbffc8
4200b31c:	0057c703          	lbu	a4,5(a5)
4200b320:	0047c683          	lbu	a3,4(a5)
4200b324:	4390                	lw	a2,0(a5)
4200b326:	3c0c35b7          	lui	a1,0x3c0c3
4200b32a:	b3458593          	addi	a1,a1,-1228 # 0x3c0c2b34
4200b32e:	3fcbb537          	lui	a0,0x3fcbb
4200b332:	9a850513          	addi	a0,a0,-1624 # 0x3fcba9a8
4200b336:	fdff5097          	auipc	ra,0xfdff5
4200b33a:	372080e7          	jalr	882(ra) # 0x400006a8
4200b33e:	b711                	j	0x4200b242
