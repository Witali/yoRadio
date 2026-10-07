
idf\esp32c3-oled-native\build-heap-fragment\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026544 <__wrap_esp_audio_simple_dec_process>:
42026544:	0015b793          	seqz	a5,a1
42026548:	00163713          	seqz	a4,a2
4202654c:	8fd9                	or	a5,a5,a4
4202654e:	ebe9                	bnez	a5,42026620 <__wrap_esp_audio_simple_dec_process+0xdc>
42026550:	c961                	beqz	a0,42026620 <__wrap_esp_audio_simple_dec_process+0xdc>
42026552:	419c                	lw	a5,0(a1)
42026554:	c7e1                	beqz	a5,4202661c <__wrap_esp_audio_simple_dec_process+0xd8>
42026556:	5558                	lw	a4,44(a0)
42026558:	204747b7          	lui	a5,0x20474
4202655c:	74f78793          	addi	a5,a5,1871 # 2047474f <_rtc_slow_length+0x20473073>
42026560:	0af71c63          	bne	a4,a5,42026618 <__wrap_esp_audio_simple_dec_process+0xd4>
42026564:	7139                	addi	sp,sp,-64
42026566:	03054683          	lbu	a3,48(a0)
4202656a:	de06                	sw	ra,60(sp)
4202656c:	0005a623          	sw	zero,12(a1)
42026570:	00062623          	sw	zero,12(a2)
42026574:	872a                	mv	a4,a0
42026576:	87ae                	mv	a5,a1
42026578:	eab1                	bnez	a3,420265cc <__wrap_esp_audio_simple_dec_process+0x88>
4202657a:	43d4                	lw	a3,4(a5)
4202657c:	c6a1                	beqz	a3,420265c4 <__wrap_esp_audio_simple_dec_process+0x80>
4202657e:	0087c583          	lbu	a1,8(a5)
42026582:	edd5                	bnez	a1,4202663e <__wrap_esp_audio_simple_dec_process+0xfa>
42026584:	4805                	li	a6,1
42026586:	0b068263          	beq	a3,a6,4202662a <__wrap_esp_audio_simple_dec_process+0xe6>
4202658a:	0007ae83          	lw	t4,0(a5)
4202658e:	0087ae03          	lw	t3,8(a5)
42026592:	00c7a303          	lw	t1,12(a5)
42026596:	0107a883          	lw	a7,16(a5)
4202659a:	16fd                	addi	a3,a3,-1
4202659c:	086c                	addi	a1,sp,28
4202659e:	853a                	mv	a0,a4
420265a0:	c23e                	sw	a5,4(sp)
420265a2:	d036                	sw	a3,32(sp)
420265a4:	c43a                	sw	a4,8(sp)
420265a6:	ce76                	sw	t4,28(sp)
420265a8:	d272                	sw	t3,36(sp)
420265aa:	d41a                	sw	t1,40(sp)
420265ac:	d646                	sw	a7,44(sp)
420265ae:	d71ff0ef          	jal	4202631e <process_checked>
420265b2:	56a2                	lw	a3,40(sp)
420265b4:	4792                	lw	a5,4(sp)
420265b6:	c7d4                	sw	a3,12(a5)
420265b8:	e519                	bnez	a0,420265c6 <__wrap_esp_audio_simple_dec_process+0x82>
420265ba:	5602                	lw	a2,32(sp)
420265bc:	4722                	lw	a4,8(sp)
420265be:	4805                	li	a6,1
420265c0:	08c68563          	beq	a3,a2,4202664a <__wrap_esp_audio_simple_dec_process+0x106>
420265c4:	4501                	li	a0,0
420265c6:	50f2                	lw	ra,60(sp)
420265c8:	6121                	addi	sp,sp,64
420265ca:	8082                	ret
420265cc:	0085c683          	lbu	a3,8(a1)
420265d0:	03150513          	addi	a0,a0,49
420265d4:	4585                	li	a1,1
420265d6:	4801                	li	a6,0
420265d8:	4881                	li	a7,0
420265da:	d242                	sw	a6,36(sp)
420265dc:	d446                	sw	a7,40(sp)
420265de:	ce2a                	sw	a0,28(sp)
420265e0:	d02e                	sw	a1,32(sp)
420265e2:	c681                	beqz	a3,420265ea <__wrap_esp_audio_simple_dec_process+0xa6>
420265e4:	43d4                	lw	a3,4(a5)
420265e6:	0016b693          	seqz	a3,a3
420265ea:	02d10223          	sb	a3,36(sp)
420265ee:	4b94                	lw	a3,16(a5)
420265f0:	853a                	mv	a0,a4
420265f2:	086c                	addi	a1,sp,28
420265f4:	c63e                	sw	a5,12(sp)
420265f6:	c432                	sw	a2,8(sp)
420265f8:	c23a                	sw	a4,4(sp)
420265fa:	d636                	sw	a3,44(sp)
420265fc:	d23ff0ef          	jal	4202631e <process_checked>
42026600:	56a2                	lw	a3,40(sp)
42026602:	4712                	lw	a4,4(sp)
42026604:	4622                	lw	a2,8(sp)
42026606:	47b2                	lw	a5,12(sp)
42026608:	ee91                	bnez	a3,42026624 <__wrap_esp_audio_simple_dec_process+0xe0>
4202660a:	fd55                	bnez	a0,420265c6 <__wrap_esp_audio_simple_dec_process+0x82>
4202660c:	4654                	lw	a3,12(a2)
4202660e:	fec5                	bnez	a3,420265c6 <__wrap_esp_audio_simple_dec_process+0x82>
42026610:	03074683          	lbu	a3,48(a4)
42026614:	d2bd                	beqz	a3,4202657a <__wrap_esp_audio_simple_dec_process+0x36>
42026616:	bf45                	j	420265c6 <__wrap_esp_audio_simple_dec_process+0x82>
42026618:	0e01106f          	j	420376f8 <esp_audio_simple_dec_process>
4202661c:	41dc                	lw	a5,4(a1)
4202661e:	df85                	beqz	a5,42026556 <__wrap_esp_audio_simple_dec_process+0x12>
42026620:	556d                	li	a0,-5
42026622:	8082                	ret
42026624:	02070823          	sb	zero,48(a4)
42026628:	b7cd                	j	4202660a <__wrap_esp_audio_simple_dec_process+0xc6>
4202662a:	4390                	lw	a2,0(a5)
4202662c:	4501                	li	a0,0
4202662e:	00064603          	lbu	a2,0(a2)
42026632:	02d70823          	sb	a3,48(a4)
42026636:	02c708a3          	sb	a2,49(a4)
4202663a:	c7d4                	sw	a3,12(a5)
4202663c:	b769                	j	420265c6 <__wrap_esp_audio_simple_dec_process+0x82>
4202663e:	50f2                	lw	ra,60(sp)
42026640:	85be                	mv	a1,a5
42026642:	853a                	mv	a0,a4
42026644:	6121                	addi	sp,sp,64
42026646:	cd9ff06f          	j	4202631e <process_checked>
4202664a:	4390                	lw	a2,0(a5)
4202664c:	010685b3          	add	a1,a3,a6
42026650:	4501                	li	a0,0
42026652:	96b2                	add	a3,a3,a2
42026654:	0006c683          	lbu	a3,0(a3)
42026658:	03070823          	sb	a6,48(a4)
4202665c:	02d708a3          	sb	a3,49(a4)
42026660:	c7cc                	sw	a1,12(a5)
42026662:	b795                	j	420265c6 <__wrap_esp_audio_simple_dec_process+0x82>
