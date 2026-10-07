
idf\esp32c3-oled-native\build-output-dma\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42025e78 <__wrap_esp_vorbis_dec_decode>:
42025e78:	c169                	beqz	a0,42025f3a <__wrap_esp_vorbis_dec_decode+0xc2>
42025e7a:	c1e1                	beqz	a1,42025f3a <__wrap_esp_vorbis_dec_decode+0xc2>
42025e7c:	ce5d                	beqz	a2,42025f3a <__wrap_esp_vorbis_dec_decode+0xc2>
42025e7e:	ced5                	beqz	a3,42025f3a <__wrap_esp_vorbis_dec_decode+0xc2>
42025e80:	0005a803          	lw	a6,0(a1)
42025e84:	0a080b63          	beqz	a6,42025f3a <__wrap_esp_vorbis_dec_decode+0xc2>
42025e88:	421c                	lw	a5,0(a2)
42025e8a:	cbc5                	beqz	a5,42025f3a <__wrap_esp_vorbis_dec_decode+0xc2>
42025e8c:	00052e83          	lw	t4,0(a0)
42025e90:	4701                	li	a4,0
42025e92:	000eaf03          	lw	t5,0(t4)
42025e96:	01cf2883          	lw	a7,28(t5)
42025e9a:	0088a303          	lw	t1,8(a7)
42025e9e:	fff30793          	addi	a5,t1,-1
42025ea2:	c781                	beqz	a5,42025eaa <__wrap_esp_vorbis_dec_decode+0x32>
42025ea4:	8385                	srli	a5,a5,0x1
42025ea6:	0705                	addi	a4,a4,1
42025ea8:	fff5                	bnez	a5,42025ea4 <__wrap_esp_vorbis_dec_decode+0x2c>
42025eaa:	0045ae03          	lw	t3,4(a1)
42025eae:	060e0d63          	beqz	t3,42025f28 <__wrap_esp_vorbis_dec_decode+0xb0>
42025eb2:	00084803          	lbu	a6,0(a6)
42025eb6:	00187793          	andi	a5,a6,1
42025eba:	e7bd                	bnez	a5,42025f28 <__wrap_esp_vorbis_dec_decode+0xb0>
42025ebc:	5ffd                	li	t6,-1
42025ebe:	00ef97b3          	sll	a5,t6,a4
42025ec2:	00185813          	srli	a6,a6,0x1
42025ec6:	fff7c793          	not	a5,a5
42025eca:	0107f7b3          	and	a5,a5,a6
42025ece:	0467fd63          	bgeu	a5,t1,42025f28 <__wrap_esp_vorbis_dec_decode+0xb0>
42025ed2:	01c8a803          	lw	a6,28(a7)
42025ed6:	0786                	slli	a5,a5,0x1
42025ed8:	97c2                	add	a5,a5,a6
42025eda:	0007c803          	lbu	a6,0(a5)
42025ede:	010037b3          	snez	a5,a6
42025ee2:	0786                	slli	a5,a5,0x1
42025ee4:	97ba                	add	a5,a5,a4
42025ee6:	838d                	srli	a5,a5,0x3
42025ee8:	0785                	addi	a5,a5,1
42025eea:	02fe6f63          	bltu	t3,a5,42025f28 <__wrap_esp_vorbis_dec_decode+0xb0>
42025eee:	024ea783          	lw	a5,36(t4)
42025ef2:	03f78b63          	beq	a5,t6,42025f28 <__wrap_esp_vorbis_dec_decode+0xb0>
42025ef6:	030ea703          	lw	a4,48(t4)
42025efa:	00281793          	slli	a5,a6,0x2
42025efe:	97c6                	add	a5,a5,a7
42025f00:	070a                	slli	a4,a4,0x2
42025f02:	98ba                	add	a7,a7,a4
42025f04:	0008a703          	lw	a4,0(a7)
42025f08:	439c                	lw	a5,0(a5)
42025f0a:	004f2883          	lw	a7,4(t5)
42025f0e:	00462803          	lw	a6,4(a2)
42025f12:	973e                	add	a4,a4,a5
42025f14:	41f75793          	srai	a5,a4,0x1f
42025f18:	8b8d                	andi	a5,a5,3
42025f1a:	97ba                	add	a5,a5,a4
42025f1c:	8789                	srai	a5,a5,0x2
42025f1e:	031787b3          	mul	a5,a5,a7
42025f22:	0786                	slli	a5,a5,0x1
42025f24:	00f86463          	bltu	a6,a5,42025f2c <__wrap_esp_vorbis_dec_decode+0xb4>
42025f28:	6022206f          	j	4204852a <esp_vorbis_dec_decode>
42025f2c:	0005a423          	sw	zero,8(a1)
42025f30:	00062623          	sw	zero,12(a2)
42025f34:	c61c                	sw	a5,8(a2)
42025f36:	5561                	li	a0,-8
42025f38:	8082                	ret
42025f3a:	556d                	li	a0,-5
42025f3c:	8082                	ret
