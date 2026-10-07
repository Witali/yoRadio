
idf\esp32c3-oled-native\build-rx-owner\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026514 <__wrap_esp_audio_simple_dec_process>:
42026514:	0015b793          	seqz	a5,a1
42026518:	00163713          	seqz	a4,a2
4202651c:	8fd9                	or	a5,a5,a4
4202651e:	ebe9                	bnez	a5,420265f0 <__wrap_esp_audio_simple_dec_process+0xdc>
42026520:	c961                	beqz	a0,420265f0 <__wrap_esp_audio_simple_dec_process+0xdc>
42026522:	419c                	lw	a5,0(a1)
42026524:	c7e1                	beqz	a5,420265ec <__wrap_esp_audio_simple_dec_process+0xd8>
42026526:	5558                	lw	a4,44(a0)
42026528:	204747b7          	lui	a5,0x20474
4202652c:	74f78793          	addi	a5,a5,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
42026530:	0af71c63          	bne	a4,a5,420265e8 <__wrap_esp_audio_simple_dec_process+0xd4>
42026534:	7139                	addi	sp,sp,-64
42026536:	03054683          	lbu	a3,48(a0)
4202653a:	de06                	sw	ra,60(sp)
4202653c:	0005a623          	sw	zero,12(a1)
42026540:	00062623          	sw	zero,12(a2)
42026544:	872a                	mv	a4,a0
42026546:	87ae                	mv	a5,a1
42026548:	eab1                	bnez	a3,4202659c <__wrap_esp_audio_simple_dec_process+0x88>
4202654a:	43d4                	lw	a3,4(a5)
4202654c:	c6a1                	beqz	a3,42026594 <__wrap_esp_audio_simple_dec_process+0x80>
4202654e:	0087c583          	lbu	a1,8(a5)
42026552:	edd5                	bnez	a1,4202660e <__wrap_esp_audio_simple_dec_process+0xfa>
42026554:	4805                	li	a6,1
42026556:	0b068263          	beq	a3,a6,420265fa <__wrap_esp_audio_simple_dec_process+0xe6>
4202655a:	0007ae83          	lw	t4,0(a5)
4202655e:	0087ae03          	lw	t3,8(a5)
42026562:	00c7a303          	lw	t1,12(a5)
42026566:	0107a883          	lw	a7,16(a5)
4202656a:	16fd                	addi	a3,a3,-1
4202656c:	086c                	addi	a1,sp,28
4202656e:	853a                	mv	a0,a4
42026570:	c23e                	sw	a5,4(sp)
42026572:	d036                	sw	a3,32(sp)
42026574:	c43a                	sw	a4,8(sp)
42026576:	ce76                	sw	t4,28(sp)
42026578:	d272                	sw	t3,36(sp)
4202657a:	d41a                	sw	t1,40(sp)
4202657c:	d646                	sw	a7,44(sp)
4202657e:	d71ff0ef          	jal	420262ee <process_checked>
42026582:	56a2                	lw	a3,40(sp)
42026584:	4792                	lw	a5,4(sp)
42026586:	c7d4                	sw	a3,12(a5)
42026588:	e519                	bnez	a0,42026596 <__wrap_esp_audio_simple_dec_process+0x82>
4202658a:	5602                	lw	a2,32(sp)
4202658c:	4722                	lw	a4,8(sp)
4202658e:	4805                	li	a6,1
42026590:	08c68563          	beq	a3,a2,4202661a <__wrap_esp_audio_simple_dec_process+0x106>
42026594:	4501                	li	a0,0
42026596:	50f2                	lw	ra,60(sp)
42026598:	6121                	addi	sp,sp,64
4202659a:	8082                	ret
4202659c:	0085c683          	lbu	a3,8(a1)
420265a0:	03150513          	addi	a0,a0,49
420265a4:	4585                	li	a1,1
420265a6:	4801                	li	a6,0
420265a8:	4881                	li	a7,0
420265aa:	d242                	sw	a6,36(sp)
420265ac:	d446                	sw	a7,40(sp)
420265ae:	ce2a                	sw	a0,28(sp)
420265b0:	d02e                	sw	a1,32(sp)
420265b2:	c681                	beqz	a3,420265ba <__wrap_esp_audio_simple_dec_process+0xa6>
420265b4:	43d4                	lw	a3,4(a5)
420265b6:	0016b693          	seqz	a3,a3
420265ba:	02d10223          	sb	a3,36(sp)
420265be:	4b94                	lw	a3,16(a5)
420265c0:	853a                	mv	a0,a4
420265c2:	086c                	addi	a1,sp,28
420265c4:	c63e                	sw	a5,12(sp)
420265c6:	c432                	sw	a2,8(sp)
420265c8:	c23a                	sw	a4,4(sp)
420265ca:	d636                	sw	a3,44(sp)
420265cc:	d23ff0ef          	jal	420262ee <process_checked>
420265d0:	56a2                	lw	a3,40(sp)
420265d2:	4712                	lw	a4,4(sp)
420265d4:	4622                	lw	a2,8(sp)
420265d6:	47b2                	lw	a5,12(sp)
420265d8:	ee91                	bnez	a3,420265f4 <__wrap_esp_audio_simple_dec_process+0xe0>
420265da:	fd55                	bnez	a0,42026596 <__wrap_esp_audio_simple_dec_process+0x82>
420265dc:	4654                	lw	a3,12(a2)
420265de:	fec5                	bnez	a3,42026596 <__wrap_esp_audio_simple_dec_process+0x82>
420265e0:	03074683          	lbu	a3,48(a4)
420265e4:	d2bd                	beqz	a3,4202654a <__wrap_esp_audio_simple_dec_process+0x36>
420265e6:	bf45                	j	42026596 <__wrap_esp_audio_simple_dec_process+0x82>
420265e8:	20b1206f          	j	42038ff2 <esp_audio_simple_dec_process>
420265ec:	41dc                	lw	a5,4(a1)
420265ee:	df85                	beqz	a5,42026526 <__wrap_esp_audio_simple_dec_process+0x12>
420265f0:	556d                	li	a0,-5
420265f2:	8082                	ret
420265f4:	02070823          	sb	zero,48(a4)
420265f8:	b7cd                	j	420265da <__wrap_esp_audio_simple_dec_process+0xc6>
420265fa:	4390                	lw	a2,0(a5)
420265fc:	4501                	li	a0,0
420265fe:	00064603          	lbu	a2,0(a2)
42026602:	02d70823          	sb	a3,48(a4)
42026606:	02c708a3          	sb	a2,49(a4)
4202660a:	c7d4                	sw	a3,12(a5)
4202660c:	b769                	j	42026596 <__wrap_esp_audio_simple_dec_process+0x82>
4202660e:	50f2                	lw	ra,60(sp)
42026610:	85be                	mv	a1,a5
42026612:	853a                	mv	a0,a4
42026614:	6121                	addi	sp,sp,64
42026616:	cd9ff06f          	j	420262ee <process_checked>
4202661a:	4390                	lw	a2,0(a5)
4202661c:	010685b3          	add	a1,a3,a6
42026620:	4501                	li	a0,0
42026622:	96b2                	add	a3,a3,a2
42026624:	0006c683          	lbu	a3,0(a3)
42026628:	03070823          	sb	a6,48(a4)
4202662c:	02d708a3          	sb	a3,49(a4)
42026630:	c7cc                	sw	a1,12(a5)
42026632:	b795                	j	42026596 <__wrap_esp_audio_simple_dec_process+0x82>
