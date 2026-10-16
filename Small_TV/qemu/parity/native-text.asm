
small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42012cf4 <text_utf8_decode>:
42012cf4:	88aa                	mv	a7,a0
42012cf6:	e219                	bnez	a2,42012cfc <text_utf8_decode+0x8>
42012cf8:	4501                	li	a0,0
42012cfa:	8082                	ret
42012cfc:	00062023          	sw	zero,0(a2)
42012d00:	dd65                	beqz	a0,42012cf8 <text_utf8_decode+0x4>
42012d02:	d9fd                	beqz	a1,42012cf8 <text_utf8_decode+0x4>
42012d04:	00054783          	lbu	a5,0(a0)
42012d08:	dbe5                	beqz	a5,42012cf8 <text_utf8_decode+0x4>
42012d0a:	4785                	li	a5,1
42012d0c:	c21c                	sw	a5,0(a2)
42012d0e:	00054683          	lbu	a3,0(a0)
42012d12:	01869793          	slli	a5,a3,0x18
42012d16:	87e1                	srai	a5,a5,0x18
42012d18:	0007c463          	bltz	a5,42012d20 <text_utf8_decode+0x2c>
42012d1c:	8536                	mv	a0,a3
42012d1e:	8082                	ret
42012d20:	03e68793          	addi	a5,a3,62
42012d24:	0ff7f793          	zext.b	a5,a5
42012d28:	4775                	li	a4,29
42012d2a:	04f76e63          	bltu	a4,a5,42012d86 <text_utf8_decode+0x92>
42012d2e:	01f6f513          	andi	a0,a3,31
42012d32:	4709                	li	a4,2
42012d34:	08000693          	li	a3,128
42012d38:	08e5e263          	bltu	a1,a4,42012dbc <text_utf8_decode+0xc8>
42012d3c:	4585                	li	a1,1
42012d3e:	08000313          	li	t1,128
42012d42:	00b887b3          	add	a5,a7,a1
42012d46:	0007c803          	lbu	a6,0(a5)
42012d4a:	0c087793          	andi	a5,a6,192
42012d4e:	06679763          	bne	a5,t1,42012dbc <text_utf8_decode+0xc8>
42012d52:	00651793          	slli	a5,a0,0x6
42012d56:	03f87813          	andi	a6,a6,63
42012d5a:	0585                	addi	a1,a1,1
42012d5c:	00f86533          	or	a0,a6,a5
42012d60:	feb711e3          	bne	a4,a1,42012d42 <text_utf8_decode+0x4e>
42012d64:	001107b7          	lui	a5,0x110
42012d68:	17fd                	addi	a5,a5,-1 # 10ffff <CSR_UINTSTATUS+0x10f34e>
42012d6a:	04a7e963          	bltu	a5,a0,42012dbc <text_utf8_decode+0xc8>
42012d6e:	04d56763          	bltu	a0,a3,42012dbc <text_utf8_decode+0xc8>
42012d72:	77cd                	lui	a5,0xffff3
42012d74:	80078793          	addi	a5,a5,-2048 # ffff2800 <SYSTEM+0x9ff32800>
42012d78:	97aa                	add	a5,a5,a0
42012d7a:	7ff00693          	li	a3,2047
42012d7e:	02f6ff63          	bgeu	a3,a5,42012dbc <text_utf8_decode+0xc8>
42012d82:	c218                	sw	a4,0(a2)
42012d84:	8082                	ret
42012d86:	02068793          	addi	a5,a3,32
42012d8a:	0ff7f793          	zext.b	a5,a5
42012d8e:	473d                	li	a4,15
42012d90:	00f76963          	bltu	a4,a5,42012da2 <text_utf8_decode+0xae>
42012d94:	00e6f533          	and	a0,a3,a4
42012d98:	6685                	lui	a3,0x1
42012d9a:	80068693          	addi	a3,a3,-2048 # 800 <ALIGN_VECTOR_TABLE+0x700>
42012d9e:	470d                	li	a4,3
42012da0:	bf61                	j	42012d38 <text_utf8_decode+0x44>
42012da2:	01068813          	addi	a6,a3,16
42012da6:	6541                	lui	a0,0x10
42012da8:	0ff87813          	zext.b	a6,a6
42012dac:	4711                	li	a4,4
42012dae:	1575                	addi	a0,a0,-3 # fffd <CSR_UINTSTATUS+0xf34c>
42012db0:	01076863          	bltu	a4,a6,42012dc0 <text_utf8_decode+0xcc>
42012db4:	0076f513          	andi	a0,a3,7
42012db8:	66c1                	lui	a3,0x10
42012dba:	bfbd                	j	42012d38 <text_utf8_decode+0x44>
42012dbc:	6541                	lui	a0,0x10
42012dbe:	1575                	addi	a0,a0,-3 # fffd <CSR_UINTSTATUS+0xf34c>
42012dc0:	8082                	ret


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42012dc2 <text_utf8_copy>:
42012dc2:	715d                	addi	sp,sp,-80
42012dc4:	c686                	sw	ra,76(sp)
42012dc6:	c4a2                	sw	s0,72(sp)
42012dc8:	c2a6                	sw	s1,68(sp)
42012dca:	c0ca                	sw	s2,64(sp)
42012dcc:	de4e                	sw	s3,60(sp)
42012dce:	dc52                	sw	s4,56(sp)
42012dd0:	da56                	sw	s5,52(sp)
42012dd2:	d85a                	sw	s6,48(sp)
42012dd4:	d65e                	sw	s7,44(sp)
42012dd6:	d462                	sw	s8,40(sp)
42012dd8:	d266                	sw	s9,36(sp)
42012dda:	c509                	beqz	a0,42012de4 <text_utf8_copy+0x22>
42012ddc:	c581                	beqz	a1,42012de4 <text_utf8_copy+0x22>
42012dde:	e215                	bnez	a2,42012e02 <text_utf8_copy+0x40>
42012de0:	00050023          	sb	zero,0(a0)
42012de4:	4401                	li	s0,0
42012de6:	40b6                	lw	ra,76(sp)
42012de8:	8522                	mv	a0,s0
42012dea:	4426                	lw	s0,72(sp)
42012dec:	4496                	lw	s1,68(sp)
42012dee:	4906                	lw	s2,64(sp)
42012df0:	59f2                	lw	s3,60(sp)
42012df2:	5a62                	lw	s4,56(sp)
42012df4:	5ad2                	lw	s5,52(sp)
42012df6:	5b42                	lw	s6,48(sp)
42012df8:	5bb2                	lw	s7,44(sp)
42012dfa:	5c22                	lw	s8,40(sp)
42012dfc:	5c92                	lw	s9,36(sp)
42012dfe:	6161                	addi	sp,sp,80
42012e00:	8082                	ret
42012e02:	84aa                	mv	s1,a0
42012e04:	8532                	mv	a0,a2
42012e06:	89b6                	mv	s3,a3
42012e08:	8932                	mv	s2,a2
42012e0a:	8a2e                	mv	s4,a1
42012e0c:	7b41                	lui	s6,0xffff0
42012e0e:	fdfed097          	auipc	ra,0xfdfed
42012e12:	69a080e7          	jalr	1690(ra) # 400004a8 <strlen>
42012e16:	8baa                	mv	s7,a0
42012e18:	4401                	li	s0,0
42012e1a:	0b0d                	addi	s6,s6,3 # ffff0003 <SYSTEM+0x9ff30003>
42012e1c:	03f00c13          	li	s8,63
42012e20:	00848ab3          	add	s5,s1,s0
42012e24:	87de                	mv	a5,s7
42012e26:	0179f363          	bgeu	s3,s7,42012e2c <text_utf8_copy+0x6a>
42012e2a:	87ce                	mv	a5,s3
42012e2c:	00f46563          	bltu	s0,a5,42012e36 <text_utf8_copy+0x74>
42012e30:	000a8023          	sb	zero,0(s5)
42012e34:	bf4d                	j	42012de6 <text_utf8_copy+0x24>
42012e36:	00890cb3          	add	s9,s2,s0
42012e3a:	0870                	addi	a2,sp,28
42012e3c:	408b85b3          	sub	a1,s7,s0
42012e40:	8566                	mv	a0,s9
42012e42:	eb3ff0ef          	jal	42012cf4 <text_utf8_decode>
42012e46:	4672                	lw	a2,28(sp)
42012e48:	d665                	beqz	a2,42012e30 <text_utf8_copy+0x6e>
42012e4a:	408987b3          	sub	a5,s3,s0
42012e4e:	fec7e1e3          	bltu	a5,a2,42012e30 <text_utf8_copy+0x6e>
42012e52:	408a07b3          	sub	a5,s4,s0
42012e56:	fcf67de3          	bgeu	a2,a5,42012e30 <text_utf8_copy+0x6e>
42012e5a:	fff60793          	addi	a5,a2,-1
42012e5e:	e799                	bnez	a5,42012e6c <text_utf8_copy+0xaa>
42012e60:	955a                	add	a0,a0,s6
42012e62:	e509                	bnez	a0,42012e6c <text_utf8_copy+0xaa>
42012e64:	018a8023          	sb	s8,0(s5)
42012e68:	9432                	add	s0,s0,a2
42012e6a:	bf5d                	j	42012e20 <text_utf8_copy+0x5e>
42012e6c:	85e6                	mv	a1,s9
42012e6e:	8556                	mv	a0,s5
42012e70:	c632                	sw	a2,12(sp)
42012e72:	fe374097          	auipc	ra,0xfe374
42012e76:	49c080e7          	jalr	1180(ra) # 4038730e <memmove>
42012e7a:	4632                	lw	a2,12(sp)
42012e7c:	b7f5                	j	42012e68 <text_utf8_copy+0xa6>


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200d8aa <text_token>:
4200d8aa:	4785                	li	a5,1
4200d8ac:	04f58663          	beq	a1,a5,4200d8f8 <text_token+0x4e>
4200d8b0:	00054783          	lbu	a5,0(a0)
4200d8b4:	0a100713          	li	a4,161
4200d8b8:	02e79763          	bne	a5,a4,4200d8e6 <text_token+0x3c>
4200d8bc:	00154703          	lbu	a4,1(a0)
4200d8c0:	0e600793          	li	a5,230
4200d8c4:	02f71a63          	bne	a4,a5,4200d8f8 <text_token+0x4e>
4200d8c8:	4789                	li	a5,2
4200d8ca:	c21c                	sw	a5,0(a2)
4200d8cc:	00054703          	lbu	a4,0(a0)
4200d8d0:	0a100793          	li	a5,161
4200d8d4:	6509                	lui	a0,0x2
4200d8d6:	10950513          	addi	a0,a0,265 # 2109 <CSR_UINTSTATUS+0x1458>
4200d8da:	06f71863          	bne	a4,a5,4200d94a <text_token+0xa0>
4200d8de:	6509                	lui	a0,0x2
4200d8e0:	10350513          	addi	a0,a0,259 # 2103 <CSR_UINTSTATUS+0x1452>
4200d8e4:	8082                	ret
4200d8e6:	0a800713          	li	a4,168
4200d8ea:	00e79763          	bne	a5,a4,4200d8f8 <text_token+0x4e>
4200d8ee:	00154703          	lbu	a4,1(a0)
4200d8f2:	04800793          	li	a5,72
4200d8f6:	b7f9                	j	4200d8c4 <text_token+0x1a>
4200d8f8:	1101                	addi	sp,sp,-32
4200d8fa:	cc22                	sw	s0,24(sp)
4200d8fc:	c632                	sw	a2,12(sp)
4200d8fe:	c42e                	sw	a1,8(sp)
4200d900:	ce06                	sw	ra,28(sp)
4200d902:	842a                	mv	s0,a0
4200d904:	3f0050ef          	jal	42012cf4 <text_utf8_decode>
4200d908:	0b000793          	li	a5,176
4200d90c:	45a2                	lw	a1,8(sp)
4200d90e:	4632                	lw	a2,12(sp)
4200d910:	02f51563          	bne	a0,a5,4200d93a <text_token+0x90>
4200d914:	421c                	lw	a5,0(a2)
4200d916:	02b7f263          	bgeu	a5,a1,4200d93a <text_token+0x90>
4200d91a:	943e                	add	s0,s0,a5
4200d91c:	00044703          	lbu	a4,0(s0)
4200d920:	04300693          	li	a3,67
4200d924:	00d70f63          	beq	a4,a3,4200d942 <text_token+0x98>
4200d928:	04600693          	li	a3,70
4200d92c:	00d71763          	bne	a4,a3,4200d93a <text_token+0x90>
4200d930:	6509                	lui	a0,0x2
4200d932:	10950513          	addi	a0,a0,265 # 2109 <CSR_UINTSTATUS+0x1458>
4200d936:	0785                	addi	a5,a5,1
4200d938:	c21c                	sw	a5,0(a2)
4200d93a:	40f2                	lw	ra,28(sp)
4200d93c:	4462                	lw	s0,24(sp)
4200d93e:	6105                	addi	sp,sp,32
4200d940:	8082                	ret
4200d942:	6509                	lui	a0,0x2
4200d944:	10350513          	addi	a0,a0,259 # 2103 <CSR_UINTSTATUS+0x1452>
4200d948:	b7fd                	j	4200d936 <text_token+0x8c>
4200d94a:	8082                	ret


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200da7e <draw_text>:
4200da7e:	7175                	addi	sp,sp,-144
4200da80:	dece                	sw	s3,124(sp)
4200da82:	89be                	mv	s3,a5
4200da84:	09015783          	lhu	a5,144(sp)
4200da88:	d4e2                	sw	s8,104(sp)
4200da8a:	c706                	sw	ra,140(sp)
4200da8c:	c522                	sw	s0,136(sp)
4200da8e:	c326                	sw	s1,132(sp)
4200da90:	c14a                	sw	s2,128(sp)
4200da92:	dcd2                	sw	s4,120(sp)
4200da94:	dad6                	sw	s5,116(sp)
4200da96:	d8da                	sw	s6,112(sp)
4200da98:	d6de                	sw	s7,108(sp)
4200da9a:	d2e6                	sw	s9,100(sp)
4200da9c:	d0ea                	sw	s10,96(sp)
4200da9e:	ceee                	sw	s11,92(sp)
4200daa0:	ce3e                	sw	a5,28(sp)
4200daa2:	09414c03          	lbu	s8,148(sp)
4200daa6:	04098563          	beqz	s3,4200daf0 <draw_text+0x72>
4200daaa:	842a                	mv	s0,a0
4200daac:	854e                	mv	a0,s3
4200daae:	84c2                	mv	s1,a6
4200dab0:	8cba                	mv	s9,a4
4200dab2:	d046                	sw	a7,32(sp)
4200dab4:	8b36                	mv	s6,a3
4200dab6:	8ab2                	mv	s5,a2
4200dab8:	cc2e                	sw	a1,24(sp)
4200daba:	fdff3097          	auipc	ra,0xfdff3
4200dabe:	9ee080e7          	jalr	-1554(ra) # 400004a8 <strlen>
4200dac2:	ff048793          	addi	a5,s1,-16
4200dac6:	00f037b3          	snez	a5,a5
4200daca:	001c4713          	xori	a4,s8,1
4200dace:	8fd9                	or	a5,a5,a4
4200dad0:	d23e                	sw	a5,36(sp)
4200dad2:	77f9                	lui	a5,0xffffe
4200dad4:	ef778793          	addi	a5,a5,-265 # ffffdef7 <SYSTEM+0x9ff3def7>
4200dad8:	d43e                	sw	a5,40(sp)
4200dada:	77f9                	lui	a5,0xffffe
4200dadc:	efd78793          	addi	a5,a5,-259 # ffffdefd <SYSTEM+0x9ff3defd>
4200dae0:	8baa                	mv	s7,a0
4200dae2:	d63e                	sw	a5,44(sp)
4200dae4:	07f00d93          	li	s11,127
4200dae8:	01645463          	bge	s0,s6,4200daf0 <draw_text+0x72>
4200daec:	020b9163          	bnez	s7,4200db0e <draw_text+0x90>
4200daf0:	40ba                	lw	ra,140(sp)
4200daf2:	442a                	lw	s0,136(sp)
4200daf4:	449a                	lw	s1,132(sp)
4200daf6:	490a                	lw	s2,128(sp)
4200daf8:	59f6                	lw	s3,124(sp)
4200dafa:	5a66                	lw	s4,120(sp)
4200dafc:	5ad6                	lw	s5,116(sp)
4200dafe:	5b46                	lw	s6,112(sp)
4200db00:	5bb6                	lw	s7,108(sp)
4200db02:	5c26                	lw	s8,104(sp)
4200db04:	5c96                	lw	s9,100(sp)
4200db06:	5d06                	lw	s10,96(sp)
4200db08:	4df6                	lw	s11,92(sp)
4200db0a:	6149                	addi	sp,sp,144
4200db0c:	8082                	ret
4200db0e:	1870                	addi	a2,sp,60
4200db10:	85de                	mv	a1,s7
4200db12:	854e                	mv	a0,s3
4200db14:	d97ff0ef          	jal	4200d8aa <text_token>
4200db18:	57a2                	lw	a5,40(sp)
4200db1a:	5732                	lw	a4,44(sp)
4200db1c:	0014d913          	srli	s2,s1,0x1
4200db20:	97aa                	add	a5,a5,a0
4200db22:	972a                	add	a4,a4,a0
4200db24:	8d2a                	mv	s10,a0
4200db26:	0017b793          	seqz	a5,a5
4200db2a:	c311                	beqz	a4,4200db2e <draw_text+0xb0>
4200db2c:	c3a5                	beqz	a5,4200db8c <draw_text+0x10e>
4200db2e:	008c                	addi	a1,sp,64
4200db30:	853e                	mv	a0,a5
4200db32:	f23ff0ef          	jal	4200da54 <factory_symbol>
4200db36:	8926                	mv	s2,s1
4200db38:	ff890793          	addi	a5,s2,-8
4200db3c:	5d72                	lw	s10,60(sp)
4200db3e:	e781                	bnez	a5,4200db46 <draw_text+0xc8>
4200db40:	5792                	lw	a5,36(sp)
4200db42:	4a15                	li	s4,5
4200db44:	c391                	beqz	a5,4200db48 <draw_text+0xca>
4200db46:	8a4a                	mv	s4,s2
4200db48:	c92d                	beqz	a0,4200dbba <draw_text+0x13c>
4200db4a:	000c8b63          	beqz	s9,4200db60 <draw_text+0xe2>
4200db4e:	4796                	lw	a5,68(sp)
4200db50:	0147f363          	bgeu	a5,s4,4200db56 <draw_text+0xd8>
4200db54:	87d2                	mv	a5,s4
4200db56:	408b0733          	sub	a4,s6,s0
4200db5a:	f8f76be3          	bltu	a4,a5,4200daf0 <draw_text+0x72>
4200db5e:	c125                	beqz	a0,4200dbbe <draw_text+0x140>
4200db60:	040ac463          	bltz	s5,4200dba8 <draw_text+0x12a>
4200db64:	47f2                	lw	a5,28(sp)
4200db66:	4762                	lw	a4,24(sp)
4200db68:	5882                	lw	a7,32(sp)
4200db6a:	c03e                	sw	a5,0(sp)
4200db6c:	47e2                	lw	a5,24(sp)
4200db6e:	c262                	sw	s8,4(sp)
4200db70:	86d6                	mv	a3,s5
4200db72:	00978833          	add	a6,a5,s1
4200db76:	0090                	addi	a2,sp,64
4200db78:	87da                	mv	a5,s6
4200db7a:	85ba                	mv	a1,a4
4200db7c:	8522                	mv	a0,s0
4200db7e:	bbeff0ef          	jal	4200cf3c <display_bitmap_region>
4200db82:	99ea                	add	s3,s3,s10
4200db84:	41ab8bb3          	sub	s7,s7,s10
4200db88:	9452                	add	s0,s0,s4
4200db8a:	bfb9                	j	4200dae8 <draw_text+0x6a>
4200db8c:	0090                	addi	a2,sp,64
4200db8e:	85a6                	mv	a1,s1
4200db90:	dbdff0ef          	jal	4200d94c <factory_glyph>
4200db94:	f155                	bnez	a0,4200db38 <draw_text+0xba>
4200db96:	fbadf1e3          	bgeu	s11,s10,4200db38 <draw_text+0xba>
4200db9a:	0090                	addi	a2,sp,64
4200db9c:	85a6                	mv	a1,s1
4200db9e:	03f00513          	li	a0,63
4200dba2:	dabff0ef          	jal	4200d94c <factory_glyph>
4200dba6:	bf49                	j	4200db38 <draw_text+0xba>
4200dba8:	4772                	lw	a4,28(sp)
4200dbaa:	5682                	lw	a3,32(sp)
4200dbac:	45e2                	lw	a1,24(sp)
4200dbae:	87e2                	mv	a5,s8
4200dbb0:	0090                	addi	a2,sp,64
4200dbb2:	8522                	mv	a0,s0
4200dbb4:	d32ff0ef          	jal	4200d0e6 <display_bitmap>
4200dbb8:	b7e9                	j	4200db82 <draw_text+0x104>
4200dbba:	f80c9de3          	bnez	s9,4200db54 <draw_text+0xd6>
4200dbbe:	fc0c12e3          	bnez	s8,4200db82 <draw_text+0x104>
4200dbc2:	8522                	mv	a0,s0
4200dbc4:	000ac563          	bltz	s5,4200dbce <draw_text+0x150>
4200dbc8:	01545363          	bge	s0,s5,4200dbce <draw_text+0x150>
4200dbcc:	8556                	mv	a0,s5
4200dbce:	00890633          	add	a2,s2,s0
4200dbd2:	00cb5363          	bge	s6,a2,4200dbd8 <draw_text+0x15a>
4200dbd6:	865a                	mv	a2,s6
4200dbd8:	4772                	lw	a4,28(sp)
4200dbda:	45e2                	lw	a1,24(sp)
4200dbdc:	86a6                	mv	a3,s1
4200dbde:	8e09                	sub	a2,a2,a0
4200dbe0:	814ff0ef          	jal	4200cbf4 <display_fill>
4200dbe4:	bf79                	j	4200db82 <draw_text+0x104>


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200d94c <factory_glyph>:
4200d94c:	3c1006b7          	lui	a3,0x3c100
4200d950:	56868693          	addi	a3,a3,1384 # 3c100568 <factory_fonts>
4200d954:	4701                	li	a4,0
4200d956:	87b6                	mv	a5,a3
4200d958:	4819                	li	a6,6
4200d95a:	0086a883          	lw	a7,8(a3)
4200d95e:	02b89663          	bne	a7,a1,4200d98a <factory_glyph+0x3e>
4200d962:	46e1                	li	a3,24
4200d964:	02d70733          	mul	a4,a4,a3
4200d968:	97ba                	add	a5,a5,a4
4200d96a:	4b98                	lw	a4,16(a5)
4200d96c:	02e57463          	bgeu	a0,a4,4200d994 <factory_glyph+0x48>
4200d970:	07f00793          	li	a5,127
4200d974:	4701                	li	a4,0
4200d976:	0aa7f563          	bgeu	a5,a0,4200da20 <factory_glyph+0xd4>
4200d97a:	3c0d3837          	lui	a6,0x3c0d3
4200d97e:	1c400693          	li	a3,452
4200d982:	4781                	li	a5,0
4200d984:	35080813          	addi	a6,a6,848 # 3c0d3350 <unicode_codepoints>
4200d988:	a881                	j	4200d9d8 <factory_glyph+0x8c>
4200d98a:	0705                	addi	a4,a4,1
4200d98c:	06e1                	addi	a3,a3,24
4200d98e:	fd0716e3          	bne	a4,a6,4200d95a <factory_glyph+0xe>
4200d992:	bff9                	j	4200d970 <factory_glyph+0x24>
4200d994:	4bd4                	lw	a3,20(a5)
4200d996:	96ba                	add	a3,a3,a4
4200d998:	fcd57ce3          	bgeu	a0,a3,4200d970 <factory_glyph+0x24>
4200d99c:	47d4                	lw	a3,12(a5)
4200d99e:	8d19                	sub	a0,a0,a4
4200d9a0:	0047a803          	lw	a6,4(a5)
4200d9a4:	02b68733          	mul	a4,a3,a1
4200d9a8:	439c                	lw	a5,0(a5)
4200d9aa:	01062223          	sw	a6,4(a2)
4200d9ae:	c60c                	sw	a1,8(a2)
4200d9b0:	c654                	sw	a3,12(a2)
4200d9b2:	02e50533          	mul	a0,a0,a4
4200d9b6:	97aa                	add	a5,a5,a0
4200d9b8:	c21c                	sw	a5,0(a2)
4200d9ba:	4505                	li	a0,1
4200d9bc:	8082                	ret
4200d9be:	40f68733          	sub	a4,a3,a5
4200d9c2:	8305                	srli	a4,a4,0x1
4200d9c4:	973e                	add	a4,a4,a5
4200d9c6:	00271893          	slli	a7,a4,0x2
4200d9ca:	98c2                	add	a7,a7,a6
4200d9cc:	0008a883          	lw	a7,0(a7)
4200d9d0:	04a8fa63          	bgeu	a7,a0,4200da24 <factory_glyph+0xd8>
4200d9d4:	00170793          	addi	a5,a4,1
4200d9d8:	fed7e3e3          	bltu	a5,a3,4200d9be <factory_glyph+0x72>
4200d9dc:	1c400693          	li	a3,452
4200d9e0:	4701                	li	a4,0
4200d9e2:	02d78f63          	beq	a5,a3,4200da20 <factory_glyph+0xd4>
4200d9e6:	3c0d3737          	lui	a4,0x3c0d3
4200d9ea:	00279693          	slli	a3,a5,0x2
4200d9ee:	35070713          	addi	a4,a4,848 # 3c0d3350 <unicode_codepoints>
4200d9f2:	9736                	add	a4,a4,a3
4200d9f4:	4314                	lw	a3,0(a4)
4200d9f6:	4701                	li	a4,0
4200d9f8:	02d51463          	bne	a0,a3,4200da20 <factory_glyph+0xd4>
4200d9fc:	46c1                	li	a3,16
4200d9fe:	02d59563          	bne	a1,a3,4200da28 <factory_glyph+0xdc>
4200da02:	3c0d1737          	lui	a4,0x3c0d1
4200da06:	0792                	slli	a5,a5,0x4
4200da08:	71070713          	addi	a4,a4,1808 # 3c0d1710 <unicode_font16>
4200da0c:	97ba                	add	a5,a5,a4
4200da0e:	0015d713          	srli	a4,a1,0x1
4200da12:	c258                	sw	a4,4(a2)
4200da14:	071d                	addi	a4,a4,7
4200da16:	830d                	srli	a4,a4,0x3
4200da18:	c658                	sw	a4,12(a2)
4200da1a:	c21c                	sw	a5,0(a2)
4200da1c:	c60c                	sw	a1,8(a2)
4200da1e:	4705                	li	a4,1
4200da20:	853a                	mv	a0,a4
4200da22:	8082                	ret
4200da24:	86ba                	mv	a3,a4
4200da26:	bf4d                	j	4200d9d8 <factory_glyph+0x8c>
4200da28:	46e1                	li	a3,24
4200da2a:	00d59b63          	bne	a1,a3,4200da40 <factory_glyph+0xf4>
4200da2e:	03000713          	li	a4,48
4200da32:	02e787b3          	mul	a5,a5,a4
4200da36:	3c0cc737          	lui	a4,0x3c0cc
4200da3a:	25070713          	addi	a4,a4,592 # 3c0cc250 <unicode_font24>
4200da3e:	b7f9                	j	4200da0c <factory_glyph+0xc0>
4200da40:	02000693          	li	a3,32
4200da44:	fcd59ee3          	bne	a1,a3,4200da20 <factory_glyph+0xd4>
4200da48:	3c0c5737          	lui	a4,0x3c0c5
4200da4c:	079a                	slli	a5,a5,0x6
4200da4e:	15070713          	addi	a4,a4,336 # 3c0c5150 <unicode_font32>
4200da52:	bf6d                	j	4200da0c <factory_glyph+0xc0>


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200dc44 <display_factory_text_width>:
4200dc44:	7139                	addi	sp,sp,-64
4200dc46:	da26                	sw	s1,52(sp)
4200dc48:	de06                	sw	ra,60(sp)
4200dc4a:	dc22                	sw	s0,56(sp)
4200dc4c:	d84a                	sw	s2,48(sp)
4200dc4e:	d64e                	sw	s3,44(sp)
4200dc50:	d452                	sw	s4,40(sp)
4200dc52:	4481                	li	s1,0
4200dc54:	c105                	beqz	a0,4200dc74 <display_factory_text_width+0x30>
4200dc56:	892e                	mv	s2,a1
4200dc58:	842a                	mv	s0,a0
4200dc5a:	79f9                	lui	s3,0xffffe
4200dc5c:	fdff3097          	auipc	ra,0xfdff3
4200dc60:	84c080e7          	jalr	-1972(ra) # 400004a8 <strlen>
4200dc64:	7a79                	lui	s4,0xffffe
4200dc66:	85aa                	mv	a1,a0
4200dc68:	4481                	li	s1,0
4200dc6a:	ef798993          	addi	s3,s3,-265 # ffffdef7 <SYSTEM+0x9ff3def7>
4200dc6e:	efda0a13          	addi	s4,s4,-259 # ffffdefd <SYSTEM+0x9ff3defd>
4200dc72:	e991                	bnez	a1,4200dc86 <display_factory_text_width+0x42>
4200dc74:	50f2                	lw	ra,60(sp)
4200dc76:	5462                	lw	s0,56(sp)
4200dc78:	5942                	lw	s2,48(sp)
4200dc7a:	59b2                	lw	s3,44(sp)
4200dc7c:	5a22                	lw	s4,40(sp)
4200dc7e:	8526                	mv	a0,s1
4200dc80:	54d2                	lw	s1,52(sp)
4200dc82:	6121                	addi	sp,sp,64
4200dc84:	8082                	ret
4200dc86:	0870                	addi	a2,sp,28
4200dc88:	8522                	mv	a0,s0
4200dc8a:	c62e                	sw	a1,12(sp)
4200dc8c:	c1fff0ef          	jal	4200d8aa <text_token>
4200dc90:	013507b3          	add	a5,a0,s3
4200dc94:	45b2                	lw	a1,12(sp)
4200dc96:	c789                	beqz	a5,4200dca0 <display_factory_text_width+0x5c>
4200dc98:	9552                	add	a0,a0,s4
4200dc9a:	00195793          	srli	a5,s2,0x1
4200dc9e:	e111                	bnez	a0,4200dca2 <display_factory_text_width+0x5e>
4200dca0:	87ca                	mv	a5,s2
4200dca2:	94be                	add	s1,s1,a5
4200dca4:	47f2                	lw	a5,28(sp)
4200dca6:	943e                	add	s0,s0,a5
4200dca8:	8d9d                	sub	a1,a1,a5
4200dcaa:	b7e1                	j	4200dc72 <display_factory_text_width+0x2e>


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42010dce <url_escape>:
42010dce:	4665                	li	a2,25
42010dd0:	00054783          	lbu	a5,0(a0)
42010dd4:	e781                	bnez	a5,42010ddc <url_escape+0xe>
42010dd6:	00058023          	sb	zero,0(a1)
42010dda:	8082                	ret
42010ddc:	fdf7f713          	andi	a4,a5,-33
42010de0:	fbf70713          	addi	a4,a4,-65
42010de4:	0ff77713          	zext.b	a4,a4
42010de8:	02e67463          	bgeu	a2,a4,42010e10 <url_escape+0x42>
42010dec:	fd078693          	addi	a3,a5,-48
42010df0:	fd378713          	addi	a4,a5,-45
42010df4:	00273713          	sltiu	a4,a4,2
42010df8:	00a6b693          	sltiu	a3,a3,10
42010dfc:	8ed9                	or	a3,a3,a4
42010dfe:	fa178713          	addi	a4,a5,-95
42010e02:	00173713          	seqz	a4,a4
42010e06:	8f55                	or	a4,a4,a3
42010e08:	e701                	bnez	a4,42010e10 <url_escape+0x42>
42010e0a:	f8278713          	addi	a4,a5,-126
42010e0e:	e711                	bnez	a4,42010e1a <url_escape+0x4c>
42010e10:	00f58023          	sb	a5,0(a1)
42010e14:	0585                	addi	a1,a1,1
42010e16:	0505                	addi	a0,a0,1
42010e18:	bf65                	j	42010dd0 <url_escape+0x2>
42010e1a:	02500713          	li	a4,37
42010e1e:	00e58023          	sb	a4,0(a1)
42010e22:	3c0eb737          	lui	a4,0x3c0eb
42010e26:	99870713          	addi	a4,a4,-1640 # 3c0ea998 <hex.0>
42010e2a:	0047d693          	srli	a3,a5,0x4
42010e2e:	8bbd                	andi	a5,a5,15
42010e30:	96ba                	add	a3,a3,a4
42010e32:	973e                	add	a4,a4,a5
42010e34:	0006c683          	lbu	a3,0(a3)
42010e38:	00074783          	lbu	a5,0(a4)
42010e3c:	058d                	addi	a1,a1,3
42010e3e:	fed58f23          	sb	a3,-2(a1)
42010e42:	fef58fa3          	sb	a5,-1(a1)
42010e46:	bfc1                	j	42010e16 <url_escape+0x48>


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42010e48 <weather_task>:
42010e48:	8a010113          	addi	sp,sp,-1888
42010e4c:	04100613          	li	a2,65
42010e50:	4581                	li	a1,0
42010e52:	1068                	addi	a0,sp,44
42010e54:	74112e23          	sw	ra,1884(sp)
42010e58:	74912a23          	sw	s1,1876(sp)
42010e5c:	75312623          	sw	s3,1868(sp)
42010e60:	75412423          	sw	s4,1864(sp)
42010e64:	74812c23          	sw	s0,1880(sp)
42010e68:	75212823          	sw	s2,1872(sp)
42010e6c:	75512223          	sw	s5,1860(sp)
42010e70:	fdfef097          	auipc	ra,0xfdfef
42010e74:	618080e7          	jalr	1560(ra) # 40000488 <memset>
42010e78:	04100613          	li	a2,65
42010e7c:	4581                	li	a1,0
42010e7e:	1888                	addi	a0,sp,112
42010e80:	cc02                	sw	zero,24(sp)
42010e82:	ce02                	sw	zero,28(sp)
42010e84:	d002                	sw	zero,32(sp)
42010e86:	d202                	sw	zero,36(sp)
42010e88:	d402                	sw	zero,40(sp)
42010e8a:	fdfef097          	auipc	ra,0xfdfef
42010e8e:	5fe080e7          	jalr	1534(ra) # 40000488 <memset>
42010e92:	3fcb47b7          	lui	a5,0x3fcb4
42010e96:	3fcb04b7          	lui	s1,0x3fcb0
42010e9a:	4985                	li	s3,1
42010e9c:	92478a13          	addi	s4,a5,-1756 # 3fcb3924 <request_state>
42010ea0:	aa048493          	addi	s1,s1,-1376 # 3fcafaa0 <cached_weather>
42010ea4:	567d                	li	a2,-1
42010ea6:	4585                	li	a1,1
42010ea8:	4501                	li	a0,0
42010eaa:	7489c0ef          	jal	420ad5f2 <ulTaskGenericNotifyTake>
42010eae:	4615                	li	a2,5
42010eb0:	4585                	li	a1,1
42010eb2:	8552                	mv	a0,s4
42010eb4:	fe376097          	auipc	ra,0xfe376
42010eb8:	6d2080e7          	jalr	1746(ra) # 40387586 <__atomic_fetch_or_4>
42010ebc:	55f5                	li	a1,-3
42010ebe:	4615                	li	a2,5
42010ec0:	8552                	mv	a0,s4
42010ec2:	fe376097          	auipc	ra,0xfe376
42010ec6:	69c080e7          	jalr	1692(ra) # 4038755e <__atomic_fetch_and_4>
42010eca:	0fc8                	addi	a0,sp,980
42010ecc:	dc4fb0ef          	jal	4200c490 <settings_snapshot>
42010ed0:	43a10593          	addi	a1,sp,1082
42010ed4:	1068                	addi	a0,sp,44
42010ed6:	fe376097          	auipc	ra,0xfe376
42010eda:	77c080e7          	jalr	1916(ra) # 40387652 <strcmp>
42010ede:	e10d                	bnez	a0,42010f00 <weather_task+0xb8>
42010ee0:	47b10593          	addi	a1,sp,1147
42010ee4:	0828                	addi	a0,sp,24
42010ee6:	fe376097          	auipc	ra,0xfe376
42010eea:	76c080e7          	jalr	1900(ra) # 40387652 <strcmp>
42010eee:	e909                	bnez	a0,42010f00 <weather_task+0xb8>
42010ef0:	4d010593          	addi	a1,sp,1232
42010ef4:	1888                	addi	a0,sp,112
42010ef6:	fe376097          	auipc	ra,0xfe376
42010efa:	75c080e7          	jalr	1884(ra) # 40387652 <strcmp>
42010efe:	c939                	beqz	a0,42010f54 <weather_task+0x10c>
42010f00:	43a10593          	addi	a1,sp,1082
42010f04:	1068                	addi	a0,sp,44
42010f06:	fe377097          	auipc	ra,0xfe377
42010f0a:	862080e7          	jalr	-1950(ra) # 40387768 <strcpy>
42010f0e:	47b10593          	addi	a1,sp,1147
42010f12:	0828                	addi	a0,sp,24
42010f14:	fe377097          	auipc	ra,0xfe377
42010f18:	854080e7          	jalr	-1964(ra) # 40387768 <strcpy>
42010f1c:	4d010593          	addi	a1,sp,1232
42010f20:	1888                	addi	a0,sp,112
42010f22:	fe377097          	auipc	ra,0xfe377
42010f26:	846080e7          	jalr	-1978(ra) # 40387768 <strcpy>
42010f2a:	3fcb4437          	lui	s0,0x3fcb4
42010f2e:	92c42503          	lw	a0,-1748(s0) # 3fcb392c <weather_mutex>
42010f32:	55fd                	li	a1,-1
42010f34:	55e9b0ef          	jal	420ac492 <xQueueSemaphoreTake>
42010f38:	0f04a783          	lw	a5,240(s1)
42010f3c:	92c42503          	lw	a0,-1748(s0)
42010f40:	4681                	li	a3,0
42010f42:	0785                	addi	a5,a5,1
42010f44:	4601                	li	a2,0
42010f46:	4581                	li	a1,0
42010f48:	00048023          	sb	zero,0(s1)
42010f4c:	0ef4a823          	sw	a5,240(s1)
42010f50:	1229b0ef          	jal	420ac072 <xQueueGenericSend>
42010f54:	a96ff0ef          	jal	420101ea <network_connected>
42010f58:	14050e63          	beqz	a0,420110b4 <weather_task+0x26c>
42010f5c:	4d014783          	lbu	a5,1232(sp)
42010f60:	14078a63          	beqz	a5,420110b4 <weather_task+0x26c>
42010f64:	0a8c                	addi	a1,sp,336
42010f66:	43a10513          	addi	a0,sp,1082
42010f6a:	e65ff0ef          	jal	42010dce <url_escape>
42010f6e:	0c4c                	addi	a1,sp,532
42010f70:	4d010513          	addi	a0,sp,1232
42010f74:	e5bff0ef          	jal	42010dce <url_escape>
42010f78:	54010913          	addi	s2,sp,1344
42010f7c:	3c0b4637          	lui	a2,0x3c0b4
42010f80:	0c5c                	addi	a5,sp,532
42010f82:	47b10713          	addi	a4,sp,1147
42010f86:	0a94                	addi	a3,sp,336
42010f88:	2bc60613          	addi	a2,a2,700 # 3c0b42bc <_esp_libc_clock_array_end+0x416c>
42010f8c:	20000593          	li	a1,512
42010f90:	854a                	mv	a0,s2
42010f92:	6998c0ef          	jal	4209de2a <snprintf>
42010f96:	6589                	lui	a1,0x2
42010f98:	4781                	li	a5,0
42010f9a:	4801                	li	a6,0
42010f9c:	0585                	addi	a1,a1,1 # 2001 <CSR_UINTSTATUS+0x1350>
42010f9e:	4505                	li	a0,1
42010fa0:	c83e                	sw	a5,16(sp)
42010fa2:	ca42                	sw	a6,20(sp)
42010fa4:	fe376097          	auipc	ra,0xfe376
42010fa8:	222080e7          	jalr	546(ra) # 403871c6 <calloc>
42010fac:	c62a                	sw	a0,12(sp)
42010fae:	10050363          	beqz	a0,420110b4 <weather_task+0x26c>
42010fb2:	09800613          	li	a2,152
42010fb6:	4581                	li	a1,0
42010fb8:	1928                	addi	a0,sp,184
42010fba:	fdfef097          	auipc	ra,0xfdfef
42010fbe:	4ce080e7          	jalr	1230(ra) # 40000488 <memset>
42010fc2:	6789                	lui	a5,0x2
42010fc4:	71078793          	addi	a5,a5,1808 # 2710 <CSR_UINTSTATUS+0x1a5f>
42010fc8:	10f12223          	sw	a5,260(sp)
42010fcc:	420117b7          	lui	a5,0x42011
42010fd0:	0c878793          	addi	a5,a5,200 # 420110c8 <weather_http_event>
42010fd4:	10f12a23          	sw	a5,276(sp)
42010fd8:	40000793          	li	a5,1024
42010fdc:	10f12e23          	sw	a5,284(sp)
42010fe0:	12f12023          	sw	a5,288(sp)
42010fe4:	1948                	addi	a0,sp,180
42010fe6:	007c                	addi	a5,sp,12
42010fe8:	db4a                	sw	s2,180(sp)
42010fea:	11310423          	sb	s3,264(sp)
42010fee:	12f12223          	sw	a5,292(sp)
42010ff2:	6b4240ef          	jal	420356a6 <esp_http_client_init>
42010ff6:	8aaa                	mv	s5,a0
42010ff8:	10100413          	li	s0,257
42010ffc:	c915                	beqz	a0,42011030 <weather_task+0x1e8>
42010ffe:	194250ef          	jal	42036192 <esp_http_client_perform>
42011002:	842a                	mv	s0,a0
42011004:	8556                	mv	a0,s5
42011006:	0c4250ef          	jal	420360ca <esp_http_client_get_status_code>
4201100a:	0c800793          	li	a5,200
4201100e:	0af51b63          	bne	a0,a5,420110c4 <weather_task+0x27c>
42011012:	01414783          	lbu	a5,20(sp)
42011016:	e7dd                	bnez	a5,420110c4 <weather_task+0x27c>
42011018:	8556                	mv	a0,s5
4201101a:	314240ef          	jal	4203532e <esp_http_client_cleanup>
4201101e:	e809                	bnez	s0,42011030 <weather_task+0x1e8>
42011020:	45c2                	lw	a1,16(sp)
42011022:	4532                	lw	a0,12(sp)
42011024:	0db4                	addi	a3,sp,728
42011026:	0fd0                	addi	a2,sp,980
42011028:	24dd                	jal	4201130e <weather_parse_response>
4201102a:	e119                	bnez	a0,42011030 <weather_task+0x1e8>
4201102c:	10800413          	li	s0,264
42011030:	4532                	lw	a0,12(sp)
42011032:	fe376097          	auipc	ra,0xfe376
42011036:	190080e7          	jalr	400(ra) # 403871c2 <cfree>
4201103a:	ec2d                	bnez	s0,420110b4 <weather_task+0x26c>
4201103c:	854a                	mv	a0,s2
4201103e:	c52fb0ef          	jal	4200c490 <settings_snapshot>
42011042:	43a10593          	addi	a1,sp,1082
42011046:	5a610513          	addi	a0,sp,1446
4201104a:	fe376097          	auipc	ra,0xfe376
4201104e:	608080e7          	jalr	1544(ra) # 40387652 <strcmp>
42011052:	e12d                	bnez	a0,420110b4 <weather_task+0x26c>
42011054:	47b10593          	addi	a1,sp,1147
42011058:	5e710513          	addi	a0,sp,1511
4201105c:	fe376097          	auipc	ra,0xfe376
42011060:	5f6080e7          	jalr	1526(ra) # 40387652 <strcmp>
42011064:	e921                	bnez	a0,420110b4 <weather_task+0x26c>
42011066:	4d010593          	addi	a1,sp,1232
4201106a:	63c10513          	addi	a0,sp,1596
4201106e:	fe376097          	auipc	ra,0xfe376
42011072:	5e4080e7          	jalr	1508(ra) # 40387652 <strcmp>
42011076:	ed1d                	bnez	a0,420110b4 <weather_task+0x26c>
42011078:	3fcb4437          	lui	s0,0x3fcb4
4201107c:	92c42503          	lw	a0,-1748(s0) # 3fcb392c <weather_mutex>
42011080:	55fd                	li	a1,-1
42011082:	4109b0ef          	jal	420ac492 <xQueueSemaphoreTake>
42011086:	3fcb0537          	lui	a0,0x3fcb0
4201108a:	aa050513          	addi	a0,a0,-1376 # 3fcafaa0 <cached_weather>
4201108e:	0f052783          	lw	a5,240(a0)
42011092:	0f800613          	li	a2,248
42011096:	0dac                	addi	a1,sp,728
42011098:	0785                	addi	a5,a5,1
4201109a:	3cf12423          	sw	a5,968(sp)
4201109e:	fe376097          	auipc	ra,0xfe376
420110a2:	19c080e7          	jalr	412(ra) # 4038723a <memcpy>
420110a6:	92c42503          	lw	a0,-1748(s0)
420110aa:	4681                	li	a3,0
420110ac:	4601                	li	a2,0
420110ae:	4581                	li	a1,0
420110b0:	7c39a0ef          	jal	420ac072 <xQueueGenericSend>
420110b4:	4615                	li	a2,5
420110b6:	55f9                	li	a1,-2
420110b8:	8552                	mv	a0,s4
420110ba:	fe376097          	auipc	ra,0xfe376
420110be:	4a4080e7          	jalr	1188(ra) # 4038755e <__atomic_fetch_and_4>
420110c2:	b3cd                	j	42010ea4 <weather_task+0x5c>
420110c4:	547d                	li	s0,-1
420110c6:	bf89                	j	42011018 <weather_task+0x1d0>
