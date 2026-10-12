
factory-irom.bin:     file format binary


Disassembly of section .data:

42008d62 <.data+0x8d42>:
42008d62:	715d                	addi	sp,sp,-80
42008d64:	c686                	sw	ra,76(sp)
42008d66:	3fcc47b7          	lui	a5,0x3fcc4
42008d6a:	06400713          	li	a4,100
42008d6e:	9ee7a623          	sw	a4,-1556(a5) # 0x3fcc39ec
42008d72:	d402                	sw	zero,40(sp)
42008d74:	d602                	sw	zero,44(sp)
42008d76:	d802                	sw	zero,48(sp)
42008d78:	da02                	sw	zero,52(sp)
42008d7a:	dc02                	sw	zero,56(sp)
42008d7c:	de02                	sw	zero,60(sp)
42008d7e:	47b5                	li	a5,13
42008d80:	d63e                	sw	a5,44(sp)
42008d82:	3e800793          	li	a5,1000
42008d86:	da3e                	sw	a5,52(sp)
42008d88:	1028                	addi	a0,sp,40
42008d8a:	6a50b0ef          	jal	0x42014c2e
42008d8e:	e90d                	bnez	a0,0x42008dc0
42008d90:	c202                	sw	zero,4(sp)
42008d92:	c402                	sw	zero,8(sp)
42008d94:	c602                	sw	zero,12(sp)
42008d96:	c802                	sw	zero,16(sp)
42008d98:	ca02                	sw	zero,20(sp)
42008d9a:	cc02                	sw	zero,24(sp)
42008d9c:	ce02                	sw	zero,28(sp)
42008d9e:	d002                	sw	zero,32(sp)
42008da0:	d202                	sw	zero,36(sp)
42008da2:	47c9                	li	a5,18
42008da4:	c23e                	sw	a5,4(sp)
42008da6:	0048                	addi	a0,sp,4
42008da8:	35c0c0ef          	jal	0x42015104
42008dac:	ed05                	bnez	a0,0x42008de4
42008dae:	3fcc47b7          	lui	a5,0x3fcc4
42008db2:	9ec7a503          	lw	a0,-1556(a5) # 0x3fcc39ec
42008db6:	e1dff0ef          	jal	0x42008bd2
42008dba:	40b6                	lw	ra,76(sp)
42008dbc:	6161                	addi	sp,sp,80
42008dbe:	8082                	ret
42008dc0:	3c0c3737          	lui	a4,0x3c0c3
42008dc4:	a8c70713          	addi	a4,a4,-1396 # 0x3c0c2a8c
42008dc8:	3c0d66b7          	lui	a3,0x3c0d6
42008dcc:	25068693          	addi	a3,a3,592 # 0x3c0d6250
42008dd0:	2ec00613          	li	a2,748
42008dd4:	3c0c35b7          	lui	a1,0x3c0c3
42008dd8:	93458593          	addi	a1,a1,-1740 # 0x3c0c2934
42008ddc:	fe37e097          	auipc	ra,0xfe37e
42008de0:	48e080e7          	jalr	1166(ra) # 0x4038726a
42008de4:	3c0c3737          	lui	a4,0x3c0c3
42008de8:	aac70713          	addi	a4,a4,-1364 # 0x3c0c2aac
42008dec:	3c0d66b7          	lui	a3,0x3c0d6
42008df0:	25068693          	addi	a3,a3,592 # 0x3c0d6250
42008df4:	2f800613          	li	a2,760
42008df8:	3c0c35b7          	lui	a1,0x3c0c3
42008dfc:	93458593          	addi	a1,a1,-1740 # 0x3c0c2934
42008e00:	fe37e097          	auipc	ra,0xfe37e
42008e04:	46a080e7          	jalr	1130(ra) # 0x4038726a
