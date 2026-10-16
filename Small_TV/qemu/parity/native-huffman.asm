
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
420130bc:	22050e63          	beqz	a0,420132f8 <jd_prepare+0x28a>
420130c0:	6a41                	lui	s4,0x10
420130c2:	892a                	mv	s2,a0
420130c4:	4981                	li	s3,0
420130c6:	4481                	li	s1,0
420130c8:	4b05                	li	s6,1
420130ca:	fd8a0a13          	addi	s4,s4,-40 # ffd8 <CSR_UINTSTATUS+0xf327>
420130ce:	583c                	lw	a5,112(s0)
420130d0:	4605                	li	a2,1
420130d2:	85ca                	mv	a1,s2
420130d4:	8522                	mv	a0,s0
420130d6:	9782                	jalr	a5
420130d8:	c42a                	sw	a0,8(sp)
420130da:	0b651b63          	bne	a0,s6,42013190 <jd_prepare+0x122>
420130de:	00094783          	lbu	a5,0(s2)
420130e2:	04a2                	slli	s1,s1,0x8
420130e4:	0985                	addi	s3,s3,1
420130e6:	8cdd                	or	s1,s1,a5
420130e8:	04c2                	slli	s1,s1,0x10
420130ea:	80c1                	srli	s1,s1,0x10
420130ec:	ff4491e3          	bne	s1,s4,420130ce <jd_prepare+0x60>
420130f0:	6a41                	lui	s4,0x10
420130f2:	1a7d                	addi	s4,s4,-1 # ffff <CSR_UINTSTATUS+0xf34e>
420130f4:	0ff00c13          	li	s8,255
420130f8:	4cc5                	li	s9,17
420130fa:	583c                	lw	a5,112(s0)
420130fc:	4611                	li	a2,4
420130fe:	85ca                	mv	a1,s2
42013100:	8522                	mv	a0,s0
42013102:	9782                	jalr	a5
42013104:	4791                	li	a5,4
42013106:	8d2a                	mv	s10,a0
42013108:	08f51463          	bne	a0,a5,42013190 <jd_prepare+0x122>
4201310c:	00095703          	lhu	a4,0(s2)
42013110:	09470263          	beq	a4,s4,42013194 <jd_prepare+0x126>
42013114:	00875793          	srli	a5,a4,0x8
42013118:	0722                	slli	a4,a4,0x8
4201311a:	97ba                	add	a5,a5,a4
4201311c:	00295703          	lhu	a4,2(s2)
42013120:	07c2                	slli	a5,a5,0x10
42013122:	83c1                	srli	a5,a5,0x10
42013124:	00875493          	srli	s1,a4,0x8
42013128:	0722                	slli	a4,a4,0x8
4201312a:	94ba                	add	s1,s1,a4
4201312c:	04c2                	slli	s1,s1,0x10
4201312e:	80c1                	srli	s1,s1,0x10
42013130:	4709                	li	a4,2
42013132:	3e977963          	bgeu	a4,s1,42013524 <jd_prepare+0x4b6>
42013136:	0087d713          	srli	a4,a5,0x8
4201313a:	3f871563          	bne	a4,s8,42013524 <jd_prepare+0x4b6>
4201313e:	14f9                	addi	s1,s1,-2
42013140:	0991                	addi	s3,s3,4
42013142:	0ff7f793          	zext.b	a5,a5
42013146:	0da00713          	li	a4,218
4201314a:	99a6                	add	s3,s3,s1
4201314c:	30e78e63          	beq	a5,a4,42013468 <jd_prepare+0x3fa>
42013150:	06f76663          	bltu	a4,a5,420131bc <jd_prepare+0x14e>
42013154:	f4078793          	addi	a5,a5,-192
42013158:	07c2                	slli	a5,a5,0x10
4201315a:	83c1                	srli	a5,a5,0x10
4201315c:	4765                	li	a4,25
4201315e:	02f76263          	bltu	a4,a5,42013182 <jd_prepare+0x114>
42013162:	4705                	li	a4,1
42013164:	0200fdb7          	lui	s11,0x200f
42013168:	00f71733          	sll	a4,a4,a5
4201316c:	eeed8d93          	addi	s11,s11,-274 # 200eeee <CSR_UINTSTATUS+0x200e23d>
42013170:	01b77db3          	and	s11,a4,s11
42013174:	120d9663          	bnez	s11,420132a0 <jd_prepare+0x232>
42013178:	4691                	li	a3,4
4201317a:	14d78463          	beq	a5,a3,420132c2 <jd_prepare+0x254>
4201317e:	8b05                	andi	a4,a4,1
42013180:	eb35                	bnez	a4,420131f4 <jd_prepare+0x186>
42013182:	583c                	lw	a5,112(s0)
42013184:	8626                	mv	a2,s1
42013186:	4581                	li	a1,0
42013188:	8522                	mv	a0,s0
4201318a:	9782                	jalr	a5
4201318c:	f69507e3          	beq	a0,s1,420130fa <jd_prepare+0x8c>
42013190:	4d09                	li	s10,2
42013192:	aa01                	j	420132a2 <jd_prepare+0x234>
42013194:	583c                	lw	a5,112(s0)
42013196:	4605                	li	a2,1
42013198:	00490593          	addi	a1,s2,4
4201319c:	8522                	mv	a0,s0
4201319e:	9782                	jalr	a5
420131a0:	4785                	li	a5,1
420131a2:	fef517e3          	bne	a0,a5,42013190 <jd_prepare+0x122>
420131a6:	00195703          	lhu	a4,1(s2)
420131aa:	00875793          	srli	a5,a4,0x8
420131ae:	0722                	slli	a4,a4,0x8
420131b0:	97ba                	add	a5,a5,a4
420131b2:	07c2                	slli	a5,a5,0x10
420131b4:	00395703          	lhu	a4,3(s2)
420131b8:	83c1                	srli	a5,a5,0x10
420131ba:	b7ad                	j	42013124 <jd_prepare+0xb6>
420131bc:	0db00713          	li	a4,219
420131c0:	20e78c63          	beq	a5,a4,420133d8 <jd_prepare+0x36a>
420131c4:	0dd00713          	li	a4,221
420131c8:	fae79de3          	bne	a5,a4,42013182 <jd_prepare+0x114>
420131cc:	20000793          	li	a5,512
420131d0:	0c97e963          	bltu	a5,s1,420132a2 <jd_prepare+0x234>
420131d4:	583c                	lw	a5,112(s0)
420131d6:	8626                	mv	a2,s1
420131d8:	85ca                	mv	a1,s2
420131da:	8522                	mv	a0,s0
420131dc:	9782                	jalr	a5
420131de:	fa9519e3          	bne	a0,s1,42013190 <jd_prepare+0x122>
420131e2:	00095783          	lhu	a5,0(s2)
420131e6:	0087d713          	srli	a4,a5,0x8
420131ea:	07a2                	slli	a5,a5,0x8
420131ec:	97ba                	add	a5,a5,a4
420131ee:	00f41d23          	sh	a5,26(s0)
420131f2:	b721                	j	420130fa <jd_prepare+0x8c>
420131f4:	20000793          	li	a5,512
420131f8:	0a97e563          	bltu	a5,s1,420132a2 <jd_prepare+0x234>
420131fc:	583c                	lw	a5,112(s0)
420131fe:	8626                	mv	a2,s1
42013200:	85ca                	mv	a1,s2
42013202:	8522                	mv	a0,s0
42013204:	9782                	jalr	a5
42013206:	f89515e3          	bne	a0,s1,42013190 <jd_prepare+0x122>
4201320a:	4795                	li	a5,5
4201320c:	3097fc63          	bgeu	a5,s1,42013524 <jd_prepare+0x4b6>
42013210:	00094703          	lbu	a4,0(s2)
42013214:	47a1                	li	a5,8
42013216:	08f71563          	bne	a4,a5,420132a0 <jd_prepare+0x232>
4201321a:	00395783          	lhu	a5,3(s2)
4201321e:	0087d713          	srli	a4,a5,0x8
42013222:	07a2                	slli	a5,a5,0x8
42013224:	97ba                	add	a5,a5,a4
42013226:	00f41e23          	sh	a5,28(s0)
4201322a:	00195783          	lhu	a5,1(s2)
4201322e:	0087d713          	srli	a4,a5,0x8
42013232:	07a2                	slli	a5,a5,0x8
42013234:	97ba                	add	a5,a5,a4
42013236:	00f41f23          	sh	a5,30(s0)
4201323a:	00594683          	lbu	a3,5(s2)
4201323e:	4785                	li	a5,1
42013240:	00d409a3          	sb	a3,19(s0)
42013244:	0fd6f713          	andi	a4,a3,253
42013248:	04f71c63          	bne	a4,a5,420132a0 <jd_prepare+0x232>
4201324c:	478d                	li	a5,3
4201324e:	02f687b3          	mul	a5,a3,a5
42013252:	0799                	addi	a5,a5,6
42013254:	2c979863          	bne	a5,s1,42013524 <jd_prepare+0x4b6>
42013258:	00794783          	lbu	a5,7(s2)
4201325c:	00790713          	addi	a4,s2,7
42013260:	fdf78613          	addi	a2,a5,-33
42013264:	00263613          	sltiu	a2,a2,2
42013268:	e601                	bnez	a2,42013270 <jd_prepare+0x202>
4201326a:	fef78613          	addi	a2,a5,-17
4201326e:	ea0d                	bnez	a2,420132a0 <jd_prepare+0x232>
42013270:	0047d613          	srli	a2,a5,0x4
42013274:	8bbd                	andi	a5,a5,15
42013276:	00c40723          	sb	a2,14(s0)
4201327a:	00f407a3          	sb	a5,15(s0)
4201327e:	460d                	li	a2,3
42013280:	00174783          	lbu	a5,1(a4)
42013284:	01b405b3          	add	a1,s0,s11
42013288:	00f58823          	sb	a5,16(a1)
4201328c:	00f66a63          	bltu	a2,a5,420132a0 <jd_prepare+0x232>
42013290:	0d85                	addi	s11,s11,1
42013292:	e6ddf4e3          	bgeu	s11,a3,420130fa <jd_prepare+0x8c>
42013296:	00374783          	lbu	a5,3(a4)
4201329a:	070d                	addi	a4,a4,3
4201329c:	ff9782e3          	beq	a5,s9,42013280 <jd_prepare+0x212>
420132a0:	4d21                	li	s10,8
420132a2:	40b6                	lw	ra,76(sp)
420132a4:	4426                	lw	s0,72(sp)
420132a6:	4496                	lw	s1,68(sp)
420132a8:	4906                	lw	s2,64(sp)
420132aa:	59f2                	lw	s3,60(sp)
420132ac:	5a62                	lw	s4,56(sp)
420132ae:	5ad2                	lw	s5,52(sp)
420132b0:	5b42                	lw	s6,48(sp)
420132b2:	5bb2                	lw	s7,44(sp)
420132b4:	5c22                	lw	s8,40(sp)
420132b6:	5c92                	lw	s9,36(sp)
420132b8:	4df2                	lw	s11,28(sp)
420132ba:	856a                	mv	a0,s10
420132bc:	5d02                	lw	s10,32(sp)
420132be:	6161                	addi	sp,sp,80
420132c0:	8082                	ret
420132c2:	20000793          	li	a5,512
420132c6:	fc97eee3          	bltu	a5,s1,420132a2 <jd_prepare+0x234>
420132ca:	583c                	lw	a5,112(s0)
420132cc:	8626                	mv	a2,s1
420132ce:	85ca                	mv	a1,s2
420132d0:	8522                	mv	a0,s0
420132d2:	9782                	jalr	a5
420132d4:	ea951ee3          	bne	a0,s1,42013190 <jd_prepare+0x122>
420132d8:	8d4a                	mv	s10,s2
420132da:	4dc1                	li	s11,16
420132dc:	249df463          	bgeu	s11,s1,42013524 <jd_prepare+0x4b6>
420132e0:	000d4a83          	lbu	s5,0(s10)
420132e4:	0eeaf713          	andi	a4,s5,238
420132e8:	22071e63          	bnez	a4,42013524 <jd_prepare+0x4b6>
420132ec:	45c1                	li	a1,16
420132ee:	8522                	mv	a0,s0
420132f0:	bf9ff0ef          	jal	42012ee8 <alloc_pool>
420132f4:	882a                	mv	a6,a0
420132f6:	e119                	bnez	a0,420132fc <jd_prepare+0x28e>
420132f8:	4d0d                	li	s10,3
420132fa:	b765                	j	420132a2 <jd_prepare+0x234>
420132fc:	00faf793          	andi	a5,s5,15
42013300:	001d0b13          	addi	s6,s10,1
42013304:	0786                	slli	a5,a5,0x1
42013306:	004add13          	srli	s10,s5,0x4
4201330a:	97ea                	add	a5,a5,s10
4201330c:	078a                	slli	a5,a5,0x2
4201330e:	4622                	lw	a2,8(sp)
42013310:	00f40bb3          	add	s7,s0,a5
42013314:	02aba023          	sw	a0,32(s7)
42013318:	4a81                	li	s5,0
4201331a:	4581                	li	a1,0
4201331c:	000b4503          	lbu	a0,0(s6)
42013320:	00b808b3          	add	a7,a6,a1
42013324:	0606                	slli	a2,a2,0x1
42013326:	00a88023          	sb	a0,0(a7)
4201332a:	1ea66d63          	bltu	a2,a0,42013524 <jd_prepare+0x4b6>
4201332e:	0585                	addi	a1,a1,1
42013330:	0b05                	addi	s6,s6,1
42013332:	8e09                	sub	a2,a2,a0
42013334:	9aaa                	add	s5,s5,a0
42013336:	ffb593e3          	bne	a1,s11,4201331c <jd_prepare+0x2ae>
4201333a:	001a9593          	slli	a1,s5,0x1
4201333e:	8522                	mv	a0,s0
42013340:	c642                	sw	a6,12(sp)
42013342:	ba7ff0ef          	jal	42012ee8 <alloc_pool>
42013346:	d94d                	beqz	a0,420132f8 <jd_prepare+0x28a>
42013348:	4832                	lw	a6,12(sp)
4201334a:	fef48893          	addi	a7,s1,-17
4201334e:	02aba823          	sw	a0,48(s7)
42013352:	4e01                	li	t3,0
42013354:	4301                	li	t1,0
42013356:	4601                	li	a2,0
42013358:	4f41                	li	t5,16
4201335a:	006805b3          	add	a1,a6,t1
4201335e:	0005ce83          	lbu	t4,0(a1)
42013362:	001e1593          	slli	a1,t3,0x1
42013366:	95aa                	add	a1,a1,a0
42013368:	8fb2                	mv	t6,a2
4201336a:	84f6                	mv	s1,t4
4201336c:	e0a9                	bnez	s1,420133ae <jd_prepare+0x340>
4201336e:	9676                	add	a2,a2,t4
42013370:	0606                	slli	a2,a2,0x1
42013372:	0642                	slli	a2,a2,0x10
42013374:	0305                	addi	t1,t1,1
42013376:	9e76                	add	t3,t3,t4
42013378:	8241                	srli	a2,a2,0x10
4201337a:	ffe310e3          	bne	t1,t5,4201335a <jd_prepare+0x2ec>
4201337e:	1b58e363          	bltu	a7,s5,42013524 <jd_prepare+0x4b6>
42013382:	85d6                	mv	a1,s5
42013384:	8522                	mv	a0,s0
42013386:	c646                	sw	a7,12(sp)
42013388:	b61ff0ef          	jal	42012ee8 <alloc_pool>
4201338c:	d535                	beqz	a0,420132f8 <jd_prepare+0x28a>
4201338e:	48b2                	lw	a7,12(sp)
42013390:	001d4d13          	xori	s10,s10,1
42013394:	04aba023          	sw	a0,64(s7)
42013398:	001d7d13          	andi	s10,s10,1
4201339c:	009a9f63          	bne	s5,s1,420133ba <jd_prepare+0x34c>
420133a0:	415884b3          	sub	s1,a7,s5
420133a4:	d5588be3          	beq	a7,s5,420130fa <jd_prepare+0x8c>
420133a8:	015b0d33          	add	s10,s6,s5
420133ac:	bf05                	j	420132dc <jd_prepare+0x26e>
420133ae:	01f59023          	sh	t6,0(a1)
420133b2:	14fd                	addi	s1,s1,-1
420133b4:	0589                	addi	a1,a1,2
420133b6:	0f85                	addi	t6,t6,1
420133b8:	bf55                	j	4201336c <jd_prepare+0x2fe>
420133ba:	009b07b3          	add	a5,s6,s1
420133be:	0007c783          	lbu	a5,0(a5)
420133c2:	00c7b613          	sltiu	a2,a5,12
420133c6:	e219                	bnez	a2,420133cc <jd_prepare+0x35e>
420133c8:	140d1e63          	bnez	s10,42013524 <jd_prepare+0x4b6>
420133cc:	00950633          	add	a2,a0,s1
420133d0:	00f60023          	sb	a5,0(a2)
420133d4:	0485                	addi	s1,s1,1
420133d6:	b7d9                	j	4201339c <jd_prepare+0x32e>
420133d8:	20000793          	li	a5,512
420133dc:	ec97e3e3          	bltu	a5,s1,420132a2 <jd_prepare+0x234>
420133e0:	583c                	lw	a5,112(s0)
420133e2:	8626                	mv	a2,s1
420133e4:	85ca                	mv	a1,s2
420133e6:	8522                	mv	a0,s0
420133e8:	9782                	jalr	a5
420133ea:	da9513e3          	bne	a0,s1,42013190 <jd_prepare+0x122>
420133ee:	8dca                	mv	s11,s2
420133f0:	04000813          	li	a6,64
420133f4:	488d                	li	a7,3
420133f6:	12987763          	bgeu	a6,s1,42013524 <jd_prepare+0x4b6>
420133fa:	000dcd03          	lbu	s10,0(s11)
420133fe:	13a8e363          	bltu	a7,s10,42013524 <jd_prepare+0x4b6>
42013402:	10000593          	li	a1,256
42013406:	8522                	mv	a0,s0
42013408:	ae1ff0ef          	jal	42012ee8 <alloc_pool>
4201340c:	ee0506e3          	beqz	a0,420132f8 <jd_prepare+0x28a>
42013410:	0d51                	addi	s10,s10,20
42013412:	3c0ec7b7          	lui	a5,0x3c0ec
42013416:	0d0a                	slli	s10,s10,0x2
42013418:	9d22                	add	s10,s10,s0
4201341a:	9d478613          	addi	a2,a5,-1580 # 3c0eb9d4 <Ipsf>
4201341e:	3c0ec7b7          	lui	a5,0x3c0ec
42013422:	fbf48493          	addi	s1,s1,-65
42013426:	00ad2023          	sw	a0,0(s10)
4201342a:	4701                	li	a4,0
4201342c:	a5478693          	addi	a3,a5,-1452 # 3c0eba54 <Zig>
42013430:	04000813          	li	a6,64
42013434:	488d                	li	a7,3
42013436:	00d707b3          	add	a5,a4,a3
4201343a:	0007c783          	lbu	a5,0(a5)
4201343e:	00ed8333          	add	t1,s11,a4
42013442:	00134303          	lbu	t1,1(t1)
42013446:	00279593          	slli	a1,a5,0x2
4201344a:	0786                	slli	a5,a5,0x1
4201344c:	97b2                	add	a5,a5,a2
4201344e:	0007d783          	lhu	a5,0(a5)
42013452:	95aa                	add	a1,a1,a0
42013454:	0705                	addi	a4,a4,1
42013456:	02f307b3          	mul	a5,t1,a5
4201345a:	c19c                	sw	a5,0(a1)
4201345c:	fd071de3          	bne	a4,a6,42013436 <jd_prepare+0x3c8>
42013460:	041d8d93          	addi	s11,s11,65
42013464:	f8c9                	bnez	s1,420133f6 <jd_prepare+0x388>
42013466:	b951                	j	420130fa <jd_prepare+0x8c>
42013468:	20000793          	li	a5,512
4201346c:	e297ebe3          	bltu	a5,s1,420132a2 <jd_prepare+0x234>
42013470:	583c                	lw	a5,112(s0)
42013472:	8626                	mv	a2,s1
42013474:	85ca                	mv	a1,s2
42013476:	8522                	mv	a0,s0
42013478:	9782                	jalr	a5
4201347a:	d0951be3          	bne	a0,s1,42013190 <jd_prepare+0x122>
4201347e:	01c45783          	lhu	a5,28(s0)
42013482:	c3cd                	beqz	a5,42013524 <jd_prepare+0x4b6>
42013484:	01e45783          	lhu	a5,30(s0)
42013488:	cfd1                	beqz	a5,42013524 <jd_prepare+0x4b6>
4201348a:	01344583          	lbu	a1,19(s0)
4201348e:	00094783          	lbu	a5,0(s2)
42013492:	e0b797e3          	bne	a5,a1,420132a0 <jd_prepare+0x232>
42013496:	00290613          	addi	a2,s2,2
4201349a:	4701                	li	a4,0
4201349c:	06b76563          	bltu	a4,a1,42013506 <jd_prepare+0x498>
420134a0:	00f44483          	lbu	s1,15(s0)
420134a4:	00e44783          	lbu	a5,14(s0)
420134a8:	02f484b3          	mul	s1,s1,a5
420134ac:	cca5                	beqz	s1,42013524 <jd_prepare+0x4b6>
420134ae:	00749593          	slli	a1,s1,0x7
420134b2:	04058593          	addi	a1,a1,64
420134b6:	10000793          	li	a5,256
420134ba:	00f5f363          	bgeu	a1,a5,420134c0 <jd_prepare+0x452>
420134be:	85be                	mv	a1,a5
420134c0:	8522                	mv	a0,s0
420134c2:	a27ff0ef          	jal	42012ee8 <alloc_pool>
420134c6:	d028                	sw	a0,96(s0)
420134c8:	e20508e3          	beqz	a0,420132f8 <jd_prepare+0x28a>
420134cc:	00248593          	addi	a1,s1,2
420134d0:	059a                	slli	a1,a1,0x6
420134d2:	8522                	mv	a0,s0
420134d4:	a15ff0ef          	jal	42012ee8 <alloc_pool>
420134d8:	d068                	sw	a0,100(s0)
420134da:	e0050fe3          	beqz	a0,420132f8 <jd_prepare+0x28a>
420134de:	1ff9f993          	andi	s3,s3,511
420134e2:	00098c63          	beqz	s3,420134fa <jd_prepare+0x48c>
420134e6:	583c                	lw	a5,112(s0)
420134e8:	20000613          	li	a2,512
420134ec:	41360633          	sub	a2,a2,s3
420134f0:	013905b3          	add	a1,s2,s3
420134f4:	8522                	mv	a0,s0
420134f6:	9782                	jalr	a5
420134f8:	c008                	sw	a0,0(s0)
420134fa:	19fd                	addi	s3,s3,-1
420134fc:	99ca                	add	s3,s3,s2
420134fe:	01342223          	sw	s3,4(s0)
42013502:	4d01                	li	s10,0
42013504:	bb79                	j	420132a2 <jd_prepare+0x234>
42013506:	00064783          	lbu	a5,0(a2)
4201350a:	fef78693          	addi	a3,a5,-17
4201350e:	c299                	beqz	a3,42013514 <jd_prepare+0x4a6>
42013510:	d80798e3          	bnez	a5,420132a0 <jd_prepare+0x232>
42013514:	00e037b3          	snez	a5,a4
42013518:	00478693          	addi	a3,a5,4
4201351c:	068e                	slli	a3,a3,0x3
4201351e:	96a2                	add	a3,a3,s0
42013520:	4294                	lw	a3,0(a3)
42013522:	e299                	bnez	a3,42013528 <jd_prepare+0x4ba>
42013524:	4d19                	li	s10,6
42013526:	bbb5                	j	420132a2 <jd_prepare+0x234>
42013528:	078e                	slli	a5,a5,0x3
4201352a:	97a2                	add	a5,a5,s0
4201352c:	53dc                	lw	a5,36(a5)
4201352e:	dbfd                	beqz	a5,42013524 <jd_prepare+0x4b6>
42013530:	00e407b3          	add	a5,s0,a4
42013534:	0107c783          	lbu	a5,16(a5)
42013538:	0705                	addi	a4,a4,1
4201353a:	0609                	addi	a2,a2,2
4201353c:	07d1                	addi	a5,a5,20
4201353e:	078a                	slli	a5,a5,0x2
42013540:	97a2                	add	a5,a5,s0
42013542:	439c                	lw	a5,0(a5)
42013544:	ffa1                	bnez	a5,4201349c <jd_prepare+0x42e>
42013546:	bff9                	j	42013524 <jd_prepare+0x4b6>


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
4200f498:	0929d0ef          	jal	420ac52a <xQueueSemaphoreTake>
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
4200f4b8:	4539c0ef          	jal	420ac10a <xQueueGenericSend>
4200f4bc:	40f2                	lw	ra,28(sp)
4200f4be:	8522                	mv	a0,s0
4200f4c0:	4462                	lw	s0,24(sp)
4200f4c2:	44d2                	lw	s1,20(sp)
4200f4c4:	4942                	lw	s2,16(sp)
4200f4c6:	6105                	addi	sp,sp,32
4200f4c8:	8082                	ret
4200f4ca:	10300413          	li	s0,259
4200f4ce:	b7c5                	j	4200f4ae <media_draw_jpeg+0x32>
