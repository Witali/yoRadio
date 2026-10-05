
idf\esp32c3-oled-native\build-output-dma-leased\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026110 <process_checked>:
42026110:	0015b713          	seqz	a4,a1
42026114:	00163793          	seqz	a5,a2
42026118:	8f5d                	or	a4,a4,a5
4202611a:	e351                	bnez	a4,4202619e <process_checked+0x8e>
4202611c:	c149                	beqz	a0,4202619e <process_checked+0x8e>
4202611e:	02c52883          	lw	a7,44(a0)
42026122:	20474737          	lui	a4,0x20474
42026126:	74f70713          	addi	a4,a4,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
4202612a:	06e89863          	bne	a7,a4,4202619a <process_checked+0x8a>
4202612e:	4558                	lw	a4,12(a0)
42026130:	7139                	addi	sp,sp,-64
42026132:	dc22                	sw	s0,56(sp)
42026134:	da26                	sw	s1,52(sp)
42026136:	d84a                	sw	s2,48(sp)
42026138:	d64e                	sw	s3,44(sp)
4202613a:	de06                	sw	ra,60(sp)
4202613c:	01c10893          	addi	a7,sp,28
42026140:	01022803          	lw	a6,16(tp) # 10 <active_scope>
42026144:	893a                	mv	s2,a4
42026146:	01122823          	sw	a7,16(tp) # 10 <active_scope>
4202614a:	4958                	lw	a4,20(a0)
4202614c:	4914                	lw	a3,16(a0)
4202614e:	c242                	sw	a6,4(sp)
42026150:	89ba                	mv	s3,a4
42026152:	8432                	mv	s0,a2
42026154:	84ae                	mv	s1,a1
42026156:	00010e23          	sb	zero,28(sp)
4202615a:	c436                	sw	a3,8(sp)
4202615c:	c62a                	sw	a0,12(sp)
4202615e:	4d3100ef          	jal	42036e30 <esp_audio_simple_dec_process>
42026162:	4812                	lw	a6,4(sp)
42026164:	01022823          	sw	a6,16(tp) # 10 <active_scope>
42026168:	00850713          	addi	a4,a0,8
4202616c:	ef09                	bnez	a4,42026186 <process_checked+0x76>
4202616e:	46a2                	lw	a3,8(sp)
42026170:	ca99                	beqz	a3,42026186 <process_checked+0x76>
42026172:	47b2                	lw	a5,12(sp)
42026174:	0127a623          	sw	s2,12(a5)
42026178:	cb94                	sw	a3,16(a5)
4202617a:	0137aa23          	sw	s3,20(a5)
4202617e:	0004a623          	sw	zero,12(s1)
42026182:	00042623          	sw	zero,12(s0)
42026186:	01c14783          	lbu	a5,28(sp)
4202618a:	ef81                	bnez	a5,420261a2 <process_checked+0x92>
4202618c:	50f2                	lw	ra,60(sp)
4202618e:	5462                	lw	s0,56(sp)
42026190:	54d2                	lw	s1,52(sp)
42026192:	5942                	lw	s2,48(sp)
42026194:	59b2                	lw	s3,44(sp)
42026196:	6121                	addi	sp,sp,64
42026198:	8082                	ret
4202619a:	4971006f          	j	42036e30 <esp_audio_simple_dec_process>
4202619e:	556d                	li	a0,-5
420261a0:	8082                	ret
420261a2:	00042623          	sw	zero,12(s0)
420261a6:	5579                	li	a0,-2
420261a8:	b7d5                	j	4202618c <process_checked+0x7c>
