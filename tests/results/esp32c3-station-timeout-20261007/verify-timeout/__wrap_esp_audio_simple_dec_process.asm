
idf\esp32c3-oled-native\build-connect-retry\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026b46 <__wrap_esp_audio_simple_dec_process>:
42026b46:	0015b793          	seqz	a5,a1
42026b4a:	00163713          	seqz	a4,a2
42026b4e:	8fd9                	or	a5,a5,a4
42026b50:	ebe9                	bnez	a5,42026c22 <__wrap_esp_audio_simple_dec_process+0xdc>
42026b52:	c961                	beqz	a0,42026c22 <__wrap_esp_audio_simple_dec_process+0xdc>
42026b54:	419c                	lw	a5,0(a1)
42026b56:	c7e1                	beqz	a5,42026c1e <__wrap_esp_audio_simple_dec_process+0xd8>
42026b58:	5558                	lw	a4,44(a0)
42026b5a:	204747b7          	lui	a5,0x20474
42026b5e:	74f78793          	addi	a5,a5,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
42026b62:	0af71c63          	bne	a4,a5,42026c1a <__wrap_esp_audio_simple_dec_process+0xd4>
42026b66:	7139                	addi	sp,sp,-64
42026b68:	03054683          	lbu	a3,48(a0)
42026b6c:	de06                	sw	ra,60(sp)
42026b6e:	0005a623          	sw	zero,12(a1)
42026b72:	00062623          	sw	zero,12(a2)
42026b76:	872a                	mv	a4,a0
42026b78:	87ae                	mv	a5,a1
42026b7a:	eab1                	bnez	a3,42026bce <__wrap_esp_audio_simple_dec_process+0x88>
42026b7c:	43d4                	lw	a3,4(a5)
42026b7e:	c6a1                	beqz	a3,42026bc6 <__wrap_esp_audio_simple_dec_process+0x80>
42026b80:	0087c583          	lbu	a1,8(a5)
42026b84:	edd5                	bnez	a1,42026c40 <__wrap_esp_audio_simple_dec_process+0xfa>
42026b86:	4805                	li	a6,1
42026b88:	0b068263          	beq	a3,a6,42026c2c <__wrap_esp_audio_simple_dec_process+0xe6>
42026b8c:	0007ae83          	lw	t4,0(a5)
42026b90:	0087ae03          	lw	t3,8(a5)
42026b94:	00c7a303          	lw	t1,12(a5)
42026b98:	0107a883          	lw	a7,16(a5)
42026b9c:	16fd                	addi	a3,a3,-1
42026b9e:	086c                	addi	a1,sp,28
42026ba0:	853a                	mv	a0,a4
42026ba2:	c23e                	sw	a5,4(sp)
42026ba4:	d036                	sw	a3,32(sp)
42026ba6:	c43a                	sw	a4,8(sp)
42026ba8:	ce76                	sw	t4,28(sp)
42026baa:	d272                	sw	t3,36(sp)
42026bac:	d41a                	sw	t1,40(sp)
42026bae:	d646                	sw	a7,44(sp)
42026bb0:	d71ff0ef          	jal	42026920 <process_checked>
42026bb4:	56a2                	lw	a3,40(sp)
42026bb6:	4792                	lw	a5,4(sp)
42026bb8:	c7d4                	sw	a3,12(a5)
42026bba:	e519                	bnez	a0,42026bc8 <__wrap_esp_audio_simple_dec_process+0x82>
42026bbc:	5602                	lw	a2,32(sp)
42026bbe:	4722                	lw	a4,8(sp)
42026bc0:	4805                	li	a6,1
42026bc2:	08c68563          	beq	a3,a2,42026c4c <__wrap_esp_audio_simple_dec_process+0x106>
42026bc6:	4501                	li	a0,0
42026bc8:	50f2                	lw	ra,60(sp)
42026bca:	6121                	addi	sp,sp,64
42026bcc:	8082                	ret
42026bce:	0085c683          	lbu	a3,8(a1)
42026bd2:	03150513          	addi	a0,a0,49
42026bd6:	4585                	li	a1,1
42026bd8:	4801                	li	a6,0
42026bda:	4881                	li	a7,0
42026bdc:	d242                	sw	a6,36(sp)
42026bde:	d446                	sw	a7,40(sp)
42026be0:	ce2a                	sw	a0,28(sp)
42026be2:	d02e                	sw	a1,32(sp)
42026be4:	c681                	beqz	a3,42026bec <__wrap_esp_audio_simple_dec_process+0xa6>
42026be6:	43d4                	lw	a3,4(a5)
42026be8:	0016b693          	seqz	a3,a3
42026bec:	02d10223          	sb	a3,36(sp)
42026bf0:	4b94                	lw	a3,16(a5)
42026bf2:	853a                	mv	a0,a4
42026bf4:	086c                	addi	a1,sp,28
42026bf6:	c63e                	sw	a5,12(sp)
42026bf8:	c432                	sw	a2,8(sp)
42026bfa:	c23a                	sw	a4,4(sp)
42026bfc:	d636                	sw	a3,44(sp)
42026bfe:	d23ff0ef          	jal	42026920 <process_checked>
42026c02:	56a2                	lw	a3,40(sp)
42026c04:	4712                	lw	a4,4(sp)
42026c06:	4622                	lw	a2,8(sp)
42026c08:	47b2                	lw	a5,12(sp)
42026c0a:	ee91                	bnez	a3,42026c26 <__wrap_esp_audio_simple_dec_process+0xe0>
42026c0c:	fd55                	bnez	a0,42026bc8 <__wrap_esp_audio_simple_dec_process+0x82>
42026c0e:	4654                	lw	a3,12(a2)
42026c10:	fec5                	bnez	a3,42026bc8 <__wrap_esp_audio_simple_dec_process+0x82>
42026c12:	03074683          	lbu	a3,48(a4)
42026c16:	d2bd                	beqz	a3,42026b7c <__wrap_esp_audio_simple_dec_process+0x36>
42026c18:	bf45                	j	42026bc8 <__wrap_esp_audio_simple_dec_process+0x82>
42026c1a:	5bc1206f          	j	420391d6 <esp_audio_simple_dec_process>
42026c1e:	41dc                	lw	a5,4(a1)
42026c20:	df85                	beqz	a5,42026b58 <__wrap_esp_audio_simple_dec_process+0x12>
42026c22:	556d                	li	a0,-5
42026c24:	8082                	ret
42026c26:	02070823          	sb	zero,48(a4)
42026c2a:	b7cd                	j	42026c0c <__wrap_esp_audio_simple_dec_process+0xc6>
42026c2c:	4390                	lw	a2,0(a5)
42026c2e:	4501                	li	a0,0
42026c30:	00064603          	lbu	a2,0(a2)
42026c34:	02d70823          	sb	a3,48(a4)
42026c38:	02c708a3          	sb	a2,49(a4)
42026c3c:	c7d4                	sw	a3,12(a5)
42026c3e:	b769                	j	42026bc8 <__wrap_esp_audio_simple_dec_process+0x82>
42026c40:	50f2                	lw	ra,60(sp)
42026c42:	85be                	mv	a1,a5
42026c44:	853a                	mv	a0,a4
42026c46:	6121                	addi	sp,sp,64
42026c48:	cd9ff06f          	j	42026920 <process_checked>
42026c4c:	4390                	lw	a2,0(a5)
42026c4e:	010685b3          	add	a1,a3,a6
42026c52:	4501                	li	a0,0
42026c54:	96b2                	add	a3,a3,a2
42026c56:	0006c683          	lbu	a3,0(a3)
42026c5a:	03070823          	sb	a6,48(a4)
42026c5e:	02d708a3          	sb	a3,49(a4)
42026c62:	c7cc                	sw	a1,12(a5)
42026c64:	b795                	j	42026bc8 <__wrap_esp_audio_simple_dec_process+0x82>
