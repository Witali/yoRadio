
factory-irom.bin:     file format binary


Disassembly of section .data:

4200fccc <.data+0xfcac>:
4200fccc:	7179                	addi	sp,sp,-48
4200fcce:	d606                	sw	ra,44(sp)
4200fcd0:	d422                	sw	s0,40(sp)
4200fcd2:	d226                	sw	s1,36(sp)
4200fcd4:	d04a                	sw	s2,32(sp)
4200fcd6:	ce4e                	sw	s3,28(sp)
4200fcd8:	cc52                	sw	s4,24(sp)
4200fcda:	ca56                	sw	s5,20(sp)
4200fcdc:	842a                	mv	s0,a0
4200fcde:	411c                	lw	a5,0(a0)
4200fce0:	4719                	li	a4,6
4200fce2:	34e787e3          	beq	a5,a4,0x42010830
4200fce6:	28f76163          	bltu	a4,a5,0x4200ff68
4200fcea:	4711                	li	a4,4
4200fcec:	2ce78663          	beq	a5,a4,0x4200ffb8
4200fcf0:	4715                	li	a4,5
4200fcf2:	26e79963          	bne	a5,a4,0x4200ff64
4200fcf6:	3fcc47b7          	lui	a5,0x3fcc4
4200fcfa:	aa07a503          	lw	a0,-1376(a5) # 0x3fcc3aa0
4200fcfe:	34050de3          	beqz	a0,0x42010858
4200fd02:	2a3030ef          	jal	0x420137a4
4200fd06:	842a                	mv	s0,a0
4200fd08:	22050e63          	beqz	a0,0x4200ff44
4200fd0c:	3c0c45b7          	lui	a1,0x3c0c4
4200fd10:	9b858593          	addi	a1,a1,-1608 # 0x3c0c39b8
4200fd14:	2cd030ef          	jal	0x420137e0
4200fd18:	84aa                	mv	s1,a0
4200fd1a:	47d030ef          	jal	0x42013996
4200fd1e:	30051d63          	bnez	a0,0x42010038
4200fd22:	3c0c15b7          	lui	a1,0x3c0c1
4200fd26:	6bc58593          	addi	a1,a1,1724 # 0x3c0c16bc
4200fd2a:	8522                	mv	a0,s0
4200fd2c:	2b5030ef          	jal	0x420137e0
4200fd30:	84aa                	mv	s1,a0
4200fd32:	cd69                	beqz	a0,0x4200fe0c
4200fd34:	3c0c45b7          	lui	a1,0x3c0c4
4200fd38:	a1c58593          	addi	a1,a1,-1508 # 0x3c0c3a1c
4200fd3c:	2a5030ef          	jal	0x420137e0
4200fd40:	8aaa                	mv	s5,a0
4200fd42:	3c0c45b7          	lui	a1,0x3c0c4
4200fd46:	a2458593          	addi	a1,a1,-1500 # 0x3c0c3a24
4200fd4a:	8526                	mv	a0,s1
4200fd4c:	295030ef          	jal	0x420137e0
4200fd50:	8a2a                	mv	s4,a0
4200fd52:	3c0c45b7          	lui	a1,0x3c0c4
4200fd56:	a3058593          	addi	a1,a1,-1488 # 0x3c0c3a30
4200fd5a:	8526                	mv	a0,s1
4200fd5c:	285030ef          	jal	0x420137e0
4200fd60:	89aa                	mv	s3,a0
4200fd62:	3c0c45b7          	lui	a1,0x3c0c4
4200fd66:	a3c58593          	addi	a1,a1,-1476 # 0x3c0c3a3c
4200fd6a:	8526                	mv	a0,s1
4200fd6c:	275030ef          	jal	0x420137e0
4200fd70:	892a                	mv	s2,a0
4200fd72:	3c0c45b7          	lui	a1,0x3c0c4
4200fd76:	a4858593          	addi	a1,a1,-1464 # 0x3c0c3a48
4200fd7a:	8526                	mv	a0,s1
4200fd7c:	265030ef          	jal	0x420137e0
4200fd80:	3c0d64b7          	lui	s1,0x3c0d6
4200fd84:	3484a603          	lw	a2,840(s1) # 0x3c0d6348
4200fd88:	34c4a683          	lw	a3,844(s1)
4200fd8c:	018aa503          	lw	a0,24(s5)
4200fd90:	01caa583          	lw	a1,28(s5)
4200fd94:	fdff1097          	auipc	ra,0xfdff1
4200fd98:	d08080e7          	jalr	-760(ra) # 0x40000a9c
4200fd9c:	fdff1097          	auipc	ra,0xfdff1
4200fda0:	c98080e7          	jalr	-872(ra) # 0x40000a34
4200fda4:	3fcc47b7          	lui	a5,0x3fcc4
4200fda8:	a4a7a623          	sw	a0,-1460(a5) # 0x3fcc3a4c
4200fdac:	018a2503          	lw	a0,24(s4)
4200fdb0:	01ca2583          	lw	a1,28(s4)
4200fdb4:	fdff1097          	auipc	ra,0xfdff1
4200fdb8:	c80080e7          	jalr	-896(ra) # 0x40000a34
4200fdbc:	3fcc47b7          	lui	a5,0x3fcc4
4200fdc0:	a4a7a423          	sw	a0,-1464(a5) # 0x3fcc3a48
4200fdc4:	3484a603          	lw	a2,840(s1)
4200fdc8:	34c4a683          	lw	a3,844(s1)
4200fdcc:	01892503          	lw	a0,24(s2)
4200fdd0:	01c92583          	lw	a1,28(s2)
4200fdd4:	fdff1097          	auipc	ra,0xfdff1
4200fdd8:	cc8080e7          	jalr	-824(ra) # 0x40000a9c
4200fddc:	3fcc47b7          	lui	a5,0x3fcc4
4200fde0:	a2a7ac23          	sw	a0,-1480(a5) # 0x3fcc3a38
4200fde4:	a2b7ae23          	sw	a1,-1476(a5)
4200fde8:	3484a603          	lw	a2,840(s1)
4200fdec:	34c4a683          	lw	a3,844(s1)
4200fdf0:	0189a503          	lw	a0,24(s3)
4200fdf4:	01c9a583          	lw	a1,28(s3)
4200fdf8:	fdff1097          	auipc	ra,0xfdff1
4200fdfc:	ca4080e7          	jalr	-860(ra) # 0x40000a9c
4200fe00:	3fcc47b7          	lui	a5,0x3fcc4
4200fe04:	a2a7a823          	sw	a0,-1488(a5) # 0x3fcc3a30
4200fe08:	a2b7aa23          	sw	a1,-1484(a5)
4200fe0c:	3c0c45b7          	lui	a1,0x3c0c4
4200fe10:	a5458593          	addi	a1,a1,-1452 # 0x3c0c3a54
4200fe14:	8522                	mv	a0,s0
4200fe16:	1cb030ef          	jal	0x420137e0
4200fe1a:	84aa                	mv	s1,a0
4200fe1c:	c545                	beqz	a0,0x4200fec4
4200fe1e:	3c0c45b7          	lui	a1,0x3c0c4
4200fe22:	a5c58593          	addi	a1,a1,-1444 # 0x3c0c3a5c
4200fe26:	1bb030ef          	jal	0x420137e0
4200fe2a:	892a                	mv	s2,a0
4200fe2c:	3c0c45b7          	lui	a1,0x3c0c4
4200fe30:	a6458593          	addi	a1,a1,-1436 # 0x3c0c3a64
4200fe34:	8526                	mv	a0,s1
4200fe36:	1ab030ef          	jal	0x420137e0
4200fe3a:	01892603          	lw	a2,24(s2)
4200fe3e:	01c92683          	lw	a3,28(s2)
4200fe42:	3fcc47b7          	lui	a5,0x3fcc4
4200fe46:	a4c7a023          	sw	a2,-1472(a5) # 0x3fcc3a40
4200fe4a:	a4d7a223          	sw	a3,-1468(a5)
4200fe4e:	3fcc07b7          	lui	a5,0x3fcc0
4200fe52:	f9478793          	addi	a5,a5,-108 # 0x3fcbff94
4200fe56:	0007a023          	sw	zero,0(a5)
4200fe5a:	0007a223          	sw	zero,4(a5)
4200fe5e:	0007a423          	sw	zero,8(a5)
4200fe62:	0007a623          	sw	zero,12(a5)
4200fe66:	0007a823          	sw	zero,16(a5)
4200fe6a:	01852903          	lw	s2,24(a0)
4200fe6e:	01c52983          	lw	s3,28(a0)
4200fe72:	3c0d67b7          	lui	a5,0x3c0d6
4200fe76:	3507a603          	lw	a2,848(a5) # 0x3c0d6350
4200fe7a:	3547a683          	lw	a3,852(a5)
4200fe7e:	854a                	mv	a0,s2
4200fe80:	85ce                	mv	a1,s3
4200fe82:	fdff1097          	auipc	ra,0xfdff1
4200fe86:	bea080e7          	jalr	-1046(ra) # 0x40000a6c
4200fe8a:	02055063          	bgez	a0,0x4200feaa
4200fe8e:	3c0d67b7          	lui	a5,0x3c0d6
4200fe92:	3587a603          	lw	a2,856(a5) # 0x3c0d6358
4200fe96:	35c7a683          	lw	a3,860(a5)
4200fe9a:	854a                	mv	a0,s2
4200fe9c:	85ce                	mv	a1,s3
4200fe9e:	fdff1097          	auipc	ra,0xfdff1
4200fea2:	be6080e7          	jalr	-1050(ra) # 0x40000a84
4200fea6:	5c055963          	bgez	a0,0x42010478
4200feaa:	3fcc07b7          	lui	a5,0x3fcc0
4200feae:	f9478793          	addi	a5,a5,-108 # 0x3fcbff94
4200feb2:	74727737          	lui	a4,0x74727
4200feb6:	f4e70713          	addi	a4,a4,-178 # 0x74726f4e
4200feba:	c398                	sw	a4,0(a5)
4200febc:	06800713          	li	a4,104
4200fec0:	00e79223          	sh	a4,4(a5)
4200fec4:	3c0c45b7          	lui	a1,0x3c0c4
4200fec8:	b0c58593          	addi	a1,a1,-1268 # 0x3c0c3b0c
4200fecc:	8522                	mv	a0,s0
4200fece:	113030ef          	jal	0x420137e0
4200fed2:	3c0c45b7          	lui	a1,0x3c0c4
4200fed6:	b1858593          	addi	a1,a1,-1256 # 0x3c0c3b18
4200feda:	8522                	mv	a0,s0
4200fedc:	105030ef          	jal	0x420137e0
4200fee0:	c931                	beqz	a0,0x4200ff34
4200fee2:	4d4c                	lw	a1,28(a0)
4200fee4:	4d08                	lw	a0,24(a0)
4200fee6:	fdff1097          	auipc	ra,0xfdff1
4200feea:	b4a080e7          	jalr	-1206(ra) # 0x40000a30
4200feee:	c42a                	sw	a0,8(sp)
4200fef0:	c62e                	sw	a1,12(sp)
4200fef2:	3c0c45b7          	lui	a1,0x3c0c4
4200fef6:	b1c58593          	addi	a1,a1,-1252 # 0x3c0c3b1c
4200fefa:	8522                	mv	a0,s0
4200fefc:	0e5030ef          	jal	0x420137e0
4200ff00:	cd19                	beqz	a0,0x4200ff1e
4200ff02:	4d4c                	lw	a1,28(a0)
4200ff04:	4d08                	lw	a0,24(a0)
4200ff06:	fdff1097          	auipc	ra,0xfdff1
4200ff0a:	b3a080e7          	jalr	-1222(ra) # 0x40000a40
4200ff0e:	47a2                	lw	a5,8(sp)
4200ff10:	953e                	add	a0,a0,a5
4200ff12:	00f537b3          	sltu	a5,a0,a5
4200ff16:	4732                	lw	a4,12(sp)
4200ff18:	97ba                	add	a5,a5,a4
4200ff1a:	c42a                	sw	a0,8(sp)
4200ff1c:	c63e                	sw	a5,12(sp)
4200ff1e:	0028                	addi	a0,sp,8
4200ff20:	65a9a0ef          	jal	0x420aa57a
4200ff24:	3fcc47b7          	lui	a5,0x3fcc4
4200ff28:	aaa7a223          	sw	a0,-1372(a5) # 0x3fcc3aa4
4200ff2c:	495c                	lw	a5,20(a0)
4200ff2e:	76c78793          	addi	a5,a5,1900
4200ff32:	c95c                	sw	a5,20(a0)
4200ff34:	3fcc47b7          	lui	a5,0x3fcc4
4200ff38:	4705                	li	a4,1
4200ff3a:	9ce78ba3          	sb	a4,-1577(a5) # 0x3fcc39d7
4200ff3e:	8522                	mv	a0,s0
4200ff40:	2ea030ef          	jal	0x4201322a
4200ff44:	3fcc4437          	lui	s0,0x3fcc4
4200ff48:	aa042503          	lw	a0,-1376(s0) # 0x3fcc3aa0
4200ff4c:	fe37e097          	auipc	ra,0xfe37e
4200ff50:	58e080e7          	jalr	1422(ra) # 0x4038e4da
4200ff54:	aa042023          	sw	zero,-1376(s0)
4200ff58:	3fcc47b7          	lui	a5,0x3fcc4
4200ff5c:	a807ae23          	sw	zero,-1380(a5) # 0x3fcc3a9c
4200ff60:	4501                	li	a0,0
4200ff62:	a081                	j	0x4200ffa2
4200ff64:	4501                	li	a0,0
4200ff66:	a835                	j	0x4200ffa2
4200ff68:	471d                	li	a4,7
4200ff6a:	04e79563          	bne	a5,a4,0x4200ffb4
4200ff6e:	3c0c4637          	lui	a2,0x3c0c4
4200ff72:	b2860613          	addi	a2,a2,-1240 # 0x3c0c3b28
4200ff76:	3c0c45b7          	lui	a1,0x3c0c4
4200ff7a:	b3c58593          	addi	a1,a1,-1220 # 0x3c0c3b3c
4200ff7e:	4148                	lw	a0,4(a0)
4200ff80:	4262d0ef          	jal	0x4203d3a6
4200ff84:	3c0c4637          	lui	a2,0x3c0c4
4200ff88:	b4460613          	addi	a2,a2,-1212 # 0x3c0c3b44
4200ff8c:	3c0c45b7          	lui	a1,0x3c0c4
4200ff90:	b5058593          	addi	a1,a1,-1200 # 0x3c0c3b50
4200ff94:	4048                	lw	a0,4(s0)
4200ff96:	4102d0ef          	jal	0x4203d3a6
4200ff9a:	4048                	lw	a0,4(s0)
4200ff9c:	4a22e0ef          	jal	0x4203e43e
4200ffa0:	4501                	li	a0,0
4200ffa2:	50b2                	lw	ra,44(sp)
4200ffa4:	5422                	lw	s0,40(sp)
4200ffa6:	5492                	lw	s1,36(sp)
4200ffa8:	5902                	lw	s2,32(sp)
4200ffaa:	49f2                	lw	s3,28(sp)
4200ffac:	4a62                	lw	s4,24(sp)
4200ffae:	4ad2                	lw	s5,20(sp)
4200ffb0:	6145                	addi	sp,sp,48
4200ffb2:	8082                	ret
4200ffb4:	4501                	li	a0,0
4200ffb6:	b7f5                	j	0x4200ffa2
4200ffb8:	3fcc47b7          	lui	a5,0x3fcc4
4200ffbc:	aa07a783          	lw	a5,-1376(a5) # 0x3fcc3aa0
4200ffc0:	c795                	beqz	a5,0x4200ffec
4200ffc2:	3fcc47b7          	lui	a5,0x3fcc4
4200ffc6:	aa07a503          	lw	a0,-1376(a5) # 0x3fcc3aa0
4200ffca:	3fcc4937          	lui	s2,0x3fcc4
4200ffce:	a9c92483          	lw	s1,-1380(s2) # 0x3fcc3a9c
4200ffd2:	4450                	lw	a2,12(s0)
4200ffd4:	440c                	lw	a1,8(s0)
4200ffd6:	9526                	add	a0,a0,s1
4200ffd8:	fdff0097          	auipc	ra,0xfdff0
4200ffdc:	4b4080e7          	jalr	1204(ra) # 0x4000048c
4200ffe0:	445c                	lw	a5,12(s0)
4200ffe2:	94be                	add	s1,s1,a5
4200ffe4:	a8992e23          	sw	s1,-1380(s2)
4200ffe8:	4501                	li	a0,0
4200ffea:	bf65                	j	0x4200ffa2
4200ffec:	4148                	lw	a0,4(a0)
4200ffee:	62c2e0ef          	jal	0x4203e61a
4200fff2:	fe37e097          	auipc	ra,0xfe37e
4200fff6:	4cc080e7          	jalr	1228(ra) # 0x4038e4be
4200fffa:	3fcc47b7          	lui	a5,0x3fcc4
4200fffe:	aaa7a023          	sw	a0,-1376(a5) # 0x3fcc3aa0
42010002:	3fcc47b7          	lui	a5,0x3fcc4
42010006:	a807ae23          	sw	zero,-1380(a5) # 0x3fcc3a9c
4201000a:	fd45                	bnez	a0,0x4200ffc2
4201000c:	fe37d097          	auipc	ra,0xfe37d
42010010:	3a8080e7          	jalr	936(ra) # 0x4038d3b4
42010014:	86aa                	mv	a3,a0
42010016:	3c0c45b7          	lui	a1,0x3c0c4
4201001a:	97458713          	addi	a4,a1,-1676 # 0x3c0c3974
4201001e:	3c0c4637          	lui	a2,0x3c0c4
42010022:	97c60613          	addi	a2,a2,-1668 # 0x3c0c397c
42010026:	97458593          	addi	a1,a1,-1676
4201002a:	4505                	li	a0,1
4201002c:	fe37d097          	auipc	ra,0xfe37d
42010030:	276080e7          	jalr	630(ra) # 0x4038d2a2
42010034:	557d                	li	a0,-1
42010036:	b7b5                	j	0x4200ffa2
42010038:	4581                	li	a1,0
4201003a:	8526                	mv	a0,s1
4201003c:	78e030ef          	jal	0x420137ca
42010040:	84aa                	mv	s1,a0
42010042:	3c0c15b7          	lui	a1,0x3c0c1
42010046:	6bc58593          	addi	a1,a1,1724 # 0x3c0c16bc
4201004a:	796030ef          	jal	0x420137e0
4201004e:	89aa                	mv	s3,a0
42010050:	3c0c45b7          	lui	a1,0x3c0c4
42010054:	9c058593          	addi	a1,a1,-1600 # 0x3c0c39c0
42010058:	8526                	mv	a0,s1
4201005a:	786030ef          	jal	0x420137e0
4201005e:	892a                	mv	s2,a0
42010060:	3c0c45b7          	lui	a1,0x3c0c4
42010064:	9cc58593          	addi	a1,a1,-1588 # 0x3c0c39cc
42010068:	8526                	mv	a0,s1
4201006a:	776030ef          	jal	0x420137e0
4201006e:	84aa                	mv	s1,a0
42010070:	3fcc07b7          	lui	a5,0x3fcc0
42010074:	f6c78793          	addi	a5,a5,-148 # 0x3fcbff6c
42010078:	0007a023          	sw	zero,0(a5)
4201007c:	0007a223          	sw	zero,4(a5)
42010080:	0007a423          	sw	zero,8(a5)
42010084:	0007a623          	sw	zero,12(a5)
42010088:	0007a823          	sw	zero,16(a5)
4201008c:	0109a983          	lw	s3,16(s3)
42010090:	854e                	mv	a0,s3
42010092:	fdff0097          	auipc	ra,0xfdff0
42010096:	416080e7          	jalr	1046(ra) # 0x400004a8
4201009a:	47bd                	li	a5,15
4201009c:	0aa7ea63          	bltu	a5,a0,0x42010150
420100a0:	85ce                	mv	a1,s3
420100a2:	3fcc0537          	lui	a0,0x3fcc0
420100a6:	f6c50513          	addi	a0,a0,-148 # 0x3fcbff6c
420100aa:	fdff0097          	auipc	ra,0xfdff0
420100ae:	3ee080e7          	jalr	1006(ra) # 0x40000498
420100b2:	3fcc07b7          	lui	a5,0x3fcc0
420100b6:	f8078793          	addi	a5,a5,-128 # 0x3fcbff80
420100ba:	0007a023          	sw	zero,0(a5)
420100be:	0007a223          	sw	zero,4(a5)
420100c2:	0007a423          	sw	zero,8(a5)
420100c6:	0007a623          	sw	zero,12(a5)
420100ca:	0007a823          	sw	zero,16(a5)
420100ce:	01092903          	lw	s2,16(s2)
420100d2:	854a                	mv	a0,s2
420100d4:	fdff0097          	auipc	ra,0xfdff0
420100d8:	3d4080e7          	jalr	980(ra) # 0x400004a8
420100dc:	47bd                	li	a5,15
420100de:	08a7e463          	bltu	a5,a0,0x42010166
420100e2:	85ca                	mv	a1,s2
420100e4:	3fcc0537          	lui	a0,0x3fcc0
420100e8:	f8050513          	addi	a0,a0,-128 # 0x3fcbff80
420100ec:	fdff0097          	auipc	ra,0xfdff0
420100f0:	3ac080e7          	jalr	940(ra) # 0x40000498
420100f4:	3fcc47b7          	lui	a5,0x3fcc4
420100f8:	aac78793          	addi	a5,a5,-1364 # 0x3fcc3aac
420100fc:	0007a023          	sw	zero,0(a5)
42010100:	00078223          	sb	zero,4(a5)
42010104:	4884                	lw	s1,16(s1)
42010106:	8526                	mv	a0,s1
42010108:	fdff0097          	auipc	ra,0xfdff0
4201010c:	3a0080e7          	jalr	928(ra) # 0x400004a8
42010110:	4795                	li	a5,5
42010112:	06a7e563          	bltu	a5,a0,0x4201017c
42010116:	85a6                	mv	a1,s1
42010118:	3fcc4537          	lui	a0,0x3fcc4
4201011c:	aac50513          	addi	a0,a0,-1364 # 0x3fcc3aac
42010120:	fdff0097          	auipc	ra,0xfdff0
42010124:	378080e7          	jalr	888(ra) # 0x40000498
42010128:	3c0c45b7          	lui	a1,0x3c0c4
4201012c:	9d458593          	addi	a1,a1,-1580 # 0x3c0c39d4
42010130:	3fcc4537          	lui	a0,0x3fcc4
42010134:	aac50513          	addi	a0,a0,-1364 # 0x3fcc3aac
42010138:	fdff0097          	auipc	ra,0xfdff0
4201013c:	374080e7          	jalr	884(ra) # 0x400004ac
42010140:	c929                	beqz	a0,0x42010192
42010142:	3fcc47b7          	lui	a5,0x3fcc4
42010146:	00377737          	lui	a4,0x377
4201014a:	aae7a423          	sw	a4,-1368(a5) # 0x3fcc3aa8
4201014e:	bed1                	j	0x4200fd22
42010150:	463d                	li	a2,15
42010152:	85ce                	mv	a1,s3
42010154:	3fcc0537          	lui	a0,0x3fcc0
42010158:	f6c50513          	addi	a0,a0,-148 # 0x3fcbff6c
4201015c:	fdff0097          	auipc	ra,0xfdff0
42010160:	340080e7          	jalr	832(ra) # 0x4000049c
42010164:	b7b9                	j	0x420100b2
42010166:	463d                	li	a2,15
42010168:	85ca                	mv	a1,s2
4201016a:	3fcc0537          	lui	a0,0x3fcc0
4201016e:	f8050513          	addi	a0,a0,-128 # 0x3fcbff80
42010172:	fdff0097          	auipc	ra,0xfdff0
42010176:	32a080e7          	jalr	810(ra) # 0x4000049c
4201017a:	bfad                	j	0x420100f4
4201017c:	4615                	li	a2,5
4201017e:	85a6                	mv	a1,s1
42010180:	3fcc4537          	lui	a0,0x3fcc4
42010184:	aac50513          	addi	a0,a0,-1364 # 0x3fcc3aac
42010188:	fdff0097          	auipc	ra,0xfdff0
4201018c:	314080e7          	jalr	788(ra) # 0x4000049c
42010190:	bf61                	j	0x42010128
42010192:	3c0c45b7          	lui	a1,0x3c0c4
42010196:	9d858593          	addi	a1,a1,-1576 # 0x3c0c39d8
4201019a:	3fcc4537          	lui	a0,0x3fcc4
4201019e:	aac50513          	addi	a0,a0,-1364 # 0x3fcc3aac
420101a2:	fdff0097          	auipc	ra,0xfdff0
420101a6:	30a080e7          	jalr	778(ra) # 0x400004ac
420101aa:	c911                	beqz	a0,0x420101be
420101ac:	3fcc4737          	lui	a4,0x3fcc4
420101b0:	0037b7b7          	lui	a5,0x37b
420101b4:	c0078793          	addi	a5,a5,-1024 # 0x37ac00
420101b8:	aaf72423          	sw	a5,-1368(a4) # 0x3fcc3aa8
420101bc:	b69d                	j	0x4200fd22
420101be:	3c0c45b7          	lui	a1,0x3c0c4
420101c2:	9dc58593          	addi	a1,a1,-1572 # 0x3c0c39dc
420101c6:	3fcc4537          	lui	a0,0x3fcc4
420101ca:	aac50513          	addi	a0,a0,-1364 # 0x3fcc3aac
420101ce:	fdff0097          	auipc	ra,0xfdff0
420101d2:	2de080e7          	jalr	734(ra) # 0x400004ac
420101d6:	c911                	beqz	a0,0x420101ea
420101d8:	3fcc4737          	lui	a4,0x3fcc4
420101dc:	0037f7b7          	lui	a5,0x37f
420101e0:	80078793          	addi	a5,a5,-2048 # 0x37e800
420101e4:	aaf72423          	sw	a5,-1368(a4) # 0x3fcc3aa8
420101e8:	be2d                	j	0x4200fd22
420101ea:	3c0c45b7          	lui	a1,0x3c0c4
420101ee:	9e058593          	addi	a1,a1,-1568 # 0x3c0c39e0
420101f2:	3fcc4537          	lui	a0,0x3fcc4
420101f6:	aac50513          	addi	a0,a0,-1364 # 0x3fcc3aac
420101fa:	fdff0097          	auipc	ra,0xfdff0
420101fe:	2b2080e7          	jalr	690(ra) # 0x400004ac
42010202:	c911                	beqz	a0,0x42010216
42010204:	3fcc4737          	lui	a4,0x3fcc4
42010208:	003827b7          	lui	a5,0x382
4201020c:	40078793          	addi	a5,a5,1024 # 0x382400
42010210:	aaf72423          	sw	a5,-1368(a4) # 0x3fcc3aa8
42010214:	b639                	j	0x4200fd22
42010216:	3c0c45b7          	lui	a1,0x3c0c4
4201021a:	9e458593          	addi	a1,a1,-1564 # 0x3c0c39e4
4201021e:	3fcc4537          	lui	a0,0x3fcc4
42010222:	aac50513          	addi	a0,a0,-1364 # 0x3fcc3aac
42010226:	fdff0097          	auipc	ra,0xfdff0
4201022a:	286080e7          	jalr	646(ra) # 0x400004ac
4201022e:	c901                	beqz	a0,0x4201023e
42010230:	3fcc47b7          	lui	a5,0x3fcc4
42010234:	00386737          	lui	a4,0x386
42010238:	aae7a423          	sw	a4,-1368(a5) # 0x3fcc3aa8
4201023c:	b4dd                	j	0x4200fd22
4201023e:	3c0c45b7          	lui	a1,0x3c0c4
42010242:	9e858593          	addi	a1,a1,-1560 # 0x3c0c39e8
42010246:	3fcc4537          	lui	a0,0x3fcc4
4201024a:	aac50513          	addi	a0,a0,-1364 # 0x3fcc3aac
4201024e:	fdff0097          	auipc	ra,0xfdff0
42010252:	25e080e7          	jalr	606(ra) # 0x400004ac
42010256:	c911                	beqz	a0,0x4201026a
42010258:	3fcc4737          	lui	a4,0x3fcc4
4201025c:	0038a7b7          	lui	a5,0x38a
42010260:	c0078793          	addi	a5,a5,-1024 # 0x389c00
42010264:	aaf72423          	sw	a5,-1368(a4) # 0x3fcc3aa8
42010268:	bc6d                	j	0x4200fd22
4201026a:	3c0c45b7          	lui	a1,0x3c0c4
4201026e:	9ec58593          	addi	a1,a1,-1556 # 0x3c0c39ec
42010272:	3fcc4537          	lui	a0,0x3fcc4
42010276:	aac50513          	addi	a0,a0,-1364 # 0x3fcc3aac
4201027a:	fdff0097          	auipc	ra,0xfdff0
4201027e:	232080e7          	jalr	562(ra) # 0x400004ac
42010282:	c911                	beqz	a0,0x42010296
42010284:	3fcc4737          	lui	a4,0x3fcc4
42010288:	0038e7b7          	lui	a5,0x38e
4201028c:	80078793          	addi	a5,a5,-2048 # 0x38d800
42010290:	aaf72423          	sw	a5,-1368(a4) # 0x3fcc3aa8
42010294:	b479                	j	0x4200fd22
42010296:	3c0c45b7          	lui	a1,0x3c0c4
4201029a:	9f058593          	addi	a1,a1,-1552 # 0x3c0c39f0
4201029e:	3fcc4537          	lui	a0,0x3fcc4
420102a2:	aac50513          	addi	a0,a0,-1364 # 0x3fcc3aac
420102a6:	fdff0097          	auipc	ra,0xfdff0
420102aa:	206080e7          	jalr	518(ra) # 0x400004ac
420102ae:	c911                	beqz	a0,0x420102c2
420102b0:	3fcc4737          	lui	a4,0x3fcc4
420102b4:	003917b7          	lui	a5,0x391
420102b8:	40078793          	addi	a5,a5,1024 # 0x391400
420102bc:	aaf72423          	sw	a5,-1368(a4) # 0x3fcc3aa8
420102c0:	b48d                	j	0x4200fd22
420102c2:	3c0c45b7          	lui	a1,0x3c0c4
420102c6:	9f458593          	addi	a1,a1,-1548 # 0x3c0c39f4
420102ca:	3fcc4537          	lui	a0,0x3fcc4
420102ce:	aac50513          	addi	a0,a0,-1364 # 0x3fcc3aac
420102d2:	fdff0097          	auipc	ra,0xfdff0
420102d6:	1da080e7          	jalr	474(ra) # 0x400004ac
420102da:	c901                	beqz	a0,0x420102ea
420102dc:	3fcc47b7          	lui	a5,0x3fcc4
420102e0:	00395737          	lui	a4,0x395
420102e4:	aae7a423          	sw	a4,-1368(a5) # 0x3fcc3aa8
420102e8:	bc2d                	j	0x4200fd22
420102ea:	3c0c45b7          	lui	a1,0x3c0c4
420102ee:	9f858593          	addi	a1,a1,-1544 # 0x3c0c39f8
420102f2:	3fcc4537          	lui	a0,0x3fcc4
420102f6:	aac50513          	addi	a0,a0,-1364 # 0x3fcc3aac
420102fa:	fdff0097          	auipc	ra,0xfdff0
420102fe:	1b2080e7          	jalr	434(ra) # 0x400004ac
42010302:	c911                	beqz	a0,0x42010316
42010304:	3fcc4737          	lui	a4,0x3fcc4
42010308:	003997b7          	lui	a5,0x399
4201030c:	c0078793          	addi	a5,a5,-1024 # 0x398c00
42010310:	aaf72423          	sw	a5,-1368(a4) # 0x3fcc3aa8
42010314:	b439                	j	0x4200fd22
42010316:	3c0c45b7          	lui	a1,0x3c0c4
4201031a:	9fc58593          	addi	a1,a1,-1540 # 0x3c0c39fc
4201031e:	3fcc4537          	lui	a0,0x3fcc4
42010322:	aac50513          	addi	a0,a0,-1364 # 0x3fcc3aac
42010326:	fdff0097          	auipc	ra,0xfdff0
4201032a:	186080e7          	jalr	390(ra) # 0x400004ac
4201032e:	c911                	beqz	a0,0x42010342
42010330:	3fcc4737          	lui	a4,0x3fcc4
42010334:	0039d7b7          	lui	a5,0x39d
42010338:	80078793          	addi	a5,a5,-2048 # 0x39c800
4201033c:	aaf72423          	sw	a5,-1368(a4) # 0x3fcc3aa8
42010340:	b2cd                	j	0x4200fd22
42010342:	3c0c45b7          	lui	a1,0x3c0c4
42010346:	a0058593          	addi	a1,a1,-1536 # 0x3c0c3a00
4201034a:	3fcc4537          	lui	a0,0x3fcc4
4201034e:	aac50513          	addi	a0,a0,-1364 # 0x3fcc3aac
42010352:	fdff0097          	auipc	ra,0xfdff0
42010356:	15a080e7          	jalr	346(ra) # 0x400004ac
4201035a:	c911                	beqz	a0,0x4201036e
4201035c:	3fcc4737          	lui	a4,0x3fcc4
42010360:	003a07b7          	lui	a5,0x3a0
42010364:	40078793          	addi	a5,a5,1024 # 0x3a0400
42010368:	aaf72423          	sw	a5,-1368(a4) # 0x3fcc3aa8
4201036c:	ba5d                	j	0x4200fd22
4201036e:	3c0c45b7          	lui	a1,0x3c0c4
42010372:	a0458593          	addi	a1,a1,-1532 # 0x3c0c3a04
42010376:	3fcc4537          	lui	a0,0x3fcc4
4201037a:	aac50513          	addi	a0,a0,-1364 # 0x3fcc3aac
4201037e:	fdff0097          	auipc	ra,0xfdff0
42010382:	12e080e7          	jalr	302(ra) # 0x400004ac
42010386:	c901                	beqz	a0,0x42010396
42010388:	3fcc47b7          	lui	a5,0x3fcc4
4201038c:	003a4737          	lui	a4,0x3a4
42010390:	aae7a423          	sw	a4,-1368(a5) # 0x3fcc3aa8
42010394:	b279                	j	0x4200fd22
42010396:	3c0c45b7          	lui	a1,0x3c0c4
4201039a:	a0858593          	addi	a1,a1,-1528 # 0x3c0c3a08
4201039e:	3fcc4537          	lui	a0,0x3fcc4
420103a2:	aac50513          	addi	a0,a0,-1364 # 0x3fcc3aac
420103a6:	fdff0097          	auipc	ra,0xfdff0
420103aa:	106080e7          	jalr	262(ra) # 0x400004ac
420103ae:	c911                	beqz	a0,0x420103c2
420103b0:	3fcc4737          	lui	a4,0x3fcc4
420103b4:	003a87b7          	lui	a5,0x3a8
420103b8:	c0078793          	addi	a5,a5,-1024 # 0x3a7c00
420103bc:	aaf72423          	sw	a5,-1368(a4) # 0x3fcc3aa8
420103c0:	b28d                	j	0x4200fd22
420103c2:	3c0c45b7          	lui	a1,0x3c0c4
420103c6:	a0c58593          	addi	a1,a1,-1524 # 0x3c0c3a0c
420103ca:	3fcc4537          	lui	a0,0x3fcc4
420103ce:	aac50513          	addi	a0,a0,-1364 # 0x3fcc3aac
420103d2:	fdff0097          	auipc	ra,0xfdff0
420103d6:	0da080e7          	jalr	218(ra) # 0x400004ac
420103da:	c911                	beqz	a0,0x420103ee
420103dc:	3fcc4737          	lui	a4,0x3fcc4
420103e0:	003ac7b7          	lui	a5,0x3ac
420103e4:	80078793          	addi	a5,a5,-2048 # 0x3ab800
420103e8:	aaf72423          	sw	a5,-1368(a4) # 0x3fcc3aa8
420103ec:	ba1d                	j	0x4200fd22
420103ee:	3c0c45b7          	lui	a1,0x3c0c4
420103f2:	a1058593          	addi	a1,a1,-1520 # 0x3c0c3a10
420103f6:	3fcc4537          	lui	a0,0x3fcc4
420103fa:	aac50513          	addi	a0,a0,-1364 # 0x3fcc3aac
420103fe:	fdff0097          	auipc	ra,0xfdff0
42010402:	0ae080e7          	jalr	174(ra) # 0x400004ac
42010406:	c911                	beqz	a0,0x4201041a
42010408:	3fcc4737          	lui	a4,0x3fcc4
4201040c:	003af7b7          	lui	a5,0x3af
42010410:	40078793          	addi	a5,a5,1024 # 0x3af400
42010414:	aaf72423          	sw	a5,-1368(a4) # 0x3fcc3aa8
42010418:	b229                	j	0x4200fd22
4201041a:	3c0c45b7          	lui	a1,0x3c0c4
4201041e:	a1458593          	addi	a1,a1,-1516 # 0x3c0c3a14
42010422:	3fcc4537          	lui	a0,0x3fcc4
42010426:	aac50513          	addi	a0,a0,-1364 # 0x3fcc3aac
4201042a:	fdff0097          	auipc	ra,0xfdff0
4201042e:	082080e7          	jalr	130(ra) # 0x400004ac
42010432:	c901                	beqz	a0,0x42010442
42010434:	3fcc47b7          	lui	a5,0x3fcc4
42010438:	003b3737          	lui	a4,0x3b3
4201043c:	aae7a423          	sw	a4,-1368(a5) # 0x3fcc3aa8
42010440:	b0cd                	j	0x4200fd22
42010442:	3c0c45b7          	lui	a1,0x3c0c4
42010446:	a1858593          	addi	a1,a1,-1512 # 0x3c0c3a18
4201044a:	3fcc4537          	lui	a0,0x3fcc4
4201044e:	aac50513          	addi	a0,a0,-1364 # 0x3fcc3aac
42010452:	fdff0097          	auipc	ra,0xfdff0
42010456:	05a080e7          	jalr	90(ra) # 0x400004ac
4201045a:	c911                	beqz	a0,0x4201046e
4201045c:	3fcc4737          	lui	a4,0x3fcc4
42010460:	003b77b7          	lui	a5,0x3b7
42010464:	c0078793          	addi	a5,a5,-1024 # 0x3b6c00
42010468:	aaf72423          	sw	a5,-1368(a4) # 0x3fcc3aa8
4201046c:	b85d                	j	0x4200fd22
4201046e:	3fcc47b7          	lui	a5,0x3fcc4
42010472:	aa07a423          	sw	zero,-1368(a5) # 0x3fcc3aa8
42010476:	b075                	j	0x4200fd22
42010478:	3c0d67b7          	lui	a5,0x3c0d6
4201047c:	3607a603          	lw	a2,864(a5) # 0x3c0d6360
42010480:	3647a683          	lw	a3,868(a5)
42010484:	854a                	mv	a0,s2
42010486:	85ce                	mv	a1,s3
42010488:	fdff0097          	auipc	ra,0xfdff0
4201048c:	5fc080e7          	jalr	1532(ra) # 0x40000a84
42010490:	18054963          	bltz	a0,0x42010622
42010494:	3c0d67b7          	lui	a5,0x3c0d6
42010498:	3687a603          	lw	a2,872(a5) # 0x3c0d6368
4201049c:	36c7a683          	lw	a3,876(a5)
420104a0:	854a                	mv	a0,s2
420104a2:	85ce                	mv	a1,s3
420104a4:	fdff0097          	auipc	ra,0xfdff0
420104a8:	5e0080e7          	jalr	1504(ra) # 0x40000a84
420104ac:	18054c63          	bltz	a0,0x42010644
420104b0:	3c0d67b7          	lui	a5,0x3c0d6
420104b4:	3707a603          	lw	a2,880(a5) # 0x3c0d6370
420104b8:	3747a683          	lw	a3,884(a5)
420104bc:	854a                	mv	a0,s2
420104be:	85ce                	mv	a1,s3
420104c0:	fdff0097          	auipc	ra,0xfdff0
420104c4:	5c4080e7          	jalr	1476(ra) # 0x40000a84
420104c8:	1a054163          	bltz	a0,0x4201066a
420104cc:	3c0d67b7          	lui	a5,0x3c0d6
420104d0:	3787a603          	lw	a2,888(a5) # 0x3c0d6378
420104d4:	37c7a683          	lw	a3,892(a5)
420104d8:	854a                	mv	a0,s2
420104da:	85ce                	mv	a1,s3
420104dc:	fdff0097          	auipc	ra,0xfdff0
420104e0:	5a8080e7          	jalr	1448(ra) # 0x40000a84
420104e4:	1a054b63          	bltz	a0,0x4201069a
420104e8:	3c0d67b7          	lui	a5,0x3c0d6
420104ec:	3807a603          	lw	a2,896(a5) # 0x3c0d6380
420104f0:	3847a683          	lw	a3,900(a5)
420104f4:	854a                	mv	a0,s2
420104f6:	85ce                	mv	a1,s3
420104f8:	fdff0097          	auipc	ra,0xfdff0
420104fc:	58c080e7          	jalr	1420(ra) # 0x40000a84
42010500:	1a054a63          	bltz	a0,0x420106b4
42010504:	3c0d67b7          	lui	a5,0x3c0d6
42010508:	3887a603          	lw	a2,904(a5) # 0x3c0d6388
4201050c:	38c7a683          	lw	a3,908(a5)
42010510:	854a                	mv	a0,s2
42010512:	85ce                	mv	a1,s3
42010514:	fdff0097          	auipc	ra,0xfdff0
42010518:	570080e7          	jalr	1392(ra) # 0x40000a84
4201051c:	1c054463          	bltz	a0,0x420106e4
42010520:	3c0d67b7          	lui	a5,0x3c0d6
42010524:	3907a603          	lw	a2,912(a5) # 0x3c0d6390
42010528:	3947a683          	lw	a3,916(a5)
4201052c:	854a                	mv	a0,s2
4201052e:	85ce                	mv	a1,s3
42010530:	fdff0097          	auipc	ra,0xfdff0
42010534:	554080e7          	jalr	1364(ra) # 0x40000a84
42010538:	1c054863          	bltz	a0,0x42010708
4201053c:	3c0d67b7          	lui	a5,0x3c0d6
42010540:	3987a603          	lw	a2,920(a5) # 0x3c0d6398
42010544:	39c7a683          	lw	a3,924(a5)
42010548:	854a                	mv	a0,s2
4201054a:	85ce                	mv	a1,s3
4201054c:	fdff0097          	auipc	ra,0xfdff0
42010550:	538080e7          	jalr	1336(ra) # 0x40000a84
42010554:	1c054c63          	bltz	a0,0x4201072c
42010558:	3c0d67b7          	lui	a5,0x3c0d6
4201055c:	3a07a603          	lw	a2,928(a5) # 0x3c0d63a0
42010560:	3a47a683          	lw	a3,932(a5)
42010564:	854a                	mv	a0,s2
42010566:	85ce                	mv	a1,s3
42010568:	fdff0097          	auipc	ra,0xfdff0
4201056c:	51c080e7          	jalr	1308(ra) # 0x40000a84
42010570:	1c054d63          	bltz	a0,0x4201074a
42010574:	3c0d67b7          	lui	a5,0x3c0d6
42010578:	3a87a603          	lw	a2,936(a5) # 0x3c0d63a8
4201057c:	3ac7a683          	lw	a3,940(a5)
42010580:	854a                	mv	a0,s2
42010582:	85ce                	mv	a1,s3
42010584:	fdff0097          	auipc	ra,0xfdff0
42010588:	500080e7          	jalr	1280(ra) # 0x40000a84
4201058c:	1e054163          	bltz	a0,0x4201076e
42010590:	3c0d67b7          	lui	a5,0x3c0d6
42010594:	3b07a603          	lw	a2,944(a5) # 0x3c0d63b0
42010598:	3b47a683          	lw	a3,948(a5)
4201059c:	854a                	mv	a0,s2
4201059e:	85ce                	mv	a1,s3
420105a0:	fdff0097          	auipc	ra,0xfdff0
420105a4:	4e4080e7          	jalr	1252(ra) # 0x40000a84
420105a8:	1e054563          	bltz	a0,0x42010792
420105ac:	3c0d67b7          	lui	a5,0x3c0d6
420105b0:	3b87a603          	lw	a2,952(a5) # 0x3c0d63b8
420105b4:	3bc7a683          	lw	a3,956(a5)
420105b8:	854a                	mv	a0,s2
420105ba:	85ce                	mv	a1,s3
420105bc:	fdff0097          	auipc	ra,0xfdff0
420105c0:	4c8080e7          	jalr	1224(ra) # 0x40000a84
420105c4:	1e054f63          	bltz	a0,0x420107c2
420105c8:	3c0d67b7          	lui	a5,0x3c0d6
420105cc:	3c07a603          	lw	a2,960(a5) # 0x3c0d63c0
420105d0:	3c47a683          	lw	a3,964(a5)
420105d4:	854a                	mv	a0,s2
420105d6:	85ce                	mv	a1,s3
420105d8:	fdff0097          	auipc	ra,0xfdff0
420105dc:	4ac080e7          	jalr	1196(ra) # 0x40000a84
420105e0:	1e054e63          	bltz	a0,0x420107dc
420105e4:	3c0d67b7          	lui	a5,0x3c0d6
420105e8:	3c87a603          	lw	a2,968(a5) # 0x3c0d63c8
420105ec:	3cc7a683          	lw	a3,972(a5)
420105f0:	854a                	mv	a0,s2
420105f2:	85ce                	mv	a1,s3
420105f4:	fdff0097          	auipc	ra,0xfdff0
420105f8:	490080e7          	jalr	1168(ra) # 0x40000a84
420105fc:	20055863          	bgez	a0,0x4201080c
42010600:	3fcc07b7          	lui	a5,0x3fcc0
42010604:	f9478793          	addi	a5,a5,-108 # 0x3fcbff94
42010608:	3c0c4737          	lui	a4,0x3c0c4
4201060c:	af070713          	addi	a4,a4,-1296 # 0x3c0c3af0
42010610:	4310                	lw	a2,0(a4)
42010612:	4354                	lw	a3,4(a4)
42010614:	c390                	sw	a2,0(a5)
42010616:	c3d4                	sw	a3,4(a5)
42010618:	00875703          	lhu	a4,8(a4)
4201061c:	00e79423          	sh	a4,8(a5)
42010620:	b055                	j	0x4200fec4
42010622:	3fcc07b7          	lui	a5,0x3fcc0
42010626:	f9478793          	addi	a5,a5,-108 # 0x3fcbff94
4201062a:	3c0c4737          	lui	a4,0x3c0c4
4201062e:	a6870713          	addi	a4,a4,-1432 # 0x3c0c3a68
42010632:	430c                	lw	a1,0(a4)
42010634:	4350                	lw	a2,4(a4)
42010636:	4714                	lw	a3,8(a4)
42010638:	4758                	lw	a4,12(a4)
4201063a:	c38c                	sw	a1,0(a5)
4201063c:	c3d0                	sw	a2,4(a5)
4201063e:	c794                	sw	a3,8(a5)
42010640:	c7d8                	sw	a4,12(a5)
42010642:	b049                	j	0x4200fec4
42010644:	3fcc07b7          	lui	a5,0x3fcc0
42010648:	f9478793          	addi	a5,a5,-108 # 0x3fcbff94
4201064c:	74727737          	lui	a4,0x74727
42010650:	f4e70713          	addi	a4,a4,-178 # 0x74726f4e
42010654:	c398                	sw	a4,0(a5)
42010656:	73616737          	lui	a4,0x73616
4201065a:	56870713          	addi	a4,a4,1384 # 0x73616568
4201065e:	c3d8                	sw	a4,4(a5)
42010660:	07400713          	li	a4,116
42010664:	00e79423          	sh	a4,8(a5)
42010668:	b8b1                	j	0x4200fec4
4201066a:	3fcc07b7          	lui	a5,0x3fcc0
4201066e:	f9478793          	addi	a5,a5,-108 # 0x3fcbff94
42010672:	3c0c4737          	lui	a4,0x3c0c4
42010676:	a7870713          	addi	a4,a4,-1416 # 0x3c0c3a78
4201067a:	430c                	lw	a1,0(a4)
4201067c:	4350                	lw	a2,4(a4)
4201067e:	4714                	lw	a3,8(a4)
42010680:	c38c                	sw	a1,0(a5)
42010682:	c3d0                	sw	a2,4(a5)
42010684:	c794                	sw	a3,8(a5)
42010686:	00c75683          	lhu	a3,12(a4)
4201068a:	00d79623          	sh	a3,12(a5)
4201068e:	00e74703          	lbu	a4,14(a4)
42010692:	00e78723          	sb	a4,14(a5)
42010696:	82fff06f          	j	0x4200fec4
4201069a:	3fcc07b7          	lui	a5,0x3fcc0
4201069e:	f9478793          	addi	a5,a5,-108 # 0x3fcbff94
420106a2:	74736737          	lui	a4,0x74736
420106a6:	14570713          	addi	a4,a4,325 # 0x74736145
420106aa:	c398                	sw	a4,0(a5)
420106ac:	00078223          	sb	zero,4(a5)
420106b0:	815ff06f          	j	0x4200fec4
420106b4:	3fcc07b7          	lui	a5,0x3fcc0
420106b8:	f9478793          	addi	a5,a5,-108 # 0x3fcbff94
420106bc:	3c0c4737          	lui	a4,0x3c0c4
420106c0:	a8870713          	addi	a4,a4,-1400 # 0x3c0c3a88
420106c4:	430c                	lw	a1,0(a4)
420106c6:	4350                	lw	a2,4(a4)
420106c8:	4714                	lw	a3,8(a4)
420106ca:	c38c                	sw	a1,0(a5)
420106cc:	c3d0                	sw	a2,4(a5)
420106ce:	c794                	sw	a3,8(a5)
420106d0:	00c75683          	lhu	a3,12(a4)
420106d4:	00d79623          	sh	a3,12(a5)
420106d8:	00e74703          	lbu	a4,14(a4)
420106dc:	00e78723          	sb	a4,14(a5)
420106e0:	fe4ff06f          	j	0x4200fec4
420106e4:	3fcc07b7          	lui	a5,0x3fcc0
420106e8:	f9478793          	addi	a5,a5,-108 # 0x3fcbff94
420106ec:	3c0c4737          	lui	a4,0x3c0c4
420106f0:	a9870713          	addi	a4,a4,-1384 # 0x3c0c3a98
420106f4:	4310                	lw	a2,0(a4)
420106f6:	4354                	lw	a3,4(a4)
420106f8:	c390                	sw	a2,0(a5)
420106fa:	c3d4                	sw	a3,4(a5)
420106fc:	00875703          	lhu	a4,8(a4)
42010700:	00e79423          	sh	a4,8(a5)
42010704:	fc0ff06f          	j	0x4200fec4
42010708:	3fcc07b7          	lui	a5,0x3fcc0
4201070c:	f9478793          	addi	a5,a5,-108 # 0x3fcbff94
42010710:	3c0c4737          	lui	a4,0x3c0c4
42010714:	aa470713          	addi	a4,a4,-1372 # 0x3c0c3aa4
42010718:	430c                	lw	a1,0(a4)
4201071a:	4350                	lw	a2,4(a4)
4201071c:	4714                	lw	a3,8(a4)
4201071e:	4758                	lw	a4,12(a4)
42010720:	c38c                	sw	a1,0(a5)
42010722:	c3d0                	sw	a2,4(a5)
42010724:	c794                	sw	a3,8(a5)
42010726:	c7d8                	sw	a4,12(a5)
42010728:	f9cff06f          	j	0x4200fec4
4201072c:	3fcc07b7          	lui	a5,0x3fcc0
42010730:	f9478793          	addi	a5,a5,-108 # 0x3fcbff94
42010734:	74757737          	lui	a4,0x74757
42010738:	f5370713          	addi	a4,a4,-173 # 0x74756f53
4201073c:	c398                	sw	a4,0(a5)
4201073e:	06800713          	li	a4,104
42010742:	00e79223          	sh	a4,4(a5)
42010746:	f7eff06f          	j	0x4200fec4
4201074a:	3fcc07b7          	lui	a5,0x3fcc0
4201074e:	f9478793          	addi	a5,a5,-108 # 0x3fcbff94
42010752:	3c0c4737          	lui	a4,0x3c0c4
42010756:	ab470713          	addi	a4,a4,-1356 # 0x3c0c3ab4
4201075a:	430c                	lw	a1,0(a4)
4201075c:	4350                	lw	a2,4(a4)
4201075e:	4714                	lw	a3,8(a4)
42010760:	4758                	lw	a4,12(a4)
42010762:	c38c                	sw	a1,0(a5)
42010764:	c3d0                	sw	a2,4(a5)
42010766:	c794                	sw	a3,8(a5)
42010768:	c7d8                	sw	a4,12(a5)
4201076a:	f5aff06f          	j	0x4200fec4
4201076e:	3fcc07b7          	lui	a5,0x3fcc0
42010772:	f9478793          	addi	a5,a5,-108 # 0x3fcbff94
42010776:	3c0c4737          	lui	a4,0x3c0c4
4201077a:	ac470713          	addi	a4,a4,-1340 # 0x3c0c3ac4
4201077e:	4310                	lw	a2,0(a4)
42010780:	4354                	lw	a3,4(a4)
42010782:	c390                	sw	a2,0(a5)
42010784:	c3d4                	sw	a3,4(a5)
42010786:	00875703          	lhu	a4,8(a4)
4201078a:	00e79423          	sh	a4,8(a5)
4201078e:	f36ff06f          	j	0x4200fec4
42010792:	3fcc07b7          	lui	a5,0x3fcc0
42010796:	f9478793          	addi	a5,a5,-108 # 0x3fcbff94
4201079a:	3c0c4737          	lui	a4,0x3c0c4
4201079e:	ad070713          	addi	a4,a4,-1328 # 0x3c0c3ad0
420107a2:	430c                	lw	a1,0(a4)
420107a4:	4350                	lw	a2,4(a4)
420107a6:	4714                	lw	a3,8(a4)
420107a8:	c38c                	sw	a1,0(a5)
420107aa:	c3d0                	sw	a2,4(a5)
420107ac:	c794                	sw	a3,8(a5)
420107ae:	00c75683          	lhu	a3,12(a4)
420107b2:	00d79623          	sh	a3,12(a5)
420107b6:	00e74703          	lbu	a4,14(a4)
420107ba:	00e78723          	sb	a4,14(a5)
420107be:	f06ff06f          	j	0x4200fec4
420107c2:	3fcc07b7          	lui	a5,0x3fcc0
420107c6:	f9478793          	addi	a5,a5,-108 # 0x3fcbff94
420107ca:	74736737          	lui	a4,0x74736
420107ce:	55770713          	addi	a4,a4,1367 # 0x74736557
420107d2:	c398                	sw	a4,0(a5)
420107d4:	00078223          	sb	zero,4(a5)
420107d8:	eecff06f          	j	0x4200fec4
420107dc:	3fcc07b7          	lui	a5,0x3fcc0
420107e0:	f9478793          	addi	a5,a5,-108 # 0x3fcbff94
420107e4:	3c0c4737          	lui	a4,0x3c0c4
420107e8:	ae070713          	addi	a4,a4,-1312 # 0x3c0c3ae0
420107ec:	430c                	lw	a1,0(a4)
420107ee:	4350                	lw	a2,4(a4)
420107f0:	4714                	lw	a3,8(a4)
420107f2:	c38c                	sw	a1,0(a5)
420107f4:	c3d0                	sw	a2,4(a5)
420107f6:	c794                	sw	a3,8(a5)
420107f8:	00c75683          	lhu	a3,12(a4)
420107fc:	00d79623          	sh	a3,12(a5)
42010800:	00e74703          	lbu	a4,14(a4)
42010804:	00e78723          	sb	a4,14(a5)
42010808:	ebcff06f          	j	0x4200fec4
4201080c:	3fcc07b7          	lui	a5,0x3fcc0
42010810:	f9478793          	addi	a5,a5,-108 # 0x3fcbff94
42010814:	3c0c4737          	lui	a4,0x3c0c4
42010818:	afc70713          	addi	a4,a4,-1284 # 0x3c0c3afc
4201081c:	430c                	lw	a1,0(a4)
4201081e:	4350                	lw	a2,4(a4)
42010820:	4714                	lw	a3,8(a4)
42010822:	4758                	lw	a4,12(a4)
42010824:	c38c                	sw	a1,0(a5)
42010826:	c3d0                	sw	a2,4(a5)
42010828:	c794                	sw	a3,8(a5)
4201082a:	c7d8                	sw	a4,12(a5)
4201082c:	e98ff06f          	j	0x4200fec4
42010830:	3fcc47b7          	lui	a5,0x3fcc4
42010834:	aa07a503          	lw	a0,-1376(a5) # 0x3fcc3aa0
42010838:	c11d                	beqz	a0,0x4201085e
4201083a:	fe37e097          	auipc	ra,0xfe37e
4201083e:	ca0080e7          	jalr	-864(ra) # 0x4038e4da
42010842:	3fcc47b7          	lui	a5,0x3fcc4
42010846:	aa07a023          	sw	zero,-1376(a5) # 0x3fcc3aa0
4201084a:	3fcc47b7          	lui	a5,0x3fcc4
4201084e:	a807ae23          	sw	zero,-1380(a5) # 0x3fcc3a9c
42010852:	4501                	li	a0,0
42010854:	f4eff06f          	j	0x4200ffa2
42010858:	4501                	li	a0,0
4201085a:	f48ff06f          	j	0x4200ffa2
4201085e:	4501                	li	a0,0
42010860:	f42ff06f          	j	0x4200ffa2
