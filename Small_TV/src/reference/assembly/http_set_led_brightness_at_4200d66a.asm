
factory-analysis.elf:     file format elf32-littleriscv


Disassembly of section .flash.text:

4200d66a <.flash.text+0xd64a>:
4200d66a:	715d                	addi	sp,sp,-80
4200d66c:	c686                	sw	ra,76(sp)
4200d66e:	c4a2                	sw	s0,72(sp)
4200d670:	842a                	mv	s0,a0
4200d672:	03f00613          	li	a2,63
4200d676:	858a                	mv	a1,sp
4200d678:	01c2e0ef          	jal	0x4203b694
4200d67c:	08a05b63          	blez	a0,0x4200d712
4200d680:	04050793          	addi	a5,a0,64
4200d684:	978a                	add	a5,a5,sp
4200d686:	fc078023          	sb	zero,-64(a5)
4200d68a:	3c0c35b7          	lui	a1,0x3c0c3
4200d68e:	25058593          	addi	a1,a1,592 # 0x3c0c3250
4200d692:	850a                	mv	a0,sp
4200d694:	fdff3097          	auipc	ra,0xfdff3
4200d698:	e18080e7          	jalr	-488(ra) # 0x400004ac
4200d69c:	c139                	beqz	a0,0x4200d6e2
4200d69e:	0539                	addi	a0,a0,14
4200d6a0:	fdff3097          	auipc	ra,0xfdff3
4200d6a4:	ee0080e7          	jalr	-288(ra) # 0x40000580
4200d6a8:	00251793          	slli	a5,a0,0x2
4200d6ac:	97aa                	add	a5,a5,a0
4200d6ae:	0786                	slli	a5,a5,0x1
4200d6b0:	40f007b3          	neg	a5,a5
4200d6b4:	3e878793          	addi	a5,a5,1000
4200d6b8:	3fcb8737          	lui	a4,0x3fcb8
4200d6bc:	b9c70713          	addi	a4,a4,-1124 # 0x3fcb7b9c
4200d6c0:	18f72023          	sw	a5,384(a4)
4200d6c4:	4785                	li	a5,1
4200d6c6:	3fcc4737          	lui	a4,0x3fcc4
4200d6ca:	9ef70923          	sb	a5,-1550(a4) # 0x3fcc39f2
4200d6ce:	3fcc4737          	lui	a4,0x3fcc4
4200d6d2:	9ef70023          	sb	a5,-1568(a4) # 0x3fcc39e0
4200d6d6:	3fcc47b7          	lui	a5,0x3fcc4
4200d6da:	03200713          	li	a4,50
4200d6de:	9ce7ae23          	sw	a4,-1572(a5) # 0x3fcc39dc
4200d6e2:	3c0c3637          	lui	a2,0x3c0c3
4200d6e6:	1dc60613          	addi	a2,a2,476 # 0x3c0c31dc
4200d6ea:	3c0c35b7          	lui	a1,0x3c0c3
4200d6ee:	1e458593          	addi	a1,a1,484 # 0x3c0c31e4
4200d6f2:	8522                	mv	a0,s0
4200d6f4:	2212d0ef          	jal	0x4203b114
4200d6f8:	4609                	li	a2,2
4200d6fa:	3c0c35b7          	lui	a1,0x3c0c3
4200d6fe:	28c58593          	addi	a1,a1,652 # 0x3c0c328c
4200d702:	8522                	mv	a0,s0
4200d704:	28f2d0ef          	jal	0x4203b192
4200d708:	4501                	li	a0,0
4200d70a:	40b6                	lw	ra,76(sp)
4200d70c:	4426                	lw	s0,72(sp)
4200d70e:	6161                	addi	sp,sp,80
4200d710:	8082                	ret
4200d712:	4601                	li	a2,0
4200d714:	45a1                	li	a1,8
4200d716:	8522                	mv	a0,s0
4200d718:	46b2d0ef          	jal	0x4203b382
4200d71c:	557d                	li	a0,-1
4200d71e:	b7f5                	j	0x4200d70a
