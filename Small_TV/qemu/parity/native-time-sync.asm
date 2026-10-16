
small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420107c8 <time_sync_notify>:
420107c8:	3fcb47b7          	lui	a5,0x3fcb4
420107cc:	4705                	li	a4,1
420107ce:	92078793          	addi	a5,a5,-1760 # 3fcb3920 <time_synced>
420107d2:	0310000f          	fence	rw,w
420107d6:	00e78023          	sb	a4,0(a5)
420107da:	8082                	ret


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420107dc <services_time_synced>:
420107dc:	3fcb47b7          	lui	a5,0x3fcb4
420107e0:	92078793          	addi	a5,a5,-1760 # 3fcb3920 <time_synced>
420107e4:	00078503          	lb	a0,0(a5)
420107e8:	0230000f          	fence	r,rw
420107ec:	0ff57513          	zext.b	a0,a0
420107f0:	8082                	ret


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420107f2 <services_local_time>:
420107f2:	1101                	addi	sp,sp,-32
420107f4:	cc22                	sw	s0,24(sp)
420107f6:	c42e                	sw	a1,8(sp)
420107f8:	c632                	sw	a2,12(sp)
420107fa:	c236                	sw	a3,4(sp)
420107fc:	ce06                	sw	ra,28(sp)
420107fe:	842a                	mv	s0,a0
42010800:	fddff0ef          	jal	420107dc <services_time_synced>
42010804:	4692                	lw	a3,4(sp)
42010806:	45a2                	lw	a1,8(sp)
42010808:	4632                	lw	a2,12(sp)
4201080a:	c511                	beqz	a0,42010816 <services_local_time+0x24>
4201080c:	8522                	mv	a0,s0
4201080e:	4462                	lw	s0,24(sp)
42010810:	40f2                	lw	ra,28(sp)
42010812:	6105                	addi	sp,sp,32
42010814:	a331                	j	42010d20 <timezone_local_time>
42010816:	40f2                	lw	ra,28(sp)
42010818:	4462                	lw	s0,24(sp)
4201081a:	6105                	addi	sp,sp,32
4201081c:	8082                	ret


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4201060e <time_sync_task>:
4201060e:	d8010113          	addi	sp,sp,-640
42010612:	04100613          	li	a2,65
42010616:	4581                	li	a1,0
42010618:	10e8                	addi	a0,sp,108
4201061a:	26112e23          	sw	ra,636(sp)
4201061e:	26812c23          	sw	s0,632(sp)
42010622:	26912a23          	sw	s1,628(sp)
42010626:	27212823          	sw	s2,624(sp)
4201062a:	27412423          	sw	s4,616(sp)
4201062e:	27512223          	sw	s5,612(sp)
42010632:	27312623          	sw	s3,620(sp)
42010636:	fdff0097          	auipc	ra,0xfdff0
4201063a:	e52080e7          	jalr	-430(ra) # 40000488 <memset>
4201063e:	04100613          	li	a2,65
42010642:	4581                	li	a1,0
42010644:	1908                	addi	a0,sp,176
42010646:	ca02                	sw	zero,20(sp)
42010648:	cc02                	sw	zero,24(sp)
4201064a:	ce02                	sw	zero,28(sp)
4201064c:	d002                	sw	zero,32(sp)
4201064e:	d202                	sw	zero,36(sp)
42010650:	fdff0097          	auipc	ra,0xfdff0
42010654:	e38080e7          	jalr	-456(ra) # 40000488 <memset>
42010658:	02000613          	li	a2,32
4201065c:	4581                	li	a1,0
4201065e:	1028                	addi	a0,sp,40
42010660:	fdff0097          	auipc	ra,0xfdff0
42010664:	e28080e7          	jalr	-472(ra) # 40000488 <memset>
42010668:	3c0b47b7          	lui	a5,0x3c0b4
4201066c:	05078a13          	addi	s4,a5,80 # 3c0b4050 <_esp_libc_clock_array_end+0x3f00>
42010670:	3c0b4937          	lui	s2,0x3c0b4
42010674:	3c0b47b7          	lui	a5,0x3c0b4
42010678:	4401                	li	s0,0
4201067a:	4481                	li	s1,0
4201067c:	06478a93          	addi	s5,a5,100 # 3c0b4064 <_esp_libc_clock_array_end+0x3f14>
42010680:	06890913          	addi	s2,s2,104 # 3c0b4068 <_esp_libc_clock_array_end+0x3f18>
42010684:	19c8                	addi	a0,sp,244
42010686:	e0bfb0ef          	jal	4200c490 <settings_snapshot>
4201068a:	084c                	addi	a1,sp,20
4201068c:	19b10513          	addi	a0,sp,411
42010690:	fe377097          	auipc	ra,0xfe377
42010694:	fc2080e7          	jalr	-62(ra) # 40387652 <strcmp>
42010698:	e909                	bnez	a0,420106aa <time_sync_task+0x9c>
4201069a:	190c                	addi	a1,sp,176
4201069c:	15a10513          	addi	a0,sp,346
420106a0:	fe377097          	auipc	ra,0xfe377
420106a4:	fb2080e7          	jalr	-78(ra) # 40387652 <strcmp>
420106a8:	c105                	beqz	a0,420106c8 <time_sync_task+0xba>
420106aa:	19b10593          	addi	a1,sp,411
420106ae:	0848                	addi	a0,sp,20
420106b0:	fe377097          	auipc	ra,0xfe377
420106b4:	0b8080e7          	jalr	184(ra) # 40387768 <strcpy>
420106b8:	15a10593          	addi	a1,sp,346
420106bc:	1908                	addi	a0,sp,176
420106be:	fe377097          	auipc	ra,0xfe377
420106c2:	0aa080e7          	jalr	170(ra) # 40387768 <strcpy>
420106c6:	4481                	li	s1,0
420106c8:	4501                	li	a0,0
420106ca:	3718c0ef          	jal	4209d23a <time>
420106ce:	862e                	mv	a2,a1
420106d0:	00f10713          	addi	a4,sp,15
420106d4:	85aa                	mv	a1,a0
420106d6:	0814                	addi	a3,sp,16
420106d8:	19b10513          	addi	a0,sp,411
420106dc:	29a9                	jal	42010b36 <timezone_utc_offset>
420106de:	89aa                	mv	s3,a0
420106e0:	c53d                	beqz	a0,4201074e <time_sync_task+0x140>
420106e2:	46c2                	lw	a3,16(sp)
420106e4:	8652                	mv	a2,s4
420106e6:	00a8                	addi	a0,sp,72
420106e8:	41f6d793          	srai	a5,a3,0x1f
420106ec:	00d7c5b3          	xor	a1,a5,a3
420106f0:	8d9d                	sub	a1,a1,a5
420106f2:	03c00793          	li	a5,60
420106f6:	02f5d733          	divu	a4,a1,a5
420106fa:	fff6c693          	not	a3,a3
420106fe:	86fd                	srai	a3,a3,0x1f
42010700:	8a89                	andi	a3,a3,2
42010702:	02b68693          	addi	a3,a3,43
42010706:	02f5f833          	remu	a6,a1,a5
4201070a:	02f777b3          	remu	a5,a4,a5
4201070e:	6705                	lui	a4,0x1
42010710:	e1070713          	addi	a4,a4,-496 # e10 <CSR_UINTSTATUS+0x15f>
42010714:	02e5d733          	divu	a4,a1,a4
42010718:	02000593          	li	a1,32
4201071c:	70e8d0ef          	jal	4209de2a <snprintf>
42010720:	c881                	beqz	s1,42010730 <time_sync_task+0x122>
42010722:	102c                	addi	a1,sp,40
42010724:	00a8                	addi	a0,sp,72
42010726:	fe377097          	auipc	ra,0xfe377
4201072a:	f2c080e7          	jalr	-212(ra) # 40387652 <strcmp>
4201072e:	cd19                	beqz	a0,4201074c <time_sync_task+0x13e>
42010730:	4605                	li	a2,1
42010732:	00ac                	addi	a1,sp,72
42010734:	8556                	mv	a0,s5
42010736:	27a8c0ef          	jal	4209c9b0 <setenv>
4201073a:	e911                	bnez	a0,4201074e <time_sync_task+0x140>
4201073c:	13c8d0ef          	jal	4209d878 <tzset>
42010740:	00ac                	addi	a1,sp,72
42010742:	1028                	addi	a0,sp,40
42010744:	fe377097          	auipc	ra,0xfe377
42010748:	024080e7          	jalr	36(ra) # 40387768 <strcpy>
4201074c:	84ce                	mv	s1,s3
4201074e:	a9dff0ef          	jal	420101ea <network_connected>
42010752:	c12d                	beqz	a0,420107b4 <time_sync_task+0x1a6>
42010754:	c819                	beqz	s0,4201076a <time_sync_task+0x15c>
42010756:	1af10593          	addi	a1,sp,431
4201075a:	10e8                	addi	a0,sp,108
4201075c:	fe377097          	auipc	ra,0xfe377
42010760:	ef6080e7          	jalr	-266(ra) # 40387652 <strcmp>
42010764:	c921                	beqz	a0,420107b4 <time_sync_task+0x1a6>
42010766:	115210ef          	jal	4203207a <esp_netif_sntp_deinit>
4201076a:	1af10593          	addi	a1,sp,431
4201076e:	10e8                	addi	a0,sp,108
42010770:	fe377097          	auipc	ra,0xfe377
42010774:	ff8080e7          	jalr	-8(ra) # 40387768 <strcpy>
42010778:	4785                	li	a5,1
4201077a:	c482                	sw	zero,72(sp)
4201077c:	04f105a3          	sb	a5,75(sp)
42010780:	478d                	li	a5,3
42010782:	cebe                	sw	a5,92(sp)
42010784:	06c14783          	lbu	a5,108(sp)
42010788:	c882                	sw	zero,80(sp)
4201078a:	ca82                	sw	zero,84(sp)
4201078c:	cc82                	sw	zero,88(sp)
4201078e:	d0ca                	sw	s2,96(sp)
42010790:	c79d                	beqz	a5,420107be <time_sync_task+0x1b0>
42010792:	10fc                	addi	a5,sp,108
42010794:	d2be                	sw	a5,100(sp)
42010796:	3c0b47b7          	lui	a5,0x3c0b4
4201079a:	96878793          	addi	a5,a5,-1688 # 3c0b3968 <_esp_libc_clock_array_end+0x3818>
4201079e:	d4be                	sw	a5,104(sp)
420107a0:	420107b7          	lui	a5,0x42010
420107a4:	7c878793          	addi	a5,a5,1992 # 420107c8 <time_sync_notify>
420107a8:	00a8                	addi	a0,sp,72
420107aa:	c6be                	sw	a5,76(sp)
420107ac:	15b210ef          	jal	42032106 <esp_netif_sntp_init>
420107b0:	00153413          	seqz	s0,a0
420107b4:	06400513          	li	a0,100
420107b8:	6cc9c0ef          	jal	420ace84 <vTaskDelay>
420107bc:	b5e1                	j	42010684 <time_sync_task+0x76>
420107be:	3c0b47b7          	lui	a5,0x3c0b4
420107c2:	04078793          	addi	a5,a5,64 # 3c0b4040 <_esp_libc_clock_array_end+0x3ef0>
420107c6:	b7f9                	j	42010794 <time_sync_task+0x186>
