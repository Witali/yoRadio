
idf\esp32c3-oled-native\build-flac-predictor\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420263b6 <__wrap_esp_audio_simple_dec_process>:
420263b6:	0015b793          	seqz	a5,a1
420263ba:	00163713          	seqz	a4,a2
420263be:	8fd9                	or	a5,a5,a4
420263c0:	ebe9                	bnez	a5,42026492 <__wrap_esp_audio_simple_dec_process+0xdc>
420263c2:	c961                	beqz	a0,42026492 <__wrap_esp_audio_simple_dec_process+0xdc>
420263c4:	419c                	lw	a5,0(a1)
420263c6:	c7e1                	beqz	a5,4202648e <__wrap_esp_audio_simple_dec_process+0xd8>
420263c8:	5558                	lw	a4,44(a0)
420263ca:	204747b7          	lui	a5,0x20474
420263ce:	74f78793          	addi	a5,a5,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
420263d2:	0af71c63          	bne	a4,a5,4202648a <__wrap_esp_audio_simple_dec_process+0xd4>
420263d6:	7139                	addi	sp,sp,-64
420263d8:	03054683          	lbu	a3,48(a0)
420263dc:	de06                	sw	ra,60(sp)
420263de:	0005a623          	sw	zero,12(a1)
420263e2:	00062623          	sw	zero,12(a2)
420263e6:	872a                	mv	a4,a0
420263e8:	87ae                	mv	a5,a1
420263ea:	eab1                	bnez	a3,4202643e <__wrap_esp_audio_simple_dec_process+0x88>
420263ec:	43d4                	lw	a3,4(a5)
420263ee:	c6a1                	beqz	a3,42026436 <__wrap_esp_audio_simple_dec_process+0x80>
420263f0:	0087c583          	lbu	a1,8(a5)
420263f4:	edd5                	bnez	a1,420264b0 <__wrap_esp_audio_simple_dec_process+0xfa>
420263f6:	4805                	li	a6,1
420263f8:	0b068263          	beq	a3,a6,4202649c <__wrap_esp_audio_simple_dec_process+0xe6>
420263fc:	0007ae83          	lw	t4,0(a5)
42026400:	0087ae03          	lw	t3,8(a5)
42026404:	00c7a303          	lw	t1,12(a5)
42026408:	0107a883          	lw	a7,16(a5)
4202640c:	16fd                	addi	a3,a3,-1
4202640e:	086c                	addi	a1,sp,28
42026410:	853a                	mv	a0,a4
42026412:	c23e                	sw	a5,4(sp)
42026414:	d036                	sw	a3,32(sp)
42026416:	c43a                	sw	a4,8(sp)
42026418:	ce76                	sw	t4,28(sp)
4202641a:	d272                	sw	t3,36(sp)
4202641c:	d41a                	sw	t1,40(sp)
4202641e:	d646                	sw	a7,44(sp)
42026420:	d71ff0ef          	jal	42026190 <process_checked>
42026424:	56a2                	lw	a3,40(sp)
42026426:	4792                	lw	a5,4(sp)
42026428:	c7d4                	sw	a3,12(a5)
4202642a:	e519                	bnez	a0,42026438 <__wrap_esp_audio_simple_dec_process+0x82>
4202642c:	5602                	lw	a2,32(sp)
4202642e:	4722                	lw	a4,8(sp)
42026430:	4805                	li	a6,1
42026432:	08c68563          	beq	a3,a2,420264bc <__wrap_esp_audio_simple_dec_process+0x106>
42026436:	4501                	li	a0,0
42026438:	50f2                	lw	ra,60(sp)
4202643a:	6121                	addi	sp,sp,64
4202643c:	8082                	ret
4202643e:	0085c683          	lbu	a3,8(a1)
42026442:	03150513          	addi	a0,a0,49
42026446:	4585                	li	a1,1
42026448:	4801                	li	a6,0
4202644a:	4881                	li	a7,0
4202644c:	d242                	sw	a6,36(sp)
4202644e:	d446                	sw	a7,40(sp)
42026450:	ce2a                	sw	a0,28(sp)
42026452:	d02e                	sw	a1,32(sp)
42026454:	c681                	beqz	a3,4202645c <__wrap_esp_audio_simple_dec_process+0xa6>
42026456:	43d4                	lw	a3,4(a5)
42026458:	0016b693          	seqz	a3,a3
4202645c:	02d10223          	sb	a3,36(sp)
42026460:	4b94                	lw	a3,16(a5)
42026462:	853a                	mv	a0,a4
42026464:	086c                	addi	a1,sp,28
42026466:	c63e                	sw	a5,12(sp)
42026468:	c432                	sw	a2,8(sp)
4202646a:	c23a                	sw	a4,4(sp)
4202646c:	d636                	sw	a3,44(sp)
4202646e:	d23ff0ef          	jal	42026190 <process_checked>
42026472:	56a2                	lw	a3,40(sp)
42026474:	4712                	lw	a4,4(sp)
42026476:	4622                	lw	a2,8(sp)
42026478:	47b2                	lw	a5,12(sp)
4202647a:	ee91                	bnez	a3,42026496 <__wrap_esp_audio_simple_dec_process+0xe0>
4202647c:	fd55                	bnez	a0,42026438 <__wrap_esp_audio_simple_dec_process+0x82>
4202647e:	4654                	lw	a3,12(a2)
42026480:	fec5                	bnez	a3,42026438 <__wrap_esp_audio_simple_dec_process+0x82>
42026482:	03074683          	lbu	a3,48(a4)
42026486:	d2bd                	beqz	a3,420263ec <__wrap_esp_audio_simple_dec_process+0x36>
42026488:	bf45                	j	42026438 <__wrap_esp_audio_simple_dec_process+0x82>
4202648a:	5bc1206f          	j	42038a46 <esp_audio_simple_dec_process>
4202648e:	41dc                	lw	a5,4(a1)
42026490:	df85                	beqz	a5,420263c8 <__wrap_esp_audio_simple_dec_process+0x12>
42026492:	556d                	li	a0,-5
42026494:	8082                	ret
42026496:	02070823          	sb	zero,48(a4)
4202649a:	b7cd                	j	4202647c <__wrap_esp_audio_simple_dec_process+0xc6>
4202649c:	4390                	lw	a2,0(a5)
4202649e:	4501                	li	a0,0
420264a0:	00064603          	lbu	a2,0(a2)
420264a4:	02d70823          	sb	a3,48(a4)
420264a8:	02c708a3          	sb	a2,49(a4)
420264ac:	c7d4                	sw	a3,12(a5)
420264ae:	b769                	j	42026438 <__wrap_esp_audio_simple_dec_process+0x82>
420264b0:	50f2                	lw	ra,60(sp)
420264b2:	85be                	mv	a1,a5
420264b4:	853a                	mv	a0,a4
420264b6:	6121                	addi	sp,sp,64
420264b8:	cd9ff06f          	j	42026190 <process_checked>
420264bc:	4390                	lw	a2,0(a5)
420264be:	010685b3          	add	a1,a3,a6
420264c2:	4501                	li	a0,0
420264c4:	96b2                	add	a3,a3,a2
420264c6:	0006c683          	lbu	a3,0(a3)
420264ca:	03070823          	sb	a6,48(a4)
420264ce:	02d708a3          	sb	a3,49(a4)
420264d2:	c7cc                	sw	a1,12(a5)
420264d4:	b795                	j	42026438 <__wrap_esp_audio_simple_dec_process+0x82>
