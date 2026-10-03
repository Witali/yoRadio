
C:\Work\yoRadio\.worktree\aac-storage18\idf\esp32c3-oled-native\build-aac-low-production\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42021854 <__wrap_compact5_sbr_dec>:
42021854:	72f5                	lui	t0,0xffffd
42021856:	1101                	addi	sp,sp,-32
42021858:	7e028293          	addi	t0,t0,2016 # ffffd7e0 <SYSTEM+0x9ff3d7e0>
4202185c:	c05a                	sw	s6,0(sp)
4202185e:	cc22                	sw	s0,24(sp)
42021860:	ca26                	sw	s1,20(sp)
42021862:	c84a                	sw	s2,16(sp)
42021864:	c64e                	sw	s3,12(sp)
42021866:	c452                	sw	s4,8(sp)
42021868:	c256                	sw	s5,4(sp)
4202186a:	ce06                	sw	ra,28(sp)
4202186c:	9116                	add	sp,sp,t0
4202186e:	c03a                	sw	a4,0(sp)
42021870:	8a3e                	mv	s4,a5
42021872:	84aa                	mv	s1,a0
42021874:	892e                	mv	s2,a1
42021876:	8432                	mv	s0,a2
42021878:	89b6                	mv	s3,a3
4202187a:	8ac2                	mv	s5,a6
4202187c:	8b46                	mv	s6,a7
4202187e:	f8ff00ef          	jal	4201280c <aac_compact_owner_high_context>
42021882:	411c                	lw	a5,0(a0)
42021884:	4702                	lw	a4,0(sp)
42021886:	1c079f63          	bnez	a5,42021a64 <__wrap_compact5_sbr_dec+0x210>
4202188a:	c100                	sw	s0,0(a0)
4202188c:	435c                	lw	a5,4(a4)
4202188e:	660d                	lui	a2,0x3
42021890:	00052623          	sw	zero,12(a0)
42021894:	00f037b3          	snez	a5,a5
42021898:	00f50223          	sb	a5,4(a0)
4202189c:	00052423          	sw	zero,8(a0)
420218a0:	51ab77b7          	lui	a5,0x51ab7
420218a4:	80c60613          	addi	a2,a2,-2036 # 280c <CSR_UINTSTATUS+0x1b5b>
420218a8:	080c                	addi	a1,sp,16
420218aa:	ff842683          	lw	a3,-8(s0)
420218ae:	3cd78793          	addi	a5,a5,973 # 51ab73cd <_rtc_reserved_end+0x1ab53cd>
420218b2:	962e                	add	a2,a2,a1
420218b4:	cc3e                	sw	a5,24(sp)
420218b6:	c21c                	sw	a5,0(a2)
420218b8:	8e2a                	mv	t3,a0
420218ba:	12069a63          	bnez	a3,420219ee <__wrap_compact5_sbr_dec+0x19a>
420218be:	ffc42783          	lw	a5,-4(s0)
420218c2:	12079663          	bnez	a5,420219ee <__wrap_compact5_sbr_dec+0x19a>
420218c6:	6305                	lui	t1,0x1
420218c8:	1b030313          	addi	t1,t1,432 # 11b0 <CSR_UINTSTATUS+0x4ff>
420218cc:	9322                	add	t1,t1,s0
420218ce:	869a                	mv	a3,t1
420218d0:	40030613          	addi	a2,t1,1024
420218d4:	087c                	addi	a5,sp,28
420218d6:	468c                	lw	a1,8(a3)
420218d8:	0006a803          	lw	a6,0(a3)
420218dc:	42c8                	lw	a0,4(a3)
420218de:	c78c                	sw	a1,8(a5)
420218e0:	0107a023          	sw	a6,0(a5)
420218e4:	c3c8                	sw	a0,4(a5)
420218e6:	46cc                	lw	a1,12(a3)
420218e8:	06c1                	addi	a3,a3,16
420218ea:	07c1                	addi	a5,a5,16
420218ec:	feb7ae23          	sw	a1,-4(a5)
420218f0:	fec693e3          	bne	a3,a2,420218d6 <__wrap_compact5_sbr_dec+0x82>
420218f4:	6f05                	lui	t5,0x1
420218f6:	5b0f0f13          	addi	t5,t5,1456 # 15b0 <CSR_UINTSTATUS+0x8ff>
420218fa:	6785                	lui	a5,0x1
420218fc:	9f22                	add	t5,t5,s0
420218fe:	41c78793          	addi	a5,a5,1052 # 141c <CSR_UINTSTATUS+0x76b>
42021902:	86fa                	mv	a3,t5
42021904:	400f0613          	addi	a2,t5,1024
42021908:	978a                	add	a5,a5,sp
4202190a:	468c                	lw	a1,8(a3)
4202190c:	0006a803          	lw	a6,0(a3)
42021910:	42c8                	lw	a0,4(a3)
42021912:	c78c                	sw	a1,8(a5)
42021914:	0107a023          	sw	a6,0(a5)
42021918:	c3c8                	sw	a0,4(a5)
4202191a:	46cc                	lw	a1,12(a3)
4202191c:	06c1                	addi	a3,a3,16
4202191e:	07c1                	addi	a5,a5,16
42021920:	feb7ae23          	sw	a1,-4(a5)
42021924:	fec693e3          	bne	a3,a2,4202190a <__wrap_compact5_sbr_dec+0xb6>
42021928:	6605                	lui	a2,0x1
4202192a:	01810293          	addi	t0,sp,24
4202192e:	40460613          	addi	a2,a2,1028 # 1404 <CSR_UINTSTATUS+0x753>
42021932:	01c10e93          	addi	t4,sp,28
42021936:	9616                	add	a2,a2,t0
42021938:	408e8fb3          	sub	t6,t4,s0
4202193c:	8e01                	sub	a2,a2,s0
4202193e:	87d2                	mv	a5,s4
42021940:	86ce                	mv	a3,s3
42021942:	fec42e23          	sw	a2,-4(s0)
42021946:	88da                	mv	a7,s6
42021948:	8856                	mv	a6,s5
4202194a:	85ca                	mv	a1,s2
4202194c:	8526                	mv	a0,s1
4202194e:	fff42c23          	sw	t6,-8(s0)
42021952:	8622                	mv	a2,s0
42021954:	c672                	sw	t3,12(sp)
42021956:	c47a                	sw	t5,8(sp)
42021958:	c21a                	sw	t1,4(sp)
4202195a:	c076                	sw	t4,0(sp)
4202195c:	6f0010ef          	jal	4202304c <compact5_sbr_dec>
42021960:	4e32                	lw	t3,12(sp)
42021962:	4789                	li	a5,2
42021964:	4e82                	lw	t4,0(sp)
42021966:	004e4683          	lbu	a3,4(t3)
4202196a:	008e2703          	lw	a4,8(t3)
4202196e:	4312                	lw	t1,4(sp)
42021970:	8f95                	sub	a5,a5,a3
42021972:	4f22                	lw	t5,8(sp)
42021974:	10f71a63          	bne	a4,a5,42021a88 <__wrap_compact5_sbr_dec+0x234>
42021978:	00ce2783          	lw	a5,12(t3)
4202197c:	12e79863          	bne	a5,a4,42021aac <__wrap_compact5_sbr_dec+0x258>
42021980:	4662                	lw	a2,24(sp)
42021982:	51ab77b7          	lui	a5,0x51ab7
42021986:	3cd78793          	addi	a5,a5,973 # 51ab73cd <_rtc_reserved_end+0x1ab53cd>
4202198a:	0af61b63          	bne	a2,a5,42021a40 <__wrap_compact5_sbr_dec+0x1ec>
4202198e:	678d                	lui	a5,0x3
42021990:	0818                	addi	a4,sp,16
42021992:	80c78793          	addi	a5,a5,-2036 # 280c <CSR_UINTSTATUS+0x1b5b>
42021996:	97ba                	add	a5,a5,a4
42021998:	438c                	lw	a1,0(a5)
4202199a:	8776                	mv	a4,t4
4202199c:	879a                	mv	a5,t1
4202199e:	41c10693          	addi	a3,sp,1052
420219a2:	08c59f63          	bne	a1,a2,42021a40 <__wrap_compact5_sbr_dec+0x1ec>
420219a6:	4710                	lw	a2,8(a4)
420219a8:	4308                	lw	a0,0(a4)
420219aa:	434c                	lw	a1,4(a4)
420219ac:	c790                	sw	a2,8(a5)
420219ae:	c388                	sw	a0,0(a5)
420219b0:	c3cc                	sw	a1,4(a5)
420219b2:	4750                	lw	a2,12(a4)
420219b4:	0741                	addi	a4,a4,16
420219b6:	07c1                	addi	a5,a5,16
420219b8:	fec7ae23          	sw	a2,-4(a5)
420219bc:	fed715e3          	bne	a4,a3,420219a6 <__wrap_compact5_sbr_dec+0x152>
420219c0:	004e4783          	lbu	a5,4(t3)
420219c4:	c7b9                	beqz	a5,42021a12 <__wrap_compact5_sbr_dec+0x1be>
420219c6:	fe042e23          	sw	zero,-4(s0)
420219ca:	fe042c23          	sw	zero,-8(s0)
420219ce:	628d                	lui	t0,0x3
420219d0:	000e2023          	sw	zero,0(t3)
420219d4:	82028293          	addi	t0,t0,-2016 # 2820 <CSR_UINTSTATUS+0x1b6f>
420219d8:	9116                	add	sp,sp,t0
420219da:	40f2                	lw	ra,28(sp)
420219dc:	4462                	lw	s0,24(sp)
420219de:	44d2                	lw	s1,20(sp)
420219e0:	4942                	lw	s2,16(sp)
420219e2:	49b2                	lw	s3,12(sp)
420219e4:	4a22                	lw	s4,8(sp)
420219e6:	4a92                	lw	s5,4(sp)
420219e8:	4b02                	lw	s6,0(sp)
420219ea:	6105                	addi	sp,sp,32
420219ec:	8082                	ret
420219ee:	3c12a6b7          	lui	a3,0x3c12a
420219f2:	3c140637          	lui	a2,0x3c140
420219f6:	3c12a537          	lui	a0,0x3c12a
420219fa:	0d468693          	addi	a3,a3,212 # 3c12a0d4 <_esp_trace_encoder_array_end+0x9fb4>
420219fe:	19860613          	addi	a2,a2,408 # 3c140198 <__func__.0>
42021a02:	f3450513          	addi	a0,a0,-204 # 3c129f34 <_esp_trace_encoder_array_end+0x9e14>
42021a06:	08200593          	li	a1,130
42021a0a:	fe365097          	auipc	ra,0xfe365
42021a0e:	81c080e7          	jalr	-2020(ra) # 40386226 <__assert_func>
42021a12:	6785                	lui	a5,0x1
42021a14:	41c78793          	addi	a5,a5,1052 # 141c <CSR_UINTSTATUS+0x76b>
42021a18:	978a                	add	a5,a5,sp
42021a1a:	40078713          	addi	a4,a5,1024
42021a1e:	4794                	lw	a3,8(a5)
42021a20:	438c                	lw	a1,0(a5)
42021a22:	43d0                	lw	a2,4(a5)
42021a24:	00df2423          	sw	a3,8(t5)
42021a28:	00bf2023          	sw	a1,0(t5)
42021a2c:	00cf2223          	sw	a2,4(t5)
42021a30:	47d4                	lw	a3,12(a5)
42021a32:	07c1                	addi	a5,a5,16
42021a34:	0f41                	addi	t5,t5,16
42021a36:	fedf2e23          	sw	a3,-4(t5)
42021a3a:	fee792e3          	bne	a5,a4,42021a1e <__wrap_compact5_sbr_dec+0x1ca>
42021a3e:	b761                	j	420219c6 <__wrap_compact5_sbr_dec+0x172>
42021a40:	3c12a6b7          	lui	a3,0x3c12a
42021a44:	3c140637          	lui	a2,0x3c140
42021a48:	3c12a537          	lui	a0,0x3c12a
42021a4c:	16868693          	addi	a3,a3,360 # 3c12a168 <_esp_trace_encoder_array_end+0xa048>
42021a50:	19860613          	addi	a2,a2,408 # 3c140198 <__func__.0>
42021a54:	f3450513          	addi	a0,a0,-204 # 3c129f34 <_esp_trace_encoder_array_end+0x9e14>
42021a58:	0ad00593          	li	a1,173
42021a5c:	fe364097          	auipc	ra,0xfe364
42021a60:	7ca080e7          	jalr	1994(ra) # 40386226 <__assert_func>
42021a64:	3c12a6b7          	lui	a3,0x3c12a
42021a68:	3c140637          	lui	a2,0x3c140
42021a6c:	3c12a537          	lui	a0,0x3c12a
42021a70:	0c468693          	addi	a3,a3,196 # 3c12a0c4 <_esp_trace_encoder_array_end+0x9fa4>
42021a74:	19860613          	addi	a2,a2,408 # 3c140198 <__func__.0>
42021a78:	f3450513          	addi	a0,a0,-204 # 3c129f34 <_esp_trace_encoder_array_end+0x9e14>
42021a7c:	07400593          	li	a1,116
42021a80:	fe364097          	auipc	ra,0xfe364
42021a84:	7a6080e7          	jalr	1958(ra) # 40386226 <__assert_func>
42021a88:	3c12a6b7          	lui	a3,0x3c12a
42021a8c:	3c140637          	lui	a2,0x3c140
42021a90:	3c12a537          	lui	a0,0x3c12a
42021a94:	11068693          	addi	a3,a3,272 # 3c12a110 <_esp_trace_encoder_array_end+0x9ff0>
42021a98:	19860613          	addi	a2,a2,408 # 3c140198 <__func__.0>
42021a9c:	f3450513          	addi	a0,a0,-204 # 3c129f34 <_esp_trace_encoder_array_end+0x9e14>
42021aa0:	0aa00593          	li	a1,170
42021aa4:	fe364097          	auipc	ra,0xfe364
42021aa8:	782080e7          	jalr	1922(ra) # 40386226 <__assert_func>
42021aac:	3c12a6b7          	lui	a3,0x3c12a
42021ab0:	3c140637          	lui	a2,0x3c140
42021ab4:	3c12a537          	lui	a0,0x3c12a
42021ab8:	13c68693          	addi	a3,a3,316 # 3c12a13c <_esp_trace_encoder_array_end+0xa01c>
42021abc:	19860613          	addi	a2,a2,408 # 3c140198 <__func__.0>
42021ac0:	f3450513          	addi	a0,a0,-204 # 3c129f34 <_esp_trace_encoder_array_end+0x9e14>
42021ac4:	0ab00593          	li	a1,171
42021ac8:	fe364097          	auipc	ra,0xfe364
42021acc:	75e080e7          	jalr	1886(ra) # 40386226 <__assert_func>
