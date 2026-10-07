
idf\esp32c3-oled-native\build-flac-predictor\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420264de <__wrap_esp_vorbis_dec_decode>:
420264de:	c169                	beqz	a0,420265a0 <__wrap_esp_vorbis_dec_decode+0xc2>
420264e0:	c1e1                	beqz	a1,420265a0 <__wrap_esp_vorbis_dec_decode+0xc2>
420264e2:	ce5d                	beqz	a2,420265a0 <__wrap_esp_vorbis_dec_decode+0xc2>
420264e4:	ced5                	beqz	a3,420265a0 <__wrap_esp_vorbis_dec_decode+0xc2>
420264e6:	0005a803          	lw	a6,0(a1)
420264ea:	0a080b63          	beqz	a6,420265a0 <__wrap_esp_vorbis_dec_decode+0xc2>
420264ee:	421c                	lw	a5,0(a2)
420264f0:	cbc5                	beqz	a5,420265a0 <__wrap_esp_vorbis_dec_decode+0xc2>
420264f2:	00052e83          	lw	t4,0(a0)
420264f6:	4701                	li	a4,0
420264f8:	000eaf03          	lw	t5,0(t4)
420264fc:	01cf2883          	lw	a7,28(t5)
42026500:	0088a303          	lw	t1,8(a7)
42026504:	fff30793          	addi	a5,t1,-1
42026508:	c781                	beqz	a5,42026510 <__wrap_esp_vorbis_dec_decode+0x32>
4202650a:	8385                	srli	a5,a5,0x1
4202650c:	0705                	addi	a4,a4,1
4202650e:	fff5                	bnez	a5,4202650a <__wrap_esp_vorbis_dec_decode+0x2c>
42026510:	0045ae03          	lw	t3,4(a1)
42026514:	060e0d63          	beqz	t3,4202658e <__wrap_esp_vorbis_dec_decode+0xb0>
42026518:	00084803          	lbu	a6,0(a6)
4202651c:	00187793          	andi	a5,a6,1
42026520:	e7bd                	bnez	a5,4202658e <__wrap_esp_vorbis_dec_decode+0xb0>
42026522:	5ffd                	li	t6,-1
42026524:	00ef97b3          	sll	a5,t6,a4
42026528:	00185813          	srli	a6,a6,0x1
4202652c:	fff7c793          	not	a5,a5
42026530:	0107f7b3          	and	a5,a5,a6
42026534:	0467fd63          	bgeu	a5,t1,4202658e <__wrap_esp_vorbis_dec_decode+0xb0>
42026538:	01c8a803          	lw	a6,28(a7)
4202653c:	0786                	slli	a5,a5,0x1
4202653e:	97c2                	add	a5,a5,a6
42026540:	0007c803          	lbu	a6,0(a5)
42026544:	010037b3          	snez	a5,a6
42026548:	0786                	slli	a5,a5,0x1
4202654a:	97ba                	add	a5,a5,a4
4202654c:	838d                	srli	a5,a5,0x3
4202654e:	0785                	addi	a5,a5,1
42026550:	02fe6f63          	bltu	t3,a5,4202658e <__wrap_esp_vorbis_dec_decode+0xb0>
42026554:	024ea783          	lw	a5,36(t4)
42026558:	03f78b63          	beq	a5,t6,4202658e <__wrap_esp_vorbis_dec_decode+0xb0>
4202655c:	030ea703          	lw	a4,48(t4)
42026560:	00281793          	slli	a5,a6,0x2
42026564:	97c6                	add	a5,a5,a7
42026566:	070a                	slli	a4,a4,0x2
42026568:	98ba                	add	a7,a7,a4
4202656a:	0008a703          	lw	a4,0(a7)
4202656e:	439c                	lw	a5,0(a5)
42026570:	004f2883          	lw	a7,4(t5)
42026574:	00462803          	lw	a6,4(a2)
42026578:	973e                	add	a4,a4,a5
4202657a:	41f75793          	srai	a5,a4,0x1f
4202657e:	8b8d                	andi	a5,a5,3
42026580:	97ba                	add	a5,a5,a4
42026582:	8789                	srai	a5,a5,0x2
42026584:	031787b3          	mul	a5,a5,a7
42026588:	0786                	slli	a5,a5,0x1
4202658a:	00f86463          	bltu	a6,a5,42026592 <__wrap_esp_vorbis_dec_decode+0xb4>
4202658e:	5682406f          	j	4204aaf6 <esp_vorbis_dec_decode>
42026592:	0005a423          	sw	zero,8(a1)
42026596:	00062623          	sw	zero,12(a2)
4202659a:	c61c                	sw	a5,8(a2)
4202659c:	5561                	li	a0,-8
4202659e:	8082                	ret
420265a0:	556d                	li	a0,-5
420265a2:	8082                	ret
