
idf\esp32c3-oled-native\build-output-dma-leased\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026456 <__wrap_esp_vorbis_dec_decode>:
42026456:	c169                	beqz	a0,42026518 <__wrap_esp_vorbis_dec_decode+0xc2>
42026458:	c1e1                	beqz	a1,42026518 <__wrap_esp_vorbis_dec_decode+0xc2>
4202645a:	ce5d                	beqz	a2,42026518 <__wrap_esp_vorbis_dec_decode+0xc2>
4202645c:	ced5                	beqz	a3,42026518 <__wrap_esp_vorbis_dec_decode+0xc2>
4202645e:	0005a803          	lw	a6,0(a1)
42026462:	0a080b63          	beqz	a6,42026518 <__wrap_esp_vorbis_dec_decode+0xc2>
42026466:	421c                	lw	a5,0(a2)
42026468:	cbc5                	beqz	a5,42026518 <__wrap_esp_vorbis_dec_decode+0xc2>
4202646a:	00052e83          	lw	t4,0(a0)
4202646e:	4701                	li	a4,0
42026470:	000eaf03          	lw	t5,0(t4)
42026474:	01cf2883          	lw	a7,28(t5)
42026478:	0088a303          	lw	t1,8(a7)
4202647c:	fff30793          	addi	a5,t1,-1
42026480:	c781                	beqz	a5,42026488 <__wrap_esp_vorbis_dec_decode+0x32>
42026482:	8385                	srli	a5,a5,0x1
42026484:	0705                	addi	a4,a4,1
42026486:	fff5                	bnez	a5,42026482 <__wrap_esp_vorbis_dec_decode+0x2c>
42026488:	0045ae03          	lw	t3,4(a1)
4202648c:	060e0d63          	beqz	t3,42026506 <__wrap_esp_vorbis_dec_decode+0xb0>
42026490:	00084803          	lbu	a6,0(a6)
42026494:	00187793          	andi	a5,a6,1
42026498:	e7bd                	bnez	a5,42026506 <__wrap_esp_vorbis_dec_decode+0xb0>
4202649a:	5ffd                	li	t6,-1
4202649c:	00ef97b3          	sll	a5,t6,a4
420264a0:	00185813          	srli	a6,a6,0x1
420264a4:	fff7c793          	not	a5,a5
420264a8:	0107f7b3          	and	a5,a5,a6
420264ac:	0467fd63          	bgeu	a5,t1,42026506 <__wrap_esp_vorbis_dec_decode+0xb0>
420264b0:	01c8a803          	lw	a6,28(a7)
420264b4:	0786                	slli	a5,a5,0x1
420264b6:	97c2                	add	a5,a5,a6
420264b8:	0007c803          	lbu	a6,0(a5)
420264bc:	010037b3          	snez	a5,a6
420264c0:	0786                	slli	a5,a5,0x1
420264c2:	97ba                	add	a5,a5,a4
420264c4:	838d                	srli	a5,a5,0x3
420264c6:	0785                	addi	a5,a5,1
420264c8:	02fe6f63          	bltu	t3,a5,42026506 <__wrap_esp_vorbis_dec_decode+0xb0>
420264cc:	024ea783          	lw	a5,36(t4)
420264d0:	03f78b63          	beq	a5,t6,42026506 <__wrap_esp_vorbis_dec_decode+0xb0>
420264d4:	030ea703          	lw	a4,48(t4)
420264d8:	00281793          	slli	a5,a6,0x2
420264dc:	97c6                	add	a5,a5,a7
420264de:	070a                	slli	a4,a4,0x2
420264e0:	98ba                	add	a7,a7,a4
420264e2:	0008a703          	lw	a4,0(a7)
420264e6:	439c                	lw	a5,0(a5)
420264e8:	004f2883          	lw	a7,4(t5)
420264ec:	00462803          	lw	a6,4(a2)
420264f0:	973e                	add	a4,a4,a5
420264f2:	41f75793          	srai	a5,a4,0x1f
420264f6:	8b8d                	andi	a5,a5,3
420264f8:	97ba                	add	a5,a5,a4
420264fa:	8789                	srai	a5,a5,0x2
420264fc:	031787b3          	mul	a5,a5,a7
42026500:	0786                	slli	a5,a5,0x1
42026502:	00f86463          	bltu	a6,a5,4202650a <__wrap_esp_vorbis_dec_decode+0xb4>
42026506:	6042206f          	j	42048b0a <esp_vorbis_dec_decode>
4202650a:	0005a423          	sw	zero,8(a1)
4202650e:	00062623          	sw	zero,12(a2)
42026512:	c61c                	sw	a5,8(a2)
42026514:	5561                	li	a0,-8
42026516:	8082                	ret
42026518:	556d                	li	a0,-5
4202651a:	8082                	ret
