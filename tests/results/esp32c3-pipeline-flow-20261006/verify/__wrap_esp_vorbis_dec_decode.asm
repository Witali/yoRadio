
idf\esp32c3-oled-native\build-pipeline-profile\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420269e0 <__wrap_esp_vorbis_dec_decode>:
420269e0:	c169                	beqz	a0,42026aa2 <__wrap_esp_vorbis_dec_decode+0xc2>
420269e2:	c1e1                	beqz	a1,42026aa2 <__wrap_esp_vorbis_dec_decode+0xc2>
420269e4:	ce5d                	beqz	a2,42026aa2 <__wrap_esp_vorbis_dec_decode+0xc2>
420269e6:	ced5                	beqz	a3,42026aa2 <__wrap_esp_vorbis_dec_decode+0xc2>
420269e8:	0005a803          	lw	a6,0(a1)
420269ec:	0a080b63          	beqz	a6,42026aa2 <__wrap_esp_vorbis_dec_decode+0xc2>
420269f0:	421c                	lw	a5,0(a2)
420269f2:	cbc5                	beqz	a5,42026aa2 <__wrap_esp_vorbis_dec_decode+0xc2>
420269f4:	00052e83          	lw	t4,0(a0)
420269f8:	4701                	li	a4,0
420269fa:	000eaf03          	lw	t5,0(t4)
420269fe:	01cf2883          	lw	a7,28(t5)
42026a02:	0088a303          	lw	t1,8(a7)
42026a06:	fff30793          	addi	a5,t1,-1
42026a0a:	c781                	beqz	a5,42026a12 <__wrap_esp_vorbis_dec_decode+0x32>
42026a0c:	8385                	srli	a5,a5,0x1
42026a0e:	0705                	addi	a4,a4,1
42026a10:	fff5                	bnez	a5,42026a0c <__wrap_esp_vorbis_dec_decode+0x2c>
42026a12:	0045ae03          	lw	t3,4(a1)
42026a16:	060e0d63          	beqz	t3,42026a90 <__wrap_esp_vorbis_dec_decode+0xb0>
42026a1a:	00084803          	lbu	a6,0(a6)
42026a1e:	00187793          	andi	a5,a6,1
42026a22:	e7bd                	bnez	a5,42026a90 <__wrap_esp_vorbis_dec_decode+0xb0>
42026a24:	5ffd                	li	t6,-1
42026a26:	00ef97b3          	sll	a5,t6,a4
42026a2a:	00185813          	srli	a6,a6,0x1
42026a2e:	fff7c793          	not	a5,a5
42026a32:	0107f7b3          	and	a5,a5,a6
42026a36:	0467fd63          	bgeu	a5,t1,42026a90 <__wrap_esp_vorbis_dec_decode+0xb0>
42026a3a:	01c8a803          	lw	a6,28(a7)
42026a3e:	0786                	slli	a5,a5,0x1
42026a40:	97c2                	add	a5,a5,a6
42026a42:	0007c803          	lbu	a6,0(a5)
42026a46:	010037b3          	snez	a5,a6
42026a4a:	0786                	slli	a5,a5,0x1
42026a4c:	97ba                	add	a5,a5,a4
42026a4e:	838d                	srli	a5,a5,0x3
42026a50:	0785                	addi	a5,a5,1
42026a52:	02fe6f63          	bltu	t3,a5,42026a90 <__wrap_esp_vorbis_dec_decode+0xb0>
42026a56:	024ea783          	lw	a5,36(t4)
42026a5a:	03f78b63          	beq	a5,t6,42026a90 <__wrap_esp_vorbis_dec_decode+0xb0>
42026a5e:	030ea703          	lw	a4,48(t4)
42026a62:	00281793          	slli	a5,a6,0x2
42026a66:	97c6                	add	a5,a5,a7
42026a68:	070a                	slli	a4,a4,0x2
42026a6a:	98ba                	add	a7,a7,a4
42026a6c:	0008a703          	lw	a4,0(a7)
42026a70:	439c                	lw	a5,0(a5)
42026a72:	004f2883          	lw	a7,4(t5)
42026a76:	00462803          	lw	a6,4(a2)
42026a7a:	973e                	add	a4,a4,a5
42026a7c:	41f75793          	srai	a5,a4,0x1f
42026a80:	8b8d                	andi	a5,a5,3
42026a82:	97ba                	add	a5,a5,a4
42026a84:	8789                	srai	a5,a5,0x2
42026a86:	031787b3          	mul	a5,a5,a7
42026a8a:	0786                	slli	a5,a5,0x1
42026a8c:	00f86463          	bltu	a6,a5,42026a94 <__wrap_esp_vorbis_dec_decode+0xb4>
42026a90:	1982406f          	j	4204ac28 <esp_vorbis_dec_decode>
42026a94:	0005a423          	sw	zero,8(a1)
42026a98:	00062623          	sw	zero,12(a2)
42026a9c:	c61c                	sw	a5,8(a2)
42026a9e:	5561                	li	a0,-8
42026aa0:	8082                	ret
42026aa2:	556d                	li	a0,-5
42026aa4:	8082                	ret
