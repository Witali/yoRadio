
factory-irom.bin:     file format binary


Disassembly of section .data:

4200ce9e <.data+0xce7e>:
4200ce9e:	7151                	addi	sp,sp,-240
4200cea0:	d786                	sw	ra,236(sp)
4200cea2:	d5a2                	sw	s0,232(sp)
4200cea4:	d3a6                	sw	s1,228(sp)
4200cea6:	3c0c3537          	lui	a0,0x3c0c3
4200ceaa:	cac50513          	addi	a0,a0,-852 # 0x3c0c2cac
4200ceae:	0c3290ef          	jal	0x42036770
4200ceb2:	c119                	beqz	a0,0x4200ceb8
4200ceb4:	0db290ef          	jal	0x4203678e
4200ceb8:	31f380ef          	jal	0x420459d6
4200cebc:	842a                	mv	s0,a0
4200cebe:	cb82                	sw	zero,212(sp)
4200cec0:	cd82                	sw	zero,216(sp)
4200cec2:	cf82                	sw	zero,220(sp)
4200cec4:	3c0c34b7          	lui	s1,0x3c0c3
4200cec8:	ae848513          	addi	a0,s1,-1304 # 0x3c0c2ae8
4200cecc:	4371e0ef          	jal	0x4202bb02
4200ced0:	cbaa                	sw	a0,212(sp)
4200ced2:	3c0c3537          	lui	a0,0x3c0c3
4200ced6:	f5c50513          	addi	a0,a0,-164 # 0x3c0c2f5c
4200ceda:	4291e0ef          	jal	0x4202bb02
4200cede:	cdaa                	sw	a0,216(sp)
4200cee0:	ae848513          	addi	a0,s1,-1304
4200cee4:	41f1e0ef          	jal	0x4202bb02
4200cee8:	cfaa                	sw	a0,220(sp)
4200ceea:	8522                	mv	a0,s0
4200ceec:	2db290ef          	jal	0x420369c6
4200cef0:	e14d                	bnez	a0,0x4200cf92
4200cef2:	4515                	li	a0,5
4200cef4:	fe37d097          	auipc	ra,0xfe37d
4200cef8:	bfa080e7          	jalr	-1030(ra) # 0x40389aee
4200cefc:	09cc                	addi	a1,sp,212
4200cefe:	8522                	mv	a0,s0
4200cf00:	0282a0ef          	jal	0x42036f28
4200cf04:	e955                	bnez	a0,0x4200cfb8
4200cf06:	47de                	lw	a5,212(sp)
4200cf08:	df3e                	sw	a5,188(sp)
4200cf0a:	0c010823          	sb	zero,208(sp)
4200cf0e:	1970                	addi	a2,sp,188
4200cf10:	4581                	li	a1,0
4200cf12:	8522                	mv	a0,s0
4200cf14:	02e2a0ef          	jal	0x42036f42
4200cf18:	e171                	bnez	a0,0x4200cfdc
4200cf1a:	4585                	li	a1,1
4200cf1c:	0ab10da3          	sb	a1,187(sp)
4200cf20:	872e                	mv	a4,a1
4200cf22:	0bb10693          	addi	a3,sp,187
4200cf26:	4619                	li	a2,6
4200cf28:	8522                	mv	a0,s0
4200cf2a:	2c62a0ef          	jal	0x420371f0
4200cf2e:	e969                	bnez	a0,0x4200d000
4200cf30:	8522                	mv	a0,s0
4200cf32:	27b290ef          	jal	0x420369ac
4200cf36:	e57d                	bnez	a0,0x4200d024
4200cf38:	0b800613          	li	a2,184
4200cf3c:	4581                	li	a1,0
4200cf3e:	850a                	mv	a0,sp
4200cf40:	fdff3097          	auipc	ra,0xfdff3
4200cf44:	548080e7          	jalr	1352(ra) # 0x40000488
4200cf48:	6c6177b7          	lui	a5,0x6c617
4200cf4c:	d5378793          	addi	a5,a5,-685 # 0x6c616d53
4200cf50:	c03e                	sw	a5,0(sp)
4200cf52:	565467b7          	lui	a5,0x56546
4200cf56:	f6c78793          	addi	a5,a5,-148 # 0x56545f6c
4200cf5a:	c23e                	sw	a5,4(sp)
4200cf5c:	c402                	sw	zero,8(sp)
4200cf5e:	c602                	sw	zero,12(sp)
4200cf60:	c802                	sw	zero,16(sp)
4200cf62:	ca02                	sw	zero,20(sp)
4200cf64:	cc02                	sw	zero,24(sp)
4200cf66:	ce02                	sw	zero,28(sp)
4200cf68:	47a1                	li	a5,8
4200cf6a:	06f10023          	sb	a5,96(sp)
4200cf6e:	4505                	li	a0,1
4200cf70:	06a100a3          	sb	a0,97(sp)
4200cf74:	478d                	li	a5,3
4200cf76:	d2be                	sw	a5,100(sp)
4200cf78:	06f104a3          	sb	a5,105(sp)
4200cf7c:	d282                	sw	zero,100(sp)
4200cf7e:	858a                	mv	a1,sp
4200cf80:	35a5c0ef          	jal	0x420692da
4200cf84:	e179                	bnez	a0,0x4200d04a
4200cf86:	8522                	mv	a0,s0
4200cf88:	50be                	lw	ra,236(sp)
4200cf8a:	542e                	lw	s0,232(sp)
4200cf8c:	549e                	lw	s1,228(sp)
4200cf8e:	616d                	addi	sp,sp,240
4200cf90:	8082                	ret
4200cf92:	3c0c3737          	lui	a4,0x3c0c3
4200cf96:	f6c70713          	addi	a4,a4,-148 # 0x3c0c2f6c
4200cf9a:	3c0d66b7          	lui	a3,0x3c0d6
4200cf9e:	63868693          	addi	a3,a3,1592 # 0x3c0d6638
4200cfa2:	19700613          	li	a2,407
4200cfa6:	3c0c35b7          	lui	a1,0x3c0c3
4200cfaa:	d1458593          	addi	a1,a1,-748 # 0x3c0c2d14
4200cfae:	fe37a097          	auipc	ra,0xfe37a
4200cfb2:	29a080e7          	jalr	666(ra) # 0x40387248
4200cfb6:	bf35                	j	0x4200cef2
4200cfb8:	3c0c3737          	lui	a4,0x3c0c3
4200cfbc:	f9070713          	addi	a4,a4,-112 # 0x3c0c2f90
4200cfc0:	3c0d66b7          	lui	a3,0x3c0d6
4200cfc4:	63868693          	addi	a3,a3,1592 # 0x3c0d6638
4200cfc8:	19900613          	li	a2,409
4200cfcc:	3c0c35b7          	lui	a1,0x3c0c3
4200cfd0:	d1458593          	addi	a1,a1,-748 # 0x3c0c2d14
4200cfd4:	fe37a097          	auipc	ra,0xfe37a
4200cfd8:	296080e7          	jalr	662(ra) # 0x4038726a
4200cfdc:	3c0c3737          	lui	a4,0x3c0c3
4200cfe0:	fc070713          	addi	a4,a4,-64 # 0x3c0c2fc0
4200cfe4:	3c0d66b7          	lui	a3,0x3c0d6
4200cfe8:	63868693          	addi	a3,a3,1592 # 0x3c0d6638
4200cfec:	1a500613          	li	a2,421
4200cff0:	3c0c35b7          	lui	a1,0x3c0c3
4200cff4:	d1458593          	addi	a1,a1,-748 # 0x3c0c2d14
4200cff8:	fe37a097          	auipc	ra,0xfe37a
4200cffc:	272080e7          	jalr	626(ra) # 0x4038726a
4200d000:	3c0c3737          	lui	a4,0x3c0c3
4200d004:	00470713          	addi	a4,a4,4 # 0x3c0c3004
4200d008:	3c0d66b7          	lui	a3,0x3c0d6
4200d00c:	63868693          	addi	a3,a3,1592 # 0x3c0d6638
4200d010:	1aa00613          	li	a2,426
4200d014:	3c0c35b7          	lui	a1,0x3c0c3
4200d018:	d1458593          	addi	a1,a1,-748 # 0x3c0c2d14
4200d01c:	fe37a097          	auipc	ra,0xfe37a
4200d020:	24e080e7          	jalr	590(ra) # 0x4038726a
4200d024:	3c0c3737          	lui	a4,0x3c0c3
4200d028:	08c70713          	addi	a4,a4,140 # 0x3c0c308c
4200d02c:	3c0d66b7          	lui	a3,0x3c0d6
4200d030:	63868693          	addi	a3,a3,1592 # 0x3c0d6638
4200d034:	1b400613          	li	a2,436
4200d038:	3c0c35b7          	lui	a1,0x3c0c3
4200d03c:	d1458593          	addi	a1,a1,-748 # 0x3c0c2d14
4200d040:	fe37a097          	auipc	ra,0xfe37a
4200d044:	208080e7          	jalr	520(ra) # 0x40387248
4200d048:	bdc5                	j	0x4200cf38
4200d04a:	3c0c3737          	lui	a4,0x3c0c3
4200d04e:	0b070713          	addi	a4,a4,176 # 0x3c0c30b0
4200d052:	3c0d66b7          	lui	a3,0x3c0d6
4200d056:	63868693          	addi	a3,a3,1592 # 0x3c0d6638
4200d05a:	1c800613          	li	a2,456
4200d05e:	3c0c35b7          	lui	a1,0x3c0c3
4200d062:	d1458593          	addi	a1,a1,-748 # 0x3c0c2d14
4200d066:	fe37a097          	auipc	ra,0xfe37a
4200d06a:	204080e7          	jalr	516(ra) # 0x4038726a
