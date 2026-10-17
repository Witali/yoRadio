
factory-analysis.elf:     file format elf32-littleriscv


Disassembly of section .flash.text:

4200826a <.flash.text+0x824a>:
4200826a:	1141                	addi	sp,sp,-16
4200826c:	c606                	sw	ra,12(sp)
4200826e:	3fcc47b7          	lui	a5,0x3fcc4
42008272:	9eb7c783          	lbu	a5,-1557(a5) # 0x3fcc39eb
42008276:	c785                	beqz	a5,0x4200829e
42008278:	3fcc4737          	lui	a4,0x3fcc4
4200827c:	a5674783          	lbu	a5,-1450(a4) # 0x3fcc3a56
42008280:	0785                	addi	a5,a5,1
42008282:	0ff7f793          	zext.b	a5,a5
42008286:	a4f70b23          	sb	a5,-1450(a4)
4200828a:	0b400713          	li	a4,180
4200828e:	00f77663          	bgeu	a4,a5,0x4200829a
42008292:	3fcc47b7          	lui	a5,0x3fcc4
42008296:	9e0785a3          	sb	zero,-1557(a5) # 0x3fcc39eb
4200829a:	72f030ef          	jal	0x4200c1c8
4200829e:	3fcc4737          	lui	a4,0x3fcc4
420082a2:	9cc74783          	lbu	a5,-1588(a4) # 0x3fcc39cc
420082a6:	0785                	addi	a5,a5,1
420082a8:	0ff7f793          	zext.b	a5,a5
420082ac:	9cf70623          	sb	a5,-1588(a4)
420082b0:	4729                	li	a4,10
420082b2:	0ef77e63          	bgeu	a4,a5,0x420083ae
420082b6:	3fcc47b7          	lui	a5,0x3fcc4
420082ba:	9c078623          	sb	zero,-1588(a5) # 0x3fcc39cc
420082be:	3fcc47b7          	lui	a5,0x3fcc4
420082c2:	4705                	li	a4,1
420082c4:	9ee78b23          	sb	a4,-1546(a5) # 0x3fcc39f6
420082c8:	3fcc4737          	lui	a4,0x3fcc4
420082cc:	9cb74783          	lbu	a5,-1589(a4) # 0x3fcc39cb
420082d0:	0785                	addi	a5,a5,1
420082d2:	0ff7f793          	zext.b	a5,a5
420082d6:	9cf705a3          	sb	a5,-1589(a4)
420082da:	4709                	li	a4,2
420082dc:	00f77b63          	bgeu	a4,a5,0x420082f2
420082e0:	3fcc47b7          	lui	a5,0x3fcc4
420082e4:	9c0785a3          	sb	zero,-1589(a5) # 0x3fcc39cb
420082e8:	3fcc47b7          	lui	a5,0x3fcc4
420082ec:	4705                	li	a4,1
420082ee:	9ee78ba3          	sb	a4,-1545(a5) # 0x3fcc39f7
420082f2:	3fcc4737          	lui	a4,0x3fcc4
420082f6:	9ca74783          	lbu	a5,-1590(a4) # 0x3fcc39ca
420082fa:	0785                	addi	a5,a5,1
420082fc:	0ff7f793          	zext.b	a5,a5
42008300:	9cf70523          	sb	a5,-1590(a4)
42008304:	3fcb8737          	lui	a4,0x3fcb8
42008308:	b9c70713          	addi	a4,a4,-1124 # 0x3fcb7b9c
4200830c:	1a072703          	lw	a4,416(a4)
42008310:	00e7eb63          	bltu	a5,a4,0x42008326
42008314:	3fcc47b7          	lui	a5,0x3fcc4
42008318:	9c078523          	sb	zero,-1590(a5) # 0x3fcc39ca
4200831c:	3fcc47b7          	lui	a5,0x3fcc4
42008320:	4705                	li	a4,1
42008322:	9ee78c23          	sb	a4,-1544(a5) # 0x3fcc39f8
42008326:	3fcc4737          	lui	a4,0x3fcc4
4200832a:	9c974783          	lbu	a5,-1591(a4) # 0x3fcc39c9
4200832e:	0785                	addi	a5,a5,1
42008330:	0ff7f793          	zext.b	a5,a5
42008334:	9cf704a3          	sb	a5,-1591(a4)
42008338:	03b00713          	li	a4,59
4200833c:	00f77f63          	bgeu	a4,a5,0x4200835a
42008340:	3fcc47b7          	lui	a5,0x3fcc4
42008344:	9c0784a3          	sb	zero,-1591(a5) # 0x3fcc39c9
42008348:	4785                	li	a5,1
4200834a:	3fcc4737          	lui	a4,0x3fcc4
4200834e:	9ef70aa3          	sb	a5,-1547(a4) # 0x3fcc39f5
42008352:	3fcc4737          	lui	a4,0x3fcc4
42008356:	9ef70823          	sb	a5,-1552(a4) # 0x3fcc39f0
4200835a:	3fcc4737          	lui	a4,0x3fcc4
4200835e:	9c874783          	lbu	a5,-1592(a4) # 0x3fcc39c8
42008362:	0785                	addi	a5,a5,1
42008364:	0ff7f793          	zext.b	a5,a5
42008368:	9cf70423          	sb	a5,-1592(a4)
4200836c:	0b400713          	li	a4,180
42008370:	00f77b63          	bgeu	a4,a5,0x42008386
42008374:	3fcc47b7          	lui	a5,0x3fcc4
42008378:	9c078423          	sb	zero,-1592(a5) # 0x3fcc39c8
4200837c:	3fcc47b7          	lui	a5,0x3fcc4
42008380:	4705                	li	a4,1
42008382:	9ee78a23          	sb	a4,-1548(a5) # 0x3fcc39f4
42008386:	3fcc4737          	lui	a4,0x3fcc4
4200838a:	9c472783          	lw	a5,-1596(a4) # 0x3fcc39c4
4200838e:	0785                	addi	a5,a5,1
42008390:	9cf72223          	sw	a5,-1596(a4)
42008394:	70800713          	li	a4,1800
42008398:	00f77b63          	bgeu	a4,a5,0x420083ae
4200839c:	3fcc47b7          	lui	a5,0x3fcc4
420083a0:	9c07a223          	sw	zero,-1596(a5) # 0x3fcc39c4
420083a4:	3fcc47b7          	lui	a5,0x3fcc4
420083a8:	4705                	li	a4,1
420083aa:	9ee789a3          	sb	a4,-1549(a5) # 0x3fcc39f3
420083ae:	4501                	li	a0,0
420083b0:	40b2                	lw	ra,12(sp)
420083b2:	0141                	addi	sp,sp,16
420083b4:	8082                	ret


