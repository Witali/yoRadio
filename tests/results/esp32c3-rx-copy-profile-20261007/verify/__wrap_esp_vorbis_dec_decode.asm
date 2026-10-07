
idf\esp32c3-oled-native\build-rx-copy\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026cbe <__wrap_esp_vorbis_dec_decode>:
42026cbe:	c169                	beqz	a0,42026d80 <__wrap_esp_vorbis_dec_decode+0xc2>
42026cc0:	c1e1                	beqz	a1,42026d80 <__wrap_esp_vorbis_dec_decode+0xc2>
42026cc2:	ce5d                	beqz	a2,42026d80 <__wrap_esp_vorbis_dec_decode+0xc2>
42026cc4:	ced5                	beqz	a3,42026d80 <__wrap_esp_vorbis_dec_decode+0xc2>
42026cc6:	0005a803          	lw	a6,0(a1)
42026cca:	0a080b63          	beqz	a6,42026d80 <__wrap_esp_vorbis_dec_decode+0xc2>
42026cce:	421c                	lw	a5,0(a2)
42026cd0:	cbc5                	beqz	a5,42026d80 <__wrap_esp_vorbis_dec_decode+0xc2>
42026cd2:	00052e83          	lw	t4,0(a0)
42026cd6:	4701                	li	a4,0
42026cd8:	000eaf03          	lw	t5,0(t4)
42026cdc:	01cf2883          	lw	a7,28(t5)
42026ce0:	0088a303          	lw	t1,8(a7)
42026ce4:	fff30793          	addi	a5,t1,-1
42026ce8:	c781                	beqz	a5,42026cf0 <__wrap_esp_vorbis_dec_decode+0x32>
42026cea:	8385                	srli	a5,a5,0x1
42026cec:	0705                	addi	a4,a4,1
42026cee:	fff5                	bnez	a5,42026cea <__wrap_esp_vorbis_dec_decode+0x2c>
42026cf0:	0045ae03          	lw	t3,4(a1)
42026cf4:	060e0d63          	beqz	t3,42026d6e <__wrap_esp_vorbis_dec_decode+0xb0>
42026cf8:	00084803          	lbu	a6,0(a6)
42026cfc:	00187793          	andi	a5,a6,1
42026d00:	e7bd                	bnez	a5,42026d6e <__wrap_esp_vorbis_dec_decode+0xb0>
42026d02:	5ffd                	li	t6,-1
42026d04:	00ef97b3          	sll	a5,t6,a4
42026d08:	00185813          	srli	a6,a6,0x1
42026d0c:	fff7c793          	not	a5,a5
42026d10:	0107f7b3          	and	a5,a5,a6
42026d14:	0467fd63          	bgeu	a5,t1,42026d6e <__wrap_esp_vorbis_dec_decode+0xb0>
42026d18:	01c8a803          	lw	a6,28(a7)
42026d1c:	0786                	slli	a5,a5,0x1
42026d1e:	97c2                	add	a5,a5,a6
42026d20:	0007c803          	lbu	a6,0(a5)
42026d24:	010037b3          	snez	a5,a6
42026d28:	0786                	slli	a5,a5,0x1
42026d2a:	97ba                	add	a5,a5,a4
42026d2c:	838d                	srli	a5,a5,0x3
42026d2e:	0785                	addi	a5,a5,1
42026d30:	02fe6f63          	bltu	t3,a5,42026d6e <__wrap_esp_vorbis_dec_decode+0xb0>
42026d34:	024ea783          	lw	a5,36(t4)
42026d38:	03f78b63          	beq	a5,t6,42026d6e <__wrap_esp_vorbis_dec_decode+0xb0>
42026d3c:	030ea703          	lw	a4,48(t4)
42026d40:	00281793          	slli	a5,a6,0x2
42026d44:	97c6                	add	a5,a5,a7
42026d46:	070a                	slli	a4,a4,0x2
42026d48:	98ba                	add	a7,a7,a4
42026d4a:	0008a703          	lw	a4,0(a7)
42026d4e:	439c                	lw	a5,0(a5)
42026d50:	004f2883          	lw	a7,4(t5)
42026d54:	00462803          	lw	a6,4(a2)
42026d58:	973e                	add	a4,a4,a5
42026d5a:	41f75793          	srai	a5,a4,0x1f
42026d5e:	8b8d                	andi	a5,a5,3
42026d60:	97ba                	add	a5,a5,a4
42026d62:	8789                	srai	a5,a5,0x2
42026d64:	031787b3          	mul	a5,a5,a7
42026d68:	0786                	slli	a5,a5,0x1
42026d6a:	00f86463          	bltu	a6,a5,42026d72 <__wrap_esp_vorbis_dec_decode+0xb4>
42026d6e:	60a2406f          	j	4204b378 <esp_vorbis_dec_decode>
42026d72:	0005a423          	sw	zero,8(a1)
42026d76:	00062623          	sw	zero,12(a2)
42026d7a:	c61c                	sw	a5,8(a2)
42026d7c:	5561                	li	a0,-8
42026d7e:	8082                	ret
42026d80:	556d                	li	a0,-5
42026d82:	8082                	ret
