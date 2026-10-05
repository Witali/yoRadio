
idf\esp32c3-oled-native\build-rx-owner\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026266 <process_checked>:
42026266:	0015b713          	seqz	a4,a1
4202626a:	00163793          	seqz	a5,a2
4202626e:	8f5d                	or	a4,a4,a5
42026270:	e351                	bnez	a4,420262f4 <process_checked+0x8e>
42026272:	c149                	beqz	a0,420262f4 <process_checked+0x8e>
42026274:	02c52883          	lw	a7,44(a0)
42026278:	20474737          	lui	a4,0x20474
4202627c:	74f70713          	addi	a4,a4,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
42026280:	06e89863          	bne	a7,a4,420262f0 <process_checked+0x8a>
42026284:	4558                	lw	a4,12(a0)
42026286:	7139                	addi	sp,sp,-64
42026288:	dc22                	sw	s0,56(sp)
4202628a:	da26                	sw	s1,52(sp)
4202628c:	d84a                	sw	s2,48(sp)
4202628e:	d64e                	sw	s3,44(sp)
42026290:	de06                	sw	ra,60(sp)
42026292:	01c10893          	addi	a7,sp,28
42026296:	01022803          	lw	a6,16(tp) # 10 <active_scope>
4202629a:	893a                	mv	s2,a4
4202629c:	01122823          	sw	a7,16(tp) # 10 <active_scope>
420262a0:	4958                	lw	a4,20(a0)
420262a2:	4914                	lw	a3,16(a0)
420262a4:	c242                	sw	a6,4(sp)
420262a6:	89ba                	mv	s3,a4
420262a8:	8432                	mv	s0,a2
420262aa:	84ae                	mv	s1,a1
420262ac:	00010e23          	sb	zero,28(sp)
420262b0:	c436                	sw	a3,8(sp)
420262b2:	c62a                	sw	a0,12(sp)
420262b4:	120110ef          	jal	420373d4 <esp_audio_simple_dec_process>
420262b8:	4812                	lw	a6,4(sp)
420262ba:	01022823          	sw	a6,16(tp) # 10 <active_scope>
420262be:	00850713          	addi	a4,a0,8
420262c2:	ef09                	bnez	a4,420262dc <process_checked+0x76>
420262c4:	46a2                	lw	a3,8(sp)
420262c6:	ca99                	beqz	a3,420262dc <process_checked+0x76>
420262c8:	47b2                	lw	a5,12(sp)
420262ca:	0127a623          	sw	s2,12(a5)
420262ce:	cb94                	sw	a3,16(a5)
420262d0:	0137aa23          	sw	s3,20(a5)
420262d4:	0004a623          	sw	zero,12(s1)
420262d8:	00042623          	sw	zero,12(s0)
420262dc:	01c14783          	lbu	a5,28(sp)
420262e0:	ef81                	bnez	a5,420262f8 <process_checked+0x92>
420262e2:	50f2                	lw	ra,60(sp)
420262e4:	5462                	lw	s0,56(sp)
420262e6:	54d2                	lw	s1,52(sp)
420262e8:	5942                	lw	s2,48(sp)
420262ea:	59b2                	lw	s3,44(sp)
420262ec:	6121                	addi	sp,sp,64
420262ee:	8082                	ret
420262f0:	0e41106f          	j	420373d4 <esp_audio_simple_dec_process>
420262f4:	556d                	li	a0,-5
420262f6:	8082                	ret
420262f8:	00042623          	sw	zero,12(s0)
420262fc:	5579                	li	a0,-2
420262fe:	b7d5                	j	420262e2 <process_checked+0x7c>
