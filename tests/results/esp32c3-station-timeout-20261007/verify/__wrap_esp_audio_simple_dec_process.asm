
idf\esp32c3-oled-native\build-connect-retry\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026624 <__wrap_esp_audio_simple_dec_process>:
42026624:	0015b793          	seqz	a5,a1
42026628:	00163713          	seqz	a4,a2
4202662c:	8fd9                	or	a5,a5,a4
4202662e:	ebe9                	bnez	a5,42026700 <__wrap_esp_audio_simple_dec_process+0xdc>
42026630:	c961                	beqz	a0,42026700 <__wrap_esp_audio_simple_dec_process+0xdc>
42026632:	419c                	lw	a5,0(a1)
42026634:	c7e1                	beqz	a5,420266fc <__wrap_esp_audio_simple_dec_process+0xd8>
42026636:	5558                	lw	a4,44(a0)
42026638:	204747b7          	lui	a5,0x20474
4202663c:	74f78793          	addi	a5,a5,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
42026640:	0af71c63          	bne	a4,a5,420266f8 <__wrap_esp_audio_simple_dec_process+0xd4>
42026644:	7139                	addi	sp,sp,-64
42026646:	03054683          	lbu	a3,48(a0)
4202664a:	de06                	sw	ra,60(sp)
4202664c:	0005a623          	sw	zero,12(a1)
42026650:	00062623          	sw	zero,12(a2)
42026654:	872a                	mv	a4,a0
42026656:	87ae                	mv	a5,a1
42026658:	eab1                	bnez	a3,420266ac <__wrap_esp_audio_simple_dec_process+0x88>
4202665a:	43d4                	lw	a3,4(a5)
4202665c:	c6a1                	beqz	a3,420266a4 <__wrap_esp_audio_simple_dec_process+0x80>
4202665e:	0087c583          	lbu	a1,8(a5)
42026662:	edd5                	bnez	a1,4202671e <__wrap_esp_audio_simple_dec_process+0xfa>
42026664:	4805                	li	a6,1
42026666:	0b068263          	beq	a3,a6,4202670a <__wrap_esp_audio_simple_dec_process+0xe6>
4202666a:	0007ae83          	lw	t4,0(a5)
4202666e:	0087ae03          	lw	t3,8(a5)
42026672:	00c7a303          	lw	t1,12(a5)
42026676:	0107a883          	lw	a7,16(a5)
4202667a:	16fd                	addi	a3,a3,-1
4202667c:	086c                	addi	a1,sp,28
4202667e:	853a                	mv	a0,a4
42026680:	c23e                	sw	a5,4(sp)
42026682:	d036                	sw	a3,32(sp)
42026684:	c43a                	sw	a4,8(sp)
42026686:	ce76                	sw	t4,28(sp)
42026688:	d272                	sw	t3,36(sp)
4202668a:	d41a                	sw	t1,40(sp)
4202668c:	d646                	sw	a7,44(sp)
4202668e:	d71ff0ef          	jal	420263fe <process_checked>
42026692:	56a2                	lw	a3,40(sp)
42026694:	4792                	lw	a5,4(sp)
42026696:	c7d4                	sw	a3,12(a5)
42026698:	e519                	bnez	a0,420266a6 <__wrap_esp_audio_simple_dec_process+0x82>
4202669a:	5602                	lw	a2,32(sp)
4202669c:	4722                	lw	a4,8(sp)
4202669e:	4805                	li	a6,1
420266a0:	08c68563          	beq	a3,a2,4202672a <__wrap_esp_audio_simple_dec_process+0x106>
420266a4:	4501                	li	a0,0
420266a6:	50f2                	lw	ra,60(sp)
420266a8:	6121                	addi	sp,sp,64
420266aa:	8082                	ret
420266ac:	0085c683          	lbu	a3,8(a1)
420266b0:	03150513          	addi	a0,a0,49
420266b4:	4585                	li	a1,1
420266b6:	4801                	li	a6,0
420266b8:	4881                	li	a7,0
420266ba:	d242                	sw	a6,36(sp)
420266bc:	d446                	sw	a7,40(sp)
420266be:	ce2a                	sw	a0,28(sp)
420266c0:	d02e                	sw	a1,32(sp)
420266c2:	c681                	beqz	a3,420266ca <__wrap_esp_audio_simple_dec_process+0xa6>
420266c4:	43d4                	lw	a3,4(a5)
420266c6:	0016b693          	seqz	a3,a3
420266ca:	02d10223          	sb	a3,36(sp)
420266ce:	4b94                	lw	a3,16(a5)
420266d0:	853a                	mv	a0,a4
420266d2:	086c                	addi	a1,sp,28
420266d4:	c63e                	sw	a5,12(sp)
420266d6:	c432                	sw	a2,8(sp)
420266d8:	c23a                	sw	a4,4(sp)
420266da:	d636                	sw	a3,44(sp)
420266dc:	d23ff0ef          	jal	420263fe <process_checked>
420266e0:	56a2                	lw	a3,40(sp)
420266e2:	4712                	lw	a4,4(sp)
420266e4:	4622                	lw	a2,8(sp)
420266e6:	47b2                	lw	a5,12(sp)
420266e8:	ee91                	bnez	a3,42026704 <__wrap_esp_audio_simple_dec_process+0xe0>
420266ea:	fd55                	bnez	a0,420266a6 <__wrap_esp_audio_simple_dec_process+0x82>
420266ec:	4654                	lw	a3,12(a2)
420266ee:	fec5                	bnez	a3,420266a6 <__wrap_esp_audio_simple_dec_process+0x82>
420266f0:	03074683          	lbu	a3,48(a4)
420266f4:	d2bd                	beqz	a3,4202665a <__wrap_esp_audio_simple_dec_process+0x36>
420266f6:	bf45                	j	420266a6 <__wrap_esp_audio_simple_dec_process+0x82>
420266f8:	5ba1206f          	j	42038cb2 <esp_audio_simple_dec_process>
420266fc:	41dc                	lw	a5,4(a1)
420266fe:	df85                	beqz	a5,42026636 <__wrap_esp_audio_simple_dec_process+0x12>
42026700:	556d                	li	a0,-5
42026702:	8082                	ret
42026704:	02070823          	sb	zero,48(a4)
42026708:	b7cd                	j	420266ea <__wrap_esp_audio_simple_dec_process+0xc6>
4202670a:	4390                	lw	a2,0(a5)
4202670c:	4501                	li	a0,0
4202670e:	00064603          	lbu	a2,0(a2)
42026712:	02d70823          	sb	a3,48(a4)
42026716:	02c708a3          	sb	a2,49(a4)
4202671a:	c7d4                	sw	a3,12(a5)
4202671c:	b769                	j	420266a6 <__wrap_esp_audio_simple_dec_process+0x82>
4202671e:	50f2                	lw	ra,60(sp)
42026720:	85be                	mv	a1,a5
42026722:	853a                	mv	a0,a4
42026724:	6121                	addi	sp,sp,64
42026726:	cd9ff06f          	j	420263fe <process_checked>
4202672a:	4390                	lw	a2,0(a5)
4202672c:	010685b3          	add	a1,a3,a6
42026730:	4501                	li	a0,0
42026732:	96b2                	add	a3,a3,a2
42026734:	0006c683          	lbu	a3,0(a3)
42026738:	03070823          	sb	a6,48(a4)
4202673c:	02d708a3          	sb	a3,49(a4)
42026740:	c7cc                	sw	a1,12(a5)
42026742:	b795                	j	420266a6 <__wrap_esp_audio_simple_dec_process+0x82>
