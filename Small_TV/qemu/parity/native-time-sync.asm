
small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420107aa <time_sync_notify>:
420107aa:	3fcb47b7          	lui	a5,0x3fcb4
420107ae:	4705                	li	a4,1
420107b0:	92078793          	addi	a5,a5,-1760 # 3fcb3920 <time_synced>
420107b4:	0310000f          	fence	rw,w
420107b8:	00e78023          	sb	a4,0(a5)
420107bc:	8082                	ret


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420107be <services_time_synced>:
420107be:	3fcb47b7          	lui	a5,0x3fcb4
420107c2:	92078793          	addi	a5,a5,-1760 # 3fcb3920 <time_synced>
420107c6:	00078503          	lb	a0,0(a5)
420107ca:	0230000f          	fence	r,rw
420107ce:	0ff57513          	zext.b	a0,a0
420107d2:	8082                	ret


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420107d4 <services_local_time>:
420107d4:	1101                	addi	sp,sp,-32
420107d6:	cc22                	sw	s0,24(sp)
420107d8:	c42e                	sw	a1,8(sp)
420107da:	c632                	sw	a2,12(sp)
420107dc:	c236                	sw	a3,4(sp)
420107de:	ce06                	sw	ra,28(sp)
420107e0:	842a                	mv	s0,a0
420107e2:	fddff0ef          	jal	420107be <services_time_synced>
420107e6:	4692                	lw	a3,4(sp)
420107e8:	45a2                	lw	a1,8(sp)
420107ea:	4632                	lw	a2,12(sp)
420107ec:	c511                	beqz	a0,420107f8 <services_local_time+0x24>
420107ee:	8522                	mv	a0,s0
420107f0:	4462                	lw	s0,24(sp)
420107f2:	40f2                	lw	ra,28(sp)
420107f4:	6105                	addi	sp,sp,32
420107f6:	a331                	j	42010d02 <timezone_local_time>
420107f8:	40f2                	lw	ra,28(sp)
420107fa:	4462                	lw	s0,24(sp)
420107fc:	6105                	addi	sp,sp,32
420107fe:	8082                	ret


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420105f0 <time_sync_task>:
420105f0:	d8010113          	addi	sp,sp,-640
420105f4:	04100613          	li	a2,65
420105f8:	4581                	li	a1,0
420105fa:	10e8                	addi	a0,sp,108
420105fc:	26112e23          	sw	ra,636(sp)
42010600:	26812c23          	sw	s0,632(sp)
42010604:	26912a23          	sw	s1,628(sp)
42010608:	27212823          	sw	s2,624(sp)
4201060c:	27412423          	sw	s4,616(sp)
42010610:	27512223          	sw	s5,612(sp)
42010614:	27312623          	sw	s3,620(sp)
42010618:	fdff0097          	auipc	ra,0xfdff0
4201061c:	e70080e7          	jalr	-400(ra) # 40000488 <memset>
42010620:	04100613          	li	a2,65
42010624:	4581                	li	a1,0
42010626:	1908                	addi	a0,sp,176
42010628:	ca02                	sw	zero,20(sp)
4201062a:	cc02                	sw	zero,24(sp)
4201062c:	ce02                	sw	zero,28(sp)
4201062e:	d002                	sw	zero,32(sp)
42010630:	d202                	sw	zero,36(sp)
42010632:	fdff0097          	auipc	ra,0xfdff0
42010636:	e56080e7          	jalr	-426(ra) # 40000488 <memset>
4201063a:	02000613          	li	a2,32
4201063e:	4581                	li	a1,0
42010640:	1028                	addi	a0,sp,40
42010642:	fdff0097          	auipc	ra,0xfdff0
42010646:	e46080e7          	jalr	-442(ra) # 40000488 <memset>
4201064a:	3c0b47b7          	lui	a5,0x3c0b4
4201064e:	05078a13          	addi	s4,a5,80 # 3c0b4050 <_esp_libc_clock_array_end+0x3f00>
42010652:	3c0b4937          	lui	s2,0x3c0b4
42010656:	3c0b47b7          	lui	a5,0x3c0b4
4201065a:	4401                	li	s0,0
4201065c:	4481                	li	s1,0
4201065e:	06478a93          	addi	s5,a5,100 # 3c0b4064 <_esp_libc_clock_array_end+0x3f14>
42010662:	06890913          	addi	s2,s2,104 # 3c0b4068 <_esp_libc_clock_array_end+0x3f18>
42010666:	19c8                	addi	a0,sp,244
42010668:	e29fb0ef          	jal	4200c490 <settings_snapshot>
4201066c:	084c                	addi	a1,sp,20
4201066e:	19b10513          	addi	a0,sp,411
42010672:	fe377097          	auipc	ra,0xfe377
42010676:	fe0080e7          	jalr	-32(ra) # 40387652 <strcmp>
4201067a:	e909                	bnez	a0,4201068c <time_sync_task+0x9c>
4201067c:	190c                	addi	a1,sp,176
4201067e:	15a10513          	addi	a0,sp,346
42010682:	fe377097          	auipc	ra,0xfe377
42010686:	fd0080e7          	jalr	-48(ra) # 40387652 <strcmp>
4201068a:	c105                	beqz	a0,420106aa <time_sync_task+0xba>
4201068c:	19b10593          	addi	a1,sp,411
42010690:	0848                	addi	a0,sp,20
42010692:	fe377097          	auipc	ra,0xfe377
42010696:	0d6080e7          	jalr	214(ra) # 40387768 <strcpy>
4201069a:	15a10593          	addi	a1,sp,346
4201069e:	1908                	addi	a0,sp,176
420106a0:	fe377097          	auipc	ra,0xfe377
420106a4:	0c8080e7          	jalr	200(ra) # 40387768 <strcpy>
420106a8:	4481                	li	s1,0
420106aa:	4501                	li	a0,0
420106ac:	3718c0ef          	jal	4209d21c <time>
420106b0:	862e                	mv	a2,a1
420106b2:	00f10713          	addi	a4,sp,15
420106b6:	85aa                	mv	a1,a0
420106b8:	0814                	addi	a3,sp,16
420106ba:	19b10513          	addi	a0,sp,411
420106be:	29a9                	jal	42010b18 <timezone_utc_offset>
420106c0:	89aa                	mv	s3,a0
420106c2:	c53d                	beqz	a0,42010730 <time_sync_task+0x140>
420106c4:	46c2                	lw	a3,16(sp)
420106c6:	8652                	mv	a2,s4
420106c8:	00a8                	addi	a0,sp,72
420106ca:	41f6d793          	srai	a5,a3,0x1f
420106ce:	00d7c5b3          	xor	a1,a5,a3
420106d2:	8d9d                	sub	a1,a1,a5
420106d4:	03c00793          	li	a5,60
420106d8:	02f5d733          	divu	a4,a1,a5
420106dc:	fff6c693          	not	a3,a3
420106e0:	86fd                	srai	a3,a3,0x1f
420106e2:	8a89                	andi	a3,a3,2
420106e4:	02b68693          	addi	a3,a3,43
420106e8:	02f5f833          	remu	a6,a1,a5
420106ec:	02f777b3          	remu	a5,a4,a5
420106f0:	6705                	lui	a4,0x1
420106f2:	e1070713          	addi	a4,a4,-496 # e10 <CSR_UINTSTATUS+0x15f>
420106f6:	02e5d733          	divu	a4,a1,a4
420106fa:	02000593          	li	a1,32
420106fe:	70e8d0ef          	jal	4209de0c <snprintf>
42010702:	c881                	beqz	s1,42010712 <time_sync_task+0x122>
42010704:	102c                	addi	a1,sp,40
42010706:	00a8                	addi	a0,sp,72
42010708:	fe377097          	auipc	ra,0xfe377
4201070c:	f4a080e7          	jalr	-182(ra) # 40387652 <strcmp>
42010710:	cd19                	beqz	a0,4201072e <time_sync_task+0x13e>
42010712:	4605                	li	a2,1
42010714:	00ac                	addi	a1,sp,72
42010716:	8556                	mv	a0,s5
42010718:	27a8c0ef          	jal	4209c992 <setenv>
4201071c:	e911                	bnez	a0,42010730 <time_sync_task+0x140>
4201071e:	13c8d0ef          	jal	4209d85a <tzset>
42010722:	00ac                	addi	a1,sp,72
42010724:	1028                	addi	a0,sp,40
42010726:	fe377097          	auipc	ra,0xfe377
4201072a:	042080e7          	jalr	66(ra) # 40387768 <strcpy>
4201072e:	84ce                	mv	s1,s3
42010730:	a9dff0ef          	jal	420101cc <network_connected>
42010734:	c12d                	beqz	a0,42010796 <time_sync_task+0x1a6>
42010736:	c819                	beqz	s0,4201074c <time_sync_task+0x15c>
42010738:	1af10593          	addi	a1,sp,431
4201073c:	10e8                	addi	a0,sp,108
4201073e:	fe377097          	auipc	ra,0xfe377
42010742:	f14080e7          	jalr	-236(ra) # 40387652 <strcmp>
42010746:	c921                	beqz	a0,42010796 <time_sync_task+0x1a6>
42010748:	115210ef          	jal	4203205c <esp_netif_sntp_deinit>
4201074c:	1af10593          	addi	a1,sp,431
42010750:	10e8                	addi	a0,sp,108
42010752:	fe377097          	auipc	ra,0xfe377
42010756:	016080e7          	jalr	22(ra) # 40387768 <strcpy>
4201075a:	4785                	li	a5,1
4201075c:	c482                	sw	zero,72(sp)
4201075e:	04f105a3          	sb	a5,75(sp)
42010762:	478d                	li	a5,3
42010764:	cebe                	sw	a5,92(sp)
42010766:	06c14783          	lbu	a5,108(sp)
4201076a:	c882                	sw	zero,80(sp)
4201076c:	ca82                	sw	zero,84(sp)
4201076e:	cc82                	sw	zero,88(sp)
42010770:	d0ca                	sw	s2,96(sp)
42010772:	c79d                	beqz	a5,420107a0 <time_sync_task+0x1b0>
42010774:	10fc                	addi	a5,sp,108
42010776:	d2be                	sw	a5,100(sp)
42010778:	3c0b47b7          	lui	a5,0x3c0b4
4201077c:	96878793          	addi	a5,a5,-1688 # 3c0b3968 <_esp_libc_clock_array_end+0x3818>
42010780:	d4be                	sw	a5,104(sp)
42010782:	420107b7          	lui	a5,0x42010
42010786:	7aa78793          	addi	a5,a5,1962 # 420107aa <time_sync_notify>
4201078a:	00a8                	addi	a0,sp,72
4201078c:	c6be                	sw	a5,76(sp)
4201078e:	15b210ef          	jal	420320e8 <esp_netif_sntp_init>
42010792:	00153413          	seqz	s0,a0
42010796:	06400513          	li	a0,100
4201079a:	6cc9c0ef          	jal	420ace66 <vTaskDelay>
4201079e:	b5e1                	j	42010666 <time_sync_task+0x76>
420107a0:	3c0b47b7          	lui	a5,0x3c0b4
420107a4:	04078793          	addi	a5,a5,64 # 3c0b4040 <_esp_libc_clock_array_end+0x3ef0>
420107a8:	b7f9                	j	42010776 <time_sync_task+0x186>
