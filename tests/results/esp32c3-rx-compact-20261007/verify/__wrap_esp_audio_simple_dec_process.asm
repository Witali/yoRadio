
idf\esp32c3-oled-native\build-rx-owner\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026518 <__wrap_esp_audio_simple_dec_process>:
42026518:	0015b793          	seqz	a5,a1
4202651c:	00163713          	seqz	a4,a2
42026520:	8fd9                	or	a5,a5,a4
42026522:	ebe9                	bnez	a5,420265f4 <__wrap_esp_audio_simple_dec_process+0xdc>
42026524:	c961                	beqz	a0,420265f4 <__wrap_esp_audio_simple_dec_process+0xdc>
42026526:	419c                	lw	a5,0(a1)
42026528:	c7e1                	beqz	a5,420265f0 <__wrap_esp_audio_simple_dec_process+0xd8>
4202652a:	5558                	lw	a4,44(a0)
4202652c:	204747b7          	lui	a5,0x20474
42026530:	74f78793          	addi	a5,a5,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
42026534:	0af71c63          	bne	a4,a5,420265ec <__wrap_esp_audio_simple_dec_process+0xd4>
42026538:	7139                	addi	sp,sp,-64
4202653a:	03054683          	lbu	a3,48(a0)
4202653e:	de06                	sw	ra,60(sp)
42026540:	0005a623          	sw	zero,12(a1)
42026544:	00062623          	sw	zero,12(a2)
42026548:	872a                	mv	a4,a0
4202654a:	87ae                	mv	a5,a1
4202654c:	eab1                	bnez	a3,420265a0 <__wrap_esp_audio_simple_dec_process+0x88>
4202654e:	43d4                	lw	a3,4(a5)
42026550:	c6a1                	beqz	a3,42026598 <__wrap_esp_audio_simple_dec_process+0x80>
42026552:	0087c583          	lbu	a1,8(a5)
42026556:	edd5                	bnez	a1,42026612 <__wrap_esp_audio_simple_dec_process+0xfa>
42026558:	4805                	li	a6,1
4202655a:	0b068263          	beq	a3,a6,420265fe <__wrap_esp_audio_simple_dec_process+0xe6>
4202655e:	0007ae83          	lw	t4,0(a5)
42026562:	0087ae03          	lw	t3,8(a5)
42026566:	00c7a303          	lw	t1,12(a5)
4202656a:	0107a883          	lw	a7,16(a5)
4202656e:	16fd                	addi	a3,a3,-1
42026570:	086c                	addi	a1,sp,28
42026572:	853a                	mv	a0,a4
42026574:	c23e                	sw	a5,4(sp)
42026576:	d036                	sw	a3,32(sp)
42026578:	c43a                	sw	a4,8(sp)
4202657a:	ce76                	sw	t4,28(sp)
4202657c:	d272                	sw	t3,36(sp)
4202657e:	d41a                	sw	t1,40(sp)
42026580:	d646                	sw	a7,44(sp)
42026582:	d71ff0ef          	jal	420262f2 <process_checked>
42026586:	56a2                	lw	a3,40(sp)
42026588:	4792                	lw	a5,4(sp)
4202658a:	c7d4                	sw	a3,12(a5)
4202658c:	e519                	bnez	a0,4202659a <__wrap_esp_audio_simple_dec_process+0x82>
4202658e:	5602                	lw	a2,32(sp)
42026590:	4722                	lw	a4,8(sp)
42026592:	4805                	li	a6,1
42026594:	08c68563          	beq	a3,a2,4202661e <__wrap_esp_audio_simple_dec_process+0x106>
42026598:	4501                	li	a0,0
4202659a:	50f2                	lw	ra,60(sp)
4202659c:	6121                	addi	sp,sp,64
4202659e:	8082                	ret
420265a0:	0085c683          	lbu	a3,8(a1)
420265a4:	03150513          	addi	a0,a0,49
420265a8:	4585                	li	a1,1
420265aa:	4801                	li	a6,0
420265ac:	4881                	li	a7,0
420265ae:	d242                	sw	a6,36(sp)
420265b0:	d446                	sw	a7,40(sp)
420265b2:	ce2a                	sw	a0,28(sp)
420265b4:	d02e                	sw	a1,32(sp)
420265b6:	c681                	beqz	a3,420265be <__wrap_esp_audio_simple_dec_process+0xa6>
420265b8:	43d4                	lw	a3,4(a5)
420265ba:	0016b693          	seqz	a3,a3
420265be:	02d10223          	sb	a3,36(sp)
420265c2:	4b94                	lw	a3,16(a5)
420265c4:	853a                	mv	a0,a4
420265c6:	086c                	addi	a1,sp,28
420265c8:	c63e                	sw	a5,12(sp)
420265ca:	c432                	sw	a2,8(sp)
420265cc:	c23a                	sw	a4,4(sp)
420265ce:	d636                	sw	a3,44(sp)
420265d0:	d23ff0ef          	jal	420262f2 <process_checked>
420265d4:	56a2                	lw	a3,40(sp)
420265d6:	4712                	lw	a4,4(sp)
420265d8:	4622                	lw	a2,8(sp)
420265da:	47b2                	lw	a5,12(sp)
420265dc:	ee91                	bnez	a3,420265f8 <__wrap_esp_audio_simple_dec_process+0xe0>
420265de:	fd55                	bnez	a0,4202659a <__wrap_esp_audio_simple_dec_process+0x82>
420265e0:	4654                	lw	a3,12(a2)
420265e2:	fec5                	bnez	a3,4202659a <__wrap_esp_audio_simple_dec_process+0x82>
420265e4:	03074683          	lbu	a3,48(a4)
420265e8:	d2bd                	beqz	a3,4202654e <__wrap_esp_audio_simple_dec_process+0x36>
420265ea:	bf45                	j	4202659a <__wrap_esp_audio_simple_dec_process+0x82>
420265ec:	2871206f          	j	42039072 <esp_audio_simple_dec_process>
420265f0:	41dc                	lw	a5,4(a1)
420265f2:	df85                	beqz	a5,4202652a <__wrap_esp_audio_simple_dec_process+0x12>
420265f4:	556d                	li	a0,-5
420265f6:	8082                	ret
420265f8:	02070823          	sb	zero,48(a4)
420265fc:	b7cd                	j	420265de <__wrap_esp_audio_simple_dec_process+0xc6>
420265fe:	4390                	lw	a2,0(a5)
42026600:	4501                	li	a0,0
42026602:	00064603          	lbu	a2,0(a2)
42026606:	02d70823          	sb	a3,48(a4)
4202660a:	02c708a3          	sb	a2,49(a4)
4202660e:	c7d4                	sw	a3,12(a5)
42026610:	b769                	j	4202659a <__wrap_esp_audio_simple_dec_process+0x82>
42026612:	50f2                	lw	ra,60(sp)
42026614:	85be                	mv	a1,a5
42026616:	853a                	mv	a0,a4
42026618:	6121                	addi	sp,sp,64
4202661a:	cd9ff06f          	j	420262f2 <process_checked>
4202661e:	4390                	lw	a2,0(a5)
42026620:	010685b3          	add	a1,a3,a6
42026624:	4501                	li	a0,0
42026626:	96b2                	add	a3,a3,a2
42026628:	0006c683          	lbu	a3,0(a3)
4202662c:	03070823          	sb	a6,48(a4)
42026630:	02d708a3          	sb	a3,49(a4)
42026634:	c7cc                	sw	a1,12(a5)
42026636:	b795                	j	4202659a <__wrap_esp_audio_simple_dec_process+0x82>
