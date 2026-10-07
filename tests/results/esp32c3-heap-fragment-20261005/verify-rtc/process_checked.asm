
idf\esp32c3-oled-native\build-heap-fragment\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4202631e <process_checked>:
4202631e:	0015b713          	seqz	a4,a1
42026322:	00163793          	seqz	a5,a2
42026326:	8f5d                	or	a4,a4,a5
42026328:	e351                	bnez	a4,420263ac <process_checked+0x8e>
4202632a:	c149                	beqz	a0,420263ac <process_checked+0x8e>
4202632c:	02c52883          	lw	a7,44(a0)
42026330:	20474737          	lui	a4,0x20474
42026334:	74f70713          	addi	a4,a4,1871 # 2047474f <_rtc_slow_length+0x20473073>
42026338:	06e89863          	bne	a7,a4,420263a8 <process_checked+0x8a>
4202633c:	4558                	lw	a4,12(a0)
4202633e:	7139                	addi	sp,sp,-64
42026340:	dc22                	sw	s0,56(sp)
42026342:	da26                	sw	s1,52(sp)
42026344:	d84a                	sw	s2,48(sp)
42026346:	d64e                	sw	s3,44(sp)
42026348:	de06                	sw	ra,60(sp)
4202634a:	01c10893          	addi	a7,sp,28
4202634e:	01022803          	lw	a6,16(tp) # 10 <active_scope>
42026352:	893a                	mv	s2,a4
42026354:	01122823          	sw	a7,16(tp) # 10 <active_scope>
42026358:	4958                	lw	a4,20(a0)
4202635a:	4914                	lw	a3,16(a0)
4202635c:	c242                	sw	a6,4(sp)
4202635e:	89ba                	mv	s3,a4
42026360:	8432                	mv	s0,a2
42026362:	84ae                	mv	s1,a1
42026364:	00010e23          	sb	zero,28(sp)
42026368:	c436                	sw	a3,8(sp)
4202636a:	c62a                	sw	a0,12(sp)
4202636c:	38c110ef          	jal	420376f8 <esp_audio_simple_dec_process>
42026370:	4812                	lw	a6,4(sp)
42026372:	01022823          	sw	a6,16(tp) # 10 <active_scope>
42026376:	00850713          	addi	a4,a0,8
4202637a:	ef09                	bnez	a4,42026394 <process_checked+0x76>
4202637c:	46a2                	lw	a3,8(sp)
4202637e:	ca99                	beqz	a3,42026394 <process_checked+0x76>
42026380:	47b2                	lw	a5,12(sp)
42026382:	0127a623          	sw	s2,12(a5)
42026386:	cb94                	sw	a3,16(a5)
42026388:	0137aa23          	sw	s3,20(a5)
4202638c:	0004a623          	sw	zero,12(s1)
42026390:	00042623          	sw	zero,12(s0)
42026394:	01c14783          	lbu	a5,28(sp)
42026398:	ef81                	bnez	a5,420263b0 <process_checked+0x92>
4202639a:	50f2                	lw	ra,60(sp)
4202639c:	5462                	lw	s0,56(sp)
4202639e:	54d2                	lw	s1,52(sp)
420263a0:	5942                	lw	s2,48(sp)
420263a2:	59b2                	lw	s3,44(sp)
420263a4:	6121                	addi	sp,sp,64
420263a6:	8082                	ret
420263a8:	3501106f          	j	420376f8 <esp_audio_simple_dec_process>
420263ac:	556d                	li	a0,-5
420263ae:	8082                	ret
420263b0:	00042623          	sw	zero,12(s0)
420263b4:	5579                	li	a0,-2
420263b6:	b7d5                	j	4202639a <process_checked+0x7c>
