
factory-irom.bin:     file format binary


Disassembly of section .data:

4200c6e2 <.data+0xc6c2>:
4200c6e2:	1141                	addi	sp,sp,-16
4200c6e4:	c606                	sw	ra,12(sp)
4200c6e6:	3c0f27b7          	lui	a5,0x3c0f2
4200c6ea:	eb87a783          	lw	a5,-328(a5) # 0x3c0f1eb8
4200c6ee:	00b78f63          	beq	a5,a1,0x4200c70c
4200c6f2:	02b78363          	beq	a5,a1,0x4200c718
4200c6f6:	02b78763          	beq	a5,a1,0x4200c724
4200c6fa:	3c0f27b7          	lui	a5,0x3c0f2
4200c6fe:	8487a783          	lw	a5,-1976(a5) # 0x3c0f1848
4200c702:	02b78763          	beq	a5,a1,0x4200c730
4200c706:	40b2                	lw	ra,12(sp)
4200c708:	0141                	addi	sp,sp,16
4200c70a:	8082                	ret
4200c70c:	4739                	li	a4,14
4200c70e:	fee612e3          	bne	a2,a4,0x4200c6f2
4200c712:	edbff0ef          	jal	0x4200c5ec
4200c716:	bfc5                	j	0x4200c706
4200c718:	473d                	li	a4,15
4200c71a:	fce61ee3          	bne	a2,a4,0x4200c6f6
4200c71e:	e5bff0ef          	jal	0x4200c578
4200c722:	b7d5                	j	0x4200c706
4200c724:	4789                	li	a5,2
4200c726:	fcf61ae3          	bne	a2,a5,0x4200c6fa
4200c72a:	5f5380ef          	jal	0x4204551e
4200c72e:	bfe1                	j	0x4200c706
4200c730:	fa79                	bnez	a2,0x4200c706
4200c732:	3fcc47b7          	lui	a5,0x3fcc4
4200c736:	a607ac23          	sw	zero,-1416(a5) # 0x3fcc3a78
4200c73a:	4585                	li	a1,1
4200c73c:	3fcc47b7          	lui	a5,0x3fcc4
4200c740:	a7c7a503          	lw	a0,-1412(a5) # 0x3fcc3a7c
4200c744:	fe37c097          	auipc	ra,0xfe37c
4200c748:	6ea080e7          	jalr	1770(ra) # 0x40388e2e
4200c74c:	bf6d                	j	0x4200c706
