
idf\esp32c3-oled-native\build-rx-owner\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420109a2 <decoder_task>:
420109a2:	7151                	addi	sp,sp,-240
420109a4:	d5a2                	sw	s0,232(sp)
420109a6:	d3a6                	sw	s1,228(sp)
420109a8:	d1ca                	sw	s2,224(sp)
420109aa:	cfce                	sw	s3,220(sp)
420109ac:	cdd2                	sw	s4,216(sp)
420109ae:	cbd6                	sw	s5,212(sp)
420109b0:	c9da                	sw	s6,208(sp)
420109b2:	c7de                	sw	s7,204(sp)
420109b4:	c5e2                	sw	s8,200(sp)
420109b6:	df6e                	sw	s11,188(sp)
420109b8:	d786                	sw	ra,236(sp)
420109ba:	c3e6                	sw	s9,196(sp)
420109bc:	c1ea                	sw	s10,192(sp)
420109be:	619010ef          	jal	420127d6 <decoder_register_codecs>
420109c2:	3fc95737          	lui	a4,0x3fc95
420109c6:	000f47b7          	lui	a5,0xf4
420109ca:	cd870713          	addi	a4,a4,-808 # 3fc94cd8 <s_bitrate_updated_us>
420109ce:	24078793          	addi	a5,a5,576 # f4240 <CSR_UINTSTATUS+0xf358f>
420109d2:	ce02                	sw	zero,28(sp)
420109d4:	c102                	sw	zero,128(sp)
420109d6:	c302                	sw	zero,132(sp)
420109d8:	c502                	sw	zero,136(sp)
420109da:	c702                	sw	zero,140(sp)
420109dc:	c902                	sw	zero,144(sp)
420109de:	cb02                	sw	zero,148(sp)
420109e0:	cd02                	sw	zero,152(sp)
420109e2:	cf02                	sw	zero,156(sp)
420109e4:	d102                	sw	zero,160(sp)
420109e6:	d302                	sw	zero,164(sp)
420109e8:	d502                	sw	zero,168(sp)
420109ea:	d702                	sw	zero,172(sp)
420109ec:	d202                	sw	zero,36(sp)
420109ee:	d402                	sw	zero,40(sp)
420109f0:	d602                	sw	zero,44(sp)
420109f2:	d802                	sw	zero,48(sp)
420109f4:	00010d23          	sb	zero,26(sp)
420109f8:	842a                	mv	s0,a0
420109fa:	c23a                	sw	a4,4(sp)
420109fc:	c43e                	sw	a5,8(sp)
420109fe:	4981                	li	s3,0
42010a00:	4a01                	li	s4,0
42010a02:	4901                	li	s2,0
42010a04:	4d81                	li	s11,0
42010a06:	4b01                	li	s6,0
42010a08:	4c01                	li	s8,0
42010a0a:	4481                	li	s1,0
42010a0c:	4b81                	li	s7,0
42010a0e:	3fc95ab7          	lui	s5,0x3fc95
42010a12:	68f150ef          	jal	420268a0 <rx_buffer_diagnostic_poll>
42010a16:	cf0a8793          	addi	a5,s5,-784 # 3fc94cf0 <s_generation>
42010a1a:	0330000f          	fence	rw,rw
42010a1e:	0007ac83          	lw	s9,0(a5)
42010a22:	0230000f          	fence	r,rw
42010a26:	429c8163          	beq	s9,s1,42010e48 <decoder_task+0x4a6>
42010a2a:	3fc957b7          	lui	a5,0x3fc95
42010a2e:	cec78793          	addi	a5,a5,-788 # 3fc94cec <s_decoder_target_codec>
42010a32:	0330000f          	fence	rw,rw
42010a36:	4384                	lw	s1,0(a5)
42010a38:	0230000f          	fence	r,rw
42010a3c:	4572                	lw	a0,28(sp)
42010a3e:	c119                	beqz	a0,42010a44 <decoder_task+0xa2>
42010a40:	19d280ef          	jal	420393dc <esp_audio_simple_dec_close>
42010a44:	854e                	mv	a0,s3
42010a46:	ce02                	sw	zero,28(sp)
42010a48:	5f1010ef          	jal	42012838 <native_aac_decoder_destroy>
42010a4c:	000b8563          	beqz	s7,42010a56 <decoder_task+0xb4>
42010a50:	855e                	mv	a0,s7
42010a52:	2e5240ef          	jal	42035536 <custom_flac_decoder_destroy>
42010a56:	46048e63          	beqz	s1,42010ed2 <decoder_task+0x530>
42010a5a:	d202                	sw	zero,36(sp)
42010a5c:	d402                	sw	zero,40(sp)
42010a5e:	d602                	sw	zero,44(sp)
42010a60:	d802                	sw	zero,48(sp)
42010a62:	00010d23          	sb	zero,26(sp)
42010a66:	3fc957b7          	lui	a5,0x3fc95
42010a6a:	ce878793          	addi	a5,a5,-792 # 3fc94ce8 <s_decoder_released_generation>
42010a6e:	0310000f          	fence	rw,w
42010a72:	0197a023          	sw	s9,0(a5)
42010a76:	0330000f          	fence	rw,rw
42010a7a:	4b81                	li	s7,0
42010a7c:	84e6                	mv	s1,s9
42010a7e:	4c01                	li	s8,0
42010a80:	4b01                	li	s6,0
42010a82:	4d81                	li	s11,0
42010a84:	4981                	li	s3,0
42010a86:	3fc957b7          	lui	a5,0x3fc95
42010a8a:	cfc7a503          	lw	a0,-772(a5) # 3fc94cfc <s_encoded>
42010a8e:	4651                	li	a2,20
42010a90:	100c                	addi	a1,sp,32
42010a92:	d002                	sw	zero,32(sp)
42010a94:	42e680ef          	jal	42078ec2 <xRingbufferReceive>
42010a98:	8caa                	mv	s9,a0
42010a9a:	dd25                	beqz	a0,42010a12 <decoder_task+0x70>
42010a9c:	4118                	lw	a4,0(a0)
42010a9e:	cf0a8793          	addi	a5,s5,-784
42010aa2:	0330000f          	fence	rw,rw
42010aa6:	439c                	lw	a5,0(a5)
42010aa8:	0230000f          	fence	r,rw
42010aac:	40f71b63          	bne	a4,a5,42010ec2 <decoder_task+0x520>
42010ab0:	411c                	lw	a5,0(a0)
42010ab2:	41878863          	beq	a5,s8,42010ec2 <decoder_task+0x520>
42010ab6:	4158                	lw	a4,4(a0)
42010ab8:	e709                	bnez	a4,42010ac2 <decoder_task+0x120>
42010aba:	00a54703          	lbu	a4,10(a0)
42010abe:	3e071e63          	bnez	a4,42010eba <decoder_task+0x518>
42010ac2:	12041563          	bnez	s0,42010bec <decoder_task+0x24a>
42010ac6:	12f48c63          	beq	s1,a5,42010bfe <decoder_task+0x25c>
42010aca:	4572                	lw	a0,28(sp)
42010acc:	c119                	beqz	a0,42010ad2 <decoder_task+0x130>
42010ace:	10f280ef          	jal	420393dc <esp_audio_simple_dec_close>
42010ad2:	854e                	mv	a0,s3
42010ad4:	ce02                	sw	zero,28(sp)
42010ad6:	563010ef          	jal	42012838 <native_aac_decoder_destroy>
42010ada:	000b8563          	beqz	s7,42010ae4 <decoder_task+0x142>
42010ade:	855e                	mv	a0,s7
42010ae0:	257240ef          	jal	42035536 <custom_flac_decoder_destroy>
42010ae4:	4712                	lw	a4,4(sp)
42010ae6:	000ca483          	lw	s1,0(s9)
42010aea:	004cab03          	lw	s6,4(s9)
42010aee:	3fc957b7          	lui	a5,0x3fc95
42010af2:	ce07a023          	sw	zero,-800(a5) # 3fc94ce0 <s_published_bitrate_bps>
42010af6:	4801                	li	a6,0
42010af8:	4781                	li	a5,0
42010afa:	c31c                	sw	a5,0(a4)
42010afc:	00010d23          	sb	zero,26(sp)
42010b00:	01072223          	sw	a6,4(a4)
42010b04:	fe371097          	auipc	ra,0xfe371
42010b08:	836080e7          	jalr	-1994(ra) # 4038133a <esp_timer_get_time>
42010b0c:	c52a                	sw	a0,136(sp)
42010b0e:	c902                	sw	zero,144(sp)
42010b10:	cb02                	sw	zero,148(sp)
42010b12:	cd02                	sw	zero,152(sp)
42010b14:	cf02                	sw	zero,156(sp)
42010b16:	d102                	sw	zero,160(sp)
42010b18:	d302                	sw	zero,164(sp)
42010b1a:	d502                	sw	zero,168(sp)
42010b1c:	d702                	sw	zero,172(sp)
42010b1e:	c126                	sw	s1,128(sp)
42010b20:	c35a                	sw	s6,132(sp)
42010b22:	c72e                	sw	a1,140(sp)
42010b24:	478d                	li	a5,3
42010b26:	3afb0c63          	beq	s6,a5,42010ede <decoder_task+0x53c>
42010b2a:	4789                	li	a5,2
42010b2c:	48fb0363          	beq	s6,a5,42010fb2 <decoder_task+0x610>
42010b30:	640d                	lui	s0,0x3
42010b32:	008a70e3          	bgeu	s4,s0,42011332 <decoder_task+0x990>
42010b36:	85a2                	mv	a1,s0
42010b38:	854a                	mv	a0,s2
42010b3a:	b15f70ef          	jal	4200864e <realloc>
42010b3e:	7e050f63          	beqz	a0,4201133c <decoder_task+0x99a>
42010b42:	d682                	sw	zero,108(sp)
42010b44:	d882                	sw	zero,112(sp)
42010b46:	da82                	sw	zero,116(sp)
42010b48:	892a                	mv	s2,a0
42010b4a:	8a22                	mv	s4,s0
42010b4c:	4791                	li	a5,4
42010b4e:	7afb0663          	beq	s6,a5,420112fa <decoder_task+0x958>
42010b52:	203357b7          	lui	a5,0x20335
42010b56:	04d78793          	addi	a5,a5,77 # 2033504d <CSR_UINTSTATUS+0x2033439c>
42010b5a:	086c                	addi	a1,sp,28
42010b5c:	10a8                	addi	a0,sp,104
42010b5e:	d4be                	sw	a5,104(sp)
42010b60:	029150ef          	jal	42026388 <__wrap_esp_audio_simple_dec_open>
42010b64:	842a                	mv	s0,a0
42010b66:	7a050663          	beqz	a0,42011312 <decoder_task+0x970>
42010b6a:	fe378097          	auipc	ra,0xfe378
42010b6e:	850080e7          	jalr	-1968(ra) # 403883ba <esp_log_timestamp>
42010b72:	3c1267b7          	lui	a5,0x3c126
42010b76:	4985                	li	s3,1
42010b78:	86aa                	mv	a3,a0
42010b7a:	89878793          	addi	a5,a5,-1896 # 3c125898 <_esp_trace_encoder_array_end+0x5778>
42010b7e:	0f3b1ce3          	bne	s6,s3,42011476 <decoder_task+0xad4>
42010b82:	3c126737          	lui	a4,0x3c126
42010b86:	8a470713          	addi	a4,a4,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
42010b8a:	3c126637          	lui	a2,0x3c126
42010b8e:	85ba                	mv	a1,a4
42010b90:	8822                	mv	a6,s0
42010b92:	b5c60613          	addi	a2,a2,-1188 # 3c125b5c <_esp_trace_encoder_array_end+0x5a3c>
42010b96:	4505                	li	a0,1
42010b98:	fe377097          	auipc	ra,0xfe377
42010b9c:	71a080e7          	jalr	1818(ra) # 403882b2 <esp_log>
42010ba0:	3c126737          	lui	a4,0x3c126
42010ba4:	57f9                	li	a5,-2
42010ba6:	a9470693          	addi	a3,a4,-1388 # 3c125a94 <_esp_trace_encoder_array_end+0x5974>
42010baa:	2af400e3          	beq	s0,a5,4201164a <decoder_task+0xca8>
42010bae:	3fc957b7          	lui	a5,0x3fc95
42010bb2:	d047a503          	lw	a0,-764(a5) # 3fc94d04 <s_state>
42010bb6:	4601                	li	a2,0
42010bb8:	85a6                	mv	a1,s1
42010bba:	7f2040ef          	jal	420153ac <native_state_set_audio>
42010bbe:	4572                	lw	a0,28(sp)
42010bc0:	c501                	beqz	a0,42010bc8 <decoder_task+0x226>
42010bc2:	01b280ef          	jal	420393dc <esp_audio_simple_dec_close>
42010bc6:	ce02                	sw	zero,28(sp)
42010bc8:	854a                	mv	a0,s2
42010bca:	a89f70ef          	jal	42008652 <cfree>
42010bce:	8c26                	mv	s8,s1
42010bd0:	4a01                	li	s4,0
42010bd2:	4901                	li	s2,0
42010bd4:	4b81                	li	s7,0
42010bd6:	4d81                	li	s11,0
42010bd8:	3fc957b7          	lui	a5,0x3fc95
42010bdc:	cfc7a503          	lw	a0,-772(a5) # 3fc94cfc <s_encoded>
42010be0:	85e6                	mv	a1,s9
42010be2:	4981                	li	s3,0
42010be4:	35a680ef          	jal	42078f3e <vRingbufferReturnItem>
42010be8:	4401                	li	s0,0
42010bea:	b525                	j	42010a12 <decoder_task+0x70>
42010bec:	3eb010ef          	jal	420127d6 <decoder_register_codecs>
42010bf0:	842a                	mv	s0,a0
42010bf2:	28051063          	bnez	a0,42010e72 <decoder_task+0x4d0>
42010bf6:	000ca783          	lw	a5,0(s9)
42010bfa:	ecf498e3          	bne	s1,a5,42010aca <decoder_task+0x128>
42010bfe:	004ca783          	lw	a5,4(s9)
42010c02:	ed6794e3          	bne	a5,s6,42010aca <decoder_task+0x128>
42010c06:	478d                	li	a5,3
42010c08:	00fb09e3          	beq	s6,a5,4201141a <decoder_task+0xa78>
42010c0c:	47f2                	lw	a5,28(sp)
42010c0e:	00f9e7b3          	or	a5,s3,a5
42010c12:	d3f9                	beqz	a5,42010bd8 <decoder_task+0x236>
42010c14:	008cd783          	lhu	a5,8(s9)
42010c18:	00bc8713          	addi	a4,s9,11
42010c1c:	ce82                	sw	zero,92(sp)
42010c1e:	d082                	sw	zero,96(sp)
42010c20:	d282                	sw	zero,100(sp)
42010c22:	ccbe                	sw	a5,88(sp)
42010c24:	caba                	sw	a4,84(sp)
42010c26:	00acc703          	lbu	a4,10(s9)
42010c2a:	ffeb0693          	addi	a3,s6,-2
42010c2e:	0016b693          	seqz	a3,a3
42010c32:	00e03733          	snez	a4,a4
42010c36:	c036                	sw	a3,0(sp)
42010c38:	04e10e23          	sb	a4,92(sp)
42010c3c:	3a098663          	beqz	s3,42010fe8 <decoder_task+0x646>
42010c40:	e789                	bnez	a5,42010c4a <decoder_task+0x2a8>
42010c42:	05c14783          	lbu	a5,92(sp)
42010c46:	1c078a63          	beqz	a5,42010e1a <decoder_task+0x478>
42010c4a:	4781                	li	a5,0
42010c4c:	4801                	li	a6,0
42010c4e:	de3e                	sw	a5,60(sp)
42010c50:	c0c2                	sw	a6,64(sp)
42010c52:	da4a                	sw	s2,52(sp)
42010c54:	dc52                	sw	s4,56(sp)
42010c56:	d082                	sw	zero,96(sp)
42010c58:	fe370097          	auipc	ra,0xfe370
42010c5c:	6e2080e7          	jalr	1762(ra) # 4038133a <esp_timer_get_time>
42010c60:	842a                	mv	s0,a0
42010c62:	1850                	addi	a2,sp,52
42010c64:	08cc                	addi	a1,sp,84
42010c66:	854e                	mv	a0,s3
42010c68:	407010ef          	jal	4201286e <native_aac_decoder_process>
42010c6c:	8d2a                	mv	s10,a0
42010c6e:	fe370097          	auipc	ra,0xfe370
42010c72:	6cc080e7          	jalr	1740(ra) # 4038133a <esp_timer_get_time>
42010c76:	47ca                	lw	a5,144(sp)
42010c78:	46da                	lw	a3,148(sp)
42010c7a:	8d01                	sub	a0,a0,s0
42010c7c:	00a78733          	add	a4,a5,a0
42010c80:	00f737b3          	sltu	a5,a4,a5
42010c84:	97b6                	add	a5,a5,a3
42010c86:	cb3e                	sw	a5,148(sp)
42010c88:	578a                	lw	a5,160(sp)
42010c8a:	c93a                	sw	a4,144(sp)
42010c8c:	571a                	lw	a4,164(sp)
42010c8e:	0785                	addi	a5,a5,1
42010c90:	d13e                	sw	a5,160(sp)
42010c92:	00a77363          	bgeu	a4,a0,42010c98 <decoder_task+0x2f6>
42010c96:	d32a                	sw	a0,164(sp)
42010c98:	8bfd                	andi	a5,a5,31
42010c9a:	56078963          	beqz	a5,4201120c <decoder_task+0x86a>
42010c9e:	cf0a8793          	addi	a5,s5,-784
42010ca2:	0330000f          	fence	rw,rw
42010ca6:	439c                	lw	a5,0(a5)
42010ca8:	0230000f          	fence	r,rw
42010cac:	16979763          	bne	a5,s1,42010e1a <decoder_task+0x478>
42010cb0:	57e1                	li	a5,-8
42010cb2:	52fd0763          	beq	s10,a5,420111e0 <decoder_task+0x83e>
42010cb6:	5a0d1663          	bnez	s10,42011262 <decoder_task+0x8c0>
42010cba:	5786                	lw	a5,96(sp)
42010cbc:	4766                	lw	a4,88(sp)
42010cbe:	6ef76a63          	bltu	a4,a5,420113b2 <decoder_task+0xa10>
42010cc2:	8f1d                	sub	a4,a4,a5
42010cc4:	56aa                	lw	a3,168(sp)
42010cc6:	ccba                	sw	a4,88(sp)
42010cc8:	4756                	lw	a4,84(sp)
42010cca:	96be                	add	a3,a3,a5
42010ccc:	d536                	sw	a3,168(sp)
42010cce:	97ba                	add	a5,a5,a4
42010cd0:	4706                	lw	a4,64(sp)
42010cd2:	cabe                	sw	a5,84(sp)
42010cd4:	10070c63          	beqz	a4,42010dec <decoder_task+0x44a>
42010cd8:	00cc                	addi	a1,sp,68
42010cda:	854e                	mv	a0,s3
42010cdc:	c282                	sw	zero,68(sp)
42010cde:	c482                	sw	zero,72(sp)
42010ce0:	c682                	sw	zero,76(sp)
42010ce2:	c882                	sw	zero,80(sp)
42010ce4:	6b3010ef          	jal	42012b96 <native_aac_decoder_get_info>
42010ce8:	52051863          	bnez	a0,42011218 <decoder_task+0x876>
42010cec:	4782                	lw	a5,0(sp)
42010cee:	01b10613          	addi	a2,sp,27
42010cf2:	00cc                	addi	a1,sp,68
42010cf4:	854e                	mv	a0,s3
42010cf6:	00f10da3          	sb	a5,27(sp)
42010cfa:	6ab010ef          	jal	42012ba4 <native_aac_decoder_label>
42010cfe:	01b14683          	lbu	a3,27(sp)
42010d02:	842a                	mv	s0,a0
42010d04:	4501                	li	a0,0
42010d06:	5e068263          	beqz	a3,420112ea <decoder_task+0x948>
42010d0a:	cf0a8793          	addi	a5,s5,-784
42010d0e:	0330000f          	fence	rw,rw
42010d12:	4398                	lw	a4,0(a5)
42010d14:	0230000f          	fence	r,rw
42010d18:	4781                	li	a5,0
42010d1a:	06971163          	bne	a4,s1,42010d7c <decoder_task+0x3da>
42010d1e:	4716                	lw	a4,68(sp)
42010d20:	cf31                	beqz	a4,42010d7c <decoder_task+0x3da>
42010d22:	04914803          	lbu	a6,73(sp)
42010d26:	04080b63          	beqz	a6,42010d7c <decoder_task+0x3da>
42010d2a:	04814603          	lbu	a2,72(sp)
42010d2e:	c639                	beqz	a2,42010d7c <decoder_task+0x3da>
42010d30:	45a6                	lw	a1,72(sp)
42010d32:	47b6                	lw	a5,76(sp)
42010d34:	d23a                	sw	a4,36(sp)
42010d36:	d42e                	sw	a1,40(sp)
42010d38:	45c6                	lw	a1,80(sp)
42010d3a:	d63e                	sw	a5,44(sp)
42010d3c:	4785                	li	a5,1
42010d3e:	06012923          	sw	zero,114(sp)
42010d42:	06012b23          	sw	zero,118(sp)
42010d46:	06011d23          	sh	zero,122(sp)
42010d4a:	d4a2                	sw	s0,104(sp)
42010d4c:	d6ba                	sw	a4,108(sp)
42010d4e:	d82e                	sw	a1,48(sp)
42010d50:	00f10d23          	sb	a5,26(sp)
42010d54:	70050f63          	beqz	a0,42011472 <decoder_task+0xad0>
42010d58:	3fc957b7          	lui	a5,0x3fc95
42010d5c:	06a10823          	sb	a0,112(sp)
42010d60:	d047a503          	lw	a0,-764(a5) # 3fc94d04 <s_state>
42010d64:	06c108a3          	sb	a2,113(sp)
42010d68:	85a6                	mv	a1,s1
42010d6a:	10b0                	addi	a2,sp,104
42010d6c:	daba                	sw	a4,116(sp)
42010d6e:	07010c23          	sb	a6,120(sp)
42010d72:	06d10d23          	sb	a3,122(sp)
42010d76:	716040ef          	jal	4201548c <native_state_set_stream_info>
42010d7a:	4785                	li	a5,1
42010d7c:	45b6                	lw	a1,76(sp)
42010d7e:	8526                	mv	a0,s1
42010d80:	00f10d23          	sb	a5,26(sp)
42010d84:	ea2ff0ef          	jal	42010426 <state_set_decoder_bitrate>
42010d88:	01a14783          	lbu	a5,26(sp)
42010d8c:	c3a5                	beqz	a5,42010dec <decoder_task+0x44a>
42010d8e:	4c0d8363          	beqz	s11,42011254 <decoder_task+0x8b2>
42010d92:	02814503          	lbu	a0,40(sp)
42010d96:	02914783          	lbu	a5,41(sp)
42010d9a:	4406                	lw	s0,64(sp)
42010d9c:	051d                	addi	a0,a0,7
42010d9e:	810d                	srli	a0,a0,0x3
42010da0:	02f50533          	mul	a0,a0,a5
42010da4:	c91d                	beqz	a0,42010dda <decoder_task+0x438>
42010da6:	5612                	lw	a2,36(sp)
42010da8:	ca0d                	beqz	a2,42010dda <decoder_task+0x438>
42010daa:	02a45533          	divu	a0,s0,a0
42010dae:	47a2                	lw	a5,8(sp)
42010db0:	4681                	li	a3,0
42010db2:	02f535b3          	mulhu	a1,a0,a5
42010db6:	02f50533          	mul	a0,a0,a5
42010dba:	fdff0097          	auipc	ra,0xfdff0
42010dbe:	af2080e7          	jalr	-1294(ra) # 400008ac <__udivdi3>
42010dc2:	47ea                	lw	a5,152(sp)
42010dc4:	46fa                	lw	a3,156(sp)
42010dc6:	573a                	lw	a4,172(sp)
42010dc8:	953e                	add	a0,a0,a5
42010dca:	96ae                	add	a3,a3,a1
42010dcc:	00f537b3          	sltu	a5,a0,a5
42010dd0:	97b6                	add	a5,a5,a3
42010dd2:	9722                	add	a4,a4,s0
42010dd4:	cf3e                	sw	a5,156(sp)
42010dd6:	cd2a                	sw	a0,152(sp)
42010dd8:	d73a                	sw	a4,172(sp)
42010dda:	86a2                	mv	a3,s0
42010ddc:	864a                	mv	a2,s2
42010dde:	104c                	addi	a1,sp,36
42010de0:	8526                	mv	a0,s1
42010de2:	a85ff0ef          	jal	42010866 <send_pcm.isra.0>
42010de6:	8daa                	mv	s11,a0
42010de8:	74050a63          	beqz	a0,4201153c <decoder_task+0xb9a>
42010dec:	fe370097          	auipc	ra,0xfe370
42010df0:	54e080e7          	jalr	1358(ra) # 4038133a <esp_timer_get_time>
42010df4:	862e                	mv	a2,a1
42010df6:	85aa                	mv	a1,a0
42010df8:	0108                	addi	a0,sp,128
42010dfa:	9aeff0ef          	jal	4200ffa8 <decode_stats_report>
42010dfe:	4706                	lw	a4,64(sp)
42010e00:	5786                	lw	a5,96(sp)
42010e02:	05c14683          	lbu	a3,92(sp)
42010e06:	8fd9                	or	a5,a5,a4
42010e08:	3c079663          	bnez	a5,420111d4 <decoder_task+0x832>
42010e0c:	76068e63          	beqz	a3,42011588 <decoder_task+0xbe6>
42010e10:	4701                	li	a4,0
42010e12:	47e6                	lw	a5,88(sp)
42010e14:	8f5d                	or	a4,a4,a5
42010e16:	e20715e3          	bnez	a4,42010c40 <decoder_task+0x29e>
42010e1a:	00acc783          	lbu	a5,10(s9)
42010e1e:	4a079563          	bnez	a5,420112c8 <decoder_task+0x926>
42010e22:	4a9c0363          	beq	s8,s1,420112c8 <decoder_task+0x926>
42010e26:	8566                	mv	a0,s9
42010e28:	85e2                	mv	a1,s8
42010e2a:	975ff0ef          	jal	4201079e <return_decoded_packet>
42010e2e:	4401                	li	s0,0
42010e30:	271150ef          	jal	420268a0 <rx_buffer_diagnostic_poll>
42010e34:	cf0a8793          	addi	a5,s5,-784
42010e38:	0330000f          	fence	rw,rw
42010e3c:	0007ac83          	lw	s9,0(a5)
42010e40:	0230000f          	fence	r,rw
42010e44:	be9c93e3          	bne	s9,s1,42010a2a <decoder_task+0x88>
42010e48:	c20c0fe3          	beqz	s8,42010a86 <decoder_task+0xe4>
42010e4c:	c29c1de3          	bne	s8,s1,42010a86 <decoder_task+0xe4>
42010e50:	4572                	lw	a0,28(sp)
42010e52:	c119                	beqz	a0,42010e58 <decoder_task+0x4b6>
42010e54:	588280ef          	jal	420393dc <esp_audio_simple_dec_close>
42010e58:	ce02                	sw	zero,28(sp)
42010e5a:	00098563          	beqz	s3,42010e64 <decoder_task+0x4c2>
42010e5e:	854e                	mv	a0,s3
42010e60:	1d9010ef          	jal	42012838 <native_aac_decoder_destroy>
42010e64:	854a                	mv	a0,s2
42010e66:	fecf70ef          	jal	42008652 <cfree>
42010e6a:	4981                	li	s3,0
42010e6c:	4a01                	li	s4,0
42010e6e:	4901                	li	s2,0
42010e70:	b919                	j	42010a86 <decoder_task+0xe4>
42010e72:	fe377097          	auipc	ra,0xfe377
42010e76:	548080e7          	jalr	1352(ra) # 403883ba <esp_log_timestamp>
42010e7a:	3c126737          	lui	a4,0x3c126
42010e7e:	8a470713          	addi	a4,a4,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
42010e82:	3c126637          	lui	a2,0x3c126
42010e86:	86aa                	mv	a3,a0
42010e88:	85ba                	mv	a1,a4
42010e8a:	87a2                	mv	a5,s0
42010e8c:	ab460613          	addi	a2,a2,-1356 # 3c125ab4 <_esp_trace_encoder_array_end+0x5994>
42010e90:	4505                	li	a0,1
42010e92:	fe377097          	auipc	ra,0xfe377
42010e96:	420080e7          	jalr	1056(ra) # 403882b2 <esp_log>
42010e9a:	3fc957b7          	lui	a5,0x3fc95
42010e9e:	d047a503          	lw	a0,-764(a5) # 3fc94d04 <s_state>
42010ea2:	000ca583          	lw	a1,0(s9)
42010ea6:	3c1267b7          	lui	a5,0x3c126
42010eaa:	ae478693          	addi	a3,a5,-1308 # 3c125ae4 <_esp_trace_encoder_array_end+0x59c4>
42010eae:	4601                	li	a2,0
42010eb0:	4fc040ef          	jal	420153ac <native_state_set_audio>
42010eb4:	000cac03          	lw	s8,0(s9)
42010eb8:	8566                	mv	a0,s9
42010eba:	85e2                	mv	a1,s8
42010ebc:	8e3ff0ef          	jal	4201079e <return_decoded_packet>
42010ec0:	be89                	j	42010a12 <decoder_task+0x70>
42010ec2:	3fc957b7          	lui	a5,0x3fc95
42010ec6:	cfc7a503          	lw	a0,-772(a5) # 3fc94cfc <s_encoded>
42010eca:	85e6                	mv	a1,s9
42010ecc:	072680ef          	jal	42078f3e <vRingbufferReturnItem>
42010ed0:	b689                	j	42010a12 <decoder_task+0x70>
42010ed2:	854a                	mv	a0,s2
42010ed4:	f7ef70ef          	jal	42008652 <cfree>
42010ed8:	4a01                	li	s4,0
42010eda:	4901                	li	s2,0
42010edc:	bebd                	j	42010a5a <decoder_task+0xb8>
42010ede:	854a                	mv	a0,s2
42010ee0:	f72f70ef          	jal	42008652 <cfree>
42010ee4:	5f2240ef          	jal	420354d6 <custom_flac_decoder_create>
42010ee8:	8baa                	mv	s7,a0
42010eea:	52050b63          	beqz	a0,42011420 <decoder_task+0xa7e>
42010eee:	4981                	li	s3,0
42010ef0:	4a01                	li	s4,0
42010ef2:	4901                	li	s2,0
42010ef4:	4d81                	li	s11,0
42010ef6:	4661                	li	a2,24
42010ef8:	4581                	li	a1,0
42010efa:	10a8                	addi	a0,sp,104
42010efc:	fdfef097          	auipc	ra,0xfdfef
42010f00:	458080e7          	jalr	1112(ra) # 40000354 <memset>
42010f04:	011c                	addi	a5,sp,128
42010f06:	ccbe                	sw	a5,88(sp)
42010f08:	105c                	addi	a5,sp,36
42010f0a:	cebe                	sw	a5,92(sp)
42010f0c:	01a10793          	addi	a5,sp,26
42010f10:	d0be                	sw	a5,96(sp)
42010f12:	caa6                	sw	s1,84(sp)
42010f14:	00acc683          	lbu	a3,10(s9)
42010f18:	008cd603          	lhu	a2,8(s9)
42010f1c:	42011737          	lui	a4,0x42011
42010f20:	00d036b3          	snez	a3,a3
42010f24:	08dc                	addi	a5,sp,84
42010f26:	67470713          	addi	a4,a4,1652 # 42011674 <custom_flac_output>
42010f2a:	00bc8593          	addi	a1,s9,11
42010f2e:	06810813          	addi	a6,sp,104
42010f32:	855e                	mv	a0,s7
42010f34:	628240ef          	jal	4203555c <custom_flac_decoder_feed>
42010f38:	47ca                	lw	a5,144(sp)
42010f3a:	5726                	lw	a4,104(sp)
42010f3c:	465a                	lw	a2,148(sp)
42010f3e:	55b6                	lw	a1,108(sp)
42010f40:	568a                	lw	a3,160(sp)
42010f42:	973e                	add	a4,a4,a5
42010f44:	842a                	mv	s0,a0
42010f46:	5546                	lw	a0,112(sp)
42010f48:	962e                	add	a2,a2,a1
42010f4a:	00f737b3          	sltu	a5,a4,a5
42010f4e:	97b2                	add	a5,a5,a2
42010f50:	55d6                	lw	a1,116(sp)
42010f52:	561a                	lw	a2,164(sp)
42010f54:	96aa                	add	a3,a3,a0
42010f56:	c93a                	sw	a4,144(sp)
42010f58:	cb3e                	sw	a5,148(sp)
42010f5a:	d136                	sw	a3,160(sp)
42010f5c:	00b67363          	bgeu	a2,a1,42010f62 <decoder_task+0x5c0>
42010f60:	d32e                	sw	a1,164(sp)
42010f62:	57aa                	lw	a5,168(sp)
42010f64:	5766                	lw	a4,120(sp)
42010f66:	97ba                	add	a5,a5,a4
42010f68:	d53e                	sw	a5,168(sp)
42010f6a:	500d8c63          	beqz	s11,42011482 <decoder_task+0xae0>
42010f6e:	4d85                	li	s11,1
42010f70:	fe370097          	auipc	ra,0xfe370
42010f74:	3ca080e7          	jalr	970(ra) # 4038133a <esp_timer_get_time>
42010f78:	862e                	mv	a2,a1
42010f7a:	85aa                	mv	a1,a0
42010f7c:	0108                	addi	a0,sp,128
42010f7e:	82aff0ef          	jal	4200ffa8 <decode_stats_report>
42010f82:	00045b63          	bgez	s0,42010f98 <decoder_task+0x5f6>
42010f86:	cf0a8793          	addi	a5,s5,-784
42010f8a:	0330000f          	fence	rw,rw
42010f8e:	439c                	lw	a5,0(a5)
42010f90:	0230000f          	fence	r,rw
42010f94:	64978c63          	beq	a5,s1,420115ec <decoder_task+0xc4a>
42010f98:	00acc783          	lbu	a5,10(s9)
42010f9c:	4c079663          	bnez	a5,42011468 <decoder_task+0xac6>
42010fa0:	4c9c0463          	beq	s8,s1,42011468 <decoder_task+0xac6>
42010fa4:	8566                	mv	a0,s9
42010fa6:	85e2                	mv	a1,s8
42010fa8:	ff6ff0ef          	jal	4201079e <return_decoded_packet>
42010fac:	4b0d                	li	s6,3
42010fae:	4401                	li	s0,0
42010fb0:	b48d                	j	42010a12 <decoder_task+0x70>
42010fb2:	6589                	lui	a1,0x2
42010fb4:	36ba0663          	beq	s4,a1,42011320 <decoder_task+0x97e>
42010fb8:	854a                	mv	a0,s2
42010fba:	e94f70ef          	jal	4200864e <realloc>
42010fbe:	842a                	mv	s0,a0
42010fc0:	6a050063          	beqz	a0,42011660 <decoder_task+0xcbe>
42010fc4:	204347b7          	lui	a5,0x20434
42010fc8:	14178793          	addi	a5,a5,321 # 20434141 <CSR_UINTSTATUS+0x20433490>
42010fcc:	d682                	sw	zero,108(sp)
42010fce:	d882                	sw	zero,112(sp)
42010fd0:	da82                	sw	zero,116(sp)
42010fd2:	d4be                	sw	a5,104(sp)
42010fd4:	039010ef          	jal	4201280c <native_aac_decoder_create>
42010fd8:	89aa                	mv	s3,a0
42010fda:	4c050463          	beqz	a0,420114a2 <decoder_task+0xb00>
42010fde:	8922                	mv	s2,s0
42010fe0:	6a09                	lui	s4,0x2
42010fe2:	4b81                	li	s7,0
42010fe4:	4d81                	li	s11,0
42010fe6:	b13d                	j	42010c14 <decoder_task+0x272>
42010fe8:	5d61                	li	s10,-8
42010fea:	c662                	sw	s8,12(sp)
42010fec:	e789                	bnez	a5,42010ff6 <decoder_task+0x654>
42010fee:	05c14783          	lbu	a5,92(sp)
42010ff2:	1c078f63          	beqz	a5,420111d0 <decoder_task+0x82e>
42010ff6:	4781                	li	a5,0
42010ff8:	4801                	li	a6,0
42010ffa:	de3e                	sw	a5,60(sp)
42010ffc:	c0c2                	sw	a6,64(sp)
42010ffe:	da4a                	sw	s2,52(sp)
42011000:	dc52                	sw	s4,56(sp)
42011002:	d082                	sw	zero,96(sp)
42011004:	fe370097          	auipc	ra,0xfe370
42011008:	336080e7          	jalr	822(ra) # 4038133a <esp_timer_get_time>
4201100c:	842a                	mv	s0,a0
4201100e:	4572                	lw	a0,28(sp)
42011010:	1850                	addi	a2,sp,52
42011012:	08cc                	addi	a1,sp,84
42011014:	500150ef          	jal	42026514 <__wrap_esp_audio_simple_dec_process>
42011018:	8c2a                	mv	s8,a0
4201101a:	fe370097          	auipc	ra,0xfe370
4201101e:	320080e7          	jalr	800(ra) # 4038133a <esp_timer_get_time>
42011022:	47ca                	lw	a5,144(sp)
42011024:	46da                	lw	a3,148(sp)
42011026:	8d01                	sub	a0,a0,s0
42011028:	00a78733          	add	a4,a5,a0
4201102c:	00f737b3          	sltu	a5,a4,a5
42011030:	97b6                	add	a5,a5,a3
42011032:	cb3e                	sw	a5,148(sp)
42011034:	578a                	lw	a5,160(sp)
42011036:	c93a                	sw	a4,144(sp)
42011038:	571a                	lw	a4,164(sp)
4201103a:	0785                	addi	a5,a5,1
4201103c:	d13e                	sw	a5,160(sp)
4201103e:	00a77363          	bgeu	a4,a0,42011044 <decoder_task+0x6a2>
42011042:	d32a                	sw	a0,164(sp)
42011044:	8bfd                	andi	a5,a5,31
42011046:	1e078e63          	beqz	a5,42011242 <decoder_task+0x8a0>
4201104a:	cf0a8793          	addi	a5,s5,-784
4201104e:	0330000f          	fence	rw,rw
42011052:	439c                	lw	a5,0(a5)
42011054:	0230000f          	fence	r,rw
42011058:	16979c63          	bne	a5,s1,420111d0 <decoder_task+0x82e>
4201105c:	1dac0763          	beq	s8,s10,4201122a <decoder_task+0x888>
42011060:	500c1363          	bnez	s8,42011566 <decoder_task+0xbc4>
42011064:	5786                	lw	a5,96(sp)
42011066:	4766                	lw	a4,88(sp)
42011068:	34f76563          	bltu	a4,a5,420113b2 <decoder_task+0xa10>
4201106c:	8f1d                	sub	a4,a4,a5
4201106e:	56aa                	lw	a3,168(sp)
42011070:	ccba                	sw	a4,88(sp)
42011072:	4756                	lw	a4,84(sp)
42011074:	96be                	add	a3,a3,a5
42011076:	d536                	sw	a3,168(sp)
42011078:	97ba                	add	a5,a5,a4
4201107a:	4706                	lw	a4,64(sp)
4201107c:	cabe                	sw	a5,84(sp)
4201107e:	12070363          	beqz	a4,420111a4 <decoder_task+0x802>
42011082:	4572                	lw	a0,28(sp)
42011084:	00cc                	addi	a1,sp,68
42011086:	c282                	sw	zero,68(sp)
42011088:	c482                	sw	zero,72(sp)
4201108a:	c682                	sw	zero,76(sp)
4201108c:	c882                	sw	zero,80(sp)
4201108e:	2d6280ef          	jal	42039364 <esp_audio_simple_dec_get_info>
42011092:	1a051e63          	bnez	a0,4201124e <decoder_task+0x8ac>
42011096:	4782                	lw	a5,0(sp)
42011098:	00f10da3          	sb	a5,27(sp)
4201109c:	4789                	li	a5,2
4201109e:	46fb0663          	beq	s6,a5,4201150a <decoder_task+0xb68>
420110a2:	4791                	li	a5,4
420110a4:	44fb0e63          	beq	s6,a5,42011500 <decoder_task+0xb5e>
420110a8:	3c126737          	lui	a4,0x3c126
420110ac:	4785                	li	a5,1
420110ae:	89870593          	addi	a1,a4,-1896 # 3c125898 <_esp_trace_encoder_array_end+0x5778>
420110b2:	3efb1363          	bne	s6,a5,42011498 <decoder_task+0xaf6>
420110b6:	cf0a8793          	addi	a5,s5,-784
420110ba:	0330000f          	fence	rw,rw
420110be:	439c                	lw	a5,0(a5)
420110c0:	0230000f          	fence	r,rw
420110c4:	06979463          	bne	a5,s1,4201112c <decoder_task+0x78a>
420110c8:	4796                	lw	a5,68(sp)
420110ca:	c3b5                	beqz	a5,4201112e <decoder_task+0x78c>
420110cc:	04914683          	lbu	a3,73(sp)
420110d0:	ceb1                	beqz	a3,4201112c <decoder_task+0x78a>
420110d2:	04815703          	lhu	a4,72(sp)
420110d6:	04814503          	lbu	a0,72(sp)
420110da:	00875613          	srli	a2,a4,0x8
420110de:	0722                	slli	a4,a4,0x8
420110e0:	963a                	add	a2,a2,a4
420110e2:	c529                	beqz	a0,4201112c <decoder_task+0x78a>
420110e4:	06012b23          	sw	zero,118(sp)
420110e8:	06012923          	sw	zero,114(sp)
420110ec:	d23e                	sw	a5,36(sp)
420110ee:	06c11823          	sh	a2,112(sp)
420110f2:	d6be                	sw	a5,108(sp)
420110f4:	4626                	lw	a2,72(sp)
420110f6:	dabe                	sw	a5,116(sp)
420110f8:	3fc957b7          	lui	a5,0x3fc95
420110fc:	4746                	lw	a4,80(sp)
420110fe:	d047a503          	lw	a0,-764(a5) # 3fc94d04 <s_state>
42011102:	06d10c23          	sb	a3,120(sp)
42011106:	4782                	lw	a5,0(sp)
42011108:	46b6                	lw	a3,76(sp)
4201110a:	06011d23          	sh	zero,122(sp)
4201110e:	d4ae                	sw	a1,104(sp)
42011110:	d432                	sw	a2,40(sp)
42011112:	4405                	li	s0,1
42011114:	10b0                	addi	a2,sp,104
42011116:	85a6                	mv	a1,s1
42011118:	06f10d23          	sb	a5,122(sp)
4201111c:	d636                	sw	a3,44(sp)
4201111e:	d83a                	sw	a4,48(sp)
42011120:	00810d23          	sb	s0,26(sp)
42011124:	368040ef          	jal	4201548c <native_state_set_stream_info>
42011128:	87a2                	mv	a5,s0
4201112a:	a011                	j	4201112e <decoder_task+0x78c>
4201112c:	4781                	li	a5,0
4201112e:	45b6                	lw	a1,76(sp)
42011130:	8526                	mv	a0,s1
42011132:	00f10d23          	sb	a5,26(sp)
42011136:	af0ff0ef          	jal	42010426 <state_set_decoder_bitrate>
4201113a:	01a14783          	lbu	a5,26(sp)
4201113e:	c3bd                	beqz	a5,420111a4 <decoder_task+0x802>
42011140:	1e0d8263          	beqz	s11,42011324 <decoder_task+0x982>
42011144:	02814503          	lbu	a0,40(sp)
42011148:	02914783          	lbu	a5,41(sp)
4201114c:	4406                	lw	s0,64(sp)
4201114e:	051d                	addi	a0,a0,7
42011150:	810d                	srli	a0,a0,0x3
42011152:	02f50533          	mul	a0,a0,a5
42011156:	cd15                	beqz	a0,42011192 <decoder_task+0x7f0>
42011158:	5612                	lw	a2,36(sp)
4201115a:	ce05                	beqz	a2,42011192 <decoder_task+0x7f0>
4201115c:	02a45533          	divu	a0,s0,a0
42011160:	000f47b7          	lui	a5,0xf4
42011164:	24078793          	addi	a5,a5,576 # f4240 <CSR_UINTSTATUS+0xf358f>
42011168:	4681                	li	a3,0
4201116a:	02f535b3          	mulhu	a1,a0,a5
4201116e:	02f50533          	mul	a0,a0,a5
42011172:	fdfef097          	auipc	ra,0xfdfef
42011176:	73a080e7          	jalr	1850(ra) # 400008ac <__udivdi3>
4201117a:	47ea                	lw	a5,152(sp)
4201117c:	46fa                	lw	a3,156(sp)
4201117e:	573a                	lw	a4,172(sp)
42011180:	953e                	add	a0,a0,a5
42011182:	96ae                	add	a3,a3,a1
42011184:	00f537b3          	sltu	a5,a0,a5
42011188:	97b6                	add	a5,a5,a3
4201118a:	9722                	add	a4,a4,s0
4201118c:	cf3e                	sw	a5,156(sp)
4201118e:	cd2a                	sw	a0,152(sp)
42011190:	d73a                	sw	a4,172(sp)
42011192:	86a2                	mv	a3,s0
42011194:	864a                	mv	a2,s2
42011196:	104c                	addi	a1,sp,36
42011198:	8526                	mv	a0,s1
4201119a:	eccff0ef          	jal	42010866 <send_pcm.isra.0>
4201119e:	8daa                	mv	s11,a0
420111a0:	38050d63          	beqz	a0,4201153a <decoder_task+0xb98>
420111a4:	fe370097          	auipc	ra,0xfe370
420111a8:	196080e7          	jalr	406(ra) # 4038133a <esp_timer_get_time>
420111ac:	862e                	mv	a2,a1
420111ae:	85aa                	mv	a1,a0
420111b0:	0108                	addi	a0,sp,128
420111b2:	df7fe0ef          	jal	4200ffa8 <decode_stats_report>
420111b6:	4706                	lw	a4,64(sp)
420111b8:	5786                	lw	a5,96(sp)
420111ba:	05c14683          	lbu	a3,92(sp)
420111be:	8fd9                	or	a5,a5,a4
420111c0:	efb9                	bnez	a5,4201121e <decoder_task+0x87c>
420111c2:	3c068363          	beqz	a3,42011588 <decoder_task+0xbe6>
420111c6:	4701                	li	a4,0
420111c8:	47e6                	lw	a5,88(sp)
420111ca:	8f5d                	or	a4,a4,a5
420111cc:	e20710e3          	bnez	a4,42010fec <decoder_task+0x64a>
420111d0:	4c32                	lw	s8,12(sp)
420111d2:	b1a1                	j	42010e1a <decoder_task+0x478>
420111d4:	c2069fe3          	bnez	a3,42010e12 <decoder_task+0x470>
420111d8:	47e6                	lw	a5,88(sp)
420111da:	a60798e3          	bnez	a5,42010c4a <decoder_task+0x2a8>
420111de:	b935                	j	42010e1a <decoder_task+0x478>
420111e0:	5706                	lw	a4,96(sp)
420111e2:	47d6                	lw	a5,84(sp)
420111e4:	56aa                	lw	a3,168(sp)
420111e6:	5472                	lw	s0,60(sp)
420111e8:	97ba                	add	a5,a5,a4
420111ea:	cabe                	sw	a5,84(sp)
420111ec:	47e6                	lw	a5,88(sp)
420111ee:	96ba                	add	a3,a3,a4
420111f0:	d536                	sw	a3,168(sp)
420111f2:	8f99                	sub	a5,a5,a4
420111f4:	ccbe                	sw	a5,88(sp)
420111f6:	308a7f63          	bgeu	s4,s0,42011514 <decoder_task+0xb72>
420111fa:	85a2                	mv	a1,s0
420111fc:	854a                	mv	a0,s2
420111fe:	c50f70ef          	jal	4200864e <realloc>
42011202:	30050963          	beqz	a0,42011514 <decoder_task+0xb72>
42011206:	8a22                	mv	s4,s0
42011208:	892a                	mv	s2,a0
4201120a:	b481                	j	42010c4a <decoder_task+0x2a8>
4201120c:	4505                	li	a0,1
4201120e:	00102097          	auipc	ra,0x102
42011212:	b14080e7          	jalr	-1260(ra) # 42112d22 <vTaskDelay>
42011216:	b461                	j	42010c9e <decoder_task+0x2fc>
42011218:	00010d23          	sb	zero,26(sp)
4201121c:	bec1                	j	42010dec <decoder_task+0x44a>
4201121e:	f6cd                	bnez	a3,420111c8 <decoder_task+0x826>
42011220:	47e6                	lw	a5,88(sp)
42011222:	dc079ae3          	bnez	a5,42010ff6 <decoder_task+0x654>
42011226:	4c32                	lw	s8,12(sp)
42011228:	becd                	j	42010e1a <decoder_task+0x478>
4201122a:	5472                	lw	s0,60(sp)
4201122c:	2e8a7463          	bgeu	s4,s0,42011514 <decoder_task+0xb72>
42011230:	85a2                	mv	a1,s0
42011232:	854a                	mv	a0,s2
42011234:	c1af70ef          	jal	4200864e <realloc>
42011238:	2c050e63          	beqz	a0,42011514 <decoder_task+0xb72>
4201123c:	892a                	mv	s2,a0
4201123e:	8a22                	mv	s4,s0
42011240:	bb5d                	j	42010ff6 <decoder_task+0x654>
42011242:	4505                	li	a0,1
42011244:	00102097          	auipc	ra,0x102
42011248:	ade080e7          	jalr	-1314(ra) # 42112d22 <vTaskDelay>
4201124c:	bbfd                	j	4201104a <decoder_task+0x6a8>
4201124e:	00010d23          	sb	zero,26(sp)
42011252:	bf89                	j	420111a4 <decoder_task+0x802>
42011254:	3c1267b7          	lui	a5,0x3c126
42011258:	bc878513          	addi	a0,a5,-1080 # 3c125bc8 <_esp_trace_encoder_array_end+0x5aa8>
4201125c:	966ff0ef          	jal	420103c2 <log_runtime_memory>
42011260:	be0d                	j	42010d92 <decoder_task+0x3f0>
42011262:	846a                	mv	s0,s10
42011264:	4a09                	li	s4,2
42011266:	fe377097          	auipc	ra,0xfe377
4201126a:	154080e7          	jalr	340(ra) # 403883ba <esp_log_timestamp>
4201126e:	2f4b0e63          	beq	s6,s4,4201156a <decoder_task+0xbc8>
42011272:	4791                	li	a5,4
42011274:	30fb0063          	beq	s6,a5,42011574 <decoder_task+0xbd2>
42011278:	3c1267b7          	lui	a5,0x3c126
4201127c:	4705                	li	a4,1
4201127e:	89878793          	addi	a5,a5,-1896 # 3c125898 <_esp_trace_encoder_array_end+0x5778>
42011282:	00eb0663          	beq	s6,a4,4201128e <decoder_task+0x8ec>
42011286:	3c1267b7          	lui	a5,0x3c126
4201128a:	89c78793          	addi	a5,a5,-1892 # 3c12589c <_esp_trace_encoder_array_end+0x577c>
4201128e:	3c126737          	lui	a4,0x3c126
42011292:	8a470713          	addi	a4,a4,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
42011296:	3c126637          	lui	a2,0x3c126
4201129a:	86aa                	mv	a3,a0
4201129c:	85ba                	mv	a1,a4
4201129e:	8822                	mv	a6,s0
420112a0:	bfc60613          	addi	a2,a2,-1028 # 3c125bfc <_esp_trace_encoder_array_end+0x5adc>
420112a4:	4509                	li	a0,2
420112a6:	fe377097          	auipc	ra,0xfe377
420112aa:	00c080e7          	jalr	12(ra) # 403882b2 <esp_log>
420112ae:	3fc957b7          	lui	a5,0x3fc95
420112b2:	d047a503          	lw	a0,-764(a5) # 3fc94d04 <s_state>
420112b6:	3c1267b7          	lui	a5,0x3c126
420112ba:	aa478693          	addi	a3,a5,-1372 # 3c125aa4 <_esp_trace_encoder_array_end+0x5984>
420112be:	85a6                	mv	a1,s1
420112c0:	4601                	li	a2,0
420112c2:	0ea040ef          	jal	420153ac <native_state_set_audio>
420112c6:	8c26                	mv	s8,s1
420112c8:	4572                	lw	a0,28(sp)
420112ca:	c119                	beqz	a0,420112d0 <decoder_task+0x92e>
420112cc:	110280ef          	jal	420393dc <esp_audio_simple_dec_close>
420112d0:	ce02                	sw	zero,28(sp)
420112d2:	00098563          	beqz	s3,420112dc <decoder_task+0x93a>
420112d6:	854e                	mv	a0,s3
420112d8:	560010ef          	jal	42012838 <native_aac_decoder_destroy>
420112dc:	854a                	mv	a0,s2
420112de:	b74f70ef          	jal	42008652 <cfree>
420112e2:	4981                	li	s3,0
420112e4:	4a01                	li	s4,0
420112e6:	4901                	li	s2,0
420112e8:	be3d                	j	42010e26 <decoder_task+0x484>
420112ea:	854e                	mv	a0,s3
420112ec:	111010ef          	jal	42012bfc <native_aac_decoder_source_channels>
420112f0:	01b14683          	lbu	a3,27(sp)
420112f4:	0ff57513          	zext.b	a0,a0
420112f8:	bc09                	j	42010d0a <decoder_task+0x368>
420112fa:	204747b7          	lui	a5,0x20474
420112fe:	74f78793          	addi	a5,a5,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
42011302:	086c                	addi	a1,sp,28
42011304:	10a8                	addi	a0,sp,104
42011306:	d4be                	sw	a5,104(sp)
42011308:	080150ef          	jal	42026388 <__wrap_esp_audio_simple_dec_open>
4201130c:	842a                	mv	s0,a0
4201130e:	1c051963          	bnez	a0,420114e0 <decoder_task+0xb3e>
42011312:	4bf2                	lw	s7,28(sp)
42011314:	4d81                	li	s11,0
42011316:	8c0b81e3          	beqz	s7,42010bd8 <decoder_task+0x236>
4201131a:	4981                	li	s3,0
4201131c:	4b81                	li	s7,0
4201131e:	b8dd                	j	42010c14 <decoder_task+0x272>
42011320:	844a                	mv	s0,s2
42011322:	b14d                	j	42010fc4 <decoder_task+0x622>
42011324:	3c1267b7          	lui	a5,0x3c126
42011328:	bc878513          	addi	a0,a5,-1080 # 3c125bc8 <_esp_trace_encoder_array_end+0x5aa8>
4201132c:	896ff0ef          	jal	420103c2 <log_runtime_memory>
42011330:	bd11                	j	42011144 <decoder_task+0x7a2>
42011332:	d682                	sw	zero,108(sp)
42011334:	d882                	sw	zero,112(sp)
42011336:	da82                	sw	zero,116(sp)
42011338:	815ff06f          	j	42010b4c <decoder_task+0x1aa>
4201133c:	fe377097          	auipc	ra,0xfe377
42011340:	07e080e7          	jalr	126(ra) # 403883ba <esp_log_timestamp>
42011344:	4791                	li	a5,4
42011346:	4405                	li	s0,1
42011348:	86aa                	mv	a3,a0
4201134a:	1efb0363          	beq	s6,a5,42011530 <decoder_task+0xb8e>
4201134e:	3c1267b7          	lui	a5,0x3c126
42011352:	89878793          	addi	a5,a5,-1896 # 3c125898 <_esp_trace_encoder_array_end+0x5778>
42011356:	008b0663          	beq	s6,s0,42011362 <decoder_task+0x9c0>
4201135a:	3c1267b7          	lui	a5,0x3c126
4201135e:	89c78793          	addi	a5,a5,-1892 # 3c12589c <_esp_trace_encoder_array_end+0x577c>
42011362:	3c126737          	lui	a4,0x3c126
42011366:	8a470713          	addi	a4,a4,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
4201136a:	3c126637          	lui	a2,0x3c126
4201136e:	85ba                	mv	a1,a4
42011370:	b2c60613          	addi	a2,a2,-1236 # 3c125b2c <_esp_trace_encoder_array_end+0x5a0c>
42011374:	4505                	li	a0,1
42011376:	fe377097          	auipc	ra,0xfe377
4201137a:	f3c080e7          	jalr	-196(ra) # 403882b2 <esp_log>
4201137e:	3fc957b7          	lui	a5,0x3fc95
42011382:	d047a503          	lw	a0,-764(a5) # 3fc94d04 <s_state>
42011386:	3c1267b7          	lui	a5,0x3c126
4201138a:	a8878693          	addi	a3,a5,-1400 # 3c125a88 <_esp_trace_encoder_array_end+0x5968>
4201138e:	85a6                	mv	a1,s1
42011390:	4601                	li	a2,0
42011392:	01a040ef          	jal	420153ac <native_state_set_audio>
42011396:	3fc957b7          	lui	a5,0x3fc95
4201139a:	cfc7a503          	lw	a0,-772(a5) # 3fc94cfc <s_encoded>
4201139e:	85e6                	mv	a1,s9
420113a0:	8c26                	mv	s8,s1
420113a2:	39d670ef          	jal	42078f3e <vRingbufferReturnItem>
420113a6:	4981                	li	s3,0
420113a8:	4d81                	li	s11,0
420113aa:	4b81                	li	s7,0
420113ac:	4401                	li	s0,0
420113ae:	e64ff06f          	j	42010a12 <decoder_task+0x70>
420113b2:	fe377097          	auipc	ra,0xfe377
420113b6:	008080e7          	jalr	8(ra) # 403883ba <esp_log_timestamp>
420113ba:	4789                	li	a5,2
420113bc:	4405                	li	s0,1
420113be:	12fb0c63          	beq	s6,a5,420114f6 <decoder_task+0xb54>
420113c2:	4791                	li	a5,4
420113c4:	1afb0d63          	beq	s6,a5,4201157e <decoder_task+0xbdc>
420113c8:	3c1267b7          	lui	a5,0x3c126
420113cc:	89878793          	addi	a5,a5,-1896 # 3c125898 <_esp_trace_encoder_array_end+0x5778>
420113d0:	008b0663          	beq	s6,s0,420113dc <decoder_task+0xa3a>
420113d4:	3c1267b7          	lui	a5,0x3c126
420113d8:	89c78793          	addi	a5,a5,-1892 # 3c12589c <_esp_trace_encoder_array_end+0x577c>
420113dc:	48e6                	lw	a7,88(sp)
420113de:	5806                	lw	a6,96(sp)
420113e0:	3c126737          	lui	a4,0x3c126
420113e4:	8a470713          	addi	a4,a4,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
420113e8:	3c126637          	lui	a2,0x3c126
420113ec:	86aa                	mv	a3,a0
420113ee:	85ba                	mv	a1,a4
420113f0:	c2060613          	addi	a2,a2,-992 # 3c125c20 <_esp_trace_encoder_array_end+0x5b00>
420113f4:	4505                	li	a0,1
420113f6:	fe377097          	auipc	ra,0xfe377
420113fa:	ebc080e7          	jalr	-324(ra) # 403882b2 <esp_log>
420113fe:	3fc957b7          	lui	a5,0x3fc95
42011402:	d047a503          	lw	a0,-764(a5) # 3fc94d04 <s_state>
42011406:	3c1267b7          	lui	a5,0x3c126
4201140a:	c5c78693          	addi	a3,a5,-932 # 3c125c5c <_esp_trace_encoder_array_end+0x5b3c>
4201140e:	85a6                	mv	a1,s1
42011410:	4601                	li	a2,0
42011412:	79b030ef          	jal	420153ac <native_state_set_audio>
42011416:	8c26                	mv	s8,s1
42011418:	bd45                	j	420112c8 <decoder_task+0x926>
4201141a:	b60b8fe3          	beqz	s7,42010f98 <decoder_task+0x5f6>
4201141e:	bce1                	j	42010ef6 <decoder_task+0x554>
42011420:	fe377097          	auipc	ra,0xfe377
42011424:	f9a080e7          	jalr	-102(ra) # 403883ba <esp_log_timestamp>
42011428:	3c1267b7          	lui	a5,0x3c126
4201142c:	8a478713          	addi	a4,a5,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
42011430:	3c1267b7          	lui	a5,0x3c126
42011434:	86aa                	mv	a3,a0
42011436:	85ba                	mv	a1,a4
42011438:	af878613          	addi	a2,a5,-1288 # 3c125af8 <_esp_trace_encoder_array_end+0x59d8>
4201143c:	4505                	li	a0,1
4201143e:	fe377097          	auipc	ra,0xfe377
42011442:	e74080e7          	jalr	-396(ra) # 403882b2 <esp_log>
42011446:	3fc957b7          	lui	a5,0x3fc95
4201144a:	d047a503          	lw	a0,-764(a5) # 3fc94d04 <s_state>
4201144e:	3c1267b7          	lui	a5,0x3c126
42011452:	a8878693          	addi	a3,a5,-1400 # 3c125a88 <_esp_trace_encoder_array_end+0x5968>
42011456:	85a6                	mv	a1,s1
42011458:	4601                	li	a2,0
4201145a:	753030ef          	jal	420153ac <native_state_set_audio>
4201145e:	8c26                	mv	s8,s1
42011460:	4981                	li	s3,0
42011462:	4901                	li	s2,0
42011464:	4a01                	li	s4,0
42011466:	4d81                	li	s11,0
42011468:	855e                	mv	a0,s7
4201146a:	0cc240ef          	jal	42035536 <custom_flac_decoder_destroy>
4201146e:	4b81                	li	s7,0
42011470:	be15                	j	42010fa4 <decoder_task+0x602>
42011472:	8542                	mv	a0,a6
42011474:	b0d5                	j	42010d58 <decoder_task+0x3b6>
42011476:	3c1267b7          	lui	a5,0x3c126
4201147a:	89c78793          	addi	a5,a5,-1892 # 3c12589c <_esp_trace_encoder_array_end+0x577c>
4201147e:	f04ff06f          	j	42010b82 <decoder_task+0x1e0>
42011482:	01a14d83          	lbu	s11,26(sp)
42011486:	ae0d85e3          	beqz	s11,42010f70 <decoder_task+0x5ce>
4201148a:	3c1267b7          	lui	a5,0x3c126
4201148e:	b8478513          	addi	a0,a5,-1148 # 3c125b84 <_esp_trace_encoder_array_end+0x5a64>
42011492:	f31fe0ef          	jal	420103c2 <log_runtime_memory>
42011496:	bce1                	j	42010f6e <decoder_task+0x5cc>
42011498:	3c1267b7          	lui	a5,0x3c126
4201149c:	89c78593          	addi	a1,a5,-1892 # 3c12589c <_esp_trace_encoder_array_end+0x577c>
420114a0:	b919                	j	420110b6 <decoder_task+0x714>
420114a2:	fe377097          	auipc	ra,0xfe377
420114a6:	f18080e7          	jalr	-232(ra) # 403883ba <esp_log_timestamp>
420114aa:	3c1267b7          	lui	a5,0x3c126
420114ae:	8a478713          	addi	a4,a5,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
420114b2:	3c126637          	lui	a2,0x3c126
420114b6:	3c1267b7          	lui	a5,0x3c126
420114ba:	86aa                	mv	a3,a0
420114bc:	88878793          	addi	a5,a5,-1912 # 3c125888 <_esp_trace_encoder_array_end+0x5768>
420114c0:	85ba                	mv	a1,a4
420114c2:	b5c60613          	addi	a2,a2,-1188 # 3c125b5c <_esp_trace_encoder_array_end+0x5a3c>
420114c6:	5879                	li	a6,-2
420114c8:	4505                	li	a0,1
420114ca:	fe377097          	auipc	ra,0xfe377
420114ce:	de8080e7          	jalr	-536(ra) # 403882b2 <esp_log>
420114d2:	3c1267b7          	lui	a5,0x3c126
420114d6:	8922                	mv	s2,s0
420114d8:	a8878693          	addi	a3,a5,-1400 # 3c125a88 <_esp_trace_encoder_array_end+0x5968>
420114dc:	ed2ff06f          	j	42010bae <decoder_task+0x20c>
420114e0:	fe377097          	auipc	ra,0xfe377
420114e4:	eda080e7          	jalr	-294(ra) # 403883ba <esp_log_timestamp>
420114e8:	3c1267b7          	lui	a5,0x3c126
420114ec:	86aa                	mv	a3,a0
420114ee:	89478793          	addi	a5,a5,-1900 # 3c125894 <_esp_trace_encoder_array_end+0x5774>
420114f2:	e90ff06f          	j	42010b82 <decoder_task+0x1e0>
420114f6:	3c1267b7          	lui	a5,0x3c126
420114fa:	88878793          	addi	a5,a5,-1912 # 3c125888 <_esp_trace_encoder_array_end+0x5768>
420114fe:	bdf9                	j	420113dc <decoder_task+0xa3a>
42011500:	3c1267b7          	lui	a5,0x3c126
42011504:	89478593          	addi	a1,a5,-1900 # 3c125894 <_esp_trace_encoder_array_end+0x5774>
42011508:	b67d                	j	420110b6 <decoder_task+0x714>
4201150a:	3c1267b7          	lui	a5,0x3c126
4201150e:	88878593          	addi	a1,a5,-1912 # 3c125888 <_esp_trace_encoder_array_end+0x5768>
42011512:	b655                	j	420110b6 <decoder_task+0x714>
42011514:	3fc957b7          	lui	a5,0x3fc95
42011518:	d047a503          	lw	a0,-764(a5) # 3fc94d04 <s_state>
4201151c:	3c1267b7          	lui	a5,0x3c126
42011520:	be478693          	addi	a3,a5,-1052 # 3c125be4 <_esp_trace_encoder_array_end+0x5ac4>
42011524:	4601                	li	a2,0
42011526:	85a6                	mv	a1,s1
42011528:	685030ef          	jal	420153ac <native_state_set_audio>
4201152c:	8c26                	mv	s8,s1
4201152e:	bb69                	j	420112c8 <decoder_task+0x926>
42011530:	3c1267b7          	lui	a5,0x3c126
42011534:	89478793          	addi	a5,a5,-1900 # 3c125894 <_esp_trace_encoder_array_end+0x5774>
42011538:	b52d                	j	42011362 <decoder_task+0x9c0>
4201153a:	4c32                	lw	s8,12(sp)
4201153c:	fe377097          	auipc	ra,0xfe377
42011540:	e7e080e7          	jalr	-386(ra) # 403883ba <esp_log_timestamp>
42011544:	3c1267b7          	lui	a5,0x3c126
42011548:	8a478713          	addi	a4,a5,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
4201154c:	3c1267b7          	lui	a5,0x3c126
42011550:	86aa                	mv	a3,a0
42011552:	85ba                	mv	a1,a4
42011554:	c7078613          	addi	a2,a5,-912 # 3c125c70 <_esp_trace_encoder_array_end+0x5b50>
42011558:	4509                	li	a0,2
4201155a:	fe377097          	auipc	ra,0xfe377
4201155e:	d58080e7          	jalr	-680(ra) # 403882b2 <esp_log>
42011562:	4d85                	li	s11,1
42011564:	b85d                	j	42010e1a <decoder_task+0x478>
42011566:	8462                	mv	s0,s8
42011568:	b9f5                	j	42011264 <decoder_task+0x8c2>
4201156a:	3c1267b7          	lui	a5,0x3c126
4201156e:	88878793          	addi	a5,a5,-1912 # 3c125888 <_esp_trace_encoder_array_end+0x5768>
42011572:	bb31                	j	4201128e <decoder_task+0x8ec>
42011574:	3c1267b7          	lui	a5,0x3c126
42011578:	89478793          	addi	a5,a5,-1900 # 3c125894 <_esp_trace_encoder_array_end+0x5774>
4201157c:	bb09                	j	4201128e <decoder_task+0x8ec>
4201157e:	3c1267b7          	lui	a5,0x3c126
42011582:	89478793          	addi	a5,a5,-1900 # 3c125894 <_esp_trace_encoder_array_end+0x5774>
42011586:	bd99                	j	420113dc <decoder_task+0xa3a>
42011588:	fe377097          	auipc	ra,0xfe377
4201158c:	e32080e7          	jalr	-462(ra) # 403883ba <esp_log_timestamp>
42011590:	4789                	li	a5,2
42011592:	4405                	li	s0,1
42011594:	86aa                	mv	a3,a0
42011596:	0afb0563          	beq	s6,a5,42011640 <decoder_task+0xc9e>
4201159a:	4791                	li	a5,4
4201159c:	0afb0d63          	beq	s6,a5,42011656 <decoder_task+0xcb4>
420115a0:	3c1267b7          	lui	a5,0x3c126
420115a4:	89878793          	addi	a5,a5,-1896 # 3c125898 <_esp_trace_encoder_array_end+0x5778>
420115a8:	008b0663          	beq	s6,s0,420115b4 <decoder_task+0xc12>
420115ac:	3c1267b7          	lui	a5,0x3c126
420115b0:	89c78793          	addi	a5,a5,-1892 # 3c12589c <_esp_trace_encoder_array_end+0x577c>
420115b4:	3c126737          	lui	a4,0x3c126
420115b8:	8a470713          	addi	a4,a4,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
420115bc:	3c126637          	lui	a2,0x3c126
420115c0:	85ba                	mv	a1,a4
420115c2:	c9060613          	addi	a2,a2,-880 # 3c125c90 <_esp_trace_encoder_array_end+0x5b70>
420115c6:	4505                	li	a0,1
420115c8:	fe377097          	auipc	ra,0xfe377
420115cc:	cea080e7          	jalr	-790(ra) # 403882b2 <esp_log>
420115d0:	3fc957b7          	lui	a5,0x3fc95
420115d4:	d047a503          	lw	a0,-764(a5) # 3fc94d04 <s_state>
420115d8:	3c1267b7          	lui	a5,0x3c126
420115dc:	cc078693          	addi	a3,a5,-832 # 3c125cc0 <_esp_trace_encoder_array_end+0x5ba0>
420115e0:	85a6                	mv	a1,s1
420115e2:	4601                	li	a2,0
420115e4:	5c9030ef          	jal	420153ac <native_state_set_audio>
420115e8:	8c26                	mv	s8,s1
420115ea:	b9f9                	j	420112c8 <decoder_task+0x926>
420115ec:	fe377097          	auipc	ra,0xfe377
420115f0:	dce080e7          	jalr	-562(ra) # 403883ba <esp_log_timestamp>
420115f4:	3c126737          	lui	a4,0x3c126
420115f8:	8a470713          	addi	a4,a4,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
420115fc:	3c126637          	lui	a2,0x3c126
42011600:	86aa                	mv	a3,a0
42011602:	87a2                	mv	a5,s0
42011604:	85ba                	mv	a1,a4
42011606:	b9c60613          	addi	a2,a2,-1124 # 3c125b9c <_esp_trace_encoder_array_end+0x5a7c>
4201160a:	4509                	li	a0,2
4201160c:	fe377097          	auipc	ra,0xfe377
42011610:	ca6080e7          	jalr	-858(ra) # 403882b2 <esp_log>
42011614:	3c126737          	lui	a4,0x3c126
42011618:	0419                	addi	s0,s0,6 # 3006 <CSR_UINTSTATUS+0x2355>
4201161a:	4785                	li	a5,1
4201161c:	aa470693          	addi	a3,a4,-1372 # 3c125aa4 <_esp_trace_encoder_array_end+0x5984>
42011620:	0087e663          	bltu	a5,s0,4201162c <decoder_task+0xc8a>
42011624:	3c1267b7          	lui	a5,0x3c126
42011628:	a8878693          	addi	a3,a5,-1400 # 3c125a88 <_esp_trace_encoder_array_end+0x5968>
4201162c:	3fc957b7          	lui	a5,0x3fc95
42011630:	d047a503          	lw	a0,-764(a5) # 3fc94d04 <s_state>
42011634:	4601                	li	a2,0
42011636:	85a6                	mv	a1,s1
42011638:	575030ef          	jal	420153ac <native_state_set_audio>
4201163c:	8c26                	mv	s8,s1
4201163e:	baa9                	j	42010f98 <decoder_task+0x5f6>
42011640:	3c1267b7          	lui	a5,0x3c126
42011644:	88878793          	addi	a5,a5,-1912 # 3c125888 <_esp_trace_encoder_array_end+0x5768>
42011648:	b7b5                	j	420115b4 <decoder_task+0xc12>
4201164a:	3c1267b7          	lui	a5,0x3c126
4201164e:	a8878693          	addi	a3,a5,-1400 # 3c125a88 <_esp_trace_encoder_array_end+0x5968>
42011652:	d5cff06f          	j	42010bae <decoder_task+0x20c>
42011656:	3c1267b7          	lui	a5,0x3c126
4201165a:	89478793          	addi	a5,a5,-1900 # 3c125894 <_esp_trace_encoder_array_end+0x5774>
4201165e:	bf99                	j	420115b4 <decoder_task+0xc12>
42011660:	fe377097          	auipc	ra,0xfe377
42011664:	d5a080e7          	jalr	-678(ra) # 403883ba <esp_log_timestamp>
42011668:	3c1267b7          	lui	a5,0x3c126
4201166c:	86aa                	mv	a3,a0
4201166e:	88878793          	addi	a5,a5,-1912 # 3c125888 <_esp_trace_encoder_array_end+0x5768>
42011672:	b9c5                	j	42011362 <decoder_task+0x9c0>
