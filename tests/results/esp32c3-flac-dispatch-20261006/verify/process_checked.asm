
idf\esp32c3-oled-native\build-flac-predictor\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026190 <process_checked>:
42026190:	0015b713          	seqz	a4,a1
42026194:	00163793          	seqz	a5,a2
42026198:	8f5d                	or	a4,a4,a5
4202619a:	e351                	bnez	a4,4202621e <process_checked+0x8e>
4202619c:	c149                	beqz	a0,4202621e <process_checked+0x8e>
4202619e:	02c52883          	lw	a7,44(a0)
420261a2:	20474737          	lui	a4,0x20474
420261a6:	74f70713          	addi	a4,a4,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
420261aa:	06e89863          	bne	a7,a4,4202621a <process_checked+0x8a>
420261ae:	4558                	lw	a4,12(a0)
420261b0:	7139                	addi	sp,sp,-64
420261b2:	dc22                	sw	s0,56(sp)
420261b4:	da26                	sw	s1,52(sp)
420261b6:	d84a                	sw	s2,48(sp)
420261b8:	d64e                	sw	s3,44(sp)
420261ba:	de06                	sw	ra,60(sp)
420261bc:	01c10893          	addi	a7,sp,28
420261c0:	01022803          	lw	a6,16(tp) # 10 <active_scope>
420261c4:	893a                	mv	s2,a4
420261c6:	01122823          	sw	a7,16(tp) # 10 <active_scope>
420261ca:	4958                	lw	a4,20(a0)
420261cc:	4914                	lw	a3,16(a0)
420261ce:	c242                	sw	a6,4(sp)
420261d0:	89ba                	mv	s3,a4
420261d2:	8432                	mv	s0,a2
420261d4:	84ae                	mv	s1,a1
420261d6:	00010e23          	sb	zero,28(sp)
420261da:	c436                	sw	a3,8(sp)
420261dc:	c62a                	sw	a0,12(sp)
420261de:	069120ef          	jal	42038a46 <esp_audio_simple_dec_process>
420261e2:	4812                	lw	a6,4(sp)
420261e4:	01022823          	sw	a6,16(tp) # 10 <active_scope>
420261e8:	00850713          	addi	a4,a0,8
420261ec:	ef09                	bnez	a4,42026206 <process_checked+0x76>
420261ee:	46a2                	lw	a3,8(sp)
420261f0:	ca99                	beqz	a3,42026206 <process_checked+0x76>
420261f2:	47b2                	lw	a5,12(sp)
420261f4:	0127a623          	sw	s2,12(a5)
420261f8:	cb94                	sw	a3,16(a5)
420261fa:	0137aa23          	sw	s3,20(a5)
420261fe:	0004a623          	sw	zero,12(s1)
42026202:	00042623          	sw	zero,12(s0)
42026206:	01c14783          	lbu	a5,28(sp)
4202620a:	ef81                	bnez	a5,42026222 <process_checked+0x92>
4202620c:	50f2                	lw	ra,60(sp)
4202620e:	5462                	lw	s0,56(sp)
42026210:	54d2                	lw	s1,52(sp)
42026212:	5942                	lw	s2,48(sp)
42026214:	59b2                	lw	s3,44(sp)
42026216:	6121                	addi	sp,sp,64
42026218:	8082                	ret
4202621a:	02d1206f          	j	42038a46 <esp_audio_simple_dec_process>
4202621e:	556d                	li	a0,-5
42026220:	8082                	ret
42026222:	00042623          	sw	zero,12(s0)
42026226:	5579                	li	a0,-2
42026228:	b7d5                	j	4202620c <process_checked+0x7c>
