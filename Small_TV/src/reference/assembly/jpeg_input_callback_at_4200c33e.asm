
factory-irom.bin:     file format binary


Disassembly of section .data:

4200c33e <.data+0xc31e>:
4200c33e:	1141                	addi	sp,sp,-16
4200c340:	c606                	sw	ra,12(sp)
4200c342:	c422                	sw	s0,8(sp)
4200c344:	c226                	sw	s1,4(sp)
4200c346:	8432                	mv	s0,a2
4200c348:	5964                	lw	s1,116(a0)
4200c34a:	c18d                	beqz	a1,0x4200c36c
4200c34c:	86b2                	mv	a3,a2
4200c34e:	4090                	lw	a2,0(s1)
4200c350:	4501                	li	a0,0
4200c352:	fe386097          	auipc	ra,0xfe386
4200c356:	fd4080e7          	jalr	-44(ra) # 0x40392326
4200c35a:	409c                	lw	a5,0(s1)
4200c35c:	97a2                	add	a5,a5,s0
4200c35e:	c09c                	sw	a5,0(s1)
4200c360:	8522                	mv	a0,s0
4200c362:	40b2                	lw	ra,12(sp)
4200c364:	4422                	lw	s0,8(sp)
4200c366:	4492                	lw	s1,4(sp)
4200c368:	0141                	addi	sp,sp,16
4200c36a:	8082                	ret
4200c36c:	409c                	lw	a5,0(s1)
4200c36e:	97b2                	add	a5,a5,a2
4200c370:	c09c                	sw	a5,0(s1)
4200c372:	b7fd                	j	0x4200c360
