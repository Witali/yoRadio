
small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200d31a <clock_task>:
4200d31a:	c4010113          	addi	sp,sp,-960
4200d31e:	3b512223          	sw	s5,932(sp)
4200d322:	0ff00793          	li	a5,255
4200d326:	3fcafab7          	lui	s5,0x3fcaf
4200d32a:	3b212823          	sw	s2,944(sp)
4200d32e:	3b412423          	sw	s4,936(sp)
4200d332:	39712e23          	sw	s7,924(sp)
4200d336:	39812c23          	sw	s8,920(sp)
4200d33a:	39912a23          	sw	s9,916(sp)
4200d33e:	39a12823          	sw	s10,912(sp)
4200d342:	39b12623          	sw	s11,908(sp)
4200d346:	3a112e23          	sw	ra,956(sp)
4200d34a:	3a812c23          	sw	s0,952(sp)
4200d34e:	3a912a23          	sw	s1,948(sp)
4200d352:	3b312623          	sw	s3,940(sp)
4200d356:	3b612023          	sw	s6,928(sp)
4200d35a:	04010623          	sb	zero,76(sp)
4200d35e:	04011823          	sh	zero,80(sp)
4200d362:	4c01                	li	s8,0
4200d364:	d402                	sw	zero,40(sp)
4200d366:	4d01                	li	s10,0
4200d368:	d202                	sw	zero,36(sp)
4200d36a:	d03e                	sw	a5,32(sp)
4200d36c:	ce02                	sw	zero,28(sp)
4200d36e:	4901                	li	s2,0
4200d370:	4c81                	li	s9,0
4200d372:	4b81                	li	s7,0
4200d374:	4a01                	li	s4,0
4200d376:	cc02                	sw	zero,24(sp)
4200d378:	ca02                	sw	zero,20(sp)
4200d37a:	c802                	sw	zero,16(sp)
4200d37c:	4d85                	li	s11,1
4200d37e:	73ca8a93          	addi	s5,s5,1852 # 3fcaf73c <timer_state>
4200d382:	08b0                	addi	a2,sp,88
4200d384:	08cc                	addi	a1,sp,84
4200d386:	0c48                	addi	a0,sp,532
4200d388:	910ff0ef          	jal	4200c498 <settings_snapshot_with_revisions>
4200d38c:	0a28                	addi	a0,sp,280
4200d38e:	6ad030ef          	jal	4201123a <weather_snapshot>
4200d392:	36114603          	lbu	a2,865(sp)
4200d396:	4581                	li	a1,0
4200d398:	08e8                	addi	a0,sp,92
4200d39a:	f21ff0ef          	jal	4200d2ba <timer_snapshot>
4200d39e:	06a14783          	lbu	a5,106(sp)
4200d3a2:	d63e                	sw	a5,44(sp)
4200d3a4:	745020ef          	jal	420102e8 <network_connected>
4200d3a8:	45d1                	li	a1,20
4200d3aa:	8b2a                	mv	s6,a0
4200d3ac:	1968                	addi	a0,sp,188
4200d3ae:	76f020ef          	jal	4201031c <network_address>
4200d3b2:	4501                	li	a0,0
4200d3b4:	7f78f0ef          	jal	4209d3aa <time>
4200d3b8:	c62e                	sw	a1,12(sp)
4200d3ba:	4632                	lw	a2,12(sp)
4200d3bc:	c42a                	sw	a0,8(sp)
4200d3be:	85aa                	mv	a1,a0
4200d3c0:	19d4                	addi	a3,sp,244
4200d3c2:	2bb10513          	addi	a0,sp,699
4200d3c6:	540030ef          	jal	42010906 <services_local_time>
4200d3ca:	89aa                	mv	s3,a0
4200d3cc:	e91d                	bnez	a0,4200d402 <clock_task+0xe8>
4200d3ce:	4781                	li	a5,0
4200d3d0:	10f12823          	sw	a5,272(sp)
4200d3d4:	02800793          	li	a5,40
4200d3d8:	dbbe                	sw	a5,244(sp)
4200d3da:	4791                	li	a5,4
4200d3dc:	ddbe                	sw	a5,248(sp)
4200d3de:	47c5                	li	a5,17
4200d3e0:	dfbe                	sw	a5,252(sp)
4200d3e2:	47cd                	li	a5,19
4200d3e4:	10f12023          	sw	a5,256(sp)
4200d3e8:	47a1                	li	a5,8
4200d3ea:	10f12223          	sw	a5,260(sp)
4200d3ee:	07d00793          	li	a5,125
4200d3f2:	4801                	li	a6,0
4200d3f4:	10f12423          	sw	a5,264(sp)
4200d3f8:	4795                	li	a5,5
4200d3fa:	11012a23          	sw	a6,276(sp)
4200d3fe:	10f12623          	sw	a5,268(sp)
4200d402:	02400613          	li	a2,36
4200d406:	19cc                	addi	a1,sp,244
4200d408:	0988                	addi	a0,sp,208
4200d40a:	fe37a097          	auipc	ra,0xfe37a
4200d40e:	e30080e7          	jalr	-464(ra) # 4038723a <memcpy>
4200d412:	47d6                	lw	a5,84(sp)
4200d414:	4742                	lw	a4,16(sp)
4200d416:	4405                	li	s0,1
4200d418:	00e79e63          	bne	a5,a4,4200d434 <clock_task+0x11a>
4200d41c:	47d2                	lw	a5,20(sp)
4200d41e:	20812403          	lw	s0,520(sp)
4200d422:	8c1d                	sub	s0,s0,a5
4200d424:	57a2                	lw	a5,40(sp)
4200d426:	00803433          	snez	s0,s0
4200d42a:	0137c7b3          	xor	a5,a5,s3
4200d42e:	8c5d                	or	s0,s0,a5
4200d430:	0ff47413          	zext.b	s0,s0
4200d434:	000b0d63          	beqz	s6,4200d44e <clock_task+0x134>
4200d438:	11814783          	lbu	a5,280(sp)
4200d43c:	eb89                	bnez	a5,4200d44e <clock_task+0x134>
4200d43e:	683030ef          	jal	420112c0 <weather_request_active>
4200d442:	e511                	bnez	a0,4200d44e <clock_task+0x134>
4200d444:	000c1d63          	bnez	s8,4200d45e <clock_task+0x144>
4200d448:	637030ef          	jal	4201127e <weather_request_update>
4200d44c:	4c79                	li	s8,30
4200d44e:	07e020ef          	jal	4200f4cc <media_upload_active>
4200d452:	84aa                	mv	s1,a0
4200d454:	c519                	beqz	a0,4200d462 <clock_task+0x148>
4200d456:	4529                	li	a0,10
4200d458:	39d9f0ef          	jal	420acff4 <vTaskDelay>
4200d45c:	b71d                	j	4200d382 <clock_task+0x68>
4200d45e:	1c7d                	addi	s8,s8,-1
4200d460:	b7fd                	j	4200d44e <clock_task+0x134>
4200d462:	57b2                	lw	a5,44(sp)
4200d464:	10078263          	beqz	a5,4200d568 <clock_task+0x24e>
4200d468:	080b0d63          	beqz	s6,4200d502 <clock_task+0x1e8>
4200d46c:	00099763          	bnez	s3,4200d47a <clock_task+0x160>
4200d470:	35c14703          	lbu	a4,860(sp)
4200d474:	4789                	li	a5,2
4200d476:	08f71663          	bne	a4,a5,4200d502 <clock_task+0x1e8>
4200d47a:	fe37b097          	auipc	ra,0xfe37b
4200d47e:	9bc080e7          	jalr	-1604(ra) # 40387e36 <vPortEnterCritical>
4200d482:	004aa783          	lw	a5,4(s5)
4200d486:	000a8723          	sb	zero,14(s5)
4200d48a:	f7f7f793          	andi	a5,a5,-129
4200d48e:	00faa223          	sw	a5,4(s5)
4200d492:	fe37b097          	auipc	ra,0xfe37b
4200d496:	9d0080e7          	jalr	-1584(ra) # 40387e62 <vPortExitCritical>
4200d49a:	478d                	li	a5,3
4200d49c:	00f91763          	bne	s2,a5,4200d4aa <clock_task+0x190>
4200d4a0:	35c14783          	lbu	a5,860(sp)
4200d4a4:	5702                	lw	a4,32(sp)
4200d4a6:	0ee78163          	beq	a5,a4,4200d588 <clock_task+0x26e>
4200d4aa:	0f000693          	li	a3,240
4200d4ae:	4701                	li	a4,0
4200d4b0:	8636                	mv	a2,a3
4200d4b2:	4581                	li	a1,0
4200d4b4:	4501                	li	a0,0
4200d4b6:	fcaff0ef          	jal	4200cc80 <display_fill>
4200d4ba:	35c14703          	lbu	a4,860(sp)
4200d4be:	4789                	li	a5,2
4200d4c0:	442d                	li	s0,11
4200d4c2:	00f71563          	bne	a4,a5,4200d4cc <clock_task+0x1b2>
4200d4c6:	04010823          	sb	zero,80(sp)
4200d4ca:	443d                	li	s0,15
4200d4cc:	fe37b097          	auipc	ra,0xfe37b
4200d4d0:	96a080e7          	jalr	-1686(ra) # 40387e36 <vPortEnterCritical>
4200d4d4:	004aa783          	lw	a5,4(s5)
4200d4d8:	8fc1                	or	a5,a5,s0
4200d4da:	00faa223          	sw	a5,4(s5)
4200d4de:	fe37b097          	auipc	ra,0xfe37b
4200d4e2:	984080e7          	jalr	-1660(ra) # 40387e62 <vPortExitCritical>
4200d4e6:	35c14783          	lbu	a5,860(sp)
4200d4ea:	00fde863          	bltu	s11,a5,4200d4fa <clock_task+0x1e0>
4200d4ee:	465e                	lw	a2,212(sp)
4200d4f0:	45ee                	lw	a1,216(sp)
4200d4f2:	86ce                	mv	a3,s3
4200d4f4:	0c48                	addi	a0,sp,532
4200d4f6:	d77ff0ef          	jal	4200d26c <backlight_update>
4200d4fa:	4485                	li	s1,1
4200d4fc:	8426                	mv	s0,s1
4200d4fe:	4a01                	li	s4,0
4200d500:	a841                	j	4200d590 <clock_task+0x276>
4200d502:	06914403          	lbu	s0,105(sp)
4200d506:	47f2                	lw	a5,28(sp)
4200d508:	197d                	addi	s2,s2,-1
4200d50a:	01203933          	snez	s2,s2
4200d50e:	8f81                	sub	a5,a5,s0
4200d510:	00f037b3          	snez	a5,a5
4200d514:	0127e7b3          	or	a5,a5,s2
4200d518:	e799                	bnez	a5,4200d526 <clock_task+0x20c>
4200d51a:	5792                	lw	a5,36(sp)
4200d51c:	0167c7b3          	xor	a5,a5,s6
4200d520:	0ff7f793          	zext.b	a5,a5
4200d524:	cb91                	beqz	a5,4200d538 <clock_task+0x21e>
4200d526:	01603533          	snez	a0,s6
4200d52a:	40a00533          	neg	a0,a0
4200d52e:	197c                	addi	a5,sp,188
4200d530:	85a2                	mv	a1,s0
4200d532:	8d7d                	and	a0,a0,a5
4200d534:	635000ef          	jal	4200e368 <factory_draw_startup>
4200d538:	36114603          	lbu	a2,865(sp)
4200d53c:	08000593          	li	a1,128
4200d540:	1808                	addi	a0,sp,48
4200d542:	d79ff0ef          	jal	4200d2ba <timer_snapshot>
4200d546:	4905                	li	s2,1
4200d548:	ce22                	sw	s0,28(sp)
4200d54a:	47d6                	lw	a5,84(sp)
4200d54c:	4529                	li	a0,10
4200d54e:	11814d03          	lbu	s10,280(sp)
4200d552:	c83e                	sw	a5,16(sp)
4200d554:	20812783          	lw	a5,520(sp)
4200d558:	ca3e                	sw	a5,20(sp)
4200d55a:	29b9f0ef          	jal	420acff4 <vTaskDelay>
4200d55e:	4ca2                	lw	s9,8(sp)
4200d560:	4bb2                	lw	s7,12(sp)
4200d562:	d44e                	sw	s3,40(sp)
4200d564:	d25a                	sw	s6,36(sp)
4200d566:	bd31                	j	4200d382 <clock_task+0x68>
4200d568:	f20b19e3          	bnez	s6,4200d49a <clock_task+0x180>
4200d56c:	597020ef          	jal	42010302 <network_ap_active>
4200d570:	c901                	beqz	a0,4200d580 <clock_task+0x266>
4200d572:	4409                	li	s0,2
4200d574:	fc890be3          	beq	s2,s0,4200d54a <clock_task+0x230>
4200d578:	55b000ef          	jal	4200e2d2 <factory_draw_setup>
4200d57c:	8922                	mv	s2,s0
4200d57e:	b7f1                	j	4200d54a <clock_task+0x230>
4200d580:	478d                	li	a5,3
4200d582:	fcf914e3          	bne	s2,a5,4200d54a <clock_task+0x230>
4200d586:	bf29                	j	4200d4a0 <clock_task+0x186>
4200d588:	47e6                	lw	a5,88(sp)
4200d58a:	4762                	lw	a4,24(sp)
4200d58c:	f0e79fe3          	bne	a5,a4,4200d4aa <clock_task+0x190>
4200d590:	11814783          	lbu	a5,280(sp)
4200d594:	c399                	beqz	a5,4200d59a <clock_task+0x280>
4200d596:	000d1363          	bnez	s10,4200d59c <clock_task+0x282>
4200d59a:	4a01                	li	s4,0
4200d59c:	35c14783          	lbu	a5,860(sp)
4200d5a0:	eb91                	bnez	a5,4200d5b4 <clock_task+0x29a>
4200d5a2:	c4cd                	beqz	s1,4200d64c <clock_task+0x332>
4200d5a4:	36114603          	lbu	a2,865(sp)
4200d5a8:	4589                	li	a1,2
4200d5aa:	10e8                	addi	a0,sp,108
4200d5ac:	d0fff0ef          	jal	4200d2ba <timer_snapshot>
4200d5b0:	57c6                	lw	a5,112(sp)
4200d5b2:	e3cd                	bnez	a5,4200d654 <clock_task+0x33a>
4200d5b4:	35c14783          	lbu	a5,860(sp)
4200d5b8:	ebe9                	bnez	a5,4200d68a <clock_task+0x370>
4200d5ba:	35d14503          	lbu	a0,861(sp)
4200d5be:	04c020ef          	jal	4200f60a <media_animation_frames>
4200d5c2:	85aa                	mv	a1,a0
4200d5c4:	00e8                	addi	a0,sp,76
4200d5c6:	2655                	jal	4200d96a <factory_animation_next>
4200d5c8:	36114603          	lbu	a2,865(sp)
4200d5cc:	892a                	mv	s2,a0
4200d5ce:	45a1                	li	a1,8
4200d5d0:	18e8                	addi	a0,sp,124
4200d5d2:	ce9ff0ef          	jal	4200d2ba <timer_snapshot>
4200d5d6:	47a2                	lw	a5,8(sp)
4200d5d8:	4732                	lw	a4,12(sp)
4200d5da:	480a                	lw	a6,128(sp)
4200d5dc:	00fcc7b3          	xor	a5,s9,a5
4200d5e0:	00ebc733          	xor	a4,s7,a4
4200d5e4:	8fd9                	or	a5,a5,a4
4200d5e6:	01003833          	snez	a6,a6
4200d5ea:	00f037b3          	snez	a5,a5
4200d5ee:	00f867b3          	or	a5,a6,a5
4200d5f2:	e391                	bnez	a5,4200d5f6 <clock_task+0x2dc>
4200d5f4:	c041                	beqz	s0,4200d674 <clock_task+0x35a>
4200d5f6:	fff94713          	not	a4,s2
4200d5fa:	877d                	srai	a4,a4,0x1f
4200d5fc:	87a6                	mv	a5,s1
4200d5fe:	00e97733          	and	a4,s2,a4
4200d602:	86d2                	mv	a3,s4
4200d604:	0a30                	addi	a2,sp,280
4200d606:	098c                	addi	a1,sp,208
4200d608:	0c48                	addi	a0,sp,532
4200d60a:	627000ef          	jal	4200e430 <factory_draw_classic>
4200d60e:	427000ef          	jal	4200e234 <factory_scroll_tick>
4200d612:	35c14703          	lbu	a4,860(sp)
4200d616:	4789                	li	a5,2
4200d618:	00f70863          	beq	a4,a5,4200d628 <clock_task+0x30e>
4200d61c:	465e                	lw	a2,212(sp)
4200d61e:	45ee                	lw	a1,216(sp)
4200d620:	86ce                	mv	a3,s3
4200d622:	0c48                	addi	a0,sp,532
4200d624:	c49ff0ef          	jal	4200d26c <backlight_update>
4200d628:	35c14783          	lbu	a5,860(sp)
4200d62c:	36114603          	lbu	a2,865(sp)
4200d630:	04000593          	li	a1,64
4200d634:	d03e                	sw	a5,32(sp)
4200d636:	47e6                	lw	a5,88(sp)
4200d638:	1168                	addi	a0,sp,172
4200d63a:	cc3e                	sw	a5,24(sp)
4200d63c:	c7fff0ef          	jal	4200d2ba <timer_snapshot>
4200d640:	57ca                	lw	a5,176(sp)
4200d642:	c399                	beqz	a5,4200d648 <clock_task+0x32e>
4200d644:	43b030ef          	jal	4201127e <weather_request_update>
4200d648:	490d                	li	s2,3
4200d64a:	b701                	j	4200d54a <clock_task+0x230>
4200d64c:	465000ef          	jal	4200e2b0 <factory_scroll_description_ready>
4200d650:	f931                	bnez	a0,4200d5a4 <clock_task+0x28a>
4200d652:	b78d                	j	4200d5b4 <clock_task+0x29a>
4200d654:	e891                	bnez	s1,4200d668 <clock_task+0x34e>
4200d656:	11814783          	lbu	a5,280(sp)
4200d65a:	c799                	beqz	a5,4200d668 <clock_task+0x34e>
4200d65c:	000d0663          	beqz	s10,4200d668 <clock_task+0x34e>
4200d660:	0a05                	addi	s4,s4,1
4200d662:	47a9                	li	a5,10
4200d664:	02fa7a33          	remu	s4,s4,a5
4200d668:	f431                	bnez	s0,4200d5b4 <clock_task+0x29a>
4200d66a:	35c14403          	lbu	s0,860(sp)
4200d66e:	00143413          	seqz	s0,s0
4200d672:	b789                	j	4200d5b4 <clock_task+0x29a>
4200d674:	f8094de3          	bltz	s2,4200d60e <clock_task+0x2f4>
4200d678:	35d14503          	lbu	a0,861(sp)
4200d67c:	0a000693          	li	a3,160
4200d680:	8636                	mv	a2,a3
4200d682:	85ca                	mv	a1,s2
4200d684:	7e1010ef          	jal	4200f664 <media_draw_animation>
4200d688:	b759                	j	4200d60e <clock_task+0x2f4>
4200d68a:	03b79463          	bne	a5,s11,4200d6b2 <clock_task+0x398>
4200d68e:	36114603          	lbu	a2,865(sp)
4200d692:	0168                	addi	a0,sp,140
4200d694:	45a5                	li	a1,9
4200d696:	c25ff0ef          	jal	4200d2ba <timer_snapshot>
4200d69a:	474a                	lw	a4,144(sp)
4200d69c:	86a6                	mv	a3,s1
4200d69e:	1970                	addi	a2,sp,188
4200d6a0:	00375793          	srli	a5,a4,0x3
4200d6a4:	8b85                	andi	a5,a5,1
4200d6a6:	8b05                	andi	a4,a4,1
4200d6a8:	098c                	addi	a1,sp,208
4200d6aa:	0c48                	addi	a0,sp,532
4200d6ac:	38e010ef          	jal	4200ea3a <factory_draw_simple>
4200d6b0:	b78d                	j	4200d612 <clock_task+0x2f8>
4200d6b2:	4709                	li	a4,2
4200d6b4:	0ae79763          	bne	a5,a4,4200d762 <clock_task+0x448>
4200d6b8:	0c58                	addi	a4,sp,532
4200d6ba:	4781                	li	a5,0
4200d6bc:	4601                	li	a2,0
4200d6be:	4695                	li	a3,5
4200d6c0:	15872583          	lw	a1,344(a4)
4200d6c4:	c581                	beqz	a1,4200d6cc <clock_task+0x3b2>
4200d6c6:	00fd95b3          	sll	a1,s11,a5
4200d6ca:	8e4d                	or	a2,a2,a1
4200d6cc:	0785                	addi	a5,a5,1
4200d6ce:	0711                	addi	a4,a4,4
4200d6d0:	fed798e3          	bne	a5,a3,4200d6c0 <clock_task+0x3a6>
4200d6d4:	5686                	lw	a3,96(sp)
4200d6d6:	36814583          	lbu	a1,872(sp)
4200d6da:	19dc                	addi	a5,sp,244
4200d6dc:	8289                	srli	a3,a3,0x2
4200d6de:	8a85                	andi	a3,a3,1
4200d6e0:	8ec5                	or	a3,a3,s1
4200d6e2:	4701                	li	a4,0
4200d6e4:	0ff6f693          	zext.b	a3,a3
4200d6e8:	0888                	addi	a0,sp,80
4200d6ea:	2af9                	jal	4200d8c8 <factory_photo_step>
4200d6ec:	0f714783          	lbu	a5,247(sp)
4200d6f0:	c789                	beqz	a5,4200d6fa <clock_task+0x3e0>
4200d6f2:	0f415503          	lhu	a0,244(sp)
4200d6f6:	aa5ff0ef          	jal	4200d19a <backlight_set_level>
4200d6fa:	0f610503          	lb	a0,246(sp)
4200d6fe:	57fd                	li	a5,-1
4200d700:	02f54663          	blt	a0,a5,4200d72c <clock_task+0x412>
4200d704:	04f51b63          	bne	a0,a5,4200d75a <clock_task+0x440>
4200d708:	0f000693          	li	a3,240
4200d70c:	8636                	mv	a2,a3
4200d70e:	4701                	li	a4,0
4200d710:	4581                	li	a1,0
4200d712:	4501                	li	a0,0
4200d714:	d6cff0ef          	jal	4200cc80 <display_fill>
4200d718:	6741                	lui	a4,0x10
4200d71a:	4805                	li	a6,1
4200d71c:	4781                	li	a5,0
4200d71e:	177d                	addi	a4,a4,-1 # ffff <CSR_UINTSTATUS+0xf34e>
4200d720:	46c1                	li	a3,16
4200d722:	1970                	addi	a2,sp,188
4200d724:	0e100593          	li	a1,225
4200d728:	4515                	li	a0,5
4200d72a:	2355                	jal	4200dcce <display_factory_text>
4200d72c:	0f814783          	lbu	a5,248(sp)
4200d730:	c799                	beqz	a5,4200d73e <clock_task+0x424>
4200d732:	36114603          	lbu	a2,865(sp)
4200d736:	4591                	li	a1,4
4200d738:	1808                	addi	a0,sp,48
4200d73a:	b81ff0ef          	jal	4200d2ba <timer_snapshot>
4200d73e:	0f714783          	lbu	a5,247(sp)
4200d742:	c789                	beqz	a5,4200d74c <clock_task+0x432>
4200d744:	0f814783          	lbu	a5,248(sp)
4200d748:	ec0785e3          	beqz	a5,4200d612 <clock_task+0x2f8>
4200d74c:	465e                	lw	a2,212(sp)
4200d74e:	45ee                	lw	a1,216(sp)
4200d750:	86ce                	mv	a3,s3
4200d752:	0c48                	addi	a0,sp,532
4200d754:	b19ff0ef          	jal	4200d26c <backlight_update>
4200d758:	bd6d                	j	4200d612 <clock_task+0x2f8>
4200d75a:	196c                	addi	a1,sp,188
4200d75c:	1f9010ef          	jal	4200f154 <factory_draw_photo>
4200d760:	b7f1                	j	4200d72c <clock_task+0x412>
4200d762:	36114603          	lbu	a2,865(sp)
4200d766:	4585                	li	a1,1
4200d768:	0968                	addi	a0,sp,156
4200d76a:	b51ff0ef          	jal	4200d2ba <timer_snapshot>
4200d76e:	578a                	lw	a5,160(sp)
4200d770:	00f037b3          	snez	a5,a5
4200d774:	8fc5                	or	a5,a5,s1
4200d776:	0ff7f793          	zext.b	a5,a5
4200d77a:	e399                	bnez	a5,4200d780 <clock_task+0x466>
4200d77c:	e8040be3          	beqz	s0,4200d612 <clock_task+0x2f8>
4200d780:	8626                	mv	a2,s1
4200d782:	196c                	addi	a1,sp,188
4200d784:	0988                	addi	a0,sp,208
4200d786:	4d6010ef          	jal	4200ec5c <factory_draw_dial>
4200d78a:	b561                	j	4200d612 <clock_task+0x2f8>


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42011f7c <web_settings_post>:
42011f7c:	7101                	addi	sp,sp,-512
42011f7e:	1e912a23          	sw	s1,500(sp)
42011f82:	84aa                	mv	s1,a0
42011f84:	18c8                	addi	a0,sp,116
42011f86:	1e112e23          	sw	ra,508(sp)
42011f8a:	1e812c23          	sw	s0,504(sp)
42011f8e:	1f212823          	sw	s2,496(sp)
42011f92:	1f312623          	sw	s3,492(sp)
42011f96:	1f412423          	sw	s4,488(sp)
42011f9a:	1f512223          	sw	s5,484(sp)
42011f9e:	1f612023          	sw	s6,480(sp)
42011fa2:	d62fa0ef          	jal	4200c504 <settings_snapshot>
42011fa6:	3c0b45b7          	lui	a1,0x3c0b4
42011faa:	65058593          	addi	a1,a1,1616 # 3c0b4650 <_esp_libc_clock_array_end+0x4500>
42011fae:	00848513          	addi	a0,s1,8
42011fb2:	fe375097          	auipc	ra,0xfe375
42011fb6:	6a0080e7          	jalr	1696(ra) # 40387652 <strcmp>
42011fba:	ed31                	bnez	a0,42012016 <web_settings_post+0x9a>
42011fbc:	20c4a783          	lw	a5,524(s1)
42011fc0:	c7a9                	beqz	a5,4201200a <web_settings_post+0x8e>
42011fc2:	08000593          	li	a1,128
42011fc6:	8526                	mv	a0,s1
42011fc8:	9b3ff0ef          	jal	4201197a <web_body>
42011fcc:	e91d                	bnez	a0,42012002 <web_settings_post+0x86>
42011fce:	3c0b55b7          	lui	a1,0x3c0b5
42011fd2:	88858593          	addi	a1,a1,-1912 # 3c0b4888 <_esp_libc_clock_array_end+0x4738>
42011fd6:	8526                	mv	a0,s1
42011fd8:	8d5ff0ef          	jal	420118ac <web_error>
42011fdc:	1fc12083          	lw	ra,508(sp)
42011fe0:	1f812403          	lw	s0,504(sp)
42011fe4:	1f412483          	lw	s1,500(sp)
42011fe8:	1f012903          	lw	s2,496(sp)
42011fec:	1ec12983          	lw	s3,492(sp)
42011ff0:	1e812a03          	lw	s4,488(sp)
42011ff4:	1e412a83          	lw	s5,484(sp)
42011ff8:	1e012b03          	lw	s6,480(sp)
42011ffc:	20010113          	addi	sp,sp,512
42012000:	8082                	ret
42012002:	fe375097          	auipc	ra,0xfe375
42012006:	1c0080e7          	jalr	448(ra) # 403871c2 <cfree>
4201200a:	c0cfe0ef          	jal	42010416 <network_restart_later>
4201200e:	8526                	mv	a0,s1
42012010:	8d5ff0ef          	jal	420118e4 <web_ok>
42012014:	b7e1                	j	42011fdc <web_settings_post+0x60>
42012016:	3c0b45b7          	lui	a1,0x3c0b4
4201201a:	70458593          	addi	a1,a1,1796 # 3c0b4704 <_esp_libc_clock_array_end+0x45b4>
4201201e:	00848513          	addi	a0,s1,8
42012022:	fe375097          	auipc	ra,0xfe375
42012026:	630080e7          	jalr	1584(ra) # 40387652 <strcmp>
4201202a:	89aa                	mv	s3,a0
4201202c:	c92d                	beqz	a0,4201209e <web_settings_post+0x122>
4201202e:	3c0b45b7          	lui	a1,0x3c0b4
42012032:	6ac58593          	addi	a1,a1,1708 # 3c0b46ac <_esp_libc_clock_array_end+0x455c>
42012036:	00848513          	addi	a0,s1,8
4201203a:	fe375097          	auipc	ra,0xfe375
4201203e:	618080e7          	jalr	1560(ra) # 40387652 <strcmp>
42012042:	e945                	bnez	a0,420120f2 <web_settings_post+0x176>
42012044:	3c0b5937          	lui	s2,0x3c0b5
42012048:	87890913          	addi	s2,s2,-1928 # 3c0b4878 <_esp_libc_clock_array_end+0x4728>
4201204c:	08000593          	li	a1,128
42012050:	8526                	mv	a0,s1
42012052:	929ff0ef          	jal	4201197a <web_body>
42012056:	8a2a                	mv	s4,a0
42012058:	20050663          	beqz	a0,42012264 <web_settings_post+0x2e8>
4201205c:	20c4a603          	lw	a2,524(s1)
42012060:	4581                	li	a1,0
42012062:	fdfee097          	auipc	ra,0xfdfee
42012066:	49a080e7          	jalr	1178(ra) # 400004fc <memchr>
4201206a:	cd1d                	beqz	a0,420120a8 <web_settings_post+0x12c>
4201206c:	4901                	li	s2,0
4201206e:	8552                	mv	a0,s4
42012070:	fe375097          	auipc	ra,0xfe375
42012074:	152080e7          	jalr	338(ra) # 403871c2 <cfree>
42012078:	1e090663          	beqz	s2,42012264 <web_settings_post+0x2e8>
4201207c:	47a9                	li	a5,10
4201207e:	02f40433          	mul	s0,s0,a5
42012082:	3e800793          	li	a5,1000
42012086:	40878433          	sub	s0,a5,s0
4201208a:	06099163          	bnez	s3,420120ec <web_settings_post+0x170>
4201208e:	1a811923          	sh	s0,434(sp)
42012092:	4901                	li	s2,0
42012094:	4981                	li	s3,0
42012096:	18c8                	addi	a0,sp,116
42012098:	d00fa0ef          	jal	4200c598 <settings_replace>
4201209c:	a2d1                	j	42012260 <web_settings_post+0x2e4>
4201209e:	3c0b5937          	lui	s2,0x3c0b5
420120a2:	86890913          	addi	s2,s2,-1944 # 3c0b4868 <_esp_libc_clock_array_end+0x4718>
420120a6:	b75d                	j	4201204c <web_settings_post+0xd0>
420120a8:	46a1                	li	a3,8
420120aa:	0870                	addi	a2,sp,28
420120ac:	85ca                	mv	a1,s2
420120ae:	8552                	mv	a0,s4
420120b0:	5b0260ef          	jal	42038660 <httpd_query_key_value>
420120b4:	fd45                	bnez	a0,4201206c <web_settings_post+0xf0>
420120b6:	01c14783          	lbu	a5,28(sp)
420120ba:	dbcd                	beqz	a5,4201206c <web_settings_post+0xf0>
420120bc:	0878                	addi	a4,sp,28
420120be:	4905                	li	s2,1
420120c0:	a801                	j	420120d0 <web_settings_post+0x154>
420120c2:	fd078793          	addi	a5,a5,-48
420120c6:	00a7b793          	sltiu	a5,a5,10
420120ca:	00f97933          	and	s2,s2,a5
420120ce:	0705                	addi	a4,a4,1
420120d0:	00074783          	lbu	a5,0(a4)
420120d4:	f7fd                	bnez	a5,420120c2 <web_settings_post+0x146>
420120d6:	4629                	li	a2,10
420120d8:	4581                	li	a1,0
420120da:	0868                	addi	a0,sp,28
420120dc:	4fc8c0ef          	jal	4209e5d8 <strtoul>
420120e0:	06553793          	sltiu	a5,a0,101
420120e4:	842a                	mv	s0,a0
420120e6:	00f97933          	and	s2,s2,a5
420120ea:	b751                	j	4201206e <web_settings_post+0xf2>
420120ec:	1a811a23          	sh	s0,436(sp)
420120f0:	b74d                	j	42012092 <web_settings_post+0x116>
420120f2:	8526                	mv	a0,s1
420120f4:	987ff0ef          	jal	42011a7a <web_parse_json>
420120f8:	8aaa                	mv	s5,a0
420120fa:	e511                	bnez	a0,42012106 <web_settings_post+0x18a>
420120fc:	3c0b55b7          	lui	a1,0x3c0b5
42012100:	89858593          	addi	a1,a1,-1896 # 3c0b4898 <_esp_libc_clock_array_end+0x4748>
42012104:	bdc9                	j	42011fd6 <web_settings_post+0x5a>
42012106:	3c0eb937          	lui	s2,0x3c0eb
4201210a:	54490913          	addi	s2,s2,1348 # 3c0eb544 <integers>
4201210e:	09090993          	addi	s3,s2,144
42012112:	4a01                	li	s4,0
42012114:	4401                	li	s0,0
42012116:	00492583          	lw	a1,4(s2)
4201211a:	00848513          	addi	a0,s1,8
4201211e:	fe375097          	auipc	ra,0xfe375
42012122:	534080e7          	jalr	1332(ra) # 40387652 <strcmp>
42012126:	e131                	bnez	a0,4201216a <web_settings_post+0x1ee>
42012128:	01492683          	lw	a3,20(s2)
4201212c:	01092603          	lw	a2,16(s2)
42012130:	00892583          	lw	a1,8(s2)
42012134:	0878                	addi	a4,sp,28
42012136:	8556                	mv	a0,s5
42012138:	98fff0ef          	jal	42011ac6 <web_integer>
4201213c:	842a                	mv	s0,a0
4201213e:	c515                	beqz	a0,4201216a <web_settings_post+0x1ee>
42012140:	00c92783          	lw	a5,12(s2)
42012144:	0818                	addi	a4,sp,16
42012146:	3c0b45b7          	lui	a1,0x3c0b4
4201214a:	1d078793          	addi	a5,a5,464
4201214e:	97ba                	add	a5,a5,a4
42012150:	4772                	lw	a4,28(sp)
42012152:	78c58593          	addi	a1,a1,1932 # 3c0b478c <_esp_libc_clock_array_end+0x463c>
42012156:	00848513          	addi	a0,s1,8
4201215a:	e8e78a23          	sb	a4,-364(a5)
4201215e:	fe375097          	auipc	ra,0xfe375
42012162:	4f4080e7          	jalr	1268(ra) # 40387652 <strcmp>
42012166:	00153a13          	seqz	s4,a0
4201216a:	0961                	addi	s2,s2,24
4201216c:	fb3915e3          	bne	s2,s3,42012116 <web_settings_post+0x19a>
42012170:	3c0b45b7          	lui	a1,0x3c0b4
42012174:	77058593          	addi	a1,a1,1904 # 3c0b4770 <_esp_libc_clock_array_end+0x4620>
42012178:	00848513          	addi	a0,s1,8
4201217c:	fe375097          	auipc	ra,0xfe375
42012180:	4d6080e7          	jalr	1238(ra) # 40387652 <strcmp>
42012184:	e531                	bnez	a0,420121d0 <web_settings_post+0x254>
42012186:	3c0eb937          	lui	s2,0x3c0eb
4201218a:	51c90913          	addi	s2,s2,1308 # 3c0eb51c <switches>
4201218e:	02890993          	addi	s3,s2,40
42012192:	4401                	li	s0,0
42012194:	00092583          	lw	a1,0(s2)
42012198:	8556                	mv	a0,s5
4201219a:	c62e                	sw	a1,12(sp)
4201219c:	4b1020ef          	jal	42014e4c <cJSON_HasObjectItem>
420121a0:	45b2                	lw	a1,12(sp)
420121a2:	c115                	beqz	a0,420121c6 <web_settings_post+0x24a>
420121a4:	0878                	addi	a4,sp,28
420121a6:	4685                	li	a3,1
420121a8:	4601                	li	a2,0
420121aa:	8556                	mv	a0,s5
420121ac:	91bff0ef          	jal	42011ac6 <web_integer>
420121b0:	842a                	mv	s0,a0
420121b2:	cd09                	beqz	a0,420121cc <web_settings_post+0x250>
420121b4:	00492783          	lw	a5,4(s2)
420121b8:	0818                	addi	a4,sp,16
420121ba:	1d078793          	addi	a5,a5,464
420121be:	97ba                	add	a5,a5,a4
420121c0:	4772                	lw	a4,28(sp)
420121c2:	e8e78a23          	sb	a4,-364(a5)
420121c6:	0921                	addi	s2,s2,8
420121c8:	fd2996e3          	bne	s3,s2,42012194 <web_settings_post+0x218>
420121cc:	4981                	li	s3,0
420121ce:	aa11                	j	420122e2 <web_settings_post+0x366>
420121d0:	3c0b45b7          	lui	a1,0x3c0b4
420121d4:	7c458593          	addi	a1,a1,1988 # 3c0b47c4 <_esp_libc_clock_array_end+0x4674>
420121d8:	00848513          	addi	a0,s1,8
420121dc:	fe375097          	auipc	ra,0xfe375
420121e0:	476080e7          	jalr	1142(ra) # 40387652 <strcmp>
420121e4:	cd01                	beqz	a0,420121fc <web_settings_post+0x280>
420121e6:	3c0b45b7          	lui	a1,0x3c0b4
420121ea:	63458593          	addi	a1,a1,1588 # 3c0b4634 <_esp_libc_clock_array_end+0x44e4>
420121ee:	00848513          	addi	a0,s1,8
420121f2:	fe375097          	auipc	ra,0xfe375
420121f6:	460080e7          	jalr	1120(ra) # 40387652 <strcmp>
420121fa:	e141                	bnez	a0,4201227a <web_settings_post+0x2fe>
420121fc:	3c0bf5b7          	lui	a1,0x3c0bf
42012200:	02100693          	li	a3,33
42012204:	18b0                	addi	a2,sp,120
42012206:	1e058593          	addi	a1,a1,480 # 3c0bf1e0 <_esp_libc_clock_array_end+0xf090>
4201220a:	8556                	mv	a0,s5
4201220c:	acdff0ef          	jal	42011cd8 <copy_string>
42012210:	c91d                	beqz	a0,42012246 <web_settings_post+0x2ca>
42012212:	07814783          	lbu	a5,120(sp)
42012216:	cb85                	beqz	a5,42012246 <web_settings_post+0x2ca>
42012218:	3c0b55b7          	lui	a1,0x3c0b5
4201221c:	04100693          	li	a3,65
42012220:	09910613          	addi	a2,sp,153
42012224:	8b858593          	addi	a1,a1,-1864 # 3c0b48b8 <_esp_libc_clock_array_end+0x4768>
42012228:	8556                	mv	a0,s5
4201222a:	aafff0ef          	jal	42011cd8 <copy_string>
4201222e:	842a                	mv	s0,a0
42012230:	c919                	beqz	a0,42012246 <web_settings_post+0x2ca>
42012232:	09910513          	addi	a0,sp,153
42012236:	fdfee097          	auipc	ra,0xfdfee
4201223a:	272080e7          	jalr	626(ra) # 400004a8 <strlen>
4201223e:	157d                	addi	a0,a0,-1
42012240:	4799                	li	a5,6
42012242:	02a7e663          	bltu	a5,a0,4201226e <web_settings_post+0x2f2>
42012246:	4981                	li	s3,0
42012248:	4901                	li	s2,0
4201224a:	4401                	li	s0,0
4201224c:	8556                	mv	a0,s5
4201224e:	6b0020ef          	jal	420148fe <cJSON_Delete>
42012252:	c809                	beqz	s0,42012264 <web_settings_post+0x2e8>
42012254:	e40a01e3          	beqz	s4,42012096 <web_settings_post+0x11a>
42012258:	1bc14503          	lbu	a0,444(sp)
4201225c:	ab0fa0ef          	jal	4200c50c <settings_select_theme>
42012260:	2e050063          	beqz	a0,42012540 <web_settings_post+0x5c4>
42012264:	3c0b55b7          	lui	a1,0x3c0b5
42012268:	92058593          	addi	a1,a1,-1760 # 3c0b4920 <_esp_libc_clock_array_end+0x47d0>
4201226c:	b3ad                	j	42011fd6 <web_settings_post+0x5a>
4201226e:	4785                	li	a5,1
42012270:	1cf104a3          	sb	a5,457(sp)
42012274:	8922                	mv	s2,s0
42012276:	4981                	li	s3,0
42012278:	bfd1                	j	4201224c <web_settings_post+0x2d0>
4201227a:	3c0b45b7          	lui	a1,0x3c0b4
4201227e:	64058593          	addi	a1,a1,1600 # 3c0b4640 <_esp_libc_clock_array_end+0x44f0>
42012282:	00848513          	addi	a0,s1,8
42012286:	fe375097          	auipc	ra,0xfe375
4201228a:	3cc080e7          	jalr	972(ra) # 40387652 <strcmp>
4201228e:	ed21                	bnez	a0,420122e6 <web_settings_post+0x36a>
42012290:	3c0b55b7          	lui	a1,0x3c0b5
42012294:	04100693          	li	a3,65
42012298:	12f10613          	addi	a2,sp,303
4201229c:	8c458593          	addi	a1,a1,-1852 # 3c0b48c4 <_esp_libc_clock_array_end+0x4774>
420122a0:	8556                	mv	a0,s5
420122a2:	a37ff0ef          	jal	42011cd8 <copy_string>
420122a6:	e119                	bnez	a0,420122ac <web_settings_post+0x330>
420122a8:	4401                	li	s0,0
420122aa:	a81d                	j	420122e0 <web_settings_post+0x364>
420122ac:	3c0b55b7          	lui	a1,0x3c0b5
420122b0:	04100693          	li	a3,65
420122b4:	1a90                	addi	a2,sp,368
420122b6:	8c858593          	addi	a1,a1,-1848 # 3c0b48c8 <_esp_libc_clock_array_end+0x4778>
420122ba:	8556                	mv	a0,s5
420122bc:	a1dff0ef          	jal	42011cd8 <copy_string>
420122c0:	d565                	beqz	a0,420122a8 <web_settings_post+0x32c>
420122c2:	3c0b55b7          	lui	a1,0x3c0b5
420122c6:	0878                	addi	a4,sp,28
420122c8:	46a9                	li	a3,10
420122ca:	4601                	li	a2,0
420122cc:	8dc58593          	addi	a1,a1,-1828 # 3c0b48dc <_esp_libc_clock_array_end+0x478c>
420122d0:	8556                	mv	a0,s5
420122d2:	ff4ff0ef          	jal	42011ac6 <web_integer>
420122d6:	842a                	mv	s0,a0
420122d8:	d961                	beqz	a0,420122a8 <web_settings_post+0x32c>
420122da:	47f2                	lw	a5,28(sp)
420122dc:	1cf103a3          	sb	a5,455(sp)
420122e0:	89a2                	mv	s3,s0
420122e2:	4901                	li	s2,0
420122e4:	b7a5                	j	4201224c <web_settings_post+0x2d0>
420122e6:	3c0b45b7          	lui	a1,0x3c0b4
420122ea:	72c58593          	addi	a1,a1,1836 # 3c0b472c <_esp_libc_clock_array_end+0x45dc>
420122ee:	00848513          	addi	a0,s1,8
420122f2:	fe375097          	auipc	ra,0xfe375
420122f6:	360080e7          	jalr	864(ra) # 40387652 <strcmp>
420122fa:	e95d                	bnez	a0,420123b0 <web_settings_post+0x434>
420122fc:	3c0b55b7          	lui	a1,0x3c0b5
42012300:	05700693          	li	a3,87
42012304:	0870                	addi	a2,sp,28
42012306:	8e858593          	addi	a1,a1,-1816 # 3c0b48e8 <_esp_libc_clock_array_end+0x4798>
4201230a:	8556                	mv	a0,s5
4201230c:	9cdff0ef          	jal	42011cd8 <copy_string>
42012310:	dd41                	beqz	a0,420122a8 <web_settings_post+0x32c>
42012312:	02c00593          	li	a1,44
42012316:	0868                	addi	a0,sp,28
42012318:	fdfee097          	auipc	ra,0xfdfee
4201231c:	224080e7          	jalr	548(ra) # 4000053c <strrchr>
42012320:	892a                	mv	s2,a0
42012322:	4985                	li	s3,1
42012324:	ed09                	bnez	a0,4201233e <web_settings_post+0x3c2>
42012326:	3c0b55b7          	lui	a1,0x3c0b5
4201232a:	8f058593          	addi	a1,a1,-1808 # 3c0b48f0 <_esp_libc_clock_array_end+0x47a0>
4201232e:	0868                	addi	a0,sp,28
42012330:	fdfee097          	auipc	ra,0xfdfee
42012334:	17c080e7          	jalr	380(ra) # 400004ac <strstr>
42012338:	892a                	mv	s2,a0
4201233a:	d53d                	beqz	a0,420122a8 <web_settings_post+0x32c>
4201233c:	498d                	li	s3,3
4201233e:	99ca                	add	s3,s3,s2
42012340:	854e                	mv	a0,s3
42012342:	fdfee097          	auipc	ra,0xfdfee
42012346:	166080e7          	jalr	358(ra) # 400004a8 <strlen>
4201234a:	47cd                	li	a5,19
4201234c:	f4a7eee3          	bltu	a5,a0,420122a8 <web_settings_post+0x32c>
42012350:	854e                	mv	a0,s3
42012352:	bb7f90ef          	jal	4200bf08 <settings_country_valid>
42012356:	842a                	mv	s0,a0
42012358:	d921                	beqz	a0,420122a8 <web_settings_post+0x32c>
4201235a:	00090023          	sb	zero,0(s2)
4201235e:	0868                	addi	a0,sp,28
42012360:	fdfee097          	auipc	ra,0xfdfee
42012364:	148080e7          	jalr	328(ra) # 400004a8 <strlen>
42012368:	157d                	addi	a0,a0,-1
4201236a:	03f00793          	li	a5,63
4201236e:	f2a7ede3          	bltu	a5,a0,420122a8 <web_settings_post+0x32c>
42012372:	086c                	addi	a1,sp,28
42012374:	0da10513          	addi	a0,sp,218
42012378:	fe375097          	auipc	ra,0xfe375
4201237c:	3f0080e7          	jalr	1008(ra) # 40387768 <strcpy>
42012380:	854e                	mv	a0,s3
42012382:	fdfee097          	auipc	ra,0xfdfee
42012386:	126080e7          	jalr	294(ra) # 400004a8 <strlen>
4201238a:	18d4                	addi	a3,sp,116
4201238c:	4781                	li	a5,0
4201238e:	4665                	li	a2,25
42012390:	00f98733          	add	a4,s3,a5
42012394:	00074703          	lbu	a4,0(a4)
42012398:	f9f70593          	addi	a1,a4,-97
4201239c:	00b66363          	bltu	a2,a1,420123a2 <web_settings_post+0x426>
420123a0:	1701                	addi	a4,a4,-32
420123a2:	0ae683a3          	sb	a4,167(a3)
420123a6:	0785                	addi	a5,a5,1
420123a8:	0685                	addi	a3,a3,1
420123aa:	fef573e3          	bgeu	a0,a5,42012390 <web_settings_post+0x414>
420123ae:	bf0d                	j	420122e0 <web_settings_post+0x364>
420123b0:	3c0b45b7          	lui	a1,0x3c0b4
420123b4:	6dc58593          	addi	a1,a1,1756 # 3c0b46dc <_esp_libc_clock_array_end+0x458c>
420123b8:	00848513          	addi	a0,s1,8
420123bc:	fe375097          	auipc	ra,0xfe375
420123c0:	296080e7          	jalr	662(ra) # 40387652 <strcmp>
420123c4:	e945                	bnez	a0,42012474 <web_settings_post+0x4f8>
420123c6:	3c0b55b7          	lui	a1,0x3c0b5
420123ca:	8f458593          	addi	a1,a1,-1804 # 3c0b48f4 <_esp_libc_clock_array_end+0x47a4>
420123ce:	8556                	mv	a0,s5
420123d0:	277020ef          	jal	42014e46 <cJSON_GetObjectItemCaseSensitive>
420123d4:	3c0ba5b7          	lui	a1,0x3c0ba
420123d8:	892a                	mv	s2,a0
420123da:	0878                	addi	a4,sp,28
420123dc:	4689                	li	a3,2
420123de:	4601                	li	a2,0
420123e0:	86458593          	addi	a1,a1,-1948 # 3c0b9864 <_esp_libc_clock_array_end+0x9714>
420123e4:	8556                	mv	a0,s5
420123e6:	ee0ff0ef          	jal	42011ac6 <web_integer>
420123ea:	842a                	mv	s0,a0
420123ec:	e119                	bnez	a0,420123f2 <web_settings_post+0x476>
420123ee:	4401                	li	s0,0
420123f0:	bbf1                	j	420121cc <web_settings_post+0x250>
420123f2:	854a                	mv	a0,s2
420123f4:	451020ef          	jal	42015044 <cJSON_IsString>
420123f8:	d97d                	beqz	a0,420123ee <web_settings_post+0x472>
420123fa:	01092903          	lw	s2,16(s2)
420123fe:	854a                	mv	a0,s2
42012400:	fdfee097          	auipc	ra,0xfdfee
42012404:	0a8080e7          	jalr	168(ra) # 400004a8 <strlen>
42012408:	479d                	li	a5,7
4201240a:	fef512e3          	bne	a0,a5,420123ee <web_settings_post+0x472>
4201240e:	00094703          	lbu	a4,0(s2)
42012412:	02300793          	li	a5,35
42012416:	fcf71ce3          	bne	a4,a5,420123ee <web_settings_post+0x472>
4201241a:	4705                	li	a4,1
4201241c:	4625                	li	a2,9
4201241e:	4595                	li	a1,5
42012420:	86aa                	mv	a3,a0
42012422:	00e907b3          	add	a5,s2,a4
42012426:	0007c783          	lbu	a5,0(a5)
4201242a:	fd078513          	addi	a0,a5,-48
4201242e:	00a67b63          	bgeu	a2,a0,42012444 <web_settings_post+0x4c8>
42012432:	fbf78513          	addi	a0,a5,-65
42012436:	00a5f763          	bgeu	a1,a0,42012444 <web_settings_post+0x4c8>
4201243a:	f9f78793          	addi	a5,a5,-97
4201243e:	0067b793          	sltiu	a5,a5,6
42012442:	8c7d                	and	s0,s0,a5
42012444:	0705                	addi	a4,a4,1
42012446:	fcd71ee3          	bne	a4,a3,42012422 <web_settings_post+0x4a6>
4201244a:	d055                	beqz	s0,420123ee <web_settings_post+0x472>
4201244c:	4641                	li	a2,16
4201244e:	4581                	li	a1,0
42012450:	00190513          	addi	a0,s2,1
42012454:	1848c0ef          	jal	4209e5d8 <strtoul>
42012458:	4972                	lw	s2,28(sp)
4201245a:	a61f90ef          	jal	4200beba <rgb565_from_rgb888>
4201245e:	0818                	addi	a4,sp,16
42012460:	0a090913          	addi	s2,s2,160
42012464:	0906                	slli	s2,s2,0x1
42012466:	1d090793          	addi	a5,s2,464
4201246a:	00e78933          	add	s2,a5,a4
4201246e:	e8a91b23          	sh	a0,-362(s2)
42012472:	bba9                	j	420121cc <web_settings_post+0x250>
42012474:	3c0b45b7          	lui	a1,0x3c0b4
42012478:	5e458593          	addi	a1,a1,1508 # 3c0b45e4 <_esp_libc_clock_array_end+0x4494>
4201247c:	00848513          	addi	a0,s1,8
42012480:	fe375097          	auipc	ra,0xfe375
42012484:	1d2080e7          	jalr	466(ra) # 40387652 <strcmp>
42012488:	d40512e3          	bnez	a0,420121cc <web_settings_post+0x250>
4201248c:	3c0b55b7          	lui	a1,0x3c0b5
42012490:	8fc58593          	addi	a1,a1,-1796 # 3c0b48fc <_esp_libc_clock_array_end+0x47ac>
42012494:	8556                	mv	a0,s5
42012496:	1b1020ef          	jal	42014e46 <cJSON_GetObjectItemCaseSensitive>
4201249a:	3c0b55b7          	lui	a1,0x3c0b5
4201249e:	842a                	mv	s0,a0
420124a0:	90858593          	addi	a1,a1,-1784 # 3c0b4908 <_esp_libc_clock_array_end+0x47b8>
420124a4:	8556                	mv	a0,s5
420124a6:	1a1020ef          	jal	42014e46 <cJSON_GetObjectItemCaseSensitive>
420124aa:	892a                	mv	s2,a0
420124ac:	8522                	mv	a0,s0
420124ae:	397020ef          	jal	42015044 <cJSON_IsString>
420124b2:	d8050ae3          	beqz	a0,42012246 <web_settings_post+0x2ca>
420124b6:	854a                	mv	a0,s2
420124b8:	373020ef          	jal	4201502a <cJSON_IsBool>
420124bc:	d80505e3          	beqz	a0,42012246 <web_settings_post+0x2ca>
420124c0:	4800                	lw	s0,16(s0)
420124c2:	8522                	mv	a0,s0
420124c4:	fdfee097          	auipc	ra,0xfdfee
420124c8:	fe4080e7          	jalr	-28(ra) # 400004a8 <strlen>
420124cc:	47b1                	li	a5,12
420124ce:	d6f51ce3          	bne	a0,a5,42012246 <web_settings_post+0x2ca>
420124d2:	3c0b55b7          	lui	a1,0x3c0b5
420124d6:	4611                	li	a2,4
420124d8:	91058593          	addi	a1,a1,-1776 # 3c0b4910 <_esp_libc_clock_array_end+0x47c0>
420124dc:	8522                	mv	a0,s0
420124de:	fe375097          	auipc	ra,0xfe375
420124e2:	d1e080e7          	jalr	-738(ra) # 403871fc <memcmp>
420124e6:	d60510e3          	bnez	a0,42012246 <web_settings_post+0x2ca>
420124ea:	3c0b55b7          	lui	a1,0x3c0b5
420124ee:	91858593          	addi	a1,a1,-1768 # 3c0b4918 <_esp_libc_clock_array_end+0x47c8>
420124f2:	00540513          	addi	a0,s0,5
420124f6:	fe375097          	auipc	ra,0xfe375
420124fa:	15c080e7          	jalr	348(ra) # 40387652 <strcmp>
420124fe:	d40514e3          	bnez	a0,42012246 <web_settings_post+0x2ca>
42012502:	00444403          	lbu	s0,4(s0)
42012506:	4791                	li	a5,4
42012508:	fcf40413          	addi	s0,s0,-49
4201250c:	0ff47713          	zext.b	a4,s0
42012510:	d2e7ebe3          	bltu	a5,a4,42012246 <web_settings_post+0x2ca>
42012514:	854a                	mv	a0,s2
42012516:	307020ef          	jal	4201501c <cJSON_IsTrue>
4201251a:	4785                	li	a5,1
4201251c:	008797b3          	sll	a5,a5,s0
42012520:	1c814703          	lbu	a4,456(sp)
42012524:	0ff7f793          	zext.b	a5,a5
42012528:	c901                	beqz	a0,42012538 <web_settings_post+0x5bc>
4201252a:	8f5d                	or	a4,a4,a5
4201252c:	1ce10423          	sb	a4,456(sp)
42012530:	4981                	li	s3,0
42012532:	4901                	li	s2,0
42012534:	4405                	li	s0,1
42012536:	bb19                	j	4201224c <web_settings_post+0x2d0>
42012538:	fff7c793          	not	a5,a5
4201253c:	8f7d                	and	a4,a4,a5
4201253e:	b7fd                	j	4201252c <web_settings_post+0x5b0>
42012540:	00098463          	beqz	s3,42012548 <web_settings_post+0x5cc>
42012544:	d3bfe0ef          	jal	4201127e <weather_request_update>
42012548:	00090463          	beqz	s2,42012550 <web_settings_post+0x5d4>
4201254c:	ecbfd0ef          	jal	42010416 <network_restart_later>
42012550:	3c0b45b7          	lui	a1,0x3c0b4
42012554:	64058593          	addi	a1,a1,1600 # 3c0b4640 <_esp_libc_clock_array_end+0x44f0>
42012558:	00848513          	addi	a0,s1,8
4201255c:	fe375097          	auipc	ra,0xfe375
42012560:	0f6080e7          	jalr	246(ra) # 40387652 <strcmp>
42012564:	aa0515e3          	bnez	a0,4201200e <web_settings_post+0x92>
42012568:	3c0b55b7          	lui	a1,0x3c0b5
4201256c:	567d                	li	a2,-1
4201256e:	93c58593          	addi	a1,a1,-1732 # 3c0b493c <_esp_libc_clock_array_end+0x47ec>
42012572:	8526                	mv	a0,s1
42012574:	3f5260ef          	jal	42039168 <httpd_resp_send>
42012578:	b495                	j	42011fdc <web_settings_post+0x60>


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200c50c <settings_select_theme>:
4200c50c:	478d                	li	a5,3
4200c50e:	08a7e263          	bltu	a5,a0,4200c592 <settings_select_theme+0x86>
4200c512:	1141                	addi	sp,sp,-16
4200c514:	c226                	sw	s1,4(sp)
4200c516:	3fcb44b7          	lui	s1,0x3fcb4
4200c51a:	c422                	sw	s0,8(sp)
4200c51c:	842a                	mv	s0,a0
4200c51e:	8f04a503          	lw	a0,-1808(s1) # 3fcb38f0 <settings_mutex>
4200c522:	55fd                	li	a1,-1
4200c524:	c606                	sw	ra,12(sp)
4200c526:	0dca00ef          	jal	420ac602 <xQueueSemaphoreTake>
4200c52a:	3fcaf7b7          	lui	a5,0x3fcaf
4200c52e:	5d078793          	addi	a5,a5,1488 # 3fcaf5d0 <current_settings>
4200c532:	1487c703          	lbu	a4,328(a5)
4200c536:	02870a63          	beq	a4,s0,4200c56a <settings_select_theme+0x5e>
4200c53a:	3fcb4737          	lui	a4,0x3fcb4
4200c53e:	14878423          	sb	s0,328(a5)
4200c542:	8e872783          	lw	a5,-1816(a4) # 3fcb38e8 <generation>
4200c546:	0785                	addi	a5,a5,1
4200c548:	8ef72423          	sw	a5,-1816(a4)
4200c54c:	3fcb47b7          	lui	a5,0x3fcb4
4200c550:	4705                	li	a4,1
4200c552:	8ee78023          	sb	a4,-1824(a5) # 3fcb38e0 <dirty>
4200c556:	fe375097          	auipc	ra,0xfe375
4200c55a:	620080e7          	jalr	1568(ra) # 40381b76 <esp_timer_get_time>
4200c55e:	3fcb47b7          	lui	a5,0x3fcb4
4200c562:	8d878793          	addi	a5,a5,-1832 # 3fcb38d8 <last_change_us>
4200c566:	c388                	sw	a0,0(a5)
4200c568:	c3cc                	sw	a1,4(a5)
4200c56a:	3fcb4737          	lui	a4,0x3fcb4
4200c56e:	8e472783          	lw	a5,-1820(a4) # 3fcb38e4 <theme_selection_generation>
4200c572:	8f04a503          	lw	a0,-1808(s1)
4200c576:	4681                	li	a3,0
4200c578:	0785                	addi	a5,a5,1
4200c57a:	4601                	li	a2,0
4200c57c:	4581                	li	a1,0
4200c57e:	8ef72223          	sw	a5,-1820(a4)
4200c582:	4619f0ef          	jal	420ac1e2 <xQueueGenericSend>
4200c586:	40b2                	lw	ra,12(sp)
4200c588:	4422                	lw	s0,8(sp)
4200c58a:	4492                	lw	s1,4(sp)
4200c58c:	4501                	li	a0,0
4200c58e:	0141                	addi	sp,sp,16
4200c590:	8082                	ret
4200c592:	10200513          	li	a0,258
4200c596:	8082                	ret


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200c504 <settings_snapshot>:
4200c504:	4601                	li	a2,0
4200c506:	4581                	li	a1,0
4200c508:	f91ff06f          	j	4200c498 <settings_snapshot_with_revisions>


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200c498 <settings_snapshot_with_revisions>:
4200c498:	1101                	addi	sp,sp,-32
4200c49a:	cc22                	sw	s0,24(sp)
4200c49c:	3fcb4437          	lui	s0,0x3fcb4
4200c4a0:	c64e                	sw	s3,12(sp)
4200c4a2:	89aa                	mv	s3,a0
4200c4a4:	8f042503          	lw	a0,-1808(s0) # 3fcb38f0 <settings_mutex>
4200c4a8:	c84a                	sw	s2,16(sp)
4200c4aa:	892e                	mv	s2,a1
4200c4ac:	55fd                	li	a1,-1
4200c4ae:	ca26                	sw	s1,20(sp)
4200c4b0:	ce06                	sw	ra,28(sp)
4200c4b2:	84b2                	mv	s1,a2
4200c4b4:	14ea00ef          	jal	420ac602 <xQueueSemaphoreTake>
4200c4b8:	3fcaf5b7          	lui	a1,0x3fcaf
4200c4bc:	16c00613          	li	a2,364
4200c4c0:	5d058593          	addi	a1,a1,1488 # 3fcaf5d0 <current_settings>
4200c4c4:	854e                	mv	a0,s3
4200c4c6:	fe37b097          	auipc	ra,0xfe37b
4200c4ca:	d74080e7          	jalr	-652(ra) # 4038723a <memcpy>
4200c4ce:	00090863          	beqz	s2,4200c4de <settings_snapshot_with_revisions+0x46>
4200c4d2:	3fcb47b7          	lui	a5,0x3fcb4
4200c4d6:	8e87a783          	lw	a5,-1816(a5) # 3fcb38e8 <generation>
4200c4da:	00f92023          	sw	a5,0(s2)
4200c4de:	c491                	beqz	s1,4200c4ea <settings_snapshot_with_revisions+0x52>
4200c4e0:	3fcb47b7          	lui	a5,0x3fcb4
4200c4e4:	8e47a783          	lw	a5,-1820(a5) # 3fcb38e4 <theme_selection_generation>
4200c4e8:	c09c                	sw	a5,0(s1)
4200c4ea:	8f042503          	lw	a0,-1808(s0)
4200c4ee:	4462                	lw	s0,24(sp)
4200c4f0:	40f2                	lw	ra,28(sp)
4200c4f2:	44d2                	lw	s1,20(sp)
4200c4f4:	4942                	lw	s2,16(sp)
4200c4f6:	49b2                	lw	s3,12(sp)
4200c4f8:	4681                	li	a3,0
4200c4fa:	4601                	li	a2,0
4200c4fc:	4581                	li	a1,0
4200c4fe:	6105                	addi	sp,sp,32
4200c500:	4e39f06f          	j	420ac1e2 <xQueueGenericSend>


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200d8c8 <factory_photo_step>:
4200d8c8:	0007a023          	sw	zero,0(a5)
4200d8cc:	5879                	li	a6,-2
4200d8ce:	00079223          	sh	zero,4(a5)
4200d8d2:	01078123          	sb	a6,2(a5)
4200d8d6:	0016c693          	xori	a3,a3,1
4200d8da:	e6d9                	bnez	a3,4200d968 <factory_photo_step+0xa0>
4200d8dc:	e751                	bnez	a4,4200d968 <factory_photo_step+0xa0>
4200d8de:	00054703          	lbu	a4,0(a0)
4200d8e2:	4695                	li	a3,5
4200d8e4:	00e6f363          	bgeu	a3,a4,4200d8ea <factory_photo_step+0x22>
4200d8e8:	4701                	li	a4,0
4200d8ea:	3c0c56b7          	lui	a3,0x3c0c5
4200d8ee:	00171813          	slli	a6,a4,0x1
4200d8f2:	14468693          	addi	a3,a3,324 # 3c0c5144 <levels.0>
4200d8f6:	96c2                	add	a3,a3,a6
4200d8f8:	0006d683          	lhu	a3,0(a3)
4200d8fc:	4885                	li	a7,1
4200d8fe:	011781a3          	sb	a7,3(a5)
4200d902:	00d79023          	sh	a3,0(a5)
4200d906:	4689                	li	a3,2
4200d908:	04d71263          	bne	a4,a3,4200d94c <factory_photo_step+0x84>
4200d90c:	4e01                	li	t3,0
4200d90e:	8df1                	and	a1,a1,a2
4200d910:	4695                	li	a3,5
4200d912:	00154803          	lbu	a6,1(a0)
4200d916:	01089333          	sll	t1,a7,a6
4200d91a:	0065f333          	and	t1,a1,t1
4200d91e:	00180713          	addi	a4,a6,1
4200d922:	00030963          	beqz	t1,4200d934 <factory_photo_step+0x6c>
4200d926:	02d76733          	rem	a4,a4,a3
4200d92a:	01078123          	sb	a6,2(a5)
4200d92e:	00e500a3          	sb	a4,1(a0)
4200d932:	a819                	j	4200d948 <factory_photo_step+0x80>
4200d934:	02d76733          	rem	a4,a4,a3
4200d938:	0e05                	addi	t3,t3,1
4200d93a:	00e500a3          	sb	a4,1(a0)
4200d93e:	fcde1ae3          	bne	t3,a3,4200d912 <factory_photo_step+0x4a>
4200d942:	577d                	li	a4,-1
4200d944:	00e78123          	sb	a4,2(a5)
4200d948:	470d                	li	a4,3
4200d94a:	a039                	j	4200d958 <factory_photo_step+0x90>
4200d94c:	0705                	addi	a4,a4,1
4200d94e:	0ff77713          	zext.b	a4,a4
4200d952:	4699                	li	a3,6
4200d954:	00d70563          	beq	a4,a3,4200d95e <factory_photo_step+0x96>
4200d958:	00e50023          	sb	a4,0(a0)
4200d95c:	8082                	ret
4200d95e:	00050023          	sb	zero,0(a0)
4200d962:	01178223          	sb	a7,4(a5)
4200d966:	8082                	ret
4200d968:	8082                	ret
