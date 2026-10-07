
idf\esp32c3-oled-native\build-rx-owner\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420262ee <process_checked>:
420262ee:	0015b713          	seqz	a4,a1
420262f2:	00163793          	seqz	a5,a2
420262f6:	8f5d                	or	a4,a4,a5
420262f8:	e351                	bnez	a4,4202637c <process_checked+0x8e>
420262fa:	c149                	beqz	a0,4202637c <process_checked+0x8e>
420262fc:	02c52883          	lw	a7,44(a0)
42026300:	20474737          	lui	a4,0x20474
42026304:	74f70713          	addi	a4,a4,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
42026308:	06e89863          	bne	a7,a4,42026378 <process_checked+0x8a>
4202630c:	4558                	lw	a4,12(a0)
4202630e:	7139                	addi	sp,sp,-64
42026310:	dc22                	sw	s0,56(sp)
42026312:	da26                	sw	s1,52(sp)
42026314:	d84a                	sw	s2,48(sp)
42026316:	d64e                	sw	s3,44(sp)
42026318:	de06                	sw	ra,60(sp)
4202631a:	01c10893          	addi	a7,sp,28
4202631e:	01022803          	lw	a6,16(tp) # 10 <active_scope>
42026322:	893a                	mv	s2,a4
42026324:	01122823          	sw	a7,16(tp) # 10 <active_scope>
42026328:	4958                	lw	a4,20(a0)
4202632a:	4914                	lw	a3,16(a0)
4202632c:	c242                	sw	a6,4(sp)
4202632e:	89ba                	mv	s3,a4
42026330:	8432                	mv	s0,a2
42026332:	84ae                	mv	s1,a1
42026334:	00010e23          	sb	zero,28(sp)
42026338:	c436                	sw	a3,8(sp)
4202633a:	c62a                	sw	a0,12(sp)
4202633c:	4b7120ef          	jal	42038ff2 <esp_audio_simple_dec_process>
42026340:	4812                	lw	a6,4(sp)
42026342:	01022823          	sw	a6,16(tp) # 10 <active_scope>
42026346:	00850713          	addi	a4,a0,8
4202634a:	ef09                	bnez	a4,42026364 <process_checked+0x76>
4202634c:	46a2                	lw	a3,8(sp)
4202634e:	ca99                	beqz	a3,42026364 <process_checked+0x76>
42026350:	47b2                	lw	a5,12(sp)
42026352:	0127a623          	sw	s2,12(a5)
42026356:	cb94                	sw	a3,16(a5)
42026358:	0137aa23          	sw	s3,20(a5)
4202635c:	0004a623          	sw	zero,12(s1)
42026360:	00042623          	sw	zero,12(s0)
42026364:	01c14783          	lbu	a5,28(sp)
42026368:	ef81                	bnez	a5,42026380 <process_checked+0x92>
4202636a:	50f2                	lw	ra,60(sp)
4202636c:	5462                	lw	s0,56(sp)
4202636e:	54d2                	lw	s1,52(sp)
42026370:	5942                	lw	s2,48(sp)
42026372:	59b2                	lw	s3,44(sp)
42026374:	6121                	addi	sp,sp,64
42026376:	8082                	ret
42026378:	47b1206f          	j	42038ff2 <esp_audio_simple_dec_process>
4202637c:	556d                	li	a0,-5
4202637e:	8082                	ret
42026380:	00042623          	sw	zero,12(s0)
42026384:	5579                	li	a0,-2
42026386:	b7d5                	j	4202636a <process_checked+0x7c>
