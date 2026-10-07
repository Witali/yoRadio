
C:\Work\yoRadio\.worktree\aac-storage18\idf\esp32c3-oled-native\build-aac-asymmetric-production\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42021868 <__wrap_compact5_sbr_dec>:
42021868:	72f5                	lui	t0,0xffffd
4202186a:	1101                	addi	sp,sp,-32
4202186c:	7e028293          	addi	t0,t0,2016 # ffffd7e0 <SYSTEM+0x9ff3d7e0>
42021870:	c05a                	sw	s6,0(sp)
42021872:	cc22                	sw	s0,24(sp)
42021874:	ca26                	sw	s1,20(sp)
42021876:	c84a                	sw	s2,16(sp)
42021878:	c64e                	sw	s3,12(sp)
4202187a:	c452                	sw	s4,8(sp)
4202187c:	c256                	sw	s5,4(sp)
4202187e:	ce06                	sw	ra,28(sp)
42021880:	9116                	add	sp,sp,t0
42021882:	c03a                	sw	a4,0(sp)
42021884:	8a3e                	mv	s4,a5
42021886:	84aa                	mv	s1,a0
42021888:	892e                	mv	s2,a1
4202188a:	8432                	mv	s0,a2
4202188c:	89b6                	mv	s3,a3
4202188e:	8ac2                	mv	s5,a6
42021890:	8b46                	mv	s6,a7
42021892:	f7bf00ef          	jal	4201280c <aac_compact_owner_high_context>
42021896:	411c                	lw	a5,0(a0)
42021898:	4702                	lw	a4,0(sp)
4202189a:	1c079f63          	bnez	a5,42021a78 <__wrap_compact5_sbr_dec+0x210>
4202189e:	c100                	sw	s0,0(a0)
420218a0:	435c                	lw	a5,4(a4)
420218a2:	660d                	lui	a2,0x3
420218a4:	00052623          	sw	zero,12(a0)
420218a8:	00f037b3          	snez	a5,a5
420218ac:	00f50223          	sb	a5,4(a0)
420218b0:	00052423          	sw	zero,8(a0)
420218b4:	51ab77b7          	lui	a5,0x51ab7
420218b8:	80c60613          	addi	a2,a2,-2036 # 280c <CSR_UINTSTATUS+0x1b5b>
420218bc:	080c                	addi	a1,sp,16
420218be:	fa842683          	lw	a3,-88(s0)
420218c2:	3cd78793          	addi	a5,a5,973 # 51ab73cd <_rtc_reserved_end+0x1ab53cd>
420218c6:	962e                	add	a2,a2,a1
420218c8:	cc3e                	sw	a5,24(sp)
420218ca:	c21c                	sw	a5,0(a2)
420218cc:	8e2a                	mv	t3,a0
420218ce:	12069a63          	bnez	a3,42021a02 <__wrap_compact5_sbr_dec+0x19a>
420218d2:	fac42783          	lw	a5,-84(s0)
420218d6:	12079663          	bnez	a5,42021a02 <__wrap_compact5_sbr_dec+0x19a>
420218da:	6305                	lui	t1,0x1
420218dc:	1b030313          	addi	t1,t1,432 # 11b0 <CSR_UINTSTATUS+0x4ff>
420218e0:	9322                	add	t1,t1,s0
420218e2:	869a                	mv	a3,t1
420218e4:	40030613          	addi	a2,t1,1024
420218e8:	087c                	addi	a5,sp,28
420218ea:	468c                	lw	a1,8(a3)
420218ec:	0006a803          	lw	a6,0(a3)
420218f0:	42c8                	lw	a0,4(a3)
420218f2:	c78c                	sw	a1,8(a5)
420218f4:	0107a023          	sw	a6,0(a5)
420218f8:	c3c8                	sw	a0,4(a5)
420218fa:	46cc                	lw	a1,12(a3)
420218fc:	06c1                	addi	a3,a3,16
420218fe:	07c1                	addi	a5,a5,16
42021900:	feb7ae23          	sw	a1,-4(a5)
42021904:	fec693e3          	bne	a3,a2,420218ea <__wrap_compact5_sbr_dec+0x82>
42021908:	6f05                	lui	t5,0x1
4202190a:	5b0f0f13          	addi	t5,t5,1456 # 15b0 <CSR_UINTSTATUS+0x8ff>
4202190e:	6785                	lui	a5,0x1
42021910:	9f22                	add	t5,t5,s0
42021912:	41c78793          	addi	a5,a5,1052 # 141c <CSR_UINTSTATUS+0x76b>
42021916:	86fa                	mv	a3,t5
42021918:	400f0613          	addi	a2,t5,1024
4202191c:	978a                	add	a5,a5,sp
4202191e:	468c                	lw	a1,8(a3)
42021920:	0006a803          	lw	a6,0(a3)
42021924:	42c8                	lw	a0,4(a3)
42021926:	c78c                	sw	a1,8(a5)
42021928:	0107a023          	sw	a6,0(a5)
4202192c:	c3c8                	sw	a0,4(a5)
4202192e:	46cc                	lw	a1,12(a3)
42021930:	06c1                	addi	a3,a3,16
42021932:	07c1                	addi	a5,a5,16
42021934:	feb7ae23          	sw	a1,-4(a5)
42021938:	fec693e3          	bne	a3,a2,4202191e <__wrap_compact5_sbr_dec+0xb6>
4202193c:	6605                	lui	a2,0x1
4202193e:	01810293          	addi	t0,sp,24
42021942:	40460613          	addi	a2,a2,1028 # 1404 <CSR_UINTSTATUS+0x753>
42021946:	01c10e93          	addi	t4,sp,28
4202194a:	9616                	add	a2,a2,t0
4202194c:	408e8fb3          	sub	t6,t4,s0
42021950:	8e01                	sub	a2,a2,s0
42021952:	87d2                	mv	a5,s4
42021954:	86ce                	mv	a3,s3
42021956:	fac42623          	sw	a2,-84(s0)
4202195a:	88da                	mv	a7,s6
4202195c:	8856                	mv	a6,s5
4202195e:	85ca                	mv	a1,s2
42021960:	8526                	mv	a0,s1
42021962:	fbf42423          	sw	t6,-88(s0)
42021966:	8622                	mv	a2,s0
42021968:	c672                	sw	t3,12(sp)
4202196a:	c47a                	sw	t5,8(sp)
4202196c:	c21a                	sw	t1,4(sp)
4202196e:	c076                	sw	t4,0(sp)
42021970:	62c010ef          	jal	42022f9c <compact5_sbr_dec>
42021974:	4e32                	lw	t3,12(sp)
42021976:	4789                	li	a5,2
42021978:	4e82                	lw	t4,0(sp)
4202197a:	004e4683          	lbu	a3,4(t3)
4202197e:	008e2703          	lw	a4,8(t3)
42021982:	4312                	lw	t1,4(sp)
42021984:	8f95                	sub	a5,a5,a3
42021986:	4f22                	lw	t5,8(sp)
42021988:	10f71a63          	bne	a4,a5,42021a9c <__wrap_compact5_sbr_dec+0x234>
4202198c:	00ce2783          	lw	a5,12(t3)
42021990:	12e79863          	bne	a5,a4,42021ac0 <__wrap_compact5_sbr_dec+0x258>
42021994:	4662                	lw	a2,24(sp)
42021996:	51ab77b7          	lui	a5,0x51ab7
4202199a:	3cd78793          	addi	a5,a5,973 # 51ab73cd <_rtc_reserved_end+0x1ab53cd>
4202199e:	0af61b63          	bne	a2,a5,42021a54 <__wrap_compact5_sbr_dec+0x1ec>
420219a2:	678d                	lui	a5,0x3
420219a4:	0818                	addi	a4,sp,16
420219a6:	80c78793          	addi	a5,a5,-2036 # 280c <CSR_UINTSTATUS+0x1b5b>
420219aa:	97ba                	add	a5,a5,a4
420219ac:	438c                	lw	a1,0(a5)
420219ae:	8776                	mv	a4,t4
420219b0:	879a                	mv	a5,t1
420219b2:	41c10693          	addi	a3,sp,1052
420219b6:	08c59f63          	bne	a1,a2,42021a54 <__wrap_compact5_sbr_dec+0x1ec>
420219ba:	4710                	lw	a2,8(a4)
420219bc:	4308                	lw	a0,0(a4)
420219be:	434c                	lw	a1,4(a4)
420219c0:	c790                	sw	a2,8(a5)
420219c2:	c388                	sw	a0,0(a5)
420219c4:	c3cc                	sw	a1,4(a5)
420219c6:	4750                	lw	a2,12(a4)
420219c8:	0741                	addi	a4,a4,16
420219ca:	07c1                	addi	a5,a5,16
420219cc:	fec7ae23          	sw	a2,-4(a5)
420219d0:	fed715e3          	bne	a4,a3,420219ba <__wrap_compact5_sbr_dec+0x152>
420219d4:	004e4783          	lbu	a5,4(t3)
420219d8:	c7b9                	beqz	a5,42021a26 <__wrap_compact5_sbr_dec+0x1be>
420219da:	fa042623          	sw	zero,-84(s0)
420219de:	fa042423          	sw	zero,-88(s0)
420219e2:	628d                	lui	t0,0x3
420219e4:	000e2023          	sw	zero,0(t3)
420219e8:	82028293          	addi	t0,t0,-2016 # 2820 <CSR_UINTSTATUS+0x1b6f>
420219ec:	9116                	add	sp,sp,t0
420219ee:	40f2                	lw	ra,28(sp)
420219f0:	4462                	lw	s0,24(sp)
420219f2:	44d2                	lw	s1,20(sp)
420219f4:	4942                	lw	s2,16(sp)
420219f6:	49b2                	lw	s3,12(sp)
420219f8:	4a22                	lw	s4,8(sp)
420219fa:	4a92                	lw	s5,4(sp)
420219fc:	4b02                	lw	s6,0(sp)
420219fe:	6105                	addi	sp,sp,32
42021a00:	8082                	ret
42021a02:	3c12a6b7          	lui	a3,0x3c12a
42021a06:	3c140637          	lui	a2,0x3c140
42021a0a:	3c12a537          	lui	a0,0x3c12a
42021a0e:	0d468693          	addi	a3,a3,212 # 3c12a0d4 <_esp_trace_encoder_array_end+0x9fb4>
42021a12:	1a860613          	addi	a2,a2,424 # 3c1401a8 <__func__.0>
42021a16:	f3450513          	addi	a0,a0,-204 # 3c129f34 <_esp_trace_encoder_array_end+0x9e14>
42021a1a:	08200593          	li	a1,130
42021a1e:	fe365097          	auipc	ra,0xfe365
42021a22:	808080e7          	jalr	-2040(ra) # 40386226 <__assert_func>
42021a26:	6785                	lui	a5,0x1
42021a28:	41c78793          	addi	a5,a5,1052 # 141c <CSR_UINTSTATUS+0x76b>
42021a2c:	978a                	add	a5,a5,sp
42021a2e:	40078713          	addi	a4,a5,1024
42021a32:	4794                	lw	a3,8(a5)
42021a34:	438c                	lw	a1,0(a5)
42021a36:	43d0                	lw	a2,4(a5)
42021a38:	00df2423          	sw	a3,8(t5)
42021a3c:	00bf2023          	sw	a1,0(t5)
42021a40:	00cf2223          	sw	a2,4(t5)
42021a44:	47d4                	lw	a3,12(a5)
42021a46:	07c1                	addi	a5,a5,16
42021a48:	0f41                	addi	t5,t5,16
42021a4a:	fedf2e23          	sw	a3,-4(t5)
42021a4e:	fee792e3          	bne	a5,a4,42021a32 <__wrap_compact5_sbr_dec+0x1ca>
42021a52:	b761                	j	420219da <__wrap_compact5_sbr_dec+0x172>
42021a54:	3c12a6b7          	lui	a3,0x3c12a
42021a58:	3c140637          	lui	a2,0x3c140
42021a5c:	3c12a537          	lui	a0,0x3c12a
42021a60:	16868693          	addi	a3,a3,360 # 3c12a168 <_esp_trace_encoder_array_end+0xa048>
42021a64:	1a860613          	addi	a2,a2,424 # 3c1401a8 <__func__.0>
42021a68:	f3450513          	addi	a0,a0,-204 # 3c129f34 <_esp_trace_encoder_array_end+0x9e14>
42021a6c:	0ad00593          	li	a1,173
42021a70:	fe364097          	auipc	ra,0xfe364
42021a74:	7b6080e7          	jalr	1974(ra) # 40386226 <__assert_func>
42021a78:	3c12a6b7          	lui	a3,0x3c12a
42021a7c:	3c140637          	lui	a2,0x3c140
42021a80:	3c12a537          	lui	a0,0x3c12a
42021a84:	0c468693          	addi	a3,a3,196 # 3c12a0c4 <_esp_trace_encoder_array_end+0x9fa4>
42021a88:	1a860613          	addi	a2,a2,424 # 3c1401a8 <__func__.0>
42021a8c:	f3450513          	addi	a0,a0,-204 # 3c129f34 <_esp_trace_encoder_array_end+0x9e14>
42021a90:	07400593          	li	a1,116
42021a94:	fe364097          	auipc	ra,0xfe364
42021a98:	792080e7          	jalr	1938(ra) # 40386226 <__assert_func>
42021a9c:	3c12a6b7          	lui	a3,0x3c12a
42021aa0:	3c140637          	lui	a2,0x3c140
42021aa4:	3c12a537          	lui	a0,0x3c12a
42021aa8:	11068693          	addi	a3,a3,272 # 3c12a110 <_esp_trace_encoder_array_end+0x9ff0>
42021aac:	1a860613          	addi	a2,a2,424 # 3c1401a8 <__func__.0>
42021ab0:	f3450513          	addi	a0,a0,-204 # 3c129f34 <_esp_trace_encoder_array_end+0x9e14>
42021ab4:	0aa00593          	li	a1,170
42021ab8:	fe364097          	auipc	ra,0xfe364
42021abc:	76e080e7          	jalr	1902(ra) # 40386226 <__assert_func>
42021ac0:	3c12a6b7          	lui	a3,0x3c12a
42021ac4:	3c140637          	lui	a2,0x3c140
42021ac8:	3c12a537          	lui	a0,0x3c12a
42021acc:	13c68693          	addi	a3,a3,316 # 3c12a13c <_esp_trace_encoder_array_end+0xa01c>
42021ad0:	1a860613          	addi	a2,a2,424 # 3c1401a8 <__func__.0>
42021ad4:	f3450513          	addi	a0,a0,-204 # 3c129f34 <_esp_trace_encoder_array_end+0x9e14>
42021ad8:	0ab00593          	li	a1,171
42021adc:	fe364097          	auipc	ra,0xfe364
42021ae0:	74a080e7          	jalr	1866(ra) # 40386226 <__assert_func>
