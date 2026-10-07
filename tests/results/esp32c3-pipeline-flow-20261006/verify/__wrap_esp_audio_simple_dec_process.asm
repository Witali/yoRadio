
idf\esp32c3-oled-native\build-pipeline-profile\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420268c0 <__wrap_esp_audio_simple_dec_process>:
420268c0:	0015b793          	seqz	a5,a1
420268c4:	00163713          	seqz	a4,a2
420268c8:	8fd9                	or	a5,a5,a4
420268ca:	ebe9                	bnez	a5,4202699c <__wrap_esp_audio_simple_dec_process+0xdc>
420268cc:	c961                	beqz	a0,4202699c <__wrap_esp_audio_simple_dec_process+0xdc>
420268ce:	419c                	lw	a5,0(a1)
420268d0:	c7e1                	beqz	a5,42026998 <__wrap_esp_audio_simple_dec_process+0xd8>
420268d2:	5558                	lw	a4,44(a0)
420268d4:	204747b7          	lui	a5,0x20474
420268d8:	74f78793          	addi	a5,a5,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
420268dc:	0af71c63          	bne	a4,a5,42026994 <__wrap_esp_audio_simple_dec_process+0xd4>
420268e0:	7139                	addi	sp,sp,-64
420268e2:	03054683          	lbu	a3,48(a0)
420268e6:	de06                	sw	ra,60(sp)
420268e8:	0005a623          	sw	zero,12(a1)
420268ec:	00062623          	sw	zero,12(a2)
420268f0:	872a                	mv	a4,a0
420268f2:	87ae                	mv	a5,a1
420268f4:	eab1                	bnez	a3,42026948 <__wrap_esp_audio_simple_dec_process+0x88>
420268f6:	43d4                	lw	a3,4(a5)
420268f8:	c6a1                	beqz	a3,42026940 <__wrap_esp_audio_simple_dec_process+0x80>
420268fa:	0087c583          	lbu	a1,8(a5)
420268fe:	edd5                	bnez	a1,420269ba <__wrap_esp_audio_simple_dec_process+0xfa>
42026900:	4805                	li	a6,1
42026902:	0b068263          	beq	a3,a6,420269a6 <__wrap_esp_audio_simple_dec_process+0xe6>
42026906:	0007ae83          	lw	t4,0(a5)
4202690a:	0087ae03          	lw	t3,8(a5)
4202690e:	00c7a303          	lw	t1,12(a5)
42026912:	0107a883          	lw	a7,16(a5)
42026916:	16fd                	addi	a3,a3,-1
42026918:	086c                	addi	a1,sp,28
4202691a:	853a                	mv	a0,a4
4202691c:	c23e                	sw	a5,4(sp)
4202691e:	d036                	sw	a3,32(sp)
42026920:	c43a                	sw	a4,8(sp)
42026922:	ce76                	sw	t4,28(sp)
42026924:	d272                	sw	t3,36(sp)
42026926:	d41a                	sw	t1,40(sp)
42026928:	d646                	sw	a7,44(sp)
4202692a:	d71ff0ef          	jal	4202669a <process_checked>
4202692e:	56a2                	lw	a3,40(sp)
42026930:	4792                	lw	a5,4(sp)
42026932:	c7d4                	sw	a3,12(a5)
42026934:	e519                	bnez	a0,42026942 <__wrap_esp_audio_simple_dec_process+0x82>
42026936:	5602                	lw	a2,32(sp)
42026938:	4722                	lw	a4,8(sp)
4202693a:	4805                	li	a6,1
4202693c:	08c68563          	beq	a3,a2,420269c6 <__wrap_esp_audio_simple_dec_process+0x106>
42026940:	4501                	li	a0,0
42026942:	50f2                	lw	ra,60(sp)
42026944:	6121                	addi	sp,sp,64
42026946:	8082                	ret
42026948:	0085c683          	lbu	a3,8(a1)
4202694c:	03150513          	addi	a0,a0,49
42026950:	4585                	li	a1,1
42026952:	4801                	li	a6,0
42026954:	4881                	li	a7,0
42026956:	d242                	sw	a6,36(sp)
42026958:	d446                	sw	a7,40(sp)
4202695a:	ce2a                	sw	a0,28(sp)
4202695c:	d02e                	sw	a1,32(sp)
4202695e:	c681                	beqz	a3,42026966 <__wrap_esp_audio_simple_dec_process+0xa6>
42026960:	43d4                	lw	a3,4(a5)
42026962:	0016b693          	seqz	a3,a3
42026966:	02d10223          	sb	a3,36(sp)
4202696a:	4b94                	lw	a3,16(a5)
4202696c:	853a                	mv	a0,a4
4202696e:	086c                	addi	a1,sp,28
42026970:	c63e                	sw	a5,12(sp)
42026972:	c432                	sw	a2,8(sp)
42026974:	c23a                	sw	a4,4(sp)
42026976:	d636                	sw	a3,44(sp)
42026978:	d23ff0ef          	jal	4202669a <process_checked>
4202697c:	56a2                	lw	a3,40(sp)
4202697e:	4712                	lw	a4,4(sp)
42026980:	4622                	lw	a2,8(sp)
42026982:	47b2                	lw	a5,12(sp)
42026984:	ee91                	bnez	a3,420269a0 <__wrap_esp_audio_simple_dec_process+0xe0>
42026986:	fd55                	bnez	a0,42026942 <__wrap_esp_audio_simple_dec_process+0x82>
42026988:	4654                	lw	a3,12(a2)
4202698a:	fec5                	bnez	a3,42026942 <__wrap_esp_audio_simple_dec_process+0x82>
4202698c:	03074683          	lbu	a3,48(a4)
42026990:	d2bd                	beqz	a3,420268f6 <__wrap_esp_audio_simple_dec_process+0x36>
42026992:	bf45                	j	42026942 <__wrap_esp_audio_simple_dec_process+0x82>
42026994:	5ba1206f          	j	42038f4e <esp_audio_simple_dec_process>
42026998:	41dc                	lw	a5,4(a1)
4202699a:	df85                	beqz	a5,420268d2 <__wrap_esp_audio_simple_dec_process+0x12>
4202699c:	556d                	li	a0,-5
4202699e:	8082                	ret
420269a0:	02070823          	sb	zero,48(a4)
420269a4:	b7cd                	j	42026986 <__wrap_esp_audio_simple_dec_process+0xc6>
420269a6:	4390                	lw	a2,0(a5)
420269a8:	4501                	li	a0,0
420269aa:	00064603          	lbu	a2,0(a2)
420269ae:	02d70823          	sb	a3,48(a4)
420269b2:	02c708a3          	sb	a2,49(a4)
420269b6:	c7d4                	sw	a3,12(a5)
420269b8:	b769                	j	42026942 <__wrap_esp_audio_simple_dec_process+0x82>
420269ba:	50f2                	lw	ra,60(sp)
420269bc:	85be                	mv	a1,a5
420269be:	853a                	mv	a0,a4
420269c0:	6121                	addi	sp,sp,64
420269c2:	cd9ff06f          	j	4202669a <process_checked>
420269c6:	4390                	lw	a2,0(a5)
420269c8:	010685b3          	add	a1,a3,a6
420269cc:	4501                	li	a0,0
420269ce:	96b2                	add	a3,a3,a2
420269d0:	0006c683          	lbu	a3,0(a3)
420269d4:	03070823          	sb	a6,48(a4)
420269d8:	02d708a3          	sb	a3,49(a4)
420269dc:	c7cc                	sw	a1,12(a5)
420269de:	b795                	j	42026942 <__wrap_esp_audio_simple_dec_process+0x82>
