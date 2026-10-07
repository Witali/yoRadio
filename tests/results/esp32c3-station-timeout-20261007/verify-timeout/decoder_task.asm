
idf\esp32c3-oled-native\build-connect-retry\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420108f8 <decoder_task>:
420108f8:	7151                	addi	sp,sp,-240
420108fa:	d5a2                	sw	s0,232(sp)
420108fc:	d3a6                	sw	s1,228(sp)
420108fe:	d1ca                	sw	s2,224(sp)
42010900:	cfce                	sw	s3,220(sp)
42010902:	cdd2                	sw	s4,216(sp)
42010904:	cbd6                	sw	s5,212(sp)
42010906:	c9da                	sw	s6,208(sp)
42010908:	c7de                	sw	s7,204(sp)
4201090a:	c5e2                	sw	s8,200(sp)
4201090c:	df6e                	sw	s11,188(sp)
4201090e:	d786                	sw	ra,236(sp)
42010910:	c3e6                	sw	s9,196(sp)
42010912:	c1ea                	sw	s10,192(sp)
42010914:	2de020ef          	jal	42012bf2 <decoder_register_codecs>
42010918:	3fc95737          	lui	a4,0x3fc95
4201091c:	000f47b7          	lui	a5,0xf4
42010920:	ad870713          	addi	a4,a4,-1320 # 3fc94ad8 <s_bitrate_updated_us>
42010924:	24078793          	addi	a5,a5,576 # f4240 <CSR_UINTSTATUS+0xf358f>
42010928:	ce02                	sw	zero,28(sp)
4201092a:	c102                	sw	zero,128(sp)
4201092c:	c302                	sw	zero,132(sp)
4201092e:	c502                	sw	zero,136(sp)
42010930:	c702                	sw	zero,140(sp)
42010932:	c902                	sw	zero,144(sp)
42010934:	cb02                	sw	zero,148(sp)
42010936:	cd02                	sw	zero,152(sp)
42010938:	cf02                	sw	zero,156(sp)
4201093a:	d102                	sw	zero,160(sp)
4201093c:	d302                	sw	zero,164(sp)
4201093e:	d502                	sw	zero,168(sp)
42010940:	d702                	sw	zero,172(sp)
42010942:	d202                	sw	zero,36(sp)
42010944:	d402                	sw	zero,40(sp)
42010946:	d602                	sw	zero,44(sp)
42010948:	d802                	sw	zero,48(sp)
4201094a:	00010d23          	sb	zero,26(sp)
4201094e:	842a                	mv	s0,a0
42010950:	c23a                	sw	a4,4(sp)
42010952:	c43e                	sw	a5,8(sp)
42010954:	4981                	li	s3,0
42010956:	4a01                	li	s4,0
42010958:	4901                	li	s2,0
4201095a:	4d81                	li	s11,0
4201095c:	4b01                	li	s6,0
4201095e:	4c01                	li	s8,0
42010960:	4481                	li	s1,0
42010962:	4b81                	li	s7,0
42010964:	3fc95ab7          	lui	s5,0x3fc95
42010968:	af0a8793          	addi	a5,s5,-1296 # 3fc94af0 <s_generation>
4201096c:	0330000f          	fence	rw,rw
42010970:	0007ac83          	lw	s9,0(a5)
42010974:	0230000f          	fence	r,rw
42010978:	409c8f63          	beq	s9,s1,42010d96 <decoder_task+0x49e>
4201097c:	3fc957b7          	lui	a5,0x3fc95
42010980:	aec78793          	addi	a5,a5,-1300 # 3fc94aec <s_decoder_target_codec>
42010984:	0330000f          	fence	rw,rw
42010988:	4384                	lw	s1,0(a5)
4201098a:	0230000f          	fence	r,rw
4201098e:	4572                	lw	a0,28(sp)
42010990:	c119                	beqz	a0,42010996 <decoder_task+0x9e>
42010992:	42f280ef          	jal	420395c0 <esp_audio_simple_dec_close>
42010996:	854e                	mv	a0,s3
42010998:	ce02                	sw	zero,28(sp)
4201099a:	2ba020ef          	jal	42012c54 <native_aac_decoder_destroy>
4201099e:	000b8563          	beqz	s7,420109a8 <decoder_task+0xb0>
420109a2:	855e                	mv	a0,s7
420109a4:	577240ef          	jal	4203571a <custom_flac_decoder_destroy>
420109a8:	46048c63          	beqz	s1,42010e20 <decoder_task+0x528>
420109ac:	d202                	sw	zero,36(sp)
420109ae:	d402                	sw	zero,40(sp)
420109b0:	d602                	sw	zero,44(sp)
420109b2:	d802                	sw	zero,48(sp)
420109b4:	00010d23          	sb	zero,26(sp)
420109b8:	3fc957b7          	lui	a5,0x3fc95
420109bc:	ae878793          	addi	a5,a5,-1304 # 3fc94ae8 <s_decoder_released_generation>
420109c0:	0310000f          	fence	rw,w
420109c4:	0197a023          	sw	s9,0(a5)
420109c8:	0330000f          	fence	rw,rw
420109cc:	4b81                	li	s7,0
420109ce:	84e6                	mv	s1,s9
420109d0:	4c01                	li	s8,0
420109d2:	4b01                	li	s6,0
420109d4:	4d81                	li	s11,0
420109d6:	4981                	li	s3,0
420109d8:	3fc957b7          	lui	a5,0x3fc95
420109dc:	afc7a503          	lw	a0,-1284(a5) # 3fc94afc <s_encoded>
420109e0:	4651                	li	a2,20
420109e2:	100c                	addi	a1,sp,32
420109e4:	d002                	sw	zero,32(sp)
420109e6:	6c0680ef          	jal	420790a6 <xRingbufferReceive>
420109ea:	8caa                	mv	s9,a0
420109ec:	dd35                	beqz	a0,42010968 <decoder_task+0x70>
420109ee:	4118                	lw	a4,0(a0)
420109f0:	af0a8793          	addi	a5,s5,-1296
420109f4:	0330000f          	fence	rw,rw
420109f8:	439c                	lw	a5,0(a5)
420109fa:	0230000f          	fence	r,rw
420109fe:	40f71963          	bne	a4,a5,42010e10 <decoder_task+0x518>
42010a02:	411c                	lw	a5,0(a0)
42010a04:	41878663          	beq	a5,s8,42010e10 <decoder_task+0x518>
42010a08:	4158                	lw	a4,4(a0)
42010a0a:	e709                	bnez	a4,42010a14 <decoder_task+0x11c>
42010a0c:	00a54703          	lbu	a4,10(a0)
42010a10:	3e071c63          	bnez	a4,42010e08 <decoder_task+0x510>
42010a14:	12041563          	bnez	s0,42010b3e <decoder_task+0x246>
42010a18:	12f48c63          	beq	s1,a5,42010b50 <decoder_task+0x258>
42010a1c:	4572                	lw	a0,28(sp)
42010a1e:	c119                	beqz	a0,42010a24 <decoder_task+0x12c>
42010a20:	3a1280ef          	jal	420395c0 <esp_audio_simple_dec_close>
42010a24:	854e                	mv	a0,s3
42010a26:	ce02                	sw	zero,28(sp)
42010a28:	22c020ef          	jal	42012c54 <native_aac_decoder_destroy>
42010a2c:	000b8563          	beqz	s7,42010a36 <decoder_task+0x13e>
42010a30:	855e                	mv	a0,s7
42010a32:	4e9240ef          	jal	4203571a <custom_flac_decoder_destroy>
42010a36:	4712                	lw	a4,4(sp)
42010a38:	000ca483          	lw	s1,0(s9)
42010a3c:	004cab03          	lw	s6,4(s9)
42010a40:	3fc957b7          	lui	a5,0x3fc95
42010a44:	ae07a023          	sw	zero,-1312(a5) # 3fc94ae0 <s_published_bitrate_bps>
42010a48:	4801                	li	a6,0
42010a4a:	4781                	li	a5,0
42010a4c:	c31c                	sw	a5,0(a4)
42010a4e:	00010d23          	sb	zero,26(sp)
42010a52:	01072223          	sw	a6,4(a4)
42010a56:	fe371097          	auipc	ra,0xfe371
42010a5a:	8e4080e7          	jalr	-1820(ra) # 4038133a <esp_timer_get_time>
42010a5e:	c52a                	sw	a0,136(sp)
42010a60:	c902                	sw	zero,144(sp)
42010a62:	cb02                	sw	zero,148(sp)
42010a64:	cd02                	sw	zero,152(sp)
42010a66:	cf02                	sw	zero,156(sp)
42010a68:	d102                	sw	zero,160(sp)
42010a6a:	d302                	sw	zero,164(sp)
42010a6c:	d502                	sw	zero,168(sp)
42010a6e:	d702                	sw	zero,172(sp)
42010a70:	c126                	sw	s1,128(sp)
42010a72:	c35a                	sw	s6,132(sp)
42010a74:	c72e                	sw	a1,140(sp)
42010a76:	478d                	li	a5,3
42010a78:	3afb0a63          	beq	s6,a5,42010e2c <decoder_task+0x534>
42010a7c:	4789                	li	a5,2
42010a7e:	48fb0163          	beq	s6,a5,42010f00 <decoder_task+0x608>
42010a82:	640d                	lui	s0,0x3
42010a84:	7e8a7e63          	bgeu	s4,s0,42011280 <decoder_task+0x988>
42010a88:	85a2                	mv	a1,s0
42010a8a:	854a                	mv	a0,s2
42010a8c:	a75f70ef          	jal	42008500 <realloc>
42010a90:	7e050d63          	beqz	a0,4201128a <decoder_task+0x992>
42010a94:	d682                	sw	zero,108(sp)
42010a96:	d882                	sw	zero,112(sp)
42010a98:	da82                	sw	zero,116(sp)
42010a9a:	892a                	mv	s2,a0
42010a9c:	8a22                	mv	s4,s0
42010a9e:	4791                	li	a5,4
42010aa0:	7afb0463          	beq	s6,a5,42011248 <decoder_task+0x950>
42010aa4:	203357b7          	lui	a5,0x20335
42010aa8:	04d78793          	addi	a5,a5,77 # 2033504d <CSR_UINTSTATUS+0x2033439c>
42010aac:	086c                	addi	a1,sp,28
42010aae:	10a8                	addi	a0,sp,104
42010ab0:	d4be                	sw	a5,104(sp)
42010ab2:	709150ef          	jal	420269ba <__wrap_esp_audio_simple_dec_open>
42010ab6:	842a                	mv	s0,a0
42010ab8:	7a050463          	beqz	a0,42011260 <decoder_task+0x968>
42010abc:	fe378097          	auipc	ra,0xfe378
42010ac0:	8fe080e7          	jalr	-1794(ra) # 403883ba <esp_log_timestamp>
42010ac4:	3c1267b7          	lui	a5,0x3c126
42010ac8:	4985                	li	s3,1
42010aca:	86aa                	mv	a3,a0
42010acc:	81478793          	addi	a5,a5,-2028 # 3c125814 <_esp_trace_encoder_array_end+0x56f4>
42010ad0:	0f3b1ae3          	bne	s6,s3,420113c4 <decoder_task+0xacc>
42010ad4:	3c126737          	lui	a4,0x3c126
42010ad8:	82070713          	addi	a4,a4,-2016 # 3c125820 <_esp_trace_encoder_array_end+0x5700>
42010adc:	3c126637          	lui	a2,0x3c126
42010ae0:	85ba                	mv	a1,a4
42010ae2:	8822                	mv	a6,s0
42010ae4:	ad860613          	addi	a2,a2,-1320 # 3c125ad8 <_esp_trace_encoder_array_end+0x59b8>
42010ae8:	4505                	li	a0,1
42010aea:	fe377097          	auipc	ra,0xfe377
42010aee:	7c8080e7          	jalr	1992(ra) # 403882b2 <esp_log>
42010af2:	3c126737          	lui	a4,0x3c126
42010af6:	57f9                	li	a5,-2
42010af8:	a1070693          	addi	a3,a4,-1520 # 3c125a10 <_esp_trace_encoder_array_end+0x58f0>
42010afc:	28f40ee3          	beq	s0,a5,42011598 <decoder_task+0xca0>
42010b00:	3fc957b7          	lui	a5,0x3fc95
42010b04:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42010b08:	4601                	li	a2,0
42010b0a:	85a6                	mv	a1,s1
42010b0c:	4bd040ef          	jal	420157c8 <native_state_set_audio>
42010b10:	4572                	lw	a0,28(sp)
42010b12:	c501                	beqz	a0,42010b1a <decoder_task+0x222>
42010b14:	2ad280ef          	jal	420395c0 <esp_audio_simple_dec_close>
42010b18:	ce02                	sw	zero,28(sp)
42010b1a:	854a                	mv	a0,s2
42010b1c:	9e9f70ef          	jal	42008504 <cfree>
42010b20:	8c26                	mv	s8,s1
42010b22:	4a01                	li	s4,0
42010b24:	4901                	li	s2,0
42010b26:	4b81                	li	s7,0
42010b28:	4d81                	li	s11,0
42010b2a:	3fc957b7          	lui	a5,0x3fc95
42010b2e:	afc7a503          	lw	a0,-1284(a5) # 3fc94afc <s_encoded>
42010b32:	85e6                	mv	a1,s9
42010b34:	4981                	li	s3,0
42010b36:	5ec680ef          	jal	42079122 <vRingbufferReturnItem>
42010b3a:	4401                	li	s0,0
42010b3c:	b535                	j	42010968 <decoder_task+0x70>
42010b3e:	0b4020ef          	jal	42012bf2 <decoder_register_codecs>
42010b42:	842a                	mv	s0,a0
42010b44:	26051e63          	bnez	a0,42010dc0 <decoder_task+0x4c8>
42010b48:	000ca783          	lw	a5,0(s9)
42010b4c:	ecf498e3          	bne	s1,a5,42010a1c <decoder_task+0x124>
42010b50:	004ca783          	lw	a5,4(s9)
42010b54:	ed6794e3          	bne	a5,s6,42010a1c <decoder_task+0x124>
42010b58:	478d                	li	a5,3
42010b5a:	00fb07e3          	beq	s6,a5,42011368 <decoder_task+0xa70>
42010b5e:	47f2                	lw	a5,28(sp)
42010b60:	00f9e7b3          	or	a5,s3,a5
42010b64:	d3f9                	beqz	a5,42010b2a <decoder_task+0x232>
42010b66:	008cd783          	lhu	a5,8(s9)
42010b6a:	00bc8713          	addi	a4,s9,11
42010b6e:	ce82                	sw	zero,92(sp)
42010b70:	d082                	sw	zero,96(sp)
42010b72:	d282                	sw	zero,100(sp)
42010b74:	ccbe                	sw	a5,88(sp)
42010b76:	caba                	sw	a4,84(sp)
42010b78:	00acc703          	lbu	a4,10(s9)
42010b7c:	ffeb0693          	addi	a3,s6,-2
42010b80:	0016b693          	seqz	a3,a3
42010b84:	00e03733          	snez	a4,a4
42010b88:	c036                	sw	a3,0(sp)
42010b8a:	04e10e23          	sb	a4,92(sp)
42010b8e:	3a098463          	beqz	s3,42010f36 <decoder_task+0x63e>
42010b92:	e789                	bnez	a5,42010b9c <decoder_task+0x2a4>
42010b94:	05c14783          	lbu	a5,92(sp)
42010b98:	1c078a63          	beqz	a5,42010d6c <decoder_task+0x474>
42010b9c:	4781                	li	a5,0
42010b9e:	4801                	li	a6,0
42010ba0:	de3e                	sw	a5,60(sp)
42010ba2:	c0c2                	sw	a6,64(sp)
42010ba4:	da4a                	sw	s2,52(sp)
42010ba6:	dc52                	sw	s4,56(sp)
42010ba8:	d082                	sw	zero,96(sp)
42010baa:	fe370097          	auipc	ra,0xfe370
42010bae:	790080e7          	jalr	1936(ra) # 4038133a <esp_timer_get_time>
42010bb2:	842a                	mv	s0,a0
42010bb4:	1850                	addi	a2,sp,52
42010bb6:	08cc                	addi	a1,sp,84
42010bb8:	854e                	mv	a0,s3
42010bba:	0d0020ef          	jal	42012c8a <native_aac_decoder_process>
42010bbe:	8d2a                	mv	s10,a0
42010bc0:	fe370097          	auipc	ra,0xfe370
42010bc4:	77a080e7          	jalr	1914(ra) # 4038133a <esp_timer_get_time>
42010bc8:	47ca                	lw	a5,144(sp)
42010bca:	46da                	lw	a3,148(sp)
42010bcc:	8d01                	sub	a0,a0,s0
42010bce:	00a78733          	add	a4,a5,a0
42010bd2:	00f737b3          	sltu	a5,a4,a5
42010bd6:	97b6                	add	a5,a5,a3
42010bd8:	cb3e                	sw	a5,148(sp)
42010bda:	578a                	lw	a5,160(sp)
42010bdc:	c93a                	sw	a4,144(sp)
42010bde:	571a                	lw	a4,164(sp)
42010be0:	0785                	addi	a5,a5,1
42010be2:	d13e                	sw	a5,160(sp)
42010be4:	00a77363          	bgeu	a4,a0,42010bea <decoder_task+0x2f2>
42010be8:	d32a                	sw	a0,164(sp)
42010bea:	8bfd                	andi	a5,a5,31
42010bec:	56078763          	beqz	a5,4201115a <decoder_task+0x862>
42010bf0:	af0a8793          	addi	a5,s5,-1296
42010bf4:	0330000f          	fence	rw,rw
42010bf8:	439c                	lw	a5,0(a5)
42010bfa:	0230000f          	fence	r,rw
42010bfe:	16979763          	bne	a5,s1,42010d6c <decoder_task+0x474>
42010c02:	57e1                	li	a5,-8
42010c04:	52fd0563          	beq	s10,a5,4201112e <decoder_task+0x836>
42010c08:	5a0d1463          	bnez	s10,420111b0 <decoder_task+0x8b8>
42010c0c:	5786                	lw	a5,96(sp)
42010c0e:	4766                	lw	a4,88(sp)
42010c10:	6ef76863          	bltu	a4,a5,42011300 <decoder_task+0xa08>
42010c14:	8f1d                	sub	a4,a4,a5
42010c16:	56aa                	lw	a3,168(sp)
42010c18:	ccba                	sw	a4,88(sp)
42010c1a:	4756                	lw	a4,84(sp)
42010c1c:	96be                	add	a3,a3,a5
42010c1e:	d536                	sw	a3,168(sp)
42010c20:	97ba                	add	a5,a5,a4
42010c22:	4706                	lw	a4,64(sp)
42010c24:	cabe                	sw	a5,84(sp)
42010c26:	10070c63          	beqz	a4,42010d3e <decoder_task+0x446>
42010c2a:	00cc                	addi	a1,sp,68
42010c2c:	854e                	mv	a0,s3
42010c2e:	c282                	sw	zero,68(sp)
42010c30:	c482                	sw	zero,72(sp)
42010c32:	c682                	sw	zero,76(sp)
42010c34:	c882                	sw	zero,80(sp)
42010c36:	37c020ef          	jal	42012fb2 <native_aac_decoder_get_info>
42010c3a:	52051663          	bnez	a0,42011166 <decoder_task+0x86e>
42010c3e:	4782                	lw	a5,0(sp)
42010c40:	01b10613          	addi	a2,sp,27
42010c44:	00cc                	addi	a1,sp,68
42010c46:	854e                	mv	a0,s3
42010c48:	00f10da3          	sb	a5,27(sp)
42010c4c:	374020ef          	jal	42012fc0 <native_aac_decoder_label>
42010c50:	01b14683          	lbu	a3,27(sp)
42010c54:	842a                	mv	s0,a0
42010c56:	4501                	li	a0,0
42010c58:	5e068063          	beqz	a3,42011238 <decoder_task+0x940>
42010c5c:	af0a8793          	addi	a5,s5,-1296
42010c60:	0330000f          	fence	rw,rw
42010c64:	4398                	lw	a4,0(a5)
42010c66:	0230000f          	fence	r,rw
42010c6a:	4781                	li	a5,0
42010c6c:	06971163          	bne	a4,s1,42010cce <decoder_task+0x3d6>
42010c70:	4716                	lw	a4,68(sp)
42010c72:	cf31                	beqz	a4,42010cce <decoder_task+0x3d6>
42010c74:	04914803          	lbu	a6,73(sp)
42010c78:	04080b63          	beqz	a6,42010cce <decoder_task+0x3d6>
42010c7c:	04814603          	lbu	a2,72(sp)
42010c80:	c639                	beqz	a2,42010cce <decoder_task+0x3d6>
42010c82:	45a6                	lw	a1,72(sp)
42010c84:	47b6                	lw	a5,76(sp)
42010c86:	d23a                	sw	a4,36(sp)
42010c88:	d42e                	sw	a1,40(sp)
42010c8a:	45c6                	lw	a1,80(sp)
42010c8c:	d63e                	sw	a5,44(sp)
42010c8e:	4785                	li	a5,1
42010c90:	06012923          	sw	zero,114(sp)
42010c94:	06012b23          	sw	zero,118(sp)
42010c98:	06011d23          	sh	zero,122(sp)
42010c9c:	d4a2                	sw	s0,104(sp)
42010c9e:	d6ba                	sw	a4,108(sp)
42010ca0:	d82e                	sw	a1,48(sp)
42010ca2:	00f10d23          	sb	a5,26(sp)
42010ca6:	70050d63          	beqz	a0,420113c0 <decoder_task+0xac8>
42010caa:	3fc957b7          	lui	a5,0x3fc95
42010cae:	06a10823          	sb	a0,112(sp)
42010cb2:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42010cb6:	06c108a3          	sb	a2,113(sp)
42010cba:	85a6                	mv	a1,s1
42010cbc:	10b0                	addi	a2,sp,104
42010cbe:	daba                	sw	a4,116(sp)
42010cc0:	07010c23          	sb	a6,120(sp)
42010cc4:	06d10d23          	sb	a3,122(sp)
42010cc8:	3e1040ef          	jal	420158a8 <native_state_set_stream_info>
42010ccc:	4785                	li	a5,1
42010cce:	45b6                	lw	a1,76(sp)
42010cd0:	8526                	mv	a0,s1
42010cd2:	00f10d23          	sb	a5,26(sp)
42010cd6:	ea6ff0ef          	jal	4201037c <state_set_decoder_bitrate>
42010cda:	01a14783          	lbu	a5,26(sp)
42010cde:	c3a5                	beqz	a5,42010d3e <decoder_task+0x446>
42010ce0:	4c0d8163          	beqz	s11,420111a2 <decoder_task+0x8aa>
42010ce4:	02814503          	lbu	a0,40(sp)
42010ce8:	02914783          	lbu	a5,41(sp)
42010cec:	4406                	lw	s0,64(sp)
42010cee:	051d                	addi	a0,a0,7
42010cf0:	810d                	srli	a0,a0,0x3
42010cf2:	02f50533          	mul	a0,a0,a5
42010cf6:	c91d                	beqz	a0,42010d2c <decoder_task+0x434>
42010cf8:	5612                	lw	a2,36(sp)
42010cfa:	ca0d                	beqz	a2,42010d2c <decoder_task+0x434>
42010cfc:	02a45533          	divu	a0,s0,a0
42010d00:	47a2                	lw	a5,8(sp)
42010d02:	4681                	li	a3,0
42010d04:	02f535b3          	mulhu	a1,a0,a5
42010d08:	02f50533          	mul	a0,a0,a5
42010d0c:	fdff0097          	auipc	ra,0xfdff0
42010d10:	ba0080e7          	jalr	-1120(ra) # 400008ac <__udivdi3>
42010d14:	47ea                	lw	a5,152(sp)
42010d16:	46fa                	lw	a3,156(sp)
42010d18:	573a                	lw	a4,172(sp)
42010d1a:	953e                	add	a0,a0,a5
42010d1c:	96ae                	add	a3,a3,a1
42010d1e:	00f537b3          	sltu	a5,a0,a5
42010d22:	97b6                	add	a5,a5,a3
42010d24:	9722                	add	a4,a4,s0
42010d26:	cf3e                	sw	a5,156(sp)
42010d28:	cd2a                	sw	a0,152(sp)
42010d2a:	d73a                	sw	a4,172(sp)
42010d2c:	86a2                	mv	a3,s0
42010d2e:	864a                	mv	a2,s2
42010d30:	104c                	addi	a1,sp,36
42010d32:	8526                	mv	a0,s1
42010d34:	a89ff0ef          	jal	420107bc <send_pcm.isra.0>
42010d38:	8daa                	mv	s11,a0
42010d3a:	74050863          	beqz	a0,4201148a <decoder_task+0xb92>
42010d3e:	fe370097          	auipc	ra,0xfe370
42010d42:	5fc080e7          	jalr	1532(ra) # 4038133a <esp_timer_get_time>
42010d46:	862e                	mv	a2,a1
42010d48:	85aa                	mv	a1,a0
42010d4a:	0108                	addi	a0,sp,128
42010d4c:	9a4ff0ef          	jal	4200fef0 <decode_stats_report>
42010d50:	4706                	lw	a4,64(sp)
42010d52:	5786                	lw	a5,96(sp)
42010d54:	05c14683          	lbu	a3,92(sp)
42010d58:	8fd9                	or	a5,a5,a4
42010d5a:	3c079463          	bnez	a5,42011122 <decoder_task+0x82a>
42010d5e:	76068c63          	beqz	a3,420114d6 <decoder_task+0xbde>
42010d62:	4701                	li	a4,0
42010d64:	47e6                	lw	a5,88(sp)
42010d66:	8f5d                	or	a4,a4,a5
42010d68:	e20715e3          	bnez	a4,42010b92 <decoder_task+0x29a>
42010d6c:	00acc783          	lbu	a5,10(s9)
42010d70:	4a079363          	bnez	a5,42011216 <decoder_task+0x91e>
42010d74:	4a9c0163          	beq	s8,s1,42011216 <decoder_task+0x91e>
42010d78:	8566                	mv	a0,s9
42010d7a:	85e2                	mv	a1,s8
42010d7c:	979ff0ef          	jal	420106f4 <return_decoded_packet>
42010d80:	4401                	li	s0,0
42010d82:	af0a8793          	addi	a5,s5,-1296
42010d86:	0330000f          	fence	rw,rw
42010d8a:	0007ac83          	lw	s9,0(a5)
42010d8e:	0230000f          	fence	r,rw
42010d92:	be9c95e3          	bne	s9,s1,4201097c <decoder_task+0x84>
42010d96:	c40c01e3          	beqz	s8,420109d8 <decoder_task+0xe0>
42010d9a:	c29c1fe3          	bne	s8,s1,420109d8 <decoder_task+0xe0>
42010d9e:	4572                	lw	a0,28(sp)
42010da0:	c119                	beqz	a0,42010da6 <decoder_task+0x4ae>
42010da2:	01f280ef          	jal	420395c0 <esp_audio_simple_dec_close>
42010da6:	ce02                	sw	zero,28(sp)
42010da8:	00098563          	beqz	s3,42010db2 <decoder_task+0x4ba>
42010dac:	854e                	mv	a0,s3
42010dae:	6a7010ef          	jal	42012c54 <native_aac_decoder_destroy>
42010db2:	854a                	mv	a0,s2
42010db4:	f50f70ef          	jal	42008504 <cfree>
42010db8:	4981                	li	s3,0
42010dba:	4a01                	li	s4,0
42010dbc:	4901                	li	s2,0
42010dbe:	b929                	j	420109d8 <decoder_task+0xe0>
42010dc0:	fe377097          	auipc	ra,0xfe377
42010dc4:	5fa080e7          	jalr	1530(ra) # 403883ba <esp_log_timestamp>
42010dc8:	3c126737          	lui	a4,0x3c126
42010dcc:	82070713          	addi	a4,a4,-2016 # 3c125820 <_esp_trace_encoder_array_end+0x5700>
42010dd0:	3c126637          	lui	a2,0x3c126
42010dd4:	86aa                	mv	a3,a0
42010dd6:	85ba                	mv	a1,a4
42010dd8:	87a2                	mv	a5,s0
42010dda:	a3060613          	addi	a2,a2,-1488 # 3c125a30 <_esp_trace_encoder_array_end+0x5910>
42010dde:	4505                	li	a0,1
42010de0:	fe377097          	auipc	ra,0xfe377
42010de4:	4d2080e7          	jalr	1234(ra) # 403882b2 <esp_log>
42010de8:	3fc957b7          	lui	a5,0x3fc95
42010dec:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42010df0:	000ca583          	lw	a1,0(s9)
42010df4:	3c1267b7          	lui	a5,0x3c126
42010df8:	a6078693          	addi	a3,a5,-1440 # 3c125a60 <_esp_trace_encoder_array_end+0x5940>
42010dfc:	4601                	li	a2,0
42010dfe:	1cb040ef          	jal	420157c8 <native_state_set_audio>
42010e02:	000cac03          	lw	s8,0(s9)
42010e06:	8566                	mv	a0,s9
42010e08:	85e2                	mv	a1,s8
42010e0a:	8ebff0ef          	jal	420106f4 <return_decoded_packet>
42010e0e:	bea9                	j	42010968 <decoder_task+0x70>
42010e10:	3fc957b7          	lui	a5,0x3fc95
42010e14:	afc7a503          	lw	a0,-1284(a5) # 3fc94afc <s_encoded>
42010e18:	85e6                	mv	a1,s9
42010e1a:	308680ef          	jal	42079122 <vRingbufferReturnItem>
42010e1e:	b6a9                	j	42010968 <decoder_task+0x70>
42010e20:	854a                	mv	a0,s2
42010e22:	ee2f70ef          	jal	42008504 <cfree>
42010e26:	4a01                	li	s4,0
42010e28:	4901                	li	s2,0
42010e2a:	b649                	j	420109ac <decoder_task+0xb4>
42010e2c:	854a                	mv	a0,s2
42010e2e:	ed6f70ef          	jal	42008504 <cfree>
42010e32:	089240ef          	jal	420356ba <custom_flac_decoder_create>
42010e36:	8baa                	mv	s7,a0
42010e38:	52050b63          	beqz	a0,4201136e <decoder_task+0xa76>
42010e3c:	4981                	li	s3,0
42010e3e:	4a01                	li	s4,0
42010e40:	4901                	li	s2,0
42010e42:	4d81                	li	s11,0
42010e44:	4661                	li	a2,24
42010e46:	4581                	li	a1,0
42010e48:	10a8                	addi	a0,sp,104
42010e4a:	fdfef097          	auipc	ra,0xfdfef
42010e4e:	50a080e7          	jalr	1290(ra) # 40000354 <memset>
42010e52:	011c                	addi	a5,sp,128
42010e54:	ccbe                	sw	a5,88(sp)
42010e56:	105c                	addi	a5,sp,36
42010e58:	cebe                	sw	a5,92(sp)
42010e5a:	01a10793          	addi	a5,sp,26
42010e5e:	d0be                	sw	a5,96(sp)
42010e60:	caa6                	sw	s1,84(sp)
42010e62:	00acc683          	lbu	a3,10(s9)
42010e66:	008cd603          	lhu	a2,8(s9)
42010e6a:	42011737          	lui	a4,0x42011
42010e6e:	00d036b3          	snez	a3,a3
42010e72:	08dc                	addi	a5,sp,84
42010e74:	5c270713          	addi	a4,a4,1474 # 420115c2 <custom_flac_output>
42010e78:	00bc8593          	addi	a1,s9,11
42010e7c:	06810813          	addi	a6,sp,104
42010e80:	855e                	mv	a0,s7
42010e82:	0bf240ef          	jal	42035740 <custom_flac_decoder_feed>
42010e86:	47ca                	lw	a5,144(sp)
42010e88:	5726                	lw	a4,104(sp)
42010e8a:	465a                	lw	a2,148(sp)
42010e8c:	55b6                	lw	a1,108(sp)
42010e8e:	568a                	lw	a3,160(sp)
42010e90:	973e                	add	a4,a4,a5
42010e92:	842a                	mv	s0,a0
42010e94:	5546                	lw	a0,112(sp)
42010e96:	962e                	add	a2,a2,a1
42010e98:	00f737b3          	sltu	a5,a4,a5
42010e9c:	97b2                	add	a5,a5,a2
42010e9e:	55d6                	lw	a1,116(sp)
42010ea0:	561a                	lw	a2,164(sp)
42010ea2:	96aa                	add	a3,a3,a0
42010ea4:	c93a                	sw	a4,144(sp)
42010ea6:	cb3e                	sw	a5,148(sp)
42010ea8:	d136                	sw	a3,160(sp)
42010eaa:	00b67363          	bgeu	a2,a1,42010eb0 <decoder_task+0x5b8>
42010eae:	d32e                	sw	a1,164(sp)
42010eb0:	57aa                	lw	a5,168(sp)
42010eb2:	5766                	lw	a4,120(sp)
42010eb4:	97ba                	add	a5,a5,a4
42010eb6:	d53e                	sw	a5,168(sp)
42010eb8:	500d8c63          	beqz	s11,420113d0 <decoder_task+0xad8>
42010ebc:	4d85                	li	s11,1
42010ebe:	fe370097          	auipc	ra,0xfe370
42010ec2:	47c080e7          	jalr	1148(ra) # 4038133a <esp_timer_get_time>
42010ec6:	862e                	mv	a2,a1
42010ec8:	85aa                	mv	a1,a0
42010eca:	0108                	addi	a0,sp,128
42010ecc:	824ff0ef          	jal	4200fef0 <decode_stats_report>
42010ed0:	00045b63          	bgez	s0,42010ee6 <decoder_task+0x5ee>
42010ed4:	af0a8793          	addi	a5,s5,-1296
42010ed8:	0330000f          	fence	rw,rw
42010edc:	439c                	lw	a5,0(a5)
42010ede:	0230000f          	fence	r,rw
42010ee2:	64978c63          	beq	a5,s1,4201153a <decoder_task+0xc42>
42010ee6:	00acc783          	lbu	a5,10(s9)
42010eea:	4c079663          	bnez	a5,420113b6 <decoder_task+0xabe>
42010eee:	4c9c0463          	beq	s8,s1,420113b6 <decoder_task+0xabe>
42010ef2:	8566                	mv	a0,s9
42010ef4:	85e2                	mv	a1,s8
42010ef6:	ffeff0ef          	jal	420106f4 <return_decoded_packet>
42010efa:	4b0d                	li	s6,3
42010efc:	4401                	li	s0,0
42010efe:	b4ad                	j	42010968 <decoder_task+0x70>
42010f00:	6589                	lui	a1,0x2
42010f02:	36ba0663          	beq	s4,a1,4201126e <decoder_task+0x976>
42010f06:	854a                	mv	a0,s2
42010f08:	df8f70ef          	jal	42008500 <realloc>
42010f0c:	842a                	mv	s0,a0
42010f0e:	6a050063          	beqz	a0,420115ae <decoder_task+0xcb6>
42010f12:	204347b7          	lui	a5,0x20434
42010f16:	14178793          	addi	a5,a5,321 # 20434141 <CSR_UINTSTATUS+0x20433490>
42010f1a:	d682                	sw	zero,108(sp)
42010f1c:	d882                	sw	zero,112(sp)
42010f1e:	da82                	sw	zero,116(sp)
42010f20:	d4be                	sw	a5,104(sp)
42010f22:	507010ef          	jal	42012c28 <native_aac_decoder_create>
42010f26:	89aa                	mv	s3,a0
42010f28:	4c050463          	beqz	a0,420113f0 <decoder_task+0xaf8>
42010f2c:	8922                	mv	s2,s0
42010f2e:	6a09                	lui	s4,0x2
42010f30:	4b81                	li	s7,0
42010f32:	4d81                	li	s11,0
42010f34:	b90d                	j	42010b66 <decoder_task+0x26e>
42010f36:	5d61                	li	s10,-8
42010f38:	c662                	sw	s8,12(sp)
42010f3a:	e789                	bnez	a5,42010f44 <decoder_task+0x64c>
42010f3c:	05c14783          	lbu	a5,92(sp)
42010f40:	1c078f63          	beqz	a5,4201111e <decoder_task+0x826>
42010f44:	4781                	li	a5,0
42010f46:	4801                	li	a6,0
42010f48:	de3e                	sw	a5,60(sp)
42010f4a:	c0c2                	sw	a6,64(sp)
42010f4c:	da4a                	sw	s2,52(sp)
42010f4e:	dc52                	sw	s4,56(sp)
42010f50:	d082                	sw	zero,96(sp)
42010f52:	fe370097          	auipc	ra,0xfe370
42010f56:	3e8080e7          	jalr	1000(ra) # 4038133a <esp_timer_get_time>
42010f5a:	842a                	mv	s0,a0
42010f5c:	4572                	lw	a0,28(sp)
42010f5e:	1850                	addi	a2,sp,52
42010f60:	08cc                	addi	a1,sp,84
42010f62:	3e5150ef          	jal	42026b46 <__wrap_esp_audio_simple_dec_process>
42010f66:	8c2a                	mv	s8,a0
42010f68:	fe370097          	auipc	ra,0xfe370
42010f6c:	3d2080e7          	jalr	978(ra) # 4038133a <esp_timer_get_time>
42010f70:	47ca                	lw	a5,144(sp)
42010f72:	46da                	lw	a3,148(sp)
42010f74:	8d01                	sub	a0,a0,s0
42010f76:	00a78733          	add	a4,a5,a0
42010f7a:	00f737b3          	sltu	a5,a4,a5
42010f7e:	97b6                	add	a5,a5,a3
42010f80:	cb3e                	sw	a5,148(sp)
42010f82:	578a                	lw	a5,160(sp)
42010f84:	c93a                	sw	a4,144(sp)
42010f86:	571a                	lw	a4,164(sp)
42010f88:	0785                	addi	a5,a5,1
42010f8a:	d13e                	sw	a5,160(sp)
42010f8c:	00a77363          	bgeu	a4,a0,42010f92 <decoder_task+0x69a>
42010f90:	d32a                	sw	a0,164(sp)
42010f92:	8bfd                	andi	a5,a5,31
42010f94:	1e078e63          	beqz	a5,42011190 <decoder_task+0x898>
42010f98:	af0a8793          	addi	a5,s5,-1296
42010f9c:	0330000f          	fence	rw,rw
42010fa0:	439c                	lw	a5,0(a5)
42010fa2:	0230000f          	fence	r,rw
42010fa6:	16979c63          	bne	a5,s1,4201111e <decoder_task+0x826>
42010faa:	1dac0763          	beq	s8,s10,42011178 <decoder_task+0x880>
42010fae:	500c1363          	bnez	s8,420114b4 <decoder_task+0xbbc>
42010fb2:	5786                	lw	a5,96(sp)
42010fb4:	4766                	lw	a4,88(sp)
42010fb6:	34f76563          	bltu	a4,a5,42011300 <decoder_task+0xa08>
42010fba:	8f1d                	sub	a4,a4,a5
42010fbc:	56aa                	lw	a3,168(sp)
42010fbe:	ccba                	sw	a4,88(sp)
42010fc0:	4756                	lw	a4,84(sp)
42010fc2:	96be                	add	a3,a3,a5
42010fc4:	d536                	sw	a3,168(sp)
42010fc6:	97ba                	add	a5,a5,a4
42010fc8:	4706                	lw	a4,64(sp)
42010fca:	cabe                	sw	a5,84(sp)
42010fcc:	12070363          	beqz	a4,420110f2 <decoder_task+0x7fa>
42010fd0:	4572                	lw	a0,28(sp)
42010fd2:	00cc                	addi	a1,sp,68
42010fd4:	c282                	sw	zero,68(sp)
42010fd6:	c482                	sw	zero,72(sp)
42010fd8:	c682                	sw	zero,76(sp)
42010fda:	c882                	sw	zero,80(sp)
42010fdc:	56c280ef          	jal	42039548 <esp_audio_simple_dec_get_info>
42010fe0:	1a051e63          	bnez	a0,4201119c <decoder_task+0x8a4>
42010fe4:	4782                	lw	a5,0(sp)
42010fe6:	00f10da3          	sb	a5,27(sp)
42010fea:	4789                	li	a5,2
42010fec:	46fb0663          	beq	s6,a5,42011458 <decoder_task+0xb60>
42010ff0:	4791                	li	a5,4
42010ff2:	44fb0e63          	beq	s6,a5,4201144e <decoder_task+0xb56>
42010ff6:	3c126737          	lui	a4,0x3c126
42010ffa:	4785                	li	a5,1
42010ffc:	81470593          	addi	a1,a4,-2028 # 3c125814 <_esp_trace_encoder_array_end+0x56f4>
42011000:	3efb1363          	bne	s6,a5,420113e6 <decoder_task+0xaee>
42011004:	af0a8793          	addi	a5,s5,-1296
42011008:	0330000f          	fence	rw,rw
4201100c:	439c                	lw	a5,0(a5)
4201100e:	0230000f          	fence	r,rw
42011012:	06979463          	bne	a5,s1,4201107a <decoder_task+0x782>
42011016:	4796                	lw	a5,68(sp)
42011018:	c3b5                	beqz	a5,4201107c <decoder_task+0x784>
4201101a:	04914683          	lbu	a3,73(sp)
4201101e:	ceb1                	beqz	a3,4201107a <decoder_task+0x782>
42011020:	04815703          	lhu	a4,72(sp)
42011024:	04814503          	lbu	a0,72(sp)
42011028:	00875613          	srli	a2,a4,0x8
4201102c:	0722                	slli	a4,a4,0x8
4201102e:	963a                	add	a2,a2,a4
42011030:	c529                	beqz	a0,4201107a <decoder_task+0x782>
42011032:	06012b23          	sw	zero,118(sp)
42011036:	06012923          	sw	zero,114(sp)
4201103a:	d23e                	sw	a5,36(sp)
4201103c:	06c11823          	sh	a2,112(sp)
42011040:	d6be                	sw	a5,108(sp)
42011042:	4626                	lw	a2,72(sp)
42011044:	dabe                	sw	a5,116(sp)
42011046:	3fc957b7          	lui	a5,0x3fc95
4201104a:	4746                	lw	a4,80(sp)
4201104c:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42011050:	06d10c23          	sb	a3,120(sp)
42011054:	4782                	lw	a5,0(sp)
42011056:	46b6                	lw	a3,76(sp)
42011058:	06011d23          	sh	zero,122(sp)
4201105c:	d4ae                	sw	a1,104(sp)
4201105e:	d432                	sw	a2,40(sp)
42011060:	4405                	li	s0,1
42011062:	10b0                	addi	a2,sp,104
42011064:	85a6                	mv	a1,s1
42011066:	06f10d23          	sb	a5,122(sp)
4201106a:	d636                	sw	a3,44(sp)
4201106c:	d83a                	sw	a4,48(sp)
4201106e:	00810d23          	sb	s0,26(sp)
42011072:	037040ef          	jal	420158a8 <native_state_set_stream_info>
42011076:	87a2                	mv	a5,s0
42011078:	a011                	j	4201107c <decoder_task+0x784>
4201107a:	4781                	li	a5,0
4201107c:	45b6                	lw	a1,76(sp)
4201107e:	8526                	mv	a0,s1
42011080:	00f10d23          	sb	a5,26(sp)
42011084:	af8ff0ef          	jal	4201037c <state_set_decoder_bitrate>
42011088:	01a14783          	lbu	a5,26(sp)
4201108c:	c3bd                	beqz	a5,420110f2 <decoder_task+0x7fa>
4201108e:	1e0d8263          	beqz	s11,42011272 <decoder_task+0x97a>
42011092:	02814503          	lbu	a0,40(sp)
42011096:	02914783          	lbu	a5,41(sp)
4201109a:	4406                	lw	s0,64(sp)
4201109c:	051d                	addi	a0,a0,7
4201109e:	810d                	srli	a0,a0,0x3
420110a0:	02f50533          	mul	a0,a0,a5
420110a4:	cd15                	beqz	a0,420110e0 <decoder_task+0x7e8>
420110a6:	5612                	lw	a2,36(sp)
420110a8:	ce05                	beqz	a2,420110e0 <decoder_task+0x7e8>
420110aa:	02a45533          	divu	a0,s0,a0
420110ae:	000f47b7          	lui	a5,0xf4
420110b2:	24078793          	addi	a5,a5,576 # f4240 <CSR_UINTSTATUS+0xf358f>
420110b6:	4681                	li	a3,0
420110b8:	02f535b3          	mulhu	a1,a0,a5
420110bc:	02f50533          	mul	a0,a0,a5
420110c0:	fdfef097          	auipc	ra,0xfdfef
420110c4:	7ec080e7          	jalr	2028(ra) # 400008ac <__udivdi3>
420110c8:	47ea                	lw	a5,152(sp)
420110ca:	46fa                	lw	a3,156(sp)
420110cc:	573a                	lw	a4,172(sp)
420110ce:	953e                	add	a0,a0,a5
420110d0:	96ae                	add	a3,a3,a1
420110d2:	00f537b3          	sltu	a5,a0,a5
420110d6:	97b6                	add	a5,a5,a3
420110d8:	9722                	add	a4,a4,s0
420110da:	cf3e                	sw	a5,156(sp)
420110dc:	cd2a                	sw	a0,152(sp)
420110de:	d73a                	sw	a4,172(sp)
420110e0:	86a2                	mv	a3,s0
420110e2:	864a                	mv	a2,s2
420110e4:	104c                	addi	a1,sp,36
420110e6:	8526                	mv	a0,s1
420110e8:	ed4ff0ef          	jal	420107bc <send_pcm.isra.0>
420110ec:	8daa                	mv	s11,a0
420110ee:	38050d63          	beqz	a0,42011488 <decoder_task+0xb90>
420110f2:	fe370097          	auipc	ra,0xfe370
420110f6:	248080e7          	jalr	584(ra) # 4038133a <esp_timer_get_time>
420110fa:	862e                	mv	a2,a1
420110fc:	85aa                	mv	a1,a0
420110fe:	0108                	addi	a0,sp,128
42011100:	df1fe0ef          	jal	4200fef0 <decode_stats_report>
42011104:	4706                	lw	a4,64(sp)
42011106:	5786                	lw	a5,96(sp)
42011108:	05c14683          	lbu	a3,92(sp)
4201110c:	8fd9                	or	a5,a5,a4
4201110e:	efb9                	bnez	a5,4201116c <decoder_task+0x874>
42011110:	3c068363          	beqz	a3,420114d6 <decoder_task+0xbde>
42011114:	4701                	li	a4,0
42011116:	47e6                	lw	a5,88(sp)
42011118:	8f5d                	or	a4,a4,a5
4201111a:	e20710e3          	bnez	a4,42010f3a <decoder_task+0x642>
4201111e:	4c32                	lw	s8,12(sp)
42011120:	b1b1                	j	42010d6c <decoder_task+0x474>
42011122:	c40691e3          	bnez	a3,42010d64 <decoder_task+0x46c>
42011126:	47e6                	lw	a5,88(sp)
42011128:	a6079ae3          	bnez	a5,42010b9c <decoder_task+0x2a4>
4201112c:	b181                	j	42010d6c <decoder_task+0x474>
4201112e:	5706                	lw	a4,96(sp)
42011130:	47d6                	lw	a5,84(sp)
42011132:	56aa                	lw	a3,168(sp)
42011134:	5472                	lw	s0,60(sp)
42011136:	97ba                	add	a5,a5,a4
42011138:	cabe                	sw	a5,84(sp)
4201113a:	47e6                	lw	a5,88(sp)
4201113c:	96ba                	add	a3,a3,a4
4201113e:	d536                	sw	a3,168(sp)
42011140:	8f99                	sub	a5,a5,a4
42011142:	ccbe                	sw	a5,88(sp)
42011144:	308a7f63          	bgeu	s4,s0,42011462 <decoder_task+0xb6a>
42011148:	85a2                	mv	a1,s0
4201114a:	854a                	mv	a0,s2
4201114c:	bb4f70ef          	jal	42008500 <realloc>
42011150:	30050963          	beqz	a0,42011462 <decoder_task+0xb6a>
42011154:	8a22                	mv	s4,s0
42011156:	892a                	mv	s2,a0
42011158:	b491                	j	42010b9c <decoder_task+0x2a4>
4201115a:	4505                	li	a0,1
4201115c:	00102097          	auipc	ra,0x102
42011160:	db0080e7          	jalr	-592(ra) # 42112f0c <vTaskDelay>
42011164:	b471                	j	42010bf0 <decoder_task+0x2f8>
42011166:	00010d23          	sb	zero,26(sp)
4201116a:	bed1                	j	42010d3e <decoder_task+0x446>
4201116c:	f6cd                	bnez	a3,42011116 <decoder_task+0x81e>
4201116e:	47e6                	lw	a5,88(sp)
42011170:	dc079ae3          	bnez	a5,42010f44 <decoder_task+0x64c>
42011174:	4c32                	lw	s8,12(sp)
42011176:	bedd                	j	42010d6c <decoder_task+0x474>
42011178:	5472                	lw	s0,60(sp)
4201117a:	2e8a7463          	bgeu	s4,s0,42011462 <decoder_task+0xb6a>
4201117e:	85a2                	mv	a1,s0
42011180:	854a                	mv	a0,s2
42011182:	b7ef70ef          	jal	42008500 <realloc>
42011186:	2c050e63          	beqz	a0,42011462 <decoder_task+0xb6a>
4201118a:	892a                	mv	s2,a0
4201118c:	8a22                	mv	s4,s0
4201118e:	bb5d                	j	42010f44 <decoder_task+0x64c>
42011190:	4505                	li	a0,1
42011192:	00102097          	auipc	ra,0x102
42011196:	d7a080e7          	jalr	-646(ra) # 42112f0c <vTaskDelay>
4201119a:	bbfd                	j	42010f98 <decoder_task+0x6a0>
4201119c:	00010d23          	sb	zero,26(sp)
420111a0:	bf89                	j	420110f2 <decoder_task+0x7fa>
420111a2:	3c1267b7          	lui	a5,0x3c126
420111a6:	b4478513          	addi	a0,a5,-1212 # 3c125b44 <_esp_trace_encoder_array_end+0x5a24>
420111aa:	96eff0ef          	jal	42010318 <log_runtime_memory>
420111ae:	be1d                	j	42010ce4 <decoder_task+0x3ec>
420111b0:	846a                	mv	s0,s10
420111b2:	4a09                	li	s4,2
420111b4:	fe377097          	auipc	ra,0xfe377
420111b8:	206080e7          	jalr	518(ra) # 403883ba <esp_log_timestamp>
420111bc:	2f4b0e63          	beq	s6,s4,420114b8 <decoder_task+0xbc0>
420111c0:	4791                	li	a5,4
420111c2:	30fb0063          	beq	s6,a5,420114c2 <decoder_task+0xbca>
420111c6:	3c1267b7          	lui	a5,0x3c126
420111ca:	4705                	li	a4,1
420111cc:	81478793          	addi	a5,a5,-2028 # 3c125814 <_esp_trace_encoder_array_end+0x56f4>
420111d0:	00eb0663          	beq	s6,a4,420111dc <decoder_task+0x8e4>
420111d4:	3c1267b7          	lui	a5,0x3c126
420111d8:	81878793          	addi	a5,a5,-2024 # 3c125818 <_esp_trace_encoder_array_end+0x56f8>
420111dc:	3c126737          	lui	a4,0x3c126
420111e0:	82070713          	addi	a4,a4,-2016 # 3c125820 <_esp_trace_encoder_array_end+0x5700>
420111e4:	3c126637          	lui	a2,0x3c126
420111e8:	86aa                	mv	a3,a0
420111ea:	85ba                	mv	a1,a4
420111ec:	8822                	mv	a6,s0
420111ee:	b7860613          	addi	a2,a2,-1160 # 3c125b78 <_esp_trace_encoder_array_end+0x5a58>
420111f2:	4509                	li	a0,2
420111f4:	fe377097          	auipc	ra,0xfe377
420111f8:	0be080e7          	jalr	190(ra) # 403882b2 <esp_log>
420111fc:	3fc957b7          	lui	a5,0x3fc95
42011200:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42011204:	3c1267b7          	lui	a5,0x3c126
42011208:	a2078693          	addi	a3,a5,-1504 # 3c125a20 <_esp_trace_encoder_array_end+0x5900>
4201120c:	85a6                	mv	a1,s1
4201120e:	4601                	li	a2,0
42011210:	5b8040ef          	jal	420157c8 <native_state_set_audio>
42011214:	8c26                	mv	s8,s1
42011216:	4572                	lw	a0,28(sp)
42011218:	c119                	beqz	a0,4201121e <decoder_task+0x926>
4201121a:	3a6280ef          	jal	420395c0 <esp_audio_simple_dec_close>
4201121e:	ce02                	sw	zero,28(sp)
42011220:	00098563          	beqz	s3,4201122a <decoder_task+0x932>
42011224:	854e                	mv	a0,s3
42011226:	22f010ef          	jal	42012c54 <native_aac_decoder_destroy>
4201122a:	854a                	mv	a0,s2
4201122c:	ad8f70ef          	jal	42008504 <cfree>
42011230:	4981                	li	s3,0
42011232:	4a01                	li	s4,0
42011234:	4901                	li	s2,0
42011236:	b689                	j	42010d78 <decoder_task+0x480>
42011238:	854e                	mv	a0,s3
4201123a:	5df010ef          	jal	42013018 <native_aac_decoder_source_channels>
4201123e:	01b14683          	lbu	a3,27(sp)
42011242:	0ff57513          	zext.b	a0,a0
42011246:	bc19                	j	42010c5c <decoder_task+0x364>
42011248:	204747b7          	lui	a5,0x20474
4201124c:	74f78793          	addi	a5,a5,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
42011250:	086c                	addi	a1,sp,28
42011252:	10a8                	addi	a0,sp,104
42011254:	d4be                	sw	a5,104(sp)
42011256:	764150ef          	jal	420269ba <__wrap_esp_audio_simple_dec_open>
4201125a:	842a                	mv	s0,a0
4201125c:	1c051963          	bnez	a0,4201142e <decoder_task+0xb36>
42011260:	4bf2                	lw	s7,28(sp)
42011262:	4d81                	li	s11,0
42011264:	8c0b83e3          	beqz	s7,42010b2a <decoder_task+0x232>
42011268:	4981                	li	s3,0
4201126a:	4b81                	li	s7,0
4201126c:	b8ed                	j	42010b66 <decoder_task+0x26e>
4201126e:	844a                	mv	s0,s2
42011270:	b14d                	j	42010f12 <decoder_task+0x61a>
42011272:	3c1267b7          	lui	a5,0x3c126
42011276:	b4478513          	addi	a0,a5,-1212 # 3c125b44 <_esp_trace_encoder_array_end+0x5a24>
4201127a:	89eff0ef          	jal	42010318 <log_runtime_memory>
4201127e:	bd11                	j	42011092 <decoder_task+0x79a>
42011280:	d682                	sw	zero,108(sp)
42011282:	d882                	sw	zero,112(sp)
42011284:	da82                	sw	zero,116(sp)
42011286:	819ff06f          	j	42010a9e <decoder_task+0x1a6>
4201128a:	fe377097          	auipc	ra,0xfe377
4201128e:	130080e7          	jalr	304(ra) # 403883ba <esp_log_timestamp>
42011292:	4791                	li	a5,4
42011294:	4405                	li	s0,1
42011296:	86aa                	mv	a3,a0
42011298:	1efb0363          	beq	s6,a5,4201147e <decoder_task+0xb86>
4201129c:	3c1267b7          	lui	a5,0x3c126
420112a0:	81478793          	addi	a5,a5,-2028 # 3c125814 <_esp_trace_encoder_array_end+0x56f4>
420112a4:	008b0663          	beq	s6,s0,420112b0 <decoder_task+0x9b8>
420112a8:	3c1267b7          	lui	a5,0x3c126
420112ac:	81878793          	addi	a5,a5,-2024 # 3c125818 <_esp_trace_encoder_array_end+0x56f8>
420112b0:	3c126737          	lui	a4,0x3c126
420112b4:	82070713          	addi	a4,a4,-2016 # 3c125820 <_esp_trace_encoder_array_end+0x5700>
420112b8:	3c126637          	lui	a2,0x3c126
420112bc:	85ba                	mv	a1,a4
420112be:	aa860613          	addi	a2,a2,-1368 # 3c125aa8 <_esp_trace_encoder_array_end+0x5988>
420112c2:	4505                	li	a0,1
420112c4:	fe377097          	auipc	ra,0xfe377
420112c8:	fee080e7          	jalr	-18(ra) # 403882b2 <esp_log>
420112cc:	3fc957b7          	lui	a5,0x3fc95
420112d0:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
420112d4:	3c1267b7          	lui	a5,0x3c126
420112d8:	a0478693          	addi	a3,a5,-1532 # 3c125a04 <_esp_trace_encoder_array_end+0x58e4>
420112dc:	85a6                	mv	a1,s1
420112de:	4601                	li	a2,0
420112e0:	4e8040ef          	jal	420157c8 <native_state_set_audio>
420112e4:	3fc957b7          	lui	a5,0x3fc95
420112e8:	afc7a503          	lw	a0,-1284(a5) # 3fc94afc <s_encoded>
420112ec:	85e6                	mv	a1,s9
420112ee:	8c26                	mv	s8,s1
420112f0:	633670ef          	jal	42079122 <vRingbufferReturnItem>
420112f4:	4981                	li	s3,0
420112f6:	4d81                	li	s11,0
420112f8:	4b81                	li	s7,0
420112fa:	4401                	li	s0,0
420112fc:	e6cff06f          	j	42010968 <decoder_task+0x70>
42011300:	fe377097          	auipc	ra,0xfe377
42011304:	0ba080e7          	jalr	186(ra) # 403883ba <esp_log_timestamp>
42011308:	4789                	li	a5,2
4201130a:	4405                	li	s0,1
4201130c:	12fb0c63          	beq	s6,a5,42011444 <decoder_task+0xb4c>
42011310:	4791                	li	a5,4
42011312:	1afb0d63          	beq	s6,a5,420114cc <decoder_task+0xbd4>
42011316:	3c1267b7          	lui	a5,0x3c126
4201131a:	81478793          	addi	a5,a5,-2028 # 3c125814 <_esp_trace_encoder_array_end+0x56f4>
4201131e:	008b0663          	beq	s6,s0,4201132a <decoder_task+0xa32>
42011322:	3c1267b7          	lui	a5,0x3c126
42011326:	81878793          	addi	a5,a5,-2024 # 3c125818 <_esp_trace_encoder_array_end+0x56f8>
4201132a:	48e6                	lw	a7,88(sp)
4201132c:	5806                	lw	a6,96(sp)
4201132e:	3c126737          	lui	a4,0x3c126
42011332:	82070713          	addi	a4,a4,-2016 # 3c125820 <_esp_trace_encoder_array_end+0x5700>
42011336:	3c126637          	lui	a2,0x3c126
4201133a:	86aa                	mv	a3,a0
4201133c:	85ba                	mv	a1,a4
4201133e:	b9c60613          	addi	a2,a2,-1124 # 3c125b9c <_esp_trace_encoder_array_end+0x5a7c>
42011342:	4505                	li	a0,1
42011344:	fe377097          	auipc	ra,0xfe377
42011348:	f6e080e7          	jalr	-146(ra) # 403882b2 <esp_log>
4201134c:	3fc957b7          	lui	a5,0x3fc95
42011350:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42011354:	3c1267b7          	lui	a5,0x3c126
42011358:	bd878693          	addi	a3,a5,-1064 # 3c125bd8 <_esp_trace_encoder_array_end+0x5ab8>
4201135c:	85a6                	mv	a1,s1
4201135e:	4601                	li	a2,0
42011360:	468040ef          	jal	420157c8 <native_state_set_audio>
42011364:	8c26                	mv	s8,s1
42011366:	bd45                	j	42011216 <decoder_task+0x91e>
42011368:	b60b8fe3          	beqz	s7,42010ee6 <decoder_task+0x5ee>
4201136c:	bce1                	j	42010e44 <decoder_task+0x54c>
4201136e:	fe377097          	auipc	ra,0xfe377
42011372:	04c080e7          	jalr	76(ra) # 403883ba <esp_log_timestamp>
42011376:	3c1267b7          	lui	a5,0x3c126
4201137a:	82078713          	addi	a4,a5,-2016 # 3c125820 <_esp_trace_encoder_array_end+0x5700>
4201137e:	3c1267b7          	lui	a5,0x3c126
42011382:	86aa                	mv	a3,a0
42011384:	85ba                	mv	a1,a4
42011386:	a7478613          	addi	a2,a5,-1420 # 3c125a74 <_esp_trace_encoder_array_end+0x5954>
4201138a:	4505                	li	a0,1
4201138c:	fe377097          	auipc	ra,0xfe377
42011390:	f26080e7          	jalr	-218(ra) # 403882b2 <esp_log>
42011394:	3fc957b7          	lui	a5,0x3fc95
42011398:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
4201139c:	3c1267b7          	lui	a5,0x3c126
420113a0:	a0478693          	addi	a3,a5,-1532 # 3c125a04 <_esp_trace_encoder_array_end+0x58e4>
420113a4:	85a6                	mv	a1,s1
420113a6:	4601                	li	a2,0
420113a8:	420040ef          	jal	420157c8 <native_state_set_audio>
420113ac:	8c26                	mv	s8,s1
420113ae:	4981                	li	s3,0
420113b0:	4901                	li	s2,0
420113b2:	4a01                	li	s4,0
420113b4:	4d81                	li	s11,0
420113b6:	855e                	mv	a0,s7
420113b8:	362240ef          	jal	4203571a <custom_flac_decoder_destroy>
420113bc:	4b81                	li	s7,0
420113be:	be15                	j	42010ef2 <decoder_task+0x5fa>
420113c0:	8542                	mv	a0,a6
420113c2:	b0e5                	j	42010caa <decoder_task+0x3b2>
420113c4:	3c1267b7          	lui	a5,0x3c126
420113c8:	81878793          	addi	a5,a5,-2024 # 3c125818 <_esp_trace_encoder_array_end+0x56f8>
420113cc:	f08ff06f          	j	42010ad4 <decoder_task+0x1dc>
420113d0:	01a14d83          	lbu	s11,26(sp)
420113d4:	ae0d85e3          	beqz	s11,42010ebe <decoder_task+0x5c6>
420113d8:	3c1267b7          	lui	a5,0x3c126
420113dc:	b0078513          	addi	a0,a5,-1280 # 3c125b00 <_esp_trace_encoder_array_end+0x59e0>
420113e0:	f39fe0ef          	jal	42010318 <log_runtime_memory>
420113e4:	bce1                	j	42010ebc <decoder_task+0x5c4>
420113e6:	3c1267b7          	lui	a5,0x3c126
420113ea:	81878593          	addi	a1,a5,-2024 # 3c125818 <_esp_trace_encoder_array_end+0x56f8>
420113ee:	b919                	j	42011004 <decoder_task+0x70c>
420113f0:	fe377097          	auipc	ra,0xfe377
420113f4:	fca080e7          	jalr	-54(ra) # 403883ba <esp_log_timestamp>
420113f8:	3c1267b7          	lui	a5,0x3c126
420113fc:	82078713          	addi	a4,a5,-2016 # 3c125820 <_esp_trace_encoder_array_end+0x5700>
42011400:	3c126637          	lui	a2,0x3c126
42011404:	3c1267b7          	lui	a5,0x3c126
42011408:	86aa                	mv	a3,a0
4201140a:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
4201140e:	85ba                	mv	a1,a4
42011410:	ad860613          	addi	a2,a2,-1320 # 3c125ad8 <_esp_trace_encoder_array_end+0x59b8>
42011414:	5879                	li	a6,-2
42011416:	4505                	li	a0,1
42011418:	fe377097          	auipc	ra,0xfe377
4201141c:	e9a080e7          	jalr	-358(ra) # 403882b2 <esp_log>
42011420:	3c1267b7          	lui	a5,0x3c126
42011424:	8922                	mv	s2,s0
42011426:	a0478693          	addi	a3,a5,-1532 # 3c125a04 <_esp_trace_encoder_array_end+0x58e4>
4201142a:	ed6ff06f          	j	42010b00 <decoder_task+0x208>
4201142e:	fe377097          	auipc	ra,0xfe377
42011432:	f8c080e7          	jalr	-116(ra) # 403883ba <esp_log_timestamp>
42011436:	3c1267b7          	lui	a5,0x3c126
4201143a:	86aa                	mv	a3,a0
4201143c:	81078793          	addi	a5,a5,-2032 # 3c125810 <_esp_trace_encoder_array_end+0x56f0>
42011440:	e94ff06f          	j	42010ad4 <decoder_task+0x1dc>
42011444:	3c1267b7          	lui	a5,0x3c126
42011448:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
4201144c:	bdf9                	j	4201132a <decoder_task+0xa32>
4201144e:	3c1267b7          	lui	a5,0x3c126
42011452:	81078593          	addi	a1,a5,-2032 # 3c125810 <_esp_trace_encoder_array_end+0x56f0>
42011456:	b67d                	j	42011004 <decoder_task+0x70c>
42011458:	3c1267b7          	lui	a5,0x3c126
4201145c:	80478593          	addi	a1,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
42011460:	b655                	j	42011004 <decoder_task+0x70c>
42011462:	3fc957b7          	lui	a5,0x3fc95
42011466:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
4201146a:	3c1267b7          	lui	a5,0x3c126
4201146e:	b6078693          	addi	a3,a5,-1184 # 3c125b60 <_esp_trace_encoder_array_end+0x5a40>
42011472:	4601                	li	a2,0
42011474:	85a6                	mv	a1,s1
42011476:	352040ef          	jal	420157c8 <native_state_set_audio>
4201147a:	8c26                	mv	s8,s1
4201147c:	bb69                	j	42011216 <decoder_task+0x91e>
4201147e:	3c1267b7          	lui	a5,0x3c126
42011482:	81078793          	addi	a5,a5,-2032 # 3c125810 <_esp_trace_encoder_array_end+0x56f0>
42011486:	b52d                	j	420112b0 <decoder_task+0x9b8>
42011488:	4c32                	lw	s8,12(sp)
4201148a:	fe377097          	auipc	ra,0xfe377
4201148e:	f30080e7          	jalr	-208(ra) # 403883ba <esp_log_timestamp>
42011492:	3c1267b7          	lui	a5,0x3c126
42011496:	82078713          	addi	a4,a5,-2016 # 3c125820 <_esp_trace_encoder_array_end+0x5700>
4201149a:	3c1267b7          	lui	a5,0x3c126
4201149e:	86aa                	mv	a3,a0
420114a0:	85ba                	mv	a1,a4
420114a2:	bec78613          	addi	a2,a5,-1044 # 3c125bec <_esp_trace_encoder_array_end+0x5acc>
420114a6:	4509                	li	a0,2
420114a8:	fe377097          	auipc	ra,0xfe377
420114ac:	e0a080e7          	jalr	-502(ra) # 403882b2 <esp_log>
420114b0:	4d85                	li	s11,1
420114b2:	b86d                	j	42010d6c <decoder_task+0x474>
420114b4:	8462                	mv	s0,s8
420114b6:	b9f5                	j	420111b2 <decoder_task+0x8ba>
420114b8:	3c1267b7          	lui	a5,0x3c126
420114bc:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
420114c0:	bb31                	j	420111dc <decoder_task+0x8e4>
420114c2:	3c1267b7          	lui	a5,0x3c126
420114c6:	81078793          	addi	a5,a5,-2032 # 3c125810 <_esp_trace_encoder_array_end+0x56f0>
420114ca:	bb09                	j	420111dc <decoder_task+0x8e4>
420114cc:	3c1267b7          	lui	a5,0x3c126
420114d0:	81078793          	addi	a5,a5,-2032 # 3c125810 <_esp_trace_encoder_array_end+0x56f0>
420114d4:	bd99                	j	4201132a <decoder_task+0xa32>
420114d6:	fe377097          	auipc	ra,0xfe377
420114da:	ee4080e7          	jalr	-284(ra) # 403883ba <esp_log_timestamp>
420114de:	4789                	li	a5,2
420114e0:	4405                	li	s0,1
420114e2:	86aa                	mv	a3,a0
420114e4:	0afb0563          	beq	s6,a5,4201158e <decoder_task+0xc96>
420114e8:	4791                	li	a5,4
420114ea:	0afb0d63          	beq	s6,a5,420115a4 <decoder_task+0xcac>
420114ee:	3c1267b7          	lui	a5,0x3c126
420114f2:	81478793          	addi	a5,a5,-2028 # 3c125814 <_esp_trace_encoder_array_end+0x56f4>
420114f6:	008b0663          	beq	s6,s0,42011502 <decoder_task+0xc0a>
420114fa:	3c1267b7          	lui	a5,0x3c126
420114fe:	81878793          	addi	a5,a5,-2024 # 3c125818 <_esp_trace_encoder_array_end+0x56f8>
42011502:	3c126737          	lui	a4,0x3c126
42011506:	82070713          	addi	a4,a4,-2016 # 3c125820 <_esp_trace_encoder_array_end+0x5700>
4201150a:	3c126637          	lui	a2,0x3c126
4201150e:	85ba                	mv	a1,a4
42011510:	c0c60613          	addi	a2,a2,-1012 # 3c125c0c <_esp_trace_encoder_array_end+0x5aec>
42011514:	4505                	li	a0,1
42011516:	fe377097          	auipc	ra,0xfe377
4201151a:	d9c080e7          	jalr	-612(ra) # 403882b2 <esp_log>
4201151e:	3fc957b7          	lui	a5,0x3fc95
42011522:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42011526:	3c1267b7          	lui	a5,0x3c126
4201152a:	c3c78693          	addi	a3,a5,-964 # 3c125c3c <_esp_trace_encoder_array_end+0x5b1c>
4201152e:	85a6                	mv	a1,s1
42011530:	4601                	li	a2,0
42011532:	296040ef          	jal	420157c8 <native_state_set_audio>
42011536:	8c26                	mv	s8,s1
42011538:	b9f9                	j	42011216 <decoder_task+0x91e>
4201153a:	fe377097          	auipc	ra,0xfe377
4201153e:	e80080e7          	jalr	-384(ra) # 403883ba <esp_log_timestamp>
42011542:	3c126737          	lui	a4,0x3c126
42011546:	82070713          	addi	a4,a4,-2016 # 3c125820 <_esp_trace_encoder_array_end+0x5700>
4201154a:	3c126637          	lui	a2,0x3c126
4201154e:	86aa                	mv	a3,a0
42011550:	87a2                	mv	a5,s0
42011552:	85ba                	mv	a1,a4
42011554:	b1860613          	addi	a2,a2,-1256 # 3c125b18 <_esp_trace_encoder_array_end+0x59f8>
42011558:	4509                	li	a0,2
4201155a:	fe377097          	auipc	ra,0xfe377
4201155e:	d58080e7          	jalr	-680(ra) # 403882b2 <esp_log>
42011562:	3c126737          	lui	a4,0x3c126
42011566:	0419                	addi	s0,s0,6 # 3006 <CSR_UINTSTATUS+0x2355>
42011568:	4785                	li	a5,1
4201156a:	a2070693          	addi	a3,a4,-1504 # 3c125a20 <_esp_trace_encoder_array_end+0x5900>
4201156e:	0087e663          	bltu	a5,s0,4201157a <decoder_task+0xc82>
42011572:	3c1267b7          	lui	a5,0x3c126
42011576:	a0478693          	addi	a3,a5,-1532 # 3c125a04 <_esp_trace_encoder_array_end+0x58e4>
4201157a:	3fc957b7          	lui	a5,0x3fc95
4201157e:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42011582:	4601                	li	a2,0
42011584:	85a6                	mv	a1,s1
42011586:	242040ef          	jal	420157c8 <native_state_set_audio>
4201158a:	8c26                	mv	s8,s1
4201158c:	baa9                	j	42010ee6 <decoder_task+0x5ee>
4201158e:	3c1267b7          	lui	a5,0x3c126
42011592:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
42011596:	b7b5                	j	42011502 <decoder_task+0xc0a>
42011598:	3c1267b7          	lui	a5,0x3c126
4201159c:	a0478693          	addi	a3,a5,-1532 # 3c125a04 <_esp_trace_encoder_array_end+0x58e4>
420115a0:	d60ff06f          	j	42010b00 <decoder_task+0x208>
420115a4:	3c1267b7          	lui	a5,0x3c126
420115a8:	81078793          	addi	a5,a5,-2032 # 3c125810 <_esp_trace_encoder_array_end+0x56f0>
420115ac:	bf99                	j	42011502 <decoder_task+0xc0a>
420115ae:	fe377097          	auipc	ra,0xfe377
420115b2:	e0c080e7          	jalr	-500(ra) # 403883ba <esp_log_timestamp>
420115b6:	3c1267b7          	lui	a5,0x3c126
420115ba:	86aa                	mv	a3,a0
420115bc:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
420115c0:	b9c5                	j	420112b0 <decoder_task+0x9b8>
