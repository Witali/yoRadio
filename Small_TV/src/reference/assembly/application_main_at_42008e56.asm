
factory-irom.bin:     file format binary


Disassembly of section .data:

42008e56 <.data+0x8e36>:
42008e56:	1101                	addi	sp,sp,-32
42008e58:	ce06                	sw	ra,28(sp)
42008e5a:	06400513          	li	a0,100
42008e5e:	fe381097          	auipc	ra,0xfe381
42008e62:	c90080e7          	jalr	-880(ra) # 0x40389aee
42008e66:	0048                	addi	a0,sp,4
42008e68:	6650e0ef          	jal	0x42017ccc
42008e6c:	858a                	mv	a1,sp
42008e6e:	4501                	li	a0,0
42008e70:	fe389097          	auipc	ra,0xfe389
42008e74:	2d8080e7          	jalr	728(ra) # 0x40392148
42008e78:	c501                	beqz	a0,0x42008e80
42008e7a:	40f2                	lw	ra,28(sp)
42008e7c:	6105                	addi	sp,sp,32
42008e7e:	8082                	ret
42008e80:	fe382097          	auipc	ra,0xfe382
42008e84:	c9e080e7          	jalr	-866(ra) # 0x4038ab1e
42008e88:	4508                	lw	a0,8(a0)
42008e8a:	fdff7097          	auipc	ra,0xfdff7
42008e8e:	706080e7          	jalr	1798(ra) # 0x40000590
42008e92:	6f4360ef          	jal	0x4203f586
42008e96:	6785                	lui	a5,0x1
42008e98:	10d78793          	addi	a5,a5,269 # 0x110d
42008e9c:	02f50a63          	beq	a0,a5,0x42008ed0
42008ea0:	6785                	lui	a5,0x1
42008ea2:	11078793          	addi	a5,a5,272 # 0x1110
42008ea6:	02f50563          	beq	a0,a5,0x42008ed0
42008eaa:	c939                	beqz	a0,0x42008f00
42008eac:	3c0c3737          	lui	a4,0x3c0c3
42008eb0:	ae470713          	addi	a4,a4,-1308 # 0x3c0c2ae4
42008eb4:	3c0d66b7          	lui	a3,0x3c0d6
42008eb8:	24468693          	addi	a3,a3,580 # 0x3c0d6244
42008ebc:	34100613          	li	a2,833
42008ec0:	3c0c35b7          	lui	a1,0x3c0c3
42008ec4:	93458593          	addi	a1,a1,-1740 # 0x3c0c2934
42008ec8:	fe37e097          	auipc	ra,0xfe37e
42008ecc:	3a2080e7          	jalr	930(ra) # 0x4038726a
42008ed0:	069360ef          	jal	0x4203f738
42008ed4:	e501                	bnez	a0,0x42008edc
42008ed6:	6b0360ef          	jal	0x4203f586
42008eda:	bfc1                	j	0x42008eaa
42008edc:	3c0c3737          	lui	a4,0x3c0c3
42008ee0:	ad070713          	addi	a4,a4,-1328 # 0x3c0c2ad0
42008ee4:	3c0d66b7          	lui	a3,0x3c0d6
42008ee8:	24468693          	addi	a3,a3,580 # 0x3c0d6244
42008eec:	33e00613          	li	a2,830
42008ef0:	3c0c35b7          	lui	a1,0x3c0c3
42008ef4:	93458593          	addi	a1,a1,-1740 # 0x3c0c2934
42008ef8:	fe37e097          	auipc	ra,0xfe37e
42008efc:	372080e7          	jalr	882(ra) # 0x4038726a
42008f00:	3fcb87b7          	lui	a5,0x3fcb8
42008f04:	b8478793          	addi	a5,a5,-1148 # 0x3fcb7b84
42008f08:	3c0c3737          	lui	a4,0x3c0c3
42008f0c:	ae870713          	addi	a4,a4,-1304 # 0x3c0c2ae8
42008f10:	430c                	lw	a1,0(a4)
42008f12:	4350                	lw	a2,4(a4)
42008f14:	4714                	lw	a3,8(a4)
42008f16:	c38c                	sw	a1,0(a5)
42008f18:	c3d0                	sw	a2,4(a5)
42008f1a:	c794                	sw	a3,8(a5)
42008f1c:	00c74703          	lbu	a4,12(a4)
42008f20:	00e78623          	sb	a4,12(a5)
42008f24:	301000ef          	jal	0x42009a24
42008f28:	e2aff0ef          	jal	0x42008552
42008f2c:	c8aff0ef          	jal	0x420083b6
42008f30:	4501                	li	a0,0
42008f32:	2d9000ef          	jal	0x42009a0a
42008f36:	e2dff0ef          	jal	0x42008d62
42008f3a:	3fcc47b7          	lui	a5,0x3fcc4
42008f3e:	9e0784a3          	sb	zero,-1559(a5) # 0x3fcc39e9
42008f42:	3fcc47b7          	lui	a5,0x3fcc4
42008f46:	9c078ba3          	sb	zero,-1577(a5) # 0x3fcc39d7
42008f4a:	3fcc47b7          	lui	a5,0x3fcc4
42008f4e:	9c078b23          	sb	zero,-1578(a5) # 0x3fcc39d6
42008f52:	3fcb87b7          	lui	a5,0x3fcb8
42008f56:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
42008f5a:	1607a703          	lw	a4,352(a5)
42008f5e:	4789                	li	a5,2
42008f60:	02f71463          	bne	a4,a5,0x42008f88
42008f64:	3fcc47b7          	lui	a5,0x3fcc4
42008f68:	9e0785a3          	sb	zero,-1557(a5) # 0x3fcc39eb
42008f6c:	3fcc47b7          	lui	a5,0x3fcc4
42008f70:	a4078a23          	sb	zero,-1452(a5) # 0x3fcc3a54
42008f74:	3fcc47b7          	lui	a5,0x3fcc4
42008f78:	a6078a23          	sb	zero,-1420(a5) # 0x3fcc3a74
42008f7c:	3fcc47b7          	lui	a5,0x3fcc4
42008f80:	4705                	li	a4,1
42008f82:	9ee78523          	sb	a4,-1558(a5) # 0x3fcc39ea
42008f86:	a899                	j	0x42008fdc
42008f88:	178030ef          	jal	0x4200c100
42008f8c:	a881                	j	0x42008fdc
42008f8e:	3fcc47b7          	lui	a5,0x3fcc4
42008f92:	4779                	li	a4,30
42008f94:	9ce78b23          	sb	a4,-1578(a5) # 0x3fcc39d6
42008f98:	0cd070ef          	jal	0x42010864
42008f9c:	a89d                	j	0x42009012
42008f9e:	3fcc47b7          	lui	a5,0x3fcc4
42008fa2:	4779                	li	a4,30
42008fa4:	9ce78a23          	sb	a4,-1580(a5) # 0x3fcc39d4
42008fa8:	3c9070ef          	jal	0x42010b70
42008fac:	a019                	j	0x42008fb2
42008fae:	693030ef          	jal	0x4200ce40
42008fb2:	3fcc47b7          	lui	a5,0x3fcc4
42008fb6:	9e87c783          	lbu	a5,-1560(a5) # 0x3fcc39e8
42008fba:	cf81                	beqz	a5,0x42008fd2
42008fbc:	3fcc47b7          	lui	a5,0x3fcc4
42008fc0:	9e47a783          	lw	a5,-1564(a5) # 0x3fcc39e4
42008fc4:	1a078663          	beqz	a5,0x42009170
42008fc8:	17fd                	addi	a5,a5,-1
42008fca:	3fcc4737          	lui	a4,0x3fcc4
42008fce:	9ef72223          	sw	a5,-1564(a4) # 0x3fcc39e4
42008fd2:	4529                	li	a0,10
42008fd4:	fe381097          	auipc	ra,0xfe381
42008fd8:	b1a080e7          	jalr	-1254(ra) # 0x40389aee
42008fdc:	3fcc47b7          	lui	a5,0x3fcc4
42008fe0:	9eb7c783          	lbu	a5,-1557(a5) # 0x3fcc39eb
42008fe4:	c7b9                	beqz	a5,0x42009032
42008fe6:	3fcc47b7          	lui	a5,0x3fcc4
42008fea:	a747c703          	lbu	a4,-1420(a5) # 0x3fcc3a74
42008fee:	4789                	li	a5,2
42008ff0:	faf71fe3          	bne	a4,a5,0x42008fae
42008ff4:	3fcc47b7          	lui	a5,0x3fcc4
42008ff8:	9d77c783          	lbu	a5,-1577(a5) # 0x3fcc39d7
42008ffc:	eb99                	bnez	a5,0x42009012
42008ffe:	3fcc47b7          	lui	a5,0x3fcc4
42009002:	9d67c783          	lbu	a5,-1578(a5) # 0x3fcc39d6
42009006:	d7c1                	beqz	a5,0x42008f8e
42009008:	17fd                	addi	a5,a5,-1
4200900a:	3fcc4737          	lui	a4,0x3fcc4
4200900e:	9cf70b23          	sb	a5,-1578(a4) # 0x3fcc39d6
42009012:	3fcc47b7          	lui	a5,0x3fcc4
42009016:	9d57c783          	lbu	a5,-1579(a5) # 0x3fcc39d5
4200901a:	ffc1                	bnez	a5,0x42008fb2
4200901c:	3fcc47b7          	lui	a5,0x3fcc4
42009020:	9d47c783          	lbu	a5,-1580(a5) # 0x3fcc39d4
42009024:	dfad                	beqz	a5,0x42008f9e
42009026:	17fd                	addi	a5,a5,-1
42009028:	3fcc4737          	lui	a4,0x3fcc4
4200902c:	9cf70a23          	sb	a5,-1580(a4) # 0x3fcc39d4
42009030:	b749                	j	0x42008fb2
42009032:	3fcc47b7          	lui	a5,0x3fcc4
42009036:	9ea7c783          	lbu	a5,-1558(a5) # 0x3fcc39ea
4200903a:	cf89                	beqz	a5,0x42009054
4200903c:	3fcc47b7          	lui	a5,0x3fcc4
42009040:	a747c703          	lbu	a4,-1420(a5) # 0x3fcc3a74
42009044:	4795                	li	a5,5
42009046:	f6f706e3          	beq	a4,a5,0x42008fb2
4200904a:	024040ef          	jal	0x4200d06e
4200904e:	401070ef          	jal	0x42010c4e
42009052:	b785                	j	0x42008fb2
42009054:	3fcc47b7          	lui	a5,0x3fcc4
42009058:	a747c703          	lbu	a4,-1420(a5) # 0x3fcc3a74
4200905c:	4789                	li	a5,2
4200905e:	02f70a63          	beq	a4,a5,0x42009092
42009062:	3fcc47b7          	lui	a5,0x3fcc4
42009066:	9e97c783          	lbu	a5,-1559(a5) # 0x3fcc39e9
4200906a:	cfa1                	beqz	a5,0x420090c2
4200906c:	3fcb87b7          	lui	a5,0x3fcb8
42009070:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
42009074:	1687a783          	lw	a5,360(a5)
42009078:	c7e9                	beqz	a5,0x42009142
4200907a:	4705                	li	a4,1
4200907c:	0ce78663          	beq	a5,a4,0x42009148
42009080:	4709                	li	a4,2
42009082:	0ce78663          	beq	a5,a4,0x4200914e
42009086:	470d                	li	a4,3
42009088:	04e79463          	bne	a5,a4,0x420090d0
4200908c:	524010ef          	jal	0x4200a5b0
42009090:	a081                	j	0x420090d0
42009092:	3fcc47b7          	lui	a5,0x3fcc4
42009096:	9d77c783          	lbu	a5,-1577(a5) # 0x3fcc39d7
4200909a:	f7e1                	bnez	a5,0x42009062
4200909c:	3fcc47b7          	lui	a5,0x3fcc4
420090a0:	9d67c783          	lbu	a5,-1578(a5) # 0x3fcc39d6
420090a4:	c799                	beqz	a5,0x420090b2
420090a6:	17fd                	addi	a5,a5,-1
420090a8:	3fcc4737          	lui	a4,0x3fcc4
420090ac:	9cf70b23          	sb	a5,-1578(a4) # 0x3fcc39d6
420090b0:	bf4d                	j	0x42009062
420090b2:	3fcc47b7          	lui	a5,0x3fcc4
420090b6:	4779                	li	a4,30
420090b8:	9ce78b23          	sb	a4,-1578(a5) # 0x3fcc39d6
420090bc:	7a8070ef          	jal	0x42010864
420090c0:	b74d                	j	0x42009062
420090c2:	3fcc47b7          	lui	a5,0x3fcc4
420090c6:	4705                	li	a4,1
420090c8:	9ee784a3          	sb	a4,-1559(a5) # 0x3fcc39e9
420090cc:	d3dff0ef          	jal	0x42008e08
420090d0:	3fcc47b7          	lui	a5,0x3fcc4
420090d4:	9f37c783          	lbu	a5,-1549(a5) # 0x3fcc39f3
420090d8:	efb5                	bnez	a5,0x42009154
420090da:	297070ef          	jal	0x42010b70
420090de:	3fcc47b7          	lui	a5,0x3fcc4
420090e2:	9e07c783          	lbu	a5,-1568(a5) # 0x3fcc39e0
420090e6:	cb99                	beqz	a5,0x420090fc
420090e8:	3fcc47b7          	lui	a5,0x3fcc4
420090ec:	9dc7a783          	lw	a5,-1572(a5) # 0x3fcc39dc
420090f0:	cbad                	beqz	a5,0x42009162
420090f2:	17fd                	addi	a5,a5,-1
420090f4:	3fcc4737          	lui	a4,0x3fcc4
420090f8:	9cf72e23          	sw	a5,-1572(a4) # 0x3fcc39dc
420090fc:	3fcc07b7          	lui	a5,0x3fcc0
42009100:	fc878793          	addi	a5,a5,-56 # 0x3fcbffc8
42009104:	0087c783          	lbu	a5,8(a5)
42009108:	3fcc4737          	lui	a4,0x3fcc4
4200910c:	9f174703          	lbu	a4,-1551(a4) # 0x3fcc39f1
42009110:	00e78c63          	beq	a5,a4,0x42009128
42009114:	3fcc4737          	lui	a4,0x3fcc4
42009118:	9ef708a3          	sb	a5,-1551(a4) # 0x3fcc39f1
4200911c:	e791                	bnez	a5,0x42009128
4200911e:	3fcc47b7          	lui	a5,0x3fcc4
42009122:	4705                	li	a4,1
42009124:	9ee78923          	sb	a4,-1550(a5) # 0x3fcc39f2
42009128:	3fcc47b7          	lui	a5,0x3fcc4
4200912c:	9f27c783          	lbu	a5,-1550(a5) # 0x3fcc39f2
42009130:	e80781e3          	beqz	a5,0x42008fb2
42009134:	3fcc47b7          	lui	a5,0x3fcc4
42009138:	9e078923          	sb	zero,-1550(a5) # 0x3fcc39f2
4200913c:	b11ff0ef          	jal	0x42008c4c
42009140:	bd8d                	j	0x42008fb2
42009142:	5f6020ef          	jal	0x4200b738
42009146:	b769                	j	0x420090d0
42009148:	445020ef          	jal	0x4200bd8c
4200914c:	b751                	j	0x420090d0
4200914e:	2e9020ef          	jal	0x4200bc36
42009152:	bfbd                	j	0x420090d0
42009154:	3fcc47b7          	lui	a5,0x3fcc4
42009158:	9e0789a3          	sb	zero,-1549(a5) # 0x3fcc39f3
4200915c:	708070ef          	jal	0x42010864
42009160:	bfad                	j	0x420090da
42009162:	3fcc47b7          	lui	a5,0x3fcc4
42009166:	9e078023          	sb	zero,-1568(a5) # 0x3fcc39e0
4200916a:	897ff0ef          	jal	0x42008a00
4200916e:	b779                	j	0x420090fc
42009170:	3fcc47b7          	lui	a5,0x3fcc4
42009174:	9e078423          	sb	zero,-1560(a5) # 0x3fcc39e8
42009178:	ce4f70ef          	jal	0x4200065c
