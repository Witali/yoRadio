
idf\esp32c3-oled-native\build-connect-retry\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026920 <process_checked>:
42026920:	0015b713          	seqz	a4,a1
42026924:	00163793          	seqz	a5,a2
42026928:	8f5d                	or	a4,a4,a5
4202692a:	e351                	bnez	a4,420269ae <process_checked+0x8e>
4202692c:	c149                	beqz	a0,420269ae <process_checked+0x8e>
4202692e:	02c52883          	lw	a7,44(a0)
42026932:	20474737          	lui	a4,0x20474
42026936:	74f70713          	addi	a4,a4,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
4202693a:	06e89863          	bne	a7,a4,420269aa <process_checked+0x8a>
4202693e:	4558                	lw	a4,12(a0)
42026940:	7139                	addi	sp,sp,-64
42026942:	dc22                	sw	s0,56(sp)
42026944:	da26                	sw	s1,52(sp)
42026946:	d84a                	sw	s2,48(sp)
42026948:	d64e                	sw	s3,44(sp)
4202694a:	de06                	sw	ra,60(sp)
4202694c:	01c10893          	addi	a7,sp,28
42026950:	01022803          	lw	a6,16(tp) # 10 <active_scope>
42026954:	893a                	mv	s2,a4
42026956:	01122823          	sw	a7,16(tp) # 10 <active_scope>
4202695a:	4958                	lw	a4,20(a0)
4202695c:	4914                	lw	a3,16(a0)
4202695e:	c242                	sw	a6,4(sp)
42026960:	89ba                	mv	s3,a4
42026962:	8432                	mv	s0,a2
42026964:	84ae                	mv	s1,a1
42026966:	00010e23          	sb	zero,28(sp)
4202696a:	c436                	sw	a3,8(sp)
4202696c:	c62a                	sw	a0,12(sp)
4202696e:	069120ef          	jal	420391d6 <esp_audio_simple_dec_process>
42026972:	4812                	lw	a6,4(sp)
42026974:	01022823          	sw	a6,16(tp) # 10 <active_scope>
42026978:	00850713          	addi	a4,a0,8
4202697c:	ef09                	bnez	a4,42026996 <process_checked+0x76>
4202697e:	46a2                	lw	a3,8(sp)
42026980:	ca99                	beqz	a3,42026996 <process_checked+0x76>
42026982:	47b2                	lw	a5,12(sp)
42026984:	0127a623          	sw	s2,12(a5)
42026988:	cb94                	sw	a3,16(a5)
4202698a:	0137aa23          	sw	s3,20(a5)
4202698e:	0004a623          	sw	zero,12(s1)
42026992:	00042623          	sw	zero,12(s0)
42026996:	01c14783          	lbu	a5,28(sp)
4202699a:	ef81                	bnez	a5,420269b2 <process_checked+0x92>
4202699c:	50f2                	lw	ra,60(sp)
4202699e:	5462                	lw	s0,56(sp)
420269a0:	54d2                	lw	s1,52(sp)
420269a2:	5942                	lw	s2,48(sp)
420269a4:	59b2                	lw	s3,44(sp)
420269a6:	6121                	addi	sp,sp,64
420269a8:	8082                	ret
420269aa:	02d1206f          	j	420391d6 <esp_audio_simple_dec_process>
420269ae:	556d                	li	a0,-5
420269b0:	8082                	ret
420269b2:	00042623          	sw	zero,12(s0)
420269b6:	5579                	li	a0,-2
420269b8:	b7d5                	j	4202699c <process_checked+0x7c>
