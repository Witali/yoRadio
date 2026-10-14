
small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .flash.text:

420103da <time_sync_notify>:
420103da:	3fcb47b7          	lui	a5,0x3fcb4
420103de:	4705                	li	a4,1
420103e0:	8e878793          	addi	a5,a5,-1816 # 3fcb38e8 <time_synced>
420103e4:	0310000f          	fence	rw,w
420103e8:	00e78023          	sb	a4,0(a5)
420103ec:	8082                	ret


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .flash.text:

420103ee <services_time_synced>:
420103ee:	3fcb47b7          	lui	a5,0x3fcb4
420103f2:	8e878793          	addi	a5,a5,-1816 # 3fcb38e8 <time_synced>
420103f6:	00078503          	lb	a0,0(a5)
420103fa:	0230000f          	fence	r,rw
420103fe:	0ff57513          	zext.b	a0,a0
42010402:	8082                	ret


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .flash.text:

42010404 <services_local_time>:
42010404:	1101                	addi	sp,sp,-32
42010406:	cc22                	sw	s0,24(sp)
42010408:	c42e                	sw	a1,8(sp)
4201040a:	c632                	sw	a2,12(sp)
4201040c:	c236                	sw	a3,4(sp)
4201040e:	ce06                	sw	ra,28(sp)
42010410:	842a                	mv	s0,a0
42010412:	fddff0ef          	jal	420103ee <services_time_synced>
42010416:	4692                	lw	a3,4(sp)
42010418:	45a2                	lw	a1,8(sp)
4201041a:	4632                	lw	a2,12(sp)
4201041c:	c511                	beqz	a0,42010428 <services_local_time+0x24>
4201041e:	8522                	mv	a0,s0
42010420:	4462                	lw	s0,24(sp)
42010422:	40f2                	lw	ra,28(sp)
42010424:	6105                	addi	sp,sp,32
42010426:	a331                	j	42010932 <timezone_local_time>
42010428:	40f2                	lw	ra,28(sp)
4201042a:	4462                	lw	s0,24(sp)
4201042c:	6105                	addi	sp,sp,32
4201042e:	8082                	ret


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .flash.text:

