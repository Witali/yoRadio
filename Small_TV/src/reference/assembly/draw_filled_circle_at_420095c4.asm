
factory-irom.bin:     file format binary


Disassembly of section .data:

420095c4 <.data+0x95a4>:
420095c4:	1101                	addi	sp,sp,-32
420095c6:	ce06                	sw	ra,28(sp)
420095c8:	cc22                	sw	s0,24(sp)
420095ca:	ca26                	sw	s1,20(sp)
420095cc:	c84a                	sw	s2,16(sp)
420095ce:	c64e                	sw	s3,12(sp)
420095d0:	c452                	sw	s4,8(sp)
420095d2:	c256                	sw	s5,4(sp)
420095d4:	c05a                	sw	s6,0(sp)
420095d6:	8aaa                	mv	s5,a0
420095d8:	8a2e                	mv	s4,a1
420095da:	84b2                	mv	s1,a2
420095dc:	89b6                	mv	s3,a3
420095de:	40c00b33          	neg	s6,a2
420095e2:	0b42                	slli	s6,s6,0x10
420095e4:	410b5b13          	srai	s6,s6,0x10
420095e8:	895a                	mv	s2,s6
420095ea:	a83d                	j	0x42009628
420095ec:	012a05b3          	add	a1,s4,s2
420095f0:	008a8533          	add	a0,s5,s0
420095f4:	864e                	mv	a2,s3
420095f6:	05c2                	slli	a1,a1,0x10
420095f8:	81c1                	srli	a1,a1,0x10
420095fa:	0542                	slli	a0,a0,0x10
420095fc:	8141                	srli	a0,a0,0x10
420095fe:	f8dff0ef          	jal	0x4200958a
42009602:	0405                	addi	s0,s0,1
42009604:	0442                	slli	s0,s0,0x10
42009606:	8441                	srai	s0,s0,0x10
42009608:	0084cc63          	blt	s1,s0,0x42009620
4200960c:	028407b3          	mul	a5,s0,s0
42009610:	03290733          	mul	a4,s2,s2
42009614:	97ba                	add	a5,a5,a4
42009616:	02948733          	mul	a4,s1,s1
4200961a:	fef744e3          	blt	a4,a5,0x42009602
4200961e:	b7f9                	j	0x420095ec
42009620:	0905                	addi	s2,s2,1
42009622:	0942                	slli	s2,s2,0x10
42009624:	41095913          	srai	s2,s2,0x10
42009628:	0124c463          	blt	s1,s2,0x42009630
4200962c:	845a                	mv	s0,s6
4200962e:	bfe9                	j	0x42009608
42009630:	40f2                	lw	ra,28(sp)
42009632:	4462                	lw	s0,24(sp)
42009634:	44d2                	lw	s1,20(sp)
42009636:	4942                	lw	s2,16(sp)
42009638:	49b2                	lw	s3,12(sp)
4200963a:	4a22                	lw	s4,8(sp)
4200963c:	4a92                	lw	s5,4(sp)
4200963e:	4b02                	lw	s6,0(sp)
42009640:	6105                	addi	sp,sp,32
42009642:	8082                	ret
