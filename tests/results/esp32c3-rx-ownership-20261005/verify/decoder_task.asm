
idf\esp32c3-oled-native\build-rx-owner\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4201099e <decoder_task>:
4201099e:	7151                	addi	sp,sp,-240
420109a0:	d5a2                	sw	s0,232(sp)
420109a2:	d3a6                	sw	s1,228(sp)
420109a4:	d1ca                	sw	s2,224(sp)
420109a6:	cfce                	sw	s3,220(sp)
420109a8:	cdd2                	sw	s4,216(sp)
420109aa:	cbd6                	sw	s5,212(sp)
420109ac:	c9da                	sw	s6,208(sp)
420109ae:	c7de                	sw	s7,204(sp)
420109b0:	c5e2                	sw	s8,200(sp)
420109b2:	df6e                	sw	s11,188(sp)
420109b4:	d786                	sw	ra,236(sp)
420109b6:	c3e6                	sw	s9,196(sp)
420109b8:	c1ea                	sw	s10,192(sp)
420109ba:	5d1010ef          	jal	4201278a <decoder_register_codecs>
420109be:	3fc95737          	lui	a4,0x3fc95
420109c2:	000f47b7          	lui	a5,0xf4
420109c6:	cd870713          	addi	a4,a4,-808 # 3fc94cd8 <s_bitrate_updated_us>
420109ca:	24078793          	addi	a5,a5,576 # f4240 <CSR_UINTSTATUS+0xf358f>
420109ce:	ce02                	sw	zero,28(sp)
420109d0:	c102                	sw	zero,128(sp)
420109d2:	c302                	sw	zero,132(sp)
420109d4:	c502                	sw	zero,136(sp)
420109d6:	c702                	sw	zero,140(sp)
420109d8:	c902                	sw	zero,144(sp)
420109da:	cb02                	sw	zero,148(sp)
420109dc:	cd02                	sw	zero,152(sp)
420109de:	cf02                	sw	zero,156(sp)
420109e0:	d102                	sw	zero,160(sp)
420109e2:	d302                	sw	zero,164(sp)
420109e4:	d502                	sw	zero,168(sp)
420109e6:	d702                	sw	zero,172(sp)
420109e8:	d202                	sw	zero,36(sp)
420109ea:	d402                	sw	zero,40(sp)
420109ec:	d602                	sw	zero,44(sp)
420109ee:	d802                	sw	zero,48(sp)
420109f0:	00010d23          	sb	zero,26(sp)
420109f4:	842a                	mv	s0,a0
420109f6:	c23a                	sw	a4,4(sp)
420109f8:	c43e                	sw	a5,8(sp)
420109fa:	4981                	li	s3,0
420109fc:	4a01                	li	s4,0
420109fe:	4901                	li	s2,0
42010a00:	4d81                	li	s11,0
42010a02:	4b01                	li	s6,0
42010a04:	4c01                	li	s8,0
42010a06:	4481                	li	s1,0
42010a08:	4b81                	li	s7,0
42010a0a:	3fc95ab7          	lui	s5,0x3fc95
42010a0e:	60b150ef          	jal	42026818 <rx_buffer_diagnostic_poll>
42010a12:	cf0a8793          	addi	a5,s5,-784 # 3fc94cf0 <s_generation>
42010a16:	0330000f          	fence	rw,rw
42010a1a:	0007ac83          	lw	s9,0(a5)
42010a1e:	0230000f          	fence	r,rw
42010a22:	429c8163          	beq	s9,s1,42010e44 <decoder_task+0x4a6>
42010a26:	3fc957b7          	lui	a5,0x3fc95
42010a2a:	cec78793          	addi	a5,a5,-788 # 3fc94cec <s_decoder_target_codec>
42010a2e:	0330000f          	fence	rw,rw
42010a32:	4384                	lw	s1,0(a5)
42010a34:	0230000f          	fence	r,rw
42010a38:	4572                	lw	a0,28(sp)
42010a3a:	c119                	beqz	a0,42010a40 <decoder_task+0xa2>
42010a3c:	583260ef          	jal	420377be <esp_audio_simple_dec_close>
42010a40:	854e                	mv	a0,s3
42010a42:	ce02                	sw	zero,28(sp)
42010a44:	5a9010ef          	jal	420127ec <native_aac_decoder_destroy>
42010a48:	000b8563          	beqz	s7,42010a52 <decoder_task+0xb4>
42010a4c:	855e                	mv	a0,s7
42010a4e:	25d240ef          	jal	420354aa <custom_flac_decoder_destroy>
42010a52:	46048e63          	beqz	s1,42010ece <decoder_task+0x530>
42010a56:	d202                	sw	zero,36(sp)
42010a58:	d402                	sw	zero,40(sp)
42010a5a:	d602                	sw	zero,44(sp)
42010a5c:	d802                	sw	zero,48(sp)
42010a5e:	00010d23          	sb	zero,26(sp)
42010a62:	3fc957b7          	lui	a5,0x3fc95
42010a66:	ce878793          	addi	a5,a5,-792 # 3fc94ce8 <s_decoder_released_generation>
42010a6a:	0310000f          	fence	rw,w
42010a6e:	0197a023          	sw	s9,0(a5)
42010a72:	0330000f          	fence	rw,rw
42010a76:	4b81                	li	s7,0
42010a78:	84e6                	mv	s1,s9
42010a7a:	4c01                	li	s8,0
42010a7c:	4b01                	li	s6,0
42010a7e:	4d81                	li	s11,0
42010a80:	4981                	li	s3,0
42010a82:	3fc957b7          	lui	a5,0x3fc95
42010a86:	cfc7a503          	lw	a0,-772(a5) # 3fc94cfc <s_encoded>
42010a8a:	4651                	li	a2,20
42010a8c:	100c                	addi	a1,sp,32
42010a8e:	d002                	sw	zero,32(sp)
42010a90:	015660ef          	jal	420772a4 <xRingbufferReceive>
42010a94:	8caa                	mv	s9,a0
42010a96:	dd25                	beqz	a0,42010a0e <decoder_task+0x70>
42010a98:	4118                	lw	a4,0(a0)
42010a9a:	cf0a8793          	addi	a5,s5,-784
42010a9e:	0330000f          	fence	rw,rw
42010aa2:	439c                	lw	a5,0(a5)
42010aa4:	0230000f          	fence	r,rw
42010aa8:	40f71b63          	bne	a4,a5,42010ebe <decoder_task+0x520>
42010aac:	411c                	lw	a5,0(a0)
42010aae:	41878863          	beq	a5,s8,42010ebe <decoder_task+0x520>
42010ab2:	4158                	lw	a4,4(a0)
42010ab4:	e709                	bnez	a4,42010abe <decoder_task+0x120>
42010ab6:	00a54703          	lbu	a4,10(a0)
42010aba:	3e071e63          	bnez	a4,42010eb6 <decoder_task+0x518>
42010abe:	12041563          	bnez	s0,42010be8 <decoder_task+0x24a>
42010ac2:	12978c63          	beq	a5,s1,42010bfa <decoder_task+0x25c>
42010ac6:	4572                	lw	a0,28(sp)
42010ac8:	c119                	beqz	a0,42010ace <decoder_task+0x130>
42010aca:	4f5260ef          	jal	420377be <esp_audio_simple_dec_close>
42010ace:	854e                	mv	a0,s3
42010ad0:	ce02                	sw	zero,28(sp)
42010ad2:	51b010ef          	jal	420127ec <native_aac_decoder_destroy>
42010ad6:	000b8563          	beqz	s7,42010ae0 <decoder_task+0x142>
42010ada:	855e                	mv	a0,s7
42010adc:	1cf240ef          	jal	420354aa <custom_flac_decoder_destroy>
42010ae0:	4712                	lw	a4,4(sp)
42010ae2:	000ca483          	lw	s1,0(s9)
42010ae6:	004cab03          	lw	s6,4(s9)
42010aea:	3fc957b7          	lui	a5,0x3fc95
42010aee:	ce07a023          	sw	zero,-800(a5) # 3fc94ce0 <s_published_bitrate_bps>
42010af2:	4801                	li	a6,0
42010af4:	4781                	li	a5,0
42010af6:	c31c                	sw	a5,0(a4)
42010af8:	00010d23          	sb	zero,26(sp)
42010afc:	01072223          	sw	a6,4(a4)
42010b00:	fe371097          	auipc	ra,0xfe371
42010b04:	83a080e7          	jalr	-1990(ra) # 4038133a <esp_timer_get_time>
42010b08:	c52a                	sw	a0,136(sp)
42010b0a:	c902                	sw	zero,144(sp)
42010b0c:	cb02                	sw	zero,148(sp)
42010b0e:	cd02                	sw	zero,152(sp)
42010b10:	cf02                	sw	zero,156(sp)
42010b12:	d102                	sw	zero,160(sp)
42010b14:	d302                	sw	zero,164(sp)
42010b16:	d502                	sw	zero,168(sp)
42010b18:	d702                	sw	zero,172(sp)
42010b1a:	c126                	sw	s1,128(sp)
42010b1c:	c35a                	sw	s6,132(sp)
42010b1e:	c72e                	sw	a1,140(sp)
42010b20:	478d                	li	a5,3
42010b22:	3afb0c63          	beq	s6,a5,42010eda <decoder_task+0x53c>
42010b26:	4789                	li	a5,2
42010b28:	46fb0d63          	beq	s6,a5,42010fa2 <decoder_task+0x604>
42010b2c:	640d                	lui	s0,0x3
42010b2e:	7e8a7663          	bgeu	s4,s0,4201131a <decoder_task+0x97c>
42010b32:	85a2                	mv	a1,s0
42010b34:	854a                	mv	a0,s2
42010b36:	b19f70ef          	jal	4200864e <realloc>
42010b3a:	7e050563          	beqz	a0,42011324 <decoder_task+0x986>
42010b3e:	d682                	sw	zero,108(sp)
42010b40:	d882                	sw	zero,112(sp)
42010b42:	da82                	sw	zero,116(sp)
42010b44:	892a                	mv	s2,a0
42010b46:	8a22                	mv	s4,s0
42010b48:	4791                	li	a5,4
42010b4a:	78fb0c63          	beq	s6,a5,420112e2 <decoder_task+0x944>
42010b4e:	203357b7          	lui	a5,0x20335
42010b52:	04d78793          	addi	a5,a5,77 # 2033504d <CSR_UINTSTATUS+0x2033439c>
42010b56:	086c                	addi	a1,sp,28
42010b58:	10a8                	addi	a0,sp,104
42010b5a:	d4be                	sw	a5,104(sp)
42010b5c:	7a4150ef          	jal	42026300 <__wrap_esp_audio_simple_dec_open>
42010b60:	842a                	mv	s0,a0
42010b62:	78050c63          	beqz	a0,420112fa <decoder_task+0x95c>
42010b66:	fe378097          	auipc	ra,0xfe378
42010b6a:	854080e7          	jalr	-1964(ra) # 403883ba <esp_log_timestamp>
42010b6e:	3c1267b7          	lui	a5,0x3c126
42010b72:	4985                	li	s3,1
42010b74:	86aa                	mv	a3,a0
42010b76:	89878793          	addi	a5,a5,-1896 # 3c125898 <_esp_trace_encoder_array_end+0x5778>
42010b7a:	093b19e3          	bne	s6,s3,4201140c <decoder_task+0xa6e>
42010b7e:	3c126737          	lui	a4,0x3c126
42010b82:	8a470713          	addi	a4,a4,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
42010b86:	3c126637          	lui	a2,0x3c126
42010b8a:	85ba                	mv	a1,a4
42010b8c:	8822                	mv	a6,s0
42010b8e:	b5c60613          	addi	a2,a2,-1188 # 3c125b5c <_esp_trace_encoder_array_end+0x5a3c>
42010b92:	4505                	li	a0,1
42010b94:	fe377097          	auipc	ra,0xfe377
42010b98:	71e080e7          	jalr	1822(ra) # 403882b2 <esp_log>
42010b9c:	3c126737          	lui	a4,0x3c126
42010ba0:	57f9                	li	a5,-2
42010ba2:	a9470693          	addi	a3,a4,-1388 # 3c125a94 <_esp_trace_encoder_array_end+0x5974>
42010ba6:	28f402e3          	beq	s0,a5,4201162a <decoder_task+0xc8c>
42010baa:	3fc957b7          	lui	a5,0x3fc95
42010bae:	d047a503          	lw	a0,-764(a5) # 3fc94d04 <s_state>
42010bb2:	4601                	li	a2,0
42010bb4:	85a6                	mv	a1,s1
42010bb6:	76e040ef          	jal	42015324 <native_state_set_audio>
42010bba:	4572                	lw	a0,28(sp)
42010bbc:	c501                	beqz	a0,42010bc4 <decoder_task+0x226>
42010bbe:	401260ef          	jal	420377be <esp_audio_simple_dec_close>
42010bc2:	ce02                	sw	zero,28(sp)
42010bc4:	854a                	mv	a0,s2
42010bc6:	a8df70ef          	jal	42008652 <cfree>
42010bca:	8c26                	mv	s8,s1
42010bcc:	4a01                	li	s4,0
42010bce:	4901                	li	s2,0
42010bd0:	4b81                	li	s7,0
42010bd2:	4d81                	li	s11,0
42010bd4:	3fc957b7          	lui	a5,0x3fc95
42010bd8:	cfc7a503          	lw	a0,-772(a5) # 3fc94cfc <s_encoded>
42010bdc:	85e6                	mv	a1,s9
42010bde:	4981                	li	s3,0
42010be0:	740660ef          	jal	42077320 <vRingbufferReturnItem>
42010be4:	4401                	li	s0,0
42010be6:	b525                	j	42010a0e <decoder_task+0x70>
42010be8:	3a3010ef          	jal	4201278a <decoder_register_codecs>
42010bec:	842a                	mv	s0,a0
42010bee:	28051063          	bnez	a0,42010e6e <decoder_task+0x4d0>
42010bf2:	000ca783          	lw	a5,0(s9)
42010bf6:	ec9798e3          	bne	a5,s1,42010ac6 <decoder_task+0x128>
42010bfa:	004ca783          	lw	a5,4(s9)
42010bfe:	ed6794e3          	bne	a5,s6,42010ac6 <decoder_task+0x128>
42010c02:	478d                	li	a5,3
42010c04:	78fb0b63          	beq	s6,a5,4201139a <decoder_task+0x9fc>
42010c08:	47f2                	lw	a5,28(sp)
42010c0a:	00f9e7b3          	or	a5,s3,a5
42010c0e:	d3f9                	beqz	a5,42010bd4 <decoder_task+0x236>
42010c10:	008cd783          	lhu	a5,8(s9)
42010c14:	00bc8713          	addi	a4,s9,11
42010c18:	ce82                	sw	zero,92(sp)
42010c1a:	d082                	sw	zero,96(sp)
42010c1c:	d282                	sw	zero,100(sp)
42010c1e:	ccbe                	sw	a5,88(sp)
42010c20:	caba                	sw	a4,84(sp)
42010c22:	00acc703          	lbu	a4,10(s9)
42010c26:	ffeb0693          	addi	a3,s6,-2
42010c2a:	0016b693          	seqz	a3,a3
42010c2e:	00e03733          	snez	a4,a4
42010c32:	c036                	sw	a3,0(sp)
42010c34:	04e10e23          	sb	a4,92(sp)
42010c38:	3a098063          	beqz	s3,42010fd8 <decoder_task+0x63a>
42010c3c:	e789                	bnez	a5,42010c46 <decoder_task+0x2a8>
42010c3e:	05c14783          	lbu	a5,92(sp)
42010c42:	1c078a63          	beqz	a5,42010e16 <decoder_task+0x478>
42010c46:	4781                	li	a5,0
42010c48:	4801                	li	a6,0
42010c4a:	de3e                	sw	a5,60(sp)
42010c4c:	c0c2                	sw	a6,64(sp)
42010c4e:	da4a                	sw	s2,52(sp)
42010c50:	dc52                	sw	s4,56(sp)
42010c52:	d082                	sw	zero,96(sp)
42010c54:	fe370097          	auipc	ra,0xfe370
42010c58:	6e6080e7          	jalr	1766(ra) # 4038133a <esp_timer_get_time>
42010c5c:	842a                	mv	s0,a0
42010c5e:	1850                	addi	a2,sp,52
42010c60:	08cc                	addi	a1,sp,84
42010c62:	854e                	mv	a0,s3
42010c64:	3bf010ef          	jal	42012822 <native_aac_decoder_process>
42010c68:	8d2a                	mv	s10,a0
42010c6a:	fe370097          	auipc	ra,0xfe370
42010c6e:	6d0080e7          	jalr	1744(ra) # 4038133a <esp_timer_get_time>
42010c72:	47ca                	lw	a5,144(sp)
42010c74:	46da                	lw	a3,148(sp)
42010c76:	8d01                	sub	a0,a0,s0
42010c78:	00a78733          	add	a4,a5,a0
42010c7c:	00f737b3          	sltu	a5,a4,a5
42010c80:	97b6                	add	a5,a5,a3
42010c82:	cb3e                	sw	a5,148(sp)
42010c84:	578a                	lw	a5,160(sp)
42010c86:	c93a                	sw	a4,144(sp)
42010c88:	571a                	lw	a4,164(sp)
42010c8a:	0785                	addi	a5,a5,1
42010c8c:	d13e                	sw	a5,160(sp)
42010c8e:	00a77363          	bgeu	a4,a0,42010c94 <decoder_task+0x2f6>
42010c92:	d32a                	sw	a0,164(sp)
42010c94:	8bfd                	andi	a5,a5,31
42010c96:	56078363          	beqz	a5,420111fc <decoder_task+0x85e>
42010c9a:	cf0a8793          	addi	a5,s5,-784
42010c9e:	0330000f          	fence	rw,rw
42010ca2:	439c                	lw	a5,0(a5)
42010ca4:	0230000f          	fence	r,rw
42010ca8:	16979763          	bne	a5,s1,42010e16 <decoder_task+0x478>
42010cac:	57e1                	li	a5,-8
42010cae:	52fd0163          	beq	s10,a5,420111d0 <decoder_task+0x832>
42010cb2:	580d1c63          	bnez	s10,4201124a <decoder_task+0x8ac>
42010cb6:	5786                	lw	a5,96(sp)
42010cb8:	4766                	lw	a4,88(sp)
42010cba:	6ef76363          	bltu	a4,a5,420113a0 <decoder_task+0xa02>
42010cbe:	8f1d                	sub	a4,a4,a5
42010cc0:	56aa                	lw	a3,168(sp)
42010cc2:	ccba                	sw	a4,88(sp)
42010cc4:	4756                	lw	a4,84(sp)
42010cc6:	96be                	add	a3,a3,a5
42010cc8:	d536                	sw	a3,168(sp)
42010cca:	97ba                	add	a5,a5,a4
42010ccc:	4706                	lw	a4,64(sp)
42010cce:	cabe                	sw	a5,84(sp)
42010cd0:	10070c63          	beqz	a4,42010de8 <decoder_task+0x44a>
42010cd4:	00cc                	addi	a1,sp,68
42010cd6:	854e                	mv	a0,s3
42010cd8:	c282                	sw	zero,68(sp)
42010cda:	c482                	sw	zero,72(sp)
42010cdc:	c682                	sw	zero,76(sp)
42010cde:	c882                	sw	zero,80(sp)
42010ce0:	66b010ef          	jal	42012b4a <native_aac_decoder_get_info>
42010ce4:	52051063          	bnez	a0,42011204 <decoder_task+0x866>
42010ce8:	4782                	lw	a5,0(sp)
42010cea:	01b10613          	addi	a2,sp,27
42010cee:	00cc                	addi	a1,sp,68
42010cf0:	854e                	mv	a0,s3
42010cf2:	00f10da3          	sb	a5,27(sp)
42010cf6:	663010ef          	jal	42012b58 <native_aac_decoder_label>
42010cfa:	01b14683          	lbu	a3,27(sp)
42010cfe:	842a                	mv	s0,a0
42010d00:	4501                	li	a0,0
42010d02:	5c068863          	beqz	a3,420112d2 <decoder_task+0x934>
42010d06:	cf0a8793          	addi	a5,s5,-784
42010d0a:	0330000f          	fence	rw,rw
42010d0e:	4398                	lw	a4,0(a5)
42010d10:	0230000f          	fence	r,rw
42010d14:	4781                	li	a5,0
42010d16:	06971163          	bne	a4,s1,42010d78 <decoder_task+0x3da>
42010d1a:	4716                	lw	a4,68(sp)
42010d1c:	cf31                	beqz	a4,42010d78 <decoder_task+0x3da>
42010d1e:	04914803          	lbu	a6,73(sp)
42010d22:	04080b63          	beqz	a6,42010d78 <decoder_task+0x3da>
42010d26:	04814603          	lbu	a2,72(sp)
42010d2a:	c639                	beqz	a2,42010d78 <decoder_task+0x3da>
42010d2c:	45a6                	lw	a1,72(sp)
42010d2e:	47b6                	lw	a5,76(sp)
42010d30:	d23a                	sw	a4,36(sp)
42010d32:	d42e                	sw	a1,40(sp)
42010d34:	45c6                	lw	a1,80(sp)
42010d36:	d63e                	sw	a5,44(sp)
42010d38:	4785                	li	a5,1
42010d3a:	06012923          	sw	zero,114(sp)
42010d3e:	06012b23          	sw	zero,118(sp)
42010d42:	06011d23          	sh	zero,122(sp)
42010d46:	d4a2                	sw	s0,104(sp)
42010d48:	d6ba                	sw	a4,108(sp)
42010d4a:	d82e                	sw	a1,48(sp)
42010d4c:	00f10d23          	sb	a5,26(sp)
42010d50:	6a050c63          	beqz	a0,42011408 <decoder_task+0xa6a>
42010d54:	3fc957b7          	lui	a5,0x3fc95
42010d58:	06a10823          	sb	a0,112(sp)
42010d5c:	d047a503          	lw	a0,-764(a5) # 3fc94d04 <s_state>
42010d60:	06c108a3          	sb	a2,113(sp)
42010d64:	85a6                	mv	a1,s1
42010d66:	10b0                	addi	a2,sp,104
42010d68:	daba                	sw	a4,116(sp)
42010d6a:	07010c23          	sb	a6,120(sp)
42010d6e:	06d10d23          	sb	a3,122(sp)
42010d72:	692040ef          	jal	42015404 <native_state_set_stream_info>
42010d76:	4785                	li	a5,1
42010d78:	45b6                	lw	a1,76(sp)
42010d7a:	8526                	mv	a0,s1
42010d7c:	00f10d23          	sb	a5,26(sp)
42010d80:	fe2ff0ef          	jal	42010562 <state_set_decoder_bitrate>
42010d84:	01a14783          	lbu	a5,26(sp)
42010d88:	c3a5                	beqz	a5,42010de8 <decoder_task+0x44a>
42010d8a:	4a0d8963          	beqz	s11,4201123c <decoder_task+0x89e>
42010d8e:	02814503          	lbu	a0,40(sp)
42010d92:	02914783          	lbu	a5,41(sp)
42010d96:	4406                	lw	s0,64(sp)
42010d98:	051d                	addi	a0,a0,7
42010d9a:	810d                	srli	a0,a0,0x3
42010d9c:	02f50533          	mul	a0,a0,a5
42010da0:	c91d                	beqz	a0,42010dd6 <decoder_task+0x438>
42010da2:	5612                	lw	a2,36(sp)
42010da4:	ca0d                	beqz	a2,42010dd6 <decoder_task+0x438>
42010da6:	02a45533          	divu	a0,s0,a0
42010daa:	47a2                	lw	a5,8(sp)
42010dac:	4681                	li	a3,0
42010dae:	02f535b3          	mulhu	a1,a0,a5
42010db2:	02f50533          	mul	a0,a0,a5
42010db6:	fdff0097          	auipc	ra,0xfdff0
42010dba:	af6080e7          	jalr	-1290(ra) # 400008ac <__udivdi3>
42010dbe:	47ea                	lw	a5,152(sp)
42010dc0:	46fa                	lw	a3,156(sp)
42010dc2:	573a                	lw	a4,172(sp)
42010dc4:	953e                	add	a0,a0,a5
42010dc6:	96ae                	add	a3,a3,a1
42010dc8:	00f537b3          	sltu	a5,a0,a5
42010dcc:	97b6                	add	a5,a5,a3
42010dce:	9722                	add	a4,a4,s0
42010dd0:	cf3e                	sw	a5,156(sp)
42010dd2:	cd2a                	sw	a0,152(sp)
42010dd4:	d73a                	sw	a4,172(sp)
42010dd6:	86a2                	mv	a3,s0
42010dd8:	864a                	mv	a2,s2
42010dda:	104c                	addi	a1,sp,36
42010ddc:	8526                	mv	a0,s1
42010dde:	e48ff0ef          	jal	42010426 <send_pcm>
42010de2:	8daa                	mv	s11,a0
42010de4:	72050c63          	beqz	a0,4201151c <decoder_task+0xb7e>
42010de8:	fe370097          	auipc	ra,0xfe370
42010dec:	552080e7          	jalr	1362(ra) # 4038133a <esp_timer_get_time>
42010df0:	862e                	mv	a2,a1
42010df2:	85aa                	mv	a1,a0
42010df4:	0108                	addi	a0,sp,128
42010df6:	9b2ff0ef          	jal	4200ffa8 <decode_stats_report>
42010dfa:	4706                	lw	a4,64(sp)
42010dfc:	5786                	lw	a5,96(sp)
42010dfe:	05c14683          	lbu	a3,92(sp)
42010e02:	8fd9                	or	a5,a5,a4
42010e04:	3c079063          	bnez	a5,420111c4 <decoder_task+0x826>
42010e08:	76068063          	beqz	a3,42011568 <decoder_task+0xbca>
42010e0c:	4701                	li	a4,0
42010e0e:	47e6                	lw	a5,88(sp)
42010e10:	8f5d                	or	a4,a4,a5
42010e12:	e20715e3          	bnez	a4,42010c3c <decoder_task+0x29e>
42010e16:	00acc783          	lbu	a5,10(s9)
42010e1a:	48079b63          	bnez	a5,420112b0 <decoder_task+0x912>
42010e1e:	489c0963          	beq	s8,s1,420112b0 <decoder_task+0x912>
42010e22:	8566                	mv	a0,s9
42010e24:	85e2                	mv	a1,s8
42010e26:	ab1ff0ef          	jal	420108d6 <return_decoded_packet>
42010e2a:	4401                	li	s0,0
42010e2c:	1ed150ef          	jal	42026818 <rx_buffer_diagnostic_poll>
42010e30:	cf0a8793          	addi	a5,s5,-784
42010e34:	0330000f          	fence	rw,rw
42010e38:	0007ac83          	lw	s9,0(a5)
42010e3c:	0230000f          	fence	r,rw
42010e40:	be9c93e3          	bne	s9,s1,42010a26 <decoder_task+0x88>
42010e44:	c20c0fe3          	beqz	s8,42010a82 <decoder_task+0xe4>
42010e48:	c29c1de3          	bne	s8,s1,42010a82 <decoder_task+0xe4>
42010e4c:	4572                	lw	a0,28(sp)
42010e4e:	c119                	beqz	a0,42010e54 <decoder_task+0x4b6>
42010e50:	16f260ef          	jal	420377be <esp_audio_simple_dec_close>
42010e54:	ce02                	sw	zero,28(sp)
42010e56:	00098563          	beqz	s3,42010e60 <decoder_task+0x4c2>
42010e5a:	854e                	mv	a0,s3
42010e5c:	191010ef          	jal	420127ec <native_aac_decoder_destroy>
42010e60:	854a                	mv	a0,s2
42010e62:	ff0f70ef          	jal	42008652 <cfree>
42010e66:	4981                	li	s3,0
42010e68:	4a01                	li	s4,0
42010e6a:	4901                	li	s2,0
42010e6c:	b919                	j	42010a82 <decoder_task+0xe4>
42010e6e:	fe377097          	auipc	ra,0xfe377
42010e72:	54c080e7          	jalr	1356(ra) # 403883ba <esp_log_timestamp>
42010e76:	3c126737          	lui	a4,0x3c126
42010e7a:	8a470713          	addi	a4,a4,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
42010e7e:	3c126637          	lui	a2,0x3c126
42010e82:	86aa                	mv	a3,a0
42010e84:	85ba                	mv	a1,a4
42010e86:	87a2                	mv	a5,s0
42010e88:	ab460613          	addi	a2,a2,-1356 # 3c125ab4 <_esp_trace_encoder_array_end+0x5994>
42010e8c:	4505                	li	a0,1
42010e8e:	fe377097          	auipc	ra,0xfe377
42010e92:	424080e7          	jalr	1060(ra) # 403882b2 <esp_log>
42010e96:	3fc957b7          	lui	a5,0x3fc95
42010e9a:	d047a503          	lw	a0,-764(a5) # 3fc94d04 <s_state>
42010e9e:	000ca583          	lw	a1,0(s9)
42010ea2:	3c1267b7          	lui	a5,0x3c126
42010ea6:	ae478693          	addi	a3,a5,-1308 # 3c125ae4 <_esp_trace_encoder_array_end+0x59c4>
42010eaa:	4601                	li	a2,0
42010eac:	478040ef          	jal	42015324 <native_state_set_audio>
42010eb0:	000cac03          	lw	s8,0(s9)
42010eb4:	8566                	mv	a0,s9
42010eb6:	85e2                	mv	a1,s8
42010eb8:	a1fff0ef          	jal	420108d6 <return_decoded_packet>
42010ebc:	be89                	j	42010a0e <decoder_task+0x70>
42010ebe:	3fc957b7          	lui	a5,0x3fc95
42010ec2:	cfc7a503          	lw	a0,-772(a5) # 3fc94cfc <s_encoded>
42010ec6:	85e6                	mv	a1,s9
42010ec8:	458660ef          	jal	42077320 <vRingbufferReturnItem>
42010ecc:	b689                	j	42010a0e <decoder_task+0x70>
42010ece:	854a                	mv	a0,s2
42010ed0:	f82f70ef          	jal	42008652 <cfree>
42010ed4:	4a01                	li	s4,0
42010ed6:	4901                	li	s2,0
42010ed8:	bebd                	j	42010a56 <decoder_task+0xb8>
42010eda:	854a                	mv	a0,s2
42010edc:	f76f70ef          	jal	42008652 <cfree>
42010ee0:	56a240ef          	jal	4203544a <custom_flac_decoder_create>
42010ee4:	8baa                	mv	s7,a0
42010ee6:	5a050863          	beqz	a0,42011496 <decoder_task+0xaf8>
42010eea:	4981                	li	s3,0
42010eec:	4a01                	li	s4,0
42010eee:	4901                	li	s2,0
42010ef0:	4d81                	li	s11,0
42010ef2:	4661                	li	a2,24
42010ef4:	4581                	li	a1,0
42010ef6:	10a8                	addi	a0,sp,104
42010ef8:	fdfef097          	auipc	ra,0xfdfef
42010efc:	45c080e7          	jalr	1116(ra) # 40000354 <memset>
42010f00:	011c                	addi	a5,sp,128
42010f02:	ccbe                	sw	a5,88(sp)
42010f04:	105c                	addi	a5,sp,36
42010f06:	cebe                	sw	a5,92(sp)
42010f08:	01a10793          	addi	a5,sp,26
42010f0c:	d0be                	sw	a5,96(sp)
42010f0e:	caa6                	sw	s1,84(sp)
42010f10:	00acc683          	lbu	a3,10(s9)
42010f14:	008cd603          	lhu	a2,8(s9)
42010f18:	42011737          	lui	a4,0x42011
42010f1c:	00d036b3          	snez	a3,a3
42010f20:	08dc                	addi	a5,sp,84
42010f22:	65470713          	addi	a4,a4,1620 # 42011654 <custom_flac_output>
42010f26:	00bc8593          	addi	a1,s9,11
42010f2a:	06810813          	addi	a6,sp,104
42010f2e:	855e                	mv	a0,s7
42010f30:	5a0240ef          	jal	420354d0 <custom_flac_decoder_feed>
42010f34:	47ca                	lw	a5,144(sp)
42010f36:	5726                	lw	a4,104(sp)
42010f38:	465a                	lw	a2,148(sp)
42010f3a:	55b6                	lw	a1,108(sp)
42010f3c:	568a                	lw	a3,160(sp)
42010f3e:	973e                	add	a4,a4,a5
42010f40:	842a                	mv	s0,a0
42010f42:	5546                	lw	a0,112(sp)
42010f44:	962e                	add	a2,a2,a1
42010f46:	00f737b3          	sltu	a5,a4,a5
42010f4a:	97b2                	add	a5,a5,a2
42010f4c:	55d6                	lw	a1,116(sp)
42010f4e:	561a                	lw	a2,164(sp)
42010f50:	96aa                	add	a3,a3,a0
42010f52:	c93a                	sw	a4,144(sp)
42010f54:	cb3e                	sw	a5,148(sp)
42010f56:	d136                	sw	a3,160(sp)
42010f58:	00b67363          	bgeu	a2,a1,42010f5e <decoder_task+0x5c0>
42010f5c:	d32e                	sw	a1,164(sp)
42010f5e:	57aa                	lw	a5,168(sp)
42010f60:	5766                	lw	a4,120(sp)
42010f62:	97ba                	add	a5,a5,a4
42010f64:	d53e                	sw	a5,168(sp)
42010f66:	4a0d8963          	beqz	s11,42011418 <decoder_task+0xa7a>
42010f6a:	4d85                	li	s11,1
42010f6c:	fe370097          	auipc	ra,0xfe370
42010f70:	3ce080e7          	jalr	974(ra) # 4038133a <esp_timer_get_time>
42010f74:	862e                	mv	a2,a1
42010f76:	85aa                	mv	a1,a0
42010f78:	0108                	addi	a0,sp,128
42010f7a:	82eff0ef          	jal	4200ffa8 <decode_stats_report>
42010f7e:	00045b63          	bgez	s0,42010f94 <decoder_task+0x5f6>
42010f82:	cf0a8793          	addi	a5,s5,-784
42010f86:	0330000f          	fence	rw,rw
42010f8a:	439c                	lw	a5,0(a5)
42010f8c:	0230000f          	fence	r,rw
42010f90:	62978e63          	beq	a5,s1,420115cc <decoder_task+0xc2e>
42010f94:	8566                	mv	a0,s9
42010f96:	85e2                	mv	a1,s8
42010f98:	93fff0ef          	jal	420108d6 <return_decoded_packet>
42010f9c:	4b0d                	li	s6,3
42010f9e:	4401                	li	s0,0
42010fa0:	b4bd                	j	42010a0e <decoder_task+0x70>
42010fa2:	6589                	lui	a1,0x2
42010fa4:	36ba0263          	beq	s4,a1,42011308 <decoder_task+0x96a>
42010fa8:	854a                	mv	a0,s2
42010faa:	ea4f70ef          	jal	4200864e <realloc>
42010fae:	842a                	mv	s0,a0
42010fb0:	68050863          	beqz	a0,42011640 <decoder_task+0xca2>
42010fb4:	204347b7          	lui	a5,0x20434
42010fb8:	14178793          	addi	a5,a5,321 # 20434141 <CSR_UINTSTATUS+0x20433490>
42010fbc:	d682                	sw	zero,108(sp)
42010fbe:	d882                	sw	zero,112(sp)
42010fc0:	da82                	sw	zero,116(sp)
42010fc2:	d4be                	sw	a5,104(sp)
42010fc4:	7fc010ef          	jal	420127c0 <native_aac_decoder_create>
42010fc8:	89aa                	mv	s3,a0
42010fca:	46050763          	beqz	a0,42011438 <decoder_task+0xa9a>
42010fce:	8922                	mv	s2,s0
42010fd0:	6a09                	lui	s4,0x2
42010fd2:	4b81                	li	s7,0
42010fd4:	4d81                	li	s11,0
42010fd6:	b92d                	j	42010c10 <decoder_task+0x272>
42010fd8:	5d61                	li	s10,-8
42010fda:	c662                	sw	s8,12(sp)
42010fdc:	e789                	bnez	a5,42010fe6 <decoder_task+0x648>
42010fde:	05c14783          	lbu	a5,92(sp)
42010fe2:	1c078f63          	beqz	a5,420111c0 <decoder_task+0x822>
42010fe6:	4781                	li	a5,0
42010fe8:	4801                	li	a6,0
42010fea:	de3e                	sw	a5,60(sp)
42010fec:	c0c2                	sw	a6,64(sp)
42010fee:	da4a                	sw	s2,52(sp)
42010ff0:	dc52                	sw	s4,56(sp)
42010ff2:	d082                	sw	zero,96(sp)
42010ff4:	fe370097          	auipc	ra,0xfe370
42010ff8:	346080e7          	jalr	838(ra) # 4038133a <esp_timer_get_time>
42010ffc:	842a                	mv	s0,a0
42010ffe:	4572                	lw	a0,28(sp)
42011000:	1850                	addi	a2,sp,52
42011002:	08cc                	addi	a1,sp,84
42011004:	488150ef          	jal	4202648c <__wrap_esp_audio_simple_dec_process>
42011008:	8c2a                	mv	s8,a0
4201100a:	fe370097          	auipc	ra,0xfe370
4201100e:	330080e7          	jalr	816(ra) # 4038133a <esp_timer_get_time>
42011012:	47ca                	lw	a5,144(sp)
42011014:	46da                	lw	a3,148(sp)
42011016:	8d01                	sub	a0,a0,s0
42011018:	00a78733          	add	a4,a5,a0
4201101c:	00f737b3          	sltu	a5,a4,a5
42011020:	97b6                	add	a5,a5,a3
42011022:	cb3e                	sw	a5,148(sp)
42011024:	578a                	lw	a5,160(sp)
42011026:	c93a                	sw	a4,144(sp)
42011028:	571a                	lw	a4,164(sp)
4201102a:	0785                	addi	a5,a5,1
4201102c:	d13e                	sw	a5,160(sp)
4201102e:	00a77363          	bgeu	a4,a0,42011034 <decoder_task+0x696>
42011032:	d32a                	sw	a0,164(sp)
42011034:	8bfd                	andi	a5,a5,31
42011036:	1e078c63          	beqz	a5,4201122e <decoder_task+0x890>
4201103a:	cf0a8793          	addi	a5,s5,-784
4201103e:	0330000f          	fence	rw,rw
42011042:	439c                	lw	a5,0(a5)
42011044:	0230000f          	fence	r,rw
42011048:	16979c63          	bne	a5,s1,420111c0 <decoder_task+0x822>
4201104c:	1dac0563          	beq	s8,s10,42011216 <decoder_task+0x878>
42011050:	4e0c1b63          	bnez	s8,42011546 <decoder_task+0xba8>
42011054:	5786                	lw	a5,96(sp)
42011056:	4766                	lw	a4,88(sp)
42011058:	34f76463          	bltu	a4,a5,420113a0 <decoder_task+0xa02>
4201105c:	8f1d                	sub	a4,a4,a5
4201105e:	56aa                	lw	a3,168(sp)
42011060:	ccba                	sw	a4,88(sp)
42011062:	4756                	lw	a4,84(sp)
42011064:	96be                	add	a3,a3,a5
42011066:	d536                	sw	a3,168(sp)
42011068:	97ba                	add	a5,a5,a4
4201106a:	4706                	lw	a4,64(sp)
4201106c:	cabe                	sw	a5,84(sp)
4201106e:	12070363          	beqz	a4,42011194 <decoder_task+0x7f6>
42011072:	4572                	lw	a0,28(sp)
42011074:	00cc                	addi	a1,sp,68
42011076:	c282                	sw	zero,68(sp)
42011078:	c482                	sw	zero,72(sp)
4201107a:	c682                	sw	zero,76(sp)
4201107c:	c882                	sw	zero,80(sp)
4201107e:	6c8260ef          	jal	42037746 <esp_audio_simple_dec_get_info>
42011082:	1a051a63          	bnez	a0,42011236 <decoder_task+0x898>
42011086:	4782                	lw	a5,0(sp)
42011088:	00f10da3          	sb	a5,27(sp)
4201108c:	4789                	li	a5,2
4201108e:	44fb0e63          	beq	s6,a5,420114ea <decoder_task+0xb4c>
42011092:	4791                	li	a5,4
42011094:	44fb0663          	beq	s6,a5,420114e0 <decoder_task+0xb42>
42011098:	3c126737          	lui	a4,0x3c126
4201109c:	4785                	li	a5,1
4201109e:	89870593          	addi	a1,a4,-1896 # 3c125898 <_esp_trace_encoder_array_end+0x5778>
420110a2:	38fb1663          	bne	s6,a5,4201142e <decoder_task+0xa90>
420110a6:	cf0a8793          	addi	a5,s5,-784
420110aa:	0330000f          	fence	rw,rw
420110ae:	439c                	lw	a5,0(a5)
420110b0:	0230000f          	fence	r,rw
420110b4:	06979463          	bne	a5,s1,4201111c <decoder_task+0x77e>
420110b8:	4796                	lw	a5,68(sp)
420110ba:	c3b5                	beqz	a5,4201111e <decoder_task+0x780>
420110bc:	04914683          	lbu	a3,73(sp)
420110c0:	ceb1                	beqz	a3,4201111c <decoder_task+0x77e>
420110c2:	04815703          	lhu	a4,72(sp)
420110c6:	04814503          	lbu	a0,72(sp)
420110ca:	00875613          	srli	a2,a4,0x8
420110ce:	0722                	slli	a4,a4,0x8
420110d0:	963a                	add	a2,a2,a4
420110d2:	c529                	beqz	a0,4201111c <decoder_task+0x77e>
420110d4:	06012b23          	sw	zero,118(sp)
420110d8:	06012923          	sw	zero,114(sp)
420110dc:	d23e                	sw	a5,36(sp)
420110de:	06c11823          	sh	a2,112(sp)
420110e2:	d6be                	sw	a5,108(sp)
420110e4:	4626                	lw	a2,72(sp)
420110e6:	dabe                	sw	a5,116(sp)
420110e8:	3fc957b7          	lui	a5,0x3fc95
420110ec:	4746                	lw	a4,80(sp)
420110ee:	d047a503          	lw	a0,-764(a5) # 3fc94d04 <s_state>
420110f2:	06d10c23          	sb	a3,120(sp)
420110f6:	4782                	lw	a5,0(sp)
420110f8:	46b6                	lw	a3,76(sp)
420110fa:	06011d23          	sh	zero,122(sp)
420110fe:	d4ae                	sw	a1,104(sp)
42011100:	d432                	sw	a2,40(sp)
42011102:	4405                	li	s0,1
42011104:	10b0                	addi	a2,sp,104
42011106:	85a6                	mv	a1,s1
42011108:	06f10d23          	sb	a5,122(sp)
4201110c:	d636                	sw	a3,44(sp)
4201110e:	d83a                	sw	a4,48(sp)
42011110:	00810d23          	sb	s0,26(sp)
42011114:	2f0040ef          	jal	42015404 <native_state_set_stream_info>
42011118:	87a2                	mv	a5,s0
4201111a:	a011                	j	4201111e <decoder_task+0x780>
4201111c:	4781                	li	a5,0
4201111e:	45b6                	lw	a1,76(sp)
42011120:	8526                	mv	a0,s1
42011122:	00f10d23          	sb	a5,26(sp)
42011126:	c3cff0ef          	jal	42010562 <state_set_decoder_bitrate>
4201112a:	01a14783          	lbu	a5,26(sp)
4201112e:	c3bd                	beqz	a5,42011194 <decoder_task+0x7f6>
42011130:	1c0d8e63          	beqz	s11,4201130c <decoder_task+0x96e>
42011134:	02814503          	lbu	a0,40(sp)
42011138:	02914783          	lbu	a5,41(sp)
4201113c:	4406                	lw	s0,64(sp)
4201113e:	051d                	addi	a0,a0,7
42011140:	810d                	srli	a0,a0,0x3
42011142:	02f50533          	mul	a0,a0,a5
42011146:	cd15                	beqz	a0,42011182 <decoder_task+0x7e4>
42011148:	5612                	lw	a2,36(sp)
4201114a:	ce05                	beqz	a2,42011182 <decoder_task+0x7e4>
4201114c:	02a45533          	divu	a0,s0,a0
42011150:	000f47b7          	lui	a5,0xf4
42011154:	24078793          	addi	a5,a5,576 # f4240 <CSR_UINTSTATUS+0xf358f>
42011158:	4681                	li	a3,0
4201115a:	02f535b3          	mulhu	a1,a0,a5
4201115e:	02f50533          	mul	a0,a0,a5
42011162:	fdfef097          	auipc	ra,0xfdfef
42011166:	74a080e7          	jalr	1866(ra) # 400008ac <__udivdi3>
4201116a:	47ea                	lw	a5,152(sp)
4201116c:	46fa                	lw	a3,156(sp)
4201116e:	573a                	lw	a4,172(sp)
42011170:	953e                	add	a0,a0,a5
42011172:	96ae                	add	a3,a3,a1
42011174:	00f537b3          	sltu	a5,a0,a5
42011178:	97b6                	add	a5,a5,a3
4201117a:	9722                	add	a4,a4,s0
4201117c:	cf3e                	sw	a5,156(sp)
4201117e:	cd2a                	sw	a0,152(sp)
42011180:	d73a                	sw	a4,172(sp)
42011182:	86a2                	mv	a3,s0
42011184:	864a                	mv	a2,s2
42011186:	104c                	addi	a1,sp,36
42011188:	8526                	mv	a0,s1
4201118a:	a9cff0ef          	jal	42010426 <send_pcm>
4201118e:	8daa                	mv	s11,a0
42011190:	38050563          	beqz	a0,4201151a <decoder_task+0xb7c>
42011194:	fe370097          	auipc	ra,0xfe370
42011198:	1a6080e7          	jalr	422(ra) # 4038133a <esp_timer_get_time>
4201119c:	862e                	mv	a2,a1
4201119e:	85aa                	mv	a1,a0
420111a0:	0108                	addi	a0,sp,128
420111a2:	e07fe0ef          	jal	4200ffa8 <decode_stats_report>
420111a6:	4706                	lw	a4,64(sp)
420111a8:	5786                	lw	a5,96(sp)
420111aa:	05c14683          	lbu	a3,92(sp)
420111ae:	8fd9                	or	a5,a5,a4
420111b0:	efa9                	bnez	a5,4201120a <decoder_task+0x86c>
420111b2:	3a068b63          	beqz	a3,42011568 <decoder_task+0xbca>
420111b6:	4701                	li	a4,0
420111b8:	47e6                	lw	a5,88(sp)
420111ba:	8f5d                	or	a4,a4,a5
420111bc:	e20710e3          	bnez	a4,42010fdc <decoder_task+0x63e>
420111c0:	4c32                	lw	s8,12(sp)
420111c2:	b991                	j	42010e16 <decoder_task+0x478>
420111c4:	c40695e3          	bnez	a3,42010e0e <decoder_task+0x470>
420111c8:	47e6                	lw	a5,88(sp)
420111ca:	a6079ee3          	bnez	a5,42010c46 <decoder_task+0x2a8>
420111ce:	b1a1                	j	42010e16 <decoder_task+0x478>
420111d0:	5706                	lw	a4,96(sp)
420111d2:	47d6                	lw	a5,84(sp)
420111d4:	56aa                	lw	a3,168(sp)
420111d6:	5472                	lw	s0,60(sp)
420111d8:	97ba                	add	a5,a5,a4
420111da:	cabe                	sw	a5,84(sp)
420111dc:	47e6                	lw	a5,88(sp)
420111de:	96ba                	add	a3,a3,a4
420111e0:	d536                	sw	a3,168(sp)
420111e2:	8f99                	sub	a5,a5,a4
420111e4:	ccbe                	sw	a5,88(sp)
420111e6:	308a7763          	bgeu	s4,s0,420114f4 <decoder_task+0xb56>
420111ea:	85a2                	mv	a1,s0
420111ec:	854a                	mv	a0,s2
420111ee:	c60f70ef          	jal	4200864e <realloc>
420111f2:	30050163          	beqz	a0,420114f4 <decoder_task+0xb56>
420111f6:	8a22                	mv	s4,s0
420111f8:	892a                	mv	s2,a0
420111fa:	b4b1                	j	42010c46 <decoder_task+0x2a8>
420111fc:	4505                	li	a0,1
420111fe:	703ff0ef          	jal	42111100 <vTaskDelay>
42011202:	bc61                	j	42010c9a <decoder_task+0x2fc>
42011204:	00010d23          	sb	zero,26(sp)
42011208:	b6c5                	j	42010de8 <decoder_task+0x44a>
4201120a:	f6dd                	bnez	a3,420111b8 <decoder_task+0x81a>
4201120c:	47e6                	lw	a5,88(sp)
4201120e:	dc079ce3          	bnez	a5,42010fe6 <decoder_task+0x648>
42011212:	4c32                	lw	s8,12(sp)
42011214:	b109                	j	42010e16 <decoder_task+0x478>
42011216:	5472                	lw	s0,60(sp)
42011218:	2c8a7e63          	bgeu	s4,s0,420114f4 <decoder_task+0xb56>
4201121c:	85a2                	mv	a1,s0
4201121e:	854a                	mv	a0,s2
42011220:	c2ef70ef          	jal	4200864e <realloc>
42011224:	2c050863          	beqz	a0,420114f4 <decoder_task+0xb56>
42011228:	892a                	mv	s2,a0
4201122a:	8a22                	mv	s4,s0
4201122c:	bb6d                	j	42010fe6 <decoder_task+0x648>
4201122e:	4505                	li	a0,1
42011230:	6d1ff0ef          	jal	42111100 <vTaskDelay>
42011234:	b519                	j	4201103a <decoder_task+0x69c>
42011236:	00010d23          	sb	zero,26(sp)
4201123a:	bfa9                	j	42011194 <decoder_task+0x7f6>
4201123c:	3c1267b7          	lui	a5,0x3c126
42011240:	bc878513          	addi	a0,a5,-1080 # 3c125bc8 <_esp_trace_encoder_array_end+0x5aa8>
42011244:	97eff0ef          	jal	420103c2 <log_runtime_memory>
42011248:	b699                	j	42010d8e <decoder_task+0x3f0>
4201124a:	846a                	mv	s0,s10
4201124c:	4a09                	li	s4,2
4201124e:	fe377097          	auipc	ra,0xfe377
42011252:	16c080e7          	jalr	364(ra) # 403883ba <esp_log_timestamp>
42011256:	2f4b0a63          	beq	s6,s4,4201154a <decoder_task+0xbac>
4201125a:	4791                	li	a5,4
4201125c:	2efb0c63          	beq	s6,a5,42011554 <decoder_task+0xbb6>
42011260:	3c1267b7          	lui	a5,0x3c126
42011264:	4705                	li	a4,1
42011266:	89878793          	addi	a5,a5,-1896 # 3c125898 <_esp_trace_encoder_array_end+0x5778>
4201126a:	00eb0663          	beq	s6,a4,42011276 <decoder_task+0x8d8>
4201126e:	3c1267b7          	lui	a5,0x3c126
42011272:	89c78793          	addi	a5,a5,-1892 # 3c12589c <_esp_trace_encoder_array_end+0x577c>
42011276:	3c126737          	lui	a4,0x3c126
4201127a:	8a470713          	addi	a4,a4,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
4201127e:	3c126637          	lui	a2,0x3c126
42011282:	86aa                	mv	a3,a0
42011284:	85ba                	mv	a1,a4
42011286:	8822                	mv	a6,s0
42011288:	bfc60613          	addi	a2,a2,-1028 # 3c125bfc <_esp_trace_encoder_array_end+0x5adc>
4201128c:	4509                	li	a0,2
4201128e:	fe377097          	auipc	ra,0xfe377
42011292:	024080e7          	jalr	36(ra) # 403882b2 <esp_log>
42011296:	3fc957b7          	lui	a5,0x3fc95
4201129a:	d047a503          	lw	a0,-764(a5) # 3fc94d04 <s_state>
4201129e:	3c1267b7          	lui	a5,0x3c126
420112a2:	aa478693          	addi	a3,a5,-1372 # 3c125aa4 <_esp_trace_encoder_array_end+0x5984>
420112a6:	85a6                	mv	a1,s1
420112a8:	4601                	li	a2,0
420112aa:	07a040ef          	jal	42015324 <native_state_set_audio>
420112ae:	8c26                	mv	s8,s1
420112b0:	4572                	lw	a0,28(sp)
420112b2:	c119                	beqz	a0,420112b8 <decoder_task+0x91a>
420112b4:	50a260ef          	jal	420377be <esp_audio_simple_dec_close>
420112b8:	ce02                	sw	zero,28(sp)
420112ba:	00098563          	beqz	s3,420112c4 <decoder_task+0x926>
420112be:	854e                	mv	a0,s3
420112c0:	52c010ef          	jal	420127ec <native_aac_decoder_destroy>
420112c4:	854a                	mv	a0,s2
420112c6:	b8cf70ef          	jal	42008652 <cfree>
420112ca:	4981                	li	s3,0
420112cc:	4a01                	li	s4,0
420112ce:	4901                	li	s2,0
420112d0:	be89                	j	42010e22 <decoder_task+0x484>
420112d2:	854e                	mv	a0,s3
420112d4:	0dd010ef          	jal	42012bb0 <native_aac_decoder_source_channels>
420112d8:	01b14683          	lbu	a3,27(sp)
420112dc:	0ff57513          	zext.b	a0,a0
420112e0:	b41d                	j	42010d06 <decoder_task+0x368>
420112e2:	204747b7          	lui	a5,0x20474
420112e6:	74f78793          	addi	a5,a5,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
420112ea:	086c                	addi	a1,sp,28
420112ec:	10a8                	addi	a0,sp,104
420112ee:	d4be                	sw	a5,104(sp)
420112f0:	010150ef          	jal	42026300 <__wrap_esp_audio_simple_dec_open>
420112f4:	842a                	mv	s0,a0
420112f6:	18051063          	bnez	a0,42011476 <decoder_task+0xad8>
420112fa:	4bf2                	lw	s7,28(sp)
420112fc:	4d81                	li	s11,0
420112fe:	8c0b8be3          	beqz	s7,42010bd4 <decoder_task+0x236>
42011302:	4981                	li	s3,0
42011304:	4b81                	li	s7,0
42011306:	b229                	j	42010c10 <decoder_task+0x272>
42011308:	844a                	mv	s0,s2
4201130a:	b16d                	j	42010fb4 <decoder_task+0x616>
4201130c:	3c1267b7          	lui	a5,0x3c126
42011310:	bc878513          	addi	a0,a5,-1080 # 3c125bc8 <_esp_trace_encoder_array_end+0x5aa8>
42011314:	8aeff0ef          	jal	420103c2 <log_runtime_memory>
42011318:	bd31                	j	42011134 <decoder_task+0x796>
4201131a:	d682                	sw	zero,108(sp)
4201131c:	d882                	sw	zero,112(sp)
4201131e:	da82                	sw	zero,116(sp)
42011320:	829ff06f          	j	42010b48 <decoder_task+0x1aa>
42011324:	fe377097          	auipc	ra,0xfe377
42011328:	096080e7          	jalr	150(ra) # 403883ba <esp_log_timestamp>
4201132c:	4791                	li	a5,4
4201132e:	4405                	li	s0,1
42011330:	86aa                	mv	a3,a0
42011332:	1cfb0f63          	beq	s6,a5,42011510 <decoder_task+0xb72>
42011336:	3c1267b7          	lui	a5,0x3c126
4201133a:	89878793          	addi	a5,a5,-1896 # 3c125898 <_esp_trace_encoder_array_end+0x5778>
4201133e:	008b0663          	beq	s6,s0,4201134a <decoder_task+0x9ac>
42011342:	3c1267b7          	lui	a5,0x3c126
42011346:	89c78793          	addi	a5,a5,-1892 # 3c12589c <_esp_trace_encoder_array_end+0x577c>
4201134a:	3c126737          	lui	a4,0x3c126
4201134e:	8a470713          	addi	a4,a4,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
42011352:	3c126637          	lui	a2,0x3c126
42011356:	85ba                	mv	a1,a4
42011358:	b2c60613          	addi	a2,a2,-1236 # 3c125b2c <_esp_trace_encoder_array_end+0x5a0c>
4201135c:	4505                	li	a0,1
4201135e:	fe377097          	auipc	ra,0xfe377
42011362:	f54080e7          	jalr	-172(ra) # 403882b2 <esp_log>
42011366:	3fc957b7          	lui	a5,0x3fc95
4201136a:	d047a503          	lw	a0,-764(a5) # 3fc94d04 <s_state>
4201136e:	3c1267b7          	lui	a5,0x3c126
42011372:	a8878693          	addi	a3,a5,-1400 # 3c125a88 <_esp_trace_encoder_array_end+0x5968>
42011376:	85a6                	mv	a1,s1
42011378:	4601                	li	a2,0
4201137a:	7ab030ef          	jal	42015324 <native_state_set_audio>
4201137e:	3fc957b7          	lui	a5,0x3fc95
42011382:	cfc7a503          	lw	a0,-772(a5) # 3fc94cfc <s_encoded>
42011386:	85e6                	mv	a1,s9
42011388:	8c26                	mv	s8,s1
4201138a:	797650ef          	jal	42077320 <vRingbufferReturnItem>
4201138e:	4981                	li	s3,0
42011390:	4d81                	li	s11,0
42011392:	4b81                	li	s7,0
42011394:	4401                	li	s0,0
42011396:	e78ff06f          	j	42010a0e <decoder_task+0x70>
4201139a:	be0b8de3          	beqz	s7,42010f94 <decoder_task+0x5f6>
4201139e:	be91                	j	42010ef2 <decoder_task+0x554>
420113a0:	fe377097          	auipc	ra,0xfe377
420113a4:	01a080e7          	jalr	26(ra) # 403883ba <esp_log_timestamp>
420113a8:	4789                	li	a5,2
420113aa:	4405                	li	s0,1
420113ac:	0efb0063          	beq	s6,a5,4201148c <decoder_task+0xaee>
420113b0:	4791                	li	a5,4
420113b2:	1afb0663          	beq	s6,a5,4201155e <decoder_task+0xbc0>
420113b6:	3c1267b7          	lui	a5,0x3c126
420113ba:	89878793          	addi	a5,a5,-1896 # 3c125898 <_esp_trace_encoder_array_end+0x5778>
420113be:	008b0663          	beq	s6,s0,420113ca <decoder_task+0xa2c>
420113c2:	3c1267b7          	lui	a5,0x3c126
420113c6:	89c78793          	addi	a5,a5,-1892 # 3c12589c <_esp_trace_encoder_array_end+0x577c>
420113ca:	48e6                	lw	a7,88(sp)
420113cc:	5806                	lw	a6,96(sp)
420113ce:	3c126737          	lui	a4,0x3c126
420113d2:	8a470713          	addi	a4,a4,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
420113d6:	3c126637          	lui	a2,0x3c126
420113da:	86aa                	mv	a3,a0
420113dc:	85ba                	mv	a1,a4
420113de:	c2060613          	addi	a2,a2,-992 # 3c125c20 <_esp_trace_encoder_array_end+0x5b00>
420113e2:	4505                	li	a0,1
420113e4:	fe377097          	auipc	ra,0xfe377
420113e8:	ece080e7          	jalr	-306(ra) # 403882b2 <esp_log>
420113ec:	3fc957b7          	lui	a5,0x3fc95
420113f0:	d047a503          	lw	a0,-764(a5) # 3fc94d04 <s_state>
420113f4:	3c1267b7          	lui	a5,0x3c126
420113f8:	c5c78693          	addi	a3,a5,-932 # 3c125c5c <_esp_trace_encoder_array_end+0x5b3c>
420113fc:	85a6                	mv	a1,s1
420113fe:	4601                	li	a2,0
42011400:	725030ef          	jal	42015324 <native_state_set_audio>
42011404:	8c26                	mv	s8,s1
42011406:	b56d                	j	420112b0 <decoder_task+0x912>
42011408:	8542                	mv	a0,a6
4201140a:	b2a9                	j	42010d54 <decoder_task+0x3b6>
4201140c:	3c1267b7          	lui	a5,0x3c126
42011410:	89c78793          	addi	a5,a5,-1892 # 3c12589c <_esp_trace_encoder_array_end+0x577c>
42011414:	f6aff06f          	j	42010b7e <decoder_task+0x1e0>
42011418:	01a14d83          	lbu	s11,26(sp)
4201141c:	b40d88e3          	beqz	s11,42010f6c <decoder_task+0x5ce>
42011420:	3c1267b7          	lui	a5,0x3c126
42011424:	b8478513          	addi	a0,a5,-1148 # 3c125b84 <_esp_trace_encoder_array_end+0x5a64>
42011428:	f9bfe0ef          	jal	420103c2 <log_runtime_memory>
4201142c:	be3d                	j	42010f6a <decoder_task+0x5cc>
4201142e:	3c1267b7          	lui	a5,0x3c126
42011432:	89c78593          	addi	a1,a5,-1892 # 3c12589c <_esp_trace_encoder_array_end+0x577c>
42011436:	b985                	j	420110a6 <decoder_task+0x708>
42011438:	fe377097          	auipc	ra,0xfe377
4201143c:	f82080e7          	jalr	-126(ra) # 403883ba <esp_log_timestamp>
42011440:	3c1267b7          	lui	a5,0x3c126
42011444:	8a478713          	addi	a4,a5,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
42011448:	3c126637          	lui	a2,0x3c126
4201144c:	3c1267b7          	lui	a5,0x3c126
42011450:	86aa                	mv	a3,a0
42011452:	88878793          	addi	a5,a5,-1912 # 3c125888 <_esp_trace_encoder_array_end+0x5768>
42011456:	85ba                	mv	a1,a4
42011458:	b5c60613          	addi	a2,a2,-1188 # 3c125b5c <_esp_trace_encoder_array_end+0x5a3c>
4201145c:	5879                	li	a6,-2
4201145e:	4505                	li	a0,1
42011460:	fe377097          	auipc	ra,0xfe377
42011464:	e52080e7          	jalr	-430(ra) # 403882b2 <esp_log>
42011468:	3c1267b7          	lui	a5,0x3c126
4201146c:	8922                	mv	s2,s0
4201146e:	a8878693          	addi	a3,a5,-1400 # 3c125a88 <_esp_trace_encoder_array_end+0x5968>
42011472:	f38ff06f          	j	42010baa <decoder_task+0x20c>
42011476:	fe377097          	auipc	ra,0xfe377
4201147a:	f44080e7          	jalr	-188(ra) # 403883ba <esp_log_timestamp>
4201147e:	3c1267b7          	lui	a5,0x3c126
42011482:	86aa                	mv	a3,a0
42011484:	89478793          	addi	a5,a5,-1900 # 3c125894 <_esp_trace_encoder_array_end+0x5774>
42011488:	ef6ff06f          	j	42010b7e <decoder_task+0x1e0>
4201148c:	3c1267b7          	lui	a5,0x3c126
42011490:	88878793          	addi	a5,a5,-1912 # 3c125888 <_esp_trace_encoder_array_end+0x5768>
42011494:	bf1d                	j	420113ca <decoder_task+0xa2c>
42011496:	fe377097          	auipc	ra,0xfe377
4201149a:	f24080e7          	jalr	-220(ra) # 403883ba <esp_log_timestamp>
4201149e:	3c1267b7          	lui	a5,0x3c126
420114a2:	8a478713          	addi	a4,a5,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
420114a6:	3c1267b7          	lui	a5,0x3c126
420114aa:	86aa                	mv	a3,a0
420114ac:	85ba                	mv	a1,a4
420114ae:	af878613          	addi	a2,a5,-1288 # 3c125af8 <_esp_trace_encoder_array_end+0x59d8>
420114b2:	4505                	li	a0,1
420114b4:	fe377097          	auipc	ra,0xfe377
420114b8:	dfe080e7          	jalr	-514(ra) # 403882b2 <esp_log>
420114bc:	3fc957b7          	lui	a5,0x3fc95
420114c0:	d047a503          	lw	a0,-764(a5) # 3fc94d04 <s_state>
420114c4:	3c1267b7          	lui	a5,0x3c126
420114c8:	a8878693          	addi	a3,a5,-1400 # 3c125a88 <_esp_trace_encoder_array_end+0x5968>
420114cc:	85a6                	mv	a1,s1
420114ce:	4601                	li	a2,0
420114d0:	655030ef          	jal	42015324 <native_state_set_audio>
420114d4:	8c26                	mv	s8,s1
420114d6:	4981                	li	s3,0
420114d8:	4901                	li	s2,0
420114da:	4a01                	li	s4,0
420114dc:	4d81                	li	s11,0
420114de:	bc5d                	j	42010f94 <decoder_task+0x5f6>
420114e0:	3c1267b7          	lui	a5,0x3c126
420114e4:	89478593          	addi	a1,a5,-1900 # 3c125894 <_esp_trace_encoder_array_end+0x5774>
420114e8:	be7d                	j	420110a6 <decoder_task+0x708>
420114ea:	3c1267b7          	lui	a5,0x3c126
420114ee:	88878593          	addi	a1,a5,-1912 # 3c125888 <_esp_trace_encoder_array_end+0x5768>
420114f2:	be55                	j	420110a6 <decoder_task+0x708>
420114f4:	3fc957b7          	lui	a5,0x3fc95
420114f8:	d047a503          	lw	a0,-764(a5) # 3fc94d04 <s_state>
420114fc:	3c1267b7          	lui	a5,0x3c126
42011500:	be478693          	addi	a3,a5,-1052 # 3c125be4 <_esp_trace_encoder_array_end+0x5ac4>
42011504:	4601                	li	a2,0
42011506:	85a6                	mv	a1,s1
42011508:	61d030ef          	jal	42015324 <native_state_set_audio>
4201150c:	8c26                	mv	s8,s1
4201150e:	b34d                	j	420112b0 <decoder_task+0x912>
42011510:	3c1267b7          	lui	a5,0x3c126
42011514:	89478793          	addi	a5,a5,-1900 # 3c125894 <_esp_trace_encoder_array_end+0x5774>
42011518:	bd0d                	j	4201134a <decoder_task+0x9ac>
4201151a:	4c32                	lw	s8,12(sp)
4201151c:	fe377097          	auipc	ra,0xfe377
42011520:	e9e080e7          	jalr	-354(ra) # 403883ba <esp_log_timestamp>
42011524:	3c1267b7          	lui	a5,0x3c126
42011528:	8a478713          	addi	a4,a5,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
4201152c:	3c1267b7          	lui	a5,0x3c126
42011530:	86aa                	mv	a3,a0
42011532:	85ba                	mv	a1,a4
42011534:	c7078613          	addi	a2,a5,-912 # 3c125c70 <_esp_trace_encoder_array_end+0x5b50>
42011538:	4509                	li	a0,2
4201153a:	fe377097          	auipc	ra,0xfe377
4201153e:	d78080e7          	jalr	-648(ra) # 403882b2 <esp_log>
42011542:	4d85                	li	s11,1
42011544:	b8c9                	j	42010e16 <decoder_task+0x478>
42011546:	8462                	mv	s0,s8
42011548:	b311                	j	4201124c <decoder_task+0x8ae>
4201154a:	3c1267b7          	lui	a5,0x3c126
4201154e:	88878793          	addi	a5,a5,-1912 # 3c125888 <_esp_trace_encoder_array_end+0x5768>
42011552:	b315                	j	42011276 <decoder_task+0x8d8>
42011554:	3c1267b7          	lui	a5,0x3c126
42011558:	89478793          	addi	a5,a5,-1900 # 3c125894 <_esp_trace_encoder_array_end+0x5774>
4201155c:	bb29                	j	42011276 <decoder_task+0x8d8>
4201155e:	3c1267b7          	lui	a5,0x3c126
42011562:	89478793          	addi	a5,a5,-1900 # 3c125894 <_esp_trace_encoder_array_end+0x5774>
42011566:	b595                	j	420113ca <decoder_task+0xa2c>
42011568:	fe377097          	auipc	ra,0xfe377
4201156c:	e52080e7          	jalr	-430(ra) # 403883ba <esp_log_timestamp>
42011570:	4789                	li	a5,2
42011572:	4405                	li	s0,1
42011574:	86aa                	mv	a3,a0
42011576:	0afb0563          	beq	s6,a5,42011620 <decoder_task+0xc82>
4201157a:	4791                	li	a5,4
4201157c:	0afb0d63          	beq	s6,a5,42011636 <decoder_task+0xc98>
42011580:	3c1267b7          	lui	a5,0x3c126
42011584:	89878793          	addi	a5,a5,-1896 # 3c125898 <_esp_trace_encoder_array_end+0x5778>
42011588:	008b0663          	beq	s6,s0,42011594 <decoder_task+0xbf6>
4201158c:	3c1267b7          	lui	a5,0x3c126
42011590:	89c78793          	addi	a5,a5,-1892 # 3c12589c <_esp_trace_encoder_array_end+0x577c>
42011594:	3c126737          	lui	a4,0x3c126
42011598:	8a470713          	addi	a4,a4,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
4201159c:	3c126637          	lui	a2,0x3c126
420115a0:	85ba                	mv	a1,a4
420115a2:	c9060613          	addi	a2,a2,-880 # 3c125c90 <_esp_trace_encoder_array_end+0x5b70>
420115a6:	4505                	li	a0,1
420115a8:	fe377097          	auipc	ra,0xfe377
420115ac:	d0a080e7          	jalr	-758(ra) # 403882b2 <esp_log>
420115b0:	3fc957b7          	lui	a5,0x3fc95
420115b4:	d047a503          	lw	a0,-764(a5) # 3fc94d04 <s_state>
420115b8:	3c1267b7          	lui	a5,0x3c126
420115bc:	cc078693          	addi	a3,a5,-832 # 3c125cc0 <_esp_trace_encoder_array_end+0x5ba0>
420115c0:	85a6                	mv	a1,s1
420115c2:	4601                	li	a2,0
420115c4:	561030ef          	jal	42015324 <native_state_set_audio>
420115c8:	8c26                	mv	s8,s1
420115ca:	b1dd                	j	420112b0 <decoder_task+0x912>
420115cc:	fe377097          	auipc	ra,0xfe377
420115d0:	dee080e7          	jalr	-530(ra) # 403883ba <esp_log_timestamp>
420115d4:	3c126737          	lui	a4,0x3c126
420115d8:	8a470713          	addi	a4,a4,-1884 # 3c1258a4 <_esp_trace_encoder_array_end+0x5784>
420115dc:	3c126637          	lui	a2,0x3c126
420115e0:	86aa                	mv	a3,a0
420115e2:	87a2                	mv	a5,s0
420115e4:	85ba                	mv	a1,a4
420115e6:	b9c60613          	addi	a2,a2,-1124 # 3c125b9c <_esp_trace_encoder_array_end+0x5a7c>
420115ea:	4509                	li	a0,2
420115ec:	fe377097          	auipc	ra,0xfe377
420115f0:	cc6080e7          	jalr	-826(ra) # 403882b2 <esp_log>
420115f4:	3c126737          	lui	a4,0x3c126
420115f8:	0419                	addi	s0,s0,6 # 3006 <CSR_UINTSTATUS+0x2355>
420115fa:	4785                	li	a5,1
420115fc:	aa470693          	addi	a3,a4,-1372 # 3c125aa4 <_esp_trace_encoder_array_end+0x5984>
42011600:	0087e663          	bltu	a5,s0,4201160c <decoder_task+0xc6e>
42011604:	3c1267b7          	lui	a5,0x3c126
42011608:	a8878693          	addi	a3,a5,-1400 # 3c125a88 <_esp_trace_encoder_array_end+0x5968>
4201160c:	3fc957b7          	lui	a5,0x3fc95
42011610:	d047a503          	lw	a0,-764(a5) # 3fc94d04 <s_state>
42011614:	4601                	li	a2,0
42011616:	85a6                	mv	a1,s1
42011618:	50d030ef          	jal	42015324 <native_state_set_audio>
4201161c:	8c26                	mv	s8,s1
4201161e:	ba9d                	j	42010f94 <decoder_task+0x5f6>
42011620:	3c1267b7          	lui	a5,0x3c126
42011624:	88878793          	addi	a5,a5,-1912 # 3c125888 <_esp_trace_encoder_array_end+0x5768>
42011628:	b7b5                	j	42011594 <decoder_task+0xbf6>
4201162a:	3c1267b7          	lui	a5,0x3c126
4201162e:	a8878693          	addi	a3,a5,-1400 # 3c125a88 <_esp_trace_encoder_array_end+0x5968>
42011632:	d78ff06f          	j	42010baa <decoder_task+0x20c>
42011636:	3c1267b7          	lui	a5,0x3c126
4201163a:	89478793          	addi	a5,a5,-1900 # 3c125894 <_esp_trace_encoder_array_end+0x5774>
4201163e:	bf99                	j	42011594 <decoder_task+0xbf6>
42011640:	fe377097          	auipc	ra,0xfe377
42011644:	d7a080e7          	jalr	-646(ra) # 403883ba <esp_log_timestamp>
42011648:	3c1267b7          	lui	a5,0x3c126
4201164c:	86aa                	mv	a3,a0
4201164e:	88878793          	addi	a5,a5,-1912 # 3c125888 <_esp_trace_encoder_array_end+0x5768>
42011652:	b9e5                	j	4201134a <decoder_task+0x9ac>
