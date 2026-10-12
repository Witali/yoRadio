
factory-irom.bin:     file format binary


Disassembly of section .data:

42010a06 <.data+0x109e6>:
42010a06:	1141                	addi	sp,sp,-16
42010a08:	c606                	sw	ra,12(sp)
42010a0a:	c422                	sw	s0,8(sp)
42010a0c:	538070ef          	jal	0x42017f44
42010a10:	e51d                	bnez	a0,0x42010a3e
42010a12:	3fcc07b7          	lui	a5,0x3fcc0
42010a16:	fa878793          	addi	a5,a5,-88 # 0x3fcbffa8
42010a1a:	0007a023          	sw	zero,0(a5)
42010a1e:	0007a223          	sw	zero,4(a5)
42010a22:	0007a423          	sw	zero,8(a5)
42010a26:	0007a623          	sw	zero,12(a5)
42010a2a:	0007a823          	sw	zero,16(a5)
42010a2e:	0007aa23          	sw	zero,20(a5)
42010a32:	0007ac23          	sw	zero,24(a5)
42010a36:	0007ae23          	sw	zero,28(a5)
42010a3a:	4401                	li	s0,0
42010a3c:	a029                	j	0x42010a46
42010a3e:	4cc070ef          	jal	0x42017f0a
42010a42:	bfc1                	j	0x42010a12
42010a44:	0405                	addi	s0,s0,1
42010a46:	3c0d77b7          	lui	a5,0x3c0d7
42010a4a:	00141713          	slli	a4,s0,0x1
42010a4e:	9722                	add	a4,a4,s0
42010a50:	070a                	slli	a4,a4,0x2
42010a52:	9b478793          	addi	a5,a5,-1612 # 0x3c0d69b4
42010a56:	97ba                	add	a5,a5,a4
42010a58:	43c8                	lw	a0,4(a5)
42010a5a:	c121                	beqz	a0,0x42010a9a
42010a5c:	3fcb85b7          	lui	a1,0x3fcb8
42010a60:	c6358593          	addi	a1,a1,-925 # 0x3fcb7c63
42010a64:	fdff0097          	auipc	ra,0xfdff0
42010a68:	a3c080e7          	jalr	-1476(ra) # 0x400004a0
42010a6c:	fd61                	bnez	a0,0x42010a44
42010a6e:	3c0d77b7          	lui	a5,0x3c0d7
42010a72:	00141713          	slli	a4,s0,0x1
42010a76:	9722                	add	a4,a4,s0
42010a78:	070a                	slli	a4,a4,0x2
42010a7a:	9b478793          	addi	a5,a5,-1612 # 0x3c0d69b4
42010a7e:	97ba                	add	a5,a5,a4
42010a80:	467d                	li	a2,31
42010a82:	478c                	lw	a1,8(a5)
42010a84:	3fcc0437          	lui	s0,0x3fcc0
42010a88:	fa840513          	addi	a0,s0,-88 # 0x3fcbffa8
42010a8c:	fdff0097          	auipc	ra,0xfdff0
42010a90:	a10080e7          	jalr	-1520(ra) # 0x4000049c
42010a94:	fa844783          	lbu	a5,-88(s0)
42010a98:	e3b9                	bnez	a5,0x42010ade
42010a9a:	3fcc07b7          	lui	a5,0x3fcc0
42010a9e:	fa878793          	addi	a5,a5,-88 # 0x3fcbffa8
42010aa2:	30545737          	lui	a4,0x30545
42010aa6:	d4770713          	addi	a4,a4,-697 # 0x30544d47
42010aaa:	c398                	sw	a4,0(a5)
42010aac:	00545737          	lui	a4,0x545
42010ab0:	34270713          	addi	a4,a4,834 # 0x545342
42010ab4:	c3d8                	sw	a4,4(a5)
42010ab6:	fe37d097          	auipc	ra,0xfe37d
42010aba:	8fe080e7          	jalr	-1794(ra) # 0x4038d3b4
42010abe:	86aa                	mv	a3,a0
42010ac0:	3c0c45b7          	lui	a1,0x3c0c4
42010ac4:	bc458713          	addi	a4,a1,-1084 # 0x3c0c3bc4
42010ac8:	3c0c4637          	lui	a2,0x3c0c4
42010acc:	bc860613          	addi	a2,a2,-1080 # 0x3c0c3bc8
42010ad0:	bc458593          	addi	a1,a1,-1084
42010ad4:	4509                	li	a0,2
42010ad6:	fe37c097          	auipc	ra,0xfe37c
42010ada:	7cc080e7          	jalr	1996(ra) # 0x4038d2a2
42010ade:	4501                	li	a0,0
42010ae0:	3fa070ef          	jal	0x42017eda
42010ae4:	3c0c45b7          	lui	a1,0x3c0c4
42010ae8:	c0858593          	addi	a1,a1,-1016 # 0x3c0c3c08
42010aec:	4501                	li	a0,0
42010aee:	434070ef          	jal	0x42017f22
42010af2:	3fcb87b7          	lui	a5,0x3fcb8
42010af6:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
42010afa:	0867c783          	lbu	a5,134(a5)
42010afe:	c3ad                	beqz	a5,0x42010b60
42010b00:	3fcb85b7          	lui	a1,0x3fcb8
42010b04:	c2258593          	addi	a1,a1,-990 # 0x3fcb7c22
42010b08:	4505                	li	a0,1
42010b0a:	418070ef          	jal	0x42017f22
42010b0e:	3c0c35b7          	lui	a1,0x3c0c3
42010b12:	9ec58593          	addi	a1,a1,-1556 # 0x3c0c29ec
42010b16:	4509                	li	a0,2
42010b18:	40a070ef          	jal	0x42017f22
42010b1c:	42011537          	lui	a0,0x42011
42010b20:	9de50513          	addi	a0,a0,-1570 # 0x420109de
42010b24:	36c070ef          	jal	0x42017e90
42010b28:	3ca070ef          	jal	0x42017ef2
42010b2c:	4605                	li	a2,1
42010b2e:	3fcc05b7          	lui	a1,0x3fcc0
42010b32:	fa858593          	addi	a1,a1,-88 # 0x3fcbffa8
42010b36:	3c0c4537          	lui	a0,0x3c0c4
42010b3a:	c2850513          	addi	a0,a0,-984 # 0x3c0c3c28
42010b3e:	003980ef          	jal	0x420a9340
42010b42:	687990ef          	jal	0x420aa9c8
42010b46:	3fcc47b7          	lui	a5,0x3fcc4
42010b4a:	4705                	li	a4,1
42010b4c:	aae78ca3          	sb	a4,-1351(a5) # 0x3fcc3ab9
42010b50:	3fcc47b7          	lui	a5,0x3fcc4
42010b54:	aa078c23          	sb	zero,-1352(a5) # 0x3fcc3ab8
42010b58:	40b2                	lw	ra,12(sp)
42010b5a:	4422                	lw	s0,8(sp)
42010b5c:	0141                	addi	sp,sp,16
42010b5e:	8082                	ret
42010b60:	3c0c45b7          	lui	a1,0x3c0c4
42010b64:	c1858593          	addi	a1,a1,-1000 # 0x3c0c3c18
42010b68:	4505                	li	a0,1
42010b6a:	3b8070ef          	jal	0x42017f22
42010b6e:	b745                	j	0x42010b0e
