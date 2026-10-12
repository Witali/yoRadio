
factory-irom.bin:     file format binary


Disassembly of section .data:

4200ca30 <.data+0xca10>:
4200ca30:	7149                	addi	sp,sp,-368
4200ca32:	16112623          	sw	ra,364(sp)
4200ca36:	16812423          	sw	s0,360(sp)
4200ca3a:	16912223          	sw	s1,356(sp)
4200ca3e:	17212023          	sw	s2,352(sp)
4200ca42:	fe37c097          	auipc	ra,0xfe37c
4200ca46:	1bc080e7          	jalr	444(ra) # 0x40388bfe
4200ca4a:	3fcc47b7          	lui	a5,0x3fcc4
4200ca4e:	a6a7ae23          	sw	a0,-1412(a5) # 0x3fcc3a7c
4200ca52:	3fcc47b7          	lui	a5,0x3fcc4
4200ca56:	a6078a23          	sb	zero,-1420(a5) # 0x3fcc3a74
4200ca5a:	3ab290ef          	jal	0x42036604
4200ca5e:	20051963          	bnez	a0,0x4200cc70
4200ca62:	0cea20ef          	jal	0x420aeb30
4200ca66:	22051763          	bnez	a0,0x4200cc94
4200ca6a:	010390ef          	jal	0x42045a7a
4200ca6e:	bdc18793          	addi	a5,gp,-1060
4200ca72:	c5be                	sw	a5,200(sp)
4200ca74:	3c0f27b7          	lui	a5,0x3c0f2
4200ca78:	e8c78793          	addi	a5,a5,-372 # 0x3c0f1e8c
4200ca7c:	0007ae83          	lw	t4,0(a5)
4200ca80:	0047ae03          	lw	t3,4(a5)
4200ca84:	0087a303          	lw	t1,8(a5)
4200ca88:	00c7a883          	lw	a7,12(a5)
4200ca8c:	0107a803          	lw	a6,16(a5)
4200ca90:	4bc8                	lw	a0,20(a5)
4200ca92:	4f8c                	lw	a1,24(a5)
4200ca94:	4fd0                	lw	a2,28(a5)
4200ca96:	5394                	lw	a3,32(a5)
4200ca98:	53d8                	lw	a4,36(a5)
4200ca9a:	579c                	lw	a5,40(a5)
4200ca9c:	c7f6                	sw	t4,204(sp)
4200ca9e:	c9f2                	sw	t3,208(sp)
4200caa0:	cb9a                	sw	t1,212(sp)
4200caa2:	cdc6                	sw	a7,216(sp)
4200caa4:	cfc2                	sw	a6,220(sp)
4200caa6:	d1aa                	sw	a0,224(sp)
4200caa8:	d3ae                	sw	a1,228(sp)
4200caaa:	d5b2                	sw	a2,232(sp)
4200caac:	d7b6                	sw	a3,236(sp)
4200caae:	d9ba                	sw	a4,240(sp)
4200cab0:	dbbe                	sw	a5,244(sp)
4200cab2:	47a9                	li	a5,10
4200cab4:	ddbe                	sw	a5,248(sp)
4200cab6:	02000713          	li	a4,32
4200caba:	dfba                	sw	a4,252(sp)
4200cabc:	4785                	li	a5,1
4200cabe:	10f12023          	sw	a5,256(sp)
4200cac2:	10012223          	sw	zero,260(sp)
4200cac6:	10e12423          	sw	a4,264(sp)
4200caca:	10012623          	sw	zero,268(sp)
4200cace:	4695                	li	a3,5
4200cad0:	10d12823          	sw	a3,272(sp)
4200cad4:	10012a23          	sw	zero,276(sp)
4200cad8:	10012c23          	sw	zero,280(sp)
4200cadc:	10f12e23          	sw	a5,284(sp)
4200cae0:	12f12023          	sw	a5,288(sp)
4200cae4:	12012223          	sw	zero,292(sp)
4200cae8:	12f12423          	sw	a5,296(sp)
4200caec:	12f12623          	sw	a5,300(sp)
4200caf0:	4699                	li	a3,6
4200caf2:	12d12823          	sw	a3,304(sp)
4200caf6:	12012a23          	sw	zero,308(sp)
4200cafa:	2f000693          	li	a3,752
4200cafe:	12d12c23          	sw	a3,312(sp)
4200cb02:	12e12e23          	sw	a4,316(sp)
4200cb06:	0a100613          	li	a2,161
4200cb0a:	4681                	li	a3,0
4200cb0c:	14c12023          	sw	a2,320(sp)
4200cb10:	14d12223          	sw	a3,324(sp)
4200cb14:	14f10423          	sb	a5,328(sp)
4200cb18:	4709                	li	a4,2
4200cb1a:	14e12623          	sw	a4,332(sp)
4200cb1e:	14f12823          	sw	a5,336(sp)
4200cb22:	14010a23          	sb	zero,340(sp)
4200cb26:	1f2f47b7          	lui	a5,0x1f2f4
4200cb2a:	f4f78793          	addi	a5,a5,-177 # 0x1f2f3f4f
4200cb2e:	14f12c23          	sw	a5,344(sp)
4200cb32:	01a8                	addi	a0,sp,200
4200cb34:	11b380ef          	jal	0x4204544e
4200cb38:	18051063          	bnez	a0,0x4200ccb8
4200cb3c:	3c0f27b7          	lui	a5,0x3c0f2
4200cb40:	eb87a403          	lw	s0,-328(a5) # 0x3c0f1eb8
4200cb44:	01d8                	addi	a4,sp,196
4200cb46:	4681                	li	a3,0
4200cb48:	4200c637          	lui	a2,0x4200c
4200cb4c:	60260613          	addi	a2,a2,1538 # 0x4200c602
4200cb50:	55fd                	li	a1,-1
4200cb52:	8522                	mv	a0,s0
4200cb54:	763a10ef          	jal	0x420aeab6
4200cb58:	18051263          	bnez	a0,0x4200ccdc
4200cb5c:	3c0f27b7          	lui	a5,0x3c0f2
4200cb60:	8487a483          	lw	s1,-1976(a5) # 0x3c0f1848
4200cb64:	0198                	addi	a4,sp,192
4200cb66:	4681                	li	a3,0
4200cb68:	4200c637          	lui	a2,0x4200c
4200cb6c:	60260613          	addi	a2,a2,1538 # 0x4200c602
4200cb70:	4581                	li	a1,0
4200cb72:	8526                	mv	a0,s1
4200cb74:	743a10ef          	jal	0x420aeab6
4200cb78:	18051463          	bnez	a0,0x4200cd00
4200cb7c:	00810913          	addi	s2,sp,8
4200cb80:	0b800613          	li	a2,184
4200cb84:	4581                	li	a1,0
4200cb86:	854a                	mv	a0,s2
4200cb88:	fdff4097          	auipc	ra,0xfdff4
4200cb8c:	900080e7          	jalr	-1792(ra) # 0x40000488
4200cb90:	6c6177b7          	lui	a5,0x6c617
4200cb94:	d5378793          	addi	a5,a5,-685 # 0x6c616d53
4200cb98:	c43e                	sw	a5,8(sp)
4200cb9a:	565467b7          	lui	a5,0x56546
4200cb9e:	f6c78793          	addi	a5,a5,-148 # 0x56545f6c
4200cba2:	c63e                	sw	a5,12(sp)
4200cba4:	c802                	sw	zero,16(sp)
4200cba6:	ca02                	sw	zero,20(sp)
4200cba8:	cc02                	sw	zero,24(sp)
4200cbaa:	ce02                	sw	zero,28(sp)
4200cbac:	d002                	sw	zero,32(sp)
4200cbae:	d202                	sw	zero,36(sp)
4200cbb0:	3fcb85b7          	lui	a1,0x3fcb8
4200cbb4:	ba058593          	addi	a1,a1,-1120 # 0x3fcb7ba0
4200cbb8:	854a                	mv	a0,s2
4200cbba:	fdff4097          	auipc	ra,0xfdff4
4200cbbe:	8de080e7          	jalr	-1826(ra) # 0x40000498
4200cbc2:	3fcb85b7          	lui	a1,0x3fcb8
4200cbc6:	be158593          	addi	a1,a1,-1055 # 0x3fcb7be1
4200cbca:	1028                	addi	a0,sp,40
4200cbcc:	fdff4097          	auipc	ra,0xfdff4
4200cbd0:	8cc080e7          	jalr	-1844(ra) # 0x40000498
4200cbd4:	02814783          	lbu	a5,40(sp)
4200cbd8:	c399                	beqz	a5,0x4200cbde
4200cbda:	478d                	li	a5,3
4200cbdc:	c13e                	sw	a5,128(sp)
4200cbde:	4505                	li	a0,1
4200cbe0:	0d65c0ef          	jal	0x42068cb6
4200cbe4:	14051063          	bnez	a0,0x4200cd24
4200cbe8:	002c                	addi	a1,sp,8
4200cbea:	4501                	li	a0,0
4200cbec:	6ee5c0ef          	jal	0x420692da
4200cbf0:	14051c63          	bnez	a0,0x4200cd48
4200cbf4:	1125c0ef          	jal	0x42068d06
4200cbf8:	16051a63          	bnez	a0,0x4200cd6c
4200cbfc:	de5ff0ef          	jal	0x4200c9e0
4200cc00:	4cea40ef          	jal	0x420b10ce
4200cc04:	3fcc47b7          	lui	a5,0x3fcc4
4200cc08:	4705                	li	a4,1
4200cc0a:	a6e78a23          	sb	a4,-1420(a5) # 0x3fcc3a74
4200cc0e:	577d                	li	a4,-1
4200cc10:	4681                	li	a3,0
4200cc12:	4601                	li	a2,0
4200cc14:	458d                	li	a1,3
4200cc16:	3fcc47b7          	lui	a5,0x3fcc4
4200cc1a:	a7c7a503          	lw	a0,-1412(a5) # 0x3fcc3a7c
4200cc1e:	fe37c097          	auipc	ra,0xfe37c
4200cc22:	030080e7          	jalr	48(ra) # 0x40388c4e
4200cc26:	00157793          	andi	a5,a0,1
4200cc2a:	16079363          	bnez	a5,0x4200cd90
4200cc2e:	8909                	andi	a0,a0,2
4200cc30:	1e051863          	bnez	a0,0x4200ce20
4200cc34:	fe380097          	auipc	ra,0xfe380
4200cc38:	780080e7          	jalr	1920(ra) # 0x4038d3b4
4200cc3c:	86aa                	mv	a3,a0
4200cc3e:	3c0c35b7          	lui	a1,0x3c0c3
4200cc42:	bd858713          	addi	a4,a1,-1064 # 0x3c0c2bd8
4200cc46:	3c0c3637          	lui	a2,0x3c0c3
4200cc4a:	f3c60613          	addi	a2,a2,-196 # 0x3c0c2f3c
4200cc4e:	bd858593          	addi	a1,a1,-1064
4200cc52:	4505                	li	a0,1
4200cc54:	fe380097          	auipc	ra,0xfe380
4200cc58:	64e080e7          	jalr	1614(ra) # 0x4038d2a2
4200cc5c:	16c12083          	lw	ra,364(sp)
4200cc60:	16812403          	lw	s0,360(sp)
4200cc64:	16412483          	lw	s1,356(sp)
4200cc68:	16012903          	lw	s2,352(sp)
4200cc6c:	6175                	addi	sp,sp,368
4200cc6e:	8082                	ret
4200cc70:	3c0c3737          	lui	a4,0x3c0c3
4200cc74:	d0070713          	addi	a4,a4,-768 # 0x3c0c2d00
4200cc78:	3c0d66b7          	lui	a3,0x3c0d6
4200cc7c:	64c68693          	addi	a3,a3,1612 # 0x3c0d664c
4200cc80:	0a500613          	li	a2,165
4200cc84:	3c0c35b7          	lui	a1,0x3c0c3
4200cc88:	d1458593          	addi	a1,a1,-748 # 0x3c0c2d14
4200cc8c:	fe37a097          	auipc	ra,0xfe37a
4200cc90:	5de080e7          	jalr	1502(ra) # 0x4038726a
4200cc94:	3c0c3737          	lui	a4,0x3c0c3
4200cc98:	d2c70713          	addi	a4,a4,-724 # 0x3c0c2d2c
4200cc9c:	3c0d66b7          	lui	a3,0x3c0d6
4200cca0:	64c68693          	addi	a3,a3,1612 # 0x3c0d664c
4200cca4:	0a700613          	li	a2,167
4200cca8:	3c0c35b7          	lui	a1,0x3c0c3
4200ccac:	d1458593          	addi	a1,a1,-748 # 0x3c0c2d14
4200ccb0:	fe37a097          	auipc	ra,0xfe37a
4200ccb4:	5ba080e7          	jalr	1466(ra) # 0x4038726a
4200ccb8:	3c0c3737          	lui	a4,0x3c0c3
4200ccbc:	d4c70713          	addi	a4,a4,-692 # 0x3c0c2d4c
4200ccc0:	3c0d66b7          	lui	a3,0x3c0d6
4200ccc4:	64c68693          	addi	a3,a3,1612 # 0x3c0d664c
4200ccc8:	0ab00613          	li	a2,171
4200cccc:	3c0c35b7          	lui	a1,0x3c0c3
4200ccd0:	d1458593          	addi	a1,a1,-748 # 0x3c0c2d14
4200ccd4:	fe37a097          	auipc	ra,0xfe37a
4200ccd8:	596080e7          	jalr	1430(ra) # 0x4038726a
4200ccdc:	3c0c3737          	lui	a4,0x3c0c3
4200cce0:	d6070713          	addi	a4,a4,-672 # 0x3c0c2d60
4200cce4:	3c0d66b7          	lui	a3,0x3c0d6
4200cce8:	64c68693          	addi	a3,a3,1612 # 0x3c0d664c
4200ccec:	0af00613          	li	a2,175
4200ccf0:	3c0c35b7          	lui	a1,0x3c0c3
4200ccf4:	d1458593          	addi	a1,a1,-748 # 0x3c0c2d14
4200ccf8:	fe37a097          	auipc	ra,0xfe37a
4200ccfc:	572080e7          	jalr	1394(ra) # 0x4038726a
4200cd00:	3c0c3737          	lui	a4,0x3c0c3
4200cd04:	dcc70713          	addi	a4,a4,-564 # 0x3c0c2dcc
4200cd08:	3c0d66b7          	lui	a3,0x3c0d6
4200cd0c:	64c68693          	addi	a3,a3,1612 # 0x3c0d664c
4200cd10:	0b400613          	li	a2,180
4200cd14:	3c0c35b7          	lui	a1,0x3c0c3
4200cd18:	d1458593          	addi	a1,a1,-748 # 0x3c0c2d14
4200cd1c:	fe37a097          	auipc	ra,0xfe37a
4200cd20:	54e080e7          	jalr	1358(ra) # 0x4038726a
4200cd24:	3c0c3737          	lui	a4,0x3c0c3
4200cd28:	e3870713          	addi	a4,a4,-456 # 0x3c0c2e38
4200cd2c:	3c0d66b7          	lui	a3,0x3c0d6
4200cd30:	64c68693          	addi	a3,a3,1612 # 0x3c0d664c
4200cd34:	0d100613          	li	a2,209
4200cd38:	3c0c35b7          	lui	a1,0x3c0c3
4200cd3c:	d1458593          	addi	a1,a1,-748 # 0x3c0c2d14
4200cd40:	fe37a097          	auipc	ra,0xfe37a
4200cd44:	52a080e7          	jalr	1322(ra) # 0x4038726a
4200cd48:	3c0c3737          	lui	a4,0x3c0c3
4200cd4c:	e5c70713          	addi	a4,a4,-420 # 0x3c0c2e5c
4200cd50:	3c0d66b7          	lui	a3,0x3c0d6
4200cd54:	64c68693          	addi	a3,a3,1612 # 0x3c0d664c
4200cd58:	0d200613          	li	a2,210
4200cd5c:	3c0c35b7          	lui	a1,0x3c0c3
4200cd60:	d1458593          	addi	a1,a1,-748 # 0x3c0c2d14
4200cd64:	fe37a097          	auipc	ra,0xfe37a
4200cd68:	506080e7          	jalr	1286(ra) # 0x4038726a
4200cd6c:	3c0c3737          	lui	a4,0x3c0c3
4200cd70:	e9070713          	addi	a4,a4,-368 # 0x3c0c2e90
4200cd74:	3c0d66b7          	lui	a3,0x3c0d6
4200cd78:	64c68693          	addi	a3,a3,1612 # 0x3c0d664c
4200cd7c:	0d300613          	li	a2,211
4200cd80:	3c0c35b7          	lui	a1,0x3c0c3
4200cd84:	d1458593          	addi	a1,a1,-748 # 0x3c0c2d14
4200cd88:	fe37a097          	auipc	ra,0xfe37a
4200cd8c:	4e2080e7          	jalr	1250(ra) # 0x4038726a
4200cd90:	3fcc47b7          	lui	a5,0x3fcc4
4200cd94:	4709                	li	a4,2
4200cd96:	a6e78a23          	sb	a4,-1420(a5) # 0x3fcc3a74
4200cd9a:	3fcc47b7          	lui	a5,0x3fcc4
4200cd9e:	9e078523          	sb	zero,-1558(a5) # 0x3fcc39ea
4200cda2:	4200c637          	lui	a2,0x4200c
4200cda6:	60260613          	addi	a2,a2,1538 # 0x4200c602
4200cdaa:	4581                	li	a1,0
4200cdac:	8526                	mv	a0,s1
4200cdae:	533a10ef          	jal	0x420aeae0
4200cdb2:	e11d                	bnez	a0,0x4200cdd8
4200cdb4:	4200c637          	lui	a2,0x4200c
4200cdb8:	60260613          	addi	a2,a2,1538 # 0x4200c602
4200cdbc:	55fd                	li	a1,-1
4200cdbe:	8522                	mv	a0,s0
4200cdc0:	521a10ef          	jal	0x420aeae0
4200cdc4:	ed05                	bnez	a0,0x4200cdfc
4200cdc6:	3fcc47b7          	lui	a5,0x3fcc4
4200cdca:	a7c7a503          	lw	a0,-1412(a5) # 0x3fcc3a7c
4200cdce:	fe37c097          	auipc	ra,0xfe37c
4200cdd2:	132080e7          	jalr	306(ra) # 0x40388f00
4200cdd6:	b559                	j	0x4200cc5c
4200cdd8:	3c0c3737          	lui	a4,0x3c0c3
4200cddc:	ea470713          	addi	a4,a4,-348 # 0x3c0c2ea4
4200cde0:	3c0d66b7          	lui	a3,0x3c0d6
4200cde4:	64c68693          	addi	a3,a3,1612 # 0x3c0d664c
4200cde8:	0eb00613          	li	a2,235
4200cdec:	3c0c35b7          	lui	a1,0x3c0c3
4200cdf0:	d1458593          	addi	a1,a1,-748 # 0x3c0c2d14
4200cdf4:	fe37a097          	auipc	ra,0xfe37a
4200cdf8:	476080e7          	jalr	1142(ra) # 0x4038726a
4200cdfc:	3c0c3737          	lui	a4,0x3c0c3
4200ce00:	ef070713          	addi	a4,a4,-272 # 0x3c0c2ef0
4200ce04:	3c0d66b7          	lui	a3,0x3c0d6
4200ce08:	64c68693          	addi	a3,a3,1612 # 0x3c0d664c
4200ce0c:	0ec00613          	li	a2,236
4200ce10:	3c0c35b7          	lui	a1,0x3c0c3
4200ce14:	d1458593          	addi	a1,a1,-748 # 0x3c0c2d14
4200ce18:	fe37a097          	auipc	ra,0xfe37a
4200ce1c:	452080e7          	jalr	1106(ra) # 0x4038726a
4200ce20:	3fcc47b7          	lui	a5,0x3fcc4
4200ce24:	4711                	li	a4,4
4200ce26:	a6e78a23          	sb	a4,-1420(a5) # 0x3fcc3a74
4200ce2a:	3fcb87b7          	lui	a5,0x3fcb8
4200ce2e:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200ce32:	4709                	li	a4,2
4200ce34:	16e7a023          	sw	a4,352(a5)
4200ce38:	bc9fb0ef          	jal	0x42008a00
4200ce3c:	821f30ef          	jal	0x4200065c
