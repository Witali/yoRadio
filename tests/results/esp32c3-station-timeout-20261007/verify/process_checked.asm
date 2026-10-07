
idf\esp32c3-oled-native\build-connect-retry\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420263fe <process_checked>:
420263fe:	0015b713          	seqz	a4,a1
42026402:	00163793          	seqz	a5,a2
42026406:	8f5d                	or	a4,a4,a5
42026408:	e351                	bnez	a4,4202648c <process_checked+0x8e>
4202640a:	c149                	beqz	a0,4202648c <process_checked+0x8e>
4202640c:	02c52883          	lw	a7,44(a0)
42026410:	20474737          	lui	a4,0x20474
42026414:	74f70713          	addi	a4,a4,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
42026418:	06e89863          	bne	a7,a4,42026488 <process_checked+0x8a>
4202641c:	4558                	lw	a4,12(a0)
4202641e:	7139                	addi	sp,sp,-64
42026420:	dc22                	sw	s0,56(sp)
42026422:	da26                	sw	s1,52(sp)
42026424:	d84a                	sw	s2,48(sp)
42026426:	d64e                	sw	s3,44(sp)
42026428:	de06                	sw	ra,60(sp)
4202642a:	01c10893          	addi	a7,sp,28
4202642e:	01022803          	lw	a6,16(tp) # 10 <active_scope>
42026432:	893a                	mv	s2,a4
42026434:	01122823          	sw	a7,16(tp) # 10 <active_scope>
42026438:	4958                	lw	a4,20(a0)
4202643a:	4914                	lw	a3,16(a0)
4202643c:	c242                	sw	a6,4(sp)
4202643e:	89ba                	mv	s3,a4
42026440:	8432                	mv	s0,a2
42026442:	84ae                	mv	s1,a1
42026444:	00010e23          	sb	zero,28(sp)
42026448:	c436                	sw	a3,8(sp)
4202644a:	c62a                	sw	a0,12(sp)
4202644c:	067120ef          	jal	42038cb2 <esp_audio_simple_dec_process>
42026450:	4812                	lw	a6,4(sp)
42026452:	01022823          	sw	a6,16(tp) # 10 <active_scope>
42026456:	00850713          	addi	a4,a0,8
4202645a:	ef09                	bnez	a4,42026474 <process_checked+0x76>
4202645c:	46a2                	lw	a3,8(sp)
4202645e:	ca99                	beqz	a3,42026474 <process_checked+0x76>
42026460:	47b2                	lw	a5,12(sp)
42026462:	0127a623          	sw	s2,12(a5)
42026466:	cb94                	sw	a3,16(a5)
42026468:	0137aa23          	sw	s3,20(a5)
4202646c:	0004a623          	sw	zero,12(s1)
42026470:	00042623          	sw	zero,12(s0)
42026474:	01c14783          	lbu	a5,28(sp)
42026478:	ef81                	bnez	a5,42026490 <process_checked+0x92>
4202647a:	50f2                	lw	ra,60(sp)
4202647c:	5462                	lw	s0,56(sp)
4202647e:	54d2                	lw	s1,52(sp)
42026480:	5942                	lw	s2,48(sp)
42026482:	59b2                	lw	s3,44(sp)
42026484:	6121                	addi	sp,sp,64
42026486:	8082                	ret
42026488:	02b1206f          	j	42038cb2 <esp_audio_simple_dec_process>
4202648c:	556d                	li	a0,-5
4202648e:	8082                	ret
42026490:	00042623          	sw	zero,12(s0)
42026494:	5579                	li	a0,-2
42026496:	b7d5                	j	4202647a <process_checked+0x7c>
