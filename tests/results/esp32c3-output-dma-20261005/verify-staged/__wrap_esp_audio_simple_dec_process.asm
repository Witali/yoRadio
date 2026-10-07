
idf\esp32c3-oled-native\build-output-staged\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42025c7c <__wrap_esp_audio_simple_dec_process>:
42025c7c:	0015b793          	seqz	a5,a1
42025c80:	00163713          	seqz	a4,a2
42025c84:	8fd9                	or	a5,a5,a4
42025c86:	ebe9                	bnez	a5,42025d58 <__wrap_esp_audio_simple_dec_process+0xdc>
42025c88:	c961                	beqz	a0,42025d58 <__wrap_esp_audio_simple_dec_process+0xdc>
42025c8a:	419c                	lw	a5,0(a1)
42025c8c:	c7e1                	beqz	a5,42025d54 <__wrap_esp_audio_simple_dec_process+0xd8>
42025c8e:	5558                	lw	a4,44(a0)
42025c90:	204747b7          	lui	a5,0x20474
42025c94:	74f78793          	addi	a5,a5,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
42025c98:	0af71c63          	bne	a4,a5,42025d50 <__wrap_esp_audio_simple_dec_process+0xd4>
42025c9c:	7139                	addi	sp,sp,-64
42025c9e:	03054683          	lbu	a3,48(a0)
42025ca2:	de06                	sw	ra,60(sp)
42025ca4:	0005a623          	sw	zero,12(a1)
42025ca8:	00062623          	sw	zero,12(a2)
42025cac:	872a                	mv	a4,a0
42025cae:	87ae                	mv	a5,a1
42025cb0:	eab1                	bnez	a3,42025d04 <__wrap_esp_audio_simple_dec_process+0x88>
42025cb2:	43d4                	lw	a3,4(a5)
42025cb4:	c6a1                	beqz	a3,42025cfc <__wrap_esp_audio_simple_dec_process+0x80>
42025cb6:	0087c583          	lbu	a1,8(a5)
42025cba:	edd5                	bnez	a1,42025d76 <__wrap_esp_audio_simple_dec_process+0xfa>
42025cbc:	4805                	li	a6,1
42025cbe:	0b068263          	beq	a3,a6,42025d62 <__wrap_esp_audio_simple_dec_process+0xe6>
42025cc2:	0007ae83          	lw	t4,0(a5)
42025cc6:	0087ae03          	lw	t3,8(a5)
42025cca:	00c7a303          	lw	t1,12(a5)
42025cce:	0107a883          	lw	a7,16(a5)
42025cd2:	16fd                	addi	a3,a3,-1
42025cd4:	086c                	addi	a1,sp,28
42025cd6:	853a                	mv	a0,a4
42025cd8:	c23e                	sw	a5,4(sp)
42025cda:	d036                	sw	a3,32(sp)
42025cdc:	c43a                	sw	a4,8(sp)
42025cde:	ce76                	sw	t4,28(sp)
42025ce0:	d272                	sw	t3,36(sp)
42025ce2:	d41a                	sw	t1,40(sp)
42025ce4:	d646                	sw	a7,44(sp)
42025ce6:	d71ff0ef          	jal	42025a56 <process_checked>
42025cea:	56a2                	lw	a3,40(sp)
42025cec:	4792                	lw	a5,4(sp)
42025cee:	c7d4                	sw	a3,12(a5)
42025cf0:	e519                	bnez	a0,42025cfe <__wrap_esp_audio_simple_dec_process+0x82>
42025cf2:	5602                	lw	a2,32(sp)
42025cf4:	4722                	lw	a4,8(sp)
42025cf6:	4805                	li	a6,1
42025cf8:	08c68563          	beq	a3,a2,42025d82 <__wrap_esp_audio_simple_dec_process+0x106>
42025cfc:	4501                	li	a0,0
42025cfe:	50f2                	lw	ra,60(sp)
42025d00:	6121                	addi	sp,sp,64
42025d02:	8082                	ret
42025d04:	0085c683          	lbu	a3,8(a1)
42025d08:	03150513          	addi	a0,a0,49
42025d0c:	4585                	li	a1,1
42025d0e:	4801                	li	a6,0
42025d10:	4881                	li	a7,0
42025d12:	d242                	sw	a6,36(sp)
42025d14:	d446                	sw	a7,40(sp)
42025d16:	ce2a                	sw	a0,28(sp)
42025d18:	d02e                	sw	a1,32(sp)
42025d1a:	c681                	beqz	a3,42025d22 <__wrap_esp_audio_simple_dec_process+0xa6>
42025d1c:	43d4                	lw	a3,4(a5)
42025d1e:	0016b693          	seqz	a3,a3
42025d22:	02d10223          	sb	a3,36(sp)
42025d26:	4b94                	lw	a3,16(a5)
42025d28:	853a                	mv	a0,a4
42025d2a:	086c                	addi	a1,sp,28
42025d2c:	c63e                	sw	a5,12(sp)
42025d2e:	c432                	sw	a2,8(sp)
42025d30:	c23a                	sw	a4,4(sp)
42025d32:	d636                	sw	a3,44(sp)
42025d34:	d23ff0ef          	jal	42025a56 <process_checked>
42025d38:	56a2                	lw	a3,40(sp)
42025d3a:	4712                	lw	a4,4(sp)
42025d3c:	4622                	lw	a2,8(sp)
42025d3e:	47b2                	lw	a5,12(sp)
42025d40:	ee91                	bnez	a3,42025d5c <__wrap_esp_audio_simple_dec_process+0xe0>
42025d42:	fd55                	bnez	a0,42025cfe <__wrap_esp_audio_simple_dec_process+0x82>
42025d44:	4654                	lw	a3,12(a2)
42025d46:	fec5                	bnez	a3,42025cfe <__wrap_esp_audio_simple_dec_process+0x82>
42025d48:	03074683          	lbu	a3,48(a4)
42025d4c:	d2bd                	beqz	a3,42025cb2 <__wrap_esp_audio_simple_dec_process+0x36>
42025d4e:	bf45                	j	42025cfe <__wrap_esp_audio_simple_dec_process+0x82>
42025d50:	2251006f          	j	42036774 <esp_audio_simple_dec_process>
42025d54:	41dc                	lw	a5,4(a1)
42025d56:	df85                	beqz	a5,42025c8e <__wrap_esp_audio_simple_dec_process+0x12>
42025d58:	556d                	li	a0,-5
42025d5a:	8082                	ret
42025d5c:	02070823          	sb	zero,48(a4)
42025d60:	b7cd                	j	42025d42 <__wrap_esp_audio_simple_dec_process+0xc6>
42025d62:	4390                	lw	a2,0(a5)
42025d64:	4501                	li	a0,0
42025d66:	00064603          	lbu	a2,0(a2)
42025d6a:	02d70823          	sb	a3,48(a4)
42025d6e:	02c708a3          	sb	a2,49(a4)
42025d72:	c7d4                	sw	a3,12(a5)
42025d74:	b769                	j	42025cfe <__wrap_esp_audio_simple_dec_process+0x82>
42025d76:	50f2                	lw	ra,60(sp)
42025d78:	85be                	mv	a1,a5
42025d7a:	853a                	mv	a0,a4
42025d7c:	6121                	addi	sp,sp,64
42025d7e:	cd9ff06f          	j	42025a56 <process_checked>
42025d82:	4390                	lw	a2,0(a5)
42025d84:	010685b3          	add	a1,a3,a6
42025d88:	4501                	li	a0,0
42025d8a:	96b2                	add	a3,a3,a2
42025d8c:	0006c683          	lbu	a3,0(a3)
42025d90:	03070823          	sb	a6,48(a4)
42025d94:	02d708a3          	sb	a3,49(a4)
42025d98:	c7cc                	sw	a1,12(a5)
42025d9a:	b795                	j	42025cfe <__wrap_esp_audio_simple_dec_process+0x82>
