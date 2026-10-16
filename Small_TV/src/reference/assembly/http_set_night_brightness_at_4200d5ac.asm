
factory-analysis.elf:     file format elf32-littleriscv


Disassembly of section .flash.text:

4200d5ac <.flash.text+0xd58c>:
4200d5ac:	715d                	addi	sp,sp,-80
4200d5ae:	c686                	sw	ra,76(sp)
4200d5b0:	c4a2                	sw	s0,72(sp)
4200d5b2:	842a                	mv	s0,a0
4200d5b4:	03f00613          	li	a2,63
4200d5b8:	858a                	mv	a1,sp
4200d5ba:	0da2e0ef          	jal	0x4203b694
4200d5be:	08a05f63          	blez	a0,0x4200d65c
4200d5c2:	04050793          	addi	a5,a0,64
4200d5c6:	978a                	add	a5,a5,sp
4200d5c8:	fc078023          	sb	zero,-64(a5)
4200d5cc:	3c0c35b7          	lui	a1,0x3c0c3
4200d5d0:	23c58593          	addi	a1,a1,572 # 0x3c0c323c
4200d5d4:	850a                	mv	a0,sp
4200d5d6:	fdff3097          	auipc	ra,0xfdff3
4200d5da:	ed6080e7          	jalr	-298(ra) # 0x400004ac
4200d5de:	c539                	beqz	a0,0x4200d62c
4200d5e0:	0541                	addi	a0,a0,16
4200d5e2:	fdff3097          	auipc	ra,0xfdff3
4200d5e6:	f9e080e7          	jalr	-98(ra) # 0x40000580
4200d5ea:	3fcc47b7          	lui	a5,0x3fcc4
4200d5ee:	a8a7ac23          	sw	a0,-1384(a5) # 0x3fcc3a98
4200d5f2:	00251793          	slli	a5,a0,0x2
4200d5f6:	97aa                	add	a5,a5,a0
4200d5f8:	0786                	slli	a5,a5,0x1
4200d5fa:	40f007b3          	neg	a5,a5
4200d5fe:	3e878793          	addi	a5,a5,1000
4200d602:	3fcb8737          	lui	a4,0x3fcb8
4200d606:	b9c70713          	addi	a4,a4,-1124 # 0x3fcb7b9c
4200d60a:	18f72e23          	sw	a5,412(a4)
4200d60e:	4785                	li	a5,1
4200d610:	3fcc4737          	lui	a4,0x3fcc4
4200d614:	9ef70923          	sb	a5,-1550(a4) # 0x3fcc39f2
4200d618:	3fcc4737          	lui	a4,0x3fcc4
4200d61c:	9ef70023          	sb	a5,-1568(a4) # 0x3fcc39e0
4200d620:	3fcc47b7          	lui	a5,0x3fcc4
4200d624:	03200713          	li	a4,50
4200d628:	9ce7ae23          	sw	a4,-1572(a5) # 0x3fcc39dc
4200d62c:	3c0c3637          	lui	a2,0x3c0c3
4200d630:	1dc60613          	addi	a2,a2,476 # 0x3c0c31dc
4200d634:	3c0c35b7          	lui	a1,0x3c0c3
4200d638:	1e458593          	addi	a1,a1,484 # 0x3c0c31e4
4200d63c:	8522                	mv	a0,s0
4200d63e:	2d72d0ef          	jal	0x4203b114
4200d642:	4609                	li	a2,2
4200d644:	3c0c35b7          	lui	a1,0x3c0c3
4200d648:	28c58593          	addi	a1,a1,652 # 0x3c0c328c
4200d64c:	8522                	mv	a0,s0
4200d64e:	3452d0ef          	jal	0x4203b192
4200d652:	4501                	li	a0,0
4200d654:	40b6                	lw	ra,76(sp)
4200d656:	4426                	lw	s0,72(sp)
4200d658:	6161                	addi	sp,sp,80
4200d65a:	8082                	ret
4200d65c:	4601                	li	a2,0
4200d65e:	45a1                	li	a1,8
4200d660:	8522                	mv	a0,s0
4200d662:	5212d0ef          	jal	0x4203b382
4200d666:	557d                	li	a0,-1
4200d668:	b7f5                	j	0x4200d654
