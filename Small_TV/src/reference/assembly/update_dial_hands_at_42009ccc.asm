
factory-irom.bin:     file format binary


Disassembly of section .data:

42009ccc <.data+0x9cac>:
42009ccc:	7139                	addi	sp,sp,-64
42009cce:	de06                	sw	ra,60(sp)
42009cd0:	dc22                	sw	s0,56(sp)
42009cd2:	da26                	sw	s1,52(sp)
42009cd4:	d84a                	sw	s2,48(sp)
42009cd6:	d64e                	sw	s3,44(sp)
42009cd8:	d452                	sw	s4,40(sp)
42009cda:	d256                	sw	s5,36(sp)
42009cdc:	d05a                	sw	s6,32(sp)
42009cde:	ce5e                	sw	s7,28(sp)
42009ce0:	cc62                	sw	s8,24(sp)
42009ce2:	ca66                	sw	s9,20(sp)
42009ce4:	c86a                	sw	s10,16(sp)
42009ce6:	c66e                	sw	s11,12(sp)
42009ce8:	3fcc47b7          	lui	a5,0x3fcc4
42009cec:	9f67c783          	lbu	a5,-1546(a5) # 0x3fcc39f6
42009cf0:	44078463          	beqz	a5,0x4200a138
42009cf4:	3fcc47b7          	lui	a5,0x3fcc4
42009cf8:	9e078b23          	sb	zero,-1546(a5) # 0x3fcc39f6
42009cfc:	3fcc0637          	lui	a2,0x3fcc0
42009d00:	fc860613          	addi	a2,a2,-56 # 0x3fcbffc8
42009d04:	00664703          	lbu	a4,6(a2)
42009d08:	aaaab7b7          	lui	a5,0xaaaab
42009d0c:	aab78793          	addi	a5,a5,-1365 # 0xaaaaaaab
42009d10:	02f737b3          	mulhu	a5,a4,a5
42009d14:	838d                	srli	a5,a5,0x3
42009d16:	00179693          	slli	a3,a5,0x1
42009d1a:	97b6                	add	a5,a5,a3
42009d1c:	078a                	slli	a5,a5,0x2
42009d1e:	8f1d                	sub	a4,a4,a5
42009d20:	0ff77b13          	zext.b	s6,a4
42009d24:	00764503          	lbu	a0,7(a2)
42009d28:	fdff7097          	auipc	ra,0xfdff7
42009d2c:	d30080e7          	jalr	-720(ra) # 0x40000a58
42009d30:	3c0d67b7          	lui	a5,0x3c0d6
42009d34:	6207a583          	lw	a1,1568(a5) # 0x3c0d6620
42009d38:	fdff7097          	auipc	ra,0xfdff7
42009d3c:	ce8080e7          	jalr	-792(ra) # 0x40000a20
42009d40:	8baa                	mv	s7,a0
42009d42:	855a                	mv	a0,s6
42009d44:	fdff7097          	auipc	ra,0xfdff7
42009d48:	d14080e7          	jalr	-748(ra) # 0x40000a58
42009d4c:	85de                	mv	a1,s7
42009d4e:	fdff7097          	auipc	ra,0xfdff7
42009d52:	cce080e7          	jalr	-818(ra) # 0x40000a1c
42009d56:	fdff7097          	auipc	ra,0xfdff7
42009d5a:	cd6080e7          	jalr	-810(ra) # 0x40000a2c
42009d5e:	3c0d67b7          	lui	a5,0x3c0d6
42009d62:	2f07a603          	lw	a2,752(a5) # 0x3c0d62f0
42009d66:	2f47a683          	lw	a3,756(a5)
42009d6a:	fdff7097          	auipc	ra,0xfdff7
42009d6e:	d22080e7          	jalr	-734(ra) # 0x40000a8c
42009d72:	3c0d67b7          	lui	a5,0x3c0d6
42009d76:	2f87a603          	lw	a2,760(a5) # 0x3c0d62f8
42009d7a:	2fc7a683          	lw	a3,764(a5)
42009d7e:	fdff7097          	auipc	ra,0xfdff7
42009d82:	b76080e7          	jalr	-1162(ra) # 0x400008f4
42009d86:	fdff7097          	auipc	ra,0xfdff7
42009d8a:	d1e080e7          	jalr	-738(ra) # 0x40000aa4
42009d8e:	3fcc47b7          	lui	a5,0x3fcc4
42009d92:	a0a7a623          	sw	a0,-1524(a5) # 0x3fcc3a0c
42009d96:	fdff7097          	auipc	ra,0xfdff7
42009d9a:	c96080e7          	jalr	-874(ra) # 0x40000a2c
42009d9e:	8caa                	mv	s9,a0
42009da0:	8c2e                	mv	s8,a1
42009da2:	6c29d0ef          	jal	0x420a7464
42009da6:	3c0d6db7          	lui	s11,0x3c0d6
42009daa:	308da603          	lw	a2,776(s11) # 0x3c0d6308
42009dae:	30cda683          	lw	a3,780(s11)
42009db2:	fdff7097          	auipc	ra,0xfdff7
42009db6:	cda080e7          	jalr	-806(ra) # 0x40000a8c
42009dba:	3c0d6d37          	lui	s10,0x3c0d6
42009dbe:	2e8d2603          	lw	a2,744(s10) # 0x3c0d62e8
42009dc2:	2ecd2683          	lw	a3,748(s10)
42009dc6:	fdff7097          	auipc	ra,0xfdff7
42009dca:	c52080e7          	jalr	-942(ra) # 0x40000a18
42009dce:	fdff7097          	auipc	ra,0xfdff7
42009dd2:	c66080e7          	jalr	-922(ra) # 0x40000a34
42009dd6:	8b2a                	mv	s6,a0
42009dd8:	3fcb8bb7          	lui	s7,0x3fcb8
42009ddc:	d90b8b93          	addi	s7,s7,-624 # 0x3fcb7d90
42009de0:	00aba023          	sw	a0,0(s7)
42009de4:	8566                	mv	a0,s9
42009de6:	85e2                	mv	a1,s8
42009de8:	5f89d0ef          	jal	0x420a73e0
42009dec:	308da603          	lw	a2,776(s11)
42009df0:	30cda683          	lw	a3,780(s11)
42009df4:	fdff7097          	auipc	ra,0xfdff7
42009df8:	c98080e7          	jalr	-872(ra) # 0x40000a8c
42009dfc:	862a                	mv	a2,a0
42009dfe:	86ae                	mv	a3,a1
42009e00:	2e8d2503          	lw	a0,744(s10)
42009e04:	2ecd2583          	lw	a1,748(s10)
42009e08:	fdff7097          	auipc	ra,0xfdff7
42009e0c:	c94080e7          	jalr	-876(ra) # 0x40000a9c
42009e10:	fdff7097          	auipc	ra,0xfdff7
42009e14:	c24080e7          	jalr	-988(ra) # 0x40000a34
42009e18:	00aba223          	sw	a0,4(s7)
42009e1c:	3fcb87b7          	lui	a5,0x3fcb8
42009e20:	d787a783          	lw	a5,-648(a5) # 0x3fcb7d78
42009e24:	00fb1963          	bne	s6,a5,0x42009e36
42009e28:	3fcb87b7          	lui	a5,0x3fcb8
42009e2c:	d7878793          	addi	a5,a5,-648 # 0x3fcb7d78
42009e30:	43dc                	lw	a5,4(a5)
42009e32:	00f50c63          	beq	a0,a5,0x42009e4a
42009e36:	4695                	li	a3,5
42009e38:	4601                	li	a2,0
42009e3a:	03200593          	li	a1,50
42009e3e:	3fcc47b7          	lui	a5,0x3fcc4
42009e42:	a007a503          	lw	a0,-1536(a5) # 0x3fcc3a00
42009e46:	bf3ff0ef          	jal	0x42009a38
42009e4a:	3fcc07b7          	lui	a5,0x3fcc0
42009e4e:	fc878793          	addi	a5,a5,-56 # 0x3fcbffc8
42009e52:	0077ca83          	lbu	s5,7(a5)
42009e56:	0087c503          	lbu	a0,8(a5)
42009e5a:	fdff7097          	auipc	ra,0xfdff7
42009e5e:	bfe080e7          	jalr	-1026(ra) # 0x40000a58
42009e62:	3c0d67b7          	lui	a5,0x3c0d6
42009e66:	6207a583          	lw	a1,1568(a5) # 0x3c0d6620
42009e6a:	fdff7097          	auipc	ra,0xfdff7
42009e6e:	bb6080e7          	jalr	-1098(ra) # 0x40000a20
42009e72:	8a2a                	mv	s4,a0
42009e74:	8556                	mv	a0,s5
42009e76:	fdff7097          	auipc	ra,0xfdff7
42009e7a:	be2080e7          	jalr	-1054(ra) # 0x40000a58
42009e7e:	85d2                	mv	a1,s4
42009e80:	fdff7097          	auipc	ra,0xfdff7
42009e84:	b9c080e7          	jalr	-1124(ra) # 0x40000a1c
42009e88:	fdff7097          	auipc	ra,0xfdff7
42009e8c:	ba4080e7          	jalr	-1116(ra) # 0x40000a2c
42009e90:	3c0d67b7          	lui	a5,0x3c0d6
42009e94:	2f07a603          	lw	a2,752(a5) # 0x3c0d62f0
42009e98:	2f47a683          	lw	a3,756(a5)
42009e9c:	fdff7097          	auipc	ra,0xfdff7
42009ea0:	bf0080e7          	jalr	-1040(ra) # 0x40000a8c
42009ea4:	3c0d67b7          	lui	a5,0x3c0d6
42009ea8:	3107a603          	lw	a2,784(a5) # 0x3c0d6310
42009eac:	3147a683          	lw	a3,788(a5)
42009eb0:	fdff7097          	auipc	ra,0xfdff7
42009eb4:	a44080e7          	jalr	-1468(ra) # 0x400008f4
42009eb8:	fdff7097          	auipc	ra,0xfdff7
42009ebc:	bec080e7          	jalr	-1044(ra) # 0x40000aa4
42009ec0:	3fcc47b7          	lui	a5,0x3fcc4
42009ec4:	a0a7a823          	sw	a0,-1520(a5) # 0x3fcc3a10
42009ec8:	fdff7097          	auipc	ra,0xfdff7
42009ecc:	b64080e7          	jalr	-1180(ra) # 0x40000a2c
42009ed0:	8baa                	mv	s7,a0
42009ed2:	8b2e                	mv	s6,a1
42009ed4:	5909d0ef          	jal	0x420a7464
42009ed8:	3c0d6cb7          	lui	s9,0x3c0d6
42009edc:	318ca603          	lw	a2,792(s9) # 0x3c0d6318
42009ee0:	31cca683          	lw	a3,796(s9)
42009ee4:	fdff7097          	auipc	ra,0xfdff7
42009ee8:	ba8080e7          	jalr	-1112(ra) # 0x40000a8c
42009eec:	3c0d6c37          	lui	s8,0x3c0d6
42009ef0:	2e8c2603          	lw	a2,744(s8) # 0x3c0d62e8
42009ef4:	2ecc2683          	lw	a3,748(s8)
42009ef8:	fdff7097          	auipc	ra,0xfdff7
42009efc:	b20080e7          	jalr	-1248(ra) # 0x40000a18
42009f00:	fdff7097          	auipc	ra,0xfdff7
42009f04:	b34080e7          	jalr	-1228(ra) # 0x40000a34
42009f08:	8a2a                	mv	s4,a0
42009f0a:	3fcb8ab7          	lui	s5,0x3fcb8
42009f0e:	d90a8a93          	addi	s5,s5,-624 # 0x3fcb7d90
42009f12:	00aaa423          	sw	a0,8(s5)
42009f16:	855e                	mv	a0,s7
42009f18:	85da                	mv	a1,s6
42009f1a:	4c69d0ef          	jal	0x420a73e0
42009f1e:	318ca603          	lw	a2,792(s9)
42009f22:	31cca683          	lw	a3,796(s9)
42009f26:	fdff7097          	auipc	ra,0xfdff7
42009f2a:	b66080e7          	jalr	-1178(ra) # 0x40000a8c
42009f2e:	862a                	mv	a2,a0
42009f30:	86ae                	mv	a3,a1
42009f32:	2e8c2503          	lw	a0,744(s8)
42009f36:	2ecc2583          	lw	a1,748(s8)
42009f3a:	fdff7097          	auipc	ra,0xfdff7
42009f3e:	b62080e7          	jalr	-1182(ra) # 0x40000a9c
42009f42:	fdff7097          	auipc	ra,0xfdff7
42009f46:	af2080e7          	jalr	-1294(ra) # 0x40000a34
42009f4a:	00aaa623          	sw	a0,12(s5)
42009f4e:	3fcb87b7          	lui	a5,0x3fcb8
42009f52:	d7878793          	addi	a5,a5,-648 # 0x3fcb7d78
42009f56:	479c                	lw	a5,8(a5)
42009f58:	00fa1963          	bne	s4,a5,0x42009f6a
42009f5c:	3fcb87b7          	lui	a5,0x3fcb8
42009f60:	d7878793          	addi	a5,a5,-648 # 0x3fcb7d78
42009f64:	47dc                	lw	a5,12(a5)
42009f66:	00f50c63          	beq	a0,a5,0x42009f7e
42009f6a:	4695                	li	a3,5
42009f6c:	4601                	li	a2,0
42009f6e:	04600593          	li	a1,70
42009f72:	3fcc47b7          	lui	a5,0x3fcc4
42009f76:	a047a503          	lw	a0,-1532(a5) # 0x3fcc3a04
42009f7a:	abfff0ef          	jal	0x42009a38
42009f7e:	3fcc07b7          	lui	a5,0x3fcc0
42009f82:	fc878793          	addi	a5,a5,-56 # 0x3fcbffc8
42009f86:	0087c503          	lbu	a0,8(a5)
42009f8a:	fdff7097          	auipc	ra,0xfdff7
42009f8e:	aca080e7          	jalr	-1334(ra) # 0x40000a54
42009f92:	3c0d67b7          	lui	a5,0x3c0d6
42009f96:	2f07a603          	lw	a2,752(a5) # 0x3c0d62f0
42009f9a:	2f47a683          	lw	a3,756(a5)
42009f9e:	fdff7097          	auipc	ra,0xfdff7
42009fa2:	aee080e7          	jalr	-1298(ra) # 0x40000a8c
42009fa6:	3c0d67b7          	lui	a5,0x3c0d6
42009faa:	3107a603          	lw	a2,784(a5) # 0x3c0d6310
42009fae:	3147a683          	lw	a3,788(a5)
42009fb2:	fdff7097          	auipc	ra,0xfdff7
42009fb6:	942080e7          	jalr	-1726(ra) # 0x400008f4
42009fba:	fdff7097          	auipc	ra,0xfdff7
42009fbe:	aea080e7          	jalr	-1302(ra) # 0x40000aa4
42009fc2:	3fcc47b7          	lui	a5,0x3fcc4
42009fc6:	a0a7aa23          	sw	a0,-1516(a5) # 0x3fcc3a14
42009fca:	fdff7097          	auipc	ra,0xfdff7
42009fce:	a62080e7          	jalr	-1438(ra) # 0x40000a2c
42009fd2:	8aaa                	mv	s5,a0
42009fd4:	8a2e                	mv	s4,a1
42009fd6:	48e9d0ef          	jal	0x420a7464
42009fda:	3c0d6bb7          	lui	s7,0x3c0d6
42009fde:	320ba603          	lw	a2,800(s7) # 0x3c0d6320
42009fe2:	324ba683          	lw	a3,804(s7)
42009fe6:	fdff7097          	auipc	ra,0xfdff7
42009fea:	aa6080e7          	jalr	-1370(ra) # 0x40000a8c
42009fee:	3c0d6b37          	lui	s6,0x3c0d6
42009ff2:	2e8b2603          	lw	a2,744(s6) # 0x3c0d62e8
42009ff6:	2ecb2683          	lw	a3,748(s6)
42009ffa:	fdff7097          	auipc	ra,0xfdff7
42009ffe:	a1e080e7          	jalr	-1506(ra) # 0x40000a18
4200a002:	fdff7097          	auipc	ra,0xfdff7
4200a006:	a32080e7          	jalr	-1486(ra) # 0x40000a34
4200a00a:	892a                	mv	s2,a0
4200a00c:	3fcb89b7          	lui	s3,0x3fcb8
4200a010:	d9098993          	addi	s3,s3,-624 # 0x3fcb7d90
4200a014:	00a9a823          	sw	a0,16(s3)
4200a018:	8556                	mv	a0,s5
4200a01a:	85d2                	mv	a1,s4
4200a01c:	3c49d0ef          	jal	0x420a73e0
4200a020:	320ba603          	lw	a2,800(s7)
4200a024:	324ba683          	lw	a3,804(s7)
4200a028:	fdff7097          	auipc	ra,0xfdff7
4200a02c:	a64080e7          	jalr	-1436(ra) # 0x40000a8c
4200a030:	862a                	mv	a2,a0
4200a032:	86ae                	mv	a3,a1
4200a034:	2e8b2503          	lw	a0,744(s6)
4200a038:	2ecb2583          	lw	a1,748(s6)
4200a03c:	fdff7097          	auipc	ra,0xfdff7
4200a040:	a60080e7          	jalr	-1440(ra) # 0x40000a9c
4200a044:	fdff7097          	auipc	ra,0xfdff7
4200a048:	9f0080e7          	jalr	-1552(ra) # 0x40000a34
4200a04c:	00a9aa23          	sw	a0,20(s3)
4200a050:	3fcb87b7          	lui	a5,0x3fcb8
4200a054:	d7878793          	addi	a5,a5,-648 # 0x3fcb7d78
4200a058:	4b9c                	lw	a5,16(a5)
4200a05a:	00f91963          	bne	s2,a5,0x4200a06c
4200a05e:	3fcb87b7          	lui	a5,0x3fcb8
4200a062:	d7878793          	addi	a5,a5,-648 # 0x3fcb7d78
4200a066:	4bdc                	lw	a5,20(a5)
4200a068:	00f50c63          	beq	a0,a5,0x4200a080
4200a06c:	4695                	li	a3,5
4200a06e:	4601                	li	a2,0
4200a070:	05a00593          	li	a1,90
4200a074:	3fcc47b7          	lui	a5,0x3fcc4
4200a078:	a087a503          	lw	a0,-1528(a5) # 0x3fcc3a08
4200a07c:	9bdff0ef          	jal	0x42009a38
4200a080:	3fcc44b7          	lui	s1,0x3fcc4
4200a084:	4695                	li	a3,5
4200a086:	6441                	lui	s0,0x10
4200a088:	80040613          	addi	a2,s0,-2048 # 0xf800
4200a08c:	03200593          	li	a1,50
4200a090:	a0c4a503          	lw	a0,-1524(s1) # 0x3fcc3a0c
4200a094:	9a5ff0ef          	jal	0x42009a38
4200a098:	3fcc4937          	lui	s2,0x3fcc4
4200a09c:	4695                	li	a3,5
4200a09e:	fe040613          	addi	a2,s0,-32
4200a0a2:	04600593          	li	a1,70
4200a0a6:	a1092503          	lw	a0,-1520(s2) # 0x3fcc3a10
4200a0aa:	98fff0ef          	jal	0x42009a38
4200a0ae:	3fcc49b7          	lui	s3,0x3fcc4
4200a0b2:	468d                	li	a3,3
4200a0b4:	fff40613          	addi	a2,s0,-1
4200a0b8:	05a00593          	li	a1,90
4200a0bc:	a149a503          	lw	a0,-1516(s3) # 0x3fcc3a14
4200a0c0:	979ff0ef          	jal	0x42009a38
4200a0c4:	fff40693          	addi	a3,s0,-1
4200a0c8:	4619                	li	a2,6
4200a0ca:	07800593          	li	a1,120
4200a0ce:	852e                	mv	a0,a1
4200a0d0:	cf4ff0ef          	jal	0x420095c4
4200a0d4:	a149a703          	lw	a4,-1516(s3)
4200a0d8:	3fcc47b7          	lui	a5,0x3fcc4
4200a0dc:	a0e7a423          	sw	a4,-1528(a5) # 0x3fcc3a08
4200a0e0:	a1092703          	lw	a4,-1520(s2)
4200a0e4:	3fcc47b7          	lui	a5,0x3fcc4
4200a0e8:	a0e7a223          	sw	a4,-1532(a5) # 0x3fcc3a04
4200a0ec:	a0c4a703          	lw	a4,-1524(s1)
4200a0f0:	3fcc47b7          	lui	a5,0x3fcc4
4200a0f4:	a0e7a023          	sw	a4,-1536(a5) # 0x3fcc3a00
4200a0f8:	3fcb8737          	lui	a4,0x3fcb8
4200a0fc:	d9070713          	addi	a4,a4,-624 # 0x3fcb7d90
4200a100:	4b14                	lw	a3,16(a4)
4200a102:	3fcb87b7          	lui	a5,0x3fcb8
4200a106:	d7878793          	addi	a5,a5,-648 # 0x3fcb7d78
4200a10a:	cb94                	sw	a3,16(a5)
4200a10c:	4b54                	lw	a3,20(a4)
4200a10e:	cbd4                	sw	a3,20(a5)
4200a110:	4714                	lw	a3,8(a4)
4200a112:	c794                	sw	a3,8(a5)
4200a114:	4754                	lw	a3,12(a4)
4200a116:	c7d4                	sw	a3,12(a5)
4200a118:	4314                	lw	a3,0(a4)
4200a11a:	c394                	sw	a3,0(a5)
4200a11c:	4358                	lw	a4,4(a4)
4200a11e:	c3d8                	sw	a4,4(a5)
4200a120:	fff40713          	addi	a4,s0,-1
4200a124:	46c1                	li	a3,16
4200a126:	3fcb8637          	lui	a2,0x3fcb8
4200a12a:	b8460613          	addi	a2,a2,-1148 # 0x3fcb7b84
4200a12e:	0e100593          	li	a1,225
4200a132:	4515                	li	a0,5
4200a134:	0eb000ef          	jal	0x4200aa1e
4200a138:	50f2                	lw	ra,60(sp)
4200a13a:	5462                	lw	s0,56(sp)
4200a13c:	54d2                	lw	s1,52(sp)
4200a13e:	5942                	lw	s2,48(sp)
4200a140:	59b2                	lw	s3,44(sp)
4200a142:	5a22                	lw	s4,40(sp)
4200a144:	5a92                	lw	s5,36(sp)
4200a146:	5b02                	lw	s6,32(sp)
4200a148:	4bf2                	lw	s7,28(sp)
4200a14a:	4c62                	lw	s8,24(sp)
4200a14c:	4cd2                	lw	s9,20(sp)
4200a14e:	4d42                	lw	s10,16(sp)
4200a150:	4db2                	lw	s11,12(sp)
4200a152:	6121                	addi	sp,sp,64
4200a154:	8082                	ret
