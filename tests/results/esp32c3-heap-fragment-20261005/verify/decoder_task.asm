
idf\esp32c3-oled-native\build-heap-fragment\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420109e4 <decoder_task>:
420109e4:	7151                	addi	sp,sp,-240
420109e6:	d3a6                	sw	s1,228(sp)
420109e8:	d1ca                	sw	s2,224(sp)
420109ea:	cfce                	sw	s3,220(sp)
420109ec:	cdd2                	sw	s4,216(sp)
420109ee:	cbd6                	sw	s5,212(sp)
420109f0:	c9da                	sw	s6,208(sp)
420109f2:	c7de                	sw	s7,204(sp)
420109f4:	c5e2                	sw	s8,200(sp)
420109f6:	c1ea                	sw	s10,192(sp)
420109f8:	df6e                	sw	s11,188(sp)
420109fa:	d786                	sw	ra,236(sp)
420109fc:	d5a2                	sw	s0,232(sp)
420109fe:	c3e6                	sw	s9,196(sp)
42010a00:	643010ef          	jal	42012842 <decoder_register_codecs>
42010a04:	3fc95737          	lui	a4,0x3fc95
42010a08:	000f47b7          	lui	a5,0xf4
42010a0c:	ad870713          	addi	a4,a4,-1320 # 3fc94ad8 <s_bitrate_updated_us>
42010a10:	24078793          	addi	a5,a5,576 # f4240 <_rtc_slow_length+0xf2b9c>
42010a14:	ce02                	sw	zero,28(sp)
42010a16:	c102                	sw	zero,128(sp)
42010a18:	c302                	sw	zero,132(sp)
42010a1a:	c502                	sw	zero,136(sp)
42010a1c:	c702                	sw	zero,140(sp)
42010a1e:	c902                	sw	zero,144(sp)
42010a20:	cb02                	sw	zero,148(sp)
42010a22:	cd02                	sw	zero,152(sp)
42010a24:	cf02                	sw	zero,156(sp)
42010a26:	d102                	sw	zero,160(sp)
42010a28:	d302                	sw	zero,164(sp)
42010a2a:	d502                	sw	zero,168(sp)
42010a2c:	d702                	sw	zero,172(sp)
42010a2e:	d202                	sw	zero,36(sp)
42010a30:	d402                	sw	zero,40(sp)
42010a32:	d602                	sw	zero,44(sp)
42010a34:	d802                	sw	zero,48(sp)
42010a36:	00010d23          	sb	zero,26(sp)
42010a3a:	c23a                	sw	a4,4(sp)
42010a3c:	c43e                	sw	a5,8(sp)
42010a3e:	4901                	li	s2,0
42010a40:	4a01                	li	s4,0
42010a42:	4981                	li	s3,0
42010a44:	4d81                	li	s11,0
42010a46:	4b81                	li	s7,0
42010a48:	4c01                	li	s8,0
42010a4a:	4481                	li	s1,0
42010a4c:	4b01                	li	s6,0
42010a4e:	3fc95ab7          	lui	s5,0x3fc95
42010a52:	8d2a                	mv	s10,a0
42010a54:	af0a8793          	addi	a5,s5,-1296 # 3fc94af0 <s_generation>
42010a58:	0330000f          	fence	rw,rw
42010a5c:	4380                	lw	s0,0(a5)
42010a5e:	0230000f          	fence	r,rw
42010a62:	42940563          	beq	s0,s1,42010e8c <decoder_task+0x4a8>
42010a66:	3fc957b7          	lui	a5,0x3fc95
42010a6a:	aec78793          	addi	a5,a5,-1300 # 3fc94aec <s_decoder_target_codec>
42010a6e:	0330000f          	fence	rw,rw
42010a72:	4384                	lw	s1,0(a5)
42010a74:	0230000f          	fence	r,rw
42010a78:	4572                	lw	a0,28(sp)
42010a7a:	c119                	beqz	a0,42010a80 <decoder_task+0x9c>
42010a7c:	066270ef          	jal	42037ae2 <esp_audio_simple_dec_close>
42010a80:	854a                	mv	a0,s2
42010a82:	ce02                	sw	zero,28(sp)
42010a84:	621010ef          	jal	420128a4 <native_aac_decoder_destroy>
42010a88:	000b0563          	beqz	s6,42010a92 <decoder_task+0xae>
42010a8c:	855a                	mv	a0,s6
42010a8e:	541240ef          	jal	420357ce <custom_flac_decoder_destroy>
42010a92:	44048d63          	beqz	s1,42010eec <decoder_task+0x508>
42010a96:	d202                	sw	zero,36(sp)
42010a98:	d402                	sw	zero,40(sp)
42010a9a:	d602                	sw	zero,44(sp)
42010a9c:	d802                	sw	zero,48(sp)
42010a9e:	00010d23          	sb	zero,26(sp)
42010aa2:	3fc957b7          	lui	a5,0x3fc95
42010aa6:	ae878793          	addi	a5,a5,-1304 # 3fc94ae8 <s_decoder_released_generation>
42010aaa:	0310000f          	fence	rw,w
42010aae:	c380                	sw	s0,0(a5)
42010ab0:	0330000f          	fence	rw,rw
42010ab4:	47f2                	lw	a5,28(sp)
42010ab6:	4701                	li	a4,0
42010ab8:	d002                	sw	zero,32(sp)
42010aba:	8fd9                	or	a5,a5,a4
42010abc:	4b01                	li	s6,0
42010abe:	4c01                	li	s8,0
42010ac0:	4b81                	li	s7,0
42010ac2:	4d81                	li	s11,0
42010ac4:	4901                	li	s2,0
42010ac6:	4501                	li	a0,0
42010ac8:	40078d63          	beqz	a5,42010ee2 <decoder_task+0x4fe>
42010acc:	06c160ef          	jal	42026b38 <heap_fragment_probe_poll>
42010ad0:	3fc957b7          	lui	a5,0x3fc95
42010ad4:	afc7a503          	lw	a0,-1284(a5) # 3fc94afc <s_encoded>
42010ad8:	100c                	addi	a1,sp,32
42010ada:	4651                	li	a2,20
42010adc:	2ed660ef          	jal	420775c8 <xRingbufferReceive>
42010ae0:	8caa                	mv	s9,a0
42010ae2:	3e050663          	beqz	a0,42010ece <decoder_task+0x4ea>
42010ae6:	4118                	lw	a4,0(a0)
42010ae8:	af0a8793          	addi	a5,s5,-1296
42010aec:	0330000f          	fence	rw,rw
42010af0:	439c                	lw	a5,0(a5)
42010af2:	0230000f          	fence	r,rw
42010af6:	3cf71563          	bne	a4,a5,42010ec0 <decoder_task+0x4dc>
42010afa:	4104                	lw	s1,0(a0)
42010afc:	3d848263          	beq	s1,s8,42010ec0 <decoder_task+0x4dc>
42010b00:	415c                	lw	a5,4(a0)
42010b02:	e789                	bnez	a5,42010b0c <decoder_task+0x128>
42010b04:	00a54783          	lbu	a5,10(a0)
42010b08:	50079163          	bnez	a5,4201100a <decoder_task+0x626>
42010b0c:	120d1563          	bnez	s10,42010c36 <decoder_task+0x252>
42010b10:	12848c63          	beq	s1,s0,42010c48 <decoder_task+0x264>
42010b14:	4572                	lw	a0,28(sp)
42010b16:	c119                	beqz	a0,42010b1c <decoder_task+0x138>
42010b18:	7cb260ef          	jal	42037ae2 <esp_audio_simple_dec_close>
42010b1c:	854a                	mv	a0,s2
42010b1e:	ce02                	sw	zero,28(sp)
42010b20:	585010ef          	jal	420128a4 <native_aac_decoder_destroy>
42010b24:	000b0563          	beqz	s6,42010b2e <decoder_task+0x14a>
42010b28:	855a                	mv	a0,s6
42010b2a:	4a5240ef          	jal	420357ce <custom_flac_decoder_destroy>
42010b2e:	4712                	lw	a4,4(sp)
42010b30:	000ca483          	lw	s1,0(s9)
42010b34:	004cab83          	lw	s7,4(s9)
42010b38:	3fc957b7          	lui	a5,0x3fc95
42010b3c:	ae07a023          	sw	zero,-1312(a5) # 3fc94ae0 <s_published_bitrate_bps>
42010b40:	4801                	li	a6,0
42010b42:	4781                	li	a5,0
42010b44:	c31c                	sw	a5,0(a4)
42010b46:	00010d23          	sb	zero,26(sp)
42010b4a:	01072223          	sw	a6,4(a4)
42010b4e:	fe370097          	auipc	ra,0xfe370
42010b52:	7ec080e7          	jalr	2028(ra) # 4038133a <esp_timer_get_time>
42010b56:	c52a                	sw	a0,136(sp)
42010b58:	c902                	sw	zero,144(sp)
42010b5a:	cb02                	sw	zero,148(sp)
42010b5c:	cd02                	sw	zero,152(sp)
42010b5e:	cf02                	sw	zero,156(sp)
42010b60:	d102                	sw	zero,160(sp)
42010b62:	d302                	sw	zero,164(sp)
42010b64:	d502                	sw	zero,168(sp)
42010b66:	d702                	sw	zero,172(sp)
42010b68:	c126                	sw	s1,128(sp)
42010b6a:	c35e                	sw	s7,132(sp)
42010b6c:	c72e                	sw	a1,140(sp)
42010b6e:	478d                	li	a5,3
42010b70:	38fb8f63          	beq	s7,a5,42010f0e <decoder_task+0x52a>
42010b74:	4789                	li	a5,2
42010b76:	44fb8f63          	beq	s7,a5,42010fd4 <decoder_task+0x5f0>
42010b7a:	640d                	lui	s0,0x3
42010b7c:	7e8a7163          	bgeu	s4,s0,4201135e <decoder_task+0x97a>
42010b80:	85a2                	mv	a1,s0
42010b82:	854e                	mv	a0,s3
42010b84:	b11f70ef          	jal	42008694 <realloc>
42010b88:	7e050063          	beqz	a0,42011368 <decoder_task+0x984>
42010b8c:	d682                	sw	zero,108(sp)
42010b8e:	d882                	sw	zero,112(sp)
42010b90:	da82                	sw	zero,116(sp)
42010b92:	89aa                	mv	s3,a0
42010b94:	8a22                	mv	s4,s0
42010b96:	4791                	li	a5,4
42010b98:	78fb8763          	beq	s7,a5,42011326 <decoder_task+0x942>
42010b9c:	203357b7          	lui	a5,0x20335
42010ba0:	04d78793          	addi	a5,a5,77 # 2033504d <_rtc_slow_length+0x203339a9>
42010ba4:	086c                	addi	a1,sp,28
42010ba6:	10a8                	addi	a0,sp,104
42010ba8:	d4be                	sw	a5,104(sp)
42010baa:	00f150ef          	jal	420263b8 <__wrap_esp_audio_simple_dec_open>
42010bae:	842a                	mv	s0,a0
42010bb0:	78050763          	beqz	a0,4201133e <decoder_task+0x95a>
42010bb4:	fe378097          	auipc	ra,0xfe378
42010bb8:	806080e7          	jalr	-2042(ra) # 403883ba <esp_log_timestamp>
42010bbc:	3c1267b7          	lui	a5,0x3c126
42010bc0:	4905                	li	s2,1
42010bc2:	86aa                	mv	a3,a0
42010bc4:	89878793          	addi	a5,a5,-1896 # 3c125898 <_esp_trace_encoder_array_end+0x5778>
42010bc8:	132b98e3          	bne	s7,s2,420114f8 <decoder_task+0xb14>
42010bcc:	3c126737          	lui	a4,0x3c126
42010bd0:	8a470713          	addi	a4,a4,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
42010bd4:	3c126637          	lui	a2,0x3c126
42010bd8:	85ba                	mv	a1,a4
42010bda:	8822                	mv	a6,s0
42010bdc:	b5c60613          	addi	a2,a2,-1188 # 3c125b5c <_esp_trace_encoder_array_end+0x5a3c>
42010be0:	4505                	li	a0,1
42010be2:	fe377097          	auipc	ra,0xfe377
42010be6:	6d0080e7          	jalr	1744(ra) # 403882b2 <esp_log>
42010bea:	3c126737          	lui	a4,0x3c126
42010bee:	57f9                	li	a5,-2
42010bf0:	a9470693          	addi	a3,a4,-1388 # 3c125a94 <_esp_trace_encoder_array_end+0x5974>
42010bf4:	2ef407e3          	beq	s0,a5,420116e2 <decoder_task+0xcfe>
42010bf8:	3fc957b7          	lui	a5,0x3fc95
42010bfc:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42010c00:	4601                	li	a2,0
42010c02:	85a6                	mv	a1,s1
42010c04:	7d8040ef          	jal	420153dc <native_state_set_audio>
42010c08:	4572                	lw	a0,28(sp)
42010c0a:	c501                	beqz	a0,42010c12 <decoder_task+0x22e>
42010c0c:	6d7260ef          	jal	42037ae2 <esp_audio_simple_dec_close>
42010c10:	ce02                	sw	zero,28(sp)
42010c12:	854e                	mv	a0,s3
42010c14:	a85f70ef          	jal	42008698 <cfree>
42010c18:	8c26                	mv	s8,s1
42010c1a:	4a01                	li	s4,0
42010c1c:	4981                	li	s3,0
42010c1e:	4b01                	li	s6,0
42010c20:	4d81                	li	s11,0
42010c22:	3fc957b7          	lui	a5,0x3fc95
42010c26:	afc7a503          	lw	a0,-1284(a5) # 3fc94afc <s_encoded>
42010c2a:	85e6                	mv	a1,s9
42010c2c:	4901                	li	s2,0
42010c2e:	217660ef          	jal	42077644 <vRingbufferReturnItem>
42010c32:	4d01                	li	s10,0
42010c34:	b505                	j	42010a54 <decoder_task+0x70>
42010c36:	40d010ef          	jal	42012842 <decoder_register_codecs>
42010c3a:	8d2a                	mv	s10,a0
42010c3c:	7a051163          	bnez	a0,420113de <decoder_task+0x9fa>
42010c40:	000ca483          	lw	s1,0(s9)
42010c44:	ec8498e3          	bne	s1,s0,42010b14 <decoder_task+0x130>
42010c48:	004ca783          	lw	a5,4(s9)
42010c4c:	ed7794e3          	bne	a5,s7,42010b14 <decoder_task+0x130>
42010c50:	478d                	li	a5,3
42010c52:	04fb84e3          	beq	s7,a5,4201149a <decoder_task+0xab6>
42010c56:	47f2                	lw	a5,28(sp)
42010c58:	00f967b3          	or	a5,s2,a5
42010c5c:	d3f9                	beqz	a5,42010c22 <decoder_task+0x23e>
42010c5e:	008cd783          	lhu	a5,8(s9)
42010c62:	00bc8713          	addi	a4,s9,11
42010c66:	ce82                	sw	zero,92(sp)
42010c68:	d082                	sw	zero,96(sp)
42010c6a:	d282                	sw	zero,100(sp)
42010c6c:	ccbe                	sw	a5,88(sp)
42010c6e:	caba                	sw	a4,84(sp)
42010c70:	00acc703          	lbu	a4,10(s9)
42010c74:	ffeb8693          	addi	a3,s7,-2
42010c78:	0016b693          	seqz	a3,a3
42010c7c:	00e03733          	snez	a4,a4
42010c80:	c036                	sw	a3,0(sp)
42010c82:	04e10e23          	sb	a4,92(sp)
42010c86:	38090763          	beqz	s2,42011014 <decoder_task+0x630>
42010c8a:	e789                	bnez	a5,42010c94 <decoder_task+0x2b0>
42010c8c:	05c14783          	lbu	a5,92(sp)
42010c90:	1c078a63          	beqz	a5,42010e64 <decoder_task+0x480>
42010c94:	4781                	li	a5,0
42010c96:	4801                	li	a6,0
42010c98:	de3e                	sw	a5,60(sp)
42010c9a:	c0c2                	sw	a6,64(sp)
42010c9c:	da4e                	sw	s3,52(sp)
42010c9e:	dc52                	sw	s4,56(sp)
42010ca0:	d082                	sw	zero,96(sp)
42010ca2:	fe370097          	auipc	ra,0xfe370
42010ca6:	698080e7          	jalr	1688(ra) # 4038133a <esp_timer_get_time>
42010caa:	842a                	mv	s0,a0
42010cac:	1850                	addi	a2,sp,52
42010cae:	08cc                	addi	a1,sp,84
42010cb0:	854a                	mv	a0,s2
42010cb2:	429010ef          	jal	420128da <native_aac_decoder_process>
42010cb6:	8d2a                	mv	s10,a0
42010cb8:	fe370097          	auipc	ra,0xfe370
42010cbc:	682080e7          	jalr	1666(ra) # 4038133a <esp_timer_get_time>
42010cc0:	47ca                	lw	a5,144(sp)
42010cc2:	46da                	lw	a3,148(sp)
42010cc4:	8d01                	sub	a0,a0,s0
42010cc6:	00a78733          	add	a4,a5,a0
42010cca:	00f737b3          	sltu	a5,a4,a5
42010cce:	97b6                	add	a5,a5,a3
42010cd0:	cb3e                	sw	a5,148(sp)
42010cd2:	578a                	lw	a5,160(sp)
42010cd4:	c93a                	sw	a4,144(sp)
42010cd6:	571a                	lw	a4,164(sp)
42010cd8:	0785                	addi	a5,a5,1
42010cda:	d13e                	sw	a5,160(sp)
42010cdc:	00a77363          	bgeu	a4,a0,42010ce2 <decoder_task+0x2fe>
42010ce0:	d32a                	sw	a0,164(sp)
42010ce2:	8bfd                	andi	a5,a5,31
42010ce4:	54078a63          	beqz	a5,42011238 <decoder_task+0x854>
42010ce8:	af0a8793          	addi	a5,s5,-1296
42010cec:	0330000f          	fence	rw,rw
42010cf0:	439c                	lw	a5,0(a5)
42010cf2:	0230000f          	fence	r,rw
42010cf6:	16979763          	bne	a5,s1,42010e64 <decoder_task+0x480>
42010cfa:	57e1                	li	a5,-8
42010cfc:	50fd0863          	beq	s10,a5,4201120c <decoder_task+0x828>
42010d00:	580d1763          	bnez	s10,4201128e <decoder_task+0x8aa>
42010d04:	5786                	lw	a5,96(sp)
42010d06:	4766                	lw	a4,88(sp)
42010d08:	72f76563          	bltu	a4,a5,42011432 <decoder_task+0xa4e>
42010d0c:	8f1d                	sub	a4,a4,a5
42010d0e:	56aa                	lw	a3,168(sp)
42010d10:	ccba                	sw	a4,88(sp)
42010d12:	4756                	lw	a4,84(sp)
42010d14:	96be                	add	a3,a3,a5
42010d16:	d536                	sw	a3,168(sp)
42010d18:	97ba                	add	a5,a5,a4
42010d1a:	4706                	lw	a4,64(sp)
42010d1c:	cabe                	sw	a5,84(sp)
42010d1e:	10070c63          	beqz	a4,42010e36 <decoder_task+0x452>
42010d22:	00cc                	addi	a1,sp,68
42010d24:	854a                	mv	a0,s2
42010d26:	c282                	sw	zero,68(sp)
42010d28:	c482                	sw	zero,72(sp)
42010d2a:	c682                	sw	zero,76(sp)
42010d2c:	c882                	sw	zero,80(sp)
42010d2e:	6d5010ef          	jal	42012c02 <native_aac_decoder_get_info>
42010d32:	50051963          	bnez	a0,42011244 <decoder_task+0x860>
42010d36:	4782                	lw	a5,0(sp)
42010d38:	01b10613          	addi	a2,sp,27
42010d3c:	00cc                	addi	a1,sp,68
42010d3e:	854a                	mv	a0,s2
42010d40:	00f10da3          	sb	a5,27(sp)
42010d44:	6cd010ef          	jal	42012c10 <native_aac_decoder_label>
42010d48:	01b14683          	lbu	a3,27(sp)
42010d4c:	842a                	mv	s0,a0
42010d4e:	4501                	li	a0,0
42010d50:	5c068363          	beqz	a3,42011316 <decoder_task+0x932>
42010d54:	af0a8793          	addi	a5,s5,-1296
42010d58:	0330000f          	fence	rw,rw
42010d5c:	4398                	lw	a4,0(a5)
42010d5e:	0230000f          	fence	r,rw
42010d62:	4781                	li	a5,0
42010d64:	06971163          	bne	a4,s1,42010dc6 <decoder_task+0x3e2>
42010d68:	4716                	lw	a4,68(sp)
42010d6a:	cf31                	beqz	a4,42010dc6 <decoder_task+0x3e2>
42010d6c:	04914803          	lbu	a6,73(sp)
42010d70:	04080b63          	beqz	a6,42010dc6 <decoder_task+0x3e2>
42010d74:	04814603          	lbu	a2,72(sp)
42010d78:	c639                	beqz	a2,42010dc6 <decoder_task+0x3e2>
42010d7a:	45a6                	lw	a1,72(sp)
42010d7c:	47b6                	lw	a5,76(sp)
42010d7e:	d23a                	sw	a4,36(sp)
42010d80:	d42e                	sw	a1,40(sp)
42010d82:	45c6                	lw	a1,80(sp)
42010d84:	d63e                	sw	a5,44(sp)
42010d86:	4785                	li	a5,1
42010d88:	06012923          	sw	zero,114(sp)
42010d8c:	06012b23          	sw	zero,118(sp)
42010d90:	06011d23          	sh	zero,122(sp)
42010d94:	d4a2                	sw	s0,104(sp)
42010d96:	d6ba                	sw	a4,108(sp)
42010d98:	d82e                	sw	a1,48(sp)
42010d9a:	00f10d23          	sb	a5,26(sp)
42010d9e:	74050b63          	beqz	a0,420114f4 <decoder_task+0xb10>
42010da2:	3fc957b7          	lui	a5,0x3fc95
42010da6:	06a10823          	sb	a0,112(sp)
42010daa:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42010dae:	06c108a3          	sb	a2,113(sp)
42010db2:	85a6                	mv	a1,s1
42010db4:	10b0                	addi	a2,sp,104
42010db6:	daba                	sw	a4,116(sp)
42010db8:	07010c23          	sb	a6,120(sp)
42010dbc:	06d10d23          	sb	a3,122(sp)
42010dc0:	6fc040ef          	jal	420154bc <native_state_set_stream_info>
42010dc4:	4785                	li	a5,1
42010dc6:	45b6                	lw	a1,76(sp)
42010dc8:	8526                	mv	a0,s1
42010dca:	00f10d23          	sb	a5,26(sp)
42010dce:	fdaff0ef          	jal	420105a8 <state_set_decoder_bitrate>
42010dd2:	01a14783          	lbu	a5,26(sp)
42010dd6:	c3a5                	beqz	a5,42010e36 <decoder_task+0x452>
42010dd8:	4a0d8463          	beqz	s11,42011280 <decoder_task+0x89c>
42010ddc:	02814503          	lbu	a0,40(sp)
42010de0:	02914783          	lbu	a5,41(sp)
42010de4:	4406                	lw	s0,64(sp)
42010de6:	051d                	addi	a0,a0,7
42010de8:	810d                	srli	a0,a0,0x3
42010dea:	02f50533          	mul	a0,a0,a5
42010dee:	c91d                	beqz	a0,42010e24 <decoder_task+0x440>
42010df0:	5612                	lw	a2,36(sp)
42010df2:	ca0d                	beqz	a2,42010e24 <decoder_task+0x440>
42010df4:	02a45533          	divu	a0,s0,a0
42010df8:	47a2                	lw	a5,8(sp)
42010dfa:	4681                	li	a3,0
42010dfc:	02f535b3          	mulhu	a1,a0,a5
42010e00:	02f50533          	mul	a0,a0,a5
42010e04:	fdff0097          	auipc	ra,0xfdff0
42010e08:	aa8080e7          	jalr	-1368(ra) # 400008ac <__udivdi3>
42010e0c:	47ea                	lw	a5,152(sp)
42010e0e:	46fa                	lw	a3,156(sp)
42010e10:	573a                	lw	a4,172(sp)
42010e12:	953e                	add	a0,a0,a5
42010e14:	96ae                	add	a3,a3,a1
42010e16:	00f537b3          	sltu	a5,a0,a5
42010e1a:	97b6                	add	a5,a5,a3
42010e1c:	9722                	add	a4,a4,s0
42010e1e:	cf3e                	sw	a5,156(sp)
42010e20:	cd2a                	sw	a0,152(sp)
42010e22:	d73a                	sw	a4,172(sp)
42010e24:	86a2                	mv	a3,s0
42010e26:	864e                	mv	a2,s3
42010e28:	104c                	addi	a1,sp,36
42010e2a:	8526                	mv	a0,s1
42010e2c:	e40ff0ef          	jal	4201046c <send_pcm>
42010e30:	8daa                	mv	s11,a0
42010e32:	7e050a63          	beqz	a0,42011626 <decoder_task+0xc42>
42010e36:	fe370097          	auipc	ra,0xfe370
42010e3a:	504080e7          	jalr	1284(ra) # 4038133a <esp_timer_get_time>
42010e3e:	862e                	mv	a2,a1
42010e40:	85aa                	mv	a1,a0
42010e42:	0108                	addi	a0,sp,128
42010e44:	9aaff0ef          	jal	4200ffee <decode_stats_report>
42010e48:	4706                	lw	a4,64(sp)
42010e4a:	5786                	lw	a5,96(sp)
42010e4c:	05c14683          	lbu	a3,92(sp)
42010e50:	8fd9                	or	a5,a5,a4
42010e52:	3a079763          	bnez	a5,42011200 <decoder_task+0x81c>
42010e56:	00068fe3          	beqz	a3,42011674 <decoder_task+0xc90>
42010e5a:	4701                	li	a4,0
42010e5c:	47e6                	lw	a5,88(sp)
42010e5e:	8f5d                	or	a4,a4,a5
42010e60:	e20715e3          	bnez	a4,42010c8a <decoder_task+0x2a6>
42010e64:	00acc783          	lbu	a5,10(s9)
42010e68:	48079663          	bnez	a5,420112f4 <decoder_task+0x910>
42010e6c:	489c0463          	beq	s8,s1,420112f4 <decoder_task+0x910>
42010e70:	8566                	mv	a0,s9
42010e72:	85e2                	mv	a1,s8
42010e74:	aa9ff0ef          	jal	4201091c <return_decoded_packet>
42010e78:	4d01                	li	s10,0
42010e7a:	af0a8793          	addi	a5,s5,-1296
42010e7e:	0330000f          	fence	rw,rw
42010e82:	4380                	lw	s0,0(a5)
42010e84:	0230000f          	fence	r,rw
42010e88:	bc941fe3          	bne	s0,s1,42010a66 <decoder_task+0x82>
42010e8c:	040c0363          	beqz	s8,42010ed2 <decoder_task+0x4ee>
42010e90:	049c1163          	bne	s8,s1,42010ed2 <decoder_task+0x4ee>
42010e94:	4572                	lw	a0,28(sp)
42010e96:	c119                	beqz	a0,42010e9c <decoder_task+0x4b8>
42010e98:	44b260ef          	jal	42037ae2 <esp_audio_simple_dec_close>
42010e9c:	ce02                	sw	zero,28(sp)
42010e9e:	04090d63          	beqz	s2,42010ef8 <decoder_task+0x514>
42010ea2:	854a                	mv	a0,s2
42010ea4:	201010ef          	jal	420128a4 <native_aac_decoder_destroy>
42010ea8:	4472                	lw	s0,28(sp)
42010eaa:	854e                	mv	a0,s3
42010eac:	fecf70ef          	jal	42008698 <cfree>
42010eb0:	d002                	sw	zero,32(sp)
42010eb2:	c439                	beqz	s0,42010f00 <decoder_task+0x51c>
42010eb4:	8426                	mv	s0,s1
42010eb6:	4501                	li	a0,0
42010eb8:	4901                	li	s2,0
42010eba:	4a01                	li	s4,0
42010ebc:	4981                	li	s3,0
42010ebe:	b139                	j	42010acc <decoder_task+0xe8>
42010ec0:	3fc957b7          	lui	a5,0x3fc95
42010ec4:	afc7a503          	lw	a0,-1284(a5) # 3fc94afc <s_encoded>
42010ec8:	85e6                	mv	a1,s9
42010eca:	77a660ef          	jal	42077644 <vRingbufferReturnItem>
42010ece:	84a2                	mv	s1,s0
42010ed0:	b651                	j	42010a54 <decoder_task+0x70>
42010ed2:	47f2                	lw	a5,28(sp)
42010ed4:	874a                	mv	a4,s2
42010ed6:	d002                	sw	zero,32(sp)
42010ed8:	8fd9                	or	a5,a5,a4
42010eda:	8426                	mv	s0,s1
42010edc:	4501                	li	a0,0
42010ede:	be0797e3          	bnez	a5,42010acc <decoder_task+0xe8>
42010ee2:	4901                	li	s2,0
42010ee4:	be0994e3          	bnez	s3,42010acc <decoder_task+0xe8>
42010ee8:	84a2                	mv	s1,s0
42010eea:	a821                	j	42010f02 <decoder_task+0x51e>
42010eec:	854e                	mv	a0,s3
42010eee:	faaf70ef          	jal	42008698 <cfree>
42010ef2:	4a01                	li	s4,0
42010ef4:	4981                	li	s3,0
42010ef6:	b645                	j	42010a96 <decoder_task+0xb2>
42010ef8:	854e                	mv	a0,s3
42010efa:	f9ef70ef          	jal	42008698 <cfree>
42010efe:	d002                	sw	zero,32(sp)
42010f00:	4a01                	li	s4,0
42010f02:	8426                	mv	s0,s1
42010f04:	001b3513          	seqz	a0,s6
42010f08:	4901                	li	s2,0
42010f0a:	4981                	li	s3,0
42010f0c:	b6c1                	j	42010acc <decoder_task+0xe8>
42010f0e:	854e                	mv	a0,s3
42010f10:	f88f70ef          	jal	42008698 <cfree>
42010f14:	05b240ef          	jal	4203576e <custom_flac_decoder_create>
42010f18:	8b2a                	mv	s6,a0
42010f1a:	58050363          	beqz	a0,420114a0 <decoder_task+0xabc>
42010f1e:	4901                	li	s2,0
42010f20:	4a01                	li	s4,0
42010f22:	4981                	li	s3,0
42010f24:	4d81                	li	s11,0
42010f26:	4661                	li	a2,24
42010f28:	4581                	li	a1,0
42010f2a:	10a8                	addi	a0,sp,104
42010f2c:	fdfef097          	auipc	ra,0xfdfef
42010f30:	428080e7          	jalr	1064(ra) # 40000354 <memset>
42010f34:	011c                	addi	a5,sp,128
42010f36:	ccbe                	sw	a5,88(sp)
42010f38:	105c                	addi	a5,sp,36
42010f3a:	cebe                	sw	a5,92(sp)
42010f3c:	01a10793          	addi	a5,sp,26
42010f40:	d0be                	sw	a5,96(sp)
42010f42:	caa6                	sw	s1,84(sp)
42010f44:	00acc683          	lbu	a3,10(s9)
42010f48:	008cd603          	lhu	a2,8(s9)
42010f4c:	42011737          	lui	a4,0x42011
42010f50:	00d036b3          	snez	a3,a3
42010f54:	08dc                	addi	a5,sp,84
42010f56:	70c70713          	addi	a4,a4,1804 # 4201170c <custom_flac_output>
42010f5a:	00bc8593          	addi	a1,s9,11
42010f5e:	06810813          	addi	a6,sp,104
42010f62:	855a                	mv	a0,s6
42010f64:	091240ef          	jal	420357f4 <custom_flac_decoder_feed>
42010f68:	47ca                	lw	a5,144(sp)
42010f6a:	5726                	lw	a4,104(sp)
42010f6c:	465a                	lw	a2,148(sp)
42010f6e:	55b6                	lw	a1,108(sp)
42010f70:	568a                	lw	a3,160(sp)
42010f72:	973e                	add	a4,a4,a5
42010f74:	842a                	mv	s0,a0
42010f76:	5546                	lw	a0,112(sp)
42010f78:	962e                	add	a2,a2,a1
42010f7a:	00f737b3          	sltu	a5,a4,a5
42010f7e:	97b2                	add	a5,a5,a2
42010f80:	55d6                	lw	a1,116(sp)
42010f82:	561a                	lw	a2,164(sp)
42010f84:	96aa                	add	a3,a3,a0
42010f86:	c93a                	sw	a4,144(sp)
42010f88:	cb3e                	sw	a5,148(sp)
42010f8a:	d136                	sw	a3,160(sp)
42010f8c:	00b67363          	bgeu	a2,a1,42010f92 <decoder_task+0x5ae>
42010f90:	d32e                	sw	a1,164(sp)
42010f92:	57aa                	lw	a5,168(sp)
42010f94:	5766                	lw	a4,120(sp)
42010f96:	97ba                	add	a5,a5,a4
42010f98:	d53e                	sw	a5,168(sp)
42010f9a:	560d8563          	beqz	s11,42011504 <decoder_task+0xb20>
42010f9e:	4d85                	li	s11,1
42010fa0:	fe370097          	auipc	ra,0xfe370
42010fa4:	39a080e7          	jalr	922(ra) # 4038133a <esp_timer_get_time>
42010fa8:	862e                	mv	a2,a1
42010faa:	85aa                	mv	a1,a0
42010fac:	0108                	addi	a0,sp,128
42010fae:	840ff0ef          	jal	4200ffee <decode_stats_report>
42010fb2:	5c044363          	bltz	s0,42011578 <decoder_task+0xb94>
42010fb6:	8426                	mv	s0,s1
42010fb8:	00acc783          	lbu	a5,10(s9)
42010fbc:	52079763          	bnez	a5,420114ea <decoder_task+0xb06>
42010fc0:	528c0563          	beq	s8,s0,420114ea <decoder_task+0xb06>
42010fc4:	8566                	mv	a0,s9
42010fc6:	85e2                	mv	a1,s8
42010fc8:	955ff0ef          	jal	4201091c <return_decoded_packet>
42010fcc:	84a2                	mv	s1,s0
42010fce:	4b8d                	li	s7,3
42010fd0:	4d01                	li	s10,0
42010fd2:	b449                	j	42010a54 <decoder_task+0x70>
42010fd4:	6589                	lui	a1,0x2
42010fd6:	36ba0b63          	beq	s4,a1,4201134c <decoder_task+0x968>
42010fda:	854e                	mv	a0,s3
42010fdc:	eb8f70ef          	jal	42008694 <realloc>
42010fe0:	842a                	mv	s0,a0
42010fe2:	70050b63          	beqz	a0,420116f8 <decoder_task+0xd14>
42010fe6:	204347b7          	lui	a5,0x20434
42010fea:	14178793          	addi	a5,a5,321 # 20434141 <_rtc_slow_length+0x20432a9d>
42010fee:	d682                	sw	zero,108(sp)
42010ff0:	d882                	sw	zero,112(sp)
42010ff2:	da82                	sw	zero,116(sp)
42010ff4:	d4be                	sw	a5,104(sp)
42010ff6:	083010ef          	jal	42012878 <native_aac_decoder_create>
42010ffa:	892a                	mv	s2,a0
42010ffc:	52050463          	beqz	a0,42011524 <decoder_task+0xb40>
42011000:	89a2                	mv	s3,s0
42011002:	6a09                	lui	s4,0x2
42011004:	4b01                	li	s6,0
42011006:	4d81                	li	s11,0
42011008:	b999                	j	42010c5e <decoder_task+0x27a>
4201100a:	85e2                	mv	a1,s8
4201100c:	911ff0ef          	jal	4201091c <return_decoded_packet>
42011010:	84a2                	mv	s1,s0
42011012:	b489                	j	42010a54 <decoder_task+0x70>
42011014:	5d61                	li	s10,-8
42011016:	c662                	sw	s8,12(sp)
42011018:	e789                	bnez	a5,42011022 <decoder_task+0x63e>
4201101a:	05c14783          	lbu	a5,92(sp)
4201101e:	1c078f63          	beqz	a5,420111fc <decoder_task+0x818>
42011022:	4781                	li	a5,0
42011024:	4801                	li	a6,0
42011026:	de3e                	sw	a5,60(sp)
42011028:	c0c2                	sw	a6,64(sp)
4201102a:	da4e                	sw	s3,52(sp)
4201102c:	dc52                	sw	s4,56(sp)
4201102e:	d082                	sw	zero,96(sp)
42011030:	fe370097          	auipc	ra,0xfe370
42011034:	30a080e7          	jalr	778(ra) # 4038133a <esp_timer_get_time>
42011038:	842a                	mv	s0,a0
4201103a:	4572                	lw	a0,28(sp)
4201103c:	1850                	addi	a2,sp,52
4201103e:	08cc                	addi	a1,sp,84
42011040:	504150ef          	jal	42026544 <__wrap_esp_audio_simple_dec_process>
42011044:	8c2a                	mv	s8,a0
42011046:	fe370097          	auipc	ra,0xfe370
4201104a:	2f4080e7          	jalr	756(ra) # 4038133a <esp_timer_get_time>
4201104e:	47ca                	lw	a5,144(sp)
42011050:	46da                	lw	a3,148(sp)
42011052:	8d01                	sub	a0,a0,s0
42011054:	00a78733          	add	a4,a5,a0
42011058:	00f737b3          	sltu	a5,a4,a5
4201105c:	97b6                	add	a5,a5,a3
4201105e:	cb3e                	sw	a5,148(sp)
42011060:	578a                	lw	a5,160(sp)
42011062:	c93a                	sw	a4,144(sp)
42011064:	571a                	lw	a4,164(sp)
42011066:	0785                	addi	a5,a5,1
42011068:	d13e                	sw	a5,160(sp)
4201106a:	00a77363          	bgeu	a4,a0,42011070 <decoder_task+0x68c>
4201106e:	d32a                	sw	a0,164(sp)
42011070:	8bfd                	andi	a5,a5,31
42011072:	1e078e63          	beqz	a5,4201126e <decoder_task+0x88a>
42011076:	af0a8793          	addi	a5,s5,-1296
4201107a:	0330000f          	fence	rw,rw
4201107e:	439c                	lw	a5,0(a5)
42011080:	0230000f          	fence	r,rw
42011084:	16979c63          	bne	a5,s1,420111fc <decoder_task+0x818>
42011088:	1dac0763          	beq	s8,s10,42011256 <decoder_task+0x872>
4201108c:	5c0c1363          	bnez	s8,42011652 <decoder_task+0xc6e>
42011090:	5786                	lw	a5,96(sp)
42011092:	4766                	lw	a4,88(sp)
42011094:	38f76f63          	bltu	a4,a5,42011432 <decoder_task+0xa4e>
42011098:	8f1d                	sub	a4,a4,a5
4201109a:	56aa                	lw	a3,168(sp)
4201109c:	ccba                	sw	a4,88(sp)
4201109e:	4756                	lw	a4,84(sp)
420110a0:	96be                	add	a3,a3,a5
420110a2:	d536                	sw	a3,168(sp)
420110a4:	97ba                	add	a5,a5,a4
420110a6:	4706                	lw	a4,64(sp)
420110a8:	cabe                	sw	a5,84(sp)
420110aa:	12070363          	beqz	a4,420111d0 <decoder_task+0x7ec>
420110ae:	4572                	lw	a0,28(sp)
420110b0:	00cc                	addi	a1,sp,68
420110b2:	c282                	sw	zero,68(sp)
420110b4:	c482                	sw	zero,72(sp)
420110b6:	c682                	sw	zero,76(sp)
420110b8:	c882                	sw	zero,80(sp)
420110ba:	1b1260ef          	jal	42037a6a <esp_audio_simple_dec_get_info>
420110be:	1a051e63          	bnez	a0,4201127a <decoder_task+0x896>
420110c2:	4782                	lw	a5,0(sp)
420110c4:	00f10da3          	sb	a5,27(sp)
420110c8:	4789                	li	a5,2
420110ca:	52fb8063          	beq	s7,a5,420115ea <decoder_task+0xc06>
420110ce:	4791                	li	a5,4
420110d0:	52fb8263          	beq	s7,a5,420115f4 <decoder_task+0xc10>
420110d4:	3c126737          	lui	a4,0x3c126
420110d8:	4785                	li	a5,1
420110da:	89870593          	addi	a1,a4,-1896 # 3c125898 <_esp_trace_encoder_array_end+0x5778>
420110de:	42fb9e63          	bne	s7,a5,4201151a <decoder_task+0xb36>
420110e2:	af0a8793          	addi	a5,s5,-1296
420110e6:	0330000f          	fence	rw,rw
420110ea:	439c                	lw	a5,0(a5)
420110ec:	0230000f          	fence	r,rw
420110f0:	06979463          	bne	a5,s1,42011158 <decoder_task+0x774>
420110f4:	4796                	lw	a5,68(sp)
420110f6:	c3b5                	beqz	a5,4201115a <decoder_task+0x776>
420110f8:	04914683          	lbu	a3,73(sp)
420110fc:	ceb1                	beqz	a3,42011158 <decoder_task+0x774>
420110fe:	04815703          	lhu	a4,72(sp)
42011102:	04814503          	lbu	a0,72(sp)
42011106:	00875613          	srli	a2,a4,0x8
4201110a:	0722                	slli	a4,a4,0x8
4201110c:	963a                	add	a2,a2,a4
4201110e:	c529                	beqz	a0,42011158 <decoder_task+0x774>
42011110:	06012b23          	sw	zero,118(sp)
42011114:	06012923          	sw	zero,114(sp)
42011118:	d23e                	sw	a5,36(sp)
4201111a:	06c11823          	sh	a2,112(sp)
4201111e:	d6be                	sw	a5,108(sp)
42011120:	4626                	lw	a2,72(sp)
42011122:	dabe                	sw	a5,116(sp)
42011124:	3fc957b7          	lui	a5,0x3fc95
42011128:	4746                	lw	a4,80(sp)
4201112a:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
4201112e:	06d10c23          	sb	a3,120(sp)
42011132:	4782                	lw	a5,0(sp)
42011134:	46b6                	lw	a3,76(sp)
42011136:	06011d23          	sh	zero,122(sp)
4201113a:	d4ae                	sw	a1,104(sp)
4201113c:	d432                	sw	a2,40(sp)
4201113e:	4405                	li	s0,1
42011140:	10b0                	addi	a2,sp,104
42011142:	85a6                	mv	a1,s1
42011144:	06f10d23          	sb	a5,122(sp)
42011148:	d636                	sw	a3,44(sp)
4201114a:	d83a                	sw	a4,48(sp)
4201114c:	00810d23          	sb	s0,26(sp)
42011150:	36c040ef          	jal	420154bc <native_state_set_stream_info>
42011154:	87a2                	mv	a5,s0
42011156:	a011                	j	4201115a <decoder_task+0x776>
42011158:	4781                	li	a5,0
4201115a:	45b6                	lw	a1,76(sp)
4201115c:	8526                	mv	a0,s1
4201115e:	00f10d23          	sb	a5,26(sp)
42011162:	c46ff0ef          	jal	420105a8 <state_set_decoder_bitrate>
42011166:	01a14783          	lbu	a5,26(sp)
4201116a:	c3bd                	beqz	a5,420111d0 <decoder_task+0x7ec>
4201116c:	1e0d8263          	beqz	s11,42011350 <decoder_task+0x96c>
42011170:	02814503          	lbu	a0,40(sp)
42011174:	02914783          	lbu	a5,41(sp)
42011178:	4406                	lw	s0,64(sp)
4201117a:	051d                	addi	a0,a0,7
4201117c:	810d                	srli	a0,a0,0x3
4201117e:	02f50533          	mul	a0,a0,a5
42011182:	cd15                	beqz	a0,420111be <decoder_task+0x7da>
42011184:	5612                	lw	a2,36(sp)
42011186:	ce05                	beqz	a2,420111be <decoder_task+0x7da>
42011188:	02a45533          	divu	a0,s0,a0
4201118c:	000f47b7          	lui	a5,0xf4
42011190:	24078793          	addi	a5,a5,576 # f4240 <_rtc_slow_length+0xf2b9c>
42011194:	4681                	li	a3,0
42011196:	02f535b3          	mulhu	a1,a0,a5
4201119a:	02f50533          	mul	a0,a0,a5
4201119e:	fdfef097          	auipc	ra,0xfdfef
420111a2:	70e080e7          	jalr	1806(ra) # 400008ac <__udivdi3>
420111a6:	47ea                	lw	a5,152(sp)
420111a8:	46fa                	lw	a3,156(sp)
420111aa:	573a                	lw	a4,172(sp)
420111ac:	953e                	add	a0,a0,a5
420111ae:	96ae                	add	a3,a3,a1
420111b0:	00f537b3          	sltu	a5,a0,a5
420111b4:	97b6                	add	a5,a5,a3
420111b6:	9722                	add	a4,a4,s0
420111b8:	cf3e                	sw	a5,156(sp)
420111ba:	cd2a                	sw	a0,152(sp)
420111bc:	d73a                	sw	a4,172(sp)
420111be:	86a2                	mv	a3,s0
420111c0:	864e                	mv	a2,s3
420111c2:	104c                	addi	a1,sp,36
420111c4:	8526                	mv	a0,s1
420111c6:	aa6ff0ef          	jal	4201046c <send_pcm>
420111ca:	8daa                	mv	s11,a0
420111cc:	44050c63          	beqz	a0,42011624 <decoder_task+0xc40>
420111d0:	fe370097          	auipc	ra,0xfe370
420111d4:	16a080e7          	jalr	362(ra) # 4038133a <esp_timer_get_time>
420111d8:	862e                	mv	a2,a1
420111da:	85aa                	mv	a1,a0
420111dc:	0108                	addi	a0,sp,128
420111de:	e11fe0ef          	jal	4200ffee <decode_stats_report>
420111e2:	4706                	lw	a4,64(sp)
420111e4:	5786                	lw	a5,96(sp)
420111e6:	05c14683          	lbu	a3,92(sp)
420111ea:	8fd9                	or	a5,a5,a4
420111ec:	efb9                	bnez	a5,4201124a <decoder_task+0x866>
420111ee:	48068363          	beqz	a3,42011674 <decoder_task+0xc90>
420111f2:	4701                	li	a4,0
420111f4:	47e6                	lw	a5,88(sp)
420111f6:	8f5d                	or	a4,a4,a5
420111f8:	e20710e3          	bnez	a4,42011018 <decoder_task+0x634>
420111fc:	4c32                	lw	s8,12(sp)
420111fe:	b19d                	j	42010e64 <decoder_task+0x480>
42011200:	c4069ee3          	bnez	a3,42010e5c <decoder_task+0x478>
42011204:	47e6                	lw	a5,88(sp)
42011206:	a80797e3          	bnez	a5,42010c94 <decoder_task+0x2b0>
4201120a:	b9a9                	j	42010e64 <decoder_task+0x480>
4201120c:	5706                	lw	a4,96(sp)
4201120e:	47d6                	lw	a5,84(sp)
42011210:	56aa                	lw	a3,168(sp)
42011212:	5472                	lw	s0,60(sp)
42011214:	97ba                	add	a5,a5,a4
42011216:	cabe                	sw	a5,84(sp)
42011218:	47e6                	lw	a5,88(sp)
4201121a:	96ba                	add	a3,a3,a4
4201121c:	d536                	sw	a3,168(sp)
4201121e:	8f99                	sub	a5,a5,a4
42011220:	ccbe                	sw	a5,88(sp)
42011222:	3c8a7e63          	bgeu	s4,s0,420115fe <decoder_task+0xc1a>
42011226:	85a2                	mv	a1,s0
42011228:	854e                	mv	a0,s3
4201122a:	c6af70ef          	jal	42008694 <realloc>
4201122e:	3c050863          	beqz	a0,420115fe <decoder_task+0xc1a>
42011232:	8a22                	mv	s4,s0
42011234:	89aa                	mv	s3,a0
42011236:	bcb9                	j	42010c94 <decoder_task+0x2b0>
42011238:	4505                	li	a0,1
4201123a:	00100097          	auipc	ra,0x100
4201123e:	1e8080e7          	jalr	488(ra) # 42111422 <vTaskDelay>
42011242:	b45d                	j	42010ce8 <decoder_task+0x304>
42011244:	00010d23          	sb	zero,26(sp)
42011248:	b6fd                	j	42010e36 <decoder_task+0x452>
4201124a:	f6cd                	bnez	a3,420111f4 <decoder_task+0x810>
4201124c:	47e6                	lw	a5,88(sp)
4201124e:	dc079ae3          	bnez	a5,42011022 <decoder_task+0x63e>
42011252:	4c32                	lw	s8,12(sp)
42011254:	b901                	j	42010e64 <decoder_task+0x480>
42011256:	5472                	lw	s0,60(sp)
42011258:	3a8a7363          	bgeu	s4,s0,420115fe <decoder_task+0xc1a>
4201125c:	85a2                	mv	a1,s0
4201125e:	854e                	mv	a0,s3
42011260:	c34f70ef          	jal	42008694 <realloc>
42011264:	38050d63          	beqz	a0,420115fe <decoder_task+0xc1a>
42011268:	89aa                	mv	s3,a0
4201126a:	8a22                	mv	s4,s0
4201126c:	bb5d                	j	42011022 <decoder_task+0x63e>
4201126e:	4505                	li	a0,1
42011270:	00100097          	auipc	ra,0x100
42011274:	1b2080e7          	jalr	434(ra) # 42111422 <vTaskDelay>
42011278:	bbfd                	j	42011076 <decoder_task+0x692>
4201127a:	00010d23          	sb	zero,26(sp)
4201127e:	bf89                	j	420111d0 <decoder_task+0x7ec>
42011280:	3c1267b7          	lui	a5,0x3c126
42011284:	bc878513          	addi	a0,a5,-1080 # 3c125bc8 <_esp_trace_encoder_array_end+0x5aa8>
42011288:	980ff0ef          	jal	42010408 <log_runtime_memory>
4201128c:	be81                	j	42010ddc <decoder_task+0x3f8>
4201128e:	846a                	mv	s0,s10
42011290:	4a09                	li	s4,2
42011292:	fe377097          	auipc	ra,0xfe377
42011296:	128080e7          	jalr	296(ra) # 403883ba <esp_log_timestamp>
4201129a:	3d4b8363          	beq	s7,s4,42011660 <decoder_task+0xc7c>
4201129e:	4791                	li	a5,4
420112a0:	3afb8b63          	beq	s7,a5,42011656 <decoder_task+0xc72>
420112a4:	3c1267b7          	lui	a5,0x3c126
420112a8:	4705                	li	a4,1
420112aa:	89878793          	addi	a5,a5,-1896 # 3c125898 <_esp_trace_encoder_array_end+0x5778>
420112ae:	00eb8663          	beq	s7,a4,420112ba <decoder_task+0x8d6>
420112b2:	3c1267b7          	lui	a5,0x3c126
420112b6:	89c78793          	addi	a5,a5,-1892 # 3c12589c <_esp_trace_encoder_array_end+0x577c>
420112ba:	3c126737          	lui	a4,0x3c126
420112be:	8a470713          	addi	a4,a4,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
420112c2:	3c126637          	lui	a2,0x3c126
420112c6:	86aa                	mv	a3,a0
420112c8:	85ba                	mv	a1,a4
420112ca:	8822                	mv	a6,s0
420112cc:	bfc60613          	addi	a2,a2,-1028 # 3c125bfc <_esp_trace_encoder_array_end+0x5adc>
420112d0:	4509                	li	a0,2
420112d2:	fe377097          	auipc	ra,0xfe377
420112d6:	fe0080e7          	jalr	-32(ra) # 403882b2 <esp_log>
420112da:	3fc957b7          	lui	a5,0x3fc95
420112de:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
420112e2:	3c1267b7          	lui	a5,0x3c126
420112e6:	aa478693          	addi	a3,a5,-1372 # 3c125aa4 <_esp_trace_encoder_array_end+0x5984>
420112ea:	85a6                	mv	a1,s1
420112ec:	4601                	li	a2,0
420112ee:	0ee040ef          	jal	420153dc <native_state_set_audio>
420112f2:	8c26                	mv	s8,s1
420112f4:	4572                	lw	a0,28(sp)
420112f6:	c119                	beqz	a0,420112fc <decoder_task+0x918>
420112f8:	7ea260ef          	jal	42037ae2 <esp_audio_simple_dec_close>
420112fc:	ce02                	sw	zero,28(sp)
420112fe:	00090563          	beqz	s2,42011308 <decoder_task+0x924>
42011302:	854a                	mv	a0,s2
42011304:	5a0010ef          	jal	420128a4 <native_aac_decoder_destroy>
42011308:	854e                	mv	a0,s3
4201130a:	b8ef70ef          	jal	42008698 <cfree>
4201130e:	4901                	li	s2,0
42011310:	4a01                	li	s4,0
42011312:	4981                	li	s3,0
42011314:	beb1                	j	42010e70 <decoder_task+0x48c>
42011316:	854a                	mv	a0,s2
42011318:	151010ef          	jal	42012c68 <native_aac_decoder_source_channels>
4201131c:	01b14683          	lbu	a3,27(sp)
42011320:	0ff57513          	zext.b	a0,a0
42011324:	bc05                	j	42010d54 <decoder_task+0x370>
42011326:	204747b7          	lui	a5,0x20474
4201132a:	74f78793          	addi	a5,a5,1871 # 2047474f <_rtc_slow_length+0x204730ab>
4201132e:	086c                	addi	a1,sp,28
42011330:	10a8                	addi	a0,sp,104
42011332:	d4be                	sw	a5,104(sp)
42011334:	084150ef          	jal	420263b8 <__wrap_esp_audio_simple_dec_open>
42011338:	842a                	mv	s0,a0
4201133a:	22051463          	bnez	a0,42011562 <decoder_task+0xb7e>
4201133e:	4b72                	lw	s6,28(sp)
42011340:	4d81                	li	s11,0
42011342:	8e0b00e3          	beqz	s6,42010c22 <decoder_task+0x23e>
42011346:	4901                	li	s2,0
42011348:	4b01                	li	s6,0
4201134a:	ba11                	j	42010c5e <decoder_task+0x27a>
4201134c:	844e                	mv	s0,s3
4201134e:	b961                	j	42010fe6 <decoder_task+0x602>
42011350:	3c1267b7          	lui	a5,0x3c126
42011354:	bc878513          	addi	a0,a5,-1080 # 3c125bc8 <_esp_trace_encoder_array_end+0x5aa8>
42011358:	8b0ff0ef          	jal	42010408 <log_runtime_memory>
4201135c:	bd11                	j	42011170 <decoder_task+0x78c>
4201135e:	d682                	sw	zero,108(sp)
42011360:	d882                	sw	zero,112(sp)
42011362:	da82                	sw	zero,116(sp)
42011364:	833ff06f          	j	42010b96 <decoder_task+0x1b2>
42011368:	fe377097          	auipc	ra,0xfe377
4201136c:	052080e7          	jalr	82(ra) # 403883ba <esp_log_timestamp>
42011370:	4791                	li	a5,4
42011372:	4405                	li	s0,1
42011374:	86aa                	mv	a3,a0
42011376:	2afb8263          	beq	s7,a5,4201161a <decoder_task+0xc36>
4201137a:	3c1267b7          	lui	a5,0x3c126
4201137e:	89878793          	addi	a5,a5,-1896 # 3c125898 <_esp_trace_encoder_array_end+0x5778>
42011382:	008b8663          	beq	s7,s0,4201138e <decoder_task+0x9aa>
42011386:	3c1267b7          	lui	a5,0x3c126
4201138a:	89c78793          	addi	a5,a5,-1892 # 3c12589c <_esp_trace_encoder_array_end+0x577c>
4201138e:	3c126737          	lui	a4,0x3c126
42011392:	8a470713          	addi	a4,a4,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
42011396:	3c126637          	lui	a2,0x3c126
4201139a:	85ba                	mv	a1,a4
4201139c:	b2c60613          	addi	a2,a2,-1236 # 3c125b2c <_esp_trace_encoder_array_end+0x5a0c>
420113a0:	4505                	li	a0,1
420113a2:	fe377097          	auipc	ra,0xfe377
420113a6:	f10080e7          	jalr	-240(ra) # 403882b2 <esp_log>
420113aa:	3fc957b7          	lui	a5,0x3fc95
420113ae:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
420113b2:	3c1267b7          	lui	a5,0x3c126
420113b6:	a8878693          	addi	a3,a5,-1400 # 3c125a88 <_esp_trace_encoder_array_end+0x5968>
420113ba:	85a6                	mv	a1,s1
420113bc:	4601                	li	a2,0
420113be:	01e040ef          	jal	420153dc <native_state_set_audio>
420113c2:	3fc957b7          	lui	a5,0x3fc95
420113c6:	afc7a503          	lw	a0,-1284(a5) # 3fc94afc <s_encoded>
420113ca:	85e6                	mv	a1,s9
420113cc:	8c26                	mv	s8,s1
420113ce:	276660ef          	jal	42077644 <vRingbufferReturnItem>
420113d2:	4901                	li	s2,0
420113d4:	4d81                	li	s11,0
420113d6:	4b01                	li	s6,0
420113d8:	4d01                	li	s10,0
420113da:	e7aff06f          	j	42010a54 <decoder_task+0x70>
420113de:	fe377097          	auipc	ra,0xfe377
420113e2:	fdc080e7          	jalr	-36(ra) # 403883ba <esp_log_timestamp>
420113e6:	3c126737          	lui	a4,0x3c126
420113ea:	8a470713          	addi	a4,a4,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
420113ee:	3c126637          	lui	a2,0x3c126
420113f2:	85ba                	mv	a1,a4
420113f4:	86aa                	mv	a3,a0
420113f6:	87ea                	mv	a5,s10
420113f8:	ab460613          	addi	a2,a2,-1356 # 3c125ab4 <_esp_trace_encoder_array_end+0x5994>
420113fc:	4505                	li	a0,1
420113fe:	fe377097          	auipc	ra,0xfe377
42011402:	eb4080e7          	jalr	-332(ra) # 403882b2 <esp_log>
42011406:	3fc957b7          	lui	a5,0x3fc95
4201140a:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
4201140e:	000ca583          	lw	a1,0(s9)
42011412:	3c1267b7          	lui	a5,0x3c126
42011416:	ae478693          	addi	a3,a5,-1308 # 3c125ae4 <_esp_trace_encoder_array_end+0x59c4>
4201141a:	4601                	li	a2,0
4201141c:	7c1030ef          	jal	420153dc <native_state_set_audio>
42011420:	000cac03          	lw	s8,0(s9)
42011424:	8566                	mv	a0,s9
42011426:	84a2                	mv	s1,s0
42011428:	85e2                	mv	a1,s8
4201142a:	cf2ff0ef          	jal	4201091c <return_decoded_packet>
4201142e:	e26ff06f          	j	42010a54 <decoder_task+0x70>
42011432:	fe377097          	auipc	ra,0xfe377
42011436:	f88080e7          	jalr	-120(ra) # 403883ba <esp_log_timestamp>
4201143a:	4789                	li	a5,2
4201143c:	4405                	li	s0,1
4201143e:	1afb8163          	beq	s7,a5,420115e0 <decoder_task+0xbfc>
42011442:	4791                	li	a5,4
42011444:	22fb8363          	beq	s7,a5,4201166a <decoder_task+0xc86>
42011448:	3c1267b7          	lui	a5,0x3c126
4201144c:	89878793          	addi	a5,a5,-1896 # 3c125898 <_esp_trace_encoder_array_end+0x5778>
42011450:	008b8663          	beq	s7,s0,4201145c <decoder_task+0xa78>
42011454:	3c1267b7          	lui	a5,0x3c126
42011458:	89c78793          	addi	a5,a5,-1892 # 3c12589c <_esp_trace_encoder_array_end+0x577c>
4201145c:	48e6                	lw	a7,88(sp)
4201145e:	5806                	lw	a6,96(sp)
42011460:	3c126737          	lui	a4,0x3c126
42011464:	8a470713          	addi	a4,a4,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
42011468:	3c126637          	lui	a2,0x3c126
4201146c:	86aa                	mv	a3,a0
4201146e:	85ba                	mv	a1,a4
42011470:	c2060613          	addi	a2,a2,-992 # 3c125c20 <_esp_trace_encoder_array_end+0x5b00>
42011474:	4505                	li	a0,1
42011476:	fe377097          	auipc	ra,0xfe377
4201147a:	e3c080e7          	jalr	-452(ra) # 403882b2 <esp_log>
4201147e:	3fc957b7          	lui	a5,0x3fc95
42011482:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42011486:	3c1267b7          	lui	a5,0x3c126
4201148a:	c5c78693          	addi	a3,a5,-932 # 3c125c5c <_esp_trace_encoder_array_end+0x5b3c>
4201148e:	85a6                	mv	a1,s1
42011490:	4601                	li	a2,0
42011492:	74b030ef          	jal	420153dc <native_state_set_audio>
42011496:	8c26                	mv	s8,s1
42011498:	bdb1                	j	420112f4 <decoder_task+0x910>
4201149a:	b00b0fe3          	beqz	s6,42010fb8 <decoder_task+0x5d4>
4201149e:	b461                	j	42010f26 <decoder_task+0x542>
420114a0:	fe377097          	auipc	ra,0xfe377
420114a4:	f1a080e7          	jalr	-230(ra) # 403883ba <esp_log_timestamp>
420114a8:	3c1267b7          	lui	a5,0x3c126
420114ac:	8a478713          	addi	a4,a5,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
420114b0:	3c1267b7          	lui	a5,0x3c126
420114b4:	86aa                	mv	a3,a0
420114b6:	85ba                	mv	a1,a4
420114b8:	af878613          	addi	a2,a5,-1288 # 3c125af8 <_esp_trace_encoder_array_end+0x59d8>
420114bc:	4505                	li	a0,1
420114be:	fe377097          	auipc	ra,0xfe377
420114c2:	df4080e7          	jalr	-524(ra) # 403882b2 <esp_log>
420114c6:	3fc957b7          	lui	a5,0x3fc95
420114ca:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
420114ce:	3c1267b7          	lui	a5,0x3c126
420114d2:	a8878693          	addi	a3,a5,-1400 # 3c125a88 <_esp_trace_encoder_array_end+0x5968>
420114d6:	85a6                	mv	a1,s1
420114d8:	4601                	li	a2,0
420114da:	703030ef          	jal	420153dc <native_state_set_audio>
420114de:	8c26                	mv	s8,s1
420114e0:	8426                	mv	s0,s1
420114e2:	4901                	li	s2,0
420114e4:	4981                	li	s3,0
420114e6:	4a01                	li	s4,0
420114e8:	4d81                	li	s11,0
420114ea:	855a                	mv	a0,s6
420114ec:	2e2240ef          	jal	420357ce <custom_flac_decoder_destroy>
420114f0:	4b01                	li	s6,0
420114f2:	bcc9                	j	42010fc4 <decoder_task+0x5e0>
420114f4:	8542                	mv	a0,a6
420114f6:	b075                	j	42010da2 <decoder_task+0x3be>
420114f8:	3c1267b7          	lui	a5,0x3c126
420114fc:	89c78793          	addi	a5,a5,-1892 # 3c12589c <_esp_trace_encoder_array_end+0x577c>
42011500:	eccff06f          	j	42010bcc <decoder_task+0x1e8>
42011504:	01a14d83          	lbu	s11,26(sp)
42011508:	a80d8ce3          	beqz	s11,42010fa0 <decoder_task+0x5bc>
4201150c:	3c1267b7          	lui	a5,0x3c126
42011510:	b8478513          	addi	a0,a5,-1148 # 3c125b84 <_esp_trace_encoder_array_end+0x5a64>
42011514:	ef5fe0ef          	jal	42010408 <log_runtime_memory>
42011518:	b459                	j	42010f9e <decoder_task+0x5ba>
4201151a:	3c1267b7          	lui	a5,0x3c126
4201151e:	89c78593          	addi	a1,a5,-1892 # 3c12589c <_esp_trace_encoder_array_end+0x577c>
42011522:	b6c1                	j	420110e2 <decoder_task+0x6fe>
42011524:	fe377097          	auipc	ra,0xfe377
42011528:	e96080e7          	jalr	-362(ra) # 403883ba <esp_log_timestamp>
4201152c:	3c1267b7          	lui	a5,0x3c126
42011530:	8a478713          	addi	a4,a5,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
42011534:	3c126637          	lui	a2,0x3c126
42011538:	3c1267b7          	lui	a5,0x3c126
4201153c:	86aa                	mv	a3,a0
4201153e:	88878793          	addi	a5,a5,-1912 # 3c125888 <_esp_trace_encoder_array_end+0x5768>
42011542:	85ba                	mv	a1,a4
42011544:	b5c60613          	addi	a2,a2,-1188 # 3c125b5c <_esp_trace_encoder_array_end+0x5a3c>
42011548:	5879                	li	a6,-2
4201154a:	4505                	li	a0,1
4201154c:	fe377097          	auipc	ra,0xfe377
42011550:	d66080e7          	jalr	-666(ra) # 403882b2 <esp_log>
42011554:	3c1267b7          	lui	a5,0x3c126
42011558:	89a2                	mv	s3,s0
4201155a:	a8878693          	addi	a3,a5,-1400 # 3c125a88 <_esp_trace_encoder_array_end+0x5968>
4201155e:	e9aff06f          	j	42010bf8 <decoder_task+0x214>
42011562:	fe377097          	auipc	ra,0xfe377
42011566:	e58080e7          	jalr	-424(ra) # 403883ba <esp_log_timestamp>
4201156a:	3c1267b7          	lui	a5,0x3c126
4201156e:	86aa                	mv	a3,a0
42011570:	89478793          	addi	a5,a5,-1900 # 3c125894 <_esp_trace_encoder_array_end+0x5774>
42011574:	e58ff06f          	j	42010bcc <decoder_task+0x1e8>
42011578:	af0a8793          	addi	a5,s5,-1296
4201157c:	0330000f          	fence	rw,rw
42011580:	439c                	lw	a5,0(a5)
42011582:	0230000f          	fence	r,rw
42011586:	a29798e3          	bne	a5,s1,42010fb6 <decoder_task+0x5d2>
4201158a:	fe377097          	auipc	ra,0xfe377
4201158e:	e30080e7          	jalr	-464(ra) # 403883ba <esp_log_timestamp>
42011592:	3c126737          	lui	a4,0x3c126
42011596:	8a470713          	addi	a4,a4,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
4201159a:	3c126637          	lui	a2,0x3c126
4201159e:	86aa                	mv	a3,a0
420115a0:	87a2                	mv	a5,s0
420115a2:	85ba                	mv	a1,a4
420115a4:	b9c60613          	addi	a2,a2,-1124 # 3c125b9c <_esp_trace_encoder_array_end+0x5a7c>
420115a8:	4509                	li	a0,2
420115aa:	fe377097          	auipc	ra,0xfe377
420115ae:	d08080e7          	jalr	-760(ra) # 403882b2 <esp_log>
420115b2:	3c126737          	lui	a4,0x3c126
420115b6:	0419                	addi	s0,s0,6 # 3006 <_rtc_slow_length+0x1962>
420115b8:	4785                	li	a5,1
420115ba:	aa470693          	addi	a3,a4,-1372 # 3c125aa4 <_esp_trace_encoder_array_end+0x5984>
420115be:	0087e663          	bltu	a5,s0,420115ca <decoder_task+0xbe6>
420115c2:	3c1267b7          	lui	a5,0x3c126
420115c6:	a8878693          	addi	a3,a5,-1400 # 3c125a88 <_esp_trace_encoder_array_end+0x5968>
420115ca:	3fc957b7          	lui	a5,0x3fc95
420115ce:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
420115d2:	4601                	li	a2,0
420115d4:	85a6                	mv	a1,s1
420115d6:	607030ef          	jal	420153dc <native_state_set_audio>
420115da:	8c26                	mv	s8,s1
420115dc:	8426                	mv	s0,s1
420115de:	bae9                	j	42010fb8 <decoder_task+0x5d4>
420115e0:	3c1267b7          	lui	a5,0x3c126
420115e4:	88878793          	addi	a5,a5,-1912 # 3c125888 <_esp_trace_encoder_array_end+0x5768>
420115e8:	bd95                	j	4201145c <decoder_task+0xa78>
420115ea:	3c1267b7          	lui	a5,0x3c126
420115ee:	88878593          	addi	a1,a5,-1912 # 3c125888 <_esp_trace_encoder_array_end+0x5768>
420115f2:	bcc5                	j	420110e2 <decoder_task+0x6fe>
420115f4:	3c1267b7          	lui	a5,0x3c126
420115f8:	89478593          	addi	a1,a5,-1900 # 3c125894 <_esp_trace_encoder_array_end+0x5774>
420115fc:	b4dd                	j	420110e2 <decoder_task+0x6fe>
420115fe:	3fc957b7          	lui	a5,0x3fc95
42011602:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42011606:	3c1267b7          	lui	a5,0x3c126
4201160a:	be478693          	addi	a3,a5,-1052 # 3c125be4 <_esp_trace_encoder_array_end+0x5ac4>
4201160e:	4601                	li	a2,0
42011610:	85a6                	mv	a1,s1
42011612:	5cb030ef          	jal	420153dc <native_state_set_audio>
42011616:	8c26                	mv	s8,s1
42011618:	b9f1                	j	420112f4 <decoder_task+0x910>
4201161a:	3c1267b7          	lui	a5,0x3c126
4201161e:	89478793          	addi	a5,a5,-1900 # 3c125894 <_esp_trace_encoder_array_end+0x5774>
42011622:	b3b5                	j	4201138e <decoder_task+0x9aa>
42011624:	4c32                	lw	s8,12(sp)
42011626:	fe377097          	auipc	ra,0xfe377
4201162a:	d94080e7          	jalr	-620(ra) # 403883ba <esp_log_timestamp>
4201162e:	3c1267b7          	lui	a5,0x3c126
42011632:	8a478713          	addi	a4,a5,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
42011636:	3c1267b7          	lui	a5,0x3c126
4201163a:	86aa                	mv	a3,a0
4201163c:	85ba                	mv	a1,a4
4201163e:	c7078613          	addi	a2,a5,-912 # 3c125c70 <_esp_trace_encoder_array_end+0x5b50>
42011642:	4509                	li	a0,2
42011644:	fe377097          	auipc	ra,0xfe377
42011648:	c6e080e7          	jalr	-914(ra) # 403882b2 <esp_log>
4201164c:	4d85                	li	s11,1
4201164e:	817ff06f          	j	42010e64 <decoder_task+0x480>
42011652:	8462                	mv	s0,s8
42011654:	b935                	j	42011290 <decoder_task+0x8ac>
42011656:	3c1267b7          	lui	a5,0x3c126
4201165a:	89478793          	addi	a5,a5,-1900 # 3c125894 <_esp_trace_encoder_array_end+0x5774>
4201165e:	b9b1                	j	420112ba <decoder_task+0x8d6>
42011660:	3c1267b7          	lui	a5,0x3c126
42011664:	88878793          	addi	a5,a5,-1912 # 3c125888 <_esp_trace_encoder_array_end+0x5768>
42011668:	b989                	j	420112ba <decoder_task+0x8d6>
4201166a:	3c1267b7          	lui	a5,0x3c126
4201166e:	89478793          	addi	a5,a5,-1900 # 3c125894 <_esp_trace_encoder_array_end+0x5774>
42011672:	b3ed                	j	4201145c <decoder_task+0xa78>
42011674:	fe377097          	auipc	ra,0xfe377
42011678:	d46080e7          	jalr	-698(ra) # 403883ba <esp_log_timestamp>
4201167c:	4789                	li	a5,2
4201167e:	4405                	li	s0,1
42011680:	86aa                	mv	a3,a0
42011682:	04fb8b63          	beq	s7,a5,420116d8 <decoder_task+0xcf4>
42011686:	4791                	li	a5,4
42011688:	06fb8363          	beq	s7,a5,420116ee <decoder_task+0xd0a>
4201168c:	3c1267b7          	lui	a5,0x3c126
42011690:	89878793          	addi	a5,a5,-1896 # 3c125898 <_esp_trace_encoder_array_end+0x5778>
42011694:	008b8663          	beq	s7,s0,420116a0 <decoder_task+0xcbc>
42011698:	3c1267b7          	lui	a5,0x3c126
4201169c:	89c78793          	addi	a5,a5,-1892 # 3c12589c <_esp_trace_encoder_array_end+0x577c>
420116a0:	3c126737          	lui	a4,0x3c126
420116a4:	8a470713          	addi	a4,a4,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
420116a8:	3c126637          	lui	a2,0x3c126
420116ac:	85ba                	mv	a1,a4
420116ae:	c9060613          	addi	a2,a2,-880 # 3c125c90 <_esp_trace_encoder_array_end+0x5b70>
420116b2:	4505                	li	a0,1
420116b4:	fe377097          	auipc	ra,0xfe377
420116b8:	bfe080e7          	jalr	-1026(ra) # 403882b2 <esp_log>
420116bc:	3fc957b7          	lui	a5,0x3fc95
420116c0:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
420116c4:	3c1267b7          	lui	a5,0x3c126
420116c8:	cc078693          	addi	a3,a5,-832 # 3c125cc0 <_esp_trace_encoder_array_end+0x5ba0>
420116cc:	85a6                	mv	a1,s1
420116ce:	4601                	li	a2,0
420116d0:	50d030ef          	jal	420153dc <native_state_set_audio>
420116d4:	8c26                	mv	s8,s1
420116d6:	b939                	j	420112f4 <decoder_task+0x910>
420116d8:	3c1267b7          	lui	a5,0x3c126
420116dc:	88878793          	addi	a5,a5,-1912 # 3c125888 <_esp_trace_encoder_array_end+0x5768>
420116e0:	b7c1                	j	420116a0 <decoder_task+0xcbc>
420116e2:	3c1267b7          	lui	a5,0x3c126
420116e6:	a8878693          	addi	a3,a5,-1400 # 3c125a88 <_esp_trace_encoder_array_end+0x5968>
420116ea:	d0eff06f          	j	42010bf8 <decoder_task+0x214>
420116ee:	3c1267b7          	lui	a5,0x3c126
420116f2:	89478793          	addi	a5,a5,-1900 # 3c125894 <_esp_trace_encoder_array_end+0x5774>
420116f6:	b76d                	j	420116a0 <decoder_task+0xcbc>
420116f8:	fe377097          	auipc	ra,0xfe377
420116fc:	cc2080e7          	jalr	-830(ra) # 403883ba <esp_log_timestamp>
42011700:	3c1267b7          	lui	a5,0x3c126
42011704:	86aa                	mv	a3,a0
42011706:	88878793          	addi	a5,a5,-1912 # 3c125888 <_esp_trace_encoder_array_end+0x5768>
4201170a:	b151                	j	4201138e <decoder_task+0x9aa>
