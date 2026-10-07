
idf\esp32c3-oled-native\build-output-dma\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42010772 <decoder_task>:
42010772:	7151                	addi	sp,sp,-240
42010774:	d5a2                	sw	s0,232(sp)
42010776:	d3a6                	sw	s1,228(sp)
42010778:	d1ca                	sw	s2,224(sp)
4201077a:	cfce                	sw	s3,220(sp)
4201077c:	cdd2                	sw	s4,216(sp)
4201077e:	cbd6                	sw	s5,212(sp)
42010780:	c9da                	sw	s6,208(sp)
42010782:	c7de                	sw	s7,204(sp)
42010784:	c5e2                	sw	s8,200(sp)
42010786:	df6e                	sw	s11,188(sp)
42010788:	d786                	sw	ra,236(sp)
4201078a:	c3e6                	sw	s9,196(sp)
4201078c:	c1ea                	sw	s10,192(sp)
4201078e:	5c9010ef          	jal	42012556 <decoder_register_codecs>
42010792:	3fc95737          	lui	a4,0x3fc95
42010796:	000f47b7          	lui	a5,0xf4
4201079a:	ad870713          	addi	a4,a4,-1320 # 3fc94ad8 <s_bitrate_updated_us>
4201079e:	24078793          	addi	a5,a5,576 # f4240 <CSR_UINTSTATUS+0xf358f>
420107a2:	ce02                	sw	zero,28(sp)
420107a4:	c102                	sw	zero,128(sp)
420107a6:	c302                	sw	zero,132(sp)
420107a8:	c502                	sw	zero,136(sp)
420107aa:	c702                	sw	zero,140(sp)
420107ac:	c902                	sw	zero,144(sp)
420107ae:	cb02                	sw	zero,148(sp)
420107b0:	cd02                	sw	zero,152(sp)
420107b2:	cf02                	sw	zero,156(sp)
420107b4:	d102                	sw	zero,160(sp)
420107b6:	d302                	sw	zero,164(sp)
420107b8:	d502                	sw	zero,168(sp)
420107ba:	d702                	sw	zero,172(sp)
420107bc:	d202                	sw	zero,36(sp)
420107be:	d402                	sw	zero,40(sp)
420107c0:	d602                	sw	zero,44(sp)
420107c2:	d802                	sw	zero,48(sp)
420107c4:	00010d23          	sb	zero,26(sp)
420107c8:	842a                	mv	s0,a0
420107ca:	c23a                	sw	a4,4(sp)
420107cc:	c43e                	sw	a5,8(sp)
420107ce:	4981                	li	s3,0
420107d0:	4a01                	li	s4,0
420107d2:	4901                	li	s2,0
420107d4:	4d81                	li	s11,0
420107d6:	4b01                	li	s6,0
420107d8:	4c01                	li	s8,0
420107da:	4481                	li	s1,0
420107dc:	4b81                	li	s7,0
420107de:	3fc95ab7          	lui	s5,0x3fc95
420107e2:	af0a8793          	addi	a5,s5,-1296 # 3fc94af0 <s_generation>
420107e6:	0330000f          	fence	rw,rw
420107ea:	0007ac83          	lw	s9,0(a5)
420107ee:	0230000f          	fence	r,rw
420107f2:	409c8f63          	beq	s9,s1,42010c10 <decoder_task+0x49e>
420107f6:	3fc957b7          	lui	a5,0x3fc95
420107fa:	aec78793          	addi	a5,a5,-1300 # 3fc94aec <s_decoder_target_codec>
420107fe:	0330000f          	fence	rw,rw
42010802:	4384                	lw	s1,0(a5)
42010804:	0230000f          	fence	r,rw
42010808:	4572                	lw	a0,28(sp)
4201080a:	c119                	beqz	a0,42010810 <decoder_task+0x9e>
4201080c:	42e260ef          	jal	42036c3a <esp_audio_simple_dec_close>
42010810:	854e                	mv	a0,s3
42010812:	ce02                	sw	zero,28(sp)
42010814:	5a5010ef          	jal	420125b8 <native_aac_decoder_destroy>
42010818:	000b8563          	beqz	s7,42010822 <decoder_task+0xb0>
4201081c:	855e                	mv	a0,s7
4201081e:	108240ef          	jal	42034926 <custom_flac_decoder_destroy>
42010822:	46048c63          	beqz	s1,42010c9a <decoder_task+0x528>
42010826:	d202                	sw	zero,36(sp)
42010828:	d402                	sw	zero,40(sp)
4201082a:	d602                	sw	zero,44(sp)
4201082c:	d802                	sw	zero,48(sp)
4201082e:	00010d23          	sb	zero,26(sp)
42010832:	3fc957b7          	lui	a5,0x3fc95
42010836:	ae878793          	addi	a5,a5,-1304 # 3fc94ae8 <s_decoder_released_generation>
4201083a:	0310000f          	fence	rw,w
4201083e:	0197a023          	sw	s9,0(a5)
42010842:	0330000f          	fence	rw,rw
42010846:	4b81                	li	s7,0
42010848:	84e6                	mv	s1,s9
4201084a:	4c01                	li	s8,0
4201084c:	4b01                	li	s6,0
4201084e:	4d81                	li	s11,0
42010850:	4981                	li	s3,0
42010852:	3fc957b7          	lui	a5,0x3fc95
42010856:	afc7a503          	lw	a0,-1284(a5) # 3fc94afc <s_encoded>
4201085a:	4651                	li	a2,20
4201085c:	100c                	addi	a1,sp,32
4201085e:	d002                	sw	zero,32(sp)
42010860:	6c1650ef          	jal	42076720 <xRingbufferReceive>
42010864:	8caa                	mv	s9,a0
42010866:	dd35                	beqz	a0,420107e2 <decoder_task+0x70>
42010868:	4118                	lw	a4,0(a0)
4201086a:	af0a8793          	addi	a5,s5,-1296
4201086e:	0330000f          	fence	rw,rw
42010872:	439c                	lw	a5,0(a5)
42010874:	0230000f          	fence	r,rw
42010878:	40f71963          	bne	a4,a5,42010c8a <decoder_task+0x518>
4201087c:	411c                	lw	a5,0(a0)
4201087e:	41878663          	beq	a5,s8,42010c8a <decoder_task+0x518>
42010882:	4158                	lw	a4,4(a0)
42010884:	e709                	bnez	a4,4201088e <decoder_task+0x11c>
42010886:	00a54703          	lbu	a4,10(a0)
4201088a:	3e071c63          	bnez	a4,42010c82 <decoder_task+0x510>
4201088e:	12041563          	bnez	s0,420109b8 <decoder_task+0x246>
42010892:	12978c63          	beq	a5,s1,420109ca <decoder_task+0x258>
42010896:	4572                	lw	a0,28(sp)
42010898:	c119                	beqz	a0,4201089e <decoder_task+0x12c>
4201089a:	3a0260ef          	jal	42036c3a <esp_audio_simple_dec_close>
4201089e:	854e                	mv	a0,s3
420108a0:	ce02                	sw	zero,28(sp)
420108a2:	517010ef          	jal	420125b8 <native_aac_decoder_destroy>
420108a6:	000b8563          	beqz	s7,420108b0 <decoder_task+0x13e>
420108aa:	855e                	mv	a0,s7
420108ac:	07a240ef          	jal	42034926 <custom_flac_decoder_destroy>
420108b0:	4712                	lw	a4,4(sp)
420108b2:	000ca483          	lw	s1,0(s9)
420108b6:	004cab03          	lw	s6,4(s9)
420108ba:	3fc957b7          	lui	a5,0x3fc95
420108be:	ae07a023          	sw	zero,-1312(a5) # 3fc94ae0 <s_published_bitrate_bps>
420108c2:	4801                	li	a6,0
420108c4:	4781                	li	a5,0
420108c6:	c31c                	sw	a5,0(a4)
420108c8:	00010d23          	sb	zero,26(sp)
420108cc:	01072223          	sw	a6,4(a4)
420108d0:	fe371097          	auipc	ra,0xfe371
420108d4:	a6a080e7          	jalr	-1430(ra) # 4038133a <esp_timer_get_time>
420108d8:	c52a                	sw	a0,136(sp)
420108da:	c902                	sw	zero,144(sp)
420108dc:	cb02                	sw	zero,148(sp)
420108de:	cd02                	sw	zero,152(sp)
420108e0:	cf02                	sw	zero,156(sp)
420108e2:	d102                	sw	zero,160(sp)
420108e4:	d302                	sw	zero,164(sp)
420108e6:	d502                	sw	zero,168(sp)
420108e8:	d702                	sw	zero,172(sp)
420108ea:	c126                	sw	s1,128(sp)
420108ec:	c35a                	sw	s6,132(sp)
420108ee:	c72e                	sw	a1,140(sp)
420108f0:	478d                	li	a5,3
420108f2:	3afb0a63          	beq	s6,a5,42010ca6 <decoder_task+0x534>
420108f6:	4789                	li	a5,2
420108f8:	46fb0b63          	beq	s6,a5,42010d6e <decoder_task+0x5fc>
420108fc:	640d                	lui	s0,0x3
420108fe:	7e8a7463          	bgeu	s4,s0,420110e6 <decoder_task+0x974>
42010902:	85a2                	mv	a1,s0
42010904:	854a                	mv	a0,s2
42010906:	be7f70ef          	jal	420084ec <realloc>
4201090a:	7e050363          	beqz	a0,420110f0 <decoder_task+0x97e>
4201090e:	d682                	sw	zero,108(sp)
42010910:	d882                	sw	zero,112(sp)
42010912:	da82                	sw	zero,116(sp)
42010914:	892a                	mv	s2,a0
42010916:	8a22                	mv	s4,s0
42010918:	4791                	li	a5,4
4201091a:	78fb0a63          	beq	s6,a5,420110ae <decoder_task+0x93c>
4201091e:	203357b7          	lui	a5,0x20335
42010922:	04d78793          	addi	a5,a5,77 # 2033504d <CSR_UINTSTATUS+0x2033439c>
42010926:	086c                	addi	a1,sp,28
42010928:	10a8                	addi	a0,sp,104
4201092a:	d4be                	sw	a5,104(sp)
4201092c:	2a0150ef          	jal	42025bcc <__wrap_esp_audio_simple_dec_open>
42010930:	842a                	mv	s0,a0
42010932:	78050a63          	beqz	a0,420110c6 <decoder_task+0x954>
42010936:	fe378097          	auipc	ra,0xfe378
4201093a:	a84080e7          	jalr	-1404(ra) # 403883ba <esp_log_timestamp>
4201093e:	3c1267b7          	lui	a5,0x3c126
42010942:	4985                	li	s3,1
42010944:	86aa                	mv	a3,a0
42010946:	80078793          	addi	a5,a5,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
4201094a:	093b17e3          	bne	s6,s3,420111d8 <decoder_task+0xa66>
4201094e:	3c126737          	lui	a4,0x3c126
42010952:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
42010956:	3c126637          	lui	a2,0x3c126
4201095a:	85ba                	mv	a1,a4
4201095c:	8822                	mv	a6,s0
4201095e:	a9c60613          	addi	a2,a2,-1380 # 3c125a9c <_esp_trace_encoder_array_end+0x597c>
42010962:	4505                	li	a0,1
42010964:	fe378097          	auipc	ra,0xfe378
42010968:	94e080e7          	jalr	-1714(ra) # 403882b2 <esp_log>
4201096c:	3c126737          	lui	a4,0x3c126
42010970:	57f9                	li	a5,-2
42010972:	9d470693          	addi	a3,a4,-1580 # 3c1259d4 <_esp_trace_encoder_array_end+0x58b4>
42010976:	28f400e3          	beq	s0,a5,420113f6 <decoder_task+0xc84>
4201097a:	3fc957b7          	lui	a5,0x3fc95
4201097e:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42010982:	4601                	li	a2,0
42010984:	85a6                	mv	a1,s1
42010986:	76a040ef          	jal	420150f0 <native_state_set_audio>
4201098a:	4572                	lw	a0,28(sp)
4201098c:	c501                	beqz	a0,42010994 <decoder_task+0x222>
4201098e:	2ac260ef          	jal	42036c3a <esp_audio_simple_dec_close>
42010992:	ce02                	sw	zero,28(sp)
42010994:	854a                	mv	a0,s2
42010996:	b5bf70ef          	jal	420084f0 <cfree>
4201099a:	8c26                	mv	s8,s1
4201099c:	4a01                	li	s4,0
4201099e:	4901                	li	s2,0
420109a0:	4b81                	li	s7,0
420109a2:	4d81                	li	s11,0
420109a4:	3fc957b7          	lui	a5,0x3fc95
420109a8:	afc7a503          	lw	a0,-1284(a5) # 3fc94afc <s_encoded>
420109ac:	85e6                	mv	a1,s9
420109ae:	4981                	li	s3,0
420109b0:	5ed650ef          	jal	4207679c <vRingbufferReturnItem>
420109b4:	4401                	li	s0,0
420109b6:	b535                	j	420107e2 <decoder_task+0x70>
420109b8:	39f010ef          	jal	42012556 <decoder_register_codecs>
420109bc:	842a                	mv	s0,a0
420109be:	26051e63          	bnez	a0,42010c3a <decoder_task+0x4c8>
420109c2:	000ca783          	lw	a5,0(s9)
420109c6:	ec9798e3          	bne	a5,s1,42010896 <decoder_task+0x124>
420109ca:	004ca783          	lw	a5,4(s9)
420109ce:	ed6794e3          	bne	a5,s6,42010896 <decoder_task+0x124>
420109d2:	478d                	li	a5,3
420109d4:	78fb0963          	beq	s6,a5,42011166 <decoder_task+0x9f4>
420109d8:	47f2                	lw	a5,28(sp)
420109da:	00f9e7b3          	or	a5,s3,a5
420109de:	d3f9                	beqz	a5,420109a4 <decoder_task+0x232>
420109e0:	008cd783          	lhu	a5,8(s9)
420109e4:	00bc8713          	addi	a4,s9,11
420109e8:	ce82                	sw	zero,92(sp)
420109ea:	d082                	sw	zero,96(sp)
420109ec:	d282                	sw	zero,100(sp)
420109ee:	ccbe                	sw	a5,88(sp)
420109f0:	caba                	sw	a4,84(sp)
420109f2:	00acc703          	lbu	a4,10(s9)
420109f6:	ffeb0693          	addi	a3,s6,-2
420109fa:	0016b693          	seqz	a3,a3
420109fe:	00e03733          	snez	a4,a4
42010a02:	c036                	sw	a3,0(sp)
42010a04:	04e10e23          	sb	a4,92(sp)
42010a08:	38098e63          	beqz	s3,42010da4 <decoder_task+0x632>
42010a0c:	e789                	bnez	a5,42010a16 <decoder_task+0x2a4>
42010a0e:	05c14783          	lbu	a5,92(sp)
42010a12:	1c078a63          	beqz	a5,42010be6 <decoder_task+0x474>
42010a16:	4781                	li	a5,0
42010a18:	4801                	li	a6,0
42010a1a:	de3e                	sw	a5,60(sp)
42010a1c:	c0c2                	sw	a6,64(sp)
42010a1e:	da4a                	sw	s2,52(sp)
42010a20:	dc52                	sw	s4,56(sp)
42010a22:	d082                	sw	zero,96(sp)
42010a24:	fe371097          	auipc	ra,0xfe371
42010a28:	916080e7          	jalr	-1770(ra) # 4038133a <esp_timer_get_time>
42010a2c:	842a                	mv	s0,a0
42010a2e:	1850                	addi	a2,sp,52
42010a30:	08cc                	addi	a1,sp,84
42010a32:	854e                	mv	a0,s3
42010a34:	3bb010ef          	jal	420125ee <native_aac_decoder_process>
42010a38:	8d2a                	mv	s10,a0
42010a3a:	fe371097          	auipc	ra,0xfe371
42010a3e:	900080e7          	jalr	-1792(ra) # 4038133a <esp_timer_get_time>
42010a42:	47ca                	lw	a5,144(sp)
42010a44:	46da                	lw	a3,148(sp)
42010a46:	8d01                	sub	a0,a0,s0
42010a48:	00a78733          	add	a4,a5,a0
42010a4c:	00f737b3          	sltu	a5,a4,a5
42010a50:	97b6                	add	a5,a5,a3
42010a52:	cb3e                	sw	a5,148(sp)
42010a54:	578a                	lw	a5,160(sp)
42010a56:	c93a                	sw	a4,144(sp)
42010a58:	571a                	lw	a4,164(sp)
42010a5a:	0785                	addi	a5,a5,1
42010a5c:	d13e                	sw	a5,160(sp)
42010a5e:	00a77363          	bgeu	a4,a0,42010a64 <decoder_task+0x2f2>
42010a62:	d32a                	sw	a0,164(sp)
42010a64:	8bfd                	andi	a5,a5,31
42010a66:	56078163          	beqz	a5,42010fc8 <decoder_task+0x856>
42010a6a:	af0a8793          	addi	a5,s5,-1296
42010a6e:	0330000f          	fence	rw,rw
42010a72:	439c                	lw	a5,0(a5)
42010a74:	0230000f          	fence	r,rw
42010a78:	16979763          	bne	a5,s1,42010be6 <decoder_task+0x474>
42010a7c:	57e1                	li	a5,-8
42010a7e:	50fd0f63          	beq	s10,a5,42010f9c <decoder_task+0x82a>
42010a82:	580d1a63          	bnez	s10,42011016 <decoder_task+0x8a4>
42010a86:	5786                	lw	a5,96(sp)
42010a88:	4766                	lw	a4,88(sp)
42010a8a:	6ef76163          	bltu	a4,a5,4201116c <decoder_task+0x9fa>
42010a8e:	8f1d                	sub	a4,a4,a5
42010a90:	56aa                	lw	a3,168(sp)
42010a92:	ccba                	sw	a4,88(sp)
42010a94:	4756                	lw	a4,84(sp)
42010a96:	96be                	add	a3,a3,a5
42010a98:	d536                	sw	a3,168(sp)
42010a9a:	97ba                	add	a5,a5,a4
42010a9c:	4706                	lw	a4,64(sp)
42010a9e:	cabe                	sw	a5,84(sp)
42010aa0:	10070c63          	beqz	a4,42010bb8 <decoder_task+0x446>
42010aa4:	00cc                	addi	a1,sp,68
42010aa6:	854e                	mv	a0,s3
42010aa8:	c282                	sw	zero,68(sp)
42010aaa:	c482                	sw	zero,72(sp)
42010aac:	c682                	sw	zero,76(sp)
42010aae:	c882                	sw	zero,80(sp)
42010ab0:	667010ef          	jal	42012916 <native_aac_decoder_get_info>
42010ab4:	50051e63          	bnez	a0,42010fd0 <decoder_task+0x85e>
42010ab8:	4782                	lw	a5,0(sp)
42010aba:	01b10613          	addi	a2,sp,27
42010abe:	00cc                	addi	a1,sp,68
42010ac0:	854e                	mv	a0,s3
42010ac2:	00f10da3          	sb	a5,27(sp)
42010ac6:	65f010ef          	jal	42012924 <native_aac_decoder_label>
42010aca:	01b14683          	lbu	a3,27(sp)
42010ace:	842a                	mv	s0,a0
42010ad0:	4501                	li	a0,0
42010ad2:	5c068663          	beqz	a3,4201109e <decoder_task+0x92c>
42010ad6:	af0a8793          	addi	a5,s5,-1296
42010ada:	0330000f          	fence	rw,rw
42010ade:	4398                	lw	a4,0(a5)
42010ae0:	0230000f          	fence	r,rw
42010ae4:	4781                	li	a5,0
42010ae6:	06971163          	bne	a4,s1,42010b48 <decoder_task+0x3d6>
42010aea:	4716                	lw	a4,68(sp)
42010aec:	cf31                	beqz	a4,42010b48 <decoder_task+0x3d6>
42010aee:	04914803          	lbu	a6,73(sp)
42010af2:	04080b63          	beqz	a6,42010b48 <decoder_task+0x3d6>
42010af6:	04814603          	lbu	a2,72(sp)
42010afa:	c639                	beqz	a2,42010b48 <decoder_task+0x3d6>
42010afc:	45a6                	lw	a1,72(sp)
42010afe:	47b6                	lw	a5,76(sp)
42010b00:	d23a                	sw	a4,36(sp)
42010b02:	d42e                	sw	a1,40(sp)
42010b04:	45c6                	lw	a1,80(sp)
42010b06:	d63e                	sw	a5,44(sp)
42010b08:	4785                	li	a5,1
42010b0a:	06012923          	sw	zero,114(sp)
42010b0e:	06012b23          	sw	zero,118(sp)
42010b12:	06011d23          	sh	zero,122(sp)
42010b16:	d4a2                	sw	s0,104(sp)
42010b18:	d6ba                	sw	a4,108(sp)
42010b1a:	d82e                	sw	a1,48(sp)
42010b1c:	00f10d23          	sb	a5,26(sp)
42010b20:	6a050a63          	beqz	a0,420111d4 <decoder_task+0xa62>
42010b24:	3fc957b7          	lui	a5,0x3fc95
42010b28:	06a10823          	sb	a0,112(sp)
42010b2c:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42010b30:	06c108a3          	sb	a2,113(sp)
42010b34:	85a6                	mv	a1,s1
42010b36:	10b0                	addi	a2,sp,104
42010b38:	daba                	sw	a4,116(sp)
42010b3a:	07010c23          	sb	a6,120(sp)
42010b3e:	06d10d23          	sb	a3,122(sp)
42010b42:	68e040ef          	jal	420151d0 <native_state_set_stream_info>
42010b46:	4785                	li	a5,1
42010b48:	45b6                	lw	a1,76(sp)
42010b4a:	8526                	mv	a0,s1
42010b4c:	00f10d23          	sb	a5,26(sp)
42010b50:	80dff0ef          	jal	4201035c <state_set_decoder_bitrate>
42010b54:	01a14783          	lbu	a5,26(sp)
42010b58:	c3a5                	beqz	a5,42010bb8 <decoder_task+0x446>
42010b5a:	4a0d8763          	beqz	s11,42011008 <decoder_task+0x896>
42010b5e:	02814503          	lbu	a0,40(sp)
42010b62:	02914783          	lbu	a5,41(sp)
42010b66:	4406                	lw	s0,64(sp)
42010b68:	051d                	addi	a0,a0,7
42010b6a:	810d                	srli	a0,a0,0x3
42010b6c:	02f50533          	mul	a0,a0,a5
42010b70:	c91d                	beqz	a0,42010ba6 <decoder_task+0x434>
42010b72:	5612                	lw	a2,36(sp)
42010b74:	ca0d                	beqz	a2,42010ba6 <decoder_task+0x434>
42010b76:	02a45533          	divu	a0,s0,a0
42010b7a:	47a2                	lw	a5,8(sp)
42010b7c:	4681                	li	a3,0
42010b7e:	02f535b3          	mulhu	a1,a0,a5
42010b82:	02f50533          	mul	a0,a0,a5
42010b86:	fdff0097          	auipc	ra,0xfdff0
42010b8a:	d26080e7          	jalr	-730(ra) # 400008ac <__udivdi3>
42010b8e:	47ea                	lw	a5,152(sp)
42010b90:	46fa                	lw	a3,156(sp)
42010b92:	573a                	lw	a4,172(sp)
42010b94:	953e                	add	a0,a0,a5
42010b96:	96ae                	add	a3,a3,a1
42010b98:	00f537b3          	sltu	a5,a0,a5
42010b9c:	97b6                	add	a5,a5,a3
42010b9e:	9722                	add	a4,a4,s0
42010ba0:	cf3e                	sw	a5,156(sp)
42010ba2:	cd2a                	sw	a0,152(sp)
42010ba4:	d73a                	sw	a4,172(sp)
42010ba6:	86a2                	mv	a3,s0
42010ba8:	864a                	mv	a2,s2
42010baa:	104c                	addi	a1,sp,36
42010bac:	8526                	mv	a0,s1
42010bae:	e68ff0ef          	jal	42010216 <send_pcm>
42010bb2:	8daa                	mv	s11,a0
42010bb4:	72050a63          	beqz	a0,420112e8 <decoder_task+0xb76>
42010bb8:	fe370097          	auipc	ra,0xfe370
42010bbc:	782080e7          	jalr	1922(ra) # 4038133a <esp_timer_get_time>
42010bc0:	862e                	mv	a2,a1
42010bc2:	85aa                	mv	a1,a0
42010bc4:	0108                	addi	a0,sp,128
42010bc6:	a74ff0ef          	jal	4200fe3a <decode_stats_report>
42010bca:	4706                	lw	a4,64(sp)
42010bcc:	5786                	lw	a5,96(sp)
42010bce:	05c14683          	lbu	a3,92(sp)
42010bd2:	8fd9                	or	a5,a5,a4
42010bd4:	3a079e63          	bnez	a5,42010f90 <decoder_task+0x81e>
42010bd8:	74068e63          	beqz	a3,42011334 <decoder_task+0xbc2>
42010bdc:	4701                	li	a4,0
42010bde:	47e6                	lw	a5,88(sp)
42010be0:	8f5d                	or	a4,a4,a5
42010be2:	e20715e3          	bnez	a4,42010a0c <decoder_task+0x29a>
42010be6:	00acc783          	lbu	a5,10(s9)
42010bea:	48079963          	bnez	a5,4201107c <decoder_task+0x90a>
42010bee:	489c0763          	beq	s8,s1,4201107c <decoder_task+0x90a>
42010bf2:	8566                	mv	a0,s9
42010bf4:	85e2                	mv	a1,s8
42010bf6:	adbff0ef          	jal	420106d0 <return_decoded_packet>
42010bfa:	4401                	li	s0,0
42010bfc:	af0a8793          	addi	a5,s5,-1296
42010c00:	0330000f          	fence	rw,rw
42010c04:	0007ac83          	lw	s9,0(a5)
42010c08:	0230000f          	fence	r,rw
42010c0c:	be9c95e3          	bne	s9,s1,420107f6 <decoder_task+0x84>
42010c10:	c40c01e3          	beqz	s8,42010852 <decoder_task+0xe0>
42010c14:	c29c1fe3          	bne	s8,s1,42010852 <decoder_task+0xe0>
42010c18:	4572                	lw	a0,28(sp)
42010c1a:	c119                	beqz	a0,42010c20 <decoder_task+0x4ae>
42010c1c:	01e260ef          	jal	42036c3a <esp_audio_simple_dec_close>
42010c20:	ce02                	sw	zero,28(sp)
42010c22:	00098563          	beqz	s3,42010c2c <decoder_task+0x4ba>
42010c26:	854e                	mv	a0,s3
42010c28:	191010ef          	jal	420125b8 <native_aac_decoder_destroy>
42010c2c:	854a                	mv	a0,s2
42010c2e:	8c3f70ef          	jal	420084f0 <cfree>
42010c32:	4981                	li	s3,0
42010c34:	4a01                	li	s4,0
42010c36:	4901                	li	s2,0
42010c38:	b929                	j	42010852 <decoder_task+0xe0>
42010c3a:	fe377097          	auipc	ra,0xfe377
42010c3e:	780080e7          	jalr	1920(ra) # 403883ba <esp_log_timestamp>
42010c42:	3c126737          	lui	a4,0x3c126
42010c46:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
42010c4a:	3c126637          	lui	a2,0x3c126
42010c4e:	86aa                	mv	a3,a0
42010c50:	85ba                	mv	a1,a4
42010c52:	87a2                	mv	a5,s0
42010c54:	9f460613          	addi	a2,a2,-1548 # 3c1259f4 <_esp_trace_encoder_array_end+0x58d4>
42010c58:	4505                	li	a0,1
42010c5a:	fe377097          	auipc	ra,0xfe377
42010c5e:	658080e7          	jalr	1624(ra) # 403882b2 <esp_log>
42010c62:	3fc957b7          	lui	a5,0x3fc95
42010c66:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42010c6a:	000ca583          	lw	a1,0(s9)
42010c6e:	3c1267b7          	lui	a5,0x3c126
42010c72:	a2478693          	addi	a3,a5,-1500 # 3c125a24 <_esp_trace_encoder_array_end+0x5904>
42010c76:	4601                	li	a2,0
42010c78:	478040ef          	jal	420150f0 <native_state_set_audio>
42010c7c:	000cac03          	lw	s8,0(s9)
42010c80:	8566                	mv	a0,s9
42010c82:	85e2                	mv	a1,s8
42010c84:	a4dff0ef          	jal	420106d0 <return_decoded_packet>
42010c88:	bea9                	j	420107e2 <decoder_task+0x70>
42010c8a:	3fc957b7          	lui	a5,0x3fc95
42010c8e:	afc7a503          	lw	a0,-1284(a5) # 3fc94afc <s_encoded>
42010c92:	85e6                	mv	a1,s9
42010c94:	309650ef          	jal	4207679c <vRingbufferReturnItem>
42010c98:	b6a9                	j	420107e2 <decoder_task+0x70>
42010c9a:	854a                	mv	a0,s2
42010c9c:	855f70ef          	jal	420084f0 <cfree>
42010ca0:	4a01                	li	s4,0
42010ca2:	4901                	li	s2,0
42010ca4:	b649                	j	42010826 <decoder_task+0xb4>
42010ca6:	854a                	mv	a0,s2
42010ca8:	849f70ef          	jal	420084f0 <cfree>
42010cac:	41b230ef          	jal	420348c6 <custom_flac_decoder_create>
42010cb0:	8baa                	mv	s7,a0
42010cb2:	5a050863          	beqz	a0,42011262 <decoder_task+0xaf0>
42010cb6:	4981                	li	s3,0
42010cb8:	4a01                	li	s4,0
42010cba:	4901                	li	s2,0
42010cbc:	4d81                	li	s11,0
42010cbe:	4661                	li	a2,24
42010cc0:	4581                	li	a1,0
42010cc2:	10a8                	addi	a0,sp,104
42010cc4:	fdfef097          	auipc	ra,0xfdfef
42010cc8:	690080e7          	jalr	1680(ra) # 40000354 <memset>
42010ccc:	011c                	addi	a5,sp,128
42010cce:	ccbe                	sw	a5,88(sp)
42010cd0:	105c                	addi	a5,sp,36
42010cd2:	cebe                	sw	a5,92(sp)
42010cd4:	01a10793          	addi	a5,sp,26
42010cd8:	d0be                	sw	a5,96(sp)
42010cda:	caa6                	sw	s1,84(sp)
42010cdc:	00acc683          	lbu	a3,10(s9)
42010ce0:	008cd603          	lhu	a2,8(s9)
42010ce4:	42011737          	lui	a4,0x42011
42010ce8:	00d036b3          	snez	a3,a3
42010cec:	08dc                	addi	a5,sp,84
42010cee:	42070713          	addi	a4,a4,1056 # 42011420 <custom_flac_output>
42010cf2:	00bc8593          	addi	a1,s9,11
42010cf6:	06810813          	addi	a6,sp,104
42010cfa:	855e                	mv	a0,s7
42010cfc:	451230ef          	jal	4203494c <custom_flac_decoder_feed>
42010d00:	47ca                	lw	a5,144(sp)
42010d02:	5726                	lw	a4,104(sp)
42010d04:	465a                	lw	a2,148(sp)
42010d06:	55b6                	lw	a1,108(sp)
42010d08:	568a                	lw	a3,160(sp)
42010d0a:	973e                	add	a4,a4,a5
42010d0c:	842a                	mv	s0,a0
42010d0e:	5546                	lw	a0,112(sp)
42010d10:	962e                	add	a2,a2,a1
42010d12:	00f737b3          	sltu	a5,a4,a5
42010d16:	97b2                	add	a5,a5,a2
42010d18:	55d6                	lw	a1,116(sp)
42010d1a:	561a                	lw	a2,164(sp)
42010d1c:	96aa                	add	a3,a3,a0
42010d1e:	c93a                	sw	a4,144(sp)
42010d20:	cb3e                	sw	a5,148(sp)
42010d22:	d136                	sw	a3,160(sp)
42010d24:	00b67363          	bgeu	a2,a1,42010d2a <decoder_task+0x5b8>
42010d28:	d32e                	sw	a1,164(sp)
42010d2a:	57aa                	lw	a5,168(sp)
42010d2c:	5766                	lw	a4,120(sp)
42010d2e:	97ba                	add	a5,a5,a4
42010d30:	d53e                	sw	a5,168(sp)
42010d32:	4a0d8963          	beqz	s11,420111e4 <decoder_task+0xa72>
42010d36:	4d85                	li	s11,1
42010d38:	fe370097          	auipc	ra,0xfe370
42010d3c:	602080e7          	jalr	1538(ra) # 4038133a <esp_timer_get_time>
42010d40:	862e                	mv	a2,a1
42010d42:	85aa                	mv	a1,a0
42010d44:	0108                	addi	a0,sp,128
42010d46:	8f4ff0ef          	jal	4200fe3a <decode_stats_report>
42010d4a:	00045b63          	bgez	s0,42010d60 <decoder_task+0x5ee>
42010d4e:	af0a8793          	addi	a5,s5,-1296
42010d52:	0330000f          	fence	rw,rw
42010d56:	439c                	lw	a5,0(a5)
42010d58:	0230000f          	fence	r,rw
42010d5c:	62978e63          	beq	a5,s1,42011398 <decoder_task+0xc26>
42010d60:	8566                	mv	a0,s9
42010d62:	85e2                	mv	a1,s8
42010d64:	96dff0ef          	jal	420106d0 <return_decoded_packet>
42010d68:	4b0d                	li	s6,3
42010d6a:	4401                	li	s0,0
42010d6c:	bc9d                	j	420107e2 <decoder_task+0x70>
42010d6e:	6589                	lui	a1,0x2
42010d70:	36ba0263          	beq	s4,a1,420110d4 <decoder_task+0x962>
42010d74:	854a                	mv	a0,s2
42010d76:	f76f70ef          	jal	420084ec <realloc>
42010d7a:	842a                	mv	s0,a0
42010d7c:	68050863          	beqz	a0,4201140c <decoder_task+0xc9a>
42010d80:	204347b7          	lui	a5,0x20434
42010d84:	14178793          	addi	a5,a5,321 # 20434141 <CSR_UINTSTATUS+0x20433490>
42010d88:	d682                	sw	zero,108(sp)
42010d8a:	d882                	sw	zero,112(sp)
42010d8c:	da82                	sw	zero,116(sp)
42010d8e:	d4be                	sw	a5,104(sp)
42010d90:	7fc010ef          	jal	4201258c <native_aac_decoder_create>
42010d94:	89aa                	mv	s3,a0
42010d96:	46050763          	beqz	a0,42011204 <decoder_task+0xa92>
42010d9a:	8922                	mv	s2,s0
42010d9c:	6a09                	lui	s4,0x2
42010d9e:	4b81                	li	s7,0
42010da0:	4d81                	li	s11,0
42010da2:	b93d                	j	420109e0 <decoder_task+0x26e>
42010da4:	5d61                	li	s10,-8
42010da6:	c662                	sw	s8,12(sp)
42010da8:	e789                	bnez	a5,42010db2 <decoder_task+0x640>
42010daa:	05c14783          	lbu	a5,92(sp)
42010dae:	1c078f63          	beqz	a5,42010f8c <decoder_task+0x81a>
42010db2:	4781                	li	a5,0
42010db4:	4801                	li	a6,0
42010db6:	de3e                	sw	a5,60(sp)
42010db8:	c0c2                	sw	a6,64(sp)
42010dba:	da4a                	sw	s2,52(sp)
42010dbc:	dc52                	sw	s4,56(sp)
42010dbe:	d082                	sw	zero,96(sp)
42010dc0:	fe370097          	auipc	ra,0xfe370
42010dc4:	57a080e7          	jalr	1402(ra) # 4038133a <esp_timer_get_time>
42010dc8:	842a                	mv	s0,a0
42010dca:	4572                	lw	a0,28(sp)
42010dcc:	1850                	addi	a2,sp,52
42010dce:	08cc                	addi	a1,sp,84
42010dd0:	789140ef          	jal	42025d58 <__wrap_esp_audio_simple_dec_process>
42010dd4:	8c2a                	mv	s8,a0
42010dd6:	fe370097          	auipc	ra,0xfe370
42010dda:	564080e7          	jalr	1380(ra) # 4038133a <esp_timer_get_time>
42010dde:	47ca                	lw	a5,144(sp)
42010de0:	46da                	lw	a3,148(sp)
42010de2:	8d01                	sub	a0,a0,s0
42010de4:	00a78733          	add	a4,a5,a0
42010de8:	00f737b3          	sltu	a5,a4,a5
42010dec:	97b6                	add	a5,a5,a3
42010dee:	cb3e                	sw	a5,148(sp)
42010df0:	578a                	lw	a5,160(sp)
42010df2:	c93a                	sw	a4,144(sp)
42010df4:	571a                	lw	a4,164(sp)
42010df6:	0785                	addi	a5,a5,1
42010df8:	d13e                	sw	a5,160(sp)
42010dfa:	00a77363          	bgeu	a4,a0,42010e00 <decoder_task+0x68e>
42010dfe:	d32a                	sw	a0,164(sp)
42010e00:	8bfd                	andi	a5,a5,31
42010e02:	1e078c63          	beqz	a5,42010ffa <decoder_task+0x888>
42010e06:	af0a8793          	addi	a5,s5,-1296
42010e0a:	0330000f          	fence	rw,rw
42010e0e:	439c                	lw	a5,0(a5)
42010e10:	0230000f          	fence	r,rw
42010e14:	16979c63          	bne	a5,s1,42010f8c <decoder_task+0x81a>
42010e18:	1dac0563          	beq	s8,s10,42010fe2 <decoder_task+0x870>
42010e1c:	4e0c1b63          	bnez	s8,42011312 <decoder_task+0xba0>
42010e20:	5786                	lw	a5,96(sp)
42010e22:	4766                	lw	a4,88(sp)
42010e24:	34f76463          	bltu	a4,a5,4201116c <decoder_task+0x9fa>
42010e28:	8f1d                	sub	a4,a4,a5
42010e2a:	56aa                	lw	a3,168(sp)
42010e2c:	ccba                	sw	a4,88(sp)
42010e2e:	4756                	lw	a4,84(sp)
42010e30:	96be                	add	a3,a3,a5
42010e32:	d536                	sw	a3,168(sp)
42010e34:	97ba                	add	a5,a5,a4
42010e36:	4706                	lw	a4,64(sp)
42010e38:	cabe                	sw	a5,84(sp)
42010e3a:	12070363          	beqz	a4,42010f60 <decoder_task+0x7ee>
42010e3e:	4572                	lw	a0,28(sp)
42010e40:	00cc                	addi	a1,sp,68
42010e42:	c282                	sw	zero,68(sp)
42010e44:	c482                	sw	zero,72(sp)
42010e46:	c682                	sw	zero,76(sp)
42010e48:	c882                	sw	zero,80(sp)
42010e4a:	579250ef          	jal	42036bc2 <esp_audio_simple_dec_get_info>
42010e4e:	1a051a63          	bnez	a0,42011002 <decoder_task+0x890>
42010e52:	4782                	lw	a5,0(sp)
42010e54:	00f10da3          	sb	a5,27(sp)
42010e58:	4789                	li	a5,2
42010e5a:	44fb0e63          	beq	s6,a5,420112b6 <decoder_task+0xb44>
42010e5e:	4791                	li	a5,4
42010e60:	44fb0663          	beq	s6,a5,420112ac <decoder_task+0xb3a>
42010e64:	3c126737          	lui	a4,0x3c126
42010e68:	4785                	li	a5,1
42010e6a:	80070593          	addi	a1,a4,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
42010e6e:	38fb1663          	bne	s6,a5,420111fa <decoder_task+0xa88>
42010e72:	af0a8793          	addi	a5,s5,-1296
42010e76:	0330000f          	fence	rw,rw
42010e7a:	439c                	lw	a5,0(a5)
42010e7c:	0230000f          	fence	r,rw
42010e80:	06979463          	bne	a5,s1,42010ee8 <decoder_task+0x776>
42010e84:	4796                	lw	a5,68(sp)
42010e86:	c3b5                	beqz	a5,42010eea <decoder_task+0x778>
42010e88:	04914683          	lbu	a3,73(sp)
42010e8c:	ceb1                	beqz	a3,42010ee8 <decoder_task+0x776>
42010e8e:	04815703          	lhu	a4,72(sp)
42010e92:	04814503          	lbu	a0,72(sp)
42010e96:	00875613          	srli	a2,a4,0x8
42010e9a:	0722                	slli	a4,a4,0x8
42010e9c:	963a                	add	a2,a2,a4
42010e9e:	c529                	beqz	a0,42010ee8 <decoder_task+0x776>
42010ea0:	06012b23          	sw	zero,118(sp)
42010ea4:	06012923          	sw	zero,114(sp)
42010ea8:	d23e                	sw	a5,36(sp)
42010eaa:	06c11823          	sh	a2,112(sp)
42010eae:	d6be                	sw	a5,108(sp)
42010eb0:	4626                	lw	a2,72(sp)
42010eb2:	dabe                	sw	a5,116(sp)
42010eb4:	3fc957b7          	lui	a5,0x3fc95
42010eb8:	4746                	lw	a4,80(sp)
42010eba:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42010ebe:	06d10c23          	sb	a3,120(sp)
42010ec2:	4782                	lw	a5,0(sp)
42010ec4:	46b6                	lw	a3,76(sp)
42010ec6:	06011d23          	sh	zero,122(sp)
42010eca:	d4ae                	sw	a1,104(sp)
42010ecc:	d432                	sw	a2,40(sp)
42010ece:	4405                	li	s0,1
42010ed0:	10b0                	addi	a2,sp,104
42010ed2:	85a6                	mv	a1,s1
42010ed4:	06f10d23          	sb	a5,122(sp)
42010ed8:	d636                	sw	a3,44(sp)
42010eda:	d83a                	sw	a4,48(sp)
42010edc:	00810d23          	sb	s0,26(sp)
42010ee0:	2f0040ef          	jal	420151d0 <native_state_set_stream_info>
42010ee4:	87a2                	mv	a5,s0
42010ee6:	a011                	j	42010eea <decoder_task+0x778>
42010ee8:	4781                	li	a5,0
42010eea:	45b6                	lw	a1,76(sp)
42010eec:	8526                	mv	a0,s1
42010eee:	00f10d23          	sb	a5,26(sp)
42010ef2:	c6aff0ef          	jal	4201035c <state_set_decoder_bitrate>
42010ef6:	01a14783          	lbu	a5,26(sp)
42010efa:	c3bd                	beqz	a5,42010f60 <decoder_task+0x7ee>
42010efc:	1c0d8e63          	beqz	s11,420110d8 <decoder_task+0x966>
42010f00:	02814503          	lbu	a0,40(sp)
42010f04:	02914783          	lbu	a5,41(sp)
42010f08:	4406                	lw	s0,64(sp)
42010f0a:	051d                	addi	a0,a0,7
42010f0c:	810d                	srli	a0,a0,0x3
42010f0e:	02f50533          	mul	a0,a0,a5
42010f12:	cd15                	beqz	a0,42010f4e <decoder_task+0x7dc>
42010f14:	5612                	lw	a2,36(sp)
42010f16:	ce05                	beqz	a2,42010f4e <decoder_task+0x7dc>
42010f18:	02a45533          	divu	a0,s0,a0
42010f1c:	000f47b7          	lui	a5,0xf4
42010f20:	24078793          	addi	a5,a5,576 # f4240 <CSR_UINTSTATUS+0xf358f>
42010f24:	4681                	li	a3,0
42010f26:	02f535b3          	mulhu	a1,a0,a5
42010f2a:	02f50533          	mul	a0,a0,a5
42010f2e:	fdff0097          	auipc	ra,0xfdff0
42010f32:	97e080e7          	jalr	-1666(ra) # 400008ac <__udivdi3>
42010f36:	47ea                	lw	a5,152(sp)
42010f38:	46fa                	lw	a3,156(sp)
42010f3a:	573a                	lw	a4,172(sp)
42010f3c:	953e                	add	a0,a0,a5
42010f3e:	96ae                	add	a3,a3,a1
42010f40:	00f537b3          	sltu	a5,a0,a5
42010f44:	97b6                	add	a5,a5,a3
42010f46:	9722                	add	a4,a4,s0
42010f48:	cf3e                	sw	a5,156(sp)
42010f4a:	cd2a                	sw	a0,152(sp)
42010f4c:	d73a                	sw	a4,172(sp)
42010f4e:	86a2                	mv	a3,s0
42010f50:	864a                	mv	a2,s2
42010f52:	104c                	addi	a1,sp,36
42010f54:	8526                	mv	a0,s1
42010f56:	ac0ff0ef          	jal	42010216 <send_pcm>
42010f5a:	8daa                	mv	s11,a0
42010f5c:	38050563          	beqz	a0,420112e6 <decoder_task+0xb74>
42010f60:	fe370097          	auipc	ra,0xfe370
42010f64:	3da080e7          	jalr	986(ra) # 4038133a <esp_timer_get_time>
42010f68:	862e                	mv	a2,a1
42010f6a:	85aa                	mv	a1,a0
42010f6c:	0108                	addi	a0,sp,128
42010f6e:	ecdfe0ef          	jal	4200fe3a <decode_stats_report>
42010f72:	4706                	lw	a4,64(sp)
42010f74:	5786                	lw	a5,96(sp)
42010f76:	05c14683          	lbu	a3,92(sp)
42010f7a:	8fd9                	or	a5,a5,a4
42010f7c:	efa9                	bnez	a5,42010fd6 <decoder_task+0x864>
42010f7e:	3a068b63          	beqz	a3,42011334 <decoder_task+0xbc2>
42010f82:	4701                	li	a4,0
42010f84:	47e6                	lw	a5,88(sp)
42010f86:	8f5d                	or	a4,a4,a5
42010f88:	e20710e3          	bnez	a4,42010da8 <decoder_task+0x636>
42010f8c:	4c32                	lw	s8,12(sp)
42010f8e:	b9a1                	j	42010be6 <decoder_task+0x474>
42010f90:	c40697e3          	bnez	a3,42010bde <decoder_task+0x46c>
42010f94:	47e6                	lw	a5,88(sp)
42010f96:	a80790e3          	bnez	a5,42010a16 <decoder_task+0x2a4>
42010f9a:	b1b1                	j	42010be6 <decoder_task+0x474>
42010f9c:	5706                	lw	a4,96(sp)
42010f9e:	47d6                	lw	a5,84(sp)
42010fa0:	56aa                	lw	a3,168(sp)
42010fa2:	5472                	lw	s0,60(sp)
42010fa4:	97ba                	add	a5,a5,a4
42010fa6:	cabe                	sw	a5,84(sp)
42010fa8:	47e6                	lw	a5,88(sp)
42010faa:	96ba                	add	a3,a3,a4
42010fac:	d536                	sw	a3,168(sp)
42010fae:	8f99                	sub	a5,a5,a4
42010fb0:	ccbe                	sw	a5,88(sp)
42010fb2:	308a7763          	bgeu	s4,s0,420112c0 <decoder_task+0xb4e>
42010fb6:	85a2                	mv	a1,s0
42010fb8:	854a                	mv	a0,s2
42010fba:	d32f70ef          	jal	420084ec <realloc>
42010fbe:	30050163          	beqz	a0,420112c0 <decoder_task+0xb4e>
42010fc2:	8a22                	mv	s4,s0
42010fc4:	892a                	mv	s2,a0
42010fc6:	bc81                	j	42010a16 <decoder_task+0x2a4>
42010fc8:	4505                	li	a0,1
42010fca:	560ff0ef          	jal	4211052a <vTaskDelay>
42010fce:	bc71                	j	42010a6a <decoder_task+0x2f8>
42010fd0:	00010d23          	sb	zero,26(sp)
42010fd4:	b6d5                	j	42010bb8 <decoder_task+0x446>
42010fd6:	f6dd                	bnez	a3,42010f84 <decoder_task+0x812>
42010fd8:	47e6                	lw	a5,88(sp)
42010fda:	dc079ce3          	bnez	a5,42010db2 <decoder_task+0x640>
42010fde:	4c32                	lw	s8,12(sp)
42010fe0:	b119                	j	42010be6 <decoder_task+0x474>
42010fe2:	5472                	lw	s0,60(sp)
42010fe4:	2c8a7e63          	bgeu	s4,s0,420112c0 <decoder_task+0xb4e>
42010fe8:	85a2                	mv	a1,s0
42010fea:	854a                	mv	a0,s2
42010fec:	d00f70ef          	jal	420084ec <realloc>
42010ff0:	2c050863          	beqz	a0,420112c0 <decoder_task+0xb4e>
42010ff4:	892a                	mv	s2,a0
42010ff6:	8a22                	mv	s4,s0
42010ff8:	bb6d                	j	42010db2 <decoder_task+0x640>
42010ffa:	4505                	li	a0,1
42010ffc:	52eff0ef          	jal	4211052a <vTaskDelay>
42011000:	b519                	j	42010e06 <decoder_task+0x694>
42011002:	00010d23          	sb	zero,26(sp)
42011006:	bfa9                	j	42010f60 <decoder_task+0x7ee>
42011008:	3c1267b7          	lui	a5,0x3c126
4201100c:	b0878513          	addi	a0,a5,-1272 # 3c125b08 <_esp_trace_encoder_array_end+0x59e8>
42011010:	9a2ff0ef          	jal	420101b2 <log_runtime_memory>
42011014:	b6a9                	j	42010b5e <decoder_task+0x3ec>
42011016:	846a                	mv	s0,s10
42011018:	4a09                	li	s4,2
4201101a:	fe377097          	auipc	ra,0xfe377
4201101e:	3a0080e7          	jalr	928(ra) # 403883ba <esp_log_timestamp>
42011022:	2f4b0a63          	beq	s6,s4,42011316 <decoder_task+0xba4>
42011026:	4791                	li	a5,4
42011028:	2efb0c63          	beq	s6,a5,42011320 <decoder_task+0xbae>
4201102c:	3c1267b7          	lui	a5,0x3c126
42011030:	4705                	li	a4,1
42011032:	80078793          	addi	a5,a5,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
42011036:	00eb0663          	beq	s6,a4,42011042 <decoder_task+0x8d0>
4201103a:	3c1267b7          	lui	a5,0x3c126
4201103e:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
42011042:	3c126737          	lui	a4,0x3c126
42011046:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
4201104a:	3c126637          	lui	a2,0x3c126
4201104e:	86aa                	mv	a3,a0
42011050:	85ba                	mv	a1,a4
42011052:	8822                	mv	a6,s0
42011054:	b3c60613          	addi	a2,a2,-1220 # 3c125b3c <_esp_trace_encoder_array_end+0x5a1c>
42011058:	4509                	li	a0,2
4201105a:	fe377097          	auipc	ra,0xfe377
4201105e:	258080e7          	jalr	600(ra) # 403882b2 <esp_log>
42011062:	3fc957b7          	lui	a5,0x3fc95
42011066:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
4201106a:	3c1267b7          	lui	a5,0x3c126
4201106e:	9e478693          	addi	a3,a5,-1564 # 3c1259e4 <_esp_trace_encoder_array_end+0x58c4>
42011072:	85a6                	mv	a1,s1
42011074:	4601                	li	a2,0
42011076:	07a040ef          	jal	420150f0 <native_state_set_audio>
4201107a:	8c26                	mv	s8,s1
4201107c:	4572                	lw	a0,28(sp)
4201107e:	c119                	beqz	a0,42011084 <decoder_task+0x912>
42011080:	3bb250ef          	jal	42036c3a <esp_audio_simple_dec_close>
42011084:	ce02                	sw	zero,28(sp)
42011086:	00098563          	beqz	s3,42011090 <decoder_task+0x91e>
4201108a:	854e                	mv	a0,s3
4201108c:	52c010ef          	jal	420125b8 <native_aac_decoder_destroy>
42011090:	854a                	mv	a0,s2
42011092:	c5ef70ef          	jal	420084f0 <cfree>
42011096:	4981                	li	s3,0
42011098:	4a01                	li	s4,0
4201109a:	4901                	li	s2,0
4201109c:	be99                	j	42010bf2 <decoder_task+0x480>
4201109e:	854e                	mv	a0,s3
420110a0:	0dd010ef          	jal	4201297c <native_aac_decoder_source_channels>
420110a4:	01b14683          	lbu	a3,27(sp)
420110a8:	0ff57513          	zext.b	a0,a0
420110ac:	b42d                	j	42010ad6 <decoder_task+0x364>
420110ae:	204747b7          	lui	a5,0x20474
420110b2:	74f78793          	addi	a5,a5,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
420110b6:	086c                	addi	a1,sp,28
420110b8:	10a8                	addi	a0,sp,104
420110ba:	d4be                	sw	a5,104(sp)
420110bc:	311140ef          	jal	42025bcc <__wrap_esp_audio_simple_dec_open>
420110c0:	842a                	mv	s0,a0
420110c2:	18051063          	bnez	a0,42011242 <decoder_task+0xad0>
420110c6:	4bf2                	lw	s7,28(sp)
420110c8:	4d81                	li	s11,0
420110ca:	8c0b8de3          	beqz	s7,420109a4 <decoder_task+0x232>
420110ce:	4981                	li	s3,0
420110d0:	4b81                	li	s7,0
420110d2:	b239                	j	420109e0 <decoder_task+0x26e>
420110d4:	844a                	mv	s0,s2
420110d6:	b16d                	j	42010d80 <decoder_task+0x60e>
420110d8:	3c1267b7          	lui	a5,0x3c126
420110dc:	b0878513          	addi	a0,a5,-1272 # 3c125b08 <_esp_trace_encoder_array_end+0x59e8>
420110e0:	8d2ff0ef          	jal	420101b2 <log_runtime_memory>
420110e4:	bd31                	j	42010f00 <decoder_task+0x78e>
420110e6:	d682                	sw	zero,108(sp)
420110e8:	d882                	sw	zero,112(sp)
420110ea:	da82                	sw	zero,116(sp)
420110ec:	82dff06f          	j	42010918 <decoder_task+0x1a6>
420110f0:	fe377097          	auipc	ra,0xfe377
420110f4:	2ca080e7          	jalr	714(ra) # 403883ba <esp_log_timestamp>
420110f8:	4791                	li	a5,4
420110fa:	4405                	li	s0,1
420110fc:	86aa                	mv	a3,a0
420110fe:	1cfb0f63          	beq	s6,a5,420112dc <decoder_task+0xb6a>
42011102:	3c1267b7          	lui	a5,0x3c126
42011106:	80078793          	addi	a5,a5,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
4201110a:	008b0663          	beq	s6,s0,42011116 <decoder_task+0x9a4>
4201110e:	3c1267b7          	lui	a5,0x3c126
42011112:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
42011116:	3c126737          	lui	a4,0x3c126
4201111a:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
4201111e:	3c126637          	lui	a2,0x3c126
42011122:	85ba                	mv	a1,a4
42011124:	a6c60613          	addi	a2,a2,-1428 # 3c125a6c <_esp_trace_encoder_array_end+0x594c>
42011128:	4505                	li	a0,1
4201112a:	fe377097          	auipc	ra,0xfe377
4201112e:	188080e7          	jalr	392(ra) # 403882b2 <esp_log>
42011132:	3fc957b7          	lui	a5,0x3fc95
42011136:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
4201113a:	3c1267b7          	lui	a5,0x3c126
4201113e:	9c878693          	addi	a3,a5,-1592 # 3c1259c8 <_esp_trace_encoder_array_end+0x58a8>
42011142:	85a6                	mv	a1,s1
42011144:	4601                	li	a2,0
42011146:	7ab030ef          	jal	420150f0 <native_state_set_audio>
4201114a:	3fc957b7          	lui	a5,0x3fc95
4201114e:	afc7a503          	lw	a0,-1284(a5) # 3fc94afc <s_encoded>
42011152:	85e6                	mv	a1,s9
42011154:	8c26                	mv	s8,s1
42011156:	646650ef          	jal	4207679c <vRingbufferReturnItem>
4201115a:	4981                	li	s3,0
4201115c:	4d81                	li	s11,0
4201115e:	4b81                	li	s7,0
42011160:	4401                	li	s0,0
42011162:	e80ff06f          	j	420107e2 <decoder_task+0x70>
42011166:	be0b8de3          	beqz	s7,42010d60 <decoder_task+0x5ee>
4201116a:	be91                	j	42010cbe <decoder_task+0x54c>
4201116c:	fe377097          	auipc	ra,0xfe377
42011170:	24e080e7          	jalr	590(ra) # 403883ba <esp_log_timestamp>
42011174:	4789                	li	a5,2
42011176:	4405                	li	s0,1
42011178:	0efb0063          	beq	s6,a5,42011258 <decoder_task+0xae6>
4201117c:	4791                	li	a5,4
4201117e:	1afb0663          	beq	s6,a5,4201132a <decoder_task+0xbb8>
42011182:	3c1267b7          	lui	a5,0x3c126
42011186:	80078793          	addi	a5,a5,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
4201118a:	008b0663          	beq	s6,s0,42011196 <decoder_task+0xa24>
4201118e:	3c1267b7          	lui	a5,0x3c126
42011192:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
42011196:	48e6                	lw	a7,88(sp)
42011198:	5806                	lw	a6,96(sp)
4201119a:	3c126737          	lui	a4,0x3c126
4201119e:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
420111a2:	3c126637          	lui	a2,0x3c126
420111a6:	86aa                	mv	a3,a0
420111a8:	85ba                	mv	a1,a4
420111aa:	b6060613          	addi	a2,a2,-1184 # 3c125b60 <_esp_trace_encoder_array_end+0x5a40>
420111ae:	4505                	li	a0,1
420111b0:	fe377097          	auipc	ra,0xfe377
420111b4:	102080e7          	jalr	258(ra) # 403882b2 <esp_log>
420111b8:	3fc957b7          	lui	a5,0x3fc95
420111bc:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
420111c0:	3c1267b7          	lui	a5,0x3c126
420111c4:	b9c78693          	addi	a3,a5,-1124 # 3c125b9c <_esp_trace_encoder_array_end+0x5a7c>
420111c8:	85a6                	mv	a1,s1
420111ca:	4601                	li	a2,0
420111cc:	725030ef          	jal	420150f0 <native_state_set_audio>
420111d0:	8c26                	mv	s8,s1
420111d2:	b56d                	j	4201107c <decoder_task+0x90a>
420111d4:	8542                	mv	a0,a6
420111d6:	b2b9                	j	42010b24 <decoder_task+0x3b2>
420111d8:	3c1267b7          	lui	a5,0x3c126
420111dc:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
420111e0:	f6eff06f          	j	4201094e <decoder_task+0x1dc>
420111e4:	01a14d83          	lbu	s11,26(sp)
420111e8:	b40d88e3          	beqz	s11,42010d38 <decoder_task+0x5c6>
420111ec:	3c1267b7          	lui	a5,0x3c126
420111f0:	ac478513          	addi	a0,a5,-1340 # 3c125ac4 <_esp_trace_encoder_array_end+0x59a4>
420111f4:	fbffe0ef          	jal	420101b2 <log_runtime_memory>
420111f8:	be3d                	j	42010d36 <decoder_task+0x5c4>
420111fa:	3c1267b7          	lui	a5,0x3c126
420111fe:	80478593          	addi	a1,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
42011202:	b985                	j	42010e72 <decoder_task+0x700>
42011204:	fe377097          	auipc	ra,0xfe377
42011208:	1b6080e7          	jalr	438(ra) # 403883ba <esp_log_timestamp>
4201120c:	3c1267b7          	lui	a5,0x3c126
42011210:	80c78713          	addi	a4,a5,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
42011214:	3c126637          	lui	a2,0x3c126
42011218:	3c1257b7          	lui	a5,0x3c125
4201121c:	86aa                	mv	a3,a0
4201121e:	7f078793          	addi	a5,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
42011222:	85ba                	mv	a1,a4
42011224:	a9c60613          	addi	a2,a2,-1380 # 3c125a9c <_esp_trace_encoder_array_end+0x597c>
42011228:	5879                	li	a6,-2
4201122a:	4505                	li	a0,1
4201122c:	fe377097          	auipc	ra,0xfe377
42011230:	086080e7          	jalr	134(ra) # 403882b2 <esp_log>
42011234:	3c1267b7          	lui	a5,0x3c126
42011238:	8922                	mv	s2,s0
4201123a:	9c878693          	addi	a3,a5,-1592 # 3c1259c8 <_esp_trace_encoder_array_end+0x58a8>
4201123e:	f3cff06f          	j	4201097a <decoder_task+0x208>
42011242:	fe377097          	auipc	ra,0xfe377
42011246:	178080e7          	jalr	376(ra) # 403883ba <esp_log_timestamp>
4201124a:	3c1257b7          	lui	a5,0x3c125
4201124e:	86aa                	mv	a3,a0
42011250:	7fc78793          	addi	a5,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
42011254:	efaff06f          	j	4201094e <decoder_task+0x1dc>
42011258:	3c1257b7          	lui	a5,0x3c125
4201125c:	7f078793          	addi	a5,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
42011260:	bf1d                	j	42011196 <decoder_task+0xa24>
42011262:	fe377097          	auipc	ra,0xfe377
42011266:	158080e7          	jalr	344(ra) # 403883ba <esp_log_timestamp>
4201126a:	3c1267b7          	lui	a5,0x3c126
4201126e:	80c78713          	addi	a4,a5,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
42011272:	3c1267b7          	lui	a5,0x3c126
42011276:	86aa                	mv	a3,a0
42011278:	85ba                	mv	a1,a4
4201127a:	a3878613          	addi	a2,a5,-1480 # 3c125a38 <_esp_trace_encoder_array_end+0x5918>
4201127e:	4505                	li	a0,1
42011280:	fe377097          	auipc	ra,0xfe377
42011284:	032080e7          	jalr	50(ra) # 403882b2 <esp_log>
42011288:	3fc957b7          	lui	a5,0x3fc95
4201128c:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42011290:	3c1267b7          	lui	a5,0x3c126
42011294:	9c878693          	addi	a3,a5,-1592 # 3c1259c8 <_esp_trace_encoder_array_end+0x58a8>
42011298:	85a6                	mv	a1,s1
4201129a:	4601                	li	a2,0
4201129c:	655030ef          	jal	420150f0 <native_state_set_audio>
420112a0:	8c26                	mv	s8,s1
420112a2:	4981                	li	s3,0
420112a4:	4901                	li	s2,0
420112a6:	4a01                	li	s4,0
420112a8:	4d81                	li	s11,0
420112aa:	bc5d                	j	42010d60 <decoder_task+0x5ee>
420112ac:	3c1257b7          	lui	a5,0x3c125
420112b0:	7fc78593          	addi	a1,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
420112b4:	be7d                	j	42010e72 <decoder_task+0x700>
420112b6:	3c1257b7          	lui	a5,0x3c125
420112ba:	7f078593          	addi	a1,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
420112be:	be55                	j	42010e72 <decoder_task+0x700>
420112c0:	3fc957b7          	lui	a5,0x3fc95
420112c4:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
420112c8:	3c1267b7          	lui	a5,0x3c126
420112cc:	b2478693          	addi	a3,a5,-1244 # 3c125b24 <_esp_trace_encoder_array_end+0x5a04>
420112d0:	4601                	li	a2,0
420112d2:	85a6                	mv	a1,s1
420112d4:	61d030ef          	jal	420150f0 <native_state_set_audio>
420112d8:	8c26                	mv	s8,s1
420112da:	b34d                	j	4201107c <decoder_task+0x90a>
420112dc:	3c1257b7          	lui	a5,0x3c125
420112e0:	7fc78793          	addi	a5,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
420112e4:	bd0d                	j	42011116 <decoder_task+0x9a4>
420112e6:	4c32                	lw	s8,12(sp)
420112e8:	fe377097          	auipc	ra,0xfe377
420112ec:	0d2080e7          	jalr	210(ra) # 403883ba <esp_log_timestamp>
420112f0:	3c1267b7          	lui	a5,0x3c126
420112f4:	80c78713          	addi	a4,a5,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
420112f8:	3c1267b7          	lui	a5,0x3c126
420112fc:	86aa                	mv	a3,a0
420112fe:	85ba                	mv	a1,a4
42011300:	bb078613          	addi	a2,a5,-1104 # 3c125bb0 <_esp_trace_encoder_array_end+0x5a90>
42011304:	4509                	li	a0,2
42011306:	fe377097          	auipc	ra,0xfe377
4201130a:	fac080e7          	jalr	-84(ra) # 403882b2 <esp_log>
4201130e:	4d85                	li	s11,1
42011310:	b8d9                	j	42010be6 <decoder_task+0x474>
42011312:	8462                	mv	s0,s8
42011314:	b311                	j	42011018 <decoder_task+0x8a6>
42011316:	3c1257b7          	lui	a5,0x3c125
4201131a:	7f078793          	addi	a5,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
4201131e:	b315                	j	42011042 <decoder_task+0x8d0>
42011320:	3c1257b7          	lui	a5,0x3c125
42011324:	7fc78793          	addi	a5,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
42011328:	bb29                	j	42011042 <decoder_task+0x8d0>
4201132a:	3c1257b7          	lui	a5,0x3c125
4201132e:	7fc78793          	addi	a5,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
42011332:	b595                	j	42011196 <decoder_task+0xa24>
42011334:	fe377097          	auipc	ra,0xfe377
42011338:	086080e7          	jalr	134(ra) # 403883ba <esp_log_timestamp>
4201133c:	4789                	li	a5,2
4201133e:	4405                	li	s0,1
42011340:	86aa                	mv	a3,a0
42011342:	0afb0563          	beq	s6,a5,420113ec <decoder_task+0xc7a>
42011346:	4791                	li	a5,4
42011348:	0afb0d63          	beq	s6,a5,42011402 <decoder_task+0xc90>
4201134c:	3c1267b7          	lui	a5,0x3c126
42011350:	80078793          	addi	a5,a5,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
42011354:	008b0663          	beq	s6,s0,42011360 <decoder_task+0xbee>
42011358:	3c1267b7          	lui	a5,0x3c126
4201135c:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
42011360:	3c126737          	lui	a4,0x3c126
42011364:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
42011368:	3c126637          	lui	a2,0x3c126
4201136c:	85ba                	mv	a1,a4
4201136e:	bd060613          	addi	a2,a2,-1072 # 3c125bd0 <_esp_trace_encoder_array_end+0x5ab0>
42011372:	4505                	li	a0,1
42011374:	fe377097          	auipc	ra,0xfe377
42011378:	f3e080e7          	jalr	-194(ra) # 403882b2 <esp_log>
4201137c:	3fc957b7          	lui	a5,0x3fc95
42011380:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
42011384:	3c1267b7          	lui	a5,0x3c126
42011388:	c0078693          	addi	a3,a5,-1024 # 3c125c00 <_esp_trace_encoder_array_end+0x5ae0>
4201138c:	85a6                	mv	a1,s1
4201138e:	4601                	li	a2,0
42011390:	561030ef          	jal	420150f0 <native_state_set_audio>
42011394:	8c26                	mv	s8,s1
42011396:	b1dd                	j	4201107c <decoder_task+0x90a>
42011398:	fe377097          	auipc	ra,0xfe377
4201139c:	022080e7          	jalr	34(ra) # 403883ba <esp_log_timestamp>
420113a0:	3c126737          	lui	a4,0x3c126
420113a4:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
420113a8:	3c126637          	lui	a2,0x3c126
420113ac:	86aa                	mv	a3,a0
420113ae:	87a2                	mv	a5,s0
420113b0:	85ba                	mv	a1,a4
420113b2:	adc60613          	addi	a2,a2,-1316 # 3c125adc <_esp_trace_encoder_array_end+0x59bc>
420113b6:	4509                	li	a0,2
420113b8:	fe377097          	auipc	ra,0xfe377
420113bc:	efa080e7          	jalr	-262(ra) # 403882b2 <esp_log>
420113c0:	3c126737          	lui	a4,0x3c126
420113c4:	0419                	addi	s0,s0,6 # 3006 <CSR_UINTSTATUS+0x2355>
420113c6:	4785                	li	a5,1
420113c8:	9e470693          	addi	a3,a4,-1564 # 3c1259e4 <_esp_trace_encoder_array_end+0x58c4>
420113cc:	0087e663          	bltu	a5,s0,420113d8 <decoder_task+0xc66>
420113d0:	3c1267b7          	lui	a5,0x3c126
420113d4:	9c878693          	addi	a3,a5,-1592 # 3c1259c8 <_esp_trace_encoder_array_end+0x58a8>
420113d8:	3fc957b7          	lui	a5,0x3fc95
420113dc:	b047a503          	lw	a0,-1276(a5) # 3fc94b04 <s_state>
420113e0:	4601                	li	a2,0
420113e2:	85a6                	mv	a1,s1
420113e4:	50d030ef          	jal	420150f0 <native_state_set_audio>
420113e8:	8c26                	mv	s8,s1
420113ea:	ba9d                	j	42010d60 <decoder_task+0x5ee>
420113ec:	3c1257b7          	lui	a5,0x3c125
420113f0:	7f078793          	addi	a5,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
420113f4:	b7b5                	j	42011360 <decoder_task+0xbee>
420113f6:	3c1267b7          	lui	a5,0x3c126
420113fa:	9c878693          	addi	a3,a5,-1592 # 3c1259c8 <_esp_trace_encoder_array_end+0x58a8>
420113fe:	d7cff06f          	j	4201097a <decoder_task+0x208>
42011402:	3c1257b7          	lui	a5,0x3c125
42011406:	7fc78793          	addi	a5,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
4201140a:	bf99                	j	42011360 <decoder_task+0xbee>
4201140c:	fe377097          	auipc	ra,0xfe377
42011410:	fae080e7          	jalr	-82(ra) # 403883ba <esp_log_timestamp>
42011414:	3c1257b7          	lui	a5,0x3c125
42011418:	86aa                	mv	a3,a0
4201141a:	7f078793          	addi	a5,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
4201141e:	b9e5                	j	42011116 <decoder_task+0x9a4>
