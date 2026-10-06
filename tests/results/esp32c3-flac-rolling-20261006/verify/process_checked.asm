
idf\esp32c3-oled-native\build-flac-predictor\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026198 <process_checked>:
42026198:	0015b713          	seqz	a4,a1
4202619c:	00163793          	seqz	a5,a2
420261a0:	8f5d                	or	a4,a4,a5
420261a2:	e351                	bnez	a4,42026226 <process_checked+0x8e>
420261a4:	c149                	beqz	a0,42026226 <process_checked+0x8e>
420261a6:	02c52883          	lw	a7,44(a0)
420261aa:	20474737          	lui	a4,0x20474
420261ae:	74f70713          	addi	a4,a4,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
420261b2:	06e89863          	bne	a7,a4,42026222 <process_checked+0x8a>
420261b6:	4558                	lw	a4,12(a0)
420261b8:	7139                	addi	sp,sp,-64
420261ba:	dc22                	sw	s0,56(sp)
420261bc:	da26                	sw	s1,52(sp)
420261be:	d84a                	sw	s2,48(sp)
420261c0:	d64e                	sw	s3,44(sp)
420261c2:	de06                	sw	ra,60(sp)
420261c4:	01c10893          	addi	a7,sp,28
420261c8:	01022803          	lw	a6,16(tp) # 10 <active_scope>
420261cc:	893a                	mv	s2,a4
420261ce:	01122823          	sw	a7,16(tp) # 10 <active_scope>
420261d2:	4958                	lw	a4,20(a0)
420261d4:	4914                	lw	a3,16(a0)
420261d6:	c242                	sw	a6,4(sp)
420261d8:	89ba                	mv	s3,a4
420261da:	8432                	mv	s0,a2
420261dc:	84ae                	mv	s1,a1
420261de:	00010e23          	sb	zero,28(sp)
420261e2:	c436                	sw	a3,8(sp)
420261e4:	c62a                	sw	a0,12(sp)
420261e6:	437120ef          	jal	42038e1c <esp_audio_simple_dec_process>
420261ea:	4812                	lw	a6,4(sp)
420261ec:	01022823          	sw	a6,16(tp) # 10 <active_scope>
420261f0:	00850713          	addi	a4,a0,8
420261f4:	ef09                	bnez	a4,4202620e <process_checked+0x76>
420261f6:	46a2                	lw	a3,8(sp)
420261f8:	ca99                	beqz	a3,4202620e <process_checked+0x76>
420261fa:	47b2                	lw	a5,12(sp)
420261fc:	0127a623          	sw	s2,12(a5)
42026200:	cb94                	sw	a3,16(a5)
42026202:	0137aa23          	sw	s3,20(a5)
42026206:	0004a623          	sw	zero,12(s1)
4202620a:	00042623          	sw	zero,12(s0)
4202620e:	01c14783          	lbu	a5,28(sp)
42026212:	ef81                	bnez	a5,4202622a <process_checked+0x92>
42026214:	50f2                	lw	ra,60(sp)
42026216:	5462                	lw	s0,56(sp)
42026218:	54d2                	lw	s1,52(sp)
4202621a:	5942                	lw	s2,48(sp)
4202621c:	59b2                	lw	s3,44(sp)
4202621e:	6121                	addi	sp,sp,64
42026220:	8082                	ret
42026222:	3fb1206f          	j	42038e1c <esp_audio_simple_dec_process>
42026226:	556d                	li	a0,-5
42026228:	8082                	ret
4202622a:	00042623          	sw	zero,12(s0)
4202622e:	5579                	li	a0,-2
42026230:	b7d5                	j	42026214 <process_checked+0x7c>
