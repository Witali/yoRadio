
small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4201306e <jd_prepare>:
4201306e:	715d                	addi	sp,sp,-80
42013070:	c2a6                	sw	s1,68(sp)
42013072:	c0ca                	sw	s2,64(sp)
42013074:	84ae                	mv	s1,a1
42013076:	8932                	mv	s2,a2
42013078:	4581                	li	a1,0
4201307a:	07800613          	li	a2,120
4201307e:	c686                	sw	ra,76(sp)
42013080:	c4a2                	sw	s0,72(sp)
42013082:	c636                	sw	a3,12(sp)
42013084:	842a                	mv	s0,a0
42013086:	c43a                	sw	a4,8(sp)
42013088:	de4e                	sw	s3,60(sp)
4201308a:	dc52                	sw	s4,56(sp)
4201308c:	da56                	sw	s5,52(sp)
4201308e:	d85a                	sw	s6,48(sp)
42013090:	d65e                	sw	s7,44(sp)
42013092:	d462                	sw	s8,40(sp)
42013094:	d266                	sw	s9,36(sp)
42013096:	d06a                	sw	s10,32(sp)
42013098:	ce6e                	sw	s11,28(sp)
4201309a:	fdfed097          	auipc	ra,0xfdfed
4201309e:	3ee080e7          	jalr	1006(ra) # 40000488 <memset>
420130a2:	46b2                	lw	a3,12(sp)
420130a4:	4722                	lw	a4,8(sp)
420130a6:	07242423          	sw	s2,104(s0)
420130aa:	d474                	sw	a3,108(s0)
420130ac:	d824                	sw	s1,112(s0)
420130ae:	d878                	sw	a4,116(s0)
420130b0:	20000593          	li	a1,512
420130b4:	8522                	mv	a0,s0
420130b6:	e33ff0ef          	jal	42012ee8 <alloc_pool>
420130ba:	c408                	sw	a0,8(s0)
420130bc:	22050d63          	beqz	a0,420132f6 <jd_prepare+0x288>
420130c0:	6a41                	lui	s4,0x10
420130c2:	892a                	mv	s2,a0
420130c4:	4981                	li	s3,0
420130c6:	4481                	li	s1,0
420130c8:	4a85                	li	s5,1
420130ca:	fd8a0a13          	addi	s4,s4,-40 # ffd8 <CSR_UINTSTATUS+0xf327>
420130ce:	583c                	lw	a5,112(s0)
420130d0:	4605                	li	a2,1
420130d2:	85ca                	mv	a1,s2
420130d4:	8522                	mv	a0,s0
420130d6:	9782                	jalr	a5
420130d8:	0b551b63          	bne	a0,s5,4201318e <jd_prepare+0x120>
420130dc:	00094783          	lbu	a5,0(s2)
420130e0:	04a2                	slli	s1,s1,0x8
420130e2:	0985                	addi	s3,s3,1
420130e4:	8cdd                	or	s1,s1,a5
420130e6:	04c2                	slli	s1,s1,0x10
420130e8:	80c1                	srli	s1,s1,0x10
420130ea:	ff4492e3          	bne	s1,s4,420130ce <jd_prepare+0x60>
420130ee:	6a41                	lui	s4,0x10
420130f0:	1a7d                	addi	s4,s4,-1 # ffff <CSR_UINTSTATUS+0xf34e>
420130f2:	0ff00b93          	li	s7,255
420130f6:	4c45                	li	s8,17
420130f8:	583c                	lw	a5,112(s0)
420130fa:	4611                	li	a2,4
420130fc:	85ca                	mv	a1,s2
420130fe:	8522                	mv	a0,s0
42013100:	9782                	jalr	a5
42013102:	4791                	li	a5,4
42013104:	8caa                	mv	s9,a0
42013106:	08f51463          	bne	a0,a5,4201318e <jd_prepare+0x120>
4201310a:	00095703          	lhu	a4,0(s2)
4201310e:	09470263          	beq	a4,s4,42013192 <jd_prepare+0x124>
42013112:	00875793          	srli	a5,a4,0x8
42013116:	0722                	slli	a4,a4,0x8
42013118:	97ba                	add	a5,a5,a4
4201311a:	00295703          	lhu	a4,2(s2)
4201311e:	07c2                	slli	a5,a5,0x10
42013120:	83c1                	srli	a5,a5,0x10
42013122:	00875493          	srli	s1,a4,0x8
42013126:	0722                	slli	a4,a4,0x8
42013128:	94ba                	add	s1,s1,a4
4201312a:	04c2                	slli	s1,s1,0x10
4201312c:	80c1                	srli	s1,s1,0x10
4201312e:	4709                	li	a4,2
42013130:	3c977f63          	bgeu	a4,s1,4201350e <jd_prepare+0x4a0>
42013134:	0087d713          	srli	a4,a5,0x8
42013138:	3d771b63          	bne	a4,s7,4201350e <jd_prepare+0x4a0>
4201313c:	14f9                	addi	s1,s1,-2
4201313e:	0991                	addi	s3,s3,4
42013140:	0ff7f793          	zext.b	a5,a5
42013144:	0da00713          	li	a4,218
42013148:	99a6                	add	s3,s3,s1
4201314a:	30e78463          	beq	a5,a4,42013452 <jd_prepare+0x3e4>
4201314e:	06f76663          	bltu	a4,a5,420131ba <jd_prepare+0x14c>
42013152:	f4078793          	addi	a5,a5,-192
42013156:	07c2                	slli	a5,a5,0x10
42013158:	83c1                	srli	a5,a5,0x10
4201315a:	4765                	li	a4,25
4201315c:	02f76263          	bltu	a4,a5,42013180 <jd_prepare+0x112>
42013160:	4705                	li	a4,1
42013162:	0200fd37          	lui	s10,0x200f
42013166:	00f71733          	sll	a4,a4,a5
4201316a:	eeed0d13          	addi	s10,s10,-274 # 200eeee <CSR_UINTSTATUS+0x200e23d>
4201316e:	01a77d33          	and	s10,a4,s10
42013172:	120d1663          	bnez	s10,4201329e <jd_prepare+0x230>
42013176:	4691                	li	a3,4
42013178:	14d78463          	beq	a5,a3,420132c0 <jd_prepare+0x252>
4201317c:	8b05                	andi	a4,a4,1
4201317e:	eb35                	bnez	a4,420131f2 <jd_prepare+0x184>
42013180:	583c                	lw	a5,112(s0)
42013182:	8626                	mv	a2,s1
42013184:	4581                	li	a1,0
42013186:	8522                	mv	a0,s0
42013188:	9782                	jalr	a5
4201318a:	f69507e3          	beq	a0,s1,420130f8 <jd_prepare+0x8a>
4201318e:	4c89                	li	s9,2
42013190:	aa01                	j	420132a0 <jd_prepare+0x232>
42013192:	583c                	lw	a5,112(s0)
42013194:	4605                	li	a2,1
42013196:	00490593          	addi	a1,s2,4
4201319a:	8522                	mv	a0,s0
4201319c:	9782                	jalr	a5
4201319e:	4785                	li	a5,1
420131a0:	fef517e3          	bne	a0,a5,4201318e <jd_prepare+0x120>
420131a4:	00195703          	lhu	a4,1(s2)
420131a8:	00875793          	srli	a5,a4,0x8
420131ac:	0722                	slli	a4,a4,0x8
420131ae:	97ba                	add	a5,a5,a4
420131b0:	07c2                	slli	a5,a5,0x10
420131b2:	00395703          	lhu	a4,3(s2)
420131b6:	83c1                	srli	a5,a5,0x10
420131b8:	b7ad                	j	42013122 <jd_prepare+0xb4>
420131ba:	0db00713          	li	a4,219
420131be:	20e78263          	beq	a5,a4,420133c2 <jd_prepare+0x354>
420131c2:	0dd00713          	li	a4,221
420131c6:	fae79de3          	bne	a5,a4,42013180 <jd_prepare+0x112>
420131ca:	20000793          	li	a5,512
420131ce:	0c97e963          	bltu	a5,s1,420132a0 <jd_prepare+0x232>
420131d2:	583c                	lw	a5,112(s0)
420131d4:	8626                	mv	a2,s1
420131d6:	85ca                	mv	a1,s2
420131d8:	8522                	mv	a0,s0
420131da:	9782                	jalr	a5
420131dc:	fa9519e3          	bne	a0,s1,4201318e <jd_prepare+0x120>
420131e0:	00095783          	lhu	a5,0(s2)
420131e4:	0087d713          	srli	a4,a5,0x8
420131e8:	07a2                	slli	a5,a5,0x8
420131ea:	97ba                	add	a5,a5,a4
420131ec:	00f41d23          	sh	a5,26(s0)
420131f0:	b721                	j	420130f8 <jd_prepare+0x8a>
420131f2:	20000793          	li	a5,512
420131f6:	0a97e563          	bltu	a5,s1,420132a0 <jd_prepare+0x232>
420131fa:	583c                	lw	a5,112(s0)
420131fc:	8626                	mv	a2,s1
420131fe:	85ca                	mv	a1,s2
42013200:	8522                	mv	a0,s0
42013202:	9782                	jalr	a5
42013204:	f89515e3          	bne	a0,s1,4201318e <jd_prepare+0x120>
42013208:	4795                	li	a5,5
4201320a:	3097f263          	bgeu	a5,s1,4201350e <jd_prepare+0x4a0>
4201320e:	00094703          	lbu	a4,0(s2)
42013212:	47a1                	li	a5,8
42013214:	08f71563          	bne	a4,a5,4201329e <jd_prepare+0x230>
42013218:	00395783          	lhu	a5,3(s2)
4201321c:	0087d713          	srli	a4,a5,0x8
42013220:	07a2                	slli	a5,a5,0x8
42013222:	97ba                	add	a5,a5,a4
42013224:	00f41e23          	sh	a5,28(s0)
42013228:	00195783          	lhu	a5,1(s2)
4201322c:	0087d713          	srli	a4,a5,0x8
42013230:	07a2                	slli	a5,a5,0x8
42013232:	97ba                	add	a5,a5,a4
42013234:	00f41f23          	sh	a5,30(s0)
42013238:	00594683          	lbu	a3,5(s2)
4201323c:	4785                	li	a5,1
4201323e:	00d409a3          	sb	a3,19(s0)
42013242:	0fd6f713          	andi	a4,a3,253
42013246:	04f71c63          	bne	a4,a5,4201329e <jd_prepare+0x230>
4201324a:	478d                	li	a5,3
4201324c:	02f687b3          	mul	a5,a3,a5
42013250:	0799                	addi	a5,a5,6
42013252:	2a979e63          	bne	a5,s1,4201350e <jd_prepare+0x4a0>
42013256:	00794783          	lbu	a5,7(s2)
4201325a:	00790713          	addi	a4,s2,7
4201325e:	fdf78613          	addi	a2,a5,-33
42013262:	00263613          	sltiu	a2,a2,2
42013266:	e601                	bnez	a2,4201326e <jd_prepare+0x200>
42013268:	fef78613          	addi	a2,a5,-17
4201326c:	ea0d                	bnez	a2,4201329e <jd_prepare+0x230>
4201326e:	0047d613          	srli	a2,a5,0x4
42013272:	8bbd                	andi	a5,a5,15
42013274:	00c40723          	sb	a2,14(s0)
42013278:	00f407a3          	sb	a5,15(s0)
4201327c:	460d                	li	a2,3
4201327e:	00174783          	lbu	a5,1(a4)
42013282:	01a405b3          	add	a1,s0,s10
42013286:	00f58823          	sb	a5,16(a1)
4201328a:	00f66a63          	bltu	a2,a5,4201329e <jd_prepare+0x230>
4201328e:	0d05                	addi	s10,s10,1
42013290:	e6dd74e3          	bgeu	s10,a3,420130f8 <jd_prepare+0x8a>
42013294:	00374783          	lbu	a5,3(a4)
42013298:	070d                	addi	a4,a4,3
4201329a:	ff8782e3          	beq	a5,s8,4201327e <jd_prepare+0x210>
4201329e:	4ca1                	li	s9,8
420132a0:	40b6                	lw	ra,76(sp)
420132a2:	4426                	lw	s0,72(sp)
420132a4:	4496                	lw	s1,68(sp)
420132a6:	4906                	lw	s2,64(sp)
420132a8:	59f2                	lw	s3,60(sp)
420132aa:	5a62                	lw	s4,56(sp)
420132ac:	5ad2                	lw	s5,52(sp)
420132ae:	5b42                	lw	s6,48(sp)
420132b0:	5bb2                	lw	s7,44(sp)
420132b2:	5c22                	lw	s8,40(sp)
420132b4:	5d02                	lw	s10,32(sp)
420132b6:	4df2                	lw	s11,28(sp)
420132b8:	8566                	mv	a0,s9
420132ba:	5c92                	lw	s9,36(sp)
420132bc:	6161                	addi	sp,sp,80
420132be:	8082                	ret
420132c0:	20000793          	li	a5,512
420132c4:	fc97eee3          	bltu	a5,s1,420132a0 <jd_prepare+0x232>
420132c8:	583c                	lw	a5,112(s0)
420132ca:	8626                	mv	a2,s1
420132cc:	85ca                	mv	a1,s2
420132ce:	8522                	mv	a0,s0
420132d0:	9782                	jalr	a5
420132d2:	ea951ee3          	bne	a0,s1,4201318e <jd_prepare+0x120>
420132d6:	8b4a                	mv	s6,s2
420132d8:	4dc1                	li	s11,16
420132da:	229dfa63          	bgeu	s11,s1,4201350e <jd_prepare+0x4a0>
420132de:	000b4c83          	lbu	s9,0(s6)
420132e2:	0eecf793          	andi	a5,s9,238
420132e6:	22079463          	bnez	a5,4201350e <jd_prepare+0x4a0>
420132ea:	45c1                	li	a1,16
420132ec:	8522                	mv	a0,s0
420132ee:	bfbff0ef          	jal	42012ee8 <alloc_pool>
420132f2:	882a                	mv	a6,a0
420132f4:	e119                	bnez	a0,420132fa <jd_prepare+0x28c>
420132f6:	4c8d                	li	s9,3
420132f8:	b765                	j	420132a0 <jd_prepare+0x232>
420132fa:	004cdd13          	srli	s10,s9,0x4
420132fe:	00fcfc93          	andi	s9,s9,15
42013302:	0c86                	slli	s9,s9,0x1
42013304:	9cea                	add	s9,s9,s10
42013306:	0c8a                	slli	s9,s9,0x2
42013308:	9ca2                	add	s9,s9,s0
4201330a:	02aca023          	sw	a0,32(s9)
4201330e:	4a81                	li	s5,0
42013310:	4681                	li	a3,0
42013312:	00db0633          	add	a2,s6,a3
42013316:	00164603          	lbu	a2,1(a2)
4201331a:	00d805b3          	add	a1,a6,a3
4201331e:	0685                	addi	a3,a3,1
42013320:	00c58023          	sb	a2,0(a1)
42013324:	9ab2                	add	s5,s5,a2
42013326:	ffb696e3          	bne	a3,s11,42013312 <jd_prepare+0x2a4>
4201332a:	001a9593          	slli	a1,s5,0x1
4201332e:	8522                	mv	a0,s0
42013330:	c442                	sw	a6,8(sp)
42013332:	bb7ff0ef          	jal	42012ee8 <alloc_pool>
42013336:	d161                	beqz	a0,420132f6 <jd_prepare+0x288>
42013338:	4822                	lw	a6,8(sp)
4201333a:	fef48893          	addi	a7,s1,-17
4201333e:	02aca823          	sw	a0,48(s9)
42013342:	4301                	li	t1,0
42013344:	4581                	li	a1,0
42013346:	4681                	li	a3,0
42013348:	00b80633          	add	a2,a6,a1
4201334c:	00064e03          	lbu	t3,0(a2)
42013350:	00131613          	slli	a2,t1,0x1
42013354:	962a                	add	a2,a2,a0
42013356:	8eb6                	mv	t4,a3
42013358:	84f2                	mv	s1,t3
4201335a:	e0a1                	bnez	s1,4201339a <jd_prepare+0x32c>
4201335c:	96f2                	add	a3,a3,t3
4201335e:	0686                	slli	a3,a3,0x1
42013360:	06c2                	slli	a3,a3,0x10
42013362:	0585                	addi	a1,a1,1
42013364:	9372                	add	t1,t1,t3
42013366:	82c1                	srli	a3,a3,0x10
42013368:	ffb590e3          	bne	a1,s11,42013348 <jd_prepare+0x2da>
4201336c:	1b58e163          	bltu	a7,s5,4201350e <jd_prepare+0x4a0>
42013370:	85d6                	mv	a1,s5
42013372:	8522                	mv	a0,s0
42013374:	c446                	sw	a7,8(sp)
42013376:	b73ff0ef          	jal	42012ee8 <alloc_pool>
4201337a:	dd35                	beqz	a0,420132f6 <jd_prepare+0x288>
4201337c:	48a2                	lw	a7,8(sp)
4201337e:	001d4d13          	xori	s10,s10,1
42013382:	0b45                	addi	s6,s6,17
42013384:	04aca023          	sw	a0,64(s9)
42013388:	001d7d13          	andi	s10,s10,1
4201338c:	009a9d63          	bne	s5,s1,420133a6 <jd_prepare+0x338>
42013390:	415884b3          	sub	s1,a7,s5
42013394:	f55893e3          	bne	a7,s5,420132da <jd_prepare+0x26c>
42013398:	b385                	j	420130f8 <jd_prepare+0x8a>
4201339a:	01d61023          	sh	t4,0(a2)
4201339e:	14fd                	addi	s1,s1,-1
420133a0:	0609                	addi	a2,a2,2
420133a2:	0e85                	addi	t4,t4,1
420133a4:	bf5d                	j	4201335a <jd_prepare+0x2ec>
420133a6:	000b4683          	lbu	a3,0(s6)
420133aa:	00c6b613          	sltiu	a2,a3,12
420133ae:	e219                	bnez	a2,420133b4 <jd_prepare+0x346>
420133b0:	140d1f63          	bnez	s10,4201350e <jd_prepare+0x4a0>
420133b4:	00950633          	add	a2,a0,s1
420133b8:	0b05                	addi	s6,s6,1
420133ba:	00d60023          	sb	a3,0(a2)
420133be:	0485                	addi	s1,s1,1
420133c0:	b7f1                	j	4201338c <jd_prepare+0x31e>
420133c2:	20000793          	li	a5,512
420133c6:	ec97ede3          	bltu	a5,s1,420132a0 <jd_prepare+0x232>
420133ca:	583c                	lw	a5,112(s0)
420133cc:	8626                	mv	a2,s1
420133ce:	85ca                	mv	a1,s2
420133d0:	8522                	mv	a0,s0
420133d2:	9782                	jalr	a5
420133d4:	da951de3          	bne	a0,s1,4201318e <jd_prepare+0x120>
420133d8:	3c0ecdb7          	lui	s11,0x3c0ec
420133dc:	8d4a                	mv	s10,s2
420133de:	04000813          	li	a6,64
420133e2:	488d                	li	a7,3
420133e4:	a54d8d93          	addi	s11,s11,-1452 # 3c0eba54 <Zig>
420133e8:	12987363          	bgeu	a6,s1,4201350e <jd_prepare+0x4a0>
420133ec:	000d4c83          	lbu	s9,0(s10)
420133f0:	1198ef63          	bltu	a7,s9,4201350e <jd_prepare+0x4a0>
420133f4:	10000593          	li	a1,256
420133f8:	8522                	mv	a0,s0
420133fa:	aefff0ef          	jal	42012ee8 <alloc_pool>
420133fe:	ee050ce3          	beqz	a0,420132f6 <jd_prepare+0x288>
42013402:	0cd1                	addi	s9,s9,20
42013404:	0c8a                	slli	s9,s9,0x2
42013406:	9ca2                	add	s9,s9,s0
42013408:	3c0ec7b7          	lui	a5,0x3c0ec
4201340c:	fbf48493          	addi	s1,s1,-65
42013410:	00aca023          	sw	a0,0(s9)
42013414:	4701                	li	a4,0
42013416:	9d478693          	addi	a3,a5,-1580 # 3c0eb9d4 <Ipsf>
4201341a:	04000813          	li	a6,64
4201341e:	488d                	li	a7,3
42013420:	01b707b3          	add	a5,a4,s11
42013424:	0007c783          	lbu	a5,0(a5)
42013428:	00ed05b3          	add	a1,s10,a4
4201342c:	0015c583          	lbu	a1,1(a1)
42013430:	00279613          	slli	a2,a5,0x2
42013434:	0786                	slli	a5,a5,0x1
42013436:	97b6                	add	a5,a5,a3
42013438:	0007d783          	lhu	a5,0(a5)
4201343c:	962a                	add	a2,a2,a0
4201343e:	0705                	addi	a4,a4,1
42013440:	02f587b3          	mul	a5,a1,a5
42013444:	c21c                	sw	a5,0(a2)
42013446:	fd071de3          	bne	a4,a6,42013420 <jd_prepare+0x3b2>
4201344a:	041d0d13          	addi	s10,s10,65
4201344e:	fcc9                	bnez	s1,420133e8 <jd_prepare+0x37a>
42013450:	b165                	j	420130f8 <jd_prepare+0x8a>
42013452:	20000793          	li	a5,512
42013456:	e497e5e3          	bltu	a5,s1,420132a0 <jd_prepare+0x232>
4201345a:	583c                	lw	a5,112(s0)
4201345c:	8626                	mv	a2,s1
4201345e:	85ca                	mv	a1,s2
42013460:	8522                	mv	a0,s0
42013462:	9782                	jalr	a5
42013464:	d29515e3          	bne	a0,s1,4201318e <jd_prepare+0x120>
42013468:	01c45783          	lhu	a5,28(s0)
4201346c:	c3cd                	beqz	a5,4201350e <jd_prepare+0x4a0>
4201346e:	01e45783          	lhu	a5,30(s0)
42013472:	cfd1                	beqz	a5,4201350e <jd_prepare+0x4a0>
42013474:	01344583          	lbu	a1,19(s0)
42013478:	00094783          	lbu	a5,0(s2)
4201347c:	e2b791e3          	bne	a5,a1,4201329e <jd_prepare+0x230>
42013480:	00290613          	addi	a2,s2,2
42013484:	4701                	li	a4,0
42013486:	06b76563          	bltu	a4,a1,420134f0 <jd_prepare+0x482>
4201348a:	00f44483          	lbu	s1,15(s0)
4201348e:	00e44783          	lbu	a5,14(s0)
42013492:	02f484b3          	mul	s1,s1,a5
42013496:	cca5                	beqz	s1,4201350e <jd_prepare+0x4a0>
42013498:	00749593          	slli	a1,s1,0x7
4201349c:	04058593          	addi	a1,a1,64
420134a0:	10000793          	li	a5,256
420134a4:	00f5f363          	bgeu	a1,a5,420134aa <jd_prepare+0x43c>
420134a8:	85be                	mv	a1,a5
420134aa:	8522                	mv	a0,s0
420134ac:	a3dff0ef          	jal	42012ee8 <alloc_pool>
420134b0:	d028                	sw	a0,96(s0)
420134b2:	e40502e3          	beqz	a0,420132f6 <jd_prepare+0x288>
420134b6:	00248593          	addi	a1,s1,2
420134ba:	059a                	slli	a1,a1,0x6
420134bc:	8522                	mv	a0,s0
420134be:	a2bff0ef          	jal	42012ee8 <alloc_pool>
420134c2:	d068                	sw	a0,100(s0)
420134c4:	e20509e3          	beqz	a0,420132f6 <jd_prepare+0x288>
420134c8:	1ff9f993          	andi	s3,s3,511
420134cc:	00098c63          	beqz	s3,420134e4 <jd_prepare+0x476>
420134d0:	583c                	lw	a5,112(s0)
420134d2:	20000613          	li	a2,512
420134d6:	41360633          	sub	a2,a2,s3
420134da:	013905b3          	add	a1,s2,s3
420134de:	8522                	mv	a0,s0
420134e0:	9782                	jalr	a5
420134e2:	c008                	sw	a0,0(s0)
420134e4:	19fd                	addi	s3,s3,-1
420134e6:	99ca                	add	s3,s3,s2
420134e8:	01342223          	sw	s3,4(s0)
420134ec:	4c81                	li	s9,0
420134ee:	bb4d                	j	420132a0 <jd_prepare+0x232>
420134f0:	00064783          	lbu	a5,0(a2)
420134f4:	fef78693          	addi	a3,a5,-17
420134f8:	c299                	beqz	a3,420134fe <jd_prepare+0x490>
420134fa:	da0792e3          	bnez	a5,4201329e <jd_prepare+0x230>
420134fe:	00e037b3          	snez	a5,a4
42013502:	00478693          	addi	a3,a5,4
42013506:	068e                	slli	a3,a3,0x3
42013508:	96a2                	add	a3,a3,s0
4201350a:	4294                	lw	a3,0(a3)
4201350c:	e299                	bnez	a3,42013512 <jd_prepare+0x4a4>
4201350e:	4c99                	li	s9,6
42013510:	bb41                	j	420132a0 <jd_prepare+0x232>
42013512:	078e                	slli	a5,a5,0x3
42013514:	97a2                	add	a5,a5,s0
42013516:	53dc                	lw	a5,36(a5)
42013518:	dbfd                	beqz	a5,4201350e <jd_prepare+0x4a0>
4201351a:	00e407b3          	add	a5,s0,a4
4201351e:	0107c783          	lbu	a5,16(a5)
42013522:	0705                	addi	a4,a4,1
42013524:	0609                	addi	a2,a2,2
42013526:	07d1                	addi	a5,a5,20
42013528:	078a                	slli	a5,a5,0x2
4201352a:	97a2                	add	a5,a5,s0
4201352c:	439c                	lw	a5,0(a5)
4201352e:	ffa1                	bnez	a5,42013486 <jd_prepare+0x418>
42013530:	bff9                	j	4201350e <jd_prepare+0x4a0>


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200f456 <media_validate_jpeg_unlocked>:
4200f456:	7179                	addi	sp,sp,-48
4200f458:	ce02                	sw	zero,28(sp)
4200f45a:	c42a                	sw	a0,8(sp)
4200f45c:	c62e                	sw	a1,12(sp)
4200f45e:	4705                	li	a4,1
4200f460:	85b2                	mv	a1,a2
4200f462:	0028                	addi	a0,sp,8
4200f464:	8636                	mv	a2,a3
4200f466:	d606                	sw	ra,44(sp)
4200f468:	c802                	sw	zero,16(sp)
4200f46a:	ca02                	sw	zero,20(sp)
4200f46c:	cc02                	sw	zero,24(sp)
4200f46e:	00e10e23          	sb	a4,28(sp)
4200f472:	c7bff0ef          	jal	4200f0ec <jpeg_decode_unlocked>
4200f476:	50b2                	lw	ra,44(sp)
4200f478:	6145                	addi	sp,sp,48
4200f47a:	8082                	ret


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200f47c <media_draw_jpeg>:
4200f47c:	1101                	addi	sp,sp,-32
4200f47e:	ca26                	sw	s1,20(sp)
4200f480:	3fcb44b7          	lui	s1,0x3fcb4
4200f484:	cc22                	sw	s0,24(sp)
4200f486:	842a                	mv	s0,a0
4200f488:	9044a503          	lw	a0,-1788(s1) # 3fcb3904 <media_mutex>
4200f48c:	c84a                	sw	s2,16(sp)
4200f48e:	892e                	mv	s2,a1
4200f490:	55fd                	li	a1,-1
4200f492:	ce06                	sw	ra,28(sp)
4200f494:	c632                	sw	a2,12(sp)
4200f496:	c436                	sw	a3,8(sp)
4200f498:	07c9d0ef          	jal	420ac514 <xQueueSemaphoreTake>
4200f49c:	2605                	jal	4200f7bc <photo_upload_active_unlocked>
4200f49e:	e515                	bnez	a0,4200f4ca <media_draw_jpeg+0x4e>
4200f4a0:	46a2                	lw	a3,8(sp)
4200f4a2:	4632                	lw	a2,12(sp)
4200f4a4:	8522                	mv	a0,s0
4200f4a6:	85ca                	mv	a1,s2
4200f4a8:	d1fff0ef          	jal	4200f1c6 <draw_jpeg_unlocked>
4200f4ac:	842a                	mv	s0,a0
4200f4ae:	9044a503          	lw	a0,-1788(s1)
4200f4b2:	4681                	li	a3,0
4200f4b4:	4601                	li	a2,0
4200f4b6:	4581                	li	a1,0
4200f4b8:	43d9c0ef          	jal	420ac0f4 <xQueueGenericSend>
4200f4bc:	40f2                	lw	ra,28(sp)
4200f4be:	8522                	mv	a0,s0
4200f4c0:	4462                	lw	s0,24(sp)
4200f4c2:	44d2                	lw	s1,20(sp)
4200f4c4:	4942                	lw	s2,16(sp)
4200f4c6:	6105                	addi	sp,sp,32
4200f4c8:	8082                	ret
4200f4ca:	10300413          	li	s0,259
4200f4ce:	b7c5                	j	4200f4ae <media_draw_jpeg+0x32>
