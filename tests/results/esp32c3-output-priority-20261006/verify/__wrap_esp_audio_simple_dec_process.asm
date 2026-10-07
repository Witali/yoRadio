
idf\esp32c3-oled-native\build-pipeline-profile\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420268ec <__wrap_esp_audio_simple_dec_process>:
420268ec:	0015b793          	seqz	a5,a1
420268f0:	00163713          	seqz	a4,a2
420268f4:	8fd9                	or	a5,a5,a4
420268f6:	ebe9                	bnez	a5,420269c8 <__wrap_esp_audio_simple_dec_process+0xdc>
420268f8:	c961                	beqz	a0,420269c8 <__wrap_esp_audio_simple_dec_process+0xdc>
420268fa:	419c                	lw	a5,0(a1)
420268fc:	c7e1                	beqz	a5,420269c4 <__wrap_esp_audio_simple_dec_process+0xd8>
420268fe:	5558                	lw	a4,44(a0)
42026900:	204747b7          	lui	a5,0x20474
42026904:	74f78793          	addi	a5,a5,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
42026908:	0af71c63          	bne	a4,a5,420269c0 <__wrap_esp_audio_simple_dec_process+0xd4>
4202690c:	7139                	addi	sp,sp,-64
4202690e:	03054683          	lbu	a3,48(a0)
42026912:	de06                	sw	ra,60(sp)
42026914:	0005a623          	sw	zero,12(a1)
42026918:	00062623          	sw	zero,12(a2)
4202691c:	872a                	mv	a4,a0
4202691e:	87ae                	mv	a5,a1
42026920:	eab1                	bnez	a3,42026974 <__wrap_esp_audio_simple_dec_process+0x88>
42026922:	43d4                	lw	a3,4(a5)
42026924:	c6a1                	beqz	a3,4202696c <__wrap_esp_audio_simple_dec_process+0x80>
42026926:	0087c583          	lbu	a1,8(a5)
4202692a:	edd5                	bnez	a1,420269e6 <__wrap_esp_audio_simple_dec_process+0xfa>
4202692c:	4805                	li	a6,1
4202692e:	0b068263          	beq	a3,a6,420269d2 <__wrap_esp_audio_simple_dec_process+0xe6>
42026932:	0007ae83          	lw	t4,0(a5)
42026936:	0087ae03          	lw	t3,8(a5)
4202693a:	00c7a303          	lw	t1,12(a5)
4202693e:	0107a883          	lw	a7,16(a5)
42026942:	16fd                	addi	a3,a3,-1
42026944:	086c                	addi	a1,sp,28
42026946:	853a                	mv	a0,a4
42026948:	c23e                	sw	a5,4(sp)
4202694a:	d036                	sw	a3,32(sp)
4202694c:	c43a                	sw	a4,8(sp)
4202694e:	ce76                	sw	t4,28(sp)
42026950:	d272                	sw	t3,36(sp)
42026952:	d41a                	sw	t1,40(sp)
42026954:	d646                	sw	a7,44(sp)
42026956:	d71ff0ef          	jal	420266c6 <process_checked>
4202695a:	56a2                	lw	a3,40(sp)
4202695c:	4792                	lw	a5,4(sp)
4202695e:	c7d4                	sw	a3,12(a5)
42026960:	e519                	bnez	a0,4202696e <__wrap_esp_audio_simple_dec_process+0x82>
42026962:	5602                	lw	a2,32(sp)
42026964:	4722                	lw	a4,8(sp)
42026966:	4805                	li	a6,1
42026968:	08c68563          	beq	a3,a2,420269f2 <__wrap_esp_audio_simple_dec_process+0x106>
4202696c:	4501                	li	a0,0
4202696e:	50f2                	lw	ra,60(sp)
42026970:	6121                	addi	sp,sp,64
42026972:	8082                	ret
42026974:	0085c683          	lbu	a3,8(a1)
42026978:	03150513          	addi	a0,a0,49
4202697c:	4585                	li	a1,1
4202697e:	4801                	li	a6,0
42026980:	4881                	li	a7,0
42026982:	d242                	sw	a6,36(sp)
42026984:	d446                	sw	a7,40(sp)
42026986:	ce2a                	sw	a0,28(sp)
42026988:	d02e                	sw	a1,32(sp)
4202698a:	c681                	beqz	a3,42026992 <__wrap_esp_audio_simple_dec_process+0xa6>
4202698c:	43d4                	lw	a3,4(a5)
4202698e:	0016b693          	seqz	a3,a3
42026992:	02d10223          	sb	a3,36(sp)
42026996:	4b94                	lw	a3,16(a5)
42026998:	853a                	mv	a0,a4
4202699a:	086c                	addi	a1,sp,28
4202699c:	c63e                	sw	a5,12(sp)
4202699e:	c432                	sw	a2,8(sp)
420269a0:	c23a                	sw	a4,4(sp)
420269a2:	d636                	sw	a3,44(sp)
420269a4:	d23ff0ef          	jal	420266c6 <process_checked>
420269a8:	56a2                	lw	a3,40(sp)
420269aa:	4712                	lw	a4,4(sp)
420269ac:	4622                	lw	a2,8(sp)
420269ae:	47b2                	lw	a5,12(sp)
420269b0:	ee91                	bnez	a3,420269cc <__wrap_esp_audio_simple_dec_process+0xe0>
420269b2:	fd55                	bnez	a0,4202696e <__wrap_esp_audio_simple_dec_process+0x82>
420269b4:	4654                	lw	a3,12(a2)
420269b6:	fec5                	bnez	a3,4202696e <__wrap_esp_audio_simple_dec_process+0x82>
420269b8:	03074683          	lbu	a3,48(a4)
420269bc:	d2bd                	beqz	a3,42026922 <__wrap_esp_audio_simple_dec_process+0x36>
420269be:	bf45                	j	4202696e <__wrap_esp_audio_simple_dec_process+0x82>
420269c0:	5ba1206f          	j	42038f7a <esp_audio_simple_dec_process>
420269c4:	41dc                	lw	a5,4(a1)
420269c6:	df85                	beqz	a5,420268fe <__wrap_esp_audio_simple_dec_process+0x12>
420269c8:	556d                	li	a0,-5
420269ca:	8082                	ret
420269cc:	02070823          	sb	zero,48(a4)
420269d0:	b7cd                	j	420269b2 <__wrap_esp_audio_simple_dec_process+0xc6>
420269d2:	4390                	lw	a2,0(a5)
420269d4:	4501                	li	a0,0
420269d6:	00064603          	lbu	a2,0(a2)
420269da:	02d70823          	sb	a3,48(a4)
420269de:	02c708a3          	sb	a2,49(a4)
420269e2:	c7d4                	sw	a3,12(a5)
420269e4:	b769                	j	4202696e <__wrap_esp_audio_simple_dec_process+0x82>
420269e6:	50f2                	lw	ra,60(sp)
420269e8:	85be                	mv	a1,a5
420269ea:	853a                	mv	a0,a4
420269ec:	6121                	addi	sp,sp,64
420269ee:	cd9ff06f          	j	420266c6 <process_checked>
420269f2:	4390                	lw	a2,0(a5)
420269f4:	010685b3          	add	a1,a3,a6
420269f8:	4501                	li	a0,0
420269fa:	96b2                	add	a3,a3,a2
420269fc:	0006c683          	lbu	a3,0(a3)
42026a00:	03070823          	sb	a6,48(a4)
42026a04:	02d708a3          	sb	a3,49(a4)
42026a08:	c7cc                	sw	a1,12(a5)
42026a0a:	b795                	j	4202696e <__wrap_esp_audio_simple_dec_process+0x82>
