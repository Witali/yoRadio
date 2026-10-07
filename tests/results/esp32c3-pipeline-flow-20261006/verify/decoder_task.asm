
idf\esp32c3-oled-native\build-pipeline-profile\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42010c80 <decoder_task>:
42010c80:	712d                	addi	sp,sp,-288
42010c82:	10112e23          	sw	ra,284(sp)
42010c86:	10912a23          	sw	s1,276(sp)
42010c8a:	11212823          	sw	s2,272(sp)
42010c8e:	11312623          	sw	s3,268(sp)
42010c92:	11412423          	sw	s4,264(sp)
42010c96:	11512223          	sw	s5,260(sp)
42010c9a:	11612023          	sw	s6,256(sp)
42010c9e:	dfde                	sw	s7,252(sp)
42010ca0:	d9ea                	sw	s10,240(sp)
42010ca2:	d7ee                	sw	s11,236(sp)
42010ca4:	10812c23          	sw	s0,280(sp)
42010ca8:	dde2                	sw	s8,248(sp)
42010caa:	dbe6                	sw	s9,244(sp)
42010cac:	69d010ef          	jal	42012b48 <decoder_register_codecs>
42010cb0:	8d2a                	mv	s10,a0
42010cb2:	06000613          	li	a2,96
42010cb6:	0108                	addi	a0,sp,128
42010cb8:	4581                	li	a1,0
42010cba:	ce02                	sw	zero,28(sp)
42010cbc:	fdfef097          	auipc	ra,0xfdfef
42010cc0:	698080e7          	jalr	1688(ra) # 40000354 <memset>
42010cc4:	3fc95737          	lui	a4,0x3fc95
42010cc8:	000f47b7          	lui	a5,0xf4
42010ccc:	af070713          	addi	a4,a4,-1296 # 3fc94af0 <s_bitrate_updated_us>
42010cd0:	24078793          	addi	a5,a5,576 # f4240 <CSR_UINTSTATUS+0xf358f>
42010cd4:	d202                	sw	zero,36(sp)
42010cd6:	d402                	sw	zero,40(sp)
42010cd8:	d602                	sw	zero,44(sp)
42010cda:	d802                	sw	zero,48(sp)
42010cdc:	00010d23          	sb	zero,26(sp)
42010ce0:	c23a                	sw	a4,4(sp)
42010ce2:	c63e                	sw	a5,12(sp)
42010ce4:	4981                	li	s3,0
42010ce6:	4a01                	li	s4,0
42010ce8:	4901                	li	s2,0
42010cea:	4d81                	li	s11,0
42010cec:	4b01                	li	s6,0
42010cee:	c002                	sw	zero,0(sp)
42010cf0:	4481                	li	s1,0
42010cf2:	4b81                	li	s7,0
42010cf4:	3fc95ab7          	lui	s5,0x3fc95
42010cf8:	b08a8793          	addi	a5,s5,-1272 # 3fc94b08 <s_generation>
42010cfc:	0330000f          	fence	rw,rw
42010d00:	4380                	lw	s0,0(a5)
42010d02:	0230000f          	fence	r,rw
42010d06:	42940863          	beq	s0,s1,42011136 <decoder_task+0x4b6>
42010d0a:	3fc957b7          	lui	a5,0x3fc95
42010d0e:	b0478793          	addi	a5,a5,-1276 # 3fc94b04 <s_decoder_target_codec>
42010d12:	0330000f          	fence	rw,rw
42010d16:	4384                	lw	s1,0(a5)
42010d18:	0230000f          	fence	r,rw
42010d1c:	4572                	lw	a0,28(sp)
42010d1e:	c119                	beqz	a0,42010d24 <decoder_task+0xa4>
42010d20:	618280ef          	jal	42039338 <esp_audio_simple_dec_close>
42010d24:	854e                	mv	a0,s3
42010d26:	ce02                	sw	zero,28(sp)
42010d28:	683010ef          	jal	42012baa <native_aac_decoder_destroy>
42010d2c:	000b8563          	beqz	s7,42010d36 <decoder_task+0xb6>
42010d30:	855e                	mv	a0,s7
42010d32:	760240ef          	jal	42035492 <custom_flac_decoder_destroy>
42010d36:	4a048163          	beqz	s1,420111d8 <decoder_task+0x558>
42010d3a:	d202                	sw	zero,36(sp)
42010d3c:	d402                	sw	zero,40(sp)
42010d3e:	d602                	sw	zero,44(sp)
42010d40:	d802                	sw	zero,48(sp)
42010d42:	00010d23          	sb	zero,26(sp)
42010d46:	3fc957b7          	lui	a5,0x3fc95
42010d4a:	b0078793          	addi	a5,a5,-1280 # 3fc94b00 <s_decoder_released_generation>
42010d4e:	0310000f          	fence	rw,w
42010d52:	c380                	sw	s0,0(a5)
42010d54:	0330000f          	fence	rw,rw
42010d58:	4b81                	li	s7,0
42010d5a:	84a2                	mv	s1,s0
42010d5c:	c002                	sw	zero,0(sp)
42010d5e:	4b01                	li	s6,0
42010d60:	4d81                	li	s11,0
42010d62:	4981                	li	s3,0
42010d64:	3fc957b7          	lui	a5,0x3fc95
42010d68:	b147a403          	lw	s0,-1260(a5) # 3fc94b14 <s_encoded>
42010d6c:	4601                	li	a2,0
42010d6e:	100c                	addi	a1,sp,32
42010d70:	8522                	mv	a0,s0
42010d72:	d002                	sw	zero,32(sp)
42010d74:	0aa680ef          	jal	42078e1e <xRingbufferReceive>
42010d78:	8caa                	mv	s9,a0
42010d7a:	3e050463          	beqz	a0,42011162 <decoder_task+0x4e2>
42010d7e:	000ca703          	lw	a4,0(s9)
42010d82:	b08a8793          	addi	a5,s5,-1272
42010d86:	0330000f          	fence	rw,rw
42010d8a:	439c                	lw	a5,0(a5)
42010d8c:	0230000f          	fence	r,rw
42010d90:	42f71c63          	bne	a4,a5,420111c8 <decoder_task+0x548>
42010d94:	000ca783          	lw	a5,0(s9)
42010d98:	4702                	lw	a4,0(sp)
42010d9a:	42e78763          	beq	a5,a4,420111c8 <decoder_task+0x548>
42010d9e:	004ca703          	lw	a4,4(s9)
42010da2:	e709                	bnez	a4,42010dac <decoder_task+0x12c>
42010da4:	00acc703          	lbu	a4,10(s9)
42010da8:	54071463          	bnez	a4,420112f0 <decoder_task+0x670>
42010dac:	120d1763          	bnez	s10,42010eda <decoder_task+0x25a>
42010db0:	12978e63          	beq	a5,s1,42010eec <decoder_task+0x26c>
42010db4:	4572                	lw	a0,28(sp)
42010db6:	c119                	beqz	a0,42010dbc <decoder_task+0x13c>
42010db8:	580280ef          	jal	42039338 <esp_audio_simple_dec_close>
42010dbc:	854e                	mv	a0,s3
42010dbe:	ce02                	sw	zero,28(sp)
42010dc0:	5eb010ef          	jal	42012baa <native_aac_decoder_destroy>
42010dc4:	000b8563          	beqz	s7,42010dce <decoder_task+0x14e>
42010dc8:	855e                	mv	a0,s7
42010dca:	6c8240ef          	jal	42035492 <custom_flac_decoder_destroy>
42010dce:	4712                	lw	a4,4(sp)
42010dd0:	3fc957b7          	lui	a5,0x3fc95
42010dd4:	4801                	li	a6,0
42010dd6:	ae07ac23          	sw	zero,-1288(a5) # 3fc94af8 <s_published_bitrate_bps>
42010dda:	4781                	li	a5,0
42010ddc:	c31c                	sw	a5,0(a4)
42010dde:	000ca483          	lw	s1,0(s9)
42010de2:	004cab03          	lw	s6,4(s9)
42010de6:	01072223          	sw	a6,4(a4)
42010dea:	00010d23          	sb	zero,26(sp)
42010dee:	fe370097          	auipc	ra,0xfe370
42010df2:	54c080e7          	jalr	1356(ra) # 4038133a <esp_timer_get_time>
42010df6:	8d2a                	mv	s10,a0
42010df8:	8dae                	mv	s11,a1
42010dfa:	05000613          	li	a2,80
42010dfe:	0908                	addi	a0,sp,144
42010e00:	4581                	li	a1,0
42010e02:	fdfef097          	auipc	ra,0xfdfef
42010e06:	552080e7          	jalr	1362(ra) # 40000354 <memset>
42010e0a:	478d                	li	a5,3
42010e0c:	c126                	sw	s1,128(sp)
42010e0e:	c35a                	sw	s6,132(sp)
42010e10:	c56a                	sw	s10,136(sp)
42010e12:	c76e                	sw	s11,140(sp)
42010e14:	3cfb0863          	beq	s6,a5,420111e4 <decoder_task+0x564>
42010e18:	4789                	li	a5,2
42010e1a:	4afb0063          	beq	s6,a5,420112ba <decoder_task+0x63a>
42010e1e:	640d                	lui	s0,0x3
42010e20:	028a70e3          	bgeu	s4,s0,42011640 <decoder_task+0x9c0>
42010e24:	85a2                	mv	a1,s0
42010e26:	854a                	mv	a0,s2
42010e28:	ed8f70ef          	jal	42008500 <realloc>
42010e2c:	00050fe3          	beqz	a0,4201164a <decoder_task+0x9ca>
42010e30:	d682                	sw	zero,108(sp)
42010e32:	d882                	sw	zero,112(sp)
42010e34:	da82                	sw	zero,116(sp)
42010e36:	892a                	mv	s2,a0
42010e38:	8a22                	mv	s4,s0
42010e3a:	4791                	li	a5,4
42010e3c:	7cfb0663          	beq	s6,a5,42011608 <decoder_task+0x988>
42010e40:	203357b7          	lui	a5,0x20335
42010e44:	04d78793          	addi	a5,a5,77 # 2033504d <CSR_UINTSTATUS+0x2033439c>
42010e48:	086c                	addi	a1,sp,28
42010e4a:	10a8                	addi	a0,sp,104
42010e4c:	d4be                	sw	a5,104(sp)
42010e4e:	0e7150ef          	jal	42026734 <__wrap_esp_audio_simple_dec_open>
42010e52:	842a                	mv	s0,a0
42010e54:	7c050663          	beqz	a0,42011620 <decoder_task+0x9a0>
42010e58:	fe377097          	auipc	ra,0xfe377
42010e5c:	574080e7          	jalr	1396(ra) # 403883cc <esp_log_timestamp>
42010e60:	3c1267b7          	lui	a5,0x3c126
42010e64:	4985                	li	s3,1
42010e66:	86aa                	mv	a3,a0
42010e68:	80078793          	addi	a5,a5,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
42010e6c:	173b17e3          	bne	s6,s3,420117da <decoder_task+0xb5a>
42010e70:	3c126737          	lui	a4,0x3c126
42010e74:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
42010e78:	3c126637          	lui	a2,0x3c126
42010e7c:	85ba                	mv	a1,a4
42010e7e:	8822                	mv	a6,s0
42010e80:	c4c60613          	addi	a2,a2,-948 # 3c125c4c <_esp_trace_encoder_array_end+0x5b2c>
42010e84:	4505                	li	a0,1
42010e86:	fe377097          	auipc	ra,0xfe377
42010e8a:	43e080e7          	jalr	1086(ra) # 403882c4 <esp_log>
42010e8e:	3c126737          	lui	a4,0x3c126
42010e92:	57f9                	li	a5,-2
42010e94:	b8470693          	addi	a3,a4,-1148 # 3c125b84 <_esp_trace_encoder_array_end+0x5a64>
42010e98:	30f409e3          	beq	s0,a5,420119aa <decoder_task+0xd2a>
42010e9c:	3fc957b7          	lui	a5,0x3fc95
42010ea0:	b1c7a503          	lw	a0,-1252(a5) # 3fc94b1c <s_state>
42010ea4:	4601                	li	a2,0
42010ea6:	85a6                	mv	a1,s1
42010ea8:	077040ef          	jal	4201571e <native_state_set_audio>
42010eac:	4572                	lw	a0,28(sp)
42010eae:	c501                	beqz	a0,42010eb6 <decoder_task+0x236>
42010eb0:	488280ef          	jal	42039338 <esp_audio_simple_dec_close>
42010eb4:	ce02                	sw	zero,28(sp)
42010eb6:	854a                	mv	a0,s2
42010eb8:	e4cf70ef          	jal	42008504 <cfree>
42010ebc:	4a01                	li	s4,0
42010ebe:	c026                	sw	s1,0(sp)
42010ec0:	4901                	li	s2,0
42010ec2:	4b81                	li	s7,0
42010ec4:	4d81                	li	s11,0
42010ec6:	3fc957b7          	lui	a5,0x3fc95
42010eca:	b147a503          	lw	a0,-1260(a5) # 3fc94b14 <s_encoded>
42010ece:	85e6                	mv	a1,s9
42010ed0:	4981                	li	s3,0
42010ed2:	7c9670ef          	jal	42078e9a <vRingbufferReturnItem>
42010ed6:	4d01                	li	s10,0
42010ed8:	b505                	j	42010cf8 <decoder_task+0x78>
42010eda:	46f010ef          	jal	42012b48 <decoder_register_codecs>
42010ede:	8d2a                	mv	s10,a0
42010ee0:	7e051063          	bnez	a0,420116c0 <decoder_task+0xa40>
42010ee4:	000ca783          	lw	a5,0(s9)
42010ee8:	ec9796e3          	bne	a5,s1,42010db4 <decoder_task+0x134>
42010eec:	004ca783          	lw	a5,4(s9)
42010ef0:	ed6792e3          	bne	a5,s6,42010db4 <decoder_task+0x134>
42010ef4:	478d                	li	a5,3
42010ef6:	08fb03e3          	beq	s6,a5,4201177c <decoder_task+0xafc>
42010efa:	47f2                	lw	a5,28(sp)
42010efc:	00f9e7b3          	or	a5,s3,a5
42010f00:	d3f9                	beqz	a5,42010ec6 <decoder_task+0x246>
42010f02:	008cd783          	lhu	a5,8(s9)
42010f06:	00bc8713          	addi	a4,s9,11
42010f0a:	ce82                	sw	zero,92(sp)
42010f0c:	d082                	sw	zero,96(sp)
42010f0e:	d282                	sw	zero,100(sp)
42010f10:	ccbe                	sw	a5,88(sp)
42010f12:	caba                	sw	a4,84(sp)
42010f14:	00acc703          	lbu	a4,10(s9)
42010f18:	ffeb0693          	addi	a3,s6,-2
42010f1c:	0016b693          	seqz	a3,a3
42010f20:	00e03733          	snez	a4,a4
42010f24:	c436                	sw	a3,8(sp)
42010f26:	04e10e23          	sb	a4,92(sp)
42010f2a:	8c36                	mv	s8,a3
42010f2c:	3c098763          	beqz	s3,420112fa <decoder_task+0x67a>
42010f30:	e789                	bnez	a5,42010f3a <decoder_task+0x2ba>
42010f32:	05c14783          	lbu	a5,92(sp)
42010f36:	1c078b63          	beqz	a5,4201110c <decoder_task+0x48c>
42010f3a:	4781                	li	a5,0
42010f3c:	4801                	li	a6,0
42010f3e:	de3e                	sw	a5,60(sp)
42010f40:	c0c2                	sw	a6,64(sp)
42010f42:	da4a                	sw	s2,52(sp)
42010f44:	dc52                	sw	s4,56(sp)
42010f46:	d082                	sw	zero,96(sp)
42010f48:	fe370097          	auipc	ra,0xfe370
42010f4c:	3f2080e7          	jalr	1010(ra) # 4038133a <esp_timer_get_time>
42010f50:	8d2a                	mv	s10,a0
42010f52:	1850                	addi	a2,sp,52
42010f54:	08cc                	addi	a1,sp,84
42010f56:	854e                	mv	a0,s3
42010f58:	489010ef          	jal	42012be0 <native_aac_decoder_process>
42010f5c:	842a                	mv	s0,a0
42010f5e:	fe370097          	auipc	ra,0xfe370
42010f62:	3dc080e7          	jalr	988(ra) # 4038133a <esp_timer_get_time>
42010f66:	47ca                	lw	a5,144(sp)
42010f68:	46da                	lw	a3,148(sp)
42010f6a:	41a50533          	sub	a0,a0,s10
42010f6e:	00a78733          	add	a4,a5,a0
42010f72:	00f737b3          	sltu	a5,a4,a5
42010f76:	97b6                	add	a5,a5,a3
42010f78:	cb3e                	sw	a5,148(sp)
42010f7a:	578a                	lw	a5,160(sp)
42010f7c:	c93a                	sw	a4,144(sp)
42010f7e:	571a                	lw	a4,164(sp)
42010f80:	0785                	addi	a5,a5,1
42010f82:	d13e                	sw	a5,160(sp)
42010f84:	00a77363          	bgeu	a4,a0,42010f8a <decoder_task+0x30a>
42010f88:	d32a                	sw	a0,164(sp)
42010f8a:	8bfd                	andi	a5,a5,31
42010f8c:	58078863          	beqz	a5,4201151c <decoder_task+0x89c>
42010f90:	b08a8793          	addi	a5,s5,-1272
42010f94:	0330000f          	fence	rw,rw
42010f98:	439c                	lw	a5,0(a5)
42010f9a:	0230000f          	fence	r,rw
42010f9e:	16979763          	bne	a5,s1,4201110c <decoder_task+0x48c>
42010fa2:	57e1                	li	a5,-8
42010fa4:	54f40663          	beq	s0,a5,420114f0 <decoder_task+0x870>
42010fa8:	5c041563          	bnez	s0,42011572 <decoder_task+0x8f2>
42010fac:	5786                	lw	a5,96(sp)
42010fae:	4766                	lw	a4,88(sp)
42010fb0:	76f76263          	bltu	a4,a5,42011714 <decoder_task+0xa94>
42010fb4:	8f1d                	sub	a4,a4,a5
42010fb6:	56aa                	lw	a3,168(sp)
42010fb8:	ccba                	sw	a4,88(sp)
42010fba:	4756                	lw	a4,84(sp)
42010fbc:	96be                	add	a3,a3,a5
42010fbe:	d536                	sw	a3,168(sp)
42010fc0:	97ba                	add	a5,a5,a4
42010fc2:	4706                	lw	a4,64(sp)
42010fc4:	cabe                	sw	a5,84(sp)
42010fc6:	10070c63          	beqz	a4,420110de <decoder_task+0x45e>
42010fca:	00cc                	addi	a1,sp,68
42010fcc:	854e                	mv	a0,s3
42010fce:	c282                	sw	zero,68(sp)
42010fd0:	c482                	sw	zero,72(sp)
42010fd2:	c682                	sw	zero,76(sp)
42010fd4:	c882                	sw	zero,80(sp)
42010fd6:	733010ef          	jal	42012f08 <native_aac_decoder_get_info>
42010fda:	54051763          	bnez	a0,42011528 <decoder_task+0x8a8>
42010fde:	01b10613          	addi	a2,sp,27
42010fe2:	00cc                	addi	a1,sp,68
42010fe4:	854e                	mv	a0,s3
42010fe6:	01810da3          	sb	s8,27(sp)
42010fea:	72d010ef          	jal	42012f16 <native_aac_decoder_label>
42010fee:	01b14683          	lbu	a3,27(sp)
42010ff2:	842a                	mv	s0,a0
42010ff4:	4501                	li	a0,0
42010ff6:	60068163          	beqz	a3,420115f8 <decoder_task+0x978>
42010ffa:	b08a8793          	addi	a5,s5,-1272
42010ffe:	0330000f          	fence	rw,rw
42011002:	4398                	lw	a4,0(a5)
42011004:	0230000f          	fence	r,rw
42011008:	4781                	li	a5,0
4201100a:	06971163          	bne	a4,s1,4201106c <decoder_task+0x3ec>
4201100e:	4716                	lw	a4,68(sp)
42011010:	cf31                	beqz	a4,4201106c <decoder_task+0x3ec>
42011012:	04914803          	lbu	a6,73(sp)
42011016:	04080b63          	beqz	a6,4201106c <decoder_task+0x3ec>
4201101a:	04814603          	lbu	a2,72(sp)
4201101e:	c639                	beqz	a2,4201106c <decoder_task+0x3ec>
42011020:	45a6                	lw	a1,72(sp)
42011022:	47b6                	lw	a5,76(sp)
42011024:	d23a                	sw	a4,36(sp)
42011026:	d42e                	sw	a1,40(sp)
42011028:	45c6                	lw	a1,80(sp)
4201102a:	d63e                	sw	a5,44(sp)
4201102c:	4785                	li	a5,1
4201102e:	06012923          	sw	zero,114(sp)
42011032:	06012b23          	sw	zero,118(sp)
42011036:	06011d23          	sh	zero,122(sp)
4201103a:	d4a2                	sw	s0,104(sp)
4201103c:	d6ba                	sw	a4,108(sp)
4201103e:	d82e                	sw	a1,48(sp)
42011040:	00f10d23          	sb	a5,26(sp)
42011044:	78050863          	beqz	a0,420117d4 <decoder_task+0xb54>
42011048:	3fc957b7          	lui	a5,0x3fc95
4201104c:	06a10823          	sb	a0,112(sp)
42011050:	b1c7a503          	lw	a0,-1252(a5) # 3fc94b1c <s_state>
42011054:	06c108a3          	sb	a2,113(sp)
42011058:	85a6                	mv	a1,s1
4201105a:	10b0                	addi	a2,sp,104
4201105c:	daba                	sw	a4,116(sp)
4201105e:	07010c23          	sb	a6,120(sp)
42011062:	06d10d23          	sb	a3,122(sp)
42011066:	798040ef          	jal	420157fe <native_state_set_stream_info>
4201106a:	4785                	li	a5,1
4201106c:	45b6                	lw	a1,76(sp)
4201106e:	8526                	mv	a0,s1
42011070:	00f10d23          	sb	a5,26(sp)
42011074:	a30ff0ef          	jal	420102a4 <state_set_decoder_bitrate>
42011078:	01a14783          	lbu	a5,26(sp)
4201107c:	c3ad                	beqz	a5,420110de <decoder_task+0x45e>
4201107e:	4e0d8263          	beqz	s11,42011562 <decoder_task+0x8e2>
42011082:	02814503          	lbu	a0,40(sp)
42011086:	02914783          	lbu	a5,41(sp)
4201108a:	4406                	lw	s0,64(sp)
4201108c:	051d                	addi	a0,a0,7
4201108e:	810d                	srli	a0,a0,0x3
42011090:	02f50533          	mul	a0,a0,a5
42011094:	c91d                	beqz	a0,420110ca <decoder_task+0x44a>
42011096:	5612                	lw	a2,36(sp)
42011098:	ca0d                	beqz	a2,420110ca <decoder_task+0x44a>
4201109a:	02a45533          	divu	a0,s0,a0
4201109e:	47b2                	lw	a5,12(sp)
420110a0:	4681                	li	a3,0
420110a2:	02f535b3          	mulhu	a1,a0,a5
420110a6:	02f50533          	mul	a0,a0,a5
420110aa:	fdff0097          	auipc	ra,0xfdff0
420110ae:	802080e7          	jalr	-2046(ra) # 400008ac <__udivdi3>
420110b2:	47ea                	lw	a5,152(sp)
420110b4:	46fa                	lw	a3,156(sp)
420110b6:	573a                	lw	a4,172(sp)
420110b8:	953e                	add	a0,a0,a5
420110ba:	96ae                	add	a3,a3,a1
420110bc:	00f537b3          	sltu	a5,a0,a5
420110c0:	97b6                	add	a5,a5,a3
420110c2:	9722                	add	a4,a4,s0
420110c4:	cf3e                	sw	a5,156(sp)
420110c6:	cd2a                	sw	a0,152(sp)
420110c8:	d73a                	sw	a4,172(sp)
420110ca:	8722                	mv	a4,s0
420110cc:	86ca                	mv	a3,s2
420110ce:	1050                	addi	a2,sp,36
420110d0:	85a6                	mv	a1,s1
420110d2:	0108                	addi	a0,sp,128
420110d4:	d48ff0ef          	jal	4201061c <send_pcm>
420110d8:	8daa                	mv	s11,a0
420110da:	7c050763          	beqz	a0,420118a8 <decoder_task+0xc28>
420110de:	fe370097          	auipc	ra,0xfe370
420110e2:	25c080e7          	jalr	604(ra) # 4038133a <esp_timer_get_time>
420110e6:	862e                	mv	a2,a1
420110e8:	85aa                	mv	a1,a0
420110ea:	0108                	addi	a0,sp,128
420110ec:	d6ffe0ef          	jal	4200fe5a <decode_stats_report>
420110f0:	4706                	lw	a4,64(sp)
420110f2:	5786                	lw	a5,96(sp)
420110f4:	05c14683          	lbu	a3,92(sp)
420110f8:	8fd9                	or	a5,a5,a4
420110fa:	3e079563          	bnez	a5,420114e4 <decoder_task+0x864>
420110fe:	7e068563          	beqz	a3,420118e8 <decoder_task+0xc68>
42011102:	4701                	li	a4,0
42011104:	47e6                	lw	a5,88(sp)
42011106:	8f5d                	or	a4,a4,a5
42011108:	e20714e3          	bnez	a4,42010f30 <decoder_task+0x2b0>
4201110c:	00acc783          	lbu	a5,10(s9)
42011110:	4c079363          	bnez	a5,420115d6 <decoder_task+0x956>
42011114:	4782                	lw	a5,0(sp)
42011116:	4c978063          	beq	a5,s1,420115d6 <decoder_task+0x956>
4201111a:	4582                	lw	a1,0(sp)
4201111c:	8566                	mv	a0,s9
4201111e:	4d01                	li	s10,0
42011120:	ea0ff0ef          	jal	420107c0 <return_decoded_packet>
42011124:	b08a8793          	addi	a5,s5,-1272
42011128:	0330000f          	fence	rw,rw
4201112c:	4380                	lw	s0,0(a5)
4201112e:	0230000f          	fence	r,rw
42011132:	bc941ce3          	bne	s0,s1,42010d0a <decoder_task+0x8a>
42011136:	4782                	lw	a5,0(sp)
42011138:	c20786e3          	beqz	a5,42010d64 <decoder_task+0xe4>
4201113c:	c29794e3          	bne	a5,s1,42010d64 <decoder_task+0xe4>
42011140:	4572                	lw	a0,28(sp)
42011142:	c119                	beqz	a0,42011148 <decoder_task+0x4c8>
42011144:	1f4280ef          	jal	42039338 <esp_audio_simple_dec_close>
42011148:	ce02                	sw	zero,28(sp)
4201114a:	00098563          	beqz	s3,42011154 <decoder_task+0x4d4>
4201114e:	854e                	mv	a0,s3
42011150:	25b010ef          	jal	42012baa <native_aac_decoder_destroy>
42011154:	854a                	mv	a0,s2
42011156:	baef70ef          	jal	42008504 <cfree>
4201115a:	4981                	li	s3,0
4201115c:	4a01                	li	s4,0
4201115e:	4901                	li	s2,0
42011160:	b111                	j	42010d64 <decoder_task+0xe4>
42011162:	fe370097          	auipc	ra,0xfe370
42011166:	1d8080e7          	jalr	472(ra) # 4038133a <esp_timer_get_time>
4201116a:	8c2a                	mv	s8,a0
4201116c:	100c                	addi	a1,sp,32
4201116e:	4651                	li	a2,20
42011170:	8522                	mv	a0,s0
42011172:	4ad670ef          	jal	42078e1e <xRingbufferReceive>
42011176:	8caa                	mv	s9,a0
42011178:	fe370097          	auipc	ra,0xfe370
4201117c:	1c2080e7          	jalr	450(ra) # 4038133a <esp_timer_get_time>
42011180:	57ca                	lw	a5,176(sp)
42011182:	56da                	lw	a3,180(sp)
42011184:	41850533          	sub	a0,a0,s8
42011188:	00a78733          	add	a4,a5,a0
4201118c:	00f737b3          	sltu	a5,a4,a5
42011190:	d93a                	sw	a4,176(sp)
42011192:	576a                	lw	a4,184(sp)
42011194:	97b6                	add	a5,a5,a3
42011196:	db3e                	sw	a5,180(sp)
42011198:	57fa                	lw	a5,188(sp)
4201119a:	0705                	addi	a4,a4,1
4201119c:	001cb693          	seqz	a3,s9
420111a0:	dd3a                	sw	a4,184(sp)
420111a2:	470e                	lw	a4,192(sp)
420111a4:	97b6                	add	a5,a5,a3
420111a6:	df3e                	sw	a5,188(sp)
420111a8:	00a77363          	bgeu	a4,a0,420111ae <decoder_task+0x52e>
420111ac:	c1aa                	sw	a0,192(sp)
420111ae:	b40c85e3          	beqz	s9,42010cf8 <decoder_task+0x78>
420111b2:	000ca703          	lw	a4,0(s9)
420111b6:	b08a8793          	addi	a5,s5,-1272
420111ba:	0330000f          	fence	rw,rw
420111be:	439c                	lw	a5,0(a5)
420111c0:	0230000f          	fence	r,rw
420111c4:	bcf708e3          	beq	a4,a5,42010d94 <decoder_task+0x114>
420111c8:	3fc957b7          	lui	a5,0x3fc95
420111cc:	b147a503          	lw	a0,-1260(a5) # 3fc94b14 <s_encoded>
420111d0:	85e6                	mv	a1,s9
420111d2:	4c9670ef          	jal	42078e9a <vRingbufferReturnItem>
420111d6:	b60d                	j	42010cf8 <decoder_task+0x78>
420111d8:	854a                	mv	a0,s2
420111da:	b2af70ef          	jal	42008504 <cfree>
420111de:	4a01                	li	s4,0
420111e0:	4901                	li	s2,0
420111e2:	bea1                	j	42010d3a <decoder_task+0xba>
420111e4:	854a                	mv	a0,s2
420111e6:	b1ef70ef          	jal	42008504 <cfree>
420111ea:	248240ef          	jal	42035432 <custom_flac_decoder_create>
420111ee:	8baa                	mv	s7,a0
420111f0:	58050963          	beqz	a0,42011782 <decoder_task+0xb02>
420111f4:	4981                	li	s3,0
420111f6:	4a01                	li	s4,0
420111f8:	4901                	li	s2,0
420111fa:	4d81                	li	s11,0
420111fc:	4661                	li	a2,24
420111fe:	4581                	li	a1,0
42011200:	10a8                	addi	a0,sp,104
42011202:	fdfef097          	auipc	ra,0xfdfef
42011206:	152080e7          	jalr	338(ra) # 40000354 <memset>
4201120a:	011c                	addi	a5,sp,128
4201120c:	ccbe                	sw	a5,88(sp)
4201120e:	105c                	addi	a5,sp,36
42011210:	cebe                	sw	a5,92(sp)
42011212:	01a10793          	addi	a5,sp,26
42011216:	d0be                	sw	a5,96(sp)
42011218:	caa6                	sw	s1,84(sp)
4201121a:	00acc683          	lbu	a3,10(s9)
4201121e:	008cd603          	lhu	a2,8(s9)
42011222:	42012737          	lui	a4,0x42012
42011226:	00d036b3          	snez	a3,a3
4201122a:	08dc                	addi	a5,sp,84
4201122c:	9d470713          	addi	a4,a4,-1580 # 420119d4 <custom_flac_output>
42011230:	00bc8593          	addi	a1,s9,11
42011234:	06810813          	addi	a6,sp,104
42011238:	855e                	mv	a0,s7
4201123a:	27e240ef          	jal	420354b8 <custom_flac_decoder_feed>
4201123e:	47ca                	lw	a5,144(sp)
42011240:	5726                	lw	a4,104(sp)
42011242:	465a                	lw	a2,148(sp)
42011244:	55b6                	lw	a1,108(sp)
42011246:	568a                	lw	a3,160(sp)
42011248:	973e                	add	a4,a4,a5
4201124a:	842a                	mv	s0,a0
4201124c:	5546                	lw	a0,112(sp)
4201124e:	962e                	add	a2,a2,a1
42011250:	00f737b3          	sltu	a5,a4,a5
42011254:	97b2                	add	a5,a5,a2
42011256:	55d6                	lw	a1,116(sp)
42011258:	561a                	lw	a2,164(sp)
4201125a:	96aa                	add	a3,a3,a0
4201125c:	c93a                	sw	a4,144(sp)
4201125e:	cb3e                	sw	a5,148(sp)
42011260:	d136                	sw	a3,160(sp)
42011262:	00b67363          	bgeu	a2,a1,42011268 <decoder_task+0x5e8>
42011266:	d32e                	sw	a1,164(sp)
42011268:	57aa                	lw	a5,168(sp)
4201126a:	5766                	lw	a4,120(sp)
4201126c:	97ba                	add	a5,a5,a4
4201126e:	d53e                	sw	a5,168(sp)
42011270:	560d8b63          	beqz	s11,420117e6 <decoder_task+0xb66>
42011274:	4d85                	li	s11,1
42011276:	fe370097          	auipc	ra,0xfe370
4201127a:	0c4080e7          	jalr	196(ra) # 4038133a <esp_timer_get_time>
4201127e:	862e                	mv	a2,a1
42011280:	85aa                	mv	a1,a0
42011282:	0108                	addi	a0,sp,128
42011284:	bd7fe0ef          	jal	4200fe5a <decode_stats_report>
42011288:	00045b63          	bgez	s0,4201129e <decoder_task+0x61e>
4201128c:	b08a8793          	addi	a5,s5,-1272
42011290:	0330000f          	fence	rw,rw
42011294:	439c                	lw	a5,0(a5)
42011296:	0230000f          	fence	r,rw
4201129a:	6a978963          	beq	a5,s1,4201194c <decoder_task+0xccc>
4201129e:	00acc783          	lbu	a5,10(s9)
420112a2:	52079463          	bnez	a5,420117ca <decoder_task+0xb4a>
420112a6:	4782                	lw	a5,0(sp)
420112a8:	52978163          	beq	a5,s1,420117ca <decoder_task+0xb4a>
420112ac:	4582                	lw	a1,0(sp)
420112ae:	8566                	mv	a0,s9
420112b0:	4b0d                	li	s6,3
420112b2:	d0eff0ef          	jal	420107c0 <return_decoded_packet>
420112b6:	4d01                	li	s10,0
420112b8:	b481                	j	42010cf8 <decoder_task+0x78>
420112ba:	6589                	lui	a1,0x2
420112bc:	36ba0963          	beq	s4,a1,4201162e <decoder_task+0x9ae>
420112c0:	854a                	mv	a0,s2
420112c2:	a3ef70ef          	jal	42008500 <realloc>
420112c6:	842a                	mv	s0,a0
420112c8:	6e050c63          	beqz	a0,420119c0 <decoder_task+0xd40>
420112cc:	204347b7          	lui	a5,0x20434
420112d0:	14178793          	addi	a5,a5,321 # 20434141 <CSR_UINTSTATUS+0x20433490>
420112d4:	d682                	sw	zero,108(sp)
420112d6:	d882                	sw	zero,112(sp)
420112d8:	da82                	sw	zero,116(sp)
420112da:	d4be                	sw	a5,104(sp)
420112dc:	0a3010ef          	jal	42012b7e <native_aac_decoder_create>
420112e0:	89aa                	mv	s3,a0
420112e2:	52050263          	beqz	a0,42011806 <decoder_task+0xb86>
420112e6:	8922                	mv	s2,s0
420112e8:	6a09                	lui	s4,0x2
420112ea:	4b81                	li	s7,0
420112ec:	4d81                	li	s11,0
420112ee:	b911                	j	42010f02 <decoder_task+0x282>
420112f0:	4582                	lw	a1,0(sp)
420112f2:	8566                	mv	a0,s9
420112f4:	cccff0ef          	jal	420107c0 <return_decoded_packet>
420112f8:	b401                	j	42010cf8 <decoder_task+0x78>
420112fa:	5d61                	li	s10,-8
420112fc:	e789                	bnez	a5,42011306 <decoder_task+0x686>
420112fe:	05c14783          	lbu	a5,92(sp)
42011302:	e00785e3          	beqz	a5,4201110c <decoder_task+0x48c>
42011306:	4781                	li	a5,0
42011308:	4801                	li	a6,0
4201130a:	de3e                	sw	a5,60(sp)
4201130c:	c0c2                	sw	a6,64(sp)
4201130e:	da4a                	sw	s2,52(sp)
42011310:	dc52                	sw	s4,56(sp)
42011312:	d082                	sw	zero,96(sp)
42011314:	fe370097          	auipc	ra,0xfe370
42011318:	026080e7          	jalr	38(ra) # 4038133a <esp_timer_get_time>
4201131c:	842a                	mv	s0,a0
4201131e:	4572                	lw	a0,28(sp)
42011320:	1850                	addi	a2,sp,52
42011322:	08cc                	addi	a1,sp,84
42011324:	59c150ef          	jal	420268c0 <__wrap_esp_audio_simple_dec_process>
42011328:	8c2a                	mv	s8,a0
4201132a:	fe370097          	auipc	ra,0xfe370
4201132e:	010080e7          	jalr	16(ra) # 4038133a <esp_timer_get_time>
42011332:	47ca                	lw	a5,144(sp)
42011334:	46da                	lw	a3,148(sp)
42011336:	8d01                	sub	a0,a0,s0
42011338:	00a78733          	add	a4,a5,a0
4201133c:	00f737b3          	sltu	a5,a4,a5
42011340:	97b6                	add	a5,a5,a3
42011342:	cb3e                	sw	a5,148(sp)
42011344:	578a                	lw	a5,160(sp)
42011346:	c93a                	sw	a4,144(sp)
42011348:	571a                	lw	a4,164(sp)
4201134a:	0785                	addi	a5,a5,1
4201134c:	d13e                	sw	a5,160(sp)
4201134e:	00a77363          	bgeu	a4,a0,42011354 <decoder_task+0x6d4>
42011352:	d32a                	sw	a0,164(sp)
42011354:	8bfd                	andi	a5,a5,31
42011356:	1e078d63          	beqz	a5,42011550 <decoder_task+0x8d0>
4201135a:	b08a8793          	addi	a5,s5,-1272
4201135e:	0330000f          	fence	rw,rw
42011362:	439c                	lw	a5,0(a5)
42011364:	0230000f          	fence	r,rw
42011368:	da9792e3          	bne	a5,s1,4201110c <decoder_task+0x48c>
4201136c:	1dac0663          	beq	s8,s10,42011538 <decoder_task+0x8b8>
42011370:	200c1063          	bnez	s8,42011570 <decoder_task+0x8f0>
42011374:	5786                	lw	a5,96(sp)
42011376:	4766                	lw	a4,88(sp)
42011378:	38f76e63          	bltu	a4,a5,42011714 <decoder_task+0xa94>
4201137c:	8f1d                	sub	a4,a4,a5
4201137e:	56aa                	lw	a3,168(sp)
42011380:	ccba                	sw	a4,88(sp)
42011382:	4756                	lw	a4,84(sp)
42011384:	96be                	add	a3,a3,a5
42011386:	d536                	sw	a3,168(sp)
42011388:	97ba                	add	a5,a5,a4
4201138a:	4706                	lw	a4,64(sp)
4201138c:	cabe                	sw	a5,84(sp)
4201138e:	12070463          	beqz	a4,420114b6 <decoder_task+0x836>
42011392:	4572                	lw	a0,28(sp)
42011394:	00cc                	addi	a1,sp,68
42011396:	c282                	sw	zero,68(sp)
42011398:	c482                	sw	zero,72(sp)
4201139a:	c682                	sw	zero,76(sp)
4201139c:	c882                	sw	zero,80(sp)
4201139e:	723270ef          	jal	420392c0 <esp_audio_simple_dec_get_info>
420113a2:	1a051d63          	bnez	a0,4201155c <decoder_task+0x8dc>
420113a6:	47a2                	lw	a5,8(sp)
420113a8:	00f10da3          	sb	a5,27(sp)
420113ac:	4789                	li	a5,2
420113ae:	4cfb0563          	beq	s6,a5,42011878 <decoder_task+0xbf8>
420113b2:	4791                	li	a5,4
420113b4:	4afb0d63          	beq	s6,a5,4201186e <decoder_task+0xbee>
420113b8:	3c126737          	lui	a4,0x3c126
420113bc:	4785                	li	a5,1
420113be:	80070593          	addi	a1,a4,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
420113c2:	42fb1d63          	bne	s6,a5,420117fc <decoder_task+0xb7c>
420113c6:	b08a8793          	addi	a5,s5,-1272
420113ca:	0330000f          	fence	rw,rw
420113ce:	439c                	lw	a5,0(a5)
420113d0:	0230000f          	fence	r,rw
420113d4:	06979463          	bne	a5,s1,4201143c <decoder_task+0x7bc>
420113d8:	4796                	lw	a5,68(sp)
420113da:	c3b5                	beqz	a5,4201143e <decoder_task+0x7be>
420113dc:	04914683          	lbu	a3,73(sp)
420113e0:	ceb1                	beqz	a3,4201143c <decoder_task+0x7bc>
420113e2:	04815703          	lhu	a4,72(sp)
420113e6:	04814503          	lbu	a0,72(sp)
420113ea:	00875613          	srli	a2,a4,0x8
420113ee:	0722                	slli	a4,a4,0x8
420113f0:	963a                	add	a2,a2,a4
420113f2:	c529                	beqz	a0,4201143c <decoder_task+0x7bc>
420113f4:	06012b23          	sw	zero,118(sp)
420113f8:	06012923          	sw	zero,114(sp)
420113fc:	d23e                	sw	a5,36(sp)
420113fe:	06c11823          	sh	a2,112(sp)
42011402:	d6be                	sw	a5,108(sp)
42011404:	4626                	lw	a2,72(sp)
42011406:	dabe                	sw	a5,116(sp)
42011408:	3fc957b7          	lui	a5,0x3fc95
4201140c:	4746                	lw	a4,80(sp)
4201140e:	b1c7a503          	lw	a0,-1252(a5) # 3fc94b1c <s_state>
42011412:	06d10c23          	sb	a3,120(sp)
42011416:	47a2                	lw	a5,8(sp)
42011418:	46b6                	lw	a3,76(sp)
4201141a:	06011d23          	sh	zero,122(sp)
4201141e:	d4ae                	sw	a1,104(sp)
42011420:	d432                	sw	a2,40(sp)
42011422:	4405                	li	s0,1
42011424:	10b0                	addi	a2,sp,104
42011426:	85a6                	mv	a1,s1
42011428:	06f10d23          	sb	a5,122(sp)
4201142c:	d636                	sw	a3,44(sp)
4201142e:	d83a                	sw	a4,48(sp)
42011430:	00810d23          	sb	s0,26(sp)
42011434:	3ca040ef          	jal	420157fe <native_state_set_stream_info>
42011438:	87a2                	mv	a5,s0
4201143a:	a011                	j	4201143e <decoder_task+0x7be>
4201143c:	4781                	li	a5,0
4201143e:	45b6                	lw	a1,76(sp)
42011440:	8526                	mv	a0,s1
42011442:	00f10d23          	sb	a5,26(sp)
42011446:	e5ffe0ef          	jal	420102a4 <state_set_decoder_bitrate>
4201144a:	01a14783          	lbu	a5,26(sp)
4201144e:	c7a5                	beqz	a5,420114b6 <decoder_task+0x836>
42011450:	1e0d8163          	beqz	s11,42011632 <decoder_task+0x9b2>
42011454:	02814503          	lbu	a0,40(sp)
42011458:	02914783          	lbu	a5,41(sp)
4201145c:	4406                	lw	s0,64(sp)
4201145e:	051d                	addi	a0,a0,7
42011460:	810d                	srli	a0,a0,0x3
42011462:	02f50533          	mul	a0,a0,a5
42011466:	cd15                	beqz	a0,420114a2 <decoder_task+0x822>
42011468:	5612                	lw	a2,36(sp)
4201146a:	ce05                	beqz	a2,420114a2 <decoder_task+0x822>
4201146c:	02a45533          	divu	a0,s0,a0
42011470:	000f47b7          	lui	a5,0xf4
42011474:	24078793          	addi	a5,a5,576 # f4240 <CSR_UINTSTATUS+0xf358f>
42011478:	4681                	li	a3,0
4201147a:	02f535b3          	mulhu	a1,a0,a5
4201147e:	02f50533          	mul	a0,a0,a5
42011482:	fdfef097          	auipc	ra,0xfdfef
42011486:	42a080e7          	jalr	1066(ra) # 400008ac <__udivdi3>
4201148a:	47ea                	lw	a5,152(sp)
4201148c:	46fa                	lw	a3,156(sp)
4201148e:	573a                	lw	a4,172(sp)
42011490:	953e                	add	a0,a0,a5
42011492:	96ae                	add	a3,a3,a1
42011494:	00f537b3          	sltu	a5,a0,a5
42011498:	97b6                	add	a5,a5,a3
4201149a:	9722                	add	a4,a4,s0
4201149c:	cf3e                	sw	a5,156(sp)
4201149e:	cd2a                	sw	a0,152(sp)
420114a0:	d73a                	sw	a4,172(sp)
420114a2:	8722                	mv	a4,s0
420114a4:	86ca                	mv	a3,s2
420114a6:	1050                	addi	a2,sp,36
420114a8:	85a6                	mv	a1,s1
420114aa:	0108                	addi	a0,sp,128
420114ac:	970ff0ef          	jal	4201061c <send_pcm>
420114b0:	8daa                	mv	s11,a0
420114b2:	3e050b63          	beqz	a0,420118a8 <decoder_task+0xc28>
420114b6:	fe370097          	auipc	ra,0xfe370
420114ba:	e84080e7          	jalr	-380(ra) # 4038133a <esp_timer_get_time>
420114be:	862e                	mv	a2,a1
420114c0:	85aa                	mv	a1,a0
420114c2:	0108                	addi	a0,sp,128
420114c4:	997fe0ef          	jal	4200fe5a <decode_stats_report>
420114c8:	4706                	lw	a4,64(sp)
420114ca:	5786                	lw	a5,96(sp)
420114cc:	05c14683          	lbu	a3,92(sp)
420114d0:	8fd9                	or	a5,a5,a4
420114d2:	efb1                	bnez	a5,4201152e <decoder_task+0x8ae>
420114d4:	40068a63          	beqz	a3,420118e8 <decoder_task+0xc68>
420114d8:	4701                	li	a4,0
420114da:	47e6                	lw	a5,88(sp)
420114dc:	8f5d                	or	a4,a4,a5
420114de:	e0071fe3          	bnez	a4,420112fc <decoder_task+0x67c>
420114e2:	b12d                	j	4201110c <decoder_task+0x48c>
420114e4:	c20690e3          	bnez	a3,42011104 <decoder_task+0x484>
420114e8:	47e6                	lw	a5,88(sp)
420114ea:	a40798e3          	bnez	a5,42010f3a <decoder_task+0x2ba>
420114ee:	b939                	j	4201110c <decoder_task+0x48c>
420114f0:	5706                	lw	a4,96(sp)
420114f2:	47d6                	lw	a5,84(sp)
420114f4:	56aa                	lw	a3,168(sp)
420114f6:	5472                	lw	s0,60(sp)
420114f8:	97ba                	add	a5,a5,a4
420114fa:	cabe                	sw	a5,84(sp)
420114fc:	47e6                	lw	a5,88(sp)
420114fe:	96ba                	add	a3,a3,a4
42011500:	d536                	sw	a3,168(sp)
42011502:	8f99                	sub	a5,a5,a4
42011504:	ccbe                	sw	a5,88(sp)
42011506:	368a7e63          	bgeu	s4,s0,42011882 <decoder_task+0xc02>
4201150a:	85a2                	mv	a1,s0
4201150c:	854a                	mv	a0,s2
4201150e:	ff3f60ef          	jal	42008500 <realloc>
42011512:	36050863          	beqz	a0,42011882 <decoder_task+0xc02>
42011516:	8a22                	mv	s4,s0
42011518:	892a                	mv	s2,a0
4201151a:	b405                	j	42010f3a <decoder_task+0x2ba>
4201151c:	4505                	li	a0,1
4201151e:	00102097          	auipc	ra,0x102
42011522:	948080e7          	jalr	-1720(ra) # 42112e66 <vTaskDelay>
42011526:	b4ad                	j	42010f90 <decoder_task+0x310>
42011528:	00010d23          	sb	zero,26(sp)
4201152c:	be4d                	j	420110de <decoder_task+0x45e>
4201152e:	f6d5                	bnez	a3,420114da <decoder_task+0x85a>
42011530:	47e6                	lw	a5,88(sp)
42011532:	dc079ae3          	bnez	a5,42011306 <decoder_task+0x686>
42011536:	bed9                	j	4201110c <decoder_task+0x48c>
42011538:	5472                	lw	s0,60(sp)
4201153a:	348a7463          	bgeu	s4,s0,42011882 <decoder_task+0xc02>
4201153e:	85a2                	mv	a1,s0
42011540:	854a                	mv	a0,s2
42011542:	fbff60ef          	jal	42008500 <realloc>
42011546:	32050e63          	beqz	a0,42011882 <decoder_task+0xc02>
4201154a:	892a                	mv	s2,a0
4201154c:	8a22                	mv	s4,s0
4201154e:	bb65                	j	42011306 <decoder_task+0x686>
42011550:	4505                	li	a0,1
42011552:	00102097          	auipc	ra,0x102
42011556:	914080e7          	jalr	-1772(ra) # 42112e66 <vTaskDelay>
4201155a:	b501                	j	4201135a <decoder_task+0x6da>
4201155c:	00010d23          	sb	zero,26(sp)
42011560:	bf99                	j	420114b6 <decoder_task+0x836>
42011562:	3c1267b7          	lui	a5,0x3c126
42011566:	cb878513          	addi	a0,a5,-840 # 3c125cb8 <_esp_trace_encoder_array_end+0x5b98>
4201156a:	cd7fe0ef          	jal	42010240 <log_runtime_memory>
4201156e:	be11                	j	42011082 <decoder_task+0x402>
42011570:	8462                	mv	s0,s8
42011572:	4a09                	li	s4,2
42011574:	fe377097          	auipc	ra,0xfe377
42011578:	e58080e7          	jalr	-424(ra) # 403883cc <esp_log_timestamp>
4201157c:	2d4b0f63          	beq	s6,s4,4201185a <decoder_task+0xbda>
42011580:	4791                	li	a5,4
42011582:	34fb0963          	beq	s6,a5,420118d4 <decoder_task+0xc54>
42011586:	3c1267b7          	lui	a5,0x3c126
4201158a:	4705                	li	a4,1
4201158c:	80078793          	addi	a5,a5,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
42011590:	00eb0663          	beq	s6,a4,4201159c <decoder_task+0x91c>
42011594:	3c1267b7          	lui	a5,0x3c126
42011598:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
4201159c:	3c126737          	lui	a4,0x3c126
420115a0:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
420115a4:	3c126637          	lui	a2,0x3c126
420115a8:	86aa                	mv	a3,a0
420115aa:	85ba                	mv	a1,a4
420115ac:	8822                	mv	a6,s0
420115ae:	cec60613          	addi	a2,a2,-788 # 3c125cec <_esp_trace_encoder_array_end+0x5bcc>
420115b2:	4509                	li	a0,2
420115b4:	fe377097          	auipc	ra,0xfe377
420115b8:	d10080e7          	jalr	-752(ra) # 403882c4 <esp_log>
420115bc:	3fc957b7          	lui	a5,0x3fc95
420115c0:	b1c7a503          	lw	a0,-1252(a5) # 3fc94b1c <s_state>
420115c4:	3c1267b7          	lui	a5,0x3c126
420115c8:	b9478693          	addi	a3,a5,-1132 # 3c125b94 <_esp_trace_encoder_array_end+0x5a74>
420115cc:	85a6                	mv	a1,s1
420115ce:	4601                	li	a2,0
420115d0:	14e040ef          	jal	4201571e <native_state_set_audio>
420115d4:	c026                	sw	s1,0(sp)
420115d6:	4572                	lw	a0,28(sp)
420115d8:	c119                	beqz	a0,420115de <decoder_task+0x95e>
420115da:	55f270ef          	jal	42039338 <esp_audio_simple_dec_close>
420115de:	ce02                	sw	zero,28(sp)
420115e0:	00098563          	beqz	s3,420115ea <decoder_task+0x96a>
420115e4:	854e                	mv	a0,s3
420115e6:	5c4010ef          	jal	42012baa <native_aac_decoder_destroy>
420115ea:	854a                	mv	a0,s2
420115ec:	f19f60ef          	jal	42008504 <cfree>
420115f0:	4981                	li	s3,0
420115f2:	4a01                	li	s4,0
420115f4:	4901                	li	s2,0
420115f6:	b615                	j	4201111a <decoder_task+0x49a>
420115f8:	854e                	mv	a0,s3
420115fa:	175010ef          	jal	42012f6e <native_aac_decoder_source_channels>
420115fe:	01b14683          	lbu	a3,27(sp)
42011602:	0ff57513          	zext.b	a0,a0
42011606:	bad5                	j	42010ffa <decoder_task+0x37a>
42011608:	204747b7          	lui	a5,0x20474
4201160c:	74f78793          	addi	a5,a5,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
42011610:	086c                	addi	a1,sp,28
42011612:	10a8                	addi	a0,sp,104
42011614:	d4be                	sw	a5,104(sp)
42011616:	11e150ef          	jal	42026734 <__wrap_esp_audio_simple_dec_open>
4201161a:	842a                	mv	s0,a0
4201161c:	22051463          	bnez	a0,42011844 <decoder_task+0xbc4>
42011620:	4bf2                	lw	s7,28(sp)
42011622:	4d81                	li	s11,0
42011624:	8a0b81e3          	beqz	s7,42010ec6 <decoder_task+0x246>
42011628:	4981                	li	s3,0
4201162a:	4b81                	li	s7,0
4201162c:	b8d9                	j	42010f02 <decoder_task+0x282>
4201162e:	844a                	mv	s0,s2
42011630:	b971                	j	420112cc <decoder_task+0x64c>
42011632:	3c1267b7          	lui	a5,0x3c126
42011636:	cb878513          	addi	a0,a5,-840 # 3c125cb8 <_esp_trace_encoder_array_end+0x5b98>
4201163a:	c07fe0ef          	jal	42010240 <log_runtime_memory>
4201163e:	bd19                	j	42011454 <decoder_task+0x7d4>
42011640:	d682                	sw	zero,108(sp)
42011642:	d882                	sw	zero,112(sp)
42011644:	da82                	sw	zero,116(sp)
42011646:	ff4ff06f          	j	42010e3a <decoder_task+0x1ba>
4201164a:	fe377097          	auipc	ra,0xfe377
4201164e:	d82080e7          	jalr	-638(ra) # 403883cc <esp_log_timestamp>
42011652:	4791                	li	a5,4
42011654:	4405                	li	s0,1
42011656:	86aa                	mv	a3,a0
42011658:	24fb0363          	beq	s6,a5,4201189e <decoder_task+0xc1e>
4201165c:	3c1267b7          	lui	a5,0x3c126
42011660:	80078793          	addi	a5,a5,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
42011664:	008b0663          	beq	s6,s0,42011670 <decoder_task+0x9f0>
42011668:	3c1267b7          	lui	a5,0x3c126
4201166c:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
42011670:	3c126737          	lui	a4,0x3c126
42011674:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
42011678:	3c126637          	lui	a2,0x3c126
4201167c:	85ba                	mv	a1,a4
4201167e:	c1c60613          	addi	a2,a2,-996 # 3c125c1c <_esp_trace_encoder_array_end+0x5afc>
42011682:	4505                	li	a0,1
42011684:	fe377097          	auipc	ra,0xfe377
42011688:	c40080e7          	jalr	-960(ra) # 403882c4 <esp_log>
4201168c:	3fc957b7          	lui	a5,0x3fc95
42011690:	b1c7a503          	lw	a0,-1252(a5) # 3fc94b1c <s_state>
42011694:	3c1267b7          	lui	a5,0x3c126
42011698:	b7878693          	addi	a3,a5,-1160 # 3c125b78 <_esp_trace_encoder_array_end+0x5a58>
4201169c:	85a6                	mv	a1,s1
4201169e:	4601                	li	a2,0
420116a0:	07e040ef          	jal	4201571e <native_state_set_audio>
420116a4:	3fc957b7          	lui	a5,0x3fc95
420116a8:	b147a503          	lw	a0,-1260(a5) # 3fc94b14 <s_encoded>
420116ac:	85e6                	mv	a1,s9
420116ae:	4981                	li	s3,0
420116b0:	7ea670ef          	jal	42078e9a <vRingbufferReturnItem>
420116b4:	4d81                	li	s11,0
420116b6:	c026                	sw	s1,0(sp)
420116b8:	4b81                	li	s7,0
420116ba:	4d01                	li	s10,0
420116bc:	e3cff06f          	j	42010cf8 <decoder_task+0x78>
420116c0:	fe377097          	auipc	ra,0xfe377
420116c4:	d0c080e7          	jalr	-756(ra) # 403883cc <esp_log_timestamp>
420116c8:	3c126737          	lui	a4,0x3c126
420116cc:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
420116d0:	3c126637          	lui	a2,0x3c126
420116d4:	85ba                	mv	a1,a4
420116d6:	86aa                	mv	a3,a0
420116d8:	87ea                	mv	a5,s10
420116da:	ba460613          	addi	a2,a2,-1116 # 3c125ba4 <_esp_trace_encoder_array_end+0x5a84>
420116de:	4505                	li	a0,1
420116e0:	fe377097          	auipc	ra,0xfe377
420116e4:	be4080e7          	jalr	-1052(ra) # 403882c4 <esp_log>
420116e8:	3fc957b7          	lui	a5,0x3fc95
420116ec:	000ca583          	lw	a1,0(s9)
420116f0:	b1c7a503          	lw	a0,-1252(a5) # 3fc94b1c <s_state>
420116f4:	3c1267b7          	lui	a5,0x3c126
420116f8:	bd478693          	addi	a3,a5,-1068 # 3c125bd4 <_esp_trace_encoder_array_end+0x5ab4>
420116fc:	4601                	li	a2,0
420116fe:	020040ef          	jal	4201571e <native_state_set_audio>
42011702:	000ca783          	lw	a5,0(s9)
42011706:	8566                	mv	a0,s9
42011708:	85be                	mv	a1,a5
4201170a:	c03e                	sw	a5,0(sp)
4201170c:	8b4ff0ef          	jal	420107c0 <return_decoded_packet>
42011710:	de8ff06f          	j	42010cf8 <decoder_task+0x78>
42011714:	fe377097          	auipc	ra,0xfe377
42011718:	cb8080e7          	jalr	-840(ra) # 403883cc <esp_log_timestamp>
4201171c:	4789                	li	a5,2
4201171e:	4405                	li	s0,1
42011720:	14fb0263          	beq	s6,a5,42011864 <decoder_task+0xbe4>
42011724:	4791                	li	a5,4
42011726:	1afb0c63          	beq	s6,a5,420118de <decoder_task+0xc5e>
4201172a:	3c1267b7          	lui	a5,0x3c126
4201172e:	80078793          	addi	a5,a5,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
42011732:	008b0663          	beq	s6,s0,4201173e <decoder_task+0xabe>
42011736:	3c1267b7          	lui	a5,0x3c126
4201173a:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
4201173e:	48e6                	lw	a7,88(sp)
42011740:	5806                	lw	a6,96(sp)
42011742:	3c126737          	lui	a4,0x3c126
42011746:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
4201174a:	3c126637          	lui	a2,0x3c126
4201174e:	86aa                	mv	a3,a0
42011750:	85ba                	mv	a1,a4
42011752:	d1060613          	addi	a2,a2,-752 # 3c125d10 <_esp_trace_encoder_array_end+0x5bf0>
42011756:	4505                	li	a0,1
42011758:	fe377097          	auipc	ra,0xfe377
4201175c:	b6c080e7          	jalr	-1172(ra) # 403882c4 <esp_log>
42011760:	3fc957b7          	lui	a5,0x3fc95
42011764:	b1c7a503          	lw	a0,-1252(a5) # 3fc94b1c <s_state>
42011768:	3c1267b7          	lui	a5,0x3c126
4201176c:	d4c78693          	addi	a3,a5,-692 # 3c125d4c <_esp_trace_encoder_array_end+0x5c2c>
42011770:	85a6                	mv	a1,s1
42011772:	4601                	li	a2,0
42011774:	7ab030ef          	jal	4201571e <native_state_set_audio>
42011778:	c026                	sw	s1,0(sp)
4201177a:	bdb1                	j	420115d6 <decoder_task+0x956>
4201177c:	b20b81e3          	beqz	s7,4201129e <decoder_task+0x61e>
42011780:	bcb5                	j	420111fc <decoder_task+0x57c>
42011782:	fe377097          	auipc	ra,0xfe377
42011786:	c4a080e7          	jalr	-950(ra) # 403883cc <esp_log_timestamp>
4201178a:	3c1267b7          	lui	a5,0x3c126
4201178e:	80c78713          	addi	a4,a5,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
42011792:	3c1267b7          	lui	a5,0x3c126
42011796:	86aa                	mv	a3,a0
42011798:	85ba                	mv	a1,a4
4201179a:	be878613          	addi	a2,a5,-1048 # 3c125be8 <_esp_trace_encoder_array_end+0x5ac8>
4201179e:	4505                	li	a0,1
420117a0:	fe377097          	auipc	ra,0xfe377
420117a4:	b24080e7          	jalr	-1244(ra) # 403882c4 <esp_log>
420117a8:	3fc957b7          	lui	a5,0x3fc95
420117ac:	b1c7a503          	lw	a0,-1252(a5) # 3fc94b1c <s_state>
420117b0:	3c1267b7          	lui	a5,0x3c126
420117b4:	b7878693          	addi	a3,a5,-1160 # 3c125b78 <_esp_trace_encoder_array_end+0x5a58>
420117b8:	85a6                	mv	a1,s1
420117ba:	4601                	li	a2,0
420117bc:	763030ef          	jal	4201571e <native_state_set_audio>
420117c0:	4981                	li	s3,0
420117c2:	c026                	sw	s1,0(sp)
420117c4:	4901                	li	s2,0
420117c6:	4a01                	li	s4,0
420117c8:	4d81                	li	s11,0
420117ca:	855e                	mv	a0,s7
420117cc:	4c7230ef          	jal	42035492 <custom_flac_decoder_destroy>
420117d0:	4b81                	li	s7,0
420117d2:	bce9                	j	420112ac <decoder_task+0x62c>
420117d4:	8542                	mv	a0,a6
420117d6:	873ff06f          	j	42011048 <decoder_task+0x3c8>
420117da:	3c1267b7          	lui	a5,0x3c126
420117de:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
420117e2:	e8eff06f          	j	42010e70 <decoder_task+0x1f0>
420117e6:	01a14d83          	lbu	s11,26(sp)
420117ea:	a80d86e3          	beqz	s11,42011276 <decoder_task+0x5f6>
420117ee:	3c1267b7          	lui	a5,0x3c126
420117f2:	c7478513          	addi	a0,a5,-908 # 3c125c74 <_esp_trace_encoder_array_end+0x5b54>
420117f6:	a4bfe0ef          	jal	42010240 <log_runtime_memory>
420117fa:	bcad                	j	42011274 <decoder_task+0x5f4>
420117fc:	3c1267b7          	lui	a5,0x3c126
42011800:	80478593          	addi	a1,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
42011804:	b6c9                	j	420113c6 <decoder_task+0x746>
42011806:	fe377097          	auipc	ra,0xfe377
4201180a:	bc6080e7          	jalr	-1082(ra) # 403883cc <esp_log_timestamp>
4201180e:	3c1267b7          	lui	a5,0x3c126
42011812:	80c78713          	addi	a4,a5,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
42011816:	3c126637          	lui	a2,0x3c126
4201181a:	3c1257b7          	lui	a5,0x3c125
4201181e:	86aa                	mv	a3,a0
42011820:	7f078793          	addi	a5,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
42011824:	85ba                	mv	a1,a4
42011826:	c4c60613          	addi	a2,a2,-948 # 3c125c4c <_esp_trace_encoder_array_end+0x5b2c>
4201182a:	5879                	li	a6,-2
4201182c:	4505                	li	a0,1
4201182e:	fe377097          	auipc	ra,0xfe377
42011832:	a96080e7          	jalr	-1386(ra) # 403882c4 <esp_log>
42011836:	3c1267b7          	lui	a5,0x3c126
4201183a:	8922                	mv	s2,s0
4201183c:	b7878693          	addi	a3,a5,-1160 # 3c125b78 <_esp_trace_encoder_array_end+0x5a58>
42011840:	e5cff06f          	j	42010e9c <decoder_task+0x21c>
42011844:	fe377097          	auipc	ra,0xfe377
42011848:	b88080e7          	jalr	-1144(ra) # 403883cc <esp_log_timestamp>
4201184c:	3c1257b7          	lui	a5,0x3c125
42011850:	86aa                	mv	a3,a0
42011852:	7fc78793          	addi	a5,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
42011856:	e1aff06f          	j	42010e70 <decoder_task+0x1f0>
4201185a:	3c1257b7          	lui	a5,0x3c125
4201185e:	7f078793          	addi	a5,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
42011862:	bb2d                	j	4201159c <decoder_task+0x91c>
42011864:	3c1257b7          	lui	a5,0x3c125
42011868:	7f078793          	addi	a5,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
4201186c:	bdc9                	j	4201173e <decoder_task+0xabe>
4201186e:	3c1257b7          	lui	a5,0x3c125
42011872:	7fc78593          	addi	a1,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
42011876:	be81                	j	420113c6 <decoder_task+0x746>
42011878:	3c1257b7          	lui	a5,0x3c125
4201187c:	7f078593          	addi	a1,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
42011880:	b699                	j	420113c6 <decoder_task+0x746>
42011882:	3fc957b7          	lui	a5,0x3fc95
42011886:	b1c7a503          	lw	a0,-1252(a5) # 3fc94b1c <s_state>
4201188a:	3c1267b7          	lui	a5,0x3c126
4201188e:	cd478693          	addi	a3,a5,-812 # 3c125cd4 <_esp_trace_encoder_array_end+0x5bb4>
42011892:	4601                	li	a2,0
42011894:	85a6                	mv	a1,s1
42011896:	689030ef          	jal	4201571e <native_state_set_audio>
4201189a:	c026                	sw	s1,0(sp)
4201189c:	bb2d                	j	420115d6 <decoder_task+0x956>
4201189e:	3c1257b7          	lui	a5,0x3c125
420118a2:	7fc78793          	addi	a5,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
420118a6:	b3e9                	j	42011670 <decoder_task+0x9f0>
420118a8:	fe377097          	auipc	ra,0xfe377
420118ac:	b24080e7          	jalr	-1244(ra) # 403883cc <esp_log_timestamp>
420118b0:	3c1267b7          	lui	a5,0x3c126
420118b4:	80c78713          	addi	a4,a5,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
420118b8:	3c1267b7          	lui	a5,0x3c126
420118bc:	86aa                	mv	a3,a0
420118be:	85ba                	mv	a1,a4
420118c0:	d6078613          	addi	a2,a5,-672 # 3c125d60 <_esp_trace_encoder_array_end+0x5c40>
420118c4:	4509                	li	a0,2
420118c6:	fe377097          	auipc	ra,0xfe377
420118ca:	9fe080e7          	jalr	-1538(ra) # 403882c4 <esp_log>
420118ce:	4d85                	li	s11,1
420118d0:	83dff06f          	j	4201110c <decoder_task+0x48c>
420118d4:	3c1257b7          	lui	a5,0x3c125
420118d8:	7fc78793          	addi	a5,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
420118dc:	b1c1                	j	4201159c <decoder_task+0x91c>
420118de:	3c1257b7          	lui	a5,0x3c125
420118e2:	7fc78793          	addi	a5,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
420118e6:	bda1                	j	4201173e <decoder_task+0xabe>
420118e8:	fe377097          	auipc	ra,0xfe377
420118ec:	ae4080e7          	jalr	-1308(ra) # 403883cc <esp_log_timestamp>
420118f0:	4789                	li	a5,2
420118f2:	4405                	li	s0,1
420118f4:	86aa                	mv	a3,a0
420118f6:	0afb0563          	beq	s6,a5,420119a0 <decoder_task+0xd20>
420118fa:	4791                	li	a5,4
420118fc:	0afb0d63          	beq	s6,a5,420119b6 <decoder_task+0xd36>
42011900:	3c1267b7          	lui	a5,0x3c126
42011904:	80078793          	addi	a5,a5,-2048 # 3c125800 <_esp_trace_encoder_array_end+0x56e0>
42011908:	008b0663          	beq	s6,s0,42011914 <decoder_task+0xc94>
4201190c:	3c1267b7          	lui	a5,0x3c126
42011910:	80478793          	addi	a5,a5,-2044 # 3c125804 <_esp_trace_encoder_array_end+0x56e4>
42011914:	3c126737          	lui	a4,0x3c126
42011918:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
4201191c:	3c126637          	lui	a2,0x3c126
42011920:	85ba                	mv	a1,a4
42011922:	d8060613          	addi	a2,a2,-640 # 3c125d80 <_esp_trace_encoder_array_end+0x5c60>
42011926:	4505                	li	a0,1
42011928:	fe377097          	auipc	ra,0xfe377
4201192c:	99c080e7          	jalr	-1636(ra) # 403882c4 <esp_log>
42011930:	3fc957b7          	lui	a5,0x3fc95
42011934:	b1c7a503          	lw	a0,-1252(a5) # 3fc94b1c <s_state>
42011938:	3c1267b7          	lui	a5,0x3c126
4201193c:	db078693          	addi	a3,a5,-592 # 3c125db0 <_esp_trace_encoder_array_end+0x5c90>
42011940:	85a6                	mv	a1,s1
42011942:	4601                	li	a2,0
42011944:	5db030ef          	jal	4201571e <native_state_set_audio>
42011948:	c026                	sw	s1,0(sp)
4201194a:	b171                	j	420115d6 <decoder_task+0x956>
4201194c:	fe377097          	auipc	ra,0xfe377
42011950:	a80080e7          	jalr	-1408(ra) # 403883cc <esp_log_timestamp>
42011954:	3c126737          	lui	a4,0x3c126
42011958:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
4201195c:	3c126637          	lui	a2,0x3c126
42011960:	86aa                	mv	a3,a0
42011962:	87a2                	mv	a5,s0
42011964:	85ba                	mv	a1,a4
42011966:	c8c60613          	addi	a2,a2,-884 # 3c125c8c <_esp_trace_encoder_array_end+0x5b6c>
4201196a:	4509                	li	a0,2
4201196c:	fe377097          	auipc	ra,0xfe377
42011970:	958080e7          	jalr	-1704(ra) # 403882c4 <esp_log>
42011974:	3c126737          	lui	a4,0x3c126
42011978:	0419                	addi	s0,s0,6 # 3006 <CSR_UINTSTATUS+0x2355>
4201197a:	4785                	li	a5,1
4201197c:	b9470693          	addi	a3,a4,-1132 # 3c125b94 <_esp_trace_encoder_array_end+0x5a74>
42011980:	0087e663          	bltu	a5,s0,4201198c <decoder_task+0xd0c>
42011984:	3c1267b7          	lui	a5,0x3c126
42011988:	b7878693          	addi	a3,a5,-1160 # 3c125b78 <_esp_trace_encoder_array_end+0x5a58>
4201198c:	3fc957b7          	lui	a5,0x3fc95
42011990:	b1c7a503          	lw	a0,-1252(a5) # 3fc94b1c <s_state>
42011994:	4601                	li	a2,0
42011996:	85a6                	mv	a1,s1
42011998:	587030ef          	jal	4201571e <native_state_set_audio>
4201199c:	c026                	sw	s1,0(sp)
4201199e:	b201                	j	4201129e <decoder_task+0x61e>
420119a0:	3c1257b7          	lui	a5,0x3c125
420119a4:	7f078793          	addi	a5,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
420119a8:	b7b5                	j	42011914 <decoder_task+0xc94>
420119aa:	3c1267b7          	lui	a5,0x3c126
420119ae:	b7878693          	addi	a3,a5,-1160 # 3c125b78 <_esp_trace_encoder_array_end+0x5a58>
420119b2:	ceaff06f          	j	42010e9c <decoder_task+0x21c>
420119b6:	3c1257b7          	lui	a5,0x3c125
420119ba:	7fc78793          	addi	a5,a5,2044 # 3c1257fc <_esp_trace_encoder_array_end+0x56dc>
420119be:	bf99                	j	42011914 <decoder_task+0xc94>
420119c0:	fe377097          	auipc	ra,0xfe377
420119c4:	a0c080e7          	jalr	-1524(ra) # 403883cc <esp_log_timestamp>
420119c8:	3c1257b7          	lui	a5,0x3c125
420119cc:	86aa                	mv	a3,a0
420119ce:	7f078793          	addi	a5,a5,2032 # 3c1257f0 <_esp_trace_encoder_array_end+0x56d0>
420119d2:	b979                	j	42011670 <decoder_task+0x9f0>
