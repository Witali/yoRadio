
factory-irom.bin:     file format binary


Disassembly of section .data:

420a74e6 <.data+0xa74c6>:
420a74e6:	4145d813          	srai	a6,a1,0x14
420a74ea:	1141                	addi	sp,sp,-16
420a74ec:	7ff87813          	andi	a6,a6,2047
420a74f0:	c606                	sw	ra,12(sp)
420a74f2:	c422                	sw	s0,8(sp)
420a74f4:	c226                	sw	s1,4(sp)
420a74f6:	c0180e13          	addi	t3,a6,-1023
420a74fa:	464d                	li	a2,19
420a74fc:	86aa                	mv	a3,a0
420a74fe:	872e                	mv	a4,a1
420a7500:	87ae                	mv	a5,a1
420a7502:	05c64663          	blt	a2,t3,0x420a754e
420a7506:	020e5163          	bgez	t3,0x420a7528
420a750a:	80000737          	lui	a4,0x80000
420a750e:	57fd                	li	a5,-1
420a7510:	8f6d                	and	a4,a4,a1
420a7512:	00fe0763          	beq	t3,a5,0x420a7520
420a7516:	87ba                	mv	a5,a4
420a7518:	4601                	li	a2,0
420a751a:	86b2                	mv	a3,a2
420a751c:	873e                	mv	a4,a5
420a751e:	a881                	j	0x420a756e
420a7520:	3ff007b7          	lui	a5,0x3ff00
420a7524:	8fd9                	or	a5,a5,a4
420a7526:	bfcd                	j	0x420a7518
420a7528:	001007b7          	lui	a5,0x100
420a752c:	17fd                	addi	a5,a5,-1 # 0xfffff
420a752e:	41c7d7b3          	sra	a5,a5,t3
420a7532:	00b7f633          	and	a2,a5,a1
420a7536:	8e49                	or	a2,a2,a0
420a7538:	ca1d                	beqz	a2,0x420a756e
420a753a:	000806b7          	lui	a3,0x80
420a753e:	41c6d6b3          	sra	a3,a3,t3
420a7542:	00b68733          	add	a4,a3,a1
420a7546:	fff7c793          	not	a5,a5
420a754a:	8ff9                	and	a5,a5,a4
420a754c:	b7f1                	j	0x420a7518
420a754e:	03300313          	li	t1,51
420a7552:	03c35563          	bge	t1,t3,0x420a757c
420a7556:	40000793          	li	a5,1024
420a755a:	00fe1a63          	bne	t3,a5,0x420a756e
420a755e:	86ae                	mv	a3,a1
420a7560:	862a                	mv	a2,a0
420a7562:	fdf59097          	auipc	ra,0xfdf59
420a7566:	4b6080e7          	jalr	1206(ra) # 0x40000a18
420a756a:	86aa                	mv	a3,a0
420a756c:	872e                	mv	a4,a1
420a756e:	40b2                	lw	ra,12(sp)
420a7570:	4422                	lw	s0,8(sp)
420a7572:	4492                	lw	s1,4(sp)
420a7574:	8536                	mv	a0,a3
420a7576:	85ba                	mv	a1,a4
420a7578:	0141                	addi	sp,sp,16
420a757a:	8082                	ret
420a757c:	bed80813          	addi	a6,a6,-1043
