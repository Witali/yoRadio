
small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200d28e <clock_task>:
4200d28e:	c5010113          	addi	sp,sp,-944
4200d292:	39512a23          	sw	s5,916(sp)
4200d296:	0ff00793          	li	a5,255
4200d29a:	3fcafab7          	lui	s5,0x3fcaf
4200d29e:	3b212023          	sw	s2,928(sp)
4200d2a2:	39412c23          	sw	s4,920(sp)
4200d2a6:	39712623          	sw	s7,908(sp)
4200d2aa:	39812423          	sw	s8,904(sp)
4200d2ae:	39912223          	sw	s9,900(sp)
4200d2b2:	39a12023          	sw	s10,896(sp)
4200d2b6:	37b12e23          	sw	s11,892(sp)
4200d2ba:	3a112623          	sw	ra,940(sp)
4200d2be:	3a812423          	sw	s0,936(sp)
4200d2c2:	3a912223          	sw	s1,932(sp)
4200d2c6:	39312e23          	sw	s3,924(sp)
4200d2ca:	39612823          	sw	s6,912(sp)
4200d2ce:	04010223          	sb	zero,68(sp)
4200d2d2:	04011423          	sh	zero,72(sp)
4200d2d6:	4c01                	li	s8,0
4200d2d8:	d002                	sw	zero,32(sp)
4200d2da:	4d01                	li	s10,0
4200d2dc:	ce02                	sw	zero,28(sp)
4200d2de:	cc3e                	sw	a5,24(sp)
4200d2e0:	ca02                	sw	zero,20(sp)
4200d2e2:	4901                	li	s2,0
4200d2e4:	d202                	sw	zero,36(sp)
4200d2e6:	4c81                	li	s9,0
4200d2e8:	4a01                	li	s4,0
4200d2ea:	c802                	sw	zero,16(sp)
4200d2ec:	4b81                	li	s7,0
4200d2ee:	4d85                	li	s11,1
4200d2f0:	73ca8a93          	addi	s5,s5,1852 # 3fcaf73c <timer_state>
4200d2f4:	0448                	addi	a0,sp,516
4200d2f6:	99aff0ef          	jal	4200c490 <settings_snapshot>
4200d2fa:	0228                	addi	a0,sp,264
4200d2fc:	6a1030ef          	jal	4201119c <weather_snapshot>
4200d300:	35114603          	lbu	a2,849(sp)
4200d304:	4581                	li	a1,0
4200d306:	00e8                	addi	a0,sp,76
4200d308:	f27ff0ef          	jal	4200d22e <timer_snapshot>
4200d30c:	05a14783          	lbu	a5,90(sp)
4200d310:	d63e                	sw	a5,44(sp)
4200d312:	739020ef          	jal	4201024a <network_connected>
4200d316:	45d1                	li	a1,20
4200d318:	8b2a                	mv	s6,a0
4200d31a:	1168                	addi	a0,sp,172
4200d31c:	763020ef          	jal	4201027e <network_address>
4200d320:	4501                	li	a0,0
4200d322:	7bd8f0ef          	jal	4209d2de <time>
4200d326:	c62e                	sw	a1,12(sp)
4200d328:	4632                	lw	a2,12(sp)
4200d32a:	c42a                	sw	a0,8(sp)
4200d32c:	85aa                	mv	a1,a0
4200d32e:	11d4                	addi	a3,sp,228
4200d330:	2ab10513          	addi	a0,sp,683
4200d334:	534030ef          	jal	42010868 <services_local_time>
4200d338:	89aa                	mv	s3,a0
4200d33a:	e51d                	bnez	a0,4200d368 <clock_task+0xda>
4200d33c:	4781                	li	a5,0
4200d33e:	10f12023          	sw	a5,256(sp)
4200d342:	02800793          	li	a5,40
4200d346:	d3be                	sw	a5,228(sp)
4200d348:	4791                	li	a5,4
4200d34a:	d5be                	sw	a5,232(sp)
4200d34c:	47c5                	li	a5,17
4200d34e:	d7be                	sw	a5,236(sp)
4200d350:	47cd                	li	a5,19
4200d352:	d9be                	sw	a5,240(sp)
4200d354:	47a1                	li	a5,8
4200d356:	dbbe                	sw	a5,244(sp)
4200d358:	07d00793          	li	a5,125
4200d35c:	4801                	li	a6,0
4200d35e:	ddbe                	sw	a5,248(sp)
4200d360:	4795                	li	a5,5
4200d362:	11012223          	sw	a6,260(sp)
4200d366:	dfbe                	sw	a5,252(sp)
4200d368:	02400613          	li	a2,36
4200d36c:	11cc                	addi	a1,sp,228
4200d36e:	0188                	addi	a0,sp,192
4200d370:	fe37a097          	auipc	ra,0xfe37a
4200d374:	eca080e7          	jalr	-310(ra) # 4038723a <memcpy>
4200d378:	a7cff0ef          	jal	4200c5f4 <settings_generation>
4200d37c:	d42a                	sw	a0,40(sp)
4200d37e:	4405                	li	s0,1
4200d380:	00ab9e63          	bne	s7,a0,4200d39c <clock_task+0x10e>
4200d384:	47c2                	lw	a5,16(sp)
4200d386:	1f812403          	lw	s0,504(sp)
4200d38a:	8c1d                	sub	s0,s0,a5
4200d38c:	5782                	lw	a5,32(sp)
4200d38e:	00803433          	snez	s0,s0
4200d392:	0137c7b3          	xor	a5,a5,s3
4200d396:	8c5d                	or	s0,s0,a5
4200d398:	0ff47413          	zext.b	s0,s0
4200d39c:	000b0d63          	beqz	s6,4200d3b6 <clock_task+0x128>
4200d3a0:	10814783          	lbu	a5,264(sp)
4200d3a4:	eb89                	bnez	a5,4200d3b6 <clock_task+0x128>
4200d3a6:	67d030ef          	jal	42011222 <weather_request_active>
4200d3aa:	e511                	bnez	a0,4200d3b6 <clock_task+0x128>
4200d3ac:	000c1d63          	bnez	s8,4200d3c6 <clock_task+0x138>
4200d3b0:	631030ef          	jal	420111e0 <weather_request_update>
4200d3b4:	4c79                	li	s8,30
4200d3b6:	078020ef          	jal	4200f42e <media_upload_active>
4200d3ba:	84aa                	mv	s1,a0
4200d3bc:	c519                	beqz	a0,4200d3ca <clock_task+0x13c>
4200d3be:	4529                	li	a0,10
4200d3c0:	3699f0ef          	jal	420acf28 <vTaskDelay>
4200d3c4:	bf05                	j	4200d2f4 <clock_task+0x66>
4200d3c6:	1c7d                	addi	s8,s8,-1
4200d3c8:	b7fd                	j	4200d3b6 <clock_task+0x128>
4200d3ca:	57b2                	lw	a5,44(sp)
4200d3cc:	1a078f63          	beqz	a5,4200d58a <clock_task+0x2fc>
4200d3d0:	140b0a63          	beqz	s6,4200d524 <clock_task+0x296>
4200d3d4:	00099763          	bnez	s3,4200d3e2 <clock_task+0x154>
4200d3d8:	34c14703          	lbu	a4,844(sp)
4200d3dc:	4789                	li	a5,2
4200d3de:	14f71363          	bne	a4,a5,4200d524 <clock_task+0x296>
4200d3e2:	fe37b097          	auipc	ra,0xfe37b
4200d3e6:	a54080e7          	jalr	-1452(ra) # 40387e36 <vPortEnterCritical>
4200d3ea:	004aa783          	lw	a5,4(s5)
4200d3ee:	000a8723          	sb	zero,14(s5)
4200d3f2:	f7f7f793          	andi	a5,a5,-129
4200d3f6:	00faa223          	sw	a5,4(s5)
4200d3fa:	fe37b097          	auipc	ra,0xfe37b
4200d3fe:	a68080e7          	jalr	-1432(ra) # 40387e62 <vPortExitCritical>
4200d402:	478d                	li	a5,3
4200d404:	00f91763          	bne	s2,a5,4200d412 <clock_task+0x184>
4200d408:	34c14783          	lbu	a5,844(sp)
4200d40c:	4762                	lw	a4,24(sp)
4200d40e:	04e78b63          	beq	a5,a4,4200d464 <clock_task+0x1d6>
4200d412:	0f000693          	li	a3,240
4200d416:	4701                	li	a4,0
4200d418:	8636                	mv	a2,a3
4200d41a:	4581                	li	a1,0
4200d41c:	4501                	li	a0,0
4200d41e:	fd6ff0ef          	jal	4200cbf4 <display_fill>
4200d422:	34c14703          	lbu	a4,844(sp)
4200d426:	4789                	li	a5,2
4200d428:	442d                	li	s0,11
4200d42a:	00f71363          	bne	a4,a5,4200d430 <clock_task+0x1a2>
4200d42e:	443d                	li	s0,15
4200d430:	fe37b097          	auipc	ra,0xfe37b
4200d434:	a06080e7          	jalr	-1530(ra) # 40387e36 <vPortEnterCritical>
4200d438:	004aa783          	lw	a5,4(s5)
4200d43c:	8fc1                	or	a5,a5,s0
4200d43e:	00faa223          	sw	a5,4(s5)
4200d442:	fe37b097          	auipc	ra,0xfe37b
4200d446:	a20080e7          	jalr	-1504(ra) # 40387e62 <vPortExitCritical>
4200d44a:	34c14783          	lbu	a5,844(sp)
4200d44e:	00fde863          	bltu	s11,a5,4200d45e <clock_task+0x1d0>
4200d452:	461e                	lw	a2,196(sp)
4200d454:	45ae                	lw	a1,200(sp)
4200d456:	86ce                	mv	a3,s3
4200d458:	0448                	addi	a0,sp,516
4200d45a:	d87ff0ef          	jal	4200d1e0 <backlight_update>
4200d45e:	4485                	li	s1,1
4200d460:	8426                	mv	s0,s1
4200d462:	4a01                	li	s4,0
4200d464:	10814783          	lbu	a5,264(sp)
4200d468:	c399                	beqz	a5,4200d46e <clock_task+0x1e0>
4200d46a:	000d1363          	bnez	s10,4200d470 <clock_task+0x1e2>
4200d46e:	4a01                	li	s4,0
4200d470:	34c14783          	lbu	a5,844(sp)
4200d474:	ef81                	bnez	a5,4200d48c <clock_task+0x1fe>
4200d476:	12048a63          	beqz	s1,4200d5aa <clock_task+0x31c>
4200d47a:	35114603          	lbu	a2,849(sp)
4200d47e:	4589                	li	a1,2
4200d480:	08e8                	addi	a0,sp,92
4200d482:	dadff0ef          	jal	4200d22e <timer_snapshot>
4200d486:	5786                	lw	a5,96(sp)
4200d488:	12079663          	bnez	a5,4200d5b4 <clock_task+0x326>
4200d48c:	34c14783          	lbu	a5,844(sp)
4200d490:	14079e63          	bnez	a5,4200d5ec <clock_task+0x35e>
4200d494:	34d14503          	lbu	a0,845(sp)
4200d498:	0d4020ef          	jal	4200f56c <media_animation_frames>
4200d49c:	85aa                	mv	a1,a0
4200d49e:	00c8                	addi	a0,sp,68
4200d4a0:	2135                	jal	4200d8cc <factory_animation_next>
4200d4a2:	35114603          	lbu	a2,849(sp)
4200d4a6:	892a                	mv	s2,a0
4200d4a8:	45a1                	li	a1,8
4200d4aa:	10e8                	addi	a0,sp,108
4200d4ac:	d83ff0ef          	jal	4200d22e <timer_snapshot>
4200d4b0:	4722                	lw	a4,8(sp)
4200d4b2:	5792                	lw	a5,36(sp)
4200d4b4:	5846                	lw	a6,112(sp)
4200d4b6:	8fb9                	xor	a5,a5,a4
4200d4b8:	4732                	lw	a4,12(sp)
4200d4ba:	01003833          	snez	a6,a6
4200d4be:	00ecc733          	xor	a4,s9,a4
4200d4c2:	8fd9                	or	a5,a5,a4
4200d4c4:	00f037b3          	snez	a5,a5
4200d4c8:	00f867b3          	or	a5,a6,a5
4200d4cc:	e399                	bnez	a5,4200d4d2 <clock_task+0x244>
4200d4ce:	10040463          	beqz	s0,4200d5d6 <clock_task+0x348>
4200d4d2:	fff94713          	not	a4,s2
4200d4d6:	877d                	srai	a4,a4,0x1f
4200d4d8:	87a6                	mv	a5,s1
4200d4da:	00e97733          	and	a4,s2,a4
4200d4de:	86d2                	mv	a3,s4
4200d4e0:	0230                	addi	a2,sp,264
4200d4e2:	018c                	addi	a1,sp,192
4200d4e4:	0448                	addi	a0,sp,516
4200d4e6:	6ad000ef          	jal	4200e392 <factory_draw_classic>
4200d4ea:	4ad000ef          	jal	4200e196 <factory_scroll_tick>
4200d4ee:	34c14703          	lbu	a4,844(sp)
4200d4f2:	4789                	li	a5,2
4200d4f4:	00f70863          	beq	a4,a5,4200d504 <clock_task+0x276>
4200d4f8:	461e                	lw	a2,196(sp)
4200d4fa:	45ae                	lw	a1,200(sp)
4200d4fc:	86ce                	mv	a3,s3
4200d4fe:	0448                	addi	a0,sp,516
4200d500:	ce1ff0ef          	jal	4200d1e0 <backlight_update>
4200d504:	34c14783          	lbu	a5,844(sp)
4200d508:	35114603          	lbu	a2,849(sp)
4200d50c:	04000593          	li	a1,64
4200d510:	0968                	addi	a0,sp,156
4200d512:	cc3e                	sw	a5,24(sp)
4200d514:	d1bff0ef          	jal	4200d22e <timer_snapshot>
4200d518:	578a                	lw	a5,160(sp)
4200d51a:	c399                	beqz	a5,4200d520 <clock_task+0x292>
4200d51c:	4c5030ef          	jal	420111e0 <weather_request_update>
4200d520:	490d                	li	s2,3
4200d522:	a0a9                	j	4200d56c <clock_task+0x2de>
4200d524:	05914403          	lbu	s0,89(sp)
4200d528:	47d2                	lw	a5,20(sp)
4200d52a:	197d                	addi	s2,s2,-1
4200d52c:	01203933          	snez	s2,s2
4200d530:	8f81                	sub	a5,a5,s0
4200d532:	00f037b3          	snez	a5,a5
4200d536:	0127e7b3          	or	a5,a5,s2
4200d53a:	e799                	bnez	a5,4200d548 <clock_task+0x2ba>
4200d53c:	47f2                	lw	a5,28(sp)
4200d53e:	0167c7b3          	xor	a5,a5,s6
4200d542:	0ff7f793          	zext.b	a5,a5
4200d546:	cb91                	beqz	a5,4200d55a <clock_task+0x2cc>
4200d548:	01603533          	snez	a0,s6
4200d54c:	40a00533          	neg	a0,a0
4200d550:	117c                	addi	a5,sp,172
4200d552:	85a2                	mv	a1,s0
4200d554:	8d7d                	and	a0,a0,a5
4200d556:	575000ef          	jal	4200e2ca <factory_draw_startup>
4200d55a:	35114603          	lbu	a2,849(sp)
4200d55e:	08000593          	li	a1,128
4200d562:	1808                	addi	a0,sp,48
4200d564:	ccbff0ef          	jal	4200d22e <timer_snapshot>
4200d568:	4905                	li	s2,1
4200d56a:	ca22                	sw	s0,20(sp)
4200d56c:	1f812783          	lw	a5,504(sp)
4200d570:	4529                	li	a0,10
4200d572:	10814d03          	lbu	s10,264(sp)
4200d576:	c83e                	sw	a5,16(sp)
4200d578:	1b19f0ef          	jal	420acf28 <vTaskDelay>
4200d57c:	47a2                	lw	a5,8(sp)
4200d57e:	4cb2                	lw	s9,12(sp)
4200d580:	5ba2                	lw	s7,40(sp)
4200d582:	d04e                	sw	s3,32(sp)
4200d584:	ce5a                	sw	s6,28(sp)
4200d586:	d23e                	sw	a5,36(sp)
4200d588:	b3b5                	j	4200d2f4 <clock_task+0x66>
4200d58a:	e60b1ce3          	bnez	s6,4200d402 <clock_task+0x174>
4200d58e:	4d7020ef          	jal	42010264 <network_ap_active>
4200d592:	c901                	beqz	a0,4200d5a2 <clock_task+0x314>
4200d594:	4409                	li	s0,2
4200d596:	fc890be3          	beq	s2,s0,4200d56c <clock_task+0x2de>
4200d59a:	49b000ef          	jal	4200e234 <factory_draw_setup>
4200d59e:	8922                	mv	s2,s0
4200d5a0:	b7f1                	j	4200d56c <clock_task+0x2de>
4200d5a2:	478d                	li	a5,3
4200d5a4:	fcf914e3          	bne	s2,a5,4200d56c <clock_task+0x2de>
4200d5a8:	b585                	j	4200d408 <clock_task+0x17a>
4200d5aa:	469000ef          	jal	4200e212 <factory_scroll_description_ready>
4200d5ae:	ec0516e3          	bnez	a0,4200d47a <clock_task+0x1ec>
4200d5b2:	bde9                	j	4200d48c <clock_task+0x1fe>
4200d5b4:	e891                	bnez	s1,4200d5c8 <clock_task+0x33a>
4200d5b6:	10814783          	lbu	a5,264(sp)
4200d5ba:	c799                	beqz	a5,4200d5c8 <clock_task+0x33a>
4200d5bc:	000d0663          	beqz	s10,4200d5c8 <clock_task+0x33a>
4200d5c0:	0a05                	addi	s4,s4,1
4200d5c2:	47a9                	li	a5,10
4200d5c4:	02fa7a33          	remu	s4,s4,a5
4200d5c8:	ec0412e3          	bnez	s0,4200d48c <clock_task+0x1fe>
4200d5cc:	34c14403          	lbu	s0,844(sp)
4200d5d0:	00143413          	seqz	s0,s0
4200d5d4:	bd65                	j	4200d48c <clock_task+0x1fe>
4200d5d6:	f0094ae3          	bltz	s2,4200d4ea <clock_task+0x25c>
4200d5da:	34d14503          	lbu	a0,845(sp)
4200d5de:	0a000693          	li	a3,160
4200d5e2:	8636                	mv	a2,a3
4200d5e4:	85ca                	mv	a1,s2
4200d5e6:	7e1010ef          	jal	4200f5c6 <media_draw_animation>
4200d5ea:	b701                	j	4200d4ea <clock_task+0x25c>
4200d5ec:	03b79463          	bne	a5,s11,4200d614 <clock_task+0x386>
4200d5f0:	35114603          	lbu	a2,849(sp)
4200d5f4:	18e8                	addi	a0,sp,124
4200d5f6:	45a5                	li	a1,9
4200d5f8:	c37ff0ef          	jal	4200d22e <timer_snapshot>
4200d5fc:	470a                	lw	a4,128(sp)
4200d5fe:	86a6                	mv	a3,s1
4200d600:	1170                	addi	a2,sp,172
4200d602:	00375793          	srli	a5,a4,0x3
4200d606:	8b85                	andi	a5,a5,1
4200d608:	8b05                	andi	a4,a4,1
4200d60a:	018c                	addi	a1,sp,192
4200d60c:	0448                	addi	a0,sp,516
4200d60e:	38e010ef          	jal	4200e99c <factory_draw_simple>
4200d612:	bdf1                	j	4200d4ee <clock_task+0x260>
4200d614:	4709                	li	a4,2
4200d616:	0ae79763          	bne	a5,a4,4200d6c4 <clock_task+0x436>
4200d61a:	0458                	addi	a4,sp,516
4200d61c:	4781                	li	a5,0
4200d61e:	4601                	li	a2,0
4200d620:	4695                	li	a3,5
4200d622:	15872583          	lw	a1,344(a4)
4200d626:	c581                	beqz	a1,4200d62e <clock_task+0x3a0>
4200d628:	00fd95b3          	sll	a1,s11,a5
4200d62c:	8e4d                	or	a2,a2,a1
4200d62e:	0785                	addi	a5,a5,1
4200d630:	0711                	addi	a4,a4,4
4200d632:	fed798e3          	bne	a5,a3,4200d622 <clock_task+0x394>
4200d636:	46c6                	lw	a3,80(sp)
4200d638:	35814583          	lbu	a1,856(sp)
4200d63c:	11dc                	addi	a5,sp,228
4200d63e:	8289                	srli	a3,a3,0x2
4200d640:	8a85                	andi	a3,a3,1
4200d642:	8ec5                	or	a3,a3,s1
4200d644:	4701                	li	a4,0
4200d646:	0ff6f693          	zext.b	a3,a3
4200d64a:	00a8                	addi	a0,sp,72
4200d64c:	2af9                	jal	4200d82a <factory_photo_step>
4200d64e:	0e714783          	lbu	a5,231(sp)
4200d652:	c789                	beqz	a5,4200d65c <clock_task+0x3ce>
4200d654:	0e415503          	lhu	a0,228(sp)
4200d658:	ab7ff0ef          	jal	4200d10e <backlight_set_level>
4200d65c:	0e610503          	lb	a0,230(sp)
4200d660:	57fd                	li	a5,-1
4200d662:	02f54663          	blt	a0,a5,4200d68e <clock_task+0x400>
4200d666:	04f51b63          	bne	a0,a5,4200d6bc <clock_task+0x42e>
4200d66a:	0f000693          	li	a3,240
4200d66e:	8636                	mv	a2,a3
4200d670:	4701                	li	a4,0
4200d672:	4581                	li	a1,0
4200d674:	4501                	li	a0,0
4200d676:	d7eff0ef          	jal	4200cbf4 <display_fill>
4200d67a:	6741                	lui	a4,0x10
4200d67c:	4805                	li	a6,1
4200d67e:	4781                	li	a5,0
4200d680:	177d                	addi	a4,a4,-1 # ffff <CSR_UINTSTATUS+0xf34e>
4200d682:	46c1                	li	a3,16
4200d684:	1170                	addi	a2,sp,172
4200d686:	0e100593          	li	a1,225
4200d68a:	4515                	li	a0,5
4200d68c:	2355                	jal	4200dc30 <display_factory_text>
4200d68e:	0e814783          	lbu	a5,232(sp)
4200d692:	c799                	beqz	a5,4200d6a0 <clock_task+0x412>
4200d694:	35114603          	lbu	a2,849(sp)
4200d698:	4591                	li	a1,4
4200d69a:	1808                	addi	a0,sp,48
4200d69c:	b93ff0ef          	jal	4200d22e <timer_snapshot>
4200d6a0:	0e714783          	lbu	a5,231(sp)
4200d6a4:	c789                	beqz	a5,4200d6ae <clock_task+0x420>
4200d6a6:	0e814783          	lbu	a5,232(sp)
4200d6aa:	e40782e3          	beqz	a5,4200d4ee <clock_task+0x260>
4200d6ae:	461e                	lw	a2,196(sp)
4200d6b0:	45ae                	lw	a1,200(sp)
4200d6b2:	86ce                	mv	a3,s3
4200d6b4:	0448                	addi	a0,sp,516
4200d6b6:	b2bff0ef          	jal	4200d1e0 <backlight_update>
4200d6ba:	bd15                	j	4200d4ee <clock_task+0x260>
4200d6bc:	116c                	addi	a1,sp,172
4200d6be:	1f9010ef          	jal	4200f0b6 <factory_draw_photo>
4200d6c2:	b7f1                	j	4200d68e <clock_task+0x400>
4200d6c4:	35114603          	lbu	a2,849(sp)
4200d6c8:	4585                	li	a1,1
4200d6ca:	0168                	addi	a0,sp,140
4200d6cc:	b63ff0ef          	jal	4200d22e <timer_snapshot>
4200d6d0:	47ca                	lw	a5,144(sp)
4200d6d2:	00f037b3          	snez	a5,a5
4200d6d6:	8fc5                	or	a5,a5,s1
4200d6d8:	0ff7f793          	zext.b	a5,a5
4200d6dc:	e399                	bnez	a5,4200d6e2 <clock_task+0x454>
4200d6de:	e00408e3          	beqz	s0,4200d4ee <clock_task+0x260>
4200d6e2:	8626                	mv	a2,s1
4200d6e4:	116c                	addi	a1,sp,172
4200d6e6:	0188                	addi	a0,sp,192
4200d6e8:	4d6010ef          	jal	4200ebbe <factory_draw_dial>
4200d6ec:	b509                	j	4200d4ee <clock_task+0x260>


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200d82a <factory_photo_step>:
4200d82a:	0007a023          	sw	zero,0(a5)
4200d82e:	5879                	li	a6,-2
4200d830:	00079223          	sh	zero,4(a5)
4200d834:	01078123          	sb	a6,2(a5)
4200d838:	0016c693          	xori	a3,a3,1
4200d83c:	e6d9                	bnez	a3,4200d8ca <factory_photo_step+0xa0>
4200d83e:	e751                	bnez	a4,4200d8ca <factory_photo_step+0xa0>
4200d840:	00054703          	lbu	a4,0(a0)
4200d844:	4695                	li	a3,5
4200d846:	00e6f363          	bgeu	a3,a4,4200d84c <factory_photo_step+0x22>
4200d84a:	4701                	li	a4,0
4200d84c:	3c0c56b7          	lui	a3,0x3c0c5
4200d850:	00171813          	slli	a6,a4,0x1
4200d854:	14468693          	addi	a3,a3,324 # 3c0c5144 <levels.0>
4200d858:	96c2                	add	a3,a3,a6
4200d85a:	0006d683          	lhu	a3,0(a3)
4200d85e:	4885                	li	a7,1
4200d860:	011781a3          	sb	a7,3(a5)
4200d864:	00d79023          	sh	a3,0(a5)
4200d868:	4689                	li	a3,2
4200d86a:	04d71263          	bne	a4,a3,4200d8ae <factory_photo_step+0x84>
4200d86e:	4e01                	li	t3,0
4200d870:	8df1                	and	a1,a1,a2
4200d872:	4695                	li	a3,5
4200d874:	00154803          	lbu	a6,1(a0)
4200d878:	01089333          	sll	t1,a7,a6
4200d87c:	0065f333          	and	t1,a1,t1
4200d880:	00180713          	addi	a4,a6,1
4200d884:	00030963          	beqz	t1,4200d896 <factory_photo_step+0x6c>
4200d888:	02d76733          	rem	a4,a4,a3
4200d88c:	01078123          	sb	a6,2(a5)
4200d890:	00e500a3          	sb	a4,1(a0)
4200d894:	a819                	j	4200d8aa <factory_photo_step+0x80>
4200d896:	02d76733          	rem	a4,a4,a3
4200d89a:	0e05                	addi	t3,t3,1
4200d89c:	00e500a3          	sb	a4,1(a0)
4200d8a0:	fcde1ae3          	bne	t3,a3,4200d874 <factory_photo_step+0x4a>
4200d8a4:	577d                	li	a4,-1
4200d8a6:	00e78123          	sb	a4,2(a5)
4200d8aa:	470d                	li	a4,3
4200d8ac:	a039                	j	4200d8ba <factory_photo_step+0x90>
4200d8ae:	0705                	addi	a4,a4,1
4200d8b0:	0ff77713          	zext.b	a4,a4
4200d8b4:	4699                	li	a3,6
4200d8b6:	00d70563          	beq	a4,a3,4200d8c0 <factory_photo_step+0x96>
4200d8ba:	00e50023          	sb	a4,0(a0)
4200d8be:	8082                	ret
4200d8c0:	00050023          	sb	zero,0(a0)
4200d8c4:	01178223          	sb	a7,4(a5)
4200d8c8:	8082                	ret
4200d8ca:	8082                	ret


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200d1e0 <backlight_update>:
4200d1e0:	14b54783          	lbu	a5,331(a0)
4200d1e4:	03c00713          	li	a4,60
4200d1e8:	02e585b3          	mul	a1,a1,a4
4200d1ec:	02e787b3          	mul	a5,a5,a4
4200d1f0:	962e                	add	a2,a2,a1
4200d1f2:	02f67863          	bgeu	a2,a5,4200d222 <backlight_update+0x42>
4200d1f6:	2d000793          	li	a5,720
4200d1fa:	02c7e663          	bltu	a5,a2,4200d226 <backlight_update+0x46>
4200d1fe:	14c54783          	lbu	a5,332(a0)
4200d202:	02e787b3          	mul	a5,a5,a4
4200d206:	00c7b7b3          	sltu	a5,a5,a2
4200d20a:	15254703          	lbu	a4,338(a0)
4200d20e:	cf01                	beqz	a4,4200d226 <backlight_update+0x46>
4200d210:	eb99                	bnez	a5,4200d226 <backlight_update+0x46>
4200d212:	14055503          	lhu	a0,320(a0)
4200d216:	8601a783          	lw	a5,-1952(gp) # 3fcab590 <backlight_applied_level>
4200d21a:	00a78963          	beq	a5,a0,4200d22c <backlight_update+0x4c>
4200d21e:	ef1ff06f          	j	4200d10e <backlight_set_level>
4200d222:	4781                	li	a5,0
4200d224:	b7dd                	j	4200d20a <backlight_update+0x2a>
4200d226:	13e55503          	lhu	a0,318(a0)
4200d22a:	b7f5                	j	4200d216 <backlight_update+0x36>
4200d22c:	8082                	ret


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200d10e <backlight_set_level>:
4200d10e:	1141                	addi	sp,sp,-16
4200d110:	c422                	sw	s0,8(sp)
4200d112:	3e800793          	li	a5,1000
4200d116:	c606                	sw	ra,12(sp)
4200d118:	843e                	mv	s0,a5
4200d11a:	00a7e363          	bltu	a5,a0,4200d120 <backlight_set_level+0x12>
4200d11e:	842a                	mv	s0,a0
4200d120:	6789                	lui	a5,0x2
4200d122:	17fd                	addi	a5,a5,-1 # 1fff <CSR_UINTSTATUS+0x134e>
4200d124:	02f407b3          	mul	a5,s0,a5
4200d128:	3e800613          	li	a2,1000
4200d12c:	4581                	li	a1,0
4200d12e:	4501                	li	a0,0
4200d130:	02c7d633          	divu	a2,a5,a2
4200d134:	26b090ef          	jal	42016b9e <ledc_set_duty>
4200d138:	c11d                	beqz	a0,4200d15e <backlight_set_level+0x50>
4200d13a:	3c0b4737          	lui	a4,0x3c0b4
4200d13e:	3c0c56b7          	lui	a3,0x3c0c5
4200d142:	9d070713          	addi	a4,a4,-1584 # 3c0b39d0 <_esp_libc_clock_array_end+0x3880>
4200d146:	12068693          	addi	a3,a3,288 # 3c0c5120 <__func__.0>
4200d14a:	02b00613          	li	a2,43
4200d14e:	3c0b45b7          	lui	a1,0x3c0b4
4200d152:	a1c58593          	addi	a1,a1,-1508 # 3c0b3a1c <_esp_libc_clock_array_end+0x38cc>
4200d156:	fe37b097          	auipc	ra,0xfe37b
4200d15a:	a7e080e7          	jalr	-1410(ra) # 40387bd4 <_esp_error_check_failed>
4200d15e:	4581                	li	a1,0
4200d160:	488090ef          	jal	420165e8 <ledc_update_duty>
4200d164:	cd01                	beqz	a0,4200d17c <backlight_set_level+0x6e>
4200d166:	3c0b4737          	lui	a4,0x3c0b4
4200d16a:	3c0c56b7          	lui	a3,0x3c0c5
4200d16e:	a3870713          	addi	a4,a4,-1480 # 3c0b3a38 <_esp_libc_clock_array_end+0x38e8>
4200d172:	12068693          	addi	a3,a3,288 # 3c0c5120 <__func__.0>
4200d176:	02c00613          	li	a2,44
4200d17a:	bfd1                	j	4200d14e <backlight_set_level+0x40>
4200d17c:	40b2                	lw	ra,12(sp)
4200d17e:	8681a023          	sw	s0,-1952(gp) # 3fcab590 <backlight_applied_level>
4200d182:	4422                	lw	s0,8(sp)
4200d184:	0141                	addi	sp,sp,16
4200d186:	8082                	ret
