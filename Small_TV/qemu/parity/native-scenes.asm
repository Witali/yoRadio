
small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200d28e <clock_task>:
4200d28e:	c5010113          	addi	sp,sp,-944
4200d292:	39812423          	sw	s8,904(sp)
4200d296:	0ff00793          	li	a5,255
4200d29a:	3fcafc37          	lui	s8,0x3fcaf
4200d29e:	3a912223          	sw	s1,932(sp)
4200d2a2:	39412c23          	sw	s4,920(sp)
4200d2a6:	39612823          	sw	s6,912(sp)
4200d2aa:	39712623          	sw	s7,908(sp)
4200d2ae:	39912223          	sw	s9,900(sp)
4200d2b2:	39a12023          	sw	s10,896(sp)
4200d2b6:	37b12e23          	sw	s11,892(sp)
4200d2ba:	3a112623          	sw	ra,940(sp)
4200d2be:	3a812423          	sw	s0,936(sp)
4200d2c2:	3b212023          	sw	s2,928(sp)
4200d2c6:	39312e23          	sw	s3,924(sp)
4200d2ca:	39512a23          	sw	s5,916(sp)
4200d2ce:	04010223          	sb	zero,68(sp)
4200d2d2:	04011423          	sh	zero,72(sp)
4200d2d6:	4b81                	li	s7,0
4200d2d8:	d202                	sw	zero,36(sp)
4200d2da:	4d01                	li	s10,0
4200d2dc:	d002                	sw	zero,32(sp)
4200d2de:	ce3e                	sw	a5,28(sp)
4200d2e0:	cc02                	sw	zero,24(sp)
4200d2e2:	4481                	li	s1,0
4200d2e4:	d402                	sw	zero,40(sp)
4200d2e6:	4c81                	li	s9,0
4200d2e8:	4a01                	li	s4,0
4200d2ea:	ca02                	sw	zero,20(sp)
4200d2ec:	4b01                	li	s6,0
4200d2ee:	4d85                	li	s11,1
4200d2f0:	73cc0c13          	addi	s8,s8,1852 # 3fcaf73c <timer_state>
4200d2f4:	0448                	addi	a0,sp,516
4200d2f6:	99aff0ef          	jal	4200c490 <settings_snapshot>
4200d2fa:	0228                	addi	a0,sp,264
4200d2fc:	62b030ef          	jal	42011126 <weather_snapshot>
4200d300:	35114603          	lbu	a2,849(sp)
4200d304:	4581                	li	a1,0
4200d306:	00e8                	addi	a0,sp,76
4200d308:	f27ff0ef          	jal	4200d22e <timer_snapshot>
4200d30c:	05a14903          	lbu	s2,90(sp)
4200d310:	6db020ef          	jal	420101ea <network_connected>
4200d314:	45d1                	li	a1,20
4200d316:	89aa                	mv	s3,a0
4200d318:	1168                	addi	a0,sp,172
4200d31a:	705020ef          	jal	4201021e <network_address>
4200d31e:	4501                	li	a0,0
4200d320:	71b8f0ef          	jal	4209d23a <time>
4200d324:	c82e                	sw	a1,16(sp)
4200d326:	4642                	lw	a2,16(sp)
4200d328:	c62a                	sw	a0,12(sp)
4200d32a:	85aa                	mv	a1,a0
4200d32c:	11d4                	addi	a3,sp,228
4200d32e:	2ab10513          	addi	a0,sp,683
4200d332:	4c0030ef          	jal	420107f2 <services_local_time>
4200d336:	8aaa                	mv	s5,a0
4200d338:	e51d                	bnez	a0,4200d366 <clock_task+0xd8>
4200d33a:	4781                	li	a5,0
4200d33c:	10f12023          	sw	a5,256(sp)
4200d340:	02800793          	li	a5,40
4200d344:	d3be                	sw	a5,228(sp)
4200d346:	4791                	li	a5,4
4200d348:	d5be                	sw	a5,232(sp)
4200d34a:	47c5                	li	a5,17
4200d34c:	d7be                	sw	a5,236(sp)
4200d34e:	47cd                	li	a5,19
4200d350:	d9be                	sw	a5,240(sp)
4200d352:	47a1                	li	a5,8
4200d354:	dbbe                	sw	a5,244(sp)
4200d356:	07d00793          	li	a5,125
4200d35a:	4801                	li	a6,0
4200d35c:	ddbe                	sw	a5,248(sp)
4200d35e:	4795                	li	a5,5
4200d360:	11012223          	sw	a6,260(sp)
4200d364:	dfbe                	sw	a5,252(sp)
4200d366:	02400613          	li	a2,36
4200d36a:	11cc                	addi	a1,sp,228
4200d36c:	0188                	addi	a0,sp,192
4200d36e:	fe37a097          	auipc	ra,0xfe37a
4200d372:	ecc080e7          	jalr	-308(ra) # 4038723a <memcpy>
4200d376:	a7eff0ef          	jal	4200c5f4 <settings_generation>
4200d37a:	d62a                	sw	a0,44(sp)
4200d37c:	4405                	li	s0,1
4200d37e:	00ab1e63          	bne	s6,a0,4200d39a <clock_task+0x10c>
4200d382:	47d2                	lw	a5,20(sp)
4200d384:	1f812403          	lw	s0,504(sp)
4200d388:	8c1d                	sub	s0,s0,a5
4200d38a:	5792                	lw	a5,36(sp)
4200d38c:	00803433          	snez	s0,s0
4200d390:	0157c7b3          	xor	a5,a5,s5
4200d394:	8c5d                	or	s0,s0,a5
4200d396:	0ff47413          	zext.b	s0,s0
4200d39a:	00098d63          	beqz	s3,4200d3b4 <clock_task+0x126>
4200d39e:	10814783          	lbu	a5,264(sp)
4200d3a2:	eb89                	bnez	a5,4200d3b4 <clock_task+0x126>
4200d3a4:	609030ef          	jal	420111ac <weather_request_active>
4200d3a8:	e511                	bnez	a0,4200d3b4 <clock_task+0x126>
4200d3aa:	000b9c63          	bnez	s7,4200d3c2 <clock_task+0x134>
4200d3ae:	5bd030ef          	jal	4201116a <weather_request_update>
4200d3b2:	4bf9                	li	s7,30
4200d3b4:	030020ef          	jal	4200f3e4 <media_upload_active>
4200d3b8:	c519                	beqz	a0,4200d3c6 <clock_task+0x138>
4200d3ba:	4529                	li	a0,10
4200d3bc:	2c99f0ef          	jal	420ace84 <vTaskDelay>
4200d3c0:	bf15                	j	4200d2f4 <clock_task+0x66>
4200d3c2:	1bfd                	addi	s7,s7,-1
4200d3c4:	bfc5                	j	4200d3b4 <clock_task+0x126>
4200d3c6:	02091263          	bnez	s2,4200d3ea <clock_task+0x15c>
4200d3ca:	5e3030ef          	jal	420111ac <weather_request_active>
4200d3ce:	892a                	mv	s2,a0
4200d3d0:	f56d                	bnez	a0,4200d3ba <clock_task+0x12c>
4200d3d2:	06099f63          	bnez	s3,4200d450 <clock_task+0x1c2>
4200d3d6:	62f020ef          	jal	42010204 <network_ap_active>
4200d3da:	c131                	beqz	a0,4200d41e <clock_task+0x190>
4200d3dc:	4409                	li	s0,2
4200d3de:	04848063          	beq	s1,s0,4200d41e <clock_task+0x190>
4200d3e2:	609000ef          	jal	4200e1ea <factory_draw_setup>
4200d3e6:	84a2                	mv	s1,s0
4200d3e8:	a81d                	j	4200d41e <clock_task+0x190>
4200d3ea:	05914403          	lbu	s0,89(sp)
4200d3ee:	47e2                	lw	a5,24(sp)
4200d3f0:	14fd                	addi	s1,s1,-1
4200d3f2:	009034b3          	snez	s1,s1
4200d3f6:	8f81                	sub	a5,a5,s0
4200d3f8:	00f037b3          	snez	a5,a5
4200d3fc:	8cdd                	or	s1,s1,a5
4200d3fe:	ec9d                	bnez	s1,4200d43c <clock_task+0x1ae>
4200d400:	5782                	lw	a5,32(sp)
4200d402:	0137c7b3          	xor	a5,a5,s3
4200d406:	0ff7f793          	zext.b	a5,a5
4200d40a:	eb8d                	bnez	a5,4200d43c <clock_task+0x1ae>
4200d40c:	35114603          	lbu	a2,849(sp)
4200d410:	08000593          	li	a1,128
4200d414:	1808                	addi	a0,sp,48
4200d416:	e19ff0ef          	jal	4200d22e <timer_snapshot>
4200d41a:	4485                	li	s1,1
4200d41c:	cc22                	sw	s0,24(sp)
4200d41e:	1f812783          	lw	a5,504(sp)
4200d422:	4529                	li	a0,10
4200d424:	10814d03          	lbu	s10,264(sp)
4200d428:	ca3e                	sw	a5,20(sp)
4200d42a:	25b9f0ef          	jal	420ace84 <vTaskDelay>
4200d42e:	47b2                	lw	a5,12(sp)
4200d430:	4cc2                	lw	s9,16(sp)
4200d432:	5b32                	lw	s6,44(sp)
4200d434:	d256                	sw	s5,36(sp)
4200d436:	d04e                	sw	s3,32(sp)
4200d438:	d43e                	sw	a5,40(sp)
4200d43a:	bd6d                	j	4200d2f4 <clock_task+0x66>
4200d43c:	01303533          	snez	a0,s3
4200d440:	117c                	addi	a5,sp,172
4200d442:	40a00533          	neg	a0,a0
4200d446:	85a2                	mv	a1,s0
4200d448:	8d7d                	and	a0,a0,a5
4200d44a:	637000ef          	jal	4200e280 <factory_draw_startup>
4200d44e:	bf7d                	j	4200d40c <clock_task+0x17e>
4200d450:	478d                	li	a5,3
4200d452:	00f49763          	bne	s1,a5,4200d460 <clock_task+0x1d2>
4200d456:	34c14783          	lbu	a5,844(sp)
4200d45a:	4772                	lw	a4,28(sp)
4200d45c:	04e78b63          	beq	a5,a4,4200d4b2 <clock_task+0x224>
4200d460:	0f000693          	li	a3,240
4200d464:	4701                	li	a4,0
4200d466:	8636                	mv	a2,a3
4200d468:	4581                	li	a1,0
4200d46a:	4501                	li	a0,0
4200d46c:	f88ff0ef          	jal	4200cbf4 <display_fill>
4200d470:	34c14703          	lbu	a4,844(sp)
4200d474:	4789                	li	a5,2
4200d476:	442d                	li	s0,11
4200d478:	00f71363          	bne	a4,a5,4200d47e <clock_task+0x1f0>
4200d47c:	443d                	li	s0,15
4200d47e:	fe37b097          	auipc	ra,0xfe37b
4200d482:	9b8080e7          	jalr	-1608(ra) # 40387e36 <vPortEnterCritical>
4200d486:	004c2783          	lw	a5,4(s8)
4200d48a:	8fc1                	or	a5,a5,s0
4200d48c:	00fc2223          	sw	a5,4(s8)
4200d490:	fe37b097          	auipc	ra,0xfe37b
4200d494:	9d2080e7          	jalr	-1582(ra) # 40387e62 <vPortExitCritical>
4200d498:	34c14783          	lbu	a5,844(sp)
4200d49c:	00fde863          	bltu	s11,a5,4200d4ac <clock_task+0x21e>
4200d4a0:	461e                	lw	a2,196(sp)
4200d4a2:	45ae                	lw	a1,200(sp)
4200d4a4:	86d6                	mv	a3,s5
4200d4a6:	0448                	addi	a0,sp,516
4200d4a8:	d39ff0ef          	jal	4200d1e0 <backlight_update>
4200d4ac:	894e                	mv	s2,s3
4200d4ae:	844e                	mv	s0,s3
4200d4b0:	4a01                	li	s4,0
4200d4b2:	10814783          	lbu	a5,264(sp)
4200d4b6:	c399                	beqz	a5,4200d4bc <clock_task+0x22e>
4200d4b8:	000d1363          	bnez	s10,4200d4be <clock_task+0x230>
4200d4bc:	4a01                	li	s4,0
4200d4be:	34c14783          	lbu	a5,844(sp)
4200d4c2:	eb99                	bnez	a5,4200d4d8 <clock_task+0x24a>
4200d4c4:	0a090363          	beqz	s2,4200d56a <clock_task+0x2dc>
4200d4c8:	35114603          	lbu	a2,849(sp)
4200d4cc:	4589                	li	a1,2
4200d4ce:	08e8                	addi	a0,sp,92
4200d4d0:	d5fff0ef          	jal	4200d22e <timer_snapshot>
4200d4d4:	5786                	lw	a5,96(sp)
4200d4d6:	efd1                	bnez	a5,4200d572 <clock_task+0x2e4>
4200d4d8:	34c14783          	lbu	a5,844(sp)
4200d4dc:	e7f9                	bnez	a5,4200d5aa <clock_task+0x31c>
4200d4de:	34d14503          	lbu	a0,845(sp)
4200d4e2:	040020ef          	jal	4200f522 <media_animation_frames>
4200d4e6:	85aa                	mv	a1,a0
4200d4e8:	00c8                	addi	a0,sp,68
4200d4ea:	2e61                	jal	4200d882 <factory_animation_next>
4200d4ec:	35114603          	lbu	a2,849(sp)
4200d4f0:	84aa                	mv	s1,a0
4200d4f2:	45a1                	li	a1,8
4200d4f4:	10e8                	addi	a0,sp,108
4200d4f6:	d39ff0ef          	jal	4200d22e <timer_snapshot>
4200d4fa:	4732                	lw	a4,12(sp)
4200d4fc:	57a2                	lw	a5,40(sp)
4200d4fe:	5846                	lw	a6,112(sp)
4200d500:	8fb9                	xor	a5,a5,a4
4200d502:	4742                	lw	a4,16(sp)
4200d504:	01003833          	snez	a6,a6
4200d508:	00ecc733          	xor	a4,s9,a4
4200d50c:	8fd9                	or	a5,a5,a4
4200d50e:	00f037b3          	snez	a5,a5
4200d512:	00f867b3          	or	a5,a6,a5
4200d516:	e391                	bnez	a5,4200d51a <clock_task+0x28c>
4200d518:	cc35                	beqz	s0,4200d594 <clock_task+0x306>
4200d51a:	fff4c713          	not	a4,s1
4200d51e:	877d                	srai	a4,a4,0x1f
4200d520:	87ca                	mv	a5,s2
4200d522:	8f65                	and	a4,a4,s1
4200d524:	86d2                	mv	a3,s4
4200d526:	0230                	addi	a2,sp,264
4200d528:	018c                	addi	a1,sp,192
4200d52a:	0448                	addi	a0,sp,516
4200d52c:	61d000ef          	jal	4200e348 <factory_draw_classic>
4200d530:	41d000ef          	jal	4200e14c <factory_scroll_tick>
4200d534:	34c14703          	lbu	a4,844(sp)
4200d538:	4789                	li	a5,2
4200d53a:	00f70863          	beq	a4,a5,4200d54a <clock_task+0x2bc>
4200d53e:	461e                	lw	a2,196(sp)
4200d540:	45ae                	lw	a1,200(sp)
4200d542:	86d6                	mv	a3,s5
4200d544:	0448                	addi	a0,sp,516
4200d546:	c9bff0ef          	jal	4200d1e0 <backlight_update>
4200d54a:	34c14783          	lbu	a5,844(sp)
4200d54e:	35114603          	lbu	a2,849(sp)
4200d552:	04000593          	li	a1,64
4200d556:	0968                	addi	a0,sp,156
4200d558:	ce3e                	sw	a5,28(sp)
4200d55a:	cd5ff0ef          	jal	4200d22e <timer_snapshot>
4200d55e:	578a                	lw	a5,160(sp)
4200d560:	c399                	beqz	a5,4200d566 <clock_task+0x2d8>
4200d562:	409030ef          	jal	4201116a <weather_request_update>
4200d566:	448d                	li	s1,3
4200d568:	bd5d                	j	4200d41e <clock_task+0x190>
4200d56a:	45f000ef          	jal	4200e1c8 <factory_scroll_description_ready>
4200d56e:	fd29                	bnez	a0,4200d4c8 <clock_task+0x23a>
4200d570:	b7a5                	j	4200d4d8 <clock_task+0x24a>
4200d572:	00091b63          	bnez	s2,4200d588 <clock_task+0x2fa>
4200d576:	10814783          	lbu	a5,264(sp)
4200d57a:	c799                	beqz	a5,4200d588 <clock_task+0x2fa>
4200d57c:	000d0663          	beqz	s10,4200d588 <clock_task+0x2fa>
4200d580:	0a05                	addi	s4,s4,1
4200d582:	47a9                	li	a5,10
4200d584:	02fa7a33          	remu	s4,s4,a5
4200d588:	f821                	bnez	s0,4200d4d8 <clock_task+0x24a>
4200d58a:	34c14403          	lbu	s0,844(sp)
4200d58e:	00143413          	seqz	s0,s0
4200d592:	b799                	j	4200d4d8 <clock_task+0x24a>
4200d594:	f804cee3          	bltz	s1,4200d530 <clock_task+0x2a2>
4200d598:	34d14503          	lbu	a0,845(sp)
4200d59c:	0a000693          	li	a3,160
4200d5a0:	8636                	mv	a2,a3
4200d5a2:	85a6                	mv	a1,s1
4200d5a4:	7d9010ef          	jal	4200f57c <media_draw_animation>
4200d5a8:	b761                	j	4200d530 <clock_task+0x2a2>
4200d5aa:	03b79463          	bne	a5,s11,4200d5d2 <clock_task+0x344>
4200d5ae:	35114603          	lbu	a2,849(sp)
4200d5b2:	18e8                	addi	a0,sp,124
4200d5b4:	45a5                	li	a1,9
4200d5b6:	c79ff0ef          	jal	4200d22e <timer_snapshot>
4200d5ba:	470a                	lw	a4,128(sp)
4200d5bc:	86ca                	mv	a3,s2
4200d5be:	1170                	addi	a2,sp,172
4200d5c0:	00375793          	srli	a5,a4,0x3
4200d5c4:	8b85                	andi	a5,a5,1
4200d5c6:	8b05                	andi	a4,a4,1
4200d5c8:	018c                	addi	a1,sp,192
4200d5ca:	0448                	addi	a0,sp,516
4200d5cc:	386010ef          	jal	4200e952 <factory_draw_simple>
4200d5d0:	b795                	j	4200d534 <clock_task+0x2a6>
4200d5d2:	4709                	li	a4,2
4200d5d4:	0ae79263          	bne	a5,a4,4200d678 <clock_task+0x3ea>
4200d5d8:	0458                	addi	a4,sp,516
4200d5da:	4781                	li	a5,0
4200d5dc:	4601                	li	a2,0
4200d5de:	4695                	li	a3,5
4200d5e0:	15872583          	lw	a1,344(a4)
4200d5e4:	c581                	beqz	a1,4200d5ec <clock_task+0x35e>
4200d5e6:	00fd95b3          	sll	a1,s11,a5
4200d5ea:	8e4d                	or	a2,a2,a1
4200d5ec:	0785                	addi	a5,a5,1
4200d5ee:	0711                	addi	a4,a4,4
4200d5f0:	fed798e3          	bne	a5,a3,4200d5e0 <clock_task+0x352>
4200d5f4:	46c6                	lw	a3,80(sp)
4200d5f6:	35814583          	lbu	a1,856(sp)
4200d5fa:	11dc                	addi	a5,sp,228
4200d5fc:	8289                	srli	a3,a3,0x2
4200d5fe:	8a85                	andi	a3,a3,1
4200d600:	00d966b3          	or	a3,s2,a3
4200d604:	4701                	li	a4,0
4200d606:	0ff6f693          	zext.b	a3,a3
4200d60a:	00a8                	addi	a0,sp,72
4200d60c:	2ad1                	jal	4200d7e0 <factory_photo_step>
4200d60e:	0e714783          	lbu	a5,231(sp)
4200d612:	c789                	beqz	a5,4200d61c <clock_task+0x38e>
4200d614:	0e415503          	lhu	a0,228(sp)
4200d618:	af7ff0ef          	jal	4200d10e <backlight_set_level>
4200d61c:	0e610503          	lb	a0,230(sp)
4200d620:	57fd                	li	a5,-1
4200d622:	02f54663          	blt	a0,a5,4200d64e <clock_task+0x3c0>
4200d626:	04f51563          	bne	a0,a5,4200d670 <clock_task+0x3e2>
4200d62a:	0f000693          	li	a3,240
4200d62e:	8636                	mv	a2,a3
4200d630:	4701                	li	a4,0
4200d632:	4581                	li	a1,0
4200d634:	4501                	li	a0,0
4200d636:	dbeff0ef          	jal	4200cbf4 <display_fill>
4200d63a:	6741                	lui	a4,0x10
4200d63c:	4805                	li	a6,1
4200d63e:	4781                	li	a5,0
4200d640:	177d                	addi	a4,a4,-1 # ffff <CSR_UINTSTATUS+0xf34e>
4200d642:	46c1                	li	a3,16
4200d644:	1170                	addi	a2,sp,172
4200d646:	0e100593          	li	a1,225
4200d64a:	4515                	li	a0,5
4200d64c:	2b69                	jal	4200dbe6 <display_factory_text>
4200d64e:	0e814783          	lbu	a5,232(sp)
4200d652:	ee0781e3          	beqz	a5,4200d534 <clock_task+0x2a6>
4200d656:	35114603          	lbu	a2,849(sp)
4200d65a:	1808                	addi	a0,sp,48
4200d65c:	4591                	li	a1,4
4200d65e:	bd1ff0ef          	jal	4200d22e <timer_snapshot>
4200d662:	461e                	lw	a2,196(sp)
4200d664:	45ae                	lw	a1,200(sp)
4200d666:	86d6                	mv	a3,s5
4200d668:	0448                	addi	a0,sp,516
4200d66a:	b77ff0ef          	jal	4200d1e0 <backlight_update>
4200d66e:	b5d9                	j	4200d534 <clock_task+0x2a6>
4200d670:	116c                	addi	a1,sp,172
4200d672:	1fb010ef          	jal	4200f06c <factory_draw_photo>
4200d676:	bfe1                	j	4200d64e <clock_task+0x3c0>
4200d678:	35114603          	lbu	a2,849(sp)
4200d67c:	4585                	li	a1,1
4200d67e:	0168                	addi	a0,sp,140
4200d680:	bafff0ef          	jal	4200d22e <timer_snapshot>
4200d684:	47ca                	lw	a5,144(sp)
4200d686:	00f037b3          	snez	a5,a5
4200d68a:	00f967b3          	or	a5,s2,a5
4200d68e:	0ff7f793          	zext.b	a5,a5
4200d692:	e399                	bnez	a5,4200d698 <clock_task+0x40a>
4200d694:	ea0400e3          	beqz	s0,4200d534 <clock_task+0x2a6>
4200d698:	864a                	mv	a2,s2
4200d69a:	116c                	addi	a1,sp,172
4200d69c:	0188                	addi	a0,sp,192
4200d69e:	4d6010ef          	jal	4200eb74 <factory_draw_dial>
4200d6a2:	bd49                	j	4200d534 <clock_task+0x2a6>


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200e348 <factory_draw_classic>:
4200e348:	716d                	addi	sp,sp,-272
4200e34a:	10812423          	sw	s0,264(sp)
4200e34e:	10912223          	sw	s1,260(sp)
4200e352:	11212023          	sw	s2,256(sp)
4200e356:	ddd2                	sw	s4,248(sp)
4200e358:	dbd6                	sw	s5,244(sp)
4200e35a:	d3e6                	sw	s9,228(sp)
4200e35c:	d1ea                	sw	s10,224(sp)
4200e35e:	cfee                	sw	s11,220(sp)
4200e360:	3fcafa37          	lui	s4,0x3fcaf
4200e364:	10112623          	sw	ra,268(sp)
4200e368:	dfce                	sw	s3,252(sp)
4200e36a:	d9da                	sw	s6,240(sp)
4200e36c:	d7de                	sw	s7,236(sp)
4200e36e:	d5e2                	sw	s8,232(sp)
4200e370:	84aa                	mv	s1,a0
4200e372:	892e                	mv	s2,a1
4200e374:	8432                	mv	s0,a2
4200e376:	8d36                	mv	s10,a3
4200e378:	8dba                	mv	s11,a4
4200e37a:	8abe                	mv	s5,a5
4200e37c:	3fcafcb7          	lui	s9,0x3fcaf
4200e380:	7c0a0a13          	addi	s4,s4,1984 # 3fcaf7c0 <previous_time.7>
4200e384:	42079263          	bnez	a5,4200e7a8 <factory_draw_classic+0x460>
4200e388:	16c00613          	li	a2,364
4200e38c:	7e4c8593          	addi	a1,s9,2020 # 3fcaf7e4 <previous_settings.8>
4200e390:	c642                	sw	a6,12(sp)
4200e392:	fe379097          	auipc	ra,0xfe379
4200e396:	e6a080e7          	jalr	-406(ra) # 403871fc <memcmp>
4200e39a:	00492703          	lw	a4,4(s2)
4200e39e:	004a2783          	lw	a5,4(s4)
4200e3a2:	4832                	lw	a6,12(sp)
4200e3a4:	00a03bb3          	snez	s7,a0
4200e3a8:	4985                	li	s3,1
4200e3aa:	04f71263          	bne	a4,a5,4200e3ee <factory_draw_classic+0xa6>
4200e3ae:	00892703          	lw	a4,8(s2)
4200e3b2:	008a2783          	lw	a5,8(s4)
4200e3b6:	02f71c63          	bne	a4,a5,4200e3ee <factory_draw_classic+0xa6>
4200e3ba:	01492703          	lw	a4,20(s2)
4200e3be:	014a2783          	lw	a5,20(s4)
4200e3c2:	02f71663          	bne	a4,a5,4200e3ee <factory_draw_classic+0xa6>
4200e3c6:	01092703          	lw	a4,16(s2)
4200e3ca:	010a2783          	lw	a5,16(s4)
4200e3ce:	02f71063          	bne	a4,a5,4200e3ee <factory_draw_classic+0xa6>
4200e3d2:	00c92703          	lw	a4,12(s2)
4200e3d6:	00ca2783          	lw	a5,12(s4)
4200e3da:	00f71a63          	bne	a4,a5,4200e3ee <factory_draw_classic+0xa6>
4200e3de:	01c92983          	lw	s3,28(s2)
4200e3e2:	01ca2783          	lw	a5,28(s4)
4200e3e6:	40f989b3          	sub	s3,s3,a5
4200e3ea:	013039b3          	snez	s3,s3
4200e3ee:	01786833          	or	a6,a6,s7
4200e3f2:	3fcb4c37          	lui	s8,0x3fcb4
4200e3f6:	3a081c63          	bnez	a6,4200e7ae <factory_draw_classic+0x466>
4200e3fa:	3a099a63          	bnez	s3,4200e7ae <factory_draw_classic+0x466>
4200e3fe:	0f042b03          	lw	s6,240(s0)
4200e402:	900c2783          	lw	a5,-1792(s8) # 3fcb3900 <previous_weather.6>
4200e406:	40fb0b33          	sub	s6,s6,a5
4200e40a:	01603b33          	snez	s6,s6
4200e40e:	45d1                	li	a1,20
4200e410:	0868                	addi	a0,sp,28
4200e412:	60d010ef          	jal	4201021e <network_address>
4200e416:	00044783          	lbu	a5,0(s0)
4200e41a:	38079c63          	bnez	a5,4200e7b2 <factory_draw_classic+0x46a>
4200e41e:	3c0b45b7          	lui	a1,0x3c0b4
4200e422:	bbc58593          	addi	a1,a1,-1092 # 3c0b3bbc <_esp_libc_clock_array_end+0x3a6c>
4200e426:	00a8                	addi	a0,sp,72
4200e428:	fe379097          	auipc	ra,0xfe379
4200e42c:	340080e7          	jalr	832(ra) # 40387768 <strcpy>
4200e430:	3fcafd37          	lui	s10,0x3fcaf
4200e434:	000a9a63          	bnez	s5,4200e448 <factory_draw_classic+0x100>
4200e438:	77cd0593          	addi	a1,s10,1916 # 3fcaf77c <previous_description.5>
4200e43c:	00a8                	addi	a0,sp,72
4200e43e:	fe379097          	auipc	ra,0xfe379
4200e442:	214080e7          	jalr	532(ra) # 40387652 <strcmp>
4200e446:	c505                	beqz	a0,4200e46e <factory_draw_classic+0x126>
4200e448:	67c1                	lui	a5,0x10
4200e44a:	4581                	li	a1,0
4200e44c:	4505                	li	a0,1
4200e44e:	8856                	mv	a6,s5
4200e450:	17fd                	addi	a5,a5,-1 # ffff <CSR_UINTSTATUS+0xf34e>
4200e452:	00b8                	addi	a4,sp,72
4200e454:	0b400693          	li	a3,180
4200e458:	02800613          	li	a2,40
4200e45c:	9c9ff0ef          	jal	4200de24 <scrolling_label>
4200e460:	00ac                	addi	a1,sp,72
4200e462:	77cd0513          	addi	a0,s10,1916
4200e466:	fe379097          	auipc	ra,0xfe379
4200e46a:	302080e7          	jalr	770(ra) # 40387768 <strcpy>
4200e46e:	00892683          	lw	a3,8(s2)
4200e472:	14f4c783          	lbu	a5,335(s1)
4200e476:	3c0b4d37          	lui	s10,0x3c0b4
4200e47a:	00d6a713          	slti	a4,a3,13
4200e47e:	00173713          	seqz	a4,a4
4200e482:	00f037b3          	snez	a5,a5
4200e486:	8ff9                	and	a5,a5,a4
4200e488:	40f007b3          	neg	a5,a5
4200e48c:	9bd1                	andi	a5,a5,-12
4200e48e:	96be                	add	a3,a3,a5
4200e490:	bf8d0613          	addi	a2,s10,-1032 # 3c0b3bf8 <_esp_libc_clock_array_end+0x3aa8>
4200e494:	04100593          	li	a1,65
4200e498:	00a8                	addi	a0,sp,72
4200e49a:	1918f0ef          	jal	4209de2a <snprintf>
4200e49e:	1424d703          	lhu	a4,322(s1)
4200e4a2:	4781                	li	a5,0
4200e4a4:	4801                	li	a6,0
4200e4a6:	04000693          	li	a3,64
4200e4aa:	00b0                	addi	a2,sp,72
4200e4ac:	05000593          	li	a1,80
4200e4b0:	4501                	li	a0,0
4200e4b2:	f34ff0ef          	jal	4200dbe6 <display_factory_text>
4200e4b6:	00092783          	lw	a5,0(s2)
4200e4ba:	8b85                	andi	a5,a5,1
4200e4bc:	44079b63          	bnez	a5,4200e912 <factory_draw_classic+0x5ca>
4200e4c0:	3c0b4637          	lui	a2,0x3c0b4
4200e4c4:	6741                	lui	a4,0x10
4200e4c6:	bb860613          	addi	a2,a2,-1096 # 3c0b3bb8 <_esp_libc_clock_array_end+0x3a68>
4200e4ca:	177d                	addi	a4,a4,-1 # ffff <CSR_UINTSTATUS+0xf34e>
4200e4cc:	04000693          	li	a3,64
4200e4d0:	4801                	li	a6,0
4200e4d2:	4781                	li	a5,0
4200e4d4:	05000593          	li	a1,80
4200e4d8:	8536                	mv	a0,a3
4200e4da:	f0cff0ef          	jal	4200dbe6 <display_factory_text>
4200e4de:	00099463          	bnez	s3,4200e4e6 <factory_draw_classic+0x19e>
4200e4e2:	080b8d63          	beqz	s7,4200e57c <factory_draw_classic+0x234>
4200e4e6:	00492683          	lw	a3,4(s2)
4200e4ea:	bf8d0613          	addi	a2,s10,-1032
4200e4ee:	04100593          	li	a1,65
4200e4f2:	00a8                	addi	a0,sp,72
4200e4f4:	1378f0ef          	jal	4209de2a <snprintf>
4200e4f8:	1444d703          	lhu	a4,324(s1)
4200e4fc:	4781                	li	a5,0
4200e4fe:	4801                	li	a6,0
4200e500:	04000693          	li	a3,64
4200e504:	00b0                	addi	a2,sp,72
4200e506:	05000593          	li	a1,80
4200e50a:	06000513          	li	a0,96
4200e50e:	ed8ff0ef          	jal	4200dbe6 <display_factory_text>
4200e512:	01892783          	lw	a5,24(s2)
4200e516:	4719                	li	a4,6
4200e518:	00f77363          	bgeu	a4,a5,4200e51e <factory_draw_classic+0x1d6>
4200e51c:	4781                	li	a5,0
4200e51e:	3c0d4637          	lui	a2,0x3c0d4
4200e522:	078a                	slli	a5,a5,0x2
4200e524:	a6060613          	addi	a2,a2,-1440 # 3c0d3a60 <names.4>
4200e528:	963e                	add	a2,a2,a5
4200e52a:	1464d703          	lhu	a4,326(s1)
4200e52e:	4210                	lw	a2,0(a2)
4200e530:	4801                	li	a6,0
4200e532:	4781                	li	a5,0
4200e534:	02000693          	li	a3,32
4200e538:	06e00593          	li	a1,110
4200e53c:	0b000513          	li	a0,176
4200e540:	ea6ff0ef          	jal	4200dbe6 <display_factory_text>
4200e544:	14a4c503          	lbu	a0,330(s1)
4200e548:	1810                	addi	a2,sp,48
4200e54a:	85ca                	mv	a1,s2
4200e54c:	bb1ff0ef          	jal	4200e0fc <date_label.isra.0>
4200e550:	4701                	li	a4,0
4200e552:	46e1                	li	a3,24
4200e554:	07800613          	li	a2,120
4200e558:	09600593          	li	a1,150
4200e55c:	4501                	li	a0,0
4200e55e:	e96fe0ef          	jal	4200cbf4 <display_fill>
4200e562:	67c1                	lui	a5,0x10
4200e564:	4881                	li	a7,0
4200e566:	4801                	li	a6,0
4200e568:	17fd                	addi	a5,a5,-1 # ffff <CSR_UINTSTATUS+0xf34e>
4200e56a:	4761                	li	a4,24
4200e56c:	1814                	addi	a3,sp,48
4200e56e:	07800613          	li	a2,120
4200e572:	09600593          	li	a1,150
4200e576:	4501                	li	a0,0
4200e578:	e8eff0ef          	jal	4200dc06 <display_factory_text_bounded>
4200e57c:	1c0b0063          	beqz	s6,4200e73c <factory_draw_classic+0x3f4>
4200e580:	4701                	li	a4,0
4200e582:	02200693          	li	a3,34
4200e586:	0b400613          	li	a2,180
4200e58a:	4581                	li	a1,0
4200e58c:	4501                	li	a0,0
4200e58e:	e66fe0ef          	jal	4200cbf4 <display_fill>
4200e592:	7e000793          	li	a5,2016
4200e596:	06648713          	addi	a4,s1,102
4200e59a:	8856                	mv	a6,s5
4200e59c:	0b400693          	li	a3,180
4200e5a0:	4629                	li	a2,10
4200e5a2:	4581                	li	a1,0
4200e5a4:	4501                	li	a0,0
4200e5a6:	87fff0ef          	jal	4200de24 <scrolling_label>
4200e5aa:	00044783          	lbu	a5,0(s0)
4200e5ae:	0ca40713          	addi	a4,s0,202
4200e5b2:	e789                	bnez	a5,4200e5bc <factory_draw_classic+0x274>
4200e5b4:	3c0c3737          	lui	a4,0x3c0c3
4200e5b8:	a5070713          	addi	a4,a4,-1456 # 3c0c2a50 <_esp_libc_clock_array_end+0x12900>
4200e5bc:	67c1                	lui	a5,0x10
4200e5be:	1781                	addi	a5,a5,-32 # ffe0 <CSR_UINTSTATUS+0xf32f>
4200e5c0:	8856                	mv	a6,s5
4200e5c2:	05000693          	li	a3,80
4200e5c6:	05300613          	li	a2,83
4200e5ca:	0a000593          	li	a1,160
4200e5ce:	4509                	li	a0,2
4200e5d0:	855ff0ef          	jal	4200de24 <scrolling_label>
4200e5d4:	00044783          	lbu	a5,0(s0)
4200e5d8:	cb89                	beqz	a5,4200e5ea <factory_draw_classic+0x2a2>
4200e5da:	4629                	li	a2,10
4200e5dc:	0b400593          	li	a1,180
4200e5e0:	03040513          	addi	a0,s0,48
4200e5e4:	004010ef          	jal	4200f5e8 <media_draw_weather>
4200e5e8:	c911                	beqz	a0,4200e5fc <factory_draw_classic+0x2b4>
4200e5ea:	03c00693          	li	a3,60
4200e5ee:	4701                	li	a4,0
4200e5f0:	8636                	mv	a2,a3
4200e5f2:	45a9                	li	a1,10
4200e5f4:	0b400513          	li	a0,180
4200e5f8:	dfcfe0ef          	jal	4200cbf4 <display_fill>
4200e5fc:	6591                	lui	a1,0x4
4200e5fe:	003bb537          	lui	a0,0x3bb
4200e602:	0b400693          	li	a3,180
4200e606:	4629                	li	a2,10
4200e608:	c0058593          	addi	a1,a1,-1024 # 3c00 <CSR_UINTSTATUS+0x2f4f>
4200e60c:	80050513          	addi	a0,a0,-2048 # 3ba800 <CSR_UINTSTATUS+0x3b9b4f>
4200e610:	62f000ef          	jal	4200f43e <media_draw_jpeg>
4200e614:	6591                	lui	a1,0x4
4200e616:	0ba00693          	li	a3,186
4200e61a:	02800613          	li	a2,40
4200e61e:	c0058593          	addi	a1,a1,-1024 # 3c00 <CSR_UINTSTATUS+0x2f4f>
4200e622:	003c2537          	lui	a0,0x3c2
4200e626:	619000ef          	jal	4200f43e <media_draw_jpeg>
4200e62a:	6591                	lui	a1,0x4
4200e62c:	003be537          	lui	a0,0x3be
4200e630:	0d200693          	li	a3,210
4200e634:	4631                	li	a2,12
4200e636:	c0058593          	addi	a1,a1,-1024 # 3c00 <CSR_UINTSTATUS+0x2f4f>
4200e63a:	40050513          	addi	a0,a0,1024 # 3be400 <CSR_UINTSTATUS+0x3bd74f>
4200e63e:	601000ef          	jal	4200f43e <media_draw_jpeg>
4200e642:	6591                	lui	a1,0x4
4200e644:	003c6537          	lui	a0,0x3c6
4200e648:	0d800693          	li	a3,216
4200e64c:	02800613          	li	a2,40
4200e650:	c0058593          	addi	a1,a1,-1024 # 3c00 <CSR_UINTSTATUS+0x2f4f>
4200e654:	c0050513          	addi	a0,a0,-1024 # 3c5c00 <CSR_UINTSTATUS+0x3c4f4f>
4200e658:	5e7000ef          	jal	4200f43e <media_draw_jpeg>
4200e65c:	4701                	li	a4,0
4200e65e:	46e1                	li	a3,24
4200e660:	04800613          	li	a2,72
4200e664:	0b400593          	li	a1,180
4200e668:	05000513          	li	a0,80
4200e66c:	d88fe0ef          	jal	4200cbf4 <display_fill>
4200e670:	14e4c703          	lbu	a4,334(s1)
4200e674:	2a070563          	beqz	a4,4200e91e <factory_draw_classic+0x5d6>
4200e678:	3c0b4837          	lui	a6,0x3c0b4
4200e67c:	bb080813          	addi	a6,a6,-1104 # 3c0b3bb0 <_esp_libc_clock_array_end+0x3a60>
4200e680:	00044783          	lbu	a5,0(s0)
4200e684:	2a078263          	beqz	a5,4200e928 <factory_draw_classic+0x5e0>
4200e688:	441c                	lw	a5,8(s0)
4200e68a:	444c                	lw	a1,12(s0)
4200e68c:	cb0d                	beqz	a4,4200e6be <factory_draw_classic+0x376>
4200e68e:	3c0d4737          	lui	a4,0x3c0d4
4200e692:	aa070713          	addi	a4,a4,-1376 # 3c0d3aa0 <names.4+0x40>
4200e696:	4310                	lw	a2,0(a4)
4200e698:	4354                	lw	a3,4(a4)
4200e69a:	853e                	mv	a0,a5
4200e69c:	c642                	sw	a6,12(sp)
4200e69e:	fdff2097          	auipc	ra,0xfdff2
4200e6a2:	3ee080e7          	jalr	1006(ra) # 40000a8c <__muldf3>
4200e6a6:	3c0d47b7          	lui	a5,0x3c0d4
4200e6aa:	aa878793          	addi	a5,a5,-1368 # 3c0d3aa8 <names.4+0x48>
4200e6ae:	4390                	lw	a2,0(a5)
4200e6b0:	43d4                	lw	a3,4(a5)
4200e6b2:	fdff2097          	auipc	ra,0xfdff2
4200e6b6:	366080e7          	jalr	870(ra) # 40000a18 <__adddf3>
4200e6ba:	4832                	lw	a6,12(sp)
4200e6bc:	87aa                	mv	a5,a0
4200e6be:	3c0b4637          	lui	a2,0x3c0b4
4200e6c2:	873e                	mv	a4,a5
4200e6c4:	be060613          	addi	a2,a2,-1056 # 3c0b3be0 <_esp_libc_clock_array_end+0x3a90>
4200e6c8:	87ae                	mv	a5,a1
4200e6ca:	0168                	addi	a0,sp,140
4200e6cc:	04100593          	li	a1,65
4200e6d0:	75a8f0ef          	jal	4209de2a <snprintf>
4200e6d4:	67c1                	lui	a5,0x10
4200e6d6:	17fd                	addi	a5,a5,-1 # ffff <CSR_UINTSTATUS+0xf34e>
4200e6d8:	4881                	li	a7,0
4200e6da:	4801                	li	a6,0
4200e6dc:	4761                	li	a4,24
4200e6de:	0174                	addi	a3,sp,140
4200e6e0:	04800613          	li	a2,72
4200e6e4:	0b400593          	li	a1,180
4200e6e8:	05000513          	li	a0,80
4200e6ec:	d1aff0ef          	jal	4200dc06 <display_factory_text_bounded>
4200e6f0:	4701                	li	a4,0
4200e6f2:	46e1                	li	a3,24
4200e6f4:	04800613          	li	a2,72
4200e6f8:	0d200593          	li	a1,210
4200e6fc:	05000513          	li	a0,80
4200e700:	cf4fe0ef          	jal	4200cbf4 <display_fill>
4200e704:	00044783          	lbu	a5,0(s0)
4200e708:	22078b63          	beqz	a5,4200e93e <factory_draw_classic+0x5f6>
4200e70c:	5414                	lw	a3,40(s0)
4200e70e:	3c0b4637          	lui	a2,0x3c0b4
4200e712:	c0860613          	addi	a2,a2,-1016 # 3c0b3c08 <_esp_libc_clock_array_end+0x3ab8>
4200e716:	04100593          	li	a1,65
4200e71a:	0168                	addi	a0,sp,140
4200e71c:	70e8f0ef          	jal	4209de2a <snprintf>
4200e720:	67c1                	lui	a5,0x10
4200e722:	4881                	li	a7,0
4200e724:	4801                	li	a6,0
4200e726:	17fd                	addi	a5,a5,-1 # ffff <CSR_UINTSTATUS+0xf34e>
4200e728:	4761                	li	a4,24
4200e72a:	0174                	addi	a3,sp,140
4200e72c:	04800613          	li	a2,72
4200e730:	0d200593          	li	a1,210
4200e734:	05000513          	li	a0,80
4200e738:	cceff0ef          	jal	4200dc06 <display_factory_text_bounded>
4200e73c:	1494c503          	lbu	a0,329(s1)
4200e740:	5e3000ef          	jal	4200f522 <media_animation_frames>
4200e744:	c911                	beqz	a0,4200e758 <factory_draw_classic+0x410>
4200e746:	02adf5b3          	remu	a1,s11,a0
4200e74a:	1494c503          	lbu	a0,329(s1)
4200e74e:	0a000693          	li	a3,160
4200e752:	8636                	mv	a2,a3
4200e754:	629000ef          	jal	4200f57c <media_draw_animation>
4200e758:	85a6                	mv	a1,s1
4200e75a:	16c00613          	li	a2,364
4200e75e:	7e4c8513          	addi	a0,s9,2020
4200e762:	fe379097          	auipc	ra,0xfe379
4200e766:	ad8080e7          	jalr	-1320(ra) # 4038723a <memcpy>
4200e76a:	85ca                	mv	a1,s2
4200e76c:	8552                	mv	a0,s4
4200e76e:	02400613          	li	a2,36
4200e772:	fe379097          	auipc	ra,0xfe379
4200e776:	ac8080e7          	jalr	-1336(ra) # 4038723a <memcpy>
4200e77a:	0f042783          	lw	a5,240(s0)
4200e77e:	10c12083          	lw	ra,268(sp)
4200e782:	10812403          	lw	s0,264(sp)
4200e786:	90fc2023          	sw	a5,-1792(s8)
4200e78a:	10412483          	lw	s1,260(sp)
4200e78e:	10012903          	lw	s2,256(sp)
4200e792:	59fe                	lw	s3,252(sp)
4200e794:	5a6e                	lw	s4,248(sp)
4200e796:	5ade                	lw	s5,244(sp)
4200e798:	5b4e                	lw	s6,240(sp)
4200e79a:	5bbe                	lw	s7,236(sp)
4200e79c:	5c2e                	lw	s8,232(sp)
4200e79e:	5c9e                	lw	s9,228(sp)
4200e7a0:	5d0e                	lw	s10,224(sp)
4200e7a2:	4dfe                	lw	s11,220(sp)
4200e7a4:	6151                	addi	sp,sp,272
4200e7a6:	8082                	ret
4200e7a8:	8bbe                	mv	s7,a5
4200e7aa:	4985                	li	s3,1
4200e7ac:	b189                	j	4200e3ee <factory_draw_classic+0xa6>
4200e7ae:	4b05                	li	s6,1
4200e7b0:	b9b9                	j	4200e40e <factory_draw_classic+0xc6>
4200e7b2:	47a9                	li	a5,10
4200e7b4:	02fd76b3          	remu	a3,s10,a5
4200e7b8:	4799                	li	a5,6
4200e7ba:	0ef68463          	beq	a3,a5,4200e8a2 <factory_draw_classic+0x55a>
4200e7be:	00d7ed63          	bltu	a5,a3,4200e7d8 <factory_draw_classic+0x490>
4200e7c2:	478d                	li	a5,3
4200e7c4:	08f68363          	beq	a3,a5,4200e84a <factory_draw_classic+0x502>
4200e7c8:	4791                	li	a5,4
4200e7ca:	08f68563          	beq	a3,a5,4200e854 <factory_draw_classic+0x50c>
4200e7ce:	4785                	li	a5,1
4200e7d0:	06f68163          	beq	a3,a5,4200e832 <factory_draw_classic+0x4ea>
4200e7d4:	0874                	addi	a3,sp,28
4200e7d6:	a085                	j	4200e836 <factory_draw_classic+0x4ee>
4200e7d8:	479d                	li	a5,7
4200e7da:	0cf68763          	beq	a3,a5,4200e8a8 <factory_draw_classic+0x560>
4200e7de:	47a5                	li	a5,9
4200e7e0:	fef69ae3          	bne	a3,a5,4200e7d4 <factory_draw_classic+0x48c>
4200e7e4:	14e4c703          	lbu	a4,334(s1)
4200e7e8:	501c                	lw	a5,32(s0)
4200e7ea:	504c                	lw	a1,36(s0)
4200e7ec:	10070e63          	beqz	a4,4200e908 <factory_draw_classic+0x5c0>
4200e7f0:	3c0d4737          	lui	a4,0x3c0d4
4200e7f4:	aa070713          	addi	a4,a4,-1376 # 3c0d3aa0 <names.4+0x40>
4200e7f8:	4310                	lw	a2,0(a4)
4200e7fa:	4354                	lw	a3,4(a4)
4200e7fc:	853e                	mv	a0,a5
4200e7fe:	fdff2097          	auipc	ra,0xfdff2
4200e802:	28e080e7          	jalr	654(ra) # 40000a8c <__muldf3>
4200e806:	3c0d47b7          	lui	a5,0x3c0d4
4200e80a:	aa878793          	addi	a5,a5,-1368 # 3c0d3aa8 <names.4+0x48>
4200e80e:	4390                	lw	a2,0(a5)
4200e810:	43d4                	lw	a3,4(a5)
4200e812:	fdff2097          	auipc	ra,0xfdff2
4200e816:	206080e7          	jalr	518(ra) # 40000a18 <__adddf3>
4200e81a:	3c0b4837          	lui	a6,0x3c0b4
4200e81e:	87aa                	mv	a5,a0
4200e820:	bb080813          	addi	a6,a6,-1104 # 3c0b3bb0 <_esp_libc_clock_array_end+0x3a60>
4200e824:	3c0b4637          	lui	a2,0x3c0b4
4200e828:	873e                	mv	a4,a5
4200e82a:	be860613          	addi	a2,a2,-1048 # 3c0b3be8 <_esp_libc_clock_array_end+0x3a98>
4200e82e:	87ae                	mv	a5,a1
4200e830:	a0c9                	j	4200e8f2 <factory_draw_classic+0x5aa>
4200e832:	0da40693          	addi	a3,s0,218
4200e836:	3c0b5637          	lui	a2,0x3c0b5
4200e83a:	a3c60613          	addi	a2,a2,-1476 # 3c0b4a3c <_esp_libc_clock_array_end+0x48ec>
4200e83e:	04100593          	li	a1,65
4200e842:	00a8                	addi	a0,sp,72
4200e844:	5e68f0ef          	jal	4209de2a <snprintf>
4200e848:	b6e5                	j	4200e430 <factory_draw_classic+0xe8>
4200e84a:	3c0b45b7          	lui	a1,0x3c0b4
4200e84e:	bcc58593          	addi	a1,a1,-1076 # 3c0b3bcc <_esp_libc_clock_array_end+0x3a7c>
4200e852:	bed1                	j	4200e426 <factory_draw_classic+0xde>
4200e854:	1504c783          	lbu	a5,336(s1)
4200e858:	cb9d                	beqz	a5,4200e88e <factory_draw_classic+0x546>
4200e85a:	3c0b4d37          	lui	s10,0x3c0b4
4200e85e:	b98d0d13          	addi	s10,s10,-1128 # 3c0b3b98 <_esp_libc_clock_array_end+0x3a48>
4200e862:	4808                	lw	a0,16(s0)
4200e864:	484c                	lw	a1,20(s0)
4200e866:	cb8d                	beqz	a5,4200e898 <factory_draw_classic+0x550>
4200e868:	3c0d47b7          	lui	a5,0x3c0d4
4200e86c:	a9078793          	addi	a5,a5,-1392 # 3c0d3a90 <names.4+0x30>
4200e870:	4390                	lw	a2,0(a5)
4200e872:	43d4                	lw	a3,4(a5)
4200e874:	fdff2097          	auipc	ra,0xfdff2
4200e878:	218080e7          	jalr	536(ra) # 40000a8c <__muldf3>
4200e87c:	872a                	mv	a4,a0
4200e87e:	87ae                	mv	a5,a1
4200e880:	866a                	mv	a2,s10
4200e882:	04100593          	li	a1,65
4200e886:	00a8                	addi	a0,sp,72
4200e888:	5a28f0ef          	jal	4209de2a <snprintf>
4200e88c:	b655                	j	4200e430 <factory_draw_classic+0xe8>
4200e88e:	3c0b4d37          	lui	s10,0x3c0b4
4200e892:	ba4d0d13          	addi	s10,s10,-1116 # 3c0b3ba4 <_esp_libc_clock_array_end+0x3a54>
4200e896:	b7f1                	j	4200e862 <factory_draw_classic+0x51a>
4200e898:	3c0d47b7          	lui	a5,0x3c0d4
4200e89c:	a9878793          	addi	a5,a5,-1384 # 3c0d3a98 <names.4+0x38>
4200e8a0:	bfc1                	j	4200e870 <factory_draw_classic+0x528>
4200e8a2:	03440693          	addi	a3,s0,52
4200e8a6:	bf41                	j	4200e836 <factory_draw_classic+0x4ee>
4200e8a8:	14e4c703          	lbu	a4,334(s1)
4200e8ac:	4c1c                	lw	a5,24(s0)
4200e8ae:	4c4c                	lw	a1,28(s0)
4200e8b0:	c739                	beqz	a4,4200e8fe <factory_draw_classic+0x5b6>
4200e8b2:	3c0d4737          	lui	a4,0x3c0d4
4200e8b6:	aa070713          	addi	a4,a4,-1376 # 3c0d3aa0 <names.4+0x40>
4200e8ba:	4310                	lw	a2,0(a4)
4200e8bc:	4354                	lw	a3,4(a4)
4200e8be:	853e                	mv	a0,a5
4200e8c0:	fdff2097          	auipc	ra,0xfdff2
4200e8c4:	1cc080e7          	jalr	460(ra) # 40000a8c <__muldf3>
4200e8c8:	3c0d47b7          	lui	a5,0x3c0d4
4200e8cc:	aa878793          	addi	a5,a5,-1368 # 3c0d3aa8 <names.4+0x48>
4200e8d0:	4390                	lw	a2,0(a5)
4200e8d2:	43d4                	lw	a3,4(a5)
4200e8d4:	fdff2097          	auipc	ra,0xfdff2
4200e8d8:	144080e7          	jalr	324(ra) # 40000a18 <__adddf3>
4200e8dc:	3c0b4837          	lui	a6,0x3c0b4
4200e8e0:	87aa                	mv	a5,a0
4200e8e2:	bb080813          	addi	a6,a6,-1104 # 3c0b3bb0 <_esp_libc_clock_array_end+0x3a60>
4200e8e6:	3c0b4637          	lui	a2,0x3c0b4
4200e8ea:	873e                	mv	a4,a5
4200e8ec:	bd860613          	addi	a2,a2,-1064 # 3c0b3bd8 <_esp_libc_clock_array_end+0x3a88>
4200e8f0:	87ae                	mv	a5,a1
4200e8f2:	04100593          	li	a1,65
4200e8f6:	00a8                	addi	a0,sp,72
4200e8f8:	5328f0ef          	jal	4209de2a <snprintf>
4200e8fc:	be15                	j	4200e430 <factory_draw_classic+0xe8>
4200e8fe:	3c0b4837          	lui	a6,0x3c0b4
4200e902:	bb480813          	addi	a6,a6,-1100 # 3c0b3bb4 <_esp_libc_clock_array_end+0x3a64>
4200e906:	b7c5                	j	4200e8e6 <factory_draw_classic+0x59e>
4200e908:	3c0b4837          	lui	a6,0x3c0b4
4200e90c:	bb480813          	addi	a6,a6,-1100 # 3c0b3bb4 <_esp_libc_clock_array_end+0x3a64>
4200e910:	bf11                	j	4200e824 <factory_draw_classic+0x4dc>
4200e912:	3c0b1637          	lui	a2,0x3c0b1
4200e916:	d1860613          	addi	a2,a2,-744 # 3c0b0d18 <_esp_libc_clock_array_end+0xbc8>
4200e91a:	4701                	li	a4,0
4200e91c:	be45                	j	4200e4cc <factory_draw_classic+0x184>
4200e91e:	3c0b4837          	lui	a6,0x3c0b4
4200e922:	bb480813          	addi	a6,a6,-1100 # 3c0b3bb4 <_esp_libc_clock_array_end+0x3a64>
4200e926:	bba9                	j	4200e680 <factory_draw_classic+0x338>
4200e928:	3c0b4637          	lui	a2,0x3c0b4
4200e92c:	86c2                	mv	a3,a6
4200e92e:	c0060613          	addi	a2,a2,-1024 # 3c0b3c00 <_esp_libc_clock_array_end+0x3ab0>
4200e932:	04100593          	li	a1,65
4200e936:	0168                	addi	a0,sp,140
4200e938:	4f28f0ef          	jal	4209de2a <snprintf>
4200e93c:	bb61                	j	4200e6d4 <factory_draw_classic+0x38c>
4200e93e:	3c0b45b7          	lui	a1,0x3c0b4
4200e942:	c1058593          	addi	a1,a1,-1008 # 3c0b3c10 <_esp_libc_clock_array_end+0x3ac0>
4200e946:	0168                	addi	a0,sp,140
4200e948:	fe379097          	auipc	ra,0xfe379
4200e94c:	e20080e7          	jalr	-480(ra) # 40387768 <strcpy>
4200e950:	bbc1                	j	4200e720 <factory_draw_classic+0x3d8>


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200eb74 <factory_draw_dial>:
4200eb74:	7175                	addi	sp,sp,-144
4200eb76:	03200793          	li	a5,50
4200eb7a:	d63e                	sw	a5,44(sp)
4200eb7c:	04600793          	li	a5,70
4200eb80:	d83e                	sw	a5,48(sp)
4200eb82:	05a00793          	li	a5,90
4200eb86:	da3e                	sw	a5,52(sp)
4200eb88:	ffe107b7          	lui	a5,0xffe10
4200eb8c:	dad6                	sw	s5,116(sp)
4200eb8e:	80078793          	addi	a5,a5,-2048 # ffe0f800 <SYSTEM+0x9fd4f800>
4200eb92:	8aaa                	mv	s5,a0
4200eb94:	4148                	lw	a0,4(a0)
4200eb96:	d23e                	sw	a5,36(sp)
4200eb98:	57fd                	li	a5,-1
4200eb9a:	dcd2                	sw	s4,120(sp)
4200eb9c:	02f11423          	sh	a5,40(sp)
4200eba0:	4a0d                	li	s4,3
4200eba2:	4795                	li	a5,5
4200eba4:	c706                	sw	ra,140(sp)
4200eba6:	c522                	sw	s0,136(sp)
4200eba8:	c326                	sw	s1,132(sp)
4200ebaa:	c14a                	sw	s2,128(sp)
4200ebac:	84b2                	mv	s1,a2
4200ebae:	dece                	sw	s3,124(sp)
4200ebb0:	d8da                	sw	s6,112(sp)
4200ebb2:	ceee                	sw	s11,92(sp)
4200ebb4:	dc3e                	sw	a5,56(sp)
4200ebb6:	8dae                	mv	s11,a1
4200ebb8:	de3e                	sw	a5,60(sp)
4200ebba:	d6de                	sw	s7,108(sp)
4200ebbc:	d4e2                	sw	s8,104(sp)
4200ebbe:	d2e6                	sw	s9,100(sp)
4200ebc0:	d0ea                	sw	s10,96(sp)
4200ebc2:	c0d2                	sw	s4,64(sp)
4200ebc4:	fdff2097          	auipc	ra,0xfdff2
4200ebc8:	e94080e7          	jalr	-364(ra) # 40000a58 <__floatsisf>
4200ebcc:	842a                	mv	s0,a0
4200ebce:	008aa503          	lw	a0,8(s5)
4200ebd2:	47b1                	li	a5,12
4200ebd4:	3c0d4b37          	lui	s6,0x3c0d4
4200ebd8:	02f56533          	rem	a0,a0,a5
4200ebdc:	3c0d49b7          	lui	s3,0x3c0d4
4200ebe0:	ab898993          	addi	s3,s3,-1352 # 3c0d3ab8 <names.4+0x58>
4200ebe4:	fdff2097          	auipc	ra,0xfdff2
4200ebe8:	e74080e7          	jalr	-396(ra) # 40000a58 <__floatsisf>
4200ebec:	da0b2583          	lw	a1,-608(s6) # 3c0d3da0 <names.4+0x340>
4200ebf0:	892a                	mv	s2,a0
4200ebf2:	8522                	mv	a0,s0
4200ebf4:	fdff2097          	auipc	ra,0xfdff2
4200ebf8:	e2c080e7          	jalr	-468(ra) # 40000a20 <__divsf3>
4200ebfc:	85aa                	mv	a1,a0
4200ebfe:	854a                	mv	a0,s2
4200ec00:	fdff2097          	auipc	ra,0xfdff2
4200ec04:	e1c080e7          	jalr	-484(ra) # 40000a1c <__addsf3>
4200ec08:	3c0d4937          	lui	s2,0x3c0d4
4200ec0c:	ab090913          	addi	s2,s2,-1360 # 3c0d3ab0 <names.4+0x50>
4200ec10:	fdff2097          	auipc	ra,0xfdff2
4200ec14:	e1c080e7          	jalr	-484(ra) # 40000a2c <__extendsfdf2>
4200ec18:	00092603          	lw	a2,0(s2)
4200ec1c:	00492683          	lw	a3,4(s2)
4200ec20:	fdff2097          	auipc	ra,0xfdff2
4200ec24:	e6c080e7          	jalr	-404(ra) # 40000a8c <__muldf3>
4200ec28:	0009a603          	lw	a2,0(s3)
4200ec2c:	0049a683          	lw	a3,4(s3)
4200ec30:	fdff2097          	auipc	ra,0xfdff2
4200ec34:	cc4080e7          	jalr	-828(ra) # 400008f4 <__divdf3>
4200ec38:	fdff2097          	auipc	ra,0xfdff2
4200ec3c:	e6c080e7          	jalr	-404(ra) # 40000aa4 <__truncdfsf2>
4200ec40:	000aaa83          	lw	s5,0(s5)
4200ec44:	c2aa                	sw	a0,68(sp)
4200ec46:	8556                	mv	a0,s5
4200ec48:	fdff2097          	auipc	ra,0xfdff2
4200ec4c:	e10080e7          	jalr	-496(ra) # 40000a58 <__floatsisf>
4200ec50:	da0b2583          	lw	a1,-608(s6)
4200ec54:	fdff2097          	auipc	ra,0xfdff2
4200ec58:	dcc080e7          	jalr	-564(ra) # 40000a20 <__divsf3>
4200ec5c:	85a2                	mv	a1,s0
4200ec5e:	fdff2097          	auipc	ra,0xfdff2
4200ec62:	dbe080e7          	jalr	-578(ra) # 40000a1c <__addsf3>
4200ec66:	fdff2097          	auipc	ra,0xfdff2
4200ec6a:	dc6080e7          	jalr	-570(ra) # 40000a2c <__extendsfdf2>
4200ec6e:	00092603          	lw	a2,0(s2)
4200ec72:	00492683          	lw	a3,4(s2)
4200ec76:	3c0d4437          	lui	s0,0x3c0d4
4200ec7a:	ac040413          	addi	s0,s0,-1344 # 3c0d3ac0 <names.4+0x60>
4200ec7e:	fdff2097          	auipc	ra,0xfdff2
4200ec82:	e0e080e7          	jalr	-498(ra) # 40000a8c <__muldf3>
4200ec86:	4010                	lw	a2,0(s0)
4200ec88:	4054                	lw	a3,4(s0)
4200ec8a:	fdff2097          	auipc	ra,0xfdff2
4200ec8e:	c6a080e7          	jalr	-918(ra) # 400008f4 <__divdf3>
4200ec92:	fdff2097          	auipc	ra,0xfdff2
4200ec96:	e12080e7          	jalr	-494(ra) # 40000aa4 <__truncdfsf2>
4200ec9a:	c4aa                	sw	a0,72(sp)
4200ec9c:	8556                	mv	a0,s5
4200ec9e:	fdff2097          	auipc	ra,0xfdff2
4200eca2:	db6080e7          	jalr	-586(ra) # 40000a54 <__floatsidf>
4200eca6:	00092603          	lw	a2,0(s2)
4200ecaa:	00492683          	lw	a3,4(s2)
4200ecae:	fdff2097          	auipc	ra,0xfdff2
4200ecb2:	dde080e7          	jalr	-546(ra) # 40000a8c <__muldf3>
4200ecb6:	4010                	lw	a2,0(s0)
4200ecb8:	4054                	lw	a3,4(s0)
4200ecba:	fdff2097          	auipc	ra,0xfdff2
4200ecbe:	c3a080e7          	jalr	-966(ra) # 400008f4 <__divdf3>
4200ecc2:	fdff2097          	auipc	ra,0xfdff2
4200ecc6:	de2080e7          	jalr	-542(ra) # 40000aa4 <__truncdfsf2>
4200ecca:	c6aa                	sw	a0,76(sp)
4200eccc:	14049263          	bnez	s1,4200ee10 <factory_draw_dial+0x29c>
4200ecd0:	3fcaf7b7          	lui	a5,0x3fcaf
4200ecd4:	74c78993          	addi	s3,a5,1868 # 3fcaf74c <previous.0>
4200ecd8:	3c0d47b7          	lui	a5,0x3c0d4
4200ecdc:	a8878793          	addi	a5,a5,-1400 # 3c0d3a88 <names.4+0x28>
4200ece0:	0007ab03          	lw	s6,0(a5)
4200ece4:	0047ab83          	lw	s7,4(a5)
4200ece8:	4401                	li	s0,0
4200ecea:	02c10a13          	addi	s4,sp,44
4200ecee:	04410913          	addi	s2,sp,68
4200ecf2:	008a07b3          	add	a5,s4,s0
4200ecf6:	0007aa83          	lw	s5,0(a5)
4200ecfa:	8556                	mv	a0,s5
4200ecfc:	fdff2097          	auipc	ra,0xfdff2
4200ed00:	d58080e7          	jalr	-680(ra) # 40000a54 <__floatsidf>
4200ed04:	013407b3          	add	a5,s0,s3
4200ed08:	8caa                	mv	s9,a0
4200ed0a:	4388                	lw	a0,0(a5)
4200ed0c:	8d2e                	mv	s10,a1
4200ed0e:	fdff2097          	auipc	ra,0xfdff2
4200ed12:	d1e080e7          	jalr	-738(ra) # 40000a2c <__extendsfdf2>
4200ed16:	c02a                	sw	a0,0(sp)
4200ed18:	c22e                	sw	a1,4(sp)
4200ed1a:	009920ef          	jal	420a1522 <_sin>
4200ed1e:	008907b3          	add	a5,s2,s0
4200ed22:	cc2a                	sw	a0,24(sp)
4200ed24:	4388                	lw	a0,0(a5)
4200ed26:	ce2e                	sw	a1,28(sp)
4200ed28:	fdff2097          	auipc	ra,0xfdff2
4200ed2c:	d04080e7          	jalr	-764(ra) # 40000a2c <__extendsfdf2>
4200ed30:	c42a                	sw	a0,8(sp)
4200ed32:	c62e                	sw	a1,12(sp)
4200ed34:	7ee920ef          	jal	420a1522 <_sin>
4200ed38:	4662                	lw	a2,24(sp)
4200ed3a:	46f2                	lw	a3,28(sp)
4200ed3c:	c82a                	sw	a0,16(sp)
4200ed3e:	ca2e                	sw	a1,20(sp)
4200ed40:	8566                	mv	a0,s9
4200ed42:	85ea                	mv	a1,s10
4200ed44:	fdff2097          	auipc	ra,0xfdff2
4200ed48:	d48080e7          	jalr	-696(ra) # 40000a8c <__muldf3>
4200ed4c:	865a                	mv	a2,s6
4200ed4e:	86de                	mv	a3,s7
4200ed50:	fdff2097          	auipc	ra,0xfdff2
4200ed54:	cc8080e7          	jalr	-824(ra) # 40000a18 <__adddf3>
4200ed58:	fdff2097          	auipc	ra,0xfdff2
4200ed5c:	cdc080e7          	jalr	-804(ra) # 40000a34 <__fixdfsi>
4200ed60:	4642                	lw	a2,16(sp)
4200ed62:	46d2                	lw	a3,20(sp)
4200ed64:	8c2a                	mv	s8,a0
4200ed66:	85ea                	mv	a1,s10
4200ed68:	8566                	mv	a0,s9
4200ed6a:	fdff2097          	auipc	ra,0xfdff2
4200ed6e:	d22080e7          	jalr	-734(ra) # 40000a8c <__muldf3>
4200ed72:	865a                	mv	a2,s6
4200ed74:	86de                	mv	a3,s7
4200ed76:	fdff2097          	auipc	ra,0xfdff2
4200ed7a:	ca2080e7          	jalr	-862(ra) # 40000a18 <__adddf3>
4200ed7e:	fdff2097          	auipc	ra,0xfdff2
4200ed82:	cb6080e7          	jalr	-842(ra) # 40000a34 <__fixdfsi>
4200ed86:	06ac1963          	bne	s8,a0,4200edf8 <factory_draw_dial+0x284>
4200ed8a:	4502                	lw	a0,0(sp)
4200ed8c:	4592                	lw	a1,4(sp)
4200ed8e:	102920ef          	jal	420a0e90 <_cos>
4200ed92:	c82a                	sw	a0,16(sp)
4200ed94:	ca2e                	sw	a1,20(sp)
4200ed96:	4522                	lw	a0,8(sp)
4200ed98:	45b2                	lw	a1,12(sp)
4200ed9a:	0f6920ef          	jal	420a0e90 <_cos>
4200ed9e:	4642                	lw	a2,16(sp)
4200eda0:	46d2                	lw	a3,20(sp)
4200eda2:	c42a                	sw	a0,8(sp)
4200eda4:	c62e                	sw	a1,12(sp)
4200eda6:	8566                	mv	a0,s9
4200eda8:	85ea                	mv	a1,s10
4200edaa:	fdff2097          	auipc	ra,0xfdff2
4200edae:	ce2080e7          	jalr	-798(ra) # 40000a8c <__muldf3>
4200edb2:	862a                	mv	a2,a0
4200edb4:	86ae                	mv	a3,a1
4200edb6:	855a                	mv	a0,s6
4200edb8:	85de                	mv	a1,s7
4200edba:	fdff2097          	auipc	ra,0xfdff2
4200edbe:	ce2080e7          	jalr	-798(ra) # 40000a9c <__subdf3>
4200edc2:	fdff2097          	auipc	ra,0xfdff2
4200edc6:	c72080e7          	jalr	-910(ra) # 40000a34 <__fixdfsi>
4200edca:	4622                	lw	a2,8(sp)
4200edcc:	46b2                	lw	a3,12(sp)
4200edce:	8c2a                	mv	s8,a0
4200edd0:	85ea                	mv	a1,s10
4200edd2:	8566                	mv	a0,s9
4200edd4:	fdff2097          	auipc	ra,0xfdff2
4200edd8:	cb8080e7          	jalr	-840(ra) # 40000a8c <__muldf3>
4200eddc:	862a                	mv	a2,a0
4200edde:	86ae                	mv	a3,a1
4200ede0:	855a                	mv	a0,s6
4200ede2:	85de                	mv	a1,s7
4200ede4:	fdff2097          	auipc	ra,0xfdff2
4200ede8:	cb8080e7          	jalr	-840(ra) # 40000a9c <__subdf3>
4200edec:	fdff2097          	auipc	ra,0xfdff2
4200edf0:	c48080e7          	jalr	-952(ra) # 40000a34 <__fixdfsi>
4200edf4:	00ac0963          	beq	s8,a0,4200ee06 <factory_draw_dial+0x292>
4200edf8:	4502                	lw	a0,0(sp)
4200edfa:	4592                	lw	a1,4(sp)
4200edfc:	4701                	li	a4,0
4200edfe:	4695                	li	a3,5
4200ee00:	8656                	mv	a2,s5
4200ee02:	9dcff0ef          	jal	4200dfde <hand>
4200ee06:	0411                	addi	s0,s0,4
4200ee08:	47b1                	li	a5,12
4200ee0a:	eef414e3          	bne	s0,a5,4200ecf2 <factory_draw_dial+0x17e>
4200ee0e:	aa35                	j	4200ef4a <factory_draw_dial+0x3d6>
4200ee10:	0f000693          	li	a3,240
4200ee14:	4701                	li	a4,0
4200ee16:	8636                	mv	a2,a3
4200ee18:	4581                	li	a1,0
4200ee1a:	4501                	li	a0,0
4200ee1c:	dd9fd0ef          	jal	4200cbf4 <display_fill>
4200ee20:	3c0d4437          	lui	s0,0x3c0d4
4200ee24:	3c0d4ab7          	lui	s5,0x3c0d4
4200ee28:	67c1                	lui	a5,0x10
4200ee2a:	4b01                	li	s6,0
4200ee2c:	a8840413          	addi	s0,s0,-1400 # 3c0d3a88 <names.4+0x28>
4200ee30:	ac8a8a93          	addi	s5,s5,-1336 # 3c0d3ac8 <names.4+0x68>
4200ee34:	fff78b93          	addi	s7,a5,-1 # ffff <CSR_UINTSTATUS+0xf34e>
4200ee38:	034b77b3          	remu	a5,s6,s4
4200ee3c:	10078363          	beqz	a5,4200ef42 <factory_draw_dial+0x3ce>
4200ee40:	855a                	mv	a0,s6
4200ee42:	fdff2097          	auipc	ra,0xfdff2
4200ee46:	c22080e7          	jalr	-990(ra) # 40000a64 <__floatunsidf>
4200ee4a:	00092603          	lw	a2,0(s2)
4200ee4e:	00492683          	lw	a3,4(s2)
4200ee52:	fdff2097          	auipc	ra,0xfdff2
4200ee56:	c3a080e7          	jalr	-966(ra) # 40000a8c <__muldf3>
4200ee5a:	0009a603          	lw	a2,0(s3)
4200ee5e:	0049a683          	lw	a3,4(s3)
4200ee62:	fdff2097          	auipc	ra,0xfdff2
4200ee66:	a92080e7          	jalr	-1390(ra) # 400008f4 <__divdf3>
4200ee6a:	fdff2097          	auipc	ra,0xfdff2
4200ee6e:	c3a080e7          	jalr	-966(ra) # 40000aa4 <__truncdfsf2>
4200ee72:	fdff2097          	auipc	ra,0xfdff2
4200ee76:	bba080e7          	jalr	-1094(ra) # 40000a2c <__extendsfdf2>
4200ee7a:	c02a                	sw	a0,0(sp)
4200ee7c:	c22e                	sw	a1,4(sp)
4200ee7e:	6a4920ef          	jal	420a1522 <_sin>
4200ee82:	8c2a                	mv	s8,a0
4200ee84:	8cae                	mv	s9,a1
4200ee86:	4502                	lw	a0,0(sp)
4200ee88:	4592                	lw	a1,4(sp)
4200ee8a:	006920ef          	jal	420a0e90 <_cos>
4200ee8e:	4010                	lw	a2,0(s0)
4200ee90:	4054                	lw	a3,4(s0)
4200ee92:	c02a                	sw	a0,0(sp)
4200ee94:	c22e                	sw	a1,4(sp)
4200ee96:	fdff2097          	auipc	ra,0xfdff2
4200ee9a:	bf6080e7          	jalr	-1034(ra) # 40000a8c <__muldf3>
4200ee9e:	862a                	mv	a2,a0
4200eea0:	86ae                	mv	a3,a1
4200eea2:	4008                	lw	a0,0(s0)
4200eea4:	404c                	lw	a1,4(s0)
4200eea6:	fdff2097          	auipc	ra,0xfdff2
4200eeaa:	bf6080e7          	jalr	-1034(ra) # 40000a9c <__subdf3>
4200eeae:	fdff2097          	auipc	ra,0xfdff2
4200eeb2:	b86080e7          	jalr	-1146(ra) # 40000a34 <__fixdfsi>
4200eeb6:	4010                	lw	a2,0(s0)
4200eeb8:	4054                	lw	a3,4(s0)
4200eeba:	8d2a                	mv	s10,a0
4200eebc:	85e6                	mv	a1,s9
4200eebe:	8562                	mv	a0,s8
4200eec0:	fdff2097          	auipc	ra,0xfdff2
4200eec4:	bcc080e7          	jalr	-1076(ra) # 40000a8c <__muldf3>
4200eec8:	4010                	lw	a2,0(s0)
4200eeca:	4054                	lw	a3,4(s0)
4200eecc:	fdff2097          	auipc	ra,0xfdff2
4200eed0:	b4c080e7          	jalr	-1204(ra) # 40000a18 <__adddf3>
4200eed4:	fdff2097          	auipc	ra,0xfdff2
4200eed8:	b60080e7          	jalr	-1184(ra) # 40000a34 <__fixdfsi>
4200eedc:	000aa603          	lw	a2,0(s5)
4200eee0:	004aa683          	lw	a3,4(s5)
4200eee4:	c42a                	sw	a0,8(sp)
4200eee6:	4592                	lw	a1,4(sp)
4200eee8:	4502                	lw	a0,0(sp)
4200eeea:	fdff2097          	auipc	ra,0xfdff2
4200eeee:	ba2080e7          	jalr	-1118(ra) # 40000a8c <__muldf3>
4200eef2:	862a                	mv	a2,a0
4200eef4:	86ae                	mv	a3,a1
4200eef6:	4008                	lw	a0,0(s0)
4200eef8:	404c                	lw	a1,4(s0)
4200eefa:	fdff2097          	auipc	ra,0xfdff2
4200eefe:	ba2080e7          	jalr	-1118(ra) # 40000a9c <__subdf3>
4200ef02:	fdff2097          	auipc	ra,0xfdff2
4200ef06:	b32080e7          	jalr	-1230(ra) # 40000a34 <__fixdfsi>
4200ef0a:	000aa603          	lw	a2,0(s5)
4200ef0e:	004aa683          	lw	a3,4(s5)
4200ef12:	c02a                	sw	a0,0(sp)
4200ef14:	85e6                	mv	a1,s9
4200ef16:	8562                	mv	a0,s8
4200ef18:	fdff2097          	auipc	ra,0xfdff2
4200ef1c:	b74080e7          	jalr	-1164(ra) # 40000a8c <__muldf3>
4200ef20:	4010                	lw	a2,0(s0)
4200ef22:	4054                	lw	a3,4(s0)
4200ef24:	fdff2097          	auipc	ra,0xfdff2
4200ef28:	af4080e7          	jalr	-1292(ra) # 40000a18 <__adddf3>
4200ef2c:	fdff2097          	auipc	ra,0xfdff2
4200ef30:	b08080e7          	jalr	-1272(ra) # 40000a34 <__fixdfsi>
4200ef34:	4622                	lw	a2,8(sp)
4200ef36:	4582                	lw	a1,0(sp)
4200ef38:	87de                	mv	a5,s7
4200ef3a:	4711                	li	a4,4
4200ef3c:	86ea                	mv	a3,s10
4200ef3e:	f95fe0ef          	jal	4200ded2 <thick_line>
4200ef42:	0b05                	addi	s6,s6,1
4200ef44:	47b1                	li	a5,12
4200ef46:	eefb19e3          	bne	s6,a5,4200ee38 <factory_draw_dial+0x2c4>
4200ef4a:	3fcaf9b7          	lui	s3,0x3fcaf
4200ef4e:	02410913          	addi	s2,sp,36
4200ef52:	4401                	li	s0,0
4200ef54:	04410c13          	addi	s8,sp,68
4200ef58:	03810b93          	addi	s7,sp,56
4200ef5c:	02c10b13          	addi	s6,sp,44
4200ef60:	74c98993          	addi	s3,s3,1868 # 3fcaf74c <previous.0>
4200ef64:	4ab1                	li	s5,12
4200ef66:	008c07b3          	add	a5,s8,s0
4200ef6a:	0007aa03          	lw	s4,0(a5)
4200ef6e:	008b87b3          	add	a5,s7,s0
4200ef72:	4394                	lw	a3,0(a5)
4200ef74:	008b07b3          	add	a5,s6,s0
4200ef78:	00095703          	lhu	a4,0(s2)
4200ef7c:	4390                	lw	a2,0(a5)
4200ef7e:	8552                	mv	a0,s4
4200ef80:	c83a                	sw	a4,16(sp)
4200ef82:	c436                	sw	a3,8(sp)
4200ef84:	c032                	sw	a2,0(sp)
4200ef86:	fdff2097          	auipc	ra,0xfdff2
4200ef8a:	aa6080e7          	jalr	-1370(ra) # 40000a2c <__extendsfdf2>
4200ef8e:	4742                	lw	a4,16(sp)
4200ef90:	46a2                	lw	a3,8(sp)
4200ef92:	4602                	lw	a2,0(sp)
4200ef94:	0909                	addi	s2,s2,2
4200ef96:	848ff0ef          	jal	4200dfde <hand>
4200ef9a:	013407b3          	add	a5,s0,s3
4200ef9e:	0147a023          	sw	s4,0(a5)
4200efa2:	0411                	addi	s0,s0,4
4200efa4:	fd5411e3          	bne	s0,s5,4200ef66 <factory_draw_dial+0x3f2>
4200efa8:	6441                	lui	s0,0x10
4200efaa:	c8c5                	beqz	s1,4200f05a <factory_draw_dial+0x4e6>
4200efac:	3c0b4637          	lui	a2,0x3c0b4
4200efb0:	4801                	li	a6,0
4200efb2:	4781                	li	a5,0
4200efb4:	fff40713          	addi	a4,s0,-1 # ffff <CSR_UINTSTATUS+0xf34e>
4200efb8:	02000693          	li	a3,32
4200efbc:	c1860613          	addi	a2,a2,-1000 # 3c0b3c18 <_esp_libc_clock_array_end+0x3ac8>
4200efc0:	4581                	li	a1,0
4200efc2:	06800513          	li	a0,104
4200efc6:	c21fe0ef          	jal	4200dbe6 <display_factory_text>
4200efca:	3c0b4637          	lui	a2,0x3c0b4
4200efce:	4801                	li	a6,0
4200efd0:	4781                	li	a5,0
4200efd2:	fff40713          	addi	a4,s0,-1
4200efd6:	02000693          	li	a3,32
4200efda:	c1c60613          	addi	a2,a2,-996 # 3c0b3c1c <_esp_libc_clock_array_end+0x3acc>
4200efde:	06800593          	li	a1,104
4200efe2:	4501                	li	a0,0
4200efe4:	c03fe0ef          	jal	4200dbe6 <display_factory_text>
4200efe8:	3c0b3637          	lui	a2,0x3c0b3
4200efec:	4801                	li	a6,0
4200efee:	4781                	li	a5,0
4200eff0:	fff40713          	addi	a4,s0,-1
4200eff4:	02000693          	li	a3,32
4200eff8:	ff460613          	addi	a2,a2,-12 # 3c0b2ff4 <_esp_libc_clock_array_end+0x2ea4>
4200effc:	06800593          	li	a1,104
4200f000:	0e000513          	li	a0,224
4200f004:	be3fe0ef          	jal	4200dbe6 <display_factory_text>
4200f008:	3c0c3637          	lui	a2,0x3c0c3
4200f00c:	4801                	li	a6,0
4200f00e:	4781                	li	a5,0
4200f010:	fff40713          	addi	a4,s0,-1
4200f014:	02000693          	li	a3,32
4200f018:	aac60613          	addi	a2,a2,-1364 # 3c0c2aac <_esp_libc_clock_array_end+0x1295c>
4200f01c:	0d000593          	li	a1,208
4200f020:	06800513          	li	a0,104
4200f024:	bc3fe0ef          	jal	4200dbe6 <display_factory_text>
4200f028:	442a                	lw	s0,136(sp)
4200f02a:	40ba                	lw	ra,140(sp)
4200f02c:	449a                	lw	s1,132(sp)
4200f02e:	490a                	lw	s2,128(sp)
4200f030:	59f6                	lw	s3,124(sp)
4200f032:	5a66                	lw	s4,120(sp)
4200f034:	5ad6                	lw	s5,116(sp)
4200f036:	5b46                	lw	s6,112(sp)
4200f038:	5bb6                	lw	s7,108(sp)
4200f03a:	5c26                	lw	s8,104(sp)
4200f03c:	5c96                	lw	s9,100(sp)
4200f03e:	5d06                	lw	s10,96(sp)
4200f040:	866e                	mv	a2,s11
4200f042:	4df6                	lw	s11,92(sp)
4200f044:	6741                	lui	a4,0x10
4200f046:	4805                	li	a6,1
4200f048:	4781                	li	a5,0
4200f04a:	177d                	addi	a4,a4,-1 # ffff <CSR_UINTSTATUS+0xf34e>
4200f04c:	46c1                	li	a3,16
4200f04e:	0e100593          	li	a1,225
4200f052:	4515                	li	a0,5
4200f054:	6149                	addi	sp,sp,144
4200f056:	b91fe06f          	j	4200dbe6 <display_factory_text>
4200f05a:	07800593          	li	a1,120
4200f05e:	fff40693          	addi	a3,s0,-1
4200f062:	4619                	li	a2,6
4200f064:	852e                	mv	a0,a1
4200f066:	cf1fe0ef          	jal	4200dd56 <circle>
4200f06a:	bf7d                	j	4200f028 <factory_draw_dial+0x4b4>
