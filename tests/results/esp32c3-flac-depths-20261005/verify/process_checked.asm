
idf\esp32c3-oled-native\build-flac-depths\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026150 <process_checked>:
42026150:	0015b713          	seqz	a4,a1
42026154:	00163793          	seqz	a5,a2
42026158:	8f5d                	or	a4,a4,a5
4202615a:	e351                	bnez	a4,420261de <process_checked+0x8e>
4202615c:	c149                	beqz	a0,420261de <process_checked+0x8e>
4202615e:	02c52883          	lw	a7,44(a0)
42026162:	20474737          	lui	a4,0x20474
42026166:	74f70713          	addi	a4,a4,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
4202616a:	06e89863          	bne	a7,a4,420261da <process_checked+0x8a>
4202616e:	4558                	lw	a4,12(a0)
42026170:	7139                	addi	sp,sp,-64
42026172:	dc22                	sw	s0,56(sp)
42026174:	da26                	sw	s1,52(sp)
42026176:	d84a                	sw	s2,48(sp)
42026178:	d64e                	sw	s3,44(sp)
4202617a:	de06                	sw	ra,60(sp)
4202617c:	01c10893          	addi	a7,sp,28
42026180:	01022803          	lw	a6,16(tp) # 10 <active_scope>
42026184:	893a                	mv	s2,a4
42026186:	01122823          	sw	a7,16(tp) # 10 <active_scope>
4202618a:	4958                	lw	a4,20(a0)
4202618c:	4914                	lw	a3,16(a0)
4202618e:	c242                	sw	a6,4(sp)
42026190:	89ba                	mv	s3,a4
42026192:	8432                	mv	s0,a2
42026194:	84ae                	mv	s1,a1
42026196:	00010e23          	sb	zero,28(sp)
4202619a:	c436                	sw	a3,8(sp)
4202619c:	c62a                	sw	a0,12(sp)
4202619e:	63b110ef          	jal	42037fd8 <esp_audio_simple_dec_process>
420261a2:	4812                	lw	a6,4(sp)
420261a4:	01022823          	sw	a6,16(tp) # 10 <active_scope>
420261a8:	00850713          	addi	a4,a0,8
420261ac:	ef09                	bnez	a4,420261c6 <process_checked+0x76>
420261ae:	46a2                	lw	a3,8(sp)
420261b0:	ca99                	beqz	a3,420261c6 <process_checked+0x76>
420261b2:	47b2                	lw	a5,12(sp)
420261b4:	0127a623          	sw	s2,12(a5)
420261b8:	cb94                	sw	a3,16(a5)
420261ba:	0137aa23          	sw	s3,20(a5)
420261be:	0004a623          	sw	zero,12(s1)
420261c2:	00042623          	sw	zero,12(s0)
420261c6:	01c14783          	lbu	a5,28(sp)
420261ca:	ef81                	bnez	a5,420261e2 <process_checked+0x92>
420261cc:	50f2                	lw	ra,60(sp)
420261ce:	5462                	lw	s0,56(sp)
420261d0:	54d2                	lw	s1,52(sp)
420261d2:	5942                	lw	s2,48(sp)
420261d4:	59b2                	lw	s3,44(sp)
420261d6:	6121                	addi	sp,sp,64
420261d8:	8082                	ret
420261da:	5ff1106f          	j	42037fd8 <esp_audio_simple_dec_process>
420261de:	556d                	li	a0,-5
420261e0:	8082                	ret
420261e2:	00042623          	sw	zero,12(s0)
420261e6:	5579                	li	a0,-2
420261e8:	b7d5                	j	420261cc <process_checked+0x7c>
