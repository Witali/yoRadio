
idf\esp32c3-oled-native\build-rx-owner\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026634 <__wrap_esp_vorbis_dec_decode>:
42026634:	c169                	beqz	a0,420266f6 <__wrap_esp_vorbis_dec_decode+0xc2>
42026636:	c1e1                	beqz	a1,420266f6 <__wrap_esp_vorbis_dec_decode+0xc2>
42026638:	ce5d                	beqz	a2,420266f6 <__wrap_esp_vorbis_dec_decode+0xc2>
4202663a:	ced5                	beqz	a3,420266f6 <__wrap_esp_vorbis_dec_decode+0xc2>
4202663c:	0005a803          	lw	a6,0(a1)
42026640:	0a080b63          	beqz	a6,420266f6 <__wrap_esp_vorbis_dec_decode+0xc2>
42026644:	421c                	lw	a5,0(a2)
42026646:	cbc5                	beqz	a5,420266f6 <__wrap_esp_vorbis_dec_decode+0xc2>
42026648:	00052e83          	lw	t4,0(a0)
4202664c:	4701                	li	a4,0
4202664e:	000eaf03          	lw	t5,0(t4)
42026652:	01cf2883          	lw	a7,28(t5)
42026656:	0088a303          	lw	t1,8(a7)
4202665a:	fff30793          	addi	a5,t1,-1
4202665e:	c781                	beqz	a5,42026666 <__wrap_esp_vorbis_dec_decode+0x32>
42026660:	8385                	srli	a5,a5,0x1
42026662:	0705                	addi	a4,a4,1
42026664:	fff5                	bnez	a5,42026660 <__wrap_esp_vorbis_dec_decode+0x2c>
42026666:	0045ae03          	lw	t3,4(a1)
4202666a:	060e0d63          	beqz	t3,420266e4 <__wrap_esp_vorbis_dec_decode+0xb0>
4202666e:	00084803          	lbu	a6,0(a6)
42026672:	00187793          	andi	a5,a6,1
42026676:	e7bd                	bnez	a5,420266e4 <__wrap_esp_vorbis_dec_decode+0xb0>
42026678:	5ffd                	li	t6,-1
4202667a:	00ef97b3          	sll	a5,t6,a4
4202667e:	00185813          	srli	a6,a6,0x1
42026682:	fff7c793          	not	a5,a5
42026686:	0107f7b3          	and	a5,a5,a6
4202668a:	0467fd63          	bgeu	a5,t1,420266e4 <__wrap_esp_vorbis_dec_decode+0xb0>
4202668e:	01c8a803          	lw	a6,28(a7)
42026692:	0786                	slli	a5,a5,0x1
42026694:	97c2                	add	a5,a5,a6
42026696:	0007c803          	lbu	a6,0(a5)
4202669a:	010037b3          	snez	a5,a6
4202669e:	0786                	slli	a5,a5,0x1
420266a0:	97ba                	add	a5,a5,a4
420266a2:	838d                	srli	a5,a5,0x3
420266a4:	0785                	addi	a5,a5,1
420266a6:	02fe6f63          	bltu	t3,a5,420266e4 <__wrap_esp_vorbis_dec_decode+0xb0>
420266aa:	024ea783          	lw	a5,36(t4)
420266ae:	03f78b63          	beq	a5,t6,420266e4 <__wrap_esp_vorbis_dec_decode+0xb0>
420266b2:	030ea703          	lw	a4,48(t4)
420266b6:	00281793          	slli	a5,a6,0x2
420266ba:	97c6                	add	a5,a5,a7
420266bc:	070a                	slli	a4,a4,0x2
420266be:	98ba                	add	a7,a7,a4
420266c0:	0008a703          	lw	a4,0(a7)
420266c4:	439c                	lw	a5,0(a5)
420266c6:	004f2883          	lw	a7,4(t5)
420266ca:	00462803          	lw	a6,4(a2)
420266ce:	973e                	add	a4,a4,a5
420266d0:	41f75793          	srai	a5,a4,0x1f
420266d4:	8b8d                	andi	a5,a5,3
420266d6:	97ba                	add	a5,a5,a4
420266d8:	8789                	srai	a5,a5,0x2
420266da:	031787b3          	mul	a5,a5,a7
420266de:	0786                	slli	a5,a5,0x1
420266e0:	00f86463          	bltu	a6,a5,420266e8 <__wrap_esp_vorbis_dec_decode+0xb4>
420266e4:	5e82406f          	j	4204accc <esp_vorbis_dec_decode>
420266e8:	0005a423          	sw	zero,8(a1)
420266ec:	00062623          	sw	zero,12(a2)
420266f0:	c61c                	sw	a5,8(a2)
420266f2:	5561                	li	a0,-8
420266f4:	8082                	ret
420266f6:	556d                	li	a0,-5
420266f8:	8082                	ret
