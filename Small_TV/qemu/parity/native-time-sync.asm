
small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4201058a <time_sync_notify>:
4201058a:	3fcb47b7          	lui	a5,0x3fcb4
4201058e:	4705                	li	a4,1
42010590:	8e878793          	addi	a5,a5,-1816 # 3fcb38e8 <time_synced>
42010594:	0310000f          	fence	rw,w
42010598:	00e78023          	sb	a4,0(a5)
4201059c:	8082                	ret


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4201059e <services_time_synced>:
4201059e:	3fcb47b7          	lui	a5,0x3fcb4
420105a2:	8e878793          	addi	a5,a5,-1816 # 3fcb38e8 <time_synced>
420105a6:	00078503          	lb	a0,0(a5)
420105aa:	0230000f          	fence	r,rw
420105ae:	0ff57513          	zext.b	a0,a0
420105b2:	8082                	ret


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420105b4 <services_local_time>:
420105b4:	1101                	addi	sp,sp,-32
420105b6:	cc22                	sw	s0,24(sp)
420105b8:	c42e                	sw	a1,8(sp)
420105ba:	c632                	sw	a2,12(sp)
420105bc:	c236                	sw	a3,4(sp)
420105be:	ce06                	sw	ra,28(sp)
420105c0:	842a                	mv	s0,a0
420105c2:	fddff0ef          	jal	4201059e <services_time_synced>
420105c6:	4692                	lw	a3,4(sp)
420105c8:	45a2                	lw	a1,8(sp)
420105ca:	4632                	lw	a2,12(sp)
420105cc:	c511                	beqz	a0,420105d8 <services_local_time+0x24>
420105ce:	8522                	mv	a0,s0
420105d0:	4462                	lw	s0,24(sp)
420105d2:	40f2                	lw	ra,28(sp)
420105d4:	6105                	addi	sp,sp,32
420105d6:	a331                	j	42010ae2 <timezone_local_time>
420105d8:	40f2                	lw	ra,28(sp)
420105da:	4462                	lw	s0,24(sp)
420105dc:	6105                	addi	sp,sp,32
420105de:	8082                	ret


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420103d2 <time_sync_task>:
420103d2:	db010113          	addi	sp,sp,-592
420103d6:	04100613          	li	a2,65
420103da:	4581                	li	a1,0
420103dc:	0888                	addi	a0,sp,80
420103de:	24112623          	sw	ra,588(sp)
420103e2:	24812423          	sw	s0,584(sp)
420103e6:	24912223          	sw	s1,580(sp)
420103ea:	25212023          	sw	s2,576(sp)
420103ee:	23412c23          	sw	s4,568(sp)
420103f2:	23512a23          	sw	s5,564(sp)
420103f6:	23312e23          	sw	s3,572(sp)
420103fa:	fdff0097          	auipc	ra,0xfdff0
420103fe:	08e080e7          	jalr	142(ra) # 40000488 <memset>
42010402:	04100613          	li	a2,65
42010406:	4581                	li	a1,0
42010408:	0948                	addi	a0,sp,148
4201040a:	00011223          	sh	zero,4(sp)
4201040e:	00010323          	sb	zero,6(sp)
42010412:	fdff0097          	auipc	ra,0xfdff0
42010416:	076080e7          	jalr	118(ra) # 40000488 <memset>
4201041a:	02000613          	li	a2,32
4201041e:	4581                	li	a1,0
42010420:	0068                	addi	a0,sp,12
42010422:	fdff0097          	auipc	ra,0xfdff0
42010426:	066080e7          	jalr	102(ra) # 40000488 <memset>
4201042a:	3c0b47b7          	lui	a5,0x3c0b4
4201042e:	05078a13          	addi	s4,a5,80 # 3c0b4050 <_esp_libc_clock_array_end+0x3f00>
42010432:	3c0b4937          	lui	s2,0x3c0b4
42010436:	3c0b47b7          	lui	a5,0x3c0b4
4201043a:	4401                	li	s0,0
4201043c:	4481                	li	s1,0
4201043e:	06478a93          	addi	s5,a5,100 # 3c0b4064 <_esp_libc_clock_array_end+0x3f14>
42010442:	06890913          	addi	s2,s2,104 # 3c0b4068 <_esp_libc_clock_array_end+0x3f18>
42010446:	09a8                	addi	a0,sp,216
42010448:	e8bfb0ef          	jal	4200c2d2 <settings_snapshot>
4201044c:	004c                	addi	a1,sp,4
4201044e:	17f10513          	addi	a0,sp,383
42010452:	fe377097          	auipc	ra,0xfe377
42010456:	200080e7          	jalr	512(ra) # 40387652 <strcmp>
4201045a:	e909                	bnez	a0,4201046c <time_sync_task+0x9a>
4201045c:	094c                	addi	a1,sp,148
4201045e:	13e10513          	addi	a0,sp,318
42010462:	fe377097          	auipc	ra,0xfe377
42010466:	1f0080e7          	jalr	496(ra) # 40387652 <strcmp>
4201046a:	c105                	beqz	a0,4201048a <time_sync_task+0xb8>
4201046c:	17f10593          	addi	a1,sp,383
42010470:	0048                	addi	a0,sp,4
42010472:	fe377097          	auipc	ra,0xfe377
42010476:	2f6080e7          	jalr	758(ra) # 40387768 <strcpy>
4201047a:	13e10593          	addi	a1,sp,318
4201047e:	0948                	addi	a0,sp,148
42010480:	fe377097          	auipc	ra,0xfe377
42010484:	2e8080e7          	jalr	744(ra) # 40387768 <strcpy>
42010488:	4481                	li	s1,0
4201048a:	4501                	li	a0,0
4201048c:	3938c0ef          	jal	4209d01e <time>
42010490:	862e                	mv	a2,a1
42010492:	00310713          	addi	a4,sp,3
42010496:	85aa                	mv	a1,a0
42010498:	0034                	addi	a3,sp,8
4201049a:	17f10513          	addi	a0,sp,383
4201049e:	29a9                	jal	420108f8 <timezone_utc_offset>
420104a0:	89aa                	mv	s3,a0
420104a2:	c53d                	beqz	a0,42010510 <time_sync_task+0x13e>
420104a4:	46a2                	lw	a3,8(sp)
420104a6:	8652                	mv	a2,s4
420104a8:	1068                	addi	a0,sp,44
420104aa:	41f6d793          	srai	a5,a3,0x1f
420104ae:	00d7c5b3          	xor	a1,a5,a3
420104b2:	8d9d                	sub	a1,a1,a5
420104b4:	03c00793          	li	a5,60
420104b8:	02f5d733          	divu	a4,a1,a5
420104bc:	fff6c693          	not	a3,a3
420104c0:	86fd                	srai	a3,a3,0x1f
420104c2:	8a89                	andi	a3,a3,2
420104c4:	02b68693          	addi	a3,a3,43
420104c8:	02f5f833          	remu	a6,a1,a5
420104cc:	02f777b3          	remu	a5,a4,a5
420104d0:	6705                	lui	a4,0x1
420104d2:	e1070713          	addi	a4,a4,-496 # e10 <CSR_UINTSTATUS+0x15f>
420104d6:	02e5d733          	divu	a4,a1,a4
420104da:	02000593          	li	a1,32
420104de:	7308d0ef          	jal	4209dc0e <snprintf>
420104e2:	c881                	beqz	s1,420104f2 <time_sync_task+0x120>
420104e4:	006c                	addi	a1,sp,12
420104e6:	1068                	addi	a0,sp,44
420104e8:	fe377097          	auipc	ra,0xfe377
420104ec:	16a080e7          	jalr	362(ra) # 40387652 <strcmp>
420104f0:	cd19                	beqz	a0,4201050e <time_sync_task+0x13c>
420104f2:	4605                	li	a2,1
420104f4:	106c                	addi	a1,sp,44
420104f6:	8556                	mv	a0,s5
420104f8:	29c8c0ef          	jal	4209c794 <setenv>
420104fc:	e911                	bnez	a0,42010510 <time_sync_task+0x13e>
420104fe:	15e8d0ef          	jal	4209d65c <tzset>
42010502:	106c                	addi	a1,sp,44
42010504:	0068                	addi	a0,sp,12
42010506:	fe377097          	auipc	ra,0xfe377
4201050a:	262080e7          	jalr	610(ra) # 40387768 <strcpy>
4201050e:	84ce                	mv	s1,s3
42010510:	a9fff0ef          	jal	4200ffae <network_connected>
42010514:	c12d                	beqz	a0,42010576 <time_sync_task+0x1a4>
42010516:	c819                	beqz	s0,4201052c <time_sync_task+0x15a>
42010518:	18210593          	addi	a1,sp,386
4201051c:	0888                	addi	a0,sp,80
4201051e:	fe377097          	auipc	ra,0xfe377
42010522:	134080e7          	jalr	308(ra) # 40387652 <strcmp>
42010526:	c921                	beqz	a0,42010576 <time_sync_task+0x1a4>
42010528:	137210ef          	jal	42031e5e <esp_netif_sntp_deinit>
4201052c:	18210593          	addi	a1,sp,386
42010530:	0888                	addi	a0,sp,80
42010532:	fe377097          	auipc	ra,0xfe377
42010536:	236080e7          	jalr	566(ra) # 40387768 <strcpy>
4201053a:	4785                	li	a5,1
4201053c:	d602                	sw	zero,44(sp)
4201053e:	02f107a3          	sb	a5,47(sp)
42010542:	478d                	li	a5,3
42010544:	c0be                	sw	a5,64(sp)
42010546:	05014783          	lbu	a5,80(sp)
4201054a:	da02                	sw	zero,52(sp)
4201054c:	dc02                	sw	zero,56(sp)
4201054e:	de02                	sw	zero,60(sp)
42010550:	c2ca                	sw	s2,68(sp)
42010552:	c79d                	beqz	a5,42010580 <time_sync_task+0x1ae>
42010554:	089c                	addi	a5,sp,80
42010556:	c4be                	sw	a5,72(sp)
42010558:	3c0b47b7          	lui	a5,0x3c0b4
4201055c:	96878793          	addi	a5,a5,-1688 # 3c0b3968 <_esp_libc_clock_array_end+0x3818>
42010560:	c6be                	sw	a5,76(sp)
42010562:	420107b7          	lui	a5,0x42010
42010566:	58a78793          	addi	a5,a5,1418 # 4201058a <time_sync_notify>
4201056a:	1068                	addi	a0,sp,44
4201056c:	d83e                	sw	a5,48(sp)
4201056e:	17d210ef          	jal	42031eea <esp_netif_sntp_init>
42010572:	00153413          	seqz	s0,a0
42010576:	06400513          	li	a0,100
4201057a:	6ee9c0ef          	jal	420acc68 <vTaskDelay>
4201057e:	b5e1                	j	42010446 <time_sync_task+0x74>
42010580:	3c0b47b7          	lui	a5,0x3c0b4
42010584:	04078793          	addi	a5,a5,64 # 3c0b4040 <_esp_libc_clock_array_end+0x3ef0>
42010588:	b7f9                	j	42010556 <time_sync_task+0x184>
