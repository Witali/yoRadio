
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
4200d2fc:	695030ef          	jal	42011190 <weather_snapshot>
4200d300:	35114603          	lbu	a2,849(sp)
4200d304:	4581                	li	a1,0
4200d306:	00e8                	addi	a0,sp,76
4200d308:	f27ff0ef          	jal	4200d22e <timer_snapshot>
4200d30c:	05a14783          	lbu	a5,90(sp)
4200d310:	d63e                	sw	a5,44(sp)
4200d312:	72d020ef          	jal	4201023e <network_connected>
4200d316:	45d1                	li	a1,20
4200d318:	8b2a                	mv	s6,a0
4200d31a:	1168                	addi	a0,sp,172
4200d31c:	757020ef          	jal	42010272 <network_address>
4200d320:	4501                	li	a0,0
4200d322:	7838f0ef          	jal	4209d2a4 <time>
4200d326:	c62e                	sw	a1,12(sp)
4200d328:	4632                	lw	a2,12(sp)
4200d32a:	c42a                	sw	a0,8(sp)
4200d32c:	85aa                	mv	a1,a0
4200d32e:	11d4                	addi	a3,sp,228
4200d330:	2ab10513          	addi	a0,sp,683
4200d334:	528030ef          	jal	4201085c <services_local_time>
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
4200d3a6:	671030ef          	jal	42011216 <weather_request_active>
4200d3aa:	e511                	bnez	a0,4200d3b6 <clock_task+0x128>
4200d3ac:	000c1d63          	bnez	s8,4200d3c6 <clock_task+0x138>
4200d3b0:	625030ef          	jal	420111d4 <weather_request_update>
4200d3b4:	4c79                	li	s8,30
4200d3b6:	06c020ef          	jal	4200f422 <media_upload_active>
4200d3ba:	84aa                	mv	s1,a0
4200d3bc:	c519                	beqz	a0,4200d3ca <clock_task+0x13c>
4200d3be:	4529                	li	a0,10
4200d3c0:	32f9f0ef          	jal	420aceee <vTaskDelay>
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
4200d498:	0c8020ef          	jal	4200f560 <media_animation_frames>
4200d49c:	85aa                	mv	a1,a0
4200d49e:	00c8                	addi	a0,sp,68
4200d4a0:	2105                	jal	4200d8c0 <factory_animation_next>
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
4200d4e6:	6a1000ef          	jal	4200e386 <factory_draw_classic>
4200d4ea:	4a1000ef          	jal	4200e18a <factory_scroll_tick>
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
4200d51c:	4b9030ef          	jal	420111d4 <weather_request_update>
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
4200d556:	569000ef          	jal	4200e2be <factory_draw_startup>
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
4200d578:	1779f0ef          	jal	420aceee <vTaskDelay>
4200d57c:	47a2                	lw	a5,8(sp)
4200d57e:	4cb2                	lw	s9,12(sp)
4200d580:	5ba2                	lw	s7,40(sp)
4200d582:	d04e                	sw	s3,32(sp)
4200d584:	ce5a                	sw	s6,28(sp)
4200d586:	d23e                	sw	a5,36(sp)
4200d588:	b3b5                	j	4200d2f4 <clock_task+0x66>
4200d58a:	e60b1ce3          	bnez	s6,4200d402 <clock_task+0x174>
4200d58e:	4cb020ef          	jal	42010258 <network_ap_active>
4200d592:	c901                	beqz	a0,4200d5a2 <clock_task+0x314>
4200d594:	4409                	li	s0,2
4200d596:	fc890be3          	beq	s2,s0,4200d56c <clock_task+0x2de>
4200d59a:	48f000ef          	jal	4200e228 <factory_draw_setup>
4200d59e:	8922                	mv	s2,s0
4200d5a0:	b7f1                	j	4200d56c <clock_task+0x2de>
4200d5a2:	478d                	li	a5,3
4200d5a4:	fcf914e3          	bne	s2,a5,4200d56c <clock_task+0x2de>
4200d5a8:	b585                	j	4200d408 <clock_task+0x17a>
4200d5aa:	45d000ef          	jal	4200e206 <factory_scroll_description_ready>
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
4200d5e6:	7d5010ef          	jal	4200f5ba <media_draw_animation>
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
4200d60e:	382010ef          	jal	4200e990 <factory_draw_simple>
4200d612:	bdf1                	j	4200d4ee <clock_task+0x260>
4200d614:	4709                	li	a4,2
4200d616:	0ae79163          	bne	a5,a4,4200d6b8 <clock_task+0x42a>
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
4200d64c:	2ac9                	jal	4200d81e <factory_photo_step>
4200d64e:	0e714783          	lbu	a5,231(sp)
4200d652:	c789                	beqz	a5,4200d65c <clock_task+0x3ce>
4200d654:	0e415503          	lhu	a0,228(sp)
4200d658:	ab7ff0ef          	jal	4200d10e <backlight_set_level>
4200d65c:	0e610503          	lb	a0,230(sp)
4200d660:	57fd                	li	a5,-1
4200d662:	02f54663          	blt	a0,a5,4200d68e <clock_task+0x400>
4200d666:	04f51563          	bne	a0,a5,4200d6b0 <clock_task+0x422>
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
4200d68c:	2b61                	jal	4200dc24 <display_factory_text>
4200d68e:	0e814783          	lbu	a5,232(sp)
4200d692:	e4078ee3          	beqz	a5,4200d4ee <clock_task+0x260>
4200d696:	35114603          	lbu	a2,849(sp)
4200d69a:	1808                	addi	a0,sp,48
4200d69c:	4591                	li	a1,4
4200d69e:	b91ff0ef          	jal	4200d22e <timer_snapshot>
4200d6a2:	461e                	lw	a2,196(sp)
4200d6a4:	45ae                	lw	a1,200(sp)
4200d6a6:	86ce                	mv	a3,s3
4200d6a8:	0448                	addi	a0,sp,516
4200d6aa:	b37ff0ef          	jal	4200d1e0 <backlight_update>
4200d6ae:	b581                	j	4200d4ee <clock_task+0x260>
4200d6b0:	116c                	addi	a1,sp,172
4200d6b2:	1f9010ef          	jal	4200f0aa <factory_draw_photo>
4200d6b6:	bfe1                	j	4200d68e <clock_task+0x400>
4200d6b8:	35114603          	lbu	a2,849(sp)
4200d6bc:	4585                	li	a1,1
4200d6be:	0168                	addi	a0,sp,140
4200d6c0:	b6fff0ef          	jal	4200d22e <timer_snapshot>
4200d6c4:	47ca                	lw	a5,144(sp)
4200d6c6:	00f037b3          	snez	a5,a5
4200d6ca:	8fc5                	or	a5,a5,s1
4200d6cc:	0ff7f793          	zext.b	a5,a5
4200d6d0:	e399                	bnez	a5,4200d6d6 <clock_task+0x448>
4200d6d2:	e0040ee3          	beqz	s0,4200d4ee <clock_task+0x260>
4200d6d6:	8626                	mv	a2,s1
4200d6d8:	116c                	addi	a1,sp,172
4200d6da:	0188                	addi	a0,sp,192
4200d6dc:	4d6010ef          	jal	4200ebb2 <factory_draw_dial>
4200d6e0:	b539                	j	4200d4ee <clock_task+0x260>


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200d6e2 <clock_ui_timer_init>:
4200d6e2:	7161                	addi	sp,sp,-432
4200d6e4:	1848                	addi	a0,sp,52
4200d6e6:	1a112623          	sw	ra,428(sp)
4200d6ea:	1a812423          	sw	s0,424(sp)
4200d6ee:	da3fe0ef          	jal	4200c490 <settings_snapshot>
4200d6f2:	18114703          	lbu	a4,385(sp)
4200d6f6:	3fcb47b7          	lui	a5,0x3fcb4
4200d6fa:	4581                	li	a1,0
4200d6fc:	8ee7ac23          	sw	a4,-1800(a5) # 3fcb38f8 <photo_interval>
4200d700:	18914703          	lbu	a4,393(sp)
4200d704:	4785                	li	a5,1
4200d706:	00f71663          	bne	a4,a5,4200d712 <clock_ui_timer_init+0x30>
4200d70a:	03814583          	lbu	a1,56(sp)
4200d70e:	00b035b3          	snez	a1,a1
4200d712:	3fcaf537          	lui	a0,0x3fcaf
4200d716:	73c50513          	addi	a0,a0,1852 # 3fcaf73c <timer_state>
4200d71a:	28f9                	jal	4200d7f8 <factory_timer_init>
4200d71c:	4781                	li	a5,0
4200d71e:	c83e                	sw	a5,16(sp)
4200d720:	47ad                	li	a5,11
4200d722:	c23e                	sw	a5,4(sp)
4200d724:	4785                	li	a5,1
4200d726:	c43e                	sw	a5,8(sp)
4200d728:	3fcb4437          	lui	s0,0x3fcb4
4200d72c:	000f47b7          	lui	a5,0xf4
4200d730:	4801                	li	a6,0
4200d732:	24078793          	addi	a5,a5,576 # f4240 <CSR_UINTSTATUS+0xf358f>
4200d736:	8f440593          	addi	a1,s0,-1804 # 3fcb38f4 <clock_timer>
4200d73a:	0048                	addi	a0,sp,4
4200d73c:	ca42                	sw	a6,20(sp)
4200d73e:	c63e                	sw	a5,12(sp)
4200d740:	28d9b0ef          	jal	420a91cc <gptimer_new_timer>
4200d744:	e929                	bnez	a0,4200d796 <clock_ui_timer_init+0xb4>
4200d746:	4781                	li	a5,0
4200d748:	d402                	sw	zero,40(sp)
4200d74a:	ce3e                	sw	a5,28(sp)
4200d74c:	8f442503          	lw	a0,-1804(s0)
4200d750:	4785                	li	a5,1
4200d752:	6761                	lui	a4,0x18
4200d754:	02f10423          	sb	a5,40(sp)
4200d758:	403827b7          	lui	a5,0x40382
4200d75c:	6a070713          	addi	a4,a4,1696 # 186a0 <CSR_UINTSTATUS+0x179ef>
4200d760:	f4678793          	addi	a5,a5,-186 # 40381f46 <timer_alarm>
4200d764:	082c                	addi	a1,sp,24
4200d766:	d002                	sw	zero,32(sp)
4200d768:	d202                	sw	zero,36(sp)
4200d76a:	d602                	sw	zero,44(sp)
4200d76c:	cc3a                	sw	a4,24(sp)
4200d76e:	c03e                	sw	a5,0(sp)
4200d770:	6db9b0ef          	jal	420a964a <gptimer_set_alarm_action>
4200d774:	e10d                	bnez	a0,4200d796 <clock_ui_timer_init+0xb4>
4200d776:	8f442503          	lw	a0,-1804(s0)
4200d77a:	4601                	li	a2,0
4200d77c:	858a                	mv	a1,sp
4200d77e:	5539b0ef          	jal	420a94d0 <gptimer_register_event_callbacks>
4200d782:	e911                	bnez	a0,4200d796 <clock_ui_timer_init+0xb4>
4200d784:	8f442503          	lw	a0,-1804(s0)
4200d788:	7f59b0ef          	jal	420a977c <gptimer_enable>
4200d78c:	e509                	bnez	a0,4200d796 <clock_ui_timer_init+0xb4>
4200d78e:	8f442503          	lw	a0,-1804(s0)
4200d792:	0ca9c0ef          	jal	420a985c <gptimer_start>
4200d796:	1ac12083          	lw	ra,428(sp)
4200d79a:	1a812403          	lw	s0,424(sp)
4200d79e:	615d                	addi	sp,sp,432
4200d7a0:	8082                	ret


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

