
factory-irom.bin:     file format binary


Disassembly of section .data:

4200826a <.data+0x824a>:
4200826a:	1141                	addi	sp,sp,-16
4200826c:	c606                	sw	ra,12(sp)
4200826e:	3fcc47b7          	lui	a5,0x3fcc4
42008272:	9eb7c783          	lbu	a5,-1557(a5) # 0x3fcc39eb
42008276:	c785                	beqz	a5,0x4200829e
42008278:	3fcc4737          	lui	a4,0x3fcc4
4200827c:	a5674783          	lbu	a5,-1450(a4) # 0x3fcc3a56
42008280:	0785                	addi	a5,a5,1
42008282:	0ff7f793          	zext.b	a5,a5
42008286:	a4f70b23          	sb	a5,-1450(a4)
4200828a:	0b400713          	li	a4,180
4200828e:	00f77663          	bgeu	a4,a5,0x4200829a
42008292:	3fcc47b7          	lui	a5,0x3fcc4
42008296:	9e0785a3          	sb	zero,-1557(a5) # 0x3fcc39eb
4200829a:	72f030ef          	jal	0x4200c1c8
4200829e:	3fcc4737          	lui	a4,0x3fcc4
420082a2:	9cc74783          	lbu	a5,-1588(a4) # 0x3fcc39cc
420082a6:	0785                	addi	a5,a5,1
420082a8:	0ff7f793          	zext.b	a5,a5
420082ac:	9cf70623          	sb	a5,-1588(a4)
420082b0:	4729                	li	a4,10
420082b2:	0ef77e63          	bgeu	a4,a5,0x420083ae
420082b6:	3fcc47b7          	lui	a5,0x3fcc4
420082ba:	9c078623          	sb	zero,-1588(a5) # 0x3fcc39cc
420082be:	3fcc47b7          	lui	a5,0x3fcc4
420082c2:	4705                	li	a4,1
420082c4:	9ee78b23          	sb	a4,-1546(a5) # 0x3fcc39f6
420082c8:	3fcc4737          	lui	a4,0x3fcc4
420082cc:	9cb74783          	lbu	a5,-1589(a4) # 0x3fcc39cb
420082d0:	0785                	addi	a5,a5,1
420082d2:	0ff7f793          	zext.b	a5,a5
420082d6:	9cf705a3          	sb	a5,-1589(a4)
420082da:	4709                	li	a4,2
420082dc:	00f77b63          	bgeu	a4,a5,0x420082f2
420082e0:	3fcc47b7          	lui	a5,0x3fcc4
420082e4:	9c0785a3          	sb	zero,-1589(a5) # 0x3fcc39cb
420082e8:	3fcc47b7          	lui	a5,0x3fcc4
420082ec:	4705                	li	a4,1
420082ee:	9ee78ba3          	sb	a4,-1545(a5) # 0x3fcc39f7
420082f2:	3fcc4737          	lui	a4,0x3fcc4
420082f6:	9ca74783          	lbu	a5,-1590(a4) # 0x3fcc39ca
420082fa:	0785                	addi	a5,a5,1
420082fc:	0ff7f793          	zext.b	a5,a5
42008300:	9cf70523          	sb	a5,-1590(a4)
42008304:	3fcb8737          	lui	a4,0x3fcb8
42008308:	b9c70713          	addi	a4,a4,-1124 # 0x3fcb7b9c
4200830c:	1a072703          	lw	a4,416(a4)
42008310:	00e7eb63          	bltu	a5,a4,0x42008326
42008314:	3fcc47b7          	lui	a5,0x3fcc4
42008318:	9c078523          	sb	zero,-1590(a5) # 0x3fcc39ca
4200831c:	3fcc47b7          	lui	a5,0x3fcc4
42008320:	4705                	li	a4,1
42008322:	9ee78c23          	sb	a4,-1544(a5) # 0x3fcc39f8
42008326:	3fcc4737          	lui	a4,0x3fcc4
4200832a:	9c974783          	lbu	a5,-1591(a4) # 0x3fcc39c9
4200832e:	0785                	addi	a5,a5,1
42008330:	0ff7f793          	zext.b	a5,a5
42008334:	9cf704a3          	sb	a5,-1591(a4)
42008338:	03b00713          	li	a4,59
4200833c:	00f77f63          	bgeu	a4,a5,0x4200835a
42008340:	3fcc47b7          	lui	a5,0x3fcc4
42008344:	9c0784a3          	sb	zero,-1591(a5) # 0x3fcc39c9
42008348:	4785                	li	a5,1
4200834a:	3fcc4737          	lui	a4,0x3fcc4
4200834e:	9ef70aa3          	sb	a5,-1547(a4) # 0x3fcc39f5
42008352:	3fcc4737          	lui	a4,0x3fcc4
42008356:	9ef70823          	sb	a5,-1552(a4) # 0x3fcc39f0
4200835a:	3fcc4737          	lui	a4,0x3fcc4
4200835e:	9c874783          	lbu	a5,-1592(a4) # 0x3fcc39c8
42008362:	0785                	addi	a5,a5,1
42008364:	0ff7f793          	zext.b	a5,a5
42008368:	9cf70423          	sb	a5,-1592(a4)
4200836c:	0b400713          	li	a4,180
42008370:	00f77b63          	bgeu	a4,a5,0x42008386
42008374:	3fcc47b7          	lui	a5,0x3fcc4
42008378:	9c078423          	sb	zero,-1592(a5) # 0x3fcc39c8
4200837c:	3fcc47b7          	lui	a5,0x3fcc4
42008380:	4705                	li	a4,1
42008382:	9ee78a23          	sb	a4,-1548(a5) # 0x3fcc39f4
42008386:	3fcc4737          	lui	a4,0x3fcc4
4200838a:	9c472783          	lw	a5,-1596(a4) # 0x3fcc39c4
4200838e:	0785                	addi	a5,a5,1
42008390:	9cf72223          	sw	a5,-1596(a4)
42008394:	70800713          	li	a4,1800
42008398:	00f77b63          	bgeu	a4,a5,0x420083ae
4200839c:	3fcc47b7          	lui	a5,0x3fcc4
420083a0:	9c07a223          	sw	zero,-1596(a5) # 0x3fcc39c4
420083a4:	3fcc47b7          	lui	a5,0x3fcc4
420083a8:	4705                	li	a4,1
420083aa:	9ee789a3          	sb	a4,-1549(a5) # 0x3fcc39f3
420083ae:	4501                	li	a0,0
420083b0:	40b2                	lw	ra,12(sp)
420083b2:	0141                	addi	sp,sp,16
420083b4:	8082                	ret
