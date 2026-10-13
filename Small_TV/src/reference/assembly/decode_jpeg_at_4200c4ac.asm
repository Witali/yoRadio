
factory-irom.bin:     file format binary


Disassembly of section .data:

4200c4ac <.data+0xc48c>:
4200c4ac:	7135                	addi	sp,sp,-160
4200c4ae:	cf06                	sw	ra,156(sp)
4200c4b0:	3fcc47b7          	lui	a5,0x3fcc4
4200c4b4:	a607a783          	lw	a5,-1440(a5) # 0x3fcc3a60
4200c4b8:	c43e                	sw	a5,8(sp)
4200c4ba:	0038                	addi	a4,sp,8
4200c4bc:	6685                	lui	a3,0x1
4200c4be:	dac68693          	addi	a3,a3,-596 # 0xdac
4200c4c2:	3fcbb637          	lui	a2,0x3fcbb
4200c4c6:	9f860613          	addi	a2,a2,-1544 # 0x3fcba9f8
4200c4ca:	4200c5b7          	lui	a1,0x4200c
4200c4ce:	33e58593          	addi	a1,a1,830 # 0x4200c33e
4200c4d2:	0828                	addi	a0,sp,24
4200c4d4:	774050ef          	jal	0x42011c48
4200c4d8:	c501                	beqz	a0,0x4200c4e0
4200c4da:	40fa                	lw	ra,156(sp)
4200c4dc:	610d                	addi	sp,sp,160
4200c4de:	8082                	ret
4200c4e0:	3fcbb7b7          	lui	a5,0x3fcbb
4200c4e4:	7a478793          	addi	a5,a5,1956 # 0x3fcbb7a4
4200c4e8:	c63e                	sw	a5,12(sp)
4200c4ea:	03415703          	lhu	a4,52(sp)
4200c4ee:	c83a                	sw	a4,16(sp)
4200c4f0:	03615783          	lhu	a5,54(sp)
4200c4f4:	ca3e                	sw	a5,20(sp)
4200c4f6:	3fcc46b7          	lui	a3,0x3fcc4
4200c4fa:	a6e69423          	sh	a4,-1432(a3) # 0x3fcc3a68
4200c4fe:	3fcc4737          	lui	a4,0x3fcc4
4200c502:	a6f71323          	sh	a5,-1434(a4) # 0x3fcc3a66
4200c506:	4601                	li	a2,0
4200c508:	4200c5b7          	lui	a1,0x4200c
4200c50c:	37458593          	addi	a1,a1,884 # 0x4200c374
4200c510:	0828                	addi	a0,sp,24
4200c512:	2c7050ef          	jal	0x42011fd8
4200c516:	b7d1                	j	0x4200c4da
