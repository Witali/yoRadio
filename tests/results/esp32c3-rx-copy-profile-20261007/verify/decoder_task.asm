
idf\esp32c3-oled-native\build-rx-copy\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42010944 <decoder_task>:
42010944:	7151                	addi	sp,sp,-240
42010946:	d5a2                	sw	s0,232(sp)
42010948:	d3a6                	sw	s1,228(sp)
4201094a:	d1ca                	sw	s2,224(sp)
4201094c:	cfce                	sw	s3,220(sp)
4201094e:	cdd2                	sw	s4,216(sp)
42010950:	cbd6                	sw	s5,212(sp)
42010952:	c9da                	sw	s6,208(sp)
42010954:	c7de                	sw	s7,204(sp)
42010956:	c5e2                	sw	s8,200(sp)
42010958:	df6e                	sw	s11,188(sp)
4201095a:	d786                	sw	ra,236(sp)
4201095c:	c3e6                	sw	s9,196(sp)
4201095e:	c1ea                	sw	s10,192(sp)
42010960:	2e6020ef          	jal	42012c46 <decoder_register_codecs>
42010964:	3fc95737          	lui	a4,0x3fc95
42010968:	000f47b7          	lui	a5,0xf4
4201096c:	e4870713          	addi	a4,a4,-440 # 3fc94e48 <s_bitrate_updated_us>
42010970:	24078793          	addi	a5,a5,576 # f4240 <CSR_UINTSTATUS+0xf358f>
42010974:	ce02                	sw	zero,28(sp)
42010976:	c102                	sw	zero,128(sp)
42010978:	c302                	sw	zero,132(sp)
4201097a:	c502                	sw	zero,136(sp)
4201097c:	c702                	sw	zero,140(sp)
4201097e:	c902                	sw	zero,144(sp)
42010980:	cb02                	sw	zero,148(sp)
42010982:	cd02                	sw	zero,152(sp)
42010984:	cf02                	sw	zero,156(sp)
42010986:	d102                	sw	zero,160(sp)
42010988:	d302                	sw	zero,164(sp)
4201098a:	d502                	sw	zero,168(sp)
4201098c:	d702                	sw	zero,172(sp)
4201098e:	d202                	sw	zero,36(sp)
42010990:	d402                	sw	zero,40(sp)
42010992:	d602                	sw	zero,44(sp)
42010994:	d802                	sw	zero,48(sp)
42010996:	00010d23          	sb	zero,26(sp)
4201099a:	842a                	mv	s0,a0
4201099c:	c23a                	sw	a4,4(sp)
4201099e:	c43e                	sw	a5,8(sp)
420109a0:	4981                	li	s3,0
420109a2:	4a01                	li	s4,0
420109a4:	4901                	li	s2,0
420109a6:	4d81                	li	s11,0
420109a8:	4b01                	li	s6,0
420109aa:	4c01                	li	s8,0
420109ac:	4481                	li	s1,0
420109ae:	4b81                	li	s7,0
420109b0:	3fc95ab7          	lui	s5,0x3fc95
420109b4:	6ae160ef          	jal	42027062 <rx_copy_profile_poll>
420109b8:	e60a8793          	addi	a5,s5,-416 # 3fc94e60 <s_generation>
420109bc:	0330000f          	fence	rw,rw
420109c0:	0007ac83          	lw	s9,0(a5)
420109c4:	0230000f          	fence	r,rw
420109c8:	429c8163          	beq	s9,s1,42010dea <decoder_task+0x4a6>
420109cc:	3fc957b7          	lui	a5,0x3fc95
420109d0:	e5c78793          	addi	a5,a5,-420 # 3fc94e5c <s_decoder_target_codec>
420109d4:	0330000f          	fence	rw,rw
420109d8:	4384                	lw	s1,0(a5)
420109da:	0230000f          	fence	r,rw
420109de:	4572                	lw	a0,28(sp)
420109e0:	c119                	beqz	a0,420109e6 <decoder_task+0xa2>
420109e2:	0a6290ef          	jal	42039a88 <esp_audio_simple_dec_close>
420109e6:	854e                	mv	a0,s3
420109e8:	ce02                	sw	zero,28(sp)
420109ea:	2be020ef          	jal	42012ca8 <native_aac_decoder_destroy>
420109ee:	000b8563          	beqz	s7,420109f8 <decoder_task+0xb4>
420109f2:	855e                	mv	a0,s7
420109f4:	1ee250ef          	jal	42035be2 <custom_flac_decoder_destroy>
420109f8:	46048e63          	beqz	s1,42010e74 <decoder_task+0x530>
420109fc:	d202                	sw	zero,36(sp)
420109fe:	d402                	sw	zero,40(sp)
42010a00:	d602                	sw	zero,44(sp)
42010a02:	d802                	sw	zero,48(sp)
42010a04:	00010d23          	sb	zero,26(sp)
42010a08:	3fc957b7          	lui	a5,0x3fc95
42010a0c:	e5878793          	addi	a5,a5,-424 # 3fc94e58 <s_decoder_released_generation>
42010a10:	0310000f          	fence	rw,w
42010a14:	0197a023          	sw	s9,0(a5)
42010a18:	0330000f          	fence	rw,rw
42010a1c:	4b81                	li	s7,0
42010a1e:	84e6                	mv	s1,s9
42010a20:	4c01                	li	s8,0
42010a22:	4b01                	li	s6,0
42010a24:	4d81                	li	s11,0
42010a26:	4981                	li	s3,0
42010a28:	3fc957b7          	lui	a5,0x3fc95
42010a2c:	e6c7a503          	lw	a0,-404(a5) # 3fc94e6c <s_encoded>
42010a30:	4651                	li	a2,20
42010a32:	100c                	addi	a1,sp,32
42010a34:	d002                	sw	zero,32(sp)
42010a36:	339680ef          	jal	4207956e <xRingbufferReceive>
42010a3a:	8caa                	mv	s9,a0
42010a3c:	dd25                	beqz	a0,420109b4 <decoder_task+0x70>
42010a3e:	4118                	lw	a4,0(a0)
42010a40:	e60a8793          	addi	a5,s5,-416
42010a44:	0330000f          	fence	rw,rw
42010a48:	439c                	lw	a5,0(a5)
42010a4a:	0230000f          	fence	r,rw
42010a4e:	40f71b63          	bne	a4,a5,42010e64 <decoder_task+0x520>
42010a52:	411c                	lw	a5,0(a0)
42010a54:	41878863          	beq	a5,s8,42010e64 <decoder_task+0x520>
42010a58:	4158                	lw	a4,4(a0)
42010a5a:	e709                	bnez	a4,42010a64 <decoder_task+0x120>
42010a5c:	00a54703          	lbu	a4,10(a0)
42010a60:	3e071e63          	bnez	a4,42010e5c <decoder_task+0x518>
42010a64:	12041563          	bnez	s0,42010b8e <decoder_task+0x24a>
42010a68:	12f48c63          	beq	s1,a5,42010ba0 <decoder_task+0x25c>
42010a6c:	4572                	lw	a0,28(sp)
42010a6e:	c119                	beqz	a0,42010a74 <decoder_task+0x130>
42010a70:	018290ef          	jal	42039a88 <esp_audio_simple_dec_close>
42010a74:	854e                	mv	a0,s3
42010a76:	ce02                	sw	zero,28(sp)
42010a78:	230020ef          	jal	42012ca8 <native_aac_decoder_destroy>
42010a7c:	000b8563          	beqz	s7,42010a86 <decoder_task+0x142>
42010a80:	855e                	mv	a0,s7
42010a82:	160250ef          	jal	42035be2 <custom_flac_decoder_destroy>
42010a86:	4712                	lw	a4,4(sp)
42010a88:	000ca483          	lw	s1,0(s9)
42010a8c:	004cab03          	lw	s6,4(s9)
42010a90:	3fc957b7          	lui	a5,0x3fc95
42010a94:	e407a823          	sw	zero,-432(a5) # 3fc94e50 <s_published_bitrate_bps>
42010a98:	4801                	li	a6,0
42010a9a:	4781                	li	a5,0
42010a9c:	c31c                	sw	a5,0(a4)
42010a9e:	00010d23          	sb	zero,26(sp)
42010aa2:	01072223          	sw	a6,4(a4)
42010aa6:	fe371097          	auipc	ra,0xfe371
42010aaa:	894080e7          	jalr	-1900(ra) # 4038133a <esp_timer_get_time>
42010aae:	c52a                	sw	a0,136(sp)
42010ab0:	c902                	sw	zero,144(sp)
42010ab2:	cb02                	sw	zero,148(sp)
42010ab4:	cd02                	sw	zero,152(sp)
42010ab6:	cf02                	sw	zero,156(sp)
42010ab8:	d102                	sw	zero,160(sp)
42010aba:	d302                	sw	zero,164(sp)
42010abc:	d502                	sw	zero,168(sp)
42010abe:	d702                	sw	zero,172(sp)
42010ac0:	c126                	sw	s1,128(sp)
42010ac2:	c35a                	sw	s6,132(sp)
42010ac4:	c72e                	sw	a1,140(sp)
42010ac6:	478d                	li	a5,3
42010ac8:	3afb0c63          	beq	s6,a5,42010e80 <decoder_task+0x53c>
42010acc:	4789                	li	a5,2
42010ace:	48fb0363          	beq	s6,a5,42010f54 <decoder_task+0x610>
42010ad2:	640d                	lui	s0,0x3
42010ad4:	008a70e3          	bgeu	s4,s0,420112d4 <decoder_task+0x990>
42010ad8:	85a2                	mv	a1,s0
42010ada:	854a                	mv	a0,s2
42010adc:	a71f70ef          	jal	4200854c <realloc>
42010ae0:	7e050f63          	beqz	a0,420112de <decoder_task+0x99a>
42010ae4:	d682                	sw	zero,108(sp)
42010ae6:	d882                	sw	zero,112(sp)
42010ae8:	da82                	sw	zero,116(sp)
42010aea:	892a                	mv	s2,a0
42010aec:	8a22                	mv	s4,s0
42010aee:	4791                	li	a5,4
42010af0:	7afb0663          	beq	s6,a5,4201129c <decoder_task+0x958>
42010af4:	203357b7          	lui	a5,0x20335
42010af8:	04d78793          	addi	a5,a5,77 # 2033504d <CSR_UINTSTATUS+0x2033439c>
42010afc:	086c                	addi	a1,sp,28
42010afe:	10a8                	addi	a0,sp,104
42010b00:	d4be                	sw	a5,104(sp)
42010b02:	711150ef          	jal	42026a12 <__wrap_esp_audio_simple_dec_open>
42010b06:	842a                	mv	s0,a0
42010b08:	7a050663          	beqz	a0,420112b4 <decoder_task+0x970>
42010b0c:	fe378097          	auipc	ra,0xfe378
42010b10:	8ae080e7          	jalr	-1874(ra) # 403883ba <esp_log_timestamp>
42010b14:	3c1267b7          	lui	a5,0x3c126
42010b18:	4985                	li	s3,1
42010b1a:	86aa                	mv	a3,a0
42010b1c:	89878793          	addi	a5,a5,-1896 # 3c125898 <_esp_trace_encoder_array_end+0x5778>
42010b20:	0f3b1ce3          	bne	s6,s3,42011418 <decoder_task+0xad4>
42010b24:	3c126737          	lui	a4,0x3c126
42010b28:	8a470713          	addi	a4,a4,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
42010b2c:	3c126637          	lui	a2,0x3c126
42010b30:	85ba                	mv	a1,a4
42010b32:	8822                	mv	a6,s0
42010b34:	b5c60613          	addi	a2,a2,-1188 # 3c125b5c <_esp_trace_encoder_array_end+0x5a3c>
42010b38:	4505                	li	a0,1
42010b3a:	fe377097          	auipc	ra,0xfe377
42010b3e:	778080e7          	jalr	1912(ra) # 403882b2 <esp_log>
42010b42:	3c126737          	lui	a4,0x3c126
42010b46:	57f9                	li	a5,-2
42010b48:	a9470693          	addi	a3,a4,-1388 # 3c125a94 <_esp_trace_encoder_array_end+0x5974>
42010b4c:	2af400e3          	beq	s0,a5,420115ec <decoder_task+0xca8>
42010b50:	3fc957b7          	lui	a5,0x3fc95
42010b54:	e747a503          	lw	a0,-396(a5) # 3fc94e74 <s_state>
42010b58:	4601                	li	a2,0
42010b5a:	85a6                	mv	a1,s1
42010b5c:	4c5040ef          	jal	42015820 <native_state_set_audio>
42010b60:	4572                	lw	a0,28(sp)
42010b62:	c501                	beqz	a0,42010b6a <decoder_task+0x226>
42010b64:	725280ef          	jal	42039a88 <esp_audio_simple_dec_close>
42010b68:	ce02                	sw	zero,28(sp)
42010b6a:	854a                	mv	a0,s2
42010b6c:	9e5f70ef          	jal	42008550 <cfree>
42010b70:	8c26                	mv	s8,s1
42010b72:	4a01                	li	s4,0
42010b74:	4901                	li	s2,0
42010b76:	4b81                	li	s7,0
42010b78:	4d81                	li	s11,0
42010b7a:	3fc957b7          	lui	a5,0x3fc95
42010b7e:	e6c7a503          	lw	a0,-404(a5) # 3fc94e6c <s_encoded>
42010b82:	85e6                	mv	a1,s9
42010b84:	4981                	li	s3,0
42010b86:	265680ef          	jal	420795ea <vRingbufferReturnItem>
42010b8a:	4401                	li	s0,0
42010b8c:	b525                	j	420109b4 <decoder_task+0x70>
42010b8e:	0b8020ef          	jal	42012c46 <decoder_register_codecs>
42010b92:	842a                	mv	s0,a0
42010b94:	28051063          	bnez	a0,42010e14 <decoder_task+0x4d0>
42010b98:	000ca783          	lw	a5,0(s9)
42010b9c:	ecf498e3          	bne	s1,a5,42010a6c <decoder_task+0x128>
42010ba0:	004ca783          	lw	a5,4(s9)
42010ba4:	ed6794e3          	bne	a5,s6,42010a6c <decoder_task+0x128>
42010ba8:	478d                	li	a5,3
42010baa:	00fb09e3          	beq	s6,a5,420113bc <decoder_task+0xa78>
42010bae:	47f2                	lw	a5,28(sp)
42010bb0:	00f9e7b3          	or	a5,s3,a5
42010bb4:	d3f9                	beqz	a5,42010b7a <decoder_task+0x236>
42010bb6:	008cd783          	lhu	a5,8(s9)
42010bba:	00bc8713          	addi	a4,s9,11
42010bbe:	ce82                	sw	zero,92(sp)
42010bc0:	d082                	sw	zero,96(sp)
42010bc2:	d282                	sw	zero,100(sp)
42010bc4:	ccbe                	sw	a5,88(sp)
42010bc6:	caba                	sw	a4,84(sp)
42010bc8:	00acc703          	lbu	a4,10(s9)
42010bcc:	ffeb0693          	addi	a3,s6,-2
42010bd0:	0016b693          	seqz	a3,a3
42010bd4:	00e03733          	snez	a4,a4
42010bd8:	c036                	sw	a3,0(sp)
42010bda:	04e10e23          	sb	a4,92(sp)
42010bde:	3a098663          	beqz	s3,42010f8a <decoder_task+0x646>
42010be2:	e789                	bnez	a5,42010bec <decoder_task+0x2a8>
42010be4:	05c14783          	lbu	a5,92(sp)
42010be8:	1c078a63          	beqz	a5,42010dbc <decoder_task+0x478>
42010bec:	4781                	li	a5,0
42010bee:	4801                	li	a6,0
42010bf0:	de3e                	sw	a5,60(sp)
42010bf2:	c0c2                	sw	a6,64(sp)
42010bf4:	da4a                	sw	s2,52(sp)
42010bf6:	dc52                	sw	s4,56(sp)
42010bf8:	d082                	sw	zero,96(sp)
42010bfa:	fe370097          	auipc	ra,0xfe370
42010bfe:	740080e7          	jalr	1856(ra) # 4038133a <esp_timer_get_time>
42010c02:	842a                	mv	s0,a0
42010c04:	1850                	addi	a2,sp,52
42010c06:	08cc                	addi	a1,sp,84
42010c08:	854e                	mv	a0,s3
42010c0a:	0d4020ef          	jal	42012cde <native_aac_decoder_process>
42010c0e:	8d2a                	mv	s10,a0
42010c10:	fe370097          	auipc	ra,0xfe370
42010c14:	72a080e7          	jalr	1834(ra) # 4038133a <esp_timer_get_time>
42010c18:	47ca                	lw	a5,144(sp)
42010c1a:	46da                	lw	a3,148(sp)
42010c1c:	8d01                	sub	a0,a0,s0
42010c1e:	00a78733          	add	a4,a5,a0
42010c22:	00f737b3          	sltu	a5,a4,a5
42010c26:	97b6                	add	a5,a5,a3
42010c28:	cb3e                	sw	a5,148(sp)
42010c2a:	578a                	lw	a5,160(sp)
42010c2c:	c93a                	sw	a4,144(sp)
42010c2e:	571a                	lw	a4,164(sp)
42010c30:	0785                	addi	a5,a5,1
42010c32:	d13e                	sw	a5,160(sp)
42010c34:	00a77363          	bgeu	a4,a0,42010c3a <decoder_task+0x2f6>
42010c38:	d32a                	sw	a0,164(sp)
42010c3a:	8bfd                	andi	a5,a5,31
42010c3c:	56078963          	beqz	a5,420111ae <decoder_task+0x86a>
42010c40:	e60a8793          	addi	a5,s5,-416
42010c44:	0330000f          	fence	rw,rw
42010c48:	439c                	lw	a5,0(a5)
42010c4a:	0230000f          	fence	r,rw
42010c4e:	16979763          	bne	a5,s1,42010dbc <decoder_task+0x478>
42010c52:	57e1                	li	a5,-8
42010c54:	52fd0763          	beq	s10,a5,42011182 <decoder_task+0x83e>
42010c58:	5a0d1663          	bnez	s10,42011204 <decoder_task+0x8c0>
42010c5c:	5786                	lw	a5,96(sp)
42010c5e:	4766                	lw	a4,88(sp)
42010c60:	6ef76a63          	bltu	a4,a5,42011354 <decoder_task+0xa10>
42010c64:	8f1d                	sub	a4,a4,a5
42010c66:	56aa                	lw	a3,168(sp)
42010c68:	ccba                	sw	a4,88(sp)
42010c6a:	4756                	lw	a4,84(sp)
42010c6c:	96be                	add	a3,a3,a5
42010c6e:	d536                	sw	a3,168(sp)
42010c70:	97ba                	add	a5,a5,a4
42010c72:	4706                	lw	a4,64(sp)
42010c74:	cabe                	sw	a5,84(sp)
42010c76:	10070c63          	beqz	a4,42010d8e <decoder_task+0x44a>
42010c7a:	00cc                	addi	a1,sp,68
42010c7c:	854e                	mv	a0,s3
42010c7e:	c282                	sw	zero,68(sp)
42010c80:	c482                	sw	zero,72(sp)
42010c82:	c682                	sw	zero,76(sp)
42010c84:	c882                	sw	zero,80(sp)
42010c86:	380020ef          	jal	42013006 <native_aac_decoder_get_info>
42010c8a:	52051863          	bnez	a0,420111ba <decoder_task+0x876>
42010c8e:	4782                	lw	a5,0(sp)
42010c90:	01b10613          	addi	a2,sp,27
42010c94:	00cc                	addi	a1,sp,68
42010c96:	854e                	mv	a0,s3
42010c98:	00f10da3          	sb	a5,27(sp)
42010c9c:	378020ef          	jal	42013014 <native_aac_decoder_label>
42010ca0:	01b14683          	lbu	a3,27(sp)
42010ca4:	842a                	mv	s0,a0
42010ca6:	4501                	li	a0,0
42010ca8:	5e068263          	beqz	a3,4201128c <decoder_task+0x948>
42010cac:	e60a8793          	addi	a5,s5,-416
42010cb0:	0330000f          	fence	rw,rw
42010cb4:	4398                	lw	a4,0(a5)
42010cb6:	0230000f          	fence	r,rw
42010cba:	4781                	li	a5,0
42010cbc:	06971163          	bne	a4,s1,42010d1e <decoder_task+0x3da>
42010cc0:	4716                	lw	a4,68(sp)
42010cc2:	cf31                	beqz	a4,42010d1e <decoder_task+0x3da>
42010cc4:	04914803          	lbu	a6,73(sp)
42010cc8:	04080b63          	beqz	a6,42010d1e <decoder_task+0x3da>
42010ccc:	04814603          	lbu	a2,72(sp)
42010cd0:	c639                	beqz	a2,42010d1e <decoder_task+0x3da>
42010cd2:	45a6                	lw	a1,72(sp)
42010cd4:	47b6                	lw	a5,76(sp)
42010cd6:	d23a                	sw	a4,36(sp)
42010cd8:	d42e                	sw	a1,40(sp)
42010cda:	45c6                	lw	a1,80(sp)
42010cdc:	d63e                	sw	a5,44(sp)
42010cde:	4785                	li	a5,1
42010ce0:	06012923          	sw	zero,114(sp)
42010ce4:	06012b23          	sw	zero,118(sp)
42010ce8:	06011d23          	sh	zero,122(sp)
42010cec:	d4a2                	sw	s0,104(sp)
42010cee:	d6ba                	sw	a4,108(sp)
42010cf0:	d82e                	sw	a1,48(sp)
42010cf2:	00f10d23          	sb	a5,26(sp)
42010cf6:	70050f63          	beqz	a0,42011414 <decoder_task+0xad0>
42010cfa:	3fc957b7          	lui	a5,0x3fc95
42010cfe:	06a10823          	sb	a0,112(sp)
42010d02:	e747a503          	lw	a0,-396(a5) # 3fc94e74 <s_state>
42010d06:	06c108a3          	sb	a2,113(sp)
42010d0a:	85a6                	mv	a1,s1
42010d0c:	10b0                	addi	a2,sp,104
42010d0e:	daba                	sw	a4,116(sp)
42010d10:	07010c23          	sb	a6,120(sp)
42010d14:	06d10d23          	sb	a3,122(sp)
42010d18:	3e9040ef          	jal	42015900 <native_state_set_stream_info>
42010d1c:	4785                	li	a5,1
42010d1e:	45b6                	lw	a1,76(sp)
42010d20:	8526                	mv	a0,s1
42010d22:	00f10d23          	sb	a5,26(sp)
42010d26:	ea2ff0ef          	jal	420103c8 <state_set_decoder_bitrate>
42010d2a:	01a14783          	lbu	a5,26(sp)
42010d2e:	c3a5                	beqz	a5,42010d8e <decoder_task+0x44a>
42010d30:	4c0d8363          	beqz	s11,420111f6 <decoder_task+0x8b2>
42010d34:	02814503          	lbu	a0,40(sp)
42010d38:	02914783          	lbu	a5,41(sp)
42010d3c:	4406                	lw	s0,64(sp)
42010d3e:	051d                	addi	a0,a0,7
42010d40:	810d                	srli	a0,a0,0x3
42010d42:	02f50533          	mul	a0,a0,a5
42010d46:	c91d                	beqz	a0,42010d7c <decoder_task+0x438>
42010d48:	5612                	lw	a2,36(sp)
42010d4a:	ca0d                	beqz	a2,42010d7c <decoder_task+0x438>
42010d4c:	02a45533          	divu	a0,s0,a0
42010d50:	47a2                	lw	a5,8(sp)
42010d52:	4681                	li	a3,0
42010d54:	02f535b3          	mulhu	a1,a0,a5
42010d58:	02f50533          	mul	a0,a0,a5
42010d5c:	fdff0097          	auipc	ra,0xfdff0
42010d60:	b50080e7          	jalr	-1200(ra) # 400008ac <__udivdi3>
42010d64:	47ea                	lw	a5,152(sp)
42010d66:	46fa                	lw	a3,156(sp)
42010d68:	573a                	lw	a4,172(sp)
42010d6a:	953e                	add	a0,a0,a5
42010d6c:	96ae                	add	a3,a3,a1
42010d6e:	00f537b3          	sltu	a5,a0,a5
42010d72:	97b6                	add	a5,a5,a3
42010d74:	9722                	add	a4,a4,s0
42010d76:	cf3e                	sw	a5,156(sp)
42010d78:	cd2a                	sw	a0,152(sp)
42010d7a:	d73a                	sw	a4,172(sp)
42010d7c:	86a2                	mv	a3,s0
42010d7e:	864a                	mv	a2,s2
42010d80:	104c                	addi	a1,sp,36
42010d82:	8526                	mv	a0,s1
42010d84:	a85ff0ef          	jal	42010808 <send_pcm.isra.0>
42010d88:	8daa                	mv	s11,a0
42010d8a:	74050a63          	beqz	a0,420114de <decoder_task+0xb9a>
42010d8e:	fe370097          	auipc	ra,0xfe370
42010d92:	5ac080e7          	jalr	1452(ra) # 4038133a <esp_timer_get_time>
42010d96:	862e                	mv	a2,a1
42010d98:	85aa                	mv	a1,a0
42010d9a:	0108                	addi	a0,sp,128
42010d9c:	9a0ff0ef          	jal	4200ff3c <decode_stats_report>
42010da0:	4706                	lw	a4,64(sp)
42010da2:	5786                	lw	a5,96(sp)
42010da4:	05c14683          	lbu	a3,92(sp)
42010da8:	8fd9                	or	a5,a5,a4
42010daa:	3c079663          	bnez	a5,42011176 <decoder_task+0x832>
42010dae:	76068e63          	beqz	a3,4201152a <decoder_task+0xbe6>
42010db2:	4701                	li	a4,0
42010db4:	47e6                	lw	a5,88(sp)
42010db6:	8f5d                	or	a4,a4,a5
42010db8:	e20715e3          	bnez	a4,42010be2 <decoder_task+0x29e>
42010dbc:	00acc783          	lbu	a5,10(s9)
42010dc0:	4a079563          	bnez	a5,4201126a <decoder_task+0x926>
42010dc4:	4a9c0363          	beq	s8,s1,4201126a <decoder_task+0x926>
42010dc8:	8566                	mv	a0,s9
42010dca:	85e2                	mv	a1,s8
42010dcc:	975ff0ef          	jal	42010740 <return_decoded_packet>
42010dd0:	4401                	li	s0,0
42010dd2:	290160ef          	jal	42027062 <rx_copy_profile_poll>
42010dd6:	e60a8793          	addi	a5,s5,-416
42010dda:	0330000f          	fence	rw,rw
42010dde:	0007ac83          	lw	s9,0(a5)
42010de2:	0230000f          	fence	r,rw
42010de6:	be9c93e3          	bne	s9,s1,420109cc <decoder_task+0x88>
42010dea:	c20c0fe3          	beqz	s8,42010a28 <decoder_task+0xe4>
42010dee:	c29c1de3          	bne	s8,s1,42010a28 <decoder_task+0xe4>
42010df2:	4572                	lw	a0,28(sp)
42010df4:	c119                	beqz	a0,42010dfa <decoder_task+0x4b6>
42010df6:	493280ef          	jal	42039a88 <esp_audio_simple_dec_close>
42010dfa:	ce02                	sw	zero,28(sp)
42010dfc:	00098563          	beqz	s3,42010e06 <decoder_task+0x4c2>
42010e00:	854e                	mv	a0,s3
42010e02:	6a7010ef          	jal	42012ca8 <native_aac_decoder_destroy>
42010e06:	854a                	mv	a0,s2
42010e08:	f48f70ef          	jal	42008550 <cfree>
42010e0c:	4981                	li	s3,0
42010e0e:	4a01                	li	s4,0
42010e10:	4901                	li	s2,0
42010e12:	b919                	j	42010a28 <decoder_task+0xe4>
42010e14:	fe377097          	auipc	ra,0xfe377
42010e18:	5a6080e7          	jalr	1446(ra) # 403883ba <esp_log_timestamp>
42010e1c:	3c126737          	lui	a4,0x3c126
42010e20:	8a470713          	addi	a4,a4,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
42010e24:	3c126637          	lui	a2,0x3c126
42010e28:	86aa                	mv	a3,a0
42010e2a:	85ba                	mv	a1,a4
42010e2c:	87a2                	mv	a5,s0
42010e2e:	ab460613          	addi	a2,a2,-1356 # 3c125ab4 <_esp_trace_encoder_array_end+0x5994>
42010e32:	4505                	li	a0,1
42010e34:	fe377097          	auipc	ra,0xfe377
42010e38:	47e080e7          	jalr	1150(ra) # 403882b2 <esp_log>
42010e3c:	3fc957b7          	lui	a5,0x3fc95
42010e40:	e747a503          	lw	a0,-396(a5) # 3fc94e74 <s_state>
42010e44:	000ca583          	lw	a1,0(s9)
42010e48:	3c1267b7          	lui	a5,0x3c126
42010e4c:	ae478693          	addi	a3,a5,-1308 # 3c125ae4 <_esp_trace_encoder_array_end+0x59c4>
42010e50:	4601                	li	a2,0
42010e52:	1cf040ef          	jal	42015820 <native_state_set_audio>
42010e56:	000cac03          	lw	s8,0(s9)
42010e5a:	8566                	mv	a0,s9
42010e5c:	85e2                	mv	a1,s8
42010e5e:	8e3ff0ef          	jal	42010740 <return_decoded_packet>
42010e62:	be89                	j	420109b4 <decoder_task+0x70>
42010e64:	3fc957b7          	lui	a5,0x3fc95
42010e68:	e6c7a503          	lw	a0,-404(a5) # 3fc94e6c <s_encoded>
42010e6c:	85e6                	mv	a1,s9
42010e6e:	77c680ef          	jal	420795ea <vRingbufferReturnItem>
42010e72:	b689                	j	420109b4 <decoder_task+0x70>
42010e74:	854a                	mv	a0,s2
42010e76:	edaf70ef          	jal	42008550 <cfree>
42010e7a:	4a01                	li	s4,0
42010e7c:	4901                	li	s2,0
42010e7e:	bebd                	j	420109fc <decoder_task+0xb8>
42010e80:	854a                	mv	a0,s2
42010e82:	ecef70ef          	jal	42008550 <cfree>
42010e86:	4fd240ef          	jal	42035b82 <custom_flac_decoder_create>
42010e8a:	8baa                	mv	s7,a0
42010e8c:	52050b63          	beqz	a0,420113c2 <decoder_task+0xa7e>
42010e90:	4981                	li	s3,0
42010e92:	4a01                	li	s4,0
42010e94:	4901                	li	s2,0
42010e96:	4d81                	li	s11,0
42010e98:	4661                	li	a2,24
42010e9a:	4581                	li	a1,0
42010e9c:	10a8                	addi	a0,sp,104
42010e9e:	fdfef097          	auipc	ra,0xfdfef
42010ea2:	4b6080e7          	jalr	1206(ra) # 40000354 <memset>
42010ea6:	011c                	addi	a5,sp,128
42010ea8:	ccbe                	sw	a5,88(sp)
42010eaa:	105c                	addi	a5,sp,36
42010eac:	cebe                	sw	a5,92(sp)
42010eae:	01a10793          	addi	a5,sp,26
42010eb2:	d0be                	sw	a5,96(sp)
42010eb4:	caa6                	sw	s1,84(sp)
42010eb6:	00acc683          	lbu	a3,10(s9)
42010eba:	008cd603          	lhu	a2,8(s9)
42010ebe:	42011737          	lui	a4,0x42011
42010ec2:	00d036b3          	snez	a3,a3
42010ec6:	08dc                	addi	a5,sp,84
42010ec8:	61670713          	addi	a4,a4,1558 # 42011616 <custom_flac_output>
42010ecc:	00bc8593          	addi	a1,s9,11
42010ed0:	06810813          	addi	a6,sp,104
42010ed4:	855e                	mv	a0,s7
42010ed6:	533240ef          	jal	42035c08 <custom_flac_decoder_feed>
42010eda:	47ca                	lw	a5,144(sp)
42010edc:	5726                	lw	a4,104(sp)
42010ede:	465a                	lw	a2,148(sp)
42010ee0:	55b6                	lw	a1,108(sp)
42010ee2:	568a                	lw	a3,160(sp)
42010ee4:	973e                	add	a4,a4,a5
42010ee6:	842a                	mv	s0,a0
42010ee8:	5546                	lw	a0,112(sp)
42010eea:	962e                	add	a2,a2,a1
42010eec:	00f737b3          	sltu	a5,a4,a5
42010ef0:	97b2                	add	a5,a5,a2
42010ef2:	55d6                	lw	a1,116(sp)
42010ef4:	561a                	lw	a2,164(sp)
42010ef6:	96aa                	add	a3,a3,a0
42010ef8:	c93a                	sw	a4,144(sp)
42010efa:	cb3e                	sw	a5,148(sp)
42010efc:	d136                	sw	a3,160(sp)
42010efe:	00b67363          	bgeu	a2,a1,42010f04 <decoder_task+0x5c0>
42010f02:	d32e                	sw	a1,164(sp)
42010f04:	57aa                	lw	a5,168(sp)
42010f06:	5766                	lw	a4,120(sp)
42010f08:	97ba                	add	a5,a5,a4
42010f0a:	d53e                	sw	a5,168(sp)
42010f0c:	500d8c63          	beqz	s11,42011424 <decoder_task+0xae0>
42010f10:	4d85                	li	s11,1
42010f12:	fe370097          	auipc	ra,0xfe370
42010f16:	428080e7          	jalr	1064(ra) # 4038133a <esp_timer_get_time>
42010f1a:	862e                	mv	a2,a1
42010f1c:	85aa                	mv	a1,a0
42010f1e:	0108                	addi	a0,sp,128
42010f20:	81cff0ef          	jal	4200ff3c <decode_stats_report>
42010f24:	00045b63          	bgez	s0,42010f3a <decoder_task+0x5f6>
42010f28:	e60a8793          	addi	a5,s5,-416
42010f2c:	0330000f          	fence	rw,rw
42010f30:	439c                	lw	a5,0(a5)
42010f32:	0230000f          	fence	r,rw
42010f36:	64978c63          	beq	a5,s1,4201158e <decoder_task+0xc4a>
42010f3a:	00acc783          	lbu	a5,10(s9)
42010f3e:	4c079663          	bnez	a5,4201140a <decoder_task+0xac6>
42010f42:	4c9c0463          	beq	s8,s1,4201140a <decoder_task+0xac6>
42010f46:	8566                	mv	a0,s9
42010f48:	85e2                	mv	a1,s8
42010f4a:	ff6ff0ef          	jal	42010740 <return_decoded_packet>
42010f4e:	4b0d                	li	s6,3
42010f50:	4401                	li	s0,0
42010f52:	b48d                	j	420109b4 <decoder_task+0x70>
42010f54:	6589                	lui	a1,0x2
42010f56:	36ba0663          	beq	s4,a1,420112c2 <decoder_task+0x97e>
42010f5a:	854a                	mv	a0,s2
42010f5c:	df0f70ef          	jal	4200854c <realloc>
42010f60:	842a                	mv	s0,a0
42010f62:	6a050063          	beqz	a0,42011602 <decoder_task+0xcbe>
42010f66:	204347b7          	lui	a5,0x20434
42010f6a:	14178793          	addi	a5,a5,321 # 20434141 <CSR_UINTSTATUS+0x20433490>
42010f6e:	d682                	sw	zero,108(sp)
42010f70:	d882                	sw	zero,112(sp)
42010f72:	da82                	sw	zero,116(sp)
42010f74:	d4be                	sw	a5,104(sp)
42010f76:	507010ef          	jal	42012c7c <native_aac_decoder_create>
42010f7a:	89aa                	mv	s3,a0
42010f7c:	4c050463          	beqz	a0,42011444 <decoder_task+0xb00>
42010f80:	8922                	mv	s2,s0
42010f82:	6a09                	lui	s4,0x2
42010f84:	4b81                	li	s7,0
42010f86:	4d81                	li	s11,0
42010f88:	b13d                	j	42010bb6 <decoder_task+0x272>
42010f8a:	5d61                	li	s10,-8
42010f8c:	c662                	sw	s8,12(sp)
42010f8e:	e789                	bnez	a5,42010f98 <decoder_task+0x654>
42010f90:	05c14783          	lbu	a5,92(sp)
42010f94:	1c078f63          	beqz	a5,42011172 <decoder_task+0x82e>
42010f98:	4781                	li	a5,0
42010f9a:	4801                	li	a6,0
42010f9c:	de3e                	sw	a5,60(sp)
42010f9e:	c0c2                	sw	a6,64(sp)
42010fa0:	da4a                	sw	s2,52(sp)
42010fa2:	dc52                	sw	s4,56(sp)
42010fa4:	d082                	sw	zero,96(sp)
42010fa6:	fe370097          	auipc	ra,0xfe370
42010faa:	394080e7          	jalr	916(ra) # 4038133a <esp_timer_get_time>
42010fae:	842a                	mv	s0,a0
42010fb0:	4572                	lw	a0,28(sp)
42010fb2:	1850                	addi	a2,sp,52
42010fb4:	08cc                	addi	a1,sp,84
42010fb6:	3e9150ef          	jal	42026b9e <__wrap_esp_audio_simple_dec_process>
42010fba:	8c2a                	mv	s8,a0
42010fbc:	fe370097          	auipc	ra,0xfe370
42010fc0:	37e080e7          	jalr	894(ra) # 4038133a <esp_timer_get_time>
42010fc4:	47ca                	lw	a5,144(sp)
42010fc6:	46da                	lw	a3,148(sp)
42010fc8:	8d01                	sub	a0,a0,s0
42010fca:	00a78733          	add	a4,a5,a0
42010fce:	00f737b3          	sltu	a5,a4,a5
42010fd2:	97b6                	add	a5,a5,a3
42010fd4:	cb3e                	sw	a5,148(sp)
42010fd6:	578a                	lw	a5,160(sp)
42010fd8:	c93a                	sw	a4,144(sp)
42010fda:	571a                	lw	a4,164(sp)
42010fdc:	0785                	addi	a5,a5,1
42010fde:	d13e                	sw	a5,160(sp)
42010fe0:	00a77363          	bgeu	a4,a0,42010fe6 <decoder_task+0x6a2>
42010fe4:	d32a                	sw	a0,164(sp)
42010fe6:	8bfd                	andi	a5,a5,31
42010fe8:	1e078e63          	beqz	a5,420111e4 <decoder_task+0x8a0>
42010fec:	e60a8793          	addi	a5,s5,-416
42010ff0:	0330000f          	fence	rw,rw
42010ff4:	439c                	lw	a5,0(a5)
42010ff6:	0230000f          	fence	r,rw
42010ffa:	16979c63          	bne	a5,s1,42011172 <decoder_task+0x82e>
42010ffe:	1dac0763          	beq	s8,s10,420111cc <decoder_task+0x888>
42011002:	500c1363          	bnez	s8,42011508 <decoder_task+0xbc4>
42011006:	5786                	lw	a5,96(sp)
42011008:	4766                	lw	a4,88(sp)
4201100a:	34f76563          	bltu	a4,a5,42011354 <decoder_task+0xa10>
4201100e:	8f1d                	sub	a4,a4,a5
42011010:	56aa                	lw	a3,168(sp)
42011012:	ccba                	sw	a4,88(sp)
42011014:	4756                	lw	a4,84(sp)
42011016:	96be                	add	a3,a3,a5
42011018:	d536                	sw	a3,168(sp)
4201101a:	97ba                	add	a5,a5,a4
4201101c:	4706                	lw	a4,64(sp)
4201101e:	cabe                	sw	a5,84(sp)
42011020:	12070363          	beqz	a4,42011146 <decoder_task+0x802>
42011024:	4572                	lw	a0,28(sp)
42011026:	00cc                	addi	a1,sp,68
42011028:	c282                	sw	zero,68(sp)
4201102a:	c482                	sw	zero,72(sp)
4201102c:	c682                	sw	zero,76(sp)
4201102e:	c882                	sw	zero,80(sp)
42011030:	1e1280ef          	jal	42039a10 <esp_audio_simple_dec_get_info>
42011034:	1a051e63          	bnez	a0,420111f0 <decoder_task+0x8ac>
42011038:	4782                	lw	a5,0(sp)
4201103a:	00f10da3          	sb	a5,27(sp)
4201103e:	4789                	li	a5,2
42011040:	46fb0663          	beq	s6,a5,420114ac <decoder_task+0xb68>
42011044:	4791                	li	a5,4
42011046:	44fb0e63          	beq	s6,a5,420114a2 <decoder_task+0xb5e>
4201104a:	3c126737          	lui	a4,0x3c126
4201104e:	4785                	li	a5,1
42011050:	89870593          	addi	a1,a4,-1896 # 3c125898 <_esp_trace_encoder_array_end+0x5778>
42011054:	3efb1363          	bne	s6,a5,4201143a <decoder_task+0xaf6>
42011058:	e60a8793          	addi	a5,s5,-416
4201105c:	0330000f          	fence	rw,rw
42011060:	439c                	lw	a5,0(a5)
42011062:	0230000f          	fence	r,rw
42011066:	06979463          	bne	a5,s1,420110ce <decoder_task+0x78a>
4201106a:	4796                	lw	a5,68(sp)
4201106c:	c3b5                	beqz	a5,420110d0 <decoder_task+0x78c>
4201106e:	04914683          	lbu	a3,73(sp)
42011072:	ceb1                	beqz	a3,420110ce <decoder_task+0x78a>
42011074:	04815703          	lhu	a4,72(sp)
42011078:	04814503          	lbu	a0,72(sp)
4201107c:	00875613          	srli	a2,a4,0x8
42011080:	0722                	slli	a4,a4,0x8
42011082:	963a                	add	a2,a2,a4
42011084:	c529                	beqz	a0,420110ce <decoder_task+0x78a>
42011086:	06012b23          	sw	zero,118(sp)
4201108a:	06012923          	sw	zero,114(sp)
4201108e:	d23e                	sw	a5,36(sp)
42011090:	06c11823          	sh	a2,112(sp)
42011094:	d6be                	sw	a5,108(sp)
42011096:	4626                	lw	a2,72(sp)
42011098:	dabe                	sw	a5,116(sp)
4201109a:	3fc957b7          	lui	a5,0x3fc95
4201109e:	4746                	lw	a4,80(sp)
420110a0:	e747a503          	lw	a0,-396(a5) # 3fc94e74 <s_state>
420110a4:	06d10c23          	sb	a3,120(sp)
420110a8:	4782                	lw	a5,0(sp)
420110aa:	46b6                	lw	a3,76(sp)
420110ac:	06011d23          	sh	zero,122(sp)
420110b0:	d4ae                	sw	a1,104(sp)
420110b2:	d432                	sw	a2,40(sp)
420110b4:	4405                	li	s0,1
420110b6:	10b0                	addi	a2,sp,104
420110b8:	85a6                	mv	a1,s1
420110ba:	06f10d23          	sb	a5,122(sp)
420110be:	d636                	sw	a3,44(sp)
420110c0:	d83a                	sw	a4,48(sp)
420110c2:	00810d23          	sb	s0,26(sp)
420110c6:	03b040ef          	jal	42015900 <native_state_set_stream_info>
420110ca:	87a2                	mv	a5,s0
420110cc:	a011                	j	420110d0 <decoder_task+0x78c>
420110ce:	4781                	li	a5,0
420110d0:	45b6                	lw	a1,76(sp)
420110d2:	8526                	mv	a0,s1
420110d4:	00f10d23          	sb	a5,26(sp)
420110d8:	af0ff0ef          	jal	420103c8 <state_set_decoder_bitrate>
420110dc:	01a14783          	lbu	a5,26(sp)
420110e0:	c3bd                	beqz	a5,42011146 <decoder_task+0x802>
420110e2:	1e0d8263          	beqz	s11,420112c6 <decoder_task+0x982>
420110e6:	02814503          	lbu	a0,40(sp)
420110ea:	02914783          	lbu	a5,41(sp)
420110ee:	4406                	lw	s0,64(sp)
420110f0:	051d                	addi	a0,a0,7
420110f2:	810d                	srli	a0,a0,0x3
420110f4:	02f50533          	mul	a0,a0,a5
420110f8:	cd15                	beqz	a0,42011134 <decoder_task+0x7f0>
420110fa:	5612                	lw	a2,36(sp)
420110fc:	ce05                	beqz	a2,42011134 <decoder_task+0x7f0>
420110fe:	02a45533          	divu	a0,s0,a0
42011102:	000f47b7          	lui	a5,0xf4
42011106:	24078793          	addi	a5,a5,576 # f4240 <CSR_UINTSTATUS+0xf358f>
4201110a:	4681                	li	a3,0
4201110c:	02f535b3          	mulhu	a1,a0,a5
42011110:	02f50533          	mul	a0,a0,a5
42011114:	fdfef097          	auipc	ra,0xfdfef
42011118:	798080e7          	jalr	1944(ra) # 400008ac <__udivdi3>
4201111c:	47ea                	lw	a5,152(sp)
4201111e:	46fa                	lw	a3,156(sp)
42011120:	573a                	lw	a4,172(sp)
42011122:	953e                	add	a0,a0,a5
42011124:	96ae                	add	a3,a3,a1
42011126:	00f537b3          	sltu	a5,a0,a5
4201112a:	97b6                	add	a5,a5,a3
4201112c:	9722                	add	a4,a4,s0
4201112e:	cf3e                	sw	a5,156(sp)
42011130:	cd2a                	sw	a0,152(sp)
42011132:	d73a                	sw	a4,172(sp)
42011134:	86a2                	mv	a3,s0
42011136:	864a                	mv	a2,s2
42011138:	104c                	addi	a1,sp,36
4201113a:	8526                	mv	a0,s1
4201113c:	eccff0ef          	jal	42010808 <send_pcm.isra.0>
42011140:	8daa                	mv	s11,a0
42011142:	38050d63          	beqz	a0,420114dc <decoder_task+0xb98>
42011146:	fe370097          	auipc	ra,0xfe370
4201114a:	1f4080e7          	jalr	500(ra) # 4038133a <esp_timer_get_time>
4201114e:	862e                	mv	a2,a1
42011150:	85aa                	mv	a1,a0
42011152:	0108                	addi	a0,sp,128
42011154:	de9fe0ef          	jal	4200ff3c <decode_stats_report>
42011158:	4706                	lw	a4,64(sp)
4201115a:	5786                	lw	a5,96(sp)
4201115c:	05c14683          	lbu	a3,92(sp)
42011160:	8fd9                	or	a5,a5,a4
42011162:	efb9                	bnez	a5,420111c0 <decoder_task+0x87c>
42011164:	3c068363          	beqz	a3,4201152a <decoder_task+0xbe6>
42011168:	4701                	li	a4,0
4201116a:	47e6                	lw	a5,88(sp)
4201116c:	8f5d                	or	a4,a4,a5
4201116e:	e20710e3          	bnez	a4,42010f8e <decoder_task+0x64a>
42011172:	4c32                	lw	s8,12(sp)
42011174:	b1a1                	j	42010dbc <decoder_task+0x478>
42011176:	c2069fe3          	bnez	a3,42010db4 <decoder_task+0x470>
4201117a:	47e6                	lw	a5,88(sp)
4201117c:	a60798e3          	bnez	a5,42010bec <decoder_task+0x2a8>
42011180:	b935                	j	42010dbc <decoder_task+0x478>
42011182:	5706                	lw	a4,96(sp)
42011184:	47d6                	lw	a5,84(sp)
42011186:	56aa                	lw	a3,168(sp)
42011188:	5472                	lw	s0,60(sp)
4201118a:	97ba                	add	a5,a5,a4
4201118c:	cabe                	sw	a5,84(sp)
4201118e:	47e6                	lw	a5,88(sp)
42011190:	96ba                	add	a3,a3,a4
42011192:	d536                	sw	a3,168(sp)
42011194:	8f99                	sub	a5,a5,a4
42011196:	ccbe                	sw	a5,88(sp)
42011198:	308a7f63          	bgeu	s4,s0,420114b6 <decoder_task+0xb72>
4201119c:	85a2                	mv	a1,s0
4201119e:	854a                	mv	a0,s2
420111a0:	bacf70ef          	jal	4200854c <realloc>
420111a4:	30050963          	beqz	a0,420114b6 <decoder_task+0xb72>
420111a8:	8a22                	mv	s4,s0
420111aa:	892a                	mv	s2,a0
420111ac:	b481                	j	42010bec <decoder_task+0x2a8>
420111ae:	4505                	li	a0,1
420111b0:	00102097          	auipc	ra,0x102
420111b4:	0f2080e7          	jalr	242(ra) # 421132a2 <vTaskDelay>
420111b8:	b461                	j	42010c40 <decoder_task+0x2fc>
420111ba:	00010d23          	sb	zero,26(sp)
420111be:	bec1                	j	42010d8e <decoder_task+0x44a>
420111c0:	f6cd                	bnez	a3,4201116a <decoder_task+0x826>
420111c2:	47e6                	lw	a5,88(sp)
420111c4:	dc079ae3          	bnez	a5,42010f98 <decoder_task+0x654>
420111c8:	4c32                	lw	s8,12(sp)
420111ca:	becd                	j	42010dbc <decoder_task+0x478>
420111cc:	5472                	lw	s0,60(sp)
420111ce:	2e8a7463          	bgeu	s4,s0,420114b6 <decoder_task+0xb72>
420111d2:	85a2                	mv	a1,s0
420111d4:	854a                	mv	a0,s2
420111d6:	b76f70ef          	jal	4200854c <realloc>
420111da:	2c050e63          	beqz	a0,420114b6 <decoder_task+0xb72>
420111de:	892a                	mv	s2,a0
420111e0:	8a22                	mv	s4,s0
420111e2:	bb5d                	j	42010f98 <decoder_task+0x654>
420111e4:	4505                	li	a0,1
420111e6:	00102097          	auipc	ra,0x102
420111ea:	0bc080e7          	jalr	188(ra) # 421132a2 <vTaskDelay>
420111ee:	bbfd                	j	42010fec <decoder_task+0x6a8>
420111f0:	00010d23          	sb	zero,26(sp)
420111f4:	bf89                	j	42011146 <decoder_task+0x802>
420111f6:	3c1267b7          	lui	a5,0x3c126
420111fa:	bc878513          	addi	a0,a5,-1080 # 3c125bc8 <_esp_trace_encoder_array_end+0x5aa8>
420111fe:	966ff0ef          	jal	42010364 <log_runtime_memory>
42011202:	be0d                	j	42010d34 <decoder_task+0x3f0>
42011204:	846a                	mv	s0,s10
42011206:	4a09                	li	s4,2
42011208:	fe377097          	auipc	ra,0xfe377
4201120c:	1b2080e7          	jalr	434(ra) # 403883ba <esp_log_timestamp>
42011210:	2f4b0e63          	beq	s6,s4,4201150c <decoder_task+0xbc8>
42011214:	4791                	li	a5,4
42011216:	30fb0063          	beq	s6,a5,42011516 <decoder_task+0xbd2>
4201121a:	3c1267b7          	lui	a5,0x3c126
4201121e:	4705                	li	a4,1
42011220:	89878793          	addi	a5,a5,-1896 # 3c125898 <_esp_trace_encoder_array_end+0x5778>
42011224:	00eb0663          	beq	s6,a4,42011230 <decoder_task+0x8ec>
42011228:	3c1267b7          	lui	a5,0x3c126
4201122c:	89c78793          	addi	a5,a5,-1892 # 3c12589c <_esp_trace_encoder_array_end+0x577c>
42011230:	3c126737          	lui	a4,0x3c126
42011234:	8a470713          	addi	a4,a4,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
42011238:	3c126637          	lui	a2,0x3c126
4201123c:	86aa                	mv	a3,a0
4201123e:	85ba                	mv	a1,a4
42011240:	8822                	mv	a6,s0
42011242:	bfc60613          	addi	a2,a2,-1028 # 3c125bfc <_esp_trace_encoder_array_end+0x5adc>
42011246:	4509                	li	a0,2
42011248:	fe377097          	auipc	ra,0xfe377
4201124c:	06a080e7          	jalr	106(ra) # 403882b2 <esp_log>
42011250:	3fc957b7          	lui	a5,0x3fc95
42011254:	e747a503          	lw	a0,-396(a5) # 3fc94e74 <s_state>
42011258:	3c1267b7          	lui	a5,0x3c126
4201125c:	aa478693          	addi	a3,a5,-1372 # 3c125aa4 <_esp_trace_encoder_array_end+0x5984>
42011260:	85a6                	mv	a1,s1
42011262:	4601                	li	a2,0
42011264:	5bc040ef          	jal	42015820 <native_state_set_audio>
42011268:	8c26                	mv	s8,s1
4201126a:	4572                	lw	a0,28(sp)
4201126c:	c119                	beqz	a0,42011272 <decoder_task+0x92e>
4201126e:	01b280ef          	jal	42039a88 <esp_audio_simple_dec_close>
42011272:	ce02                	sw	zero,28(sp)
42011274:	00098563          	beqz	s3,4201127e <decoder_task+0x93a>
42011278:	854e                	mv	a0,s3
4201127a:	22f010ef          	jal	42012ca8 <native_aac_decoder_destroy>
4201127e:	854a                	mv	a0,s2
42011280:	ad0f70ef          	jal	42008550 <cfree>
42011284:	4981                	li	s3,0
42011286:	4a01                	li	s4,0
42011288:	4901                	li	s2,0
4201128a:	be3d                	j	42010dc8 <decoder_task+0x484>
4201128c:	854e                	mv	a0,s3
4201128e:	5df010ef          	jal	4201306c <native_aac_decoder_source_channels>
42011292:	01b14683          	lbu	a3,27(sp)
42011296:	0ff57513          	zext.b	a0,a0
4201129a:	bc09                	j	42010cac <decoder_task+0x368>
4201129c:	204747b7          	lui	a5,0x20474
420112a0:	74f78793          	addi	a5,a5,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
420112a4:	086c                	addi	a1,sp,28
420112a6:	10a8                	addi	a0,sp,104
420112a8:	d4be                	sw	a5,104(sp)
420112aa:	768150ef          	jal	42026a12 <__wrap_esp_audio_simple_dec_open>
420112ae:	842a                	mv	s0,a0
420112b0:	1c051963          	bnez	a0,42011482 <decoder_task+0xb3e>
420112b4:	4bf2                	lw	s7,28(sp)
420112b6:	4d81                	li	s11,0
420112b8:	8c0b81e3          	beqz	s7,42010b7a <decoder_task+0x236>
420112bc:	4981                	li	s3,0
420112be:	4b81                	li	s7,0
420112c0:	b8dd                	j	42010bb6 <decoder_task+0x272>
420112c2:	844a                	mv	s0,s2
420112c4:	b14d                	j	42010f66 <decoder_task+0x622>
420112c6:	3c1267b7          	lui	a5,0x3c126
420112ca:	bc878513          	addi	a0,a5,-1080 # 3c125bc8 <_esp_trace_encoder_array_end+0x5aa8>
420112ce:	896ff0ef          	jal	42010364 <log_runtime_memory>
420112d2:	bd11                	j	420110e6 <decoder_task+0x7a2>
420112d4:	d682                	sw	zero,108(sp)
420112d6:	d882                	sw	zero,112(sp)
420112d8:	da82                	sw	zero,116(sp)
420112da:	815ff06f          	j	42010aee <decoder_task+0x1aa>
420112de:	fe377097          	auipc	ra,0xfe377
420112e2:	0dc080e7          	jalr	220(ra) # 403883ba <esp_log_timestamp>
420112e6:	4791                	li	a5,4
420112e8:	4405                	li	s0,1
420112ea:	86aa                	mv	a3,a0
420112ec:	1efb0363          	beq	s6,a5,420114d2 <decoder_task+0xb8e>
420112f0:	3c1267b7          	lui	a5,0x3c126
420112f4:	89878793          	addi	a5,a5,-1896 # 3c125898 <_esp_trace_encoder_array_end+0x5778>
420112f8:	008b0663          	beq	s6,s0,42011304 <decoder_task+0x9c0>
420112fc:	3c1267b7          	lui	a5,0x3c126
42011300:	89c78793          	addi	a5,a5,-1892 # 3c12589c <_esp_trace_encoder_array_end+0x577c>
42011304:	3c126737          	lui	a4,0x3c126
42011308:	8a470713          	addi	a4,a4,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
4201130c:	3c126637          	lui	a2,0x3c126
42011310:	85ba                	mv	a1,a4
42011312:	b2c60613          	addi	a2,a2,-1236 # 3c125b2c <_esp_trace_encoder_array_end+0x5a0c>
42011316:	4505                	li	a0,1
42011318:	fe377097          	auipc	ra,0xfe377
4201131c:	f9a080e7          	jalr	-102(ra) # 403882b2 <esp_log>
42011320:	3fc957b7          	lui	a5,0x3fc95
42011324:	e747a503          	lw	a0,-396(a5) # 3fc94e74 <s_state>
42011328:	3c1267b7          	lui	a5,0x3c126
4201132c:	a8878693          	addi	a3,a5,-1400 # 3c125a88 <_esp_trace_encoder_array_end+0x5968>
42011330:	85a6                	mv	a1,s1
42011332:	4601                	li	a2,0
42011334:	4ec040ef          	jal	42015820 <native_state_set_audio>
42011338:	3fc957b7          	lui	a5,0x3fc95
4201133c:	e6c7a503          	lw	a0,-404(a5) # 3fc94e6c <s_encoded>
42011340:	85e6                	mv	a1,s9
42011342:	8c26                	mv	s8,s1
42011344:	2a6680ef          	jal	420795ea <vRingbufferReturnItem>
42011348:	4981                	li	s3,0
4201134a:	4d81                	li	s11,0
4201134c:	4b81                	li	s7,0
4201134e:	4401                	li	s0,0
42011350:	e64ff06f          	j	420109b4 <decoder_task+0x70>
42011354:	fe377097          	auipc	ra,0xfe377
42011358:	066080e7          	jalr	102(ra) # 403883ba <esp_log_timestamp>
4201135c:	4789                	li	a5,2
4201135e:	4405                	li	s0,1
42011360:	12fb0c63          	beq	s6,a5,42011498 <decoder_task+0xb54>
42011364:	4791                	li	a5,4
42011366:	1afb0d63          	beq	s6,a5,42011520 <decoder_task+0xbdc>
4201136a:	3c1267b7          	lui	a5,0x3c126
4201136e:	89878793          	addi	a5,a5,-1896 # 3c125898 <_esp_trace_encoder_array_end+0x5778>
42011372:	008b0663          	beq	s6,s0,4201137e <decoder_task+0xa3a>
42011376:	3c1267b7          	lui	a5,0x3c126
4201137a:	89c78793          	addi	a5,a5,-1892 # 3c12589c <_esp_trace_encoder_array_end+0x577c>
4201137e:	48e6                	lw	a7,88(sp)
42011380:	5806                	lw	a6,96(sp)
42011382:	3c126737          	lui	a4,0x3c126
42011386:	8a470713          	addi	a4,a4,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
4201138a:	3c126637          	lui	a2,0x3c126
4201138e:	86aa                	mv	a3,a0
42011390:	85ba                	mv	a1,a4
42011392:	c2060613          	addi	a2,a2,-992 # 3c125c20 <_esp_trace_encoder_array_end+0x5b00>
42011396:	4505                	li	a0,1
42011398:	fe377097          	auipc	ra,0xfe377
4201139c:	f1a080e7          	jalr	-230(ra) # 403882b2 <esp_log>
420113a0:	3fc957b7          	lui	a5,0x3fc95
420113a4:	e747a503          	lw	a0,-396(a5) # 3fc94e74 <s_state>
420113a8:	3c1267b7          	lui	a5,0x3c126
420113ac:	c5c78693          	addi	a3,a5,-932 # 3c125c5c <_esp_trace_encoder_array_end+0x5b3c>
420113b0:	85a6                	mv	a1,s1
420113b2:	4601                	li	a2,0
420113b4:	46c040ef          	jal	42015820 <native_state_set_audio>
420113b8:	8c26                	mv	s8,s1
420113ba:	bd45                	j	4201126a <decoder_task+0x926>
420113bc:	b60b8fe3          	beqz	s7,42010f3a <decoder_task+0x5f6>
420113c0:	bce1                	j	42010e98 <decoder_task+0x554>
420113c2:	fe377097          	auipc	ra,0xfe377
420113c6:	ff8080e7          	jalr	-8(ra) # 403883ba <esp_log_timestamp>
420113ca:	3c1267b7          	lui	a5,0x3c126
420113ce:	8a478713          	addi	a4,a5,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
420113d2:	3c1267b7          	lui	a5,0x3c126
420113d6:	86aa                	mv	a3,a0
420113d8:	85ba                	mv	a1,a4
420113da:	af878613          	addi	a2,a5,-1288 # 3c125af8 <_esp_trace_encoder_array_end+0x59d8>
420113de:	4505                	li	a0,1
420113e0:	fe377097          	auipc	ra,0xfe377
420113e4:	ed2080e7          	jalr	-302(ra) # 403882b2 <esp_log>
420113e8:	3fc957b7          	lui	a5,0x3fc95
420113ec:	e747a503          	lw	a0,-396(a5) # 3fc94e74 <s_state>
420113f0:	3c1267b7          	lui	a5,0x3c126
420113f4:	a8878693          	addi	a3,a5,-1400 # 3c125a88 <_esp_trace_encoder_array_end+0x5968>
420113f8:	85a6                	mv	a1,s1
420113fa:	4601                	li	a2,0
420113fc:	424040ef          	jal	42015820 <native_state_set_audio>
42011400:	8c26                	mv	s8,s1
42011402:	4981                	li	s3,0
42011404:	4901                	li	s2,0
42011406:	4a01                	li	s4,0
42011408:	4d81                	li	s11,0
4201140a:	855e                	mv	a0,s7
4201140c:	7d6240ef          	jal	42035be2 <custom_flac_decoder_destroy>
42011410:	4b81                	li	s7,0
42011412:	be15                	j	42010f46 <decoder_task+0x602>
42011414:	8542                	mv	a0,a6
42011416:	b0d5                	j	42010cfa <decoder_task+0x3b6>
42011418:	3c1267b7          	lui	a5,0x3c126
4201141c:	89c78793          	addi	a5,a5,-1892 # 3c12589c <_esp_trace_encoder_array_end+0x577c>
42011420:	f04ff06f          	j	42010b24 <decoder_task+0x1e0>
42011424:	01a14d83          	lbu	s11,26(sp)
42011428:	ae0d85e3          	beqz	s11,42010f12 <decoder_task+0x5ce>
4201142c:	3c1267b7          	lui	a5,0x3c126
42011430:	b8478513          	addi	a0,a5,-1148 # 3c125b84 <_esp_trace_encoder_array_end+0x5a64>
42011434:	f31fe0ef          	jal	42010364 <log_runtime_memory>
42011438:	bce1                	j	42010f10 <decoder_task+0x5cc>
4201143a:	3c1267b7          	lui	a5,0x3c126
4201143e:	89c78593          	addi	a1,a5,-1892 # 3c12589c <_esp_trace_encoder_array_end+0x577c>
42011442:	b919                	j	42011058 <decoder_task+0x714>
42011444:	fe377097          	auipc	ra,0xfe377
42011448:	f76080e7          	jalr	-138(ra) # 403883ba <esp_log_timestamp>
4201144c:	3c1267b7          	lui	a5,0x3c126
42011450:	8a478713          	addi	a4,a5,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
42011454:	3c126637          	lui	a2,0x3c126
42011458:	3c1267b7          	lui	a5,0x3c126
4201145c:	86aa                	mv	a3,a0
4201145e:	88878793          	addi	a5,a5,-1912 # 3c125888 <_esp_trace_encoder_array_end+0x5768>
42011462:	85ba                	mv	a1,a4
42011464:	b5c60613          	addi	a2,a2,-1188 # 3c125b5c <_esp_trace_encoder_array_end+0x5a3c>
42011468:	5879                	li	a6,-2
4201146a:	4505                	li	a0,1
4201146c:	fe377097          	auipc	ra,0xfe377
42011470:	e46080e7          	jalr	-442(ra) # 403882b2 <esp_log>
42011474:	3c1267b7          	lui	a5,0x3c126
42011478:	8922                	mv	s2,s0
4201147a:	a8878693          	addi	a3,a5,-1400 # 3c125a88 <_esp_trace_encoder_array_end+0x5968>
4201147e:	ed2ff06f          	j	42010b50 <decoder_task+0x20c>
42011482:	fe377097          	auipc	ra,0xfe377
42011486:	f38080e7          	jalr	-200(ra) # 403883ba <esp_log_timestamp>
4201148a:	3c1267b7          	lui	a5,0x3c126
4201148e:	86aa                	mv	a3,a0
42011490:	89478793          	addi	a5,a5,-1900 # 3c125894 <_esp_trace_encoder_array_end+0x5774>
42011494:	e90ff06f          	j	42010b24 <decoder_task+0x1e0>
42011498:	3c1267b7          	lui	a5,0x3c126
4201149c:	88878793          	addi	a5,a5,-1912 # 3c125888 <_esp_trace_encoder_array_end+0x5768>
420114a0:	bdf9                	j	4201137e <decoder_task+0xa3a>
420114a2:	3c1267b7          	lui	a5,0x3c126
420114a6:	89478593          	addi	a1,a5,-1900 # 3c125894 <_esp_trace_encoder_array_end+0x5774>
420114aa:	b67d                	j	42011058 <decoder_task+0x714>
420114ac:	3c1267b7          	lui	a5,0x3c126
420114b0:	88878593          	addi	a1,a5,-1912 # 3c125888 <_esp_trace_encoder_array_end+0x5768>
420114b4:	b655                	j	42011058 <decoder_task+0x714>
420114b6:	3fc957b7          	lui	a5,0x3fc95
420114ba:	e747a503          	lw	a0,-396(a5) # 3fc94e74 <s_state>
420114be:	3c1267b7          	lui	a5,0x3c126
420114c2:	be478693          	addi	a3,a5,-1052 # 3c125be4 <_esp_trace_encoder_array_end+0x5ac4>
420114c6:	4601                	li	a2,0
420114c8:	85a6                	mv	a1,s1
420114ca:	356040ef          	jal	42015820 <native_state_set_audio>
420114ce:	8c26                	mv	s8,s1
420114d0:	bb69                	j	4201126a <decoder_task+0x926>
420114d2:	3c1267b7          	lui	a5,0x3c126
420114d6:	89478793          	addi	a5,a5,-1900 # 3c125894 <_esp_trace_encoder_array_end+0x5774>
420114da:	b52d                	j	42011304 <decoder_task+0x9c0>
420114dc:	4c32                	lw	s8,12(sp)
420114de:	fe377097          	auipc	ra,0xfe377
420114e2:	edc080e7          	jalr	-292(ra) # 403883ba <esp_log_timestamp>
420114e6:	3c1267b7          	lui	a5,0x3c126
420114ea:	8a478713          	addi	a4,a5,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
420114ee:	3c1267b7          	lui	a5,0x3c126
420114f2:	86aa                	mv	a3,a0
420114f4:	85ba                	mv	a1,a4
420114f6:	c7078613          	addi	a2,a5,-912 # 3c125c70 <_esp_trace_encoder_array_end+0x5b50>
420114fa:	4509                	li	a0,2
420114fc:	fe377097          	auipc	ra,0xfe377
42011500:	db6080e7          	jalr	-586(ra) # 403882b2 <esp_log>
42011504:	4d85                	li	s11,1
42011506:	b85d                	j	42010dbc <decoder_task+0x478>
42011508:	8462                	mv	s0,s8
4201150a:	b9f5                	j	42011206 <decoder_task+0x8c2>
4201150c:	3c1267b7          	lui	a5,0x3c126
42011510:	88878793          	addi	a5,a5,-1912 # 3c125888 <_esp_trace_encoder_array_end+0x5768>
42011514:	bb31                	j	42011230 <decoder_task+0x8ec>
42011516:	3c1267b7          	lui	a5,0x3c126
4201151a:	89478793          	addi	a5,a5,-1900 # 3c125894 <_esp_trace_encoder_array_end+0x5774>
4201151e:	bb09                	j	42011230 <decoder_task+0x8ec>
42011520:	3c1267b7          	lui	a5,0x3c126
42011524:	89478793          	addi	a5,a5,-1900 # 3c125894 <_esp_trace_encoder_array_end+0x5774>
42011528:	bd99                	j	4201137e <decoder_task+0xa3a>
4201152a:	fe377097          	auipc	ra,0xfe377
4201152e:	e90080e7          	jalr	-368(ra) # 403883ba <esp_log_timestamp>
42011532:	4789                	li	a5,2
42011534:	4405                	li	s0,1
42011536:	86aa                	mv	a3,a0
42011538:	0afb0563          	beq	s6,a5,420115e2 <decoder_task+0xc9e>
4201153c:	4791                	li	a5,4
4201153e:	0afb0d63          	beq	s6,a5,420115f8 <decoder_task+0xcb4>
42011542:	3c1267b7          	lui	a5,0x3c126
42011546:	89878793          	addi	a5,a5,-1896 # 3c125898 <_esp_trace_encoder_array_end+0x5778>
4201154a:	008b0663          	beq	s6,s0,42011556 <decoder_task+0xc12>
4201154e:	3c1267b7          	lui	a5,0x3c126
42011552:	89c78793          	addi	a5,a5,-1892 # 3c12589c <_esp_trace_encoder_array_end+0x577c>
42011556:	3c126737          	lui	a4,0x3c126
4201155a:	8a470713          	addi	a4,a4,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
4201155e:	3c126637          	lui	a2,0x3c126
42011562:	85ba                	mv	a1,a4
42011564:	c9060613          	addi	a2,a2,-880 # 3c125c90 <_esp_trace_encoder_array_end+0x5b70>
42011568:	4505                	li	a0,1
4201156a:	fe377097          	auipc	ra,0xfe377
4201156e:	d48080e7          	jalr	-696(ra) # 403882b2 <esp_log>
42011572:	3fc957b7          	lui	a5,0x3fc95
42011576:	e747a503          	lw	a0,-396(a5) # 3fc94e74 <s_state>
4201157a:	3c1267b7          	lui	a5,0x3c126
4201157e:	cc078693          	addi	a3,a5,-832 # 3c125cc0 <_esp_trace_encoder_array_end+0x5ba0>
42011582:	85a6                	mv	a1,s1
42011584:	4601                	li	a2,0
42011586:	29a040ef          	jal	42015820 <native_state_set_audio>
4201158a:	8c26                	mv	s8,s1
4201158c:	b9f9                	j	4201126a <decoder_task+0x926>
4201158e:	fe377097          	auipc	ra,0xfe377
42011592:	e2c080e7          	jalr	-468(ra) # 403883ba <esp_log_timestamp>
42011596:	3c126737          	lui	a4,0x3c126
4201159a:	8a470713          	addi	a4,a4,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
4201159e:	3c126637          	lui	a2,0x3c126
420115a2:	86aa                	mv	a3,a0
420115a4:	87a2                	mv	a5,s0
420115a6:	85ba                	mv	a1,a4
420115a8:	b9c60613          	addi	a2,a2,-1124 # 3c125b9c <_esp_trace_encoder_array_end+0x5a7c>
420115ac:	4509                	li	a0,2
420115ae:	fe377097          	auipc	ra,0xfe377
420115b2:	d04080e7          	jalr	-764(ra) # 403882b2 <esp_log>
420115b6:	3c126737          	lui	a4,0x3c126
420115ba:	0419                	addi	s0,s0,6 # 3006 <CSR_UINTSTATUS+0x2355>
420115bc:	4785                	li	a5,1
420115be:	aa470693          	addi	a3,a4,-1372 # 3c125aa4 <_esp_trace_encoder_array_end+0x5984>
420115c2:	0087e663          	bltu	a5,s0,420115ce <decoder_task+0xc8a>
420115c6:	3c1267b7          	lui	a5,0x3c126
420115ca:	a8878693          	addi	a3,a5,-1400 # 3c125a88 <_esp_trace_encoder_array_end+0x5968>
420115ce:	3fc957b7          	lui	a5,0x3fc95
420115d2:	e747a503          	lw	a0,-396(a5) # 3fc94e74 <s_state>
420115d6:	4601                	li	a2,0
420115d8:	85a6                	mv	a1,s1
420115da:	246040ef          	jal	42015820 <native_state_set_audio>
420115de:	8c26                	mv	s8,s1
420115e0:	baa9                	j	42010f3a <decoder_task+0x5f6>
420115e2:	3c1267b7          	lui	a5,0x3c126
420115e6:	88878793          	addi	a5,a5,-1912 # 3c125888 <_esp_trace_encoder_array_end+0x5768>
420115ea:	b7b5                	j	42011556 <decoder_task+0xc12>
420115ec:	3c1267b7          	lui	a5,0x3c126
420115f0:	a8878693          	addi	a3,a5,-1400 # 3c125a88 <_esp_trace_encoder_array_end+0x5968>
420115f4:	d5cff06f          	j	42010b50 <decoder_task+0x20c>
420115f8:	3c1267b7          	lui	a5,0x3c126
420115fc:	89478793          	addi	a5,a5,-1900 # 3c125894 <_esp_trace_encoder_array_end+0x5774>
42011600:	bf99                	j	42011556 <decoder_task+0xc12>
42011602:	fe377097          	auipc	ra,0xfe377
42011606:	db8080e7          	jalr	-584(ra) # 403883ba <esp_log_timestamp>
4201160a:	3c1267b7          	lui	a5,0x3c126
4201160e:	86aa                	mv	a3,a0
42011610:	88878793          	addi	a5,a5,-1912 # 3c125888 <_esp_trace_encoder_array_end+0x5768>
42011614:	b9c5                	j	42011304 <decoder_task+0x9c0>
