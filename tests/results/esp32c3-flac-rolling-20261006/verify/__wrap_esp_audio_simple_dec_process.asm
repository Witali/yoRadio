
idf\esp32c3-oled-native\build-flac-predictor\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420263be <__wrap_esp_audio_simple_dec_process>:
420263be:	0015b793          	seqz	a5,a1
420263c2:	00163713          	seqz	a4,a2
420263c6:	8fd9                	or	a5,a5,a4
420263c8:	ebe9                	bnez	a5,4202649a <__wrap_esp_audio_simple_dec_process+0xdc>
420263ca:	c961                	beqz	a0,4202649a <__wrap_esp_audio_simple_dec_process+0xdc>
420263cc:	419c                	lw	a5,0(a1)
420263ce:	c7e1                	beqz	a5,42026496 <__wrap_esp_audio_simple_dec_process+0xd8>
420263d0:	5558                	lw	a4,44(a0)
420263d2:	204747b7          	lui	a5,0x20474
420263d6:	74f78793          	addi	a5,a5,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
420263da:	0af71c63          	bne	a4,a5,42026492 <__wrap_esp_audio_simple_dec_process+0xd4>
420263de:	7139                	addi	sp,sp,-64
420263e0:	03054683          	lbu	a3,48(a0)
420263e4:	de06                	sw	ra,60(sp)
420263e6:	0005a623          	sw	zero,12(a1)
420263ea:	00062623          	sw	zero,12(a2)
420263ee:	872a                	mv	a4,a0
420263f0:	87ae                	mv	a5,a1
420263f2:	eab1                	bnez	a3,42026446 <__wrap_esp_audio_simple_dec_process+0x88>
420263f4:	43d4                	lw	a3,4(a5)
420263f6:	c6a1                	beqz	a3,4202643e <__wrap_esp_audio_simple_dec_process+0x80>
420263f8:	0087c583          	lbu	a1,8(a5)
420263fc:	edd5                	bnez	a1,420264b8 <__wrap_esp_audio_simple_dec_process+0xfa>
420263fe:	4805                	li	a6,1
42026400:	0b068263          	beq	a3,a6,420264a4 <__wrap_esp_audio_simple_dec_process+0xe6>
42026404:	0007ae83          	lw	t4,0(a5)
42026408:	0087ae03          	lw	t3,8(a5)
4202640c:	00c7a303          	lw	t1,12(a5)
42026410:	0107a883          	lw	a7,16(a5)
42026414:	16fd                	addi	a3,a3,-1
42026416:	086c                	addi	a1,sp,28
42026418:	853a                	mv	a0,a4
4202641a:	c23e                	sw	a5,4(sp)
4202641c:	d036                	sw	a3,32(sp)
4202641e:	c43a                	sw	a4,8(sp)
42026420:	ce76                	sw	t4,28(sp)
42026422:	d272                	sw	t3,36(sp)
42026424:	d41a                	sw	t1,40(sp)
42026426:	d646                	sw	a7,44(sp)
42026428:	d71ff0ef          	jal	42026198 <process_checked>
4202642c:	56a2                	lw	a3,40(sp)
4202642e:	4792                	lw	a5,4(sp)
42026430:	c7d4                	sw	a3,12(a5)
42026432:	e519                	bnez	a0,42026440 <__wrap_esp_audio_simple_dec_process+0x82>
42026434:	5602                	lw	a2,32(sp)
42026436:	4722                	lw	a4,8(sp)
42026438:	4805                	li	a6,1
4202643a:	08c68563          	beq	a3,a2,420264c4 <__wrap_esp_audio_simple_dec_process+0x106>
4202643e:	4501                	li	a0,0
42026440:	50f2                	lw	ra,60(sp)
42026442:	6121                	addi	sp,sp,64
42026444:	8082                	ret
42026446:	0085c683          	lbu	a3,8(a1)
4202644a:	03150513          	addi	a0,a0,49
4202644e:	4585                	li	a1,1
42026450:	4801                	li	a6,0
42026452:	4881                	li	a7,0
42026454:	d242                	sw	a6,36(sp)
42026456:	d446                	sw	a7,40(sp)
42026458:	ce2a                	sw	a0,28(sp)
4202645a:	d02e                	sw	a1,32(sp)
4202645c:	c681                	beqz	a3,42026464 <__wrap_esp_audio_simple_dec_process+0xa6>
4202645e:	43d4                	lw	a3,4(a5)
42026460:	0016b693          	seqz	a3,a3
42026464:	02d10223          	sb	a3,36(sp)
42026468:	4b94                	lw	a3,16(a5)
4202646a:	853a                	mv	a0,a4
4202646c:	086c                	addi	a1,sp,28
4202646e:	c63e                	sw	a5,12(sp)
42026470:	c432                	sw	a2,8(sp)
42026472:	c23a                	sw	a4,4(sp)
42026474:	d636                	sw	a3,44(sp)
42026476:	d23ff0ef          	jal	42026198 <process_checked>
4202647a:	56a2                	lw	a3,40(sp)
4202647c:	4712                	lw	a4,4(sp)
4202647e:	4622                	lw	a2,8(sp)
42026480:	47b2                	lw	a5,12(sp)
42026482:	ee91                	bnez	a3,4202649e <__wrap_esp_audio_simple_dec_process+0xe0>
42026484:	fd55                	bnez	a0,42026440 <__wrap_esp_audio_simple_dec_process+0x82>
42026486:	4654                	lw	a3,12(a2)
42026488:	fec5                	bnez	a3,42026440 <__wrap_esp_audio_simple_dec_process+0x82>
4202648a:	03074683          	lbu	a3,48(a4)
4202648e:	d2bd                	beqz	a3,420263f4 <__wrap_esp_audio_simple_dec_process+0x36>
42026490:	bf45                	j	42026440 <__wrap_esp_audio_simple_dec_process+0x82>
42026492:	18b1206f          	j	42038e1c <esp_audio_simple_dec_process>
42026496:	41dc                	lw	a5,4(a1)
42026498:	df85                	beqz	a5,420263d0 <__wrap_esp_audio_simple_dec_process+0x12>
4202649a:	556d                	li	a0,-5
4202649c:	8082                	ret
4202649e:	02070823          	sb	zero,48(a4)
420264a2:	b7cd                	j	42026484 <__wrap_esp_audio_simple_dec_process+0xc6>
420264a4:	4390                	lw	a2,0(a5)
420264a6:	4501                	li	a0,0
420264a8:	00064603          	lbu	a2,0(a2)
420264ac:	02d70823          	sb	a3,48(a4)
420264b0:	02c708a3          	sb	a2,49(a4)
420264b4:	c7d4                	sw	a3,12(a5)
420264b6:	b769                	j	42026440 <__wrap_esp_audio_simple_dec_process+0x82>
420264b8:	50f2                	lw	ra,60(sp)
420264ba:	85be                	mv	a1,a5
420264bc:	853a                	mv	a0,a4
420264be:	6121                	addi	sp,sp,64
420264c0:	cd9ff06f          	j	42026198 <process_checked>
420264c4:	4390                	lw	a2,0(a5)
420264c6:	010685b3          	add	a1,a3,a6
420264ca:	4501                	li	a0,0
420264cc:	96b2                	add	a3,a3,a2
420264ce:	0006c683          	lbu	a3,0(a3)
420264d2:	03070823          	sb	a6,48(a4)
420264d6:	02d708a3          	sb	a3,49(a4)
420264da:	c7cc                	sw	a1,12(a5)
420264dc:	b795                	j	42026440 <__wrap_esp_audio_simple_dec_process+0x82>
