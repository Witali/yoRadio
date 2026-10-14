
small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42012ad8 <text_utf8_decode>:
42012ad8:	88aa                	mv	a7,a0
42012ada:	e219                	bnez	a2,42012ae0 <text_utf8_decode+0x8>
42012adc:	4501                	li	a0,0
42012ade:	8082                	ret
42012ae0:	00062023          	sw	zero,0(a2)
42012ae4:	dd65                	beqz	a0,42012adc <text_utf8_decode+0x4>
42012ae6:	d9fd                	beqz	a1,42012adc <text_utf8_decode+0x4>
42012ae8:	00054783          	lbu	a5,0(a0)
42012aec:	dbe5                	beqz	a5,42012adc <text_utf8_decode+0x4>
42012aee:	4785                	li	a5,1
42012af0:	c21c                	sw	a5,0(a2)
42012af2:	00054683          	lbu	a3,0(a0)
42012af6:	01869793          	slli	a5,a3,0x18
42012afa:	87e1                	srai	a5,a5,0x18
42012afc:	0007c463          	bltz	a5,42012b04 <text_utf8_decode+0x2c>
42012b00:	8536                	mv	a0,a3
42012b02:	8082                	ret
42012b04:	03e68793          	addi	a5,a3,62
42012b08:	0ff7f793          	zext.b	a5,a5
42012b0c:	4775                	li	a4,29
42012b0e:	04f76e63          	bltu	a4,a5,42012b6a <text_utf8_decode+0x92>
42012b12:	01f6f513          	andi	a0,a3,31
42012b16:	4709                	li	a4,2
42012b18:	08000693          	li	a3,128
42012b1c:	08e5e263          	bltu	a1,a4,42012ba0 <text_utf8_decode+0xc8>
42012b20:	4585                	li	a1,1
42012b22:	08000313          	li	t1,128
42012b26:	00b887b3          	add	a5,a7,a1
42012b2a:	0007c803          	lbu	a6,0(a5)
42012b2e:	0c087793          	andi	a5,a6,192
42012b32:	06679763          	bne	a5,t1,42012ba0 <text_utf8_decode+0xc8>
42012b36:	00651793          	slli	a5,a0,0x6
42012b3a:	03f87813          	andi	a6,a6,63
42012b3e:	0585                	addi	a1,a1,1
42012b40:	00f86533          	or	a0,a6,a5
42012b44:	feb711e3          	bne	a4,a1,42012b26 <text_utf8_decode+0x4e>
42012b48:	001107b7          	lui	a5,0x110
42012b4c:	17fd                	addi	a5,a5,-1 # 10ffff <CSR_UINTSTATUS+0x10f34e>
42012b4e:	04a7e963          	bltu	a5,a0,42012ba0 <text_utf8_decode+0xc8>
42012b52:	04d56763          	bltu	a0,a3,42012ba0 <text_utf8_decode+0xc8>
42012b56:	77cd                	lui	a5,0xffff3
42012b58:	80078793          	addi	a5,a5,-2048 # ffff2800 <SYSTEM+0x9ff32800>
42012b5c:	97aa                	add	a5,a5,a0
42012b5e:	7ff00693          	li	a3,2047
42012b62:	02f6ff63          	bgeu	a3,a5,42012ba0 <text_utf8_decode+0xc8>
42012b66:	c218                	sw	a4,0(a2)
42012b68:	8082                	ret
42012b6a:	02068793          	addi	a5,a3,32
42012b6e:	0ff7f793          	zext.b	a5,a5
42012b72:	473d                	li	a4,15
42012b74:	00f76963          	bltu	a4,a5,42012b86 <text_utf8_decode+0xae>
42012b78:	00e6f533          	and	a0,a3,a4
42012b7c:	6685                	lui	a3,0x1
42012b7e:	80068693          	addi	a3,a3,-2048 # 800 <ALIGN_VECTOR_TABLE+0x700>
42012b82:	470d                	li	a4,3
42012b84:	bf61                	j	42012b1c <text_utf8_decode+0x44>
42012b86:	01068813          	addi	a6,a3,16
42012b8a:	6541                	lui	a0,0x10
42012b8c:	0ff87813          	zext.b	a6,a6
42012b90:	4711                	li	a4,4
42012b92:	1575                	addi	a0,a0,-3 # fffd <CSR_UINTSTATUS+0xf34c>
42012b94:	01076863          	bltu	a4,a6,42012ba4 <text_utf8_decode+0xcc>
42012b98:	0076f513          	andi	a0,a3,7
42012b9c:	66c1                	lui	a3,0x10
42012b9e:	bfbd                	j	42012b1c <text_utf8_decode+0x44>
42012ba0:	6541                	lui	a0,0x10
42012ba2:	1575                	addi	a0,a0,-3 # fffd <CSR_UINTSTATUS+0xf34c>
42012ba4:	8082                	ret


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42012ba6 <text_utf8_copy>:
42012ba6:	715d                	addi	sp,sp,-80
42012ba8:	c686                	sw	ra,76(sp)
42012baa:	c4a2                	sw	s0,72(sp)
42012bac:	c2a6                	sw	s1,68(sp)
42012bae:	c0ca                	sw	s2,64(sp)
42012bb0:	de4e                	sw	s3,60(sp)
42012bb2:	dc52                	sw	s4,56(sp)
42012bb4:	da56                	sw	s5,52(sp)
42012bb6:	d85a                	sw	s6,48(sp)
42012bb8:	d65e                	sw	s7,44(sp)
42012bba:	d462                	sw	s8,40(sp)
42012bbc:	d266                	sw	s9,36(sp)
42012bbe:	c509                	beqz	a0,42012bc8 <text_utf8_copy+0x22>
42012bc0:	c581                	beqz	a1,42012bc8 <text_utf8_copy+0x22>
42012bc2:	e215                	bnez	a2,42012be6 <text_utf8_copy+0x40>
42012bc4:	00050023          	sb	zero,0(a0)
42012bc8:	4401                	li	s0,0
42012bca:	40b6                	lw	ra,76(sp)
42012bcc:	8522                	mv	a0,s0
42012bce:	4426                	lw	s0,72(sp)
42012bd0:	4496                	lw	s1,68(sp)
42012bd2:	4906                	lw	s2,64(sp)
42012bd4:	59f2                	lw	s3,60(sp)
42012bd6:	5a62                	lw	s4,56(sp)
42012bd8:	5ad2                	lw	s5,52(sp)
42012bda:	5b42                	lw	s6,48(sp)
42012bdc:	5bb2                	lw	s7,44(sp)
42012bde:	5c22                	lw	s8,40(sp)
42012be0:	5c92                	lw	s9,36(sp)
42012be2:	6161                	addi	sp,sp,80
42012be4:	8082                	ret
42012be6:	84aa                	mv	s1,a0
42012be8:	8532                	mv	a0,a2
42012bea:	89b6                	mv	s3,a3
42012bec:	8932                	mv	s2,a2
42012bee:	8a2e                	mv	s4,a1
42012bf0:	7b41                	lui	s6,0xffff0
42012bf2:	fdfee097          	auipc	ra,0xfdfee
42012bf6:	8b6080e7          	jalr	-1866(ra) # 400004a8 <strlen>
42012bfa:	8baa                	mv	s7,a0
42012bfc:	4401                	li	s0,0
42012bfe:	0b0d                	addi	s6,s6,3 # ffff0003 <SYSTEM+0x9ff30003>
42012c00:	03f00c13          	li	s8,63
42012c04:	00848ab3          	add	s5,s1,s0
42012c08:	87de                	mv	a5,s7
42012c0a:	0179f363          	bgeu	s3,s7,42012c10 <text_utf8_copy+0x6a>
42012c0e:	87ce                	mv	a5,s3
42012c10:	00f46563          	bltu	s0,a5,42012c1a <text_utf8_copy+0x74>
42012c14:	000a8023          	sb	zero,0(s5)
42012c18:	bf4d                	j	42012bca <text_utf8_copy+0x24>
42012c1a:	00890cb3          	add	s9,s2,s0
42012c1e:	0870                	addi	a2,sp,28
42012c20:	408b85b3          	sub	a1,s7,s0
42012c24:	8566                	mv	a0,s9
42012c26:	eb3ff0ef          	jal	42012ad8 <text_utf8_decode>
42012c2a:	4672                	lw	a2,28(sp)
42012c2c:	d665                	beqz	a2,42012c14 <text_utf8_copy+0x6e>
42012c2e:	408987b3          	sub	a5,s3,s0
42012c32:	fec7e1e3          	bltu	a5,a2,42012c14 <text_utf8_copy+0x6e>
42012c36:	408a07b3          	sub	a5,s4,s0
42012c3a:	fcf67de3          	bgeu	a2,a5,42012c14 <text_utf8_copy+0x6e>
42012c3e:	fff60793          	addi	a5,a2,-1
42012c42:	e799                	bnez	a5,42012c50 <text_utf8_copy+0xaa>
42012c44:	955a                	add	a0,a0,s6
42012c46:	e509                	bnez	a0,42012c50 <text_utf8_copy+0xaa>
42012c48:	018a8023          	sb	s8,0(s5)
42012c4c:	9432                	add	s0,s0,a2
42012c4e:	bf5d                	j	42012c04 <text_utf8_copy+0x5e>
42012c50:	85e6                	mv	a1,s9
42012c52:	8556                	mv	a0,s5
42012c54:	c632                	sw	a2,12(sp)
42012c56:	fe374097          	auipc	ra,0xfe374
42012c5a:	6b8080e7          	jalr	1720(ra) # 4038730e <memmove>
42012c5e:	4632                	lw	a2,12(sp)
42012c60:	b7f5                	j	42012c4c <text_utf8_copy+0xa6>


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200d670 <text_token>:
4200d670:	4785                	li	a5,1
4200d672:	04f58663          	beq	a1,a5,4200d6be <text_token+0x4e>
4200d676:	00054783          	lbu	a5,0(a0)
4200d67a:	0a100713          	li	a4,161
4200d67e:	02e79763          	bne	a5,a4,4200d6ac <text_token+0x3c>
4200d682:	00154703          	lbu	a4,1(a0)
4200d686:	0e600793          	li	a5,230
4200d68a:	02f71a63          	bne	a4,a5,4200d6be <text_token+0x4e>
4200d68e:	4789                	li	a5,2
4200d690:	c21c                	sw	a5,0(a2)
4200d692:	00054703          	lbu	a4,0(a0)
4200d696:	0a100793          	li	a5,161
4200d69a:	6509                	lui	a0,0x2
4200d69c:	10950513          	addi	a0,a0,265 # 2109 <CSR_UINTSTATUS+0x1458>
4200d6a0:	06f71863          	bne	a4,a5,4200d710 <text_token+0xa0>
4200d6a4:	6509                	lui	a0,0x2
4200d6a6:	10350513          	addi	a0,a0,259 # 2103 <CSR_UINTSTATUS+0x1452>
4200d6aa:	8082                	ret
4200d6ac:	0a800713          	li	a4,168
4200d6b0:	00e79763          	bne	a5,a4,4200d6be <text_token+0x4e>
4200d6b4:	00154703          	lbu	a4,1(a0)
4200d6b8:	04800793          	li	a5,72
4200d6bc:	b7f9                	j	4200d68a <text_token+0x1a>
4200d6be:	1101                	addi	sp,sp,-32
4200d6c0:	cc22                	sw	s0,24(sp)
4200d6c2:	c632                	sw	a2,12(sp)
4200d6c4:	c42e                	sw	a1,8(sp)
4200d6c6:	ce06                	sw	ra,28(sp)
4200d6c8:	842a                	mv	s0,a0
4200d6ca:	40e050ef          	jal	42012ad8 <text_utf8_decode>
4200d6ce:	0b000793          	li	a5,176
4200d6d2:	45a2                	lw	a1,8(sp)
4200d6d4:	4632                	lw	a2,12(sp)
4200d6d6:	02f51563          	bne	a0,a5,4200d700 <text_token+0x90>
4200d6da:	421c                	lw	a5,0(a2)
4200d6dc:	02b7f263          	bgeu	a5,a1,4200d700 <text_token+0x90>
4200d6e0:	943e                	add	s0,s0,a5
4200d6e2:	00044703          	lbu	a4,0(s0)
4200d6e6:	04300693          	li	a3,67
4200d6ea:	00d70f63          	beq	a4,a3,4200d708 <text_token+0x98>
4200d6ee:	04600693          	li	a3,70
4200d6f2:	00d71763          	bne	a4,a3,4200d700 <text_token+0x90>
4200d6f6:	6509                	lui	a0,0x2
4200d6f8:	10950513          	addi	a0,a0,265 # 2109 <CSR_UINTSTATUS+0x1458>
4200d6fc:	0785                	addi	a5,a5,1
4200d6fe:	c21c                	sw	a5,0(a2)
4200d700:	40f2                	lw	ra,28(sp)
4200d702:	4462                	lw	s0,24(sp)
4200d704:	6105                	addi	sp,sp,32
4200d706:	8082                	ret
4200d708:	6509                	lui	a0,0x2
4200d70a:	10350513          	addi	a0,a0,259 # 2103 <CSR_UINTSTATUS+0x1452>
4200d70e:	b7fd                	j	4200d6fc <text_token+0x8c>
4200d710:	8082                	ret


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200d844 <draw_text>:
4200d844:	7175                	addi	sp,sp,-144
4200d846:	dece                	sw	s3,124(sp)
4200d848:	89be                	mv	s3,a5
4200d84a:	09015783          	lhu	a5,144(sp)
4200d84e:	d4e2                	sw	s8,104(sp)
4200d850:	c706                	sw	ra,140(sp)
4200d852:	c522                	sw	s0,136(sp)
4200d854:	c326                	sw	s1,132(sp)
4200d856:	c14a                	sw	s2,128(sp)
4200d858:	dcd2                	sw	s4,120(sp)
4200d85a:	dad6                	sw	s5,116(sp)
4200d85c:	d8da                	sw	s6,112(sp)
4200d85e:	d6de                	sw	s7,108(sp)
4200d860:	d2e6                	sw	s9,100(sp)
4200d862:	d0ea                	sw	s10,96(sp)
4200d864:	ceee                	sw	s11,92(sp)
4200d866:	ce3e                	sw	a5,28(sp)
4200d868:	09414c03          	lbu	s8,148(sp)
4200d86c:	04098563          	beqz	s3,4200d8b6 <draw_text+0x72>
4200d870:	842a                	mv	s0,a0
4200d872:	854e                	mv	a0,s3
4200d874:	84c2                	mv	s1,a6
4200d876:	8cba                	mv	s9,a4
4200d878:	d046                	sw	a7,32(sp)
4200d87a:	8b36                	mv	s6,a3
4200d87c:	8ab2                	mv	s5,a2
4200d87e:	cc2e                	sw	a1,24(sp)
4200d880:	fdff3097          	auipc	ra,0xfdff3
4200d884:	c28080e7          	jalr	-984(ra) # 400004a8 <strlen>
4200d888:	ff048793          	addi	a5,s1,-16
4200d88c:	00f037b3          	snez	a5,a5
4200d890:	001c4713          	xori	a4,s8,1
4200d894:	8fd9                	or	a5,a5,a4
4200d896:	d23e                	sw	a5,36(sp)
4200d898:	77f9                	lui	a5,0xffffe
4200d89a:	ef778793          	addi	a5,a5,-265 # ffffdef7 <SYSTEM+0x9ff3def7>
4200d89e:	d43e                	sw	a5,40(sp)
4200d8a0:	77f9                	lui	a5,0xffffe
4200d8a2:	efd78793          	addi	a5,a5,-259 # ffffdefd <SYSTEM+0x9ff3defd>
4200d8a6:	8baa                	mv	s7,a0
4200d8a8:	d63e                	sw	a5,44(sp)
4200d8aa:	07f00d93          	li	s11,127
4200d8ae:	01645463          	bge	s0,s6,4200d8b6 <draw_text+0x72>
4200d8b2:	020b9163          	bnez	s7,4200d8d4 <draw_text+0x90>
4200d8b6:	40ba                	lw	ra,140(sp)
4200d8b8:	442a                	lw	s0,136(sp)
4200d8ba:	449a                	lw	s1,132(sp)
4200d8bc:	490a                	lw	s2,128(sp)
4200d8be:	59f6                	lw	s3,124(sp)
4200d8c0:	5a66                	lw	s4,120(sp)
4200d8c2:	5ad6                	lw	s5,116(sp)
4200d8c4:	5b46                	lw	s6,112(sp)
4200d8c6:	5bb6                	lw	s7,108(sp)
4200d8c8:	5c26                	lw	s8,104(sp)
4200d8ca:	5c96                	lw	s9,100(sp)
4200d8cc:	5d06                	lw	s10,96(sp)
4200d8ce:	4df6                	lw	s11,92(sp)
4200d8d0:	6149                	addi	sp,sp,144
4200d8d2:	8082                	ret
4200d8d4:	1870                	addi	a2,sp,60
4200d8d6:	85de                	mv	a1,s7
4200d8d8:	854e                	mv	a0,s3
4200d8da:	d97ff0ef          	jal	4200d670 <text_token>
4200d8de:	57a2                	lw	a5,40(sp)
4200d8e0:	5732                	lw	a4,44(sp)
4200d8e2:	0014d913          	srli	s2,s1,0x1
4200d8e6:	97aa                	add	a5,a5,a0
4200d8e8:	972a                	add	a4,a4,a0
4200d8ea:	8d2a                	mv	s10,a0
4200d8ec:	0017b793          	seqz	a5,a5
4200d8f0:	c311                	beqz	a4,4200d8f4 <draw_text+0xb0>
4200d8f2:	c3a5                	beqz	a5,4200d952 <draw_text+0x10e>
4200d8f4:	008c                	addi	a1,sp,64
4200d8f6:	853e                	mv	a0,a5
4200d8f8:	f23ff0ef          	jal	4200d81a <factory_symbol>
4200d8fc:	8926                	mv	s2,s1
4200d8fe:	ff890793          	addi	a5,s2,-8
4200d902:	5d72                	lw	s10,60(sp)
4200d904:	e781                	bnez	a5,4200d90c <draw_text+0xc8>
4200d906:	5792                	lw	a5,36(sp)
4200d908:	4a15                	li	s4,5
4200d90a:	c391                	beqz	a5,4200d90e <draw_text+0xca>
4200d90c:	8a4a                	mv	s4,s2
4200d90e:	c92d                	beqz	a0,4200d980 <draw_text+0x13c>
4200d910:	000c8b63          	beqz	s9,4200d926 <draw_text+0xe2>
4200d914:	4796                	lw	a5,68(sp)
4200d916:	0147f363          	bgeu	a5,s4,4200d91c <draw_text+0xd8>
4200d91a:	87d2                	mv	a5,s4
4200d91c:	408b0733          	sub	a4,s6,s0
4200d920:	f8f76be3          	bltu	a4,a5,4200d8b6 <draw_text+0x72>
4200d924:	c125                	beqz	a0,4200d984 <draw_text+0x140>
4200d926:	040ac463          	bltz	s5,4200d96e <draw_text+0x12a>
4200d92a:	47f2                	lw	a5,28(sp)
4200d92c:	4762                	lw	a4,24(sp)
4200d92e:	5882                	lw	a7,32(sp)
4200d930:	c03e                	sw	a5,0(sp)
4200d932:	47e2                	lw	a5,24(sp)
4200d934:	c262                	sw	s8,4(sp)
4200d936:	86d6                	mv	a3,s5
4200d938:	00978833          	add	a6,a5,s1
4200d93c:	0090                	addi	a2,sp,64
4200d93e:	87da                	mv	a5,s6
4200d940:	85ba                	mv	a1,a4
4200d942:	8522                	mv	a0,s0
4200d944:	bdcff0ef          	jal	4200cd20 <display_bitmap_region>
4200d948:	99ea                	add	s3,s3,s10
4200d94a:	41ab8bb3          	sub	s7,s7,s10
4200d94e:	9452                	add	s0,s0,s4
4200d950:	bfb9                	j	4200d8ae <draw_text+0x6a>
4200d952:	0090                	addi	a2,sp,64
4200d954:	85a6                	mv	a1,s1
4200d956:	dbdff0ef          	jal	4200d712 <factory_glyph>
4200d95a:	f155                	bnez	a0,4200d8fe <draw_text+0xba>
4200d95c:	fbadf1e3          	bgeu	s11,s10,4200d8fe <draw_text+0xba>
4200d960:	0090                	addi	a2,sp,64
4200d962:	85a6                	mv	a1,s1
4200d964:	03f00513          	li	a0,63
4200d968:	dabff0ef          	jal	4200d712 <factory_glyph>
4200d96c:	bf49                	j	4200d8fe <draw_text+0xba>
4200d96e:	4772                	lw	a4,28(sp)
4200d970:	5682                	lw	a3,32(sp)
4200d972:	45e2                	lw	a1,24(sp)
4200d974:	87e2                	mv	a5,s8
4200d976:	0090                	addi	a2,sp,64
4200d978:	8522                	mv	a0,s0
4200d97a:	d50ff0ef          	jal	4200ceca <display_bitmap>
4200d97e:	b7e9                	j	4200d948 <draw_text+0x104>
4200d980:	f80c9de3          	bnez	s9,4200d91a <draw_text+0xd6>
4200d984:	fc0c12e3          	bnez	s8,4200d948 <draw_text+0x104>
4200d988:	8522                	mv	a0,s0
4200d98a:	000ac563          	bltz	s5,4200d994 <draw_text+0x150>
4200d98e:	01545363          	bge	s0,s5,4200d994 <draw_text+0x150>
4200d992:	8556                	mv	a0,s5
4200d994:	00890633          	add	a2,s2,s0
4200d998:	00cb5363          	bge	s6,a2,4200d99e <draw_text+0x15a>
4200d99c:	865a                	mv	a2,s6
4200d99e:	4772                	lw	a4,28(sp)
4200d9a0:	45e2                	lw	a1,24(sp)
4200d9a2:	86a6                	mv	a3,s1
4200d9a4:	8e09                	sub	a2,a2,a0
4200d9a6:	832ff0ef          	jal	4200c9d8 <display_fill>
4200d9aa:	bf79                	j	4200d948 <draw_text+0x104>


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200d712 <factory_glyph>:
4200d712:	3c1006b7          	lui	a3,0x3c100
4200d716:	56868693          	addi	a3,a3,1384 # 3c100568 <factory_fonts>
4200d71a:	4701                	li	a4,0
4200d71c:	87b6                	mv	a5,a3
4200d71e:	4819                	li	a6,6
4200d720:	0086a883          	lw	a7,8(a3)
4200d724:	02b89663          	bne	a7,a1,4200d750 <factory_glyph+0x3e>
4200d728:	46e1                	li	a3,24
4200d72a:	02d70733          	mul	a4,a4,a3
4200d72e:	97ba                	add	a5,a5,a4
4200d730:	4b98                	lw	a4,16(a5)
4200d732:	02e57463          	bgeu	a0,a4,4200d75a <factory_glyph+0x48>
4200d736:	07f00793          	li	a5,127
4200d73a:	4701                	li	a4,0
4200d73c:	0aa7f563          	bgeu	a5,a0,4200d7e6 <factory_glyph+0xd4>
4200d740:	3c0d3837          	lui	a6,0x3c0d3
4200d744:	1c400693          	li	a3,452
4200d748:	4781                	li	a5,0
4200d74a:	35080813          	addi	a6,a6,848 # 3c0d3350 <unicode_codepoints>
4200d74e:	a881                	j	4200d79e <factory_glyph+0x8c>
4200d750:	0705                	addi	a4,a4,1
4200d752:	06e1                	addi	a3,a3,24
4200d754:	fd0716e3          	bne	a4,a6,4200d720 <factory_glyph+0xe>
4200d758:	bff9                	j	4200d736 <factory_glyph+0x24>
4200d75a:	4bd4                	lw	a3,20(a5)
4200d75c:	96ba                	add	a3,a3,a4
4200d75e:	fcd57ce3          	bgeu	a0,a3,4200d736 <factory_glyph+0x24>
4200d762:	47d4                	lw	a3,12(a5)
4200d764:	8d19                	sub	a0,a0,a4
4200d766:	0047a803          	lw	a6,4(a5)
4200d76a:	02b68733          	mul	a4,a3,a1
4200d76e:	439c                	lw	a5,0(a5)
4200d770:	01062223          	sw	a6,4(a2)
4200d774:	c60c                	sw	a1,8(a2)
4200d776:	c654                	sw	a3,12(a2)
4200d778:	02e50533          	mul	a0,a0,a4
4200d77c:	97aa                	add	a5,a5,a0
4200d77e:	c21c                	sw	a5,0(a2)
4200d780:	4505                	li	a0,1
4200d782:	8082                	ret
4200d784:	40f68733          	sub	a4,a3,a5
4200d788:	8305                	srli	a4,a4,0x1
4200d78a:	973e                	add	a4,a4,a5
4200d78c:	00271893          	slli	a7,a4,0x2
4200d790:	98c2                	add	a7,a7,a6
4200d792:	0008a883          	lw	a7,0(a7)
4200d796:	04a8fa63          	bgeu	a7,a0,4200d7ea <factory_glyph+0xd8>
4200d79a:	00170793          	addi	a5,a4,1
4200d79e:	fed7e3e3          	bltu	a5,a3,4200d784 <factory_glyph+0x72>
4200d7a2:	1c400693          	li	a3,452
4200d7a6:	4701                	li	a4,0
4200d7a8:	02d78f63          	beq	a5,a3,4200d7e6 <factory_glyph+0xd4>
4200d7ac:	3c0d3737          	lui	a4,0x3c0d3
4200d7b0:	00279693          	slli	a3,a5,0x2
4200d7b4:	35070713          	addi	a4,a4,848 # 3c0d3350 <unicode_codepoints>
4200d7b8:	9736                	add	a4,a4,a3
4200d7ba:	4314                	lw	a3,0(a4)
4200d7bc:	4701                	li	a4,0
4200d7be:	02d51463          	bne	a0,a3,4200d7e6 <factory_glyph+0xd4>
4200d7c2:	46c1                	li	a3,16
4200d7c4:	02d59563          	bne	a1,a3,4200d7ee <factory_glyph+0xdc>
4200d7c8:	3c0d1737          	lui	a4,0x3c0d1
4200d7cc:	0792                	slli	a5,a5,0x4
4200d7ce:	71070713          	addi	a4,a4,1808 # 3c0d1710 <unicode_font16>
4200d7d2:	97ba                	add	a5,a5,a4
4200d7d4:	0015d713          	srli	a4,a1,0x1
4200d7d8:	c258                	sw	a4,4(a2)
4200d7da:	071d                	addi	a4,a4,7
4200d7dc:	830d                	srli	a4,a4,0x3
4200d7de:	c658                	sw	a4,12(a2)
4200d7e0:	c21c                	sw	a5,0(a2)
4200d7e2:	c60c                	sw	a1,8(a2)
4200d7e4:	4705                	li	a4,1
4200d7e6:	853a                	mv	a0,a4
4200d7e8:	8082                	ret
4200d7ea:	86ba                	mv	a3,a4
4200d7ec:	bf4d                	j	4200d79e <factory_glyph+0x8c>
4200d7ee:	46e1                	li	a3,24
4200d7f0:	00d59b63          	bne	a1,a3,4200d806 <factory_glyph+0xf4>
4200d7f4:	03000713          	li	a4,48
4200d7f8:	02e787b3          	mul	a5,a5,a4
4200d7fc:	3c0cc737          	lui	a4,0x3c0cc
4200d800:	25070713          	addi	a4,a4,592 # 3c0cc250 <unicode_font24>
4200d804:	b7f9                	j	4200d7d2 <factory_glyph+0xc0>
4200d806:	02000693          	li	a3,32
4200d80a:	fcd59ee3          	bne	a1,a3,4200d7e6 <factory_glyph+0xd4>
4200d80e:	3c0c5737          	lui	a4,0x3c0c5
4200d812:	079a                	slli	a5,a5,0x6
4200d814:	15070713          	addi	a4,a4,336 # 3c0c5150 <unicode_font32>
4200d818:	bf6d                	j	4200d7d2 <factory_glyph+0xc0>


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200da0a <display_factory_text_width>:
4200da0a:	7139                	addi	sp,sp,-64
4200da0c:	da26                	sw	s1,52(sp)
4200da0e:	de06                	sw	ra,60(sp)
4200da10:	dc22                	sw	s0,56(sp)
4200da12:	d84a                	sw	s2,48(sp)
4200da14:	d64e                	sw	s3,44(sp)
4200da16:	d452                	sw	s4,40(sp)
4200da18:	4481                	li	s1,0
4200da1a:	c105                	beqz	a0,4200da3a <display_factory_text_width+0x30>
4200da1c:	892e                	mv	s2,a1
4200da1e:	842a                	mv	s0,a0
4200da20:	79f9                	lui	s3,0xffffe
4200da22:	fdff3097          	auipc	ra,0xfdff3
4200da26:	a86080e7          	jalr	-1402(ra) # 400004a8 <strlen>
4200da2a:	7a79                	lui	s4,0xffffe
4200da2c:	85aa                	mv	a1,a0
4200da2e:	4481                	li	s1,0
4200da30:	ef798993          	addi	s3,s3,-265 # ffffdef7 <SYSTEM+0x9ff3def7>
4200da34:	efda0a13          	addi	s4,s4,-259 # ffffdefd <SYSTEM+0x9ff3defd>
4200da38:	e991                	bnez	a1,4200da4c <display_factory_text_width+0x42>
4200da3a:	50f2                	lw	ra,60(sp)
4200da3c:	5462                	lw	s0,56(sp)
4200da3e:	5942                	lw	s2,48(sp)
4200da40:	59b2                	lw	s3,44(sp)
4200da42:	5a22                	lw	s4,40(sp)
4200da44:	8526                	mv	a0,s1
4200da46:	54d2                	lw	s1,52(sp)
4200da48:	6121                	addi	sp,sp,64
4200da4a:	8082                	ret
4200da4c:	0870                	addi	a2,sp,28
4200da4e:	8522                	mv	a0,s0
4200da50:	c62e                	sw	a1,12(sp)
4200da52:	c1fff0ef          	jal	4200d670 <text_token>
4200da56:	013507b3          	add	a5,a0,s3
4200da5a:	45b2                	lw	a1,12(sp)
4200da5c:	c789                	beqz	a5,4200da66 <display_factory_text_width+0x5c>
4200da5e:	9552                	add	a0,a0,s4
4200da60:	00195793          	srli	a5,s2,0x1
4200da64:	e111                	bnez	a0,4200da68 <display_factory_text_width+0x5e>
4200da66:	87ca                	mv	a5,s2
4200da68:	94be                	add	s1,s1,a5
4200da6a:	47f2                	lw	a5,28(sp)
4200da6c:	943e                	add	s0,s0,a5
4200da6e:	8d9d                	sub	a1,a1,a5
4200da70:	b7e1                	j	4200da38 <display_factory_text_width+0x2e>


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42010b90 <url_escape>:
42010b90:	4665                	li	a2,25
42010b92:	00054783          	lbu	a5,0(a0)
42010b96:	e781                	bnez	a5,42010b9e <url_escape+0xe>
42010b98:	00058023          	sb	zero,0(a1)
42010b9c:	8082                	ret
42010b9e:	fdf7f713          	andi	a4,a5,-33
42010ba2:	fbf70713          	addi	a4,a4,-65
42010ba6:	0ff77713          	zext.b	a4,a4
42010baa:	02e67463          	bgeu	a2,a4,42010bd2 <url_escape+0x42>
42010bae:	fd078693          	addi	a3,a5,-48
42010bb2:	fd378713          	addi	a4,a5,-45
42010bb6:	00273713          	sltiu	a4,a4,2
42010bba:	00a6b693          	sltiu	a3,a3,10
42010bbe:	8ed9                	or	a3,a3,a4
42010bc0:	fa178713          	addi	a4,a5,-95
42010bc4:	00173713          	seqz	a4,a4
42010bc8:	8f55                	or	a4,a4,a3
42010bca:	e701                	bnez	a4,42010bd2 <url_escape+0x42>
42010bcc:	f8278713          	addi	a4,a5,-126
42010bd0:	e711                	bnez	a4,42010bdc <url_escape+0x4c>
42010bd2:	00f58023          	sb	a5,0(a1)
42010bd6:	0585                	addi	a1,a1,1
42010bd8:	0505                	addi	a0,a0,1
42010bda:	bf65                	j	42010b92 <url_escape+0x2>
42010bdc:	02500713          	li	a4,37
42010be0:	00e58023          	sb	a4,0(a1)
42010be4:	3c0eb737          	lui	a4,0x3c0eb
42010be8:	99870713          	addi	a4,a4,-1640 # 3c0ea998 <hex.0>
42010bec:	0047d693          	srli	a3,a5,0x4
42010bf0:	8bbd                	andi	a5,a5,15
42010bf2:	96ba                	add	a3,a3,a4
42010bf4:	973e                	add	a4,a4,a5
42010bf6:	0006c683          	lbu	a3,0(a3)
42010bfa:	00074783          	lbu	a5,0(a4)
42010bfe:	058d                	addi	a1,a1,3
42010c00:	fed58f23          	sb	a3,-2(a1)
42010c04:	fef58fa3          	sb	a5,-1(a1)
42010c08:	bfc1                	j	42010bd8 <url_escape+0x48>


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42010c0a <weather_task>:
42010c0a:	8e010113          	addi	sp,sp,-1824
42010c0e:	04100613          	li	a2,65
42010c12:	4581                	li	a1,0
42010c14:	0848                	addi	a0,sp,20
42010c16:	70112e23          	sw	ra,1820(sp)
42010c1a:	70912a23          	sw	s1,1812(sp)
42010c1e:	71312623          	sw	s3,1804(sp)
42010c22:	71412423          	sw	s4,1800(sp)
42010c26:	70812c23          	sw	s0,1816(sp)
42010c2a:	71212823          	sw	s2,1808(sp)
42010c2e:	71512223          	sw	s5,1796(sp)
42010c32:	fdff0097          	auipc	ra,0xfdff0
42010c36:	856080e7          	jalr	-1962(ra) # 40000488 <memset>
42010c3a:	04100613          	li	a2,65
42010c3e:	4581                	li	a1,0
42010c40:	08a8                	addi	a0,sp,88
42010c42:	00011223          	sh	zero,4(sp)
42010c46:	00010323          	sb	zero,6(sp)
42010c4a:	fdff0097          	auipc	ra,0xfdff0
42010c4e:	83e080e7          	jalr	-1986(ra) # 40000488 <memset>
42010c52:	3fcb47b7          	lui	a5,0x3fcb4
42010c56:	3fcb04b7          	lui	s1,0x3fcb0
42010c5a:	4985                	li	s3,1
42010c5c:	8ec78a13          	addi	s4,a5,-1812 # 3fcb38ec <request_state>
42010c60:	a7848493          	addi	s1,s1,-1416 # 3fcafa78 <cached_weather>
42010c64:	567d                	li	a2,-1
42010c66:	4585                	li	a1,1
42010c68:	4501                	li	a0,0
42010c6a:	76c9c0ef          	jal	420ad3d6 <ulTaskGenericNotifyTake>
42010c6e:	4615                	li	a2,5
42010c70:	4585                	li	a1,1
42010c72:	8552                	mv	a0,s4
42010c74:	fe377097          	auipc	ra,0xfe377
42010c78:	912080e7          	jalr	-1774(ra) # 40387586 <__atomic_fetch_or_4>
42010c7c:	55f5                	li	a1,-3
42010c7e:	4615                	li	a2,5
42010c80:	8552                	mv	a0,s4
42010c82:	fe377097          	auipc	ra,0xfe377
42010c86:	8dc080e7          	jalr	-1828(ra) # 4038755e <__atomic_fetch_and_4>
42010c8a:	1728                	addi	a0,sp,936
42010c8c:	e46fb0ef          	jal	4200c2d2 <settings_snapshot>
42010c90:	40e10593          	addi	a1,sp,1038
42010c94:	0848                	addi	a0,sp,20
42010c96:	fe377097          	auipc	ra,0xfe377
42010c9a:	9bc080e7          	jalr	-1604(ra) # 40387652 <strcmp>
42010c9e:	e10d                	bnez	a0,42010cc0 <weather_task+0xb6>
42010ca0:	44f10593          	addi	a1,sp,1103
42010ca4:	0048                	addi	a0,sp,4
42010ca6:	fe377097          	auipc	ra,0xfe377
42010caa:	9ac080e7          	jalr	-1620(ra) # 40387652 <strcmp>
42010cae:	e909                	bnez	a0,42010cc0 <weather_task+0xb6>
42010cb0:	49310593          	addi	a1,sp,1171
42010cb4:	08a8                	addi	a0,sp,88
42010cb6:	fe377097          	auipc	ra,0xfe377
42010cba:	99c080e7          	jalr	-1636(ra) # 40387652 <strcmp>
42010cbe:	c939                	beqz	a0,42010d14 <weather_task+0x10a>
42010cc0:	40e10593          	addi	a1,sp,1038
42010cc4:	0848                	addi	a0,sp,20
42010cc6:	fe377097          	auipc	ra,0xfe377
42010cca:	aa2080e7          	jalr	-1374(ra) # 40387768 <strcpy>
42010cce:	44f10593          	addi	a1,sp,1103
42010cd2:	0048                	addi	a0,sp,4
42010cd4:	fe377097          	auipc	ra,0xfe377
42010cd8:	a94080e7          	jalr	-1388(ra) # 40387768 <strcpy>
42010cdc:	49310593          	addi	a1,sp,1171
42010ce0:	08a8                	addi	a0,sp,88
42010ce2:	fe377097          	auipc	ra,0xfe377
42010ce6:	a86080e7          	jalr	-1402(ra) # 40387768 <strcpy>
42010cea:	3fcb4437          	lui	s0,0x3fcb4
42010cee:	8f442503          	lw	a0,-1804(s0) # 3fcb38f4 <weather_mutex>
42010cf2:	55fd                	li	a1,-1
42010cf4:	5829b0ef          	jal	420ac276 <xQueueSemaphoreTake>
42010cf8:	0e04a783          	lw	a5,224(s1)
42010cfc:	8f442503          	lw	a0,-1804(s0)
42010d00:	4681                	li	a3,0
42010d02:	0785                	addi	a5,a5,1
42010d04:	4601                	li	a2,0
42010d06:	4581                	li	a1,0
42010d08:	00048023          	sb	zero,0(s1)
42010d0c:	0ef4a023          	sw	a5,224(s1)
42010d10:	1469b0ef          	jal	420abe56 <xQueueGenericSend>
42010d14:	a9aff0ef          	jal	4200ffae <network_connected>
42010d18:	14050c63          	beqz	a0,42010e70 <weather_task+0x266>
42010d1c:	49314783          	lbu	a5,1171(sp)
42010d20:	14078863          	beqz	a5,42010e70 <weather_task+0x266>
42010d24:	1a2c                	addi	a1,sp,312
42010d26:	40e10513          	addi	a0,sp,1038
42010d2a:	e67ff0ef          	jal	42010b90 <url_escape>
42010d2e:	1bec                	addi	a1,sp,508
42010d30:	49310513          	addi	a0,sp,1171
42010d34:	e5dff0ef          	jal	42010b90 <url_escape>
42010d38:	50010913          	addi	s2,sp,1280
42010d3c:	3c0b4637          	lui	a2,0x3c0b4
42010d40:	1bfc                	addi	a5,sp,508
42010d42:	44f10713          	addi	a4,sp,1103
42010d46:	1a34                	addi	a3,sp,312
42010d48:	2bc60613          	addi	a2,a2,700 # 3c0b42bc <_esp_libc_clock_array_end+0x416c>
42010d4c:	20000593          	li	a1,512
42010d50:	854a                	mv	a0,s2
42010d52:	6bd8c0ef          	jal	4209dc0e <snprintf>
42010d56:	6589                	lui	a1,0x2
42010d58:	4781                	li	a5,0
42010d5a:	4801                	li	a6,0
42010d5c:	0585                	addi	a1,a1,1 # 2001 <CSR_UINTSTATUS+0x1350>
42010d5e:	4505                	li	a0,1
42010d60:	c63e                	sw	a5,12(sp)
42010d62:	c842                	sw	a6,16(sp)
42010d64:	fe376097          	auipc	ra,0xfe376
42010d68:	462080e7          	jalr	1122(ra) # 403871c6 <calloc>
42010d6c:	c42a                	sw	a0,8(sp)
42010d6e:	10050163          	beqz	a0,42010e70 <weather_task+0x266>
42010d72:	09800613          	li	a2,152
42010d76:	4581                	li	a1,0
42010d78:	1108                	addi	a0,sp,160
42010d7a:	fdfef097          	auipc	ra,0xfdfef
42010d7e:	70e080e7          	jalr	1806(ra) # 40000488 <memset>
42010d82:	6789                	lui	a5,0x2
42010d84:	71078793          	addi	a5,a5,1808 # 2710 <CSR_UINTSTATUS+0x1a5f>
42010d88:	d7be                	sw	a5,236(sp)
42010d8a:	420117b7          	lui	a5,0x42011
42010d8e:	e8478793          	addi	a5,a5,-380 # 42010e84 <weather_http_event>
42010d92:	dfbe                	sw	a5,252(sp)
42010d94:	40000793          	li	a5,1024
42010d98:	10f12223          	sw	a5,260(sp)
42010d9c:	10f12423          	sw	a5,264(sp)
42010da0:	0968                	addi	a0,sp,156
42010da2:	003c                	addi	a5,sp,8
42010da4:	cf4a                	sw	s2,156(sp)
42010da6:	0f310823          	sb	s3,240(sp)
42010daa:	10f12623          	sw	a5,268(sp)
42010dae:	6dc240ef          	jal	4203548a <esp_http_client_init>
42010db2:	8aaa                	mv	s5,a0
42010db4:	10100413          	li	s0,257
42010db8:	c915                	beqz	a0,42010dec <weather_task+0x1e2>
42010dba:	1bc250ef          	jal	42035f76 <esp_http_client_perform>
42010dbe:	842a                	mv	s0,a0
42010dc0:	8556                	mv	a0,s5
42010dc2:	0ec250ef          	jal	42035eae <esp_http_client_get_status_code>
42010dc6:	0c800793          	li	a5,200
42010dca:	0af51b63          	bne	a0,a5,42010e80 <weather_task+0x276>
42010dce:	01014783          	lbu	a5,16(sp)
42010dd2:	e7dd                	bnez	a5,42010e80 <weather_task+0x276>
42010dd4:	8556                	mv	a0,s5
42010dd6:	33c240ef          	jal	42035112 <esp_http_client_cleanup>
42010dda:	e809                	bnez	s0,42010dec <weather_task+0x1e2>
42010ddc:	45b2                	lw	a1,12(sp)
42010dde:	4522                	lw	a0,8(sp)
42010de0:	0594                	addi	a3,sp,704
42010de2:	1730                	addi	a2,sp,936
42010de4:	24dd                	jal	420110ca <weather_parse_response>
42010de6:	e119                	bnez	a0,42010dec <weather_task+0x1e2>
42010de8:	10800413          	li	s0,264
42010dec:	4522                	lw	a0,8(sp)
42010dee:	fe376097          	auipc	ra,0xfe376
42010df2:	3d4080e7          	jalr	980(ra) # 403871c2 <cfree>
42010df6:	ec2d                	bnez	s0,42010e70 <weather_task+0x266>
42010df8:	854a                	mv	a0,s2
42010dfa:	cd8fb0ef          	jal	4200c2d2 <settings_snapshot>
42010dfe:	40e10593          	addi	a1,sp,1038
42010e02:	56610513          	addi	a0,sp,1382
42010e06:	fe377097          	auipc	ra,0xfe377
42010e0a:	84c080e7          	jalr	-1972(ra) # 40387652 <strcmp>
42010e0e:	e12d                	bnez	a0,42010e70 <weather_task+0x266>
42010e10:	44f10593          	addi	a1,sp,1103
42010e14:	5a710513          	addi	a0,sp,1447
42010e18:	fe377097          	auipc	ra,0xfe377
42010e1c:	83a080e7          	jalr	-1990(ra) # 40387652 <strcmp>
42010e20:	e921                	bnez	a0,42010e70 <weather_task+0x266>
42010e22:	49310593          	addi	a1,sp,1171
42010e26:	5eb10513          	addi	a0,sp,1515
42010e2a:	fe377097          	auipc	ra,0xfe377
42010e2e:	828080e7          	jalr	-2008(ra) # 40387652 <strcmp>
42010e32:	ed1d                	bnez	a0,42010e70 <weather_task+0x266>
42010e34:	3fcb4437          	lui	s0,0x3fcb4
42010e38:	8f442503          	lw	a0,-1804(s0) # 3fcb38f4 <weather_mutex>
42010e3c:	55fd                	li	a1,-1
42010e3e:	4389b0ef          	jal	420ac276 <xQueueSemaphoreTake>
42010e42:	3fcb0537          	lui	a0,0x3fcb0
42010e46:	a7850513          	addi	a0,a0,-1416 # 3fcafa78 <cached_weather>
42010e4a:	0e052783          	lw	a5,224(a0)
42010e4e:	0e800613          	li	a2,232
42010e52:	058c                	addi	a1,sp,704
42010e54:	0785                	addi	a5,a5,1
42010e56:	3af12023          	sw	a5,928(sp)
42010e5a:	fe376097          	auipc	ra,0xfe376
42010e5e:	3e0080e7          	jalr	992(ra) # 4038723a <memcpy>
42010e62:	8f442503          	lw	a0,-1804(s0)
42010e66:	4681                	li	a3,0
42010e68:	4601                	li	a2,0
42010e6a:	4581                	li	a1,0
42010e6c:	7eb9a0ef          	jal	420abe56 <xQueueGenericSend>
42010e70:	4615                	li	a2,5
42010e72:	55f9                	li	a1,-2
42010e74:	8552                	mv	a0,s4
42010e76:	fe376097          	auipc	ra,0xfe376
42010e7a:	6e8080e7          	jalr	1768(ra) # 4038755e <__atomic_fetch_and_4>
42010e7e:	b3dd                	j	42010c64 <weather_task+0x5a>
42010e80:	547d                	li	s0,-1
42010e82:	bf89                	j	42010dd4 <weather_task+0x1ca>
