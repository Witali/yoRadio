
idf\esp32c3-oled-native\build-rx-copy\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420263b2 <__wrap_esp_audio_simple_dec_process>:
420263b2:	0015b793          	seqz	a5,a1
420263b6:	00163713          	seqz	a4,a2
420263ba:	8fd9                	or	a5,a5,a4
420263bc:	ebe9                	bnez	a5,4202648e <__wrap_esp_audio_simple_dec_process+0xdc>
420263be:	c961                	beqz	a0,4202648e <__wrap_esp_audio_simple_dec_process+0xdc>
420263c0:	419c                	lw	a5,0(a1)
420263c2:	c7e1                	beqz	a5,4202648a <__wrap_esp_audio_simple_dec_process+0xd8>
420263c4:	5558                	lw	a4,44(a0)
420263c6:	204747b7          	lui	a5,0x20474
420263ca:	74f78793          	addi	a5,a5,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
420263ce:	0af71c63          	bne	a4,a5,42026486 <__wrap_esp_audio_simple_dec_process+0xd4>
420263d2:	7139                	addi	sp,sp,-64
420263d4:	03054683          	lbu	a3,48(a0)
420263d8:	de06                	sw	ra,60(sp)
420263da:	0005a623          	sw	zero,12(a1)
420263de:	00062623          	sw	zero,12(a2)
420263e2:	872a                	mv	a4,a0
420263e4:	87ae                	mv	a5,a1
420263e6:	eab1                	bnez	a3,4202643a <__wrap_esp_audio_simple_dec_process+0x88>
420263e8:	43d4                	lw	a3,4(a5)
420263ea:	c6a1                	beqz	a3,42026432 <__wrap_esp_audio_simple_dec_process+0x80>
420263ec:	0087c583          	lbu	a1,8(a5)
420263f0:	edd5                	bnez	a1,420264ac <__wrap_esp_audio_simple_dec_process+0xfa>
420263f2:	4805                	li	a6,1
420263f4:	0b068263          	beq	a3,a6,42026498 <__wrap_esp_audio_simple_dec_process+0xe6>
420263f8:	0007ae83          	lw	t4,0(a5)
420263fc:	0087ae03          	lw	t3,8(a5)
42026400:	00c7a303          	lw	t1,12(a5)
42026404:	0107a883          	lw	a7,16(a5)
42026408:	16fd                	addi	a3,a3,-1
4202640a:	086c                	addi	a1,sp,28
4202640c:	853a                	mv	a0,a4
4202640e:	c23e                	sw	a5,4(sp)
42026410:	d036                	sw	a3,32(sp)
42026412:	c43a                	sw	a4,8(sp)
42026414:	ce76                	sw	t4,28(sp)
42026416:	d272                	sw	t3,36(sp)
42026418:	d41a                	sw	t1,40(sp)
4202641a:	d646                	sw	a7,44(sp)
4202641c:	d71ff0ef          	jal	4202618c <process_checked>
42026420:	56a2                	lw	a3,40(sp)
42026422:	4792                	lw	a5,4(sp)
42026424:	c7d4                	sw	a3,12(a5)
42026426:	e519                	bnez	a0,42026434 <__wrap_esp_audio_simple_dec_process+0x82>
42026428:	5602                	lw	a2,32(sp)
4202642a:	4722                	lw	a4,8(sp)
4202642c:	4805                	li	a6,1
4202642e:	08c68563          	beq	a3,a2,420264b8 <__wrap_esp_audio_simple_dec_process+0x106>
42026432:	4501                	li	a0,0
42026434:	50f2                	lw	ra,60(sp)
42026436:	6121                	addi	sp,sp,64
42026438:	8082                	ret
4202643a:	0085c683          	lbu	a3,8(a1)
4202643e:	03150513          	addi	a0,a0,49
42026442:	4585                	li	a1,1
42026444:	4801                	li	a6,0
42026446:	4881                	li	a7,0
42026448:	d242                	sw	a6,36(sp)
4202644a:	d446                	sw	a7,40(sp)
4202644c:	ce2a                	sw	a0,28(sp)
4202644e:	d02e                	sw	a1,32(sp)
42026450:	c681                	beqz	a3,42026458 <__wrap_esp_audio_simple_dec_process+0xa6>
42026452:	43d4                	lw	a3,4(a5)
42026454:	0016b693          	seqz	a3,a3
42026458:	02d10223          	sb	a3,36(sp)
4202645c:	4b94                	lw	a3,16(a5)
4202645e:	853a                	mv	a0,a4
42026460:	086c                	addi	a1,sp,28
42026462:	c63e                	sw	a5,12(sp)
42026464:	c432                	sw	a2,8(sp)
42026466:	c23a                	sw	a4,4(sp)
42026468:	d636                	sw	a3,44(sp)
4202646a:	d23ff0ef          	jal	4202618c <process_checked>
4202646e:	56a2                	lw	a3,40(sp)
42026470:	4712                	lw	a4,4(sp)
42026472:	4622                	lw	a2,8(sp)
42026474:	47b2                	lw	a5,12(sp)
42026476:	ee91                	bnez	a3,42026492 <__wrap_esp_audio_simple_dec_process+0xe0>
42026478:	fd55                	bnez	a0,42026434 <__wrap_esp_audio_simple_dec_process+0x82>
4202647a:	4654                	lw	a3,12(a2)
4202647c:	fec5                	bnez	a3,42026434 <__wrap_esp_audio_simple_dec_process+0x82>
4202647e:	03074683          	lbu	a3,48(a4)
42026482:	d2bd                	beqz	a3,420263e8 <__wrap_esp_audio_simple_dec_process+0x36>
42026484:	bf45                	j	42026434 <__wrap_esp_audio_simple_dec_process+0x82>
42026486:	5bc1206f          	j	42038a42 <esp_audio_simple_dec_process>
4202648a:	41dc                	lw	a5,4(a1)
4202648c:	df85                	beqz	a5,420263c4 <__wrap_esp_audio_simple_dec_process+0x12>
4202648e:	556d                	li	a0,-5
42026490:	8082                	ret
42026492:	02070823          	sb	zero,48(a4)
42026496:	b7cd                	j	42026478 <__wrap_esp_audio_simple_dec_process+0xc6>
42026498:	4390                	lw	a2,0(a5)
4202649a:	4501                	li	a0,0
4202649c:	00064603          	lbu	a2,0(a2)
420264a0:	02d70823          	sb	a3,48(a4)
420264a4:	02c708a3          	sb	a2,49(a4)
420264a8:	c7d4                	sw	a3,12(a5)
420264aa:	b769                	j	42026434 <__wrap_esp_audio_simple_dec_process+0x82>
420264ac:	50f2                	lw	ra,60(sp)
420264ae:	85be                	mv	a1,a5
420264b0:	853a                	mv	a0,a4
420264b2:	6121                	addi	sp,sp,64
420264b4:	cd9ff06f          	j	4202618c <process_checked>
420264b8:	4390                	lw	a2,0(a5)
420264ba:	010685b3          	add	a1,a3,a6
420264be:	4501                	li	a0,0
420264c0:	96b2                	add	a3,a3,a2
420264c2:	0006c683          	lbu	a3,0(a3)
420264c6:	03070823          	sb	a6,48(a4)
420264ca:	02d708a3          	sb	a3,49(a4)
420264ce:	c7cc                	sw	a1,12(a5)
420264d0:	b795                	j	42026434 <__wrap_esp_audio_simple_dec_process+0x82>
