
idf\esp32c3-oled-native\build-custom-terminal\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4202646a <__wrap_esp_vorbis_dec_decode>:
4202646a:	c169                	beqz	a0,4202652c <__wrap_esp_vorbis_dec_decode+0xc2>
4202646c:	c1e1                	beqz	a1,4202652c <__wrap_esp_vorbis_dec_decode+0xc2>
4202646e:	ce5d                	beqz	a2,4202652c <__wrap_esp_vorbis_dec_decode+0xc2>
42026470:	ced5                	beqz	a3,4202652c <__wrap_esp_vorbis_dec_decode+0xc2>
42026472:	0005a803          	lw	a6,0(a1)
42026476:	0a080b63          	beqz	a6,4202652c <__wrap_esp_vorbis_dec_decode+0xc2>
4202647a:	421c                	lw	a5,0(a2)
4202647c:	cbc5                	beqz	a5,4202652c <__wrap_esp_vorbis_dec_decode+0xc2>
4202647e:	00052e83          	lw	t4,0(a0)
42026482:	4701                	li	a4,0
42026484:	000eaf03          	lw	t5,0(t4)
42026488:	01cf2883          	lw	a7,28(t5)
4202648c:	0088a303          	lw	t1,8(a7)
42026490:	fff30793          	addi	a5,t1,-1
42026494:	c781                	beqz	a5,4202649c <__wrap_esp_vorbis_dec_decode+0x32>
42026496:	8385                	srli	a5,a5,0x1
42026498:	0705                	addi	a4,a4,1
4202649a:	fff5                	bnez	a5,42026496 <__wrap_esp_vorbis_dec_decode+0x2c>
4202649c:	0045ae03          	lw	t3,4(a1)
420264a0:	060e0d63          	beqz	t3,4202651a <__wrap_esp_vorbis_dec_decode+0xb0>
420264a4:	00084803          	lbu	a6,0(a6)
420264a8:	00187793          	andi	a5,a6,1
420264ac:	e7bd                	bnez	a5,4202651a <__wrap_esp_vorbis_dec_decode+0xb0>
420264ae:	5ffd                	li	t6,-1
420264b0:	00ef97b3          	sll	a5,t6,a4
420264b4:	00185813          	srli	a6,a6,0x1
420264b8:	fff7c793          	not	a5,a5
420264bc:	0107f7b3          	and	a5,a5,a6
420264c0:	0467fd63          	bgeu	a5,t1,4202651a <__wrap_esp_vorbis_dec_decode+0xb0>
420264c4:	01c8a803          	lw	a6,28(a7)
420264c8:	0786                	slli	a5,a5,0x1
420264ca:	97c2                	add	a5,a5,a6
420264cc:	0007c803          	lbu	a6,0(a5)
420264d0:	010037b3          	snez	a5,a6
420264d4:	0786                	slli	a5,a5,0x1
420264d6:	97ba                	add	a5,a5,a4
420264d8:	838d                	srli	a5,a5,0x3
420264da:	0785                	addi	a5,a5,1
420264dc:	02fe6f63          	bltu	t3,a5,4202651a <__wrap_esp_vorbis_dec_decode+0xb0>
420264e0:	024ea783          	lw	a5,36(t4)
420264e4:	03f78b63          	beq	a5,t6,4202651a <__wrap_esp_vorbis_dec_decode+0xb0>
420264e8:	030ea703          	lw	a4,48(t4)
420264ec:	00281793          	slli	a5,a6,0x2
420264f0:	97c6                	add	a5,a5,a7
420264f2:	070a                	slli	a4,a4,0x2
420264f4:	98ba                	add	a7,a7,a4
420264f6:	0008a703          	lw	a4,0(a7)
420264fa:	439c                	lw	a5,0(a5)
420264fc:	004f2883          	lw	a7,4(t5)
42026500:	00462803          	lw	a6,4(a2)
42026504:	973e                	add	a4,a4,a5
42026506:	41f75793          	srai	a5,a4,0x1f
4202650a:	8b8d                	andi	a5,a5,3
4202650c:	97ba                	add	a5,a5,a4
4202650e:	8789                	srai	a5,a5,0x2
42026510:	031787b3          	mul	a5,a5,a7
42026514:	0786                	slli	a5,a5,0x1
42026516:	00f86463          	bltu	a6,a5,4202651e <__wrap_esp_vorbis_dec_decode+0xb4>
4202651a:	6042206f          	j	42048b1e <esp_vorbis_dec_decode>
4202651e:	0005a423          	sw	zero,8(a1)
42026522:	00062623          	sw	zero,12(a2)
42026526:	c61c                	sw	a5,8(a2)
42026528:	5561                	li	a0,-8
4202652a:	8082                	ret
4202652c:	556d                	li	a0,-5
4202652e:	8082                	ret
