
C:\Work\yoRadio\.worktree\aac-storage18\idf\esp32c3-oled-native\build-flac-bounds\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4202636a <__wrap_esp_audio_simple_dec_process>:
4202636a:	0015b793          	seqz	a5,a1
4202636e:	00163713          	seqz	a4,a2
42026372:	8fd9                	or	a5,a5,a4
42026374:	ebe9                	bnez	a5,42026446 <__wrap_esp_audio_simple_dec_process+0xdc>
42026376:	c961                	beqz	a0,42026446 <__wrap_esp_audio_simple_dec_process+0xdc>
42026378:	419c                	lw	a5,0(a1)
4202637a:	c7e1                	beqz	a5,42026442 <__wrap_esp_audio_simple_dec_process+0xd8>
4202637c:	5558                	lw	a4,44(a0)
4202637e:	204747b7          	lui	a5,0x20474
42026382:	74f78793          	addi	a5,a5,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
42026386:	0af71c63          	bne	a4,a5,4202643e <__wrap_esp_audio_simple_dec_process+0xd4>
4202638a:	7139                	addi	sp,sp,-64
4202638c:	03054683          	lbu	a3,48(a0)
42026390:	de06                	sw	ra,60(sp)
42026392:	0005a623          	sw	zero,12(a1)
42026396:	00062623          	sw	zero,12(a2)
4202639a:	872a                	mv	a4,a0
4202639c:	87ae                	mv	a5,a1
4202639e:	eab1                	bnez	a3,420263f2 <__wrap_esp_audio_simple_dec_process+0x88>
420263a0:	43d4                	lw	a3,4(a5)
420263a2:	c6a1                	beqz	a3,420263ea <__wrap_esp_audio_simple_dec_process+0x80>
420263a4:	0087c583          	lbu	a1,8(a5)
420263a8:	edd5                	bnez	a1,42026464 <__wrap_esp_audio_simple_dec_process+0xfa>
420263aa:	4805                	li	a6,1
420263ac:	0b068263          	beq	a3,a6,42026450 <__wrap_esp_audio_simple_dec_process+0xe6>
420263b0:	0007ae83          	lw	t4,0(a5)
420263b4:	0087ae03          	lw	t3,8(a5)
420263b8:	00c7a303          	lw	t1,12(a5)
420263bc:	0107a883          	lw	a7,16(a5)
420263c0:	16fd                	addi	a3,a3,-1
420263c2:	086c                	addi	a1,sp,28
420263c4:	853a                	mv	a0,a4
420263c6:	c23e                	sw	a5,4(sp)
420263c8:	d036                	sw	a3,32(sp)
420263ca:	c43a                	sw	a4,8(sp)
420263cc:	ce76                	sw	t4,28(sp)
420263ce:	d272                	sw	t3,36(sp)
420263d0:	d41a                	sw	t1,40(sp)
420263d2:	d646                	sw	a7,44(sp)
420263d4:	d71ff0ef          	jal	42026144 <process_checked>
420263d8:	56a2                	lw	a3,40(sp)
420263da:	4792                	lw	a5,4(sp)
420263dc:	c7d4                	sw	a3,12(a5)
420263de:	e519                	bnez	a0,420263ec <__wrap_esp_audio_simple_dec_process+0x82>
420263e0:	5602                	lw	a2,32(sp)
420263e2:	4722                	lw	a4,8(sp)
420263e4:	4805                	li	a6,1
420263e6:	08c68563          	beq	a3,a2,42026470 <__wrap_esp_audio_simple_dec_process+0x106>
420263ea:	4501                	li	a0,0
420263ec:	50f2                	lw	ra,60(sp)
420263ee:	6121                	addi	sp,sp,64
420263f0:	8082                	ret
420263f2:	0085c683          	lbu	a3,8(a1)
420263f6:	03150513          	addi	a0,a0,49
420263fa:	4585                	li	a1,1
420263fc:	4801                	li	a6,0
420263fe:	4881                	li	a7,0
42026400:	d242                	sw	a6,36(sp)
42026402:	d446                	sw	a7,40(sp)
42026404:	ce2a                	sw	a0,28(sp)
42026406:	d02e                	sw	a1,32(sp)
42026408:	c681                	beqz	a3,42026410 <__wrap_esp_audio_simple_dec_process+0xa6>
4202640a:	43d4                	lw	a3,4(a5)
4202640c:	0016b693          	seqz	a3,a3
42026410:	02d10223          	sb	a3,36(sp)
42026414:	4b94                	lw	a3,16(a5)
42026416:	853a                	mv	a0,a4
42026418:	086c                	addi	a1,sp,28
4202641a:	c63e                	sw	a5,12(sp)
4202641c:	c432                	sw	a2,8(sp)
4202641e:	c23a                	sw	a4,4(sp)
42026420:	d636                	sw	a3,44(sp)
42026422:	d23ff0ef          	jal	42026144 <process_checked>
42026426:	56a2                	lw	a3,40(sp)
42026428:	4712                	lw	a4,4(sp)
4202642a:	4622                	lw	a2,8(sp)
4202642c:	47b2                	lw	a5,12(sp)
4202642e:	ee91                	bnez	a3,4202644a <__wrap_esp_audio_simple_dec_process+0xe0>
42026430:	fd55                	bnez	a0,420263ec <__wrap_esp_audio_simple_dec_process+0x82>
42026432:	4654                	lw	a3,12(a2)
42026434:	fec5                	bnez	a3,420263ec <__wrap_esp_audio_simple_dec_process+0x82>
42026436:	03074683          	lbu	a3,48(a4)
4202643a:	d2bd                	beqz	a3,420263a0 <__wrap_esp_audio_simple_dec_process+0x36>
4202643c:	bf45                	j	420263ec <__wrap_esp_audio_simple_dec_process+0x82>
4202643e:	2bb1106f          	j	42037ef8 <esp_audio_simple_dec_process>
42026442:	41dc                	lw	a5,4(a1)
42026444:	df85                	beqz	a5,4202637c <__wrap_esp_audio_simple_dec_process+0x12>
42026446:	556d                	li	a0,-5
42026448:	8082                	ret
4202644a:	02070823          	sb	zero,48(a4)
4202644e:	b7cd                	j	42026430 <__wrap_esp_audio_simple_dec_process+0xc6>
42026450:	4390                	lw	a2,0(a5)
42026452:	4501                	li	a0,0
42026454:	00064603          	lbu	a2,0(a2)
42026458:	02d70823          	sb	a3,48(a4)
4202645c:	02c708a3          	sb	a2,49(a4)
42026460:	c7d4                	sw	a3,12(a5)
42026462:	b769                	j	420263ec <__wrap_esp_audio_simple_dec_process+0x82>
42026464:	50f2                	lw	ra,60(sp)
42026466:	85be                	mv	a1,a5
42026468:	853a                	mv	a0,a4
4202646a:	6121                	addi	sp,sp,64
4202646c:	cd9ff06f          	j	42026144 <process_checked>
42026470:	4390                	lw	a2,0(a5)
42026472:	010685b3          	add	a1,a3,a6
42026476:	4501                	li	a0,0
42026478:	96b2                	add	a3,a3,a2
4202647a:	0006c683          	lbu	a3,0(a3)
4202647e:	03070823          	sb	a6,48(a4)
42026482:	02d708a3          	sb	a3,49(a4)
42026486:	c7cc                	sw	a1,12(a5)
42026488:	b795                	j	420263ec <__wrap_esp_audio_simple_dec_process+0x82>
