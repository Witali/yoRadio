
factory-irom.bin:     file format binary


Disassembly of section .data:

42045a7a <.data+0x45a5a>:
42045a7a:	1101                	addi	sp,sp,-32
42045a7c:	ce06                	sw	ra,28(sp)
42045a7e:	cc22                	sw	s0,24(sp)
42045a80:	3c0f67b7          	lui	a5,0x3c0f6
42045a84:	60c78793          	addi	a5,a5,1548 # 0x3c0f660c
42045a88:	c23e                	sw	a5,4(sp)
42045a8a:	c402                	sw	zero,8(sp)
42045a8c:	87c1a783          	lw	a5,-1924(gp)
42045a90:	c63e                	sw	a5,12(sp)
42045a92:	0048                	addi	a0,sp,4
42045a94:	cbff00ef          	jal	0x42036752
42045a98:	842a                	mv	s0,a0
42045a9a:	cd01                	beqz	a0,0x42045ab2
42045a9c:	ef5ff0ef          	jal	0x42045990
42045aa0:	e91d                	bnez	a0,0x42045ad6
42045aa2:	ed3ff0ef          	jal	0x42045974
42045aa6:	e931                	bnez	a0,0x42045afa
42045aa8:	8522                	mv	a0,s0
42045aaa:	40f2                	lw	ra,28(sp)
42045aac:	4462                	lw	s0,24(sp)
42045aae:	6105                	addi	sp,sp,32
42045ab0:	8082                	ret
42045ab2:	3c0c96b7          	lui	a3,0x3c0c9
42045ab6:	9bc68693          	addi	a3,a3,-1604 # 0x3c0c89bc
42045aba:	3c0f2637          	lui	a2,0x3c0f2
42045abe:	ebc60613          	addi	a2,a2,-324 # 0x3c0f1ebc
42045ac2:	1a600593          	li	a1,422
42045ac6:	3c0cf537          	lui	a0,0x3c0cf
42045aca:	42e50513          	addi	a0,a0,1070 # 0x3c0cf42e
42045ace:	fe349097          	auipc	ra,0xfe349
42045ad2:	822080e7          	jalr	-2014(ra) # 0x4038e2f0
42045ad6:	3c0cf737          	lui	a4,0x3c0cf
42045ada:	4b470713          	addi	a4,a4,1204 # 0x3c0cf4b4
42045ade:	3c0f26b7          	lui	a3,0x3c0f2
42045ae2:	ebc68693          	addi	a3,a3,-324 # 0x3c0f1ebc
42045ae6:	1a700613          	li	a2,423
42045aea:	3c0cf5b7          	lui	a1,0x3c0cf
42045aee:	46058593          	addi	a1,a1,1120 # 0x3c0cf460
42045af2:	fe341097          	auipc	ra,0xfe341
42045af6:	778080e7          	jalr	1912(ra) # 0x4038726a
42045afa:	3c0cf737          	lui	a4,0x3c0cf
42045afe:	4dc70713          	addi	a4,a4,1244 # 0x3c0cf4dc
42045b02:	3c0f26b7          	lui	a3,0x3c0f2
42045b06:	ebc68693          	addi	a3,a3,-324 # 0x3c0f1ebc
42045b0a:	1a800613          	li	a2,424
42045b0e:	3c0cf5b7          	lui	a1,0x3c0cf
42045b12:	46058593          	addi	a1,a1,1120 # 0x3c0cf460
42045b16:	fe341097          	auipc	ra,0xfe341
42045b1a:	754080e7          	jalr	1876(ra) # 0x4038726a
42045b1e:	4501                	li	a0,0
