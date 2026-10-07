
idf\esp32c3-oled-native\build-output-staged\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42010776 <decoder_task>:
42010776:	7151                	addi	sp,sp,-240
42010778:	d5a2                	sw	s0,232(sp)
4201077a:	d3a6                	sw	s1,228(sp)
4201077c:	d1ca                	sw	s2,224(sp)
4201077e:	cfce                	sw	s3,220(sp)
42010780:	cdd2                	sw	s4,216(sp)
42010782:	cbd6                	sw	s5,212(sp)
42010784:	c9da                	sw	s6,208(sp)
42010786:	c7de                	sw	s7,204(sp)
42010788:	c5e2                	sw	s8,200(sp)
4201078a:	df6e                	sw	s11,188(sp)
4201078c:	d786                	sw	ra,236(sp)
4201078e:	c3e6                	sw	s9,196(sp)
42010790:	c1ea                	sw	s10,192(sp)
42010792:	5c9010ef          	jal	4201255a <decoder_register_codecs>
42010796:	3fc95737          	lui	a4,0x3fc95
4201079a:	000f47b7          	lui	a5,0xf4
4201079e:	2d870713          	addi	a4,a4,728 # 3fc952d8 <s_bitrate_updated_us>
420107a2:	24078793          	addi	a5,a5,576 # f4240 <CSR_UINTSTATUS+0xf358f>
420107a6:	ce02                	sw	zero,28(sp)
420107a8:	c102                	sw	zero,128(sp)
420107aa:	c302                	sw	zero,132(sp)
420107ac:	c502                	sw	zero,136(sp)
420107ae:	c702                	sw	zero,140(sp)
420107b0:	c902                	sw	zero,144(sp)
420107b2:	cb02                	sw	zero,148(sp)
420107b4:	cd02                	sw	zero,152(sp)
420107b6:	cf02                	sw	zero,156(sp)
420107b8:	d102                	sw	zero,160(sp)
420107ba:	d302                	sw	zero,164(sp)
420107bc:	d502                	sw	zero,168(sp)
420107be:	d702                	sw	zero,172(sp)
420107c0:	d202                	sw	zero,36(sp)
420107c2:	d402                	sw	zero,40(sp)
420107c4:	d602                	sw	zero,44(sp)
420107c6:	d802                	sw	zero,48(sp)
420107c8:	00010d23          	sb	zero,26(sp)
420107cc:	842a                	mv	s0,a0
420107ce:	c23a                	sw	a4,4(sp)
420107d0:	c43e                	sw	a5,8(sp)
420107d2:	4981                	li	s3,0
420107d4:	4a01                	li	s4,0
420107d6:	4901                	li	s2,0
420107d8:	4d81                	li	s11,0
420107da:	4b01                	li	s6,0
420107dc:	4c01                	li	s8,0
420107de:	4481                	li	s1,0
420107e0:	4b81                	li	s7,0
420107e2:	3fc95ab7          	lui	s5,0x3fc95
420107e6:	2f0a8793          	addi	a5,s5,752 # 3fc952f0 <s_generation>
420107ea:	0330000f          	fence	rw,rw
420107ee:	0007ac83          	lw	s9,0(a5)
420107f2:	0230000f          	fence	r,rw
420107f6:	409c8f63          	beq	s9,s1,42010c14 <decoder_task+0x49e>
420107fa:	3fc957b7          	lui	a5,0x3fc95
420107fe:	2ec78793          	addi	a5,a5,748 # 3fc952ec <s_decoder_target_codec>
42010802:	0330000f          	fence	rw,rw
42010806:	4384                	lw	s1,0(a5)
42010808:	0230000f          	fence	r,rw
4201080c:	4572                	lw	a0,28(sp)
4201080e:	c119                	beqz	a0,42010814 <decoder_task+0x9e>
42010810:	34e260ef          	jal	42036b5e <esp_audio_simple_dec_close>
42010814:	854e                	mv	a0,s3
42010816:	ce02                	sw	zero,28(sp)
42010818:	5a5010ef          	jal	420125bc <native_aac_decoder_destroy>
4201081c:	000b8563          	beqz	s7,42010826 <decoder_task+0xb0>
42010820:	855e                	mv	a0,s7
42010822:	028240ef          	jal	4203484a <custom_flac_decoder_destroy>
42010826:	46048c63          	beqz	s1,42010c9e <decoder_task+0x528>
4201082a:	d202                	sw	zero,36(sp)
4201082c:	d402                	sw	zero,40(sp)
4201082e:	d602                	sw	zero,44(sp)
42010830:	d802                	sw	zero,48(sp)
42010832:	00010d23          	sb	zero,26(sp)
42010836:	3fc957b7          	lui	a5,0x3fc95
4201083a:	2e878793          	addi	a5,a5,744 # 3fc952e8 <s_decoder_released_generation>
4201083e:	0310000f          	fence	rw,w
42010842:	0197a023          	sw	s9,0(a5)
42010846:	0330000f          	fence	rw,rw
4201084a:	4b81                	li	s7,0
4201084c:	84e6                	mv	s1,s9
4201084e:	4c01                	li	s8,0
42010850:	4b01                	li	s6,0
42010852:	4d81                	li	s11,0
42010854:	4981                	li	s3,0
42010856:	3fc957b7          	lui	a5,0x3fc95
4201085a:	2fc7a503          	lw	a0,764(a5) # 3fc952fc <s_encoded>
4201085e:	4651                	li	a2,20
42010860:	100c                	addi	a1,sp,32
42010862:	d002                	sw	zero,32(sp)
42010864:	5e1650ef          	jal	42076644 <xRingbufferReceive>
42010868:	8caa                	mv	s9,a0
4201086a:	dd35                	beqz	a0,420107e6 <decoder_task+0x70>
4201086c:	4118                	lw	a4,0(a0)
4201086e:	2f0a8793          	addi	a5,s5,752
42010872:	0330000f          	fence	rw,rw
42010876:	439c                	lw	a5,0(a5)
42010878:	0230000f          	fence	r,rw
4201087c:	40f71963          	bne	a4,a5,42010c8e <decoder_task+0x518>
42010880:	411c                	lw	a5,0(a0)
42010882:	41878663          	beq	a5,s8,42010c8e <decoder_task+0x518>
42010886:	4158                	lw	a4,4(a0)
42010888:	e709                	bnez	a4,42010892 <decoder_task+0x11c>
4201088a:	00a54703          	lbu	a4,10(a0)
4201088e:	3e071c63          	bnez	a4,42010c86 <decoder_task+0x510>
42010892:	12041563          	bnez	s0,420109bc <decoder_task+0x246>
42010896:	12978c63          	beq	a5,s1,420109ce <decoder_task+0x258>
4201089a:	4572                	lw	a0,28(sp)
4201089c:	c119                	beqz	a0,420108a2 <decoder_task+0x12c>
4201089e:	2c0260ef          	jal	42036b5e <esp_audio_simple_dec_close>
420108a2:	854e                	mv	a0,s3
420108a4:	ce02                	sw	zero,28(sp)
420108a6:	517010ef          	jal	420125bc <native_aac_decoder_destroy>
420108aa:	000b8563          	beqz	s7,420108b4 <decoder_task+0x13e>
420108ae:	855e                	mv	a0,s7
420108b0:	79b230ef          	jal	4203484a <custom_flac_decoder_destroy>
420108b4:	4712                	lw	a4,4(sp)
420108b6:	000ca483          	lw	s1,0(s9)
420108ba:	004cab03          	lw	s6,4(s9)
420108be:	3fc957b7          	lui	a5,0x3fc95
420108c2:	2e07a023          	sw	zero,736(a5) # 3fc952e0 <s_published_bitrate_bps>
420108c6:	4801                	li	a6,0
420108c8:	4781                	li	a5,0
420108ca:	c31c                	sw	a5,0(a4)
420108cc:	00010d23          	sb	zero,26(sp)
420108d0:	01072223          	sw	a6,4(a4)
420108d4:	fe371097          	auipc	ra,0xfe371
420108d8:	a66080e7          	jalr	-1434(ra) # 4038133a <esp_timer_get_time>
420108dc:	c52a                	sw	a0,136(sp)
420108de:	c902                	sw	zero,144(sp)
420108e0:	cb02                	sw	zero,148(sp)
420108e2:	cd02                	sw	zero,152(sp)
420108e4:	cf02                	sw	zero,156(sp)
420108e6:	d102                	sw	zero,160(sp)
420108e8:	d302                	sw	zero,164(sp)
420108ea:	d502                	sw	zero,168(sp)
420108ec:	d702                	sw	zero,172(sp)
420108ee:	c126                	sw	s1,128(sp)
420108f0:	c35a                	sw	s6,132(sp)
420108f2:	c72e                	sw	a1,140(sp)
420108f4:	478d                	li	a5,3
420108f6:	3afb0a63          	beq	s6,a5,42010caa <decoder_task+0x534>
420108fa:	4789                	li	a5,2
420108fc:	46fb0b63          	beq	s6,a5,42010d72 <decoder_task+0x5fc>
42010900:	640d                	lui	s0,0x3
42010902:	7e8a7463          	bgeu	s4,s0,420110ea <decoder_task+0x974>
42010906:	85a2                	mv	a1,s0
42010908:	854a                	mv	a0,s2
4201090a:	be7f70ef          	jal	420084f0 <realloc>
4201090e:	7e050363          	beqz	a0,420110f4 <decoder_task+0x97e>
42010912:	d682                	sw	zero,108(sp)
42010914:	d882                	sw	zero,112(sp)
42010916:	da82                	sw	zero,116(sp)
42010918:	892a                	mv	s2,a0
4201091a:	8a22                	mv	s4,s0
4201091c:	4791                	li	a5,4
4201091e:	78fb0a63          	beq	s6,a5,420110b2 <decoder_task+0x93c>
42010922:	203357b7          	lui	a5,0x20335
42010926:	04d78793          	addi	a5,a5,77 # 2033504d <CSR_UINTSTATUS+0x2033439c>
4201092a:	086c                	addi	a1,sp,28
4201092c:	10a8                	addi	a0,sp,104
4201092e:	d4be                	sw	a5,104(sp)
42010930:	1c0150ef          	jal	42025af0 <__wrap_esp_audio_simple_dec_open>
42010934:	842a                	mv	s0,a0
42010936:	78050a63          	beqz	a0,420110ca <decoder_task+0x954>
4201093a:	fe378097          	auipc	ra,0xfe378
4201093e:	a80080e7          	jalr	-1408(ra) # 403883ba <esp_log_timestamp>
42010942:	3c1267b7          	lui	a5,0x3c126
42010946:	4985                	li	s3,1
42010948:	86aa                	mv	a3,a0
4201094a:	80078793          	addi	a5,a5,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
4201094e:	093b17e3          	bne	s6,s3,420111dc <decoder_task+0xa66>
42010952:	3c126737          	lui	a4,0x3c126
42010956:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
4201095a:	3c126637          	lui	a2,0x3c126
4201095e:	85ba                	mv	a1,a4
42010960:	8822                	mv	a6,s0
42010962:	a9c60613          	addi	a2,a2,-1380 # 3c125a9c <_esp_trace_encoder_array_end+0x597c>
42010966:	4505                	li	a0,1
42010968:	fe378097          	auipc	ra,0xfe378
4201096c:	94a080e7          	jalr	-1718(ra) # 403882b2 <esp_log>
42010970:	3c126737          	lui	a4,0x3c126
42010974:	57f9                	li	a5,-2
42010976:	9d470693          	addi	a3,a4,-1580 # 3c1259d4 <_esp_trace_encoder_array_end+0x58b4>
4201097a:	28f400e3          	beq	s0,a5,420113fa <decoder_task+0xc84>
4201097e:	3fc957b7          	lui	a5,0x3fc95
42010982:	3047a503          	lw	a0,772(a5) # 3fc95304 <s_state>
42010986:	4601                	li	a2,0
42010988:	85a6                	mv	a1,s1
4201098a:	76a040ef          	jal	420150f4 <native_state_set_audio>
4201098e:	4572                	lw	a0,28(sp)
42010990:	c501                	beqz	a0,42010998 <decoder_task+0x222>
42010992:	1cc260ef          	jal	42036b5e <esp_audio_simple_dec_close>
42010996:	ce02                	sw	zero,28(sp)
42010998:	854a                	mv	a0,s2
4201099a:	b5bf70ef          	jal	420084f4 <cfree>
4201099e:	8c26                	mv	s8,s1
420109a0:	4a01                	li	s4,0
420109a2:	4901                	li	s2,0
420109a4:	4b81                	li	s7,0
420109a6:	4d81                	li	s11,0
420109a8:	3fc957b7          	lui	a5,0x3fc95
420109ac:	2fc7a503          	lw	a0,764(a5) # 3fc952fc <s_encoded>
420109b0:	85e6                	mv	a1,s9
420109b2:	4981                	li	s3,0
420109b4:	50d650ef          	jal	420766c0 <vRingbufferReturnItem>
420109b8:	4401                	li	s0,0
420109ba:	b535                	j	420107e6 <decoder_task+0x70>
420109bc:	39f010ef          	jal	4201255a <decoder_register_codecs>
420109c0:	842a                	mv	s0,a0
420109c2:	26051e63          	bnez	a0,42010c3e <decoder_task+0x4c8>
420109c6:	000ca783          	lw	a5,0(s9)
420109ca:	ec9798e3          	bne	a5,s1,4201089a <decoder_task+0x124>
420109ce:	004ca783          	lw	a5,4(s9)
420109d2:	ed6794e3          	bne	a5,s6,4201089a <decoder_task+0x124>
420109d6:	478d                	li	a5,3
420109d8:	78fb0963          	beq	s6,a5,4201116a <decoder_task+0x9f4>
420109dc:	47f2                	lw	a5,28(sp)
420109de:	00f9e7b3          	or	a5,s3,a5
420109e2:	d3f9                	beqz	a5,420109a8 <decoder_task+0x232>
420109e4:	008cd783          	lhu	a5,8(s9)
420109e8:	00bc8713          	addi	a4,s9,11
420109ec:	ce82                	sw	zero,92(sp)
420109ee:	d082                	sw	zero,96(sp)
420109f0:	d282                	sw	zero,100(sp)
420109f2:	ccbe                	sw	a5,88(sp)
420109f4:	caba                	sw	a4,84(sp)
420109f6:	00acc703          	lbu	a4,10(s9)
420109fa:	ffeb0693          	addi	a3,s6,-2
420109fe:	0016b693          	seqz	a3,a3
42010a02:	00e03733          	snez	a4,a4
42010a06:	c036                	sw	a3,0(sp)
42010a08:	04e10e23          	sb	a4,92(sp)
42010a0c:	38098e63          	beqz	s3,42010da8 <decoder_task+0x632>
42010a10:	e789                	bnez	a5,42010a1a <decoder_task+0x2a4>
42010a12:	05c14783          	lbu	a5,92(sp)
42010a16:	1c078a63          	beqz	a5,42010bea <decoder_task+0x474>
42010a1a:	4781                	li	a5,0
42010a1c:	4801                	li	a6,0
42010a1e:	de3e                	sw	a5,60(sp)
42010a20:	c0c2                	sw	a6,64(sp)
42010a22:	da4a                	sw	s2,52(sp)
42010a24:	dc52                	sw	s4,56(sp)
42010a26:	d082                	sw	zero,96(sp)
42010a28:	fe371097          	auipc	ra,0xfe371
42010a2c:	912080e7          	jalr	-1774(ra) # 4038133a <esp_timer_get_time>
42010a30:	842a                	mv	s0,a0
42010a32:	1850                	addi	a2,sp,52
42010a34:	08cc                	addi	a1,sp,84
42010a36:	854e                	mv	a0,s3
42010a38:	3bb010ef          	jal	420125f2 <native_aac_decoder_process>
42010a3c:	8d2a                	mv	s10,a0
42010a3e:	fe371097          	auipc	ra,0xfe371
42010a42:	8fc080e7          	jalr	-1796(ra) # 4038133a <esp_timer_get_time>
42010a46:	47ca                	lw	a5,144(sp)
42010a48:	46da                	lw	a3,148(sp)
42010a4a:	8d01                	sub	a0,a0,s0
42010a4c:	00a78733          	add	a4,a5,a0
42010a50:	00f737b3          	sltu	a5,a4,a5
42010a54:	97b6                	add	a5,a5,a3
42010a56:	cb3e                	sw	a5,148(sp)
42010a58:	578a                	lw	a5,160(sp)
42010a5a:	c93a                	sw	a4,144(sp)
42010a5c:	571a                	lw	a4,164(sp)
42010a5e:	0785                	addi	a5,a5,1
42010a60:	d13e                	sw	a5,160(sp)
42010a62:	00a77363          	bgeu	a4,a0,42010a68 <decoder_task+0x2f2>
42010a66:	d32a                	sw	a0,164(sp)
42010a68:	8bfd                	andi	a5,a5,31
42010a6a:	56078163          	beqz	a5,42010fcc <decoder_task+0x856>
42010a6e:	2f0a8793          	addi	a5,s5,752
42010a72:	0330000f          	fence	rw,rw
42010a76:	439c                	lw	a5,0(a5)
42010a78:	0230000f          	fence	r,rw
42010a7c:	16979763          	bne	a5,s1,42010bea <decoder_task+0x474>
42010a80:	57e1                	li	a5,-8
42010a82:	50fd0f63          	beq	s10,a5,42010fa0 <decoder_task+0x82a>
42010a86:	580d1a63          	bnez	s10,4201101a <decoder_task+0x8a4>
42010a8a:	5786                	lw	a5,96(sp)
42010a8c:	4766                	lw	a4,88(sp)
42010a8e:	6ef76163          	bltu	a4,a5,42011170 <decoder_task+0x9fa>
42010a92:	8f1d                	sub	a4,a4,a5
42010a94:	56aa                	lw	a3,168(sp)
42010a96:	ccba                	sw	a4,88(sp)
42010a98:	4756                	lw	a4,84(sp)
42010a9a:	96be                	add	a3,a3,a5
42010a9c:	d536                	sw	a3,168(sp)
42010a9e:	97ba                	add	a5,a5,a4
42010aa0:	4706                	lw	a4,64(sp)
42010aa2:	cabe                	sw	a5,84(sp)
42010aa4:	10070c63          	beqz	a4,42010bbc <decoder_task+0x446>
42010aa8:	00cc                	addi	a1,sp,68
42010aaa:	854e                	mv	a0,s3
42010aac:	c282                	sw	zero,68(sp)
42010aae:	c482                	sw	zero,72(sp)
42010ab0:	c682                	sw	zero,76(sp)
42010ab2:	c882                	sw	zero,80(sp)
42010ab4:	667010ef          	jal	4201291a <native_aac_decoder_get_info>
42010ab8:	50051e63          	bnez	a0,42010fd4 <decoder_task+0x85e>
42010abc:	4782                	lw	a5,0(sp)
42010abe:	01b10613          	addi	a2,sp,27
42010ac2:	00cc                	addi	a1,sp,68
42010ac4:	854e                	mv	a0,s3
42010ac6:	00f10da3          	sb	a5,27(sp)
42010aca:	65f010ef          	jal	42012928 <native_aac_decoder_label>
42010ace:	01b14683          	lbu	a3,27(sp)
42010ad2:	842a                	mv	s0,a0
42010ad4:	4501                	li	a0,0
42010ad6:	5c068663          	beqz	a3,420110a2 <decoder_task+0x92c>
42010ada:	2f0a8793          	addi	a5,s5,752
42010ade:	0330000f          	fence	rw,rw
42010ae2:	4398                	lw	a4,0(a5)
42010ae4:	0230000f          	fence	r,rw
42010ae8:	4781                	li	a5,0
42010aea:	06971163          	bne	a4,s1,42010b4c <decoder_task+0x3d6>
42010aee:	4716                	lw	a4,68(sp)
42010af0:	cf31                	beqz	a4,42010b4c <decoder_task+0x3d6>
42010af2:	04914803          	lbu	a6,73(sp)
42010af6:	04080b63          	beqz	a6,42010b4c <decoder_task+0x3d6>
42010afa:	04814603          	lbu	a2,72(sp)
42010afe:	c639                	beqz	a2,42010b4c <decoder_task+0x3d6>
42010b00:	45a6                	lw	a1,72(sp)
42010b02:	47b6                	lw	a5,76(sp)
42010b04:	d23a                	sw	a4,36(sp)
42010b06:	d42e                	sw	a1,40(sp)
42010b08:	45c6                	lw	a1,80(sp)
42010b0a:	d63e                	sw	a5,44(sp)
42010b0c:	4785                	li	a5,1
42010b0e:	06012923          	sw	zero,114(sp)
42010b12:	06012b23          	sw	zero,118(sp)
42010b16:	06011d23          	sh	zero,122(sp)
42010b1a:	d4a2                	sw	s0,104(sp)
42010b1c:	d6ba                	sw	a4,108(sp)
42010b1e:	d82e                	sw	a1,48(sp)
42010b20:	00f10d23          	sb	a5,26(sp)
42010b24:	6a050a63          	beqz	a0,420111d8 <decoder_task+0xa62>
42010b28:	3fc957b7          	lui	a5,0x3fc95
42010b2c:	06a10823          	sb	a0,112(sp)
42010b30:	3047a503          	lw	a0,772(a5) # 3fc95304 <s_state>
42010b34:	06c108a3          	sb	a2,113(sp)
42010b38:	85a6                	mv	a1,s1
42010b3a:	10b0                	addi	a2,sp,104
42010b3c:	daba                	sw	a4,116(sp)
42010b3e:	07010c23          	sb	a6,120(sp)
42010b42:	06d10d23          	sb	a3,122(sp)
42010b46:	68e040ef          	jal	420151d4 <native_state_set_stream_info>
42010b4a:	4785                	li	a5,1
42010b4c:	45b6                	lw	a1,76(sp)
42010b4e:	8526                	mv	a0,s1
42010b50:	00f10d23          	sb	a5,26(sp)
42010b54:	80dff0ef          	jal	42010360 <state_set_decoder_bitrate>
42010b58:	01a14783          	lbu	a5,26(sp)
42010b5c:	c3a5                	beqz	a5,42010bbc <decoder_task+0x446>
42010b5e:	4a0d8763          	beqz	s11,4201100c <decoder_task+0x896>
42010b62:	02814503          	lbu	a0,40(sp)
42010b66:	02914783          	lbu	a5,41(sp)
42010b6a:	4406                	lw	s0,64(sp)
42010b6c:	051d                	addi	a0,a0,7
42010b6e:	810d                	srli	a0,a0,0x3
42010b70:	02f50533          	mul	a0,a0,a5
42010b74:	c91d                	beqz	a0,42010baa <decoder_task+0x434>
42010b76:	5612                	lw	a2,36(sp)
42010b78:	ca0d                	beqz	a2,42010baa <decoder_task+0x434>
42010b7a:	02a45533          	divu	a0,s0,a0
42010b7e:	47a2                	lw	a5,8(sp)
42010b80:	4681                	li	a3,0
42010b82:	02f535b3          	mulhu	a1,a0,a5
42010b86:	02f50533          	mul	a0,a0,a5
42010b8a:	fdff0097          	auipc	ra,0xfdff0
42010b8e:	d22080e7          	jalr	-734(ra) # 400008ac <__udivdi3>
42010b92:	47ea                	lw	a5,152(sp)
42010b94:	46fa                	lw	a3,156(sp)
42010b96:	573a                	lw	a4,172(sp)
42010b98:	953e                	add	a0,a0,a5
42010b9a:	96ae                	add	a3,a3,a1
42010b9c:	00f537b3          	sltu	a5,a0,a5
42010ba0:	97b6                	add	a5,a5,a3
42010ba2:	9722                	add	a4,a4,s0
42010ba4:	cf3e                	sw	a5,156(sp)
42010ba6:	cd2a                	sw	a0,152(sp)
42010ba8:	d73a                	sw	a4,172(sp)
42010baa:	86a2                	mv	a3,s0
42010bac:	864a                	mv	a2,s2
42010bae:	104c                	addi	a1,sp,36
42010bb0:	8526                	mv	a0,s1
42010bb2:	e68ff0ef          	jal	4201021a <send_pcm>
42010bb6:	8daa                	mv	s11,a0
42010bb8:	72050a63          	beqz	a0,420112ec <decoder_task+0xb76>
42010bbc:	fe370097          	auipc	ra,0xfe370
42010bc0:	77e080e7          	jalr	1918(ra) # 4038133a <esp_timer_get_time>
42010bc4:	862e                	mv	a2,a1
42010bc6:	85aa                	mv	a1,a0
42010bc8:	0108                	addi	a0,sp,128
42010bca:	a74ff0ef          	jal	4200fe3e <decode_stats_report>
42010bce:	4706                	lw	a4,64(sp)
42010bd0:	5786                	lw	a5,96(sp)
42010bd2:	05c14683          	lbu	a3,92(sp)
42010bd6:	8fd9                	or	a5,a5,a4
42010bd8:	3a079e63          	bnez	a5,42010f94 <decoder_task+0x81e>
42010bdc:	74068e63          	beqz	a3,42011338 <decoder_task+0xbc2>
42010be0:	4701                	li	a4,0
42010be2:	47e6                	lw	a5,88(sp)
42010be4:	8f5d                	or	a4,a4,a5
42010be6:	e20715e3          	bnez	a4,42010a10 <decoder_task+0x29a>
42010bea:	00acc783          	lbu	a5,10(s9)
42010bee:	48079963          	bnez	a5,42011080 <decoder_task+0x90a>
42010bf2:	489c0763          	beq	s8,s1,42011080 <decoder_task+0x90a>
42010bf6:	8566                	mv	a0,s9
42010bf8:	85e2                	mv	a1,s8
42010bfa:	adbff0ef          	jal	420106d4 <return_decoded_packet>
42010bfe:	4401                	li	s0,0
42010c00:	2f0a8793          	addi	a5,s5,752
42010c04:	0330000f          	fence	rw,rw
42010c08:	0007ac83          	lw	s9,0(a5)
42010c0c:	0230000f          	fence	r,rw
42010c10:	be9c95e3          	bne	s9,s1,420107fa <decoder_task+0x84>
42010c14:	c40c01e3          	beqz	s8,42010856 <decoder_task+0xe0>
42010c18:	c29c1fe3          	bne	s8,s1,42010856 <decoder_task+0xe0>
42010c1c:	4572                	lw	a0,28(sp)
42010c1e:	c119                	beqz	a0,42010c24 <decoder_task+0x4ae>
42010c20:	73f250ef          	jal	42036b5e <esp_audio_simple_dec_close>
42010c24:	ce02                	sw	zero,28(sp)
42010c26:	00098563          	beqz	s3,42010c30 <decoder_task+0x4ba>
42010c2a:	854e                	mv	a0,s3
42010c2c:	191010ef          	jal	420125bc <native_aac_decoder_destroy>
42010c30:	854a                	mv	a0,s2
42010c32:	8c3f70ef          	jal	420084f4 <cfree>
42010c36:	4981                	li	s3,0
42010c38:	4a01                	li	s4,0
42010c3a:	4901                	li	s2,0
42010c3c:	b929                	j	42010856 <decoder_task+0xe0>
42010c3e:	fe377097          	auipc	ra,0xfe377
42010c42:	77c080e7          	jalr	1916(ra) # 403883ba <esp_log_timestamp>
42010c46:	3c126737          	lui	a4,0x3c126
42010c4a:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
42010c4e:	3c126637          	lui	a2,0x3c126
42010c52:	86aa                	mv	a3,a0
42010c54:	85ba                	mv	a1,a4
42010c56:	87a2                	mv	a5,s0
42010c58:	9f460613          	addi	a2,a2,-1548 # 3c1259f4 <_esp_trace_encoder_array_end+0x58d4>
42010c5c:	4505                	li	a0,1
42010c5e:	fe377097          	auipc	ra,0xfe377
42010c62:	654080e7          	jalr	1620(ra) # 403882b2 <esp_log>
42010c66:	3fc957b7          	lui	a5,0x3fc95
42010c6a:	3047a503          	lw	a0,772(a5) # 3fc95304 <s_state>
42010c6e:	000ca583          	lw	a1,0(s9)
42010c72:	3c1267b7          	lui	a5,0x3c126
42010c76:	a2478693          	addi	a3,a5,-1500 # 3c125a24 <_esp_trace_encoder_array_end+0x5904>
42010c7a:	4601                	li	a2,0
42010c7c:	478040ef          	jal	420150f4 <native_state_set_audio>
42010c80:	000cac03          	lw	s8,0(s9)
42010c84:	8566                	mv	a0,s9
42010c86:	85e2                	mv	a1,s8
42010c88:	a4dff0ef          	jal	420106d4 <return_decoded_packet>
42010c8c:	bea9                	j	420107e6 <decoder_task+0x70>
42010c8e:	3fc957b7          	lui	a5,0x3fc95
42010c92:	2fc7a503          	lw	a0,764(a5) # 3fc952fc <s_encoded>
42010c96:	85e6                	mv	a1,s9
42010c98:	229650ef          	jal	420766c0 <vRingbufferReturnItem>
42010c9c:	b6a9                	j	420107e6 <decoder_task+0x70>
42010c9e:	854a                	mv	a0,s2
42010ca0:	855f70ef          	jal	420084f4 <cfree>
42010ca4:	4a01                	li	s4,0
42010ca6:	4901                	li	s2,0
42010ca8:	b649                	j	4201082a <decoder_task+0xb4>
42010caa:	854a                	mv	a0,s2
42010cac:	849f70ef          	jal	420084f4 <cfree>
42010cb0:	33b230ef          	jal	420347ea <custom_flac_decoder_create>
42010cb4:	8baa                	mv	s7,a0
42010cb6:	5a050863          	beqz	a0,42011266 <decoder_task+0xaf0>
42010cba:	4981                	li	s3,0
42010cbc:	4a01                	li	s4,0
42010cbe:	4901                	li	s2,0
42010cc0:	4d81                	li	s11,0
42010cc2:	4661                	li	a2,24
42010cc4:	4581                	li	a1,0
42010cc6:	10a8                	addi	a0,sp,104
42010cc8:	fdfef097          	auipc	ra,0xfdfef
42010ccc:	68c080e7          	jalr	1676(ra) # 40000354 <memset>
42010cd0:	011c                	addi	a5,sp,128
42010cd2:	ccbe                	sw	a5,88(sp)
42010cd4:	105c                	addi	a5,sp,36
42010cd6:	cebe                	sw	a5,92(sp)
42010cd8:	01a10793          	addi	a5,sp,26
42010cdc:	d0be                	sw	a5,96(sp)
42010cde:	caa6                	sw	s1,84(sp)
42010ce0:	00acc683          	lbu	a3,10(s9)
42010ce4:	008cd603          	lhu	a2,8(s9)
42010ce8:	42011737          	lui	a4,0x42011
42010cec:	00d036b3          	snez	a3,a3
42010cf0:	08dc                	addi	a5,sp,84
42010cf2:	42470713          	addi	a4,a4,1060 # 42011424 <custom_flac_output>
42010cf6:	00bc8593          	addi	a1,s9,11
42010cfa:	06810813          	addi	a6,sp,104
42010cfe:	855e                	mv	a0,s7
42010d00:	371230ef          	jal	42034870 <custom_flac_decoder_feed>
42010d04:	47ca                	lw	a5,144(sp)
42010d06:	5726                	lw	a4,104(sp)
42010d08:	465a                	lw	a2,148(sp)
42010d0a:	55b6                	lw	a1,108(sp)
42010d0c:	568a                	lw	a3,160(sp)
42010d0e:	973e                	add	a4,a4,a5
42010d10:	842a                	mv	s0,a0
42010d12:	5546                	lw	a0,112(sp)
42010d14:	962e                	add	a2,a2,a1
42010d16:	00f737b3          	sltu	a5,a4,a5
42010d1a:	97b2                	add	a5,a5,a2
42010d1c:	55d6                	lw	a1,116(sp)
42010d1e:	561a                	lw	a2,164(sp)
42010d20:	96aa                	add	a3,a3,a0
42010d22:	c93a                	sw	a4,144(sp)
42010d24:	cb3e                	sw	a5,148(sp)
42010d26:	d136                	sw	a3,160(sp)
42010d28:	00b67363          	bgeu	a2,a1,42010d2e <decoder_task+0x5b8>
42010d2c:	d32e                	sw	a1,164(sp)
42010d2e:	57aa                	lw	a5,168(sp)
42010d30:	5766                	lw	a4,120(sp)
42010d32:	97ba                	add	a5,a5,a4
42010d34:	d53e                	sw	a5,168(sp)
42010d36:	4a0d8963          	beqz	s11,420111e8 <decoder_task+0xa72>
42010d3a:	4d85                	li	s11,1
42010d3c:	fe370097          	auipc	ra,0xfe370
42010d40:	5fe080e7          	jalr	1534(ra) # 4038133a <esp_timer_get_time>
42010d44:	862e                	mv	a2,a1
42010d46:	85aa                	mv	a1,a0
42010d48:	0108                	addi	a0,sp,128
42010d4a:	8f4ff0ef          	jal	4200fe3e <decode_stats_report>
42010d4e:	00045b63          	bgez	s0,42010d64 <decoder_task+0x5ee>
42010d52:	2f0a8793          	addi	a5,s5,752
42010d56:	0330000f          	fence	rw,rw
42010d5a:	439c                	lw	a5,0(a5)
42010d5c:	0230000f          	fence	r,rw
42010d60:	62978e63          	beq	a5,s1,4201139c <decoder_task+0xc26>
42010d64:	8566                	mv	a0,s9
42010d66:	85e2                	mv	a1,s8
42010d68:	96dff0ef          	jal	420106d4 <return_decoded_packet>
42010d6c:	4b0d                	li	s6,3
42010d6e:	4401                	li	s0,0
42010d70:	bc9d                	j	420107e6 <decoder_task+0x70>
42010d72:	6589                	lui	a1,0x2
42010d74:	36ba0263          	beq	s4,a1,420110d8 <decoder_task+0x962>
42010d78:	854a                	mv	a0,s2
42010d7a:	f76f70ef          	jal	420084f0 <realloc>
42010d7e:	842a                	mv	s0,a0
42010d80:	68050863          	beqz	a0,42011410 <decoder_task+0xc9a>
42010d84:	204347b7          	lui	a5,0x20434
42010d88:	14178793          	addi	a5,a5,321 # 20434141 <CSR_UINTSTATUS+0x20433490>
42010d8c:	d682                	sw	zero,108(sp)
42010d8e:	d882                	sw	zero,112(sp)
42010d90:	da82                	sw	zero,116(sp)
42010d92:	d4be                	sw	a5,104(sp)
42010d94:	7fc010ef          	jal	42012590 <native_aac_decoder_create>
42010d98:	89aa                	mv	s3,a0
42010d9a:	46050763          	beqz	a0,42011208 <decoder_task+0xa92>
42010d9e:	8922                	mv	s2,s0
42010da0:	6a09                	lui	s4,0x2
42010da2:	4b81                	li	s7,0
42010da4:	4d81                	li	s11,0
42010da6:	b93d                	j	420109e4 <decoder_task+0x26e>
42010da8:	5d61                	li	s10,-8
42010daa:	c662                	sw	s8,12(sp)
42010dac:	e789                	bnez	a5,42010db6 <decoder_task+0x640>
42010dae:	05c14783          	lbu	a5,92(sp)
42010db2:	1c078f63          	beqz	a5,42010f90 <decoder_task+0x81a>
42010db6:	4781                	li	a5,0
42010db8:	4801                	li	a6,0
42010dba:	de3e                	sw	a5,60(sp)
42010dbc:	c0c2                	sw	a6,64(sp)
42010dbe:	da4a                	sw	s2,52(sp)
42010dc0:	dc52                	sw	s4,56(sp)
42010dc2:	d082                	sw	zero,96(sp)
42010dc4:	fe370097          	auipc	ra,0xfe370
42010dc8:	576080e7          	jalr	1398(ra) # 4038133a <esp_timer_get_time>
42010dcc:	842a                	mv	s0,a0
42010dce:	4572                	lw	a0,28(sp)
42010dd0:	1850                	addi	a2,sp,52
42010dd2:	08cc                	addi	a1,sp,84
42010dd4:	6a9140ef          	jal	42025c7c <__wrap_esp_audio_simple_dec_process>
42010dd8:	8c2a                	mv	s8,a0
42010dda:	fe370097          	auipc	ra,0xfe370
42010dde:	560080e7          	jalr	1376(ra) # 4038133a <esp_timer_get_time>
42010de2:	47ca                	lw	a5,144(sp)
42010de4:	46da                	lw	a3,148(sp)
42010de6:	8d01                	sub	a0,a0,s0
42010de8:	00a78733          	add	a4,a5,a0
42010dec:	00f737b3          	sltu	a5,a4,a5
42010df0:	97b6                	add	a5,a5,a3
42010df2:	cb3e                	sw	a5,148(sp)
42010df4:	578a                	lw	a5,160(sp)
42010df6:	c93a                	sw	a4,144(sp)
42010df8:	571a                	lw	a4,164(sp)
42010dfa:	0785                	addi	a5,a5,1
42010dfc:	d13e                	sw	a5,160(sp)
42010dfe:	00a77363          	bgeu	a4,a0,42010e04 <decoder_task+0x68e>
42010e02:	d32a                	sw	a0,164(sp)
42010e04:	8bfd                	andi	a5,a5,31
42010e06:	1e078c63          	beqz	a5,42010ffe <decoder_task+0x888>
42010e0a:	2f0a8793          	addi	a5,s5,752
42010e0e:	0330000f          	fence	rw,rw
42010e12:	439c                	lw	a5,0(a5)
42010e14:	0230000f          	fence	r,rw
42010e18:	16979c63          	bne	a5,s1,42010f90 <decoder_task+0x81a>
42010e1c:	1dac0563          	beq	s8,s10,42010fe6 <decoder_task+0x870>
42010e20:	4e0c1b63          	bnez	s8,42011316 <decoder_task+0xba0>
42010e24:	5786                	lw	a5,96(sp)
42010e26:	4766                	lw	a4,88(sp)
42010e28:	34f76463          	bltu	a4,a5,42011170 <decoder_task+0x9fa>
42010e2c:	8f1d                	sub	a4,a4,a5
42010e2e:	56aa                	lw	a3,168(sp)
42010e30:	ccba                	sw	a4,88(sp)
42010e32:	4756                	lw	a4,84(sp)
42010e34:	96be                	add	a3,a3,a5
42010e36:	d536                	sw	a3,168(sp)
42010e38:	97ba                	add	a5,a5,a4
42010e3a:	4706                	lw	a4,64(sp)
42010e3c:	cabe                	sw	a5,84(sp)
42010e3e:	12070363          	beqz	a4,42010f64 <decoder_task+0x7ee>
42010e42:	4572                	lw	a0,28(sp)
42010e44:	00cc                	addi	a1,sp,68
42010e46:	c282                	sw	zero,68(sp)
42010e48:	c482                	sw	zero,72(sp)
42010e4a:	c682                	sw	zero,76(sp)
42010e4c:	c882                	sw	zero,80(sp)
42010e4e:	499250ef          	jal	42036ae6 <esp_audio_simple_dec_get_info>
42010e52:	1a051a63          	bnez	a0,42011006 <decoder_task+0x890>
42010e56:	4782                	lw	a5,0(sp)
42010e58:	00f10da3          	sb	a5,27(sp)
42010e5c:	4789                	li	a5,2
42010e5e:	44fb0e63          	beq	s6,a5,420112ba <decoder_task+0xb44>
42010e62:	4791                	li	a5,4
42010e64:	44fb0663          	beq	s6,a5,420112b0 <decoder_task+0xb3a>
42010e68:	3c126737          	lui	a4,0x3c126
42010e6c:	4785                	li	a5,1
42010e6e:	80070593          	addi	a1,a4,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
42010e72:	38fb1663          	bne	s6,a5,420111fe <decoder_task+0xa88>
42010e76:	2f0a8793          	addi	a5,s5,752
42010e7a:	0330000f          	fence	rw,rw
42010e7e:	439c                	lw	a5,0(a5)
42010e80:	0230000f          	fence	r,rw
42010e84:	06979463          	bne	a5,s1,42010eec <decoder_task+0x776>
42010e88:	4796                	lw	a5,68(sp)
42010e8a:	c3b5                	beqz	a5,42010eee <decoder_task+0x778>
42010e8c:	04914683          	lbu	a3,73(sp)
42010e90:	ceb1                	beqz	a3,42010eec <decoder_task+0x776>
42010e92:	04815703          	lhu	a4,72(sp)
42010e96:	04814503          	lbu	a0,72(sp)
42010e9a:	00875613          	srli	a2,a4,0x8
42010e9e:	0722                	slli	a4,a4,0x8
42010ea0:	963a                	add	a2,a2,a4
42010ea2:	c529                	beqz	a0,42010eec <decoder_task+0x776>
42010ea4:	06012b23          	sw	zero,118(sp)
42010ea8:	06012923          	sw	zero,114(sp)
42010eac:	d23e                	sw	a5,36(sp)
42010eae:	06c11823          	sh	a2,112(sp)
42010eb2:	d6be                	sw	a5,108(sp)
42010eb4:	4626                	lw	a2,72(sp)
42010eb6:	dabe                	sw	a5,116(sp)
42010eb8:	3fc957b7          	lui	a5,0x3fc95
42010ebc:	4746                	lw	a4,80(sp)
42010ebe:	3047a503          	lw	a0,772(a5) # 3fc95304 <s_state>
42010ec2:	06d10c23          	sb	a3,120(sp)
42010ec6:	4782                	lw	a5,0(sp)
42010ec8:	46b6                	lw	a3,76(sp)
42010eca:	06011d23          	sh	zero,122(sp)
42010ece:	d4ae                	sw	a1,104(sp)
42010ed0:	d432                	sw	a2,40(sp)
42010ed2:	4405                	li	s0,1
42010ed4:	10b0                	addi	a2,sp,104
42010ed6:	85a6                	mv	a1,s1
42010ed8:	06f10d23          	sb	a5,122(sp)
42010edc:	d636                	sw	a3,44(sp)
42010ede:	d83a                	sw	a4,48(sp)
42010ee0:	00810d23          	sb	s0,26(sp)
42010ee4:	2f0040ef          	jal	420151d4 <native_state_set_stream_info>
42010ee8:	87a2                	mv	a5,s0
42010eea:	a011                	j	42010eee <decoder_task+0x778>
42010eec:	4781                	li	a5,0
42010eee:	45b6                	lw	a1,76(sp)
42010ef0:	8526                	mv	a0,s1
42010ef2:	00f10d23          	sb	a5,26(sp)
42010ef6:	c6aff0ef          	jal	42010360 <state_set_decoder_bitrate>
42010efa:	01a14783          	lbu	a5,26(sp)
42010efe:	c3bd                	beqz	a5,42010f64 <decoder_task+0x7ee>
42010f00:	1c0d8e63          	beqz	s11,420110dc <decoder_task+0x966>
42010f04:	02814503          	lbu	a0,40(sp)
42010f08:	02914783          	lbu	a5,41(sp)
42010f0c:	4406                	lw	s0,64(sp)
42010f0e:	051d                	addi	a0,a0,7
42010f10:	810d                	srli	a0,a0,0x3
42010f12:	02f50533          	mul	a0,a0,a5
42010f16:	cd15                	beqz	a0,42010f52 <decoder_task+0x7dc>
42010f18:	5612                	lw	a2,36(sp)
42010f1a:	ce05                	beqz	a2,42010f52 <decoder_task+0x7dc>
42010f1c:	02a45533          	divu	a0,s0,a0
42010f20:	000f47b7          	lui	a5,0xf4
42010f24:	24078793          	addi	a5,a5,576 # f4240 <CSR_UINTSTATUS+0xf358f>
42010f28:	4681                	li	a3,0
42010f2a:	02f535b3          	mulhu	a1,a0,a5
42010f2e:	02f50533          	mul	a0,a0,a5
42010f32:	fdff0097          	auipc	ra,0xfdff0
42010f36:	97a080e7          	jalr	-1670(ra) # 400008ac <__udivdi3>
42010f3a:	47ea                	lw	a5,152(sp)
42010f3c:	46fa                	lw	a3,156(sp)
42010f3e:	573a                	lw	a4,172(sp)
42010f40:	953e                	add	a0,a0,a5
42010f42:	96ae                	add	a3,a3,a1
42010f44:	00f537b3          	sltu	a5,a0,a5
42010f48:	97b6                	add	a5,a5,a3
42010f4a:	9722                	add	a4,a4,s0
42010f4c:	cf3e                	sw	a5,156(sp)
42010f4e:	cd2a                	sw	a0,152(sp)
42010f50:	d73a                	sw	a4,172(sp)
42010f52:	86a2                	mv	a3,s0
42010f54:	864a                	mv	a2,s2
42010f56:	104c                	addi	a1,sp,36
42010f58:	8526                	mv	a0,s1
42010f5a:	ac0ff0ef          	jal	4201021a <send_pcm>
42010f5e:	8daa                	mv	s11,a0
42010f60:	38050563          	beqz	a0,420112ea <decoder_task+0xb74>
42010f64:	fe370097          	auipc	ra,0xfe370
42010f68:	3d6080e7          	jalr	982(ra) # 4038133a <esp_timer_get_time>
42010f6c:	862e                	mv	a2,a1
42010f6e:	85aa                	mv	a1,a0
42010f70:	0108                	addi	a0,sp,128
42010f72:	ecdfe0ef          	jal	4200fe3e <decode_stats_report>
42010f76:	4706                	lw	a4,64(sp)
42010f78:	5786                	lw	a5,96(sp)
42010f7a:	05c14683          	lbu	a3,92(sp)
42010f7e:	8fd9                	or	a5,a5,a4
42010f80:	efa9                	bnez	a5,42010fda <decoder_task+0x864>
42010f82:	3a068b63          	beqz	a3,42011338 <decoder_task+0xbc2>
42010f86:	4701                	li	a4,0
42010f88:	47e6                	lw	a5,88(sp)
42010f8a:	8f5d                	or	a4,a4,a5
42010f8c:	e20710e3          	bnez	a4,42010dac <decoder_task+0x636>
42010f90:	4c32                	lw	s8,12(sp)
42010f92:	b9a1                	j	42010bea <decoder_task+0x474>
42010f94:	c40697e3          	bnez	a3,42010be2 <decoder_task+0x46c>
42010f98:	47e6                	lw	a5,88(sp)
42010f9a:	a80790e3          	bnez	a5,42010a1a <decoder_task+0x2a4>
42010f9e:	b1b1                	j	42010bea <decoder_task+0x474>
42010fa0:	5706                	lw	a4,96(sp)
42010fa2:	47d6                	lw	a5,84(sp)
42010fa4:	56aa                	lw	a3,168(sp)
42010fa6:	5472                	lw	s0,60(sp)
42010fa8:	97ba                	add	a5,a5,a4
42010faa:	cabe                	sw	a5,84(sp)
42010fac:	47e6                	lw	a5,88(sp)
42010fae:	96ba                	add	a3,a3,a4
42010fb0:	d536                	sw	a3,168(sp)
42010fb2:	8f99                	sub	a5,a5,a4
42010fb4:	ccbe                	sw	a5,88(sp)
42010fb6:	308a7763          	bgeu	s4,s0,420112c4 <decoder_task+0xb4e>
42010fba:	85a2                	mv	a1,s0
42010fbc:	854a                	mv	a0,s2
42010fbe:	d32f70ef          	jal	420084f0 <realloc>
42010fc2:	30050163          	beqz	a0,420112c4 <decoder_task+0xb4e>
42010fc6:	8a22                	mv	s4,s0
42010fc8:	892a                	mv	s2,a0
42010fca:	bc81                	j	42010a1a <decoder_task+0x2a4>
42010fcc:	4505                	li	a0,1
42010fce:	664ff0ef          	jal	42110632 <vTaskDelay>
42010fd2:	bc71                	j	42010a6e <decoder_task+0x2f8>
42010fd4:	00010d23          	sb	zero,26(sp)
42010fd8:	b6d5                	j	42010bbc <decoder_task+0x446>
42010fda:	f6dd                	bnez	a3,42010f88 <decoder_task+0x812>
42010fdc:	47e6                	lw	a5,88(sp)
42010fde:	dc079ce3          	bnez	a5,42010db6 <decoder_task+0x640>
42010fe2:	4c32                	lw	s8,12(sp)
42010fe4:	b119                	j	42010bea <decoder_task+0x474>
42010fe6:	5472                	lw	s0,60(sp)
42010fe8:	2c8a7e63          	bgeu	s4,s0,420112c4 <decoder_task+0xb4e>
42010fec:	85a2                	mv	a1,s0
42010fee:	854a                	mv	a0,s2
42010ff0:	d00f70ef          	jal	420084f0 <realloc>
42010ff4:	2c050863          	beqz	a0,420112c4 <decoder_task+0xb4e>
42010ff8:	892a                	mv	s2,a0
42010ffa:	8a22                	mv	s4,s0
42010ffc:	bb6d                	j	42010db6 <decoder_task+0x640>
42010ffe:	4505                	li	a0,1
42011000:	632ff0ef          	jal	42110632 <vTaskDelay>
42011004:	b519                	j	42010e0a <decoder_task+0x694>
42011006:	00010d23          	sb	zero,26(sp)
4201100a:	bfa9                	j	42010f64 <decoder_task+0x7ee>
4201100c:	3c1267b7          	lui	a5,0x3c126
42011010:	b0878513          	addi	a0,a5,-1272 # 3c125b08 <_esp_trace_encoder_array_end+0x59e8>
42011014:	9a2ff0ef          	jal	420101b6 <log_runtime_memory>
42011018:	b6a9                	j	42010b62 <decoder_task+0x3ec>
4201101a:	846a                	mv	s0,s10
4201101c:	4a09                	li	s4,2
4201101e:	fe377097          	auipc	ra,0xfe377
42011022:	39c080e7          	jalr	924(ra) # 403883ba <esp_log_timestamp>
42011026:	2f4b0a63          	beq	s6,s4,4201131a <decoder_task+0xba4>
4201102a:	4791                	li	a5,4
4201102c:	2efb0c63          	beq	s6,a5,42011324 <decoder_task+0xbae>
42011030:	3c1267b7          	lui	a5,0x3c126
42011034:	4705                	li	a4,1
42011036:	80078793          	addi	a5,a5,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
4201103a:	00eb0663          	beq	s6,a4,42011046 <decoder_task+0x8d0>
4201103e:	3c1267b7          	lui	a5,0x3c126
42011042:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
42011046:	3c126737          	lui	a4,0x3c126
4201104a:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
4201104e:	3c126637          	lui	a2,0x3c126
42011052:	86aa                	mv	a3,a0
42011054:	85ba                	mv	a1,a4
42011056:	8822                	mv	a6,s0
42011058:	b3c60613          	addi	a2,a2,-1220 # 3c125b3c <_esp_trace_encoder_array_end+0x5a1c>
4201105c:	4509                	li	a0,2
4201105e:	fe377097          	auipc	ra,0xfe377
42011062:	254080e7          	jalr	596(ra) # 403882b2 <esp_log>
42011066:	3fc957b7          	lui	a5,0x3fc95
4201106a:	3047a503          	lw	a0,772(a5) # 3fc95304 <s_state>
4201106e:	3c1267b7          	lui	a5,0x3c126
42011072:	9e478693          	addi	a3,a5,-1564 # 3c1259e4 <_esp_trace_encoder_array_end+0x58c4>
42011076:	85a6                	mv	a1,s1
42011078:	4601                	li	a2,0
4201107a:	07a040ef          	jal	420150f4 <native_state_set_audio>
4201107e:	8c26                	mv	s8,s1
42011080:	4572                	lw	a0,28(sp)
42011082:	c119                	beqz	a0,42011088 <decoder_task+0x912>
42011084:	2db250ef          	jal	42036b5e <esp_audio_simple_dec_close>
42011088:	ce02                	sw	zero,28(sp)
4201108a:	00098563          	beqz	s3,42011094 <decoder_task+0x91e>
4201108e:	854e                	mv	a0,s3
42011090:	52c010ef          	jal	420125bc <native_aac_decoder_destroy>
42011094:	854a                	mv	a0,s2
42011096:	c5ef70ef          	jal	420084f4 <cfree>
4201109a:	4981                	li	s3,0
4201109c:	4a01                	li	s4,0
4201109e:	4901                	li	s2,0
420110a0:	be99                	j	42010bf6 <decoder_task+0x480>
420110a2:	854e                	mv	a0,s3
420110a4:	0dd010ef          	jal	42012980 <native_aac_decoder_source_channels>
420110a8:	01b14683          	lbu	a3,27(sp)
420110ac:	0ff57513          	zext.b	a0,a0
420110b0:	b42d                	j	42010ada <decoder_task+0x364>
420110b2:	204747b7          	lui	a5,0x20474
420110b6:	74f78793          	addi	a5,a5,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
420110ba:	086c                	addi	a1,sp,28
420110bc:	10a8                	addi	a0,sp,104
420110be:	d4be                	sw	a5,104(sp)
420110c0:	231140ef          	jal	42025af0 <__wrap_esp_audio_simple_dec_open>
420110c4:	842a                	mv	s0,a0
420110c6:	18051063          	bnez	a0,42011246 <decoder_task+0xad0>
420110ca:	4bf2                	lw	s7,28(sp)
420110cc:	4d81                	li	s11,0
420110ce:	8c0b8de3          	beqz	s7,420109a8 <decoder_task+0x232>
420110d2:	4981                	li	s3,0
420110d4:	4b81                	li	s7,0
420110d6:	b239                	j	420109e4 <decoder_task+0x26e>
420110d8:	844a                	mv	s0,s2
420110da:	b16d                	j	42010d84 <decoder_task+0x60e>
420110dc:	3c1267b7          	lui	a5,0x3c126
420110e0:	b0878513          	addi	a0,a5,-1272 # 3c125b08 <_esp_trace_encoder_array_end+0x59e8>
420110e4:	8d2ff0ef          	jal	420101b6 <log_runtime_memory>
420110e8:	bd31                	j	42010f04 <decoder_task+0x78e>
420110ea:	d682                	sw	zero,108(sp)
420110ec:	d882                	sw	zero,112(sp)
420110ee:	da82                	sw	zero,116(sp)
420110f0:	82dff06f          	j	4201091c <decoder_task+0x1a6>
420110f4:	fe377097          	auipc	ra,0xfe377
420110f8:	2c6080e7          	jalr	710(ra) # 403883ba <esp_log_timestamp>
420110fc:	4791                	li	a5,4
420110fe:	4405                	li	s0,1
42011100:	86aa                	mv	a3,a0
42011102:	1cfb0f63          	beq	s6,a5,420112e0 <decoder_task+0xb6a>
42011106:	3c1267b7          	lui	a5,0x3c126
4201110a:	80078793          	addi	a5,a5,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
4201110e:	008b0663          	beq	s6,s0,4201111a <decoder_task+0x9a4>
42011112:	3c1267b7          	lui	a5,0x3c126
42011116:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
4201111a:	3c126737          	lui	a4,0x3c126
4201111e:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
42011122:	3c126637          	lui	a2,0x3c126
42011126:	85ba                	mv	a1,a4
42011128:	a6c60613          	addi	a2,a2,-1428 # 3c125a6c <_esp_trace_encoder_array_end+0x594c>
4201112c:	4505                	li	a0,1
4201112e:	fe377097          	auipc	ra,0xfe377
42011132:	184080e7          	jalr	388(ra) # 403882b2 <esp_log>
42011136:	3fc957b7          	lui	a5,0x3fc95
4201113a:	3047a503          	lw	a0,772(a5) # 3fc95304 <s_state>
4201113e:	3c1267b7          	lui	a5,0x3c126
42011142:	9c878693          	addi	a3,a5,-1592 # 3c1259c8 <_esp_trace_encoder_array_end+0x58a8>
42011146:	85a6                	mv	a1,s1
42011148:	4601                	li	a2,0
4201114a:	7ab030ef          	jal	420150f4 <native_state_set_audio>
4201114e:	3fc957b7          	lui	a5,0x3fc95
42011152:	2fc7a503          	lw	a0,764(a5) # 3fc952fc <s_encoded>
42011156:	85e6                	mv	a1,s9
42011158:	8c26                	mv	s8,s1
4201115a:	566650ef          	jal	420766c0 <vRingbufferReturnItem>
4201115e:	4981                	li	s3,0
42011160:	4d81                	li	s11,0
42011162:	4b81                	li	s7,0
42011164:	4401                	li	s0,0
42011166:	e80ff06f          	j	420107e6 <decoder_task+0x70>
4201116a:	be0b8de3          	beqz	s7,42010d64 <decoder_task+0x5ee>
4201116e:	be91                	j	42010cc2 <decoder_task+0x54c>
42011170:	fe377097          	auipc	ra,0xfe377
42011174:	24a080e7          	jalr	586(ra) # 403883ba <esp_log_timestamp>
42011178:	4789                	li	a5,2
4201117a:	4405                	li	s0,1
4201117c:	0efb0063          	beq	s6,a5,4201125c <decoder_task+0xae6>
42011180:	4791                	li	a5,4
42011182:	1afb0663          	beq	s6,a5,4201132e <decoder_task+0xbb8>
42011186:	3c1267b7          	lui	a5,0x3c126
4201118a:	80078793          	addi	a5,a5,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
4201118e:	008b0663          	beq	s6,s0,4201119a <decoder_task+0xa24>
42011192:	3c1267b7          	lui	a5,0x3c126
42011196:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
4201119a:	48e6                	lw	a7,88(sp)
4201119c:	5806                	lw	a6,96(sp)
4201119e:	3c126737          	lui	a4,0x3c126
420111a2:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
420111a6:	3c126637          	lui	a2,0x3c126
420111aa:	86aa                	mv	a3,a0
420111ac:	85ba                	mv	a1,a4
420111ae:	b6060613          	addi	a2,a2,-1184 # 3c125b60 <_esp_trace_encoder_array_end+0x5a40>
420111b2:	4505                	li	a0,1
420111b4:	fe377097          	auipc	ra,0xfe377
420111b8:	0fe080e7          	jalr	254(ra) # 403882b2 <esp_log>
420111bc:	3fc957b7          	lui	a5,0x3fc95
420111c0:	3047a503          	lw	a0,772(a5) # 3fc95304 <s_state>
420111c4:	3c1267b7          	lui	a5,0x3c126
420111c8:	b9c78693          	addi	a3,a5,-1124 # 3c125b9c <_esp_trace_encoder_array_end+0x5a7c>
420111cc:	85a6                	mv	a1,s1
420111ce:	4601                	li	a2,0
420111d0:	725030ef          	jal	420150f4 <native_state_set_audio>
420111d4:	8c26                	mv	s8,s1
420111d6:	b56d                	j	42011080 <decoder_task+0x90a>
420111d8:	8542                	mv	a0,a6
420111da:	b2b9                	j	42010b28 <decoder_task+0x3b2>
420111dc:	3c1267b7          	lui	a5,0x3c126
420111e0:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
420111e4:	f6eff06f          	j	42010952 <decoder_task+0x1dc>
420111e8:	01a14d83          	lbu	s11,26(sp)
420111ec:	b40d88e3          	beqz	s11,42010d3c <decoder_task+0x5c6>
420111f0:	3c1267b7          	lui	a5,0x3c126
420111f4:	ac478513          	addi	a0,a5,-1340 # 3c125ac4 <_esp_trace_encoder_array_end+0x59a4>
420111f8:	fbffe0ef          	jal	420101b6 <log_runtime_memory>
420111fc:	be3d                	j	42010d3a <decoder_task+0x5c4>
420111fe:	3c1267b7          	lui	a5,0x3c126
42011202:	80478593          	addi	a1,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
42011206:	b985                	j	42010e76 <decoder_task+0x700>
42011208:	fe377097          	auipc	ra,0xfe377
4201120c:	1b2080e7          	jalr	434(ra) # 403883ba <esp_log_timestamp>
42011210:	3c1267b7          	lui	a5,0x3c126
42011214:	80c78713          	addi	a4,a5,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
42011218:	3c126637          	lui	a2,0x3c126
4201121c:	3c1257b7          	lui	a5,0x3c125
42011220:	86aa                	mv	a3,a0
42011222:	7f078793          	addi	a5,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
42011226:	85ba                	mv	a1,a4
42011228:	a9c60613          	addi	a2,a2,-1380 # 3c125a9c <_esp_trace_encoder_array_end+0x597c>
4201122c:	5879                	li	a6,-2
4201122e:	4505                	li	a0,1
42011230:	fe377097          	auipc	ra,0xfe377
42011234:	082080e7          	jalr	130(ra) # 403882b2 <esp_log>
42011238:	3c1267b7          	lui	a5,0x3c126
4201123c:	8922                	mv	s2,s0
4201123e:	9c878693          	addi	a3,a5,-1592 # 3c1259c8 <_esp_trace_encoder_array_end+0x58a8>
42011242:	f3cff06f          	j	4201097e <decoder_task+0x208>
42011246:	fe377097          	auipc	ra,0xfe377
4201124a:	174080e7          	jalr	372(ra) # 403883ba <esp_log_timestamp>
4201124e:	3c1257b7          	lui	a5,0x3c125
42011252:	86aa                	mv	a3,a0
42011254:	7fc78793          	addi	a5,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
42011258:	efaff06f          	j	42010952 <decoder_task+0x1dc>
4201125c:	3c1257b7          	lui	a5,0x3c125
42011260:	7f078793          	addi	a5,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
42011264:	bf1d                	j	4201119a <decoder_task+0xa24>
42011266:	fe377097          	auipc	ra,0xfe377
4201126a:	154080e7          	jalr	340(ra) # 403883ba <esp_log_timestamp>
4201126e:	3c1267b7          	lui	a5,0x3c126
42011272:	80c78713          	addi	a4,a5,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
42011276:	3c1267b7          	lui	a5,0x3c126
4201127a:	86aa                	mv	a3,a0
4201127c:	85ba                	mv	a1,a4
4201127e:	a3878613          	addi	a2,a5,-1480 # 3c125a38 <_esp_trace_encoder_array_end+0x5918>
42011282:	4505                	li	a0,1
42011284:	fe377097          	auipc	ra,0xfe377
42011288:	02e080e7          	jalr	46(ra) # 403882b2 <esp_log>
4201128c:	3fc957b7          	lui	a5,0x3fc95
42011290:	3047a503          	lw	a0,772(a5) # 3fc95304 <s_state>
42011294:	3c1267b7          	lui	a5,0x3c126
42011298:	9c878693          	addi	a3,a5,-1592 # 3c1259c8 <_esp_trace_encoder_array_end+0x58a8>
4201129c:	85a6                	mv	a1,s1
4201129e:	4601                	li	a2,0
420112a0:	655030ef          	jal	420150f4 <native_state_set_audio>
420112a4:	8c26                	mv	s8,s1
420112a6:	4981                	li	s3,0
420112a8:	4901                	li	s2,0
420112aa:	4a01                	li	s4,0
420112ac:	4d81                	li	s11,0
420112ae:	bc5d                	j	42010d64 <decoder_task+0x5ee>
420112b0:	3c1257b7          	lui	a5,0x3c125
420112b4:	7fc78593          	addi	a1,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
420112b8:	be7d                	j	42010e76 <decoder_task+0x700>
420112ba:	3c1257b7          	lui	a5,0x3c125
420112be:	7f078593          	addi	a1,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
420112c2:	be55                	j	42010e76 <decoder_task+0x700>
420112c4:	3fc957b7          	lui	a5,0x3fc95
420112c8:	3047a503          	lw	a0,772(a5) # 3fc95304 <s_state>
420112cc:	3c1267b7          	lui	a5,0x3c126
420112d0:	b2478693          	addi	a3,a5,-1244 # 3c125b24 <_esp_trace_encoder_array_end+0x5a04>
420112d4:	4601                	li	a2,0
420112d6:	85a6                	mv	a1,s1
420112d8:	61d030ef          	jal	420150f4 <native_state_set_audio>
420112dc:	8c26                	mv	s8,s1
420112de:	b34d                	j	42011080 <decoder_task+0x90a>
420112e0:	3c1257b7          	lui	a5,0x3c125
420112e4:	7fc78793          	addi	a5,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
420112e8:	bd0d                	j	4201111a <decoder_task+0x9a4>
420112ea:	4c32                	lw	s8,12(sp)
420112ec:	fe377097          	auipc	ra,0xfe377
420112f0:	0ce080e7          	jalr	206(ra) # 403883ba <esp_log_timestamp>
420112f4:	3c1267b7          	lui	a5,0x3c126
420112f8:	80c78713          	addi	a4,a5,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
420112fc:	3c1267b7          	lui	a5,0x3c126
42011300:	86aa                	mv	a3,a0
42011302:	85ba                	mv	a1,a4
42011304:	bb078613          	addi	a2,a5,-1104 # 3c125bb0 <_esp_trace_encoder_array_end+0x5a90>
42011308:	4509                	li	a0,2
4201130a:	fe377097          	auipc	ra,0xfe377
4201130e:	fa8080e7          	jalr	-88(ra) # 403882b2 <esp_log>
42011312:	4d85                	li	s11,1
42011314:	b8d9                	j	42010bea <decoder_task+0x474>
42011316:	8462                	mv	s0,s8
42011318:	b311                	j	4201101c <decoder_task+0x8a6>
4201131a:	3c1257b7          	lui	a5,0x3c125
4201131e:	7f078793          	addi	a5,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
42011322:	b315                	j	42011046 <decoder_task+0x8d0>
42011324:	3c1257b7          	lui	a5,0x3c125
42011328:	7fc78793          	addi	a5,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
4201132c:	bb29                	j	42011046 <decoder_task+0x8d0>
4201132e:	3c1257b7          	lui	a5,0x3c125
42011332:	7fc78793          	addi	a5,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
42011336:	b595                	j	4201119a <decoder_task+0xa24>
42011338:	fe377097          	auipc	ra,0xfe377
4201133c:	082080e7          	jalr	130(ra) # 403883ba <esp_log_timestamp>
42011340:	4789                	li	a5,2
42011342:	4405                	li	s0,1
42011344:	86aa                	mv	a3,a0
42011346:	0afb0563          	beq	s6,a5,420113f0 <decoder_task+0xc7a>
4201134a:	4791                	li	a5,4
4201134c:	0afb0d63          	beq	s6,a5,42011406 <decoder_task+0xc90>
42011350:	3c1267b7          	lui	a5,0x3c126
42011354:	80078793          	addi	a5,a5,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
42011358:	008b0663          	beq	s6,s0,42011364 <decoder_task+0xbee>
4201135c:	3c1267b7          	lui	a5,0x3c126
42011360:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
42011364:	3c126737          	lui	a4,0x3c126
42011368:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
4201136c:	3c126637          	lui	a2,0x3c126
42011370:	85ba                	mv	a1,a4
42011372:	bd060613          	addi	a2,a2,-1072 # 3c125bd0 <_esp_trace_encoder_array_end+0x5ab0>
42011376:	4505                	li	a0,1
42011378:	fe377097          	auipc	ra,0xfe377
4201137c:	f3a080e7          	jalr	-198(ra) # 403882b2 <esp_log>
42011380:	3fc957b7          	lui	a5,0x3fc95
42011384:	3047a503          	lw	a0,772(a5) # 3fc95304 <s_state>
42011388:	3c1267b7          	lui	a5,0x3c126
4201138c:	c0078693          	addi	a3,a5,-1024 # 3c125c00 <_esp_trace_encoder_array_end+0x5ae0>
42011390:	85a6                	mv	a1,s1
42011392:	4601                	li	a2,0
42011394:	561030ef          	jal	420150f4 <native_state_set_audio>
42011398:	8c26                	mv	s8,s1
4201139a:	b1dd                	j	42011080 <decoder_task+0x90a>
4201139c:	fe377097          	auipc	ra,0xfe377
420113a0:	01e080e7          	jalr	30(ra) # 403883ba <esp_log_timestamp>
420113a4:	3c126737          	lui	a4,0x3c126
420113a8:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
420113ac:	3c126637          	lui	a2,0x3c126
420113b0:	86aa                	mv	a3,a0
420113b2:	87a2                	mv	a5,s0
420113b4:	85ba                	mv	a1,a4
420113b6:	adc60613          	addi	a2,a2,-1316 # 3c125adc <_esp_trace_encoder_array_end+0x59bc>
420113ba:	4509                	li	a0,2
420113bc:	fe377097          	auipc	ra,0xfe377
420113c0:	ef6080e7          	jalr	-266(ra) # 403882b2 <esp_log>
420113c4:	3c126737          	lui	a4,0x3c126
420113c8:	0419                	addi	s0,s0,6 # 3006 <CSR_UINTSTATUS+0x2355>
420113ca:	4785                	li	a5,1
420113cc:	9e470693          	addi	a3,a4,-1564 # 3c1259e4 <_esp_trace_encoder_array_end+0x58c4>
420113d0:	0087e663          	bltu	a5,s0,420113dc <decoder_task+0xc66>
420113d4:	3c1267b7          	lui	a5,0x3c126
420113d8:	9c878693          	addi	a3,a5,-1592 # 3c1259c8 <_esp_trace_encoder_array_end+0x58a8>
420113dc:	3fc957b7          	lui	a5,0x3fc95
420113e0:	3047a503          	lw	a0,772(a5) # 3fc95304 <s_state>
420113e4:	4601                	li	a2,0
420113e6:	85a6                	mv	a1,s1
420113e8:	50d030ef          	jal	420150f4 <native_state_set_audio>
420113ec:	8c26                	mv	s8,s1
420113ee:	ba9d                	j	42010d64 <decoder_task+0x5ee>
420113f0:	3c1257b7          	lui	a5,0x3c125
420113f4:	7f078793          	addi	a5,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
420113f8:	b7b5                	j	42011364 <decoder_task+0xbee>
420113fa:	3c1267b7          	lui	a5,0x3c126
420113fe:	9c878693          	addi	a3,a5,-1592 # 3c1259c8 <_esp_trace_encoder_array_end+0x58a8>
42011402:	d7cff06f          	j	4201097e <decoder_task+0x208>
42011406:	3c1257b7          	lui	a5,0x3c125
4201140a:	7fc78793          	addi	a5,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
4201140e:	bf99                	j	42011364 <decoder_task+0xbee>
42011410:	fe377097          	auipc	ra,0xfe377
42011414:	faa080e7          	jalr	-86(ra) # 403883ba <esp_log_timestamp>
42011418:	3c1257b7          	lui	a5,0x3c125
4201141c:	86aa                	mv	a3,a0
4201141e:	7f078793          	addi	a5,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
42011422:	b9e5                	j	4201111a <decoder_task+0x9a4>
