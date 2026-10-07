
C:\Work\yoRadio\.worktree\aac-storage18\idf\esp32c3-oled-native\build-flac-bounds\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4202648a <__wrap_esp_vorbis_dec_decode>:
4202648a:	c169                	beqz	a0,4202654c <__wrap_esp_vorbis_dec_decode+0xc2>
4202648c:	c1e1                	beqz	a1,4202654c <__wrap_esp_vorbis_dec_decode+0xc2>
4202648e:	ce5d                	beqz	a2,4202654c <__wrap_esp_vorbis_dec_decode+0xc2>
42026490:	ced5                	beqz	a3,4202654c <__wrap_esp_vorbis_dec_decode+0xc2>
42026492:	0005a803          	lw	a6,0(a1)
42026496:	0a080b63          	beqz	a6,4202654c <__wrap_esp_vorbis_dec_decode+0xc2>
4202649a:	421c                	lw	a5,0(a2)
4202649c:	cbc5                	beqz	a5,4202654c <__wrap_esp_vorbis_dec_decode+0xc2>
4202649e:	00052e83          	lw	t4,0(a0)
420264a2:	4701                	li	a4,0
420264a4:	000eaf03          	lw	t5,0(t4)
420264a8:	01cf2883          	lw	a7,28(t5)
420264ac:	0088a303          	lw	t1,8(a7)
420264b0:	fff30793          	addi	a5,t1,-1
420264b4:	c781                	beqz	a5,420264bc <__wrap_esp_vorbis_dec_decode+0x32>
420264b6:	8385                	srli	a5,a5,0x1
420264b8:	0705                	addi	a4,a4,1
420264ba:	fff5                	bnez	a5,420264b6 <__wrap_esp_vorbis_dec_decode+0x2c>
420264bc:	0045ae03          	lw	t3,4(a1)
420264c0:	060e0d63          	beqz	t3,4202653a <__wrap_esp_vorbis_dec_decode+0xb0>
420264c4:	00084803          	lbu	a6,0(a6)
420264c8:	00187793          	andi	a5,a6,1
420264cc:	e7bd                	bnez	a5,4202653a <__wrap_esp_vorbis_dec_decode+0xb0>
420264ce:	5ffd                	li	t6,-1
420264d0:	00ef97b3          	sll	a5,t6,a4
420264d4:	00185813          	srli	a6,a6,0x1
420264d8:	fff7c793          	not	a5,a5
420264dc:	0107f7b3          	and	a5,a5,a6
420264e0:	0467fd63          	bgeu	a5,t1,4202653a <__wrap_esp_vorbis_dec_decode+0xb0>
420264e4:	01c8a803          	lw	a6,28(a7)
420264e8:	0786                	slli	a5,a5,0x1
420264ea:	97c2                	add	a5,a5,a6
420264ec:	0007c803          	lbu	a6,0(a5)
420264f0:	010037b3          	snez	a5,a6
420264f4:	0786                	slli	a5,a5,0x1
420264f6:	97ba                	add	a5,a5,a4
420264f8:	838d                	srli	a5,a5,0x3
420264fa:	0785                	addi	a5,a5,1
420264fc:	02fe6f63          	bltu	t3,a5,4202653a <__wrap_esp_vorbis_dec_decode+0xb0>
42026500:	024ea783          	lw	a5,36(t4)
42026504:	03f78b63          	beq	a5,t6,4202653a <__wrap_esp_vorbis_dec_decode+0xb0>
42026508:	030ea703          	lw	a4,48(t4)
4202650c:	00281793          	slli	a5,a6,0x2
42026510:	97c6                	add	a5,a5,a7
42026512:	070a                	slli	a4,a4,0x2
42026514:	98ba                	add	a7,a7,a4
42026516:	0008a703          	lw	a4,0(a7)
4202651a:	439c                	lw	a5,0(a5)
4202651c:	004f2883          	lw	a7,4(t5)
42026520:	00462803          	lw	a6,4(a2)
42026524:	973e                	add	a4,a4,a5
42026526:	41f75793          	srai	a5,a4,0x1f
4202652a:	8b8d                	andi	a5,a5,3
4202652c:	97ba                	add	a5,a5,a4
4202652e:	8789                	srai	a5,a5,0x2
42026530:	031787b3          	mul	a5,a5,a7
42026534:	0786                	slli	a5,a5,0x1
42026536:	00f86463          	bltu	a6,a5,4202653e <__wrap_esp_vorbis_dec_decode+0xb4>
4202653a:	6982306f          	j	42049bd2 <esp_vorbis_dec_decode>
4202653e:	0005a423          	sw	zero,8(a1)
42026542:	00062623          	sw	zero,12(a2)
42026546:	c61c                	sw	a5,8(a2)
42026548:	5561                	li	a0,-8
4202654a:	8082                	ret
4202654c:	556d                	li	a0,-5
4202654e:	8082                	ret
