
idf\esp32c3-oled-native\build-heap-fragment\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026664 <__wrap_esp_vorbis_dec_decode>:
42026664:	c169                	beqz	a0,42026726 <__wrap_esp_vorbis_dec_decode+0xc2>
42026666:	c1e1                	beqz	a1,42026726 <__wrap_esp_vorbis_dec_decode+0xc2>
42026668:	ce5d                	beqz	a2,42026726 <__wrap_esp_vorbis_dec_decode+0xc2>
4202666a:	ced5                	beqz	a3,42026726 <__wrap_esp_vorbis_dec_decode+0xc2>
4202666c:	0005a803          	lw	a6,0(a1)
42026670:	0a080b63          	beqz	a6,42026726 <__wrap_esp_vorbis_dec_decode+0xc2>
42026674:	421c                	lw	a5,0(a2)
42026676:	cbc5                	beqz	a5,42026726 <__wrap_esp_vorbis_dec_decode+0xc2>
42026678:	00052e83          	lw	t4,0(a0)
4202667c:	4701                	li	a4,0
4202667e:	000eaf03          	lw	t5,0(t4)
42026682:	01cf2883          	lw	a7,28(t5)
42026686:	0088a303          	lw	t1,8(a7)
4202668a:	fff30793          	addi	a5,t1,-1
4202668e:	c781                	beqz	a5,42026696 <__wrap_esp_vorbis_dec_decode+0x32>
42026690:	8385                	srli	a5,a5,0x1
42026692:	0705                	addi	a4,a4,1
42026694:	fff5                	bnez	a5,42026690 <__wrap_esp_vorbis_dec_decode+0x2c>
42026696:	0045ae03          	lw	t3,4(a1)
4202669a:	060e0d63          	beqz	t3,42026714 <__wrap_esp_vorbis_dec_decode+0xb0>
4202669e:	00084803          	lbu	a6,0(a6)
420266a2:	00187793          	andi	a5,a6,1
420266a6:	e7bd                	bnez	a5,42026714 <__wrap_esp_vorbis_dec_decode+0xb0>
420266a8:	5ffd                	li	t6,-1
420266aa:	00ef97b3          	sll	a5,t6,a4
420266ae:	00185813          	srli	a6,a6,0x1
420266b2:	fff7c793          	not	a5,a5
420266b6:	0107f7b3          	and	a5,a5,a6
420266ba:	0467fd63          	bgeu	a5,t1,42026714 <__wrap_esp_vorbis_dec_decode+0xb0>
420266be:	01c8a803          	lw	a6,28(a7)
420266c2:	0786                	slli	a5,a5,0x1
420266c4:	97c2                	add	a5,a5,a6
420266c6:	0007c803          	lbu	a6,0(a5)
420266ca:	010037b3          	snez	a5,a6
420266ce:	0786                	slli	a5,a5,0x1
420266d0:	97ba                	add	a5,a5,a4
420266d2:	838d                	srli	a5,a5,0x3
420266d4:	0785                	addi	a5,a5,1
420266d6:	02fe6f63          	bltu	t3,a5,42026714 <__wrap_esp_vorbis_dec_decode+0xb0>
420266da:	024ea783          	lw	a5,36(t4)
420266de:	03f78b63          	beq	a5,t6,42026714 <__wrap_esp_vorbis_dec_decode+0xb0>
420266e2:	030ea703          	lw	a4,48(t4)
420266e6:	00281793          	slli	a5,a6,0x2
420266ea:	97c6                	add	a5,a5,a7
420266ec:	070a                	slli	a4,a4,0x2
420266ee:	98ba                	add	a7,a7,a4
420266f0:	0008a703          	lw	a4,0(a7)
420266f4:	439c                	lw	a5,0(a5)
420266f6:	004f2883          	lw	a7,4(t5)
420266fa:	00462803          	lw	a6,4(a2)
420266fe:	973e                	add	a4,a4,a5
42026700:	41f75793          	srai	a5,a4,0x1f
42026704:	8b8d                	andi	a5,a5,3
42026706:	97ba                	add	a5,a5,a4
42026708:	8789                	srai	a5,a5,0x2
4202670a:	031787b3          	mul	a5,a5,a7
4202670e:	0786                	slli	a5,a5,0x1
42026710:	00f86463          	bltu	a6,a5,42026718 <__wrap_esp_vorbis_dec_decode+0xb4>
42026714:	4bf2206f          	j	420493d2 <esp_vorbis_dec_decode>
42026718:	0005a423          	sw	zero,8(a1)
4202671c:	00062623          	sw	zero,12(a2)
42026720:	c61c                	sw	a5,8(a2)
42026722:	5561                	li	a0,-8
42026724:	8082                	ret
42026726:	556d                	li	a0,-5
42026728:	8082                	ret
