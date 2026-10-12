
factory-irom.bin:     file format binary


Disassembly of section .data:

42010b70 <.data+0x10b50>:
42010b70:	7139                	addi	sp,sp,-64
42010b72:	de06                	sw	ra,60(sp)
42010b74:	dc22                	sw	s0,56(sp)
42010b76:	3fcc47b7          	lui	a5,0x3fcc4
42010b7a:	ab97c783          	lbu	a5,-1351(a5) # 0x3fcc3ab9
42010b7e:	c7ad                	beqz	a5,0x42010be8
42010b80:	1020                	addi	s0,sp,40
42010b82:	8522                	mv	a0,s0
42010b84:	45f990ef          	jal	0x420aa7e2
42010b88:	004c                	addi	a1,sp,4
42010b8a:	8522                	mv	a0,s0
42010b8c:	243990ef          	jal	0x420aa5ce
42010b90:	47e2                	lw	a5,24(sp)
42010b92:	07c00713          	li	a4,124
42010b96:	04f75f63          	bge	a4,a5,0x42010bf4
42010b9a:	3fcc4737          	lui	a4,0x3fcc4
42010b9e:	aa072a23          	sw	zero,-1356(a4) # 0x3fcc3ab4
42010ba2:	3fcc0737          	lui	a4,0x3fcc0
42010ba6:	fc870713          	addi	a4,a4,-56 # 0x3fcbffc8
42010baa:	00874703          	lbu	a4,8(a4)
42010bae:	4692                	lw	a3,4(sp)
42010bb0:	02d70e63          	beq	a4,a3,0x42010bec
42010bb4:	76c78713          	addi	a4,a5,1900
42010bb8:	3fcc07b7          	lui	a5,0x3fcc0
42010bbc:	fc878793          	addi	a5,a5,-56 # 0x3fcbffc8
42010bc0:	c398                	sw	a4,0(a5)
42010bc2:	4752                	lw	a4,20(sp)
42010bc4:	0705                	addi	a4,a4,1
42010bc6:	00e78223          	sb	a4,4(a5)
42010bca:	4742                	lw	a4,16(sp)
42010bcc:	00e782a3          	sb	a4,5(a5)
42010bd0:	4732                	lw	a4,12(sp)
42010bd2:	00e78323          	sb	a4,6(a5)
42010bd6:	4722                	lw	a4,8(sp)
42010bd8:	00e783a3          	sb	a4,7(a5)
42010bdc:	00d78423          	sb	a3,8(a5)
42010be0:	4772                	lw	a4,28(sp)
42010be2:	00e784a3          	sb	a4,9(a5)
42010be6:	a019                	j	0x42010bec
42010be8:	e1fff0ef          	jal	0x42010a06
42010bec:	50f2                	lw	ra,60(sp)
42010bee:	5462                	lw	s0,56(sp)
42010bf0:	6121                	addi	sp,sp,64
42010bf2:	8082                	ret
42010bf4:	3fcc4737          	lui	a4,0x3fcc4
42010bf8:	ab472783          	lw	a5,-1356(a4) # 0x3fcc3ab4
42010bfc:	0785                	addi	a5,a5,1
42010bfe:	aaf72a23          	sw	a5,-1356(a4)
42010c02:	4751                	li	a4,20
42010c04:	fef754e3          	bge	a4,a5,0x42010bec
42010c08:	fe37c097          	auipc	ra,0xfe37c
42010c0c:	7ac080e7          	jalr	1964(ra) # 0x4038d3b4
42010c10:	86aa                	mv	a3,a0
42010c12:	47e2                	lw	a5,24(sp)
42010c14:	76c78793          	addi	a5,a5,1900
42010c18:	3c0c45b7          	lui	a1,0x3c0c4
42010c1c:	bc458713          	addi	a4,a1,-1084 # 0x3c0c3bc4
42010c20:	3c0c4637          	lui	a2,0x3c0c4
42010c24:	c2c60613          	addi	a2,a2,-980 # 0x3c0c3c2c
42010c28:	bc458593          	addi	a1,a1,-1084
42010c2c:	4509                	li	a0,2
42010c2e:	fe37c097          	auipc	ra,0xfe37c
42010c32:	674080e7          	jalr	1652(ra) # 0x4038d2a2
42010c36:	3fcc47b7          	lui	a5,0x3fcc4
42010c3a:	aa07aa23          	sw	zero,-1356(a5) # 0x3fcc3ab4
42010c3e:	262070ef          	jal	0x42017ea0
42010c42:	f54d                	bnez	a0,0x42010bec
42010c44:	3fcc47b7          	lui	a5,0x3fcc4
42010c48:	aa078ca3          	sb	zero,-1351(a5) # 0x3fcc3ab9
42010c4c:	b745                	j	0x42010bec