40381f6c <factory_timer_tick>:
40381f6c:	87aa                	mv	a5,a0
40381f6e:	00e54503          	lbu	a0,14(a0)
40381f72:	c115                	beqz	a0,40381f96 <factory_timer_tick+0x2a>
40381f74:	00d7c703          	lbu	a4,13(a5)
40381f78:	0b400693          	li	a3,180
40381f7c:	0705                	addi	a4,a4,1
40381f7e:	0ff77713          	zext.b	a4,a4
40381f82:	00e786a3          	sb	a4,13(a5)
40381f86:	00e6f463          	bgeu	a3,a4,40381f8e <factory_timer_tick+0x22>
40381f8a:	00078723          	sb	zero,14(a5)
40381f8e:	43d8                	lw	a4,4(a5)
40381f90:	08076713          	ori	a4,a4,128
40381f94:	c3d8                	sw	a4,4(a5)
40381f96:	0087c703          	lbu	a4,8(a5)
40381f9a:	46a9                	li	a3,10
40381f9c:	0705                	addi	a4,a4,1
40381f9e:	0ff77713          	zext.b	a4,a4
40381fa2:	00e6e563          	bltu	a3,a4,40381fac <factory_timer_tick+0x40>
40381fa6:	00e78423          	sb	a4,8(a5)
40381faa:	8082                	ret
40381fac:	43d4                	lw	a3,4(a5)
40381fae:	00078423          	sb	zero,8(a5)
40381fb2:	4609                	li	a2,2
40381fb4:	0016e713          	ori	a4,a3,1
40381fb8:	c3d8                	sw	a4,4(a5)
40381fba:	0097c703          	lbu	a4,9(a5)
40381fbe:	0705                	addi	a4,a4,1
40381fc0:	0ff77713          	zext.b	a4,a4
40381fc4:	04e66b63          	bltu	a2,a4,4038201a <factory_timer_tick+0xae>
40381fc8:	00e784a3          	sb	a4,9(a5)
40381fcc:	00a7c703          	lbu	a4,10(a5)
40381fd0:	0705                	addi	a4,a4,1
40381fd2:	0ff77713          	zext.b	a4,a4
40381fd6:	04b77863          	bgeu	a4,a1,40382026 <factory_timer_tick+0xba>
40381fda:	00e78523          	sb	a4,10(a5)
40381fde:	00b7c703          	lbu	a4,11(a5)
40381fe2:	03b00693          	li	a3,59
40381fe6:	0705                	addi	a4,a4,1
40381fe8:	0ff77713          	zext.b	a4,a4
40381fec:	04e6e463          	bltu	a3,a4,40382034 <factory_timer_tick+0xc8>
40381ff0:	00e785a3          	sb	a4,11(a5)
40381ff4:	00c7c703          	lbu	a4,12(a5)
40381ff8:	0b400693          	li	a3,180
40381ffc:	0705                	addi	a4,a4,1
40381ffe:	0ff77713          	zext.b	a4,a4
40382002:	04e6e063          	bltu	a3,a4,40382042 <factory_timer_tick+0xd6>
40382006:	00e78623          	sb	a4,12(a5)
4038200a:	4398                	lw	a4,0(a5)
4038200c:	70800693          	li	a3,1800
40382010:	0705                	addi	a4,a4,1
40382012:	02e6ef63          	bltu	a3,a4,40382050 <factory_timer_tick+0xe4>
40382016:	c398                	sw	a4,0(a5)
40382018:	8082                	ret
4038201a:	0036e693          	ori	a3,a3,3
4038201e:	000784a3          	sb	zero,9(a5)
40382022:	c3d4                	sw	a3,4(a5)
40382024:	b765                	j	40381fcc <factory_timer_tick+0x60>
40382026:	43d8                	lw	a4,4(a5)
40382028:	00078523          	sb	zero,10(a5)
4038202c:	00476713          	ori	a4,a4,4
40382030:	c3d8                	sw	a4,4(a5)
40382032:	b775                	j	40381fde <factory_timer_tick+0x72>
40382034:	43d8                	lw	a4,4(a5)
40382036:	000785a3          	sb	zero,11(a5)
4038203a:	01876713          	ori	a4,a4,24
4038203e:	c3d8                	sw	a4,4(a5)
40382040:	bf55                	j	40381ff4 <factory_timer_tick+0x88>
40382042:	43d8                	lw	a4,4(a5)
40382044:	00078623          	sb	zero,12(a5)
40382048:	02076713          	ori	a4,a4,32
4038204c:	c3d8                	sw	a4,4(a5)
4038204e:	bf75                	j	4038200a <factory_timer_tick+0x9e>
40382050:	43d8                	lw	a4,4(a5)
40382052:	0007a023          	sw	zero,0(a5)
40382056:	04076713          	ori	a4,a4,64
4038205a:	c3d8                	sw	a4,4(a5)
4038205c:	8082                	ret

