
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

Disassembly of section .flash.text:

42010832 <time_sync_notify>:
42010832:	3fcb47b7          	lui	a5,0x3fcb4
42010836:	4705                	li	a4,1
42010838:	92878793          	addi	a5,a5,-1752 # 3fcb3928 <time_synced>
4201083c:	0310000f          	fence	rw,w
42010840:	00e78023          	sb	a4,0(a5)
42010844:	8082                	ret