42010222 <time_sync_task>:
42010222:	db010113          	addi	sp,sp,-592
42010226:	04100613          	li	a2,65
4201022a:	4581                	li	a1,0
4201022c:	0888                	addi	a0,sp,80
4201022e:	24112623          	sw	ra,588(sp)
42010232:	24812423          	sw	s0,584(sp)
42010236:	24912223          	sw	s1,580(sp)
4201023a:	25212023          	sw	s2,576(sp)
4201023e:	23412c23          	sw	s4,568(sp)
42010242:	23512a23          	sw	s5,564(sp)
42010246:	23312e23          	sw	s3,572(sp)
4201024a:	fdff0097          	auipc	ra,0xfdff0
4201024e:	23e080e7          	jalr	574(ra) # 40000488 <memset>
42010252:	04100613          	li	a2,65
42010256:	4581                	li	a1,0
42010258:	0948                	addi	a0,sp,148
4201025a:	00011223          	sh	zero,4(sp)
4201025e:	00010323          	sb	zero,6(sp)
42010262:	fdff0097          	auipc	ra,0xfdff0
42010266:	226080e7          	jalr	550(ra) # 40000488 <memset>
4201026a:	02000613          	li	a2,32
4201026e:	4581                	li	a1,0
42010270:	0068                	addi	a0,sp,12
42010272:	fdff0097          	auipc	ra,0xfdff0
42010276:	216080e7          	jalr	534(ra) # 40000488 <memset>
4201027a:	3c0b47b7          	lui	a5,0x3c0b4
4201027e:	05078a13          	addi	s4,a5,80 # 3c0b4050 <_esp_libc_clock_array_end+0x3f00>
42010282:	3c0b4937          	lui	s2,0x3c0b4
42010286:	3c0b47b7          	lui	a5,0x3c0b4
4201028a:	4401                	li	s0,0
4201028c:	4481                	li	s1,0
4201028e:	06478a93          	addi	s5,a5,100 # 3c0b4064 <_esp_libc_clock_array_end+0x3f14>
42010292:	06890913          	addi	s2,s2,104 # 3c0b4068 <_esp_libc_clock_array_end+0x3f18>
42010296:	09a8                	addi	a0,sp,216
42010298:	83afc0ef          	jal	4200c2d2 <settings_snapshot>
4201029c:	004c                	addi	a1,sp,4
4201029e:	17f10513          	addi	a0,sp,383
420102a2:	fe377097          	auipc	ra,0xfe377
420102a6:	3b0080e7          	jalr	944(ra) # 40387652 <strcmp>
420102aa:	e909                	bnez	a0,420102bc <time_sync_task+0x9a>
420102ac:	094c                	addi	a1,sp,148
420102ae:	13e10513          	addi	a0,sp,318
420102b2:	fe377097          	auipc	ra,0xfe377
420102b6:	3a0080e7          	jalr	928(ra) # 40387652 <strcmp>
420102ba:	c105                	beqz	a0,420102da <time_sync_task+0xb8>
420102bc:	17f10593          	addi	a1,sp,383
420102c0:	0048                	addi	a0,sp,4
420102c2:	fe377097          	auipc	ra,0xfe377
420102c6:	4a6080e7          	jalr	1190(ra) # 40387768 <strcpy>
420102ca:	13e10593          	addi	a1,sp,318
420102ce:	0948                	addi	a0,sp,148
420102d0:	fe377097          	auipc	ra,0xfe377
420102d4:	498080e7          	jalr	1176(ra) # 40387768 <strcpy>
420102d8:	4481                	li	s1,0
420102da:	4501                	li	a0,0
420102dc:	2158c0ef          	jal	4209ccf0 <time>
420102e0:	862e                	mv	a2,a1
420102e2:	00310713          	addi	a4,sp,3
420102e6:	85aa                	mv	a1,a0
420102e8:	0034                	addi	a3,sp,8
420102ea:	17f10513          	addi	a0,sp,383
420102ee:	29a9                	jal	42010748 <timezone_utc_offset>
420102f0:	89aa                	mv	s3,a0
420102f2:	c53d                	beqz	a0,42010360 <time_sync_task+0x13e>
420102f4:	46a2                	lw	a3,8(sp)
420102f6:	8652                	mv	a2,s4
420102f8:	1068                	addi	a0,sp,44
420102fa:	41f6d793          	srai	a5,a3,0x1f
420102fe:	00d7c5b3          	xor	a1,a5,a3
42010302:	8d9d                	sub	a1,a1,a5
42010304:	03c00793          	li	a5,60
42010308:	02f5d733          	divu	a4,a1,a5
4201030c:	fff6c693          	not	a3,a3
42010310:	86fd                	srai	a3,a3,0x1f
42010312:	8a89                	andi	a3,a3,2
42010314:	02b68693          	addi	a3,a3,43
42010318:	02f5f833          	remu	a6,a1,a5
4201031c:	02f777b3          	remu	a5,a4,a5
42010320:	6705                	lui	a4,0x1
42010322:	e1070713          	addi	a4,a4,-496 # e10 <CSR_UINTSTATUS+0x15f>
42010326:	02e5d733          	divu	a4,a1,a4
4201032a:	02000593          	li	a1,32
4201032e:	5b28d0ef          	jal	4209d8e0 <snprintf>
42010332:	c881                	beqz	s1,42010342 <time_sync_task+0x120>
42010334:	006c                	addi	a1,sp,12
42010336:	1068                	addi	a0,sp,44
42010338:	fe377097          	auipc	ra,0xfe377
4201033c:	31a080e7          	jalr	794(ra) # 40387652 <strcmp>
42010340:	cd19                	beqz	a0,4201035e <time_sync_task+0x13c>
42010342:	4605                	li	a2,1
42010344:	106c                	addi	a1,sp,44
42010346:	8556                	mv	a0,s5
42010348:	11e8c0ef          	jal	4209c466 <setenv>
4201034c:	e911                	bnez	a0,42010360 <time_sync_task+0x13e>
4201034e:	7e18c0ef          	jal	4209d32e <tzset>
42010352:	106c                	addi	a1,sp,44
42010354:	0068                	addi	a0,sp,12
42010356:	fe377097          	auipc	ra,0xfe377
4201035a:	412080e7          	jalr	1042(ra) # 40387768 <strcpy>
4201035e:	84ce                	mv	s1,s3
42010360:	a9fff0ef          	jal	4200fdfe <network_connected>
42010364:	c12d                	beqz	a0,420103c6 <time_sync_task+0x1a4>
42010366:	c819                	beqz	s0,4201037c <time_sync_task+0x15a>
42010368:	18210593          	addi	a1,sp,386
4201036c:	0888                	addi	a0,sp,80
4201036e:	fe377097          	auipc	ra,0xfe377
42010372:	2e4080e7          	jalr	740(ra) # 40387652 <strcmp>
42010376:	c921                	beqz	a0,420103c6 <time_sync_task+0x1a4>
42010378:	7b8210ef          	jal	42031b30 <esp_netif_sntp_deinit>
4201037c:	18210593          	addi	a1,sp,386
42010380:	0888                	addi	a0,sp,80
42010382:	fe377097          	auipc	ra,0xfe377
42010386:	3e6080e7          	jalr	998(ra) # 40387768 <strcpy>
4201038a:	4785                	li	a5,1
4201038c:	d602                	sw	zero,44(sp)
4201038e:	02f107a3          	sb	a5,47(sp)
42010392:	478d                	li	a5,3
42010394:	c0be                	sw	a5,64(sp)
42010396:	05014783          	lbu	a5,80(sp)
4201039a:	da02                	sw	zero,52(sp)
4201039c:	dc02                	sw	zero,56(sp)
4201039e:	de02                	sw	zero,60(sp)
420103a0:	c2ca                	sw	s2,68(sp)
420103a2:	c79d                	beqz	a5,420103d0 <time_sync_task+0x1ae>
420103a4:	089c                	addi	a5,sp,80
420103a6:	c4be                	sw	a5,72(sp)
420103a8:	3c0b47b7          	lui	a5,0x3c0b4
420103ac:	96878793          	addi	a5,a5,-1688 # 3c0b3968 <_esp_libc_clock_array_end+0x3818>
420103b0:	c6be                	sw	a5,76(sp)
420103b2:	420107b7          	lui	a5,0x42010
420103b6:	3da78793          	addi	a5,a5,986 # 420103da <time_sync_notify>
420103ba:	1068                	addi	a0,sp,44
420103bc:	d83e                	sw	a5,48(sp)
420103be:	7fe210ef          	jal	42031bbc <esp_netif_sntp_init>
420103c2:	00153413          	seqz	s0,a0
420103c6:	06400513          	li	a0,100
420103ca:	5709c0ef          	jal	420ac93a <vTaskDelay>
420103ce:	b5e1                	j	42010296 <time_sync_task+0x74>
420103d0:	3c0b47b7          	lui	a5,0x3c0b4
420103d4:	04078793          	addi	a5,a5,64 # 3c0b4040 <_esp_libc_clock_array_end+0x3ef0>
420103d8:	b7f9                	j	420103a6 <time_sync_task+0x184>