factory-analysis.elf:     file format elf32-littleriscv


Disassembly of section .flash.text:

4200bb4c <.flash.text+0xbb2c>:
4200bb4c:	1141                	addi	sp,sp,-16
4200bb4e:	c606                	sw	ra,12(sp)
4200bb50:	4681                	li	a3,0
4200bb52:	a021                	j	0x4200bb5a
4200bb54:	0685                	addi	a3,a3,1
4200bb56:	06c2                	slli	a3,a3,0x10
4200bb58:	82c1                	srli	a3,a3,0x10
4200bb5a:	4791                	li	a5,4
4200bb5c:	04d7e063          	bltu	a5,a3,0x4200bb9c
4200bb60:	3fcc47b7          	lui	a5,0x3fcc4
4200bb64:	a517c783          	lbu	a5,-1455(a5) # 0x3fcc3a51
4200bb68:	4705                	li	a4,1
4200bb6a:	00f71733          	sll	a4,a4,a5
4200bb6e:	3fcb8637          	lui	a2,0x3fcb8
4200bb72:	b9c60613          	addi	a2,a2,-1124 # 0x3fcb7b9c
4200bb76:	1a462603          	lw	a2,420(a2)
4200bb7a:	8f71                	and	a4,a4,a2
4200bb7c:	e305                	bnez	a4,0x4200bb9c
4200bb7e:	0785                	addi	a5,a5,1
4200bb80:	0ff7f793          	zext.b	a5,a5
4200bb84:	3fcc4737          	lui	a4,0x3fcc4
4200bb88:	a4f708a3          	sb	a5,-1455(a4) # 0x3fcc3a51
4200bb8c:	4711                	li	a4,4
4200bb8e:	fcf773e3          	bgeu	a4,a5,0x4200bb54
4200bb92:	3fcc47b7          	lui	a5,0x3fcc4
4200bb96:	a40788a3          	sb	zero,-1455(a5) # 0x3fcc3a51
4200bb9a:	bf6d                	j	0x4200bb54
4200bb9c:	4795                	li	a5,5
4200bb9e:	02f68a63          	beq	a3,a5,0x4200bbd2
4200bba2:	3fcc47b7          	lui	a5,0x3fcc4
4200bba6:	a517c783          	lbu	a5,-1455(a5) # 0x3fcc3a51
4200bbaa:	cb85                	beqz	a5,0x4200bbda
4200bbac:	4705                	li	a4,1
4200bbae:	04e78f63          	beq	a5,a4,0x4200bc0c
4200bbb2:	4709                	li	a4,2
4200bbb4:	06e78363          	beq	a5,a4,0x4200bc1a
4200bbb8:	470d                	li	a4,3
4200bbba:	06e78763          	beq	a5,a4,0x4200bc28
4200bbbe:	4711                	li	a4,4
4200bbc0:	02e79363          	bne	a5,a4,0x4200bbe6
4200bbc4:	00264637          	lui	a2,0x264
4200bbc8:	4581                	li	a1,0
4200bbca:	4501                	li	a0,0
4200bbcc:	14d000ef          	jal	0x4200c518
4200bbd0:	a819                	j	0x4200bbe6
4200bbd2:	4501                	li	a0,0
4200bbd4:	e37fd0ef          	jal	0x42009a0a
4200bbd8:	a03d                	j	0x4200bc06
4200bbda:	00200637          	lui	a2,0x200
4200bbde:	4581                	li	a1,0
4200bbe0:	4501                	li	a0,0
4200bbe2:	137000ef          	jal	0x4200c518
4200bbe6:	3fcc4737          	lui	a4,0x3fcc4
4200bbea:	a5174783          	lbu	a5,-1455(a4) # 0x3fcc3a51
4200bbee:	0785                	addi	a5,a5,1
4200bbf0:	0ff7f793          	zext.b	a5,a5
4200bbf4:	a4f708a3          	sb	a5,-1455(a4)
4200bbf8:	4711                	li	a4,4
4200bbfa:	00f77663          	bgeu	a4,a5,0x4200bc06
4200bbfe:	3fcc47b7          	lui	a5,0x3fcc4
4200bc02:	a40788a3          	sb	zero,-1455(a5) # 0x3fcc3a51
4200bc06:	40b2                	lw	ra,12(sp)
4200bc08:	0141                	addi	sp,sp,16
4200bc0a:	8082                	ret
4200bc0c:	00219637          	lui	a2,0x219
4200bc10:	4581                	li	a1,0
4200bc12:	4501                	li	a0,0
4200bc14:	105000ef          	jal	0x4200c518
4200bc18:	b7f9                	j	0x4200bbe6
4200bc1a:	00232637          	lui	a2,0x232
4200bc1e:	4581                	li	a1,0
4200bc20:	4501                	li	a0,0
4200bc22:	0f7000ef          	jal	0x4200c518
4200bc26:	b7c1                	j	0x4200bbe6
4200bc28:	0024b637          	lui	a2,0x24b
4200bc2c:	4581                	li	a1,0
4200bc2e:	4501                	li	a0,0
4200bc30:	0e9000ef          	jal	0x4200c518
4200bc34:	bf4d                	j	0x4200bbe6


