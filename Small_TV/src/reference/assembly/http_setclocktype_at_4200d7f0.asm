
factory-analysis.elf:     file format elf32-littleriscv


Disassembly of section .flash.text:

4200d7f0 <.flash.text+0xd7d0>:
4200d7f0:	7179                	addi	sp,sp,-48
4200d7f2:	d606                	sw	ra,44(sp)
4200d7f4:	d422                	sw	s0,40(sp)
4200d7f6:	842a                	mv	s0,a0
4200d7f8:	20c52703          	lw	a4,524(a0)
4200d7fc:	04000793          	li	a5,64
4200d800:	08e7ef63          	bltu	a5,a4,0x4200d89e
4200d804:	4651                	li	a2,20
4200d806:	006c                	addi	a1,sp,12
4200d808:	68d2d0ef          	jal	0x4203b694
4200d80c:	08a05f63          	blez	a0,0x4200d8aa
4200d810:	02050793          	addi	a5,a0,32
4200d814:	00278533          	add	a0,a5,sp
4200d818:	fe050623          	sb	zero,-20(a0)
4200d81c:	3c0c45b7          	lui	a1,0x3c0c4
4200d820:	92458593          	addi	a1,a1,-1756 # 0x3c0c3924
4200d824:	0068                	addi	a0,sp,12
4200d826:	fdff3097          	auipc	ra,0xfdff3
4200d82a:	c86080e7          	jalr	-890(ra) # 0x400004ac
4200d82e:	00c54703          	lbu	a4,12(a0)
4200d832:	fd070793          	addi	a5,a4,-48
4200d836:	0ff7f793          	zext.b	a5,a5
4200d83a:	468d                	li	a3,3
4200d83c:	02f6e963          	bltu	a3,a5,0x4200d86e
4200d840:	fd070713          	addi	a4,a4,-48
4200d844:	3fcb87b7          	lui	a5,0x3fcb8
4200d848:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200d84c:	16e7a423          	sw	a4,360(a5)
4200d850:	3fcc47b7          	lui	a5,0x3fcc4
4200d854:	9e0784a3          	sb	zero,-1559(a5) # 0x3fcc39e9
4200d858:	3fcc47b7          	lui	a5,0x3fcc4
4200d85c:	4705                	li	a4,1
4200d85e:	9ee78023          	sb	a4,-1568(a5) # 0x3fcc39e0
4200d862:	3fcc47b7          	lui	a5,0x3fcc4
4200d866:	03200713          	li	a4,50
4200d86a:	9ce7ae23          	sw	a4,-1572(a5) # 0x3fcc39dc
4200d86e:	3c0c3637          	lui	a2,0x3c0c3
4200d872:	1dc60613          	addi	a2,a2,476 # 0x3c0c31dc
4200d876:	3c0c35b7          	lui	a1,0x3c0c3
4200d87a:	1e458593          	addi	a1,a1,484 # 0x3c0c31e4
4200d87e:	8522                	mv	a0,s0
4200d880:	0952d0ef          	jal	0x4203b114
4200d884:	4609                	li	a2,2
4200d886:	3c0c35b7          	lui	a1,0x3c0c3
4200d88a:	28c58593          	addi	a1,a1,652 # 0x3c0c328c
4200d88e:	8522                	mv	a0,s0
4200d890:	1032d0ef          	jal	0x4203b192
4200d894:	4501                	li	a0,0
4200d896:	50b2                	lw	ra,44(sp)
4200d898:	5422                	lw	s0,40(sp)
4200d89a:	6145                	addi	sp,sp,48
4200d89c:	8082                	ret
4200d89e:	4601                	li	a2,0
4200d8a0:	45a5                	li	a1,9
4200d8a2:	2e12d0ef          	jal	0x4203b382
4200d8a6:	557d                	li	a0,-1
4200d8a8:	b7fd                	j	0x4200d896
4200d8aa:	4601                	li	a2,0
4200d8ac:	45a1                	li	a1,8
4200d8ae:	8522                	mv	a0,s0
4200d8b0:	2d32d0ef          	jal	0x4203b382
4200d8b4:	557d                	li	a0,-1
4200d8b6:	b7c5                	j	0x4200d896
