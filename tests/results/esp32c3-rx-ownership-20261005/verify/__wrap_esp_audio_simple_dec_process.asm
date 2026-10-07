
idf\esp32c3-oled-native\build-rx-owner\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4202648c <__wrap_esp_audio_simple_dec_process>:
4202648c:	0015b793          	seqz	a5,a1
42026490:	00163713          	seqz	a4,a2
42026494:	8fd9                	or	a5,a5,a4
42026496:	ebe9                	bnez	a5,42026568 <__wrap_esp_audio_simple_dec_process+0xdc>
42026498:	c961                	beqz	a0,42026568 <__wrap_esp_audio_simple_dec_process+0xdc>
4202649a:	419c                	lw	a5,0(a1)
4202649c:	c7e1                	beqz	a5,42026564 <__wrap_esp_audio_simple_dec_process+0xd8>
4202649e:	5558                	lw	a4,44(a0)
420264a0:	204747b7          	lui	a5,0x20474
420264a4:	74f78793          	addi	a5,a5,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
420264a8:	0af71c63          	bne	a4,a5,42026560 <__wrap_esp_audio_simple_dec_process+0xd4>
420264ac:	7139                	addi	sp,sp,-64
420264ae:	03054683          	lbu	a3,48(a0)
420264b2:	de06                	sw	ra,60(sp)
420264b4:	0005a623          	sw	zero,12(a1)
420264b8:	00062623          	sw	zero,12(a2)
420264bc:	872a                	mv	a4,a0
420264be:	87ae                	mv	a5,a1
420264c0:	eab1                	bnez	a3,42026514 <__wrap_esp_audio_simple_dec_process+0x88>
420264c2:	43d4                	lw	a3,4(a5)
420264c4:	c6a1                	beqz	a3,4202650c <__wrap_esp_audio_simple_dec_process+0x80>
420264c6:	0087c583          	lbu	a1,8(a5)
420264ca:	edd5                	bnez	a1,42026586 <__wrap_esp_audio_simple_dec_process+0xfa>
420264cc:	4805                	li	a6,1
420264ce:	0b068263          	beq	a3,a6,42026572 <__wrap_esp_audio_simple_dec_process+0xe6>
420264d2:	0007ae83          	lw	t4,0(a5)
420264d6:	0087ae03          	lw	t3,8(a5)
420264da:	00c7a303          	lw	t1,12(a5)
420264de:	0107a883          	lw	a7,16(a5)
420264e2:	16fd                	addi	a3,a3,-1
420264e4:	086c                	addi	a1,sp,28
420264e6:	853a                	mv	a0,a4
420264e8:	c23e                	sw	a5,4(sp)
420264ea:	d036                	sw	a3,32(sp)
420264ec:	c43a                	sw	a4,8(sp)
420264ee:	ce76                	sw	t4,28(sp)
420264f0:	d272                	sw	t3,36(sp)
420264f2:	d41a                	sw	t1,40(sp)
420264f4:	d646                	sw	a7,44(sp)
420264f6:	d71ff0ef          	jal	42026266 <process_checked>
420264fa:	56a2                	lw	a3,40(sp)
420264fc:	4792                	lw	a5,4(sp)
420264fe:	c7d4                	sw	a3,12(a5)
42026500:	e519                	bnez	a0,4202650e <__wrap_esp_audio_simple_dec_process+0x82>
42026502:	5602                	lw	a2,32(sp)
42026504:	4722                	lw	a4,8(sp)
42026506:	4805                	li	a6,1
42026508:	08c68563          	beq	a3,a2,42026592 <__wrap_esp_audio_simple_dec_process+0x106>
4202650c:	4501                	li	a0,0
4202650e:	50f2                	lw	ra,60(sp)
42026510:	6121                	addi	sp,sp,64
42026512:	8082                	ret
42026514:	0085c683          	lbu	a3,8(a1)
42026518:	03150513          	addi	a0,a0,49
4202651c:	4585                	li	a1,1
4202651e:	4801                	li	a6,0
42026520:	4881                	li	a7,0
42026522:	d242                	sw	a6,36(sp)
42026524:	d446                	sw	a7,40(sp)
42026526:	ce2a                	sw	a0,28(sp)
42026528:	d02e                	sw	a1,32(sp)
4202652a:	c681                	beqz	a3,42026532 <__wrap_esp_audio_simple_dec_process+0xa6>
4202652c:	43d4                	lw	a3,4(a5)
4202652e:	0016b693          	seqz	a3,a3
42026532:	02d10223          	sb	a3,36(sp)
42026536:	4b94                	lw	a3,16(a5)
42026538:	853a                	mv	a0,a4
4202653a:	086c                	addi	a1,sp,28
4202653c:	c63e                	sw	a5,12(sp)
4202653e:	c432                	sw	a2,8(sp)
42026540:	c23a                	sw	a4,4(sp)
42026542:	d636                	sw	a3,44(sp)
42026544:	d23ff0ef          	jal	42026266 <process_checked>
42026548:	56a2                	lw	a3,40(sp)
4202654a:	4712                	lw	a4,4(sp)
4202654c:	4622                	lw	a2,8(sp)
4202654e:	47b2                	lw	a5,12(sp)
42026550:	ee91                	bnez	a3,4202656c <__wrap_esp_audio_simple_dec_process+0xe0>
42026552:	fd55                	bnez	a0,4202650e <__wrap_esp_audio_simple_dec_process+0x82>
42026554:	4654                	lw	a3,12(a2)
42026556:	fec5                	bnez	a3,4202650e <__wrap_esp_audio_simple_dec_process+0x82>
42026558:	03074683          	lbu	a3,48(a4)
4202655c:	d2bd                	beqz	a3,420264c2 <__wrap_esp_audio_simple_dec_process+0x36>
4202655e:	bf45                	j	4202650e <__wrap_esp_audio_simple_dec_process+0x82>
42026560:	6751006f          	j	420373d4 <esp_audio_simple_dec_process>
42026564:	41dc                	lw	a5,4(a1)
42026566:	df85                	beqz	a5,4202649e <__wrap_esp_audio_simple_dec_process+0x12>
42026568:	556d                	li	a0,-5
4202656a:	8082                	ret
4202656c:	02070823          	sb	zero,48(a4)
42026570:	b7cd                	j	42026552 <__wrap_esp_audio_simple_dec_process+0xc6>
42026572:	4390                	lw	a2,0(a5)
42026574:	4501                	li	a0,0
42026576:	00064603          	lbu	a2,0(a2)
4202657a:	02d70823          	sb	a3,48(a4)
4202657e:	02c708a3          	sb	a2,49(a4)
42026582:	c7d4                	sw	a3,12(a5)
42026584:	b769                	j	4202650e <__wrap_esp_audio_simple_dec_process+0x82>
42026586:	50f2                	lw	ra,60(sp)
42026588:	85be                	mv	a1,a5
4202658a:	853a                	mv	a0,a4
4202658c:	6121                	addi	sp,sp,64
4202658e:	cd9ff06f          	j	42026266 <process_checked>
42026592:	4390                	lw	a2,0(a5)
42026594:	010685b3          	add	a1,a3,a6
42026598:	4501                	li	a0,0
4202659a:	96b2                	add	a3,a3,a2
4202659c:	0006c683          	lbu	a3,0(a3)
420265a0:	03070823          	sb	a6,48(a4)
420265a4:	02d708a3          	sb	a3,49(a4)
420265a8:	c7cc                	sw	a1,12(a5)
420265aa:	b795                	j	4202650e <__wrap_esp_audio_simple_dec_process+0x82>
