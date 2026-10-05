
idf\esp32c3-oled-native\build-custom-terminal\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42010850 <decoder_task>:
42010850:	7151                	addi	sp,sp,-240
42010852:	d5a2                	sw	s0,232(sp)
42010854:	d3a6                	sw	s1,228(sp)
42010856:	d1ca                	sw	s2,224(sp)
42010858:	cfce                	sw	s3,220(sp)
4201085a:	cdd2                	sw	s4,216(sp)
4201085c:	cbd6                	sw	s5,212(sp)
4201085e:	c9da                	sw	s6,208(sp)
42010860:	c7de                	sw	s7,204(sp)
42010862:	c5e2                	sw	s8,200(sp)
42010864:	df6e                	sw	s11,188(sp)
42010866:	d786                	sw	ra,236(sp)
42010868:	c3e6                	sw	s9,196(sp)
4201086a:	c1ea                	sw	s10,192(sp)
4201086c:	5dd010ef          	jal	42012648 <decoder_register_codecs>
42010870:	3fc95737          	lui	a4,0x3fc95
42010874:	000f47b7          	lui	a5,0xf4
42010878:	ad870713          	addi	a4,a4,-1320 # 3fc94ad8 <s_bitrate_updated_us>
4201087c:	24078793          	addi	a5,a5,576 # f4240 <CSR_UINTSTATUS+0xf358f>
42010880:	ce02                	sw	zero,28(sp)
42010882:	c102                	sw	zero,128(sp)
42010884:	c302                	sw	zero,132(sp)
42010886:	c502                	sw	zero,136(sp)
42010888:	c702                	sw	zero,140(sp)
4201088a:	c902                	sw	zero,144(sp)
4201088c:	cb02                	sw	zero,148(sp)
4201088e:	cd02                	sw	zero,152(sp)
42010890:	cf02                	sw	zero,156(sp)
42010892:	d102                	sw	zero,160(sp)
42010894:	d302                	sw	zero,164(sp)
42010896:	d502                	sw	zero,168(sp)
42010898:	d702                	sw	zero,172(sp)
4201089a:	d202                	sw	zero,36(sp)
4201089c:	d402                	sw	zero,40(sp)
4201089e:	d602                	sw	zero,44(sp)
420108a0:	d802                	sw	zero,48(sp)
420108a2:	00010d23          	sb	zero,26(sp)
420108a6:	842a                	mv	s0,a0
420108a8:	c23a                	sw	a4,4(sp)
420108aa:	c43e                	sw	a5,8(sp)
420108ac:	4981                	li	s3,0
420108ae:	4a01                	li	s4,0
420108b0:	4901                	li	s2,0
420108b2:	4d81                	li	s11,0
420108b4:	4b01                	li	s6,0
420108b6:	4c01                	li	s8,0
420108b8:	4481                	li	s1,0
420108ba:	4b81                	li	s7,0
420108bc:	3fc95ab7          	lui	s5,0x3fc95
420108c0:	af0a8793          	addi	a5,s5,-1296 # 3fc94af0 <s_generation>
420108c4:	0330000f          	fence	rw,rw
420108c8:	0007ac83          	lw	s9,0(a5)
420108cc:	0230000f          	fence	r,rw
420108d0:	409c8f63          	beq	s9,s1,42010cee <decoder_task+0x49e>
420108d4:	3fc957b7          	lui	a5,0x3fc95
420108d8:	aec78793          	addi	a5,a5,-1300 # 3fc94aec <s_decoder_target_codec>
420108dc:	0330000f          	fence	rw,rw
420108e0:	4384                	lw	s1,0(a5)
420108e2:	0230000f          	fence	r,rw
420108e6:	4572                	lw	a0,28(sp)
420108e8:	c119                	beqz	a0,420108ee <decoder_task+0x9e>
420108ea:	145260ef          	jal	4203722e <esp_audio_simple_dec_close>
420108ee:	854e                	mv	a0,s3
420108f0:	ce02                	sw	zero,28(sp)
420108f2:	5b9010ef          	jal	420126aa <native_aac_decoder_destroy>
420108f6:	000b8563          	beqz	s7,42010900 <decoder_task+0xb0>
420108fa:	855e                	mv	a0,s7
420108fc:	61e240ef          	jal	42034f1a <custom_flac_decoder_destroy>
42010900:	46048c63          	beqz	s1,42010d78 <decoder_task+0x528>
42010904:	d202                	sw	zero,36(sp)
42010906:	d402                	sw	zero,40(sp)
42010908:	d602                	sw	zero,44(sp)
4201090a:	d802                	sw	zero,48(sp)
4201090c:	00010d23          	sb	zero,26(sp)
42010910:	3fc957b7          	lui	a5,0x3fc95
42010914:	ae878793          	addi	a5,a5,-1304 # 3fc94ae8 <s_decoder_released_generation>
42010918:	0310000f          	fence	rw,w
4201091c:	0197a023          	sw	s9,0(a5)
42010920:	0330000f          	fence	rw,rw
42010924:	4b81                	li	s7,0
42010926:	84e6                	mv	s1,s9
42010928:	4c01                	li	s8,0
4201092a:	4b01                	li	s6,0
4201092c:	4d81                	li	s11,0
4201092e:	4981                	li	s3,0
42010930:	3fc957b7          	lui	a5,0x3fc95
42010934:	afc7a503          	lw	a0,-1284(a5) # 3fc94afc <s_encoded>
42010938:	4651                	li	a2,20
4201093a:	100c                	addi	a1,sp,32
4201093c:	d002                	sw	zero,32(sp)
4201093e:	3d6660ef          	jal	42076d14 <xRingbufferReceive>
42010942:	8caa                	mv	s9,a0
42010944:	dd35                	beqz	a0,420108c0 <decoder_task+0x70>
42010946:	4118                	lw	a4,0(a0)
42010948:	af0a8793          	addi	a5,s5,-1296
4201094c:	0330000f          	fence	rw,rw
42010950:	439c                	lw	a5,0(a5)
42010952:	0230000f          	fence	r,rw
42010956:	40f71963          	bne	a4,a5,42010d68 <decoder_task+0x518>
4201095a:	411c                	lw	a5,0(a0)
4201095c:	41878663          	beq	a5,s8,42010d68 <decoder_task+0x518>
42010960:	4158                	lw	a4,4(a0)
42010962:	e709                	bnez	a4,4201096c <decoder_task+0x11c>
42010964:	00a54703          	lbu	a4,10(a0)
42010968:	3e071c63          	bnez	a4,42010d60 <decoder_task+0x510>
4201096c:	12041563          	bnez	s0,42010a96 <decoder_task+0x246>
42010970:	12f48c63          	beq	s1,a5,42010aa8 <decoder_task+0x258>
42010974:	4572                	lw	a0,28(sp)
42010976:	c119                	beqz	a0,4201097c <decoder_task+0x12c>
42010978:	0b7260ef          	jal	4203722e <esp_audio_simple_dec_close>
4201097c:	854e                	mv	a0,s3
4201097e:	ce02                	sw	zero,28(sp)
42010980:	52b010ef          	jal	420126aa <native_aac_decoder_destroy>
42010984:	000b8563          	beqz	s7,4201098e <decoder_task+0x13e>
42010988:	855e                	mv	a0,s7
4201098a:	590240ef          	jal	42034f1a <custom_flac_decoder_destroy>
4201098e:	4712                	lw	a4,4(sp)
42010990:	000ca483          	lw	s1,0(s9)
42010994:	004cab03          	lw	s6,4(s9)
42010998:	3fc957b7          	lui	a5,0x3fc95
4201099c:	ae07a023          	sw	zero,-1312(a5) # 3fc94ae0 <s_published_bitrate_bps>
420109a0:	4801                	li	a6,0
420109a2:	4781                	li	a5,0
420109a4:	c31c                	sw	a5,0(a4)
420109a6:	00010d23          	sb	zero,26(sp)
420109aa:	01072223          	sw	a6,4(a4)
420109ae:	fe371097          	auipc	ra,0xfe371
420109b2:	98c080e7          	jalr	-1652(ra) # 4038133a <esp_timer_get_time>
420109b6:	c52a                	sw	a0,136(sp)
420109b8:	c902                	sw	zero,144(sp)
420109ba:	cb02                	sw	zero,148(sp)
420109bc:	cd02                	sw	zero,152(sp)
420109be:	cf02                	sw	zero,156(sp)
420109c0:	d102                	sw	zero,160(sp)
420109c2:	d302                	sw	zero,164(sp)
420109c4:	d502                	sw	zero,168(sp)
420109c6:	d702                	sw	zero,172(sp)
420109c8:	c126                	sw	s1,128(sp)
420109ca:	c35a                	sw	s6,132(sp)
420109cc:	c72e                	sw	a1,140(sp)
420109ce:	478d                	li	a5,3
420109d0:	3afb0a63          	beq	s6,a5,42010d84 <decoder_task+0x534>
420109d4:	4789                	li	a5,2
420109d6:	48fb0163          	beq	s6,a5,42010e58 <decoder_task+0x608>
420109da:	640d                	lui	s0,0x3
420109dc:	7e8a7a63          	bgeu	s4,s0,420111d0 <decoder_task+0x980>
420109e0:	85a2                	mv	a1,s0
420109e2:	854a                	mv	a0,s2
420109e4:	b1df70ef          	jal	42008500 <realloc>
420109e8:	7e050963          	beqz	a0,420111da <decoder_task+0x98a>
420109ec:	d682                	sw	zero,108(sp)
420109ee:	d882                	sw	zero,112(sp)
420109f0:	da82                	sw	zero,116(sp)
420109f2:	892a                	mv	s2,a0
420109f4:	8a22                	mv	s4,s0
420109f6:	4791                	li	a5,4
420109f8:	7afb0063          	beq	s6,a5,42011198 <decoder_task+0x948>
420109fc:	203357b7          	lui	a5,0x20335
42010a00:	04d78793          	addi	a5,a5,77 # 2033504d <CSR_UINTSTATUS+0x2033439c>
42010a04:	086c                	addi	a1,sp,28
42010a06:	10a8                	addi	a0,sp,104
42010a08:	d4be                	sw	a5,104(sp)
42010a0a:	7b4150ef          	jal	420261be <__wrap_esp_audio_simple_dec_open>
42010a0e:	842a                	mv	s0,a0
42010a10:	7a050063          	beqz	a0,420111b0 <decoder_task+0x960>
42010a14:	fe378097          	auipc	ra,0xfe378
42010a18:	9a6080e7          	jalr	-1626(ra) # 403883ba <esp_log_timestamp>
42010a1c:	3c1267b7          	lui	a5,0x3c126
42010a20:	4985                	li	s3,1
42010a22:	86aa                	mv	a3,a0
42010a24:	80078793          	addi	a5,a5,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
42010a28:	0f3b16e3          	bne	s6,s3,42011314 <decoder_task+0xac4>
42010a2c:	3c126737          	lui	a4,0x3c126
42010a30:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
42010a34:	3c126637          	lui	a2,0x3c126
42010a38:	85ba                	mv	a1,a4
42010a3a:	8822                	mv	a6,s0
42010a3c:	ac460613          	addi	a2,a2,-1340 # 3c125ac4 <_esp_trace_encoder_array_end+0x59a4>
42010a40:	4505                	li	a0,1
42010a42:	fe378097          	auipc	ra,0xfe378
42010a46:	870080e7          	jalr	-1936(ra) # 403882b2 <esp_log>
42010a4a:	3c126737          	lui	a4,0x3c126
42010a4e:	57f9                	li	a5,-2
42010a50:	9fc70693          	addi	a3,a4,-1540 # 3c1259fc <_esp_trace_encoder_array_end+0x58dc>
42010a54:	28f40ae3          	beq	s0,a5,420114e8 <decoder_task+0xc98>
42010a58:	3fc957b7          	lui	a5,0x3fc95
42010a5c:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42010a60:	4601                	li	a2,0
42010a62:	85a6                	mv	a1,s1
42010a64:	77e040ef          	jal	420151e2 <native_state_set_audio>
42010a68:	4572                	lw	a0,28(sp)
42010a6a:	c501                	beqz	a0,42010a72 <decoder_task+0x222>
42010a6c:	7c2260ef          	jal	4203722e <esp_audio_simple_dec_close>
42010a70:	ce02                	sw	zero,28(sp)
42010a72:	854a                	mv	a0,s2
42010a74:	a91f70ef          	jal	42008504 <cfree>
42010a78:	8c26                	mv	s8,s1
42010a7a:	4a01                	li	s4,0
42010a7c:	4901                	li	s2,0
42010a7e:	4b81                	li	s7,0
42010a80:	4d81                	li	s11,0
42010a82:	3fc957b7          	lui	a5,0x3fc95
42010a86:	afc7a503          	lw	a0,-1284(a5) # 3fc94afc <s_encoded>
42010a8a:	85e6                	mv	a1,s9
42010a8c:	4981                	li	s3,0
42010a8e:	302660ef          	jal	42076d90 <vRingbufferReturnItem>
42010a92:	4401                	li	s0,0
42010a94:	b535                	j	420108c0 <decoder_task+0x70>
42010a96:	3b3010ef          	jal	42012648 <decoder_register_codecs>
42010a9a:	842a                	mv	s0,a0
42010a9c:	26051e63          	bnez	a0,42010d18 <decoder_task+0x4c8>
42010aa0:	000ca783          	lw	a5,0(s9)
42010aa4:	ecf498e3          	bne	s1,a5,42010974 <decoder_task+0x124>
42010aa8:	004ca783          	lw	a5,4(s9)
42010aac:	ed6794e3          	bne	a5,s6,42010974 <decoder_task+0x124>
42010ab0:	478d                	li	a5,3
42010ab2:	00fb03e3          	beq	s6,a5,420112b8 <decoder_task+0xa68>
42010ab6:	47f2                	lw	a5,28(sp)
42010ab8:	00f9e7b3          	or	a5,s3,a5
42010abc:	d3f9                	beqz	a5,42010a82 <decoder_task+0x232>
42010abe:	008cd783          	lhu	a5,8(s9)
42010ac2:	00bc8713          	addi	a4,s9,11
42010ac6:	ce82                	sw	zero,92(sp)
42010ac8:	d082                	sw	zero,96(sp)
42010aca:	d282                	sw	zero,100(sp)
42010acc:	ccbe                	sw	a5,88(sp)
42010ace:	caba                	sw	a4,84(sp)
42010ad0:	00acc703          	lbu	a4,10(s9)
42010ad4:	ffeb0693          	addi	a3,s6,-2
42010ad8:	0016b693          	seqz	a3,a3
42010adc:	00e03733          	snez	a4,a4
42010ae0:	c036                	sw	a3,0(sp)
42010ae2:	04e10e23          	sb	a4,92(sp)
42010ae6:	3a098463          	beqz	s3,42010e8e <decoder_task+0x63e>
42010aea:	e789                	bnez	a5,42010af4 <decoder_task+0x2a4>
42010aec:	05c14783          	lbu	a5,92(sp)
42010af0:	1c078a63          	beqz	a5,42010cc4 <decoder_task+0x474>
42010af4:	4781                	li	a5,0
42010af6:	4801                	li	a6,0
42010af8:	de3e                	sw	a5,60(sp)
42010afa:	c0c2                	sw	a6,64(sp)
42010afc:	da4a                	sw	s2,52(sp)
42010afe:	dc52                	sw	s4,56(sp)
42010b00:	d082                	sw	zero,96(sp)
42010b02:	fe371097          	auipc	ra,0xfe371
42010b06:	838080e7          	jalr	-1992(ra) # 4038133a <esp_timer_get_time>
42010b0a:	842a                	mv	s0,a0
42010b0c:	1850                	addi	a2,sp,52
42010b0e:	08cc                	addi	a1,sp,84
42010b10:	854e                	mv	a0,s3
42010b12:	3cf010ef          	jal	420126e0 <native_aac_decoder_process>
42010b16:	8d2a                	mv	s10,a0
42010b18:	fe371097          	auipc	ra,0xfe371
42010b1c:	822080e7          	jalr	-2014(ra) # 4038133a <esp_timer_get_time>
42010b20:	47ca                	lw	a5,144(sp)
42010b22:	46da                	lw	a3,148(sp)
42010b24:	8d01                	sub	a0,a0,s0
42010b26:	00a78733          	add	a4,a5,a0
42010b2a:	00f737b3          	sltu	a5,a4,a5
42010b2e:	97b6                	add	a5,a5,a3
42010b30:	cb3e                	sw	a5,148(sp)
42010b32:	578a                	lw	a5,160(sp)
42010b34:	c93a                	sw	a4,144(sp)
42010b36:	571a                	lw	a4,164(sp)
42010b38:	0785                	addi	a5,a5,1
42010b3a:	d13e                	sw	a5,160(sp)
42010b3c:	00a77363          	bgeu	a4,a0,42010b42 <decoder_task+0x2f2>
42010b40:	d32a                	sw	a0,164(sp)
42010b42:	8bfd                	andi	a5,a5,31
42010b44:	56078763          	beqz	a5,420110b2 <decoder_task+0x862>
42010b48:	af0a8793          	addi	a5,s5,-1296
42010b4c:	0330000f          	fence	rw,rw
42010b50:	439c                	lw	a5,0(a5)
42010b52:	0230000f          	fence	r,rw
42010b56:	16979763          	bne	a5,s1,42010cc4 <decoder_task+0x474>
42010b5a:	57e1                	li	a5,-8
42010b5c:	52fd0563          	beq	s10,a5,42011086 <decoder_task+0x836>
42010b60:	5a0d1063          	bnez	s10,42011100 <decoder_task+0x8b0>
42010b64:	5786                	lw	a5,96(sp)
42010b66:	4766                	lw	a4,88(sp)
42010b68:	6ef76463          	bltu	a4,a5,42011250 <decoder_task+0xa00>
42010b6c:	8f1d                	sub	a4,a4,a5
42010b6e:	56aa                	lw	a3,168(sp)
42010b70:	ccba                	sw	a4,88(sp)
42010b72:	4756                	lw	a4,84(sp)
42010b74:	96be                	add	a3,a3,a5
42010b76:	d536                	sw	a3,168(sp)
42010b78:	97ba                	add	a5,a5,a4
42010b7a:	4706                	lw	a4,64(sp)
42010b7c:	cabe                	sw	a5,84(sp)
42010b7e:	10070c63          	beqz	a4,42010c96 <decoder_task+0x446>
42010b82:	00cc                	addi	a1,sp,68
42010b84:	854e                	mv	a0,s3
42010b86:	c282                	sw	zero,68(sp)
42010b88:	c482                	sw	zero,72(sp)
42010b8a:	c682                	sw	zero,76(sp)
42010b8c:	c882                	sw	zero,80(sp)
42010b8e:	67b010ef          	jal	42012a08 <native_aac_decoder_get_info>
42010b92:	52051463          	bnez	a0,420110ba <decoder_task+0x86a>
42010b96:	4782                	lw	a5,0(sp)
42010b98:	01b10613          	addi	a2,sp,27
42010b9c:	00cc                	addi	a1,sp,68
42010b9e:	854e                	mv	a0,s3
42010ba0:	00f10da3          	sb	a5,27(sp)
42010ba4:	673010ef          	jal	42012a16 <native_aac_decoder_label>
42010ba8:	01b14683          	lbu	a3,27(sp)
42010bac:	842a                	mv	s0,a0
42010bae:	4501                	li	a0,0
42010bb0:	5c068c63          	beqz	a3,42011188 <decoder_task+0x938>
42010bb4:	af0a8793          	addi	a5,s5,-1296
42010bb8:	0330000f          	fence	rw,rw
42010bbc:	4398                	lw	a4,0(a5)
42010bbe:	0230000f          	fence	r,rw
42010bc2:	4781                	li	a5,0
42010bc4:	06971163          	bne	a4,s1,42010c26 <decoder_task+0x3d6>
42010bc8:	4716                	lw	a4,68(sp)
42010bca:	cf31                	beqz	a4,42010c26 <decoder_task+0x3d6>
42010bcc:	04914803          	lbu	a6,73(sp)
42010bd0:	04080b63          	beqz	a6,42010c26 <decoder_task+0x3d6>
42010bd4:	04814603          	lbu	a2,72(sp)
42010bd8:	c639                	beqz	a2,42010c26 <decoder_task+0x3d6>
42010bda:	45a6                	lw	a1,72(sp)
42010bdc:	47b6                	lw	a5,76(sp)
42010bde:	d23a                	sw	a4,36(sp)
42010be0:	d42e                	sw	a1,40(sp)
42010be2:	45c6                	lw	a1,80(sp)
42010be4:	d63e                	sw	a5,44(sp)
42010be6:	4785                	li	a5,1
42010be8:	06012923          	sw	zero,114(sp)
42010bec:	06012b23          	sw	zero,118(sp)
42010bf0:	06011d23          	sh	zero,122(sp)
42010bf4:	d4a2                	sw	s0,104(sp)
42010bf6:	d6ba                	sw	a4,108(sp)
42010bf8:	d82e                	sw	a1,48(sp)
42010bfa:	00f10d23          	sb	a5,26(sp)
42010bfe:	70050963          	beqz	a0,42011310 <decoder_task+0xac0>
42010c02:	3fc957b7          	lui	a5,0x3fc95
42010c06:	06a10823          	sb	a0,112(sp)
42010c0a:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42010c0e:	06c108a3          	sb	a2,113(sp)
42010c12:	85a6                	mv	a1,s1
42010c14:	10b0                	addi	a2,sp,104
42010c16:	daba                	sw	a4,116(sp)
42010c18:	07010c23          	sb	a6,120(sp)
42010c1c:	06d10d23          	sb	a3,122(sp)
42010c20:	6a2040ef          	jal	420152c2 <native_state_set_stream_info>
42010c24:	4785                	li	a5,1
42010c26:	45b6                	lw	a1,76(sp)
42010c28:	8526                	mv	a0,s1
42010c2a:	00f10d23          	sb	a5,26(sp)
42010c2e:	fe6ff0ef          	jal	42010414 <state_set_decoder_bitrate>
42010c32:	01a14783          	lbu	a5,26(sp)
42010c36:	c3a5                	beqz	a5,42010c96 <decoder_task+0x446>
42010c38:	4a0d8d63          	beqz	s11,420110f2 <decoder_task+0x8a2>
42010c3c:	02814503          	lbu	a0,40(sp)
42010c40:	02914783          	lbu	a5,41(sp)
42010c44:	4406                	lw	s0,64(sp)
42010c46:	051d                	addi	a0,a0,7
42010c48:	810d                	srli	a0,a0,0x3
42010c4a:	02f50533          	mul	a0,a0,a5
42010c4e:	c91d                	beqz	a0,42010c84 <decoder_task+0x434>
42010c50:	5612                	lw	a2,36(sp)
42010c52:	ca0d                	beqz	a2,42010c84 <decoder_task+0x434>
42010c54:	02a45533          	divu	a0,s0,a0
42010c58:	47a2                	lw	a5,8(sp)
42010c5a:	4681                	li	a3,0
42010c5c:	02f535b3          	mulhu	a1,a0,a5
42010c60:	02f50533          	mul	a0,a0,a5
42010c64:	fdff0097          	auipc	ra,0xfdff0
42010c68:	c48080e7          	jalr	-952(ra) # 400008ac <__udivdi3>
42010c6c:	47ea                	lw	a5,152(sp)
42010c6e:	46fa                	lw	a3,156(sp)
42010c70:	573a                	lw	a4,172(sp)
42010c72:	953e                	add	a0,a0,a5
42010c74:	96ae                	add	a3,a3,a1
42010c76:	00f537b3          	sltu	a5,a0,a5
42010c7a:	97b6                	add	a5,a5,a3
42010c7c:	9722                	add	a4,a4,s0
42010c7e:	cf3e                	sw	a5,156(sp)
42010c80:	cd2a                	sw	a0,152(sp)
42010c82:	d73a                	sw	a4,172(sp)
42010c84:	86a2                	mv	a3,s0
42010c86:	864a                	mv	a2,s2
42010c88:	104c                	addi	a1,sp,36
42010c8a:	8526                	mv	a0,s1
42010c8c:	e4cff0ef          	jal	420102d8 <send_pcm>
42010c90:	8daa                	mv	s11,a0
42010c92:	74050463          	beqz	a0,420113da <decoder_task+0xb8a>
42010c96:	fe370097          	auipc	ra,0xfe370
42010c9a:	6a4080e7          	jalr	1700(ra) # 4038133a <esp_timer_get_time>
42010c9e:	862e                	mv	a2,a1
42010ca0:	85aa                	mv	a1,a0
42010ca2:	0108                	addi	a0,sp,128
42010ca4:	9b6ff0ef          	jal	4200fe5a <decode_stats_report>
42010ca8:	4706                	lw	a4,64(sp)
42010caa:	5786                	lw	a5,96(sp)
42010cac:	05c14683          	lbu	a3,92(sp)
42010cb0:	8fd9                	or	a5,a5,a4
42010cb2:	3c079463          	bnez	a5,4201107a <decoder_task+0x82a>
42010cb6:	76068863          	beqz	a3,42011426 <decoder_task+0xbd6>
42010cba:	4701                	li	a4,0
42010cbc:	47e6                	lw	a5,88(sp)
42010cbe:	8f5d                	or	a4,a4,a5
42010cc0:	e20715e3          	bnez	a4,42010aea <decoder_task+0x29a>
42010cc4:	00acc783          	lbu	a5,10(s9)
42010cc8:	48079f63          	bnez	a5,42011166 <decoder_task+0x916>
42010ccc:	489c0d63          	beq	s8,s1,42011166 <decoder_task+0x916>
42010cd0:	8566                	mv	a0,s9
42010cd2:	85e2                	mv	a1,s8
42010cd4:	ab5ff0ef          	jal	42010788 <return_decoded_packet>
42010cd8:	4401                	li	s0,0
42010cda:	af0a8793          	addi	a5,s5,-1296
42010cde:	0330000f          	fence	rw,rw
42010ce2:	0007ac83          	lw	s9,0(a5)
42010ce6:	0230000f          	fence	r,rw
42010cea:	be9c95e3          	bne	s9,s1,420108d4 <decoder_task+0x84>
42010cee:	c40c01e3          	beqz	s8,42010930 <decoder_task+0xe0>
42010cf2:	c29c1fe3          	bne	s8,s1,42010930 <decoder_task+0xe0>
42010cf6:	4572                	lw	a0,28(sp)
42010cf8:	c119                	beqz	a0,42010cfe <decoder_task+0x4ae>
42010cfa:	534260ef          	jal	4203722e <esp_audio_simple_dec_close>
42010cfe:	ce02                	sw	zero,28(sp)
42010d00:	00098563          	beqz	s3,42010d0a <decoder_task+0x4ba>
42010d04:	854e                	mv	a0,s3
42010d06:	1a5010ef          	jal	420126aa <native_aac_decoder_destroy>
42010d0a:	854a                	mv	a0,s2
42010d0c:	ff8f70ef          	jal	42008504 <cfree>
42010d10:	4981                	li	s3,0
42010d12:	4a01                	li	s4,0
42010d14:	4901                	li	s2,0
42010d16:	b929                	j	42010930 <decoder_task+0xe0>
42010d18:	fe377097          	auipc	ra,0xfe377
42010d1c:	6a2080e7          	jalr	1698(ra) # 403883ba <esp_log_timestamp>
42010d20:	3c126737          	lui	a4,0x3c126
42010d24:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
42010d28:	3c126637          	lui	a2,0x3c126
42010d2c:	86aa                	mv	a3,a0
42010d2e:	85ba                	mv	a1,a4
42010d30:	87a2                	mv	a5,s0
42010d32:	a1c60613          	addi	a2,a2,-1508 # 3c125a1c <_esp_trace_encoder_array_end+0x58fc>
42010d36:	4505                	li	a0,1
42010d38:	fe377097          	auipc	ra,0xfe377
42010d3c:	57a080e7          	jalr	1402(ra) # 403882b2 <esp_log>
42010d40:	3fc957b7          	lui	a5,0x3fc95
42010d44:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42010d48:	000ca583          	lw	a1,0(s9)
42010d4c:	3c1267b7          	lui	a5,0x3c126
42010d50:	a4c78693          	addi	a3,a5,-1460 # 3c125a4c <_esp_trace_encoder_array_end+0x592c>
42010d54:	4601                	li	a2,0
42010d56:	48c040ef          	jal	420151e2 <native_state_set_audio>
42010d5a:	000cac03          	lw	s8,0(s9)
42010d5e:	8566                	mv	a0,s9
42010d60:	85e2                	mv	a1,s8
42010d62:	a27ff0ef          	jal	42010788 <return_decoded_packet>
42010d66:	bea9                	j	420108c0 <decoder_task+0x70>
42010d68:	3fc957b7          	lui	a5,0x3fc95
42010d6c:	afc7a503          	lw	a0,-1284(a5) # 3fc94afc <s_encoded>
42010d70:	85e6                	mv	a1,s9
42010d72:	01e660ef          	jal	42076d90 <vRingbufferReturnItem>
42010d76:	b6a9                	j	420108c0 <decoder_task+0x70>
42010d78:	854a                	mv	a0,s2
42010d7a:	f8af70ef          	jal	42008504 <cfree>
42010d7e:	4a01                	li	s4,0
42010d80:	4901                	li	s2,0
42010d82:	b649                	j	42010904 <decoder_task+0xb4>
42010d84:	854a                	mv	a0,s2
42010d86:	f7ef70ef          	jal	42008504 <cfree>
42010d8a:	130240ef          	jal	42034eba <custom_flac_decoder_create>
42010d8e:	8baa                	mv	s7,a0
42010d90:	52050763          	beqz	a0,420112be <decoder_task+0xa6e>
42010d94:	4981                	li	s3,0
42010d96:	4a01                	li	s4,0
42010d98:	4901                	li	s2,0
42010d9a:	4d81                	li	s11,0
42010d9c:	4661                	li	a2,24
42010d9e:	4581                	li	a1,0
42010da0:	10a8                	addi	a0,sp,104
42010da2:	fdfef097          	auipc	ra,0xfdfef
42010da6:	5b2080e7          	jalr	1458(ra) # 40000354 <memset>
42010daa:	011c                	addi	a5,sp,128
42010dac:	ccbe                	sw	a5,88(sp)
42010dae:	105c                	addi	a5,sp,36
42010db0:	cebe                	sw	a5,92(sp)
42010db2:	01a10793          	addi	a5,sp,26
42010db6:	d0be                	sw	a5,96(sp)
42010db8:	caa6                	sw	s1,84(sp)
42010dba:	00acc683          	lbu	a3,10(s9)
42010dbe:	008cd603          	lhu	a2,8(s9)
42010dc2:	42011737          	lui	a4,0x42011
42010dc6:	00d036b3          	snez	a3,a3
42010dca:	08dc                	addi	a5,sp,84
42010dcc:	51270713          	addi	a4,a4,1298 # 42011512 <custom_flac_output>
42010dd0:	00bc8593          	addi	a1,s9,11
42010dd4:	06810813          	addi	a6,sp,104
42010dd8:	855e                	mv	a0,s7
42010dda:	166240ef          	jal	42034f40 <custom_flac_decoder_feed>
42010dde:	47ca                	lw	a5,144(sp)
42010de0:	5726                	lw	a4,104(sp)
42010de2:	465a                	lw	a2,148(sp)
42010de4:	55b6                	lw	a1,108(sp)
42010de6:	568a                	lw	a3,160(sp)
42010de8:	973e                	add	a4,a4,a5
42010dea:	842a                	mv	s0,a0
42010dec:	5546                	lw	a0,112(sp)
42010dee:	962e                	add	a2,a2,a1
42010df0:	00f737b3          	sltu	a5,a4,a5
42010df4:	97b2                	add	a5,a5,a2
42010df6:	55d6                	lw	a1,116(sp)
42010df8:	561a                	lw	a2,164(sp)
42010dfa:	96aa                	add	a3,a3,a0
42010dfc:	c93a                	sw	a4,144(sp)
42010dfe:	cb3e                	sw	a5,148(sp)
42010e00:	d136                	sw	a3,160(sp)
42010e02:	00b67363          	bgeu	a2,a1,42010e08 <decoder_task+0x5b8>
42010e06:	d32e                	sw	a1,164(sp)
42010e08:	57aa                	lw	a5,168(sp)
42010e0a:	5766                	lw	a4,120(sp)
42010e0c:	97ba                	add	a5,a5,a4
42010e0e:	d53e                	sw	a5,168(sp)
42010e10:	500d8863          	beqz	s11,42011320 <decoder_task+0xad0>
42010e14:	4d85                	li	s11,1
42010e16:	fe370097          	auipc	ra,0xfe370
42010e1a:	524080e7          	jalr	1316(ra) # 4038133a <esp_timer_get_time>
42010e1e:	862e                	mv	a2,a1
42010e20:	85aa                	mv	a1,a0
42010e22:	0108                	addi	a0,sp,128
42010e24:	836ff0ef          	jal	4200fe5a <decode_stats_report>
42010e28:	00045b63          	bgez	s0,42010e3e <decoder_task+0x5ee>
42010e2c:	af0a8793          	addi	a5,s5,-1296
42010e30:	0330000f          	fence	rw,rw
42010e34:	439c                	lw	a5,0(a5)
42010e36:	0230000f          	fence	r,rw
42010e3a:	64978863          	beq	a5,s1,4201148a <decoder_task+0xc3a>
42010e3e:	00acc783          	lbu	a5,10(s9)
42010e42:	4c079263          	bnez	a5,42011306 <decoder_task+0xab6>
42010e46:	4c9c0063          	beq	s8,s1,42011306 <decoder_task+0xab6>
42010e4a:	8566                	mv	a0,s9
42010e4c:	85e2                	mv	a1,s8
42010e4e:	93bff0ef          	jal	42010788 <return_decoded_packet>
42010e52:	4b0d                	li	s6,3
42010e54:	4401                	li	s0,0
42010e56:	b4ad                	j	420108c0 <decoder_task+0x70>
42010e58:	6589                	lui	a1,0x2
42010e5a:	36ba0263          	beq	s4,a1,420111be <decoder_task+0x96e>
42010e5e:	854a                	mv	a0,s2
42010e60:	ea0f70ef          	jal	42008500 <realloc>
42010e64:	842a                	mv	s0,a0
42010e66:	68050c63          	beqz	a0,420114fe <decoder_task+0xcae>
42010e6a:	204347b7          	lui	a5,0x20434
42010e6e:	14178793          	addi	a5,a5,321 # 20434141 <CSR_UINTSTATUS+0x20433490>
42010e72:	d682                	sw	zero,108(sp)
42010e74:	d882                	sw	zero,112(sp)
42010e76:	da82                	sw	zero,116(sp)
42010e78:	d4be                	sw	a5,104(sp)
42010e7a:	005010ef          	jal	4201267e <native_aac_decoder_create>
42010e7e:	89aa                	mv	s3,a0
42010e80:	4c050063          	beqz	a0,42011340 <decoder_task+0xaf0>
42010e84:	8922                	mv	s2,s0
42010e86:	6a09                	lui	s4,0x2
42010e88:	4b81                	li	s7,0
42010e8a:	4d81                	li	s11,0
42010e8c:	b90d                	j	42010abe <decoder_task+0x26e>
42010e8e:	5d61                	li	s10,-8
42010e90:	c662                	sw	s8,12(sp)
42010e92:	e789                	bnez	a5,42010e9c <decoder_task+0x64c>
42010e94:	05c14783          	lbu	a5,92(sp)
42010e98:	1c078f63          	beqz	a5,42011076 <decoder_task+0x826>
42010e9c:	4781                	li	a5,0
42010e9e:	4801                	li	a6,0
42010ea0:	de3e                	sw	a5,60(sp)
42010ea2:	c0c2                	sw	a6,64(sp)
42010ea4:	da4a                	sw	s2,52(sp)
42010ea6:	dc52                	sw	s4,56(sp)
42010ea8:	d082                	sw	zero,96(sp)
42010eaa:	fe370097          	auipc	ra,0xfe370
42010eae:	490080e7          	jalr	1168(ra) # 4038133a <esp_timer_get_time>
42010eb2:	842a                	mv	s0,a0
42010eb4:	4572                	lw	a0,28(sp)
42010eb6:	1850                	addi	a2,sp,52
42010eb8:	08cc                	addi	a1,sp,84
42010eba:	490150ef          	jal	4202634a <__wrap_esp_audio_simple_dec_process>
42010ebe:	8c2a                	mv	s8,a0
42010ec0:	fe370097          	auipc	ra,0xfe370
42010ec4:	47a080e7          	jalr	1146(ra) # 4038133a <esp_timer_get_time>
42010ec8:	47ca                	lw	a5,144(sp)
42010eca:	46da                	lw	a3,148(sp)
42010ecc:	8d01                	sub	a0,a0,s0
42010ece:	00a78733          	add	a4,a5,a0
42010ed2:	00f737b3          	sltu	a5,a4,a5
42010ed6:	97b6                	add	a5,a5,a3
42010ed8:	cb3e                	sw	a5,148(sp)
42010eda:	578a                	lw	a5,160(sp)
42010edc:	c93a                	sw	a4,144(sp)
42010ede:	571a                	lw	a4,164(sp)
42010ee0:	0785                	addi	a5,a5,1
42010ee2:	d13e                	sw	a5,160(sp)
42010ee4:	00a77363          	bgeu	a4,a0,42010eea <decoder_task+0x69a>
42010ee8:	d32a                	sw	a0,164(sp)
42010eea:	8bfd                	andi	a5,a5,31
42010eec:	1e078c63          	beqz	a5,420110e4 <decoder_task+0x894>
42010ef0:	af0a8793          	addi	a5,s5,-1296
42010ef4:	0330000f          	fence	rw,rw
42010ef8:	439c                	lw	a5,0(a5)
42010efa:	0230000f          	fence	r,rw
42010efe:	16979c63          	bne	a5,s1,42011076 <decoder_task+0x826>
42010f02:	1dac0563          	beq	s8,s10,420110cc <decoder_task+0x87c>
42010f06:	4e0c1f63          	bnez	s8,42011404 <decoder_task+0xbb4>
42010f0a:	5786                	lw	a5,96(sp)
42010f0c:	4766                	lw	a4,88(sp)
42010f0e:	34f76163          	bltu	a4,a5,42011250 <decoder_task+0xa00>
42010f12:	8f1d                	sub	a4,a4,a5
42010f14:	56aa                	lw	a3,168(sp)
42010f16:	ccba                	sw	a4,88(sp)
42010f18:	4756                	lw	a4,84(sp)
42010f1a:	96be                	add	a3,a3,a5
42010f1c:	d536                	sw	a3,168(sp)
42010f1e:	97ba                	add	a5,a5,a4
42010f20:	4706                	lw	a4,64(sp)
42010f22:	cabe                	sw	a5,84(sp)
42010f24:	12070363          	beqz	a4,4201104a <decoder_task+0x7fa>
42010f28:	4572                	lw	a0,28(sp)
42010f2a:	00cc                	addi	a1,sp,68
42010f2c:	c282                	sw	zero,68(sp)
42010f2e:	c482                	sw	zero,72(sp)
42010f30:	c682                	sw	zero,76(sp)
42010f32:	c882                	sw	zero,80(sp)
42010f34:	282260ef          	jal	420371b6 <esp_audio_simple_dec_get_info>
42010f38:	1a051a63          	bnez	a0,420110ec <decoder_task+0x89c>
42010f3c:	4782                	lw	a5,0(sp)
42010f3e:	00f10da3          	sb	a5,27(sp)
42010f42:	4789                	li	a5,2
42010f44:	46fb0263          	beq	s6,a5,420113a8 <decoder_task+0xb58>
42010f48:	4791                	li	a5,4
42010f4a:	44fb0a63          	beq	s6,a5,4201139e <decoder_task+0xb4e>
42010f4e:	3c126737          	lui	a4,0x3c126
42010f52:	4785                	li	a5,1
42010f54:	80070593          	addi	a1,a4,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
42010f58:	3cfb1f63          	bne	s6,a5,42011336 <decoder_task+0xae6>
42010f5c:	af0a8793          	addi	a5,s5,-1296
42010f60:	0330000f          	fence	rw,rw
42010f64:	439c                	lw	a5,0(a5)
42010f66:	0230000f          	fence	r,rw
42010f6a:	06979463          	bne	a5,s1,42010fd2 <decoder_task+0x782>
42010f6e:	4796                	lw	a5,68(sp)
42010f70:	c3b5                	beqz	a5,42010fd4 <decoder_task+0x784>
42010f72:	04914683          	lbu	a3,73(sp)
42010f76:	ceb1                	beqz	a3,42010fd2 <decoder_task+0x782>
42010f78:	04815703          	lhu	a4,72(sp)
42010f7c:	04814503          	lbu	a0,72(sp)
42010f80:	00875613          	srli	a2,a4,0x8
42010f84:	0722                	slli	a4,a4,0x8
42010f86:	963a                	add	a2,a2,a4
42010f88:	c529                	beqz	a0,42010fd2 <decoder_task+0x782>
42010f8a:	06012b23          	sw	zero,118(sp)
42010f8e:	06012923          	sw	zero,114(sp)
42010f92:	d23e                	sw	a5,36(sp)
42010f94:	06c11823          	sh	a2,112(sp)
42010f98:	d6be                	sw	a5,108(sp)
42010f9a:	4626                	lw	a2,72(sp)
42010f9c:	dabe                	sw	a5,116(sp)
42010f9e:	3fc957b7          	lui	a5,0x3fc95
42010fa2:	4746                	lw	a4,80(sp)
42010fa4:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42010fa8:	06d10c23          	sb	a3,120(sp)
42010fac:	4782                	lw	a5,0(sp)
42010fae:	46b6                	lw	a3,76(sp)
42010fb0:	06011d23          	sh	zero,122(sp)
42010fb4:	d4ae                	sw	a1,104(sp)
42010fb6:	d432                	sw	a2,40(sp)
42010fb8:	4405                	li	s0,1
42010fba:	10b0                	addi	a2,sp,104
42010fbc:	85a6                	mv	a1,s1
42010fbe:	06f10d23          	sb	a5,122(sp)
42010fc2:	d636                	sw	a3,44(sp)
42010fc4:	d83a                	sw	a4,48(sp)
42010fc6:	00810d23          	sb	s0,26(sp)
42010fca:	2f8040ef          	jal	420152c2 <native_state_set_stream_info>
42010fce:	87a2                	mv	a5,s0
42010fd0:	a011                	j	42010fd4 <decoder_task+0x784>
42010fd2:	4781                	li	a5,0
42010fd4:	45b6                	lw	a1,76(sp)
42010fd6:	8526                	mv	a0,s1
42010fd8:	00f10d23          	sb	a5,26(sp)
42010fdc:	c38ff0ef          	jal	42010414 <state_set_decoder_bitrate>
42010fe0:	01a14783          	lbu	a5,26(sp)
42010fe4:	c3bd                	beqz	a5,4201104a <decoder_task+0x7fa>
42010fe6:	1c0d8e63          	beqz	s11,420111c2 <decoder_task+0x972>
42010fea:	02814503          	lbu	a0,40(sp)
42010fee:	02914783          	lbu	a5,41(sp)
42010ff2:	4406                	lw	s0,64(sp)
42010ff4:	051d                	addi	a0,a0,7
42010ff6:	810d                	srli	a0,a0,0x3
42010ff8:	02f50533          	mul	a0,a0,a5
42010ffc:	cd15                	beqz	a0,42011038 <decoder_task+0x7e8>
42010ffe:	5612                	lw	a2,36(sp)
42011000:	ce05                	beqz	a2,42011038 <decoder_task+0x7e8>
42011002:	02a45533          	divu	a0,s0,a0
42011006:	000f47b7          	lui	a5,0xf4
4201100a:	24078793          	addi	a5,a5,576 # f4240 <CSR_UINTSTATUS+0xf358f>
4201100e:	4681                	li	a3,0
42011010:	02f535b3          	mulhu	a1,a0,a5
42011014:	02f50533          	mul	a0,a0,a5
42011018:	fdff0097          	auipc	ra,0xfdff0
4201101c:	894080e7          	jalr	-1900(ra) # 400008ac <__udivdi3>
42011020:	47ea                	lw	a5,152(sp)
42011022:	46fa                	lw	a3,156(sp)
42011024:	573a                	lw	a4,172(sp)
42011026:	953e                	add	a0,a0,a5
42011028:	96ae                	add	a3,a3,a1
4201102a:	00f537b3          	sltu	a5,a0,a5
4201102e:	97b6                	add	a5,a5,a3
42011030:	9722                	add	a4,a4,s0
42011032:	cf3e                	sw	a5,156(sp)
42011034:	cd2a                	sw	a0,152(sp)
42011036:	d73a                	sw	a4,172(sp)
42011038:	86a2                	mv	a3,s0
4201103a:	864a                	mv	a2,s2
4201103c:	104c                	addi	a1,sp,36
4201103e:	8526                	mv	a0,s1
42011040:	a98ff0ef          	jal	420102d8 <send_pcm>
42011044:	8daa                	mv	s11,a0
42011046:	38050963          	beqz	a0,420113d8 <decoder_task+0xb88>
4201104a:	fe370097          	auipc	ra,0xfe370
4201104e:	2f0080e7          	jalr	752(ra) # 4038133a <esp_timer_get_time>
42011052:	862e                	mv	a2,a1
42011054:	85aa                	mv	a1,a0
42011056:	0108                	addi	a0,sp,128
42011058:	e03fe0ef          	jal	4200fe5a <decode_stats_report>
4201105c:	4706                	lw	a4,64(sp)
4201105e:	5786                	lw	a5,96(sp)
42011060:	05c14683          	lbu	a3,92(sp)
42011064:	8fd9                	or	a5,a5,a4
42011066:	efa9                	bnez	a5,420110c0 <decoder_task+0x870>
42011068:	3a068f63          	beqz	a3,42011426 <decoder_task+0xbd6>
4201106c:	4701                	li	a4,0
4201106e:	47e6                	lw	a5,88(sp)
42011070:	8f5d                	or	a4,a4,a5
42011072:	e20710e3          	bnez	a4,42010e92 <decoder_task+0x642>
42011076:	4c32                	lw	s8,12(sp)
42011078:	b1b1                	j	42010cc4 <decoder_task+0x474>
4201107a:	c40691e3          	bnez	a3,42010cbc <decoder_task+0x46c>
4201107e:	47e6                	lw	a5,88(sp)
42011080:	a6079ae3          	bnez	a5,42010af4 <decoder_task+0x2a4>
42011084:	b181                	j	42010cc4 <decoder_task+0x474>
42011086:	5706                	lw	a4,96(sp)
42011088:	47d6                	lw	a5,84(sp)
4201108a:	56aa                	lw	a3,168(sp)
4201108c:	5472                	lw	s0,60(sp)
4201108e:	97ba                	add	a5,a5,a4
42011090:	cabe                	sw	a5,84(sp)
42011092:	47e6                	lw	a5,88(sp)
42011094:	96ba                	add	a3,a3,a4
42011096:	d536                	sw	a3,168(sp)
42011098:	8f99                	sub	a5,a5,a4
4201109a:	ccbe                	sw	a5,88(sp)
4201109c:	308a7b63          	bgeu	s4,s0,420113b2 <decoder_task+0xb62>
420110a0:	85a2                	mv	a1,s0
420110a2:	854a                	mv	a0,s2
420110a4:	c5cf70ef          	jal	42008500 <realloc>
420110a8:	30050563          	beqz	a0,420113b2 <decoder_task+0xb62>
420110ac:	8a22                	mv	s4,s0
420110ae:	892a                	mv	s2,a0
420110b0:	b491                	j	42010af4 <decoder_task+0x2a4>
420110b2:	4505                	li	a0,1
420110b4:	2bbff0ef          	jal	42110b6e <vTaskDelay>
420110b8:	bc41                	j	42010b48 <decoder_task+0x2f8>
420110ba:	00010d23          	sb	zero,26(sp)
420110be:	bee1                	j	42010c96 <decoder_task+0x446>
420110c0:	f6dd                	bnez	a3,4201106e <decoder_task+0x81e>
420110c2:	47e6                	lw	a5,88(sp)
420110c4:	dc079ce3          	bnez	a5,42010e9c <decoder_task+0x64c>
420110c8:	4c32                	lw	s8,12(sp)
420110ca:	beed                	j	42010cc4 <decoder_task+0x474>
420110cc:	5472                	lw	s0,60(sp)
420110ce:	2e8a7263          	bgeu	s4,s0,420113b2 <decoder_task+0xb62>
420110d2:	85a2                	mv	a1,s0
420110d4:	854a                	mv	a0,s2
420110d6:	c2af70ef          	jal	42008500 <realloc>
420110da:	2c050c63          	beqz	a0,420113b2 <decoder_task+0xb62>
420110de:	892a                	mv	s2,a0
420110e0:	8a22                	mv	s4,s0
420110e2:	bb6d                	j	42010e9c <decoder_task+0x64c>
420110e4:	4505                	li	a0,1
420110e6:	289ff0ef          	jal	42110b6e <vTaskDelay>
420110ea:	b519                	j	42010ef0 <decoder_task+0x6a0>
420110ec:	00010d23          	sb	zero,26(sp)
420110f0:	bfa9                	j	4201104a <decoder_task+0x7fa>
420110f2:	3c1267b7          	lui	a5,0x3c126
420110f6:	b3078513          	addi	a0,a5,-1232 # 3c125b30 <_esp_trace_encoder_array_end+0x5a10>
420110fa:	97aff0ef          	jal	42010274 <log_runtime_memory>
420110fe:	be3d                	j	42010c3c <decoder_task+0x3ec>
42011100:	846a                	mv	s0,s10
42011102:	4a09                	li	s4,2
42011104:	fe377097          	auipc	ra,0xfe377
42011108:	2b6080e7          	jalr	694(ra) # 403883ba <esp_log_timestamp>
4201110c:	2f4b0e63          	beq	s6,s4,42011408 <decoder_task+0xbb8>
42011110:	4791                	li	a5,4
42011112:	30fb0063          	beq	s6,a5,42011412 <decoder_task+0xbc2>
42011116:	3c1267b7          	lui	a5,0x3c126
4201111a:	4705                	li	a4,1
4201111c:	80078793          	addi	a5,a5,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
42011120:	00eb0663          	beq	s6,a4,4201112c <decoder_task+0x8dc>
42011124:	3c1267b7          	lui	a5,0x3c126
42011128:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
4201112c:	3c126737          	lui	a4,0x3c126
42011130:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
42011134:	3c126637          	lui	a2,0x3c126
42011138:	86aa                	mv	a3,a0
4201113a:	85ba                	mv	a1,a4
4201113c:	8822                	mv	a6,s0
4201113e:	b6460613          	addi	a2,a2,-1180 # 3c125b64 <_esp_trace_encoder_array_end+0x5a44>
42011142:	4509                	li	a0,2
42011144:	fe377097          	auipc	ra,0xfe377
42011148:	16e080e7          	jalr	366(ra) # 403882b2 <esp_log>
4201114c:	3fc957b7          	lui	a5,0x3fc95
42011150:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42011154:	3c1267b7          	lui	a5,0x3c126
42011158:	a0c78693          	addi	a3,a5,-1524 # 3c125a0c <_esp_trace_encoder_array_end+0x58ec>
4201115c:	85a6                	mv	a1,s1
4201115e:	4601                	li	a2,0
42011160:	082040ef          	jal	420151e2 <native_state_set_audio>
42011164:	8c26                	mv	s8,s1
42011166:	4572                	lw	a0,28(sp)
42011168:	c119                	beqz	a0,4201116e <decoder_task+0x91e>
4201116a:	0c4260ef          	jal	4203722e <esp_audio_simple_dec_close>
4201116e:	ce02                	sw	zero,28(sp)
42011170:	00098563          	beqz	s3,4201117a <decoder_task+0x92a>
42011174:	854e                	mv	a0,s3
42011176:	534010ef          	jal	420126aa <native_aac_decoder_destroy>
4201117a:	854a                	mv	a0,s2
4201117c:	b88f70ef          	jal	42008504 <cfree>
42011180:	4981                	li	s3,0
42011182:	4a01                	li	s4,0
42011184:	4901                	li	s2,0
42011186:	b6a9                	j	42010cd0 <decoder_task+0x480>
42011188:	854e                	mv	a0,s3
4201118a:	0e5010ef          	jal	42012a6e <native_aac_decoder_source_channels>
4201118e:	01b14683          	lbu	a3,27(sp)
42011192:	0ff57513          	zext.b	a0,a0
42011196:	bc39                	j	42010bb4 <decoder_task+0x364>
42011198:	204747b7          	lui	a5,0x20474
4201119c:	74f78793          	addi	a5,a5,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
420111a0:	086c                	addi	a1,sp,28
420111a2:	10a8                	addi	a0,sp,104
420111a4:	d4be                	sw	a5,104(sp)
420111a6:	018150ef          	jal	420261be <__wrap_esp_audio_simple_dec_open>
420111aa:	842a                	mv	s0,a0
420111ac:	1c051963          	bnez	a0,4201137e <decoder_task+0xb2e>
420111b0:	4bf2                	lw	s7,28(sp)
420111b2:	4d81                	li	s11,0
420111b4:	8c0b87e3          	beqz	s7,42010a82 <decoder_task+0x232>
420111b8:	4981                	li	s3,0
420111ba:	4b81                	li	s7,0
420111bc:	b209                	j	42010abe <decoder_task+0x26e>
420111be:	844a                	mv	s0,s2
420111c0:	b16d                	j	42010e6a <decoder_task+0x61a>
420111c2:	3c1267b7          	lui	a5,0x3c126
420111c6:	b3078513          	addi	a0,a5,-1232 # 3c125b30 <_esp_trace_encoder_array_end+0x5a10>
420111ca:	8aaff0ef          	jal	42010274 <log_runtime_memory>
420111ce:	bd31                	j	42010fea <decoder_task+0x79a>
420111d0:	d682                	sw	zero,108(sp)
420111d2:	d882                	sw	zero,112(sp)
420111d4:	da82                	sw	zero,116(sp)
420111d6:	821ff06f          	j	420109f6 <decoder_task+0x1a6>
420111da:	fe377097          	auipc	ra,0xfe377
420111de:	1e0080e7          	jalr	480(ra) # 403883ba <esp_log_timestamp>
420111e2:	4791                	li	a5,4
420111e4:	4405                	li	s0,1
420111e6:	86aa                	mv	a3,a0
420111e8:	1efb0363          	beq	s6,a5,420113ce <decoder_task+0xb7e>
420111ec:	3c1267b7          	lui	a5,0x3c126
420111f0:	80078793          	addi	a5,a5,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
420111f4:	008b0663          	beq	s6,s0,42011200 <decoder_task+0x9b0>
420111f8:	3c1267b7          	lui	a5,0x3c126
420111fc:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
42011200:	3c126737          	lui	a4,0x3c126
42011204:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
42011208:	3c126637          	lui	a2,0x3c126
4201120c:	85ba                	mv	a1,a4
4201120e:	a9460613          	addi	a2,a2,-1388 # 3c125a94 <_esp_trace_encoder_array_end+0x5974>
42011212:	4505                	li	a0,1
42011214:	fe377097          	auipc	ra,0xfe377
42011218:	09e080e7          	jalr	158(ra) # 403882b2 <esp_log>
4201121c:	3fc957b7          	lui	a5,0x3fc95
42011220:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42011224:	3c1267b7          	lui	a5,0x3c126
42011228:	9f078693          	addi	a3,a5,-1552 # 3c1259f0 <_esp_trace_encoder_array_end+0x58d0>
4201122c:	85a6                	mv	a1,s1
4201122e:	4601                	li	a2,0
42011230:	7b3030ef          	jal	420151e2 <native_state_set_audio>
42011234:	3fc957b7          	lui	a5,0x3fc95
42011238:	afc7a503          	lw	a0,-1284(a5) # 3fc94afc <s_encoded>
4201123c:	85e6                	mv	a1,s9
4201123e:	8c26                	mv	s8,s1
42011240:	351650ef          	jal	42076d90 <vRingbufferReturnItem>
42011244:	4981                	li	s3,0
42011246:	4d81                	li	s11,0
42011248:	4b81                	li	s7,0
4201124a:	4401                	li	s0,0
4201124c:	e74ff06f          	j	420108c0 <decoder_task+0x70>
42011250:	fe377097          	auipc	ra,0xfe377
42011254:	16a080e7          	jalr	362(ra) # 403883ba <esp_log_timestamp>
42011258:	4789                	li	a5,2
4201125a:	4405                	li	s0,1
4201125c:	12fb0c63          	beq	s6,a5,42011394 <decoder_task+0xb44>
42011260:	4791                	li	a5,4
42011262:	1afb0d63          	beq	s6,a5,4201141c <decoder_task+0xbcc>
42011266:	3c1267b7          	lui	a5,0x3c126
4201126a:	80078793          	addi	a5,a5,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
4201126e:	008b0663          	beq	s6,s0,4201127a <decoder_task+0xa2a>
42011272:	3c1267b7          	lui	a5,0x3c126
42011276:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
4201127a:	48e6                	lw	a7,88(sp)
4201127c:	5806                	lw	a6,96(sp)
4201127e:	3c126737          	lui	a4,0x3c126
42011282:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
42011286:	3c126637          	lui	a2,0x3c126
4201128a:	86aa                	mv	a3,a0
4201128c:	85ba                	mv	a1,a4
4201128e:	b8860613          	addi	a2,a2,-1144 # 3c125b88 <_esp_trace_encoder_array_end+0x5a68>
42011292:	4505                	li	a0,1
42011294:	fe377097          	auipc	ra,0xfe377
42011298:	01e080e7          	jalr	30(ra) # 403882b2 <esp_log>
4201129c:	3fc957b7          	lui	a5,0x3fc95
420112a0:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
420112a4:	3c1267b7          	lui	a5,0x3c126
420112a8:	bc478693          	addi	a3,a5,-1084 # 3c125bc4 <_esp_trace_encoder_array_end+0x5aa4>
420112ac:	85a6                	mv	a1,s1
420112ae:	4601                	li	a2,0
420112b0:	733030ef          	jal	420151e2 <native_state_set_audio>
420112b4:	8c26                	mv	s8,s1
420112b6:	bd45                	j	42011166 <decoder_task+0x916>
420112b8:	b80b83e3          	beqz	s7,42010e3e <decoder_task+0x5ee>
420112bc:	b4c5                	j	42010d9c <decoder_task+0x54c>
420112be:	fe377097          	auipc	ra,0xfe377
420112c2:	0fc080e7          	jalr	252(ra) # 403883ba <esp_log_timestamp>
420112c6:	3c1267b7          	lui	a5,0x3c126
420112ca:	80c78713          	addi	a4,a5,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
420112ce:	3c1267b7          	lui	a5,0x3c126
420112d2:	86aa                	mv	a3,a0
420112d4:	85ba                	mv	a1,a4
420112d6:	a6078613          	addi	a2,a5,-1440 # 3c125a60 <_esp_trace_encoder_array_end+0x5940>
420112da:	4505                	li	a0,1
420112dc:	fe377097          	auipc	ra,0xfe377
420112e0:	fd6080e7          	jalr	-42(ra) # 403882b2 <esp_log>
420112e4:	3fc957b7          	lui	a5,0x3fc95
420112e8:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
420112ec:	3c1267b7          	lui	a5,0x3c126
420112f0:	9f078693          	addi	a3,a5,-1552 # 3c1259f0 <_esp_trace_encoder_array_end+0x58d0>
420112f4:	85a6                	mv	a1,s1
420112f6:	4601                	li	a2,0
420112f8:	6eb030ef          	jal	420151e2 <native_state_set_audio>
420112fc:	8c26                	mv	s8,s1
420112fe:	4981                	li	s3,0
42011300:	4901                	li	s2,0
42011302:	4a01                	li	s4,0
42011304:	4d81                	li	s11,0
42011306:	855e                	mv	a0,s7
42011308:	413230ef          	jal	42034f1a <custom_flac_decoder_destroy>
4201130c:	4b81                	li	s7,0
4201130e:	be35                	j	42010e4a <decoder_task+0x5fa>
42011310:	8542                	mv	a0,a6
42011312:	b8c5                	j	42010c02 <decoder_task+0x3b2>
42011314:	3c1267b7          	lui	a5,0x3c126
42011318:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
4201131c:	f10ff06f          	j	42010a2c <decoder_task+0x1dc>
42011320:	01a14d83          	lbu	s11,26(sp)
42011324:	ae0d89e3          	beqz	s11,42010e16 <decoder_task+0x5c6>
42011328:	3c1267b7          	lui	a5,0x3c126
4201132c:	aec78513          	addi	a0,a5,-1300 # 3c125aec <_esp_trace_encoder_array_end+0x59cc>
42011330:	f45fe0ef          	jal	42010274 <log_runtime_memory>
42011334:	b4c5                	j	42010e14 <decoder_task+0x5c4>
42011336:	3c1267b7          	lui	a5,0x3c126
4201133a:	80478593          	addi	a1,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
4201133e:	b939                	j	42010f5c <decoder_task+0x70c>
42011340:	fe377097          	auipc	ra,0xfe377
42011344:	07a080e7          	jalr	122(ra) # 403883ba <esp_log_timestamp>
42011348:	3c1267b7          	lui	a5,0x3c126
4201134c:	80c78713          	addi	a4,a5,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
42011350:	3c126637          	lui	a2,0x3c126
42011354:	3c1257b7          	lui	a5,0x3c125
42011358:	86aa                	mv	a3,a0
4201135a:	7f078793          	addi	a5,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
4201135e:	85ba                	mv	a1,a4
42011360:	ac460613          	addi	a2,a2,-1340 # 3c125ac4 <_esp_trace_encoder_array_end+0x59a4>
42011364:	5879                	li	a6,-2
42011366:	4505                	li	a0,1
42011368:	fe377097          	auipc	ra,0xfe377
4201136c:	f4a080e7          	jalr	-182(ra) # 403882b2 <esp_log>
42011370:	3c1267b7          	lui	a5,0x3c126
42011374:	8922                	mv	s2,s0
42011376:	9f078693          	addi	a3,a5,-1552 # 3c1259f0 <_esp_trace_encoder_array_end+0x58d0>
4201137a:	edeff06f          	j	42010a58 <decoder_task+0x208>
4201137e:	fe377097          	auipc	ra,0xfe377
42011382:	03c080e7          	jalr	60(ra) # 403883ba <esp_log_timestamp>
42011386:	3c1257b7          	lui	a5,0x3c125
4201138a:	86aa                	mv	a3,a0
4201138c:	7fc78793          	addi	a5,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
42011390:	e9cff06f          	j	42010a2c <decoder_task+0x1dc>
42011394:	3c1257b7          	lui	a5,0x3c125
42011398:	7f078793          	addi	a5,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
4201139c:	bdf9                	j	4201127a <decoder_task+0xa2a>
4201139e:	3c1257b7          	lui	a5,0x3c125
420113a2:	7fc78593          	addi	a1,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
420113a6:	be5d                	j	42010f5c <decoder_task+0x70c>
420113a8:	3c1257b7          	lui	a5,0x3c125
420113ac:	7f078593          	addi	a1,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
420113b0:	b675                	j	42010f5c <decoder_task+0x70c>
420113b2:	3fc957b7          	lui	a5,0x3fc95
420113b6:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
420113ba:	3c1267b7          	lui	a5,0x3c126
420113be:	b4c78693          	addi	a3,a5,-1204 # 3c125b4c <_esp_trace_encoder_array_end+0x5a2c>
420113c2:	4601                	li	a2,0
420113c4:	85a6                	mv	a1,s1
420113c6:	61d030ef          	jal	420151e2 <native_state_set_audio>
420113ca:	8c26                	mv	s8,s1
420113cc:	bb69                	j	42011166 <decoder_task+0x916>
420113ce:	3c1257b7          	lui	a5,0x3c125
420113d2:	7fc78793          	addi	a5,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
420113d6:	b52d                	j	42011200 <decoder_task+0x9b0>
420113d8:	4c32                	lw	s8,12(sp)
420113da:	fe377097          	auipc	ra,0xfe377
420113de:	fe0080e7          	jalr	-32(ra) # 403883ba <esp_log_timestamp>
420113e2:	3c1267b7          	lui	a5,0x3c126
420113e6:	80c78713          	addi	a4,a5,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
420113ea:	3c1267b7          	lui	a5,0x3c126
420113ee:	86aa                	mv	a3,a0
420113f0:	85ba                	mv	a1,a4
420113f2:	bd878613          	addi	a2,a5,-1064 # 3c125bd8 <_esp_trace_encoder_array_end+0x5ab8>
420113f6:	4509                	li	a0,2
420113f8:	fe377097          	auipc	ra,0xfe377
420113fc:	eba080e7          	jalr	-326(ra) # 403882b2 <esp_log>
42011400:	4d85                	li	s11,1
42011402:	b0c9                	j	42010cc4 <decoder_task+0x474>
42011404:	8462                	mv	s0,s8
42011406:	b9f5                	j	42011102 <decoder_task+0x8b2>
42011408:	3c1257b7          	lui	a5,0x3c125
4201140c:	7f078793          	addi	a5,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
42011410:	bb31                	j	4201112c <decoder_task+0x8dc>
42011412:	3c1257b7          	lui	a5,0x3c125
42011416:	7fc78793          	addi	a5,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
4201141a:	bb09                	j	4201112c <decoder_task+0x8dc>
4201141c:	3c1257b7          	lui	a5,0x3c125
42011420:	7fc78793          	addi	a5,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
42011424:	bd99                	j	4201127a <decoder_task+0xa2a>
42011426:	fe377097          	auipc	ra,0xfe377
4201142a:	f94080e7          	jalr	-108(ra) # 403883ba <esp_log_timestamp>
4201142e:	4789                	li	a5,2
42011430:	4405                	li	s0,1
42011432:	86aa                	mv	a3,a0
42011434:	0afb0563          	beq	s6,a5,420114de <decoder_task+0xc8e>
42011438:	4791                	li	a5,4
4201143a:	0afb0d63          	beq	s6,a5,420114f4 <decoder_task+0xca4>
4201143e:	3c1267b7          	lui	a5,0x3c126
42011442:	80078793          	addi	a5,a5,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
42011446:	008b0663          	beq	s6,s0,42011452 <decoder_task+0xc02>
4201144a:	3c1267b7          	lui	a5,0x3c126
4201144e:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
42011452:	3c126737          	lui	a4,0x3c126
42011456:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
4201145a:	3c126637          	lui	a2,0x3c126
4201145e:	85ba                	mv	a1,a4
42011460:	bf860613          	addi	a2,a2,-1032 # 3c125bf8 <_esp_trace_encoder_array_end+0x5ad8>
42011464:	4505                	li	a0,1
42011466:	fe377097          	auipc	ra,0xfe377
4201146a:	e4c080e7          	jalr	-436(ra) # 403882b2 <esp_log>
4201146e:	3fc957b7          	lui	a5,0x3fc95
42011472:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42011476:	3c1267b7          	lui	a5,0x3c126
4201147a:	c2878693          	addi	a3,a5,-984 # 3c125c28 <_esp_trace_encoder_array_end+0x5b08>
4201147e:	85a6                	mv	a1,s1
42011480:	4601                	li	a2,0
42011482:	561030ef          	jal	420151e2 <native_state_set_audio>
42011486:	8c26                	mv	s8,s1
42011488:	b9f9                	j	42011166 <decoder_task+0x916>
4201148a:	fe377097          	auipc	ra,0xfe377
4201148e:	f30080e7          	jalr	-208(ra) # 403883ba <esp_log_timestamp>
42011492:	3c126737          	lui	a4,0x3c126
42011496:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
4201149a:	3c126637          	lui	a2,0x3c126
4201149e:	86aa                	mv	a3,a0
420114a0:	87a2                	mv	a5,s0
420114a2:	85ba                	mv	a1,a4
420114a4:	b0460613          	addi	a2,a2,-1276 # 3c125b04 <_esp_trace_encoder_array_end+0x59e4>
420114a8:	4509                	li	a0,2
420114aa:	fe377097          	auipc	ra,0xfe377
420114ae:	e08080e7          	jalr	-504(ra) # 403882b2 <esp_log>
420114b2:	3c126737          	lui	a4,0x3c126
420114b6:	0419                	addi	s0,s0,6 # 3006 <CSR_UINTSTATUS+0x2355>
420114b8:	4785                	li	a5,1
420114ba:	a0c70693          	addi	a3,a4,-1524 # 3c125a0c <_esp_trace_encoder_array_end+0x58ec>
420114be:	0087e663          	bltu	a5,s0,420114ca <decoder_task+0xc7a>
420114c2:	3c1267b7          	lui	a5,0x3c126
420114c6:	9f078693          	addi	a3,a5,-1552 # 3c1259f0 <_esp_trace_encoder_array_end+0x58d0>
420114ca:	3fc957b7          	lui	a5,0x3fc95
420114ce:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
420114d2:	4601                	li	a2,0
420114d4:	85a6                	mv	a1,s1
420114d6:	50d030ef          	jal	420151e2 <native_state_set_audio>
420114da:	8c26                	mv	s8,s1
420114dc:	b28d                	j	42010e3e <decoder_task+0x5ee>
420114de:	3c1257b7          	lui	a5,0x3c125
420114e2:	7f078793          	addi	a5,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
420114e6:	b7b5                	j	42011452 <decoder_task+0xc02>
420114e8:	3c1267b7          	lui	a5,0x3c126
420114ec:	9f078693          	addi	a3,a5,-1552 # 3c1259f0 <_esp_trace_encoder_array_end+0x58d0>
420114f0:	d68ff06f          	j	42010a58 <decoder_task+0x208>
420114f4:	3c1257b7          	lui	a5,0x3c125
420114f8:	7fc78793          	addi	a5,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
420114fc:	bf99                	j	42011452 <decoder_task+0xc02>
420114fe:	fe377097          	auipc	ra,0xfe377
42011502:	ebc080e7          	jalr	-324(ra) # 403883ba <esp_log_timestamp>
42011506:	3c1257b7          	lui	a5,0x3c125
4201150a:	86aa                	mv	a3,a0
4201150c:	7f078793          	addi	a5,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
42011510:	b9c5                	j	42011200 <decoder_task+0x9b0>
