
idf\esp32c3-oled-native\build-rx-owner\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420262f2 <process_checked>:
420262f2:	0015b713          	seqz	a4,a1
420262f6:	00163793          	seqz	a5,a2
420262fa:	8f5d                	or	a4,a4,a5
420262fc:	e351                	bnez	a4,42026380 <process_checked+0x8e>
420262fe:	c149                	beqz	a0,42026380 <process_checked+0x8e>
42026300:	02c52883          	lw	a7,44(a0)
42026304:	20474737          	lui	a4,0x20474
42026308:	74f70713          	addi	a4,a4,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
4202630c:	06e89863          	bne	a7,a4,4202637c <process_checked+0x8a>
42026310:	4558                	lw	a4,12(a0)
42026312:	7139                	addi	sp,sp,-64
42026314:	dc22                	sw	s0,56(sp)
42026316:	da26                	sw	s1,52(sp)
42026318:	d84a                	sw	s2,48(sp)
4202631a:	d64e                	sw	s3,44(sp)
4202631c:	de06                	sw	ra,60(sp)
4202631e:	01c10893          	addi	a7,sp,28
42026322:	01022803          	lw	a6,16(tp) # 10 <active_scope>
42026326:	893a                	mv	s2,a4
42026328:	01122823          	sw	a7,16(tp) # 10 <active_scope>
4202632c:	4958                	lw	a4,20(a0)
4202632e:	4914                	lw	a3,16(a0)
42026330:	c242                	sw	a6,4(sp)
42026332:	89ba                	mv	s3,a4
42026334:	8432                	mv	s0,a2
42026336:	84ae                	mv	s1,a1
42026338:	00010e23          	sb	zero,28(sp)
4202633c:	c436                	sw	a3,8(sp)
4202633e:	c62a                	sw	a0,12(sp)
42026340:	533120ef          	jal	42039072 <esp_audio_simple_dec_process>
42026344:	4812                	lw	a6,4(sp)
42026346:	01022823          	sw	a6,16(tp) # 10 <active_scope>
4202634a:	00850713          	addi	a4,a0,8
4202634e:	ef09                	bnez	a4,42026368 <process_checked+0x76>
42026350:	46a2                	lw	a3,8(sp)
42026352:	ca99                	beqz	a3,42026368 <process_checked+0x76>
42026354:	47b2                	lw	a5,12(sp)
42026356:	0127a623          	sw	s2,12(a5)
4202635a:	cb94                	sw	a3,16(a5)
4202635c:	0137aa23          	sw	s3,20(a5)
42026360:	0004a623          	sw	zero,12(s1)
42026364:	00042623          	sw	zero,12(s0)
42026368:	01c14783          	lbu	a5,28(sp)
4202636c:	ef81                	bnez	a5,42026384 <process_checked+0x92>
4202636e:	50f2                	lw	ra,60(sp)
42026370:	5462                	lw	s0,56(sp)
42026372:	54d2                	lw	s1,52(sp)
42026374:	5942                	lw	s2,48(sp)
42026376:	59b2                	lw	s3,44(sp)
42026378:	6121                	addi	sp,sp,64
4202637a:	8082                	ret
4202637c:	4f71206f          	j	42039072 <esp_audio_simple_dec_process>
42026380:	556d                	li	a0,-5
42026382:	8082                	ret
42026384:	00042623          	sw	zero,12(s0)
42026388:	5579                	li	a0,-2
4202638a:	b7d5                	j	4202636e <process_checked+0x7c>
