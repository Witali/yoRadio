
idf\esp32c3-oled-native\build-custom-terminal\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026124 <process_checked>:
42026124:	0015b713          	seqz	a4,a1
42026128:	00163793          	seqz	a5,a2
4202612c:	8f5d                	or	a4,a4,a5
4202612e:	e351                	bnez	a4,420261b2 <process_checked+0x8e>
42026130:	c149                	beqz	a0,420261b2 <process_checked+0x8e>
42026132:	02c52883          	lw	a7,44(a0)
42026136:	20474737          	lui	a4,0x20474
4202613a:	74f70713          	addi	a4,a4,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
4202613e:	06e89863          	bne	a7,a4,420261ae <process_checked+0x8a>
42026142:	4558                	lw	a4,12(a0)
42026144:	7139                	addi	sp,sp,-64
42026146:	dc22                	sw	s0,56(sp)
42026148:	da26                	sw	s1,52(sp)
4202614a:	d84a                	sw	s2,48(sp)
4202614c:	d64e                	sw	s3,44(sp)
4202614e:	de06                	sw	ra,60(sp)
42026150:	01c10893          	addi	a7,sp,28
42026154:	01022803          	lw	a6,16(tp) # 10 <active_scope>
42026158:	893a                	mv	s2,a4
4202615a:	01122823          	sw	a7,16(tp) # 10 <active_scope>
4202615e:	4958                	lw	a4,20(a0)
42026160:	4914                	lw	a3,16(a0)
42026162:	c242                	sw	a6,4(sp)
42026164:	89ba                	mv	s3,a4
42026166:	8432                	mv	s0,a2
42026168:	84ae                	mv	s1,a1
4202616a:	00010e23          	sb	zero,28(sp)
4202616e:	c436                	sw	a3,8(sp)
42026170:	c62a                	sw	a0,12(sp)
42026172:	4d3100ef          	jal	42036e44 <esp_audio_simple_dec_process>
42026176:	4812                	lw	a6,4(sp)
42026178:	01022823          	sw	a6,16(tp) # 10 <active_scope>
4202617c:	00850713          	addi	a4,a0,8
42026180:	ef09                	bnez	a4,4202619a <process_checked+0x76>
42026182:	46a2                	lw	a3,8(sp)
42026184:	ca99                	beqz	a3,4202619a <process_checked+0x76>
42026186:	47b2                	lw	a5,12(sp)
42026188:	0127a623          	sw	s2,12(a5)
4202618c:	cb94                	sw	a3,16(a5)
4202618e:	0137aa23          	sw	s3,20(a5)
42026192:	0004a623          	sw	zero,12(s1)
42026196:	00042623          	sw	zero,12(s0)
4202619a:	01c14783          	lbu	a5,28(sp)
4202619e:	ef81                	bnez	a5,420261b6 <process_checked+0x92>
420261a0:	50f2                	lw	ra,60(sp)
420261a2:	5462                	lw	s0,56(sp)
420261a4:	54d2                	lw	s1,52(sp)
420261a6:	5942                	lw	s2,48(sp)
420261a8:	59b2                	lw	s3,44(sp)
420261aa:	6121                	addi	sp,sp,64
420261ac:	8082                	ret
420261ae:	4971006f          	j	42036e44 <esp_audio_simple_dec_process>
420261b2:	556d                	li	a0,-5
420261b4:	8082                	ret
420261b6:	00042623          	sw	zero,12(s0)
420261ba:	5579                	li	a0,-2
420261bc:	b7d5                	j	420261a0 <process_checked+0x7c>
