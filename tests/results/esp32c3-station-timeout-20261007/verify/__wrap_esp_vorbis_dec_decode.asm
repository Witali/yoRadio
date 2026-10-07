
idf\esp32c3-oled-native\build-connect-retry\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026744 <__wrap_esp_vorbis_dec_decode>:
42026744:	c169                	beqz	a0,42026806 <__wrap_esp_vorbis_dec_decode+0xc2>
42026746:	c1e1                	beqz	a1,42026806 <__wrap_esp_vorbis_dec_decode+0xc2>
42026748:	ce5d                	beqz	a2,42026806 <__wrap_esp_vorbis_dec_decode+0xc2>
4202674a:	ced5                	beqz	a3,42026806 <__wrap_esp_vorbis_dec_decode+0xc2>
4202674c:	0005a803          	lw	a6,0(a1)
42026750:	0a080b63          	beqz	a6,42026806 <__wrap_esp_vorbis_dec_decode+0xc2>
42026754:	421c                	lw	a5,0(a2)
42026756:	cbc5                	beqz	a5,42026806 <__wrap_esp_vorbis_dec_decode+0xc2>
42026758:	00052e83          	lw	t4,0(a0)
4202675c:	4701                	li	a4,0
4202675e:	000eaf03          	lw	t5,0(t4)
42026762:	01cf2883          	lw	a7,28(t5)
42026766:	0088a303          	lw	t1,8(a7)
4202676a:	fff30793          	addi	a5,t1,-1
4202676e:	c781                	beqz	a5,42026776 <__wrap_esp_vorbis_dec_decode+0x32>
42026770:	8385                	srli	a5,a5,0x1
42026772:	0705                	addi	a4,a4,1
42026774:	fff5                	bnez	a5,42026770 <__wrap_esp_vorbis_dec_decode+0x2c>
42026776:	0045ae03          	lw	t3,4(a1)
4202677a:	060e0d63          	beqz	t3,420267f4 <__wrap_esp_vorbis_dec_decode+0xb0>
4202677e:	00084803          	lbu	a6,0(a6)
42026782:	00187793          	andi	a5,a6,1
42026786:	e7bd                	bnez	a5,420267f4 <__wrap_esp_vorbis_dec_decode+0xb0>
42026788:	5ffd                	li	t6,-1
4202678a:	00ef97b3          	sll	a5,t6,a4
4202678e:	00185813          	srli	a6,a6,0x1
42026792:	fff7c793          	not	a5,a5
42026796:	0107f7b3          	and	a5,a5,a6
4202679a:	0467fd63          	bgeu	a5,t1,420267f4 <__wrap_esp_vorbis_dec_decode+0xb0>
4202679e:	01c8a803          	lw	a6,28(a7)
420267a2:	0786                	slli	a5,a5,0x1
420267a4:	97c2                	add	a5,a5,a6
420267a6:	0007c803          	lbu	a6,0(a5)
420267aa:	010037b3          	snez	a5,a6
420267ae:	0786                	slli	a5,a5,0x1
420267b0:	97ba                	add	a5,a5,a4
420267b2:	838d                	srli	a5,a5,0x3
420267b4:	0785                	addi	a5,a5,1
420267b6:	02fe6f63          	bltu	t3,a5,420267f4 <__wrap_esp_vorbis_dec_decode+0xb0>
420267ba:	024ea783          	lw	a5,36(t4)
420267be:	03f78b63          	beq	a5,t6,420267f4 <__wrap_esp_vorbis_dec_decode+0xb0>
420267c2:	030ea703          	lw	a4,48(t4)
420267c6:	00281793          	slli	a5,a6,0x2
420267ca:	97c6                	add	a5,a5,a7
420267cc:	070a                	slli	a4,a4,0x2
420267ce:	98ba                	add	a7,a7,a4
420267d0:	0008a703          	lw	a4,0(a7)
420267d4:	439c                	lw	a5,0(a5)
420267d6:	004f2883          	lw	a7,4(t5)
420267da:	00462803          	lw	a6,4(a2)
420267de:	973e                	add	a4,a4,a5
420267e0:	41f75793          	srai	a5,a4,0x1f
420267e4:	8b8d                	andi	a5,a5,3
420267e6:	97ba                	add	a5,a5,a4
420267e8:	8789                	srai	a5,a5,0x2
420267ea:	031787b3          	mul	a5,a5,a7
420267ee:	0786                	slli	a5,a5,0x1
420267f0:	00f86463          	bltu	a6,a5,420267f8 <__wrap_esp_vorbis_dec_decode+0xb4>
420267f4:	1982406f          	j	4204a98c <esp_vorbis_dec_decode>
420267f8:	0005a423          	sw	zero,8(a1)
420267fc:	00062623          	sw	zero,12(a2)
42026800:	c61c                	sw	a5,8(a2)
42026802:	5561                	li	a0,-8
42026804:	8082                	ret
42026806:	556d                	li	a0,-5
42026808:	8082                	ret
