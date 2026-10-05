
C:\Work\yoRadio\.worktree\aac-storage18\idf\esp32c3-oled-native\build-flac-bounds\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026144 <process_checked>:
42026144:	0015b713          	seqz	a4,a1
42026148:	00163793          	seqz	a5,a2
4202614c:	8f5d                	or	a4,a4,a5
4202614e:	e351                	bnez	a4,420261d2 <process_checked+0x8e>
42026150:	c149                	beqz	a0,420261d2 <process_checked+0x8e>
42026152:	02c52883          	lw	a7,44(a0)
42026156:	20474737          	lui	a4,0x20474
4202615a:	74f70713          	addi	a4,a4,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
4202615e:	06e89863          	bne	a7,a4,420261ce <process_checked+0x8a>
42026162:	4558                	lw	a4,12(a0)
42026164:	7139                	addi	sp,sp,-64
42026166:	dc22                	sw	s0,56(sp)
42026168:	da26                	sw	s1,52(sp)
4202616a:	d84a                	sw	s2,48(sp)
4202616c:	d64e                	sw	s3,44(sp)
4202616e:	de06                	sw	ra,60(sp)
42026170:	01c10893          	addi	a7,sp,28
42026174:	01022803          	lw	a6,16(tp) # 10 <active_scope>
42026178:	893a                	mv	s2,a4
4202617a:	01122823          	sw	a7,16(tp) # 10 <active_scope>
4202617e:	4958                	lw	a4,20(a0)
42026180:	4914                	lw	a3,16(a0)
42026182:	c242                	sw	a6,4(sp)
42026184:	89ba                	mv	s3,a4
42026186:	8432                	mv	s0,a2
42026188:	84ae                	mv	s1,a1
4202618a:	00010e23          	sb	zero,28(sp)
4202618e:	c436                	sw	a3,8(sp)
42026190:	c62a                	sw	a0,12(sp)
42026192:	567110ef          	jal	42037ef8 <esp_audio_simple_dec_process>
42026196:	4812                	lw	a6,4(sp)
42026198:	01022823          	sw	a6,16(tp) # 10 <active_scope>
4202619c:	00850713          	addi	a4,a0,8
420261a0:	ef09                	bnez	a4,420261ba <process_checked+0x76>
420261a2:	46a2                	lw	a3,8(sp)
420261a4:	ca99                	beqz	a3,420261ba <process_checked+0x76>
420261a6:	47b2                	lw	a5,12(sp)
420261a8:	0127a623          	sw	s2,12(a5)
420261ac:	cb94                	sw	a3,16(a5)
420261ae:	0137aa23          	sw	s3,20(a5)
420261b2:	0004a623          	sw	zero,12(s1)
420261b6:	00042623          	sw	zero,12(s0)
420261ba:	01c14783          	lbu	a5,28(sp)
420261be:	ef81                	bnez	a5,420261d6 <process_checked+0x92>
420261c0:	50f2                	lw	ra,60(sp)
420261c2:	5462                	lw	s0,56(sp)
420261c4:	54d2                	lw	s1,52(sp)
420261c6:	5942                	lw	s2,48(sp)
420261c8:	59b2                	lw	s3,44(sp)
420261ca:	6121                	addi	sp,sp,64
420261cc:	8082                	ret
420261ce:	52b1106f          	j	42037ef8 <esp_audio_simple_dec_process>
420261d2:	556d                	li	a0,-5
420261d4:	8082                	ret
420261d6:	00042623          	sw	zero,12(s0)
420261da:	5579                	li	a0,-2
420261dc:	b7d5                	j	420261c0 <process_checked+0x7c>
