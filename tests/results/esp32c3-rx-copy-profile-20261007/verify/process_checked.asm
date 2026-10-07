
idf\esp32c3-oled-native\build-rx-copy\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026978 <process_checked>:
42026978:	0015b713          	seqz	a4,a1
4202697c:	00163793          	seqz	a5,a2
42026980:	8f5d                	or	a4,a4,a5
42026982:	e351                	bnez	a4,42026a06 <process_checked+0x8e>
42026984:	c149                	beqz	a0,42026a06 <process_checked+0x8e>
42026986:	02c52883          	lw	a7,44(a0)
4202698a:	20474737          	lui	a4,0x20474
4202698e:	74f70713          	addi	a4,a4,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
42026992:	06e89863          	bne	a7,a4,42026a02 <process_checked+0x8a>
42026996:	4558                	lw	a4,12(a0)
42026998:	7139                	addi	sp,sp,-64
4202699a:	dc22                	sw	s0,56(sp)
4202699c:	da26                	sw	s1,52(sp)
4202699e:	d84a                	sw	s2,48(sp)
420269a0:	d64e                	sw	s3,44(sp)
420269a2:	de06                	sw	ra,60(sp)
420269a4:	01c10893          	addi	a7,sp,28
420269a8:	01022803          	lw	a6,16(tp) # 10 <active_scope>
420269ac:	893a                	mv	s2,a4
420269ae:	01122823          	sw	a7,16(tp) # 10 <active_scope>
420269b2:	4958                	lw	a4,20(a0)
420269b4:	4914                	lw	a3,16(a0)
420269b6:	c242                	sw	a6,4(sp)
420269b8:	89ba                	mv	s3,a4
420269ba:	8432                	mv	s0,a2
420269bc:	84ae                	mv	s1,a1
420269be:	00010e23          	sb	zero,28(sp)
420269c2:	c436                	sw	a3,8(sp)
420269c4:	c62a                	sw	a0,12(sp)
420269c6:	4d9120ef          	jal	4203969e <esp_audio_simple_dec_process>
420269ca:	4812                	lw	a6,4(sp)
420269cc:	01022823          	sw	a6,16(tp) # 10 <active_scope>
420269d0:	00850713          	addi	a4,a0,8
420269d4:	ef09                	bnez	a4,420269ee <process_checked+0x76>
420269d6:	46a2                	lw	a3,8(sp)
420269d8:	ca99                	beqz	a3,420269ee <process_checked+0x76>
420269da:	47b2                	lw	a5,12(sp)
420269dc:	0127a623          	sw	s2,12(a5)
420269e0:	cb94                	sw	a3,16(a5)
420269e2:	0137aa23          	sw	s3,20(a5)
420269e6:	0004a623          	sw	zero,12(s1)
420269ea:	00042623          	sw	zero,12(s0)
420269ee:	01c14783          	lbu	a5,28(sp)
420269f2:	ef81                	bnez	a5,42026a0a <process_checked+0x92>
420269f4:	50f2                	lw	ra,60(sp)
420269f6:	5462                	lw	s0,56(sp)
420269f8:	54d2                	lw	s1,52(sp)
420269fa:	5942                	lw	s2,48(sp)
420269fc:	59b2                	lw	s3,44(sp)
420269fe:	6121                	addi	sp,sp,64
42026a00:	8082                	ret
42026a02:	49d1206f          	j	4203969e <esp_audio_simple_dec_process>
42026a06:	556d                	li	a0,-5
42026a08:	8082                	ret
42026a0a:	00042623          	sw	zero,12(s0)
42026a0e:	5579                	li	a0,-2
42026a10:	b7d5                	j	420269f4 <process_checked+0x7c>
