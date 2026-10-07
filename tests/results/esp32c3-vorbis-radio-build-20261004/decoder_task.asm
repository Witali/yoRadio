
idf\esp32c3-oled-native\build-vorbis-repair-production\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42010772 <decoder_task>:
42010772:	7151                	addi	sp,sp,-240
42010774:	d5a2                	sw	s0,232(sp)
42010776:	d1ca                	sw	s2,224(sp)
42010778:	cfce                	sw	s3,220(sp)
4201077a:	cdd2                	sw	s4,216(sp)
4201077c:	cbd6                	sw	s5,212(sp)
4201077e:	c9da                	sw	s6,208(sp)
42010780:	c7de                	sw	s7,204(sp)
42010782:	c5e2                	sw	s8,200(sp)
42010784:	c3e6                	sw	s9,196(sp)
42010786:	df6e                	sw	s11,188(sp)
42010788:	d786                	sw	ra,236(sp)
4201078a:	d3a6                	sw	s1,228(sp)
4201078c:	c1ea                	sw	s10,192(sp)
4201078e:	5b1010ef          	jal	4201253e <decoder_register_codecs>
42010792:	3fc957b7          	lui	a5,0x3fc95
42010796:	2d878793          	addi	a5,a5,728 # 3fc952d8 <s_bitrate_updated_us>
4201079a:	ce02                	sw	zero,28(sp)
4201079c:	c102                	sw	zero,128(sp)
4201079e:	c302                	sw	zero,132(sp)
420107a0:	c502                	sw	zero,136(sp)
420107a2:	c702                	sw	zero,140(sp)
420107a4:	c902                	sw	zero,144(sp)
420107a6:	cb02                	sw	zero,148(sp)
420107a8:	cd02                	sw	zero,152(sp)
420107aa:	cf02                	sw	zero,156(sp)
420107ac:	d102                	sw	zero,160(sp)
420107ae:	d302                	sw	zero,164(sp)
420107b0:	d502                	sw	zero,168(sp)
420107b2:	d702                	sw	zero,172(sp)
420107b4:	d202                	sw	zero,36(sp)
420107b6:	d402                	sw	zero,40(sp)
420107b8:	d602                	sw	zero,44(sp)
420107ba:	d802                	sw	zero,48(sp)
420107bc:	00010d23          	sb	zero,26(sp)
420107c0:	842a                	mv	s0,a0
420107c2:	c43e                	sw	a5,8(sp)
420107c4:	4981                	li	s3,0
420107c6:	4a81                	li	s5,0
420107c8:	4a01                	li	s4,0
420107ca:	4d81                	li	s11,0
420107cc:	4b81                	li	s7,0
420107ce:	4c81                	li	s9,0
420107d0:	4901                	li	s2,0
420107d2:	4c01                	li	s8,0
420107d4:	3fc95b37          	lui	s6,0x3fc95
420107d8:	2f0b0793          	addi	a5,s6,752 # 3fc952f0 <s_generation>
420107dc:	0330000f          	fence	rw,rw
420107e0:	4384                	lw	s1,0(a5)
420107e2:	0230000f          	fence	r,rw
420107e6:	41248d63          	beq	s1,s2,42010c00 <decoder_task+0x48e>
420107ea:	3fc957b7          	lui	a5,0x3fc95
420107ee:	2ec78793          	addi	a5,a5,748 # 3fc952ec <s_decoder_target_codec>
420107f2:	0330000f          	fence	rw,rw
420107f6:	0007a903          	lw	s2,0(a5)
420107fa:	0230000f          	fence	r,rw
420107fe:	4572                	lw	a0,28(sp)
42010800:	c119                	beqz	a0,42010806 <decoder_task+0x94>
42010802:	120260ef          	jal	42036922 <esp_audio_simple_dec_close>
42010806:	854e                	mv	a0,s3
42010808:	ce02                	sw	zero,28(sp)
4201080a:	597010ef          	jal	420125a0 <native_aac_decoder_destroy>
4201080e:	000c0563          	beqz	s8,42010818 <decoder_task+0xa6>
42010812:	8562                	mv	a0,s8
42010814:	5fb230ef          	jal	4203460e <custom_flac_decoder_destroy>
42010818:	46090863          	beqz	s2,42010c88 <decoder_task+0x516>
4201081c:	d202                	sw	zero,36(sp)
4201081e:	d402                	sw	zero,40(sp)
42010820:	d602                	sw	zero,44(sp)
42010822:	d802                	sw	zero,48(sp)
42010824:	00010d23          	sb	zero,26(sp)
42010828:	3fc957b7          	lui	a5,0x3fc95
4201082c:	2e878793          	addi	a5,a5,744 # 3fc952e8 <s_decoder_released_generation>
42010830:	0310000f          	fence	rw,w
42010834:	c384                	sw	s1,0(a5)
42010836:	0330000f          	fence	rw,rw
4201083a:	4c01                	li	s8,0
4201083c:	8926                	mv	s2,s1
4201083e:	4c81                	li	s9,0
42010840:	4b81                	li	s7,0
42010842:	4d81                	li	s11,0
42010844:	4981                	li	s3,0
42010846:	3fc957b7          	lui	a5,0x3fc95
4201084a:	2fc7a503          	lw	a0,764(a5) # 3fc952fc <s_encoded>
4201084e:	4651                	li	a2,20
42010850:	100c                	addi	a1,sp,32
42010852:	d002                	sw	zero,32(sp)
42010854:	3b5650ef          	jal	42076408 <xRingbufferReceive>
42010858:	84aa                	mv	s1,a0
4201085a:	dd3d                	beqz	a0,420107d8 <decoder_task+0x66>
4201085c:	4118                	lw	a4,0(a0)
4201085e:	2f0b0793          	addi	a5,s6,752
42010862:	0330000f          	fence	rw,rw
42010866:	439c                	lw	a5,0(a5)
42010868:	0230000f          	fence	r,rw
4201086c:	40f71663          	bne	a4,a5,42010c78 <decoder_task+0x506>
42010870:	411c                	lw	a5,0(a0)
42010872:	41978363          	beq	a5,s9,42010c78 <decoder_task+0x506>
42010876:	4158                	lw	a4,4(a0)
42010878:	e709                	bnez	a4,42010882 <decoder_task+0x110>
4201087a:	00a54703          	lbu	a4,10(a0)
4201087e:	3e071963          	bnez	a4,42010c70 <decoder_task+0x4fe>
42010882:	12041563          	bnez	s0,420109ac <decoder_task+0x23a>
42010886:	13278b63          	beq	a5,s2,420109bc <decoder_task+0x24a>
4201088a:	4572                	lw	a0,28(sp)
4201088c:	c119                	beqz	a0,42010892 <decoder_task+0x120>
4201088e:	094260ef          	jal	42036922 <esp_audio_simple_dec_close>
42010892:	854e                	mv	a0,s3
42010894:	ce02                	sw	zero,28(sp)
42010896:	50b010ef          	jal	420125a0 <native_aac_decoder_destroy>
4201089a:	000c0563          	beqz	s8,420108a4 <decoder_task+0x132>
4201089e:	8562                	mv	a0,s8
420108a0:	56f230ef          	jal	4203460e <custom_flac_decoder_destroy>
420108a4:	4722                	lw	a4,8(sp)
420108a6:	0004a903          	lw	s2,0(s1)
420108aa:	0044ab83          	lw	s7,4(s1)
420108ae:	3fc957b7          	lui	a5,0x3fc95
420108b2:	2e07a023          	sw	zero,736(a5) # 3fc952e0 <s_published_bitrate_bps>
420108b6:	4801                	li	a6,0
420108b8:	4781                	li	a5,0
420108ba:	c31c                	sw	a5,0(a4)
420108bc:	00010d23          	sb	zero,26(sp)
420108c0:	01072223          	sw	a6,4(a4)
420108c4:	fe371097          	auipc	ra,0xfe371
420108c8:	a76080e7          	jalr	-1418(ra) # 4038133a <esp_timer_get_time>
420108cc:	c52a                	sw	a0,136(sp)
420108ce:	c902                	sw	zero,144(sp)
420108d0:	cb02                	sw	zero,148(sp)
420108d2:	cd02                	sw	zero,152(sp)
420108d4:	cf02                	sw	zero,156(sp)
420108d6:	d102                	sw	zero,160(sp)
420108d8:	d302                	sw	zero,164(sp)
420108da:	d502                	sw	zero,168(sp)
420108dc:	d702                	sw	zero,172(sp)
420108de:	c14a                	sw	s2,128(sp)
420108e0:	c35e                	sw	s7,132(sp)
420108e2:	c72e                	sw	a1,140(sp)
420108e4:	478d                	li	a5,3
420108e6:	3afb8763          	beq	s7,a5,42010c94 <decoder_task+0x522>
420108ea:	4789                	li	a5,2
420108ec:	4afb8b63          	beq	s7,a5,42010da2 <decoder_task+0x630>
420108f0:	640d                	lui	s0,0x3
420108f2:	008afae3          	bgeu	s5,s0,42011106 <decoder_task+0x994>
420108f6:	85a2                	mv	a1,s0
420108f8:	8552                	mv	a0,s4
420108fa:	bf3f70ef          	jal	420084ec <realloc>
420108fe:	000509e3          	beqz	a0,42011110 <decoder_task+0x99e>
42010902:	d682                	sw	zero,108(sp)
42010904:	d882                	sw	zero,112(sp)
42010906:	da82                	sw	zero,116(sp)
42010908:	8a2a                	mv	s4,a0
4201090a:	8aa2                	mv	s5,s0
4201090c:	4791                	li	a5,4
4201090e:	7cfb8763          	beq	s7,a5,420110dc <decoder_task+0x96a>
42010912:	203357b7          	lui	a5,0x20335
42010916:	04d78793          	addi	a5,a5,77 # 2033504d <CSR_UINTSTATUS+0x2033439c>
4201091a:	086c                	addi	a1,sp,28
4201091c:	10a8                	addi	a0,sp,104
4201091e:	d4be                	sw	a5,104(sp)
42010920:	11a150ef          	jal	42025a3a <__wrap_esp_audio_simple_dec_open>
42010924:	842a                	mv	s0,a0
42010926:	7c050763          	beqz	a0,420110f4 <decoder_task+0x982>
4201092a:	fe378097          	auipc	ra,0xfe378
4201092e:	a90080e7          	jalr	-1392(ra) # 403883ba <esp_log_timestamp>
42010932:	3c1267b7          	lui	a5,0x3c126
42010936:	4985                	li	s3,1
42010938:	86aa                	mv	a3,a0
4201093a:	80078793          	addi	a5,a5,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
4201093e:	0d3b99e3          	bne	s7,s3,42011210 <decoder_task+0xa9e>
42010942:	3c126737          	lui	a4,0x3c126
42010946:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
4201094a:	3c126637          	lui	a2,0x3c126
4201094e:	85ba                	mv	a1,a4
42010950:	8822                	mv	a6,s0
42010952:	a9c60613          	addi	a2,a2,-1380 # 3c125a9c <_esp_trace_encoder_array_end+0x597c>
42010956:	4505                	li	a0,1
42010958:	fe378097          	auipc	ra,0xfe378
4201095c:	95a080e7          	jalr	-1702(ra) # 403882b2 <esp_log>
42010960:	3c126737          	lui	a4,0x3c126
42010964:	57f9                	li	a5,-2
42010966:	9d470693          	addi	a3,a4,-1580 # 3c1259d4 <_esp_trace_encoder_array_end+0x58b4>
4201096a:	26f405e3          	beq	s0,a5,420113d4 <decoder_task+0xc62>
4201096e:	3fc957b7          	lui	a5,0x3fc95
42010972:	3047a503          	lw	a0,772(a5) # 3fc95304 <s_state>
42010976:	4601                	li	a2,0
42010978:	85ca                	mv	a1,s2
4201097a:	75e040ef          	jal	420150d8 <native_state_set_audio>
4201097e:	4572                	lw	a0,28(sp)
42010980:	c501                	beqz	a0,42010988 <decoder_task+0x216>
42010982:	7a1250ef          	jal	42036922 <esp_audio_simple_dec_close>
42010986:	ce02                	sw	zero,28(sp)
42010988:	8552                	mv	a0,s4
4201098a:	b67f70ef          	jal	420084f0 <cfree>
4201098e:	8cca                	mv	s9,s2
42010990:	4a81                	li	s5,0
42010992:	4a01                	li	s4,0
42010994:	4c01                	li	s8,0
42010996:	4d81                	li	s11,0
42010998:	3fc957b7          	lui	a5,0x3fc95
4201099c:	2fc7a503          	lw	a0,764(a5) # 3fc952fc <s_encoded>
420109a0:	85a6                	mv	a1,s1
420109a2:	4981                	li	s3,0
420109a4:	2e1650ef          	jal	42076484 <vRingbufferReturnItem>
420109a8:	4401                	li	s0,0
420109aa:	b53d                	j	420107d8 <decoder_task+0x66>
420109ac:	393010ef          	jal	4201253e <decoder_register_codecs>
420109b0:	842a                	mv	s0,a0
420109b2:	26051c63          	bnez	a0,42010c2a <decoder_task+0x4b8>
420109b6:	409c                	lw	a5,0(s1)
420109b8:	ed2799e3          	bne	a5,s2,4201088a <decoder_task+0x118>
420109bc:	40dc                	lw	a5,4(s1)
420109be:	ed7796e3          	bne	a5,s7,4201088a <decoder_task+0x118>
420109c2:	478d                	li	a5,3
420109c4:	7cfb8163          	beq	s7,a5,42011186 <decoder_task+0xa14>
420109c8:	47f2                	lw	a5,28(sp)
420109ca:	00f9e7b3          	or	a5,s3,a5
420109ce:	d7e9                	beqz	a5,42010998 <decoder_task+0x226>
420109d0:	0084d703          	lhu	a4,8(s1)
420109d4:	00b48793          	addi	a5,s1,11
420109d8:	ce82                	sw	zero,92(sp)
420109da:	cabe                	sw	a5,84(sp)
420109dc:	d082                	sw	zero,96(sp)
420109de:	d282                	sw	zero,100(sp)
420109e0:	ccba                	sw	a4,88(sp)
420109e2:	00a4c783          	lbu	a5,10(s1)
420109e6:	ffeb8693          	addi	a3,s7,-2
420109ea:	0016b693          	seqz	a3,a3
420109ee:	c636                	sw	a3,12(sp)
420109f0:	00f036b3          	snez	a3,a5
420109f4:	04d10e23          	sb	a3,92(sp)
420109f8:	4c098363          	beqz	s3,42010ebe <decoder_task+0x74c>
420109fc:	e319                	bnez	a4,42010a02 <decoder_task+0x290>
420109fe:	42078063          	beqz	a5,42010e1e <decoder_task+0x6ac>
42010a02:	4781                	li	a5,0
42010a04:	4801                	li	a6,0
42010a06:	de3e                	sw	a5,60(sp)
42010a08:	c0c2                	sw	a6,64(sp)
42010a0a:	da52                	sw	s4,52(sp)
42010a0c:	dc56                	sw	s5,56(sp)
42010a0e:	d082                	sw	zero,96(sp)
42010a10:	fe371097          	auipc	ra,0xfe371
42010a14:	92a080e7          	jalr	-1750(ra) # 4038133a <esp_timer_get_time>
42010a18:	8d2a                	mv	s10,a0
42010a1a:	1850                	addi	a2,sp,52
42010a1c:	08cc                	addi	a1,sp,84
42010a1e:	854e                	mv	a0,s3
42010a20:	3b7010ef          	jal	420125d6 <native_aac_decoder_process>
42010a24:	842a                	mv	s0,a0
42010a26:	fe371097          	auipc	ra,0xfe371
42010a2a:	914080e7          	jalr	-1772(ra) # 4038133a <esp_timer_get_time>
42010a2e:	47ca                	lw	a5,144(sp)
42010a30:	46da                	lw	a3,148(sp)
42010a32:	41a50533          	sub	a0,a0,s10
42010a36:	00a78733          	add	a4,a5,a0
42010a3a:	00f737b3          	sltu	a5,a4,a5
42010a3e:	97b6                	add	a5,a5,a3
42010a40:	cb3e                	sw	a5,148(sp)
42010a42:	578a                	lw	a5,160(sp)
42010a44:	c93a                	sw	a4,144(sp)
42010a46:	571a                	lw	a4,164(sp)
42010a48:	0785                	addi	a5,a5,1
42010a4a:	d13e                	sw	a5,160(sp)
42010a4c:	00a77363          	bgeu	a4,a0,42010a52 <decoder_task+0x2e0>
42010a50:	d32a                	sw	a0,164(sp)
42010a52:	8bfd                	andi	a5,a5,31
42010a54:	3a078963          	beqz	a5,42010e06 <decoder_task+0x694>
42010a58:	2f0b0793          	addi	a5,s6,752
42010a5c:	0330000f          	fence	rw,rw
42010a60:	439c                	lw	a5,0(a5)
42010a62:	0230000f          	fence	r,rw
42010a66:	3b279c63          	bne	a5,s2,42010e1e <decoder_task+0x6ac>
42010a6a:	57e1                	li	a5,-8
42010a6c:	36f40763          	beq	s0,a5,42010dda <decoder_task+0x668>
42010a70:	3a041d63          	bnez	s0,42010e2a <decoder_task+0x6b8>
42010a74:	5786                	lw	a5,96(sp)
42010a76:	4766                	lw	a4,88(sp)
42010a78:	72f76863          	bltu	a4,a5,420111a8 <decoder_task+0xa36>
42010a7c:	8f1d                	sub	a4,a4,a5
42010a7e:	56aa                	lw	a3,168(sp)
42010a80:	ccba                	sw	a4,88(sp)
42010a82:	4756                	lw	a4,84(sp)
42010a84:	96be                	add	a3,a3,a5
42010a86:	d536                	sw	a3,168(sp)
42010a88:	97ba                	add	a5,a5,a4
42010a8a:	4706                	lw	a4,64(sp)
42010a8c:	cabe                	sw	a5,84(sp)
42010a8e:	10070f63          	beqz	a4,42010bac <decoder_task+0x43a>
42010a92:	00cc                	addi	a1,sp,68
42010a94:	854e                	mv	a0,s3
42010a96:	c282                	sw	zero,68(sp)
42010a98:	c482                	sw	zero,72(sp)
42010a9a:	c682                	sw	zero,76(sp)
42010a9c:	c882                	sw	zero,80(sp)
42010a9e:	661010ef          	jal	420128fe <native_aac_decoder_get_info>
42010aa2:	38051163          	bnez	a0,42010e24 <decoder_task+0x6b2>
42010aa6:	47b2                	lw	a5,12(sp)
42010aa8:	01b10613          	addi	a2,sp,27
42010aac:	00cc                	addi	a1,sp,68
42010aae:	854e                	mv	a0,s3
42010ab0:	00f10da3          	sb	a5,27(sp)
42010ab4:	659010ef          	jal	4201290c <native_aac_decoder_label>
42010ab8:	01b14683          	lbu	a3,27(sp)
42010abc:	842a                	mv	s0,a0
42010abe:	4501                	li	a0,0
42010ac0:	60068663          	beqz	a3,420110cc <decoder_task+0x95a>
42010ac4:	2f0b0793          	addi	a5,s6,752
42010ac8:	0330000f          	fence	rw,rw
42010acc:	4398                	lw	a4,0(a5)
42010ace:	0230000f          	fence	r,rw
42010ad2:	4781                	li	a5,0
42010ad4:	07271163          	bne	a4,s2,42010b36 <decoder_task+0x3c4>
42010ad8:	4716                	lw	a4,68(sp)
42010ada:	cf31                	beqz	a4,42010b36 <decoder_task+0x3c4>
42010adc:	04914803          	lbu	a6,73(sp)
42010ae0:	04080b63          	beqz	a6,42010b36 <decoder_task+0x3c4>
42010ae4:	04814603          	lbu	a2,72(sp)
42010ae8:	c639                	beqz	a2,42010b36 <decoder_task+0x3c4>
42010aea:	45a6                	lw	a1,72(sp)
42010aec:	47b6                	lw	a5,76(sp)
42010aee:	d23a                	sw	a4,36(sp)
42010af0:	d42e                	sw	a1,40(sp)
42010af2:	45c6                	lw	a1,80(sp)
42010af4:	d63e                	sw	a5,44(sp)
42010af6:	4785                	li	a5,1
42010af8:	06012923          	sw	zero,114(sp)
42010afc:	06012b23          	sw	zero,118(sp)
42010b00:	06011d23          	sh	zero,122(sp)
42010b04:	d4a2                	sw	s0,104(sp)
42010b06:	d6ba                	sw	a4,108(sp)
42010b08:	d82e                	sw	a1,48(sp)
42010b0a:	00f10d23          	sb	a5,26(sp)
42010b0e:	70050763          	beqz	a0,4201121c <decoder_task+0xaaa>
42010b12:	3fc957b7          	lui	a5,0x3fc95
42010b16:	06a10823          	sb	a0,112(sp)
42010b1a:	3047a503          	lw	a0,772(a5) # 3fc95304 <s_state>
42010b1e:	06c108a3          	sb	a2,113(sp)
42010b22:	85ca                	mv	a1,s2
42010b24:	10b0                	addi	a2,sp,104
42010b26:	daba                	sw	a4,116(sp)
42010b28:	07010c23          	sb	a6,120(sp)
42010b2c:	06d10d23          	sb	a3,122(sp)
42010b30:	688040ef          	jal	420151b8 <native_state_set_stream_info>
42010b34:	4785                	li	a5,1
42010b36:	45b6                	lw	a1,76(sp)
42010b38:	854a                	mv	a0,s2
42010b3a:	00f10d23          	sb	a5,26(sp)
42010b3e:	81fff0ef          	jal	4201035c <state_set_decoder_bitrate>
42010b42:	01a14783          	lbu	a5,26(sp)
42010b46:	c3bd                	beqz	a5,42010bac <decoder_task+0x43a>
42010b48:	360d8463          	beqz	s11,42010eb0 <decoder_task+0x73e>
42010b4c:	02814503          	lbu	a0,40(sp)
42010b50:	02914783          	lbu	a5,41(sp)
42010b54:	4406                	lw	s0,64(sp)
42010b56:	051d                	addi	a0,a0,7
42010b58:	810d                	srli	a0,a0,0x3
42010b5a:	02f50533          	mul	a0,a0,a5
42010b5e:	cd15                	beqz	a0,42010b9a <decoder_task+0x428>
42010b60:	5612                	lw	a2,36(sp)
42010b62:	ce05                	beqz	a2,42010b9a <decoder_task+0x428>
42010b64:	02a45533          	divu	a0,s0,a0
42010b68:	000f47b7          	lui	a5,0xf4
42010b6c:	24078793          	addi	a5,a5,576 # f4240 <CSR_UINTSTATUS+0xf358f>
42010b70:	4681                	li	a3,0
42010b72:	02f535b3          	mulhu	a1,a0,a5
42010b76:	02f50533          	mul	a0,a0,a5
42010b7a:	fdff0097          	auipc	ra,0xfdff0
42010b7e:	d32080e7          	jalr	-718(ra) # 400008ac <__udivdi3>
42010b82:	47ea                	lw	a5,152(sp)
42010b84:	46fa                	lw	a3,156(sp)
42010b86:	573a                	lw	a4,172(sp)
42010b88:	953e                	add	a0,a0,a5
42010b8a:	96ae                	add	a3,a3,a1
42010b8c:	00f537b3          	sltu	a5,a0,a5
42010b90:	97b6                	add	a5,a5,a3
42010b92:	9722                	add	a4,a4,s0
42010b94:	cf3e                	sw	a5,156(sp)
42010b96:	cd2a                	sw	a0,152(sp)
42010b98:	d73a                	sw	a4,172(sp)
42010b9a:	86a2                	mv	a3,s0
42010b9c:	8652                	mv	a2,s4
42010b9e:	104c                	addi	a1,sp,36
42010ba0:	854a                	mv	a0,s2
42010ba2:	e74ff0ef          	jal	42010216 <send_pcm>
42010ba6:	8daa                	mv	s11,a0
42010ba8:	78050263          	beqz	a0,4201132c <decoder_task+0xbba>
42010bac:	fe370097          	auipc	ra,0xfe370
42010bb0:	78e080e7          	jalr	1934(ra) # 4038133a <esp_timer_get_time>
42010bb4:	862e                	mv	a2,a1
42010bb6:	85aa                	mv	a1,a0
42010bb8:	0108                	addi	a0,sp,128
42010bba:	a80ff0ef          	jal	4200fe3a <decode_stats_report>
42010bbe:	5786                	lw	a5,96(sp)
42010bc0:	4706                	lw	a4,64(sp)
42010bc2:	8fd9                	or	a5,a5,a4
42010bc4:	e789                	bnez	a5,42010bce <decoder_task+0x45c>
42010bc6:	05c14783          	lbu	a5,92(sp)
42010bca:	7a078363          	beqz	a5,42011370 <decoder_task+0xbfe>
42010bce:	00a4c783          	lbu	a5,10(s1)
42010bd2:	2a079e63          	bnez	a5,42010e8e <decoder_task+0x71c>
42010bd6:	4766                	lw	a4,88(sp)
42010bd8:	e20715e3          	bnez	a4,42010a02 <decoder_task+0x290>
42010bdc:	2a079963          	bnez	a5,42010e8e <decoder_task+0x71c>
42010be0:	2b2c8763          	beq	s9,s2,42010e8e <decoder_task+0x71c>
42010be4:	8526                	mv	a0,s1
42010be6:	85e6                	mv	a1,s9
42010be8:	ae9ff0ef          	jal	420106d0 <return_decoded_packet>
42010bec:	4401                	li	s0,0
42010bee:	2f0b0793          	addi	a5,s6,752
42010bf2:	0330000f          	fence	rw,rw
42010bf6:	4384                	lw	s1,0(a5)
42010bf8:	0230000f          	fence	r,rw
42010bfc:	bf2497e3          	bne	s1,s2,420107ea <decoder_task+0x78>
42010c00:	c40c83e3          	beqz	s9,42010846 <decoder_task+0xd4>
42010c04:	c52c91e3          	bne	s9,s2,42010846 <decoder_task+0xd4>
42010c08:	4572                	lw	a0,28(sp)
42010c0a:	c119                	beqz	a0,42010c10 <decoder_task+0x49e>
42010c0c:	517250ef          	jal	42036922 <esp_audio_simple_dec_close>
42010c10:	ce02                	sw	zero,28(sp)
42010c12:	00098563          	beqz	s3,42010c1c <decoder_task+0x4aa>
42010c16:	854e                	mv	a0,s3
42010c18:	189010ef          	jal	420125a0 <native_aac_decoder_destroy>
42010c1c:	8552                	mv	a0,s4
42010c1e:	8d3f70ef          	jal	420084f0 <cfree>
42010c22:	4981                	li	s3,0
42010c24:	4a81                	li	s5,0
42010c26:	4a01                	li	s4,0
42010c28:	b939                	j	42010846 <decoder_task+0xd4>
42010c2a:	fe377097          	auipc	ra,0xfe377
42010c2e:	790080e7          	jalr	1936(ra) # 403883ba <esp_log_timestamp>
42010c32:	3c126737          	lui	a4,0x3c126
42010c36:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
42010c3a:	3c126637          	lui	a2,0x3c126
42010c3e:	86aa                	mv	a3,a0
42010c40:	85ba                	mv	a1,a4
42010c42:	87a2                	mv	a5,s0
42010c44:	9f460613          	addi	a2,a2,-1548 # 3c1259f4 <_esp_trace_encoder_array_end+0x58d4>
42010c48:	4505                	li	a0,1
42010c4a:	fe377097          	auipc	ra,0xfe377
42010c4e:	668080e7          	jalr	1640(ra) # 403882b2 <esp_log>
42010c52:	3fc957b7          	lui	a5,0x3fc95
42010c56:	3047a503          	lw	a0,772(a5) # 3fc95304 <s_state>
42010c5a:	408c                	lw	a1,0(s1)
42010c5c:	3c1267b7          	lui	a5,0x3c126
42010c60:	a2478693          	addi	a3,a5,-1500 # 3c125a24 <_esp_trace_encoder_array_end+0x5904>
42010c64:	4601                	li	a2,0
42010c66:	472040ef          	jal	420150d8 <native_state_set_audio>
42010c6a:	0004ac83          	lw	s9,0(s1)
42010c6e:	8526                	mv	a0,s1
42010c70:	85e6                	mv	a1,s9
42010c72:	a5fff0ef          	jal	420106d0 <return_decoded_packet>
42010c76:	b68d                	j	420107d8 <decoder_task+0x66>
42010c78:	3fc957b7          	lui	a5,0x3fc95
42010c7c:	2fc7a503          	lw	a0,764(a5) # 3fc952fc <s_encoded>
42010c80:	85a6                	mv	a1,s1
42010c82:	003650ef          	jal	42076484 <vRingbufferReturnItem>
42010c86:	be89                	j	420107d8 <decoder_task+0x66>
42010c88:	8552                	mv	a0,s4
42010c8a:	867f70ef          	jal	420084f0 <cfree>
42010c8e:	4a81                	li	s5,0
42010c90:	4a01                	li	s4,0
42010c92:	b669                	j	4201081c <decoder_task+0xaa>
42010c94:	8552                	mv	a0,s4
42010c96:	85bf70ef          	jal	420084f0 <cfree>
42010c9a:	115230ef          	jal	420345ae <custom_flac_decoder_create>
42010c9e:	8c2a                	mv	s8,a0
42010ca0:	60050463          	beqz	a0,420112a8 <decoder_task+0xb36>
42010ca4:	4981                	li	s3,0
42010ca6:	4a81                	li	s5,0
42010ca8:	4a01                	li	s4,0
42010caa:	4d81                	li	s11,0
42010cac:	4661                	li	a2,24
42010cae:	4581                	li	a1,0
42010cb0:	10a8                	addi	a0,sp,104
42010cb2:	fdfef097          	auipc	ra,0xfdfef
42010cb6:	6a2080e7          	jalr	1698(ra) # 40000354 <memset>
42010cba:	011c                	addi	a5,sp,128
42010cbc:	ccbe                	sw	a5,88(sp)
42010cbe:	105c                	addi	a5,sp,36
42010cc0:	cebe                	sw	a5,92(sp)
42010cc2:	01a10793          	addi	a5,sp,26
42010cc6:	d0be                	sw	a5,96(sp)
42010cc8:	caca                	sw	s2,84(sp)
42010cca:	00a4c683          	lbu	a3,10(s1)
42010cce:	0084d603          	lhu	a2,8(s1)
42010cd2:	42011737          	lui	a4,0x42011
42010cd6:	00d036b3          	snez	a3,a3
42010cda:	08dc                	addi	a5,sp,84
42010cdc:	40870713          	addi	a4,a4,1032 # 42011408 <custom_flac_output>
42010ce0:	00b48593          	addi	a1,s1,11
42010ce4:	06810813          	addi	a6,sp,104
42010ce8:	8562                	mv	a0,s8
42010cea:	14b230ef          	jal	42034634 <custom_flac_decoder_feed>
42010cee:	47ca                	lw	a5,144(sp)
42010cf0:	5726                	lw	a4,104(sp)
42010cf2:	465a                	lw	a2,148(sp)
42010cf4:	55b6                	lw	a1,108(sp)
42010cf6:	568a                	lw	a3,160(sp)
42010cf8:	973e                	add	a4,a4,a5
42010cfa:	842a                	mv	s0,a0
42010cfc:	5546                	lw	a0,112(sp)
42010cfe:	962e                	add	a2,a2,a1
42010d00:	00f737b3          	sltu	a5,a4,a5
42010d04:	97b2                	add	a5,a5,a2
42010d06:	55d6                	lw	a1,116(sp)
42010d08:	561a                	lw	a2,164(sp)
42010d0a:	96aa                	add	a3,a3,a0
42010d0c:	c93a                	sw	a4,144(sp)
42010d0e:	cb3e                	sw	a5,148(sp)
42010d10:	d136                	sw	a3,160(sp)
42010d12:	00b67363          	bgeu	a2,a1,42010d18 <decoder_task+0x5a6>
42010d16:	d32e                	sw	a1,164(sp)
42010d18:	57aa                	lw	a5,168(sp)
42010d1a:	5766                	lw	a4,120(sp)
42010d1c:	97ba                	add	a5,a5,a4
42010d1e:	d53e                	sw	a5,168(sp)
42010d20:	500d8063          	beqz	s11,42011220 <decoder_task+0xaae>
42010d24:	4d85                	li	s11,1
42010d26:	fe370097          	auipc	ra,0xfe370
42010d2a:	614080e7          	jalr	1556(ra) # 4038133a <esp_timer_get_time>
42010d2e:	862e                	mv	a2,a1
42010d30:	85aa                	mv	a1,a0
42010d32:	0108                	addi	a0,sp,128
42010d34:	906ff0ef          	jal	4200fe3a <decode_stats_report>
42010d38:	44045963          	bgez	s0,4201118a <decoder_task+0xa18>
42010d3c:	2f0b0793          	addi	a5,s6,752
42010d40:	0330000f          	fence	rw,rw
42010d44:	439c                	lw	a5,0(a5)
42010d46:	0230000f          	fence	r,rw
42010d4a:	45279063          	bne	a5,s2,4201118a <decoder_task+0xa18>
42010d4e:	fe377097          	auipc	ra,0xfe377
42010d52:	66c080e7          	jalr	1644(ra) # 403883ba <esp_log_timestamp>
42010d56:	3c126737          	lui	a4,0x3c126
42010d5a:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
42010d5e:	3c126637          	lui	a2,0x3c126
42010d62:	86aa                	mv	a3,a0
42010d64:	87a2                	mv	a5,s0
42010d66:	85ba                	mv	a1,a4
42010d68:	adc60613          	addi	a2,a2,-1316 # 3c125adc <_esp_trace_encoder_array_end+0x59bc>
42010d6c:	4509                	li	a0,2
42010d6e:	fe377097          	auipc	ra,0xfe377
42010d72:	544080e7          	jalr	1348(ra) # 403882b2 <esp_log>
42010d76:	3c126737          	lui	a4,0x3c126
42010d7a:	0419                	addi	s0,s0,6 # 3006 <CSR_UINTSTATUS+0x2355>
42010d7c:	4785                	li	a5,1
42010d7e:	9e470693          	addi	a3,a4,-1564 # 3c1259e4 <_esp_trace_encoder_array_end+0x58c4>
42010d82:	0087e663          	bltu	a5,s0,42010d8e <decoder_task+0x61c>
42010d86:	3c1267b7          	lui	a5,0x3c126
42010d8a:	9c878693          	addi	a3,a5,-1592 # 3c1259c8 <_esp_trace_encoder_array_end+0x58a8>
42010d8e:	3fc957b7          	lui	a5,0x3fc95
42010d92:	3047a503          	lw	a0,772(a5) # 3fc95304 <s_state>
42010d96:	4601                	li	a2,0
42010d98:	85ca                	mv	a1,s2
42010d9a:	33e040ef          	jal	420150d8 <native_state_set_audio>
42010d9e:	8cca                	mv	s9,s2
42010da0:	a6ed                	j	4201118a <decoder_task+0xa18>
42010da2:	6789                	lui	a5,0x2
42010da4:	34fa8f63          	beq	s5,a5,42011102 <decoder_task+0x990>
42010da8:	6589                	lui	a1,0x2
42010daa:	8552                	mv	a0,s4
42010dac:	f40f70ef          	jal	420084ec <realloc>
42010db0:	842a                	mv	s0,a0
42010db2:	64050163          	beqz	a0,420113f4 <decoder_task+0xc82>
42010db6:	204347b7          	lui	a5,0x20434
42010dba:	14178793          	addi	a5,a5,321 # 20434141 <CSR_UINTSTATUS+0x20433490>
42010dbe:	d682                	sw	zero,108(sp)
42010dc0:	d882                	sw	zero,112(sp)
42010dc2:	da82                	sw	zero,116(sp)
42010dc4:	d4be                	sw	a5,104(sp)
42010dc6:	7ae010ef          	jal	42012574 <native_aac_decoder_create>
42010dca:	89aa                	mv	s3,a0
42010dcc:	46050563          	beqz	a0,42011236 <decoder_task+0xac4>
42010dd0:	8a22                	mv	s4,s0
42010dd2:	6a89                	lui	s5,0x2
42010dd4:	4c01                	li	s8,0
42010dd6:	4d81                	li	s11,0
42010dd8:	bee5                	j	420109d0 <decoder_task+0x25e>
42010dda:	5706                	lw	a4,96(sp)
42010ddc:	47d6                	lw	a5,84(sp)
42010dde:	56aa                	lw	a3,168(sp)
42010de0:	5472                	lw	s0,60(sp)
42010de2:	97ba                	add	a5,a5,a4
42010de4:	cabe                	sw	a5,84(sp)
42010de6:	47e6                	lw	a5,88(sp)
42010de8:	96ba                	add	a3,a3,a4
42010dea:	d536                	sw	a3,168(sp)
42010dec:	8f99                	sub	a5,a5,a4
42010dee:	ccbe                	sw	a5,88(sp)
42010df0:	528af063          	bgeu	s5,s0,42011310 <decoder_task+0xb9e>
42010df4:	85a2                	mv	a1,s0
42010df6:	8552                	mv	a0,s4
42010df8:	ef4f70ef          	jal	420084ec <realloc>
42010dfc:	50050a63          	beqz	a0,42011310 <decoder_task+0xb9e>
42010e00:	8aa2                	mv	s5,s0
42010e02:	8a2a                	mv	s4,a0
42010e04:	befd                	j	42010a02 <decoder_task+0x290>
42010e06:	4505                	li	a0,1
42010e08:	5eeff0ef          	jal	421103f6 <vTaskDelay>
42010e0c:	2f0b0793          	addi	a5,s6,752
42010e10:	0330000f          	fence	rw,rw
42010e14:	439c                	lw	a5,0(a5)
42010e16:	0230000f          	fence	r,rw
42010e1a:	c52788e3          	beq	a5,s2,42010a6a <decoder_task+0x2f8>
42010e1e:	00a4c783          	lbu	a5,10(s1)
42010e22:	bb6d                	j	42010bdc <decoder_task+0x46a>
42010e24:	00010d23          	sb	zero,26(sp)
42010e28:	b351                	j	42010bac <decoder_task+0x43a>
42010e2a:	4a89                	li	s5,2
42010e2c:	fe377097          	auipc	ra,0xfe377
42010e30:	58e080e7          	jalr	1422(ra) # 403883ba <esp_log_timestamp>
42010e34:	475b8063          	beq	s7,s5,42011294 <decoder_task+0xb22>
42010e38:	4791                	li	a5,4
42010e3a:	52fb8163          	beq	s7,a5,4201135c <decoder_task+0xbea>
42010e3e:	3c1267b7          	lui	a5,0x3c126
42010e42:	4705                	li	a4,1
42010e44:	80078793          	addi	a5,a5,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
42010e48:	00eb8663          	beq	s7,a4,42010e54 <decoder_task+0x6e2>
42010e4c:	3c1267b7          	lui	a5,0x3c126
42010e50:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
42010e54:	3c126737          	lui	a4,0x3c126
42010e58:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
42010e5c:	3c126637          	lui	a2,0x3c126
42010e60:	86aa                	mv	a3,a0
42010e62:	85ba                	mv	a1,a4
42010e64:	8822                	mv	a6,s0
42010e66:	b3c60613          	addi	a2,a2,-1220 # 3c125b3c <_esp_trace_encoder_array_end+0x5a1c>
42010e6a:	4509                	li	a0,2
42010e6c:	fe377097          	auipc	ra,0xfe377
42010e70:	446080e7          	jalr	1094(ra) # 403882b2 <esp_log>
42010e74:	3fc957b7          	lui	a5,0x3fc95
42010e78:	3047a503          	lw	a0,772(a5) # 3fc95304 <s_state>
42010e7c:	3c1267b7          	lui	a5,0x3c126
42010e80:	9e478693          	addi	a3,a5,-1564 # 3c1259e4 <_esp_trace_encoder_array_end+0x58c4>
42010e84:	85ca                	mv	a1,s2
42010e86:	4601                	li	a2,0
42010e88:	250040ef          	jal	420150d8 <native_state_set_audio>
42010e8c:	8cca                	mv	s9,s2
42010e8e:	4572                	lw	a0,28(sp)
42010e90:	c119                	beqz	a0,42010e96 <decoder_task+0x724>
42010e92:	291250ef          	jal	42036922 <esp_audio_simple_dec_close>
42010e96:	ce02                	sw	zero,28(sp)
42010e98:	00098563          	beqz	s3,42010ea2 <decoder_task+0x730>
42010e9c:	854e                	mv	a0,s3
42010e9e:	702010ef          	jal	420125a0 <native_aac_decoder_destroy>
42010ea2:	8552                	mv	a0,s4
42010ea4:	e4cf70ef          	jal	420084f0 <cfree>
42010ea8:	4981                	li	s3,0
42010eaa:	4a81                	li	s5,0
42010eac:	4a01                	li	s4,0
42010eae:	bb1d                	j	42010be4 <decoder_task+0x472>
42010eb0:	3c1267b7          	lui	a5,0x3c126
42010eb4:	b0878513          	addi	a0,a5,-1272 # 3c125b08 <_esp_trace_encoder_array_end+0x59e8>
42010eb8:	afaff0ef          	jal	420101b2 <log_runtime_memory>
42010ebc:	b941                	j	42010b4c <decoder_task+0x3da>
42010ebe:	e311                	bnez	a4,42010ec2 <decoder_task+0x750>
42010ec0:	dfb9                	beqz	a5,42010e1e <decoder_task+0x6ac>
42010ec2:	4781                	li	a5,0
42010ec4:	4801                	li	a6,0
42010ec6:	de3e                	sw	a5,60(sp)
42010ec8:	c0c2                	sw	a6,64(sp)
42010eca:	da52                	sw	s4,52(sp)
42010ecc:	dc56                	sw	s5,56(sp)
42010ece:	d082                	sw	zero,96(sp)
42010ed0:	fe370097          	auipc	ra,0xfe370
42010ed4:	46a080e7          	jalr	1130(ra) # 4038133a <esp_timer_get_time>
42010ed8:	8d2a                	mv	s10,a0
42010eda:	4572                	lw	a0,28(sp)
42010edc:	1850                	addi	a2,sp,52
42010ede:	08cc                	addi	a1,sp,84
42010ee0:	4e7140ef          	jal	42025bc6 <__wrap_esp_audio_simple_dec_process>
42010ee4:	842a                	mv	s0,a0
42010ee6:	fe370097          	auipc	ra,0xfe370
42010eea:	454080e7          	jalr	1108(ra) # 4038133a <esp_timer_get_time>
42010eee:	47ca                	lw	a5,144(sp)
42010ef0:	46da                	lw	a3,148(sp)
42010ef2:	41a50533          	sub	a0,a0,s10
42010ef6:	00a78733          	add	a4,a5,a0
42010efa:	00f737b3          	sltu	a5,a4,a5
42010efe:	97b6                	add	a5,a5,a3
42010f00:	cb3e                	sw	a5,148(sp)
42010f02:	578a                	lw	a5,160(sp)
42010f04:	c93a                	sw	a4,144(sp)
42010f06:	571a                	lw	a4,164(sp)
42010f08:	0785                	addi	a5,a5,1
42010f0a:	d13e                	sw	a5,160(sp)
42010f0c:	00a77363          	bgeu	a4,a0,42010f12 <decoder_task+0x7a0>
42010f10:	d32a                	sw	a0,164(sp)
42010f12:	8bfd                	andi	a5,a5,31
42010f14:	1a078563          	beqz	a5,420110be <decoder_task+0x94c>
42010f18:	2f0b0793          	addi	a5,s6,752
42010f1c:	0330000f          	fence	rw,rw
42010f20:	439c                	lw	a5,0(a5)
42010f22:	0230000f          	fence	r,rw
42010f26:	ef279ce3          	bne	a5,s2,42010e1e <decoder_task+0x6ac>
42010f2a:	57e1                	li	a5,-8
42010f2c:	16f40d63          	beq	s0,a5,420110a6 <decoder_task+0x934>
42010f30:	ee041de3          	bnez	s0,42010e2a <decoder_task+0x6b8>
42010f34:	5786                	lw	a5,96(sp)
42010f36:	4766                	lw	a4,88(sp)
42010f38:	26f76863          	bltu	a4,a5,420111a8 <decoder_task+0xa36>
42010f3c:	8f1d                	sub	a4,a4,a5
42010f3e:	56aa                	lw	a3,168(sp)
42010f40:	ccba                	sw	a4,88(sp)
42010f42:	4756                	lw	a4,84(sp)
42010f44:	96be                	add	a3,a3,a5
42010f46:	d536                	sw	a3,168(sp)
42010f48:	97ba                	add	a5,a5,a4
42010f4a:	4706                	lw	a4,64(sp)
42010f4c:	cabe                	sw	a5,84(sp)
42010f4e:	12070363          	beqz	a4,42011074 <decoder_task+0x902>
42010f52:	4572                	lw	a0,28(sp)
42010f54:	00cc                	addi	a1,sp,68
42010f56:	c282                	sw	zero,68(sp)
42010f58:	c482                	sw	zero,72(sp)
42010f5a:	c682                	sw	zero,76(sp)
42010f5c:	c882                	sw	zero,80(sp)
42010f5e:	14d250ef          	jal	420368aa <esp_audio_simple_dec_get_info>
42010f62:	16051263          	bnez	a0,420110c6 <decoder_task+0x954>
42010f66:	47b2                	lw	a5,12(sp)
42010f68:	00f10da3          	sb	a5,27(sp)
42010f6c:	4789                	li	a5,2
42010f6e:	38fb8763          	beq	s7,a5,420112fc <decoder_task+0xb8a>
42010f72:	4791                	li	a5,4
42010f74:	36fb8f63          	beq	s7,a5,420112f2 <decoder_task+0xb80>
42010f78:	3c126737          	lui	a4,0x3c126
42010f7c:	4785                	li	a5,1
42010f7e:	80070593          	addi	a1,a4,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
42010f82:	2efb9963          	bne	s7,a5,42011274 <decoder_task+0xb02>
42010f86:	2f0b0793          	addi	a5,s6,752
42010f8a:	0330000f          	fence	rw,rw
42010f8e:	439c                	lw	a5,0(a5)
42010f90:	0230000f          	fence	r,rw
42010f94:	07279463          	bne	a5,s2,42010ffc <decoder_task+0x88a>
42010f98:	4796                	lw	a5,68(sp)
42010f9a:	c3b5                	beqz	a5,42010ffe <decoder_task+0x88c>
42010f9c:	04914683          	lbu	a3,73(sp)
42010fa0:	ceb1                	beqz	a3,42010ffc <decoder_task+0x88a>
42010fa2:	04815703          	lhu	a4,72(sp)
42010fa6:	04814503          	lbu	a0,72(sp)
42010faa:	00875613          	srli	a2,a4,0x8
42010fae:	0722                	slli	a4,a4,0x8
42010fb0:	963a                	add	a2,a2,a4
42010fb2:	c529                	beqz	a0,42010ffc <decoder_task+0x88a>
42010fb4:	06012b23          	sw	zero,118(sp)
42010fb8:	06012923          	sw	zero,114(sp)
42010fbc:	d23e                	sw	a5,36(sp)
42010fbe:	06c11823          	sh	a2,112(sp)
42010fc2:	d6be                	sw	a5,108(sp)
42010fc4:	4626                	lw	a2,72(sp)
42010fc6:	dabe                	sw	a5,116(sp)
42010fc8:	3fc957b7          	lui	a5,0x3fc95
42010fcc:	4746                	lw	a4,80(sp)
42010fce:	3047a503          	lw	a0,772(a5) # 3fc95304 <s_state>
42010fd2:	06d10c23          	sb	a3,120(sp)
42010fd6:	47b2                	lw	a5,12(sp)
42010fd8:	46b6                	lw	a3,76(sp)
42010fda:	06011d23          	sh	zero,122(sp)
42010fde:	d4ae                	sw	a1,104(sp)
42010fe0:	d432                	sw	a2,40(sp)
42010fe2:	4405                	li	s0,1
42010fe4:	10b0                	addi	a2,sp,104
42010fe6:	85ca                	mv	a1,s2
42010fe8:	06f10d23          	sb	a5,122(sp)
42010fec:	d636                	sw	a3,44(sp)
42010fee:	d83a                	sw	a4,48(sp)
42010ff0:	00810d23          	sb	s0,26(sp)
42010ff4:	1c4040ef          	jal	420151b8 <native_state_set_stream_info>
42010ff8:	87a2                	mv	a5,s0
42010ffa:	a011                	j	42010ffe <decoder_task+0x88c>
42010ffc:	4781                	li	a5,0
42010ffe:	45b6                	lw	a1,76(sp)
42011000:	854a                	mv	a0,s2
42011002:	00f10d23          	sb	a5,26(sp)
42011006:	b56ff0ef          	jal	4201035c <state_set_decoder_bitrate>
4201100a:	01a14783          	lbu	a5,26(sp)
4201100e:	c3bd                	beqz	a5,42011074 <decoder_task+0x902>
42011010:	180d8563          	beqz	s11,4201119a <decoder_task+0xa28>
42011014:	02814503          	lbu	a0,40(sp)
42011018:	02914783          	lbu	a5,41(sp)
4201101c:	4406                	lw	s0,64(sp)
4201101e:	051d                	addi	a0,a0,7
42011020:	810d                	srli	a0,a0,0x3
42011022:	02f50533          	mul	a0,a0,a5
42011026:	cd15                	beqz	a0,42011062 <decoder_task+0x8f0>
42011028:	5612                	lw	a2,36(sp)
4201102a:	ce05                	beqz	a2,42011062 <decoder_task+0x8f0>
4201102c:	02a45533          	divu	a0,s0,a0
42011030:	000f47b7          	lui	a5,0xf4
42011034:	24078793          	addi	a5,a5,576 # f4240 <CSR_UINTSTATUS+0xf358f>
42011038:	4681                	li	a3,0
4201103a:	02f535b3          	mulhu	a1,a0,a5
4201103e:	02f50533          	mul	a0,a0,a5
42011042:	fdff0097          	auipc	ra,0xfdff0
42011046:	86a080e7          	jalr	-1942(ra) # 400008ac <__udivdi3>
4201104a:	47ea                	lw	a5,152(sp)
4201104c:	46fa                	lw	a3,156(sp)
4201104e:	573a                	lw	a4,172(sp)
42011050:	953e                	add	a0,a0,a5
42011052:	96ae                	add	a3,a3,a1
42011054:	00f537b3          	sltu	a5,a0,a5
42011058:	97b6                	add	a5,a5,a3
4201105a:	9722                	add	a4,a4,s0
4201105c:	cf3e                	sw	a5,156(sp)
4201105e:	cd2a                	sw	a0,152(sp)
42011060:	d73a                	sw	a4,172(sp)
42011062:	86a2                	mv	a3,s0
42011064:	8652                	mv	a2,s4
42011066:	104c                	addi	a1,sp,36
42011068:	854a                	mv	a0,s2
4201106a:	9acff0ef          	jal	42010216 <send_pcm>
4201106e:	8daa                	mv	s11,a0
42011070:	2a050e63          	beqz	a0,4201132c <decoder_task+0xbba>
42011074:	fe370097          	auipc	ra,0xfe370
42011078:	2c6080e7          	jalr	710(ra) # 4038133a <esp_timer_get_time>
4201107c:	862e                	mv	a2,a1
4201107e:	85aa                	mv	a1,a0
42011080:	0108                	addi	a0,sp,128
42011082:	db9fe0ef          	jal	4200fe3a <decode_stats_report>
42011086:	4786                	lw	a5,64(sp)
42011088:	5706                	lw	a4,96(sp)
4201108a:	8fd9                	or	a5,a5,a4
4201108c:	e789                	bnez	a5,42011096 <decoder_task+0x924>
4201108e:	05c14783          	lbu	a5,92(sp)
42011092:	2c078f63          	beqz	a5,42011370 <decoder_task+0xbfe>
42011096:	00a4c783          	lbu	a5,10(s1)
4201109a:	de079ae3          	bnez	a5,42010e8e <decoder_task+0x71c>
4201109e:	4766                	lw	a4,88(sp)
420110a0:	e20711e3          	bnez	a4,42010ec2 <decoder_task+0x750>
420110a4:	be25                	j	42010bdc <decoder_task+0x46a>
420110a6:	5472                	lw	s0,60(sp)
420110a8:	268af463          	bgeu	s5,s0,42011310 <decoder_task+0xb9e>
420110ac:	85a2                	mv	a1,s0
420110ae:	8552                	mv	a0,s4
420110b0:	c3cf70ef          	jal	420084ec <realloc>
420110b4:	24050e63          	beqz	a0,42011310 <decoder_task+0xb9e>
420110b8:	8a2a                	mv	s4,a0
420110ba:	8aa2                	mv	s5,s0
420110bc:	b519                	j	42010ec2 <decoder_task+0x750>
420110be:	4505                	li	a0,1
420110c0:	336ff0ef          	jal	421103f6 <vTaskDelay>
420110c4:	bd91                	j	42010f18 <decoder_task+0x7a6>
420110c6:	00010d23          	sb	zero,26(sp)
420110ca:	b76d                	j	42011074 <decoder_task+0x902>
420110cc:	854e                	mv	a0,s3
420110ce:	097010ef          	jal	42012964 <native_aac_decoder_source_channels>
420110d2:	01b14683          	lbu	a3,27(sp)
420110d6:	0ff57513          	zext.b	a0,a0
420110da:	b2ed                	j	42010ac4 <decoder_task+0x352>
420110dc:	204747b7          	lui	a5,0x20474
420110e0:	74f78793          	addi	a5,a5,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
420110e4:	086c                	addi	a1,sp,28
420110e6:	10a8                	addi	a0,sp,104
420110e8:	d4be                	sw	a5,104(sp)
420110ea:	151140ef          	jal	42025a3a <__wrap_esp_audio_simple_dec_open>
420110ee:	842a                	mv	s0,a0
420110f0:	18051763          	bnez	a0,4201127e <decoder_task+0xb0c>
420110f4:	4c72                	lw	s8,28(sp)
420110f6:	4d81                	li	s11,0
420110f8:	8a0c00e3          	beqz	s8,42010998 <decoder_task+0x226>
420110fc:	4981                	li	s3,0
420110fe:	4c01                	li	s8,0
42011100:	b8c1                	j	420109d0 <decoder_task+0x25e>
42011102:	8452                	mv	s0,s4
42011104:	b94d                	j	42010db6 <decoder_task+0x644>
42011106:	d682                	sw	zero,108(sp)
42011108:	d882                	sw	zero,112(sp)
4201110a:	da82                	sw	zero,116(sp)
4201110c:	801ff06f          	j	4201090c <decoder_task+0x19a>
42011110:	fe377097          	auipc	ra,0xfe377
42011114:	2aa080e7          	jalr	682(ra) # 403883ba <esp_log_timestamp>
42011118:	4791                	li	a5,4
4201111a:	4405                	li	s0,1
4201111c:	86aa                	mv	a3,a0
4201111e:	1efb8463          	beq	s7,a5,42011306 <decoder_task+0xb94>
42011122:	3c1267b7          	lui	a5,0x3c126
42011126:	80078793          	addi	a5,a5,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
4201112a:	008b8663          	beq	s7,s0,42011136 <decoder_task+0x9c4>
4201112e:	3c1267b7          	lui	a5,0x3c126
42011132:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
42011136:	3c126737          	lui	a4,0x3c126
4201113a:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
4201113e:	3c126637          	lui	a2,0x3c126
42011142:	85ba                	mv	a1,a4
42011144:	a6c60613          	addi	a2,a2,-1428 # 3c125a6c <_esp_trace_encoder_array_end+0x594c>
42011148:	4505                	li	a0,1
4201114a:	fe377097          	auipc	ra,0xfe377
4201114e:	168080e7          	jalr	360(ra) # 403882b2 <esp_log>
42011152:	3fc957b7          	lui	a5,0x3fc95
42011156:	3047a503          	lw	a0,772(a5) # 3fc95304 <s_state>
4201115a:	3c1267b7          	lui	a5,0x3c126
4201115e:	9c878693          	addi	a3,a5,-1592 # 3c1259c8 <_esp_trace_encoder_array_end+0x58a8>
42011162:	85ca                	mv	a1,s2
42011164:	4601                	li	a2,0
42011166:	773030ef          	jal	420150d8 <native_state_set_audio>
4201116a:	3fc957b7          	lui	a5,0x3fc95
4201116e:	2fc7a503          	lw	a0,764(a5) # 3fc952fc <s_encoded>
42011172:	85a6                	mv	a1,s1
42011174:	8cca                	mv	s9,s2
42011176:	30e650ef          	jal	42076484 <vRingbufferReturnItem>
4201117a:	4981                	li	s3,0
4201117c:	4d81                	li	s11,0
4201117e:	4c01                	li	s8,0
42011180:	4401                	li	s0,0
42011182:	e56ff06f          	j	420107d8 <decoder_task+0x66>
42011186:	b20c13e3          	bnez	s8,42010cac <decoder_task+0x53a>
4201118a:	8526                	mv	a0,s1
4201118c:	85e6                	mv	a1,s9
4201118e:	d42ff0ef          	jal	420106d0 <return_decoded_packet>
42011192:	4b8d                	li	s7,3
42011194:	4401                	li	s0,0
42011196:	e42ff06f          	j	420107d8 <decoder_task+0x66>
4201119a:	3c1267b7          	lui	a5,0x3c126
4201119e:	b0878513          	addi	a0,a5,-1272 # 3c125b08 <_esp_trace_encoder_array_end+0x59e8>
420111a2:	810ff0ef          	jal	420101b2 <log_runtime_memory>
420111a6:	b5bd                	j	42011014 <decoder_task+0x8a2>
420111a8:	fe377097          	auipc	ra,0xfe377
420111ac:	212080e7          	jalr	530(ra) # 403883ba <esp_log_timestamp>
420111b0:	4789                	li	a5,2
420111b2:	4405                	li	s0,1
420111b4:	0efb8563          	beq	s7,a5,4201129e <decoder_task+0xb2c>
420111b8:	4791                	li	a5,4
420111ba:	1afb8663          	beq	s7,a5,42011366 <decoder_task+0xbf4>
420111be:	3c1267b7          	lui	a5,0x3c126
420111c2:	80078793          	addi	a5,a5,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
420111c6:	008b8663          	beq	s7,s0,420111d2 <decoder_task+0xa60>
420111ca:	3c1267b7          	lui	a5,0x3c126
420111ce:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
420111d2:	48e6                	lw	a7,88(sp)
420111d4:	5806                	lw	a6,96(sp)
420111d6:	3c126737          	lui	a4,0x3c126
420111da:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
420111de:	3c126637          	lui	a2,0x3c126
420111e2:	86aa                	mv	a3,a0
420111e4:	85ba                	mv	a1,a4
420111e6:	b6060613          	addi	a2,a2,-1184 # 3c125b60 <_esp_trace_encoder_array_end+0x5a40>
420111ea:	4505                	li	a0,1
420111ec:	fe377097          	auipc	ra,0xfe377
420111f0:	0c6080e7          	jalr	198(ra) # 403882b2 <esp_log>
420111f4:	3fc957b7          	lui	a5,0x3fc95
420111f8:	3047a503          	lw	a0,772(a5) # 3fc95304 <s_state>
420111fc:	3c1267b7          	lui	a5,0x3c126
42011200:	b9c78693          	addi	a3,a5,-1124 # 3c125b9c <_esp_trace_encoder_array_end+0x5a7c>
42011204:	85ca                	mv	a1,s2
42011206:	4601                	li	a2,0
42011208:	6d1030ef          	jal	420150d8 <native_state_set_audio>
4201120c:	8cca                	mv	s9,s2
4201120e:	b141                	j	42010e8e <decoder_task+0x71c>
42011210:	3c1267b7          	lui	a5,0x3c126
42011214:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
42011218:	f2aff06f          	j	42010942 <decoder_task+0x1d0>
4201121c:	8542                	mv	a0,a6
4201121e:	b8d5                	j	42010b12 <decoder_task+0x3a0>
42011220:	01a14d83          	lbu	s11,26(sp)
42011224:	b00d81e3          	beqz	s11,42010d26 <decoder_task+0x5b4>
42011228:	3c1267b7          	lui	a5,0x3c126
4201122c:	ac478513          	addi	a0,a5,-1340 # 3c125ac4 <_esp_trace_encoder_array_end+0x59a4>
42011230:	f83fe0ef          	jal	420101b2 <log_runtime_memory>
42011234:	bcc5                	j	42010d24 <decoder_task+0x5b2>
42011236:	fe377097          	auipc	ra,0xfe377
4201123a:	184080e7          	jalr	388(ra) # 403883ba <esp_log_timestamp>
4201123e:	3c1267b7          	lui	a5,0x3c126
42011242:	80c78713          	addi	a4,a5,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
42011246:	3c126637          	lui	a2,0x3c126
4201124a:	3c1257b7          	lui	a5,0x3c125
4201124e:	86aa                	mv	a3,a0
42011250:	7f078793          	addi	a5,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
42011254:	85ba                	mv	a1,a4
42011256:	a9c60613          	addi	a2,a2,-1380 # 3c125a9c <_esp_trace_encoder_array_end+0x597c>
4201125a:	5879                	li	a6,-2
4201125c:	4505                	li	a0,1
4201125e:	fe377097          	auipc	ra,0xfe377
42011262:	054080e7          	jalr	84(ra) # 403882b2 <esp_log>
42011266:	3c1267b7          	lui	a5,0x3c126
4201126a:	8a22                	mv	s4,s0
4201126c:	9c878693          	addi	a3,a5,-1592 # 3c1259c8 <_esp_trace_encoder_array_end+0x58a8>
42011270:	efeff06f          	j	4201096e <decoder_task+0x1fc>
42011274:	3c1267b7          	lui	a5,0x3c126
42011278:	80478593          	addi	a1,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
4201127c:	b329                	j	42010f86 <decoder_task+0x814>
4201127e:	fe377097          	auipc	ra,0xfe377
42011282:	13c080e7          	jalr	316(ra) # 403883ba <esp_log_timestamp>
42011286:	3c1257b7          	lui	a5,0x3c125
4201128a:	86aa                	mv	a3,a0
4201128c:	7fc78793          	addi	a5,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
42011290:	eb2ff06f          	j	42010942 <decoder_task+0x1d0>
42011294:	3c1257b7          	lui	a5,0x3c125
42011298:	7f078793          	addi	a5,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
4201129c:	be65                	j	42010e54 <decoder_task+0x6e2>
4201129e:	3c1257b7          	lui	a5,0x3c125
420112a2:	7f078793          	addi	a5,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
420112a6:	b735                	j	420111d2 <decoder_task+0xa60>
420112a8:	fe377097          	auipc	ra,0xfe377
420112ac:	112080e7          	jalr	274(ra) # 403883ba <esp_log_timestamp>
420112b0:	3c1267b7          	lui	a5,0x3c126
420112b4:	80c78713          	addi	a4,a5,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
420112b8:	3c1267b7          	lui	a5,0x3c126
420112bc:	86aa                	mv	a3,a0
420112be:	85ba                	mv	a1,a4
420112c0:	a3878613          	addi	a2,a5,-1480 # 3c125a38 <_esp_trace_encoder_array_end+0x5918>
420112c4:	4505                	li	a0,1
420112c6:	fe377097          	auipc	ra,0xfe377
420112ca:	fec080e7          	jalr	-20(ra) # 403882b2 <esp_log>
420112ce:	3fc957b7          	lui	a5,0x3fc95
420112d2:	3047a503          	lw	a0,772(a5) # 3fc95304 <s_state>
420112d6:	3c1267b7          	lui	a5,0x3c126
420112da:	9c878693          	addi	a3,a5,-1592 # 3c1259c8 <_esp_trace_encoder_array_end+0x58a8>
420112de:	85ca                	mv	a1,s2
420112e0:	4601                	li	a2,0
420112e2:	5f7030ef          	jal	420150d8 <native_state_set_audio>
420112e6:	8cca                	mv	s9,s2
420112e8:	4981                	li	s3,0
420112ea:	4a01                	li	s4,0
420112ec:	4a81                	li	s5,0
420112ee:	4d81                	li	s11,0
420112f0:	bd69                	j	4201118a <decoder_task+0xa18>
420112f2:	3c1257b7          	lui	a5,0x3c125
420112f6:	7fc78593          	addi	a1,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
420112fa:	b171                	j	42010f86 <decoder_task+0x814>
420112fc:	3c1257b7          	lui	a5,0x3c125
42011300:	7f078593          	addi	a1,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
42011304:	b149                	j	42010f86 <decoder_task+0x814>
42011306:	3c1257b7          	lui	a5,0x3c125
4201130a:	7fc78793          	addi	a5,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
4201130e:	b525                	j	42011136 <decoder_task+0x9c4>
42011310:	3fc957b7          	lui	a5,0x3fc95
42011314:	3047a503          	lw	a0,772(a5) # 3fc95304 <s_state>
42011318:	3c1267b7          	lui	a5,0x3c126
4201131c:	b2478693          	addi	a3,a5,-1244 # 3c125b24 <_esp_trace_encoder_array_end+0x5a04>
42011320:	4601                	li	a2,0
42011322:	85ca                	mv	a1,s2
42011324:	5b5030ef          	jal	420150d8 <native_state_set_audio>
42011328:	8cca                	mv	s9,s2
4201132a:	b695                	j	42010e8e <decoder_task+0x71c>
4201132c:	fe377097          	auipc	ra,0xfe377
42011330:	08e080e7          	jalr	142(ra) # 403883ba <esp_log_timestamp>
42011334:	3c1267b7          	lui	a5,0x3c126
42011338:	80c78713          	addi	a4,a5,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
4201133c:	3c1267b7          	lui	a5,0x3c126
42011340:	86aa                	mv	a3,a0
42011342:	bb078613          	addi	a2,a5,-1104 # 3c125bb0 <_esp_trace_encoder_array_end+0x5a90>
42011346:	85ba                	mv	a1,a4
42011348:	4509                	li	a0,2
4201134a:	fe377097          	auipc	ra,0xfe377
4201134e:	f68080e7          	jalr	-152(ra) # 403882b2 <esp_log>
42011352:	00a4c783          	lbu	a5,10(s1)
42011356:	4d85                	li	s11,1
42011358:	885ff06f          	j	42010bdc <decoder_task+0x46a>
4201135c:	3c1257b7          	lui	a5,0x3c125
42011360:	7fc78793          	addi	a5,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
42011364:	bcc5                	j	42010e54 <decoder_task+0x6e2>
42011366:	3c1257b7          	lui	a5,0x3c125
4201136a:	7fc78793          	addi	a5,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
4201136e:	b595                	j	420111d2 <decoder_task+0xa60>
42011370:	fe377097          	auipc	ra,0xfe377
42011374:	04a080e7          	jalr	74(ra) # 403883ba <esp_log_timestamp>
42011378:	4789                	li	a5,2
4201137a:	4405                	li	s0,1
4201137c:	86aa                	mv	a3,a0
4201137e:	06fb8663          	beq	s7,a5,420113ea <decoder_task+0xc78>
42011382:	4791                	li	a5,4
42011384:	04fb8e63          	beq	s7,a5,420113e0 <decoder_task+0xc6e>
42011388:	3c1267b7          	lui	a5,0x3c126
4201138c:	80078793          	addi	a5,a5,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
42011390:	008b8663          	beq	s7,s0,4201139c <decoder_task+0xc2a>
42011394:	3c1267b7          	lui	a5,0x3c126
42011398:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
4201139c:	3c126737          	lui	a4,0x3c126
420113a0:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
420113a4:	3c126637          	lui	a2,0x3c126
420113a8:	85ba                	mv	a1,a4
420113aa:	bd060613          	addi	a2,a2,-1072 # 3c125bd0 <_esp_trace_encoder_array_end+0x5ab0>
420113ae:	4505                	li	a0,1
420113b0:	fe377097          	auipc	ra,0xfe377
420113b4:	f02080e7          	jalr	-254(ra) # 403882b2 <esp_log>
420113b8:	3fc957b7          	lui	a5,0x3fc95
420113bc:	3047a503          	lw	a0,772(a5) # 3fc95304 <s_state>
420113c0:	3c1267b7          	lui	a5,0x3c126
420113c4:	c0078693          	addi	a3,a5,-1024 # 3c125c00 <_esp_trace_encoder_array_end+0x5ae0>
420113c8:	85ca                	mv	a1,s2
420113ca:	4601                	li	a2,0
420113cc:	50d030ef          	jal	420150d8 <native_state_set_audio>
420113d0:	8cca                	mv	s9,s2
420113d2:	bc75                	j	42010e8e <decoder_task+0x71c>
420113d4:	3c1267b7          	lui	a5,0x3c126
420113d8:	9c878693          	addi	a3,a5,-1592 # 3c1259c8 <_esp_trace_encoder_array_end+0x58a8>
420113dc:	d92ff06f          	j	4201096e <decoder_task+0x1fc>
420113e0:	3c1257b7          	lui	a5,0x3c125
420113e4:	7fc78793          	addi	a5,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
420113e8:	bf55                	j	4201139c <decoder_task+0xc2a>
420113ea:	3c1257b7          	lui	a5,0x3c125
420113ee:	7f078793          	addi	a5,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
420113f2:	b76d                	j	4201139c <decoder_task+0xc2a>
420113f4:	fe377097          	auipc	ra,0xfe377
420113f8:	fc6080e7          	jalr	-58(ra) # 403883ba <esp_log_timestamp>
420113fc:	3c1257b7          	lui	a5,0x3c125
42011400:	86aa                	mv	a3,a0
42011402:	7f078793          	addi	a5,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
42011406:	bb05                	j	42011136 <decoder_task+0x9c4>
