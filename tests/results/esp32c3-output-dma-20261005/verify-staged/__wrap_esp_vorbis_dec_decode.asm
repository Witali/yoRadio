
idf\esp32c3-oled-native\build-output-staged\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42025d9c <__wrap_esp_vorbis_dec_decode>:
42025d9c:	c169                	beqz	a0,42025e5e <__wrap_esp_vorbis_dec_decode+0xc2>
42025d9e:	c1e1                	beqz	a1,42025e5e <__wrap_esp_vorbis_dec_decode+0xc2>
42025da0:	ce5d                	beqz	a2,42025e5e <__wrap_esp_vorbis_dec_decode+0xc2>
42025da2:	ced5                	beqz	a3,42025e5e <__wrap_esp_vorbis_dec_decode+0xc2>
42025da4:	0005a803          	lw	a6,0(a1)
42025da8:	0a080b63          	beqz	a6,42025e5e <__wrap_esp_vorbis_dec_decode+0xc2>
42025dac:	421c                	lw	a5,0(a2)
42025dae:	cbc5                	beqz	a5,42025e5e <__wrap_esp_vorbis_dec_decode+0xc2>
42025db0:	00052e83          	lw	t4,0(a0)
42025db4:	4701                	li	a4,0
42025db6:	000eaf03          	lw	t5,0(t4)
42025dba:	01cf2883          	lw	a7,28(t5)
42025dbe:	0088a303          	lw	t1,8(a7)
42025dc2:	fff30793          	addi	a5,t1,-1
42025dc6:	c781                	beqz	a5,42025dce <__wrap_esp_vorbis_dec_decode+0x32>
42025dc8:	8385                	srli	a5,a5,0x1
42025dca:	0705                	addi	a4,a4,1
42025dcc:	fff5                	bnez	a5,42025dc8 <__wrap_esp_vorbis_dec_decode+0x2c>
42025dce:	0045ae03          	lw	t3,4(a1)
42025dd2:	060e0d63          	beqz	t3,42025e4c <__wrap_esp_vorbis_dec_decode+0xb0>
42025dd6:	00084803          	lbu	a6,0(a6)
42025dda:	00187793          	andi	a5,a6,1
42025dde:	e7bd                	bnez	a5,42025e4c <__wrap_esp_vorbis_dec_decode+0xb0>
42025de0:	5ffd                	li	t6,-1
42025de2:	00ef97b3          	sll	a5,t6,a4
42025de6:	00185813          	srli	a6,a6,0x1
42025dea:	fff7c793          	not	a5,a5
42025dee:	0107f7b3          	and	a5,a5,a6
42025df2:	0467fd63          	bgeu	a5,t1,42025e4c <__wrap_esp_vorbis_dec_decode+0xb0>
42025df6:	01c8a803          	lw	a6,28(a7)
42025dfa:	0786                	slli	a5,a5,0x1
42025dfc:	97c2                	add	a5,a5,a6
42025dfe:	0007c803          	lbu	a6,0(a5)
42025e02:	010037b3          	snez	a5,a6
42025e06:	0786                	slli	a5,a5,0x1
42025e08:	97ba                	add	a5,a5,a4
42025e0a:	838d                	srli	a5,a5,0x3
42025e0c:	0785                	addi	a5,a5,1
42025e0e:	02fe6f63          	bltu	t3,a5,42025e4c <__wrap_esp_vorbis_dec_decode+0xb0>
42025e12:	024ea783          	lw	a5,36(t4)
42025e16:	03f78b63          	beq	a5,t6,42025e4c <__wrap_esp_vorbis_dec_decode+0xb0>
42025e1a:	030ea703          	lw	a4,48(t4)
42025e1e:	00281793          	slli	a5,a6,0x2
42025e22:	97c6                	add	a5,a5,a7
42025e24:	070a                	slli	a4,a4,0x2
42025e26:	98ba                	add	a7,a7,a4
42025e28:	0008a703          	lw	a4,0(a7)
42025e2c:	439c                	lw	a5,0(a5)
42025e2e:	004f2883          	lw	a7,4(t5)
42025e32:	00462803          	lw	a6,4(a2)
42025e36:	973e                	add	a4,a4,a5
42025e38:	41f75793          	srai	a5,a4,0x1f
42025e3c:	8b8d                	andi	a5,a5,3
42025e3e:	97ba                	add	a5,a5,a4
42025e40:	8789                	srai	a5,a5,0x2
42025e42:	031787b3          	mul	a5,a5,a7
42025e46:	0786                	slli	a5,a5,0x1
42025e48:	00f86463          	bltu	a6,a5,42025e50 <__wrap_esp_vorbis_dec_decode+0xb4>
42025e4c:	6022206f          	j	4204844e <esp_vorbis_dec_decode>
42025e50:	0005a423          	sw	zero,8(a1)
42025e54:	00062623          	sw	zero,12(a2)
42025e58:	c61c                	sw	a5,8(a2)
42025e5a:	5561                	li	a0,-8
42025e5c:	8082                	ret
42025e5e:	556d                	li	a0,-5
42025e60:	8082                	ret
