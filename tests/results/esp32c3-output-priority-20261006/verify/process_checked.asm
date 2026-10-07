
idf\esp32c3-oled-native\build-pipeline-profile\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420266c6 <process_checked>:
420266c6:	0015b713          	seqz	a4,a1
420266ca:	00163793          	seqz	a5,a2
420266ce:	8f5d                	or	a4,a4,a5
420266d0:	e351                	bnez	a4,42026754 <process_checked+0x8e>
420266d2:	c149                	beqz	a0,42026754 <process_checked+0x8e>
420266d4:	02c52883          	lw	a7,44(a0)
420266d8:	20474737          	lui	a4,0x20474
420266dc:	74f70713          	addi	a4,a4,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
420266e0:	06e89863          	bne	a7,a4,42026750 <process_checked+0x8a>
420266e4:	4558                	lw	a4,12(a0)
420266e6:	7139                	addi	sp,sp,-64
420266e8:	dc22                	sw	s0,56(sp)
420266ea:	da26                	sw	s1,52(sp)
420266ec:	d84a                	sw	s2,48(sp)
420266ee:	d64e                	sw	s3,44(sp)
420266f0:	de06                	sw	ra,60(sp)
420266f2:	01c10893          	addi	a7,sp,28
420266f6:	01022803          	lw	a6,16(tp) # 10 <active_scope>
420266fa:	893a                	mv	s2,a4
420266fc:	01122823          	sw	a7,16(tp) # 10 <active_scope>
42026700:	4958                	lw	a4,20(a0)
42026702:	4914                	lw	a3,16(a0)
42026704:	c242                	sw	a6,4(sp)
42026706:	89ba                	mv	s3,a4
42026708:	8432                	mv	s0,a2
4202670a:	84ae                	mv	s1,a1
4202670c:	00010e23          	sb	zero,28(sp)
42026710:	c436                	sw	a3,8(sp)
42026712:	c62a                	sw	a0,12(sp)
42026714:	067120ef          	jal	42038f7a <esp_audio_simple_dec_process>
42026718:	4812                	lw	a6,4(sp)
4202671a:	01022823          	sw	a6,16(tp) # 10 <active_scope>
4202671e:	00850713          	addi	a4,a0,8
42026722:	ef09                	bnez	a4,4202673c <process_checked+0x76>
42026724:	46a2                	lw	a3,8(sp)
42026726:	ca99                	beqz	a3,4202673c <process_checked+0x76>
42026728:	47b2                	lw	a5,12(sp)
4202672a:	0127a623          	sw	s2,12(a5)
4202672e:	cb94                	sw	a3,16(a5)
42026730:	0137aa23          	sw	s3,20(a5)
42026734:	0004a623          	sw	zero,12(s1)
42026738:	00042623          	sw	zero,12(s0)
4202673c:	01c14783          	lbu	a5,28(sp)
42026740:	ef81                	bnez	a5,42026758 <process_checked+0x92>
42026742:	50f2                	lw	ra,60(sp)
42026744:	5462                	lw	s0,56(sp)
42026746:	54d2                	lw	s1,52(sp)
42026748:	5942                	lw	s2,48(sp)
4202674a:	59b2                	lw	s3,44(sp)
4202674c:	6121                	addi	sp,sp,64
4202674e:	8082                	ret
42026750:	02b1206f          	j	42038f7a <esp_audio_simple_dec_process>
42026754:	556d                	li	a0,-5
42026756:	8082                	ret
42026758:	00042623          	sw	zero,12(s0)
4202675c:	5579                	li	a0,-2
4202675e:	b7d5                	j	42026742 <process_checked+0x7c>
