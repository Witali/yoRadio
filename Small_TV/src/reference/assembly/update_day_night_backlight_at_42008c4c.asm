
factory-irom.bin:     file format binary


Disassembly of section .data:

42008c4c <.data+0x8c2c>:
42008c4c:	1141                	addi	sp,sp,-16
42008c4e:	c606                	sw	ra,12(sp)
42008c50:	3fcb87b7          	lui	a5,0x3fcb8
42008c54:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
42008c58:	1907a703          	lw	a4,400(a5)
42008c5c:	4785                	li	a5,1
42008c5e:	02f70163          	beq	a4,a5,0x42008c80
42008c62:	3fcb87b7          	lui	a5,0x3fcb8
42008c66:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
42008c6a:	1807a503          	lw	a0,384(a5)
42008c6e:	3fcc47b7          	lui	a5,0x3fcc4
42008c72:	9ec7a783          	lw	a5,-1556(a5) # 0x3fcc39ec
42008c76:	0cf51963          	bne	a0,a5,0x42008d48
42008c7a:	40b2                	lw	ra,12(sp)
42008c7c:	0141                	addi	sp,sp,16
42008c7e:	8082                	ret
42008c80:	3fcb86b7          	lui	a3,0x3fcb8
42008c84:	b9c68693          	addi	a3,a3,-1124 # 0x3fcb7b9c
42008c88:	1946a783          	lw	a5,404(a3)
42008c8c:	00479713          	slli	a4,a5,0x4
42008c90:	8f1d                	sub	a4,a4,a5
42008c92:	00271793          	slli	a5,a4,0x2
42008c96:	01079713          	slli	a4,a5,0x10
42008c9a:	8341                	srli	a4,a4,0x10
42008c9c:	1986a683          	lw	a3,408(a3)
42008ca0:	00469793          	slli	a5,a3,0x4
42008ca4:	8f95                	sub	a5,a5,a3
42008ca6:	00279693          	slli	a3,a5,0x2
42008caa:	01069593          	slli	a1,a3,0x10
42008cae:	81c1                	srli	a1,a1,0x10
42008cb0:	3fcc06b7          	lui	a3,0x3fcc0
42008cb4:	fc868693          	addi	a3,a3,-56 # 0x3fcbffc8
42008cb8:	0066c783          	lbu	a5,6(a3)
42008cbc:	00479613          	slli	a2,a5,0x4
42008cc0:	8e1d                	sub	a2,a2,a5
42008cc2:	00261793          	slli	a5,a2,0x2
42008cc6:	07c2                	slli	a5,a5,0x10
42008cc8:	83c1                	srli	a5,a5,0x10
42008cca:	0076c683          	lbu	a3,7(a3)
42008cce:	97b6                	add	a5,a5,a3
42008cd0:	07c2                	slli	a5,a5,0x10
42008cd2:	83c1                	srli	a5,a5,0x10
42008cd4:	00e7f863          	bgeu	a5,a4,0x42008ce4
42008cd8:	2d000713          	li	a4,720
42008cdc:	02f76d63          	bltu	a4,a5,0x42008d16
42008ce0:	02f5eb63          	bltu	a1,a5,0x42008d16
42008ce4:	3fcb87b7          	lui	a5,0x3fcb8
42008ce8:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
42008cec:	19c7a503          	lw	a0,412(a5)
42008cf0:	3fcc47b7          	lui	a5,0x3fcc4
42008cf4:	9ec7a783          	lw	a5,-1556(a5) # 0x3fcc39ec
42008cf8:	f8f501e3          	beq	a0,a5,0x42008c7a
42008cfc:	ed7ff0ef          	jal	0x42008bd2
42008d00:	3fcb87b7          	lui	a5,0x3fcb8
42008d04:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
42008d08:	19c7a703          	lw	a4,412(a5)
42008d0c:	3fcc47b7          	lui	a5,0x3fcc4
42008d10:	9ee7a623          	sw	a4,-1556(a5) # 0x3fcc39ec
42008d14:	b79d                	j	0x42008c7a
42008d16:	3fcb87b7          	lui	a5,0x3fcb8
42008d1a:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
42008d1e:	1807a503          	lw	a0,384(a5)
42008d22:	3fcc47b7          	lui	a5,0x3fcc4
42008d26:	9ec7a783          	lw	a5,-1556(a5) # 0x3fcc39ec
42008d2a:	f4f508e3          	beq	a0,a5,0x42008c7a
42008d2e:	ea5ff0ef          	jal	0x42008bd2
42008d32:	3fcb87b7          	lui	a5,0x3fcb8
42008d36:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
42008d3a:	1807a703          	lw	a4,384(a5)
42008d3e:	3fcc47b7          	lui	a5,0x3fcc4
42008d42:	9ee7a623          	sw	a4,-1556(a5) # 0x3fcc39ec
42008d46:	bf15                	j	0x42008c7a
42008d48:	e8bff0ef          	jal	0x42008bd2
42008d4c:	3fcb87b7          	lui	a5,0x3fcb8
42008d50:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
42008d54:	1807a703          	lw	a4,384(a5)
42008d58:	3fcc47b7          	lui	a5,0x3fcc4
42008d5c:	9ee7a623          	sw	a4,-1556(a5) # 0x3fcc39ec
42008d60:	bf29                	j	0x42008c7a
