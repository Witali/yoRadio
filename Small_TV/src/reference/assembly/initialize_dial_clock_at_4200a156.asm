
factory-irom.bin:     file format binary


Disassembly of section .data:

4200a156 <.data+0xa136>:
4200a156:	711d                	addi	sp,sp,-96
4200a158:	ce86                	sw	ra,92(sp)
4200a15a:	cca2                	sw	s0,88(sp)
4200a15c:	caa6                	sw	s1,84(sp)
4200a15e:	c8ca                	sw	s2,80(sp)
4200a160:	c6ce                	sw	s3,76(sp)
4200a162:	c4d2                	sw	s4,72(sp)
4200a164:	c2d6                	sw	s5,68(sp)
4200a166:	c0da                	sw	s6,64(sp)
4200a168:	de5e                	sw	s7,60(sp)
4200a16a:	dc62                	sw	s8,56(sp)
4200a16c:	da66                	sw	s9,52(sp)
4200a16e:	d86a                	sw	s10,48(sp)
4200a170:	d66e                	sw	s11,44(sp)
4200a172:	3fcc04b7          	lui	s1,0x3fcc0
4200a176:	fc848493          	addi	s1,s1,-56 # 0x3fcbffc8
4200a17a:	0084c703          	lbu	a4,8(s1)
4200a17e:	3fcc47b7          	lui	a5,0x3fcc4
4200a182:	a2e7a023          	sw	a4,-1504(a5) # 0x3fcc3a20
4200a186:	0074c703          	lbu	a4,7(s1)
4200a18a:	3fcc47b7          	lui	a5,0x3fcc4
4200a18e:	a0e7ae23          	sw	a4,-1508(a5) # 0x3fcc3a1c
4200a192:	0064c703          	lbu	a4,6(s1)
4200a196:	3fcc47b7          	lui	a5,0x3fcc4
4200a19a:	a0e7ac23          	sw	a4,-1512(a5) # 0x3fcc3a18
4200a19e:	4501                	li	a0,0
4200a1a0:	86bff0ef          	jal	0x42009a0a
4200a1a4:	98fff0ef          	jal	0x42009b32
4200a1a8:	0084cd83          	lbu	s11,8(s1)
4200a1ac:	856e                	mv	a0,s11
4200a1ae:	fdff7097          	auipc	ra,0xfdff7
4200a1b2:	8a6080e7          	jalr	-1882(ra) # 0x40000a54
4200a1b6:	3c0d6cb7          	lui	s9,0x3c0d6
4200a1ba:	2f0ca603          	lw	a2,752(s9) # 0x3c0d62f0
4200a1be:	2f4ca683          	lw	a3,756(s9)
4200a1c2:	fdff7097          	auipc	ra,0xfdff7
4200a1c6:	8ca080e7          	jalr	-1846(ra) # 0x40000a8c
4200a1ca:	3c0d6d37          	lui	s10,0x3c0d6
4200a1ce:	310d2603          	lw	a2,784(s10) # 0x3c0d6310
4200a1d2:	314d2683          	lw	a3,788(s10)
4200a1d6:	fdff6097          	auipc	ra,0xfdff6
4200a1da:	71e080e7          	jalr	1822(ra) # 0x400008f4
4200a1de:	fdff7097          	auipc	ra,0xfdff7
4200a1e2:	8c6080e7          	jalr	-1850(ra) # 0x40000aa4
4200a1e6:	3fcc4c37          	lui	s8,0x3fcc4
4200a1ea:	a0ac2a23          	sw	a0,-1516(s8) # 0x3fcc3a14
4200a1ee:	fdff7097          	auipc	ra,0xfdff7
4200a1f2:	83e080e7          	jalr	-1986(ra) # 0x40000a2c
4200a1f6:	c42a                	sw	a0,8(sp)
4200a1f8:	c62e                	sw	a1,12(sp)
4200a1fa:	26a9d0ef          	jal	0x420a7464
4200a1fe:	3c0d69b7          	lui	s3,0x3c0d6
4200a202:	3209a603          	lw	a2,800(s3) # 0x3c0d6320
4200a206:	3249a683          	lw	a3,804(s3)
4200a20a:	fdff7097          	auipc	ra,0xfdff7
4200a20e:	882080e7          	jalr	-1918(ra) # 0x40000a8c
4200a212:	3c0d6937          	lui	s2,0x3c0d6
4200a216:	2e892603          	lw	a2,744(s2) # 0x3c0d62e8
4200a21a:	2ec92683          	lw	a3,748(s2)
4200a21e:	fdff6097          	auipc	ra,0xfdff6
4200a222:	7fa080e7          	jalr	2042(ra) # 0x40000a18
4200a226:	3fcb8437          	lui	s0,0x3fcb8
4200a22a:	d9040413          	addi	s0,s0,-624 # 0x3fcb7d90
4200a22e:	fdff7097          	auipc	ra,0xfdff7
4200a232:	806080e7          	jalr	-2042(ra) # 0x40000a34
4200a236:	c808                	sw	a0,16(s0)
4200a238:	4b22                	lw	s6,8(sp)
4200a23a:	4bb2                	lw	s7,12(sp)
4200a23c:	855a                	mv	a0,s6
4200a23e:	85de                	mv	a1,s7
4200a240:	1a09d0ef          	jal	0x420a73e0
4200a244:	3209a603          	lw	a2,800(s3)
4200a248:	3249a683          	lw	a3,804(s3)
4200a24c:	fdff7097          	auipc	ra,0xfdff7
4200a250:	840080e7          	jalr	-1984(ra) # 0x40000a8c
4200a254:	862a                	mv	a2,a0
4200a256:	86ae                	mv	a3,a1
4200a258:	2e892503          	lw	a0,744(s2)
4200a25c:	2ec92583          	lw	a1,748(s2)
4200a260:	fdff7097          	auipc	ra,0xfdff7
4200a264:	83c080e7          	jalr	-1988(ra) # 0x40000a9c
4200a268:	fdff6097          	auipc	ra,0xfdff6
4200a26c:	7cc080e7          	jalr	1996(ra) # 0x40000a34
4200a270:	c848                	sw	a0,20(s0)
4200a272:	0074c503          	lbu	a0,7(s1)
4200a276:	fdff6097          	auipc	ra,0xfdff6
4200a27a:	7e2080e7          	jalr	2018(ra) # 0x40000a58
4200a27e:	89aa                	mv	s3,a0
4200a280:	856e                	mv	a0,s11
4200a282:	fdff6097          	auipc	ra,0xfdff6
4200a286:	7d6080e7          	jalr	2006(ra) # 0x40000a58
4200a28a:	3c0d6bb7          	lui	s7,0x3c0d6
4200a28e:	620ba583          	lw	a1,1568(s7) # 0x3c0d6620
4200a292:	fdff6097          	auipc	ra,0xfdff6
4200a296:	78e080e7          	jalr	1934(ra) # 0x40000a20
4200a29a:	85aa                	mv	a1,a0
4200a29c:	854e                	mv	a0,s3
4200a29e:	fdff6097          	auipc	ra,0xfdff6
4200a2a2:	77e080e7          	jalr	1918(ra) # 0x40000a1c
4200a2a6:	fdff6097          	auipc	ra,0xfdff6
4200a2aa:	786080e7          	jalr	1926(ra) # 0x40000a2c
4200a2ae:	2f0ca603          	lw	a2,752(s9)
4200a2b2:	2f4ca683          	lw	a3,756(s9)
4200a2b6:	fdff6097          	auipc	ra,0xfdff6
4200a2ba:	7d6080e7          	jalr	2006(ra) # 0x40000a8c
4200a2be:	310d2603          	lw	a2,784(s10)
4200a2c2:	314d2683          	lw	a3,788(s10)
4200a2c6:	fdff6097          	auipc	ra,0xfdff6
4200a2ca:	62e080e7          	jalr	1582(ra) # 0x400008f4
4200a2ce:	fdff6097          	auipc	ra,0xfdff6
4200a2d2:	7d6080e7          	jalr	2006(ra) # 0x40000aa4
4200a2d6:	3fcc4b37          	lui	s6,0x3fcc4
4200a2da:	a0ab2823          	sw	a0,-1520(s6) # 0x3fcc3a10
4200a2de:	fdff6097          	auipc	ra,0xfdff6
4200a2e2:	74e080e7          	jalr	1870(ra) # 0x40000a2c
4200a2e6:	8daa                	mv	s11,a0
4200a2e8:	c42e                	sw	a1,8(sp)
4200a2ea:	17a9d0ef          	jal	0x420a7464
4200a2ee:	3c0d6d37          	lui	s10,0x3c0d6
4200a2f2:	318d2603          	lw	a2,792(s10) # 0x3c0d6318
4200a2f6:	31cd2683          	lw	a3,796(s10)
4200a2fa:	fdff6097          	auipc	ra,0xfdff6
4200a2fe:	792080e7          	jalr	1938(ra) # 0x40000a8c
4200a302:	2e892603          	lw	a2,744(s2)
4200a306:	2ec92683          	lw	a3,748(s2)
4200a30a:	fdff6097          	auipc	ra,0xfdff6
4200a30e:	70e080e7          	jalr	1806(ra) # 0x40000a18
4200a312:	fdff6097          	auipc	ra,0xfdff6
4200a316:	722080e7          	jalr	1826(ra) # 0x40000a34
4200a31a:	c408                	sw	a0,8(s0)
4200a31c:	4aa2                	lw	s5,8(sp)
4200a31e:	856e                	mv	a0,s11
4200a320:	85d6                	mv	a1,s5
4200a322:	0be9d0ef          	jal	0x420a73e0
4200a326:	318d2603          	lw	a2,792(s10)
4200a32a:	31cd2683          	lw	a3,796(s10)
4200a32e:	fdff6097          	auipc	ra,0xfdff6
4200a332:	75e080e7          	jalr	1886(ra) # 0x40000a8c
4200a336:	862a                	mv	a2,a0
4200a338:	86ae                	mv	a3,a1
4200a33a:	2e892503          	lw	a0,744(s2)
4200a33e:	2ec92583          	lw	a1,748(s2)
4200a342:	fdff6097          	auipc	ra,0xfdff6
4200a346:	75a080e7          	jalr	1882(ra) # 0x40000a9c
4200a34a:	fdff6097          	auipc	ra,0xfdff6
4200a34e:	6ea080e7          	jalr	1770(ra) # 0x40000a34
4200a352:	c448                	sw	a0,12(s0)
4200a354:	0064c703          	lbu	a4,6(s1)
4200a358:	aaaab7b7          	lui	a5,0xaaaab
4200a35c:	aab78793          	addi	a5,a5,-1365 # 0xaaaaaaab
4200a360:	02f737b3          	mulhu	a5,a4,a5
4200a364:	838d                	srli	a5,a5,0x3
4200a366:	00179693          	slli	a3,a5,0x1
4200a36a:	97b6                	add	a5,a5,a3
4200a36c:	078a                	slli	a5,a5,0x2
4200a36e:	8f1d                	sub	a4,a4,a5
4200a370:	0ff77493          	zext.b	s1,a4
4200a374:	620ba583          	lw	a1,1568(s7)
4200a378:	854e                	mv	a0,s3
4200a37a:	fdff6097          	auipc	ra,0xfdff6
4200a37e:	6a6080e7          	jalr	1702(ra) # 0x40000a20
4200a382:	89aa                	mv	s3,a0
4200a384:	8526                	mv	a0,s1
4200a386:	fdff6097          	auipc	ra,0xfdff6
4200a38a:	6d2080e7          	jalr	1746(ra) # 0x40000a58
4200a38e:	85ce                	mv	a1,s3
4200a390:	fdff6097          	auipc	ra,0xfdff6
4200a394:	68c080e7          	jalr	1676(ra) # 0x40000a1c
4200a398:	fdff6097          	auipc	ra,0xfdff6
4200a39c:	694080e7          	jalr	1684(ra) # 0x40000a2c
4200a3a0:	2f0ca603          	lw	a2,752(s9)
4200a3a4:	2f4ca683          	lw	a3,756(s9)
4200a3a8:	fdff6097          	auipc	ra,0xfdff6
4200a3ac:	6e4080e7          	jalr	1764(ra) # 0x40000a8c
4200a3b0:	3c0d67b7          	lui	a5,0x3c0d6
4200a3b4:	2f87a603          	lw	a2,760(a5) # 0x3c0d62f8
4200a3b8:	2fc7a683          	lw	a3,764(a5)
4200a3bc:	fdff6097          	auipc	ra,0xfdff6
4200a3c0:	538080e7          	jalr	1336(ra) # 0x400008f4
4200a3c4:	fdff6097          	auipc	ra,0xfdff6
4200a3c8:	6e0080e7          	jalr	1760(ra) # 0x40000aa4
4200a3cc:	89aa                	mv	s3,a0
4200a3ce:	3fcc4ab7          	lui	s5,0x3fcc4
4200a3d2:	a0aaa623          	sw	a0,-1524(s5) # 0x3fcc3a0c
4200a3d6:	fdff6097          	auipc	ra,0xfdff6
4200a3da:	656080e7          	jalr	1622(ra) # 0x40000a2c
4200a3de:	8a2a                	mv	s4,a0
4200a3e0:	84ae                	mv	s1,a1
4200a3e2:	0829d0ef          	jal	0x420a7464
4200a3e6:	3c0d6bb7          	lui	s7,0x3c0d6
4200a3ea:	308ba603          	lw	a2,776(s7) # 0x3c0d6308
4200a3ee:	30cba683          	lw	a3,780(s7)
4200a3f2:	fdff6097          	auipc	ra,0xfdff6
4200a3f6:	69a080e7          	jalr	1690(ra) # 0x40000a8c
4200a3fa:	2e892603          	lw	a2,744(s2)
4200a3fe:	2ec92683          	lw	a3,748(s2)
4200a402:	fdff6097          	auipc	ra,0xfdff6
4200a406:	616080e7          	jalr	1558(ra) # 0x40000a18
4200a40a:	fdff6097          	auipc	ra,0xfdff6
4200a40e:	62a080e7          	jalr	1578(ra) # 0x40000a34
4200a412:	c008                	sw	a0,0(s0)
4200a414:	c052                	sw	s4,0(sp)
4200a416:	c226                	sw	s1,4(sp)
4200a418:	4502                	lw	a0,0(sp)
4200a41a:	4592                	lw	a1,4(sp)
4200a41c:	7c59c0ef          	jal	0x420a73e0
4200a420:	308ba603          	lw	a2,776(s7)
4200a424:	30cba683          	lw	a3,780(s7)
4200a428:	fdff6097          	auipc	ra,0xfdff6
4200a42c:	664080e7          	jalr	1636(ra) # 0x40000a8c
4200a430:	862a                	mv	a2,a0
4200a432:	86ae                	mv	a3,a1
4200a434:	2e892503          	lw	a0,744(s2)
4200a438:	2ec92583          	lw	a1,748(s2)
4200a43c:	fdff6097          	auipc	ra,0xfdff6
4200a440:	660080e7          	jalr	1632(ra) # 0x40000a9c
4200a444:	fdff6097          	auipc	ra,0xfdff6
4200a448:	5f0080e7          	jalr	1520(ra) # 0x40000a34
4200a44c:	c048                	sw	a0,4(s0)
4200a44e:	4695                	li	a3,5
4200a450:	64c1                	lui	s1,0x10
4200a452:	80048613          	addi	a2,s1,-2048 # 0xf800
4200a456:	03200593          	li	a1,50
4200a45a:	854e                	mv	a0,s3
4200a45c:	ddcff0ef          	jal	0x42009a38
4200a460:	4695                	li	a3,5
4200a462:	fe048613          	addi	a2,s1,-32
4200a466:	04600593          	li	a1,70
4200a46a:	a10b2503          	lw	a0,-1520(s6)
4200a46e:	dcaff0ef          	jal	0x42009a38
4200a472:	468d                	li	a3,3
4200a474:	fff48613          	addi	a2,s1,-1
4200a478:	05a00593          	li	a1,90
4200a47c:	a14c2503          	lw	a0,-1516(s8)
4200a480:	db8ff0ef          	jal	0x42009a38
4200a484:	a14c2703          	lw	a4,-1516(s8)
4200a488:	3fcc47b7          	lui	a5,0x3fcc4
4200a48c:	a0e7a423          	sw	a4,-1528(a5) # 0x3fcc3a08
4200a490:	a10b2703          	lw	a4,-1520(s6)
4200a494:	3fcc47b7          	lui	a5,0x3fcc4
4200a498:	a0e7a223          	sw	a4,-1532(a5) # 0x3fcc3a04
4200a49c:	a0caa703          	lw	a4,-1524(s5)
4200a4a0:	3fcc47b7          	lui	a5,0x3fcc4
4200a4a4:	a0e7a023          	sw	a4,-1536(a5) # 0x3fcc3a00
4200a4a8:	4818                	lw	a4,16(s0)
4200a4aa:	3fcb87b7          	lui	a5,0x3fcb8
4200a4ae:	d7878793          	addi	a5,a5,-648 # 0x3fcb7d78
4200a4b2:	cb98                	sw	a4,16(a5)
4200a4b4:	4858                	lw	a4,20(s0)
4200a4b6:	cbd8                	sw	a4,20(a5)
4200a4b8:	4418                	lw	a4,8(s0)
4200a4ba:	c798                	sw	a4,8(a5)
4200a4bc:	4458                	lw	a4,12(s0)
4200a4be:	c7d8                	sw	a4,12(a5)
4200a4c0:	4018                	lw	a4,0(s0)
4200a4c2:	c398                	sw	a4,0(a5)
4200a4c4:	4058                	lw	a4,4(s0)
4200a4c6:	c3d8                	sw	a4,4(a5)
4200a4c8:	03100793          	li	a5,49
4200a4cc:	00f10c23          	sb	a5,24(sp)
4200a4d0:	03200793          	li	a5,50
4200a4d4:	00f10ca3          	sb	a5,25(sp)
4200a4d8:	00010d23          	sb	zero,26(sp)
4200a4dc:	0820                	addi	s0,sp,24
4200a4de:	4781                	li	a5,0
4200a4e0:	fff48713          	addi	a4,s1,-1
4200a4e4:	02000693          	li	a3,32
4200a4e8:	8622                	mv	a2,s0
4200a4ea:	4581                	li	a1,0
4200a4ec:	06800513          	li	a0,104
4200a4f0:	2dfd                	addiw	s11,s11,31
4200a4f2:	03900793          	li	a5,57
4200a4f6:	00f10c23          	sb	a5,24(sp)
4200a4fa:	00010ca3          	sb	zero,25(sp)
4200a4fe:	00010d23          	sb	zero,26(sp)
4200a502:	4781                	li	a5,0
4200a504:	fff48713          	addi	a4,s1,-1
4200a508:	02000693          	li	a3,32
4200a50c:	8622                	mv	a2,s0
4200a50e:	06800593          	li	a1,104
4200a512:	4501                	li	a0,0
4200a514:	2de9                	addiw	s11,s11,26
4200a516:	03300793          	li	a5,51
4200a51a:	00f10c23          	sb	a5,24(sp)
4200a51e:	00010ca3          	sb	zero,25(sp)
4200a522:	00010d23          	sb	zero,26(sp)
4200a526:	4781                	li	a5,0
4200a528:	fff48713          	addi	a4,s1,-1
4200a52c:	02000693          	li	a3,32
4200a530:	8622                	mv	a2,s0
4200a532:	06800593          	li	a1,104
4200a536:	0e000513          	li	a0,224
4200a53a:	2d55                	addiw	s10,s10,21
4200a53c:	03600793          	li	a5,54
4200a540:	00f10c23          	sb	a5,24(sp)
4200a544:	00010ca3          	sb	zero,25(sp)
4200a548:	00010d23          	sb	zero,26(sp)
4200a54c:	4781                	li	a5,0
4200a54e:	fff48713          	addi	a4,s1,-1
4200a552:	02000693          	li	a3,32
4200a556:	8622                	mv	a2,s0
4200a558:	0d000593          	li	a1,208
4200a55c:	06800513          	li	a0,104
4200a560:	2579                	addiw	a0,a0,30
4200a562:	fff48713          	addi	a4,s1,-1
4200a566:	46c1                	li	a3,16
4200a568:	3fcb8637          	lui	a2,0x3fcb8
4200a56c:	b8460613          	addi	a2,a2,-1148 # 0x3fcb7b84
4200a570:	0e100593          	li	a1,225
4200a574:	4515                	li	a0,5
4200a576:	2165                	addiw	sp,sp,25
4200a578:	4785                	li	a5,1
4200a57a:	3fcc4737          	lui	a4,0x3fcc4
4200a57e:	9ef70ba3          	sb	a5,-1545(a4) # 0x3fcc39f7
4200a582:	3fcc4737          	lui	a4,0x3fcc4
4200a586:	9ef70b23          	sb	a5,-1546(a4) # 0x3fcc39f6
4200a58a:	3fcc4737          	lui	a4,0x3fcc4
4200a58e:	9ef70aa3          	sb	a5,-1547(a4) # 0x3fcc39f5
4200a592:	40f6                	lw	ra,92(sp)
4200a594:	4466                	lw	s0,88(sp)
4200a596:	44d6                	lw	s1,84(sp)
4200a598:	4946                	lw	s2,80(sp)
4200a59a:	49b6                	lw	s3,76(sp)
4200a59c:	4a26                	lw	s4,72(sp)
4200a59e:	4a96                	lw	s5,68(sp)
4200a5a0:	4b06                	lw	s6,64(sp)
4200a5a2:	5bf2                	lw	s7,60(sp)
4200a5a4:	5c62                	lw	s8,56(sp)
4200a5a6:	5cd2                	lw	s9,52(sp)
4200a5a8:	5d42                	lw	s10,48(sp)
4200a5aa:	5db2                	lw	s11,44(sp)
4200a5ac:	6125                	addi	sp,sp,96
4200a5ae:	8082                	ret
