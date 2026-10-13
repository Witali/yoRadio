
factory-irom.bin:     file format binary


Disassembly of section .data:

4200c518 <.data+0xc4f8>:
4200c518:	1141                	addi	sp,sp,-16
4200c51a:	c606                	sw	ra,12(sp)
4200c51c:	c422                	sw	s0,8(sp)
4200c51e:	3fcc47b7          	lui	a5,0x3fcc4
4200c522:	a4a79d23          	sh	a0,-1446(a5) # 0x3fcc3a5a
4200c526:	3fcc47b7          	lui	a5,0x3fcc4
4200c52a:	a4b79c23          	sh	a1,-1448(a5) # 0x3fcc3a58
4200c52e:	3fcc47b7          	lui	a5,0x3fcc4
4200c532:	a60782a3          	sb	zero,-1435(a5) # 0x3fcc3a65
4200c536:	3fcc4437          	lui	s0,0x3fcc4
4200c53a:	4785                	li	a5,1
4200c53c:	a6f40223          	sb	a5,-1436(s0) # 0x3fcc3a64
4200c540:	3fcc47b7          	lui	a5,0x3fcc4
4200c544:	a6c7a023          	sw	a2,-1440(a5) # 0x3fcc3a60
4200c548:	3fcc47b7          	lui	a5,0x3fcc4
4200c54c:	a6078623          	sb	zero,-1428(a5) # 0x3fcc3a6c
4200c550:	6605                	lui	a2,0x1
4200c552:	40060613          	addi	a2,a2,1024 # 0x1400
4200c556:	4581                	li	a1,0
4200c558:	3fcbb537          	lui	a0,0x3fcbb
4200c55c:	7a450513          	addi	a0,a0,1956 # 0x3fcbb7a4
4200c560:	fdff4097          	auipc	ra,0xfdff4
4200c564:	f28080e7          	jalr	-216(ra) # 0x40000488
4200c568:	f45ff0ef          	jal	0x4200c4ac
4200c56c:	a6040223          	sb	zero,-1436(s0)
4200c570:	40b2                	lw	ra,12(sp)
4200c572:	4422                	lw	s0,8(sp)
4200c574:	0141                	addi	sp,sp,16
4200c576:	8082                	ret
