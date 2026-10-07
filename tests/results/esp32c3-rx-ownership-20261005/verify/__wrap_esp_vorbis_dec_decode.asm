
idf\esp32c3-oled-native\build-rx-owner\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420265ac <__wrap_esp_vorbis_dec_decode>:
420265ac:	c169                	beqz	a0,4202666e <__wrap_esp_vorbis_dec_decode+0xc2>
420265ae:	c1e1                	beqz	a1,4202666e <__wrap_esp_vorbis_dec_decode+0xc2>
420265b0:	ce5d                	beqz	a2,4202666e <__wrap_esp_vorbis_dec_decode+0xc2>
420265b2:	ced5                	beqz	a3,4202666e <__wrap_esp_vorbis_dec_decode+0xc2>
420265b4:	0005a803          	lw	a6,0(a1)
420265b8:	0a080b63          	beqz	a6,4202666e <__wrap_esp_vorbis_dec_decode+0xc2>
420265bc:	421c                	lw	a5,0(a2)
420265be:	cbc5                	beqz	a5,4202666e <__wrap_esp_vorbis_dec_decode+0xc2>
420265c0:	00052e83          	lw	t4,0(a0)
420265c4:	4701                	li	a4,0
420265c6:	000eaf03          	lw	t5,0(t4)
420265ca:	01cf2883          	lw	a7,28(t5)
420265ce:	0088a303          	lw	t1,8(a7)
420265d2:	fff30793          	addi	a5,t1,-1
420265d6:	c781                	beqz	a5,420265de <__wrap_esp_vorbis_dec_decode+0x32>
420265d8:	8385                	srli	a5,a5,0x1
420265da:	0705                	addi	a4,a4,1
420265dc:	fff5                	bnez	a5,420265d8 <__wrap_esp_vorbis_dec_decode+0x2c>
420265de:	0045ae03          	lw	t3,4(a1)
420265e2:	060e0d63          	beqz	t3,4202665c <__wrap_esp_vorbis_dec_decode+0xb0>
420265e6:	00084803          	lbu	a6,0(a6)
420265ea:	00187793          	andi	a5,a6,1
420265ee:	e7bd                	bnez	a5,4202665c <__wrap_esp_vorbis_dec_decode+0xb0>
420265f0:	5ffd                	li	t6,-1
420265f2:	00ef97b3          	sll	a5,t6,a4
420265f6:	00185813          	srli	a6,a6,0x1
420265fa:	fff7c793          	not	a5,a5
420265fe:	0107f7b3          	and	a5,a5,a6
42026602:	0467fd63          	bgeu	a5,t1,4202665c <__wrap_esp_vorbis_dec_decode+0xb0>
42026606:	01c8a803          	lw	a6,28(a7)
4202660a:	0786                	slli	a5,a5,0x1
4202660c:	97c2                	add	a5,a5,a6
4202660e:	0007c803          	lbu	a6,0(a5)
42026612:	010037b3          	snez	a5,a6
42026616:	0786                	slli	a5,a5,0x1
42026618:	97ba                	add	a5,a5,a4
4202661a:	838d                	srli	a5,a5,0x3
4202661c:	0785                	addi	a5,a5,1
4202661e:	02fe6f63          	bltu	t3,a5,4202665c <__wrap_esp_vorbis_dec_decode+0xb0>
42026622:	024ea783          	lw	a5,36(t4)
42026626:	03f78b63          	beq	a5,t6,4202665c <__wrap_esp_vorbis_dec_decode+0xb0>
4202662a:	030ea703          	lw	a4,48(t4)
4202662e:	00281793          	slli	a5,a6,0x2
42026632:	97c6                	add	a5,a5,a7
42026634:	070a                	slli	a4,a4,0x2
42026636:	98ba                	add	a7,a7,a4
42026638:	0008a703          	lw	a4,0(a7)
4202663c:	439c                	lw	a5,0(a5)
4202663e:	004f2883          	lw	a7,4(t5)
42026642:	00462803          	lw	a6,4(a2)
42026646:	973e                	add	a4,a4,a5
42026648:	41f75793          	srai	a5,a4,0x1f
4202664c:	8b8d                	andi	a5,a5,3
4202664e:	97ba                	add	a5,a5,a4
42026650:	8789                	srai	a5,a5,0x2
42026652:	031787b3          	mul	a5,a5,a7
42026656:	0786                	slli	a5,a5,0x1
42026658:	00f86463          	bltu	a6,a5,42026660 <__wrap_esp_vorbis_dec_decode+0xb4>
4202665c:	2532206f          	j	420490ae <esp_vorbis_dec_decode>
42026660:	0005a423          	sw	zero,8(a1)
42026664:	00062623          	sw	zero,12(a2)
42026668:	c61c                	sw	a5,8(a2)
4202666a:	5561                	li	a0,-8
4202666c:	8082                	ret
4202666e:	556d                	li	a0,-5
42026670:	8082                	ret
