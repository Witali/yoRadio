
factory-irom.bin:     file format binary


Disassembly of section .data:

4200aae0 <.data+0xaac0>:
4200aae0:	1101                	addi	sp,sp,-32
4200aae2:	ce06                	sw	ra,28(sp)
4200aae4:	cc22                	sw	s0,24(sp)
4200aae6:	ca26                	sw	s1,20(sp)
4200aae8:	c84a                	sw	s2,16(sp)
4200aaea:	c64e                	sw	s3,12(sp)
4200aaec:	c452                	sw	s4,8(sp)
4200aaee:	c256                	sw	s5,4(sp)
4200aaf0:	89aa                	mv	s3,a0
4200aaf2:	8a2e                	mv	s4,a1
4200aaf4:	843a                	mv	s0,a4
4200aaf6:	84be                	mv	s1,a5
4200aaf8:	67a9                	lui	a5,0xa
4200aafa:	1e678793          	addi	a5,a5,486 # 0xa1e6
4200aafe:	02f60863          	beq	a2,a5,0x4200ab2e
4200ab02:	67ad                	lui	a5,0xb
4200ab04:	84878793          	addi	a5,a5,-1976 # 0xa848
4200ab08:	02f60563          	beq	a2,a5,0x4200ab32
4200ab0c:	4901                	li	s2,0
4200ab0e:	3fcb8ab7          	lui	s5,0x3fcb8
4200ab12:	660d                	lui	a2,0x3
4200ab14:	80060613          	addi	a2,a2,-2048 # 0x2800
4200ab18:	4581                	li	a1,0
4200ab1a:	da8a8513          	addi	a0,s5,-600 # 0x3fcb7da8
4200ab1e:	fdff6097          	auipc	ra,0xfdff6
4200ab22:	96a080e7          	jalr	-1686(ra) # 0x40000488
4200ab26:	4301                	li	t1,0
4200ab28:	da8a8813          	addi	a6,s5,-600
4200ab2c:	a051                	j	0x4200abb0
4200ab2e:	4901                	li	s2,0
4200ab30:	bff9                	j	0x4200ab0e
4200ab32:	04800913          	li	s2,72
4200ab36:	bfe1                	j	0x4200ab0e
4200ab38:	0084d713          	srli	a4,s1,0x8
4200ab3c:	00e80023          	sb	a4,0(a6)
4200ab40:	009800a3          	sb	s1,1(a6)
4200ab44:	0809                	addi	a6,a6,2
4200ab46:	0686                	slli	a3,a3,0x1
4200ab48:	0ff6f693          	zext.b	a3,a3
4200ab4c:	fff78893          	addi	a7,a5,-1
4200ab50:	01089793          	slli	a5,a7,0x10
4200ab54:	83c1                	srli	a5,a5,0x10
4200ab56:	01089713          	slli	a4,a7,0x10
4200ab5a:	8341                	srli	a4,a4,0x10
4200ab5c:	c315                	beqz	a4,0x4200ab80
4200ab5e:	0605                	addi	a2,a2,1
4200ab60:	0ff67613          	zext.b	a2,a2
4200ab64:	489d                	li	a7,7
4200ab66:	00c8ed63          	bltu	a7,a2,0x4200ab80
4200ab6a:	00a6f733          	and	a4,a3,a0
4200ab6e:	d769                	beqz	a4,0x4200ab38
4200ab70:	00845713          	srli	a4,s0,0x8
4200ab74:	00e80023          	sb	a4,0(a6)
4200ab78:	008800a3          	sb	s0,1(a6)
4200ab7c:	0809                	addi	a6,a6,2
4200ab7e:	b7e1                	j	0x4200ab46
4200ab80:	0585                	addi	a1,a1,1
4200ab82:	0ff5f593          	zext.b	a1,a1
4200ab86:	4709                	li	a4,2
4200ab88:	02b76163          	bltu	a4,a1,0x4200abaa
4200ab8c:	00131713          	slli	a4,t1,0x1
4200ab90:	971a                	add	a4,a4,t1
4200ab92:	972e                	add	a4,a4,a1
4200ab94:	974a                	add	a4,a4,s2
4200ab96:	3c0ea6b7          	lui	a3,0x3c0ea
4200ab9a:	c7468693          	addi	a3,a3,-908 # 0x3c0e9c74
4200ab9e:	9736                	add	a4,a4,a3
4200aba0:	00074503          	lbu	a0,0(a4)
4200aba4:	4601                	li	a2,0
4200aba6:	4685                	li	a3,1
4200aba8:	bf75                	j	0x4200ab64
4200abaa:	0305                	addi	t1,t1,1
4200abac:	0ff37313          	zext.b	t1,t1
4200abb0:	47dd                	li	a5,23
4200abb2:	0067e563          	bltu	a5,t1,0x4200abbc
4200abb6:	47e1                	li	a5,24
4200abb8:	4581                	li	a1,0
4200abba:	b7f1                	j	0x4200ab86
4200abbc:	00fa06b3          	add	a3,s4,a5
4200abc0:	00f98633          	add	a2,s3,a5
4200abc4:	3fcb8737          	lui	a4,0x3fcb8
4200abc8:	da870713          	addi	a4,a4,-600 # 0x3fcb7da8
4200abcc:	06c2                	slli	a3,a3,0x10
4200abce:	82c1                	srli	a3,a3,0x10
4200abd0:	0642                	slli	a2,a2,0x10
4200abd2:	8241                	srli	a2,a2,0x10
4200abd4:	85d2                	mv	a1,s4
4200abd6:	854e                	mv	a0,s3
4200abd8:	937fe0ef          	jal	0x4200950e
4200abdc:	40f2                	lw	ra,28(sp)
4200abde:	4462                	lw	s0,24(sp)
4200abe0:	44d2                	lw	s1,20(sp)
4200abe2:	4942                	lw	s2,16(sp)
4200abe4:	49b2                	lw	s3,12(sp)
4200abe6:	4a22                	lw	s4,8(sp)
4200abe8:	4a92                	lw	s5,4(sp)
4200abea:	6105                	addi	sp,sp,32
4200abec:	8082                	ret
