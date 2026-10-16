
factory-irom.bin:     file format binary


Disassembly of section .data:

4200e9ea <.data+0xe9ca>:
4200e9ea:	7129                	addi	sp,sp,-320
4200e9ec:	12112e23          	sw	ra,316(sp)
4200e9f0:	12812c23          	sw	s0,312(sp)
4200e9f4:	12912a23          	sw	s1,308(sp)
4200e9f8:	13212823          	sw	s2,304(sp)
4200e9fc:	13312623          	sw	s3,300(sp)
4200ea00:	13412423          	sw	s4,296(sp)
4200ea04:	892a                	mv	s2,a0
4200ea06:	0ff00613          	li	a2,255
4200ea0a:	100c                	addi	a1,sp,32
4200ea0c:	4892c0ef          	jal	0x4203b694
4200ea10:	12a05863          	blez	a0,0x4200eb40
4200ea14:	12050793          	addi	a5,a0,288
4200ea18:	978a                	add	a5,a5,sp
4200ea1a:	f0078023          	sb	zero,-256(a5)
4200ea1e:	1000                	addi	s0,sp,32
4200ea20:	3c0c35b7          	lui	a1,0x3c0c3
4200ea24:	5c858593          	addi	a1,a1,1480 # 0x3c0c35c8
4200ea28:	8522                	mv	a0,s0
4200ea2a:	fdff2097          	auipc	ra,0xfdff2
4200ea2e:	a82080e7          	jalr	-1406(ra) # 0x400004ac
4200ea32:	84aa                	mv	s1,a0
4200ea34:	3c0c35b7          	lui	a1,0x3c0c3
4200ea38:	5d058593          	addi	a1,a1,1488 # 0x3c0c35d0
4200ea3c:	8522                	mv	a0,s0
4200ea3e:	fdff2097          	auipc	ra,0xfdff2
4200ea42:	a6e080e7          	jalr	-1426(ra) # 0x400004ac
4200ea46:	842a                	mv	s0,a0
4200ea48:	c085                	beqz	s1,0x4200ea68
4200ea4a:	049d                	addi	s1,s1,7
4200ea4c:	02200593          	li	a1,34
4200ea50:	8526                	mv	a0,s1
4200ea52:	fdff2097          	auipc	ra,0xfdff2
4200ea56:	ac2080e7          	jalr	-1342(ra) # 0x40000514
4200ea5a:	c519                	beqz	a0,0x4200ea68
4200ea5c:	409509b3          	sub	s3,a0,s1
4200ea60:	03f00793          	li	a5,63
4200ea64:	0f37f563          	bgeu	a5,s3,0x4200eb4e
4200ea68:	c005                	beqz	s0,0x4200ea88
4200ea6a:	0455                	addi	s0,s0,21
4200ea6c:	02200593          	li	a1,34
4200ea70:	8522                	mv	a0,s0
4200ea72:	fdff2097          	auipc	ra,0xfdff2
4200ea76:	aa2080e7          	jalr	-1374(ra) # 0x40000514
4200ea7a:	c519                	beqz	a0,0x4200ea88
4200ea7c:	408504b3          	sub	s1,a0,s0
4200ea80:	03f00793          	li	a5,63
4200ea84:	1097fb63          	bgeu	a5,s1,0x4200eb9a
4200ea88:	cc02                	sw	zero,24(sp)
4200ea8a:	00010e23          	sb	zero,28(sp)
4200ea8e:	3c0c35b7          	lui	a1,0x3c0c3
4200ea92:	5e858593          	addi	a1,a1,1512 # 0x3c0c35e8
4200ea96:	1008                	addi	a0,sp,32
4200ea98:	fdff2097          	auipc	ra,0xfdff2
4200ea9c:	a14080e7          	jalr	-1516(ra) # 0x400004ac
4200eaa0:	c105                	beqz	a0,0x4200eac0
4200eaa2:	00d50413          	addi	s0,a0,13
4200eaa6:	07d00593          	li	a1,125
4200eaaa:	8522                	mv	a0,s0
4200eaac:	fdff2097          	auipc	ra,0xfdff2
4200eab0:	a68080e7          	jalr	-1432(ra) # 0x40000514
4200eab4:	c511                	beqz	a0,0x4200eac0
4200eab6:	40850633          	sub	a2,a0,s0
4200eaba:	478d                	li	a5,3
4200eabc:	12c7f563          	bgeu	a5,a2,0x4200ebe6
4200eac0:	3c0d77b7          	lui	a5,0x3c0d7
4200eac4:	94478793          	addi	a5,a5,-1724 # 0x3c0d6944
4200eac8:	4390                	lw	a2,0(a5)
4200eaca:	43d4                	lw	a3,4(a5)
4200eacc:	4798                	lw	a4,8(a5)
4200eace:	c432                	sw	a2,8(sp)
4200ead0:	c636                	sw	a3,12(sp)
4200ead2:	c83a                	sw	a4,16(sp)
4200ead4:	00c7d703          	lhu	a4,12(a5)
4200ead8:	00e11a23          	sh	a4,20(sp)
4200eadc:	00e7c783          	lbu	a5,14(a5)
4200eae0:	00f10b23          	sb	a5,22(sp)
4200eae4:	00010ba3          	sb	zero,23(sp)
4200eae8:	3c0c35b7          	lui	a1,0x3c0c3
4200eaec:	40858593          	addi	a1,a1,1032 # 0x3c0c3408
4200eaf0:	854a                	mv	a0,s2
4200eaf2:	6862c0ef          	jal	0x4203b178
4200eaf6:	3c0c3637          	lui	a2,0x3c0c3
4200eafa:	1dc60613          	addi	a2,a2,476 # 0x3c0c31dc
4200eafe:	3c0c35b7          	lui	a1,0x3c0c3
4200eb02:	1e458593          	addi	a1,a1,484 # 0x3c0c31e4
4200eb06:	854a                	mv	a0,s2
4200eb08:	60c2c0ef          	jal	0x4203b114
4200eb0c:	0020                	addi	s0,sp,8
4200eb0e:	8522                	mv	a0,s0
4200eb10:	fdff2097          	auipc	ra,0xfdff2
4200eb14:	998080e7          	jalr	-1640(ra) # 0x400004a8
4200eb18:	862a                	mv	a2,a0
4200eb1a:	85a2                	mv	a1,s0
4200eb1c:	854a                	mv	a0,s2
4200eb1e:	6742c0ef          	jal	0x4203b192
4200eb22:	4501                	li	a0,0
4200eb24:	13c12083          	lw	ra,316(sp)
4200eb28:	13812403          	lw	s0,312(sp)
4200eb2c:	13412483          	lw	s1,308(sp)
4200eb30:	13012903          	lw	s2,304(sp)
4200eb34:	12c12983          	lw	s3,300(sp)
4200eb38:	12812a03          	lw	s4,296(sp)
4200eb3c:	6131                	addi	sp,sp,320
4200eb3e:	8082                	ret
4200eb40:	4601                	li	a2,0
4200eb42:	45a1                	li	a1,8
4200eb44:	854a                	mv	a0,s2
4200eb46:	03d2c0ef          	jal	0x4203b382
4200eb4a:	557d                	li	a0,-1
4200eb4c:	bfe1                	j	0x4200eb24
4200eb4e:	3fcb8a37          	lui	s4,0x3fcb8
4200eb52:	04100613          	li	a2,65
4200eb56:	4581                	li	a1,0
4200eb58:	c22a0513          	addi	a0,s4,-990 # 0x3fcb7c22
4200eb5c:	fdff2097          	auipc	ra,0xfdff2
4200eb60:	92c080e7          	jalr	-1748(ra) # 0x40000488
4200eb64:	864e                	mv	a2,s3
4200eb66:	85a6                	mv	a1,s1
4200eb68:	c22a0513          	addi	a0,s4,-990
4200eb6c:	fdff2097          	auipc	ra,0xfdff2
4200eb70:	930080e7          	jalr	-1744(ra) # 0x4000049c
4200eb74:	3fcb87b7          	lui	a5,0x3fcb8
4200eb78:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200eb7c:	97ce                	add	a5,a5,s3
4200eb7e:	08078323          	sb	zero,134(a5)
4200eb82:	3fcc47b7          	lui	a5,0x3fcc4
4200eb86:	4705                	li	a4,1
4200eb88:	9ee78023          	sb	a4,-1568(a5) # 0x3fcc39e0
4200eb8c:	3fcc47b7          	lui	a5,0x3fcc4
4200eb90:	03200713          	li	a4,50
4200eb94:	9ce7ae23          	sw	a4,-1572(a5) # 0x3fcc39dc
4200eb98:	bdc1                	j	0x4200ea68
4200eb9a:	3fcb89b7          	lui	s3,0x3fcb8
4200eb9e:	04100613          	li	a2,65
4200eba2:	4581                	li	a1,0
4200eba4:	cb898513          	addi	a0,s3,-840 # 0x3fcb7cb8
4200eba8:	fdff2097          	auipc	ra,0xfdff2
4200ebac:	8e0080e7          	jalr	-1824(ra) # 0x40000488
4200ebb0:	8626                	mv	a2,s1
4200ebb2:	85a2                	mv	a1,s0
4200ebb4:	cb898513          	addi	a0,s3,-840
4200ebb8:	fdff2097          	auipc	ra,0xfdff2
4200ebbc:	8e4080e7          	jalr	-1820(ra) # 0x4000049c
4200ebc0:	3fcb87b7          	lui	a5,0x3fcb8
4200ebc4:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200ebc8:	97a6                	add	a5,a5,s1
4200ebca:	10078e23          	sb	zero,284(a5)
4200ebce:	3fcc47b7          	lui	a5,0x3fcc4
4200ebd2:	4705                	li	a4,1
4200ebd4:	9ee78023          	sb	a4,-1568(a5) # 0x3fcc39e0
4200ebd8:	3fcc47b7          	lui	a5,0x3fcc4
4200ebdc:	03200713          	li	a4,50
4200ebe0:	9ce7ae23          	sw	a4,-1572(a5) # 0x3fcc39dc
4200ebe4:	b555                	j	0x4200ea88
4200ebe6:	0824                	addi	s1,sp,24
4200ebe8:	85a2                	mv	a1,s0
4200ebea:	8526                	mv	a0,s1
4200ebec:	fdff2097          	auipc	ra,0xfdff2
4200ebf0:	8b0080e7          	jalr	-1872(ra) # 0x4000049c
4200ebf4:	8526                	mv	a0,s1
4200ebf6:	fdff2097          	auipc	ra,0xfdff2
4200ebfa:	98a080e7          	jalr	-1654(ra) # 0x40000580
4200ebfe:	47a9                	li	a5,10
4200ec00:	eca7e0e3          	bltu	a5,a0,0x4200eac0
4200ec04:	0ff57513          	zext.b	a0,a0
4200ec08:	3fcc47b7          	lui	a5,0x3fcc4
4200ec0c:	a8a7a823          	sw	a0,-1392(a5) # 0x3fcc3a90
4200ec10:	bd45                	j	0x4200eac0
