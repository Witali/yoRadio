
idf\esp32c3-oled-native\build-vorbis-repair-production\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42025bc6 <__wrap_esp_audio_simple_dec_process>:
42025bc6:	0015b793          	seqz	a5,a1
42025bca:	00163693          	seqz	a3,a2
42025bce:	8fd5                	or	a5,a5,a3
42025bd0:	e7a1                	bnez	a5,42025c18 <__wrap_esp_audio_simple_dec_process+0x52>
42025bd2:	c139                	beqz	a0,42025c18 <__wrap_esp_audio_simple_dec_process+0x52>
42025bd4:	5554                	lw	a3,44(a0)
42025bd6:	204747b7          	lui	a5,0x20474
42025bda:	74f78793          	addi	a5,a5,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
42025bde:	02f69b63          	bne	a3,a5,42025c14 <__wrap_esp_audio_simple_dec_process+0x4e>
42025be2:	01022683          	lw	a3,16(tp) # 10 <active_scope>
42025be6:	7179                	addi	sp,sp,-48
42025be8:	d422                	sw	s0,40(sp)
42025bea:	d606                	sw	ra,44(sp)
42025bec:	01c10813          	addi	a6,sp,28
42025bf0:	c636                	sw	a3,12(sp)
42025bf2:	01022823          	sw	a6,16(tp) # 10 <active_scope>
42025bf6:	8432                	mv	s0,a2
42025bf8:	00010e23          	sb	zero,28(sp)
42025bfc:	13d100ef          	jal	42036538 <esp_audio_simple_dec_process>
42025c00:	46b2                	lw	a3,12(sp)
42025c02:	01c14703          	lbu	a4,28(sp)
42025c06:	00d22823          	sw	a3,16(tp) # 10 <active_scope>
42025c0a:	eb09                	bnez	a4,42025c1c <__wrap_esp_audio_simple_dec_process+0x56>
42025c0c:	50b2                	lw	ra,44(sp)
42025c0e:	5422                	lw	s0,40(sp)
42025c10:	6145                	addi	sp,sp,48
42025c12:	8082                	ret
42025c14:	1251006f          	j	42036538 <esp_audio_simple_dec_process>
42025c18:	556d                	li	a0,-5
42025c1a:	8082                	ret
42025c1c:	00042623          	sw	zero,12(s0)
42025c20:	5579                	li	a0,-2
42025c22:	b7ed                	j	42025c0c <__wrap_esp_audio_simple_dec_process+0x46>
