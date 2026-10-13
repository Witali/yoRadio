
factory-irom.bin:     file format binary


Disassembly of section .data:

42010eca <.data+0x10eaa>:
42010eca:	7159                	addi	sp,sp,-112
42010ecc:	d686                	sw	ra,108(sp)
42010ece:	d4a2                	sw	s0,104(sp)
42010ed0:	d2a6                	sw	s1,100(sp)
42010ed2:	d0ca                	sw	s2,96(sp)
42010ed4:	cece                	sw	s3,92(sp)
42010ed6:	ccd2                	sw	s4,88(sp)
42010ed8:	cad6                	sw	s5,84(sp)
42010eda:	c8da                	sw	s6,80(sp)
42010edc:	c6de                	sw	s7,76(sp)
42010ede:	c4e2                	sw	s8,72(sp)
42010ee0:	c2e6                	sw	s9,68(sp)
42010ee2:	8a2a                	mv	s4,a0
42010ee4:	8b2e                	mv	s6,a1
42010ee6:	8ab2                	mv	s5,a2
42010ee8:	46b9                	li	a3,14
42010eea:	180c                	addi	a1,sp,48
42010eec:	4501                	li	a0,0
42010eee:	fe381097          	auipc	ra,0xfe381
42010ef2:	438080e7          	jalr	1080(ra) # 0x40392326
42010ef6:	02800693          	li	a3,40
42010efa:	00ea8613          	addi	a2,s5,14
42010efe:	002c                	addi	a1,sp,8
42010f00:	4501                	li	a0,0
42010f02:	fe381097          	auipc	ra,0xfe381
42010f06:	424080e7          	jalr	1060(ra) # 0x40392326
42010f0a:	03015703          	lhu	a4,48(sp)
42010f0e:	6795                	lui	a5,0x5
42010f10:	d4278793          	addi	a5,a5,-702 # 0x4d42
42010f14:	00f71763          	bne	a4,a5,0x42010f22
42010f18:	01615703          	lhu	a4,22(sp)
42010f1c:	47e1                	li	a5,24
42010f1e:	00f70f63          	beq	a4,a5,0x42010f3c
42010f22:	50b6                	lw	ra,108(sp)
42010f24:	5426                	lw	s0,104(sp)
42010f26:	5496                	lw	s1,100(sp)
42010f28:	5906                	lw	s2,96(sp)
42010f2a:	49f6                	lw	s3,92(sp)
42010f2c:	4a66                	lw	s4,88(sp)
42010f2e:	4ad6                	lw	s5,84(sp)
42010f30:	4b46                	lw	s6,80(sp)
42010f32:	4bb6                	lw	s7,76(sp)
42010f34:	4c26                	lw	s8,72(sp)
42010f36:	4c96                	lw	s9,68(sp)
42010f38:	6165                	addi	sp,sp,112
42010f3a:	8082                	ret
42010f3c:	4cb2                	lw	s9,12(sp)
42010f3e:	8966                	mv	s2,s9
42010f40:	47c2                	lw	a5,16(sp)
42010f42:	41f7d713          	srai	a4,a5,0x1f
42010f46:	8fb9                	xor	a5,a5,a4
42010f48:	40e78c33          	sub	s8,a5,a4
42010f4c:	001c8793          	addi	a5,s9,1
42010f50:	00179b93          	slli	s7,a5,0x1
42010f54:	9bbe                	add	s7,s7,a5
42010f56:	ffcbfb93          	andi	s7,s7,-4
42010f5a:	855e                	mv	a0,s7
42010f5c:	fe37d097          	auipc	ra,0xfe37d
42010f60:	562080e7          	jalr	1378(ra) # 0x4038e4be
42010f64:	842a                	mv	s0,a0
42010f66:	001c9513          	slli	a0,s9,0x1
42010f6a:	fe37d097          	auipc	ra,0xfe37d
42010f6e:	554080e7          	jalr	1364(ra) # 0x4038e4be
42010f72:	84aa                	mv	s1,a0
42010f74:	4981                	li	s3,0
42010f76:	a8b5                	j	0x42010ff2
42010f78:	00161593          	slli	a1,a2,0x1
42010f7c:	00c587b3          	add	a5,a1,a2
42010f80:	00f40733          	add	a4,s0,a5
42010f84:	00074703          	lbu	a4,0(a4)
42010f88:	00178693          	addi	a3,a5,1
42010f8c:	96a2                	add	a3,a3,s0
42010f8e:	0006c683          	lbu	a3,0(a3)
42010f92:	0789                	addi	a5,a5,2
42010f94:	97a2                	add	a5,a5,s0
42010f96:	0007c783          	lbu	a5,0(a5)
42010f9a:	07a2                	slli	a5,a5,0x8
42010f9c:	8007f793          	andi	a5,a5,-2048
42010fa0:	07c2                	slli	a5,a5,0x10
42010fa2:	87c1                	srai	a5,a5,0x10
42010fa4:	068e                	slli	a3,a3,0x3
42010fa6:	7e06f693          	andi	a3,a3,2016
42010faa:	8fd5                	or	a5,a5,a3
42010fac:	830d                	srli	a4,a4,0x3
42010fae:	0ff77713          	zext.b	a4,a4
42010fb2:	8fd9                	or	a5,a5,a4
42010fb4:	01079713          	slli	a4,a5,0x10
42010fb8:	8741                	srai	a4,a4,0x10
42010fba:	95a6                	add	a1,a1,s1
42010fbc:	07c2                	slli	a5,a5,0x10
42010fbe:	83c1                	srli	a5,a5,0x10
42010fc0:	83a1                	srli	a5,a5,0x8
42010fc2:	0722                	slli	a4,a4,0x8
42010fc4:	8fd9                	or	a5,a5,a4
42010fc6:	00f59023          	sh	a5,0(a1)
42010fca:	0605                	addi	a2,a2,1
42010fcc:	fb2666e3          	bltu	a2,s2,0x42010f78
42010fd0:	013b05b3          	add	a1,s6,s3
42010fd4:	05c2                	slli	a1,a1,0x10
42010fd6:	81c1                	srli	a1,a1,0x10
42010fd8:	019a0633          	add	a2,s4,s9
42010fdc:	0642                	slli	a2,a2,0x10
42010fde:	8241                	srli	a2,a2,0x10
42010fe0:	167d                	addi	a2,a2,-1
42010fe2:	8726                	mv	a4,s1
42010fe4:	86ae                	mv	a3,a1
42010fe6:	0642                	slli	a2,a2,0x10
42010fe8:	8241                	srli	a2,a2,0x10
42010fea:	8552                	mv	a0,s4
42010fec:	d22f80ef          	jal	0x4200950e
42010ff0:	0985                	addi	s3,s3,1
42010ff2:	864e                	mv	a2,s3
42010ff4:	0389fb63          	bgeu	s3,s8,0x4201102a
42010ff8:	47c2                	lw	a5,16(sp)
42010ffa:	00f05563          	blez	a5,0x42011004
42010ffe:	413c0633          	sub	a2,s8,s3
42011002:	167d                	addi	a2,a2,-1
42011004:	03a15703          	lhu	a4,58(sp)
42011008:	03c15783          	lhu	a5,60(sp)
4201100c:	07c2                	slli	a5,a5,0x10
4201100e:	8fd9                	or	a5,a5,a4
42011010:	97d6                	add	a5,a5,s5
42011012:	03760633          	mul	a2,a2,s7
42011016:	86de                	mv	a3,s7
42011018:	963e                	add	a2,a2,a5
4201101a:	85a2                	mv	a1,s0
4201101c:	4501                	li	a0,0
4201101e:	fe381097          	auipc	ra,0xfe381
42011022:	308080e7          	jalr	776(ra) # 0x40392326
42011026:	4601                	li	a2,0
42011028:	b755                	j	0x42010fcc
4201102a:	8522                	mv	a0,s0
4201102c:	fe37d097          	auipc	ra,0xfe37d
42011030:	4ae080e7          	jalr	1198(ra) # 0x4038e4da
42011034:	8526                	mv	a0,s1
42011036:	fe37d097          	auipc	ra,0xfe37d
4201103a:	4a4080e7          	jalr	1188(ra) # 0x4038e4da
4201103e:	b5d5                	j	0x42010f22
