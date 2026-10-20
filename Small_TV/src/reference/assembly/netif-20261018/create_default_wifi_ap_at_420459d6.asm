
factory-irom.bin:     file format binary


Disassembly of section .data:

420459d6 <.data+0x459b6>:
420459d6:	1101                	addi	sp,sp,-32
420459d8:	ce06                	sw	ra,28(sp)
420459da:	cc22                	sw	s0,24(sp)
420459dc:	3c0f67b7          	lui	a5,0x3c0f6
420459e0:	5d878793          	addi	a5,a5,1496 # 0x3c0f65d8
420459e4:	c23e                	sw	a5,4(sp)
420459e6:	c402                	sw	zero,8(sp)
420459e8:	8781a783          	lw	a5,-1928(gp)
420459ec:	c63e                	sw	a5,12(sp)
420459ee:	0048                	addi	a0,sp,4
420459f0:	d63f00ef          	jal	0x42036752
420459f4:	842a                	mv	s0,a0
420459f6:	cd01                	beqz	a0,0x42045a0e
420459f8:	fbbff0ef          	jal	0x420459b2
420459fc:	e91d                	bnez	a0,0x42045a32
420459fe:	f85ff0ef          	jal	0x42045982
42045a02:	e931                	bnez	a0,0x42045a56
42045a04:	8522                	mv	a0,s0
42045a06:	40f2                	lw	ra,28(sp)
42045a08:	4462                	lw	s0,24(sp)
42045a0a:	6105                	addi	sp,sp,32
42045a0c:	8082                	ret
42045a0e:	3c0c96b7          	lui	a3,0x3c0c9
42045a12:	9bc68693          	addi	a3,a3,-1604 # 0x3c0c89bc
42045a16:	3c0f2637          	lui	a2,0x3c0f2
42045a1a:	ee060613          	addi	a2,a2,-288 # 0x3c0f1ee0
42045a1e:	19800593          	li	a1,408
42045a22:	3c0cf537          	lui	a0,0x3c0cf
42045a26:	42e50513          	addi	a0,a0,1070 # 0x3c0cf42e
42045a2a:	fe349097          	auipc	ra,0xfe349
42045a2e:	8c6080e7          	jalr	-1850(ra) # 0x4038e2f0
42045a32:	3c0cf737          	lui	a4,0x3c0cf
42045a36:	44070713          	addi	a4,a4,1088 # 0x3c0cf440
42045a3a:	3c0f26b7          	lui	a3,0x3c0f2
42045a3e:	ee068693          	addi	a3,a3,-288 # 0x3c0f1ee0
42045a42:	19900613          	li	a2,409
42045a46:	3c0cf5b7          	lui	a1,0x3c0cf
42045a4a:	46058593          	addi	a1,a1,1120 # 0x3c0cf460
42045a4e:	fe342097          	auipc	ra,0xfe342
42045a52:	81c080e7          	jalr	-2020(ra) # 0x4038726a
42045a56:	3c0cf737          	lui	a4,0x3c0cf
42045a5a:	48c70713          	addi	a4,a4,1164 # 0x3c0cf48c
42045a5e:	3c0f26b7          	lui	a3,0x3c0f2
42045a62:	ee068693          	addi	a3,a3,-288 # 0x3c0f1ee0
42045a66:	19a00613          	li	a2,410
42045a6a:	3c0cf5b7          	lui	a1,0x3c0cf
42045a6e:	46058593          	addi	a1,a1,1120 # 0x3c0cf460
42045a72:	fe341097          	auipc	ra,0xfe341
42045a76:	7f8080e7          	jalr	2040(ra) # 0x4038726a
