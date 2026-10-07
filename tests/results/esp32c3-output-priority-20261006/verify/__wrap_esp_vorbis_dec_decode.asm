
idf\esp32c3-oled-native\build-pipeline-profile\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026a0c <__wrap_esp_vorbis_dec_decode>:
42026a0c:	c169                	beqz	a0,42026ace <__wrap_esp_vorbis_dec_decode+0xc2>
42026a0e:	c1e1                	beqz	a1,42026ace <__wrap_esp_vorbis_dec_decode+0xc2>
42026a10:	ce5d                	beqz	a2,42026ace <__wrap_esp_vorbis_dec_decode+0xc2>
42026a12:	ced5                	beqz	a3,42026ace <__wrap_esp_vorbis_dec_decode+0xc2>
42026a14:	0005a803          	lw	a6,0(a1)
42026a18:	0a080b63          	beqz	a6,42026ace <__wrap_esp_vorbis_dec_decode+0xc2>
42026a1c:	421c                	lw	a5,0(a2)
42026a1e:	cbc5                	beqz	a5,42026ace <__wrap_esp_vorbis_dec_decode+0xc2>
42026a20:	00052e83          	lw	t4,0(a0)
42026a24:	4701                	li	a4,0
42026a26:	000eaf03          	lw	t5,0(t4)
42026a2a:	01cf2883          	lw	a7,28(t5)
42026a2e:	0088a303          	lw	t1,8(a7)
42026a32:	fff30793          	addi	a5,t1,-1
42026a36:	c781                	beqz	a5,42026a3e <__wrap_esp_vorbis_dec_decode+0x32>
42026a38:	8385                	srli	a5,a5,0x1
42026a3a:	0705                	addi	a4,a4,1
42026a3c:	fff5                	bnez	a5,42026a38 <__wrap_esp_vorbis_dec_decode+0x2c>
42026a3e:	0045ae03          	lw	t3,4(a1)
42026a42:	060e0d63          	beqz	t3,42026abc <__wrap_esp_vorbis_dec_decode+0xb0>
42026a46:	00084803          	lbu	a6,0(a6)
42026a4a:	00187793          	andi	a5,a6,1
42026a4e:	e7bd                	bnez	a5,42026abc <__wrap_esp_vorbis_dec_decode+0xb0>
42026a50:	5ffd                	li	t6,-1
42026a52:	00ef97b3          	sll	a5,t6,a4
42026a56:	00185813          	srli	a6,a6,0x1
42026a5a:	fff7c793          	not	a5,a5
42026a5e:	0107f7b3          	and	a5,a5,a6
42026a62:	0467fd63          	bgeu	a5,t1,42026abc <__wrap_esp_vorbis_dec_decode+0xb0>
42026a66:	01c8a803          	lw	a6,28(a7)
42026a6a:	0786                	slli	a5,a5,0x1
42026a6c:	97c2                	add	a5,a5,a6
42026a6e:	0007c803          	lbu	a6,0(a5)
42026a72:	010037b3          	snez	a5,a6
42026a76:	0786                	slli	a5,a5,0x1
42026a78:	97ba                	add	a5,a5,a4
42026a7a:	838d                	srli	a5,a5,0x3
42026a7c:	0785                	addi	a5,a5,1
42026a7e:	02fe6f63          	bltu	t3,a5,42026abc <__wrap_esp_vorbis_dec_decode+0xb0>
42026a82:	024ea783          	lw	a5,36(t4)
42026a86:	03f78b63          	beq	a5,t6,42026abc <__wrap_esp_vorbis_dec_decode+0xb0>
42026a8a:	030ea703          	lw	a4,48(t4)
42026a8e:	00281793          	slli	a5,a6,0x2
42026a92:	97c6                	add	a5,a5,a7
42026a94:	070a                	slli	a4,a4,0x2
42026a96:	98ba                	add	a7,a7,a4
42026a98:	0008a703          	lw	a4,0(a7)
42026a9c:	439c                	lw	a5,0(a5)
42026a9e:	004f2883          	lw	a7,4(t5)
42026aa2:	00462803          	lw	a6,4(a2)
42026aa6:	973e                	add	a4,a4,a5
42026aa8:	41f75793          	srai	a5,a4,0x1f
42026aac:	8b8d                	andi	a5,a5,3
42026aae:	97ba                	add	a5,a5,a4
42026ab0:	8789                	srai	a5,a5,0x2
42026ab2:	031787b3          	mul	a5,a5,a7
42026ab6:	0786                	slli	a5,a5,0x1
42026ab8:	00f86463          	bltu	a6,a5,42026ac0 <__wrap_esp_vorbis_dec_decode+0xb4>
42026abc:	1982406f          	j	4204ac54 <esp_vorbis_dec_decode>
42026ac0:	0005a423          	sw	zero,8(a1)
42026ac4:	00062623          	sw	zero,12(a2)
42026ac8:	c61c                	sw	a5,8(a2)
42026aca:	5561                	li	a0,-8
42026acc:	8082                	ret
42026ace:	556d                	li	a0,-5
42026ad0:	8082                	ret
