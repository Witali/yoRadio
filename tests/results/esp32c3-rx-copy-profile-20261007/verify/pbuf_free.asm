
idf\esp32c3-oled-native\build-rx-copy\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4207f9c4 <pbuf_free>:
4207f9c4:	1101                	addi	sp,sp,-32
4207f9c6:	ce06                	sw	ra,28(sp)
4207f9c8:	cc22                	sw	s0,24(sp)
4207f9ca:	ca26                	sw	s1,20(sp)
4207f9cc:	c84a                	sw	s2,16(sp)
4207f9ce:	c64e                	sw	s3,12(sp)
4207f9d0:	c452                	sw	s4,8(sp)
4207f9d2:	0e050a63          	beqz	a0,4207fac6 <pbuf_free+0x102>
4207f9d6:	84aa                	mv	s1,a0
4207f9d8:	4901                	li	s2,0
4207f9da:	4989                	li	s3,2
4207f9dc:	4a05                	li	s4,1
4207f9de:	a811                	j	4207f9f2 <pbuf_free+0x2e>
4207f9e0:	489c                	lw	a5,16(s1)
4207f9e2:	cfd1                	beqz	a5,4207fa7e <pbuf_free+0xba>
4207f9e4:	8526                	mv	a0,s1
4207f9e6:	9782                	jalr	a5
4207f9e8:	0905                	addi	s2,s2,1
4207f9ea:	0ff97913          	zext.b	s2,s2
4207f9ee:	c039                	beqz	s0,4207fa34 <pbuf_free+0x70>
4207f9f0:	84a2                	mv	s1,s0
4207f9f2:	01a060ef          	jal	42085a0c <sys_arch_protect>
4207f9f6:	00e4c783          	lbu	a5,14(s1)
4207f9fa:	c3a5                	beqz	a5,4207fa5a <pbuf_free+0x96>
4207f9fc:	17fd                	addi	a5,a5,-1
4207f9fe:	0ff7f413          	zext.b	s0,a5
4207fa02:	00848723          	sb	s0,14(s1)
4207fa06:	03a060ef          	jal	42085a40 <sys_arch_unprotect>
4207fa0a:	e40d                	bnez	s0,4207fa34 <pbuf_free+0x70>
4207fa0c:	00d4c783          	lbu	a5,13(s1)
4207fa10:	4080                	lw	s0,0(s1)
4207fa12:	8b89                	andi	a5,a5,2
4207fa14:	f7f1                	bnez	a5,4207f9e0 <pbuf_free+0x1c>
4207fa16:	00c4c783          	lbu	a5,12(s1)
4207fa1a:	8bbd                	andi	a5,a5,15
4207fa1c:	03378563          	beq	a5,s3,4207fa46 <pbuf_free+0x82>
4207fa20:	03478863          	beq	a5,s4,4207fa50 <pbuf_free+0x8c>
4207fa24:	efbd                	bnez	a5,4207faa2 <pbuf_free+0xde>
4207fa26:	8526                	mv	a0,s1
4207fa28:	0905                	addi	s2,s2,1
4207fa2a:	b5aa70ef          	jal	42026d84 <__wrap_mem_free>
4207fa2e:	0ff97913          	zext.b	s2,s2
4207fa32:	fc5d                	bnez	s0,4207f9f0 <pbuf_free+0x2c>
4207fa34:	40f2                	lw	ra,28(sp)
4207fa36:	4462                	lw	s0,24(sp)
4207fa38:	44d2                	lw	s1,20(sp)
4207fa3a:	49b2                	lw	s3,12(sp)
4207fa3c:	4a22                	lw	s4,8(sp)
4207fa3e:	854a                	mv	a0,s2
4207fa40:	4942                	lw	s2,16(sp)
4207fa42:	6105                	addi	sp,sp,32
4207fa44:	8082                	ret
4207fa46:	85a6                	mv	a1,s1
4207fa48:	4539                	li	a0,14
4207fa4a:	88ba40ef          	jal	420242d4 <__wrap_memp_free>
4207fa4e:	bf69                	j	4207f9e8 <pbuf_free+0x24>
4207fa50:	85a6                	mv	a1,s1
4207fa52:	4535                	li	a0,13
4207fa54:	881a40ef          	jal	420242d4 <__wrap_memp_free>
4207fa58:	bf41                	j	4207f9e8 <pbuf_free+0x24>
4207fa5a:	3c1316b7          	lui	a3,0x3c131
4207fa5e:	3c174637          	lui	a2,0x3c174
4207fa62:	3c131537          	lui	a0,0x3c131
4207fa66:	59c68693          	addi	a3,a3,1436 # 3c13159c <_esp_trace_encoder_array_end+0x1147c>
4207fa6a:	11460613          	addi	a2,a2,276 # 3c174114 <__func__.7>
4207fa6e:	54850513          	addi	a0,a0,1352 # 3c131548 <_esp_trace_encoder_array_end+0x11428>
4207fa72:	2f300593          	li	a1,755
4207fa76:	fe306097          	auipc	ra,0xfe306
4207fa7a:	7b0080e7          	jalr	1968(ra) # 40386226 <__assert_func>
4207fa7e:	3c1316b7          	lui	a3,0x3c131
4207fa82:	3c174637          	lui	a2,0x3c174
4207fa86:	3c131537          	lui	a0,0x3c131
4207fa8a:	5b468693          	addi	a3,a3,1460 # 3c1315b4 <_esp_trace_encoder_array_end+0x11494>
4207fa8e:	11460613          	addi	a2,a2,276 # 3c174114 <__func__.7>
4207fa92:	54850513          	addi	a0,a0,1352 # 3c131548 <_esp_trace_encoder_array_end+0x11428>
4207fa96:	30100593          	li	a1,769
4207fa9a:	fe306097          	auipc	ra,0xfe306
4207fa9e:	78c080e7          	jalr	1932(ra) # 40386226 <__assert_func>
4207faa2:	3c1316b7          	lui	a3,0x3c131
4207faa6:	3c174637          	lui	a2,0x3c174
4207faaa:	3c131537          	lui	a0,0x3c131
4207faae:	5d868693          	addi	a3,a3,1496 # 3c1315d8 <_esp_trace_encoder_array_end+0x114b8>
4207fab2:	11460613          	addi	a2,a2,276 # 3c174114 <__func__.7>
4207fab6:	54850513          	addi	a0,a0,1352 # 3c131548 <_esp_trace_encoder_array_end+0x11428>
4207faba:	31100593          	li	a1,785
4207fabe:	fe306097          	auipc	ra,0xfe306
4207fac2:	768080e7          	jalr	1896(ra) # 40386226 <__assert_func>
4207fac6:	3c1336b7          	lui	a3,0x3c133
4207faca:	3c174637          	lui	a2,0x3c174
4207face:	3c131537          	lui	a0,0x3c131
4207fad2:	40468693          	addi	a3,a3,1028 # 3c133404 <_esp_trace_encoder_array_end+0x132e4>
4207fad6:	11460613          	addi	a2,a2,276 # 3c174114 <__func__.7>
4207fada:	54850513          	addi	a0,a0,1352 # 3c131548 <_esp_trace_encoder_array_end+0x11428>
4207fade:	2de00593          	li	a1,734
4207fae2:	fe306097          	auipc	ra,0xfe306
4207fae6:	744080e7          	jalr	1860(ra) # 40386226 <__assert_func>
