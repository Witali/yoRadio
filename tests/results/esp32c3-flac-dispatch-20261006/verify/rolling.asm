
idf/esp32c3-oled-native/build-flac-predictor/yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4203541e <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj>:
4203541e:	479d                	li	a5,7
42035420:	3ac7fc63          	bgeu	a5,a2,420357d8 <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x3ba>
42035424:	711d                	addi	sp,sp,-96
42035426:	00165293          	srli	t0,a2,0x1
4203542a:	cea2                	sw	s0,92(sp)
4203542c:	c8ce                	sw	s3,80(sp)
4203542e:	ffe28813          	addi	a6,t0,-2
42035432:	4791                	li	a5,4
42035434:	8432                	mv	s0,a2
42035436:	89ae                	mv	s3,a1
42035438:	3707ea63          	bltu	a5,a6,420357ac <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x38e>
4203543c:	3fc91f37          	lui	t5,0x3fc91
42035440:	26cf2383          	lw	t2,620(t5) # 3fc9126c <_ZN12_GLOBAL__N_1L5coefsE>
42035444:	26cf0f13          	addi	t5,t5,620
42035448:	004f0713          	addi	a4,t5,4
4203544c:	00241313          	slli	t1,s0,0x2
42035450:	85ba                	mv	a1,a4
42035452:	8e7a                	mv	t3,t5
42035454:	937a                	add	t1,t1,t5
42035456:	861e                	mv	a2,t2
42035458:	4881                	li	a7,0
4203545a:	4681                	li	a3,0
4203545c:	87b2                	mv	a5,a2
4203545e:	4190                	lw	a2,0(a1)
42035460:	40f00eb3          	neg	t4,a5
42035464:	0591                	addi	a1,a1,4
42035466:	40ce8eb3          	sub	t4,t4,a2
4203546a:	40f607b3          	sub	a5,a2,a5
4203546e:	01d03eb3          	snez	t4,t4
42035472:	00f037b3          	snez	a5,a5
42035476:	98f6                	add	a7,a7,t4
42035478:	96be                	add	a3,a3,a5
4203547a:	8eb6                	mv	t4,a3
4203547c:	00d8f363          	bgeu	a7,a3,42035482 <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x64>
42035480:	8ec6                	mv	t4,a7
42035482:	35d86d63          	bltu	a6,t4,420357dc <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x3be>
42035486:	fcb31be3          	bne	t1,a1,4203545c <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x3e>
4203548a:	3fc95637          	lui	a2,0x3fc95
4203548e:	3fc957b7          	lui	a5,0x3fc95
42035492:	c5264803          	lbu	a6,-942(a2) # 3fc94c52 <_ZN12_GLOBAL__N_1L16coefficientCountE>
42035496:	c4a7d583          	lhu	a1,-950(a5) # 3fc94c4a <m_blockSize>
4203549a:	32b85a63          	bge	a6,a1,420357ce <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x3b0>
4203549e:	c4d6                	sw	s5,72(sp)
420354a0:	c2da                	sw	s6,68(sp)
420354a2:	00129a93          	slli	s5,t0,0x1
420354a6:	cca6                	sw	s1,88(sp)
420354a8:	caca                	sw	s2,84(sp)
420354aa:	c6d2                	sw	s4,76(sp)
420354ac:	c0de                	sw	s7,64(sp)
420354ae:	de62                	sw	s8,60(sp)
420354b0:	dc66                	sw	s9,56(sp)
420354b2:	fffa8b13          	addi	s6,s5,-1
420354b6:	32d8e863          	bltu	a7,a3,420357e6 <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x3c8>
420354ba:	8f9e                	mv	t6,t2
420354bc:	4905                	li	s2,1
420354be:	4781                	li	a5,0
420354c0:	02010a13          	addi	s4,sp,32
420354c4:	4304                	lw	s1,0(a4)
420354c6:	02078b93          	addi	s7,a5,32
420354ca:	00279613          	slli	a2,a5,0x2
420354ce:	01010c13          	addi	s8,sp,16
420354d2:	9c5e                	add	s8,s8,s7
420354d4:	9652                	add	a2,a2,s4
420354d6:	00190b93          	addi	s7,s2,1
420354da:	41f48cb3          	sub	s9,s1,t6
420354de:	01f48763          	beq	s1,t6,420354ec <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0xce>
420354e2:	01962023          	sw	s9,0(a2)
420354e6:	ff2c0623          	sb	s2,-20(s8)
420354ea:	0785                	addi	a5,a5,1
420354ec:	00472f83          	lw	t6,4(a4)
420354f0:	01010c93          	addi	s9,sp,16
420354f4:	00279613          	slli	a2,a5,0x2
420354f8:	02078c13          	addi	s8,a5,32
420354fc:	9c66                	add	s8,s8,s9
420354fe:	0909                	addi	s2,s2,2
42035500:	9652                	add	a2,a2,s4
42035502:	409f8cb3          	sub	s9,t6,s1
42035506:	009f8763          	beq	t6,s1,42035514 <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0xf6>
4203550a:	01962023          	sw	s9,0(a2)
4203550e:	ff7c0623          	sb	s7,-20(s8)
42035512:	0785                	addi	a5,a5,1
42035514:	0721                	addi	a4,a4,8
42035516:	fb6917e3          	bne	s2,s6,420354c4 <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0xa6>
4203551a:	fff28713          	addi	a4,t0,-1
4203551e:	070e                	slli	a4,a4,0x3
42035520:	00291613          	slli	a2,s2,0x2
42035524:	977a                	add	a4,a4,t5
42035526:	967a                	add	a2,a2,t5
42035528:	00072f83          	lw	t6,0(a4)
4203552c:	4218                	lw	a4,0(a2)
4203552e:	41f702b3          	sub	t0,a4,t6
42035532:	01f70c63          	beq	a4,t6,4203554a <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x12c>
42035536:	00279613          	slli	a2,a5,0x2
4203553a:	960a                	add	a2,a2,sp
4203553c:	02562023          	sw	t0,32(a2)
42035540:	00278633          	add	a2,a5,sp
42035544:	01260e23          	sb	s2,28(a2)
42035548:	0785                	addi	a5,a5,1
4203554a:	008afa63          	bgeu	s5,s0,4203555e <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x140>
4203554e:	002a9613          	slli	a2,s5,0x2
42035552:	967a                	add	a2,a2,t5
42035554:	4210                	lw	a2,0(a2)
42035556:	40e60fb3          	sub	t6,a2,a4
4203555a:	3ae61263          	bne	a2,a4,420358fe <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x4e0>
4203555e:	fff40793          	addi	a5,s0,-1
42035562:	078a                	slli	a5,a5,0x2
42035564:	9f3e                	add	t5,t5,a5
42035566:	000f2603          	lw	a2,0(t5)
4203556a:	3fc91fb7          	lui	t6,0x3fc91
4203556e:	050e                	slli	a0,a0,0x3
42035570:	2ecf8f93          	addi	t6,t6,748 # 3fc912ec <_ZN12_GLOBAL__N_1L13samplesBufferE>
42035574:	8f42                	mv	t5,a6
42035576:	fff80493          	addi	s1,a6,-1
4203557a:	4701                	li	a4,0
4203557c:	4781                	li	a5,0
4203557e:	00a4d293          	srli	t0,s1,0xa
42035582:	92aa                	add	t0,t0,a0
42035584:	028a                	slli	t0,t0,0x2
42035586:	92fe                	add	t0,t0,t6
42035588:	0002a283          	lw	t0,0(t0)
4203558c:	3ff4f913          	andi	s2,s1,1023
42035590:	090a                	slli	s2,s2,0x2
42035592:	92ca                	add	t0,t0,s2
42035594:	000e2a03          	lw	s4,0(t3)
42035598:	0002a283          	lw	t0,0(t0)
4203559c:	0e11                	addi	t3,t3,4
4203559e:	14fd                	addi	s1,s1,-1
420355a0:	03428933          	mul	s2,t0,s4
420355a4:	034292b3          	mulh	t0,t0,s4
420355a8:	993a                	add	s2,s2,a4
420355aa:	00e93a33          	sltu	s4,s2,a4
420355ae:	874a                	mv	a4,s2
420355b0:	92be                	add	t0,t0,a5
420355b2:	005a07b3          	add	a5,s4,t0
420355b6:	fdc314e3          	bne	t1,t3,4203557e <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x160>
420355ba:	34b87b63          	bgeu	a6,a1,42035910 <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x4f2>
420355be:	487d                	li	a6,31
420355c0:	413804b3          	sub	s1,a6,s3
420355c4:	c426                	sw	s1,8(sp)
420355c6:	01d14483          	lbu	s1,29(sp)
420355ca:	01c14c03          	lbu	s8,28(sp)
420355ce:	5902                	lw	s2,32(sp)
420355d0:	c026                	sw	s1,0(sp)
420355d2:	01e14483          	lbu	s1,30(sp)
420355d6:	5a12                	lw	s4,36(sp)
420355d8:	5b22                	lw	s6,40(sp)
420355da:	c226                	sw	s1,4(sp)
420355dc:	01f14483          	lbu	s1,31(sp)
420355e0:	5cb2                	lw	s9,44(sp)
420355e2:	da6a                	sw	s10,52(sp)
420355e4:	c626                	sw	s1,12(sp)
420355e6:	d86e                	sw	s11,48(sp)
420355e8:	40700d33          	neg	s10,t2
420355ec:	fe098493          	addi	s1,s3,-32
420355f0:	41f3da93          	srai	s5,t2,0x1f
420355f4:	4b85                	li	s7,1
420355f6:	00af5813          	srli	a6,t5,0xa
420355fa:	982a                	add	a6,a6,a0
420355fc:	080a                	slli	a6,a6,0x2
420355fe:	987e                	add	a6,a6,t6
42035600:	00082303          	lw	t1,0(a6)
42035604:	3fff7813          	andi	a6,t5,1023
42035608:	080a                	slli	a6,a6,0x2
4203560a:	9342                	add	t1,t1,a6
4203560c:	00032e03          	lw	t3,0(t1)
42035610:	41fe5293          	srai	t0,t3,0x1f
42035614:	2804c063          	bltz	s1,42035894 <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x476>
42035618:	4097d833          	sra	a6,a5,s1
4203561c:	41f7dd93          	srai	s11,a5,0x1f
42035620:	9872                	add	a6,a6,t3
42035622:	92ee                	add	t0,t0,s11
42035624:	01c83e33          	sltu	t3,a6,t3
42035628:	9e16                	add	t3,t3,t0
4203562a:	00082293          	slti	t0,a6,0
4203562e:	92f2                	add	t0,t0,t3
42035630:	18029063          	bnez	t0,420357b0 <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x392>
42035634:	01032023          	sw	a6,0(t1)
42035638:	001f0293          	addi	t0,t5,1
4203563c:	16b28f63          	beq	t0,a1,420357ba <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x39c>
42035640:	40828333          	sub	t1,t0,s0
42035644:	137d                	addi	t1,t1,-1
42035646:	00a35d93          	srli	s11,t1,0xa
4203564a:	9daa                	add	s11,s11,a0
4203564c:	0d8a                	slli	s11,s11,0x2
4203564e:	9dfe                	add	s11,s11,t6
42035650:	000dad83          	lw	s11,0(s11)
42035654:	3ff37313          	andi	t1,t1,1023
42035658:	030a                	slli	t1,t1,0x2
4203565a:	9d9a                	add	s11,s11,t1
4203565c:	000da303          	lw	t1,0(s11)
42035660:	00d8fa63          	bgeu	a7,a3,42035674 <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x256>
42035664:	00e03db3          	snez	s11,a4
42035668:	40f007b3          	neg	a5,a5
4203566c:	41b787b3          	sub	a5,a5,s11
42035670:	40e00733          	neg	a4,a4
42035674:	41f35d93          	srai	s11,t1,0x1f
42035678:	22760963          	beq	a2,t2,420358aa <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x48c>
4203567c:	26cd0163          	beq	s10,a2,420358de <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x4c0>
42035680:	030a8db3          	mul	s11,s5,a6
42035684:	027e0e33          	mul	t3,t3,t2
42035688:	9e6e                	add	t3,t3,s11
4203568a:	02783db3          	mulhu	s11,a6,t2
4203568e:	02780833          	mul	a6,a6,t2
42035692:	9df2                	add	s11,s11,t3
42035694:	02661e33          	mulh	t3,a2,t1
42035698:	02660333          	mul	t1,a2,t1
4203569c:	41cd8e33          	sub	t3,s11,t3
420356a0:	40680333          	sub	t1,a6,t1
420356a4:	00683833          	sltu	a6,a6,t1
420356a8:	410e0833          	sub	a6,t3,a6
420356ac:	933a                	add	t1,t1,a4
420356ae:	00e33733          	sltu	a4,t1,a4
420356b2:	983e                	add	a6,a6,a5
420356b4:	010707b3          	add	a5,a4,a6
420356b8:	871a                	mv	a4,t1
420356ba:	0e0e8563          	beqz	t4,420357a4 <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x386>
420356be:	418f0333          	sub	t1,t5,s8
420356c2:	00a35813          	srli	a6,t1,0xa
420356c6:	982a                	add	a6,a6,a0
420356c8:	080a                	slli	a6,a6,0x2
420356ca:	987e                	add	a6,a6,t6
420356cc:	00082803          	lw	a6,0(a6)
420356d0:	3ff37313          	andi	t1,t1,1023
420356d4:	030a                	slli	t1,t1,0x2
420356d6:	981a                	add	a6,a6,t1
420356d8:	00082803          	lw	a6,0(a6)
420356dc:	03090333          	mul	t1,s2,a6
420356e0:	03091833          	mulh	a6,s2,a6
420356e4:	933a                	add	t1,t1,a4
420356e6:	00e33e33          	sltu	t3,t1,a4
420356ea:	871a                	mv	a4,t1
420356ec:	983e                	add	a6,a6,a5
420356ee:	010e07b3          	add	a5,t3,a6
420356f2:	0b7e8963          	beq	t4,s7,420357a4 <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x386>
420356f6:	4802                	lw	a6,0(sp)
420356f8:	410f0333          	sub	t1,t5,a6
420356fc:	00a35813          	srli	a6,t1,0xa
42035700:	982a                	add	a6,a6,a0
42035702:	080a                	slli	a6,a6,0x2
42035704:	987e                	add	a6,a6,t6
42035706:	00082803          	lw	a6,0(a6)
4203570a:	3ff37313          	andi	t1,t1,1023
4203570e:	030a                	slli	t1,t1,0x2
42035710:	981a                	add	a6,a6,t1
42035712:	00082803          	lw	a6,0(a6)
42035716:	030a0333          	mul	t1,s4,a6
4203571a:	030a1833          	mulh	a6,s4,a6
4203571e:	933a                	add	t1,t1,a4
42035720:	00e33e33          	sltu	t3,t1,a4
42035724:	871a                	mv	a4,t1
42035726:	983e                	add	a6,a6,a5
42035728:	010e07b3          	add	a5,t3,a6
4203572c:	4809                	li	a6,2
4203572e:	070e8b63          	beq	t4,a6,420357a4 <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x386>
42035732:	4812                	lw	a6,4(sp)
42035734:	410f0333          	sub	t1,t5,a6
42035738:	00a35813          	srli	a6,t1,0xa
4203573c:	982a                	add	a6,a6,a0
4203573e:	080a                	slli	a6,a6,0x2
42035740:	987e                	add	a6,a6,t6
42035742:	00082803          	lw	a6,0(a6)
42035746:	3ff37313          	andi	t1,t1,1023
4203574a:	030a                	slli	t1,t1,0x2
4203574c:	981a                	add	a6,a6,t1
4203574e:	00082803          	lw	a6,0(a6)
42035752:	030b0333          	mul	t1,s6,a6
42035756:	030b1833          	mulh	a6,s6,a6
4203575a:	933a                	add	t1,t1,a4
4203575c:	00e33e33          	sltu	t3,t1,a4
42035760:	871a                	mv	a4,t1
42035762:	983e                	add	a6,a6,a5
42035764:	010e07b3          	add	a5,t3,a6
42035768:	4811                	li	a6,4
4203576a:	030e9d63          	bne	t4,a6,420357a4 <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x386>
4203576e:	4832                	lw	a6,12(sp)
42035770:	410f0f33          	sub	t5,t5,a6
42035774:	00af5813          	srli	a6,t5,0xa
42035778:	982a                	add	a6,a6,a0
4203577a:	080a                	slli	a6,a6,0x2
4203577c:	987e                	add	a6,a6,t6
4203577e:	00082803          	lw	a6,0(a6)
42035782:	3fff7f13          	andi	t5,t5,1023
42035786:	0f0a                	slli	t5,t5,0x2
42035788:	987a                	add	a6,a6,t5
4203578a:	00082803          	lw	a6,0(a6)
4203578e:	030c8333          	mul	t1,s9,a6
42035792:	030c9833          	mulh	a6,s9,a6
42035796:	933a                	add	t1,t1,a4
42035798:	00e33e33          	sltu	t3,t1,a4
4203579c:	871a                	mv	a4,t1
4203579e:	983e                	add	a6,a6,a5
420357a0:	010e07b3          	add	a5,t3,a6
420357a4:	00b2fb63          	bgeu	t0,a1,420357ba <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x39c>
420357a8:	8f16                	mv	t5,t0
420357aa:	b5b1                	j	420355f6 <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x1d8>
420357ac:	883e                	mv	a6,a5
420357ae:	b179                	j	4203543c <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x1e>
420357b0:	3fc957b7          	lui	a5,0x3fc95
420357b4:	574d                	li	a4,-13
420357b6:	c2e78823          	sb	a4,-976(a5) # 3fc94c30 <m_readError>
420357ba:	44e6                	lw	s1,88(sp)
420357bc:	4956                	lw	s2,84(sp)
420357be:	4a36                	lw	s4,76(sp)
420357c0:	4aa6                	lw	s5,72(sp)
420357c2:	4b16                	lw	s6,68(sp)
420357c4:	4b86                	lw	s7,64(sp)
420357c6:	5c72                	lw	s8,60(sp)
420357c8:	5ce2                	lw	s9,56(sp)
420357ca:	5d52                	lw	s10,52(sp)
420357cc:	5dc2                	lw	s11,48(sp)
420357ce:	4476                	lw	s0,92(sp)
420357d0:	49c6                	lw	s3,80(sp)
420357d2:	4505                	li	a0,1
420357d4:	6125                	addi	sp,sp,96
420357d6:	8082                	ret
420357d8:	4501                	li	a0,0
420357da:	8082                	ret
420357dc:	4476                	lw	s0,92(sp)
420357de:	49c6                	lw	s3,80(sp)
420357e0:	4501                	li	a0,0
420357e2:	6125                	addi	sp,sp,96
420357e4:	8082                	ret
420357e6:	861e                	mv	a2,t2
420357e8:	4905                	li	s2,1
420357ea:	4781                	li	a5,0
420357ec:	02010a13          	addi	s4,sp,32
420357f0:	4304                	lw	s1,0(a4)
420357f2:	02078b93          	addi	s7,a5,32
420357f6:	00279f93          	slli	t6,a5,0x2
420357fa:	01010c13          	addi	s8,sp,16
420357fe:	9626                	add	a2,a2,s1
42035800:	9c5e                	add	s8,s8,s7
42035802:	9fd2                	add	t6,t6,s4
42035804:	00190b93          	addi	s7,s2,1
42035808:	c611                	beqz	a2,42035814 <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x3f6>
4203580a:	00cfa023          	sw	a2,0(t6)
4203580e:	ff2c0623          	sb	s2,-20(s8)
42035812:	0785                	addi	a5,a5,1
42035814:	4350                	lw	a2,4(a4)
42035816:	00279f93          	slli	t6,a5,0x2
4203581a:	02078c13          	addi	s8,a5,32
4203581e:	01010c93          	addi	s9,sp,16
42035822:	94b2                	add	s1,s1,a2
42035824:	9c66                	add	s8,s8,s9
42035826:	9fd2                	add	t6,t6,s4
42035828:	c491                	beqz	s1,42035834 <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x416>
4203582a:	009fa023          	sw	s1,0(t6)
4203582e:	ff7c0623          	sb	s7,-20(s8)
42035832:	0785                	addi	a5,a5,1
42035834:	0909                	addi	s2,s2,2
42035836:	0721                	addi	a4,a4,8
42035838:	fb691ce3          	bne	s2,s6,420357f0 <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x3d2>
4203583c:	fff28713          	addi	a4,t0,-1
42035840:	070e                	slli	a4,a4,0x3
42035842:	00291613          	slli	a2,s2,0x2
42035846:	977a                	add	a4,a4,t5
42035848:	967a                	add	a2,a2,t5
4203584a:	4318                	lw	a4,0(a4)
4203584c:	4210                	lw	a2,0(a2)
4203584e:	9732                	add	a4,a4,a2
42035850:	cb19                	beqz	a4,42035866 <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x448>
42035852:	00279f93          	slli	t6,a5,0x2
42035856:	9f8a                	add	t6,t6,sp
42035858:	02efa023          	sw	a4,32(t6)
4203585c:	00278733          	add	a4,a5,sp
42035860:	01270e23          	sb	s2,28(a4)
42035864:	0785                	addi	a5,a5,1
42035866:	008aff63          	bgeu	s5,s0,42035884 <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x466>
4203586a:	002a9713          	slli	a4,s5,0x2
4203586e:	977a                	add	a4,a4,t5
42035870:	4318                	lw	a4,0(a4)
42035872:	963a                	add	a2,a2,a4
42035874:	ca01                	beqz	a2,42035884 <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x466>
42035876:	00279713          	slli	a4,a5,0x2
4203587a:	970a                	add	a4,a4,sp
4203587c:	978a                	add	a5,a5,sp
4203587e:	d310                	sw	a2,32(a4)
42035880:	01578e23          	sb	s5,28(a5)
42035884:	fff40793          	addi	a5,s0,-1
42035888:	078a                	slli	a5,a5,0x2
4203588a:	97fa                	add	a5,a5,t5
4203588c:	4390                	lw	a2,0(a5)
4203588e:	40c00633          	neg	a2,a2
42035892:	b9e1                	j	4203556a <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x14c>
42035894:	4822                	lw	a6,8(sp)
42035896:	00179d93          	slli	s11,a5,0x1
4203589a:	010d9db3          	sll	s11,s11,a6
4203589e:	01375833          	srl	a6,a4,s3
420358a2:	986e                	add	a6,a6,s11
420358a4:	4137ddb3          	sra	s11,a5,s3
420358a8:	bba5                	j	42035620 <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x202>
420358aa:	40680333          	sub	t1,a6,t1
420358ae:	00683833          	sltu	a6,a6,t1
420358b2:	41be0db3          	sub	s11,t3,s11
420358b6:	410d8db3          	sub	s11,s11,a6
420358ba:	02cd8db3          	mul	s11,s11,a2
420358be:	026a8833          	mul	a6,s5,t1
420358c2:	02c33e33          	mulhu	t3,t1,a2
420358c6:	986e                	add	a6,a6,s11
420358c8:	02c30333          	mul	t1,t1,a2
420358cc:	9872                	add	a6,a6,t3
420358ce:	933a                	add	t1,t1,a4
420358d0:	00e33733          	sltu	a4,t1,a4
420358d4:	983e                	add	a6,a6,a5
420358d6:	010707b3          	add	a5,a4,a6
420358da:	871a                	mv	a4,t1
420358dc:	bbf9                	j	420356ba <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x29c>
420358de:	9342                	add	t1,t1,a6
420358e0:	9df2                	add	s11,s11,t3
420358e2:	01033833          	sltu	a6,t1,a6
420358e6:	986e                	add	a6,a6,s11
420358e8:	02780e33          	mul	t3,a6,t2
420358ec:	026a8833          	mul	a6,s5,t1
420358f0:	02733db3          	mulhu	s11,t1,t2
420358f4:	9872                	add	a6,a6,t3
420358f6:	02730333          	mul	t1,t1,t2
420358fa:	986e                	add	a6,a6,s11
420358fc:	bfc9                	j	420358ce <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x4b0>
420358fe:	00279713          	slli	a4,a5,0x2
42035902:	970a                	add	a4,a4,sp
42035904:	978a                	add	a5,a5,sp
42035906:	03f72023          	sw	t6,32(a4)
4203590a:	01578e23          	sb	s5,28(a5)
4203590e:	b981                	j	4203555e <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x140>
42035910:	44e6                	lw	s1,88(sp)
42035912:	4956                	lw	s2,84(sp)
42035914:	4a36                	lw	s4,76(sp)
42035916:	4aa6                	lw	s5,72(sp)
42035918:	4b16                	lw	s6,68(sp)
4203591a:	4b86                	lw	s7,64(sp)
4203591c:	5c72                	lw	s8,60(sp)
4203591e:	5ce2                	lw	s9,56(sp)
42035920:	b57d                	j	420357ce <_ZN12_GLOBAL__N_1L28restoreSparseDeltaPredictionEhhj+0x3b0>
