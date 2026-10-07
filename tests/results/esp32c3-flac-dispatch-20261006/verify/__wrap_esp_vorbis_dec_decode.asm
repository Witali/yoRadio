
idf\esp32c3-oled-native\build-flac-predictor\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420264d6 <__wrap_esp_vorbis_dec_decode>:
420264d6:	c169                	beqz	a0,42026598 <__wrap_esp_vorbis_dec_decode+0xc2>
420264d8:	c1e1                	beqz	a1,42026598 <__wrap_esp_vorbis_dec_decode+0xc2>
420264da:	ce5d                	beqz	a2,42026598 <__wrap_esp_vorbis_dec_decode+0xc2>
420264dc:	ced5                	beqz	a3,42026598 <__wrap_esp_vorbis_dec_decode+0xc2>
420264de:	0005a803          	lw	a6,0(a1)
420264e2:	0a080b63          	beqz	a6,42026598 <__wrap_esp_vorbis_dec_decode+0xc2>
420264e6:	421c                	lw	a5,0(a2)
420264e8:	cbc5                	beqz	a5,42026598 <__wrap_esp_vorbis_dec_decode+0xc2>
420264ea:	00052e83          	lw	t4,0(a0)
420264ee:	4701                	li	a4,0
420264f0:	000eaf03          	lw	t5,0(t4)
420264f4:	01cf2883          	lw	a7,28(t5)
420264f8:	0088a303          	lw	t1,8(a7)
420264fc:	fff30793          	addi	a5,t1,-1
42026500:	c781                	beqz	a5,42026508 <__wrap_esp_vorbis_dec_decode+0x32>
42026502:	8385                	srli	a5,a5,0x1
42026504:	0705                	addi	a4,a4,1
42026506:	fff5                	bnez	a5,42026502 <__wrap_esp_vorbis_dec_decode+0x2c>
42026508:	0045ae03          	lw	t3,4(a1)
4202650c:	060e0d63          	beqz	t3,42026586 <__wrap_esp_vorbis_dec_decode+0xb0>
42026510:	00084803          	lbu	a6,0(a6)
42026514:	00187793          	andi	a5,a6,1
42026518:	e7bd                	bnez	a5,42026586 <__wrap_esp_vorbis_dec_decode+0xb0>
4202651a:	5ffd                	li	t6,-1
4202651c:	00ef97b3          	sll	a5,t6,a4
42026520:	00185813          	srli	a6,a6,0x1
42026524:	fff7c793          	not	a5,a5
42026528:	0107f7b3          	and	a5,a5,a6
4202652c:	0467fd63          	bgeu	a5,t1,42026586 <__wrap_esp_vorbis_dec_decode+0xb0>
42026530:	01c8a803          	lw	a6,28(a7)
42026534:	0786                	slli	a5,a5,0x1
42026536:	97c2                	add	a5,a5,a6
42026538:	0007c803          	lbu	a6,0(a5)
4202653c:	010037b3          	snez	a5,a6
42026540:	0786                	slli	a5,a5,0x1
42026542:	97ba                	add	a5,a5,a4
42026544:	838d                	srli	a5,a5,0x3
42026546:	0785                	addi	a5,a5,1
42026548:	02fe6f63          	bltu	t3,a5,42026586 <__wrap_esp_vorbis_dec_decode+0xb0>
4202654c:	024ea783          	lw	a5,36(t4)
42026550:	03f78b63          	beq	a5,t6,42026586 <__wrap_esp_vorbis_dec_decode+0xb0>
42026554:	030ea703          	lw	a4,48(t4)
42026558:	00281793          	slli	a5,a6,0x2
4202655c:	97c6                	add	a5,a5,a7
4202655e:	070a                	slli	a4,a4,0x2
42026560:	98ba                	add	a7,a7,a4
42026562:	0008a703          	lw	a4,0(a7)
42026566:	439c                	lw	a5,0(a5)
42026568:	004f2883          	lw	a7,4(t5)
4202656c:	00462803          	lw	a6,4(a2)
42026570:	973e                	add	a4,a4,a5
42026572:	41f75793          	srai	a5,a4,0x1f
42026576:	8b8d                	andi	a5,a5,3
42026578:	97ba                	add	a5,a5,a4
4202657a:	8789                	srai	a5,a5,0x2
4202657c:	031787b3          	mul	a5,a5,a7
42026580:	0786                	slli	a5,a5,0x1
42026582:	00f86463          	bltu	a6,a5,4202658a <__wrap_esp_vorbis_dec_decode+0xb4>
42026586:	19a2406f          	j	4204a720 <esp_vorbis_dec_decode>
4202658a:	0005a423          	sw	zero,8(a1)
4202658e:	00062623          	sw	zero,12(a2)
42026592:	c61c                	sw	a5,8(a2)
42026594:	5561                	li	a0,-8
42026596:	8082                	ret
42026598:	556d                	li	a0,-5
4202659a:	8082                	ret