factory-analysis.elf:     file format elf32-littleriscv


Disassembly of section .flash.text:

4200e2ec <.flash.text+0xe2cc>:
4200e2ec:	7135                	addi	sp,sp,-160
4200e2ee:	cf06                	sw	ra,156(sp)
4200e2f0:	cd22                	sw	s0,152(sp)
4200e2f2:	cb26                	sw	s1,148(sp)
4200e2f4:	c94a                	sw	s2,144(sp)
4200e2f6:	c74e                	sw	s3,140(sp)
4200e2f8:	c552                	sw	s4,136(sp)
4200e2fa:	89aa                	mv	s3,a0
4200e2fc:	07f00613          	li	a2,127
4200e300:	858a                	mv	a1,sp
4200e302:	3922d0ef          	jal	0x4203b694
4200e306:	12a05063          	blez	a0,0x4200e426
4200e30a:	08050793          	addi	a5,a0,128
4200e30e:	978a                	add	a5,a5,sp
4200e310:	f8078023          	sb	zero,-128(a5)
4200e314:	850a                	mv	a0,sp
4200e316:	48e050ef          	jal	0x420137a4
4200e31a:	842a                	mv	s0,a0
4200e31c:	10050f63          	beqz	a0,0x4200e43a
4200e320:	3c0c35b7          	lui	a1,0x3c0c3
4200e324:	47858593          	addi	a1,a1,1144 # 0x3c0c3478
4200e328:	4b8050ef          	jal	0x420137e0
4200e32c:	84aa                	mv	s1,a0
4200e32e:	3c0c35b7          	lui	a1,0x3c0c3
4200e332:	48458593          	addi	a1,a1,1156 # 0x3c0c3484
4200e336:	8522                	mv	a0,s0
4200e338:	4a8050ef          	jal	0x420137e0
4200e33c:	892a                	mv	s2,a0
4200e33e:	2c048c63          	beqz	s1,0x4200e616
4200e342:	8526                	mv	a0,s1
4200e344:	640050ef          	jal	0x42013984
4200e348:	2c050763          	beqz	a0,0x4200e616
4200e34c:	2c090563          	beqz	s2,0x4200e616
4200e350:	854a                	mv	a0,s2
4200e352:	622050ef          	jal	0x42013974
4200e356:	2c050063          	beqz	a0,0x4200e616
4200e35a:	0104aa03          	lw	s4,16(s1)
4200e35e:	854a                	mv	a0,s2
4200e360:	602050ef          	jal	0x42013962
4200e364:	84aa                	mv	s1,a0
4200e366:	00a03933          	snez	s2,a0
4200e36a:	3c0c35b7          	lui	a1,0x3c0c3
4200e36e:	48c58593          	addi	a1,a1,1164 # 0x3c0c348c
4200e372:	8552                	mv	a0,s4
4200e374:	fdff2097          	auipc	ra,0xfdff2
4200e378:	12c080e7          	jalr	300(ra) # 0x400004a0
4200e37c:	e17d                	bnez	a0,0x4200e462
4200e37e:	3fcc47b7          	lui	a5,0x3fcc4
4200e382:	a9278423          	sb	s2,-1400(a5) # 0x3fcc3a88
4200e386:	c4e1                	beqz	s1,0x4200e44e
4200e388:	3fcb87b7          	lui	a5,0x3fcb8
4200e38c:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200e390:	1a47a703          	lw	a4,420(a5)
4200e394:	00176713          	ori	a4,a4,1
4200e398:	1ae7a223          	sw	a4,420(a5)
4200e39c:	3fcc47b7          	lui	a5,0x3fcc4
4200e3a0:	4705                	li	a4,1
4200e3a2:	9ee78023          	sb	a4,-1568(a5) # 0x3fcc39e0
4200e3a6:	3fcc47b7          	lui	a5,0x3fcc4
4200e3aa:	03200713          	li	a4,50
4200e3ae:	9ce7ae23          	sw	a4,-1572(a5) # 0x3fcc39dc
4200e3b2:	4489                	li	s1,2
4200e3b4:	fe37f097          	auipc	ra,0xfe37f
4200e3b8:	000080e7          	jalr	ra # 0x4038d3b4
4200e3bc:	86aa                	mv	a3,a0
4200e3be:	3fcb87b7          	lui	a5,0x3fcb8
4200e3c2:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200e3c6:	1a47a783          	lw	a5,420(a5)
4200e3ca:	3c0c35b7          	lui	a1,0x3c0c3
4200e3ce:	29058713          	addi	a4,a1,656 # 0x3c0c3290
4200e3d2:	3c0c3637          	lui	a2,0x3c0c3
4200e3d6:	50460613          	addi	a2,a2,1284 # 0x3c0c3504
4200e3da:	29058593          	addi	a1,a1,656
4200e3de:	8526                	mv	a0,s1
4200e3e0:	fe37f097          	auipc	ra,0xfe37f
4200e3e4:	ec2080e7          	jalr	-318(ra) # 0x4038d2a2
4200e3e8:	8522                	mv	a0,s0
4200e3ea:	641040ef          	jal	0x4201322a
4200e3ee:	3c0c3637          	lui	a2,0x3c0c3
4200e3f2:	1dc60613          	addi	a2,a2,476 # 0x3c0c31dc
4200e3f6:	3c0c35b7          	lui	a1,0x3c0c3
4200e3fa:	1e458593          	addi	a1,a1,484 # 0x3c0c31e4
4200e3fe:	854e                	mv	a0,s3
4200e400:	5152c0ef          	jal	0x4203b114
4200e404:	8626                	mv	a2,s1
4200e406:	3c0c35b7          	lui	a1,0x3c0c3
4200e40a:	28c58593          	addi	a1,a1,652 # 0x3c0c328c
4200e40e:	854e                	mv	a0,s3
4200e410:	5832c0ef          	jal	0x4203b192
4200e414:	4501                	li	a0,0
4200e416:	40fa                	lw	ra,156(sp)
4200e418:	446a                	lw	s0,152(sp)
4200e41a:	44da                	lw	s1,148(sp)
4200e41c:	494a                	lw	s2,144(sp)
4200e41e:	49ba                	lw	s3,140(sp)
4200e420:	4a2a                	lw	s4,136(sp)
4200e422:	610d                	addi	sp,sp,160
4200e424:	8082                	ret
4200e426:	3c0c3637          	lui	a2,0x3c0c3
4200e42a:	27060613          	addi	a2,a2,624 # 0x3c0c3270
4200e42e:	4581                	li	a1,0
4200e430:	854e                	mv	a0,s3
4200e432:	7512c0ef          	jal	0x4203b382
4200e436:	557d                	li	a0,-1
4200e438:	bff9                	j	0x4200e416
4200e43a:	3c0c3637          	lui	a2,0x3c0c3
4200e43e:	39460613          	addi	a2,a2,916 # 0x3c0c3394
4200e442:	458d                	li	a1,3
4200e444:	854e                	mv	a0,s3
4200e446:	73d2c0ef          	jal	0x4203b382
4200e44a:	557d                	li	a0,-1
4200e44c:	b7e9                	j	0x4200e416
4200e44e:	3fcb87b7          	lui	a5,0x3fcb8
4200e452:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200e456:	1a47a703          	lw	a4,420(a5)
4200e45a:	9b79                	andi	a4,a4,-2
4200e45c:	1ae7a223          	sw	a4,420(a5)
4200e460:	bf35                	j	0x4200e39c
4200e462:	3c0c35b7          	lui	a1,0x3c0c3
4200e466:	49c58593          	addi	a1,a1,1180 # 0x3c0c349c
4200e46a:	8552                	mv	a0,s4
4200e46c:	fdff2097          	auipc	ra,0xfdff2
4200e470:	034080e7          	jalr	52(ra) # 0x400004a0
4200e474:	e921                	bnez	a0,0x4200e4c4
4200e476:	3fcc47b7          	lui	a5,0x3fcc4
4200e47a:	a8878793          	addi	a5,a5,-1400 # 0x3fcc3a88
4200e47e:	012780a3          	sb	s2,1(a5)
4200e482:	c49d                	beqz	s1,0x4200e4b0
4200e484:	3fcb87b7          	lui	a5,0x3fcb8
4200e488:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200e48c:	1a47a703          	lw	a4,420(a5)
4200e490:	00276713          	ori	a4,a4,2
4200e494:	1ae7a223          	sw	a4,420(a5)
4200e498:	3fcc47b7          	lui	a5,0x3fcc4
4200e49c:	4705                	li	a4,1
4200e49e:	9ee78023          	sb	a4,-1568(a5) # 0x3fcc39e0
4200e4a2:	3fcc47b7          	lui	a5,0x3fcc4
4200e4a6:	03200713          	li	a4,50
4200e4aa:	9ce7ae23          	sw	a4,-1572(a5) # 0x3fcc39dc
4200e4ae:	b711                	j	0x4200e3b2
4200e4b0:	3fcb87b7          	lui	a5,0x3fcb8
4200e4b4:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200e4b8:	1a47a703          	lw	a4,420(a5)
4200e4bc:	9b75                	andi	a4,a4,-3
4200e4be:	1ae7a223          	sw	a4,420(a5)
4200e4c2:	bfd9                	j	0x4200e498
4200e4c4:	3c0c35b7          	lui	a1,0x3c0c3
4200e4c8:	4ac58593          	addi	a1,a1,1196 # 0x3c0c34ac
4200e4cc:	8552                	mv	a0,s4
4200e4ce:	fdff2097          	auipc	ra,0xfdff2
4200e4d2:	fd2080e7          	jalr	-46(ra) # 0x400004a0
4200e4d6:	e921                	bnez	a0,0x4200e526
4200e4d8:	3fcc47b7          	lui	a5,0x3fcc4
4200e4dc:	a8878793          	addi	a5,a5,-1400 # 0x3fcc3a88
4200e4e0:	01278123          	sb	s2,2(a5)
4200e4e4:	c49d                	beqz	s1,0x4200e512
4200e4e6:	3fcb87b7          	lui	a5,0x3fcb8
4200e4ea:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200e4ee:	1a47a703          	lw	a4,420(a5)
4200e4f2:	00476713          	ori	a4,a4,4
4200e4f6:	1ae7a223          	sw	a4,420(a5)
4200e4fa:	3fcc47b7          	lui	a5,0x3fcc4
4200e4fe:	4705                	li	a4,1
4200e500:	9ee78023          	sb	a4,-1568(a5) # 0x3fcc39e0
4200e504:	3fcc47b7          	lui	a5,0x3fcc4
4200e508:	03200713          	li	a4,50
4200e50c:	9ce7ae23          	sw	a4,-1572(a5) # 0x3fcc39dc
4200e510:	b54d                	j	0x4200e3b2
4200e512:	3fcb87b7          	lui	a5,0x3fcb8
4200e516:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200e51a:	1a47a703          	lw	a4,420(a5)
4200e51e:	9b6d                	andi	a4,a4,-5
4200e520:	1ae7a223          	sw	a4,420(a5)
4200e524:	bfd9                	j	0x4200e4fa
4200e526:	3c0c35b7          	lui	a1,0x3c0c3
4200e52a:	4bc58593          	addi	a1,a1,1212 # 0x3c0c34bc
4200e52e:	8552                	mv	a0,s4
4200e530:	fdff2097          	auipc	ra,0xfdff2
4200e534:	f70080e7          	jalr	-144(ra) # 0x400004a0
4200e538:	e921                	bnez	a0,0x4200e588
4200e53a:	3fcc47b7          	lui	a5,0x3fcc4
4200e53e:	a8878793          	addi	a5,a5,-1400 # 0x3fcc3a88
4200e542:	012781a3          	sb	s2,3(a5)
4200e546:	c49d                	beqz	s1,0x4200e574
4200e548:	3fcb87b7          	lui	a5,0x3fcb8
4200e54c:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200e550:	1a47a703          	lw	a4,420(a5)
4200e554:	00876713          	ori	a4,a4,8
4200e558:	1ae7a223          	sw	a4,420(a5)
4200e55c:	3fcc47b7          	lui	a5,0x3fcc4
4200e560:	4705                	li	a4,1
4200e562:	9ee78023          	sb	a4,-1568(a5) # 0x3fcc39e0
4200e566:	3fcc47b7          	lui	a5,0x3fcc4
4200e56a:	03200713          	li	a4,50
4200e56e:	9ce7ae23          	sw	a4,-1572(a5) # 0x3fcc39dc
4200e572:	b581                	j	0x4200e3b2
4200e574:	3fcb87b7          	lui	a5,0x3fcb8
4200e578:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200e57c:	1a47a703          	lw	a4,420(a5)
4200e580:	9b5d                	andi	a4,a4,-9
4200e582:	1ae7a223          	sw	a4,420(a5)
4200e586:	bfd9                	j	0x4200e55c
4200e588:	3c0c35b7          	lui	a1,0x3c0c3
4200e58c:	4cc58593          	addi	a1,a1,1228 # 0x3c0c34cc
4200e590:	8552                	mv	a0,s4
4200e592:	fdff2097          	auipc	ra,0xfdff2
4200e596:	f0e080e7          	jalr	-242(ra) # 0x400004a0
4200e59a:	e921                	bnez	a0,0x4200e5ea
4200e59c:	3fcc47b7          	lui	a5,0x3fcc4
4200e5a0:	a8878793          	addi	a5,a5,-1400 # 0x3fcc3a88
4200e5a4:	01278223          	sb	s2,4(a5)
4200e5a8:	c49d                	beqz	s1,0x4200e5d6
4200e5aa:	3fcb87b7          	lui	a5,0x3fcb8
4200e5ae:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200e5b2:	1a47a703          	lw	a4,420(a5)
4200e5b6:	01076713          	ori	a4,a4,16
4200e5ba:	1ae7a223          	sw	a4,420(a5)
4200e5be:	3fcc47b7          	lui	a5,0x3fcc4
4200e5c2:	4705                	li	a4,1
4200e5c4:	9ee78023          	sb	a4,-1568(a5) # 0x3fcc39e0
4200e5c8:	3fcc47b7          	lui	a5,0x3fcc4
4200e5cc:	03200713          	li	a4,50
4200e5d0:	9ce7ae23          	sw	a4,-1572(a5) # 0x3fcc39dc
4200e5d4:	bbf9                	j	0x4200e3b2
4200e5d6:	3fcb87b7          	lui	a5,0x3fcb8
4200e5da:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200e5de:	1a47a703          	lw	a4,420(a5)
4200e5e2:	9b3d                	andi	a4,a4,-17
4200e5e4:	1ae7a223          	sw	a4,420(a5)
4200e5e8:	bfd9                	j	0x4200e5be
4200e5ea:	fe37f097          	auipc	ra,0xfe37f
4200e5ee:	dca080e7          	jalr	-566(ra) # 0x4038d3b4
4200e5f2:	86aa                	mv	a3,a0
4200e5f4:	87d2                	mv	a5,s4
4200e5f6:	3c0c35b7          	lui	a1,0x3c0c3
4200e5fa:	29058713          	addi	a4,a1,656 # 0x3c0c3290
4200e5fe:	3c0c3637          	lui	a2,0x3c0c3
4200e602:	4dc60613          	addi	a2,a2,1244 # 0x3c0c34dc
4200e606:	29058593          	addi	a1,a1,656
4200e60a:	4509                	li	a0,2
4200e60c:	fe37f097          	auipc	ra,0xfe37f
4200e610:	c96080e7          	jalr	-874(ra) # 0x4038d2a2
4200e614:	bb79                	j	0x4200e3b2
4200e616:	3c0c3637          	lui	a2,0x3c0c3
4200e61a:	52860613          	addi	a2,a2,1320 # 0x3c0c3528
4200e61e:	458d                	li	a1,3
4200e620:	854e                	mv	a0,s3
4200e622:	5612c0ef          	jal	0x4203b382
4200e626:	8522                	mv	a0,s0
4200e628:	403040ef          	jal	0x4201322a
4200e62c:	557d                	li	a0,-1
4200e62e:	b3e5                	j	0x4200e416


