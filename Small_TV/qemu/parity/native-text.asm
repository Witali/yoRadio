
small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42012cd6 <text_utf8_decode>:
42012cd6:	88aa                	mv	a7,a0
42012cd8:	e219                	bnez	a2,42012cde <text_utf8_decode+0x8>
42012cda:	4501                	li	a0,0
42012cdc:	8082                	ret
42012cde:	00062023          	sw	zero,0(a2)
42012ce2:	dd65                	beqz	a0,42012cda <text_utf8_decode+0x4>
42012ce4:	d9fd                	beqz	a1,42012cda <text_utf8_decode+0x4>
42012ce6:	00054783          	lbu	a5,0(a0)
42012cea:	dbe5                	beqz	a5,42012cda <text_utf8_decode+0x4>
42012cec:	4785                	li	a5,1
42012cee:	c21c                	sw	a5,0(a2)
42012cf0:	00054683          	lbu	a3,0(a0)
42012cf4:	01869793          	slli	a5,a3,0x18
42012cf8:	87e1                	srai	a5,a5,0x18
42012cfa:	0007c463          	bltz	a5,42012d02 <text_utf8_decode+0x2c>
42012cfe:	8536                	mv	a0,a3
42012d00:	8082                	ret
42012d02:	03e68793          	addi	a5,a3,62
42012d06:	0ff7f793          	zext.b	a5,a5
42012d0a:	4775                	li	a4,29
42012d0c:	04f76e63          	bltu	a4,a5,42012d68 <text_utf8_decode+0x92>
42012d10:	01f6f513          	andi	a0,a3,31
42012d14:	4709                	li	a4,2
42012d16:	08000693          	li	a3,128
42012d1a:	08e5e263          	bltu	a1,a4,42012d9e <text_utf8_decode+0xc8>
42012d1e:	4585                	li	a1,1
42012d20:	08000313          	li	t1,128
42012d24:	00b887b3          	add	a5,a7,a1
42012d28:	0007c803          	lbu	a6,0(a5)
42012d2c:	0c087793          	andi	a5,a6,192
42012d30:	06679763          	bne	a5,t1,42012d9e <text_utf8_decode+0xc8>
42012d34:	00651793          	slli	a5,a0,0x6
42012d38:	03f87813          	andi	a6,a6,63
42012d3c:	0585                	addi	a1,a1,1
42012d3e:	00f86533          	or	a0,a6,a5
42012d42:	feb711e3          	bne	a4,a1,42012d24 <text_utf8_decode+0x4e>
42012d46:	001107b7          	lui	a5,0x110
42012d4a:	17fd                	addi	a5,a5,-1 # 10ffff <CSR_UINTSTATUS+0x10f34e>
42012d4c:	04a7e963          	bltu	a5,a0,42012d9e <text_utf8_decode+0xc8>
42012d50:	04d56763          	bltu	a0,a3,42012d9e <text_utf8_decode+0xc8>
42012d54:	77cd                	lui	a5,0xffff3
42012d56:	80078793          	addi	a5,a5,-2048 # ffff2800 <SYSTEM+0x9ff32800>
42012d5a:	97aa                	add	a5,a5,a0
42012d5c:	7ff00693          	li	a3,2047
42012d60:	02f6ff63          	bgeu	a3,a5,42012d9e <text_utf8_decode+0xc8>
42012d64:	c218                	sw	a4,0(a2)
42012d66:	8082                	ret
42012d68:	02068793          	addi	a5,a3,32
42012d6c:	0ff7f793          	zext.b	a5,a5
42012d70:	473d                	li	a4,15
42012d72:	00f76963          	bltu	a4,a5,42012d84 <text_utf8_decode+0xae>
42012d76:	00e6f533          	and	a0,a3,a4
42012d7a:	6685                	lui	a3,0x1
42012d7c:	80068693          	addi	a3,a3,-2048 # 800 <ALIGN_VECTOR_TABLE+0x700>
42012d80:	470d                	li	a4,3
42012d82:	bf61                	j	42012d1a <text_utf8_decode+0x44>
42012d84:	01068813          	addi	a6,a3,16
42012d88:	6541                	lui	a0,0x10
42012d8a:	0ff87813          	zext.b	a6,a6
42012d8e:	4711                	li	a4,4
42012d90:	1575                	addi	a0,a0,-3 # fffd <CSR_UINTSTATUS+0xf34c>
42012d92:	01076863          	bltu	a4,a6,42012da2 <text_utf8_decode+0xcc>
42012d96:	0076f513          	andi	a0,a3,7
42012d9a:	66c1                	lui	a3,0x10
42012d9c:	bfbd                	j	42012d1a <text_utf8_decode+0x44>
42012d9e:	6541                	lui	a0,0x10
42012da0:	1575                	addi	a0,a0,-3 # fffd <CSR_UINTSTATUS+0xf34c>
42012da2:	8082                	ret


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42012da4 <text_utf8_copy>:
42012da4:	715d                	addi	sp,sp,-80
42012da6:	c686                	sw	ra,76(sp)
42012da8:	c4a2                	sw	s0,72(sp)
42012daa:	c2a6                	sw	s1,68(sp)
42012dac:	c0ca                	sw	s2,64(sp)
42012dae:	de4e                	sw	s3,60(sp)
42012db0:	dc52                	sw	s4,56(sp)
42012db2:	da56                	sw	s5,52(sp)
42012db4:	d85a                	sw	s6,48(sp)
42012db6:	d65e                	sw	s7,44(sp)
42012db8:	d462                	sw	s8,40(sp)
42012dba:	d266                	sw	s9,36(sp)
42012dbc:	c509                	beqz	a0,42012dc6 <text_utf8_copy+0x22>
42012dbe:	c581                	beqz	a1,42012dc6 <text_utf8_copy+0x22>
42012dc0:	e215                	bnez	a2,42012de4 <text_utf8_copy+0x40>
42012dc2:	00050023          	sb	zero,0(a0)
42012dc6:	4401                	li	s0,0
42012dc8:	40b6                	lw	ra,76(sp)
42012dca:	8522                	mv	a0,s0
42012dcc:	4426                	lw	s0,72(sp)
42012dce:	4496                	lw	s1,68(sp)
42012dd0:	4906                	lw	s2,64(sp)
42012dd2:	59f2                	lw	s3,60(sp)
42012dd4:	5a62                	lw	s4,56(sp)
42012dd6:	5ad2                	lw	s5,52(sp)
42012dd8:	5b42                	lw	s6,48(sp)
42012dda:	5bb2                	lw	s7,44(sp)
42012ddc:	5c22                	lw	s8,40(sp)
42012dde:	5c92                	lw	s9,36(sp)
42012de0:	6161                	addi	sp,sp,80
42012de2:	8082                	ret
42012de4:	84aa                	mv	s1,a0
42012de6:	8532                	mv	a0,a2
42012de8:	89b6                	mv	s3,a3
42012dea:	8932                	mv	s2,a2
42012dec:	8a2e                	mv	s4,a1
42012dee:	7b41                	lui	s6,0xffff0
42012df0:	fdfed097          	auipc	ra,0xfdfed
42012df4:	6b8080e7          	jalr	1720(ra) # 400004a8 <strlen>
42012df8:	8baa                	mv	s7,a0
42012dfa:	4401                	li	s0,0
42012dfc:	0b0d                	addi	s6,s6,3 # ffff0003 <SYSTEM+0x9ff30003>
42012dfe:	03f00c13          	li	s8,63
42012e02:	00848ab3          	add	s5,s1,s0
42012e06:	87de                	mv	a5,s7
42012e08:	0179f363          	bgeu	s3,s7,42012e0e <text_utf8_copy+0x6a>
42012e0c:	87ce                	mv	a5,s3
42012e0e:	00f46563          	bltu	s0,a5,42012e18 <text_utf8_copy+0x74>
42012e12:	000a8023          	sb	zero,0(s5)
42012e16:	bf4d                	j	42012dc8 <text_utf8_copy+0x24>
42012e18:	00890cb3          	add	s9,s2,s0
42012e1c:	0870                	addi	a2,sp,28
42012e1e:	408b85b3          	sub	a1,s7,s0
42012e22:	8566                	mv	a0,s9
42012e24:	eb3ff0ef          	jal	42012cd6 <text_utf8_decode>
42012e28:	4672                	lw	a2,28(sp)
42012e2a:	d665                	beqz	a2,42012e12 <text_utf8_copy+0x6e>
42012e2c:	408987b3          	sub	a5,s3,s0
42012e30:	fec7e1e3          	bltu	a5,a2,42012e12 <text_utf8_copy+0x6e>
42012e34:	408a07b3          	sub	a5,s4,s0
42012e38:	fcf67de3          	bgeu	a2,a5,42012e12 <text_utf8_copy+0x6e>
42012e3c:	fff60793          	addi	a5,a2,-1
42012e40:	e799                	bnez	a5,42012e4e <text_utf8_copy+0xaa>
42012e42:	955a                	add	a0,a0,s6
42012e44:	e509                	bnez	a0,42012e4e <text_utf8_copy+0xaa>
42012e46:	018a8023          	sb	s8,0(s5)
42012e4a:	9432                	add	s0,s0,a2
42012e4c:	bf5d                	j	42012e02 <text_utf8_copy+0x5e>
42012e4e:	85e6                	mv	a1,s9
42012e50:	8556                	mv	a0,s5
42012e52:	c632                	sw	a2,12(sp)
42012e54:	fe374097          	auipc	ra,0xfe374
42012e58:	4ba080e7          	jalr	1210(ra) # 4038730e <memmove>
42012e5c:	4632                	lw	a2,12(sp)
42012e5e:	b7f5                	j	42012e4a <text_utf8_copy+0xa6>


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200d88c <text_token>:
4200d88c:	4785                	li	a5,1
4200d88e:	04f58663          	beq	a1,a5,4200d8da <text_token+0x4e>
4200d892:	00054783          	lbu	a5,0(a0)
4200d896:	0a100713          	li	a4,161
4200d89a:	02e79763          	bne	a5,a4,4200d8c8 <text_token+0x3c>
4200d89e:	00154703          	lbu	a4,1(a0)
4200d8a2:	0e600793          	li	a5,230
4200d8a6:	02f71a63          	bne	a4,a5,4200d8da <text_token+0x4e>
4200d8aa:	4789                	li	a5,2
4200d8ac:	c21c                	sw	a5,0(a2)
4200d8ae:	00054703          	lbu	a4,0(a0)
4200d8b2:	0a100793          	li	a5,161
4200d8b6:	6509                	lui	a0,0x2
4200d8b8:	10950513          	addi	a0,a0,265 # 2109 <CSR_UINTSTATUS+0x1458>
4200d8bc:	06f71863          	bne	a4,a5,4200d92c <text_token+0xa0>
4200d8c0:	6509                	lui	a0,0x2
4200d8c2:	10350513          	addi	a0,a0,259 # 2103 <CSR_UINTSTATUS+0x1452>
4200d8c6:	8082                	ret
4200d8c8:	0a800713          	li	a4,168
4200d8cc:	00e79763          	bne	a5,a4,4200d8da <text_token+0x4e>
4200d8d0:	00154703          	lbu	a4,1(a0)
4200d8d4:	04800793          	li	a5,72
4200d8d8:	b7f9                	j	4200d8a6 <text_token+0x1a>
4200d8da:	1101                	addi	sp,sp,-32
4200d8dc:	cc22                	sw	s0,24(sp)
4200d8de:	c632                	sw	a2,12(sp)
4200d8e0:	c42e                	sw	a1,8(sp)
4200d8e2:	ce06                	sw	ra,28(sp)
4200d8e4:	842a                	mv	s0,a0
4200d8e6:	3f0050ef          	jal	42012cd6 <text_utf8_decode>
4200d8ea:	0b000793          	li	a5,176
4200d8ee:	45a2                	lw	a1,8(sp)
4200d8f0:	4632                	lw	a2,12(sp)
4200d8f2:	02f51563          	bne	a0,a5,4200d91c <text_token+0x90>
4200d8f6:	421c                	lw	a5,0(a2)
4200d8f8:	02b7f263          	bgeu	a5,a1,4200d91c <text_token+0x90>
4200d8fc:	943e                	add	s0,s0,a5
4200d8fe:	00044703          	lbu	a4,0(s0)
4200d902:	04300693          	li	a3,67
4200d906:	00d70f63          	beq	a4,a3,4200d924 <text_token+0x98>
4200d90a:	04600693          	li	a3,70
4200d90e:	00d71763          	bne	a4,a3,4200d91c <text_token+0x90>
4200d912:	6509                	lui	a0,0x2
4200d914:	10950513          	addi	a0,a0,265 # 2109 <CSR_UINTSTATUS+0x1458>
4200d918:	0785                	addi	a5,a5,1
4200d91a:	c21c                	sw	a5,0(a2)
4200d91c:	40f2                	lw	ra,28(sp)
4200d91e:	4462                	lw	s0,24(sp)
4200d920:	6105                	addi	sp,sp,32
4200d922:	8082                	ret
4200d924:	6509                	lui	a0,0x2
4200d926:	10350513          	addi	a0,a0,259 # 2103 <CSR_UINTSTATUS+0x1452>
4200d92a:	b7fd                	j	4200d918 <text_token+0x8c>
4200d92c:	8082                	ret


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200da60 <draw_text>:
4200da60:	7175                	addi	sp,sp,-144
4200da62:	dece                	sw	s3,124(sp)
4200da64:	89be                	mv	s3,a5
4200da66:	09015783          	lhu	a5,144(sp)
4200da6a:	d4e2                	sw	s8,104(sp)
4200da6c:	c706                	sw	ra,140(sp)
4200da6e:	c522                	sw	s0,136(sp)
4200da70:	c326                	sw	s1,132(sp)
4200da72:	c14a                	sw	s2,128(sp)
4200da74:	dcd2                	sw	s4,120(sp)
4200da76:	dad6                	sw	s5,116(sp)
4200da78:	d8da                	sw	s6,112(sp)
4200da7a:	d6de                	sw	s7,108(sp)
4200da7c:	d2e6                	sw	s9,100(sp)
4200da7e:	d0ea                	sw	s10,96(sp)
4200da80:	ceee                	sw	s11,92(sp)
4200da82:	ce3e                	sw	a5,28(sp)
4200da84:	09414c03          	lbu	s8,148(sp)
4200da88:	04098563          	beqz	s3,4200dad2 <draw_text+0x72>
4200da8c:	842a                	mv	s0,a0
4200da8e:	854e                	mv	a0,s3
4200da90:	84c2                	mv	s1,a6
4200da92:	8cba                	mv	s9,a4
4200da94:	d046                	sw	a7,32(sp)
4200da96:	8b36                	mv	s6,a3
4200da98:	8ab2                	mv	s5,a2
4200da9a:	cc2e                	sw	a1,24(sp)
4200da9c:	fdff3097          	auipc	ra,0xfdff3
4200daa0:	a0c080e7          	jalr	-1524(ra) # 400004a8 <strlen>
4200daa4:	ff048793          	addi	a5,s1,-16
4200daa8:	00f037b3          	snez	a5,a5
4200daac:	001c4713          	xori	a4,s8,1
4200dab0:	8fd9                	or	a5,a5,a4
4200dab2:	d23e                	sw	a5,36(sp)
4200dab4:	77f9                	lui	a5,0xffffe
4200dab6:	ef778793          	addi	a5,a5,-265 # ffffdef7 <SYSTEM+0x9ff3def7>
4200daba:	d43e                	sw	a5,40(sp)
4200dabc:	77f9                	lui	a5,0xffffe
4200dabe:	efd78793          	addi	a5,a5,-259 # ffffdefd <SYSTEM+0x9ff3defd>
4200dac2:	8baa                	mv	s7,a0
4200dac4:	d63e                	sw	a5,44(sp)
4200dac6:	07f00d93          	li	s11,127
4200daca:	01645463          	bge	s0,s6,4200dad2 <draw_text+0x72>
4200dace:	020b9163          	bnez	s7,4200daf0 <draw_text+0x90>
4200dad2:	40ba                	lw	ra,140(sp)
4200dad4:	442a                	lw	s0,136(sp)
4200dad6:	449a                	lw	s1,132(sp)
4200dad8:	490a                	lw	s2,128(sp)
4200dada:	59f6                	lw	s3,124(sp)
4200dadc:	5a66                	lw	s4,120(sp)
4200dade:	5ad6                	lw	s5,116(sp)
4200dae0:	5b46                	lw	s6,112(sp)
4200dae2:	5bb6                	lw	s7,108(sp)
4200dae4:	5c26                	lw	s8,104(sp)
4200dae6:	5c96                	lw	s9,100(sp)
4200dae8:	5d06                	lw	s10,96(sp)
4200daea:	4df6                	lw	s11,92(sp)
4200daec:	6149                	addi	sp,sp,144
4200daee:	8082                	ret
4200daf0:	1870                	addi	a2,sp,60
4200daf2:	85de                	mv	a1,s7
4200daf4:	854e                	mv	a0,s3
4200daf6:	d97ff0ef          	jal	4200d88c <text_token>
4200dafa:	57a2                	lw	a5,40(sp)
4200dafc:	5732                	lw	a4,44(sp)
4200dafe:	0014d913          	srli	s2,s1,0x1
4200db02:	97aa                	add	a5,a5,a0
4200db04:	972a                	add	a4,a4,a0
4200db06:	8d2a                	mv	s10,a0
4200db08:	0017b793          	seqz	a5,a5
4200db0c:	c311                	beqz	a4,4200db10 <draw_text+0xb0>
4200db0e:	c3a5                	beqz	a5,4200db6e <draw_text+0x10e>
4200db10:	008c                	addi	a1,sp,64
4200db12:	853e                	mv	a0,a5
4200db14:	f23ff0ef          	jal	4200da36 <factory_symbol>
4200db18:	8926                	mv	s2,s1
4200db1a:	ff890793          	addi	a5,s2,-8
4200db1e:	5d72                	lw	s10,60(sp)
4200db20:	e781                	bnez	a5,4200db28 <draw_text+0xc8>
4200db22:	5792                	lw	a5,36(sp)
4200db24:	4a15                	li	s4,5
4200db26:	c391                	beqz	a5,4200db2a <draw_text+0xca>
4200db28:	8a4a                	mv	s4,s2
4200db2a:	c92d                	beqz	a0,4200db9c <draw_text+0x13c>
4200db2c:	000c8b63          	beqz	s9,4200db42 <draw_text+0xe2>
4200db30:	4796                	lw	a5,68(sp)
4200db32:	0147f363          	bgeu	a5,s4,4200db38 <draw_text+0xd8>
4200db36:	87d2                	mv	a5,s4
4200db38:	408b0733          	sub	a4,s6,s0
4200db3c:	f8f76be3          	bltu	a4,a5,4200dad2 <draw_text+0x72>
4200db40:	c125                	beqz	a0,4200dba0 <draw_text+0x140>
4200db42:	040ac463          	bltz	s5,4200db8a <draw_text+0x12a>
4200db46:	47f2                	lw	a5,28(sp)
4200db48:	4762                	lw	a4,24(sp)
4200db4a:	5882                	lw	a7,32(sp)
4200db4c:	c03e                	sw	a5,0(sp)
4200db4e:	47e2                	lw	a5,24(sp)
4200db50:	c262                	sw	s8,4(sp)
4200db52:	86d6                	mv	a3,s5
4200db54:	00978833          	add	a6,a5,s1
4200db58:	0090                	addi	a2,sp,64
4200db5a:	87da                	mv	a5,s6
4200db5c:	85ba                	mv	a1,a4
4200db5e:	8522                	mv	a0,s0
4200db60:	bdcff0ef          	jal	4200cf3c <display_bitmap_region>
4200db64:	99ea                	add	s3,s3,s10
4200db66:	41ab8bb3          	sub	s7,s7,s10
4200db6a:	9452                	add	s0,s0,s4
4200db6c:	bfb9                	j	4200daca <draw_text+0x6a>
4200db6e:	0090                	addi	a2,sp,64
4200db70:	85a6                	mv	a1,s1
4200db72:	dbdff0ef          	jal	4200d92e <factory_glyph>
4200db76:	f155                	bnez	a0,4200db1a <draw_text+0xba>
4200db78:	fbadf1e3          	bgeu	s11,s10,4200db1a <draw_text+0xba>
4200db7c:	0090                	addi	a2,sp,64
4200db7e:	85a6                	mv	a1,s1
4200db80:	03f00513          	li	a0,63
4200db84:	dabff0ef          	jal	4200d92e <factory_glyph>
4200db88:	bf49                	j	4200db1a <draw_text+0xba>
4200db8a:	4772                	lw	a4,28(sp)
4200db8c:	5682                	lw	a3,32(sp)
4200db8e:	45e2                	lw	a1,24(sp)
4200db90:	87e2                	mv	a5,s8
4200db92:	0090                	addi	a2,sp,64
4200db94:	8522                	mv	a0,s0
4200db96:	d50ff0ef          	jal	4200d0e6 <display_bitmap>
4200db9a:	b7e9                	j	4200db64 <draw_text+0x104>
4200db9c:	f80c9de3          	bnez	s9,4200db36 <draw_text+0xd6>
4200dba0:	fc0c12e3          	bnez	s8,4200db64 <draw_text+0x104>
4200dba4:	8522                	mv	a0,s0
4200dba6:	000ac563          	bltz	s5,4200dbb0 <draw_text+0x150>
4200dbaa:	01545363          	bge	s0,s5,4200dbb0 <draw_text+0x150>
4200dbae:	8556                	mv	a0,s5
4200dbb0:	00890633          	add	a2,s2,s0
4200dbb4:	00cb5363          	bge	s6,a2,4200dbba <draw_text+0x15a>
4200dbb8:	865a                	mv	a2,s6
4200dbba:	4772                	lw	a4,28(sp)
4200dbbc:	45e2                	lw	a1,24(sp)
4200dbbe:	86a6                	mv	a3,s1
4200dbc0:	8e09                	sub	a2,a2,a0
4200dbc2:	832ff0ef          	jal	4200cbf4 <display_fill>
4200dbc6:	bf79                	j	4200db64 <draw_text+0x104>


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200d92e <factory_glyph>:
4200d92e:	3c1006b7          	lui	a3,0x3c100
4200d932:	56868693          	addi	a3,a3,1384 # 3c100568 <factory_fonts>
4200d936:	4701                	li	a4,0
4200d938:	87b6                	mv	a5,a3
4200d93a:	4819                	li	a6,6
4200d93c:	0086a883          	lw	a7,8(a3)
4200d940:	02b89663          	bne	a7,a1,4200d96c <factory_glyph+0x3e>
4200d944:	46e1                	li	a3,24
4200d946:	02d70733          	mul	a4,a4,a3
4200d94a:	97ba                	add	a5,a5,a4
4200d94c:	4b98                	lw	a4,16(a5)
4200d94e:	02e57463          	bgeu	a0,a4,4200d976 <factory_glyph+0x48>
4200d952:	07f00793          	li	a5,127
4200d956:	4701                	li	a4,0
4200d958:	0aa7f563          	bgeu	a5,a0,4200da02 <factory_glyph+0xd4>
4200d95c:	3c0d3837          	lui	a6,0x3c0d3
4200d960:	1c400693          	li	a3,452
4200d964:	4781                	li	a5,0
4200d966:	35080813          	addi	a6,a6,848 # 3c0d3350 <unicode_codepoints>
4200d96a:	a881                	j	4200d9ba <factory_glyph+0x8c>
4200d96c:	0705                	addi	a4,a4,1
4200d96e:	06e1                	addi	a3,a3,24
4200d970:	fd0716e3          	bne	a4,a6,4200d93c <factory_glyph+0xe>
4200d974:	bff9                	j	4200d952 <factory_glyph+0x24>
4200d976:	4bd4                	lw	a3,20(a5)
4200d978:	96ba                	add	a3,a3,a4
4200d97a:	fcd57ce3          	bgeu	a0,a3,4200d952 <factory_glyph+0x24>
4200d97e:	47d4                	lw	a3,12(a5)
4200d980:	8d19                	sub	a0,a0,a4
4200d982:	0047a803          	lw	a6,4(a5)
4200d986:	02b68733          	mul	a4,a3,a1
4200d98a:	439c                	lw	a5,0(a5)
4200d98c:	01062223          	sw	a6,4(a2)
4200d990:	c60c                	sw	a1,8(a2)
4200d992:	c654                	sw	a3,12(a2)
4200d994:	02e50533          	mul	a0,a0,a4
4200d998:	97aa                	add	a5,a5,a0
4200d99a:	c21c                	sw	a5,0(a2)
4200d99c:	4505                	li	a0,1
4200d99e:	8082                	ret
4200d9a0:	40f68733          	sub	a4,a3,a5
4200d9a4:	8305                	srli	a4,a4,0x1
4200d9a6:	973e                	add	a4,a4,a5
4200d9a8:	00271893          	slli	a7,a4,0x2
4200d9ac:	98c2                	add	a7,a7,a6
4200d9ae:	0008a883          	lw	a7,0(a7)
4200d9b2:	04a8fa63          	bgeu	a7,a0,4200da06 <factory_glyph+0xd8>
4200d9b6:	00170793          	addi	a5,a4,1
4200d9ba:	fed7e3e3          	bltu	a5,a3,4200d9a0 <factory_glyph+0x72>
4200d9be:	1c400693          	li	a3,452
4200d9c2:	4701                	li	a4,0
4200d9c4:	02d78f63          	beq	a5,a3,4200da02 <factory_glyph+0xd4>
4200d9c8:	3c0d3737          	lui	a4,0x3c0d3
4200d9cc:	00279693          	slli	a3,a5,0x2
4200d9d0:	35070713          	addi	a4,a4,848 # 3c0d3350 <unicode_codepoints>
4200d9d4:	9736                	add	a4,a4,a3
4200d9d6:	4314                	lw	a3,0(a4)
4200d9d8:	4701                	li	a4,0
4200d9da:	02d51463          	bne	a0,a3,4200da02 <factory_glyph+0xd4>
4200d9de:	46c1                	li	a3,16
4200d9e0:	02d59563          	bne	a1,a3,4200da0a <factory_glyph+0xdc>
4200d9e4:	3c0d1737          	lui	a4,0x3c0d1
4200d9e8:	0792                	slli	a5,a5,0x4
4200d9ea:	71070713          	addi	a4,a4,1808 # 3c0d1710 <unicode_font16>
4200d9ee:	97ba                	add	a5,a5,a4
4200d9f0:	0015d713          	srli	a4,a1,0x1
4200d9f4:	c258                	sw	a4,4(a2)
4200d9f6:	071d                	addi	a4,a4,7
4200d9f8:	830d                	srli	a4,a4,0x3
4200d9fa:	c658                	sw	a4,12(a2)
4200d9fc:	c21c                	sw	a5,0(a2)
4200d9fe:	c60c                	sw	a1,8(a2)
4200da00:	4705                	li	a4,1
4200da02:	853a                	mv	a0,a4
4200da04:	8082                	ret
4200da06:	86ba                	mv	a3,a4
4200da08:	bf4d                	j	4200d9ba <factory_glyph+0x8c>
4200da0a:	46e1                	li	a3,24
4200da0c:	00d59b63          	bne	a1,a3,4200da22 <factory_glyph+0xf4>
4200da10:	03000713          	li	a4,48
4200da14:	02e787b3          	mul	a5,a5,a4
4200da18:	3c0cc737          	lui	a4,0x3c0cc
4200da1c:	25070713          	addi	a4,a4,592 # 3c0cc250 <unicode_font24>
4200da20:	b7f9                	j	4200d9ee <factory_glyph+0xc0>
4200da22:	02000693          	li	a3,32
4200da26:	fcd59ee3          	bne	a1,a3,4200da02 <factory_glyph+0xd4>
4200da2a:	3c0c5737          	lui	a4,0x3c0c5
4200da2e:	079a                	slli	a5,a5,0x6
4200da30:	15070713          	addi	a4,a4,336 # 3c0c5150 <unicode_font32>
4200da34:	bf6d                	j	4200d9ee <factory_glyph+0xc0>


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200dc26 <display_factory_text_width>:
4200dc26:	7139                	addi	sp,sp,-64
4200dc28:	da26                	sw	s1,52(sp)
4200dc2a:	de06                	sw	ra,60(sp)
4200dc2c:	dc22                	sw	s0,56(sp)
4200dc2e:	d84a                	sw	s2,48(sp)
4200dc30:	d64e                	sw	s3,44(sp)
4200dc32:	d452                	sw	s4,40(sp)
4200dc34:	4481                	li	s1,0
4200dc36:	c105                	beqz	a0,4200dc56 <display_factory_text_width+0x30>
4200dc38:	892e                	mv	s2,a1
4200dc3a:	842a                	mv	s0,a0
4200dc3c:	79f9                	lui	s3,0xffffe
4200dc3e:	fdff3097          	auipc	ra,0xfdff3
4200dc42:	86a080e7          	jalr	-1942(ra) # 400004a8 <strlen>
4200dc46:	7a79                	lui	s4,0xffffe
4200dc48:	85aa                	mv	a1,a0
4200dc4a:	4481                	li	s1,0
4200dc4c:	ef798993          	addi	s3,s3,-265 # ffffdef7 <SYSTEM+0x9ff3def7>
4200dc50:	efda0a13          	addi	s4,s4,-259 # ffffdefd <SYSTEM+0x9ff3defd>
4200dc54:	e991                	bnez	a1,4200dc68 <display_factory_text_width+0x42>
4200dc56:	50f2                	lw	ra,60(sp)
4200dc58:	5462                	lw	s0,56(sp)
4200dc5a:	5942                	lw	s2,48(sp)
4200dc5c:	59b2                	lw	s3,44(sp)
4200dc5e:	5a22                	lw	s4,40(sp)
4200dc60:	8526                	mv	a0,s1
4200dc62:	54d2                	lw	s1,52(sp)
4200dc64:	6121                	addi	sp,sp,64
4200dc66:	8082                	ret
4200dc68:	0870                	addi	a2,sp,28
4200dc6a:	8522                	mv	a0,s0
4200dc6c:	c62e                	sw	a1,12(sp)
4200dc6e:	c1fff0ef          	jal	4200d88c <text_token>
4200dc72:	013507b3          	add	a5,a0,s3
4200dc76:	45b2                	lw	a1,12(sp)
4200dc78:	c789                	beqz	a5,4200dc82 <display_factory_text_width+0x5c>
4200dc7a:	9552                	add	a0,a0,s4
4200dc7c:	00195793          	srli	a5,s2,0x1
4200dc80:	e111                	bnez	a0,4200dc84 <display_factory_text_width+0x5e>
4200dc82:	87ca                	mv	a5,s2
4200dc84:	94be                	add	s1,s1,a5
4200dc86:	47f2                	lw	a5,28(sp)
4200dc88:	943e                	add	s0,s0,a5
4200dc8a:	8d9d                	sub	a1,a1,a5
4200dc8c:	b7e1                	j	4200dc54 <display_factory_text_width+0x2e>


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42010db0 <url_escape>:
42010db0:	4665                	li	a2,25
42010db2:	00054783          	lbu	a5,0(a0)
42010db6:	e781                	bnez	a5,42010dbe <url_escape+0xe>
42010db8:	00058023          	sb	zero,0(a1)
42010dbc:	8082                	ret
42010dbe:	fdf7f713          	andi	a4,a5,-33
42010dc2:	fbf70713          	addi	a4,a4,-65
42010dc6:	0ff77713          	zext.b	a4,a4
42010dca:	02e67463          	bgeu	a2,a4,42010df2 <url_escape+0x42>
42010dce:	fd078693          	addi	a3,a5,-48
42010dd2:	fd378713          	addi	a4,a5,-45
42010dd6:	00273713          	sltiu	a4,a4,2
42010dda:	00a6b693          	sltiu	a3,a3,10
42010dde:	8ed9                	or	a3,a3,a4
42010de0:	fa178713          	addi	a4,a5,-95
42010de4:	00173713          	seqz	a4,a4
42010de8:	8f55                	or	a4,a4,a3
42010dea:	e701                	bnez	a4,42010df2 <url_escape+0x42>
42010dec:	f8278713          	addi	a4,a5,-126
42010df0:	e711                	bnez	a4,42010dfc <url_escape+0x4c>
42010df2:	00f58023          	sb	a5,0(a1)
42010df6:	0585                	addi	a1,a1,1
42010df8:	0505                	addi	a0,a0,1
42010dfa:	bf65                	j	42010db2 <url_escape+0x2>
42010dfc:	02500713          	li	a4,37
42010e00:	00e58023          	sb	a4,0(a1)
42010e04:	3c0eb737          	lui	a4,0x3c0eb
42010e08:	99870713          	addi	a4,a4,-1640 # 3c0ea998 <hex.0>
42010e0c:	0047d693          	srli	a3,a5,0x4
42010e10:	8bbd                	andi	a5,a5,15
42010e12:	96ba                	add	a3,a3,a4
42010e14:	973e                	add	a4,a4,a5
42010e16:	0006c683          	lbu	a3,0(a3)
42010e1a:	00074783          	lbu	a5,0(a4)
42010e1e:	058d                	addi	a1,a1,3
42010e20:	fed58f23          	sb	a3,-2(a1)
42010e24:	fef58fa3          	sb	a5,-1(a1)
42010e28:	bfc1                	j	42010df8 <url_escape+0x48>


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42010e2a <weather_task>:
42010e2a:	8a010113          	addi	sp,sp,-1888
42010e2e:	04100613          	li	a2,65
42010e32:	4581                	li	a1,0
42010e34:	1068                	addi	a0,sp,44
42010e36:	74112e23          	sw	ra,1884(sp)
42010e3a:	74912a23          	sw	s1,1876(sp)
42010e3e:	75312623          	sw	s3,1868(sp)
42010e42:	75412423          	sw	s4,1864(sp)
42010e46:	74812c23          	sw	s0,1880(sp)
42010e4a:	75212823          	sw	s2,1872(sp)
42010e4e:	75512223          	sw	s5,1860(sp)
42010e52:	fdfef097          	auipc	ra,0xfdfef
42010e56:	636080e7          	jalr	1590(ra) # 40000488 <memset>
42010e5a:	04100613          	li	a2,65
42010e5e:	4581                	li	a1,0
42010e60:	1888                	addi	a0,sp,112
42010e62:	cc02                	sw	zero,24(sp)
42010e64:	ce02                	sw	zero,28(sp)
42010e66:	d002                	sw	zero,32(sp)
42010e68:	d202                	sw	zero,36(sp)
42010e6a:	d402                	sw	zero,40(sp)
42010e6c:	fdfef097          	auipc	ra,0xfdfef
42010e70:	61c080e7          	jalr	1564(ra) # 40000488 <memset>
42010e74:	3fcb47b7          	lui	a5,0x3fcb4
42010e78:	3fcb04b7          	lui	s1,0x3fcb0
42010e7c:	4985                	li	s3,1
42010e7e:	92478a13          	addi	s4,a5,-1756 # 3fcb3924 <request_state>
42010e82:	aa048493          	addi	s1,s1,-1376 # 3fcafaa0 <cached_weather>
42010e86:	567d                	li	a2,-1
42010e88:	4585                	li	a1,1
42010e8a:	4501                	li	a0,0
42010e8c:	7489c0ef          	jal	420ad5d4 <ulTaskGenericNotifyTake>
42010e90:	4615                	li	a2,5
42010e92:	4585                	li	a1,1
42010e94:	8552                	mv	a0,s4
42010e96:	fe376097          	auipc	ra,0xfe376
42010e9a:	6f0080e7          	jalr	1776(ra) # 40387586 <__atomic_fetch_or_4>
42010e9e:	55f5                	li	a1,-3
42010ea0:	4615                	li	a2,5
42010ea2:	8552                	mv	a0,s4
42010ea4:	fe376097          	auipc	ra,0xfe376
42010ea8:	6ba080e7          	jalr	1722(ra) # 4038755e <__atomic_fetch_and_4>
42010eac:	0fc8                	addi	a0,sp,980
42010eae:	de2fb0ef          	jal	4200c490 <settings_snapshot>
42010eb2:	43a10593          	addi	a1,sp,1082
42010eb6:	1068                	addi	a0,sp,44
42010eb8:	fe376097          	auipc	ra,0xfe376
42010ebc:	79a080e7          	jalr	1946(ra) # 40387652 <strcmp>
42010ec0:	e10d                	bnez	a0,42010ee2 <weather_task+0xb8>
42010ec2:	47b10593          	addi	a1,sp,1147
42010ec6:	0828                	addi	a0,sp,24
42010ec8:	fe376097          	auipc	ra,0xfe376
42010ecc:	78a080e7          	jalr	1930(ra) # 40387652 <strcmp>
42010ed0:	e909                	bnez	a0,42010ee2 <weather_task+0xb8>
42010ed2:	4d010593          	addi	a1,sp,1232
42010ed6:	1888                	addi	a0,sp,112
42010ed8:	fe376097          	auipc	ra,0xfe376
42010edc:	77a080e7          	jalr	1914(ra) # 40387652 <strcmp>
42010ee0:	c939                	beqz	a0,42010f36 <weather_task+0x10c>
42010ee2:	43a10593          	addi	a1,sp,1082
42010ee6:	1068                	addi	a0,sp,44
42010ee8:	fe377097          	auipc	ra,0xfe377
42010eec:	880080e7          	jalr	-1920(ra) # 40387768 <strcpy>
42010ef0:	47b10593          	addi	a1,sp,1147
42010ef4:	0828                	addi	a0,sp,24
42010ef6:	fe377097          	auipc	ra,0xfe377
42010efa:	872080e7          	jalr	-1934(ra) # 40387768 <strcpy>
42010efe:	4d010593          	addi	a1,sp,1232
42010f02:	1888                	addi	a0,sp,112
42010f04:	fe377097          	auipc	ra,0xfe377
42010f08:	864080e7          	jalr	-1948(ra) # 40387768 <strcpy>
42010f0c:	3fcb4437          	lui	s0,0x3fcb4
42010f10:	92c42503          	lw	a0,-1748(s0) # 3fcb392c <weather_mutex>
42010f14:	55fd                	li	a1,-1
42010f16:	55e9b0ef          	jal	420ac474 <xQueueSemaphoreTake>
42010f1a:	0f04a783          	lw	a5,240(s1)
42010f1e:	92c42503          	lw	a0,-1748(s0)
42010f22:	4681                	li	a3,0
42010f24:	0785                	addi	a5,a5,1
42010f26:	4601                	li	a2,0
42010f28:	4581                	li	a1,0
42010f2a:	00048023          	sb	zero,0(s1)
42010f2e:	0ef4a823          	sw	a5,240(s1)
42010f32:	1229b0ef          	jal	420ac054 <xQueueGenericSend>
42010f36:	a96ff0ef          	jal	420101cc <network_connected>
42010f3a:	14050e63          	beqz	a0,42011096 <weather_task+0x26c>
42010f3e:	4d014783          	lbu	a5,1232(sp)
42010f42:	14078a63          	beqz	a5,42011096 <weather_task+0x26c>
42010f46:	0a8c                	addi	a1,sp,336
42010f48:	43a10513          	addi	a0,sp,1082
42010f4c:	e65ff0ef          	jal	42010db0 <url_escape>
42010f50:	0c4c                	addi	a1,sp,532
42010f52:	4d010513          	addi	a0,sp,1232
42010f56:	e5bff0ef          	jal	42010db0 <url_escape>
42010f5a:	54010913          	addi	s2,sp,1344
42010f5e:	3c0b4637          	lui	a2,0x3c0b4
42010f62:	0c5c                	addi	a5,sp,532
42010f64:	47b10713          	addi	a4,sp,1147
42010f68:	0a94                	addi	a3,sp,336
42010f6a:	2bc60613          	addi	a2,a2,700 # 3c0b42bc <_esp_libc_clock_array_end+0x416c>
42010f6e:	20000593          	li	a1,512
42010f72:	854a                	mv	a0,s2
42010f74:	6998c0ef          	jal	4209de0c <snprintf>
42010f78:	6589                	lui	a1,0x2
42010f7a:	4781                	li	a5,0
42010f7c:	4801                	li	a6,0
42010f7e:	0585                	addi	a1,a1,1 # 2001 <CSR_UINTSTATUS+0x1350>
42010f80:	4505                	li	a0,1
42010f82:	c83e                	sw	a5,16(sp)
42010f84:	ca42                	sw	a6,20(sp)
42010f86:	fe376097          	auipc	ra,0xfe376
42010f8a:	240080e7          	jalr	576(ra) # 403871c6 <calloc>
42010f8e:	c62a                	sw	a0,12(sp)
42010f90:	10050363          	beqz	a0,42011096 <weather_task+0x26c>
42010f94:	09800613          	li	a2,152
42010f98:	4581                	li	a1,0
42010f9a:	1928                	addi	a0,sp,184
42010f9c:	fdfef097          	auipc	ra,0xfdfef
42010fa0:	4ec080e7          	jalr	1260(ra) # 40000488 <memset>
42010fa4:	6789                	lui	a5,0x2
42010fa6:	71078793          	addi	a5,a5,1808 # 2710 <CSR_UINTSTATUS+0x1a5f>
42010faa:	10f12223          	sw	a5,260(sp)
42010fae:	420117b7          	lui	a5,0x42011
42010fb2:	0aa78793          	addi	a5,a5,170 # 420110aa <weather_http_event>
42010fb6:	10f12a23          	sw	a5,276(sp)
42010fba:	40000793          	li	a5,1024
42010fbe:	10f12e23          	sw	a5,284(sp)
42010fc2:	12f12023          	sw	a5,288(sp)
42010fc6:	1948                	addi	a0,sp,180
42010fc8:	007c                	addi	a5,sp,12
42010fca:	db4a                	sw	s2,180(sp)
42010fcc:	11310423          	sb	s3,264(sp)
42010fd0:	12f12223          	sw	a5,292(sp)
42010fd4:	6b4240ef          	jal	42035688 <esp_http_client_init>
42010fd8:	8aaa                	mv	s5,a0
42010fda:	10100413          	li	s0,257
42010fde:	c915                	beqz	a0,42011012 <weather_task+0x1e8>
42010fe0:	194250ef          	jal	42036174 <esp_http_client_perform>
42010fe4:	842a                	mv	s0,a0
42010fe6:	8556                	mv	a0,s5
42010fe8:	0c4250ef          	jal	420360ac <esp_http_client_get_status_code>
42010fec:	0c800793          	li	a5,200
42010ff0:	0af51b63          	bne	a0,a5,420110a6 <weather_task+0x27c>
42010ff4:	01414783          	lbu	a5,20(sp)
42010ff8:	e7dd                	bnez	a5,420110a6 <weather_task+0x27c>
42010ffa:	8556                	mv	a0,s5
42010ffc:	314240ef          	jal	42035310 <esp_http_client_cleanup>
42011000:	e809                	bnez	s0,42011012 <weather_task+0x1e8>
42011002:	45c2                	lw	a1,16(sp)
42011004:	4532                	lw	a0,12(sp)
42011006:	0db4                	addi	a3,sp,728
42011008:	0fd0                	addi	a2,sp,980
4201100a:	24dd                	jal	420112f0 <weather_parse_response>
4201100c:	e119                	bnez	a0,42011012 <weather_task+0x1e8>
4201100e:	10800413          	li	s0,264
42011012:	4532                	lw	a0,12(sp)
42011014:	fe376097          	auipc	ra,0xfe376
42011018:	1ae080e7          	jalr	430(ra) # 403871c2 <cfree>
4201101c:	ec2d                	bnez	s0,42011096 <weather_task+0x26c>
4201101e:	854a                	mv	a0,s2
42011020:	c70fb0ef          	jal	4200c490 <settings_snapshot>
42011024:	43a10593          	addi	a1,sp,1082
42011028:	5a610513          	addi	a0,sp,1446
4201102c:	fe376097          	auipc	ra,0xfe376
42011030:	626080e7          	jalr	1574(ra) # 40387652 <strcmp>
42011034:	e12d                	bnez	a0,42011096 <weather_task+0x26c>
42011036:	47b10593          	addi	a1,sp,1147
4201103a:	5e710513          	addi	a0,sp,1511
4201103e:	fe376097          	auipc	ra,0xfe376
42011042:	614080e7          	jalr	1556(ra) # 40387652 <strcmp>
42011046:	e921                	bnez	a0,42011096 <weather_task+0x26c>
42011048:	4d010593          	addi	a1,sp,1232
4201104c:	63c10513          	addi	a0,sp,1596
42011050:	fe376097          	auipc	ra,0xfe376
42011054:	602080e7          	jalr	1538(ra) # 40387652 <strcmp>
42011058:	ed1d                	bnez	a0,42011096 <weather_task+0x26c>
4201105a:	3fcb4437          	lui	s0,0x3fcb4
4201105e:	92c42503          	lw	a0,-1748(s0) # 3fcb392c <weather_mutex>
42011062:	55fd                	li	a1,-1
42011064:	4109b0ef          	jal	420ac474 <xQueueSemaphoreTake>
42011068:	3fcb0537          	lui	a0,0x3fcb0
4201106c:	aa050513          	addi	a0,a0,-1376 # 3fcafaa0 <cached_weather>
42011070:	0f052783          	lw	a5,240(a0)
42011074:	0f800613          	li	a2,248
42011078:	0dac                	addi	a1,sp,728
4201107a:	0785                	addi	a5,a5,1
4201107c:	3cf12423          	sw	a5,968(sp)
42011080:	fe376097          	auipc	ra,0xfe376
42011084:	1ba080e7          	jalr	442(ra) # 4038723a <memcpy>
42011088:	92c42503          	lw	a0,-1748(s0)
4201108c:	4681                	li	a3,0
4201108e:	4601                	li	a2,0
42011090:	4581                	li	a1,0
42011092:	7c39a0ef          	jal	420ac054 <xQueueGenericSend>
42011096:	4615                	li	a2,5
42011098:	55f9                	li	a1,-2
4201109a:	8552                	mv	a0,s4
4201109c:	fe376097          	auipc	ra,0xfe376
420110a0:	4c2080e7          	jalr	1218(ra) # 4038755e <__atomic_fetch_and_4>
420110a4:	b3cd                	j	42010e86 <weather_task+0x5c>
420110a6:	547d                	li	s0,-1
420110a8:	bf89                	j	42010ffa <weather_task+0x1d0>
