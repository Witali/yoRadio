
small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4201187e <advanced_page>:
4201187e:	cc010113          	addi	sp,sp,-832
42011882:	31712e23          	sw	s7,796(sp)
42011886:	8baa                	mv	s7,a0
42011888:	0868                	addi	a0,sp,28
4201188a:	32912a23          	sw	s1,820(sp)
4201188e:	33212823          	sw	s2,816(sp)
42011892:	33312623          	sw	s3,812(sp)
42011896:	33412423          	sw	s4,808(sp)
4201189a:	33512223          	sw	s5,804(sp)
4201189e:	33612023          	sw	s6,800(sp)
420118a2:	32112e23          	sw	ra,828(sp)
420118a6:	32812c23          	sw	s0,824(sp)
420118aa:	4481                	li	s1,0
420118ac:	c59fa0ef          	jal	4200c504 <settings_snapshot>
420118b0:	0d710b13          	addi	s6,sp,215
420118b4:	02700913          	li	s2,39
420118b8:	3c0b49b7          	lui	s3,0x3c0b4
420118bc:	3c0b4a37          	lui	s4,0x3c0b4
420118c0:	3c0b4ab7          	lui	s5,0x3c0b4
420118c4:	000b4403          	lbu	s0,0(s6)
420118c8:	ec31                	bnez	s0,42011924 <advanced_page+0xa6>
420118ca:	30048793          	addi	a5,s1,768
420118ce:	0818                	addi	a4,sp,16
420118d0:	00e784b3          	add	s1,a5,a4
420118d4:	3c0b45b7          	lui	a1,0x3c0b4
420118d8:	52458593          	addi	a1,a1,1316 # 3c0b4524 <_esp_libc_clock_array_end+0x43d4>
420118dc:	e6048c23          	sb	zero,-392(s1)
420118e0:	855e                	mv	a0,s7
420118e2:	16f270ef          	jal	42039250 <httpd_resp_set_type>
420118e6:	3c0eb5b7          	lui	a1,0x3c0eb
420118ea:	17b00613          	li	a2,379
420118ee:	1ec58593          	addi	a1,a1,492 # 3c0eb1ec <prefix.1>
420118f2:	855e                	mv	a0,s7
420118f4:	3b1270ef          	jal	420394a4 <httpd_resp_send_chunk>
420118f8:	c561                	beqz	a0,420119c0 <advanced_page+0x142>
420118fa:	33c12083          	lw	ra,828(sp)
420118fe:	33812403          	lw	s0,824(sp)
42011902:	33412483          	lw	s1,820(sp)
42011906:	33012903          	lw	s2,816(sp)
4201190a:	32c12983          	lw	s3,812(sp)
4201190e:	32812a03          	lw	s4,808(sp)
42011912:	32412a83          	lw	s5,804(sp)
42011916:	32012b03          	lw	s6,800(sp)
4201191a:	31c12b83          	lw	s7,796(sp)
4201191e:	34010113          	addi	sp,sp,832
42011922:	8082                	ret
42011924:	07240263          	beq	s0,s2,42011988 <advanced_page+0x10a>
42011928:	00896d63          	bltu	s2,s0,42011942 <advanced_page+0xc4>
4201192c:	02200793          	li	a5,34
42011930:	04f40f63          	beq	s0,a5,4201198e <advanced_page+0x110>
42011934:	02600793          	li	a5,38
42011938:	06f40063          	beq	s0,a5,42011998 <advanced_page+0x11a>
4201193c:	4581                	li	a1,0
4201193e:	4605                	li	a2,1
42011940:	a01d                	j	42011966 <advanced_page+0xe8>
42011942:	03c00793          	li	a5,60
42011946:	04f40e63          	beq	s0,a5,420119a2 <advanced_page+0x124>
4201194a:	03e00793          	li	a5,62
4201194e:	550a8593          	addi	a1,s5,1360 # 3c0b4550 <_esp_libc_clock_array_end+0x4400>
42011952:	fef415e3          	bne	s0,a5,4201193c <advanced_page+0xbe>
42011956:	852e                	mv	a0,a1
42011958:	c62e                	sw	a1,12(sp)
4201195a:	fdfef097          	auipc	ra,0xfdfef
4201195e:	b4e080e7          	jalr	-1202(ra) # 400004a8 <strlen>
42011962:	45b2                	lw	a1,12(sp)
42011964:	862a                	mv	a2,a0
42011966:	18600793          	li	a5,390
4201196a:	8f85                	sub	a5,a5,s1
4201196c:	04f67163          	bgeu	a2,a5,420119ae <advanced_page+0x130>
42011970:	0328                	addi	a0,sp,392
42011972:	9526                	add	a0,a0,s1
42011974:	c995                	beqz	a1,420119a8 <advanced_page+0x12a>
42011976:	c632                	sw	a2,12(sp)
42011978:	fe376097          	auipc	ra,0xfe376
4201197c:	8c2080e7          	jalr	-1854(ra) # 4038723a <memcpy>
42011980:	4632                	lw	a2,12(sp)
42011982:	94b2                	add	s1,s1,a2
42011984:	0b05                	addi	s6,s6,1
42011986:	bf3d                	j	420118c4 <advanced_page+0x46>
42011988:	54098593          	addi	a1,s3,1344 # 3c0b4540 <_esp_libc_clock_array_end+0x43f0>
4201198c:	b7e9                	j	42011956 <advanced_page+0xd8>
4201198e:	3c0b45b7          	lui	a1,0x3c0b4
42011992:	54858593          	addi	a1,a1,1352 # 3c0b4548 <_esp_libc_clock_array_end+0x43f8>
42011996:	b7c1                	j	42011956 <advanced_page+0xd8>
42011998:	3c0b45b7          	lui	a1,0x3c0b4
4201199c:	56058593          	addi	a1,a1,1376 # 3c0b4560 <_esp_libc_clock_array_end+0x4410>
420119a0:	bf5d                	j	42011956 <advanced_page+0xd8>
420119a2:	558a0593          	addi	a1,s4,1368 # 3c0b4558 <_esp_libc_clock_array_end+0x4408>
420119a6:	bf45                	j	42011956 <advanced_page+0xd8>
420119a8:	00850023          	sb	s0,0(a0)
420119ac:	bfd9                	j	42011982 <advanced_page+0x104>
420119ae:	3c0b4637          	lui	a2,0x3c0b4
420119b2:	56860613          	addi	a2,a2,1384 # 3c0b4568 <_esp_libc_clock_array_end+0x4418>
420119b6:	4581                	li	a1,0
420119b8:	855e                	mv	a0,s7
420119ba:	4fd270ef          	jal	420396b6 <httpd_resp_send_err>
420119be:	bf35                	j	420118fa <advanced_page+0x7c>
420119c0:	18814783          	lbu	a5,392(sp)
420119c4:	e38d                	bnez	a5,420119e6 <advanced_page+0x168>
420119c6:	3c0eb5b7          	lui	a1,0x3c0eb
420119ca:	72d00613          	li	a2,1837
420119ce:	abc58593          	addi	a1,a1,-1348 # 3c0eaabc <suffix.0>
420119d2:	855e                	mv	a0,s7
420119d4:	2d1270ef          	jal	420394a4 <httpd_resp_send_chunk>
420119d8:	f10d                	bnez	a0,420118fa <advanced_page+0x7c>
420119da:	4601                	li	a2,0
420119dc:	4581                	li	a1,0
420119de:	855e                	mv	a0,s7
420119e0:	2c5270ef          	jal	420394a4 <httpd_resp_send_chunk>
420119e4:	bf19                	j	420118fa <advanced_page+0x7c>
420119e6:	0328                	addi	a0,sp,392
420119e8:	fdfef097          	auipc	ra,0xfdfef
420119ec:	ac0080e7          	jalr	-1344(ra) # 400004a8 <strlen>
420119f0:	862a                	mv	a2,a0
420119f2:	032c                	addi	a1,sp,392
420119f4:	855e                	mv	a0,s7
420119f6:	2af270ef          	jal	420394a4 <httpd_resp_send_chunk>
420119fa:	f00510e3          	bnez	a0,420118fa <advanced_page+0x7c>
420119fe:	b7e1                	j	420119c6 <advanced_page+0x148>
