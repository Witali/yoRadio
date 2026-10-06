
idf\esp32c3-oled-native\build-flac-predictor\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4202649a <__wrap_esp_vorbis_dec_decode>:
4202649a:	c169                	beqz	a0,4202655c <__wrap_esp_vorbis_dec_decode+0xc2>
4202649c:	c1e1                	beqz	a1,4202655c <__wrap_esp_vorbis_dec_decode+0xc2>
4202649e:	ce5d                	beqz	a2,4202655c <__wrap_esp_vorbis_dec_decode+0xc2>
420264a0:	ced5                	beqz	a3,4202655c <__wrap_esp_vorbis_dec_decode+0xc2>
420264a2:	0005a803          	lw	a6,0(a1)
420264a6:	0a080b63          	beqz	a6,4202655c <__wrap_esp_vorbis_dec_decode+0xc2>
420264aa:	421c                	lw	a5,0(a2)
420264ac:	cbc5                	beqz	a5,4202655c <__wrap_esp_vorbis_dec_decode+0xc2>
420264ae:	00052e83          	lw	t4,0(a0)
420264b2:	4701                	li	a4,0
420264b4:	000eaf03          	lw	t5,0(t4)
420264b8:	01cf2883          	lw	a7,28(t5)
420264bc:	0088a303          	lw	t1,8(a7)
420264c0:	fff30793          	addi	a5,t1,-1
420264c4:	c781                	beqz	a5,420264cc <__wrap_esp_vorbis_dec_decode+0x32>
420264c6:	8385                	srli	a5,a5,0x1
420264c8:	0705                	addi	a4,a4,1
420264ca:	fff5                	bnez	a5,420264c6 <__wrap_esp_vorbis_dec_decode+0x2c>
420264cc:	0045ae03          	lw	t3,4(a1)
420264d0:	060e0d63          	beqz	t3,4202654a <__wrap_esp_vorbis_dec_decode+0xb0>
420264d4:	00084803          	lbu	a6,0(a6)
420264d8:	00187793          	andi	a5,a6,1
420264dc:	e7bd                	bnez	a5,4202654a <__wrap_esp_vorbis_dec_decode+0xb0>
420264de:	5ffd                	li	t6,-1
420264e0:	00ef97b3          	sll	a5,t6,a4
420264e4:	00185813          	srli	a6,a6,0x1
420264e8:	fff7c793          	not	a5,a5
420264ec:	0107f7b3          	and	a5,a5,a6
420264f0:	0467fd63          	bgeu	a5,t1,4202654a <__wrap_esp_vorbis_dec_decode+0xb0>
420264f4:	01c8a803          	lw	a6,28(a7)
420264f8:	0786                	slli	a5,a5,0x1
420264fa:	97c2                	add	a5,a5,a6
420264fc:	0007c803          	lbu	a6,0(a5)
42026500:	010037b3          	snez	a5,a6
42026504:	0786                	slli	a5,a5,0x1
42026506:	97ba                	add	a5,a5,a4
42026508:	838d                	srli	a5,a5,0x3
4202650a:	0785                	addi	a5,a5,1
4202650c:	02fe6f63          	bltu	t3,a5,4202654a <__wrap_esp_vorbis_dec_decode+0xb0>
42026510:	024ea783          	lw	a5,36(t4)
42026514:	03f78b63          	beq	a5,t6,4202654a <__wrap_esp_vorbis_dec_decode+0xb0>
42026518:	030ea703          	lw	a4,48(t4)
4202651c:	00281793          	slli	a5,a6,0x2
42026520:	97c6                	add	a5,a5,a7
42026522:	070a                	slli	a4,a4,0x2
42026524:	98ba                	add	a7,a7,a4
42026526:	0008a703          	lw	a4,0(a7)
4202652a:	439c                	lw	a5,0(a5)
4202652c:	004f2883          	lw	a7,4(t5)
42026530:	00462803          	lw	a6,4(a2)
42026534:	973e                	add	a4,a4,a5
42026536:	41f75793          	srai	a5,a4,0x1f
4202653a:	8b8d                	andi	a5,a5,3
4202653c:	97ba                	add	a5,a5,a4
4202653e:	8789                	srai	a5,a5,0x2
42026540:	031787b3          	mul	a5,a5,a7
42026544:	0786                	slli	a5,a5,0x1
42026546:	00f86463          	bltu	a6,a5,4202654e <__wrap_esp_vorbis_dec_decode+0xb4>
4202654a:	44f2306f          	j	4204a198 <esp_vorbis_dec_decode>
4202654e:	0005a423          	sw	zero,8(a1)
42026552:	00062623          	sw	zero,12(a2)
42026556:	c61c                	sw	a5,8(a2)
42026558:	5561                	li	a0,-8
4202655a:	8082                	ret
4202655c:	556d                	li	a0,-5
4202655e:	8082                	ret
