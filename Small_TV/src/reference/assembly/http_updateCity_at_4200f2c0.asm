
factory-irom.bin:     file format binary


Disassembly of section .data:

4200f2c0 <.data+0xf2a0>:
4200f2c0:	7169                	addi	sp,sp,-304
4200f2c2:	12112623          	sw	ra,300(sp)
4200f2c6:	12812423          	sw	s0,296(sp)
4200f2ca:	12912223          	sw	s1,292(sp)
4200f2ce:	13212023          	sw	s2,288(sp)
4200f2d2:	11312e23          	sw	s3,284(sp)
4200f2d6:	11412c23          	sw	s4,280(sp)
4200f2da:	11512a23          	sw	s5,276(sp)
4200f2de:	892a                	mv	s2,a0
4200f2e0:	008cc7b7          	lui	a5,0x8cc
4200f2e4:	cef78793          	addi	a5,a5,-785 # 0x8cbcef
4200f2e8:	c63e                	sw	a5,12(sp)
4200f2ea:	0ff00613          	li	a2,255
4200f2ee:	080c                	addi	a1,sp,16
4200f2f0:	3a42c0ef          	jal	0x4203b694
4200f2f4:	12a05a63          	blez	a0,0x4200f428
4200f2f8:	11050793          	addi	a5,a0,272
4200f2fc:	978a                	add	a5,a5,sp
4200f2fe:	f0078023          	sb	zero,-256(a5)
4200f302:	3c0c35b7          	lui	a1,0x3c0c3
4200f306:	6e858593          	addi	a1,a1,1768 # 0x3c0c36e8
4200f30a:	0808                	addi	a0,sp,16
4200f30c:	fdff1097          	auipc	ra,0xfdff1
4200f310:	1a0080e7          	jalr	416(ra) # 0x400004ac
4200f314:	00850493          	addi	s1,a0,8
4200f318:	02c00593          	li	a1,44
4200f31c:	8526                	mv	a0,s1
4200f31e:	fdff1097          	auipc	ra,0xfdff1
4200f322:	1f6080e7          	jalr	502(ra) # 0x40000514
4200f326:	89aa                	mv	s3,a0
4200f328:	006c                	addi	a1,sp,12
4200f32a:	8526                	mv	a0,s1
4200f32c:	fdff1097          	auipc	ra,0xfdff1
4200f330:	180080e7          	jalr	384(ra) # 0x400004ac
4200f334:	842a                	mv	s0,a0
4200f336:	10050063          	beqz	a0,0x4200f436
4200f33a:	8aaa                	mv	s5,a0
4200f33c:	3fcb8a37          	lui	s4,0x3fcb8
4200f340:	04100613          	li	a2,65
4200f344:	4581                	li	a1,0
4200f346:	c77a0513          	addi	a0,s4,-905 # 0x3fcb7c77
4200f34a:	fdff1097          	auipc	ra,0xfdff1
4200f34e:	13e080e7          	jalr	318(ra) # 0x40000488
4200f352:	409a8633          	sub	a2,s5,s1
4200f356:	85a6                	mv	a1,s1
4200f358:	c77a0513          	addi	a0,s4,-905
4200f35c:	fdff1097          	auipc	ra,0xfdff1
4200f360:	140080e7          	jalr	320(ra) # 0x4000049c
4200f364:	c879                	beqz	s0,0x4200f43a
4200f366:	040d                	addi	s0,s0,3
4200f368:	3c0c35b7          	lui	a1,0x3c0c3
4200f36c:	6f458593          	addi	a1,a1,1780 # 0x3c0c36f4
4200f370:	8522                	mv	a0,s0
4200f372:	fdff1097          	auipc	ra,0xfdff1
4200f376:	13a080e7          	jalr	314(ra) # 0x400004ac
4200f37a:	84aa                	mv	s1,a0
4200f37c:	3fcb89b7          	lui	s3,0x3fcb8
4200f380:	4651                	li	a2,20
4200f382:	4581                	li	a1,0
4200f384:	c6398513          	addi	a0,s3,-925 # 0x3fcb7c63
4200f388:	fdff1097          	auipc	ra,0xfdff1
4200f38c:	100080e7          	jalr	256(ra) # 0x40000488
4200f390:	40848633          	sub	a2,s1,s0
4200f394:	85a2                	mv	a1,s0
4200f396:	c6398513          	addi	a0,s3,-925
4200f39a:	fdff1097          	auipc	ra,0xfdff1
4200f39e:	102080e7          	jalr	258(ra) # 0x4000049c
4200f3a2:	4785                	li	a5,1
4200f3a4:	3fcc4737          	lui	a4,0x3fcc4
4200f3a8:	9ef70023          	sb	a5,-1568(a4) # 0x3fcc39e0
4200f3ac:	3fcc4737          	lui	a4,0x3fcc4
4200f3b0:	03200693          	li	a3,50
4200f3b4:	9cd72e23          	sw	a3,-1572(a4) # 0x3fcc39dc
4200f3b8:	3fcc4737          	lui	a4,0x3fcc4
4200f3bc:	9ef709a3          	sb	a5,-1549(a4) # 0x3fcc39f3
4200f3c0:	3fcc47b7          	lui	a5,0x3fcc4
4200f3c4:	9c078ba3          	sb	zero,-1577(a5) # 0x3fcc39d7
4200f3c8:	3fcc47b7          	lui	a5,0x3fcc4
4200f3cc:	9e0784a3          	sb	zero,-1559(a5) # 0x3fcc39e9
4200f3d0:	3fcc47b7          	lui	a5,0x3fcc4
4200f3d4:	aa078ca3          	sb	zero,-1351(a5) # 0x3fcc3ab9
4200f3d8:	3fcc47b7          	lui	a5,0x3fcc4
4200f3dc:	aa078c23          	sb	zero,-1352(a5) # 0x3fcc3ab8
4200f3e0:	3c0c3637          	lui	a2,0x3c0c3
4200f3e4:	1dc60613          	addi	a2,a2,476 # 0x3c0c31dc
4200f3e8:	3c0c35b7          	lui	a1,0x3c0c3
4200f3ec:	1e458593          	addi	a1,a1,484 # 0x3c0c31e4
4200f3f0:	854a                	mv	a0,s2
4200f3f2:	5232b0ef          	jal	0x4203b114
4200f3f6:	4609                	li	a2,2
4200f3f8:	3c0c35b7          	lui	a1,0x3c0c3
4200f3fc:	28c58593          	addi	a1,a1,652 # 0x3c0c328c
4200f400:	854a                	mv	a0,s2
4200f402:	5912b0ef          	jal	0x4203b192
4200f406:	4501                	li	a0,0
4200f408:	12c12083          	lw	ra,300(sp)
4200f40c:	12812403          	lw	s0,296(sp)
4200f410:	12412483          	lw	s1,292(sp)
4200f414:	12012903          	lw	s2,288(sp)
4200f418:	11c12983          	lw	s3,284(sp)
4200f41c:	11812a03          	lw	s4,280(sp)
4200f420:	11412a83          	lw	s5,276(sp)
4200f424:	6155                	addi	sp,sp,304
4200f426:	8082                	ret
4200f428:	4601                	li	a2,0
4200f42a:	45a1                	li	a1,8
4200f42c:	854a                	mv	a0,s2
4200f42e:	7552b0ef          	jal	0x4203b382
4200f432:	557d                	li	a0,-1
4200f434:	bfd1                	j	0x4200f408
4200f436:	8ace                	mv	s5,s3
4200f438:	b711                	j	0x4200f33c
4200f43a:	00198413          	addi	s0,s3,1
4200f43e:	b72d                	j	0x4200f368
