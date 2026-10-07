
idf\esp32c3-oled-native\build-rx-owner\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026638 <__wrap_esp_vorbis_dec_decode>:
42026638:	c169                	beqz	a0,420266fa <__wrap_esp_vorbis_dec_decode+0xc2>
4202663a:	c1e1                	beqz	a1,420266fa <__wrap_esp_vorbis_dec_decode+0xc2>
4202663c:	ce5d                	beqz	a2,420266fa <__wrap_esp_vorbis_dec_decode+0xc2>
4202663e:	ced5                	beqz	a3,420266fa <__wrap_esp_vorbis_dec_decode+0xc2>
42026640:	0005a803          	lw	a6,0(a1)
42026644:	0a080b63          	beqz	a6,420266fa <__wrap_esp_vorbis_dec_decode+0xc2>
42026648:	421c                	lw	a5,0(a2)
4202664a:	cbc5                	beqz	a5,420266fa <__wrap_esp_vorbis_dec_decode+0xc2>
4202664c:	00052e83          	lw	t4,0(a0)
42026650:	4701                	li	a4,0
42026652:	000eaf03          	lw	t5,0(t4)
42026656:	01cf2883          	lw	a7,28(t5)
4202665a:	0088a303          	lw	t1,8(a7)
4202665e:	fff30793          	addi	a5,t1,-1
42026662:	c781                	beqz	a5,4202666a <__wrap_esp_vorbis_dec_decode+0x32>
42026664:	8385                	srli	a5,a5,0x1
42026666:	0705                	addi	a4,a4,1
42026668:	fff5                	bnez	a5,42026664 <__wrap_esp_vorbis_dec_decode+0x2c>
4202666a:	0045ae03          	lw	t3,4(a1)
4202666e:	060e0d63          	beqz	t3,420266e8 <__wrap_esp_vorbis_dec_decode+0xb0>
42026672:	00084803          	lbu	a6,0(a6)
42026676:	00187793          	andi	a5,a6,1
4202667a:	e7bd                	bnez	a5,420266e8 <__wrap_esp_vorbis_dec_decode+0xb0>
4202667c:	5ffd                	li	t6,-1
4202667e:	00ef97b3          	sll	a5,t6,a4
42026682:	00185813          	srli	a6,a6,0x1
42026686:	fff7c793          	not	a5,a5
4202668a:	0107f7b3          	and	a5,a5,a6
4202668e:	0467fd63          	bgeu	a5,t1,420266e8 <__wrap_esp_vorbis_dec_decode+0xb0>
42026692:	01c8a803          	lw	a6,28(a7)
42026696:	0786                	slli	a5,a5,0x1
42026698:	97c2                	add	a5,a5,a6
4202669a:	0007c803          	lbu	a6,0(a5)
4202669e:	010037b3          	snez	a5,a6
420266a2:	0786                	slli	a5,a5,0x1
420266a4:	97ba                	add	a5,a5,a4
420266a6:	838d                	srli	a5,a5,0x3
420266a8:	0785                	addi	a5,a5,1
420266aa:	02fe6f63          	bltu	t3,a5,420266e8 <__wrap_esp_vorbis_dec_decode+0xb0>
420266ae:	024ea783          	lw	a5,36(t4)
420266b2:	03f78b63          	beq	a5,t6,420266e8 <__wrap_esp_vorbis_dec_decode+0xb0>
420266b6:	030ea703          	lw	a4,48(t4)
420266ba:	00281793          	slli	a5,a6,0x2
420266be:	97c6                	add	a5,a5,a7
420266c0:	070a                	slli	a4,a4,0x2
420266c2:	98ba                	add	a7,a7,a4
420266c4:	0008a703          	lw	a4,0(a7)
420266c8:	439c                	lw	a5,0(a5)
420266ca:	004f2883          	lw	a7,4(t5)
420266ce:	00462803          	lw	a6,4(a2)
420266d2:	973e                	add	a4,a4,a5
420266d4:	41f75793          	srai	a5,a4,0x1f
420266d8:	8b8d                	andi	a5,a5,3
420266da:	97ba                	add	a5,a5,a4
420266dc:	8789                	srai	a5,a5,0x2
420266de:	031787b3          	mul	a5,a5,a7
420266e2:	0786                	slli	a5,a5,0x1
420266e4:	00f86463          	bltu	a6,a5,420266ec <__wrap_esp_vorbis_dec_decode+0xb4>
420266e8:	6642406f          	j	4204ad4c <esp_vorbis_dec_decode>
420266ec:	0005a423          	sw	zero,8(a1)
420266f0:	00062623          	sw	zero,12(a2)
420266f4:	c61c                	sw	a5,8(a2)
420266f6:	5561                	li	a0,-8
420266f8:	8082                	ret
420266fa:	556d                	li	a0,-5
420266fc:	8082                	ret
