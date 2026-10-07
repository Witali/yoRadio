
idf\esp32c3-oled-native\build-custom-terminal\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4202634a <__wrap_esp_audio_simple_dec_process>:
4202634a:	0015b793          	seqz	a5,a1
4202634e:	00163713          	seqz	a4,a2
42026352:	8fd9                	or	a5,a5,a4
42026354:	ebe9                	bnez	a5,42026426 <__wrap_esp_audio_simple_dec_process+0xdc>
42026356:	c961                	beqz	a0,42026426 <__wrap_esp_audio_simple_dec_process+0xdc>
42026358:	419c                	lw	a5,0(a1)
4202635a:	c7e1                	beqz	a5,42026422 <__wrap_esp_audio_simple_dec_process+0xd8>
4202635c:	5558                	lw	a4,44(a0)
4202635e:	204747b7          	lui	a5,0x20474
42026362:	74f78793          	addi	a5,a5,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
42026366:	0af71c63          	bne	a4,a5,4202641e <__wrap_esp_audio_simple_dec_process+0xd4>
4202636a:	7139                	addi	sp,sp,-64
4202636c:	03054683          	lbu	a3,48(a0)
42026370:	de06                	sw	ra,60(sp)
42026372:	0005a623          	sw	zero,12(a1)
42026376:	00062623          	sw	zero,12(a2)
4202637a:	872a                	mv	a4,a0
4202637c:	87ae                	mv	a5,a1
4202637e:	eab1                	bnez	a3,420263d2 <__wrap_esp_audio_simple_dec_process+0x88>
42026380:	43d4                	lw	a3,4(a5)
42026382:	c6a1                	beqz	a3,420263ca <__wrap_esp_audio_simple_dec_process+0x80>
42026384:	0087c583          	lbu	a1,8(a5)
42026388:	edd5                	bnez	a1,42026444 <__wrap_esp_audio_simple_dec_process+0xfa>
4202638a:	4805                	li	a6,1
4202638c:	0b068263          	beq	a3,a6,42026430 <__wrap_esp_audio_simple_dec_process+0xe6>
42026390:	0007ae83          	lw	t4,0(a5)
42026394:	0087ae03          	lw	t3,8(a5)
42026398:	00c7a303          	lw	t1,12(a5)
4202639c:	0107a883          	lw	a7,16(a5)
420263a0:	16fd                	addi	a3,a3,-1
420263a2:	086c                	addi	a1,sp,28
420263a4:	853a                	mv	a0,a4
420263a6:	c23e                	sw	a5,4(sp)
420263a8:	d036                	sw	a3,32(sp)
420263aa:	c43a                	sw	a4,8(sp)
420263ac:	ce76                	sw	t4,28(sp)
420263ae:	d272                	sw	t3,36(sp)
420263b0:	d41a                	sw	t1,40(sp)
420263b2:	d646                	sw	a7,44(sp)
420263b4:	d71ff0ef          	jal	42026124 <process_checked>
420263b8:	56a2                	lw	a3,40(sp)
420263ba:	4792                	lw	a5,4(sp)
420263bc:	c7d4                	sw	a3,12(a5)
420263be:	e519                	bnez	a0,420263cc <__wrap_esp_audio_simple_dec_process+0x82>
420263c0:	5602                	lw	a2,32(sp)
420263c2:	4722                	lw	a4,8(sp)
420263c4:	4805                	li	a6,1
420263c6:	08c68563          	beq	a3,a2,42026450 <__wrap_esp_audio_simple_dec_process+0x106>
420263ca:	4501                	li	a0,0
420263cc:	50f2                	lw	ra,60(sp)
420263ce:	6121                	addi	sp,sp,64
420263d0:	8082                	ret
420263d2:	0085c683          	lbu	a3,8(a1)
420263d6:	03150513          	addi	a0,a0,49
420263da:	4585                	li	a1,1
420263dc:	4801                	li	a6,0
420263de:	4881                	li	a7,0
420263e0:	d242                	sw	a6,36(sp)
420263e2:	d446                	sw	a7,40(sp)
420263e4:	ce2a                	sw	a0,28(sp)
420263e6:	d02e                	sw	a1,32(sp)
420263e8:	c681                	beqz	a3,420263f0 <__wrap_esp_audio_simple_dec_process+0xa6>
420263ea:	43d4                	lw	a3,4(a5)
420263ec:	0016b693          	seqz	a3,a3
420263f0:	02d10223          	sb	a3,36(sp)
420263f4:	4b94                	lw	a3,16(a5)
420263f6:	853a                	mv	a0,a4
420263f8:	086c                	addi	a1,sp,28
420263fa:	c63e                	sw	a5,12(sp)
420263fc:	c432                	sw	a2,8(sp)
420263fe:	c23a                	sw	a4,4(sp)
42026400:	d636                	sw	a3,44(sp)
42026402:	d23ff0ef          	jal	42026124 <process_checked>
42026406:	56a2                	lw	a3,40(sp)
42026408:	4712                	lw	a4,4(sp)
4202640a:	4622                	lw	a2,8(sp)
4202640c:	47b2                	lw	a5,12(sp)
4202640e:	ee91                	bnez	a3,4202642a <__wrap_esp_audio_simple_dec_process+0xe0>
42026410:	fd55                	bnez	a0,420263cc <__wrap_esp_audio_simple_dec_process+0x82>
42026412:	4654                	lw	a3,12(a2)
42026414:	fec5                	bnez	a3,420263cc <__wrap_esp_audio_simple_dec_process+0x82>
42026416:	03074683          	lbu	a3,48(a4)
4202641a:	d2bd                	beqz	a3,42026380 <__wrap_esp_audio_simple_dec_process+0x36>
4202641c:	bf45                	j	420263cc <__wrap_esp_audio_simple_dec_process+0x82>
4202641e:	2271006f          	j	42036e44 <esp_audio_simple_dec_process>
42026422:	41dc                	lw	a5,4(a1)
42026424:	df85                	beqz	a5,4202635c <__wrap_esp_audio_simple_dec_process+0x12>
42026426:	556d                	li	a0,-5
42026428:	8082                	ret
4202642a:	02070823          	sb	zero,48(a4)
4202642e:	b7cd                	j	42026410 <__wrap_esp_audio_simple_dec_process+0xc6>
42026430:	4390                	lw	a2,0(a5)
42026432:	4501                	li	a0,0
42026434:	00064603          	lbu	a2,0(a2)
42026438:	02d70823          	sb	a3,48(a4)
4202643c:	02c708a3          	sb	a2,49(a4)
42026440:	c7d4                	sw	a3,12(a5)
42026442:	b769                	j	420263cc <__wrap_esp_audio_simple_dec_process+0x82>
42026444:	50f2                	lw	ra,60(sp)
42026446:	85be                	mv	a1,a5
42026448:	853a                	mv	a0,a4
4202644a:	6121                	addi	sp,sp,64
4202644c:	cd9ff06f          	j	42026124 <process_checked>
42026450:	4390                	lw	a2,0(a5)
42026452:	010685b3          	add	a1,a3,a6
42026456:	4501                	li	a0,0
42026458:	96b2                	add	a3,a3,a2
4202645a:	0006c683          	lbu	a3,0(a3)
4202645e:	03070823          	sb	a6,48(a4)
42026462:	02d708a3          	sb	a3,49(a4)
42026466:	c7cc                	sw	a1,12(a5)
42026468:	b795                	j	420263cc <__wrap_esp_audio_simple_dec_process+0x82>
