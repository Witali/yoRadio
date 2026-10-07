
idf\esp32c3-oled-native\build-rx-copy\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420264d2 <__wrap_esp_vorbis_dec_decode>:
420264d2:	c169                	beqz	a0,42026594 <__wrap_esp_vorbis_dec_decode+0xc2>
420264d4:	c1e1                	beqz	a1,42026594 <__wrap_esp_vorbis_dec_decode+0xc2>
420264d6:	ce5d                	beqz	a2,42026594 <__wrap_esp_vorbis_dec_decode+0xc2>
420264d8:	ced5                	beqz	a3,42026594 <__wrap_esp_vorbis_dec_decode+0xc2>
420264da:	0005a803          	lw	a6,0(a1)
420264de:	0a080b63          	beqz	a6,42026594 <__wrap_esp_vorbis_dec_decode+0xc2>
420264e2:	421c                	lw	a5,0(a2)
420264e4:	cbc5                	beqz	a5,42026594 <__wrap_esp_vorbis_dec_decode+0xc2>
420264e6:	00052e83          	lw	t4,0(a0)
420264ea:	4701                	li	a4,0
420264ec:	000eaf03          	lw	t5,0(t4)
420264f0:	01cf2883          	lw	a7,28(t5)
420264f4:	0088a303          	lw	t1,8(a7)
420264f8:	fff30793          	addi	a5,t1,-1
420264fc:	c781                	beqz	a5,42026504 <__wrap_esp_vorbis_dec_decode+0x32>
420264fe:	8385                	srli	a5,a5,0x1
42026500:	0705                	addi	a4,a4,1
42026502:	fff5                	bnez	a5,420264fe <__wrap_esp_vorbis_dec_decode+0x2c>
42026504:	0045ae03          	lw	t3,4(a1)
42026508:	060e0d63          	beqz	t3,42026582 <__wrap_esp_vorbis_dec_decode+0xb0>
4202650c:	00084803          	lbu	a6,0(a6)
42026510:	00187793          	andi	a5,a6,1
42026514:	e7bd                	bnez	a5,42026582 <__wrap_esp_vorbis_dec_decode+0xb0>
42026516:	5ffd                	li	t6,-1
42026518:	00ef97b3          	sll	a5,t6,a4
4202651c:	00185813          	srli	a6,a6,0x1
42026520:	fff7c793          	not	a5,a5
42026524:	0107f7b3          	and	a5,a5,a6
42026528:	0467fd63          	bgeu	a5,t1,42026582 <__wrap_esp_vorbis_dec_decode+0xb0>
4202652c:	01c8a803          	lw	a6,28(a7)
42026530:	0786                	slli	a5,a5,0x1
42026532:	97c2                	add	a5,a5,a6
42026534:	0007c803          	lbu	a6,0(a5)
42026538:	010037b3          	snez	a5,a6
4202653c:	0786                	slli	a5,a5,0x1
4202653e:	97ba                	add	a5,a5,a4
42026540:	838d                	srli	a5,a5,0x3
42026542:	0785                	addi	a5,a5,1
42026544:	02fe6f63          	bltu	t3,a5,42026582 <__wrap_esp_vorbis_dec_decode+0xb0>
42026548:	024ea783          	lw	a5,36(t4)
4202654c:	03f78b63          	beq	a5,t6,42026582 <__wrap_esp_vorbis_dec_decode+0xb0>
42026550:	030ea703          	lw	a4,48(t4)
42026554:	00281793          	slli	a5,a6,0x2
42026558:	97c6                	add	a5,a5,a7
4202655a:	070a                	slli	a4,a4,0x2
4202655c:	98ba                	add	a7,a7,a4
4202655e:	0008a703          	lw	a4,0(a7)
42026562:	439c                	lw	a5,0(a5)
42026564:	004f2883          	lw	a7,4(t5)
42026568:	00462803          	lw	a6,4(a2)
4202656c:	973e                	add	a4,a4,a5
4202656e:	41f75793          	srai	a5,a4,0x1f
42026572:	8b8d                	andi	a5,a5,3
42026574:	97ba                	add	a5,a5,a4
42026576:	8789                	srai	a5,a5,0x2
42026578:	031787b3          	mul	a5,a5,a7
4202657c:	0786                	slli	a5,a5,0x1
4202657e:	00f86463          	bltu	a6,a5,42026586 <__wrap_esp_vorbis_dec_decode+0xb4>
42026582:	19a2406f          	j	4204a71c <esp_vorbis_dec_decode>
42026586:	0005a423          	sw	zero,8(a1)
4202658a:	00062623          	sw	zero,12(a2)
4202658e:	c61c                	sw	a5,8(a2)
42026590:	5561                	li	a0,-8
42026592:	8082                	ret
42026594:	556d                	li	a0,-5
42026596:	8082                	ret
