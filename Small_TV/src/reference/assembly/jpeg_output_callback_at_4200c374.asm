
factory-irom.bin:     file format binary


Disassembly of section .data:

4200c374 <.data+0xc354>:
4200c374:	1101                	addi	sp,sp,-32
4200c376:	ce06                	sw	ra,28(sp)
4200c378:	cc22                	sw	s0,24(sp)
4200c37a:	ca26                	sw	s1,20(sp)
4200c37c:	c84a                	sw	s2,16(sp)
4200c37e:	c64e                	sw	s3,12(sp)
4200c380:	c452                	sw	s4,8(sp)
4200c382:	c256                	sw	s5,4(sp)
4200c384:	c05a                	sw	s6,0(sp)
4200c386:	89ae                	mv	s3,a1
4200c388:	8a32                	mv	s4,a2
4200c38a:	07452b03          	lw	s6,116(a0)
4200c38e:	004b2483          	lw	s1,4(s6)
4200c392:	00465403          	lhu	s0,4(a2)
4200c396:	3fcc47b7          	lui	a5,0x3fcc4
4200c39a:	a657c783          	lbu	a5,-1435(a5) # 0x3fcc3a65
4200c39e:	40f407b3          	sub	a5,s0,a5
4200c3a2:	008b2a83          	lw	s5,8(s6)
4200c3a6:	035787b3          	mul	a5,a5,s5
4200c3aa:	00065703          	lhu	a4,0(a2)
4200c3ae:	97ba                	add	a5,a5,a4
4200c3b0:	0786                	slli	a5,a5,0x1
4200c3b2:	94be                	add	s1,s1,a5
4200c3b4:	00265903          	lhu	s2,2(a2)
4200c3b8:	40e90933          	sub	s2,s2,a4
4200c3bc:	0905                	addi	s2,s2,1
4200c3be:	0906                	slli	s2,s2,0x1
4200c3c0:	0942                	slli	s2,s2,0x10
4200c3c2:	01095913          	srli	s2,s2,0x10
4200c3c6:	0a86                	slli	s5,s5,0x1
4200c3c8:	a829                	j	0x4200c3e2
4200c3ca:	864a                	mv	a2,s2
4200c3cc:	85ce                	mv	a1,s3
4200c3ce:	8526                	mv	a0,s1
4200c3d0:	fdff4097          	auipc	ra,0xfdff4
4200c3d4:	0bc080e7          	jalr	188(ra) # 0x4000048c
4200c3d8:	99ca                	add	s3,s3,s2
4200c3da:	94d6                	add	s1,s1,s5
4200c3dc:	0405                	addi	s0,s0,1
4200c3de:	0442                	slli	s0,s0,0x10
4200c3e0:	8041                	srli	s0,s0,0x10
4200c3e2:	006a5683          	lhu	a3,6(s4)
4200c3e6:	fe86f2e3          	bgeu	a3,s0,0x4200c3ca
4200c3ea:	002a5603          	lhu	a2,2(s4)
4200c3ee:	008b2783          	lw	a5,8(s6)
4200c3f2:	fff78713          	addi	a4,a5,-1
4200c3f6:	06e66863          	bltu	a2,a4,0x4200c466
4200c3fa:	0792                	slli	a5,a5,0x4
4200c3fc:	07c2                	slli	a5,a5,0x10
4200c3fe:	83c1                	srli	a5,a5,0x10
4200c400:	41590933          	sub	s2,s2,s5
4200c404:	01248433          	add	s0,s1,s2
4200c408:	004b2703          	lw	a4,4(s6)
4200c40c:	8c19                	sub	s0,s0,a4
4200c40e:	0442                	slli	s0,s0,0x10
4200c410:	8041                	srli	s0,s0,0x10
4200c412:	97a2                	add	a5,a5,s0
4200c414:	6505                	lui	a0,0x1
4200c416:	3ff50513          	addi	a0,a0,1023 # 0x13ff
4200c41a:	00f54a63          	blt	a0,a5,0x4200c42e
4200c41e:	00168793          	addi	a5,a3,1
4200c422:	3fcc45b7          	lui	a1,0x3fcc4
4200c426:	a665d583          	lhu	a1,-1434(a1) # 0x3fcc3a66
4200c42a:	02b7ce63          	blt	a5,a1,0x4200c466
4200c42e:	3fcc47b7          	lui	a5,0x3fcc4
4200c432:	a6c7c783          	lbu	a5,-1428(a5) # 0x3fcc3a6c
4200c436:	c3b9                	beqz	a5,0x4200c47c
4200c438:	3fcc44b7          	lui	s1,0x3fcc4
4200c43c:	86a2                	mv	a3,s0
4200c43e:	a5c4a603          	lw	a2,-1444(s1) # 0x3fcc3a5c
4200c442:	85ba                	mv	a1,a4
4200c444:	4501                	li	a0,0
4200c446:	fe386097          	auipc	ra,0xfe386
4200c44a:	02c080e7          	jalr	44(ra) # 0x40392472
4200c44e:	a5c4a783          	lw	a5,-1444(s1)
4200c452:	97a2                	add	a5,a5,s0
4200c454:	a4f4ae23          	sw	a5,-1444(s1)
4200c458:	006a5783          	lhu	a5,6(s4)
4200c45c:	0785                	addi	a5,a5,1
4200c45e:	3fcc4737          	lui	a4,0x3fcc4
4200c462:	a6f702a3          	sb	a5,-1435(a4) # 0x3fcc3a65
4200c466:	4505                	li	a0,1
4200c468:	40f2                	lw	ra,28(sp)
4200c46a:	4462                	lw	s0,24(sp)
4200c46c:	44d2                	lw	s1,20(sp)
4200c46e:	4942                	lw	s2,16(sp)
4200c470:	49b2                	lw	s3,12(sp)
4200c472:	4a22                	lw	s4,8(sp)
4200c474:	4a92                	lw	s5,4(sp)
4200c476:	4b02                	lw	s6,0(sp)
4200c478:	6105                	addi	sp,sp,32
4200c47a:	8082                	ret
4200c47c:	3fcc47b7          	lui	a5,0x3fcc4
4200c480:	a5a7d503          	lhu	a0,-1446(a5) # 0x3fcc3a5a
4200c484:	3fcc47b7          	lui	a5,0x3fcc4
4200c488:	a587d583          	lhu	a1,-1448(a5) # 0x3fcc3a58
4200c48c:	96ae                	add	a3,a3,a1
4200c48e:	962a                	add	a2,a2,a0
4200c490:	3fcc47b7          	lui	a5,0x3fcc4
4200c494:	a657c783          	lbu	a5,-1435(a5) # 0x3fcc3a65
4200c498:	95be                	add	a1,a1,a5
4200c49a:	06c2                	slli	a3,a3,0x10
4200c49c:	82c1                	srli	a3,a3,0x10
4200c49e:	0642                	slli	a2,a2,0x10
4200c4a0:	8241                	srli	a2,a2,0x10
4200c4a2:	05c2                	slli	a1,a1,0x10
4200c4a4:	81c1                	srli	a1,a1,0x10
4200c4a6:	868fd0ef          	jal	0x4200950e
4200c4aa:	b77d                	j	0x4200c458