factory-analysis.elf:     file format elf32-littleriscv


Disassembly of section .flash.text:

4200f764 <.flash.text+0xf744>:
4200f764:	1141                	addi	sp,sp,-16
4200f766:	c606                	sw	ra,12(sp)
4200f768:	cd15                	beqz	a0,0x4200f7a4
4200f76a:	fdff1097          	auipc	ra,0xfdff1
4200f76e:	e16080e7          	jalr	-490(ra) # 0x40000580
4200f772:	ffd50713          	addi	a4,a0,-3
4200f776:	03900793          	li	a5,57
4200f77a:	02e7e563          	bltu	a5,a4,0x4200f7a4
4200f77e:	0ff57513          	zext.b	a0,a0
4200f782:	3fcb87b7          	lui	a5,0x3fcb8
4200f786:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200f78a:	1aa7a023          	sw	a0,416(a5)
4200f78e:	3fcc47b7          	lui	a5,0x3fcc4
4200f792:	4705                	li	a4,1
4200f794:	9ee78023          	sb	a4,-1568(a5) # 0x3fcc39e0
4200f798:	3fcc47b7          	lui	a5,0x3fcc4
4200f79c:	03200713          	li	a4,50
4200f7a0:	9ce7ae23          	sw	a4,-1572(a5) # 0x3fcc39dc
4200f7a4:	40b2                	lw	ra,12(sp)
4200f7a6:	0141                	addi	sp,sp,16
4200f7a8:	8082                	ret
