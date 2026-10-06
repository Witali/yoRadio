
idf\esp32c3-oled-native\build-flac-depths\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42010854 <decoder_task>:
42010854:	7151                	addi	sp,sp,-240
42010856:	d5a2                	sw	s0,232(sp)
42010858:	d3a6                	sw	s1,228(sp)
4201085a:	d1ca                	sw	s2,224(sp)
4201085c:	cfce                	sw	s3,220(sp)
4201085e:	cdd2                	sw	s4,216(sp)
42010860:	cbd6                	sw	s5,212(sp)
42010862:	c9da                	sw	s6,208(sp)
42010864:	c7de                	sw	s7,204(sp)
42010866:	c5e2                	sw	s8,200(sp)
42010868:	df6e                	sw	s11,188(sp)
4201086a:	d786                	sw	ra,236(sp)
4201086c:	c3e6                	sw	s9,196(sp)
4201086e:	c1ea                	sw	s10,192(sp)
42010870:	605010ef          	jal	42012674 <decoder_register_codecs>
42010874:	3fc95737          	lui	a4,0x3fc95
42010878:	000f47b7          	lui	a5,0xf4
4201087c:	ad870713          	addi	a4,a4,-1320 # 3fc94ad8 <s_bitrate_updated_us>
42010880:	24078793          	addi	a5,a5,576 # f4240 <CSR_UINTSTATUS+0xf358f>
42010884:	ce02                	sw	zero,28(sp)
42010886:	c102                	sw	zero,128(sp)
42010888:	c302                	sw	zero,132(sp)
4201088a:	c502                	sw	zero,136(sp)
4201088c:	c702                	sw	zero,140(sp)
4201088e:	c902                	sw	zero,144(sp)
42010890:	cb02                	sw	zero,148(sp)
42010892:	cd02                	sw	zero,152(sp)
42010894:	cf02                	sw	zero,156(sp)
42010896:	d102                	sw	zero,160(sp)
42010898:	d302                	sw	zero,164(sp)
4201089a:	d502                	sw	zero,168(sp)
4201089c:	d702                	sw	zero,172(sp)
4201089e:	d202                	sw	zero,36(sp)
420108a0:	d402                	sw	zero,40(sp)
420108a2:	d602                	sw	zero,44(sp)
420108a4:	d802                	sw	zero,48(sp)
420108a6:	00010d23          	sb	zero,26(sp)
420108aa:	842a                	mv	s0,a0
420108ac:	c23a                	sw	a4,4(sp)
420108ae:	c43e                	sw	a5,8(sp)
420108b0:	4981                	li	s3,0
420108b2:	4a01                	li	s4,0
420108b4:	4901                	li	s2,0
420108b6:	4d81                	li	s11,0
420108b8:	4b01                	li	s6,0
420108ba:	4c01                	li	s8,0
420108bc:	4481                	li	s1,0
420108be:	4b81                	li	s7,0
420108c0:	3fc95ab7          	lui	s5,0x3fc95
420108c4:	af0a8793          	addi	a5,s5,-1296 # 3fc94af0 <s_generation>
420108c8:	0330000f          	fence	rw,rw
420108cc:	0007ac83          	lw	s9,0(a5)
420108d0:	0230000f          	fence	r,rw
420108d4:	409c8f63          	beq	s9,s1,42010cf2 <decoder_task+0x49e>
420108d8:	3fc957b7          	lui	a5,0x3fc95
420108dc:	aec78793          	addi	a5,a5,-1300 # 3fc94aec <s_decoder_target_codec>
420108e0:	0330000f          	fence	rw,rw
420108e4:	4384                	lw	s1,0(a5)
420108e6:	0230000f          	fence	r,rw
420108ea:	4572                	lw	a0,28(sp)
420108ec:	c119                	beqz	a0,420108f2 <decoder_task+0x9e>
420108ee:	2d5270ef          	jal	420383c2 <esp_audio_simple_dec_close>
420108f2:	854e                	mv	a0,s3
420108f4:	ce02                	sw	zero,28(sp)
420108f6:	5e1010ef          	jal	420126d6 <native_aac_decoder_destroy>
420108fa:	000b8563          	beqz	s7,42010904 <decoder_task+0xb0>
420108fe:	855e                	mv	a0,s7
42010900:	64a240ef          	jal	42034f4a <custom_flac_decoder_destroy>
42010904:	46048c63          	beqz	s1,42010d7c <decoder_task+0x528>
42010908:	d202                	sw	zero,36(sp)
4201090a:	d402                	sw	zero,40(sp)
4201090c:	d602                	sw	zero,44(sp)
4201090e:	d802                	sw	zero,48(sp)
42010910:	00010d23          	sb	zero,26(sp)
42010914:	3fc957b7          	lui	a5,0x3fc95
42010918:	ae878793          	addi	a5,a5,-1304 # 3fc94ae8 <s_decoder_released_generation>
4201091c:	0310000f          	fence	rw,w
42010920:	0197a023          	sw	s9,0(a5)
42010924:	0330000f          	fence	rw,rw
42010928:	4b81                	li	s7,0
4201092a:	84e6                	mv	s1,s9
4201092c:	4c01                	li	s8,0
4201092e:	4b01                	li	s6,0
42010930:	4d81                	li	s11,0
42010932:	4981                	li	s3,0
42010934:	3fc957b7          	lui	a5,0x3fc95
42010938:	afc7a503          	lw	a0,-1284(a5) # 3fc94afc <s_encoded>
4201093c:	4651                	li	a2,20
4201093e:	100c                	addi	a1,sp,32
42010940:	d002                	sw	zero,32(sp)
42010942:	566670ef          	jal	42077ea8 <xRingbufferReceive>
42010946:	8caa                	mv	s9,a0
42010948:	dd35                	beqz	a0,420108c4 <decoder_task+0x70>
4201094a:	4118                	lw	a4,0(a0)
4201094c:	af0a8793          	addi	a5,s5,-1296
42010950:	0330000f          	fence	rw,rw
42010954:	439c                	lw	a5,0(a5)
42010956:	0230000f          	fence	r,rw
4201095a:	40f71963          	bne	a4,a5,42010d6c <decoder_task+0x518>
4201095e:	411c                	lw	a5,0(a0)
42010960:	41878663          	beq	a5,s8,42010d6c <decoder_task+0x518>
42010964:	4158                	lw	a4,4(a0)
42010966:	e709                	bnez	a4,42010970 <decoder_task+0x11c>
42010968:	00a54703          	lbu	a4,10(a0)
4201096c:	3e071c63          	bnez	a4,42010d64 <decoder_task+0x510>
42010970:	12041563          	bnez	s0,42010a9a <decoder_task+0x246>
42010974:	12f48c63          	beq	s1,a5,42010aac <decoder_task+0x258>
42010978:	4572                	lw	a0,28(sp)
4201097a:	c119                	beqz	a0,42010980 <decoder_task+0x12c>
4201097c:	247270ef          	jal	420383c2 <esp_audio_simple_dec_close>
42010980:	854e                	mv	a0,s3
42010982:	ce02                	sw	zero,28(sp)
42010984:	553010ef          	jal	420126d6 <native_aac_decoder_destroy>
42010988:	000b8563          	beqz	s7,42010992 <decoder_task+0x13e>
4201098c:	855e                	mv	a0,s7
4201098e:	5bc240ef          	jal	42034f4a <custom_flac_decoder_destroy>
42010992:	4712                	lw	a4,4(sp)
42010994:	000ca483          	lw	s1,0(s9)
42010998:	004cab03          	lw	s6,4(s9)
4201099c:	3fc957b7          	lui	a5,0x3fc95
420109a0:	ae07a023          	sw	zero,-1312(a5) # 3fc94ae0 <s_published_bitrate_bps>
420109a4:	4801                	li	a6,0
420109a6:	4781                	li	a5,0
420109a8:	c31c                	sw	a5,0(a4)
420109aa:	00010d23          	sb	zero,26(sp)
420109ae:	01072223          	sw	a6,4(a4)
420109b2:	fe371097          	auipc	ra,0xfe371
420109b6:	988080e7          	jalr	-1656(ra) # 4038133a <esp_timer_get_time>
420109ba:	c52a                	sw	a0,136(sp)
420109bc:	c902                	sw	zero,144(sp)
420109be:	cb02                	sw	zero,148(sp)
420109c0:	cd02                	sw	zero,152(sp)
420109c2:	cf02                	sw	zero,156(sp)
420109c4:	d102                	sw	zero,160(sp)
420109c6:	d302                	sw	zero,164(sp)
420109c8:	d502                	sw	zero,168(sp)
420109ca:	d702                	sw	zero,172(sp)
420109cc:	c126                	sw	s1,128(sp)
420109ce:	c35a                	sw	s6,132(sp)
420109d0:	c72e                	sw	a1,140(sp)
420109d2:	478d                	li	a5,3
420109d4:	3afb0a63          	beq	s6,a5,42010d88 <decoder_task+0x534>
420109d8:	4789                	li	a5,2
420109da:	48fb0163          	beq	s6,a5,42010e5c <decoder_task+0x608>
420109de:	640d                	lui	s0,0x3
420109e0:	7e8a7e63          	bgeu	s4,s0,420111dc <decoder_task+0x988>
420109e4:	85a2                	mv	a1,s0
420109e6:	854a                	mv	a0,s2
420109e8:	b19f70ef          	jal	42008500 <realloc>
420109ec:	7e050d63          	beqz	a0,420111e6 <decoder_task+0x992>
420109f0:	d682                	sw	zero,108(sp)
420109f2:	d882                	sw	zero,112(sp)
420109f4:	da82                	sw	zero,116(sp)
420109f6:	892a                	mv	s2,a0
420109f8:	8a22                	mv	s4,s0
420109fa:	4791                	li	a5,4
420109fc:	7afb0463          	beq	s6,a5,420111a4 <decoder_task+0x950>
42010a00:	203357b7          	lui	a5,0x20335
42010a04:	04d78793          	addi	a5,a5,77 # 2033504d <CSR_UINTSTATUS+0x2033439c>
42010a08:	086c                	addi	a1,sp,28
42010a0a:	10a8                	addi	a0,sp,104
42010a0c:	d4be                	sw	a5,104(sp)
42010a0e:	7dc150ef          	jal	420261ea <__wrap_esp_audio_simple_dec_open>
42010a12:	842a                	mv	s0,a0
42010a14:	7a050463          	beqz	a0,420111bc <decoder_task+0x968>
42010a18:	fe378097          	auipc	ra,0xfe378
42010a1c:	9a2080e7          	jalr	-1630(ra) # 403883ba <esp_log_timestamp>
42010a20:	3c1267b7          	lui	a5,0x3c126
42010a24:	4985                	li	s3,1
42010a26:	86aa                	mv	a3,a0
42010a28:	80078793          	addi	a5,a5,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
42010a2c:	0f3b1ae3          	bne	s6,s3,42011320 <decoder_task+0xacc>
42010a30:	3c126737          	lui	a4,0x3c126
42010a34:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
42010a38:	3c126637          	lui	a2,0x3c126
42010a3c:	85ba                	mv	a1,a4
42010a3e:	8822                	mv	a6,s0
42010a40:	ac460613          	addi	a2,a2,-1340 # 3c125ac4 <_esp_trace_encoder_array_end+0x59a4>
42010a44:	4505                	li	a0,1
42010a46:	fe378097          	auipc	ra,0xfe378
42010a4a:	86c080e7          	jalr	-1940(ra) # 403882b2 <esp_log>
42010a4e:	3c126737          	lui	a4,0x3c126
42010a52:	57f9                	li	a5,-2
42010a54:	9fc70693          	addi	a3,a4,-1540 # 3c1259fc <_esp_trace_encoder_array_end+0x58dc>
42010a58:	28f40ee3          	beq	s0,a5,420114f4 <decoder_task+0xca0>
42010a5c:	3fc957b7          	lui	a5,0x3fc95
42010a60:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42010a64:	4601                	li	a2,0
42010a66:	85a6                	mv	a1,s1
42010a68:	7a6040ef          	jal	4201520e <native_state_set_audio>
42010a6c:	4572                	lw	a0,28(sp)
42010a6e:	c501                	beqz	a0,42010a76 <decoder_task+0x222>
42010a70:	153270ef          	jal	420383c2 <esp_audio_simple_dec_close>
42010a74:	ce02                	sw	zero,28(sp)
42010a76:	854a                	mv	a0,s2
42010a78:	a8df70ef          	jal	42008504 <cfree>
42010a7c:	8c26                	mv	s8,s1
42010a7e:	4a01                	li	s4,0
42010a80:	4901                	li	s2,0
42010a82:	4b81                	li	s7,0
42010a84:	4d81                	li	s11,0
42010a86:	3fc957b7          	lui	a5,0x3fc95
42010a8a:	afc7a503          	lw	a0,-1284(a5) # 3fc94afc <s_encoded>
42010a8e:	85e6                	mv	a1,s9
42010a90:	4981                	li	s3,0
42010a92:	492670ef          	jal	42077f24 <vRingbufferReturnItem>
42010a96:	4401                	li	s0,0
42010a98:	b535                	j	420108c4 <decoder_task+0x70>
42010a9a:	3db010ef          	jal	42012674 <decoder_register_codecs>
42010a9e:	842a                	mv	s0,a0
42010aa0:	26051e63          	bnez	a0,42010d1c <decoder_task+0x4c8>
42010aa4:	000ca783          	lw	a5,0(s9)
42010aa8:	ecf498e3          	bne	s1,a5,42010978 <decoder_task+0x124>
42010aac:	004ca783          	lw	a5,4(s9)
42010ab0:	ed6794e3          	bne	a5,s6,42010978 <decoder_task+0x124>
42010ab4:	478d                	li	a5,3
42010ab6:	00fb07e3          	beq	s6,a5,420112c4 <decoder_task+0xa70>
42010aba:	47f2                	lw	a5,28(sp)
42010abc:	00f9e7b3          	or	a5,s3,a5
42010ac0:	d3f9                	beqz	a5,42010a86 <decoder_task+0x232>
42010ac2:	008cd783          	lhu	a5,8(s9)
42010ac6:	00bc8713          	addi	a4,s9,11
42010aca:	ce82                	sw	zero,92(sp)
42010acc:	d082                	sw	zero,96(sp)
42010ace:	d282                	sw	zero,100(sp)
42010ad0:	ccbe                	sw	a5,88(sp)
42010ad2:	caba                	sw	a4,84(sp)
42010ad4:	00acc703          	lbu	a4,10(s9)
42010ad8:	ffeb0693          	addi	a3,s6,-2
42010adc:	0016b693          	seqz	a3,a3
42010ae0:	00e03733          	snez	a4,a4
42010ae4:	c036                	sw	a3,0(sp)
42010ae6:	04e10e23          	sb	a4,92(sp)
42010aea:	3a098463          	beqz	s3,42010e92 <decoder_task+0x63e>
42010aee:	e789                	bnez	a5,42010af8 <decoder_task+0x2a4>
42010af0:	05c14783          	lbu	a5,92(sp)
42010af4:	1c078a63          	beqz	a5,42010cc8 <decoder_task+0x474>
42010af8:	4781                	li	a5,0
42010afa:	4801                	li	a6,0
42010afc:	de3e                	sw	a5,60(sp)
42010afe:	c0c2                	sw	a6,64(sp)
42010b00:	da4a                	sw	s2,52(sp)
42010b02:	dc52                	sw	s4,56(sp)
42010b04:	d082                	sw	zero,96(sp)
42010b06:	fe371097          	auipc	ra,0xfe371
42010b0a:	834080e7          	jalr	-1996(ra) # 4038133a <esp_timer_get_time>
42010b0e:	842a                	mv	s0,a0
42010b10:	1850                	addi	a2,sp,52
42010b12:	08cc                	addi	a1,sp,84
42010b14:	854e                	mv	a0,s3
42010b16:	3f7010ef          	jal	4201270c <native_aac_decoder_process>
42010b1a:	8d2a                	mv	s10,a0
42010b1c:	fe371097          	auipc	ra,0xfe371
42010b20:	81e080e7          	jalr	-2018(ra) # 4038133a <esp_timer_get_time>
42010b24:	47ca                	lw	a5,144(sp)
42010b26:	46da                	lw	a3,148(sp)
42010b28:	8d01                	sub	a0,a0,s0
42010b2a:	00a78733          	add	a4,a5,a0
42010b2e:	00f737b3          	sltu	a5,a4,a5
42010b32:	97b6                	add	a5,a5,a3
42010b34:	cb3e                	sw	a5,148(sp)
42010b36:	578a                	lw	a5,160(sp)
42010b38:	c93a                	sw	a4,144(sp)
42010b3a:	571a                	lw	a4,164(sp)
42010b3c:	0785                	addi	a5,a5,1
42010b3e:	d13e                	sw	a5,160(sp)
42010b40:	00a77363          	bgeu	a4,a0,42010b46 <decoder_task+0x2f2>
42010b44:	d32a                	sw	a0,164(sp)
42010b46:	8bfd                	andi	a5,a5,31
42010b48:	56078763          	beqz	a5,420110b6 <decoder_task+0x862>
42010b4c:	af0a8793          	addi	a5,s5,-1296
42010b50:	0330000f          	fence	rw,rw
42010b54:	439c                	lw	a5,0(a5)
42010b56:	0230000f          	fence	r,rw
42010b5a:	16979763          	bne	a5,s1,42010cc8 <decoder_task+0x474>
42010b5e:	57e1                	li	a5,-8
42010b60:	52fd0563          	beq	s10,a5,4201108a <decoder_task+0x836>
42010b64:	5a0d1463          	bnez	s10,4201110c <decoder_task+0x8b8>
42010b68:	5786                	lw	a5,96(sp)
42010b6a:	4766                	lw	a4,88(sp)
42010b6c:	6ef76863          	bltu	a4,a5,4201125c <decoder_task+0xa08>
42010b70:	8f1d                	sub	a4,a4,a5
42010b72:	56aa                	lw	a3,168(sp)
42010b74:	ccba                	sw	a4,88(sp)
42010b76:	4756                	lw	a4,84(sp)
42010b78:	96be                	add	a3,a3,a5
42010b7a:	d536                	sw	a3,168(sp)
42010b7c:	97ba                	add	a5,a5,a4
42010b7e:	4706                	lw	a4,64(sp)
42010b80:	cabe                	sw	a5,84(sp)
42010b82:	10070c63          	beqz	a4,42010c9a <decoder_task+0x446>
42010b86:	00cc                	addi	a1,sp,68
42010b88:	854e                	mv	a0,s3
42010b8a:	c282                	sw	zero,68(sp)
42010b8c:	c482                	sw	zero,72(sp)
42010b8e:	c682                	sw	zero,76(sp)
42010b90:	c882                	sw	zero,80(sp)
42010b92:	6a3010ef          	jal	42012a34 <native_aac_decoder_get_info>
42010b96:	52051663          	bnez	a0,420110c2 <decoder_task+0x86e>
42010b9a:	4782                	lw	a5,0(sp)
42010b9c:	01b10613          	addi	a2,sp,27
42010ba0:	00cc                	addi	a1,sp,68
42010ba2:	854e                	mv	a0,s3
42010ba4:	00f10da3          	sb	a5,27(sp)
42010ba8:	69b010ef          	jal	42012a42 <native_aac_decoder_label>
42010bac:	01b14683          	lbu	a3,27(sp)
42010bb0:	842a                	mv	s0,a0
42010bb2:	4501                	li	a0,0
42010bb4:	5e068063          	beqz	a3,42011194 <decoder_task+0x940>
42010bb8:	af0a8793          	addi	a5,s5,-1296
42010bbc:	0330000f          	fence	rw,rw
42010bc0:	4398                	lw	a4,0(a5)
42010bc2:	0230000f          	fence	r,rw
42010bc6:	4781                	li	a5,0
42010bc8:	06971163          	bne	a4,s1,42010c2a <decoder_task+0x3d6>
42010bcc:	4716                	lw	a4,68(sp)
42010bce:	cf31                	beqz	a4,42010c2a <decoder_task+0x3d6>
42010bd0:	04914803          	lbu	a6,73(sp)
42010bd4:	04080b63          	beqz	a6,42010c2a <decoder_task+0x3d6>
42010bd8:	04814603          	lbu	a2,72(sp)
42010bdc:	c639                	beqz	a2,42010c2a <decoder_task+0x3d6>
42010bde:	45a6                	lw	a1,72(sp)
42010be0:	47b6                	lw	a5,76(sp)
42010be2:	d23a                	sw	a4,36(sp)
42010be4:	d42e                	sw	a1,40(sp)
42010be6:	45c6                	lw	a1,80(sp)
42010be8:	d63e                	sw	a5,44(sp)
42010bea:	4785                	li	a5,1
42010bec:	06012923          	sw	zero,114(sp)
42010bf0:	06012b23          	sw	zero,118(sp)
42010bf4:	06011d23          	sh	zero,122(sp)
42010bf8:	d4a2                	sw	s0,104(sp)
42010bfa:	d6ba                	sw	a4,108(sp)
42010bfc:	d82e                	sw	a1,48(sp)
42010bfe:	00f10d23          	sb	a5,26(sp)
42010c02:	70050d63          	beqz	a0,4201131c <decoder_task+0xac8>
42010c06:	3fc957b7          	lui	a5,0x3fc95
42010c0a:	06a10823          	sb	a0,112(sp)
42010c0e:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42010c12:	06c108a3          	sb	a2,113(sp)
42010c16:	85a6                	mv	a1,s1
42010c18:	10b0                	addi	a2,sp,104
42010c1a:	daba                	sw	a4,116(sp)
42010c1c:	07010c23          	sb	a6,120(sp)
42010c20:	06d10d23          	sb	a3,122(sp)
42010c24:	6ca040ef          	jal	420152ee <native_state_set_stream_info>
42010c28:	4785                	li	a5,1
42010c2a:	45b6                	lw	a1,76(sp)
42010c2c:	8526                	mv	a0,s1
42010c2e:	00f10d23          	sb	a5,26(sp)
42010c32:	fe2ff0ef          	jal	42010414 <state_set_decoder_bitrate>
42010c36:	01a14783          	lbu	a5,26(sp)
42010c3a:	c3a5                	beqz	a5,42010c9a <decoder_task+0x446>
42010c3c:	4c0d8163          	beqz	s11,420110fe <decoder_task+0x8aa>
42010c40:	02814503          	lbu	a0,40(sp)
42010c44:	02914783          	lbu	a5,41(sp)
42010c48:	4406                	lw	s0,64(sp)
42010c4a:	051d                	addi	a0,a0,7
42010c4c:	810d                	srli	a0,a0,0x3
42010c4e:	02f50533          	mul	a0,a0,a5
42010c52:	c91d                	beqz	a0,42010c88 <decoder_task+0x434>
42010c54:	5612                	lw	a2,36(sp)
42010c56:	ca0d                	beqz	a2,42010c88 <decoder_task+0x434>
42010c58:	02a45533          	divu	a0,s0,a0
42010c5c:	47a2                	lw	a5,8(sp)
42010c5e:	4681                	li	a3,0
42010c60:	02f535b3          	mulhu	a1,a0,a5
42010c64:	02f50533          	mul	a0,a0,a5
42010c68:	fdff0097          	auipc	ra,0xfdff0
42010c6c:	c44080e7          	jalr	-956(ra) # 400008ac <__udivdi3>
42010c70:	47ea                	lw	a5,152(sp)
42010c72:	46fa                	lw	a3,156(sp)
42010c74:	573a                	lw	a4,172(sp)
42010c76:	953e                	add	a0,a0,a5
42010c78:	96ae                	add	a3,a3,a1
42010c7a:	00f537b3          	sltu	a5,a0,a5
42010c7e:	97b6                	add	a5,a5,a3
42010c80:	9722                	add	a4,a4,s0
42010c82:	cf3e                	sw	a5,156(sp)
42010c84:	cd2a                	sw	a0,152(sp)
42010c86:	d73a                	sw	a4,172(sp)
42010c88:	86a2                	mv	a3,s0
42010c8a:	864a                	mv	a2,s2
42010c8c:	104c                	addi	a1,sp,36
42010c8e:	8526                	mv	a0,s1
42010c90:	e48ff0ef          	jal	420102d8 <send_pcm>
42010c94:	8daa                	mv	s11,a0
42010c96:	74050863          	beqz	a0,420113e6 <decoder_task+0xb92>
42010c9a:	fe370097          	auipc	ra,0xfe370
42010c9e:	6a0080e7          	jalr	1696(ra) # 4038133a <esp_timer_get_time>
42010ca2:	862e                	mv	a2,a1
42010ca4:	85aa                	mv	a1,a0
42010ca6:	0108                	addi	a0,sp,128
42010ca8:	9b2ff0ef          	jal	4200fe5a <decode_stats_report>
42010cac:	4706                	lw	a4,64(sp)
42010cae:	5786                	lw	a5,96(sp)
42010cb0:	05c14683          	lbu	a3,92(sp)
42010cb4:	8fd9                	or	a5,a5,a4
42010cb6:	3c079463          	bnez	a5,4201107e <decoder_task+0x82a>
42010cba:	76068c63          	beqz	a3,42011432 <decoder_task+0xbde>
42010cbe:	4701                	li	a4,0
42010cc0:	47e6                	lw	a5,88(sp)
42010cc2:	8f5d                	or	a4,a4,a5
42010cc4:	e20715e3          	bnez	a4,42010aee <decoder_task+0x29a>
42010cc8:	00acc783          	lbu	a5,10(s9)
42010ccc:	4a079363          	bnez	a5,42011172 <decoder_task+0x91e>
42010cd0:	4a9c0163          	beq	s8,s1,42011172 <decoder_task+0x91e>
42010cd4:	8566                	mv	a0,s9
42010cd6:	85e2                	mv	a1,s8
42010cd8:	ab5ff0ef          	jal	4201078c <return_decoded_packet>
42010cdc:	4401                	li	s0,0
42010cde:	af0a8793          	addi	a5,s5,-1296
42010ce2:	0330000f          	fence	rw,rw
42010ce6:	0007ac83          	lw	s9,0(a5)
42010cea:	0230000f          	fence	r,rw
42010cee:	be9c95e3          	bne	s9,s1,420108d8 <decoder_task+0x84>
42010cf2:	c40c01e3          	beqz	s8,42010934 <decoder_task+0xe0>
42010cf6:	c29c1fe3          	bne	s8,s1,42010934 <decoder_task+0xe0>
42010cfa:	4572                	lw	a0,28(sp)
42010cfc:	c119                	beqz	a0,42010d02 <decoder_task+0x4ae>
42010cfe:	6c4270ef          	jal	420383c2 <esp_audio_simple_dec_close>
42010d02:	ce02                	sw	zero,28(sp)
42010d04:	00098563          	beqz	s3,42010d0e <decoder_task+0x4ba>
42010d08:	854e                	mv	a0,s3
42010d0a:	1cd010ef          	jal	420126d6 <native_aac_decoder_destroy>
42010d0e:	854a                	mv	a0,s2
42010d10:	ff4f70ef          	jal	42008504 <cfree>
42010d14:	4981                	li	s3,0
42010d16:	4a01                	li	s4,0
42010d18:	4901                	li	s2,0
42010d1a:	b929                	j	42010934 <decoder_task+0xe0>
42010d1c:	fe377097          	auipc	ra,0xfe377
42010d20:	69e080e7          	jalr	1694(ra) # 403883ba <esp_log_timestamp>
42010d24:	3c126737          	lui	a4,0x3c126
42010d28:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
42010d2c:	3c126637          	lui	a2,0x3c126
42010d30:	86aa                	mv	a3,a0
42010d32:	85ba                	mv	a1,a4
42010d34:	87a2                	mv	a5,s0
42010d36:	a1c60613          	addi	a2,a2,-1508 # 3c125a1c <_esp_trace_encoder_array_end+0x58fc>
42010d3a:	4505                	li	a0,1
42010d3c:	fe377097          	auipc	ra,0xfe377
42010d40:	576080e7          	jalr	1398(ra) # 403882b2 <esp_log>
42010d44:	3fc957b7          	lui	a5,0x3fc95
42010d48:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42010d4c:	000ca583          	lw	a1,0(s9)
42010d50:	3c1267b7          	lui	a5,0x3c126
42010d54:	a4c78693          	addi	a3,a5,-1460 # 3c125a4c <_esp_trace_encoder_array_end+0x592c>
42010d58:	4601                	li	a2,0
42010d5a:	4b4040ef          	jal	4201520e <native_state_set_audio>
42010d5e:	000cac03          	lw	s8,0(s9)
42010d62:	8566                	mv	a0,s9
42010d64:	85e2                	mv	a1,s8
42010d66:	a27ff0ef          	jal	4201078c <return_decoded_packet>
42010d6a:	bea9                	j	420108c4 <decoder_task+0x70>
42010d6c:	3fc957b7          	lui	a5,0x3fc95
42010d70:	afc7a503          	lw	a0,-1284(a5) # 3fc94afc <s_encoded>
42010d74:	85e6                	mv	a1,s9
42010d76:	1ae670ef          	jal	42077f24 <vRingbufferReturnItem>
42010d7a:	b6a9                	j	420108c4 <decoder_task+0x70>
42010d7c:	854a                	mv	a0,s2
42010d7e:	f86f70ef          	jal	42008504 <cfree>
42010d82:	4a01                	li	s4,0
42010d84:	4901                	li	s2,0
42010d86:	b649                	j	42010908 <decoder_task+0xb4>
42010d88:	854a                	mv	a0,s2
42010d8a:	f7af70ef          	jal	42008504 <cfree>
42010d8e:	15c240ef          	jal	42034eea <custom_flac_decoder_create>
42010d92:	8baa                	mv	s7,a0
42010d94:	52050b63          	beqz	a0,420112ca <decoder_task+0xa76>
42010d98:	4981                	li	s3,0
42010d9a:	4a01                	li	s4,0
42010d9c:	4901                	li	s2,0
42010d9e:	4d81                	li	s11,0
42010da0:	4661                	li	a2,24
42010da2:	4581                	li	a1,0
42010da4:	10a8                	addi	a0,sp,104
42010da6:	fdfef097          	auipc	ra,0xfdfef
42010daa:	5ae080e7          	jalr	1454(ra) # 40000354 <memset>
42010dae:	011c                	addi	a5,sp,128
42010db0:	ccbe                	sw	a5,88(sp)
42010db2:	105c                	addi	a5,sp,36
42010db4:	cebe                	sw	a5,92(sp)
42010db6:	01a10793          	addi	a5,sp,26
42010dba:	d0be                	sw	a5,96(sp)
42010dbc:	caa6                	sw	s1,84(sp)
42010dbe:	00acc683          	lbu	a3,10(s9)
42010dc2:	008cd603          	lhu	a2,8(s9)
42010dc6:	42011737          	lui	a4,0x42011
42010dca:	00d036b3          	snez	a3,a3
42010dce:	08dc                	addi	a5,sp,84
42010dd0:	51e70713          	addi	a4,a4,1310 # 4201151e <custom_flac_output>
42010dd4:	00bc8593          	addi	a1,s9,11
42010dd8:	06810813          	addi	a6,sp,104
42010ddc:	855e                	mv	a0,s7
42010dde:	192240ef          	jal	42034f70 <custom_flac_decoder_feed>
42010de2:	47ca                	lw	a5,144(sp)
42010de4:	5726                	lw	a4,104(sp)
42010de6:	465a                	lw	a2,148(sp)
42010de8:	55b6                	lw	a1,108(sp)
42010dea:	568a                	lw	a3,160(sp)
42010dec:	973e                	add	a4,a4,a5
42010dee:	842a                	mv	s0,a0
42010df0:	5546                	lw	a0,112(sp)
42010df2:	962e                	add	a2,a2,a1
42010df4:	00f737b3          	sltu	a5,a4,a5
42010df8:	97b2                	add	a5,a5,a2
42010dfa:	55d6                	lw	a1,116(sp)
42010dfc:	561a                	lw	a2,164(sp)
42010dfe:	96aa                	add	a3,a3,a0
42010e00:	c93a                	sw	a4,144(sp)
42010e02:	cb3e                	sw	a5,148(sp)
42010e04:	d136                	sw	a3,160(sp)
42010e06:	00b67363          	bgeu	a2,a1,42010e0c <decoder_task+0x5b8>
42010e0a:	d32e                	sw	a1,164(sp)
42010e0c:	57aa                	lw	a5,168(sp)
42010e0e:	5766                	lw	a4,120(sp)
42010e10:	97ba                	add	a5,a5,a4
42010e12:	d53e                	sw	a5,168(sp)
42010e14:	500d8c63          	beqz	s11,4201132c <decoder_task+0xad8>
42010e18:	4d85                	li	s11,1
42010e1a:	fe370097          	auipc	ra,0xfe370
42010e1e:	520080e7          	jalr	1312(ra) # 4038133a <esp_timer_get_time>
42010e22:	862e                	mv	a2,a1
42010e24:	85aa                	mv	a1,a0
42010e26:	0108                	addi	a0,sp,128
42010e28:	832ff0ef          	jal	4200fe5a <decode_stats_report>
42010e2c:	00045b63          	bgez	s0,42010e42 <decoder_task+0x5ee>
42010e30:	af0a8793          	addi	a5,s5,-1296
42010e34:	0330000f          	fence	rw,rw
42010e38:	439c                	lw	a5,0(a5)
42010e3a:	0230000f          	fence	r,rw
42010e3e:	64978c63          	beq	a5,s1,42011496 <decoder_task+0xc42>
42010e42:	00acc783          	lbu	a5,10(s9)
42010e46:	4c079663          	bnez	a5,42011312 <decoder_task+0xabe>
42010e4a:	4c9c0463          	beq	s8,s1,42011312 <decoder_task+0xabe>
42010e4e:	8566                	mv	a0,s9
42010e50:	85e2                	mv	a1,s8
42010e52:	93bff0ef          	jal	4201078c <return_decoded_packet>
42010e56:	4b0d                	li	s6,3
42010e58:	4401                	li	s0,0
42010e5a:	b4ad                	j	420108c4 <decoder_task+0x70>
42010e5c:	6589                	lui	a1,0x2
42010e5e:	36ba0663          	beq	s4,a1,420111ca <decoder_task+0x976>
42010e62:	854a                	mv	a0,s2
42010e64:	e9cf70ef          	jal	42008500 <realloc>
42010e68:	842a                	mv	s0,a0
42010e6a:	6a050063          	beqz	a0,4201150a <decoder_task+0xcb6>
42010e6e:	204347b7          	lui	a5,0x20434
42010e72:	14178793          	addi	a5,a5,321 # 20434141 <CSR_UINTSTATUS+0x20433490>
42010e76:	d682                	sw	zero,108(sp)
42010e78:	d882                	sw	zero,112(sp)
42010e7a:	da82                	sw	zero,116(sp)
42010e7c:	d4be                	sw	a5,104(sp)
42010e7e:	02d010ef          	jal	420126aa <native_aac_decoder_create>
42010e82:	89aa                	mv	s3,a0
42010e84:	4c050463          	beqz	a0,4201134c <decoder_task+0xaf8>
42010e88:	8922                	mv	s2,s0
42010e8a:	6a09                	lui	s4,0x2
42010e8c:	4b81                	li	s7,0
42010e8e:	4d81                	li	s11,0
42010e90:	b90d                	j	42010ac2 <decoder_task+0x26e>
42010e92:	5d61                	li	s10,-8
42010e94:	c662                	sw	s8,12(sp)
42010e96:	e789                	bnez	a5,42010ea0 <decoder_task+0x64c>
42010e98:	05c14783          	lbu	a5,92(sp)
42010e9c:	1c078f63          	beqz	a5,4201107a <decoder_task+0x826>
42010ea0:	4781                	li	a5,0
42010ea2:	4801                	li	a6,0
42010ea4:	de3e                	sw	a5,60(sp)
42010ea6:	c0c2                	sw	a6,64(sp)
42010ea8:	da4a                	sw	s2,52(sp)
42010eaa:	dc52                	sw	s4,56(sp)
42010eac:	d082                	sw	zero,96(sp)
42010eae:	fe370097          	auipc	ra,0xfe370
42010eb2:	48c080e7          	jalr	1164(ra) # 4038133a <esp_timer_get_time>
42010eb6:	842a                	mv	s0,a0
42010eb8:	4572                	lw	a0,28(sp)
42010eba:	1850                	addi	a2,sp,52
42010ebc:	08cc                	addi	a1,sp,84
42010ebe:	4b8150ef          	jal	42026376 <__wrap_esp_audio_simple_dec_process>
42010ec2:	8c2a                	mv	s8,a0
42010ec4:	fe370097          	auipc	ra,0xfe370
42010ec8:	476080e7          	jalr	1142(ra) # 4038133a <esp_timer_get_time>
42010ecc:	47ca                	lw	a5,144(sp)
42010ece:	46da                	lw	a3,148(sp)
42010ed0:	8d01                	sub	a0,a0,s0
42010ed2:	00a78733          	add	a4,a5,a0
42010ed6:	00f737b3          	sltu	a5,a4,a5
42010eda:	97b6                	add	a5,a5,a3
42010edc:	cb3e                	sw	a5,148(sp)
42010ede:	578a                	lw	a5,160(sp)
42010ee0:	c93a                	sw	a4,144(sp)
42010ee2:	571a                	lw	a4,164(sp)
42010ee4:	0785                	addi	a5,a5,1
42010ee6:	d13e                	sw	a5,160(sp)
42010ee8:	00a77363          	bgeu	a4,a0,42010eee <decoder_task+0x69a>
42010eec:	d32a                	sw	a0,164(sp)
42010eee:	8bfd                	andi	a5,a5,31
42010ef0:	1e078e63          	beqz	a5,420110ec <decoder_task+0x898>
42010ef4:	af0a8793          	addi	a5,s5,-1296
42010ef8:	0330000f          	fence	rw,rw
42010efc:	439c                	lw	a5,0(a5)
42010efe:	0230000f          	fence	r,rw
42010f02:	16979c63          	bne	a5,s1,4201107a <decoder_task+0x826>
42010f06:	1dac0763          	beq	s8,s10,420110d4 <decoder_task+0x880>
42010f0a:	500c1363          	bnez	s8,42011410 <decoder_task+0xbbc>
42010f0e:	5786                	lw	a5,96(sp)
42010f10:	4766                	lw	a4,88(sp)
42010f12:	34f76563          	bltu	a4,a5,4201125c <decoder_task+0xa08>
42010f16:	8f1d                	sub	a4,a4,a5
42010f18:	56aa                	lw	a3,168(sp)
42010f1a:	ccba                	sw	a4,88(sp)
42010f1c:	4756                	lw	a4,84(sp)
42010f1e:	96be                	add	a3,a3,a5
42010f20:	d536                	sw	a3,168(sp)
42010f22:	97ba                	add	a5,a5,a4
42010f24:	4706                	lw	a4,64(sp)
42010f26:	cabe                	sw	a5,84(sp)
42010f28:	12070363          	beqz	a4,4201104e <decoder_task+0x7fa>
42010f2c:	4572                	lw	a0,28(sp)
42010f2e:	00cc                	addi	a1,sp,68
42010f30:	c282                	sw	zero,68(sp)
42010f32:	c482                	sw	zero,72(sp)
42010f34:	c682                	sw	zero,76(sp)
42010f36:	c882                	sw	zero,80(sp)
42010f38:	412270ef          	jal	4203834a <esp_audio_simple_dec_get_info>
42010f3c:	1a051e63          	bnez	a0,420110f8 <decoder_task+0x8a4>
42010f40:	4782                	lw	a5,0(sp)
42010f42:	00f10da3          	sb	a5,27(sp)
42010f46:	4789                	li	a5,2
42010f48:	46fb0663          	beq	s6,a5,420113b4 <decoder_task+0xb60>
42010f4c:	4791                	li	a5,4
42010f4e:	44fb0e63          	beq	s6,a5,420113aa <decoder_task+0xb56>
42010f52:	3c126737          	lui	a4,0x3c126
42010f56:	4785                	li	a5,1
42010f58:	80070593          	addi	a1,a4,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
42010f5c:	3efb1363          	bne	s6,a5,42011342 <decoder_task+0xaee>
42010f60:	af0a8793          	addi	a5,s5,-1296
42010f64:	0330000f          	fence	rw,rw
42010f68:	439c                	lw	a5,0(a5)
42010f6a:	0230000f          	fence	r,rw
42010f6e:	06979463          	bne	a5,s1,42010fd6 <decoder_task+0x782>
42010f72:	4796                	lw	a5,68(sp)
42010f74:	c3b5                	beqz	a5,42010fd8 <decoder_task+0x784>
42010f76:	04914683          	lbu	a3,73(sp)
42010f7a:	ceb1                	beqz	a3,42010fd6 <decoder_task+0x782>
42010f7c:	04815703          	lhu	a4,72(sp)
42010f80:	04814503          	lbu	a0,72(sp)
42010f84:	00875613          	srli	a2,a4,0x8
42010f88:	0722                	slli	a4,a4,0x8
42010f8a:	963a                	add	a2,a2,a4
42010f8c:	c529                	beqz	a0,42010fd6 <decoder_task+0x782>
42010f8e:	06012b23          	sw	zero,118(sp)
42010f92:	06012923          	sw	zero,114(sp)
42010f96:	d23e                	sw	a5,36(sp)
42010f98:	06c11823          	sh	a2,112(sp)
42010f9c:	d6be                	sw	a5,108(sp)
42010f9e:	4626                	lw	a2,72(sp)
42010fa0:	dabe                	sw	a5,116(sp)
42010fa2:	3fc957b7          	lui	a5,0x3fc95
42010fa6:	4746                	lw	a4,80(sp)
42010fa8:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42010fac:	06d10c23          	sb	a3,120(sp)
42010fb0:	4782                	lw	a5,0(sp)
42010fb2:	46b6                	lw	a3,76(sp)
42010fb4:	06011d23          	sh	zero,122(sp)
42010fb8:	d4ae                	sw	a1,104(sp)
42010fba:	d432                	sw	a2,40(sp)
42010fbc:	4405                	li	s0,1
42010fbe:	10b0                	addi	a2,sp,104
42010fc0:	85a6                	mv	a1,s1
42010fc2:	06f10d23          	sb	a5,122(sp)
42010fc6:	d636                	sw	a3,44(sp)
42010fc8:	d83a                	sw	a4,48(sp)
42010fca:	00810d23          	sb	s0,26(sp)
42010fce:	320040ef          	jal	420152ee <native_state_set_stream_info>
42010fd2:	87a2                	mv	a5,s0
42010fd4:	a011                	j	42010fd8 <decoder_task+0x784>
42010fd6:	4781                	li	a5,0
42010fd8:	45b6                	lw	a1,76(sp)
42010fda:	8526                	mv	a0,s1
42010fdc:	00f10d23          	sb	a5,26(sp)
42010fe0:	c34ff0ef          	jal	42010414 <state_set_decoder_bitrate>
42010fe4:	01a14783          	lbu	a5,26(sp)
42010fe8:	c3bd                	beqz	a5,4201104e <decoder_task+0x7fa>
42010fea:	1e0d8263          	beqz	s11,420111ce <decoder_task+0x97a>
42010fee:	02814503          	lbu	a0,40(sp)
42010ff2:	02914783          	lbu	a5,41(sp)
42010ff6:	4406                	lw	s0,64(sp)
42010ff8:	051d                	addi	a0,a0,7
42010ffa:	810d                	srli	a0,a0,0x3
42010ffc:	02f50533          	mul	a0,a0,a5
42011000:	cd15                	beqz	a0,4201103c <decoder_task+0x7e8>
42011002:	5612                	lw	a2,36(sp)
42011004:	ce05                	beqz	a2,4201103c <decoder_task+0x7e8>
42011006:	02a45533          	divu	a0,s0,a0
4201100a:	000f47b7          	lui	a5,0xf4
4201100e:	24078793          	addi	a5,a5,576 # f4240 <CSR_UINTSTATUS+0xf358f>
42011012:	4681                	li	a3,0
42011014:	02f535b3          	mulhu	a1,a0,a5
42011018:	02f50533          	mul	a0,a0,a5
4201101c:	fdff0097          	auipc	ra,0xfdff0
42011020:	890080e7          	jalr	-1904(ra) # 400008ac <__udivdi3>
42011024:	47ea                	lw	a5,152(sp)
42011026:	46fa                	lw	a3,156(sp)
42011028:	573a                	lw	a4,172(sp)
4201102a:	953e                	add	a0,a0,a5
4201102c:	96ae                	add	a3,a3,a1
4201102e:	00f537b3          	sltu	a5,a0,a5
42011032:	97b6                	add	a5,a5,a3
42011034:	9722                	add	a4,a4,s0
42011036:	cf3e                	sw	a5,156(sp)
42011038:	cd2a                	sw	a0,152(sp)
4201103a:	d73a                	sw	a4,172(sp)
4201103c:	86a2                	mv	a3,s0
4201103e:	864a                	mv	a2,s2
42011040:	104c                	addi	a1,sp,36
42011042:	8526                	mv	a0,s1
42011044:	a94ff0ef          	jal	420102d8 <send_pcm>
42011048:	8daa                	mv	s11,a0
4201104a:	38050d63          	beqz	a0,420113e4 <decoder_task+0xb90>
4201104e:	fe370097          	auipc	ra,0xfe370
42011052:	2ec080e7          	jalr	748(ra) # 4038133a <esp_timer_get_time>
42011056:	862e                	mv	a2,a1
42011058:	85aa                	mv	a1,a0
4201105a:	0108                	addi	a0,sp,128
4201105c:	dfffe0ef          	jal	4200fe5a <decode_stats_report>
42011060:	4706                	lw	a4,64(sp)
42011062:	5786                	lw	a5,96(sp)
42011064:	05c14683          	lbu	a3,92(sp)
42011068:	8fd9                	or	a5,a5,a4
4201106a:	efb9                	bnez	a5,420110c8 <decoder_task+0x874>
4201106c:	3c068363          	beqz	a3,42011432 <decoder_task+0xbde>
42011070:	4701                	li	a4,0
42011072:	47e6                	lw	a5,88(sp)
42011074:	8f5d                	or	a4,a4,a5
42011076:	e20710e3          	bnez	a4,42010e96 <decoder_task+0x642>
4201107a:	4c32                	lw	s8,12(sp)
4201107c:	b1b1                	j	42010cc8 <decoder_task+0x474>
4201107e:	c40691e3          	bnez	a3,42010cc0 <decoder_task+0x46c>
42011082:	47e6                	lw	a5,88(sp)
42011084:	a6079ae3          	bnez	a5,42010af8 <decoder_task+0x2a4>
42011088:	b181                	j	42010cc8 <decoder_task+0x474>
4201108a:	5706                	lw	a4,96(sp)
4201108c:	47d6                	lw	a5,84(sp)
4201108e:	56aa                	lw	a3,168(sp)
42011090:	5472                	lw	s0,60(sp)
42011092:	97ba                	add	a5,a5,a4
42011094:	cabe                	sw	a5,84(sp)
42011096:	47e6                	lw	a5,88(sp)
42011098:	96ba                	add	a3,a3,a4
4201109a:	d536                	sw	a3,168(sp)
4201109c:	8f99                	sub	a5,a5,a4
4201109e:	ccbe                	sw	a5,88(sp)
420110a0:	308a7f63          	bgeu	s4,s0,420113be <decoder_task+0xb6a>
420110a4:	85a2                	mv	a1,s0
420110a6:	854a                	mv	a0,s2
420110a8:	c58f70ef          	jal	42008500 <realloc>
420110ac:	30050963          	beqz	a0,420113be <decoder_task+0xb6a>
420110b0:	8a22                	mv	s4,s0
420110b2:	892a                	mv	s2,a0
420110b4:	b491                	j	42010af8 <decoder_task+0x2a4>
420110b6:	4505                	li	a0,1
420110b8:	00101097          	auipc	ra,0x101
420110bc:	c4a080e7          	jalr	-950(ra) # 42111d02 <vTaskDelay>
420110c0:	b471                	j	42010b4c <decoder_task+0x2f8>
420110c2:	00010d23          	sb	zero,26(sp)
420110c6:	bed1                	j	42010c9a <decoder_task+0x446>
420110c8:	f6cd                	bnez	a3,42011072 <decoder_task+0x81e>
420110ca:	47e6                	lw	a5,88(sp)
420110cc:	dc079ae3          	bnez	a5,42010ea0 <decoder_task+0x64c>
420110d0:	4c32                	lw	s8,12(sp)
420110d2:	bedd                	j	42010cc8 <decoder_task+0x474>
420110d4:	5472                	lw	s0,60(sp)
420110d6:	2e8a7463          	bgeu	s4,s0,420113be <decoder_task+0xb6a>
420110da:	85a2                	mv	a1,s0
420110dc:	854a                	mv	a0,s2
420110de:	c22f70ef          	jal	42008500 <realloc>
420110e2:	2c050e63          	beqz	a0,420113be <decoder_task+0xb6a>
420110e6:	892a                	mv	s2,a0
420110e8:	8a22                	mv	s4,s0
420110ea:	bb5d                	j	42010ea0 <decoder_task+0x64c>
420110ec:	4505                	li	a0,1
420110ee:	00101097          	auipc	ra,0x101
420110f2:	c14080e7          	jalr	-1004(ra) # 42111d02 <vTaskDelay>
420110f6:	bbfd                	j	42010ef4 <decoder_task+0x6a0>
420110f8:	00010d23          	sb	zero,26(sp)
420110fc:	bf89                	j	4201104e <decoder_task+0x7fa>
420110fe:	3c1267b7          	lui	a5,0x3c126
42011102:	b3078513          	addi	a0,a5,-1232 # 3c125b30 <_esp_trace_encoder_array_end+0x5a10>
42011106:	96eff0ef          	jal	42010274 <log_runtime_memory>
4201110a:	be1d                	j	42010c40 <decoder_task+0x3ec>
4201110c:	846a                	mv	s0,s10
4201110e:	4a09                	li	s4,2
42011110:	fe377097          	auipc	ra,0xfe377
42011114:	2aa080e7          	jalr	682(ra) # 403883ba <esp_log_timestamp>
42011118:	2f4b0e63          	beq	s6,s4,42011414 <decoder_task+0xbc0>
4201111c:	4791                	li	a5,4
4201111e:	30fb0063          	beq	s6,a5,4201141e <decoder_task+0xbca>
42011122:	3c1267b7          	lui	a5,0x3c126
42011126:	4705                	li	a4,1
42011128:	80078793          	addi	a5,a5,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
4201112c:	00eb0663          	beq	s6,a4,42011138 <decoder_task+0x8e4>
42011130:	3c1267b7          	lui	a5,0x3c126
42011134:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
42011138:	3c126737          	lui	a4,0x3c126
4201113c:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
42011140:	3c126637          	lui	a2,0x3c126
42011144:	86aa                	mv	a3,a0
42011146:	85ba                	mv	a1,a4
42011148:	8822                	mv	a6,s0
4201114a:	b6460613          	addi	a2,a2,-1180 # 3c125b64 <_esp_trace_encoder_array_end+0x5a44>
4201114e:	4509                	li	a0,2
42011150:	fe377097          	auipc	ra,0xfe377
42011154:	162080e7          	jalr	354(ra) # 403882b2 <esp_log>
42011158:	3fc957b7          	lui	a5,0x3fc95
4201115c:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42011160:	3c1267b7          	lui	a5,0x3c126
42011164:	a0c78693          	addi	a3,a5,-1524 # 3c125a0c <_esp_trace_encoder_array_end+0x58ec>
42011168:	85a6                	mv	a1,s1
4201116a:	4601                	li	a2,0
4201116c:	0a2040ef          	jal	4201520e <native_state_set_audio>
42011170:	8c26                	mv	s8,s1
42011172:	4572                	lw	a0,28(sp)
42011174:	c119                	beqz	a0,4201117a <decoder_task+0x926>
42011176:	24c270ef          	jal	420383c2 <esp_audio_simple_dec_close>
4201117a:	ce02                	sw	zero,28(sp)
4201117c:	00098563          	beqz	s3,42011186 <decoder_task+0x932>
42011180:	854e                	mv	a0,s3
42011182:	554010ef          	jal	420126d6 <native_aac_decoder_destroy>
42011186:	854a                	mv	a0,s2
42011188:	b7cf70ef          	jal	42008504 <cfree>
4201118c:	4981                	li	s3,0
4201118e:	4a01                	li	s4,0
42011190:	4901                	li	s2,0
42011192:	b689                	j	42010cd4 <decoder_task+0x480>
42011194:	854e                	mv	a0,s3
42011196:	105010ef          	jal	42012a9a <native_aac_decoder_source_channels>
4201119a:	01b14683          	lbu	a3,27(sp)
4201119e:	0ff57513          	zext.b	a0,a0
420111a2:	bc19                	j	42010bb8 <decoder_task+0x364>
420111a4:	204747b7          	lui	a5,0x20474
420111a8:	74f78793          	addi	a5,a5,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
420111ac:	086c                	addi	a1,sp,28
420111ae:	10a8                	addi	a0,sp,104
420111b0:	d4be                	sw	a5,104(sp)
420111b2:	038150ef          	jal	420261ea <__wrap_esp_audio_simple_dec_open>
420111b6:	842a                	mv	s0,a0
420111b8:	1c051963          	bnez	a0,4201138a <decoder_task+0xb36>
420111bc:	4bf2                	lw	s7,28(sp)
420111be:	4d81                	li	s11,0
420111c0:	8c0b83e3          	beqz	s7,42010a86 <decoder_task+0x232>
420111c4:	4981                	li	s3,0
420111c6:	4b81                	li	s7,0
420111c8:	b8ed                	j	42010ac2 <decoder_task+0x26e>
420111ca:	844a                	mv	s0,s2
420111cc:	b14d                	j	42010e6e <decoder_task+0x61a>
420111ce:	3c1267b7          	lui	a5,0x3c126
420111d2:	b3078513          	addi	a0,a5,-1232 # 3c125b30 <_esp_trace_encoder_array_end+0x5a10>
420111d6:	89eff0ef          	jal	42010274 <log_runtime_memory>
420111da:	bd11                	j	42010fee <decoder_task+0x79a>
420111dc:	d682                	sw	zero,108(sp)
420111de:	d882                	sw	zero,112(sp)
420111e0:	da82                	sw	zero,116(sp)
420111e2:	819ff06f          	j	420109fa <decoder_task+0x1a6>
420111e6:	fe377097          	auipc	ra,0xfe377
420111ea:	1d4080e7          	jalr	468(ra) # 403883ba <esp_log_timestamp>
420111ee:	4791                	li	a5,4
420111f0:	4405                	li	s0,1
420111f2:	86aa                	mv	a3,a0
420111f4:	1efb0363          	beq	s6,a5,420113da <decoder_task+0xb86>
420111f8:	3c1267b7          	lui	a5,0x3c126
420111fc:	80078793          	addi	a5,a5,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
42011200:	008b0663          	beq	s6,s0,4201120c <decoder_task+0x9b8>
42011204:	3c1267b7          	lui	a5,0x3c126
42011208:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
4201120c:	3c126737          	lui	a4,0x3c126
42011210:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
42011214:	3c126637          	lui	a2,0x3c126
42011218:	85ba                	mv	a1,a4
4201121a:	a9460613          	addi	a2,a2,-1388 # 3c125a94 <_esp_trace_encoder_array_end+0x5974>
4201121e:	4505                	li	a0,1
42011220:	fe377097          	auipc	ra,0xfe377
42011224:	092080e7          	jalr	146(ra) # 403882b2 <esp_log>
42011228:	3fc957b7          	lui	a5,0x3fc95
4201122c:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42011230:	3c1267b7          	lui	a5,0x3c126
42011234:	9f078693          	addi	a3,a5,-1552 # 3c1259f0 <_esp_trace_encoder_array_end+0x58d0>
42011238:	85a6                	mv	a1,s1
4201123a:	4601                	li	a2,0
4201123c:	7d3030ef          	jal	4201520e <native_state_set_audio>
42011240:	3fc957b7          	lui	a5,0x3fc95
42011244:	afc7a503          	lw	a0,-1284(a5) # 3fc94afc <s_encoded>
42011248:	85e6                	mv	a1,s9
4201124a:	8c26                	mv	s8,s1
4201124c:	4d9660ef          	jal	42077f24 <vRingbufferReturnItem>
42011250:	4981                	li	s3,0
42011252:	4d81                	li	s11,0
42011254:	4b81                	li	s7,0
42011256:	4401                	li	s0,0
42011258:	e6cff06f          	j	420108c4 <decoder_task+0x70>
4201125c:	fe377097          	auipc	ra,0xfe377
42011260:	15e080e7          	jalr	350(ra) # 403883ba <esp_log_timestamp>
42011264:	4789                	li	a5,2
42011266:	4405                	li	s0,1
42011268:	12fb0c63          	beq	s6,a5,420113a0 <decoder_task+0xb4c>
4201126c:	4791                	li	a5,4
4201126e:	1afb0d63          	beq	s6,a5,42011428 <decoder_task+0xbd4>
42011272:	3c1267b7          	lui	a5,0x3c126
42011276:	80078793          	addi	a5,a5,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
4201127a:	008b0663          	beq	s6,s0,42011286 <decoder_task+0xa32>
4201127e:	3c1267b7          	lui	a5,0x3c126
42011282:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
42011286:	48e6                	lw	a7,88(sp)
42011288:	5806                	lw	a6,96(sp)
4201128a:	3c126737          	lui	a4,0x3c126
4201128e:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
42011292:	3c126637          	lui	a2,0x3c126
42011296:	86aa                	mv	a3,a0
42011298:	85ba                	mv	a1,a4
4201129a:	b8860613          	addi	a2,a2,-1144 # 3c125b88 <_esp_trace_encoder_array_end+0x5a68>
4201129e:	4505                	li	a0,1
420112a0:	fe377097          	auipc	ra,0xfe377
420112a4:	012080e7          	jalr	18(ra) # 403882b2 <esp_log>
420112a8:	3fc957b7          	lui	a5,0x3fc95
420112ac:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
420112b0:	3c1267b7          	lui	a5,0x3c126
420112b4:	bc478693          	addi	a3,a5,-1084 # 3c125bc4 <_esp_trace_encoder_array_end+0x5aa4>
420112b8:	85a6                	mv	a1,s1
420112ba:	4601                	li	a2,0
420112bc:	753030ef          	jal	4201520e <native_state_set_audio>
420112c0:	8c26                	mv	s8,s1
420112c2:	bd45                	j	42011172 <decoder_task+0x91e>
420112c4:	b60b8fe3          	beqz	s7,42010e42 <decoder_task+0x5ee>
420112c8:	bce1                	j	42010da0 <decoder_task+0x54c>
420112ca:	fe377097          	auipc	ra,0xfe377
420112ce:	0f0080e7          	jalr	240(ra) # 403883ba <esp_log_timestamp>
420112d2:	3c1267b7          	lui	a5,0x3c126
420112d6:	80c78713          	addi	a4,a5,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
420112da:	3c1267b7          	lui	a5,0x3c126
420112de:	86aa                	mv	a3,a0
420112e0:	85ba                	mv	a1,a4
420112e2:	a6078613          	addi	a2,a5,-1440 # 3c125a60 <_esp_trace_encoder_array_end+0x5940>
420112e6:	4505                	li	a0,1
420112e8:	fe377097          	auipc	ra,0xfe377
420112ec:	fca080e7          	jalr	-54(ra) # 403882b2 <esp_log>
420112f0:	3fc957b7          	lui	a5,0x3fc95
420112f4:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
420112f8:	3c1267b7          	lui	a5,0x3c126
420112fc:	9f078693          	addi	a3,a5,-1552 # 3c1259f0 <_esp_trace_encoder_array_end+0x58d0>
42011300:	85a6                	mv	a1,s1
42011302:	4601                	li	a2,0
42011304:	70b030ef          	jal	4201520e <native_state_set_audio>
42011308:	8c26                	mv	s8,s1
4201130a:	4981                	li	s3,0
4201130c:	4901                	li	s2,0
4201130e:	4a01                	li	s4,0
42011310:	4d81                	li	s11,0
42011312:	855e                	mv	a0,s7
42011314:	437230ef          	jal	42034f4a <custom_flac_decoder_destroy>
42011318:	4b81                	li	s7,0
4201131a:	be15                	j	42010e4e <decoder_task+0x5fa>
4201131c:	8542                	mv	a0,a6
4201131e:	b0e5                	j	42010c06 <decoder_task+0x3b2>
42011320:	3c1267b7          	lui	a5,0x3c126
42011324:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
42011328:	f08ff06f          	j	42010a30 <decoder_task+0x1dc>
4201132c:	01a14d83          	lbu	s11,26(sp)
42011330:	ae0d85e3          	beqz	s11,42010e1a <decoder_task+0x5c6>
42011334:	3c1267b7          	lui	a5,0x3c126
42011338:	aec78513          	addi	a0,a5,-1300 # 3c125aec <_esp_trace_encoder_array_end+0x59cc>
4201133c:	f39fe0ef          	jal	42010274 <log_runtime_memory>
42011340:	bce1                	j	42010e18 <decoder_task+0x5c4>
42011342:	3c1267b7          	lui	a5,0x3c126
42011346:	80478593          	addi	a1,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
4201134a:	b919                	j	42010f60 <decoder_task+0x70c>
4201134c:	fe377097          	auipc	ra,0xfe377
42011350:	06e080e7          	jalr	110(ra) # 403883ba <esp_log_timestamp>
42011354:	3c1267b7          	lui	a5,0x3c126
42011358:	80c78713          	addi	a4,a5,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
4201135c:	3c126637          	lui	a2,0x3c126
42011360:	3c1257b7          	lui	a5,0x3c125
42011364:	86aa                	mv	a3,a0
42011366:	7f078793          	addi	a5,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
4201136a:	85ba                	mv	a1,a4
4201136c:	ac460613          	addi	a2,a2,-1340 # 3c125ac4 <_esp_trace_encoder_array_end+0x59a4>
42011370:	5879                	li	a6,-2
42011372:	4505                	li	a0,1
42011374:	fe377097          	auipc	ra,0xfe377
42011378:	f3e080e7          	jalr	-194(ra) # 403882b2 <esp_log>
4201137c:	3c1267b7          	lui	a5,0x3c126
42011380:	8922                	mv	s2,s0
42011382:	9f078693          	addi	a3,a5,-1552 # 3c1259f0 <_esp_trace_encoder_array_end+0x58d0>
42011386:	ed6ff06f          	j	42010a5c <decoder_task+0x208>
4201138a:	fe377097          	auipc	ra,0xfe377
4201138e:	030080e7          	jalr	48(ra) # 403883ba <esp_log_timestamp>
42011392:	3c1257b7          	lui	a5,0x3c125
42011396:	86aa                	mv	a3,a0
42011398:	7fc78793          	addi	a5,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
4201139c:	e94ff06f          	j	42010a30 <decoder_task+0x1dc>
420113a0:	3c1257b7          	lui	a5,0x3c125
420113a4:	7f078793          	addi	a5,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
420113a8:	bdf9                	j	42011286 <decoder_task+0xa32>
420113aa:	3c1257b7          	lui	a5,0x3c125
420113ae:	7fc78593          	addi	a1,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
420113b2:	b67d                	j	42010f60 <decoder_task+0x70c>
420113b4:	3c1257b7          	lui	a5,0x3c125
420113b8:	7f078593          	addi	a1,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
420113bc:	b655                	j	42010f60 <decoder_task+0x70c>
420113be:	3fc957b7          	lui	a5,0x3fc95
420113c2:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
420113c6:	3c1267b7          	lui	a5,0x3c126
420113ca:	b4c78693          	addi	a3,a5,-1204 # 3c125b4c <_esp_trace_encoder_array_end+0x5a2c>
420113ce:	4601                	li	a2,0
420113d0:	85a6                	mv	a1,s1
420113d2:	63d030ef          	jal	4201520e <native_state_set_audio>
420113d6:	8c26                	mv	s8,s1
420113d8:	bb69                	j	42011172 <decoder_task+0x91e>
420113da:	3c1257b7          	lui	a5,0x3c125
420113de:	7fc78793          	addi	a5,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
420113e2:	b52d                	j	4201120c <decoder_task+0x9b8>
420113e4:	4c32                	lw	s8,12(sp)
420113e6:	fe377097          	auipc	ra,0xfe377
420113ea:	fd4080e7          	jalr	-44(ra) # 403883ba <esp_log_timestamp>
420113ee:	3c1267b7          	lui	a5,0x3c126
420113f2:	80c78713          	addi	a4,a5,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
420113f6:	3c1267b7          	lui	a5,0x3c126
420113fa:	86aa                	mv	a3,a0
420113fc:	85ba                	mv	a1,a4
420113fe:	bd878613          	addi	a2,a5,-1064 # 3c125bd8 <_esp_trace_encoder_array_end+0x5ab8>
42011402:	4509                	li	a0,2
42011404:	fe377097          	auipc	ra,0xfe377
42011408:	eae080e7          	jalr	-338(ra) # 403882b2 <esp_log>
4201140c:	4d85                	li	s11,1
4201140e:	b86d                	j	42010cc8 <decoder_task+0x474>
42011410:	8462                	mv	s0,s8
42011412:	b9f5                	j	4201110e <decoder_task+0x8ba>
42011414:	3c1257b7          	lui	a5,0x3c125
42011418:	7f078793          	addi	a5,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
4201141c:	bb31                	j	42011138 <decoder_task+0x8e4>
4201141e:	3c1257b7          	lui	a5,0x3c125
42011422:	7fc78793          	addi	a5,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
42011426:	bb09                	j	42011138 <decoder_task+0x8e4>
42011428:	3c1257b7          	lui	a5,0x3c125
4201142c:	7fc78793          	addi	a5,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
42011430:	bd99                	j	42011286 <decoder_task+0xa32>
42011432:	fe377097          	auipc	ra,0xfe377
42011436:	f88080e7          	jalr	-120(ra) # 403883ba <esp_log_timestamp>
4201143a:	4789                	li	a5,2
4201143c:	4405                	li	s0,1
4201143e:	86aa                	mv	a3,a0
42011440:	0afb0563          	beq	s6,a5,420114ea <decoder_task+0xc96>
42011444:	4791                	li	a5,4
42011446:	0afb0d63          	beq	s6,a5,42011500 <decoder_task+0xcac>
4201144a:	3c1267b7          	lui	a5,0x3c126
4201144e:	80078793          	addi	a5,a5,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
42011452:	008b0663          	beq	s6,s0,4201145e <decoder_task+0xc0a>
42011456:	3c1267b7          	lui	a5,0x3c126
4201145a:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
4201145e:	3c126737          	lui	a4,0x3c126
42011462:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
42011466:	3c126637          	lui	a2,0x3c126
4201146a:	85ba                	mv	a1,a4
4201146c:	bf860613          	addi	a2,a2,-1032 # 3c125bf8 <_esp_trace_encoder_array_end+0x5ad8>
42011470:	4505                	li	a0,1
42011472:	fe377097          	auipc	ra,0xfe377
42011476:	e40080e7          	jalr	-448(ra) # 403882b2 <esp_log>
4201147a:	3fc957b7          	lui	a5,0x3fc95
4201147e:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42011482:	3c1267b7          	lui	a5,0x3c126
42011486:	c2878693          	addi	a3,a5,-984 # 3c125c28 <_esp_trace_encoder_array_end+0x5b08>
4201148a:	85a6                	mv	a1,s1
4201148c:	4601                	li	a2,0
4201148e:	581030ef          	jal	4201520e <native_state_set_audio>
42011492:	8c26                	mv	s8,s1
42011494:	b9f9                	j	42011172 <decoder_task+0x91e>
42011496:	fe377097          	auipc	ra,0xfe377
4201149a:	f24080e7          	jalr	-220(ra) # 403883ba <esp_log_timestamp>
4201149e:	3c126737          	lui	a4,0x3c126
420114a2:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
420114a6:	3c126637          	lui	a2,0x3c126
420114aa:	86aa                	mv	a3,a0
420114ac:	87a2                	mv	a5,s0
420114ae:	85ba                	mv	a1,a4
420114b0:	b0460613          	addi	a2,a2,-1276 # 3c125b04 <_esp_trace_encoder_array_end+0x59e4>
420114b4:	4509                	li	a0,2
420114b6:	fe377097          	auipc	ra,0xfe377
420114ba:	dfc080e7          	jalr	-516(ra) # 403882b2 <esp_log>
420114be:	3c126737          	lui	a4,0x3c126
420114c2:	0419                	addi	s0,s0,6 # 3006 <CSR_UINTSTATUS+0x2355>
420114c4:	4785                	li	a5,1
420114c6:	a0c70693          	addi	a3,a4,-1524 # 3c125a0c <_esp_trace_encoder_array_end+0x58ec>
420114ca:	0087e663          	bltu	a5,s0,420114d6 <decoder_task+0xc82>
420114ce:	3c1267b7          	lui	a5,0x3c126
420114d2:	9f078693          	addi	a3,a5,-1552 # 3c1259f0 <_esp_trace_encoder_array_end+0x58d0>
420114d6:	3fc957b7          	lui	a5,0x3fc95
420114da:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
420114de:	4601                	li	a2,0
420114e0:	85a6                	mv	a1,s1
420114e2:	52d030ef          	jal	4201520e <native_state_set_audio>
420114e6:	8c26                	mv	s8,s1
420114e8:	baa9                	j	42010e42 <decoder_task+0x5ee>
420114ea:	3c1257b7          	lui	a5,0x3c125
420114ee:	7f078793          	addi	a5,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
420114f2:	b7b5                	j	4201145e <decoder_task+0xc0a>
420114f4:	3c1267b7          	lui	a5,0x3c126
420114f8:	9f078693          	addi	a3,a5,-1552 # 3c1259f0 <_esp_trace_encoder_array_end+0x58d0>
420114fc:	d60ff06f          	j	42010a5c <decoder_task+0x208>
42011500:	3c1257b7          	lui	a5,0x3c125
42011504:	7fc78793          	addi	a5,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
42011508:	bf99                	j	4201145e <decoder_task+0xc0a>
4201150a:	fe377097          	auipc	ra,0xfe377
4201150e:	eb0080e7          	jalr	-336(ra) # 403883ba <esp_log_timestamp>
42011512:	3c1257b7          	lui	a5,0x3c125
42011516:	86aa                	mv	a3,a0
42011518:	7f078793          	addi	a5,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
4201151c:	b9c5                	j	4201120c <decoder_task+0x9b8>
