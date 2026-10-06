
idf\esp32c3-oled-native\build-pipeline-profile\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4202669a <process_checked>:
4202669a:	0015b713          	seqz	a4,a1
4202669e:	00163793          	seqz	a5,a2
420266a2:	8f5d                	or	a4,a4,a5
420266a4:	e351                	bnez	a4,42026728 <process_checked+0x8e>
420266a6:	c149                	beqz	a0,42026728 <process_checked+0x8e>
420266a8:	02c52883          	lw	a7,44(a0)
420266ac:	20474737          	lui	a4,0x20474
420266b0:	74f70713          	addi	a4,a4,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
420266b4:	06e89863          	bne	a7,a4,42026724 <process_checked+0x8a>
420266b8:	4558                	lw	a4,12(a0)
420266ba:	7139                	addi	sp,sp,-64
420266bc:	dc22                	sw	s0,56(sp)
420266be:	da26                	sw	s1,52(sp)
420266c0:	d84a                	sw	s2,48(sp)
420266c2:	d64e                	sw	s3,44(sp)
420266c4:	de06                	sw	ra,60(sp)
420266c6:	01c10893          	addi	a7,sp,28
420266ca:	01022803          	lw	a6,16(tp) # 10 <active_scope>
420266ce:	893a                	mv	s2,a4
420266d0:	01122823          	sw	a7,16(tp) # 10 <active_scope>
420266d4:	4958                	lw	a4,20(a0)
420266d6:	4914                	lw	a3,16(a0)
420266d8:	c242                	sw	a6,4(sp)
420266da:	89ba                	mv	s3,a4
420266dc:	8432                	mv	s0,a2
420266de:	84ae                	mv	s1,a1
420266e0:	00010e23          	sb	zero,28(sp)
420266e4:	c436                	sw	a3,8(sp)
420266e6:	c62a                	sw	a0,12(sp)
420266e8:	067120ef          	jal	42038f4e <esp_audio_simple_dec_process>
420266ec:	4812                	lw	a6,4(sp)
420266ee:	01022823          	sw	a6,16(tp) # 10 <active_scope>
420266f2:	00850713          	addi	a4,a0,8
420266f6:	ef09                	bnez	a4,42026710 <process_checked+0x76>
420266f8:	46a2                	lw	a3,8(sp)
420266fa:	ca99                	beqz	a3,42026710 <process_checked+0x76>
420266fc:	47b2                	lw	a5,12(sp)
420266fe:	0127a623          	sw	s2,12(a5)
42026702:	cb94                	sw	a3,16(a5)
42026704:	0137aa23          	sw	s3,20(a5)
42026708:	0004a623          	sw	zero,12(s1)
4202670c:	00042623          	sw	zero,12(s0)
42026710:	01c14783          	lbu	a5,28(sp)
42026714:	ef81                	bnez	a5,4202672c <process_checked+0x92>
42026716:	50f2                	lw	ra,60(sp)
42026718:	5462                	lw	s0,56(sp)
4202671a:	54d2                	lw	s1,52(sp)
4202671c:	5942                	lw	s2,48(sp)
4202671e:	59b2                	lw	s3,44(sp)
42026720:	6121                	addi	sp,sp,64
42026722:	8082                	ret
42026724:	02b1206f          	j	42038f4e <esp_audio_simple_dec_process>
42026728:	556d                	li	a0,-5
4202672a:	8082                	ret
4202672c:	00042623          	sw	zero,12(s0)
42026730:	5579                	li	a0,-2
42026732:	b7d5                	j	42026716 <process_checked+0x7c>
