
small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .flash.text:

4200c598 <settings_replace>:
4200c598:	1141                	addi	sp,sp,-16
4200c59a:	c04a                	sw	s2,0(sp)
4200c59c:	c606                	sw	ra,12(sp)
4200c59e:	c422                	sw	s0,8(sp)
4200c5a0:	c226                	sw	s1,4(sp)
4200c5a2:	892a                	mv	s2,a0
4200c5a4:	9e5ff0ef          	jal	4200bf88 <settings_valid>
4200c5a8:	c149                	beqz	a0,4200c62a <settings_replace+0x92>
4200c5aa:	3fcb4437          	lui	s0,0x3fcb4
4200c5ae:	8f042503          	lw	a0,-1808(s0) # 3fcb38f0 <settings_mutex>
4200c5b2:	55fd                	li	a1,-1
4200c5b4:	3fcaf4b7          	lui	s1,0x3fcaf
4200c5b8:	3b0a00ef          	jal	420ac968 <xQueueSemaphoreTake>
4200c5bc:	16c00613          	li	a2,364
4200c5c0:	5d048593          	addi	a1,s1,1488 # 3fcaf5d0 <current_settings>
4200c5c4:	854a                	mv	a0,s2
4200c5c6:	fe37b097          	auipc	ra,0xfe37b
4200c5ca:	c36080e7          	jalr	-970(ra) # 403871fc <memcmp>
4200c5ce:	c121                	beqz	a0,4200c60e <settings_replace+0x76>
4200c5d0:	16c00613          	li	a2,364
4200c5d4:	85ca                	mv	a1,s2
4200c5d6:	5d048513          	addi	a0,s1,1488
4200c5da:	fe37b097          	auipc	ra,0xfe37b
4200c5de:	c60080e7          	jalr	-928(ra) # 4038723a <memcpy>
4200c5e2:	3fcb4737          	lui	a4,0x3fcb4
4200c5e6:	8e872783          	lw	a5,-1816(a4) # 3fcb38e8 <generation>
4200c5ea:	0785                	addi	a5,a5,1
4200c5ec:	8ef72423          	sw	a5,-1816(a4)
4200c5f0:	3fcb47b7          	lui	a5,0x3fcb4
4200c5f4:	4705                	li	a4,1
4200c5f6:	8ee78023          	sb	a4,-1824(a5) # 3fcb38e0 <dirty>
4200c5fa:	fe375097          	auipc	ra,0xfe375
4200c5fe:	57c080e7          	jalr	1404(ra) # 40381b76 <esp_timer_get_time>
4200c602:	3fcb47b7          	lui	a5,0x3fcb4
4200c606:	8d878793          	addi	a5,a5,-1832 # 3fcb38d8 <last_change_us>
4200c60a:	c388                	sw	a0,0(a5)
4200c60c:	c3cc                	sw	a1,4(a5)
4200c60e:	8f042503          	lw	a0,-1808(s0)
4200c612:	4681                	li	a3,0
4200c614:	4601                	li	a2,0
4200c616:	4581                	li	a1,0
4200c618:	7319f0ef          	jal	420ac548 <xQueueGenericSend>
4200c61c:	4501                	li	a0,0
4200c61e:	40b2                	lw	ra,12(sp)
4200c620:	4422                	lw	s0,8(sp)
4200c622:	4492                	lw	s1,4(sp)
4200c624:	4902                	lw	s2,0(sp)
4200c626:	0141                	addi	sp,sp,16
4200c628:	8082                	ret
4200c62a:	10200513          	li	a0,258
4200c62e:	bfc5                	j	4200c61e <settings_replace+0x86>


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


small_tv_reconstructed.elf:     file format elf32-littleriscv


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
4200d8f2:	20468693          	addi	a3,a3,516 # 3c0c5204 <levels.0>
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


small_tv_reconstructed.elf:     file format elf32-littleriscv


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
4200d3b4:	35c900ef          	jal	4209d710 <time>
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
4200d458:	7039f0ef          	jal	420ad35a <vTaskDelay>
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
4200d55a:	6019f0ef          	jal	420ad35a <vTaskDelay>
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
