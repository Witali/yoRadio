
idf\esp32c3-oled-native\build-connect-retry\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026c66 <__wrap_esp_vorbis_dec_decode>:
42026c66:	c169                	beqz	a0,42026d28 <__wrap_esp_vorbis_dec_decode+0xc2>
42026c68:	c1e1                	beqz	a1,42026d28 <__wrap_esp_vorbis_dec_decode+0xc2>
42026c6a:	ce5d                	beqz	a2,42026d28 <__wrap_esp_vorbis_dec_decode+0xc2>
42026c6c:	ced5                	beqz	a3,42026d28 <__wrap_esp_vorbis_dec_decode+0xc2>
42026c6e:	0005a803          	lw	a6,0(a1)
42026c72:	0a080b63          	beqz	a6,42026d28 <__wrap_esp_vorbis_dec_decode+0xc2>
42026c76:	421c                	lw	a5,0(a2)
42026c78:	cbc5                	beqz	a5,42026d28 <__wrap_esp_vorbis_dec_decode+0xc2>
42026c7a:	00052e83          	lw	t4,0(a0)
42026c7e:	4701                	li	a4,0
42026c80:	000eaf03          	lw	t5,0(t4)
42026c84:	01cf2883          	lw	a7,28(t5)
42026c88:	0088a303          	lw	t1,8(a7)
42026c8c:	fff30793          	addi	a5,t1,-1
42026c90:	c781                	beqz	a5,42026c98 <__wrap_esp_vorbis_dec_decode+0x32>
42026c92:	8385                	srli	a5,a5,0x1
42026c94:	0705                	addi	a4,a4,1
42026c96:	fff5                	bnez	a5,42026c92 <__wrap_esp_vorbis_dec_decode+0x2c>
42026c98:	0045ae03          	lw	t3,4(a1)
42026c9c:	060e0d63          	beqz	t3,42026d16 <__wrap_esp_vorbis_dec_decode+0xb0>
42026ca0:	00084803          	lbu	a6,0(a6)
42026ca4:	00187793          	andi	a5,a6,1
42026ca8:	e7bd                	bnez	a5,42026d16 <__wrap_esp_vorbis_dec_decode+0xb0>
42026caa:	5ffd                	li	t6,-1
42026cac:	00ef97b3          	sll	a5,t6,a4
42026cb0:	00185813          	srli	a6,a6,0x1
42026cb4:	fff7c793          	not	a5,a5
42026cb8:	0107f7b3          	and	a5,a5,a6
42026cbc:	0467fd63          	bgeu	a5,t1,42026d16 <__wrap_esp_vorbis_dec_decode+0xb0>
42026cc0:	01c8a803          	lw	a6,28(a7)
42026cc4:	0786                	slli	a5,a5,0x1
42026cc6:	97c2                	add	a5,a5,a6
42026cc8:	0007c803          	lbu	a6,0(a5)
42026ccc:	010037b3          	snez	a5,a6
42026cd0:	0786                	slli	a5,a5,0x1
42026cd2:	97ba                	add	a5,a5,a4
42026cd4:	838d                	srli	a5,a5,0x3
42026cd6:	0785                	addi	a5,a5,1
42026cd8:	02fe6f63          	bltu	t3,a5,42026d16 <__wrap_esp_vorbis_dec_decode+0xb0>
42026cdc:	024ea783          	lw	a5,36(t4)
42026ce0:	03f78b63          	beq	a5,t6,42026d16 <__wrap_esp_vorbis_dec_decode+0xb0>
42026ce4:	030ea703          	lw	a4,48(t4)
42026ce8:	00281793          	slli	a5,a6,0x2
42026cec:	97c6                	add	a5,a5,a7
42026cee:	070a                	slli	a4,a4,0x2
42026cf0:	98ba                	add	a7,a7,a4
42026cf2:	0008a703          	lw	a4,0(a7)
42026cf6:	439c                	lw	a5,0(a5)
42026cf8:	004f2883          	lw	a7,4(t5)
42026cfc:	00462803          	lw	a6,4(a2)
42026d00:	973e                	add	a4,a4,a5
42026d02:	41f75793          	srai	a5,a4,0x1f
42026d06:	8b8d                	andi	a5,a5,3
42026d08:	97ba                	add	a5,a5,a4
42026d0a:	8789                	srai	a5,a5,0x2
42026d0c:	031787b3          	mul	a5,a5,a7
42026d10:	0786                	slli	a5,a5,0x1
42026d12:	00f86463          	bltu	a6,a5,42026d1a <__wrap_esp_vorbis_dec_decode+0xb4>
42026d16:	19a2406f          	j	4204aeb0 <esp_vorbis_dec_decode>
42026d1a:	0005a423          	sw	zero,8(a1)
42026d1e:	00062623          	sw	zero,12(a2)
42026d22:	c61c                	sw	a5,8(a2)
42026d24:	5561                	li	a0,-8
42026d26:	8082                	ret
42026d28:	556d                	li	a0,-5
42026d2a:	8082                	ret
