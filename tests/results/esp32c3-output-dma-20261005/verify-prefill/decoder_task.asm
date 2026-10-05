
idf\esp32c3-oled-native\build-output-dma-leased\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


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
4201086c:	5c9010ef          	jal	42012634 <decoder_register_codecs>
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
420108ea:	131260ef          	jal	4203721a <esp_audio_simple_dec_close>
420108ee:	854e                	mv	a0,s3
420108f0:	ce02                	sw	zero,28(sp)
420108f2:	5a5010ef          	jal	42012696 <native_aac_decoder_destroy>
420108f6:	000b8563          	beqz	s7,42010900 <decoder_task+0xb0>
420108fa:	855e                	mv	a0,s7
420108fc:	60a240ef          	jal	42034f06 <custom_flac_decoder_destroy>
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
4201093e:	3c2660ef          	jal	42076d00 <xRingbufferReceive>
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
42010970:	12978c63          	beq	a5,s1,42010aa8 <decoder_task+0x258>
42010974:	4572                	lw	a0,28(sp)
42010976:	c119                	beqz	a0,4201097c <decoder_task+0x12c>
42010978:	0a3260ef          	jal	4203721a <esp_audio_simple_dec_close>
4201097c:	854e                	mv	a0,s3
4201097e:	ce02                	sw	zero,28(sp)
42010980:	517010ef          	jal	42012696 <native_aac_decoder_destroy>
42010984:	000b8563          	beqz	s7,4201098e <decoder_task+0x13e>
42010988:	855e                	mv	a0,s7
4201098a:	57c240ef          	jal	42034f06 <custom_flac_decoder_destroy>
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
420109d6:	46fb0b63          	beq	s6,a5,42010e4c <decoder_task+0x5fc>
420109da:	640d                	lui	s0,0x3
420109dc:	7e8a7463          	bgeu	s4,s0,420111c4 <decoder_task+0x974>
420109e0:	85a2                	mv	a1,s0
420109e2:	854a                	mv	a0,s2
420109e4:	b1df70ef          	jal	42008500 <realloc>
420109e8:	7e050363          	beqz	a0,420111ce <decoder_task+0x97e>
420109ec:	d682                	sw	zero,108(sp)
420109ee:	d882                	sw	zero,112(sp)
420109f0:	da82                	sw	zero,116(sp)
420109f2:	892a                	mv	s2,a0
420109f4:	8a22                	mv	s4,s0
420109f6:	4791                	li	a5,4
420109f8:	78fb0a63          	beq	s6,a5,4201118c <decoder_task+0x93c>
420109fc:	203357b7          	lui	a5,0x20335
42010a00:	04d78793          	addi	a5,a5,77 # 2033504d <CSR_UINTSTATUS+0x2033439c>
42010a04:	086c                	addi	a1,sp,28
42010a06:	10a8                	addi	a0,sp,104
42010a08:	d4be                	sw	a5,104(sp)
42010a0a:	7a0150ef          	jal	420261aa <__wrap_esp_audio_simple_dec_open>
42010a0e:	842a                	mv	s0,a0
42010a10:	78050a63          	beqz	a0,420111a4 <decoder_task+0x954>
42010a14:	fe378097          	auipc	ra,0xfe378
42010a18:	9a6080e7          	jalr	-1626(ra) # 403883ba <esp_log_timestamp>
42010a1c:	3c1267b7          	lui	a5,0x3c126
42010a20:	4985                	li	s3,1
42010a22:	86aa                	mv	a3,a0
42010a24:	80078793          	addi	a5,a5,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
42010a28:	093b17e3          	bne	s6,s3,420112b6 <decoder_task+0xa66>
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
42010a54:	28f400e3          	beq	s0,a5,420114d4 <decoder_task+0xc84>
42010a58:	3fc957b7          	lui	a5,0x3fc95
42010a5c:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42010a60:	4601                	li	a2,0
42010a62:	85a6                	mv	a1,s1
42010a64:	76a040ef          	jal	420151ce <native_state_set_audio>
42010a68:	4572                	lw	a0,28(sp)
42010a6a:	c501                	beqz	a0,42010a72 <decoder_task+0x222>
42010a6c:	7ae260ef          	jal	4203721a <esp_audio_simple_dec_close>
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
42010a8e:	2ee660ef          	jal	42076d7c <vRingbufferReturnItem>
42010a92:	4401                	li	s0,0
42010a94:	b535                	j	420108c0 <decoder_task+0x70>
42010a96:	39f010ef          	jal	42012634 <decoder_register_codecs>
42010a9a:	842a                	mv	s0,a0
42010a9c:	26051e63          	bnez	a0,42010d18 <decoder_task+0x4c8>
42010aa0:	000ca783          	lw	a5,0(s9)
42010aa4:	ec9798e3          	bne	a5,s1,42010974 <decoder_task+0x124>
42010aa8:	004ca783          	lw	a5,4(s9)
42010aac:	ed6794e3          	bne	a5,s6,42010974 <decoder_task+0x124>
42010ab0:	478d                	li	a5,3
42010ab2:	78fb0963          	beq	s6,a5,42011244 <decoder_task+0x9f4>
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
42010ae6:	38098e63          	beqz	s3,42010e82 <decoder_task+0x632>
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
42010b12:	3bb010ef          	jal	420126cc <native_aac_decoder_process>
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
42010b44:	56078163          	beqz	a5,420110a6 <decoder_task+0x856>
42010b48:	af0a8793          	addi	a5,s5,-1296
42010b4c:	0330000f          	fence	rw,rw
42010b50:	439c                	lw	a5,0(a5)
42010b52:	0230000f          	fence	r,rw
42010b56:	16979763          	bne	a5,s1,42010cc4 <decoder_task+0x474>
42010b5a:	57e1                	li	a5,-8
42010b5c:	50fd0f63          	beq	s10,a5,4201107a <decoder_task+0x82a>
42010b60:	580d1a63          	bnez	s10,420110f4 <decoder_task+0x8a4>
42010b64:	5786                	lw	a5,96(sp)
42010b66:	4766                	lw	a4,88(sp)
42010b68:	6ef76163          	bltu	a4,a5,4201124a <decoder_task+0x9fa>
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
42010b8e:	667010ef          	jal	420129f4 <native_aac_decoder_get_info>
42010b92:	50051e63          	bnez	a0,420110ae <decoder_task+0x85e>
42010b96:	4782                	lw	a5,0(sp)
42010b98:	01b10613          	addi	a2,sp,27
42010b9c:	00cc                	addi	a1,sp,68
42010b9e:	854e                	mv	a0,s3
42010ba0:	00f10da3          	sb	a5,27(sp)
42010ba4:	65f010ef          	jal	42012a02 <native_aac_decoder_label>
42010ba8:	01b14683          	lbu	a3,27(sp)
42010bac:	842a                	mv	s0,a0
42010bae:	4501                	li	a0,0
42010bb0:	5c068663          	beqz	a3,4201117c <decoder_task+0x92c>
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
42010bfe:	6a050a63          	beqz	a0,420112b2 <decoder_task+0xa62>
42010c02:	3fc957b7          	lui	a5,0x3fc95
42010c06:	06a10823          	sb	a0,112(sp)
42010c0a:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42010c0e:	06c108a3          	sb	a2,113(sp)
42010c12:	85a6                	mv	a1,s1
42010c14:	10b0                	addi	a2,sp,104
42010c16:	daba                	sw	a4,116(sp)
42010c18:	07010c23          	sb	a6,120(sp)
42010c1c:	06d10d23          	sb	a3,122(sp)
42010c20:	68e040ef          	jal	420152ae <native_state_set_stream_info>
42010c24:	4785                	li	a5,1
42010c26:	45b6                	lw	a1,76(sp)
42010c28:	8526                	mv	a0,s1
42010c2a:	00f10d23          	sb	a5,26(sp)
42010c2e:	fe6ff0ef          	jal	42010414 <state_set_decoder_bitrate>
42010c32:	01a14783          	lbu	a5,26(sp)
42010c36:	c3a5                	beqz	a5,42010c96 <decoder_task+0x446>
42010c38:	4a0d8763          	beqz	s11,420110e6 <decoder_task+0x896>
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
42010c92:	72050a63          	beqz	a0,420113c6 <decoder_task+0xb76>
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
42010cb2:	3a079e63          	bnez	a5,4201106e <decoder_task+0x81e>
42010cb6:	74068e63          	beqz	a3,42011412 <decoder_task+0xbc2>
42010cba:	4701                	li	a4,0
42010cbc:	47e6                	lw	a5,88(sp)
42010cbe:	8f5d                	or	a4,a4,a5
42010cc0:	e20715e3          	bnez	a4,42010aea <decoder_task+0x29a>
42010cc4:	00acc783          	lbu	a5,10(s9)
42010cc8:	48079963          	bnez	a5,4201115a <decoder_task+0x90a>
42010ccc:	489c0763          	beq	s8,s1,4201115a <decoder_task+0x90a>
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
42010cfa:	520260ef          	jal	4203721a <esp_audio_simple_dec_close>
42010cfe:	ce02                	sw	zero,28(sp)
42010d00:	00098563          	beqz	s3,42010d0a <decoder_task+0x4ba>
42010d04:	854e                	mv	a0,s3
42010d06:	191010ef          	jal	42012696 <native_aac_decoder_destroy>
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
42010d56:	478040ef          	jal	420151ce <native_state_set_audio>
42010d5a:	000cac03          	lw	s8,0(s9)
42010d5e:	8566                	mv	a0,s9
42010d60:	85e2                	mv	a1,s8
42010d62:	a27ff0ef          	jal	42010788 <return_decoded_packet>
42010d66:	bea9                	j	420108c0 <decoder_task+0x70>
42010d68:	3fc957b7          	lui	a5,0x3fc95
42010d6c:	afc7a503          	lw	a0,-1284(a5) # 3fc94afc <s_encoded>
42010d70:	85e6                	mv	a1,s9
42010d72:	00a660ef          	jal	42076d7c <vRingbufferReturnItem>
42010d76:	b6a9                	j	420108c0 <decoder_task+0x70>
42010d78:	854a                	mv	a0,s2
42010d7a:	f8af70ef          	jal	42008504 <cfree>
42010d7e:	4a01                	li	s4,0
42010d80:	4901                	li	s2,0
42010d82:	b649                	j	42010904 <decoder_task+0xb4>
42010d84:	854a                	mv	a0,s2
42010d86:	f7ef70ef          	jal	42008504 <cfree>
42010d8a:	11c240ef          	jal	42034ea6 <custom_flac_decoder_create>
42010d8e:	8baa                	mv	s7,a0
42010d90:	5a050863          	beqz	a0,42011340 <decoder_task+0xaf0>
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
42010dcc:	4fe70713          	addi	a4,a4,1278 # 420114fe <custom_flac_output>
42010dd0:	00bc8593          	addi	a1,s9,11
42010dd4:	06810813          	addi	a6,sp,104
42010dd8:	855e                	mv	a0,s7
42010dda:	152240ef          	jal	42034f2c <custom_flac_decoder_feed>
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
42010e10:	4a0d8963          	beqz	s11,420112c2 <decoder_task+0xa72>
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
42010e3a:	62978e63          	beq	a5,s1,42011476 <decoder_task+0xc26>
42010e3e:	8566                	mv	a0,s9
42010e40:	85e2                	mv	a1,s8
42010e42:	947ff0ef          	jal	42010788 <return_decoded_packet>
42010e46:	4b0d                	li	s6,3
42010e48:	4401                	li	s0,0
42010e4a:	bc9d                	j	420108c0 <decoder_task+0x70>
42010e4c:	6589                	lui	a1,0x2
42010e4e:	36ba0263          	beq	s4,a1,420111b2 <decoder_task+0x962>
42010e52:	854a                	mv	a0,s2
42010e54:	eacf70ef          	jal	42008500 <realloc>
42010e58:	842a                	mv	s0,a0
42010e5a:	68050863          	beqz	a0,420114ea <decoder_task+0xc9a>
42010e5e:	204347b7          	lui	a5,0x20434
42010e62:	14178793          	addi	a5,a5,321 # 20434141 <CSR_UINTSTATUS+0x20433490>
42010e66:	d682                	sw	zero,108(sp)
42010e68:	d882                	sw	zero,112(sp)
42010e6a:	da82                	sw	zero,116(sp)
42010e6c:	d4be                	sw	a5,104(sp)
42010e6e:	7fc010ef          	jal	4201266a <native_aac_decoder_create>
42010e72:	89aa                	mv	s3,a0
42010e74:	46050763          	beqz	a0,420112e2 <decoder_task+0xa92>
42010e78:	8922                	mv	s2,s0
42010e7a:	6a09                	lui	s4,0x2
42010e7c:	4b81                	li	s7,0
42010e7e:	4d81                	li	s11,0
42010e80:	b93d                	j	42010abe <decoder_task+0x26e>
42010e82:	5d61                	li	s10,-8
42010e84:	c662                	sw	s8,12(sp)
42010e86:	e789                	bnez	a5,42010e90 <decoder_task+0x640>
42010e88:	05c14783          	lbu	a5,92(sp)
42010e8c:	1c078f63          	beqz	a5,4201106a <decoder_task+0x81a>
42010e90:	4781                	li	a5,0
42010e92:	4801                	li	a6,0
42010e94:	de3e                	sw	a5,60(sp)
42010e96:	c0c2                	sw	a6,64(sp)
42010e98:	da4a                	sw	s2,52(sp)
42010e9a:	dc52                	sw	s4,56(sp)
42010e9c:	d082                	sw	zero,96(sp)
42010e9e:	fe370097          	auipc	ra,0xfe370
42010ea2:	49c080e7          	jalr	1180(ra) # 4038133a <esp_timer_get_time>
42010ea6:	842a                	mv	s0,a0
42010ea8:	4572                	lw	a0,28(sp)
42010eaa:	1850                	addi	a2,sp,52
42010eac:	08cc                	addi	a1,sp,84
42010eae:	488150ef          	jal	42026336 <__wrap_esp_audio_simple_dec_process>
42010eb2:	8c2a                	mv	s8,a0
42010eb4:	fe370097          	auipc	ra,0xfe370
42010eb8:	486080e7          	jalr	1158(ra) # 4038133a <esp_timer_get_time>
42010ebc:	47ca                	lw	a5,144(sp)
42010ebe:	46da                	lw	a3,148(sp)
42010ec0:	8d01                	sub	a0,a0,s0
42010ec2:	00a78733          	add	a4,a5,a0
42010ec6:	00f737b3          	sltu	a5,a4,a5
42010eca:	97b6                	add	a5,a5,a3
42010ecc:	cb3e                	sw	a5,148(sp)
42010ece:	578a                	lw	a5,160(sp)
42010ed0:	c93a                	sw	a4,144(sp)
42010ed2:	571a                	lw	a4,164(sp)
42010ed4:	0785                	addi	a5,a5,1
42010ed6:	d13e                	sw	a5,160(sp)
42010ed8:	00a77363          	bgeu	a4,a0,42010ede <decoder_task+0x68e>
42010edc:	d32a                	sw	a0,164(sp)
42010ede:	8bfd                	andi	a5,a5,31
42010ee0:	1e078c63          	beqz	a5,420110d8 <decoder_task+0x888>
42010ee4:	af0a8793          	addi	a5,s5,-1296
42010ee8:	0330000f          	fence	rw,rw
42010eec:	439c                	lw	a5,0(a5)
42010eee:	0230000f          	fence	r,rw
42010ef2:	16979c63          	bne	a5,s1,4201106a <decoder_task+0x81a>
42010ef6:	1dac0563          	beq	s8,s10,420110c0 <decoder_task+0x870>
42010efa:	4e0c1b63          	bnez	s8,420113f0 <decoder_task+0xba0>
42010efe:	5786                	lw	a5,96(sp)
42010f00:	4766                	lw	a4,88(sp)
42010f02:	34f76463          	bltu	a4,a5,4201124a <decoder_task+0x9fa>
42010f06:	8f1d                	sub	a4,a4,a5
42010f08:	56aa                	lw	a3,168(sp)
42010f0a:	ccba                	sw	a4,88(sp)
42010f0c:	4756                	lw	a4,84(sp)
42010f0e:	96be                	add	a3,a3,a5
42010f10:	d536                	sw	a3,168(sp)
42010f12:	97ba                	add	a5,a5,a4
42010f14:	4706                	lw	a4,64(sp)
42010f16:	cabe                	sw	a5,84(sp)
42010f18:	12070363          	beqz	a4,4201103e <decoder_task+0x7ee>
42010f1c:	4572                	lw	a0,28(sp)
42010f1e:	00cc                	addi	a1,sp,68
42010f20:	c282                	sw	zero,68(sp)
42010f22:	c482                	sw	zero,72(sp)
42010f24:	c682                	sw	zero,76(sp)
42010f26:	c882                	sw	zero,80(sp)
42010f28:	27a260ef          	jal	420371a2 <esp_audio_simple_dec_get_info>
42010f2c:	1a051a63          	bnez	a0,420110e0 <decoder_task+0x890>
42010f30:	4782                	lw	a5,0(sp)
42010f32:	00f10da3          	sb	a5,27(sp)
42010f36:	4789                	li	a5,2
42010f38:	44fb0e63          	beq	s6,a5,42011394 <decoder_task+0xb44>
42010f3c:	4791                	li	a5,4
42010f3e:	44fb0663          	beq	s6,a5,4201138a <decoder_task+0xb3a>
42010f42:	3c126737          	lui	a4,0x3c126
42010f46:	4785                	li	a5,1
42010f48:	80070593          	addi	a1,a4,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
42010f4c:	38fb1663          	bne	s6,a5,420112d8 <decoder_task+0xa88>
42010f50:	af0a8793          	addi	a5,s5,-1296
42010f54:	0330000f          	fence	rw,rw
42010f58:	439c                	lw	a5,0(a5)
42010f5a:	0230000f          	fence	r,rw
42010f5e:	06979463          	bne	a5,s1,42010fc6 <decoder_task+0x776>
42010f62:	4796                	lw	a5,68(sp)
42010f64:	c3b5                	beqz	a5,42010fc8 <decoder_task+0x778>
42010f66:	04914683          	lbu	a3,73(sp)
42010f6a:	ceb1                	beqz	a3,42010fc6 <decoder_task+0x776>
42010f6c:	04815703          	lhu	a4,72(sp)
42010f70:	04814503          	lbu	a0,72(sp)
42010f74:	00875613          	srli	a2,a4,0x8
42010f78:	0722                	slli	a4,a4,0x8
42010f7a:	963a                	add	a2,a2,a4
42010f7c:	c529                	beqz	a0,42010fc6 <decoder_task+0x776>
42010f7e:	06012b23          	sw	zero,118(sp)
42010f82:	06012923          	sw	zero,114(sp)
42010f86:	d23e                	sw	a5,36(sp)
42010f88:	06c11823          	sh	a2,112(sp)
42010f8c:	d6be                	sw	a5,108(sp)
42010f8e:	4626                	lw	a2,72(sp)
42010f90:	dabe                	sw	a5,116(sp)
42010f92:	3fc957b7          	lui	a5,0x3fc95
42010f96:	4746                	lw	a4,80(sp)
42010f98:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42010f9c:	06d10c23          	sb	a3,120(sp)
42010fa0:	4782                	lw	a5,0(sp)
42010fa2:	46b6                	lw	a3,76(sp)
42010fa4:	06011d23          	sh	zero,122(sp)
42010fa8:	d4ae                	sw	a1,104(sp)
42010faa:	d432                	sw	a2,40(sp)
42010fac:	4405                	li	s0,1
42010fae:	10b0                	addi	a2,sp,104
42010fb0:	85a6                	mv	a1,s1
42010fb2:	06f10d23          	sb	a5,122(sp)
42010fb6:	d636                	sw	a3,44(sp)
42010fb8:	d83a                	sw	a4,48(sp)
42010fba:	00810d23          	sb	s0,26(sp)
42010fbe:	2f0040ef          	jal	420152ae <native_state_set_stream_info>
42010fc2:	87a2                	mv	a5,s0
42010fc4:	a011                	j	42010fc8 <decoder_task+0x778>
42010fc6:	4781                	li	a5,0
42010fc8:	45b6                	lw	a1,76(sp)
42010fca:	8526                	mv	a0,s1
42010fcc:	00f10d23          	sb	a5,26(sp)
42010fd0:	c44ff0ef          	jal	42010414 <state_set_decoder_bitrate>
42010fd4:	01a14783          	lbu	a5,26(sp)
42010fd8:	c3bd                	beqz	a5,4201103e <decoder_task+0x7ee>
42010fda:	1c0d8e63          	beqz	s11,420111b6 <decoder_task+0x966>
42010fde:	02814503          	lbu	a0,40(sp)
42010fe2:	02914783          	lbu	a5,41(sp)
42010fe6:	4406                	lw	s0,64(sp)
42010fe8:	051d                	addi	a0,a0,7
42010fea:	810d                	srli	a0,a0,0x3
42010fec:	02f50533          	mul	a0,a0,a5
42010ff0:	cd15                	beqz	a0,4201102c <decoder_task+0x7dc>
42010ff2:	5612                	lw	a2,36(sp)
42010ff4:	ce05                	beqz	a2,4201102c <decoder_task+0x7dc>
42010ff6:	02a45533          	divu	a0,s0,a0
42010ffa:	000f47b7          	lui	a5,0xf4
42010ffe:	24078793          	addi	a5,a5,576 # f4240 <CSR_UINTSTATUS+0xf358f>
42011002:	4681                	li	a3,0
42011004:	02f535b3          	mulhu	a1,a0,a5
42011008:	02f50533          	mul	a0,a0,a5
4201100c:	fdff0097          	auipc	ra,0xfdff0
42011010:	8a0080e7          	jalr	-1888(ra) # 400008ac <__udivdi3>
42011014:	47ea                	lw	a5,152(sp)
42011016:	46fa                	lw	a3,156(sp)
42011018:	573a                	lw	a4,172(sp)
4201101a:	953e                	add	a0,a0,a5
4201101c:	96ae                	add	a3,a3,a1
4201101e:	00f537b3          	sltu	a5,a0,a5
42011022:	97b6                	add	a5,a5,a3
42011024:	9722                	add	a4,a4,s0
42011026:	cf3e                	sw	a5,156(sp)
42011028:	cd2a                	sw	a0,152(sp)
4201102a:	d73a                	sw	a4,172(sp)
4201102c:	86a2                	mv	a3,s0
4201102e:	864a                	mv	a2,s2
42011030:	104c                	addi	a1,sp,36
42011032:	8526                	mv	a0,s1
42011034:	aa4ff0ef          	jal	420102d8 <send_pcm>
42011038:	8daa                	mv	s11,a0
4201103a:	38050563          	beqz	a0,420113c4 <decoder_task+0xb74>
4201103e:	fe370097          	auipc	ra,0xfe370
42011042:	2fc080e7          	jalr	764(ra) # 4038133a <esp_timer_get_time>
42011046:	862e                	mv	a2,a1
42011048:	85aa                	mv	a1,a0
4201104a:	0108                	addi	a0,sp,128
4201104c:	e0ffe0ef          	jal	4200fe5a <decode_stats_report>
42011050:	4706                	lw	a4,64(sp)
42011052:	5786                	lw	a5,96(sp)
42011054:	05c14683          	lbu	a3,92(sp)
42011058:	8fd9                	or	a5,a5,a4
4201105a:	efa9                	bnez	a5,420110b4 <decoder_task+0x864>
4201105c:	3a068b63          	beqz	a3,42011412 <decoder_task+0xbc2>
42011060:	4701                	li	a4,0
42011062:	47e6                	lw	a5,88(sp)
42011064:	8f5d                	or	a4,a4,a5
42011066:	e20710e3          	bnez	a4,42010e86 <decoder_task+0x636>
4201106a:	4c32                	lw	s8,12(sp)
4201106c:	b9a1                	j	42010cc4 <decoder_task+0x474>
4201106e:	c40697e3          	bnez	a3,42010cbc <decoder_task+0x46c>
42011072:	47e6                	lw	a5,88(sp)
42011074:	a80790e3          	bnez	a5,42010af4 <decoder_task+0x2a4>
42011078:	b1b1                	j	42010cc4 <decoder_task+0x474>
4201107a:	5706                	lw	a4,96(sp)
4201107c:	47d6                	lw	a5,84(sp)
4201107e:	56aa                	lw	a3,168(sp)
42011080:	5472                	lw	s0,60(sp)
42011082:	97ba                	add	a5,a5,a4
42011084:	cabe                	sw	a5,84(sp)
42011086:	47e6                	lw	a5,88(sp)
42011088:	96ba                	add	a3,a3,a4
4201108a:	d536                	sw	a3,168(sp)
4201108c:	8f99                	sub	a5,a5,a4
4201108e:	ccbe                	sw	a5,88(sp)
42011090:	308a7763          	bgeu	s4,s0,4201139e <decoder_task+0xb4e>
42011094:	85a2                	mv	a1,s0
42011096:	854a                	mv	a0,s2
42011098:	c68f70ef          	jal	42008500 <realloc>
4201109c:	30050163          	beqz	a0,4201139e <decoder_task+0xb4e>
420110a0:	8a22                	mv	s4,s0
420110a2:	892a                	mv	s2,a0
420110a4:	bc81                	j	42010af4 <decoder_task+0x2a4>
420110a6:	4505                	li	a0,1
420110a8:	2b3ff0ef          	jal	42110b5a <vTaskDelay>
420110ac:	bc71                	j	42010b48 <decoder_task+0x2f8>
420110ae:	00010d23          	sb	zero,26(sp)
420110b2:	b6d5                	j	42010c96 <decoder_task+0x446>
420110b4:	f6dd                	bnez	a3,42011062 <decoder_task+0x812>
420110b6:	47e6                	lw	a5,88(sp)
420110b8:	dc079ce3          	bnez	a5,42010e90 <decoder_task+0x640>
420110bc:	4c32                	lw	s8,12(sp)
420110be:	b119                	j	42010cc4 <decoder_task+0x474>
420110c0:	5472                	lw	s0,60(sp)
420110c2:	2c8a7e63          	bgeu	s4,s0,4201139e <decoder_task+0xb4e>
420110c6:	85a2                	mv	a1,s0
420110c8:	854a                	mv	a0,s2
420110ca:	c36f70ef          	jal	42008500 <realloc>
420110ce:	2c050863          	beqz	a0,4201139e <decoder_task+0xb4e>
420110d2:	892a                	mv	s2,a0
420110d4:	8a22                	mv	s4,s0
420110d6:	bb6d                	j	42010e90 <decoder_task+0x640>
420110d8:	4505                	li	a0,1
420110da:	281ff0ef          	jal	42110b5a <vTaskDelay>
420110de:	b519                	j	42010ee4 <decoder_task+0x694>
420110e0:	00010d23          	sb	zero,26(sp)
420110e4:	bfa9                	j	4201103e <decoder_task+0x7ee>
420110e6:	3c1267b7          	lui	a5,0x3c126
420110ea:	b3078513          	addi	a0,a5,-1232 # 3c125b30 <_esp_trace_encoder_array_end+0x5a10>
420110ee:	986ff0ef          	jal	42010274 <log_runtime_memory>
420110f2:	b6a9                	j	42010c3c <decoder_task+0x3ec>
420110f4:	846a                	mv	s0,s10
420110f6:	4a09                	li	s4,2
420110f8:	fe377097          	auipc	ra,0xfe377
420110fc:	2c2080e7          	jalr	706(ra) # 403883ba <esp_log_timestamp>
42011100:	2f4b0a63          	beq	s6,s4,420113f4 <decoder_task+0xba4>
42011104:	4791                	li	a5,4
42011106:	2efb0c63          	beq	s6,a5,420113fe <decoder_task+0xbae>
4201110a:	3c1267b7          	lui	a5,0x3c126
4201110e:	4705                	li	a4,1
42011110:	80078793          	addi	a5,a5,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
42011114:	00eb0663          	beq	s6,a4,42011120 <decoder_task+0x8d0>
42011118:	3c1267b7          	lui	a5,0x3c126
4201111c:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
42011120:	3c126737          	lui	a4,0x3c126
42011124:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
42011128:	3c126637          	lui	a2,0x3c126
4201112c:	86aa                	mv	a3,a0
4201112e:	85ba                	mv	a1,a4
42011130:	8822                	mv	a6,s0
42011132:	b6460613          	addi	a2,a2,-1180 # 3c125b64 <_esp_trace_encoder_array_end+0x5a44>
42011136:	4509                	li	a0,2
42011138:	fe377097          	auipc	ra,0xfe377
4201113c:	17a080e7          	jalr	378(ra) # 403882b2 <esp_log>
42011140:	3fc957b7          	lui	a5,0x3fc95
42011144:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42011148:	3c1267b7          	lui	a5,0x3c126
4201114c:	a0c78693          	addi	a3,a5,-1524 # 3c125a0c <_esp_trace_encoder_array_end+0x58ec>
42011150:	85a6                	mv	a1,s1
42011152:	4601                	li	a2,0
42011154:	07a040ef          	jal	420151ce <native_state_set_audio>
42011158:	8c26                	mv	s8,s1
4201115a:	4572                	lw	a0,28(sp)
4201115c:	c119                	beqz	a0,42011162 <decoder_task+0x912>
4201115e:	0bc260ef          	jal	4203721a <esp_audio_simple_dec_close>
42011162:	ce02                	sw	zero,28(sp)
42011164:	00098563          	beqz	s3,4201116e <decoder_task+0x91e>
42011168:	854e                	mv	a0,s3
4201116a:	52c010ef          	jal	42012696 <native_aac_decoder_destroy>
4201116e:	854a                	mv	a0,s2
42011170:	b94f70ef          	jal	42008504 <cfree>
42011174:	4981                	li	s3,0
42011176:	4a01                	li	s4,0
42011178:	4901                	li	s2,0
4201117a:	be99                	j	42010cd0 <decoder_task+0x480>
4201117c:	854e                	mv	a0,s3
4201117e:	0dd010ef          	jal	42012a5a <native_aac_decoder_source_channels>
42011182:	01b14683          	lbu	a3,27(sp)
42011186:	0ff57513          	zext.b	a0,a0
4201118a:	b42d                	j	42010bb4 <decoder_task+0x364>
4201118c:	204747b7          	lui	a5,0x20474
42011190:	74f78793          	addi	a5,a5,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
42011194:	086c                	addi	a1,sp,28
42011196:	10a8                	addi	a0,sp,104
42011198:	d4be                	sw	a5,104(sp)
4201119a:	010150ef          	jal	420261aa <__wrap_esp_audio_simple_dec_open>
4201119e:	842a                	mv	s0,a0
420111a0:	18051063          	bnez	a0,42011320 <decoder_task+0xad0>
420111a4:	4bf2                	lw	s7,28(sp)
420111a6:	4d81                	li	s11,0
420111a8:	8c0b8de3          	beqz	s7,42010a82 <decoder_task+0x232>
420111ac:	4981                	li	s3,0
420111ae:	4b81                	li	s7,0
420111b0:	b239                	j	42010abe <decoder_task+0x26e>
420111b2:	844a                	mv	s0,s2
420111b4:	b16d                	j	42010e5e <decoder_task+0x60e>
420111b6:	3c1267b7          	lui	a5,0x3c126
420111ba:	b3078513          	addi	a0,a5,-1232 # 3c125b30 <_esp_trace_encoder_array_end+0x5a10>
420111be:	8b6ff0ef          	jal	42010274 <log_runtime_memory>
420111c2:	bd31                	j	42010fde <decoder_task+0x78e>
420111c4:	d682                	sw	zero,108(sp)
420111c6:	d882                	sw	zero,112(sp)
420111c8:	da82                	sw	zero,116(sp)
420111ca:	82dff06f          	j	420109f6 <decoder_task+0x1a6>
420111ce:	fe377097          	auipc	ra,0xfe377
420111d2:	1ec080e7          	jalr	492(ra) # 403883ba <esp_log_timestamp>
420111d6:	4791                	li	a5,4
420111d8:	4405                	li	s0,1
420111da:	86aa                	mv	a3,a0
420111dc:	1cfb0f63          	beq	s6,a5,420113ba <decoder_task+0xb6a>
420111e0:	3c1267b7          	lui	a5,0x3c126
420111e4:	80078793          	addi	a5,a5,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
420111e8:	008b0663          	beq	s6,s0,420111f4 <decoder_task+0x9a4>
420111ec:	3c1267b7          	lui	a5,0x3c126
420111f0:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
420111f4:	3c126737          	lui	a4,0x3c126
420111f8:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
420111fc:	3c126637          	lui	a2,0x3c126
42011200:	85ba                	mv	a1,a4
42011202:	a9460613          	addi	a2,a2,-1388 # 3c125a94 <_esp_trace_encoder_array_end+0x5974>
42011206:	4505                	li	a0,1
42011208:	fe377097          	auipc	ra,0xfe377
4201120c:	0aa080e7          	jalr	170(ra) # 403882b2 <esp_log>
42011210:	3fc957b7          	lui	a5,0x3fc95
42011214:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42011218:	3c1267b7          	lui	a5,0x3c126
4201121c:	9f078693          	addi	a3,a5,-1552 # 3c1259f0 <_esp_trace_encoder_array_end+0x58d0>
42011220:	85a6                	mv	a1,s1
42011222:	4601                	li	a2,0
42011224:	7ab030ef          	jal	420151ce <native_state_set_audio>
42011228:	3fc957b7          	lui	a5,0x3fc95
4201122c:	afc7a503          	lw	a0,-1284(a5) # 3fc94afc <s_encoded>
42011230:	85e6                	mv	a1,s9
42011232:	8c26                	mv	s8,s1
42011234:	349650ef          	jal	42076d7c <vRingbufferReturnItem>
42011238:	4981                	li	s3,0
4201123a:	4d81                	li	s11,0
4201123c:	4b81                	li	s7,0
4201123e:	4401                	li	s0,0
42011240:	e80ff06f          	j	420108c0 <decoder_task+0x70>
42011244:	be0b8de3          	beqz	s7,42010e3e <decoder_task+0x5ee>
42011248:	be91                	j	42010d9c <decoder_task+0x54c>
4201124a:	fe377097          	auipc	ra,0xfe377
4201124e:	170080e7          	jalr	368(ra) # 403883ba <esp_log_timestamp>
42011252:	4789                	li	a5,2
42011254:	4405                	li	s0,1
42011256:	0efb0063          	beq	s6,a5,42011336 <decoder_task+0xae6>
4201125a:	4791                	li	a5,4
4201125c:	1afb0663          	beq	s6,a5,42011408 <decoder_task+0xbb8>
42011260:	3c1267b7          	lui	a5,0x3c126
42011264:	80078793          	addi	a5,a5,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
42011268:	008b0663          	beq	s6,s0,42011274 <decoder_task+0xa24>
4201126c:	3c1267b7          	lui	a5,0x3c126
42011270:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
42011274:	48e6                	lw	a7,88(sp)
42011276:	5806                	lw	a6,96(sp)
42011278:	3c126737          	lui	a4,0x3c126
4201127c:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
42011280:	3c126637          	lui	a2,0x3c126
42011284:	86aa                	mv	a3,a0
42011286:	85ba                	mv	a1,a4
42011288:	b8860613          	addi	a2,a2,-1144 # 3c125b88 <_esp_trace_encoder_array_end+0x5a68>
4201128c:	4505                	li	a0,1
4201128e:	fe377097          	auipc	ra,0xfe377
42011292:	024080e7          	jalr	36(ra) # 403882b2 <esp_log>
42011296:	3fc957b7          	lui	a5,0x3fc95
4201129a:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
4201129e:	3c1267b7          	lui	a5,0x3c126
420112a2:	bc478693          	addi	a3,a5,-1084 # 3c125bc4 <_esp_trace_encoder_array_end+0x5aa4>
420112a6:	85a6                	mv	a1,s1
420112a8:	4601                	li	a2,0
420112aa:	725030ef          	jal	420151ce <native_state_set_audio>
420112ae:	8c26                	mv	s8,s1
420112b0:	b56d                	j	4201115a <decoder_task+0x90a>
420112b2:	8542                	mv	a0,a6
420112b4:	b2b9                	j	42010c02 <decoder_task+0x3b2>
420112b6:	3c1267b7          	lui	a5,0x3c126
420112ba:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
420112be:	f6eff06f          	j	42010a2c <decoder_task+0x1dc>
420112c2:	01a14d83          	lbu	s11,26(sp)
420112c6:	b40d88e3          	beqz	s11,42010e16 <decoder_task+0x5c6>
420112ca:	3c1267b7          	lui	a5,0x3c126
420112ce:	aec78513          	addi	a0,a5,-1300 # 3c125aec <_esp_trace_encoder_array_end+0x59cc>
420112d2:	fa3fe0ef          	jal	42010274 <log_runtime_memory>
420112d6:	be3d                	j	42010e14 <decoder_task+0x5c4>
420112d8:	3c1267b7          	lui	a5,0x3c126
420112dc:	80478593          	addi	a1,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
420112e0:	b985                	j	42010f50 <decoder_task+0x700>
420112e2:	fe377097          	auipc	ra,0xfe377
420112e6:	0d8080e7          	jalr	216(ra) # 403883ba <esp_log_timestamp>
420112ea:	3c1267b7          	lui	a5,0x3c126
420112ee:	80c78713          	addi	a4,a5,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
420112f2:	3c126637          	lui	a2,0x3c126
420112f6:	3c1257b7          	lui	a5,0x3c125
420112fa:	86aa                	mv	a3,a0
420112fc:	7f078793          	addi	a5,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
42011300:	85ba                	mv	a1,a4
42011302:	ac460613          	addi	a2,a2,-1340 # 3c125ac4 <_esp_trace_encoder_array_end+0x59a4>
42011306:	5879                	li	a6,-2
42011308:	4505                	li	a0,1
4201130a:	fe377097          	auipc	ra,0xfe377
4201130e:	fa8080e7          	jalr	-88(ra) # 403882b2 <esp_log>
42011312:	3c1267b7          	lui	a5,0x3c126
42011316:	8922                	mv	s2,s0
42011318:	9f078693          	addi	a3,a5,-1552 # 3c1259f0 <_esp_trace_encoder_array_end+0x58d0>
4201131c:	f3cff06f          	j	42010a58 <decoder_task+0x208>
42011320:	fe377097          	auipc	ra,0xfe377
42011324:	09a080e7          	jalr	154(ra) # 403883ba <esp_log_timestamp>
42011328:	3c1257b7          	lui	a5,0x3c125
4201132c:	86aa                	mv	a3,a0
4201132e:	7fc78793          	addi	a5,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
42011332:	efaff06f          	j	42010a2c <decoder_task+0x1dc>
42011336:	3c1257b7          	lui	a5,0x3c125
4201133a:	7f078793          	addi	a5,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
4201133e:	bf1d                	j	42011274 <decoder_task+0xa24>
42011340:	fe377097          	auipc	ra,0xfe377
42011344:	07a080e7          	jalr	122(ra) # 403883ba <esp_log_timestamp>
42011348:	3c1267b7          	lui	a5,0x3c126
4201134c:	80c78713          	addi	a4,a5,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
42011350:	3c1267b7          	lui	a5,0x3c126
42011354:	86aa                	mv	a3,a0
42011356:	85ba                	mv	a1,a4
42011358:	a6078613          	addi	a2,a5,-1440 # 3c125a60 <_esp_trace_encoder_array_end+0x5940>
4201135c:	4505                	li	a0,1
4201135e:	fe377097          	auipc	ra,0xfe377
42011362:	f54080e7          	jalr	-172(ra) # 403882b2 <esp_log>
42011366:	3fc957b7          	lui	a5,0x3fc95
4201136a:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
4201136e:	3c1267b7          	lui	a5,0x3c126
42011372:	9f078693          	addi	a3,a5,-1552 # 3c1259f0 <_esp_trace_encoder_array_end+0x58d0>
42011376:	85a6                	mv	a1,s1
42011378:	4601                	li	a2,0
4201137a:	655030ef          	jal	420151ce <native_state_set_audio>
4201137e:	8c26                	mv	s8,s1
42011380:	4981                	li	s3,0
42011382:	4901                	li	s2,0
42011384:	4a01                	li	s4,0
42011386:	4d81                	li	s11,0
42011388:	bc5d                	j	42010e3e <decoder_task+0x5ee>
4201138a:	3c1257b7          	lui	a5,0x3c125
4201138e:	7fc78593          	addi	a1,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
42011392:	be7d                	j	42010f50 <decoder_task+0x700>
42011394:	3c1257b7          	lui	a5,0x3c125
42011398:	7f078593          	addi	a1,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
4201139c:	be55                	j	42010f50 <decoder_task+0x700>
4201139e:	3fc957b7          	lui	a5,0x3fc95
420113a2:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
420113a6:	3c1267b7          	lui	a5,0x3c126
420113aa:	b4c78693          	addi	a3,a5,-1204 # 3c125b4c <_esp_trace_encoder_array_end+0x5a2c>
420113ae:	4601                	li	a2,0
420113b0:	85a6                	mv	a1,s1
420113b2:	61d030ef          	jal	420151ce <native_state_set_audio>
420113b6:	8c26                	mv	s8,s1
420113b8:	b34d                	j	4201115a <decoder_task+0x90a>
420113ba:	3c1257b7          	lui	a5,0x3c125
420113be:	7fc78793          	addi	a5,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
420113c2:	bd0d                	j	420111f4 <decoder_task+0x9a4>
420113c4:	4c32                	lw	s8,12(sp)
420113c6:	fe377097          	auipc	ra,0xfe377
420113ca:	ff4080e7          	jalr	-12(ra) # 403883ba <esp_log_timestamp>
420113ce:	3c1267b7          	lui	a5,0x3c126
420113d2:	80c78713          	addi	a4,a5,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
420113d6:	3c1267b7          	lui	a5,0x3c126
420113da:	86aa                	mv	a3,a0
420113dc:	85ba                	mv	a1,a4
420113de:	bd878613          	addi	a2,a5,-1064 # 3c125bd8 <_esp_trace_encoder_array_end+0x5ab8>
420113e2:	4509                	li	a0,2
420113e4:	fe377097          	auipc	ra,0xfe377
420113e8:	ece080e7          	jalr	-306(ra) # 403882b2 <esp_log>
420113ec:	4d85                	li	s11,1
420113ee:	b8d9                	j	42010cc4 <decoder_task+0x474>
420113f0:	8462                	mv	s0,s8
420113f2:	b311                	j	420110f6 <decoder_task+0x8a6>
420113f4:	3c1257b7          	lui	a5,0x3c125
420113f8:	7f078793          	addi	a5,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
420113fc:	b315                	j	42011120 <decoder_task+0x8d0>
420113fe:	3c1257b7          	lui	a5,0x3c125
42011402:	7fc78793          	addi	a5,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
42011406:	bb29                	j	42011120 <decoder_task+0x8d0>
42011408:	3c1257b7          	lui	a5,0x3c125
4201140c:	7fc78793          	addi	a5,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
42011410:	b595                	j	42011274 <decoder_task+0xa24>
42011412:	fe377097          	auipc	ra,0xfe377
42011416:	fa8080e7          	jalr	-88(ra) # 403883ba <esp_log_timestamp>
4201141a:	4789                	li	a5,2
4201141c:	4405                	li	s0,1
4201141e:	86aa                	mv	a3,a0
42011420:	0afb0563          	beq	s6,a5,420114ca <decoder_task+0xc7a>
42011424:	4791                	li	a5,4
42011426:	0afb0d63          	beq	s6,a5,420114e0 <decoder_task+0xc90>
4201142a:	3c1267b7          	lui	a5,0x3c126
4201142e:	80078793          	addi	a5,a5,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
42011432:	008b0663          	beq	s6,s0,4201143e <decoder_task+0xbee>
42011436:	3c1267b7          	lui	a5,0x3c126
4201143a:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
4201143e:	3c126737          	lui	a4,0x3c126
42011442:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
42011446:	3c126637          	lui	a2,0x3c126
4201144a:	85ba                	mv	a1,a4
4201144c:	bf860613          	addi	a2,a2,-1032 # 3c125bf8 <_esp_trace_encoder_array_end+0x5ad8>
42011450:	4505                	li	a0,1
42011452:	fe377097          	auipc	ra,0xfe377
42011456:	e60080e7          	jalr	-416(ra) # 403882b2 <esp_log>
4201145a:	3fc957b7          	lui	a5,0x3fc95
4201145e:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42011462:	3c1267b7          	lui	a5,0x3c126
42011466:	c2878693          	addi	a3,a5,-984 # 3c125c28 <_esp_trace_encoder_array_end+0x5b08>
4201146a:	85a6                	mv	a1,s1
4201146c:	4601                	li	a2,0
4201146e:	561030ef          	jal	420151ce <native_state_set_audio>
42011472:	8c26                	mv	s8,s1
42011474:	b1dd                	j	4201115a <decoder_task+0x90a>
42011476:	fe377097          	auipc	ra,0xfe377
4201147a:	f44080e7          	jalr	-188(ra) # 403883ba <esp_log_timestamp>
4201147e:	3c126737          	lui	a4,0x3c126
42011482:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
42011486:	3c126637          	lui	a2,0x3c126
4201148a:	86aa                	mv	a3,a0
4201148c:	87a2                	mv	a5,s0
4201148e:	85ba                	mv	a1,a4
42011490:	b0460613          	addi	a2,a2,-1276 # 3c125b04 <_esp_trace_encoder_array_end+0x59e4>
42011494:	4509                	li	a0,2
42011496:	fe377097          	auipc	ra,0xfe377
4201149a:	e1c080e7          	jalr	-484(ra) # 403882b2 <esp_log>
4201149e:	3c126737          	lui	a4,0x3c126
420114a2:	0419                	addi	s0,s0,6 # 3006 <CSR_UINTSTATUS+0x2355>
420114a4:	4785                	li	a5,1
420114a6:	a0c70693          	addi	a3,a4,-1524 # 3c125a0c <_esp_trace_encoder_array_end+0x58ec>
420114aa:	0087e663          	bltu	a5,s0,420114b6 <decoder_task+0xc66>
420114ae:	3c1267b7          	lui	a5,0x3c126
420114b2:	9f078693          	addi	a3,a5,-1552 # 3c1259f0 <_esp_trace_encoder_array_end+0x58d0>
420114b6:	3fc957b7          	lui	a5,0x3fc95
420114ba:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
420114be:	4601                	li	a2,0
420114c0:	85a6                	mv	a1,s1
420114c2:	50d030ef          	jal	420151ce <native_state_set_audio>
420114c6:	8c26                	mv	s8,s1
420114c8:	ba9d                	j	42010e3e <decoder_task+0x5ee>
420114ca:	3c1257b7          	lui	a5,0x3c125
420114ce:	7f078793          	addi	a5,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
420114d2:	b7b5                	j	4201143e <decoder_task+0xbee>
420114d4:	3c1267b7          	lui	a5,0x3c126
420114d8:	9f078693          	addi	a3,a5,-1552 # 3c1259f0 <_esp_trace_encoder_array_end+0x58d0>
420114dc:	d7cff06f          	j	42010a58 <decoder_task+0x208>
420114e0:	3c1257b7          	lui	a5,0x3c125
420114e4:	7fc78793          	addi	a5,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
420114e8:	bf99                	j	4201143e <decoder_task+0xbee>
420114ea:	fe377097          	auipc	ra,0xfe377
420114ee:	ed0080e7          	jalr	-304(ra) # 403883ba <esp_log_timestamp>
420114f2:	3c1257b7          	lui	a5,0x3c125
420114f6:	86aa                	mv	a3,a0
420114f8:	7f078793          	addi	a5,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
420114fc:	b9e5                	j	420111f4 <decoder_task+0x9a4>
