
factory-irom.bin:     file format binary


Disassembly of section .data:

4200b738 <.data+0xb718>:
4200b738:	1141                	addi	sp,sp,-16
4200b73a:	c606                	sw	ra,12(sp)
4200b73c:	3fcc47b7          	lui	a5,0x3fcc4
4200b740:	9f77c783          	lbu	a5,-1545(a5) # 0x3fcc39f7
4200b744:	10078663          	beqz	a5,0x4200b850
4200b748:	3fcc47b7          	lui	a5,0x3fcc4
4200b74c:	9e078ba3          	sb	zero,-1545(a5) # 0x3fcc39f7
4200b750:	3fcc47b7          	lui	a5,0x3fcc4
4200b754:	9d77c783          	lbu	a5,-1577(a5) # 0x3fcc39d7
4200b758:	cfc9                	beqz	a5,0x4200b7f2
4200b75a:	3fcc47b7          	lui	a5,0x3fcc4
4200b75e:	a257c783          	lbu	a5,-1499(a5) # 0x3fcc3a25
4200b762:	cbcd                	beqz	a5,0x4200b814
4200b764:	4705                	li	a4,1
4200b766:	16e78063          	beq	a5,a4,0x4200b8c6
4200b76a:	4709                	li	a4,2
4200b76c:	16e78a63          	beq	a5,a4,0x4200b8e0
4200b770:	470d                	li	a4,3
4200b772:	18e78463          	beq	a5,a4,0x4200b8fa
4200b776:	4711                	li	a4,4
4200b778:	1ae78663          	beq	a5,a4,0x4200b924
4200b77c:	4715                	li	a4,5
4200b77e:	24e78263          	beq	a5,a4,0x4200b9c2
4200b782:	4719                	li	a4,6
4200b784:	24e78c63          	beq	a5,a4,0x4200b9dc
4200b788:	471d                	li	a4,7
4200b78a:	26e78663          	beq	a5,a4,0x4200b9f6
4200b78e:	4721                	li	a4,8
4200b790:	30e78263          	beq	a5,a4,0x4200ba94
4200b794:	4725                	li	a4,9
4200b796:	08e79b63          	bne	a5,a4,0x4200b82c
4200b79a:	3fcbb7b7          	lui	a5,0x3fcbb
4200b79e:	9b878793          	addi	a5,a5,-1608 # 0x3fcba9b8
4200b7a2:	0007a023          	sw	zero,0(a5)
4200b7a6:	0007a223          	sw	zero,4(a5)
4200b7aa:	0007a423          	sw	zero,8(a5)
4200b7ae:	0007a623          	sw	zero,12(a5)
4200b7b2:	0007a823          	sw	zero,16(a5)
4200b7b6:	3fcc47b7          	lui	a5,0x3fcc4
4200b7ba:	a387a503          	lw	a0,-1480(a5) # 0x3fcc3a38
4200b7be:	a3c7a583          	lw	a1,-1476(a5)
4200b7c2:	3fcb87b7          	lui	a5,0x3fcb8
4200b7c6:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200b7ca:	16c7a703          	lw	a4,364(a5)
4200b7ce:	4785                	li	a5,1
4200b7d0:	2cf70f63          	beq	a4,a5,0x4200baae
4200b7d4:	862a                	mv	a2,a0
4200b7d6:	86ae                	mv	a3,a1
4200b7d8:	3c0c35b7          	lui	a1,0x3c0c3
4200b7dc:	bb458593          	addi	a1,a1,-1100 # 0x3c0c2bb4
4200b7e0:	3fcbb537          	lui	a0,0x3fcbb
4200b7e4:	9b850513          	addi	a0,a0,-1608 # 0x3fcba9b8
4200b7e8:	fdff5097          	auipc	ra,0xfdff5
4200b7ec:	ec0080e7          	jalr	-320(ra) # 0x400006a8
4200b7f0:	a835                	j	0x4200b82c
4200b7f2:	3fcbb7b7          	lui	a5,0x3fcbb
4200b7f6:	9b878793          	addi	a5,a5,-1608 # 0x3fcba9b8
4200b7fa:	3c0c3737          	lui	a4,0x3c0c3
4200b7fe:	b5070713          	addi	a4,a4,-1200 # 0x3c0c2b50
4200b802:	430c                	lw	a1,0(a4)
4200b804:	4350                	lw	a2,4(a4)
4200b806:	4714                	lw	a3,8(a4)
4200b808:	4758                	lw	a4,12(a4)
4200b80a:	c38c                	sw	a1,0(a5)
4200b80c:	c3d0                	sw	a2,4(a5)
4200b80e:	c794                	sw	a3,8(a5)
4200b810:	c7d8                	sw	a4,12(a5)
4200b812:	a82d                	j	0x4200b84c
4200b814:	3fcb85b7          	lui	a1,0x3fcb8
4200b818:	b8458593          	addi	a1,a1,-1148 # 0x3fcb7b84
4200b81c:	3fcbb537          	lui	a0,0x3fcbb
4200b820:	9b850513          	addi	a0,a0,-1608 # 0x3fcba9b8
4200b824:	fdff5097          	auipc	ra,0xfdff5
4200b828:	c74080e7          	jalr	-908(ra) # 0x40000498
4200b82c:	3fcc4737          	lui	a4,0x3fcc4
4200b830:	a2574783          	lbu	a5,-1499(a4) # 0x3fcc3a25
4200b834:	0785                	addi	a5,a5,1
4200b836:	0ff7f793          	zext.b	a5,a5
4200b83a:	a2f702a3          	sb	a5,-1499(a4)
4200b83e:	4725                	li	a4,9
4200b840:	00f77663          	bgeu	a4,a5,0x4200b84c
4200b844:	3fcc47b7          	lui	a5,0x3fcc4
4200b848:	a20782a3          	sb	zero,-1499(a5) # 0x3fcc3a25
4200b84c:	f12ff0ef          	jal	0x4200af5e
4200b850:	3fcc07b7          	lui	a5,0x3fcc0
4200b854:	fc878793          	addi	a5,a5,-56 # 0x3fcbffc8
4200b858:	0067c703          	lbu	a4,6(a5)
4200b85c:	3fcc47b7          	lui	a5,0x3fcc4
4200b860:	a297c783          	lbu	a5,-1495(a5) # 0x3fcc3a29
4200b864:	00f71e63          	bne	a4,a5,0x4200b880
4200b868:	3fcc07b7          	lui	a5,0x3fcc0
4200b86c:	fc878793          	addi	a5,a5,-56 # 0x3fcbffc8
4200b870:	0077c703          	lbu	a4,7(a5)
4200b874:	3fcc47b7          	lui	a5,0x3fcc4
4200b878:	a287c783          	lbu	a5,-1496(a5) # 0x3fcc3a28
4200b87c:	26f70c63          	beq	a4,a5,0x4200baf4
4200b880:	f4cff0ef          	jal	0x4200afcc
4200b884:	3fcc07b7          	lui	a5,0x3fcc0
4200b888:	fc878793          	addi	a5,a5,-56 # 0x3fcbffc8
4200b88c:	0067c683          	lbu	a3,6(a5)
4200b890:	3fcc4737          	lui	a4,0x3fcc4
4200b894:	a2d704a3          	sb	a3,-1495(a4) # 0x3fcc3a29
4200b898:	0077c683          	lbu	a3,7(a5)
4200b89c:	3fcc4737          	lui	a4,0x3fcc4
4200b8a0:	a2d70423          	sb	a3,-1496(a4) # 0x3fcc3a28
4200b8a4:	0087c703          	lbu	a4,8(a5)
4200b8a8:	3fcc47b7          	lui	a5,0x3fcc4
4200b8ac:	a2e783a3          	sb	a4,-1497(a5) # 0x3fcc3a27
4200b8b0:	3fcc47b7          	lui	a5,0x3fcc4
4200b8b4:	9f57c783          	lbu	a5,-1547(a5) # 0x3fcc39f5
4200b8b8:	24079b63          	bnez	a5,0x4200bb0e
4200b8bc:	d11ff0ef          	jal	0x4200b5cc
4200b8c0:	40b2                	lw	ra,12(sp)
4200b8c2:	0141                	addi	sp,sp,16
4200b8c4:	8082                	ret
4200b8c6:	3fcc05b7          	lui	a1,0x3fcc0
4200b8ca:	f9458593          	addi	a1,a1,-108 # 0x3fcbff94
4200b8ce:	3fcbb537          	lui	a0,0x3fcbb
4200b8d2:	9b850513          	addi	a0,a0,-1608 # 0x3fcba9b8
4200b8d6:	fdff5097          	auipc	ra,0xfdff5
4200b8da:	bc2080e7          	jalr	-1086(ra) # 0x40000498
4200b8de:	b7b9                	j	0x4200b82c
4200b8e0:	3fcb85b7          	lui	a1,0x3fcb8
4200b8e4:	b8458593          	addi	a1,a1,-1148 # 0x3fcb7b84
4200b8e8:	3fcbb537          	lui	a0,0x3fcbb
4200b8ec:	9b850513          	addi	a0,a0,-1608 # 0x3fcba9b8
4200b8f0:	fdff5097          	auipc	ra,0xfdff5
4200b8f4:	ba8080e7          	jalr	-1112(ra) # 0x40000498
4200b8f8:	bf15                	j	0x4200b82c
4200b8fa:	3fcbb7b7          	lui	a5,0x3fcbb
4200b8fe:	9b878793          	addi	a5,a5,-1608 # 0x3fcba9b8
4200b902:	3c0c3737          	lui	a4,0x3c0c3
4200b906:	b6070713          	addi	a4,a4,-1184 # 0x3c0c2b60
4200b90a:	4310                	lw	a2,0(a4)
4200b90c:	4354                	lw	a3,4(a4)
4200b90e:	c390                	sw	a2,0(a5)
4200b910:	c3d4                	sw	a3,4(a5)
4200b912:	00875683          	lhu	a3,8(a4)
4200b916:	00d79423          	sh	a3,8(a5)
4200b91a:	00a74703          	lbu	a4,10(a4)
4200b91e:	00e78523          	sb	a4,10(a5)
4200b922:	b729                	j	0x4200b82c
4200b924:	3fcbb7b7          	lui	a5,0x3fcbb
4200b928:	9b878793          	addi	a5,a5,-1608 # 0x3fcba9b8
4200b92c:	0007a023          	sw	zero,0(a5)
4200b930:	0007a223          	sw	zero,4(a5)
4200b934:	0007a423          	sw	zero,8(a5)
4200b938:	0007a623          	sw	zero,12(a5)
4200b93c:	0007a823          	sw	zero,16(a5)
4200b940:	3fcc47b7          	lui	a5,0x3fcc4
4200b944:	a407a503          	lw	a0,-1472(a5) # 0x3fcc3a40
4200b948:	a447a583          	lw	a1,-1468(a5)
4200b94c:	3fcb87b7          	lui	a5,0x3fcb8
4200b950:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200b954:	1747a703          	lw	a4,372(a5)
4200b958:	4785                	li	a5,1
4200b95a:	02f70b63          	beq	a4,a5,0x4200b990
4200b95e:	3c0d67b7          	lui	a5,0x3c0d6
4200b962:	3407a603          	lw	a2,832(a5) # 0x3c0d6340
4200b966:	3447a683          	lw	a3,836(a5)
4200b96a:	fdff5097          	auipc	ra,0xfdff5
4200b96e:	122080e7          	jalr	290(ra) # 0x40000a8c
4200b972:	862a                	mv	a2,a0
4200b974:	86ae                	mv	a3,a1
4200b976:	3c0c35b7          	lui	a1,0x3c0c3
4200b97a:	b7858593          	addi	a1,a1,-1160 # 0x3c0c2b78
4200b97e:	3fcbb537          	lui	a0,0x3fcbb
4200b982:	9b850513          	addi	a0,a0,-1608 # 0x3fcba9b8
4200b986:	fdff5097          	auipc	ra,0xfdff5
4200b98a:	d22080e7          	jalr	-734(ra) # 0x400006a8
4200b98e:	bd79                	j	0x4200b82c
4200b990:	3c0d67b7          	lui	a5,0x3c0d6
4200b994:	3387a603          	lw	a2,824(a5) # 0x3c0d6338
4200b998:	33c7a683          	lw	a3,828(a5)
4200b99c:	fdff5097          	auipc	ra,0xfdff5
4200b9a0:	0f0080e7          	jalr	240(ra) # 0x40000a8c
4200b9a4:	862a                	mv	a2,a0
4200b9a6:	86ae                	mv	a3,a1
4200b9a8:	3c0c35b7          	lui	a1,0x3c0c3
4200b9ac:	b6c58593          	addi	a1,a1,-1172 # 0x3c0c2b6c
4200b9b0:	3fcbb537          	lui	a0,0x3fcbb
4200b9b4:	9b850513          	addi	a0,a0,-1608 # 0x3fcba9b8
4200b9b8:	fdff5097          	auipc	ra,0xfdff5
4200b9bc:	cf0080e7          	jalr	-784(ra) # 0x400006a8
4200b9c0:	b5b5                	j	0x4200b82c
4200b9c2:	3fcb85b7          	lui	a1,0x3fcb8
4200b9c6:	b8458593          	addi	a1,a1,-1148 # 0x3fcb7b84
4200b9ca:	3fcbb537          	lui	a0,0x3fcbb
4200b9ce:	9b850513          	addi	a0,a0,-1608 # 0x3fcba9b8
4200b9d2:	fdff5097          	auipc	ra,0xfdff5
4200b9d6:	ac6080e7          	jalr	-1338(ra) # 0x40000498
4200b9da:	bd89                	j	0x4200b82c
4200b9dc:	3fcc05b7          	lui	a1,0x3fcc0
4200b9e0:	f8058593          	addi	a1,a1,-128 # 0x3fcbff80
4200b9e4:	3fcbb537          	lui	a0,0x3fcbb
4200b9e8:	9b850513          	addi	a0,a0,-1608 # 0x3fcba9b8
4200b9ec:	fdff5097          	auipc	ra,0xfdff5
4200b9f0:	aac080e7          	jalr	-1364(ra) # 0x40000498
4200b9f4:	bd25                	j	0x4200b82c
4200b9f6:	3fcbb7b7          	lui	a5,0x3fcbb
4200b9fa:	9b878793          	addi	a5,a5,-1608 # 0x3fcba9b8
4200b9fe:	0007a023          	sw	zero,0(a5)
4200ba02:	0007a223          	sw	zero,4(a5)
4200ba06:	0007a423          	sw	zero,8(a5)
4200ba0a:	0007a623          	sw	zero,12(a5)
4200ba0e:	0007a823          	sw	zero,16(a5)
4200ba12:	3fcc47b7          	lui	a5,0x3fcc4
4200ba16:	a307a503          	lw	a0,-1488(a5) # 0x3fcc3a30
4200ba1a:	a347a583          	lw	a1,-1484(a5)
4200ba1e:	3fcb87b7          	lui	a5,0x3fcb8
4200ba22:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200ba26:	16c7a703          	lw	a4,364(a5)
4200ba2a:	4785                	li	a5,1
4200ba2c:	02f70163          	beq	a4,a5,0x4200ba4e
4200ba30:	862a                	mv	a2,a0
4200ba32:	86ae                	mv	a3,a1
4200ba34:	3c0c35b7          	lui	a1,0x3c0c3
4200ba38:	b9458593          	addi	a1,a1,-1132 # 0x3c0c2b94
4200ba3c:	3fcbb537          	lui	a0,0x3fcbb
4200ba40:	9b850513          	addi	a0,a0,-1608 # 0x3fcba9b8
4200ba44:	fdff5097          	auipc	ra,0xfdff5
4200ba48:	c64080e7          	jalr	-924(ra) # 0x400006a8
4200ba4c:	b3c5                	j	0x4200b82c
4200ba4e:	3c0d67b7          	lui	a5,0x3c0d6
4200ba52:	3287a603          	lw	a2,808(a5) # 0x3c0d6328
4200ba56:	32c7a683          	lw	a3,812(a5)
4200ba5a:	fdff5097          	auipc	ra,0xfdff5
4200ba5e:	032080e7          	jalr	50(ra) # 0x40000a8c
4200ba62:	3c0d67b7          	lui	a5,0x3c0d6
4200ba66:	3307a603          	lw	a2,816(a5) # 0x3c0d6330
4200ba6a:	3347a683          	lw	a3,820(a5)
4200ba6e:	fdff5097          	auipc	ra,0xfdff5
4200ba72:	faa080e7          	jalr	-86(ra) # 0x40000a18
4200ba76:	862a                	mv	a2,a0
4200ba78:	86ae                	mv	a3,a1
4200ba7a:	3c0c35b7          	lui	a1,0x3c0c3
4200ba7e:	b8458593          	addi	a1,a1,-1148 # 0x3c0c2b84
4200ba82:	3fcbb537          	lui	a0,0x3fcbb
4200ba86:	9b850513          	addi	a0,a0,-1608 # 0x3fcba9b8
4200ba8a:	fdff5097          	auipc	ra,0xfdff5
4200ba8e:	c1e080e7          	jalr	-994(ra) # 0x400006a8
4200ba92:	bb69                	j	0x4200b82c
4200ba94:	3fcb85b7          	lui	a1,0x3fcb8
4200ba98:	b8458593          	addi	a1,a1,-1148 # 0x3fcb7b84
4200ba9c:	3fcbb537          	lui	a0,0x3fcbb
4200baa0:	9b850513          	addi	a0,a0,-1608 # 0x3fcba9b8
4200baa4:	fdff5097          	auipc	ra,0xfdff5
4200baa8:	9f4080e7          	jalr	-1548(ra) # 0x40000498
4200baac:	b341                	j	0x4200b82c
4200baae:	3c0d67b7          	lui	a5,0x3c0d6
4200bab2:	3287a603          	lw	a2,808(a5) # 0x3c0d6328
4200bab6:	32c7a683          	lw	a3,812(a5)
4200baba:	fdff5097          	auipc	ra,0xfdff5
4200babe:	fd2080e7          	jalr	-46(ra) # 0x40000a8c
4200bac2:	3c0d67b7          	lui	a5,0x3c0d6
4200bac6:	3307a603          	lw	a2,816(a5) # 0x3c0d6330
4200baca:	3347a683          	lw	a3,820(a5)
4200bace:	fdff5097          	auipc	ra,0xfdff5
4200bad2:	f4a080e7          	jalr	-182(ra) # 0x40000a18
4200bad6:	862a                	mv	a2,a0
4200bad8:	86ae                	mv	a3,a1
4200bada:	3c0c35b7          	lui	a1,0x3c0c3
4200bade:	ba458593          	addi	a1,a1,-1116 # 0x3c0c2ba4
4200bae2:	3fcbb537          	lui	a0,0x3fcbb
4200bae6:	9b850513          	addi	a0,a0,-1608 # 0x3fcba9b8
4200baea:	fdff5097          	auipc	ra,0xfdff5
4200baee:	bbe080e7          	jalr	-1090(ra) # 0x400006a8
4200baf2:	bb2d                	j	0x4200b82c
4200baf4:	3fcc07b7          	lui	a5,0x3fcc0
4200baf8:	fc878793          	addi	a5,a5,-56 # 0x3fcbffc8
4200bafc:	0087c703          	lbu	a4,8(a5)
4200bb00:	3fcc47b7          	lui	a5,0x3fcc4
4200bb04:	a277c783          	lbu	a5,-1497(a5) # 0x3fcc3a27
4200bb08:	d6f71ce3          	bne	a4,a5,0x4200b880
4200bb0c:	b355                	j	0x4200b8b0
4200bb0e:	3fcc47b7          	lui	a5,0x3fcc4
4200bb12:	9e078aa3          	sb	zero,-1547(a5) # 0x3fcc39f5
4200bb16:	82bff0ef          	jal	0x4200b340
4200bb1a:	be2ff0ef          	jal	0x4200aefc
4200bb1e:	bb79                	j	0x4200b8bc
