
factory-irom.bin:     file format binary


Disassembly of section .data:

4200c602 <.data+0xc5e2>:
4200c602:	7179                	addi	sp,sp,-48
4200c604:	d606                	sw	ra,44(sp)
4200c606:	d422                	sw	s0,40(sp)
4200c608:	d226                	sw	s1,36(sp)
4200c60a:	842a                	mv	s0,a0
4200c60c:	3c0f27b7          	lui	a5,0x3c0f2
4200c610:	eb87a783          	lw	a5,-328(a5) # 0x3c0f1eb8
4200c614:	00b78f63          	beq	a5,a1,0x4200c632
4200c618:	02b78363          	beq	a5,a1,0x4200c63e
4200c61c:	3c0f27b7          	lui	a5,0x3c0f2
4200c620:	8487a783          	lw	a5,-1976(a5) # 0x3c0f1848
4200c624:	06b78363          	beq	a5,a1,0x4200c68a
4200c628:	50b2                	lw	ra,44(sp)
4200c62a:	5422                	lw	s0,40(sp)
4200c62c:	5492                	lw	s1,36(sp)
4200c62e:	6145                	addi	sp,sp,48
4200c630:	8082                	ret
4200c632:	4709                	li	a4,2
4200c634:	fee612e3          	bne	a2,a4,0x4200c618
4200c638:	6e7380ef          	jal	0x4204551e
4200c63c:	b7f5                	j	0x4200c628
4200c63e:	4795                	li	a5,5
4200c640:	fcf61ee3          	bne	a2,a5,0x4200c61c
4200c644:	3fcc47b7          	lui	a5,0x3fcc4
4200c648:	a787a703          	lw	a4,-1416(a5) # 0x3fcc3a78
4200c64c:	478d                	li	a5,3
4200c64e:	02e7c163          	blt	a5,a4,0x4200c670
4200c652:	6cd380ef          	jal	0x4204551e
4200c656:	3fcc4737          	lui	a4,0x3fcc4
4200c65a:	a7872783          	lw	a5,-1416(a4) # 0x3fcc3a78
4200c65e:	0785                	addi	a5,a5,1
4200c660:	a6f72c23          	sw	a5,-1416(a4)
4200c664:	3fcc47b7          	lui	a5,0x3fcc4
4200c668:	4705                	li	a4,1
4200c66a:	a6e78a23          	sb	a4,-1420(a5) # 0x3fcc3a74
4200c66e:	bf6d                	j	0x4200c628
4200c670:	4589                	li	a1,2
4200c672:	3fcc47b7          	lui	a5,0x3fcc4
4200c676:	a7c7a503          	lw	a0,-1412(a5) # 0x3fcc3a7c
4200c67a:	fe37c097          	auipc	ra,0xfe37c
4200c67e:	7b4080e7          	jalr	1972(ra) # 0x40388e2e
4200c682:	8522                	mv	a0,s0
4200c684:	ef5ff0ef          	jal	0x4200c578
4200c688:	b745                	j	0x4200c628
4200c68a:	fe59                	bnez	a2,0x4200c628
4200c68c:	0024                	addi	s1,sp,8
4200c68e:	c402                	sw	zero,8(sp)
4200c690:	c602                	sw	zero,12(sp)
4200c692:	c802                	sw	zero,16(sp)
4200c694:	ca02                	sw	zero,20(sp)
4200c696:	cc02                	sw	zero,24(sp)
4200c698:	ce02                	sw	zero,28(sp)
4200c69a:	4661                	li	a2,24
4200c69c:	85a6                	mv	a1,s1
4200c69e:	00468513          	addi	a0,a3,4
4200c6a2:	751290ef          	jal	0x420365f2
4200c6a6:	85a6                	mv	a1,s1
4200c6a8:	3fcb8537          	lui	a0,0x3fcb8
4200c6ac:	b8450513          	addi	a0,a0,-1148 # 0x3fcb7b84
4200c6b0:	fdff4097          	auipc	ra,0xfdff4
4200c6b4:	de8080e7          	jalr	-536(ra) # 0x40000498
4200c6b8:	3fcc47b7          	lui	a5,0x3fcc4
4200c6bc:	a607ac23          	sw	zero,-1416(a5) # 0x3fcc3a78
4200c6c0:	3fcc47b7          	lui	a5,0x3fcc4
4200c6c4:	9e078523          	sb	zero,-1558(a5) # 0x3fcc39ea
4200c6c8:	8522                	mv	a0,s0
4200c6ca:	f23ff0ef          	jal	0x4200c5ec
4200c6ce:	4585                	li	a1,1
4200c6d0:	3fcc47b7          	lui	a5,0x3fcc4
4200c6d4:	a7c7a503          	lw	a0,-1412(a5) # 0x3fcc3a7c
4200c6d8:	fe37c097          	auipc	ra,0xfe37c
4200c6dc:	756080e7          	jalr	1878(ra) # 0x40388e2e
4200c6e0:	b7a1                	j	0x4200c628
