
idf\esp32c3-oled-native\build-output-dma-leased\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026336 <__wrap_esp_audio_simple_dec_process>:
42026336:	0015b793          	seqz	a5,a1
4202633a:	00163713          	seqz	a4,a2
4202633e:	8fd9                	or	a5,a5,a4
42026340:	ebe9                	bnez	a5,42026412 <__wrap_esp_audio_simple_dec_process+0xdc>
42026342:	c961                	beqz	a0,42026412 <__wrap_esp_audio_simple_dec_process+0xdc>
42026344:	419c                	lw	a5,0(a1)
42026346:	c7e1                	beqz	a5,4202640e <__wrap_esp_audio_simple_dec_process+0xd8>
42026348:	5558                	lw	a4,44(a0)
4202634a:	204747b7          	lui	a5,0x20474
4202634e:	74f78793          	addi	a5,a5,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
42026352:	0af71c63          	bne	a4,a5,4202640a <__wrap_esp_audio_simple_dec_process+0xd4>
42026356:	7139                	addi	sp,sp,-64
42026358:	03054683          	lbu	a3,48(a0)
4202635c:	de06                	sw	ra,60(sp)
4202635e:	0005a623          	sw	zero,12(a1)
42026362:	00062623          	sw	zero,12(a2)
42026366:	872a                	mv	a4,a0
42026368:	87ae                	mv	a5,a1
4202636a:	eab1                	bnez	a3,420263be <__wrap_esp_audio_simple_dec_process+0x88>
4202636c:	43d4                	lw	a3,4(a5)
4202636e:	c6a1                	beqz	a3,420263b6 <__wrap_esp_audio_simple_dec_process+0x80>
42026370:	0087c583          	lbu	a1,8(a5)
42026374:	edd5                	bnez	a1,42026430 <__wrap_esp_audio_simple_dec_process+0xfa>
42026376:	4805                	li	a6,1
42026378:	0b068263          	beq	a3,a6,4202641c <__wrap_esp_audio_simple_dec_process+0xe6>
4202637c:	0007ae83          	lw	t4,0(a5)
42026380:	0087ae03          	lw	t3,8(a5)
42026384:	00c7a303          	lw	t1,12(a5)
42026388:	0107a883          	lw	a7,16(a5)
4202638c:	16fd                	addi	a3,a3,-1
4202638e:	086c                	addi	a1,sp,28
42026390:	853a                	mv	a0,a4
42026392:	c23e                	sw	a5,4(sp)
42026394:	d036                	sw	a3,32(sp)
42026396:	c43a                	sw	a4,8(sp)
42026398:	ce76                	sw	t4,28(sp)
4202639a:	d272                	sw	t3,36(sp)
4202639c:	d41a                	sw	t1,40(sp)
4202639e:	d646                	sw	a7,44(sp)
420263a0:	d71ff0ef          	jal	42026110 <process_checked>
420263a4:	56a2                	lw	a3,40(sp)
420263a6:	4792                	lw	a5,4(sp)
420263a8:	c7d4                	sw	a3,12(a5)
420263aa:	e519                	bnez	a0,420263b8 <__wrap_esp_audio_simple_dec_process+0x82>
420263ac:	5602                	lw	a2,32(sp)
420263ae:	4722                	lw	a4,8(sp)
420263b0:	4805                	li	a6,1
420263b2:	08c68563          	beq	a3,a2,4202643c <__wrap_esp_audio_simple_dec_process+0x106>
420263b6:	4501                	li	a0,0
420263b8:	50f2                	lw	ra,60(sp)
420263ba:	6121                	addi	sp,sp,64
420263bc:	8082                	ret
420263be:	0085c683          	lbu	a3,8(a1)
420263c2:	03150513          	addi	a0,a0,49
420263c6:	4585                	li	a1,1
420263c8:	4801                	li	a6,0
420263ca:	4881                	li	a7,0
420263cc:	d242                	sw	a6,36(sp)
420263ce:	d446                	sw	a7,40(sp)
420263d0:	ce2a                	sw	a0,28(sp)
420263d2:	d02e                	sw	a1,32(sp)
420263d4:	c681                	beqz	a3,420263dc <__wrap_esp_audio_simple_dec_process+0xa6>
420263d6:	43d4                	lw	a3,4(a5)
420263d8:	0016b693          	seqz	a3,a3
420263dc:	02d10223          	sb	a3,36(sp)
420263e0:	4b94                	lw	a3,16(a5)
420263e2:	853a                	mv	a0,a4
420263e4:	086c                	addi	a1,sp,28
420263e6:	c63e                	sw	a5,12(sp)
420263e8:	c432                	sw	a2,8(sp)
420263ea:	c23a                	sw	a4,4(sp)
420263ec:	d636                	sw	a3,44(sp)
420263ee:	d23ff0ef          	jal	42026110 <process_checked>
420263f2:	56a2                	lw	a3,40(sp)
420263f4:	4712                	lw	a4,4(sp)
420263f6:	4622                	lw	a2,8(sp)
420263f8:	47b2                	lw	a5,12(sp)
420263fa:	ee91                	bnez	a3,42026416 <__wrap_esp_audio_simple_dec_process+0xe0>
420263fc:	fd55                	bnez	a0,420263b8 <__wrap_esp_audio_simple_dec_process+0x82>
420263fe:	4654                	lw	a3,12(a2)
42026400:	fec5                	bnez	a3,420263b8 <__wrap_esp_audio_simple_dec_process+0x82>
42026402:	03074683          	lbu	a3,48(a4)
42026406:	d2bd                	beqz	a3,4202636c <__wrap_esp_audio_simple_dec_process+0x36>
42026408:	bf45                	j	420263b8 <__wrap_esp_audio_simple_dec_process+0x82>
4202640a:	2271006f          	j	42036e30 <esp_audio_simple_dec_process>
4202640e:	41dc                	lw	a5,4(a1)
42026410:	df85                	beqz	a5,42026348 <__wrap_esp_audio_simple_dec_process+0x12>
42026412:	556d                	li	a0,-5
42026414:	8082                	ret
42026416:	02070823          	sb	zero,48(a4)
4202641a:	b7cd                	j	420263fc <__wrap_esp_audio_simple_dec_process+0xc6>
4202641c:	4390                	lw	a2,0(a5)
4202641e:	4501                	li	a0,0
42026420:	00064603          	lbu	a2,0(a2)
42026424:	02d70823          	sb	a3,48(a4)
42026428:	02c708a3          	sb	a2,49(a4)
4202642c:	c7d4                	sw	a3,12(a5)
4202642e:	b769                	j	420263b8 <__wrap_esp_audio_simple_dec_process+0x82>
42026430:	50f2                	lw	ra,60(sp)
42026432:	85be                	mv	a1,a5
42026434:	853a                	mv	a0,a4
42026436:	6121                	addi	sp,sp,64
42026438:	cd9ff06f          	j	42026110 <process_checked>
4202643c:	4390                	lw	a2,0(a5)
4202643e:	010685b3          	add	a1,a3,a6
42026442:	4501                	li	a0,0
42026444:	96b2                	add	a3,a3,a2
42026446:	0006c683          	lbu	a3,0(a3)
4202644a:	03070823          	sb	a6,48(a4)
4202644e:	02d708a3          	sb	a3,49(a4)
42026452:	c7cc                	sw	a1,12(a5)
42026454:	b795                	j	420263b8 <__wrap_esp_audio_simple_dec_process+0x82>
