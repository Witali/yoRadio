
small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200d28e <clock_task>:
4200d28e:	c5010113          	addi	sp,sp,-944
4200d292:	39812423          	sw	s8,904(sp)
4200d296:	0ff00793          	li	a5,255
4200d29a:	3fcafc37          	lui	s8,0x3fcaf
4200d29e:	3b212023          	sw	s2,928(sp)
4200d2a2:	39312e23          	sw	s3,924(sp)
4200d2a6:	39512a23          	sw	s5,916(sp)
4200d2aa:	39712623          	sw	s7,908(sp)
4200d2ae:	39912223          	sw	s9,900(sp)
4200d2b2:	39a12023          	sw	s10,896(sp)
4200d2b6:	37b12e23          	sw	s11,892(sp)
4200d2ba:	3a112623          	sw	ra,940(sp)
4200d2be:	3a812423          	sw	s0,936(sp)
4200d2c2:	3a912223          	sw	s1,932(sp)
4200d2c6:	39412c23          	sw	s4,920(sp)
4200d2ca:	39612823          	sw	s6,912(sp)
4200d2ce:	04010223          	sb	zero,68(sp)
4200d2d2:	04011423          	sh	zero,72(sp)
4200d2d6:	4b81                	li	s7,0
4200d2d8:	d202                	sw	zero,36(sp)
4200d2da:	4d01                	li	s10,0
4200d2dc:	d002                	sw	zero,32(sp)
4200d2de:	ce3e                	sw	a5,28(sp)
4200d2e0:	cc02                	sw	zero,24(sp)
4200d2e2:	4901                	li	s2,0
4200d2e4:	d402                	sw	zero,40(sp)
4200d2e6:	4c81                	li	s9,0
4200d2e8:	4981                	li	s3,0
4200d2ea:	ca02                	sw	zero,20(sp)
4200d2ec:	4a81                	li	s5,0
4200d2ee:	4d85                	li	s11,1
4200d2f0:	73cc0c13          	addi	s8,s8,1852 # 3fcaf73c <timer_state>
4200d2f4:	0448                	addi	a0,sp,516
4200d2f6:	99aff0ef          	jal	4200c490 <settings_snapshot>
4200d2fa:	0228                	addi	a0,sp,264
4200d2fc:	65d030ef          	jal	42011158 <weather_snapshot>
4200d300:	35114603          	lbu	a2,849(sp)
4200d304:	4581                	li	a1,0
4200d306:	00e8                	addi	a0,sp,76
4200d308:	f27ff0ef          	jal	4200d22e <timer_snapshot>
4200d30c:	05a14483          	lbu	s1,90(sp)
4200d310:	6f7020ef          	jal	42010206 <network_connected>
4200d314:	45d1                	li	a1,20
4200d316:	8b2a                	mv	s6,a0
4200d318:	1168                	addi	a0,sp,172
4200d31a:	721020ef          	jal	4201023a <network_address>
4200d31e:	4501                	li	a0,0
4200d320:	74d8f0ef          	jal	4209d26c <time>
4200d324:	c82e                	sw	a1,16(sp)
4200d326:	4642                	lw	a2,16(sp)
4200d328:	c62a                	sw	a0,12(sp)
4200d32a:	85aa                	mv	a1,a0
4200d32c:	11d4                	addi	a3,sp,228
4200d32e:	2ab10513          	addi	a0,sp,683
4200d332:	4f2030ef          	jal	42010824 <services_local_time>
4200d336:	8a2a                	mv	s4,a0
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
4200d37e:	00aa9e63          	bne	s5,a0,4200d39a <clock_task+0x10c>
4200d382:	47d2                	lw	a5,20(sp)
4200d384:	1f812403          	lw	s0,504(sp)
4200d388:	8c1d                	sub	s0,s0,a5
4200d38a:	5792                	lw	a5,36(sp)
4200d38c:	00803433          	snez	s0,s0
4200d390:	0147c7b3          	xor	a5,a5,s4
4200d394:	8c5d                	or	s0,s0,a5
4200d396:	0ff47413          	zext.b	s0,s0
4200d39a:	000b0d63          	beqz	s6,4200d3b4 <clock_task+0x126>
4200d39e:	10814783          	lbu	a5,264(sp)
4200d3a2:	eb89                	bnez	a5,4200d3b4 <clock_task+0x126>
4200d3a4:	63b030ef          	jal	420111de <weather_request_active>
4200d3a8:	e511                	bnez	a0,4200d3b4 <clock_task+0x126>
4200d3aa:	000b9c63          	bnez	s7,4200d3c2 <clock_task+0x134>
4200d3ae:	5ef030ef          	jal	4201119c <weather_request_update>
4200d3b2:	4bf9                	li	s7,30
4200d3b4:	036020ef          	jal	4200f3ea <media_upload_active>
4200d3b8:	c519                	beqz	a0,4200d3c6 <clock_task+0x138>
4200d3ba:	4529                	li	a0,10
4200d3bc:	2fb9f0ef          	jal	420aceb6 <vTaskDelay>
4200d3c0:	bf15                	j	4200d2f4 <clock_task+0x66>
4200d3c2:	1bfd                	addi	s7,s7,-1
4200d3c4:	bfc5                	j	4200d3b4 <clock_task+0x126>
4200d3c6:	e095                	bnez	s1,4200d3ea <clock_task+0x15c>
4200d3c8:	617030ef          	jal	420111de <weather_request_active>
4200d3cc:	84aa                	mv	s1,a0
4200d3ce:	f575                	bnez	a0,4200d3ba <clock_task+0x12c>
4200d3d0:	080b1163          	bnez	s6,4200d452 <clock_task+0x1c4>
4200d3d4:	64d020ef          	jal	42010220 <network_ap_active>
4200d3d8:	18050b63          	beqz	a0,4200d56e <clock_task+0x2e0>
4200d3dc:	4409                	li	s0,2
4200d3de:	04890163          	beq	s2,s0,4200d420 <clock_task+0x192>
4200d3e2:	60f000ef          	jal	4200e1f0 <factory_draw_setup>
4200d3e6:	8922                	mv	s2,s0
4200d3e8:	a825                	j	4200d420 <clock_task+0x192>
4200d3ea:	05914403          	lbu	s0,89(sp)
4200d3ee:	47e2                	lw	a5,24(sp)
4200d3f0:	197d                	addi	s2,s2,-1
4200d3f2:	01203933          	snez	s2,s2
4200d3f6:	8f81                	sub	a5,a5,s0
4200d3f8:	00f037b3          	snez	a5,a5
4200d3fc:	0127e7b3          	or	a5,a5,s2
4200d400:	ef9d                	bnez	a5,4200d43e <clock_task+0x1b0>
4200d402:	5782                	lw	a5,32(sp)
4200d404:	0167c7b3          	xor	a5,a5,s6
4200d408:	0ff7f793          	zext.b	a5,a5
4200d40c:	eb8d                	bnez	a5,4200d43e <clock_task+0x1b0>
4200d40e:	35114603          	lbu	a2,849(sp)
4200d412:	08000593          	li	a1,128
4200d416:	1808                	addi	a0,sp,48
4200d418:	e17ff0ef          	jal	4200d22e <timer_snapshot>
4200d41c:	4905                	li	s2,1
4200d41e:	cc22                	sw	s0,24(sp)
4200d420:	1f812783          	lw	a5,504(sp)
4200d424:	4529                	li	a0,10
4200d426:	10814d03          	lbu	s10,264(sp)
4200d42a:	ca3e                	sw	a5,20(sp)
4200d42c:	28b9f0ef          	jal	420aceb6 <vTaskDelay>
4200d430:	47b2                	lw	a5,12(sp)
4200d432:	4cc2                	lw	s9,16(sp)
4200d434:	5ab2                	lw	s5,44(sp)
4200d436:	d252                	sw	s4,36(sp)
4200d438:	d05a                	sw	s6,32(sp)
4200d43a:	d43e                	sw	a5,40(sp)
4200d43c:	bd65                	j	4200d2f4 <clock_task+0x66>
4200d43e:	01603533          	snez	a0,s6
4200d442:	117c                	addi	a5,sp,172
4200d444:	40a00533          	neg	a0,a0
4200d448:	85a2                	mv	a1,s0
4200d44a:	8d7d                	and	a0,a0,a5
4200d44c:	63b000ef          	jal	4200e286 <factory_draw_startup>
4200d450:	bf7d                	j	4200d40e <clock_task+0x180>
4200d452:	478d                	li	a5,3
4200d454:	00f91763          	bne	s2,a5,4200d462 <clock_task+0x1d4>
4200d458:	34c14783          	lbu	a5,844(sp)
4200d45c:	4772                	lw	a4,28(sp)
4200d45e:	04e78b63          	beq	a5,a4,4200d4b4 <clock_task+0x226>
4200d462:	0f000693          	li	a3,240
4200d466:	4701                	li	a4,0
4200d468:	8636                	mv	a2,a3
4200d46a:	4581                	li	a1,0
4200d46c:	4501                	li	a0,0
4200d46e:	f86ff0ef          	jal	4200cbf4 <display_fill>
4200d472:	34c14703          	lbu	a4,844(sp)
4200d476:	4789                	li	a5,2
4200d478:	442d                	li	s0,11
4200d47a:	00f71363          	bne	a4,a5,4200d480 <clock_task+0x1f2>
4200d47e:	443d                	li	s0,15
4200d480:	fe37b097          	auipc	ra,0xfe37b
4200d484:	9b6080e7          	jalr	-1610(ra) # 40387e36 <vPortEnterCritical>
4200d488:	004c2783          	lw	a5,4(s8)
4200d48c:	8fc1                	or	a5,a5,s0
4200d48e:	00fc2223          	sw	a5,4(s8)
4200d492:	fe37b097          	auipc	ra,0xfe37b
4200d496:	9d0080e7          	jalr	-1584(ra) # 40387e62 <vPortExitCritical>
4200d49a:	34c14783          	lbu	a5,844(sp)
4200d49e:	00fde863          	bltu	s11,a5,4200d4ae <clock_task+0x220>
4200d4a2:	461e                	lw	a2,196(sp)
4200d4a4:	45ae                	lw	a1,200(sp)
4200d4a6:	86d2                	mv	a3,s4
4200d4a8:	0448                	addi	a0,sp,516
4200d4aa:	d37ff0ef          	jal	4200d1e0 <backlight_update>
4200d4ae:	4485                	li	s1,1
4200d4b0:	8426                	mv	s0,s1
4200d4b2:	4981                	li	s3,0
4200d4b4:	10814783          	lbu	a5,264(sp)
4200d4b8:	c399                	beqz	a5,4200d4be <clock_task+0x230>
4200d4ba:	000d1363          	bnez	s10,4200d4c0 <clock_task+0x232>
4200d4be:	4981                	li	s3,0
4200d4c0:	34c14783          	lbu	a5,844(sp)
4200d4c4:	eb91                	bnez	a5,4200d4d8 <clock_task+0x24a>
4200d4c6:	c8c5                	beqz	s1,4200d576 <clock_task+0x2e8>
4200d4c8:	35114603          	lbu	a2,849(sp)
4200d4cc:	4589                	li	a1,2
4200d4ce:	08e8                	addi	a0,sp,92
4200d4d0:	d5fff0ef          	jal	4200d22e <timer_snapshot>
4200d4d4:	5786                	lw	a5,96(sp)
4200d4d6:	e7c5                	bnez	a5,4200d57e <clock_task+0x2f0>
4200d4d8:	34c14783          	lbu	a5,844(sp)
4200d4dc:	0c079c63          	bnez	a5,4200d5b4 <clock_task+0x326>
4200d4e0:	34d14503          	lbu	a0,845(sp)
4200d4e4:	044020ef          	jal	4200f528 <media_animation_frames>
4200d4e8:	85aa                	mv	a1,a0
4200d4ea:	00c8                	addi	a0,sp,68
4200d4ec:	2e71                	jal	4200d888 <factory_animation_next>
4200d4ee:	35114603          	lbu	a2,849(sp)
4200d4f2:	892a                	mv	s2,a0
4200d4f4:	45a1                	li	a1,8
4200d4f6:	10e8                	addi	a0,sp,108
4200d4f8:	d37ff0ef          	jal	4200d22e <timer_snapshot>
4200d4fc:	4732                	lw	a4,12(sp)
4200d4fe:	57a2                	lw	a5,40(sp)
4200d500:	5846                	lw	a6,112(sp)
4200d502:	8fb9                	xor	a5,a5,a4
4200d504:	4742                	lw	a4,16(sp)
4200d506:	01003833          	snez	a6,a6
4200d50a:	00ecc733          	xor	a4,s9,a4
4200d50e:	8fd9                	or	a5,a5,a4
4200d510:	00f037b3          	snez	a5,a5
4200d514:	00f867b3          	or	a5,a6,a5
4200d518:	e391                	bnez	a5,4200d51c <clock_task+0x28e>
4200d51a:	c051                	beqz	s0,4200d59e <clock_task+0x310>
4200d51c:	fff94713          	not	a4,s2
4200d520:	877d                	srai	a4,a4,0x1f
4200d522:	87a6                	mv	a5,s1
4200d524:	00e97733          	and	a4,s2,a4
4200d528:	86ce                	mv	a3,s3
4200d52a:	0230                	addi	a2,sp,264
4200d52c:	018c                	addi	a1,sp,192
4200d52e:	0448                	addi	a0,sp,516
4200d530:	61f000ef          	jal	4200e34e <factory_draw_classic>
4200d534:	41f000ef          	jal	4200e152 <factory_scroll_tick>
4200d538:	34c14703          	lbu	a4,844(sp)
4200d53c:	4789                	li	a5,2
4200d53e:	00f70863          	beq	a4,a5,4200d54e <clock_task+0x2c0>
4200d542:	461e                	lw	a2,196(sp)
4200d544:	45ae                	lw	a1,200(sp)
4200d546:	86d2                	mv	a3,s4
4200d548:	0448                	addi	a0,sp,516
4200d54a:	c97ff0ef          	jal	4200d1e0 <backlight_update>
4200d54e:	34c14783          	lbu	a5,844(sp)
4200d552:	35114603          	lbu	a2,849(sp)
4200d556:	04000593          	li	a1,64
4200d55a:	0968                	addi	a0,sp,156
4200d55c:	ce3e                	sw	a5,28(sp)
4200d55e:	cd1ff0ef          	jal	4200d22e <timer_snapshot>
4200d562:	578a                	lw	a5,160(sp)
4200d564:	c399                	beqz	a5,4200d56a <clock_task+0x2dc>
4200d566:	437030ef          	jal	4201119c <weather_request_update>
4200d56a:	490d                	li	s2,3
4200d56c:	bd55                	j	4200d420 <clock_task+0x192>
4200d56e:	478d                	li	a5,3
4200d570:	eaf918e3          	bne	s2,a5,4200d420 <clock_task+0x192>
4200d574:	b5d5                	j	4200d458 <clock_task+0x1ca>
4200d576:	459000ef          	jal	4200e1ce <factory_scroll_description_ready>
4200d57a:	f539                	bnez	a0,4200d4c8 <clock_task+0x23a>
4200d57c:	bfb1                	j	4200d4d8 <clock_task+0x24a>
4200d57e:	e891                	bnez	s1,4200d592 <clock_task+0x304>
4200d580:	10814783          	lbu	a5,264(sp)
4200d584:	c799                	beqz	a5,4200d592 <clock_task+0x304>
4200d586:	000d0663          	beqz	s10,4200d592 <clock_task+0x304>
4200d58a:	0985                	addi	s3,s3,1
4200d58c:	47a9                	li	a5,10
4200d58e:	02f9f9b3          	remu	s3,s3,a5
4200d592:	f039                	bnez	s0,4200d4d8 <clock_task+0x24a>
4200d594:	34c14403          	lbu	s0,844(sp)
4200d598:	00143413          	seqz	s0,s0
4200d59c:	bf35                	j	4200d4d8 <clock_task+0x24a>
4200d59e:	f8094be3          	bltz	s2,4200d534 <clock_task+0x2a6>
4200d5a2:	34d14503          	lbu	a0,845(sp)
4200d5a6:	0a000693          	li	a3,160
4200d5aa:	8636                	mv	a2,a3
4200d5ac:	85ca                	mv	a1,s2
4200d5ae:	7d5010ef          	jal	4200f582 <media_draw_animation>
4200d5b2:	b749                	j	4200d534 <clock_task+0x2a6>
4200d5b4:	03b79463          	bne	a5,s11,4200d5dc <clock_task+0x34e>
4200d5b8:	35114603          	lbu	a2,849(sp)
4200d5bc:	18e8                	addi	a0,sp,124
4200d5be:	45a5                	li	a1,9
4200d5c0:	c6fff0ef          	jal	4200d22e <timer_snapshot>
4200d5c4:	470a                	lw	a4,128(sp)
4200d5c6:	86a6                	mv	a3,s1
4200d5c8:	1170                	addi	a2,sp,172
4200d5ca:	00375793          	srli	a5,a4,0x3
4200d5ce:	8b85                	andi	a5,a5,1
4200d5d0:	8b05                	andi	a4,a4,1
4200d5d2:	018c                	addi	a1,sp,192
4200d5d4:	0448                	addi	a0,sp,516
4200d5d6:	382010ef          	jal	4200e958 <factory_draw_simple>
4200d5da:	bfb9                	j	4200d538 <clock_task+0x2aa>
4200d5dc:	4709                	li	a4,2
4200d5de:	0ae79163          	bne	a5,a4,4200d680 <clock_task+0x3f2>
4200d5e2:	0458                	addi	a4,sp,516
4200d5e4:	4781                	li	a5,0
4200d5e6:	4601                	li	a2,0
4200d5e8:	4695                	li	a3,5
4200d5ea:	15872583          	lw	a1,344(a4)
4200d5ee:	c581                	beqz	a1,4200d5f6 <clock_task+0x368>
4200d5f0:	00fd95b3          	sll	a1,s11,a5
4200d5f4:	8e4d                	or	a2,a2,a1
4200d5f6:	0785                	addi	a5,a5,1
4200d5f8:	0711                	addi	a4,a4,4
4200d5fa:	fed798e3          	bne	a5,a3,4200d5ea <clock_task+0x35c>
4200d5fe:	46c6                	lw	a3,80(sp)
4200d600:	35814583          	lbu	a1,856(sp)
4200d604:	11dc                	addi	a5,sp,228
4200d606:	8289                	srli	a3,a3,0x2
4200d608:	8a85                	andi	a3,a3,1
4200d60a:	8ec5                	or	a3,a3,s1
4200d60c:	4701                	li	a4,0
4200d60e:	0ff6f693          	zext.b	a3,a3
4200d612:	00a8                	addi	a0,sp,72
4200d614:	2ac9                	jal	4200d7e6 <factory_photo_step>
4200d616:	0e714783          	lbu	a5,231(sp)
4200d61a:	c789                	beqz	a5,4200d624 <clock_task+0x396>
4200d61c:	0e415503          	lhu	a0,228(sp)
4200d620:	aefff0ef          	jal	4200d10e <backlight_set_level>
4200d624:	0e610503          	lb	a0,230(sp)
4200d628:	57fd                	li	a5,-1
4200d62a:	02f54663          	blt	a0,a5,4200d656 <clock_task+0x3c8>
4200d62e:	04f51563          	bne	a0,a5,4200d678 <clock_task+0x3ea>
4200d632:	0f000693          	li	a3,240
4200d636:	8636                	mv	a2,a3
4200d638:	4701                	li	a4,0
4200d63a:	4581                	li	a1,0
4200d63c:	4501                	li	a0,0
4200d63e:	db6ff0ef          	jal	4200cbf4 <display_fill>
4200d642:	6741                	lui	a4,0x10
4200d644:	4805                	li	a6,1
4200d646:	4781                	li	a5,0
4200d648:	177d                	addi	a4,a4,-1 # ffff <CSR_UINTSTATUS+0xf34e>
4200d64a:	46c1                	li	a3,16
4200d64c:	1170                	addi	a2,sp,172
4200d64e:	0e100593          	li	a1,225
4200d652:	4515                	li	a0,5
4200d654:	2b61                	jal	4200dbec <display_factory_text>
4200d656:	0e814783          	lbu	a5,232(sp)
4200d65a:	ec078fe3          	beqz	a5,4200d538 <clock_task+0x2aa>
4200d65e:	35114603          	lbu	a2,849(sp)
4200d662:	1808                	addi	a0,sp,48
4200d664:	4591                	li	a1,4
4200d666:	bc9ff0ef          	jal	4200d22e <timer_snapshot>
4200d66a:	461e                	lw	a2,196(sp)
4200d66c:	45ae                	lw	a1,200(sp)
4200d66e:	86d2                	mv	a3,s4
4200d670:	0448                	addi	a0,sp,516
4200d672:	b6fff0ef          	jal	4200d1e0 <backlight_update>
4200d676:	b5c9                	j	4200d538 <clock_task+0x2aa>
4200d678:	116c                	addi	a1,sp,172
4200d67a:	1f9010ef          	jal	4200f072 <factory_draw_photo>
4200d67e:	bfe1                	j	4200d656 <clock_task+0x3c8>
4200d680:	35114603          	lbu	a2,849(sp)
4200d684:	4585                	li	a1,1
4200d686:	0168                	addi	a0,sp,140
4200d688:	ba7ff0ef          	jal	4200d22e <timer_snapshot>
4200d68c:	47ca                	lw	a5,144(sp)
4200d68e:	00f037b3          	snez	a5,a5
4200d692:	8fc5                	or	a5,a5,s1
4200d694:	0ff7f793          	zext.b	a5,a5
4200d698:	e399                	bnez	a5,4200d69e <clock_task+0x410>
4200d69a:	e8040fe3          	beqz	s0,4200d538 <clock_task+0x2aa>
4200d69e:	8626                	mv	a2,s1
4200d6a0:	116c                	addi	a1,sp,172
4200d6a2:	0188                	addi	a0,sp,192
4200d6a4:	4d6010ef          	jal	4200eb7a <factory_draw_dial>
4200d6a8:	bd41                	j	4200d538 <clock_task+0x2aa>


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200fc42 <wifi_event>:
4200fc42:	3c1087b7          	lui	a5,0x3c108
4200fc46:	01c7a783          	lw	a5,28(a5) # 3c10801c <IP_EVENT>
4200fc4a:	02b79e63          	bne	a5,a1,4200fc86 <wifi_event+0x44>
4200fc4e:	ee05                	bnez	a2,4200fc86 <wifi_event+0x44>
4200fc50:	cef1                	beqz	a3,4200fd2c <wifi_event+0xea>
4200fc52:	42d8                	lw	a4,4(a3)
4200fc54:	3fcb47b7          	lui	a5,0x3fcb4
4200fc58:	91478793          	addi	a5,a5,-1772 # 3fcb3914 <last_station_address>
4200fc5c:	0310000f          	fence	rw,w
4200fc60:	c398                	sw	a4,0(a5)
4200fc62:	0330000f          	fence	rw,rw
4200fc66:	3fcb47b7          	lui	a5,0x3fcb4
4200fc6a:	4705                	li	a4,1
4200fc6c:	91c78793          	addi	a5,a5,-1764 # 3fcb391c <connected>
4200fc70:	0310000f          	fence	rw,w
4200fc74:	00e78023          	sb	a4,0(a5)
4200fc78:	0330000f          	fence	rw,rw
4200fc7c:	3fcb47b7          	lui	a5,0x3fcb4
4200fc80:	9007a623          	sw	zero,-1780(a5) # 3fcb390c <station_retries>
4200fc84:	8082                	ret
4200fc86:	3c1087b7          	lui	a5,0x3c108
4200fc8a:	0a07a783          	lw	a5,160(a5) # 3c1080a0 <WIFI_EVENT>
4200fc8e:	08b79f63          	bne	a5,a1,4200fd2c <wifi_event+0xea>
4200fc92:	4795                	li	a5,5
4200fc94:	08f61463          	bne	a2,a5,4200fd1c <wifi_event+0xda>
4200fc98:	3fcb47b7          	lui	a5,0x3fcb4
4200fc9c:	91c78793          	addi	a5,a5,-1764 # 3fcb391c <connected>
4200fca0:	0310000f          	fence	rw,w
4200fca4:	00078023          	sb	zero,0(a5)
4200fca8:	0330000f          	fence	rw,rw
4200fcac:	3fcb46b7          	lui	a3,0x3fcb4
4200fcb0:	9106c783          	lbu	a5,-1776(a3) # 3fcb3910 <station_configured>
4200fcb4:	cfa5                	beqz	a5,4200fd2c <wifi_event+0xea>
4200fcb6:	3fcb4737          	lui	a4,0x3fcb4
4200fcba:	91a70793          	addi	a5,a4,-1766 # 3fcb391a <scanning>
4200fcbe:	0330000f          	fence	rw,rw
4200fcc2:	00078783          	lb	a5,0(a5)
4200fcc6:	0230000f          	fence	r,rw
4200fcca:	0ff7f793          	zext.b	a5,a5
4200fcce:	ef89                	bnez	a5,4200fce8 <wifi_event+0xa6>
4200fcd0:	3fcb4637          	lui	a2,0x3fcb4
4200fcd4:	90c62783          	lw	a5,-1780(a2) # 3fcb390c <station_retries>
4200fcd8:	458d                	li	a1,3
4200fcda:	00f5e763          	bltu	a1,a5,4200fce8 <wifi_event+0xa6>
4200fcde:	0785                	addi	a5,a5,1
4200fce0:	90f62623          	sw	a5,-1780(a2)
4200fce4:	3062406f          	j	42033fea <esp_wifi_connect>
4200fce8:	9106c783          	lbu	a5,-1776(a3)
4200fcec:	c3a1                	beqz	a5,4200fd2c <wifi_event+0xea>
4200fcee:	91a70793          	addi	a5,a4,-1766
4200fcf2:	0330000f          	fence	rw,rw
4200fcf6:	00078783          	lb	a5,0(a5)
4200fcfa:	0230000f          	fence	r,rw
4200fcfe:	0ff7f793          	zext.b	a5,a5
4200fd02:	e78d                	bnez	a5,4200fd2c <wifi_event+0xea>
4200fd04:	3fcb47b7          	lui	a5,0x3fcb4
4200fd08:	4705                	li	a4,1
4200fd0a:	91878793          	addi	a5,a5,-1768 # 3fcb3918 <station_failed>
4200fd0e:	0310000f          	fence	rw,w
4200fd12:	00e78023          	sb	a4,0(a5)
4200fd16:	0330000f          	fence	rw,rw
4200fd1a:	8082                	ret
4200fd1c:	4789                	li	a5,2
4200fd1e:	00f61763          	bne	a2,a5,4200fd2c <wifi_event+0xea>
4200fd22:	3fcb47b7          	lui	a5,0x3fcb4
4200fd26:	9107c783          	lbu	a5,-1776(a5) # 3fcb3910 <station_configured>
4200fd2a:	ffcd                	bnez	a5,4200fce4 <wifi_event+0xa2>
4200fd2c:	8082                	ret


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4201023a <network_address>:
4201023a:	1101                	addi	sp,sp,-32
4201023c:	ca26                	sw	s1,20(sp)
4201023e:	ce06                	sw	ra,28(sp)
42010240:	cc22                	sw	s0,24(sp)
42010242:	84aa                	mv	s1,a0
42010244:	c62e                	sw	a1,12(sp)
42010246:	3fcb47b7          	lui	a5,0x3fcb4
4201024a:	91478793          	addi	a5,a5,-1772 # 3fcb3914 <last_station_address>
4201024e:	0330000f          	fence	rw,rw
42010252:	4380                	lw	s0,0(a5)
42010254:	0230000f          	fence	r,rw
42010258:	fc9ff0ef          	jal	42010220 <network_ap_active>
4201025c:	45b2                	lw	a1,12(sp)
4201025e:	cc0d                	beqz	s0,42010298 <network_address+0x5e>
42010260:	00154513          	xori	a0,a0,1
42010264:	0ff57513          	zext.b	a0,a0
42010268:	c905                	beqz	a0,42010298 <network_address+0x5e>
4201026a:	01045793          	srli	a5,s0,0x10
4201026e:	00845713          	srli	a4,s0,0x8
42010272:	01845813          	srli	a6,s0,0x18
42010276:	0ff47693          	zext.b	a3,s0
4201027a:	4462                	lw	s0,24(sp)
4201027c:	40f2                	lw	ra,28(sp)
4201027e:	8526                	mv	a0,s1
42010280:	44d2                	lw	s1,20(sp)
42010282:	3c0b4637          	lui	a2,0x3c0b4
42010286:	0ff7f793          	zext.b	a5,a5
4201028a:	0ff77713          	zext.b	a4,a4
4201028e:	fa460613          	addi	a2,a2,-92 # 3c0b3fa4 <_esp_libc_clock_array_end+0x3e54>
42010292:	6105                	addi	sp,sp,32
42010294:	3c98d06f          	j	4209de5c <snprintf>
42010298:	4462                	lw	s0,24(sp)
4201029a:	40f2                	lw	ra,28(sp)
4201029c:	8526                	mv	a0,s1
4201029e:	44d2                	lw	s1,20(sp)
420102a0:	3c0b4637          	lui	a2,0x3c0b4
420102a4:	b6860613          	addi	a2,a2,-1176 # 3c0b3b68 <_esp_libc_clock_array_end+0x3a18>
420102a8:	6105                	addi	sp,sp,32
420102aa:	3b38d06f          	j	4209de5c <snprintf>
