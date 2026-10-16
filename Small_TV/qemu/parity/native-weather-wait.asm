
small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200d28e <clock_task>:
4200d28e:	c6010113          	addi	sp,sp,-928
4200d292:	37812c23          	sw	s8,888(sp)
4200d296:	0ff00793          	li	a5,255
4200d29a:	3fcafc37          	lui	s8,0x3fcaf
4200d29e:	38912a23          	sw	s1,916(sp)
4200d2a2:	39212823          	sw	s2,912(sp)
4200d2a6:	39312623          	sw	s3,908(sp)
4200d2aa:	39512223          	sw	s5,900(sp)
4200d2ae:	37712e23          	sw	s7,892(sp)
4200d2b2:	37912a23          	sw	s9,884(sp)
4200d2b6:	37a12823          	sw	s10,880(sp)
4200d2ba:	37b12623          	sw	s11,876(sp)
4200d2be:	38112e23          	sw	ra,924(sp)
4200d2c2:	38812c23          	sw	s0,920(sp)
4200d2c6:	39412423          	sw	s4,904(sp)
4200d2ca:	39612023          	sw	s6,896(sp)
4200d2ce:	02010a23          	sb	zero,52(sp)
4200d2d2:	02011c23          	sh	zero,56(sp)
4200d2d6:	4b81                	li	s7,0
4200d2d8:	ca02                	sw	zero,20(sp)
4200d2da:	4d01                	li	s10,0
4200d2dc:	c802                	sw	zero,16(sp)
4200d2de:	c63e                	sw	a5,12(sp)
4200d2e0:	c402                	sw	zero,8(sp)
4200d2e2:	4481                	li	s1,0
4200d2e4:	cc02                	sw	zero,24(sp)
4200d2e6:	4c81                	li	s9,0
4200d2e8:	4981                	li	s3,0
4200d2ea:	4901                	li	s2,0
4200d2ec:	4a81                	li	s5,0
4200d2ee:	4d85                	li	s11,1
4200d2f0:	73cc0c13          	addi	s8,s8,1852 # 3fcaf73c <timer_state>
4200d2f4:	1bc8                	addi	a0,sp,500
4200d2f6:	99aff0ef          	jal	4200c490 <settings_snapshot>
4200d2fa:	19a8                	addi	a0,sp,248
4200d2fc:	64b030ef          	jal	42011146 <weather_snapshot>
4200d300:	34114603          	lbu	a2,833(sp)
4200d304:	4581                	li	a1,0
4200d306:	1868                	addi	a0,sp,60
4200d308:	f27ff0ef          	jal	4200d22e <timer_snapshot>
4200d30c:	6e9020ef          	jal	420101f4 <network_connected>
4200d310:	45d1                	li	a1,20
4200d312:	8b2a                	mv	s6,a0
4200d314:	0968                	addi	a0,sp,156
4200d316:	713020ef          	jal	42010228 <network_address>
4200d31a:	4501                	li	a0,0
4200d31c:	73f8f0ef          	jal	4209d25a <time>
4200d320:	c22e                	sw	a1,4(sp)
4200d322:	4612                	lw	a2,4(sp)
4200d324:	c02a                	sw	a0,0(sp)
4200d326:	85aa                	mv	a1,a0
4200d328:	09d4                	addi	a3,sp,212
4200d32a:	29b10513          	addi	a0,sp,667
4200d32e:	4e4030ef          	jal	42010812 <services_local_time>
4200d332:	8a2a                	mv	s4,a0
4200d334:	e50d                	bnez	a0,4200d35e <clock_task+0xd0>
4200d336:	4781                	li	a5,0
4200d338:	d9be                	sw	a5,240(sp)
4200d33a:	02800793          	li	a5,40
4200d33e:	cbbe                	sw	a5,212(sp)
4200d340:	4791                	li	a5,4
4200d342:	cdbe                	sw	a5,216(sp)
4200d344:	47c5                	li	a5,17
4200d346:	cfbe                	sw	a5,220(sp)
4200d348:	47cd                	li	a5,19
4200d34a:	d1be                	sw	a5,224(sp)
4200d34c:	47a1                	li	a5,8
4200d34e:	d3be                	sw	a5,228(sp)
4200d350:	07d00793          	li	a5,125
4200d354:	4801                	li	a6,0
4200d356:	d5be                	sw	a5,232(sp)
4200d358:	4795                	li	a5,5
4200d35a:	dbc2                	sw	a6,244(sp)
4200d35c:	d7be                	sw	a5,236(sp)
4200d35e:	02400613          	li	a2,36
4200d362:	09cc                	addi	a1,sp,212
4200d364:	1908                	addi	a0,sp,176
4200d366:	fe37a097          	auipc	ra,0xfe37a
4200d36a:	ed4080e7          	jalr	-300(ra) # 4038723a <memcpy>
4200d36e:	a86ff0ef          	jal	4200c5f4 <settings_generation>
4200d372:	ce2a                	sw	a0,28(sp)
4200d374:	4405                	li	s0,1
4200d376:	00aa9e63          	bne	s5,a0,4200d392 <clock_task+0x104>
4200d37a:	1e812403          	lw	s0,488(sp)
4200d37e:	47d2                	lw	a5,20(sp)
4200d380:	41240433          	sub	s0,s0,s2
4200d384:	00803433          	snez	s0,s0
4200d388:	0147c7b3          	xor	a5,a5,s4
4200d38c:	8c5d                	or	s0,s0,a5
4200d38e:	0ff47413          	zext.b	s0,s0
4200d392:	000b0d63          	beqz	s6,4200d3ac <clock_task+0x11e>
4200d396:	0f814783          	lbu	a5,248(sp)
4200d39a:	eb89                	bnez	a5,4200d3ac <clock_task+0x11e>
4200d39c:	631030ef          	jal	420111cc <weather_request_active>
4200d3a0:	e511                	bnez	a0,4200d3ac <clock_task+0x11e>
4200d3a2:	000b9c63          	bnez	s7,4200d3ba <clock_task+0x12c>
4200d3a6:	5e5030ef          	jal	4201118a <weather_request_update>
4200d3aa:	4bf9                	li	s7,30
4200d3ac:	02c020ef          	jal	4200f3d8 <media_upload_active>
4200d3b0:	c519                	beqz	a0,4200d3be <clock_task+0x130>
4200d3b2:	4529                	li	a0,10
4200d3b4:	2f19f0ef          	jal	420acea4 <vTaskDelay>
4200d3b8:	bf35                	j	4200d2f4 <clock_task+0x66>
4200d3ba:	1bfd                	addi	s7,s7,-1
4200d3bc:	bfc5                	j	4200d3ac <clock_task+0x11e>
4200d3be:	04a14903          	lbu	s2,74(sp)
4200d3c2:	06090363          	beqz	s2,4200d428 <clock_task+0x19a>
4200d3c6:	04914403          	lbu	s0,73(sp)
4200d3ca:	47a2                	lw	a5,8(sp)
4200d3cc:	14fd                	addi	s1,s1,-1
4200d3ce:	009034b3          	snez	s1,s1
4200d3d2:	8f81                	sub	a5,a5,s0
4200d3d4:	00f037b3          	snez	a5,a5
4200d3d8:	8fc5                	or	a5,a5,s1
4200d3da:	e799                	bnez	a5,4200d3e8 <clock_task+0x15a>
4200d3dc:	47c2                	lw	a5,16(sp)
4200d3de:	0167c7b3          	xor	a5,a5,s6
4200d3e2:	0ff7f793          	zext.b	a5,a5
4200d3e6:	cb91                	beqz	a5,4200d3fa <clock_task+0x16c>
4200d3e8:	01603533          	snez	a0,s6
4200d3ec:	40a00533          	neg	a0,a0
4200d3f0:	097c                	addi	a5,sp,156
4200d3f2:	85a2                	mv	a1,s0
4200d3f4:	8d7d                	and	a0,a0,a5
4200d3f6:	67f000ef          	jal	4200e274 <factory_draw_startup>
4200d3fa:	34114603          	lbu	a2,833(sp)
4200d3fe:	08000593          	li	a1,128
4200d402:	1008                	addi	a0,sp,32
4200d404:	e2bff0ef          	jal	4200d22e <timer_snapshot>
4200d408:	4485                	li	s1,1
4200d40a:	c422                	sw	s0,8(sp)
4200d40c:	4529                	li	a0,10
4200d40e:	1e812903          	lw	s2,488(sp)
4200d412:	0f814d03          	lbu	s10,248(sp)
4200d416:	28f9f0ef          	jal	420acea4 <vTaskDelay>
4200d41a:	4782                	lw	a5,0(sp)
4200d41c:	4c92                	lw	s9,4(sp)
4200d41e:	4af2                	lw	s5,28(sp)
4200d420:	ca52                	sw	s4,20(sp)
4200d422:	c85a                	sw	s6,16(sp)
4200d424:	cc3e                	sw	a5,24(sp)
4200d426:	b5f9                	j	4200d2f4 <clock_task+0x66>
4200d428:	000b1d63          	bnez	s6,4200d442 <clock_task+0x1b4>
4200d42c:	5e3020ef          	jal	4201020e <network_ap_active>
4200d430:	12050763          	beqz	a0,4200d55e <clock_task+0x2d0>
4200d434:	4409                	li	s0,2
4200d436:	fc848be3          	beq	s1,s0,4200d40c <clock_task+0x17e>
4200d43a:	5a5000ef          	jal	4200e1de <factory_draw_setup>
4200d43e:	84a2                	mv	s1,s0
4200d440:	b7f1                	j	4200d40c <clock_task+0x17e>
4200d442:	478d                	li	a5,3
4200d444:	00f49763          	bne	s1,a5,4200d452 <clock_task+0x1c4>
4200d448:	33c14783          	lbu	a5,828(sp)
4200d44c:	4732                	lw	a4,12(sp)
4200d44e:	04e78b63          	beq	a5,a4,4200d4a4 <clock_task+0x216>
4200d452:	0f000693          	li	a3,240
4200d456:	4701                	li	a4,0
4200d458:	8636                	mv	a2,a3
4200d45a:	4581                	li	a1,0
4200d45c:	4501                	li	a0,0
4200d45e:	f96ff0ef          	jal	4200cbf4 <display_fill>
4200d462:	33c14703          	lbu	a4,828(sp)
4200d466:	4789                	li	a5,2
4200d468:	442d                	li	s0,11
4200d46a:	00f71363          	bne	a4,a5,4200d470 <clock_task+0x1e2>
4200d46e:	443d                	li	s0,15
4200d470:	fe37b097          	auipc	ra,0xfe37b
4200d474:	9c6080e7          	jalr	-1594(ra) # 40387e36 <vPortEnterCritical>
4200d478:	004c2783          	lw	a5,4(s8)
4200d47c:	8fc1                	or	a5,a5,s0
4200d47e:	00fc2223          	sw	a5,4(s8)
4200d482:	fe37b097          	auipc	ra,0xfe37b
4200d486:	9e0080e7          	jalr	-1568(ra) # 40387e62 <vPortExitCritical>
4200d48a:	33c14783          	lbu	a5,828(sp)
4200d48e:	00fde863          	bltu	s11,a5,4200d49e <clock_task+0x210>
4200d492:	565a                	lw	a2,180(sp)
4200d494:	55ea                	lw	a1,184(sp)
4200d496:	86d2                	mv	a3,s4
4200d498:	1bc8                	addi	a0,sp,500
4200d49a:	d47ff0ef          	jal	4200d1e0 <backlight_update>
4200d49e:	4905                	li	s2,1
4200d4a0:	844a                	mv	s0,s2
4200d4a2:	4981                	li	s3,0
4200d4a4:	0f814783          	lbu	a5,248(sp)
4200d4a8:	c399                	beqz	a5,4200d4ae <clock_task+0x220>
4200d4aa:	000d1363          	bnez	s10,4200d4b0 <clock_task+0x222>
4200d4ae:	4981                	li	s3,0
4200d4b0:	33c14783          	lbu	a5,828(sp)
4200d4b4:	eb99                	bnez	a5,4200d4ca <clock_task+0x23c>
4200d4b6:	0a090863          	beqz	s2,4200d566 <clock_task+0x2d8>
4200d4ba:	34114603          	lbu	a2,833(sp)
4200d4be:	4589                	li	a1,2
4200d4c0:	00e8                	addi	a0,sp,76
4200d4c2:	d6dff0ef          	jal	4200d22e <timer_snapshot>
4200d4c6:	47c6                	lw	a5,80(sp)
4200d4c8:	e3dd                	bnez	a5,4200d56e <clock_task+0x2e0>
4200d4ca:	33c14783          	lbu	a5,828(sp)
4200d4ce:	0c079c63          	bnez	a5,4200d5a6 <clock_task+0x318>
4200d4d2:	33d14503          	lbu	a0,829(sp)
4200d4d6:	040020ef          	jal	4200f516 <media_animation_frames>
4200d4da:	85aa                	mv	a1,a0
4200d4dc:	1848                	addi	a0,sp,52
4200d4de:	2e61                	jal	4200d876 <factory_animation_next>
4200d4e0:	34114603          	lbu	a2,833(sp)
4200d4e4:	84aa                	mv	s1,a0
4200d4e6:	45a1                	li	a1,8
4200d4e8:	08e8                	addi	a0,sp,92
4200d4ea:	d45ff0ef          	jal	4200d22e <timer_snapshot>
4200d4ee:	4702                	lw	a4,0(sp)
4200d4f0:	47e2                	lw	a5,24(sp)
4200d4f2:	5806                	lw	a6,96(sp)
4200d4f4:	8fb9                	xor	a5,a5,a4
4200d4f6:	4712                	lw	a4,4(sp)
4200d4f8:	01003833          	snez	a6,a6
4200d4fc:	00ecc733          	xor	a4,s9,a4
4200d500:	8fd9                	or	a5,a5,a4
4200d502:	00f037b3          	snez	a5,a5
4200d506:	00f867b3          	or	a5,a6,a5
4200d50a:	e391                	bnez	a5,4200d50e <clock_task+0x280>
4200d50c:	c051                	beqz	s0,4200d590 <clock_task+0x302>
4200d50e:	fff4c713          	not	a4,s1
4200d512:	877d                	srai	a4,a4,0x1f
4200d514:	87ca                	mv	a5,s2
4200d516:	8f65                	and	a4,a4,s1
4200d518:	86ce                	mv	a3,s3
4200d51a:	19b0                	addi	a2,sp,248
4200d51c:	190c                	addi	a1,sp,176
4200d51e:	1bc8                	addi	a0,sp,500
4200d520:	61d000ef          	jal	4200e33c <factory_draw_classic>
4200d524:	41d000ef          	jal	4200e140 <factory_scroll_tick>
4200d528:	33c14703          	lbu	a4,828(sp)
4200d52c:	4789                	li	a5,2
4200d52e:	00f70863          	beq	a4,a5,4200d53e <clock_task+0x2b0>
4200d532:	565a                	lw	a2,180(sp)
4200d534:	55ea                	lw	a1,184(sp)
4200d536:	86d2                	mv	a3,s4
4200d538:	1bc8                	addi	a0,sp,500
4200d53a:	ca7ff0ef          	jal	4200d1e0 <backlight_update>
4200d53e:	33c14783          	lbu	a5,828(sp)
4200d542:	34114603          	lbu	a2,833(sp)
4200d546:	04000593          	li	a1,64
4200d54a:	0168                	addi	a0,sp,140
4200d54c:	c63e                	sw	a5,12(sp)
4200d54e:	ce1ff0ef          	jal	4200d22e <timer_snapshot>
4200d552:	47ca                	lw	a5,144(sp)
4200d554:	c399                	beqz	a5,4200d55a <clock_task+0x2cc>
4200d556:	435030ef          	jal	4201118a <weather_request_update>
4200d55a:	448d                	li	s1,3
4200d55c:	bd45                	j	4200d40c <clock_task+0x17e>
4200d55e:	478d                	li	a5,3
4200d560:	eaf496e3          	bne	s1,a5,4200d40c <clock_task+0x17e>
4200d564:	b5d5                	j	4200d448 <clock_task+0x1ba>
4200d566:	457000ef          	jal	4200e1bc <factory_scroll_description_ready>
4200d56a:	f921                	bnez	a0,4200d4ba <clock_task+0x22c>
4200d56c:	bfb9                	j	4200d4ca <clock_task+0x23c>
4200d56e:	00091b63          	bnez	s2,4200d584 <clock_task+0x2f6>
4200d572:	0f814783          	lbu	a5,248(sp)
4200d576:	c799                	beqz	a5,4200d584 <clock_task+0x2f6>
4200d578:	000d0663          	beqz	s10,4200d584 <clock_task+0x2f6>
4200d57c:	0985                	addi	s3,s3,1
4200d57e:	47a9                	li	a5,10
4200d580:	02f9f9b3          	remu	s3,s3,a5
4200d584:	f039                	bnez	s0,4200d4ca <clock_task+0x23c>
4200d586:	33c14403          	lbu	s0,828(sp)
4200d58a:	00143413          	seqz	s0,s0
4200d58e:	bf35                	j	4200d4ca <clock_task+0x23c>
4200d590:	f804cae3          	bltz	s1,4200d524 <clock_task+0x296>
4200d594:	33d14503          	lbu	a0,829(sp)
4200d598:	0a000693          	li	a3,160
4200d59c:	8636                	mv	a2,a3
4200d59e:	85a6                	mv	a1,s1
4200d5a0:	7d1010ef          	jal	4200f570 <media_draw_animation>
4200d5a4:	b741                	j	4200d524 <clock_task+0x296>
4200d5a6:	03b79463          	bne	a5,s11,4200d5ce <clock_task+0x340>
4200d5aa:	34114603          	lbu	a2,833(sp)
4200d5ae:	10e8                	addi	a0,sp,108
4200d5b0:	45a5                	li	a1,9
4200d5b2:	c7dff0ef          	jal	4200d22e <timer_snapshot>
4200d5b6:	5746                	lw	a4,112(sp)
4200d5b8:	86ca                	mv	a3,s2
4200d5ba:	0970                	addi	a2,sp,156
4200d5bc:	00375793          	srli	a5,a4,0x3
4200d5c0:	8b85                	andi	a5,a5,1
4200d5c2:	8b05                	andi	a4,a4,1
4200d5c4:	190c                	addi	a1,sp,176
4200d5c6:	1bc8                	addi	a0,sp,500
4200d5c8:	37e010ef          	jal	4200e946 <factory_draw_simple>
4200d5cc:	bfb1                	j	4200d528 <clock_task+0x29a>
4200d5ce:	4709                	li	a4,2
4200d5d0:	0ae79063          	bne	a5,a4,4200d670 <clock_task+0x3e2>
4200d5d4:	1bd8                	addi	a4,sp,500
4200d5d6:	4781                	li	a5,0
4200d5d8:	4601                	li	a2,0
4200d5da:	4695                	li	a3,5
4200d5dc:	15872583          	lw	a1,344(a4)
4200d5e0:	c581                	beqz	a1,4200d5e8 <clock_task+0x35a>
4200d5e2:	00fd95b3          	sll	a1,s11,a5
4200d5e6:	8e4d                	or	a2,a2,a1
4200d5e8:	0785                	addi	a5,a5,1
4200d5ea:	0711                	addi	a4,a4,4
4200d5ec:	fed798e3          	bne	a5,a3,4200d5dc <clock_task+0x34e>
4200d5f0:	4686                	lw	a3,64(sp)
4200d5f2:	34814583          	lbu	a1,840(sp)
4200d5f6:	09dc                	addi	a5,sp,212
4200d5f8:	8289                	srli	a3,a3,0x2
4200d5fa:	8a85                	andi	a3,a3,1
4200d5fc:	4701                	li	a4,0
4200d5fe:	00d966b3          	or	a3,s2,a3
4200d602:	1828                	addi	a0,sp,56
4200d604:	2ac1                	jal	4200d7d4 <factory_photo_step>
4200d606:	0d714783          	lbu	a5,215(sp)
4200d60a:	c789                	beqz	a5,4200d614 <clock_task+0x386>
4200d60c:	0d415503          	lhu	a0,212(sp)
4200d610:	affff0ef          	jal	4200d10e <backlight_set_level>
4200d614:	0d610503          	lb	a0,214(sp)
4200d618:	57fd                	li	a5,-1
4200d61a:	02f54663          	blt	a0,a5,4200d646 <clock_task+0x3b8>
4200d61e:	04f51563          	bne	a0,a5,4200d668 <clock_task+0x3da>
4200d622:	0f000693          	li	a3,240
4200d626:	8636                	mv	a2,a3
4200d628:	4701                	li	a4,0
4200d62a:	4581                	li	a1,0
4200d62c:	4501                	li	a0,0
4200d62e:	dc6ff0ef          	jal	4200cbf4 <display_fill>
4200d632:	6741                	lui	a4,0x10
4200d634:	4805                	li	a6,1
4200d636:	4781                	li	a5,0
4200d638:	177d                	addi	a4,a4,-1 # ffff <CSR_UINTSTATUS+0xf34e>
4200d63a:	46c1                	li	a3,16
4200d63c:	0970                	addi	a2,sp,156
4200d63e:	0e100593          	li	a1,225
4200d642:	4515                	li	a0,5
4200d644:	2b59                	jal	4200dbda <display_factory_text>
4200d646:	0d814783          	lbu	a5,216(sp)
4200d64a:	ec078fe3          	beqz	a5,4200d528 <clock_task+0x29a>
4200d64e:	34114603          	lbu	a2,833(sp)
4200d652:	1008                	addi	a0,sp,32
4200d654:	4591                	li	a1,4
4200d656:	bd9ff0ef          	jal	4200d22e <timer_snapshot>
4200d65a:	565a                	lw	a2,180(sp)
4200d65c:	55ea                	lw	a1,184(sp)
4200d65e:	86d2                	mv	a3,s4
4200d660:	1bc8                	addi	a0,sp,500
4200d662:	b7fff0ef          	jal	4200d1e0 <backlight_update>
4200d666:	b5c9                	j	4200d528 <clock_task+0x29a>
4200d668:	096c                	addi	a1,sp,156
4200d66a:	1f7010ef          	jal	4200f060 <factory_draw_photo>
4200d66e:	bfe1                	j	4200d646 <clock_task+0x3b8>
4200d670:	34114603          	lbu	a2,833(sp)
4200d674:	4585                	li	a1,1
4200d676:	18e8                	addi	a0,sp,124
4200d678:	bb7ff0ef          	jal	4200d22e <timer_snapshot>
4200d67c:	478a                	lw	a5,128(sp)
4200d67e:	00f037b3          	snez	a5,a5
4200d682:	00f967b3          	or	a5,s2,a5
4200d686:	e399                	bnez	a5,4200d68c <clock_task+0x3fe>
4200d688:	ea0400e3          	beqz	s0,4200d528 <clock_task+0x29a>
4200d68c:	864a                	mv	a2,s2
4200d68e:	096c                	addi	a1,sp,156
4200d690:	1908                	addi	a0,sp,176
4200d692:	4d6010ef          	jal	4200eb68 <factory_draw_dial>
4200d696:	bd49                	j	4200d528 <clock_task+0x29a>


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420111cc <weather_request_active>:
420111cc:	3fcb47b7          	lui	a5,0x3fcb4
420111d0:	92c78793          	addi	a5,a5,-1748 # 3fcb392c <request_state>
420111d4:	0330000f          	fence	rw,rw
420111d8:	4388                	lw	a0,0(a5)
420111da:	0230000f          	fence	r,rw
420111de:	00a03533          	snez	a0,a0
420111e2:	8082                	ret


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42010e68 <weather_task>:
42010e68:	8a010113          	addi	sp,sp,-1888
42010e6c:	04100613          	li	a2,65
42010e70:	4581                	li	a1,0
42010e72:	1068                	addi	a0,sp,44
42010e74:	74112e23          	sw	ra,1884(sp)
42010e78:	74912a23          	sw	s1,1876(sp)
42010e7c:	75312623          	sw	s3,1868(sp)
42010e80:	75412423          	sw	s4,1864(sp)
42010e84:	74812c23          	sw	s0,1880(sp)
42010e88:	75212823          	sw	s2,1872(sp)
42010e8c:	75512223          	sw	s5,1860(sp)
42010e90:	fdfef097          	auipc	ra,0xfdfef
42010e94:	5f8080e7          	jalr	1528(ra) # 40000488 <memset>
42010e98:	04100613          	li	a2,65
42010e9c:	4581                	li	a1,0
42010e9e:	1888                	addi	a0,sp,112
42010ea0:	cc02                	sw	zero,24(sp)
42010ea2:	ce02                	sw	zero,28(sp)
42010ea4:	d002                	sw	zero,32(sp)
42010ea6:	d202                	sw	zero,36(sp)
42010ea8:	d402                	sw	zero,40(sp)
42010eaa:	fdfef097          	auipc	ra,0xfdfef
42010eae:	5de080e7          	jalr	1502(ra) # 40000488 <memset>
42010eb2:	3fcb47b7          	lui	a5,0x3fcb4
42010eb6:	3fcb04b7          	lui	s1,0x3fcb0
42010eba:	4985                	li	s3,1
42010ebc:	92c78a13          	addi	s4,a5,-1748 # 3fcb392c <request_state>
42010ec0:	aa048493          	addi	s1,s1,-1376 # 3fcafaa0 <cached_weather>
42010ec4:	567d                	li	a2,-1
42010ec6:	4585                	li	a1,1
42010ec8:	4501                	li	a0,0
42010eca:	7489c0ef          	jal	420ad612 <ulTaskGenericNotifyTake>
42010ece:	4615                	li	a2,5
42010ed0:	4585                	li	a1,1
42010ed2:	8552                	mv	a0,s4
42010ed4:	fe376097          	auipc	ra,0xfe376
42010ed8:	6b2080e7          	jalr	1714(ra) # 40387586 <__atomic_fetch_or_4>
42010edc:	55f5                	li	a1,-3
42010ede:	4615                	li	a2,5
42010ee0:	8552                	mv	a0,s4
42010ee2:	fe376097          	auipc	ra,0xfe376
42010ee6:	67c080e7          	jalr	1660(ra) # 4038755e <__atomic_fetch_and_4>
42010eea:	0fc8                	addi	a0,sp,980
42010eec:	da4fb0ef          	jal	4200c490 <settings_snapshot>
42010ef0:	43a10593          	addi	a1,sp,1082
42010ef4:	1068                	addi	a0,sp,44
42010ef6:	fe376097          	auipc	ra,0xfe376
42010efa:	75c080e7          	jalr	1884(ra) # 40387652 <strcmp>
42010efe:	e10d                	bnez	a0,42010f20 <weather_task+0xb8>
42010f00:	47b10593          	addi	a1,sp,1147
42010f04:	0828                	addi	a0,sp,24
42010f06:	fe376097          	auipc	ra,0xfe376
42010f0a:	74c080e7          	jalr	1868(ra) # 40387652 <strcmp>
42010f0e:	e909                	bnez	a0,42010f20 <weather_task+0xb8>
42010f10:	4d010593          	addi	a1,sp,1232
42010f14:	1888                	addi	a0,sp,112
42010f16:	fe376097          	auipc	ra,0xfe376
42010f1a:	73c080e7          	jalr	1852(ra) # 40387652 <strcmp>
42010f1e:	c939                	beqz	a0,42010f74 <weather_task+0x10c>
42010f20:	43a10593          	addi	a1,sp,1082
42010f24:	1068                	addi	a0,sp,44
42010f26:	fe377097          	auipc	ra,0xfe377
42010f2a:	842080e7          	jalr	-1982(ra) # 40387768 <strcpy>
42010f2e:	47b10593          	addi	a1,sp,1147
42010f32:	0828                	addi	a0,sp,24
42010f34:	fe377097          	auipc	ra,0xfe377
42010f38:	834080e7          	jalr	-1996(ra) # 40387768 <strcpy>
42010f3c:	4d010593          	addi	a1,sp,1232
42010f40:	1888                	addi	a0,sp,112
42010f42:	fe377097          	auipc	ra,0xfe377
42010f46:	826080e7          	jalr	-2010(ra) # 40387768 <strcpy>
42010f4a:	3fcb4437          	lui	s0,0x3fcb4
42010f4e:	93442503          	lw	a0,-1740(s0) # 3fcb3934 <weather_mutex>
42010f52:	55fd                	li	a1,-1
42010f54:	55e9b0ef          	jal	420ac4b2 <xQueueSemaphoreTake>
42010f58:	0f04a783          	lw	a5,240(s1)
42010f5c:	93442503          	lw	a0,-1740(s0)
42010f60:	4681                	li	a3,0
42010f62:	0785                	addi	a5,a5,1
42010f64:	4601                	li	a2,0
42010f66:	4581                	li	a1,0
42010f68:	00048023          	sb	zero,0(s1)
42010f6c:	0ef4a823          	sw	a5,240(s1)
42010f70:	1229b0ef          	jal	420ac092 <xQueueGenericSend>
42010f74:	a80ff0ef          	jal	420101f4 <network_connected>
42010f78:	14050e63          	beqz	a0,420110d4 <weather_task+0x26c>
42010f7c:	4d014783          	lbu	a5,1232(sp)
42010f80:	14078a63          	beqz	a5,420110d4 <weather_task+0x26c>
42010f84:	0a8c                	addi	a1,sp,336
42010f86:	43a10513          	addi	a0,sp,1082
42010f8a:	e65ff0ef          	jal	42010dee <url_escape>
42010f8e:	0c4c                	addi	a1,sp,532
42010f90:	4d010513          	addi	a0,sp,1232
42010f94:	e5bff0ef          	jal	42010dee <url_escape>
42010f98:	54010913          	addi	s2,sp,1344
42010f9c:	3c0b4637          	lui	a2,0x3c0b4
42010fa0:	0c5c                	addi	a5,sp,532
42010fa2:	47b10713          	addi	a4,sp,1147
42010fa6:	0a94                	addi	a3,sp,336
42010fa8:	2bc60613          	addi	a2,a2,700 # 3c0b42bc <_esp_libc_clock_array_end+0x416c>
42010fac:	20000593          	li	a1,512
42010fb0:	854a                	mv	a0,s2
42010fb2:	6998c0ef          	jal	4209de4a <snprintf>
42010fb6:	6589                	lui	a1,0x2
42010fb8:	4781                	li	a5,0
42010fba:	4801                	li	a6,0
42010fbc:	0585                	addi	a1,a1,1 # 2001 <CSR_UINTSTATUS+0x1350>
42010fbe:	4505                	li	a0,1
42010fc0:	c83e                	sw	a5,16(sp)
42010fc2:	ca42                	sw	a6,20(sp)
42010fc4:	fe376097          	auipc	ra,0xfe376
42010fc8:	202080e7          	jalr	514(ra) # 403871c6 <calloc>
42010fcc:	c62a                	sw	a0,12(sp)
42010fce:	10050363          	beqz	a0,420110d4 <weather_task+0x26c>
42010fd2:	09800613          	li	a2,152
42010fd6:	4581                	li	a1,0
42010fd8:	1928                	addi	a0,sp,184
42010fda:	fdfef097          	auipc	ra,0xfdfef
42010fde:	4ae080e7          	jalr	1198(ra) # 40000488 <memset>
42010fe2:	6789                	lui	a5,0x2
42010fe4:	71078793          	addi	a5,a5,1808 # 2710 <CSR_UINTSTATUS+0x1a5f>
42010fe8:	10f12223          	sw	a5,260(sp)
42010fec:	420117b7          	lui	a5,0x42011
42010ff0:	0e878793          	addi	a5,a5,232 # 420110e8 <weather_http_event>
42010ff4:	10f12a23          	sw	a5,276(sp)
42010ff8:	40000793          	li	a5,1024
42010ffc:	10f12e23          	sw	a5,284(sp)
42011000:	12f12023          	sw	a5,288(sp)
42011004:	1948                	addi	a0,sp,180
42011006:	007c                	addi	a5,sp,12
42011008:	db4a                	sw	s2,180(sp)
4201100a:	11310423          	sb	s3,264(sp)
4201100e:	12f12223          	sw	a5,292(sp)
42011012:	6b4240ef          	jal	420356c6 <esp_http_client_init>
42011016:	8aaa                	mv	s5,a0
42011018:	10100413          	li	s0,257
4201101c:	c915                	beqz	a0,42011050 <weather_task+0x1e8>
4201101e:	194250ef          	jal	420361b2 <esp_http_client_perform>
42011022:	842a                	mv	s0,a0
42011024:	8556                	mv	a0,s5
42011026:	0c4250ef          	jal	420360ea <esp_http_client_get_status_code>
4201102a:	0c800793          	li	a5,200
4201102e:	0af51b63          	bne	a0,a5,420110e4 <weather_task+0x27c>
42011032:	01414783          	lbu	a5,20(sp)
42011036:	e7dd                	bnez	a5,420110e4 <weather_task+0x27c>
42011038:	8556                	mv	a0,s5
4201103a:	314240ef          	jal	4203534e <esp_http_client_cleanup>
4201103e:	e809                	bnez	s0,42011050 <weather_task+0x1e8>
42011040:	45c2                	lw	a1,16(sp)
42011042:	4532                	lw	a0,12(sp)
42011044:	0db4                	addi	a3,sp,728
42011046:	0fd0                	addi	a2,sp,980
42011048:	24dd                	jal	4201132e <weather_parse_response>
4201104a:	e119                	bnez	a0,42011050 <weather_task+0x1e8>
4201104c:	10800413          	li	s0,264
42011050:	4532                	lw	a0,12(sp)
42011052:	fe376097          	auipc	ra,0xfe376
42011056:	170080e7          	jalr	368(ra) # 403871c2 <cfree>
4201105a:	ec2d                	bnez	s0,420110d4 <weather_task+0x26c>
4201105c:	854a                	mv	a0,s2
4201105e:	c32fb0ef          	jal	4200c490 <settings_snapshot>
42011062:	43a10593          	addi	a1,sp,1082
42011066:	5a610513          	addi	a0,sp,1446
4201106a:	fe376097          	auipc	ra,0xfe376
4201106e:	5e8080e7          	jalr	1512(ra) # 40387652 <strcmp>
42011072:	e12d                	bnez	a0,420110d4 <weather_task+0x26c>
42011074:	47b10593          	addi	a1,sp,1147
42011078:	5e710513          	addi	a0,sp,1511
4201107c:	fe376097          	auipc	ra,0xfe376
42011080:	5d6080e7          	jalr	1494(ra) # 40387652 <strcmp>
42011084:	e921                	bnez	a0,420110d4 <weather_task+0x26c>
42011086:	4d010593          	addi	a1,sp,1232
4201108a:	63c10513          	addi	a0,sp,1596
4201108e:	fe376097          	auipc	ra,0xfe376
42011092:	5c4080e7          	jalr	1476(ra) # 40387652 <strcmp>
42011096:	ed1d                	bnez	a0,420110d4 <weather_task+0x26c>
42011098:	3fcb4437          	lui	s0,0x3fcb4
4201109c:	93442503          	lw	a0,-1740(s0) # 3fcb3934 <weather_mutex>
420110a0:	55fd                	li	a1,-1
420110a2:	4109b0ef          	jal	420ac4b2 <xQueueSemaphoreTake>
420110a6:	3fcb0537          	lui	a0,0x3fcb0
420110aa:	aa050513          	addi	a0,a0,-1376 # 3fcafaa0 <cached_weather>
420110ae:	0f052783          	lw	a5,240(a0)
420110b2:	0f800613          	li	a2,248
420110b6:	0dac                	addi	a1,sp,728
420110b8:	0785                	addi	a5,a5,1
420110ba:	3cf12423          	sw	a5,968(sp)
420110be:	fe376097          	auipc	ra,0xfe376
420110c2:	17c080e7          	jalr	380(ra) # 4038723a <memcpy>
420110c6:	93442503          	lw	a0,-1740(s0)
420110ca:	4681                	li	a3,0
420110cc:	4601                	li	a2,0
420110ce:	4581                	li	a1,0
420110d0:	7c39a0ef          	jal	420ac092 <xQueueGenericSend>
420110d4:	4615                	li	a2,5
420110d6:	55f9                	li	a1,-2
420110d8:	8552                	mv	a0,s4
420110da:	fe376097          	auipc	ra,0xfe376
420110de:	484080e7          	jalr	1156(ra) # 4038755e <__atomic_fetch_and_4>
420110e2:	b3cd                	j	42010ec4 <weather_task+0x5c>
420110e4:	547d                	li	s0,-1
420110e6:	bf89                	j	42011038 <weather_task+0x1d0>
