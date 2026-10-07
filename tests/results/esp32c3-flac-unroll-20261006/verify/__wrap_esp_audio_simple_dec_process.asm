
idf\esp32c3-oled-native\build-flac-predictor\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4202637a <__wrap_esp_audio_simple_dec_process>:
4202637a:	0015b793          	seqz	a5,a1
4202637e:	00163713          	seqz	a4,a2
42026382:	8fd9                	or	a5,a5,a4
42026384:	ebe9                	bnez	a5,42026456 <__wrap_esp_audio_simple_dec_process+0xdc>
42026386:	c961                	beqz	a0,42026456 <__wrap_esp_audio_simple_dec_process+0xdc>
42026388:	419c                	lw	a5,0(a1)
4202638a:	c7e1                	beqz	a5,42026452 <__wrap_esp_audio_simple_dec_process+0xd8>
4202638c:	5558                	lw	a4,44(a0)
4202638e:	204747b7          	lui	a5,0x20474
42026392:	74f78793          	addi	a5,a5,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
42026396:	0af71c63          	bne	a4,a5,4202644e <__wrap_esp_audio_simple_dec_process+0xd4>
4202639a:	7139                	addi	sp,sp,-64
4202639c:	03054683          	lbu	a3,48(a0)
420263a0:	de06                	sw	ra,60(sp)
420263a2:	0005a623          	sw	zero,12(a1)
420263a6:	00062623          	sw	zero,12(a2)
420263aa:	872a                	mv	a4,a0
420263ac:	87ae                	mv	a5,a1
420263ae:	eab1                	bnez	a3,42026402 <__wrap_esp_audio_simple_dec_process+0x88>
420263b0:	43d4                	lw	a3,4(a5)
420263b2:	c6a1                	beqz	a3,420263fa <__wrap_esp_audio_simple_dec_process+0x80>
420263b4:	0087c583          	lbu	a1,8(a5)
420263b8:	edd5                	bnez	a1,42026474 <__wrap_esp_audio_simple_dec_process+0xfa>
420263ba:	4805                	li	a6,1
420263bc:	0b068263          	beq	a3,a6,42026460 <__wrap_esp_audio_simple_dec_process+0xe6>
420263c0:	0007ae83          	lw	t4,0(a5)
420263c4:	0087ae03          	lw	t3,8(a5)
420263c8:	00c7a303          	lw	t1,12(a5)
420263cc:	0107a883          	lw	a7,16(a5)
420263d0:	16fd                	addi	a3,a3,-1
420263d2:	086c                	addi	a1,sp,28
420263d4:	853a                	mv	a0,a4
420263d6:	c23e                	sw	a5,4(sp)
420263d8:	d036                	sw	a3,32(sp)
420263da:	c43a                	sw	a4,8(sp)
420263dc:	ce76                	sw	t4,28(sp)
420263de:	d272                	sw	t3,36(sp)
420263e0:	d41a                	sw	t1,40(sp)
420263e2:	d646                	sw	a7,44(sp)
420263e4:	d71ff0ef          	jal	42026154 <process_checked>
420263e8:	56a2                	lw	a3,40(sp)
420263ea:	4792                	lw	a5,4(sp)
420263ec:	c7d4                	sw	a3,12(a5)
420263ee:	e519                	bnez	a0,420263fc <__wrap_esp_audio_simple_dec_process+0x82>
420263f0:	5602                	lw	a2,32(sp)
420263f2:	4722                	lw	a4,8(sp)
420263f4:	4805                	li	a6,1
420263f6:	08c68563          	beq	a3,a2,42026480 <__wrap_esp_audio_simple_dec_process+0x106>
420263fa:	4501                	li	a0,0
420263fc:	50f2                	lw	ra,60(sp)
420263fe:	6121                	addi	sp,sp,64
42026400:	8082                	ret
42026402:	0085c683          	lbu	a3,8(a1)
42026406:	03150513          	addi	a0,a0,49
4202640a:	4585                	li	a1,1
4202640c:	4801                	li	a6,0
4202640e:	4881                	li	a7,0
42026410:	d242                	sw	a6,36(sp)
42026412:	d446                	sw	a7,40(sp)
42026414:	ce2a                	sw	a0,28(sp)
42026416:	d02e                	sw	a1,32(sp)
42026418:	c681                	beqz	a3,42026420 <__wrap_esp_audio_simple_dec_process+0xa6>
4202641a:	43d4                	lw	a3,4(a5)
4202641c:	0016b693          	seqz	a3,a3
42026420:	02d10223          	sb	a3,36(sp)
42026424:	4b94                	lw	a3,16(a5)
42026426:	853a                	mv	a0,a4
42026428:	086c                	addi	a1,sp,28
4202642a:	c63e                	sw	a5,12(sp)
4202642c:	c432                	sw	a2,8(sp)
4202642e:	c23a                	sw	a4,4(sp)
42026430:	d636                	sw	a3,44(sp)
42026432:	d23ff0ef          	jal	42026154 <process_checked>
42026436:	56a2                	lw	a3,40(sp)
42026438:	4712                	lw	a4,4(sp)
4202643a:	4622                	lw	a2,8(sp)
4202643c:	47b2                	lw	a5,12(sp)
4202643e:	ee91                	bnez	a3,4202645a <__wrap_esp_audio_simple_dec_process+0xe0>
42026440:	fd55                	bnez	a0,420263fc <__wrap_esp_audio_simple_dec_process+0x82>
42026442:	4654                	lw	a3,12(a2)
42026444:	fec5                	bnez	a3,420263fc <__wrap_esp_audio_simple_dec_process+0x82>
42026446:	03074683          	lbu	a3,48(a4)
4202644a:	d2bd                	beqz	a3,420263b0 <__wrap_esp_audio_simple_dec_process+0x36>
4202644c:	bf45                	j	420263fc <__wrap_esp_audio_simple_dec_process+0x82>
4202644e:	0141206f          	j	42038462 <esp_audio_simple_dec_process>
42026452:	41dc                	lw	a5,4(a1)
42026454:	df85                	beqz	a5,4202638c <__wrap_esp_audio_simple_dec_process+0x12>
42026456:	556d                	li	a0,-5
42026458:	8082                	ret
4202645a:	02070823          	sb	zero,48(a4)
4202645e:	b7cd                	j	42026440 <__wrap_esp_audio_simple_dec_process+0xc6>
42026460:	4390                	lw	a2,0(a5)
42026462:	4501                	li	a0,0
42026464:	00064603          	lbu	a2,0(a2)
42026468:	02d70823          	sb	a3,48(a4)
4202646c:	02c708a3          	sb	a2,49(a4)
42026470:	c7d4                	sw	a3,12(a5)
42026472:	b769                	j	420263fc <__wrap_esp_audio_simple_dec_process+0x82>
42026474:	50f2                	lw	ra,60(sp)
42026476:	85be                	mv	a1,a5
42026478:	853a                	mv	a0,a4
4202647a:	6121                	addi	sp,sp,64
4202647c:	cd9ff06f          	j	42026154 <process_checked>
42026480:	4390                	lw	a2,0(a5)
42026482:	010685b3          	add	a1,a3,a6
42026486:	4501                	li	a0,0
42026488:	96b2                	add	a3,a3,a2
4202648a:	0006c683          	lbu	a3,0(a3)
4202648e:	03070823          	sb	a6,48(a4)
42026492:	02d708a3          	sb	a3,49(a4)
42026496:	c7cc                	sw	a1,12(a5)
42026498:	b795                	j	420263fc <__wrap_esp_audio_simple_dec_process+0x82>
