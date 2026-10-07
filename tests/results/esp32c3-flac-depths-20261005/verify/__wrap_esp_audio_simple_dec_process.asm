
idf\esp32c3-oled-native\build-flac-depths\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026376 <__wrap_esp_audio_simple_dec_process>:
42026376:	0015b793          	seqz	a5,a1
4202637a:	00163713          	seqz	a4,a2
4202637e:	8fd9                	or	a5,a5,a4
42026380:	ebe9                	bnez	a5,42026452 <__wrap_esp_audio_simple_dec_process+0xdc>
42026382:	c961                	beqz	a0,42026452 <__wrap_esp_audio_simple_dec_process+0xdc>
42026384:	419c                	lw	a5,0(a1)
42026386:	c7e1                	beqz	a5,4202644e <__wrap_esp_audio_simple_dec_process+0xd8>
42026388:	5558                	lw	a4,44(a0)
4202638a:	204747b7          	lui	a5,0x20474
4202638e:	74f78793          	addi	a5,a5,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
42026392:	0af71c63          	bne	a4,a5,4202644a <__wrap_esp_audio_simple_dec_process+0xd4>
42026396:	7139                	addi	sp,sp,-64
42026398:	03054683          	lbu	a3,48(a0)
4202639c:	de06                	sw	ra,60(sp)
4202639e:	0005a623          	sw	zero,12(a1)
420263a2:	00062623          	sw	zero,12(a2)
420263a6:	872a                	mv	a4,a0
420263a8:	87ae                	mv	a5,a1
420263aa:	eab1                	bnez	a3,420263fe <__wrap_esp_audio_simple_dec_process+0x88>
420263ac:	43d4                	lw	a3,4(a5)
420263ae:	c6a1                	beqz	a3,420263f6 <__wrap_esp_audio_simple_dec_process+0x80>
420263b0:	0087c583          	lbu	a1,8(a5)
420263b4:	edd5                	bnez	a1,42026470 <__wrap_esp_audio_simple_dec_process+0xfa>
420263b6:	4805                	li	a6,1
420263b8:	0b068263          	beq	a3,a6,4202645c <__wrap_esp_audio_simple_dec_process+0xe6>
420263bc:	0007ae83          	lw	t4,0(a5)
420263c0:	0087ae03          	lw	t3,8(a5)
420263c4:	00c7a303          	lw	t1,12(a5)
420263c8:	0107a883          	lw	a7,16(a5)
420263cc:	16fd                	addi	a3,a3,-1
420263ce:	086c                	addi	a1,sp,28
420263d0:	853a                	mv	a0,a4
420263d2:	c23e                	sw	a5,4(sp)
420263d4:	d036                	sw	a3,32(sp)
420263d6:	c43a                	sw	a4,8(sp)
420263d8:	ce76                	sw	t4,28(sp)
420263da:	d272                	sw	t3,36(sp)
420263dc:	d41a                	sw	t1,40(sp)
420263de:	d646                	sw	a7,44(sp)
420263e0:	d71ff0ef          	jal	42026150 <process_checked>
420263e4:	56a2                	lw	a3,40(sp)
420263e6:	4792                	lw	a5,4(sp)
420263e8:	c7d4                	sw	a3,12(a5)
420263ea:	e519                	bnez	a0,420263f8 <__wrap_esp_audio_simple_dec_process+0x82>
420263ec:	5602                	lw	a2,32(sp)
420263ee:	4722                	lw	a4,8(sp)
420263f0:	4805                	li	a6,1
420263f2:	08c68563          	beq	a3,a2,4202647c <__wrap_esp_audio_simple_dec_process+0x106>
420263f6:	4501                	li	a0,0
420263f8:	50f2                	lw	ra,60(sp)
420263fa:	6121                	addi	sp,sp,64
420263fc:	8082                	ret
420263fe:	0085c683          	lbu	a3,8(a1)
42026402:	03150513          	addi	a0,a0,49
42026406:	4585                	li	a1,1
42026408:	4801                	li	a6,0
4202640a:	4881                	li	a7,0
4202640c:	d242                	sw	a6,36(sp)
4202640e:	d446                	sw	a7,40(sp)
42026410:	ce2a                	sw	a0,28(sp)
42026412:	d02e                	sw	a1,32(sp)
42026414:	c681                	beqz	a3,4202641c <__wrap_esp_audio_simple_dec_process+0xa6>
42026416:	43d4                	lw	a3,4(a5)
42026418:	0016b693          	seqz	a3,a3
4202641c:	02d10223          	sb	a3,36(sp)
42026420:	4b94                	lw	a3,16(a5)
42026422:	853a                	mv	a0,a4
42026424:	086c                	addi	a1,sp,28
42026426:	c63e                	sw	a5,12(sp)
42026428:	c432                	sw	a2,8(sp)
4202642a:	c23a                	sw	a4,4(sp)
4202642c:	d636                	sw	a3,44(sp)
4202642e:	d23ff0ef          	jal	42026150 <process_checked>
42026432:	56a2                	lw	a3,40(sp)
42026434:	4712                	lw	a4,4(sp)
42026436:	4622                	lw	a2,8(sp)
42026438:	47b2                	lw	a5,12(sp)
4202643a:	ee91                	bnez	a3,42026456 <__wrap_esp_audio_simple_dec_process+0xe0>
4202643c:	fd55                	bnez	a0,420263f8 <__wrap_esp_audio_simple_dec_process+0x82>
4202643e:	4654                	lw	a3,12(a2)
42026440:	fec5                	bnez	a3,420263f8 <__wrap_esp_audio_simple_dec_process+0x82>
42026442:	03074683          	lbu	a3,48(a4)
42026446:	d2bd                	beqz	a3,420263ac <__wrap_esp_audio_simple_dec_process+0x36>
42026448:	bf45                	j	420263f8 <__wrap_esp_audio_simple_dec_process+0x82>
4202644a:	38f1106f          	j	42037fd8 <esp_audio_simple_dec_process>
4202644e:	41dc                	lw	a5,4(a1)
42026450:	df85                	beqz	a5,42026388 <__wrap_esp_audio_simple_dec_process+0x12>
42026452:	556d                	li	a0,-5
42026454:	8082                	ret
42026456:	02070823          	sb	zero,48(a4)
4202645a:	b7cd                	j	4202643c <__wrap_esp_audio_simple_dec_process+0xc6>
4202645c:	4390                	lw	a2,0(a5)
4202645e:	4501                	li	a0,0
42026460:	00064603          	lbu	a2,0(a2)
42026464:	02d70823          	sb	a3,48(a4)
42026468:	02c708a3          	sb	a2,49(a4)
4202646c:	c7d4                	sw	a3,12(a5)
4202646e:	b769                	j	420263f8 <__wrap_esp_audio_simple_dec_process+0x82>
42026470:	50f2                	lw	ra,60(sp)
42026472:	85be                	mv	a1,a5
42026474:	853a                	mv	a0,a4
42026476:	6121                	addi	sp,sp,64
42026478:	cd9ff06f          	j	42026150 <process_checked>
4202647c:	4390                	lw	a2,0(a5)
4202647e:	010685b3          	add	a1,a3,a6
42026482:	4501                	li	a0,0
42026484:	96b2                	add	a3,a3,a2
42026486:	0006c683          	lbu	a3,0(a3)
4202648a:	03070823          	sb	a6,48(a4)
4202648e:	02d708a3          	sb	a3,49(a4)
42026492:	c7cc                	sw	a1,12(a5)
42026494:	b795                	j	420263f8 <__wrap_esp_audio_simple_dec_process+0x82>
