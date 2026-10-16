
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
4200d38e:	6a9030ef          	jal	42011236 <weather_snapshot>
4200d392:	36114603          	lbu	a2,865(sp)
4200d396:	4581                	li	a1,0
4200d398:	08e8                	addi	a0,sp,92
4200d39a:	f21ff0ef          	jal	4200d2ba <timer_snapshot>
4200d39e:	06a14783          	lbu	a5,106(sp)
4200d3a2:	d63e                	sw	a5,44(sp)
4200d3a4:	741020ef          	jal	420102e4 <network_connected>
4200d3a8:	45d1                	li	a1,20
4200d3aa:	8b2a                	mv	s6,a0
4200d3ac:	1968                	addi	a0,sp,188
4200d3ae:	76b020ef          	jal	42010318 <network_address>
4200d3b2:	4501                	li	a0,0
4200d3b4:	7f38f0ef          	jal	4209d3a6 <time>
4200d3b8:	c62e                	sw	a1,12(sp)
4200d3ba:	4632                	lw	a2,12(sp)
4200d3bc:	c42a                	sw	a0,8(sp)
4200d3be:	85aa                	mv	a1,a0
4200d3c0:	19d4                	addi	a3,sp,244
4200d3c2:	2bb10513          	addi	a0,sp,699
4200d3c6:	53c030ef          	jal	42010902 <services_local_time>
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
4200d43e:	67f030ef          	jal	420112bc <weather_request_active>
4200d442:	e511                	bnez	a0,4200d44e <clock_task+0x134>
4200d444:	000c1d63          	bnez	s8,4200d45e <clock_task+0x144>
4200d448:	633030ef          	jal	4201127a <weather_request_update>
4200d44c:	4c79                	li	s8,30
4200d44e:	07a020ef          	jal	4200f4c8 <media_upload_active>
4200d452:	84aa                	mv	s1,a0
4200d454:	c519                	beqz	a0,4200d462 <clock_task+0x148>
4200d456:	4529                	li	a0,10
4200d458:	3999f0ef          	jal	420acff0 <vTaskDelay>
4200d45c:	b71d                	j	4200d382 <clock_task+0x68>
4200d45e:	1c7d                	addi	s8,s8,-1
4200d460:	b7fd                	j	4200d44e <clock_task+0x134>
4200d462:	57b2                	lw	a5,44(sp)
4200d464:	10078063          	beqz	a5,4200d564 <clock_task+0x24a>
4200d468:	080b0b63          	beqz	s6,4200d4fe <clock_task+0x1e4>
4200d46c:	00099763          	bnez	s3,4200d47a <clock_task+0x160>
4200d470:	35c14703          	lbu	a4,860(sp)
4200d474:	4789                	li	a5,2
4200d476:	08f71463          	bne	a4,a5,4200d4fe <clock_task+0x1e4>
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
4200d4a6:	0ce78f63          	beq	a5,a4,4200d584 <clock_task+0x26a>
4200d4aa:	0f000693          	li	a3,240
4200d4ae:	4701                	li	a4,0
4200d4b0:	8636                	mv	a2,a3
4200d4b2:	4581                	li	a1,0
4200d4b4:	4501                	li	a0,0
4200d4b6:	fcaff0ef          	jal	4200cc80 <display_fill>
4200d4ba:	35c14703          	lbu	a4,860(sp)
4200d4be:	4789                	li	a5,2
4200d4c0:	442d                	li	s0,11
4200d4c2:	00f71363          	bne	a4,a5,4200d4c8 <clock_task+0x1ae>
4200d4c6:	443d                	li	s0,15
4200d4c8:	fe37b097          	auipc	ra,0xfe37b
4200d4cc:	96e080e7          	jalr	-1682(ra) # 40387e36 <vPortEnterCritical>
4200d4d0:	004aa783          	lw	a5,4(s5)
4200d4d4:	8fc1                	or	a5,a5,s0
4200d4d6:	00faa223          	sw	a5,4(s5)
4200d4da:	fe37b097          	auipc	ra,0xfe37b
4200d4de:	988080e7          	jalr	-1656(ra) # 40387e62 <vPortExitCritical>
4200d4e2:	35c14783          	lbu	a5,860(sp)
4200d4e6:	00fde863          	bltu	s11,a5,4200d4f6 <clock_task+0x1dc>
4200d4ea:	465e                	lw	a2,212(sp)
4200d4ec:	45ee                	lw	a1,216(sp)
4200d4ee:	86ce                	mv	a3,s3
4200d4f0:	0c48                	addi	a0,sp,532
4200d4f2:	d7bff0ef          	jal	4200d26c <backlight_update>
4200d4f6:	4485                	li	s1,1
4200d4f8:	8426                	mv	s0,s1
4200d4fa:	4a01                	li	s4,0
4200d4fc:	a841                	j	4200d58c <clock_task+0x272>
4200d4fe:	06914403          	lbu	s0,105(sp)
4200d502:	47f2                	lw	a5,28(sp)
4200d504:	197d                	addi	s2,s2,-1
4200d506:	01203933          	snez	s2,s2
4200d50a:	8f81                	sub	a5,a5,s0
4200d50c:	00f037b3          	snez	a5,a5
4200d510:	0127e7b3          	or	a5,a5,s2
4200d514:	e799                	bnez	a5,4200d522 <clock_task+0x208>
4200d516:	5792                	lw	a5,36(sp)
4200d518:	0167c7b3          	xor	a5,a5,s6
4200d51c:	0ff7f793          	zext.b	a5,a5
4200d520:	cb91                	beqz	a5,4200d534 <clock_task+0x21a>
4200d522:	01603533          	snez	a0,s6
4200d526:	40a00533          	neg	a0,a0
4200d52a:	197c                	addi	a5,sp,188
4200d52c:	85a2                	mv	a1,s0
4200d52e:	8d7d                	and	a0,a0,a5
4200d530:	635000ef          	jal	4200e364 <factory_draw_startup>
4200d534:	36114603          	lbu	a2,865(sp)
4200d538:	08000593          	li	a1,128
4200d53c:	1808                	addi	a0,sp,48
4200d53e:	d7dff0ef          	jal	4200d2ba <timer_snapshot>
4200d542:	4905                	li	s2,1
4200d544:	ce22                	sw	s0,28(sp)
4200d546:	47d6                	lw	a5,84(sp)
4200d548:	4529                	li	a0,10
4200d54a:	11814d03          	lbu	s10,280(sp)
4200d54e:	c83e                	sw	a5,16(sp)
4200d550:	20812783          	lw	a5,520(sp)
4200d554:	ca3e                	sw	a5,20(sp)
4200d556:	29b9f0ef          	jal	420acff0 <vTaskDelay>
4200d55a:	4ca2                	lw	s9,8(sp)
4200d55c:	4bb2                	lw	s7,12(sp)
4200d55e:	d44e                	sw	s3,40(sp)
4200d560:	d25a                	sw	s6,36(sp)
4200d562:	b505                	j	4200d382 <clock_task+0x68>
4200d564:	f20b1be3          	bnez	s6,4200d49a <clock_task+0x180>
4200d568:	597020ef          	jal	420102fe <network_ap_active>
4200d56c:	c901                	beqz	a0,4200d57c <clock_task+0x262>
4200d56e:	4409                	li	s0,2
4200d570:	fc890be3          	beq	s2,s0,4200d546 <clock_task+0x22c>
4200d574:	55b000ef          	jal	4200e2ce <factory_draw_setup>
4200d578:	8922                	mv	s2,s0
4200d57a:	b7f1                	j	4200d546 <clock_task+0x22c>
4200d57c:	478d                	li	a5,3
4200d57e:	fcf914e3          	bne	s2,a5,4200d546 <clock_task+0x22c>
4200d582:	bf39                	j	4200d4a0 <clock_task+0x186>
4200d584:	47e6                	lw	a5,88(sp)
4200d586:	4762                	lw	a4,24(sp)
4200d588:	f2e791e3          	bne	a5,a4,4200d4aa <clock_task+0x190>
4200d58c:	11814783          	lbu	a5,280(sp)
4200d590:	c399                	beqz	a5,4200d596 <clock_task+0x27c>
4200d592:	000d1363          	bnez	s10,4200d598 <clock_task+0x27e>
4200d596:	4a01                	li	s4,0
4200d598:	35c14783          	lbu	a5,860(sp)
4200d59c:	eb91                	bnez	a5,4200d5b0 <clock_task+0x296>
4200d59e:	c4cd                	beqz	s1,4200d648 <clock_task+0x32e>
4200d5a0:	36114603          	lbu	a2,865(sp)
4200d5a4:	4589                	li	a1,2
4200d5a6:	10e8                	addi	a0,sp,108
4200d5a8:	d13ff0ef          	jal	4200d2ba <timer_snapshot>
4200d5ac:	57c6                	lw	a5,112(sp)
4200d5ae:	e3cd                	bnez	a5,4200d650 <clock_task+0x336>
4200d5b0:	35c14783          	lbu	a5,860(sp)
4200d5b4:	ebe9                	bnez	a5,4200d686 <clock_task+0x36c>
4200d5b6:	35d14503          	lbu	a0,861(sp)
4200d5ba:	04c020ef          	jal	4200f606 <media_animation_frames>
4200d5be:	85aa                	mv	a1,a0
4200d5c0:	00e8                	addi	a0,sp,76
4200d5c2:	2655                	jal	4200d966 <factory_animation_next>
4200d5c4:	36114603          	lbu	a2,865(sp)
4200d5c8:	892a                	mv	s2,a0
4200d5ca:	45a1                	li	a1,8
4200d5cc:	18e8                	addi	a0,sp,124
4200d5ce:	cedff0ef          	jal	4200d2ba <timer_snapshot>
4200d5d2:	47a2                	lw	a5,8(sp)
4200d5d4:	4732                	lw	a4,12(sp)
4200d5d6:	480a                	lw	a6,128(sp)
4200d5d8:	00fcc7b3          	xor	a5,s9,a5
4200d5dc:	00ebc733          	xor	a4,s7,a4
4200d5e0:	8fd9                	or	a5,a5,a4
4200d5e2:	01003833          	snez	a6,a6
4200d5e6:	00f037b3          	snez	a5,a5
4200d5ea:	00f867b3          	or	a5,a6,a5
4200d5ee:	e391                	bnez	a5,4200d5f2 <clock_task+0x2d8>
4200d5f0:	c041                	beqz	s0,4200d670 <clock_task+0x356>
4200d5f2:	fff94713          	not	a4,s2
4200d5f6:	877d                	srai	a4,a4,0x1f
4200d5f8:	87a6                	mv	a5,s1
4200d5fa:	00e97733          	and	a4,s2,a4
4200d5fe:	86d2                	mv	a3,s4
4200d600:	0a30                	addi	a2,sp,280
4200d602:	098c                	addi	a1,sp,208
4200d604:	0c48                	addi	a0,sp,532
4200d606:	627000ef          	jal	4200e42c <factory_draw_classic>
4200d60a:	427000ef          	jal	4200e230 <factory_scroll_tick>
4200d60e:	35c14703          	lbu	a4,860(sp)
4200d612:	4789                	li	a5,2
4200d614:	00f70863          	beq	a4,a5,4200d624 <clock_task+0x30a>
4200d618:	465e                	lw	a2,212(sp)
4200d61a:	45ee                	lw	a1,216(sp)
4200d61c:	86ce                	mv	a3,s3
4200d61e:	0c48                	addi	a0,sp,532
4200d620:	c4dff0ef          	jal	4200d26c <backlight_update>
4200d624:	35c14783          	lbu	a5,860(sp)
4200d628:	36114603          	lbu	a2,865(sp)
4200d62c:	04000593          	li	a1,64
4200d630:	d03e                	sw	a5,32(sp)
4200d632:	47e6                	lw	a5,88(sp)
4200d634:	1168                	addi	a0,sp,172
4200d636:	cc3e                	sw	a5,24(sp)
4200d638:	c83ff0ef          	jal	4200d2ba <timer_snapshot>
4200d63c:	57ca                	lw	a5,176(sp)
4200d63e:	c399                	beqz	a5,4200d644 <clock_task+0x32a>
4200d640:	43b030ef          	jal	4201127a <weather_request_update>
4200d644:	490d                	li	s2,3
4200d646:	b701                	j	4200d546 <clock_task+0x22c>
4200d648:	465000ef          	jal	4200e2ac <factory_scroll_description_ready>
4200d64c:	f931                	bnez	a0,4200d5a0 <clock_task+0x286>
4200d64e:	b78d                	j	4200d5b0 <clock_task+0x296>
4200d650:	e891                	bnez	s1,4200d664 <clock_task+0x34a>
4200d652:	11814783          	lbu	a5,280(sp)
4200d656:	c799                	beqz	a5,4200d664 <clock_task+0x34a>
4200d658:	000d0663          	beqz	s10,4200d664 <clock_task+0x34a>
4200d65c:	0a05                	addi	s4,s4,1
4200d65e:	47a9                	li	a5,10
4200d660:	02fa7a33          	remu	s4,s4,a5
4200d664:	f431                	bnez	s0,4200d5b0 <clock_task+0x296>
4200d666:	35c14403          	lbu	s0,860(sp)
4200d66a:	00143413          	seqz	s0,s0
4200d66e:	b789                	j	4200d5b0 <clock_task+0x296>
4200d670:	f8094de3          	bltz	s2,4200d60a <clock_task+0x2f0>
4200d674:	35d14503          	lbu	a0,861(sp)
4200d678:	0a000693          	li	a3,160
4200d67c:	8636                	mv	a2,a3
4200d67e:	85ca                	mv	a1,s2
4200d680:	7e1010ef          	jal	4200f660 <media_draw_animation>
4200d684:	b759                	j	4200d60a <clock_task+0x2f0>
4200d686:	03b79463          	bne	a5,s11,4200d6ae <clock_task+0x394>
4200d68a:	36114603          	lbu	a2,865(sp)
4200d68e:	0168                	addi	a0,sp,140
4200d690:	45a5                	li	a1,9
4200d692:	c29ff0ef          	jal	4200d2ba <timer_snapshot>
4200d696:	474a                	lw	a4,144(sp)
4200d698:	86a6                	mv	a3,s1
4200d69a:	1970                	addi	a2,sp,188
4200d69c:	00375793          	srli	a5,a4,0x3
4200d6a0:	8b85                	andi	a5,a5,1
4200d6a2:	8b05                	andi	a4,a4,1
4200d6a4:	098c                	addi	a1,sp,208
4200d6a6:	0c48                	addi	a0,sp,532
4200d6a8:	38e010ef          	jal	4200ea36 <factory_draw_simple>
4200d6ac:	b78d                	j	4200d60e <clock_task+0x2f4>
4200d6ae:	4709                	li	a4,2
4200d6b0:	0ae79763          	bne	a5,a4,4200d75e <clock_task+0x444>
4200d6b4:	0c58                	addi	a4,sp,532
4200d6b6:	4781                	li	a5,0
4200d6b8:	4601                	li	a2,0
4200d6ba:	4695                	li	a3,5
4200d6bc:	15872583          	lw	a1,344(a4)
4200d6c0:	c581                	beqz	a1,4200d6c8 <clock_task+0x3ae>
4200d6c2:	00fd95b3          	sll	a1,s11,a5
4200d6c6:	8e4d                	or	a2,a2,a1
4200d6c8:	0785                	addi	a5,a5,1
4200d6ca:	0711                	addi	a4,a4,4
4200d6cc:	fed798e3          	bne	a5,a3,4200d6bc <clock_task+0x3a2>
4200d6d0:	5686                	lw	a3,96(sp)
4200d6d2:	36814583          	lbu	a1,872(sp)
4200d6d6:	19dc                	addi	a5,sp,244
4200d6d8:	8289                	srli	a3,a3,0x2
4200d6da:	8a85                	andi	a3,a3,1
4200d6dc:	8ec5                	or	a3,a3,s1
4200d6de:	4701                	li	a4,0
4200d6e0:	0ff6f693          	zext.b	a3,a3
4200d6e4:	0888                	addi	a0,sp,80
4200d6e6:	2af9                	jal	4200d8c4 <factory_photo_step>
4200d6e8:	0f714783          	lbu	a5,247(sp)
4200d6ec:	c789                	beqz	a5,4200d6f6 <clock_task+0x3dc>
4200d6ee:	0f415503          	lhu	a0,244(sp)
4200d6f2:	aa9ff0ef          	jal	4200d19a <backlight_set_level>
4200d6f6:	0f610503          	lb	a0,246(sp)
4200d6fa:	57fd                	li	a5,-1
4200d6fc:	02f54663          	blt	a0,a5,4200d728 <clock_task+0x40e>
4200d700:	04f51b63          	bne	a0,a5,4200d756 <clock_task+0x43c>
4200d704:	0f000693          	li	a3,240
4200d708:	8636                	mv	a2,a3
4200d70a:	4701                	li	a4,0
4200d70c:	4581                	li	a1,0
4200d70e:	4501                	li	a0,0
4200d710:	d70ff0ef          	jal	4200cc80 <display_fill>
4200d714:	6741                	lui	a4,0x10
4200d716:	4805                	li	a6,1
4200d718:	4781                	li	a5,0
4200d71a:	177d                	addi	a4,a4,-1 # ffff <CSR_UINTSTATUS+0xf34e>
4200d71c:	46c1                	li	a3,16
4200d71e:	1970                	addi	a2,sp,188
4200d720:	0e100593          	li	a1,225
4200d724:	4515                	li	a0,5
4200d726:	2355                	jal	4200dcca <display_factory_text>
4200d728:	0f814783          	lbu	a5,248(sp)
4200d72c:	c799                	beqz	a5,4200d73a <clock_task+0x420>
4200d72e:	36114603          	lbu	a2,865(sp)
4200d732:	4591                	li	a1,4
4200d734:	1808                	addi	a0,sp,48
4200d736:	b85ff0ef          	jal	4200d2ba <timer_snapshot>
4200d73a:	0f714783          	lbu	a5,247(sp)
4200d73e:	c789                	beqz	a5,4200d748 <clock_task+0x42e>
4200d740:	0f814783          	lbu	a5,248(sp)
4200d744:	ec0785e3          	beqz	a5,4200d60e <clock_task+0x2f4>
4200d748:	465e                	lw	a2,212(sp)
4200d74a:	45ee                	lw	a1,216(sp)
4200d74c:	86ce                	mv	a3,s3
4200d74e:	0c48                	addi	a0,sp,532
4200d750:	b1dff0ef          	jal	4200d26c <backlight_update>
4200d754:	bd6d                	j	4200d60e <clock_task+0x2f4>
4200d756:	196c                	addi	a1,sp,188
4200d758:	1f9010ef          	jal	4200f150 <factory_draw_photo>
4200d75c:	b7f1                	j	4200d728 <clock_task+0x40e>
4200d75e:	36114603          	lbu	a2,865(sp)
4200d762:	4585                	li	a1,1
4200d764:	0968                	addi	a0,sp,156
4200d766:	b55ff0ef          	jal	4200d2ba <timer_snapshot>
4200d76a:	578a                	lw	a5,160(sp)
4200d76c:	00f037b3          	snez	a5,a5
4200d770:	8fc5                	or	a5,a5,s1
4200d772:	0ff7f793          	zext.b	a5,a5
4200d776:	e399                	bnez	a5,4200d77c <clock_task+0x462>
4200d778:	e8040be3          	beqz	s0,4200d60e <clock_task+0x2f4>
4200d77c:	8626                	mv	a2,s1
4200d77e:	196c                	addi	a1,sp,188
4200d780:	0988                	addi	a0,sp,208
4200d782:	4d6010ef          	jal	4200ec58 <factory_draw_dial>
4200d786:	b561                	j	4200d60e <clock_task+0x2f4>


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42011f78 <web_settings_post>:
42011f78:	7101                	addi	sp,sp,-512
42011f7a:	1e912a23          	sw	s1,500(sp)
42011f7e:	84aa                	mv	s1,a0
42011f80:	18c8                	addi	a0,sp,116
42011f82:	1e112e23          	sw	ra,508(sp)
42011f86:	1e812c23          	sw	s0,504(sp)
42011f8a:	1f212823          	sw	s2,496(sp)
42011f8e:	1f312623          	sw	s3,492(sp)
42011f92:	1f412423          	sw	s4,488(sp)
42011f96:	1f512223          	sw	s5,484(sp)
42011f9a:	1f612023          	sw	s6,480(sp)
42011f9e:	d66fa0ef          	jal	4200c504 <settings_snapshot>
42011fa2:	3c0b45b7          	lui	a1,0x3c0b4
42011fa6:	65058593          	addi	a1,a1,1616 # 3c0b4650 <_esp_libc_clock_array_end+0x4500>
42011faa:	00848513          	addi	a0,s1,8
42011fae:	fe375097          	auipc	ra,0xfe375
42011fb2:	6a4080e7          	jalr	1700(ra) # 40387652 <strcmp>
42011fb6:	ed31                	bnez	a0,42012012 <web_settings_post+0x9a>
42011fb8:	20c4a783          	lw	a5,524(s1)
42011fbc:	c7a9                	beqz	a5,42012006 <web_settings_post+0x8e>
42011fbe:	08000593          	li	a1,128
42011fc2:	8526                	mv	a0,s1
42011fc4:	9b3ff0ef          	jal	42011976 <web_body>
42011fc8:	e91d                	bnez	a0,42011ffe <web_settings_post+0x86>
42011fca:	3c0b55b7          	lui	a1,0x3c0b5
42011fce:	88858593          	addi	a1,a1,-1912 # 3c0b4888 <_esp_libc_clock_array_end+0x4738>
42011fd2:	8526                	mv	a0,s1
42011fd4:	8d5ff0ef          	jal	420118a8 <web_error>
42011fd8:	1fc12083          	lw	ra,508(sp)
42011fdc:	1f812403          	lw	s0,504(sp)
42011fe0:	1f412483          	lw	s1,500(sp)
42011fe4:	1f012903          	lw	s2,496(sp)
42011fe8:	1ec12983          	lw	s3,492(sp)
42011fec:	1e812a03          	lw	s4,488(sp)
42011ff0:	1e412a83          	lw	s5,484(sp)
42011ff4:	1e012b03          	lw	s6,480(sp)
42011ff8:	20010113          	addi	sp,sp,512
42011ffc:	8082                	ret
42011ffe:	fe375097          	auipc	ra,0xfe375
42012002:	1c4080e7          	jalr	452(ra) # 403871c2 <cfree>
42012006:	c0cfe0ef          	jal	42010412 <network_restart_later>
4201200a:	8526                	mv	a0,s1
4201200c:	8d5ff0ef          	jal	420118e0 <web_ok>
42012010:	b7e1                	j	42011fd8 <web_settings_post+0x60>
42012012:	3c0b45b7          	lui	a1,0x3c0b4
42012016:	70458593          	addi	a1,a1,1796 # 3c0b4704 <_esp_libc_clock_array_end+0x45b4>
4201201a:	00848513          	addi	a0,s1,8
4201201e:	fe375097          	auipc	ra,0xfe375
42012022:	634080e7          	jalr	1588(ra) # 40387652 <strcmp>
42012026:	89aa                	mv	s3,a0
42012028:	c92d                	beqz	a0,4201209a <web_settings_post+0x122>
4201202a:	3c0b45b7          	lui	a1,0x3c0b4
4201202e:	6ac58593          	addi	a1,a1,1708 # 3c0b46ac <_esp_libc_clock_array_end+0x455c>
42012032:	00848513          	addi	a0,s1,8
42012036:	fe375097          	auipc	ra,0xfe375
4201203a:	61c080e7          	jalr	1564(ra) # 40387652 <strcmp>
4201203e:	e945                	bnez	a0,420120ee <web_settings_post+0x176>
42012040:	3c0b5937          	lui	s2,0x3c0b5
42012044:	87890913          	addi	s2,s2,-1928 # 3c0b4878 <_esp_libc_clock_array_end+0x4728>
42012048:	08000593          	li	a1,128
4201204c:	8526                	mv	a0,s1
4201204e:	929ff0ef          	jal	42011976 <web_body>
42012052:	8a2a                	mv	s4,a0
42012054:	20050663          	beqz	a0,42012260 <web_settings_post+0x2e8>
42012058:	20c4a603          	lw	a2,524(s1)
4201205c:	4581                	li	a1,0
4201205e:	fdfee097          	auipc	ra,0xfdfee
42012062:	49e080e7          	jalr	1182(ra) # 400004fc <memchr>
42012066:	cd1d                	beqz	a0,420120a4 <web_settings_post+0x12c>
42012068:	4901                	li	s2,0
4201206a:	8552                	mv	a0,s4
4201206c:	fe375097          	auipc	ra,0xfe375
42012070:	156080e7          	jalr	342(ra) # 403871c2 <cfree>
42012074:	1e090663          	beqz	s2,42012260 <web_settings_post+0x2e8>
42012078:	47a9                	li	a5,10
4201207a:	02f40433          	mul	s0,s0,a5
4201207e:	3e800793          	li	a5,1000
42012082:	40878433          	sub	s0,a5,s0
42012086:	06099163          	bnez	s3,420120e8 <web_settings_post+0x170>
4201208a:	1a811923          	sh	s0,434(sp)
4201208e:	4901                	li	s2,0
42012090:	4981                	li	s3,0
42012092:	18c8                	addi	a0,sp,116
42012094:	d04fa0ef          	jal	4200c598 <settings_replace>
42012098:	a2d1                	j	4201225c <web_settings_post+0x2e4>
4201209a:	3c0b5937          	lui	s2,0x3c0b5
4201209e:	86890913          	addi	s2,s2,-1944 # 3c0b4868 <_esp_libc_clock_array_end+0x4718>
420120a2:	b75d                	j	42012048 <web_settings_post+0xd0>
420120a4:	46a1                	li	a3,8
420120a6:	0870                	addi	a2,sp,28
420120a8:	85ca                	mv	a1,s2
420120aa:	8552                	mv	a0,s4
420120ac:	5b0260ef          	jal	4203865c <httpd_query_key_value>
420120b0:	fd45                	bnez	a0,42012068 <web_settings_post+0xf0>
420120b2:	01c14783          	lbu	a5,28(sp)
420120b6:	dbcd                	beqz	a5,42012068 <web_settings_post+0xf0>
420120b8:	0878                	addi	a4,sp,28
420120ba:	4905                	li	s2,1
420120bc:	a801                	j	420120cc <web_settings_post+0x154>
420120be:	fd078793          	addi	a5,a5,-48
420120c2:	00a7b793          	sltiu	a5,a5,10
420120c6:	00f97933          	and	s2,s2,a5
420120ca:	0705                	addi	a4,a4,1
420120cc:	00074783          	lbu	a5,0(a4)
420120d0:	f7fd                	bnez	a5,420120be <web_settings_post+0x146>
420120d2:	4629                	li	a2,10
420120d4:	4581                	li	a1,0
420120d6:	0868                	addi	a0,sp,28
420120d8:	4fc8c0ef          	jal	4209e5d4 <strtoul>
420120dc:	06553793          	sltiu	a5,a0,101
420120e0:	842a                	mv	s0,a0
420120e2:	00f97933          	and	s2,s2,a5
420120e6:	b751                	j	4201206a <web_settings_post+0xf2>
420120e8:	1a811a23          	sh	s0,436(sp)
420120ec:	b74d                	j	4201208e <web_settings_post+0x116>
420120ee:	8526                	mv	a0,s1
420120f0:	987ff0ef          	jal	42011a76 <web_parse_json>
420120f4:	8aaa                	mv	s5,a0
420120f6:	e511                	bnez	a0,42012102 <web_settings_post+0x18a>
420120f8:	3c0b55b7          	lui	a1,0x3c0b5
420120fc:	89858593          	addi	a1,a1,-1896 # 3c0b4898 <_esp_libc_clock_array_end+0x4748>
42012100:	bdc9                	j	42011fd2 <web_settings_post+0x5a>
42012102:	3c0eb937          	lui	s2,0x3c0eb
42012106:	54490913          	addi	s2,s2,1348 # 3c0eb544 <integers>
4201210a:	09090993          	addi	s3,s2,144
4201210e:	4a01                	li	s4,0
42012110:	4401                	li	s0,0
42012112:	00492583          	lw	a1,4(s2)
42012116:	00848513          	addi	a0,s1,8
4201211a:	fe375097          	auipc	ra,0xfe375
4201211e:	538080e7          	jalr	1336(ra) # 40387652 <strcmp>
42012122:	e131                	bnez	a0,42012166 <web_settings_post+0x1ee>
42012124:	01492683          	lw	a3,20(s2)
42012128:	01092603          	lw	a2,16(s2)
4201212c:	00892583          	lw	a1,8(s2)
42012130:	0878                	addi	a4,sp,28
42012132:	8556                	mv	a0,s5
42012134:	98fff0ef          	jal	42011ac2 <web_integer>
42012138:	842a                	mv	s0,a0
4201213a:	c515                	beqz	a0,42012166 <web_settings_post+0x1ee>
4201213c:	00c92783          	lw	a5,12(s2)
42012140:	0818                	addi	a4,sp,16
42012142:	3c0b45b7          	lui	a1,0x3c0b4
42012146:	1d078793          	addi	a5,a5,464
4201214a:	97ba                	add	a5,a5,a4
4201214c:	4772                	lw	a4,28(sp)
4201214e:	78c58593          	addi	a1,a1,1932 # 3c0b478c <_esp_libc_clock_array_end+0x463c>
42012152:	00848513          	addi	a0,s1,8
42012156:	e8e78a23          	sb	a4,-364(a5)
4201215a:	fe375097          	auipc	ra,0xfe375
4201215e:	4f8080e7          	jalr	1272(ra) # 40387652 <strcmp>
42012162:	00153a13          	seqz	s4,a0
42012166:	0961                	addi	s2,s2,24
42012168:	fb3915e3          	bne	s2,s3,42012112 <web_settings_post+0x19a>
4201216c:	3c0b45b7          	lui	a1,0x3c0b4
42012170:	77058593          	addi	a1,a1,1904 # 3c0b4770 <_esp_libc_clock_array_end+0x4620>
42012174:	00848513          	addi	a0,s1,8
42012178:	fe375097          	auipc	ra,0xfe375
4201217c:	4da080e7          	jalr	1242(ra) # 40387652 <strcmp>
42012180:	e531                	bnez	a0,420121cc <web_settings_post+0x254>
42012182:	3c0eb937          	lui	s2,0x3c0eb
42012186:	51c90913          	addi	s2,s2,1308 # 3c0eb51c <switches>
4201218a:	02890993          	addi	s3,s2,40
4201218e:	4401                	li	s0,0
42012190:	00092583          	lw	a1,0(s2)
42012194:	8556                	mv	a0,s5
42012196:	c62e                	sw	a1,12(sp)
42012198:	4b1020ef          	jal	42014e48 <cJSON_HasObjectItem>
4201219c:	45b2                	lw	a1,12(sp)
4201219e:	c115                	beqz	a0,420121c2 <web_settings_post+0x24a>
420121a0:	0878                	addi	a4,sp,28
420121a2:	4685                	li	a3,1
420121a4:	4601                	li	a2,0
420121a6:	8556                	mv	a0,s5
420121a8:	91bff0ef          	jal	42011ac2 <web_integer>
420121ac:	842a                	mv	s0,a0
420121ae:	cd09                	beqz	a0,420121c8 <web_settings_post+0x250>
420121b0:	00492783          	lw	a5,4(s2)
420121b4:	0818                	addi	a4,sp,16
420121b6:	1d078793          	addi	a5,a5,464
420121ba:	97ba                	add	a5,a5,a4
420121bc:	4772                	lw	a4,28(sp)
420121be:	e8e78a23          	sb	a4,-364(a5)
420121c2:	0921                	addi	s2,s2,8
420121c4:	fd2996e3          	bne	s3,s2,42012190 <web_settings_post+0x218>
420121c8:	4981                	li	s3,0
420121ca:	aa11                	j	420122de <web_settings_post+0x366>
420121cc:	3c0b45b7          	lui	a1,0x3c0b4
420121d0:	7c458593          	addi	a1,a1,1988 # 3c0b47c4 <_esp_libc_clock_array_end+0x4674>
420121d4:	00848513          	addi	a0,s1,8
420121d8:	fe375097          	auipc	ra,0xfe375
420121dc:	47a080e7          	jalr	1146(ra) # 40387652 <strcmp>
420121e0:	cd01                	beqz	a0,420121f8 <web_settings_post+0x280>
420121e2:	3c0b45b7          	lui	a1,0x3c0b4
420121e6:	63458593          	addi	a1,a1,1588 # 3c0b4634 <_esp_libc_clock_array_end+0x44e4>
420121ea:	00848513          	addi	a0,s1,8
420121ee:	fe375097          	auipc	ra,0xfe375
420121f2:	464080e7          	jalr	1124(ra) # 40387652 <strcmp>
420121f6:	e141                	bnez	a0,42012276 <web_settings_post+0x2fe>
420121f8:	3c0bf5b7          	lui	a1,0x3c0bf
420121fc:	02100693          	li	a3,33
42012200:	18b0                	addi	a2,sp,120
42012202:	1e058593          	addi	a1,a1,480 # 3c0bf1e0 <_esp_libc_clock_array_end+0xf090>
42012206:	8556                	mv	a0,s5
42012208:	acdff0ef          	jal	42011cd4 <copy_string>
4201220c:	c91d                	beqz	a0,42012242 <web_settings_post+0x2ca>
4201220e:	07814783          	lbu	a5,120(sp)
42012212:	cb85                	beqz	a5,42012242 <web_settings_post+0x2ca>
42012214:	3c0b55b7          	lui	a1,0x3c0b5
42012218:	04100693          	li	a3,65
4201221c:	09910613          	addi	a2,sp,153
42012220:	8b858593          	addi	a1,a1,-1864 # 3c0b48b8 <_esp_libc_clock_array_end+0x4768>
42012224:	8556                	mv	a0,s5
42012226:	aafff0ef          	jal	42011cd4 <copy_string>
4201222a:	842a                	mv	s0,a0
4201222c:	c919                	beqz	a0,42012242 <web_settings_post+0x2ca>
4201222e:	09910513          	addi	a0,sp,153
42012232:	fdfee097          	auipc	ra,0xfdfee
42012236:	276080e7          	jalr	630(ra) # 400004a8 <strlen>
4201223a:	157d                	addi	a0,a0,-1
4201223c:	4799                	li	a5,6
4201223e:	02a7e663          	bltu	a5,a0,4201226a <web_settings_post+0x2f2>
42012242:	4981                	li	s3,0
42012244:	4901                	li	s2,0
42012246:	4401                	li	s0,0
42012248:	8556                	mv	a0,s5
4201224a:	6b0020ef          	jal	420148fa <cJSON_Delete>
4201224e:	c809                	beqz	s0,42012260 <web_settings_post+0x2e8>
42012250:	e40a01e3          	beqz	s4,42012092 <web_settings_post+0x11a>
42012254:	1bc14503          	lbu	a0,444(sp)
42012258:	ab4fa0ef          	jal	4200c50c <settings_select_theme>
4201225c:	2e050063          	beqz	a0,4201253c <web_settings_post+0x5c4>
42012260:	3c0b55b7          	lui	a1,0x3c0b5
42012264:	92058593          	addi	a1,a1,-1760 # 3c0b4920 <_esp_libc_clock_array_end+0x47d0>
42012268:	b3ad                	j	42011fd2 <web_settings_post+0x5a>
4201226a:	4785                	li	a5,1
4201226c:	1cf104a3          	sb	a5,457(sp)
42012270:	8922                	mv	s2,s0
42012272:	4981                	li	s3,0
42012274:	bfd1                	j	42012248 <web_settings_post+0x2d0>
42012276:	3c0b45b7          	lui	a1,0x3c0b4
4201227a:	64058593          	addi	a1,a1,1600 # 3c0b4640 <_esp_libc_clock_array_end+0x44f0>
4201227e:	00848513          	addi	a0,s1,8
42012282:	fe375097          	auipc	ra,0xfe375
42012286:	3d0080e7          	jalr	976(ra) # 40387652 <strcmp>
4201228a:	ed21                	bnez	a0,420122e2 <web_settings_post+0x36a>
4201228c:	3c0b55b7          	lui	a1,0x3c0b5
42012290:	04100693          	li	a3,65
42012294:	12f10613          	addi	a2,sp,303
42012298:	8c458593          	addi	a1,a1,-1852 # 3c0b48c4 <_esp_libc_clock_array_end+0x4774>
4201229c:	8556                	mv	a0,s5
4201229e:	a37ff0ef          	jal	42011cd4 <copy_string>
420122a2:	e119                	bnez	a0,420122a8 <web_settings_post+0x330>
420122a4:	4401                	li	s0,0
420122a6:	a81d                	j	420122dc <web_settings_post+0x364>
420122a8:	3c0b55b7          	lui	a1,0x3c0b5
420122ac:	04100693          	li	a3,65
420122b0:	1a90                	addi	a2,sp,368
420122b2:	8c858593          	addi	a1,a1,-1848 # 3c0b48c8 <_esp_libc_clock_array_end+0x4778>
420122b6:	8556                	mv	a0,s5
420122b8:	a1dff0ef          	jal	42011cd4 <copy_string>
420122bc:	d565                	beqz	a0,420122a4 <web_settings_post+0x32c>
420122be:	3c0b55b7          	lui	a1,0x3c0b5
420122c2:	0878                	addi	a4,sp,28
420122c4:	46a9                	li	a3,10
420122c6:	4601                	li	a2,0
420122c8:	8dc58593          	addi	a1,a1,-1828 # 3c0b48dc <_esp_libc_clock_array_end+0x478c>
420122cc:	8556                	mv	a0,s5
420122ce:	ff4ff0ef          	jal	42011ac2 <web_integer>
420122d2:	842a                	mv	s0,a0
420122d4:	d961                	beqz	a0,420122a4 <web_settings_post+0x32c>
420122d6:	47f2                	lw	a5,28(sp)
420122d8:	1cf103a3          	sb	a5,455(sp)
420122dc:	89a2                	mv	s3,s0
420122de:	4901                	li	s2,0
420122e0:	b7a5                	j	42012248 <web_settings_post+0x2d0>
420122e2:	3c0b45b7          	lui	a1,0x3c0b4
420122e6:	72c58593          	addi	a1,a1,1836 # 3c0b472c <_esp_libc_clock_array_end+0x45dc>
420122ea:	00848513          	addi	a0,s1,8
420122ee:	fe375097          	auipc	ra,0xfe375
420122f2:	364080e7          	jalr	868(ra) # 40387652 <strcmp>
420122f6:	e95d                	bnez	a0,420123ac <web_settings_post+0x434>
420122f8:	3c0b55b7          	lui	a1,0x3c0b5
420122fc:	05700693          	li	a3,87
42012300:	0870                	addi	a2,sp,28
42012302:	8e858593          	addi	a1,a1,-1816 # 3c0b48e8 <_esp_libc_clock_array_end+0x4798>
42012306:	8556                	mv	a0,s5
42012308:	9cdff0ef          	jal	42011cd4 <copy_string>
4201230c:	dd41                	beqz	a0,420122a4 <web_settings_post+0x32c>
4201230e:	02c00593          	li	a1,44
42012312:	0868                	addi	a0,sp,28
42012314:	fdfee097          	auipc	ra,0xfdfee
42012318:	228080e7          	jalr	552(ra) # 4000053c <strrchr>
4201231c:	892a                	mv	s2,a0
4201231e:	4985                	li	s3,1
42012320:	ed09                	bnez	a0,4201233a <web_settings_post+0x3c2>
42012322:	3c0b55b7          	lui	a1,0x3c0b5
42012326:	8f058593          	addi	a1,a1,-1808 # 3c0b48f0 <_esp_libc_clock_array_end+0x47a0>
4201232a:	0868                	addi	a0,sp,28
4201232c:	fdfee097          	auipc	ra,0xfdfee
42012330:	180080e7          	jalr	384(ra) # 400004ac <strstr>
42012334:	892a                	mv	s2,a0
42012336:	d53d                	beqz	a0,420122a4 <web_settings_post+0x32c>
42012338:	498d                	li	s3,3
4201233a:	99ca                	add	s3,s3,s2
4201233c:	854e                	mv	a0,s3
4201233e:	fdfee097          	auipc	ra,0xfdfee
42012342:	16a080e7          	jalr	362(ra) # 400004a8 <strlen>
42012346:	47cd                	li	a5,19
42012348:	f4a7eee3          	bltu	a5,a0,420122a4 <web_settings_post+0x32c>
4201234c:	854e                	mv	a0,s3
4201234e:	bbbf90ef          	jal	4200bf08 <settings_country_valid>
42012352:	842a                	mv	s0,a0
42012354:	d921                	beqz	a0,420122a4 <web_settings_post+0x32c>
42012356:	00090023          	sb	zero,0(s2)
4201235a:	0868                	addi	a0,sp,28
4201235c:	fdfee097          	auipc	ra,0xfdfee
42012360:	14c080e7          	jalr	332(ra) # 400004a8 <strlen>
42012364:	157d                	addi	a0,a0,-1
42012366:	03f00793          	li	a5,63
4201236a:	f2a7ede3          	bltu	a5,a0,420122a4 <web_settings_post+0x32c>
4201236e:	086c                	addi	a1,sp,28
42012370:	0da10513          	addi	a0,sp,218
42012374:	fe375097          	auipc	ra,0xfe375
42012378:	3f4080e7          	jalr	1012(ra) # 40387768 <strcpy>
4201237c:	854e                	mv	a0,s3
4201237e:	fdfee097          	auipc	ra,0xfdfee
42012382:	12a080e7          	jalr	298(ra) # 400004a8 <strlen>
42012386:	18d4                	addi	a3,sp,116
42012388:	4781                	li	a5,0
4201238a:	4665                	li	a2,25
4201238c:	00f98733          	add	a4,s3,a5
42012390:	00074703          	lbu	a4,0(a4)
42012394:	f9f70593          	addi	a1,a4,-97
42012398:	00b66363          	bltu	a2,a1,4201239e <web_settings_post+0x426>
4201239c:	1701                	addi	a4,a4,-32
4201239e:	0ae683a3          	sb	a4,167(a3)
420123a2:	0785                	addi	a5,a5,1
420123a4:	0685                	addi	a3,a3,1
420123a6:	fef573e3          	bgeu	a0,a5,4201238c <web_settings_post+0x414>
420123aa:	bf0d                	j	420122dc <web_settings_post+0x364>
420123ac:	3c0b45b7          	lui	a1,0x3c0b4
420123b0:	6dc58593          	addi	a1,a1,1756 # 3c0b46dc <_esp_libc_clock_array_end+0x458c>
420123b4:	00848513          	addi	a0,s1,8
420123b8:	fe375097          	auipc	ra,0xfe375
420123bc:	29a080e7          	jalr	666(ra) # 40387652 <strcmp>
420123c0:	e945                	bnez	a0,42012470 <web_settings_post+0x4f8>
420123c2:	3c0b55b7          	lui	a1,0x3c0b5
420123c6:	8f458593          	addi	a1,a1,-1804 # 3c0b48f4 <_esp_libc_clock_array_end+0x47a4>
420123ca:	8556                	mv	a0,s5
420123cc:	277020ef          	jal	42014e42 <cJSON_GetObjectItemCaseSensitive>
420123d0:	3c0ba5b7          	lui	a1,0x3c0ba
420123d4:	892a                	mv	s2,a0
420123d6:	0878                	addi	a4,sp,28
420123d8:	4689                	li	a3,2
420123da:	4601                	li	a2,0
420123dc:	86458593          	addi	a1,a1,-1948 # 3c0b9864 <_esp_libc_clock_array_end+0x9714>
420123e0:	8556                	mv	a0,s5
420123e2:	ee0ff0ef          	jal	42011ac2 <web_integer>
420123e6:	842a                	mv	s0,a0
420123e8:	e119                	bnez	a0,420123ee <web_settings_post+0x476>
420123ea:	4401                	li	s0,0
420123ec:	bbf1                	j	420121c8 <web_settings_post+0x250>
420123ee:	854a                	mv	a0,s2
420123f0:	451020ef          	jal	42015040 <cJSON_IsString>
420123f4:	d97d                	beqz	a0,420123ea <web_settings_post+0x472>
420123f6:	01092903          	lw	s2,16(s2)
420123fa:	854a                	mv	a0,s2
420123fc:	fdfee097          	auipc	ra,0xfdfee
42012400:	0ac080e7          	jalr	172(ra) # 400004a8 <strlen>
42012404:	479d                	li	a5,7
42012406:	fef512e3          	bne	a0,a5,420123ea <web_settings_post+0x472>
4201240a:	00094703          	lbu	a4,0(s2)
4201240e:	02300793          	li	a5,35
42012412:	fcf71ce3          	bne	a4,a5,420123ea <web_settings_post+0x472>
42012416:	4705                	li	a4,1
42012418:	4625                	li	a2,9
4201241a:	4595                	li	a1,5
4201241c:	86aa                	mv	a3,a0
4201241e:	00e907b3          	add	a5,s2,a4
42012422:	0007c783          	lbu	a5,0(a5)
42012426:	fd078513          	addi	a0,a5,-48
4201242a:	00a67b63          	bgeu	a2,a0,42012440 <web_settings_post+0x4c8>
4201242e:	fbf78513          	addi	a0,a5,-65
42012432:	00a5f763          	bgeu	a1,a0,42012440 <web_settings_post+0x4c8>
42012436:	f9f78793          	addi	a5,a5,-97
4201243a:	0067b793          	sltiu	a5,a5,6
4201243e:	8c7d                	and	s0,s0,a5
42012440:	0705                	addi	a4,a4,1
42012442:	fcd71ee3          	bne	a4,a3,4201241e <web_settings_post+0x4a6>
42012446:	d055                	beqz	s0,420123ea <web_settings_post+0x472>
42012448:	4641                	li	a2,16
4201244a:	4581                	li	a1,0
4201244c:	00190513          	addi	a0,s2,1
42012450:	1848c0ef          	jal	4209e5d4 <strtoul>
42012454:	4972                	lw	s2,28(sp)
42012456:	a65f90ef          	jal	4200beba <rgb565_from_rgb888>
4201245a:	0818                	addi	a4,sp,16
4201245c:	0a090913          	addi	s2,s2,160
42012460:	0906                	slli	s2,s2,0x1
42012462:	1d090793          	addi	a5,s2,464
42012466:	00e78933          	add	s2,a5,a4
4201246a:	e8a91b23          	sh	a0,-362(s2)
4201246e:	bba9                	j	420121c8 <web_settings_post+0x250>
42012470:	3c0b45b7          	lui	a1,0x3c0b4
42012474:	5e458593          	addi	a1,a1,1508 # 3c0b45e4 <_esp_libc_clock_array_end+0x4494>
42012478:	00848513          	addi	a0,s1,8
4201247c:	fe375097          	auipc	ra,0xfe375
42012480:	1d6080e7          	jalr	470(ra) # 40387652 <strcmp>
42012484:	d40512e3          	bnez	a0,420121c8 <web_settings_post+0x250>
42012488:	3c0b55b7          	lui	a1,0x3c0b5
4201248c:	8fc58593          	addi	a1,a1,-1796 # 3c0b48fc <_esp_libc_clock_array_end+0x47ac>
42012490:	8556                	mv	a0,s5
42012492:	1b1020ef          	jal	42014e42 <cJSON_GetObjectItemCaseSensitive>
42012496:	3c0b55b7          	lui	a1,0x3c0b5
4201249a:	842a                	mv	s0,a0
4201249c:	90858593          	addi	a1,a1,-1784 # 3c0b4908 <_esp_libc_clock_array_end+0x47b8>
420124a0:	8556                	mv	a0,s5
420124a2:	1a1020ef          	jal	42014e42 <cJSON_GetObjectItemCaseSensitive>
420124a6:	892a                	mv	s2,a0
420124a8:	8522                	mv	a0,s0
420124aa:	397020ef          	jal	42015040 <cJSON_IsString>
420124ae:	d8050ae3          	beqz	a0,42012242 <web_settings_post+0x2ca>
420124b2:	854a                	mv	a0,s2
420124b4:	373020ef          	jal	42015026 <cJSON_IsBool>
420124b8:	d80505e3          	beqz	a0,42012242 <web_settings_post+0x2ca>
420124bc:	4800                	lw	s0,16(s0)
420124be:	8522                	mv	a0,s0
420124c0:	fdfee097          	auipc	ra,0xfdfee
420124c4:	fe8080e7          	jalr	-24(ra) # 400004a8 <strlen>
420124c8:	47b1                	li	a5,12
420124ca:	d6f51ce3          	bne	a0,a5,42012242 <web_settings_post+0x2ca>
420124ce:	3c0b55b7          	lui	a1,0x3c0b5
420124d2:	4611                	li	a2,4
420124d4:	91058593          	addi	a1,a1,-1776 # 3c0b4910 <_esp_libc_clock_array_end+0x47c0>
420124d8:	8522                	mv	a0,s0
420124da:	fe375097          	auipc	ra,0xfe375
420124de:	d22080e7          	jalr	-734(ra) # 403871fc <memcmp>
420124e2:	d60510e3          	bnez	a0,42012242 <web_settings_post+0x2ca>
420124e6:	3c0b55b7          	lui	a1,0x3c0b5
420124ea:	91858593          	addi	a1,a1,-1768 # 3c0b4918 <_esp_libc_clock_array_end+0x47c8>
420124ee:	00540513          	addi	a0,s0,5
420124f2:	fe375097          	auipc	ra,0xfe375
420124f6:	160080e7          	jalr	352(ra) # 40387652 <strcmp>
420124fa:	d40514e3          	bnez	a0,42012242 <web_settings_post+0x2ca>
420124fe:	00444403          	lbu	s0,4(s0)
42012502:	4791                	li	a5,4
42012504:	fcf40413          	addi	s0,s0,-49
42012508:	0ff47713          	zext.b	a4,s0
4201250c:	d2e7ebe3          	bltu	a5,a4,42012242 <web_settings_post+0x2ca>
42012510:	854a                	mv	a0,s2
42012512:	307020ef          	jal	42015018 <cJSON_IsTrue>
42012516:	4785                	li	a5,1
42012518:	008797b3          	sll	a5,a5,s0
4201251c:	1c814703          	lbu	a4,456(sp)
42012520:	0ff7f793          	zext.b	a5,a5
42012524:	c901                	beqz	a0,42012534 <web_settings_post+0x5bc>
42012526:	8f5d                	or	a4,a4,a5
42012528:	1ce10423          	sb	a4,456(sp)
4201252c:	4981                	li	s3,0
4201252e:	4901                	li	s2,0
42012530:	4405                	li	s0,1
42012532:	bb19                	j	42012248 <web_settings_post+0x2d0>
42012534:	fff7c793          	not	a5,a5
42012538:	8f7d                	and	a4,a4,a5
4201253a:	b7fd                	j	42012528 <web_settings_post+0x5b0>
4201253c:	00098463          	beqz	s3,42012544 <web_settings_post+0x5cc>
42012540:	d3bfe0ef          	jal	4201127a <weather_request_update>
42012544:	00090463          	beqz	s2,4201254c <web_settings_post+0x5d4>
42012548:	ecbfd0ef          	jal	42010412 <network_restart_later>
4201254c:	3c0b45b7          	lui	a1,0x3c0b4
42012550:	64058593          	addi	a1,a1,1600 # 3c0b4640 <_esp_libc_clock_array_end+0x44f0>
42012554:	00848513          	addi	a0,s1,8
42012558:	fe375097          	auipc	ra,0xfe375
4201255c:	0fa080e7          	jalr	250(ra) # 40387652 <strcmp>
42012560:	aa0515e3          	bnez	a0,4201200a <web_settings_post+0x92>
42012564:	3c0b55b7          	lui	a1,0x3c0b5
42012568:	567d                	li	a2,-1
4201256a:	93c58593          	addi	a1,a1,-1732 # 3c0b493c <_esp_libc_clock_array_end+0x47ec>
4201256e:	8526                	mv	a0,s1
42012570:	3f5260ef          	jal	42039164 <httpd_resp_send>
42012574:	b495                	j	42011fd8 <web_settings_post+0x60>


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
4200c526:	0d8a00ef          	jal	420ac5fe <xQueueSemaphoreTake>
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
4200c582:	45d9f0ef          	jal	420ac1de <xQueueGenericSend>
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
4200c4b4:	14aa00ef          	jal	420ac5fe <xQueueSemaphoreTake>
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
4200c500:	4df9f06f          	j	420ac1de <xQueueGenericSend>


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200d8c4 <factory_photo_step>:
4200d8c4:	0007a023          	sw	zero,0(a5)
4200d8c8:	5879                	li	a6,-2
4200d8ca:	00079223          	sh	zero,4(a5)
4200d8ce:	01078123          	sb	a6,2(a5)
4200d8d2:	0016c693          	xori	a3,a3,1
4200d8d6:	e6d9                	bnez	a3,4200d964 <factory_photo_step+0xa0>
4200d8d8:	e751                	bnez	a4,4200d964 <factory_photo_step+0xa0>
4200d8da:	00054703          	lbu	a4,0(a0)
4200d8de:	4695                	li	a3,5
4200d8e0:	00e6f363          	bgeu	a3,a4,4200d8e6 <factory_photo_step+0x22>
4200d8e4:	4701                	li	a4,0
4200d8e6:	3c0c56b7          	lui	a3,0x3c0c5
4200d8ea:	00171813          	slli	a6,a4,0x1
4200d8ee:	14468693          	addi	a3,a3,324 # 3c0c5144 <levels.0>
4200d8f2:	96c2                	add	a3,a3,a6
4200d8f4:	0006d683          	lhu	a3,0(a3)
4200d8f8:	4885                	li	a7,1
4200d8fa:	011781a3          	sb	a7,3(a5)
4200d8fe:	00d79023          	sh	a3,0(a5)
4200d902:	4689                	li	a3,2
4200d904:	04d71263          	bne	a4,a3,4200d948 <factory_photo_step+0x84>
4200d908:	4e01                	li	t3,0
4200d90a:	8df1                	and	a1,a1,a2
4200d90c:	4695                	li	a3,5
4200d90e:	00154803          	lbu	a6,1(a0)
4200d912:	01089333          	sll	t1,a7,a6
4200d916:	0065f333          	and	t1,a1,t1
4200d91a:	00180713          	addi	a4,a6,1
4200d91e:	00030963          	beqz	t1,4200d930 <factory_photo_step+0x6c>
4200d922:	02d76733          	rem	a4,a4,a3
4200d926:	01078123          	sb	a6,2(a5)
4200d92a:	00e500a3          	sb	a4,1(a0)
4200d92e:	a819                	j	4200d944 <factory_photo_step+0x80>
4200d930:	02d76733          	rem	a4,a4,a3
4200d934:	0e05                	addi	t3,t3,1
4200d936:	00e500a3          	sb	a4,1(a0)
4200d93a:	fcde1ae3          	bne	t3,a3,4200d90e <factory_photo_step+0x4a>
4200d93e:	577d                	li	a4,-1
4200d940:	00e78123          	sb	a4,2(a5)
4200d944:	470d                	li	a4,3
4200d946:	a039                	j	4200d954 <factory_photo_step+0x90>
4200d948:	0705                	addi	a4,a4,1
4200d94a:	0ff77713          	zext.b	a4,a4
4200d94e:	4699                	li	a3,6
4200d950:	00d70563          	beq	a4,a3,4200d95a <factory_photo_step+0x96>
4200d954:	00e50023          	sb	a4,0(a0)
4200d958:	8082                	ret
4200d95a:	00050023          	sb	zero,0(a0)
4200d95e:	01178223          	sb	a7,4(a5)
4200d962:	8082                	ret
4200d964:	8082                	ret
