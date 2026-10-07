
idf\esp32c3-oled-native\build-rx-copy\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026b9e <__wrap_esp_audio_simple_dec_process>:
42026b9e:	0015b793          	seqz	a5,a1
42026ba2:	00163713          	seqz	a4,a2
42026ba6:	8fd9                	or	a5,a5,a4
42026ba8:	ebe9                	bnez	a5,42026c7a <__wrap_esp_audio_simple_dec_process+0xdc>
42026baa:	c961                	beqz	a0,42026c7a <__wrap_esp_audio_simple_dec_process+0xdc>
42026bac:	419c                	lw	a5,0(a1)
42026bae:	c7e1                	beqz	a5,42026c76 <__wrap_esp_audio_simple_dec_process+0xd8>
42026bb0:	5558                	lw	a4,44(a0)
42026bb2:	204747b7          	lui	a5,0x20474
42026bb6:	74f78793          	addi	a5,a5,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
42026bba:	0af71c63          	bne	a4,a5,42026c72 <__wrap_esp_audio_simple_dec_process+0xd4>
42026bbe:	7139                	addi	sp,sp,-64
42026bc0:	03054683          	lbu	a3,48(a0)
42026bc4:	de06                	sw	ra,60(sp)
42026bc6:	0005a623          	sw	zero,12(a1)
42026bca:	00062623          	sw	zero,12(a2)
42026bce:	872a                	mv	a4,a0
42026bd0:	87ae                	mv	a5,a1
42026bd2:	eab1                	bnez	a3,42026c26 <__wrap_esp_audio_simple_dec_process+0x88>
42026bd4:	43d4                	lw	a3,4(a5)
42026bd6:	c6a1                	beqz	a3,42026c1e <__wrap_esp_audio_simple_dec_process+0x80>
42026bd8:	0087c583          	lbu	a1,8(a5)
42026bdc:	edd5                	bnez	a1,42026c98 <__wrap_esp_audio_simple_dec_process+0xfa>
42026bde:	4805                	li	a6,1
42026be0:	0b068263          	beq	a3,a6,42026c84 <__wrap_esp_audio_simple_dec_process+0xe6>
42026be4:	0007ae83          	lw	t4,0(a5)
42026be8:	0087ae03          	lw	t3,8(a5)
42026bec:	00c7a303          	lw	t1,12(a5)
42026bf0:	0107a883          	lw	a7,16(a5)
42026bf4:	16fd                	addi	a3,a3,-1
42026bf6:	086c                	addi	a1,sp,28
42026bf8:	853a                	mv	a0,a4
42026bfa:	c23e                	sw	a5,4(sp)
42026bfc:	d036                	sw	a3,32(sp)
42026bfe:	c43a                	sw	a4,8(sp)
42026c00:	ce76                	sw	t4,28(sp)
42026c02:	d272                	sw	t3,36(sp)
42026c04:	d41a                	sw	t1,40(sp)
42026c06:	d646                	sw	a7,44(sp)
42026c08:	d71ff0ef          	jal	42026978 <process_checked>
42026c0c:	56a2                	lw	a3,40(sp)
42026c0e:	4792                	lw	a5,4(sp)
42026c10:	c7d4                	sw	a3,12(a5)
42026c12:	e519                	bnez	a0,42026c20 <__wrap_esp_audio_simple_dec_process+0x82>
42026c14:	5602                	lw	a2,32(sp)
42026c16:	4722                	lw	a4,8(sp)
42026c18:	4805                	li	a6,1
42026c1a:	08c68563          	beq	a3,a2,42026ca4 <__wrap_esp_audio_simple_dec_process+0x106>
42026c1e:	4501                	li	a0,0
42026c20:	50f2                	lw	ra,60(sp)
42026c22:	6121                	addi	sp,sp,64
42026c24:	8082                	ret
42026c26:	0085c683          	lbu	a3,8(a1)
42026c2a:	03150513          	addi	a0,a0,49
42026c2e:	4585                	li	a1,1
42026c30:	4801                	li	a6,0
42026c32:	4881                	li	a7,0
42026c34:	d242                	sw	a6,36(sp)
42026c36:	d446                	sw	a7,40(sp)
42026c38:	ce2a                	sw	a0,28(sp)
42026c3a:	d02e                	sw	a1,32(sp)
42026c3c:	c681                	beqz	a3,42026c44 <__wrap_esp_audio_simple_dec_process+0xa6>
42026c3e:	43d4                	lw	a3,4(a5)
42026c40:	0016b693          	seqz	a3,a3
42026c44:	02d10223          	sb	a3,36(sp)
42026c48:	4b94                	lw	a3,16(a5)
42026c4a:	853a                	mv	a0,a4
42026c4c:	086c                	addi	a1,sp,28
42026c4e:	c63e                	sw	a5,12(sp)
42026c50:	c432                	sw	a2,8(sp)
42026c52:	c23a                	sw	a4,4(sp)
42026c54:	d636                	sw	a3,44(sp)
42026c56:	d23ff0ef          	jal	42026978 <process_checked>
42026c5a:	56a2                	lw	a3,40(sp)
42026c5c:	4712                	lw	a4,4(sp)
42026c5e:	4622                	lw	a2,8(sp)
42026c60:	47b2                	lw	a5,12(sp)
42026c62:	ee91                	bnez	a3,42026c7e <__wrap_esp_audio_simple_dec_process+0xe0>
42026c64:	fd55                	bnez	a0,42026c20 <__wrap_esp_audio_simple_dec_process+0x82>
42026c66:	4654                	lw	a3,12(a2)
42026c68:	fec5                	bnez	a3,42026c20 <__wrap_esp_audio_simple_dec_process+0x82>
42026c6a:	03074683          	lbu	a3,48(a4)
42026c6e:	d2bd                	beqz	a3,42026bd4 <__wrap_esp_audio_simple_dec_process+0x36>
42026c70:	bf45                	j	42026c20 <__wrap_esp_audio_simple_dec_process+0x82>
42026c72:	22d1206f          	j	4203969e <esp_audio_simple_dec_process>
42026c76:	41dc                	lw	a5,4(a1)
42026c78:	df85                	beqz	a5,42026bb0 <__wrap_esp_audio_simple_dec_process+0x12>
42026c7a:	556d                	li	a0,-5
42026c7c:	8082                	ret
42026c7e:	02070823          	sb	zero,48(a4)
42026c82:	b7cd                	j	42026c64 <__wrap_esp_audio_simple_dec_process+0xc6>
42026c84:	4390                	lw	a2,0(a5)
42026c86:	4501                	li	a0,0
42026c88:	00064603          	lbu	a2,0(a2)
42026c8c:	02d70823          	sb	a3,48(a4)
42026c90:	02c708a3          	sb	a2,49(a4)
42026c94:	c7d4                	sw	a3,12(a5)
42026c96:	b769                	j	42026c20 <__wrap_esp_audio_simple_dec_process+0x82>
42026c98:	50f2                	lw	ra,60(sp)
42026c9a:	85be                	mv	a1,a5
42026c9c:	853a                	mv	a0,a4
42026c9e:	6121                	addi	sp,sp,64
42026ca0:	cd9ff06f          	j	42026978 <process_checked>
42026ca4:	4390                	lw	a2,0(a5)
42026ca6:	010685b3          	add	a1,a3,a6
42026caa:	4501                	li	a0,0
42026cac:	96b2                	add	a3,a3,a2
42026cae:	0006c683          	lbu	a3,0(a3)
42026cb2:	03070823          	sb	a6,48(a4)
42026cb6:	02d708a3          	sb	a3,49(a4)
42026cba:	c7cc                	sw	a1,12(a5)
42026cbc:	b795                	j	42026c20 <__wrap_esp_audio_simple_dec_process+0x82>
