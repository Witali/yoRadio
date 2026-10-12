
factory-irom.bin:     file format binary


Disassembly of section .data:

4200bd8c <.data+0xbd6c>:
4200bd8c:	1101                	addi	sp,sp,-32
4200bd8e:	ce06                	sw	ra,28(sp)
4200bd90:	cc22                	sw	s0,24(sp)
4200bd92:	ca26                	sw	s1,20(sp)
4200bd94:	c84a                	sw	s2,16(sp)
4200bd96:	c64e                	sw	s3,12(sp)
4200bd98:	3fcc47b7          	lui	a5,0x3fcc4
4200bd9c:	9f67c783          	lbu	a5,-1546(a5) # 0x3fcc39f6
4200bda0:	cbb9                	beqz	a5,0x4200bdf6
4200bda2:	3fcc47b7          	lui	a5,0x3fcc4
4200bda6:	9e078b23          	sb	zero,-1546(a5) # 0x3fcc39f6
4200bdaa:	3fcc07b7          	lui	a5,0x3fcc0
4200bdae:	fc878793          	addi	a5,a5,-56 # 0x3fcbffc8
4200bdb2:	0087c783          	lbu	a5,8(a5)
4200bdb6:	8b85                	andi	a5,a5,1
4200bdb8:	ebb9                	bnez	a5,0x4200be0e
4200bdba:	3fcbb637          	lui	a2,0x3fcbb
4200bdbe:	9cc60793          	addi	a5,a2,-1588 # 0x3fcba9cc
4200bdc2:	0007a023          	sw	zero,0(a5)
4200bdc6:	0007a223          	sw	zero,4(a5)
4200bdca:	0007a423          	sw	zero,8(a5)
4200bdce:	00079623          	sh	zero,12(a5)
4200bdd2:	00078723          	sb	zero,14(a5)
4200bdd6:	03a00713          	li	a4,58
4200bdda:	00e78023          	sb	a4,0(a5)
4200bdde:	4781                	li	a5,0
4200bde0:	6741                	lui	a4,0x10
4200bde2:	177d                	addi	a4,a4,-1 # 0xffff
4200bde4:	05000693          	li	a3,80
4200bde8:	9cc60613          	addi	a2,a2,-1588
4200bdec:	85b6                	mv	a1,a3
4200bdee:	06400513          	li	a0,100
4200bdf2:	dfdfe0ef          	jal	0x4200abee
4200bdf6:	3fcc47b7          	lui	a5,0x3fcc4
4200bdfa:	9f57c783          	lbu	a5,-1547(a5) # 0x3fcc39f5
4200bdfe:	e7b1                	bnez	a5,0x4200be4a
4200be00:	40f2                	lw	ra,28(sp)
4200be02:	4462                	lw	s0,24(sp)
4200be04:	44d2                	lw	s1,20(sp)
4200be06:	4942                	lw	s2,16(sp)
4200be08:	49b2                	lw	s3,12(sp)
4200be0a:	6105                	addi	sp,sp,32
4200be0c:	8082                	ret
4200be0e:	3fcbb637          	lui	a2,0x3fcbb
4200be12:	9cc60793          	addi	a5,a2,-1588 # 0x3fcba9cc
4200be16:	0007a023          	sw	zero,0(a5)
4200be1a:	0007a223          	sw	zero,4(a5)
4200be1e:	0007a423          	sw	zero,8(a5)
4200be22:	00079623          	sh	zero,12(a5)
4200be26:	00078723          	sb	zero,14(a5)
4200be2a:	02000713          	li	a4,32
4200be2e:	00e78023          	sb	a4,0(a5)
4200be32:	4781                	li	a5,0
4200be34:	4701                	li	a4,0
4200be36:	05000693          	li	a3,80
4200be3a:	9cc60613          	addi	a2,a2,-1588
4200be3e:	85b6                	mv	a1,a3
4200be40:	06400513          	li	a0,100
4200be44:	dabfe0ef          	jal	0x4200abee
4200be48:	b77d                	j	0x4200bdf6
4200be4a:	3fcc47b7          	lui	a5,0x3fcc4
4200be4e:	9e078aa3          	sb	zero,-1547(a5) # 0x3fcc39f5
4200be52:	3fcbb7b7          	lui	a5,0x3fcbb
4200be56:	9cc78793          	addi	a5,a5,-1588 # 0x3fcba9cc
4200be5a:	0007a023          	sw	zero,0(a5)
4200be5e:	0007a223          	sw	zero,4(a5)
4200be62:	0007a423          	sw	zero,8(a5)
4200be66:	00079623          	sh	zero,12(a5)
4200be6a:	00078723          	sb	zero,14(a5)
4200be6e:	3fcc07b7          	lui	a5,0x3fcc0
4200be72:	fc878793          	addi	a5,a5,-56 # 0x3fcbffc8
4200be76:	0067c703          	lbu	a4,6(a5)
4200be7a:	3fcb87b7          	lui	a5,0x3fcb8
4200be7e:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200be82:	1707a683          	lw	a3,368(a5)
4200be86:	4785                	li	a5,1
4200be88:	16f68463          	beq	a3,a5,0x4200bff0
4200be8c:	ccccd437          	lui	s0,0xccccd
4200be90:	ccd40413          	addi	s0,s0,-819 # 0xcccccccd
4200be94:	028736b3          	mulhu	a3,a4,s0
4200be98:	828d                	srli	a3,a3,0x3
4200be9a:	03068793          	addi	a5,a3,48
4200be9e:	3fcbb937          	lui	s2,0x3fcbb
4200bea2:	9cc90493          	addi	s1,s2,-1588 # 0x3fcba9cc
4200bea6:	00f48023          	sb	a5,0(s1)
4200beaa:	00269793          	slli	a5,a3,0x2
4200beae:	97b6                	add	a5,a5,a3
4200beb0:	0786                	slli	a5,a5,0x1
4200beb2:	8f1d                	sub	a4,a4,a5
4200beb4:	03070713          	addi	a4,a4,48
4200beb8:	00e480a3          	sb	a4,1(s1)
4200bebc:	67b1                	lui	a5,0xc
4200bebe:	61878793          	addi	a5,a5,1560 # 0xc618
4200bec2:	69c1                	lui	s3,0x10
4200bec4:	fff98713          	addi	a4,s3,-1 # 0xffff
4200bec8:	05000693          	li	a3,80
4200becc:	9cc90613          	addi	a2,s2,-1588
4200bed0:	85b6                	mv	a1,a3
4200bed2:	4529                	li	a0,10
4200bed4:	d1bfe0ef          	jal	0x4200abee
4200bed8:	0004a023          	sw	zero,0(s1)
4200bedc:	0004a223          	sw	zero,4(s1)
4200bee0:	0004a423          	sw	zero,8(s1)
4200bee4:	00049623          	sh	zero,12(s1)
4200bee8:	00048723          	sb	zero,14(s1)
4200beec:	3fcc07b7          	lui	a5,0x3fcc0
4200bef0:	fc878793          	addi	a5,a5,-56 # 0x3fcbffc8
4200bef4:	0077c703          	lbu	a4,7(a5)
4200bef8:	028737b3          	mulhu	a5,a4,s0
4200befc:	838d                	srli	a5,a5,0x3
4200befe:	03078693          	addi	a3,a5,48
4200bf02:	00d48023          	sb	a3,0(s1)
4200bf06:	00279693          	slli	a3,a5,0x2
4200bf0a:	97b6                	add	a5,a5,a3
4200bf0c:	0786                	slli	a5,a5,0x1
4200bf0e:	8f1d                	sub	a4,a4,a5
4200bf10:	03070713          	addi	a4,a4,48
4200bf14:	00e480a3          	sb	a4,1(s1)
4200bf18:	67b1                	lui	a5,0xc
4200bf1a:	61878793          	addi	a5,a5,1560 # 0xc618
4200bf1e:	fff98713          	addi	a4,s3,-1
4200bf22:	05000693          	li	a3,80
4200bf26:	9cc90613          	addi	a2,s2,-1588
4200bf2a:	85b6                	mv	a1,a3
4200bf2c:	09600513          	li	a0,150
4200bf30:	cbffe0ef          	jal	0x4200abee
4200bf34:	3fcb87b7          	lui	a5,0x3fcb8
4200bf38:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200bf3c:	17c7a783          	lw	a5,380(a5)
4200bf40:	cfdd                	beqz	a5,0x4200bffe
4200bf42:	4705                	li	a4,1
4200bf44:	0ee78163          	beq	a5,a4,0x4200c026
4200bf48:	4709                	li	a4,2
4200bf4a:	10e78463          	beq	a5,a4,0x4200c052
4200bf4e:	3fcbb537          	lui	a0,0x3fcbb
4200bf52:	9cc50513          	addi	a0,a0,-1588 # 0x3fcba9cc
4200bf56:	fdff4097          	auipc	ra,0xfdff4
4200bf5a:	552080e7          	jalr	1362(ra) # 0x400004a8
4200bf5e:	0ff57513          	zext.b	a0,a0
4200bf62:	47d1                	li	a5,20
4200bf64:	10a7ed63          	bltu	a5,a0,0x4200c07e
4200bf68:	c915                	beqz	a0,0x4200bf9c
4200bf6a:	00151793          	slli	a5,a0,0x1
4200bf6e:	953e                	add	a0,a0,a5
4200bf70:	050a                	slli	a0,a0,0x2
4200bf72:	0ff57513          	zext.b	a0,a0
4200bf76:	0f000793          	li	a5,240
4200bf7a:	40a78533          	sub	a0,a5,a0
4200bf7e:	8505                	srai	a0,a0,0x1
4200bf80:	0542                	slli	a0,a0,0x10
4200bf82:	8141                	srli	a0,a0,0x10
4200bf84:	4781                	li	a5,0
4200bf86:	6741                	lui	a4,0x10
4200bf88:	177d                	addi	a4,a4,-1 # 0xffff
4200bf8a:	46e1                	li	a3,24
4200bf8c:	3fcbb637          	lui	a2,0x3fcbb
4200bf90:	9cc60613          	addi	a2,a2,-1588 # 0x3fcba9cc
4200bf94:	0b400593          	li	a1,180
4200bf98:	c57fe0ef          	jal	0x4200abee
4200bf9c:	3fcc07b7          	lui	a5,0x3fcc0
4200bfa0:	fc878793          	addi	a5,a5,-56 # 0x3fcbffc8
4200bfa4:	0097c783          	lbu	a5,9(a5)
4200bfa8:	4705                	li	a4,1
4200bfaa:	0ce78c63          	beq	a5,a4,0x4200c082
4200bfae:	4709                	li	a4,2
4200bfb0:	0ee78263          	beq	a5,a4,0x4200c094
4200bfb4:	470d                	li	a4,3
4200bfb6:	0ee78863          	beq	a5,a4,0x4200c0a6
4200bfba:	4711                	li	a4,4
4200bfbc:	0ee78e63          	beq	a5,a4,0x4200c0b8
4200bfc0:	4715                	li	a4,5
4200bfc2:	10e78463          	beq	a5,a4,0x4200c0ca
4200bfc6:	4719                	li	a4,6
4200bfc8:	10e78a63          	beq	a5,a4,0x4200c0dc
4200bfcc:	471d                	li	a4,7
4200bfce:	12e78063          	beq	a5,a4,0x4200c0ee
4200bfd2:	4781                	li	a5,0
4200bfd4:	7e000713          	li	a4,2016
4200bfd8:	46e1                	li	a3,24
4200bfda:	3fcbb637          	lui	a2,0x3fcbb
4200bfde:	9cc60613          	addi	a2,a2,-1588 # 0x3fcba9cc
4200bfe2:	0cc00593          	li	a1,204
4200bfe6:	06600513          	li	a0,102
4200bfea:	c05fe0ef          	jal	0x4200abee
4200bfee:	bd09                	j	0x4200be00
4200bff0:	47b1                	li	a5,12
4200bff2:	e8e7fde3          	bgeu	a5,a4,0x4200be8c
4200bff6:	1751                	addi	a4,a4,-12
4200bff8:	0ff77713          	zext.b	a4,a4
4200bffc:	bd41                	j	0x4200be8c
4200bffe:	3fcc07b7          	lui	a5,0x3fcc0
4200c002:	fc878793          	addi	a5,a5,-56 # 0x3fcbffc8
4200c006:	4398                	lw	a4,0(a5)
4200c008:	0057c683          	lbu	a3,5(a5)
4200c00c:	0047c603          	lbu	a2,4(a5)
4200c010:	3c0c35b7          	lui	a1,0x3c0c3
4200c014:	b3458593          	addi	a1,a1,-1228 # 0x3c0c2b34
4200c018:	9cc90513          	addi	a0,s2,-1588
4200c01c:	fdff4097          	auipc	ra,0xfdff4
4200c020:	68c080e7          	jalr	1676(ra) # 0x400006a8
4200c024:	b72d                	j	0x4200bf4e
4200c026:	3fcc07b7          	lui	a5,0x3fcc0
4200c02a:	fc878793          	addi	a5,a5,-56 # 0x3fcbffc8
4200c02e:	4398                	lw	a4,0(a5)
4200c030:	0047c683          	lbu	a3,4(a5)
4200c034:	0057c603          	lbu	a2,5(a5)
4200c038:	3c0c35b7          	lui	a1,0x3c0c3
4200c03c:	b3458593          	addi	a1,a1,-1228 # 0x3c0c2b34
4200c040:	3fcbb537          	lui	a0,0x3fcbb
4200c044:	9cc50513          	addi	a0,a0,-1588 # 0x3fcba9cc
4200c048:	fdff4097          	auipc	ra,0xfdff4
4200c04c:	660080e7          	jalr	1632(ra) # 0x400006a8
4200c050:	bdfd                	j	0x4200bf4e
4200c052:	3fcc07b7          	lui	a5,0x3fcc0
4200c056:	fc878793          	addi	a5,a5,-56 # 0x3fcbffc8
4200c05a:	0057c703          	lbu	a4,5(a5)
4200c05e:	0047c683          	lbu	a3,4(a5)
4200c062:	4390                	lw	a2,0(a5)
4200c064:	3c0c35b7          	lui	a1,0x3c0c3
4200c068:	b3458593          	addi	a1,a1,-1228 # 0x3c0c2b34
4200c06c:	3fcbb537          	lui	a0,0x3fcbb
4200c070:	9cc50513          	addi	a0,a0,-1588 # 0x3fcba9cc
4200c074:	fdff4097          	auipc	ra,0xfdff4
4200c078:	634080e7          	jalr	1588(ra) # 0x400006a8
4200c07c:	bdc9                	j	0x4200bf4e
4200c07e:	4551                	li	a0,20
4200c080:	b5ed                	j	0x4200bf6a
4200c082:	3fcbb737          	lui	a4,0x3fcbb
4200c086:	006e77b7          	lui	a5,0x6e7
4200c08a:	f4d78793          	addi	a5,a5,-179 # 0x6e6f4d
4200c08e:	9cf72623          	sw	a5,-1588(a4) # 0x3fcba9cc
4200c092:	b781                	j	0x4200bfd2
4200c094:	3fcbb737          	lui	a4,0x3fcbb
4200c098:	006577b7          	lui	a5,0x657
4200c09c:	55478793          	addi	a5,a5,1364 # 0x657554
4200c0a0:	9cf72623          	sw	a5,-1588(a4) # 0x3fcba9cc
4200c0a4:	b73d                	j	0x4200bfd2
4200c0a6:	3fcbb737          	lui	a4,0x3fcbb
4200c0aa:	006467b7          	lui	a5,0x646
4200c0ae:	55778793          	addi	a5,a5,1367 # 0x646557
4200c0b2:	9cf72623          	sw	a5,-1588(a4) # 0x3fcba9cc
4200c0b6:	bf31                	j	0x4200bfd2
4200c0b8:	3fcbb737          	lui	a4,0x3fcbb
4200c0bc:	007577b7          	lui	a5,0x757
4200c0c0:	85478793          	addi	a5,a5,-1964 # 0x756854
4200c0c4:	9cf72623          	sw	a5,-1588(a4) # 0x3fcba9cc
4200c0c8:	b729                	j	0x4200bfd2
4200c0ca:	3fcbb737          	lui	a4,0x3fcbb
4200c0ce:	006977b7          	lui	a5,0x697
4200c0d2:	24678793          	addi	a5,a5,582 # 0x697246
4200c0d6:	9cf72623          	sw	a5,-1588(a4) # 0x3fcba9cc
4200c0da:	bde5                	j	0x4200bfd2
4200c0dc:	3fcbb737          	lui	a4,0x3fcbb
4200c0e0:	007467b7          	lui	a5,0x746
4200c0e4:	15378793          	addi	a5,a5,339 # 0x746153
4200c0e8:	9cf72623          	sw	a5,-1588(a4) # 0x3fcba9cc
4200c0ec:	b5dd                	j	0x4200bfd2
4200c0ee:	3fcbb737          	lui	a4,0x3fcbb
4200c0f2:	006e77b7          	lui	a5,0x6e7
4200c0f6:	55378793          	addi	a5,a5,1363 # 0x6e7553
4200c0fa:	9cf72623          	sw	a5,-1588(a4) # 0x3fcba9cc
4200c0fe:	bdd1                	j	0x4200bfd2