Disassembly of section .flash.text:


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200e18a <factory_scroll_tick>:
4200e18a:	3fcb0537          	lui	a0,0x3fcb0
4200e18e:	1101                	addi	sp,sp,-32
4200e190:	95050513          	addi	a0,a0,-1712 # 3fcaf950 <scrolling_labels>
4200e194:	cc22                	sw	s0,24(sp)
4200e196:	ce06                	sw	ra,28(sp)
4200e198:	12c50413          	addi	s0,a0,300
4200e19c:	4574                	lw	a3,76(a0)
4200e19e:	00d05963          	blez	a3,4200e1b0 <factory_scroll_tick+0x26>
4200e1a2:	4978                	lw	a4,84(a0)
4200e1a4:	00e6f663          	bgeu	a3,a4,4200e1b0 <factory_scroll_tick+0x26>
4200e1a8:	4d7c                	lw	a5,92(a0)
4200e1aa:	cb99                	beqz	a5,4200e1c0 <factory_scroll_tick+0x36>
4200e1ac:	17fd                	addi	a5,a5,-1
4200e1ae:	cd7c                	sw	a5,92(a0)
4200e1b0:	06450513          	addi	a0,a0,100
4200e1b4:	fe8514e3          	bne	a0,s0,4200e19c <factory_scroll_tick+0x12>
4200e1b8:	40f2                	lw	ra,28(sp)
4200e1ba:	4462                	lw	s0,24(sp)
4200e1bc:	6105                	addi	sp,sp,32
4200e1be:	8082                	ret
4200e1c0:	8f15                	sub	a4,a4,a3
4200e1c2:	06054683          	lbu	a3,96(a0)
4200e1c6:	4d3c                	lw	a5,88(a0)
4200e1c8:	c695                	beqz	a3,4200e1f4 <factory_scroll_tick+0x6a>
4200e1ca:	ffe78613          	addi	a2,a5,-2
4200e1ce:	0027b793          	sltiu	a5,a5,2
4200e1d2:	17fd                	addi	a5,a5,-1
4200e1d4:	8ff1                	and	a5,a5,a2
4200e1d6:	cd3c                	sw	a5,88(a0)
4200e1d8:	c39d                	beqz	a5,4200e1fe <factory_scroll_tick+0x74>
4200e1da:	00f71863          	bne	a4,a5,4200e1ea <factory_scroll_tick+0x60>
4200e1de:	0016c693          	xori	a3,a3,1
4200e1e2:	47bd                	li	a5,15
4200e1e4:	06d50023          	sb	a3,96(a0)
4200e1e8:	cd7c                	sw	a5,92(a0)
4200e1ea:	c62a                	sw	a0,12(sp)
4200e1ec:	c1bff0ef          	jal	4200de06 <paint_scrolling_label>
4200e1f0:	4532                	lw	a0,12(sp)
4200e1f2:	bf7d                	j	4200e1b0 <factory_scroll_tick+0x26>
4200e1f4:	0789                	addi	a5,a5,2
4200e1f6:	fef770e3          	bgeu	a4,a5,4200e1d6 <factory_scroll_tick+0x4c>
4200e1fa:	87ba                	mv	a5,a4
4200e1fc:	bfe9                	j	4200e1d6 <factory_scroll_tick+0x4c>
4200e1fe:	4785                	li	a5,1
4200e200:	06f500a3          	sb	a5,97(a0)
4200e204:	bfe9                	j	4200e1de <factory_scroll_tick+0x54>


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200fc7a <wifi_event>:
4200fc7a:	3c1087b7          	lui	a5,0x3c108
4200fc7e:	01c7a783          	lw	a5,28(a5) # 3c10801c <IP_EVENT>
4200fc82:	02b79e63          	bne	a5,a1,4200fcbe <wifi_event+0x44>
4200fc86:	ee05                	bnez	a2,4200fcbe <wifi_event+0x44>
4200fc88:	cef1                	beqz	a3,4200fd64 <wifi_event+0xea>
4200fc8a:	42d8                	lw	a4,4(a3)
4200fc8c:	3fcb47b7          	lui	a5,0x3fcb4
4200fc90:	91478793          	addi	a5,a5,-1772 # 3fcb3914 <last_station_address>
4200fc94:	0310000f          	fence	rw,w
4200fc98:	c398                	sw	a4,0(a5)
4200fc9a:	0330000f          	fence	rw,rw
4200fc9e:	3fcb47b7          	lui	a5,0x3fcb4
4200fca2:	4705                	li	a4,1
4200fca4:	91c78793          	addi	a5,a5,-1764 # 3fcb391c <connected>
4200fca8:	0310000f          	fence	rw,w
4200fcac:	00e78023          	sb	a4,0(a5)
4200fcb0:	0330000f          	fence	rw,rw
4200fcb4:	3fcb47b7          	lui	a5,0x3fcb4
4200fcb8:	9007a623          	sw	zero,-1780(a5) # 3fcb390c <station_retries>
4200fcbc:	8082                	ret
4200fcbe:	3c1087b7          	lui	a5,0x3c108
4200fcc2:	0a07a783          	lw	a5,160(a5) # 3c1080a0 <WIFI_EVENT>
4200fcc6:	08b79f63          	bne	a5,a1,4200fd64 <wifi_event+0xea>
4200fcca:	4795                	li	a5,5
4200fccc:	08f61463          	bne	a2,a5,4200fd54 <wifi_event+0xda>
4200fcd0:	3fcb47b7          	lui	a5,0x3fcb4
4200fcd4:	91c78793          	addi	a5,a5,-1764 # 3fcb391c <connected>
4200fcd8:	0310000f          	fence	rw,w
4200fcdc:	00078023          	sb	zero,0(a5)
4200fce0:	0330000f          	fence	rw,rw
4200fce4:	3fcb46b7          	lui	a3,0x3fcb4
4200fce8:	9106c783          	lbu	a5,-1776(a3) # 3fcb3910 <station_configured>
4200fcec:	cfa5                	beqz	a5,4200fd64 <wifi_event+0xea>
4200fcee:	3fcb4737          	lui	a4,0x3fcb4
4200fcf2:	91a70793          	addi	a5,a4,-1766 # 3fcb391a <scanning>
4200fcf6:	0330000f          	fence	rw,rw
4200fcfa:	00078783          	lb	a5,0(a5)
4200fcfe:	0230000f          	fence	r,rw
4200fd02:	0ff7f793          	zext.b	a5,a5
4200fd06:	ef89                	bnez	a5,4200fd20 <wifi_event+0xa6>
4200fd08:	3fcb4637          	lui	a2,0x3fcb4
4200fd0c:	90c62783          	lw	a5,-1780(a2) # 3fcb390c <station_retries>
4200fd10:	458d                	li	a1,3
4200fd12:	00f5e763          	bltu	a1,a5,4200fd20 <wifi_event+0xa6>
4200fd16:	0785                	addi	a5,a5,1
4200fd18:	90f62623          	sw	a5,-1780(a2)
4200fd1c:	3062406f          	j	42034022 <esp_wifi_connect>
4200fd20:	9106c783          	lbu	a5,-1776(a3)
4200fd24:	c3a1                	beqz	a5,4200fd64 <wifi_event+0xea>
4200fd26:	91a70793          	addi	a5,a4,-1766
4200fd2a:	0330000f          	fence	rw,rw
4200fd2e:	00078783          	lb	a5,0(a5)
4200fd32:	0230000f          	fence	r,rw
4200fd36:	0ff7f793          	zext.b	a5,a5
4200fd3a:	e78d                	bnez	a5,4200fd64 <wifi_event+0xea>
4200fd3c:	3fcb47b7          	lui	a5,0x3fcb4
4200fd40:	4705                	li	a4,1
4200fd42:	91878793          	addi	a5,a5,-1768 # 3fcb3918 <station_failed>
4200fd46:	0310000f          	fence	rw,w
4200fd4a:	00e78023          	sb	a4,0(a5)
4200fd4e:	0330000f          	fence	rw,rw
4200fd52:	8082                	ret
4200fd54:	4789                	li	a5,2
4200fd56:	00f61763          	bne	a2,a5,4200fd64 <wifi_event+0xea>
4200fd5a:	3fcb47b7          	lui	a5,0x3fcb4
4200fd5e:	9107c783          	lbu	a5,-1776(a5) # 3fcb3910 <station_configured>
4200fd62:	ffcd                	bnez	a5,4200fd1c <wifi_event+0xa2>
4200fd64:	8082                	ret


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42010272 <network_address>:
42010272:	1101                	addi	sp,sp,-32
42010274:	ca26                	sw	s1,20(sp)
42010276:	ce06                	sw	ra,28(sp)
42010278:	cc22                	sw	s0,24(sp)
4201027a:	84aa                	mv	s1,a0
4201027c:	c62e                	sw	a1,12(sp)
4201027e:	3fcb47b7          	lui	a5,0x3fcb4
42010282:	91478793          	addi	a5,a5,-1772 # 3fcb3914 <last_station_address>
42010286:	0330000f          	fence	rw,rw
4201028a:	4380                	lw	s0,0(a5)
4201028c:	0230000f          	fence	r,rw
42010290:	fc9ff0ef          	jal	42010258 <network_ap_active>
42010294:	45b2                	lw	a1,12(sp)
42010296:	cc0d                	beqz	s0,420102d0 <network_address+0x5e>
42010298:	00154513          	xori	a0,a0,1
4201029c:	0ff57513          	zext.b	a0,a0
420102a0:	c905                	beqz	a0,420102d0 <network_address+0x5e>
420102a2:	01045793          	srli	a5,s0,0x10
420102a6:	00845713          	srli	a4,s0,0x8
420102aa:	01845813          	srli	a6,s0,0x18
420102ae:	0ff47693          	zext.b	a3,s0
420102b2:	4462                	lw	s0,24(sp)
420102b4:	40f2                	lw	ra,28(sp)
420102b6:	8526                	mv	a0,s1
420102b8:	44d2                	lw	s1,20(sp)
420102ba:	3c0b4637          	lui	a2,0x3c0b4
420102be:	0ff7f793          	zext.b	a5,a5
420102c2:	0ff77713          	zext.b	a4,a4
420102c6:	fa460613          	addi	a2,a2,-92 # 3c0b3fa4 <_esp_libc_clock_array_end+0x3e54>
420102ca:	6105                	addi	sp,sp,32
420102cc:	3c98d06f          	j	4209de94 <snprintf>
420102d0:	4462                	lw	s0,24(sp)
420102d2:	40f2                	lw	ra,28(sp)
420102d4:	8526                	mv	a0,s1
420102d6:	44d2                	lw	s1,20(sp)
420102d8:	3c0b4637          	lui	a2,0x3c0b4
420102dc:	b6860613          	addi	a2,a2,-1176 # 3c0b3b68 <_esp_libc_clock_array_end+0x3a18>
420102e0:	6105                	addi	sp,sp,32
420102e2:	3b38d06f          	j	4209de94 <snprintf>


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42010832 <time_sync_notify>:
42010832:	3fcb47b7          	lui	a5,0x3fcb4
42010836:	4705                	li	a4,1
42010838:	92878793          	addi	a5,a5,-1752 # 3fcb3928 <time_synced>
4201083c:	0310000f          	fence	rw,w
42010840:	00e78023          	sb	a4,0(a5)
42010844:	8082                	ret


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42011216 <weather_request_active>:
42011216:	3fcb47b7          	lui	a5,0x3fcb4
4201121a:	92c78793          	addi	a5,a5,-1748 # 3fcb392c <request_state>
4201121e:	0330000f          	fence	rw,rw
42011222:	4388                	lw	a0,0(a5)
42011224:	0230000f          	fence	r,rw
42011228:	00a03533          	snez	a0,a0
4201122c:	8082                	ret


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42010eb2 <weather_task>:
42010eb2:	8a010113          	addi	sp,sp,-1888
42010eb6:	04100613          	li	a2,65
42010eba:	4581                	li	a1,0
42010ebc:	1068                	addi	a0,sp,44
42010ebe:	74112e23          	sw	ra,1884(sp)
42010ec2:	74912a23          	sw	s1,1876(sp)
42010ec6:	75312623          	sw	s3,1868(sp)
42010eca:	75412423          	sw	s4,1864(sp)
42010ece:	74812c23          	sw	s0,1880(sp)
42010ed2:	75212823          	sw	s2,1872(sp)
42010ed6:	75512223          	sw	s5,1860(sp)
42010eda:	fdfef097          	auipc	ra,0xfdfef
42010ede:	5ae080e7          	jalr	1454(ra) # 40000488 <memset>
42010ee2:	04100613          	li	a2,65
42010ee6:	4581                	li	a1,0
42010ee8:	1888                	addi	a0,sp,112
42010eea:	cc02                	sw	zero,24(sp)
42010eec:	ce02                	sw	zero,28(sp)
42010eee:	d002                	sw	zero,32(sp)
42010ef0:	d202                	sw	zero,36(sp)
42010ef2:	d402                	sw	zero,40(sp)
42010ef4:	fdfef097          	auipc	ra,0xfdfef
42010ef8:	594080e7          	jalr	1428(ra) # 40000488 <memset>
42010efc:	3fcb47b7          	lui	a5,0x3fcb4
42010f00:	3fcb04b7          	lui	s1,0x3fcb0
42010f04:	4985                	li	s3,1
42010f06:	92c78a13          	addi	s4,a5,-1748 # 3fcb392c <request_state>
42010f0a:	aa048493          	addi	s1,s1,-1376 # 3fcafaa0 <cached_weather>
42010f0e:	567d                	li	a2,-1
42010f10:	4585                	li	a1,1
42010f12:	4501                	li	a0,0
42010f14:	7489c0ef          	jal	420ad65c <ulTaskGenericNotifyTake>
42010f18:	4615                	li	a2,5
42010f1a:	4585                	li	a1,1
42010f1c:	8552                	mv	a0,s4
42010f1e:	fe376097          	auipc	ra,0xfe376
42010f22:	668080e7          	jalr	1640(ra) # 40387586 <__atomic_fetch_or_4>
42010f26:	55f5                	li	a1,-3
42010f28:	4615                	li	a2,5
42010f2a:	8552                	mv	a0,s4
42010f2c:	fe376097          	auipc	ra,0xfe376
42010f30:	632080e7          	jalr	1586(ra) # 4038755e <__atomic_fetch_and_4>
42010f34:	0fc8                	addi	a0,sp,980
42010f36:	d5afb0ef          	jal	4200c490 <settings_snapshot>
42010f3a:	43a10593          	addi	a1,sp,1082
42010f3e:	1068                	addi	a0,sp,44
42010f40:	fe376097          	auipc	ra,0xfe376
42010f44:	712080e7          	jalr	1810(ra) # 40387652 <strcmp>
42010f48:	e10d                	bnez	a0,42010f6a <weather_task+0xb8>
42010f4a:	47b10593          	addi	a1,sp,1147
42010f4e:	0828                	addi	a0,sp,24
42010f50:	fe376097          	auipc	ra,0xfe376
42010f54:	702080e7          	jalr	1794(ra) # 40387652 <strcmp>
42010f58:	e909                	bnez	a0,42010f6a <weather_task+0xb8>
42010f5a:	4d010593          	addi	a1,sp,1232
42010f5e:	1888                	addi	a0,sp,112
42010f60:	fe376097          	auipc	ra,0xfe376
42010f64:	6f2080e7          	jalr	1778(ra) # 40387652 <strcmp>
42010f68:	c939                	beqz	a0,42010fbe <weather_task+0x10c>
42010f6a:	43a10593          	addi	a1,sp,1082
42010f6e:	1068                	addi	a0,sp,44
42010f70:	fe376097          	auipc	ra,0xfe376
42010f74:	7f8080e7          	jalr	2040(ra) # 40387768 <strcpy>
42010f78:	47b10593          	addi	a1,sp,1147
42010f7c:	0828                	addi	a0,sp,24
42010f7e:	fe376097          	auipc	ra,0xfe376
42010f82:	7ea080e7          	jalr	2026(ra) # 40387768 <strcpy>
42010f86:	4d010593          	addi	a1,sp,1232
42010f8a:	1888                	addi	a0,sp,112
42010f8c:	fe376097          	auipc	ra,0xfe376
42010f90:	7dc080e7          	jalr	2012(ra) # 40387768 <strcpy>
42010f94:	3fcb4437          	lui	s0,0x3fcb4
42010f98:	93442503          	lw	a0,-1740(s0) # 3fcb3934 <weather_mutex>
42010f9c:	55fd                	li	a1,-1
42010f9e:	55e9b0ef          	jal	420ac4fc <xQueueSemaphoreTake>
42010fa2:	0f04a783          	lw	a5,240(s1)
42010fa6:	93442503          	lw	a0,-1740(s0)
42010faa:	4681                	li	a3,0
42010fac:	0785                	addi	a5,a5,1
42010fae:	4601                	li	a2,0
42010fb0:	4581                	li	a1,0
42010fb2:	00048023          	sb	zero,0(s1)
42010fb6:	0ef4a823          	sw	a5,240(s1)
42010fba:	1229b0ef          	jal	420ac0dc <xQueueGenericSend>
42010fbe:	a80ff0ef          	jal	4201023e <network_connected>
42010fc2:	14050e63          	beqz	a0,4201111e <weather_task+0x26c>
42010fc6:	4d014783          	lbu	a5,1232(sp)
42010fca:	14078a63          	beqz	a5,4201111e <weather_task+0x26c>
42010fce:	0a8c                	addi	a1,sp,336
42010fd0:	43a10513          	addi	a0,sp,1082
42010fd4:	e65ff0ef          	jal	42010e38 <url_escape>
42010fd8:	0c4c                	addi	a1,sp,532
42010fda:	4d010513          	addi	a0,sp,1232
42010fde:	e5bff0ef          	jal	42010e38 <url_escape>
42010fe2:	54010913          	addi	s2,sp,1344
42010fe6:	3c0b4637          	lui	a2,0x3c0b4
42010fea:	0c5c                	addi	a5,sp,532
42010fec:	47b10713          	addi	a4,sp,1147
42010ff0:	0a94                	addi	a3,sp,336
42010ff2:	2bc60613          	addi	a2,a2,700 # 3c0b42bc <_esp_libc_clock_array_end+0x416c>
42010ff6:	20000593          	li	a1,512
42010ffa:	854a                	mv	a0,s2
42010ffc:	6998c0ef          	jal	4209de94 <snprintf>
42011000:	6589                	lui	a1,0x2
42011002:	4781                	li	a5,0
42011004:	4801                	li	a6,0
42011006:	0585                	addi	a1,a1,1 # 2001 <CSR_UINTSTATUS+0x1350>
42011008:	4505                	li	a0,1
4201100a:	c83e                	sw	a5,16(sp)
4201100c:	ca42                	sw	a6,20(sp)
4201100e:	fe376097          	auipc	ra,0xfe376
42011012:	1b8080e7          	jalr	440(ra) # 403871c6 <calloc>
42011016:	c62a                	sw	a0,12(sp)
42011018:	10050363          	beqz	a0,4201111e <weather_task+0x26c>
4201101c:	09800613          	li	a2,152
42011020:	4581                	li	a1,0
42011022:	1928                	addi	a0,sp,184
42011024:	fdfef097          	auipc	ra,0xfdfef
42011028:	464080e7          	jalr	1124(ra) # 40000488 <memset>
4201102c:	6789                	lui	a5,0x2
4201102e:	71078793          	addi	a5,a5,1808 # 2710 <CSR_UINTSTATUS+0x1a5f>
42011032:	10f12223          	sw	a5,260(sp)
42011036:	420117b7          	lui	a5,0x42011
4201103a:	13278793          	addi	a5,a5,306 # 42011132 <weather_http_event>
4201103e:	10f12a23          	sw	a5,276(sp)
42011042:	40000793          	li	a5,1024
42011046:	10f12e23          	sw	a5,284(sp)
4201104a:	12f12023          	sw	a5,288(sp)
4201104e:	1948                	addi	a0,sp,180
42011050:	007c                	addi	a5,sp,12
42011052:	db4a                	sw	s2,180(sp)
42011054:	11310423          	sb	s3,264(sp)
42011058:	12f12223          	sw	a5,292(sp)
4201105c:	6b4240ef          	jal	42035710 <esp_http_client_init>
42011060:	8aaa                	mv	s5,a0
42011062:	10100413          	li	s0,257
42011066:	c915                	beqz	a0,4201109a <weather_task+0x1e8>
42011068:	194250ef          	jal	420361fc <esp_http_client_perform>
4201106c:	842a                	mv	s0,a0
4201106e:	8556                	mv	a0,s5
42011070:	0c4250ef          	jal	42036134 <esp_http_client_get_status_code>
42011074:	0c800793          	li	a5,200
42011078:	0af51b63          	bne	a0,a5,4201112e <weather_task+0x27c>
4201107c:	01414783          	lbu	a5,20(sp)
42011080:	e7dd                	bnez	a5,4201112e <weather_task+0x27c>
42011082:	8556                	mv	a0,s5
42011084:	314240ef          	jal	42035398 <esp_http_client_cleanup>
42011088:	e809                	bnez	s0,4201109a <weather_task+0x1e8>
4201108a:	45c2                	lw	a1,16(sp)
4201108c:	4532                	lw	a0,12(sp)
4201108e:	0db4                	addi	a3,sp,728
42011090:	0fd0                	addi	a2,sp,980
42011092:	24dd                	jal	42011378 <weather_parse_response>
42011094:	e119                	bnez	a0,4201109a <weather_task+0x1e8>
42011096:	10800413          	li	s0,264
4201109a:	4532                	lw	a0,12(sp)
4201109c:	fe376097          	auipc	ra,0xfe376
420110a0:	126080e7          	jalr	294(ra) # 403871c2 <cfree>
420110a4:	ec2d                	bnez	s0,4201111e <weather_task+0x26c>
420110a6:	854a                	mv	a0,s2
420110a8:	be8fb0ef          	jal	4200c490 <settings_snapshot>
420110ac:	43a10593          	addi	a1,sp,1082
420110b0:	5a610513          	addi	a0,sp,1446
420110b4:	fe376097          	auipc	ra,0xfe376
420110b8:	59e080e7          	jalr	1438(ra) # 40387652 <strcmp>
420110bc:	e12d                	bnez	a0,4201111e <weather_task+0x26c>
420110be:	47b10593          	addi	a1,sp,1147
420110c2:	5e710513          	addi	a0,sp,1511
420110c6:	fe376097          	auipc	ra,0xfe376
420110ca:	58c080e7          	jalr	1420(ra) # 40387652 <strcmp>
420110ce:	e921                	bnez	a0,4201111e <weather_task+0x26c>
420110d0:	4d010593          	addi	a1,sp,1232
420110d4:	63c10513          	addi	a0,sp,1596
420110d8:	fe376097          	auipc	ra,0xfe376
420110dc:	57a080e7          	jalr	1402(ra) # 40387652 <strcmp>
420110e0:	ed1d                	bnez	a0,4201111e <weather_task+0x26c>
420110e2:	3fcb4437          	lui	s0,0x3fcb4
420110e6:	93442503          	lw	a0,-1740(s0) # 3fcb3934 <weather_mutex>
420110ea:	55fd                	li	a1,-1
420110ec:	4109b0ef          	jal	420ac4fc <xQueueSemaphoreTake>
420110f0:	3fcb0537          	lui	a0,0x3fcb0
420110f4:	aa050513          	addi	a0,a0,-1376 # 3fcafaa0 <cached_weather>
420110f8:	0f052783          	lw	a5,240(a0)
420110fc:	0f800613          	li	a2,248
42011100:	0dac                	addi	a1,sp,728
42011102:	0785                	addi	a5,a5,1
42011104:	3cf12423          	sw	a5,968(sp)
42011108:	fe376097          	auipc	ra,0xfe376
4201110c:	132080e7          	jalr	306(ra) # 4038723a <memcpy>
42011110:	93442503          	lw	a0,-1740(s0)
42011114:	4681                	li	a3,0
42011116:	4601                	li	a2,0
42011118:	4581                	li	a1,0
4201111a:	7c39a0ef          	jal	420ac0dc <xQueueGenericSend>
4201111e:	4615                	li	a2,5
42011120:	55f9                	li	a1,-2
42011122:	8552                	mv	a0,s4
42011124:	fe376097          	auipc	ra,0xfe376
42011128:	43a080e7          	jalr	1082(ra) # 4038755e <__atomic_fetch_and_4>
4201112c:	b3cd                	j	42010f0e <weather_task+0x5c>
4201112e:	547d                	li	s0,-1
42011130:	bf89                	j	42011082 <weather_task+0x1d0>
