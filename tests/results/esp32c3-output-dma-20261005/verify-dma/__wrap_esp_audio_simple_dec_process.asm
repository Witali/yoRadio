
idf\esp32c3-oled-native\build-output-dma\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42025d58 <__wrap_esp_audio_simple_dec_process>:
42025d58:	0015b793          	seqz	a5,a1
42025d5c:	00163713          	seqz	a4,a2
42025d60:	8fd9                	or	a5,a5,a4
42025d62:	ebe9                	bnez	a5,42025e34 <__wrap_esp_audio_simple_dec_process+0xdc>
42025d64:	c961                	beqz	a0,42025e34 <__wrap_esp_audio_simple_dec_process+0xdc>
42025d66:	419c                	lw	a5,0(a1)
42025d68:	c7e1                	beqz	a5,42025e30 <__wrap_esp_audio_simple_dec_process+0xd8>
42025d6a:	5558                	lw	a4,44(a0)
42025d6c:	204747b7          	lui	a5,0x20474
42025d70:	74f78793          	addi	a5,a5,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
42025d74:	0af71c63          	bne	a4,a5,42025e2c <__wrap_esp_audio_simple_dec_process+0xd4>
42025d78:	7139                	addi	sp,sp,-64
42025d7a:	03054683          	lbu	a3,48(a0)
42025d7e:	de06                	sw	ra,60(sp)
42025d80:	0005a623          	sw	zero,12(a1)
42025d84:	00062623          	sw	zero,12(a2)
42025d88:	872a                	mv	a4,a0
42025d8a:	87ae                	mv	a5,a1
42025d8c:	eab1                	bnez	a3,42025de0 <__wrap_esp_audio_simple_dec_process+0x88>
42025d8e:	43d4                	lw	a3,4(a5)
42025d90:	c6a1                	beqz	a3,42025dd8 <__wrap_esp_audio_simple_dec_process+0x80>
42025d92:	0087c583          	lbu	a1,8(a5)
42025d96:	edd5                	bnez	a1,42025e52 <__wrap_esp_audio_simple_dec_process+0xfa>
42025d98:	4805                	li	a6,1
42025d9a:	0b068263          	beq	a3,a6,42025e3e <__wrap_esp_audio_simple_dec_process+0xe6>
42025d9e:	0007ae83          	lw	t4,0(a5)
42025da2:	0087ae03          	lw	t3,8(a5)
42025da6:	00c7a303          	lw	t1,12(a5)
42025daa:	0107a883          	lw	a7,16(a5)
42025dae:	16fd                	addi	a3,a3,-1
42025db0:	086c                	addi	a1,sp,28
42025db2:	853a                	mv	a0,a4
42025db4:	c23e                	sw	a5,4(sp)
42025db6:	d036                	sw	a3,32(sp)
42025db8:	c43a                	sw	a4,8(sp)
42025dba:	ce76                	sw	t4,28(sp)
42025dbc:	d272                	sw	t3,36(sp)
42025dbe:	d41a                	sw	t1,40(sp)
42025dc0:	d646                	sw	a7,44(sp)
42025dc2:	d71ff0ef          	jal	42025b32 <process_checked>
42025dc6:	56a2                	lw	a3,40(sp)
42025dc8:	4792                	lw	a5,4(sp)
42025dca:	c7d4                	sw	a3,12(a5)
42025dcc:	e519                	bnez	a0,42025dda <__wrap_esp_audio_simple_dec_process+0x82>
42025dce:	5602                	lw	a2,32(sp)
42025dd0:	4722                	lw	a4,8(sp)
42025dd2:	4805                	li	a6,1
42025dd4:	08c68563          	beq	a3,a2,42025e5e <__wrap_esp_audio_simple_dec_process+0x106>
42025dd8:	4501                	li	a0,0
42025dda:	50f2                	lw	ra,60(sp)
42025ddc:	6121                	addi	sp,sp,64
42025dde:	8082                	ret
42025de0:	0085c683          	lbu	a3,8(a1)
42025de4:	03150513          	addi	a0,a0,49
42025de8:	4585                	li	a1,1
42025dea:	4801                	li	a6,0
42025dec:	4881                	li	a7,0
42025dee:	d242                	sw	a6,36(sp)
42025df0:	d446                	sw	a7,40(sp)
42025df2:	ce2a                	sw	a0,28(sp)
42025df4:	d02e                	sw	a1,32(sp)
42025df6:	c681                	beqz	a3,42025dfe <__wrap_esp_audio_simple_dec_process+0xa6>
42025df8:	43d4                	lw	a3,4(a5)
42025dfa:	0016b693          	seqz	a3,a3
42025dfe:	02d10223          	sb	a3,36(sp)
42025e02:	4b94                	lw	a3,16(a5)
42025e04:	853a                	mv	a0,a4
42025e06:	086c                	addi	a1,sp,28
42025e08:	c63e                	sw	a5,12(sp)
42025e0a:	c432                	sw	a2,8(sp)
42025e0c:	c23a                	sw	a4,4(sp)
42025e0e:	d636                	sw	a3,44(sp)
42025e10:	d23ff0ef          	jal	42025b32 <process_checked>
42025e14:	56a2                	lw	a3,40(sp)
42025e16:	4712                	lw	a4,4(sp)
42025e18:	4622                	lw	a2,8(sp)
42025e1a:	47b2                	lw	a5,12(sp)
42025e1c:	ee91                	bnez	a3,42025e38 <__wrap_esp_audio_simple_dec_process+0xe0>
42025e1e:	fd55                	bnez	a0,42025dda <__wrap_esp_audio_simple_dec_process+0x82>
42025e20:	4654                	lw	a3,12(a2)
42025e22:	fec5                	bnez	a3,42025dda <__wrap_esp_audio_simple_dec_process+0x82>
42025e24:	03074683          	lbu	a3,48(a4)
42025e28:	d2bd                	beqz	a3,42025d8e <__wrap_esp_audio_simple_dec_process+0x36>
42025e2a:	bf45                	j	42025dda <__wrap_esp_audio_simple_dec_process+0x82>
42025e2c:	2251006f          	j	42036850 <esp_audio_simple_dec_process>
42025e30:	41dc                	lw	a5,4(a1)
42025e32:	df85                	beqz	a5,42025d6a <__wrap_esp_audio_simple_dec_process+0x12>
42025e34:	556d                	li	a0,-5
42025e36:	8082                	ret
42025e38:	02070823          	sb	zero,48(a4)
42025e3c:	b7cd                	j	42025e1e <__wrap_esp_audio_simple_dec_process+0xc6>
42025e3e:	4390                	lw	a2,0(a5)
42025e40:	4501                	li	a0,0
42025e42:	00064603          	lbu	a2,0(a2)
42025e46:	02d70823          	sb	a3,48(a4)
42025e4a:	02c708a3          	sb	a2,49(a4)
42025e4e:	c7d4                	sw	a3,12(a5)
42025e50:	b769                	j	42025dda <__wrap_esp_audio_simple_dec_process+0x82>
42025e52:	50f2                	lw	ra,60(sp)
42025e54:	85be                	mv	a1,a5
42025e56:	853a                	mv	a0,a4
42025e58:	6121                	addi	sp,sp,64
42025e5a:	cd9ff06f          	j	42025b32 <process_checked>
42025e5e:	4390                	lw	a2,0(a5)
42025e60:	010685b3          	add	a1,a3,a6
42025e64:	4501                	li	a0,0
42025e66:	96b2                	add	a3,a3,a2
42025e68:	0006c683          	lbu	a3,0(a3)
42025e6c:	03070823          	sb	a6,48(a4)
42025e70:	02d708a3          	sb	a3,49(a4)
42025e74:	c7cc                	sw	a1,12(a5)
42025e76:	b795                	j	42025dda <__wrap_esp_audio_simple_dec_process+0x82>
