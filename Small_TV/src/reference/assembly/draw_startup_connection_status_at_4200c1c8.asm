
factory-irom.bin:     file format binary


Disassembly of section .data:

4200c1c8 <.data+0xc1a8>:
4200c1c8:	1141                	addi	sp,sp,-16
4200c1ca:	c606                	sw	ra,12(sp)
4200c1cc:	c422                	sw	s0,8(sp)
4200c1ce:	c226                	sw	s1,4(sp)
4200c1d0:	3fcc47b7          	lui	a5,0x3fcc4
4200c1d4:	a747c703          	lbu	a4,-1420(a5) # 0x3fcc3a74
4200c1d8:	4789                	li	a5,2
4200c1da:	02f70b63          	beq	a4,a5,0x4200c210
4200c1de:	3fcc47b7          	lui	a5,0x3fcc4
4200c1e2:	a567c603          	lbu	a2,-1450(a5) # 0x3fcc3a56
4200c1e6:	3fcc47b7          	lui	a5,0x3fcc4
4200c1ea:	a557c783          	lbu	a5,-1451(a5) # 0x3fcc3a55
4200c1ee:	08f61363          	bne	a2,a5,0x4200c274
4200c1f2:	3fcc47b7          	lui	a5,0x3fcc4
4200c1f6:	a547c703          	lbu	a4,-1452(a5) # 0x3fcc3a54
4200c1fa:	3fcc47b7          	lui	a5,0x3fcc4
4200c1fe:	a537c783          	lbu	a5,-1453(a5) # 0x3fcc3a53
4200c202:	0af71863          	bne	a4,a5,0x4200c2b2
4200c206:	40b2                	lw	ra,12(sp)
4200c208:	4422                	lw	s0,8(sp)
4200c20a:	4492                	lw	s1,4(sp)
4200c20c:	0141                	addi	sp,sp,16
4200c20e:	8082                	ret
4200c210:	3fcc47b7          	lui	a5,0x3fcc4
4200c214:	a527c783          	lbu	a5,-1454(a5) # 0x3fcc3a52
4200c218:	f3f9                	bnez	a5,0x4200c1de
4200c21a:	3fcb87b7          	lui	a5,0x3fcb8
4200c21e:	b847c783          	lbu	a5,-1148(a5) # 0x3fcb7b84
4200c222:	dfd5                	beqz	a5,0x4200c1de
4200c224:	3fcbb437          	lui	s0,0x3fcbb
4200c228:	9dc40793          	addi	a5,s0,-1572 # 0x3fcba9dc
4200c22c:	0007a023          	sw	zero,0(a5)
4200c230:	0007a223          	sw	zero,4(a5)
4200c234:	0007a423          	sw	zero,8(a5)
4200c238:	0007a623          	sw	zero,12(a5)
4200c23c:	0007a823          	sw	zero,16(a5)
4200c240:	0007aa23          	sw	zero,20(a5)
4200c244:	00078c23          	sb	zero,24(a5)
4200c248:	3fcb85b7          	lui	a1,0x3fcb8
4200c24c:	b8458593          	addi	a1,a1,-1148 # 0x3fcb7b84
4200c250:	9dc40513          	addi	a0,s0,-1572
4200c254:	fdff4097          	auipc	ra,0xfdff4
4200c258:	454080e7          	jalr	1108(ra) # 0x400006a8
4200c25c:	4781                	li	a5,0
4200c25e:	6741                	lui	a4,0x10
4200c260:	177d                	addi	a4,a4,-1 # 0xffff
4200c262:	46e1                	li	a3,24
4200c264:	9dc40613          	addi	a2,s0,-1572
4200c268:	07200593          	li	a1,114
4200c26c:	4575                	li	a0,29
4200c26e:	981fe0ef          	jal	0x4200abee
4200c272:	b7b5                	j	0x4200c1de
4200c274:	64c1                	lui	s1,0x10
4200c276:	fff48713          	addi	a4,s1,-1 # 0xffff
4200c27a:	46ad                	li	a3,11
4200c27c:	08e00593          	li	a1,142
4200c280:	4575                	li	a0,29
4200c282:	eb4fd0ef          	jal	0x42009936
4200c286:	3fcc4437          	lui	s0,0x3fcc4
4200c28a:	a5644503          	lbu	a0,-1450(s0) # 0x3fcc3a56
4200c28e:	0575                	addi	a0,a0,29
4200c290:	4701                	li	a4,0
4200c292:	fff48693          	addi	a3,s1,-1
4200c296:	4611                	li	a2,4
4200c298:	08e00593          	li	a1,142
4200c29c:	0542                	slli	a0,a0,0x10
4200c29e:	8141                	srli	a0,a0,0x10
4200c2a0:	a0ffe0ef          	jal	0x4200acae
4200c2a4:	a5644703          	lbu	a4,-1450(s0)
4200c2a8:	3fcc47b7          	lui	a5,0x3fcc4
4200c2ac:	a4e78aa3          	sb	a4,-1451(a5) # 0x3fcc3a55
4200c2b0:	b789                	j	0x4200c1f2
4200c2b2:	4701                	li	a4,0
4200c2b4:	02000693          	li	a3,32
4200c2b8:	0f000613          	li	a2,240
4200c2bc:	0a000593          	li	a1,160
4200c2c0:	4501                	li	a0,0
4200c2c2:	e74fd0ef          	jal	0x42009936
4200c2c6:	3fcbb637          	lui	a2,0x3fcbb
4200c2ca:	9dc60793          	addi	a5,a2,-1572 # 0x3fcba9dc
4200c2ce:	0007a023          	sw	zero,0(a5)
4200c2d2:	0007a223          	sw	zero,4(a5)
4200c2d6:	0007a423          	sw	zero,8(a5)
4200c2da:	0007a623          	sw	zero,12(a5)
4200c2de:	0007a823          	sw	zero,16(a5)
4200c2e2:	0007aa23          	sw	zero,20(a5)
4200c2e6:	00078c23          	sb	zero,24(a5)
4200c2ea:	3c0c3737          	lui	a4,0x3c0c3
4200c2ee:	bc470713          	addi	a4,a4,-1084 # 0x3c0c2bc4
4200c2f2:	00072803          	lw	a6,0(a4)
4200c2f6:	4348                	lw	a0,4(a4)
4200c2f8:	470c                	lw	a1,8(a4)
4200c2fa:	4754                	lw	a3,12(a4)
4200c2fc:	0107a023          	sw	a6,0(a5)
4200c300:	c3c8                	sw	a0,4(a5)
4200c302:	c78c                	sw	a1,8(a5)
4200c304:	c7d4                	sw	a3,12(a5)
4200c306:	01075683          	lhu	a3,16(a4)
4200c30a:	00d79823          	sh	a3,16(a5)
4200c30e:	01274703          	lbu	a4,18(a4)
4200c312:	00e78923          	sb	a4,18(a5)
4200c316:	4781                	li	a5,0
4200c318:	7e000713          	li	a4,2016
4200c31c:	46e1                	li	a3,24
4200c31e:	9dc60613          	addi	a2,a2,-1572
4200c322:	0a000593          	li	a1,160
4200c326:	4551                	li	a0,20
4200c328:	8c7fe0ef          	jal	0x4200abee
4200c32c:	3fcc47b7          	lui	a5,0x3fcc4
4200c330:	a547c703          	lbu	a4,-1452(a5) # 0x3fcc3a54
4200c334:	3fcc47b7          	lui	a5,0x3fcc4
4200c338:	a4e789a3          	sb	a4,-1453(a5) # 0x3fcc3a53
4200c33c:	b5e9                	j	0x4200c206
