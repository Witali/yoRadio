
factory-irom.bin:     file format binary


Disassembly of section .data:

4200b340 <.data+0xb320>:
4200b340:	1101                	addi	sp,sp,-32
4200b342:	ce06                	sw	ra,28(sp)
4200b344:	cc22                	sw	s0,24(sp)
4200b346:	ca26                	sw	s1,20(sp)
4200b348:	c84a                	sw	s2,16(sp)
4200b34a:	c64e                	sw	s3,12(sp)
4200b34c:	3fcc47b7          	lui	a5,0x3fcc4
4200b350:	9d77c783          	lbu	a5,-1577(a5) # 0x3fcc39d7
4200b354:	cfa1                	beqz	a5,0x4200b3ac
4200b356:	3fcc0537          	lui	a0,0x3fcc0
4200b35a:	f6c50513          	addi	a0,a0,-148 # 0x3fcbff6c
4200b35e:	fdff5097          	auipc	ra,0xfdff5
4200b362:	14a080e7          	jalr	330(ra) # 0x400004a8
4200b366:	0ff57513          	zext.b	a0,a0
4200b36a:	4799                	li	a5,6
4200b36c:	1aa7e363          	bltu	a5,a0,0x4200b512
4200b370:	cd15                	beqz	a0,0x4200b3ac
4200b372:	00151793          	slli	a5,a0,0x1
4200b376:	953e                	add	a0,a0,a5
4200b378:	050a                	slli	a0,a0,0x2
4200b37a:	0ff57513          	zext.b	a0,a0
4200b37e:	05000793          	li	a5,80
4200b382:	40a78533          	sub	a0,a5,a0
4200b386:	8505                	srai	a0,a0,0x1
4200b388:	0542                	slli	a0,a0,0x10
4200b38a:	8141                	srli	a0,a0,0x10
4200b38c:	0a050513          	addi	a0,a0,160
4200b390:	0542                	slli	a0,a0,0x10
4200b392:	8141                	srli	a0,a0,0x10
4200b394:	4781                	li	a5,0
4200b396:	6741                	lui	a4,0x10
4200b398:	1701                	addi	a4,a4,-32 # 0xffe0
4200b39a:	46e1                	li	a3,24
4200b39c:	3fcc0637          	lui	a2,0x3fcc0
4200b3a0:	f6c60613          	addi	a2,a2,-148 # 0x3fcbff6c
4200b3a4:	05300593          	li	a1,83
4200b3a8:	847ff0ef          	jal	0x4200abee
4200b3ac:	3fcc47b7          	lui	a5,0x3fcc4
4200b3b0:	aa87a603          	lw	a2,-1368(a5) # 0x3fcc3aa8
4200b3b4:	16061163          	bnez	a2,0x4200b516
4200b3b8:	003bb637          	lui	a2,0x3bb
4200b3bc:	80060613          	addi	a2,a2,-2048 # 0x3ba800
4200b3c0:	0b400593          	li	a1,180
4200b3c4:	4529                	li	a0,10
4200b3c6:	152010ef          	jal	0x4200c518
4200b3ca:	003c2637          	lui	a2,0x3c2
4200b3ce:	0ba00593          	li	a1,186
4200b3d2:	02800513          	li	a0,40
4200b3d6:	142010ef          	jal	0x4200c518
4200b3da:	3fcbb7b7          	lui	a5,0x3fcbb
4200b3de:	9a878793          	addi	a5,a5,-1624 # 0x3fcba9a8
4200b3e2:	0007a023          	sw	zero,0(a5)
4200b3e6:	0007a223          	sw	zero,4(a5)
4200b3ea:	0007a423          	sw	zero,8(a5)
4200b3ee:	00079623          	sh	zero,12(a5)
4200b3f2:	00078723          	sb	zero,14(a5)
4200b3f6:	4701                	li	a4,0
4200b3f8:	46e1                	li	a3,24
4200b3fa:	04800613          	li	a2,72
4200b3fe:	0b400593          	li	a1,180
4200b402:	05000513          	li	a0,80
4200b406:	d30fe0ef          	jal	0x42009936
4200b40a:	3fcc47b7          	lui	a5,0x3fcc4
4200b40e:	9d77c783          	lbu	a5,-1577(a5) # 0x3fcc39d7
4200b412:	14078b63          	beqz	a5,0x4200b568
4200b416:	3fcc47b7          	lui	a5,0x3fcc4
4200b41a:	a4c7a503          	lw	a0,-1460(a5) # 0x3fcc3a4c
4200b41e:	fdff5097          	auipc	ra,0xfdff5
4200b422:	636080e7          	jalr	1590(ra) # 0x40000a54
4200b426:	3fcb87b7          	lui	a5,0x3fcb8
4200b42a:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200b42e:	16c7a703          	lw	a4,364(a5)
4200b432:	4785                	li	a5,1
4200b434:	0ef70763          	beq	a4,a5,0x4200b522
4200b438:	862a                	mv	a2,a0
4200b43a:	86ae                	mv	a3,a1
4200b43c:	3c0c35b7          	lui	a1,0x3c0c3
4200b440:	b9c58593          	addi	a1,a1,-1124 # 0x3c0c2b9c
4200b444:	3fcbb537          	lui	a0,0x3fcbb
4200b448:	9a850513          	addi	a0,a0,-1624 # 0x3fcba9a8
4200b44c:	fdff5097          	auipc	ra,0xfdff5
4200b450:	25c080e7          	jalr	604(ra) # 0x400006a8
4200b454:	4781                	li	a5,0
4200b456:	6741                	lui	a4,0x10
4200b458:	177d                	addi	a4,a4,-1 # 0xffff
4200b45a:	46e1                	li	a3,24
4200b45c:	3fcbb437          	lui	s0,0x3fcbb
4200b460:	9a840613          	addi	a2,s0,-1624 # 0x3fcba9a8
4200b464:	0b400593          	li	a1,180
4200b468:	05000513          	li	a0,80
4200b46c:	f82ff0ef          	jal	0x4200abee
4200b470:	003be637          	lui	a2,0x3be
4200b474:	40060613          	addi	a2,a2,1024 # 0x3be400
4200b478:	0d200593          	li	a1,210
4200b47c:	4531                	li	a0,12
4200b47e:	09a010ef          	jal	0x4200c518
4200b482:	003c6637          	lui	a2,0x3c6
4200b486:	c0060613          	addi	a2,a2,-1024 # 0x3c5c00
4200b48a:	0d800593          	li	a1,216
4200b48e:	02800513          	li	a0,40
4200b492:	086010ef          	jal	0x4200c518
4200b496:	9a840793          	addi	a5,s0,-1624
4200b49a:	0007a023          	sw	zero,0(a5)
4200b49e:	0007a223          	sw	zero,4(a5)
4200b4a2:	0007a423          	sw	zero,8(a5)
4200b4a6:	00079623          	sh	zero,12(a5)
4200b4aa:	00078723          	sb	zero,14(a5)
4200b4ae:	4701                	li	a4,0
4200b4b0:	46e1                	li	a3,24
4200b4b2:	04800613          	li	a2,72
4200b4b6:	0d200593          	li	a1,210
4200b4ba:	05000513          	li	a0,80
4200b4be:	c78fe0ef          	jal	0x42009936
4200b4c2:	3fcc47b7          	lui	a5,0x3fcc4
4200b4c6:	9d77c783          	lbu	a5,-1577(a5) # 0x3fcc39d7
4200b4ca:	c7e5                	beqz	a5,0x4200b5b2
4200b4cc:	3fcc47b7          	lui	a5,0x3fcc4
4200b4d0:	a487a603          	lw	a2,-1464(a5) # 0x3fcc3a48
4200b4d4:	3c0c35b7          	lui	a1,0x3c0c3
4200b4d8:	b4058593          	addi	a1,a1,-1216 # 0x3c0c2b40
4200b4dc:	9a840513          	addi	a0,s0,-1624
4200b4e0:	fdff5097          	auipc	ra,0xfdff5
4200b4e4:	1c8080e7          	jalr	456(ra) # 0x400006a8
4200b4e8:	4781                	li	a5,0
4200b4ea:	6741                	lui	a4,0x10
4200b4ec:	177d                	addi	a4,a4,-1 # 0xffff
4200b4ee:	46e1                	li	a3,24
4200b4f0:	3fcbb637          	lui	a2,0x3fcbb
4200b4f4:	9a860613          	addi	a2,a2,-1624 # 0x3fcba9a8
4200b4f8:	0d200593          	li	a1,210
4200b4fc:	05000513          	li	a0,80
4200b500:	eeeff0ef          	jal	0x4200abee
4200b504:	40f2                	lw	ra,28(sp)
4200b506:	4462                	lw	s0,24(sp)
4200b508:	44d2                	lw	s1,20(sp)
4200b50a:	4942                	lw	s2,16(sp)
4200b50c:	49b2                	lw	s3,12(sp)
4200b50e:	6105                	addi	sp,sp,32
4200b510:	8082                	ret
4200b512:	4519                	li	a0,6
4200b514:	bdb9                	j	0x4200b372
4200b516:	45a9                	li	a1,10
4200b518:	0b400513          	li	a0,180
4200b51c:	1af050ef          	jal	0x42010eca
4200b520:	bd61                	j	0x4200b3b8
4200b522:	3c0d67b7          	lui	a5,0x3c0d6
4200b526:	3287a603          	lw	a2,808(a5) # 0x3c0d6328
4200b52a:	32c7a683          	lw	a3,812(a5)
4200b52e:	fdff5097          	auipc	ra,0xfdff5
4200b532:	55e080e7          	jalr	1374(ra) # 0x40000a8c
4200b536:	3c0d67b7          	lui	a5,0x3c0d6
4200b53a:	3307a603          	lw	a2,816(a5) # 0x3c0d6330
4200b53e:	3347a683          	lw	a3,820(a5)
4200b542:	fdff5097          	auipc	ra,0xfdff5
4200b546:	4d6080e7          	jalr	1238(ra) # 0x40000a18
4200b54a:	862a                	mv	a2,a0
4200b54c:	86ae                	mv	a3,a1
4200b54e:	3c0c35b7          	lui	a1,0x3c0c3
4200b552:	b8c58593          	addi	a1,a1,-1140 # 0x3c0c2b8c
4200b556:	3fcbb537          	lui	a0,0x3fcbb
4200b55a:	9a850513          	addi	a0,a0,-1624 # 0x3fcba9a8
4200b55e:	fdff5097          	auipc	ra,0xfdff5
4200b562:	14a080e7          	jalr	330(ra) # 0x400006a8
4200b566:	b5fd                	j	0x4200b454
4200b568:	3fcb87b7          	lui	a5,0x3fcb8
4200b56c:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200b570:	16c7a703          	lw	a4,364(a5)
4200b574:	4785                	li	a5,1
4200b576:	02f70063          	beq	a4,a5,0x4200b596
4200b57a:	3fcbb7b7          	lui	a5,0x3fcbb
4200b57e:	9a878793          	addi	a5,a5,-1624 # 0x3fcba9a8
4200b582:	a12d3737          	lui	a4,0xa12d3
4200b586:	d2070713          	addi	a4,a4,-736 # 0xa12d2d20
4200b58a:	c398                	sw	a4,0(a5)
4200b58c:	0e600713          	li	a4,230
4200b590:	00e79223          	sh	a4,4(a5)
4200b594:	b5c1                	j	0x4200b454
4200b596:	3fcbb7b7          	lui	a5,0x3fcbb
4200b59a:	9a878793          	addi	a5,a5,-1624 # 0x3fcba9a8
4200b59e:	a82d3737          	lui	a4,0xa82d3
4200b5a2:	d2070713          	addi	a4,a4,-736 # 0xa82d2d20
4200b5a6:	c398                	sw	a4,0(a5)
4200b5a8:	04800713          	li	a4,72
4200b5ac:	00e79223          	sh	a4,4(a5)
4200b5b0:	b555                	j	0x4200b454
4200b5b2:	3c0c35b7          	lui	a1,0x3c0c3
4200b5b6:	b4858593          	addi	a1,a1,-1208 # 0x3c0c2b48
4200b5ba:	3fcbb537          	lui	a0,0x3fcbb
4200b5be:	9a850513          	addi	a0,a0,-1624 # 0x3fcba9a8
4200b5c2:	fdff5097          	auipc	ra,0xfdff5
4200b5c6:	0e6080e7          	jalr	230(ra) # 0x400006a8
4200b5ca:	bf39                	j	0x4200b4e8
