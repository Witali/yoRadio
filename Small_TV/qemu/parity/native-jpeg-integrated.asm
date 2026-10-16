
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


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200d28e <clock_task>:
4200d28e:	c5010113          	addi	sp,sp,-944
4200d292:	39512a23          	sw	s5,916(sp)
4200d296:	0ff00793          	li	a5,255
4200d29a:	3fcafab7          	lui	s5,0x3fcaf
4200d29e:	3b212023          	sw	s2,928(sp)
4200d2a2:	39412c23          	sw	s4,920(sp)
4200d2a6:	39712623          	sw	s7,908(sp)
4200d2aa:	39812423          	sw	s8,904(sp)
4200d2ae:	39912223          	sw	s9,900(sp)
4200d2b2:	39a12023          	sw	s10,896(sp)
4200d2b6:	37b12e23          	sw	s11,892(sp)
4200d2ba:	3a112623          	sw	ra,940(sp)
4200d2be:	3a812423          	sw	s0,936(sp)
4200d2c2:	3a912223          	sw	s1,932(sp)
4200d2c6:	39312e23          	sw	s3,924(sp)
4200d2ca:	39612823          	sw	s6,912(sp)
4200d2ce:	04010223          	sb	zero,68(sp)
4200d2d2:	04011423          	sh	zero,72(sp)
4200d2d6:	4c01                	li	s8,0
4200d2d8:	d002                	sw	zero,32(sp)
4200d2da:	4d01                	li	s10,0
4200d2dc:	ce02                	sw	zero,28(sp)
4200d2de:	cc3e                	sw	a5,24(sp)
4200d2e0:	ca02                	sw	zero,20(sp)
4200d2e2:	4901                	li	s2,0
4200d2e4:	d202                	sw	zero,36(sp)
4200d2e6:	4c81                	li	s9,0
4200d2e8:	4a01                	li	s4,0
4200d2ea:	c802                	sw	zero,16(sp)
4200d2ec:	4b81                	li	s7,0
4200d2ee:	4d85                	li	s11,1
4200d2f0:	73ca8a93          	addi	s5,s5,1852 # 3fcaf73c <timer_state>
4200d2f4:	0448                	addi	a0,sp,516
4200d2f6:	99aff0ef          	jal	4200c490 <settings_snapshot>
4200d2fa:	0228                	addi	a0,sp,264
4200d2fc:	695030ef          	jal	42011190 <weather_snapshot>
4200d300:	35114603          	lbu	a2,849(sp)
4200d304:	4581                	li	a1,0
4200d306:	00e8                	addi	a0,sp,76
4200d308:	f27ff0ef          	jal	4200d22e <timer_snapshot>
4200d30c:	05a14783          	lbu	a5,90(sp)
4200d310:	d63e                	sw	a5,44(sp)
4200d312:	72d020ef          	jal	4201023e <network_connected>
4200d316:	45d1                	li	a1,20
4200d318:	8b2a                	mv	s6,a0
4200d31a:	1168                	addi	a0,sp,172
4200d31c:	757020ef          	jal	42010272 <network_address>
4200d320:	4501                	li	a0,0
4200d322:	7b18f0ef          	jal	4209d2d2 <time>
4200d326:	c62e                	sw	a1,12(sp)
4200d328:	4632                	lw	a2,12(sp)
4200d32a:	c42a                	sw	a0,8(sp)
4200d32c:	85aa                	mv	a1,a0
4200d32e:	11d4                	addi	a3,sp,228
4200d330:	2ab10513          	addi	a0,sp,683
4200d334:	528030ef          	jal	4201085c <services_local_time>
4200d338:	89aa                	mv	s3,a0
4200d33a:	e51d                	bnez	a0,4200d368 <clock_task+0xda>
4200d33c:	4781                	li	a5,0
4200d33e:	10f12023          	sw	a5,256(sp)
4200d342:	02800793          	li	a5,40
4200d346:	d3be                	sw	a5,228(sp)
4200d348:	4791                	li	a5,4
4200d34a:	d5be                	sw	a5,232(sp)
4200d34c:	47c5                	li	a5,17
4200d34e:	d7be                	sw	a5,236(sp)
4200d350:	47cd                	li	a5,19
4200d352:	d9be                	sw	a5,240(sp)
4200d354:	47a1                	li	a5,8
4200d356:	dbbe                	sw	a5,244(sp)
4200d358:	07d00793          	li	a5,125
4200d35c:	4801                	li	a6,0
4200d35e:	ddbe                	sw	a5,248(sp)
4200d360:	4795                	li	a5,5
4200d362:	11012223          	sw	a6,260(sp)
4200d366:	dfbe                	sw	a5,252(sp)
4200d368:	02400613          	li	a2,36
4200d36c:	11cc                	addi	a1,sp,228
4200d36e:	0188                	addi	a0,sp,192
4200d370:	fe37a097          	auipc	ra,0xfe37a
4200d374:	eca080e7          	jalr	-310(ra) # 4038723a <memcpy>
4200d378:	a7cff0ef          	jal	4200c5f4 <settings_generation>
4200d37c:	d42a                	sw	a0,40(sp)
4200d37e:	4405                	li	s0,1
4200d380:	00ab9e63          	bne	s7,a0,4200d39c <clock_task+0x10e>
4200d384:	47c2                	lw	a5,16(sp)
4200d386:	1f812403          	lw	s0,504(sp)
4200d38a:	8c1d                	sub	s0,s0,a5
4200d38c:	5782                	lw	a5,32(sp)
4200d38e:	00803433          	snez	s0,s0
4200d392:	0137c7b3          	xor	a5,a5,s3
4200d396:	8c5d                	or	s0,s0,a5
4200d398:	0ff47413          	zext.b	s0,s0
4200d39c:	000b0d63          	beqz	s6,4200d3b6 <clock_task+0x128>
4200d3a0:	10814783          	lbu	a5,264(sp)
4200d3a4:	eb89                	bnez	a5,4200d3b6 <clock_task+0x128>
4200d3a6:	671030ef          	jal	42011216 <weather_request_active>
4200d3aa:	e511                	bnez	a0,4200d3b6 <clock_task+0x128>
4200d3ac:	000c1d63          	bnez	s8,4200d3c6 <clock_task+0x138>
4200d3b0:	625030ef          	jal	420111d4 <weather_request_update>
4200d3b4:	4c79                	li	s8,30
4200d3b6:	06c020ef          	jal	4200f422 <media_upload_active>
4200d3ba:	84aa                	mv	s1,a0
4200d3bc:	c519                	beqz	a0,4200d3ca <clock_task+0x13c>
4200d3be:	4529                	li	a0,10
4200d3c0:	35d9f0ef          	jal	420acf1c <vTaskDelay>
4200d3c4:	bf05                	j	4200d2f4 <clock_task+0x66>
4200d3c6:	1c7d                	addi	s8,s8,-1
4200d3c8:	b7fd                	j	4200d3b6 <clock_task+0x128>
4200d3ca:	57b2                	lw	a5,44(sp)
4200d3cc:	1a078f63          	beqz	a5,4200d58a <clock_task+0x2fc>
4200d3d0:	140b0a63          	beqz	s6,4200d524 <clock_task+0x296>
4200d3d4:	00099763          	bnez	s3,4200d3e2 <clock_task+0x154>
4200d3d8:	34c14703          	lbu	a4,844(sp)
4200d3dc:	4789                	li	a5,2
4200d3de:	14f71363          	bne	a4,a5,4200d524 <clock_task+0x296>
4200d3e2:	fe37b097          	auipc	ra,0xfe37b
4200d3e6:	a54080e7          	jalr	-1452(ra) # 40387e36 <vPortEnterCritical>
4200d3ea:	004aa783          	lw	a5,4(s5)
4200d3ee:	000a8723          	sb	zero,14(s5)
4200d3f2:	f7f7f793          	andi	a5,a5,-129
4200d3f6:	00faa223          	sw	a5,4(s5)
4200d3fa:	fe37b097          	auipc	ra,0xfe37b
4200d3fe:	a68080e7          	jalr	-1432(ra) # 40387e62 <vPortExitCritical>
4200d402:	478d                	li	a5,3
4200d404:	00f91763          	bne	s2,a5,4200d412 <clock_task+0x184>
4200d408:	34c14783          	lbu	a5,844(sp)
4200d40c:	4762                	lw	a4,24(sp)
4200d40e:	04e78b63          	beq	a5,a4,4200d464 <clock_task+0x1d6>
4200d412:	0f000693          	li	a3,240
4200d416:	4701                	li	a4,0
4200d418:	8636                	mv	a2,a3
4200d41a:	4581                	li	a1,0
4200d41c:	4501                	li	a0,0
4200d41e:	fd6ff0ef          	jal	4200cbf4 <display_fill>
4200d422:	34c14703          	lbu	a4,844(sp)
4200d426:	4789                	li	a5,2
4200d428:	442d                	li	s0,11
4200d42a:	00f71363          	bne	a4,a5,4200d430 <clock_task+0x1a2>
4200d42e:	443d                	li	s0,15
4200d430:	fe37b097          	auipc	ra,0xfe37b
4200d434:	a06080e7          	jalr	-1530(ra) # 40387e36 <vPortEnterCritical>
4200d438:	004aa783          	lw	a5,4(s5)
4200d43c:	8fc1                	or	a5,a5,s0
4200d43e:	00faa223          	sw	a5,4(s5)
4200d442:	fe37b097          	auipc	ra,0xfe37b
4200d446:	a20080e7          	jalr	-1504(ra) # 40387e62 <vPortExitCritical>
4200d44a:	34c14783          	lbu	a5,844(sp)
4200d44e:	00fde863          	bltu	s11,a5,4200d45e <clock_task+0x1d0>
4200d452:	461e                	lw	a2,196(sp)
4200d454:	45ae                	lw	a1,200(sp)
4200d456:	86ce                	mv	a3,s3
4200d458:	0448                	addi	a0,sp,516
4200d45a:	d87ff0ef          	jal	4200d1e0 <backlight_update>
4200d45e:	4485                	li	s1,1
4200d460:	8426                	mv	s0,s1
4200d462:	4a01                	li	s4,0
4200d464:	10814783          	lbu	a5,264(sp)
4200d468:	c399                	beqz	a5,4200d46e <clock_task+0x1e0>
4200d46a:	000d1363          	bnez	s10,4200d470 <clock_task+0x1e2>
4200d46e:	4a01                	li	s4,0
4200d470:	34c14783          	lbu	a5,844(sp)
4200d474:	ef81                	bnez	a5,4200d48c <clock_task+0x1fe>
4200d476:	12048a63          	beqz	s1,4200d5aa <clock_task+0x31c>
4200d47a:	35114603          	lbu	a2,849(sp)
4200d47e:	4589                	li	a1,2
4200d480:	08e8                	addi	a0,sp,92
4200d482:	dadff0ef          	jal	4200d22e <timer_snapshot>
4200d486:	5786                	lw	a5,96(sp)
4200d488:	12079663          	bnez	a5,4200d5b4 <clock_task+0x326>
4200d48c:	34c14783          	lbu	a5,844(sp)
4200d490:	14079e63          	bnez	a5,4200d5ec <clock_task+0x35e>
4200d494:	34d14503          	lbu	a0,845(sp)
4200d498:	0c8020ef          	jal	4200f560 <media_animation_frames>
4200d49c:	85aa                	mv	a1,a0
4200d49e:	00c8                	addi	a0,sp,68
4200d4a0:	2105                	jal	4200d8c0 <factory_animation_next>
4200d4a2:	35114603          	lbu	a2,849(sp)
4200d4a6:	892a                	mv	s2,a0
4200d4a8:	45a1                	li	a1,8
4200d4aa:	10e8                	addi	a0,sp,108
4200d4ac:	d83ff0ef          	jal	4200d22e <timer_snapshot>
4200d4b0:	4722                	lw	a4,8(sp)
4200d4b2:	5792                	lw	a5,36(sp)
4200d4b4:	5846                	lw	a6,112(sp)
4200d4b6:	8fb9                	xor	a5,a5,a4
4200d4b8:	4732                	lw	a4,12(sp)
4200d4ba:	01003833          	snez	a6,a6
4200d4be:	00ecc733          	xor	a4,s9,a4
4200d4c2:	8fd9                	or	a5,a5,a4
4200d4c4:	00f037b3          	snez	a5,a5
4200d4c8:	00f867b3          	or	a5,a6,a5
4200d4cc:	e399                	bnez	a5,4200d4d2 <clock_task+0x244>
4200d4ce:	10040463          	beqz	s0,4200d5d6 <clock_task+0x348>
4200d4d2:	fff94713          	not	a4,s2
4200d4d6:	877d                	srai	a4,a4,0x1f
4200d4d8:	87a6                	mv	a5,s1
4200d4da:	00e97733          	and	a4,s2,a4
4200d4de:	86d2                	mv	a3,s4
4200d4e0:	0230                	addi	a2,sp,264
4200d4e2:	018c                	addi	a1,sp,192
4200d4e4:	0448                	addi	a0,sp,516
4200d4e6:	6a1000ef          	jal	4200e386 <factory_draw_classic>
4200d4ea:	4a1000ef          	jal	4200e18a <factory_scroll_tick>
4200d4ee:	34c14703          	lbu	a4,844(sp)
4200d4f2:	4789                	li	a5,2
4200d4f4:	00f70863          	beq	a4,a5,4200d504 <clock_task+0x276>
4200d4f8:	461e                	lw	a2,196(sp)
4200d4fa:	45ae                	lw	a1,200(sp)
4200d4fc:	86ce                	mv	a3,s3
4200d4fe:	0448                	addi	a0,sp,516
4200d500:	ce1ff0ef          	jal	4200d1e0 <backlight_update>
4200d504:	34c14783          	lbu	a5,844(sp)
4200d508:	35114603          	lbu	a2,849(sp)
4200d50c:	04000593          	li	a1,64
4200d510:	0968                	addi	a0,sp,156
4200d512:	cc3e                	sw	a5,24(sp)
4200d514:	d1bff0ef          	jal	4200d22e <timer_snapshot>
4200d518:	578a                	lw	a5,160(sp)
4200d51a:	c399                	beqz	a5,4200d520 <clock_task+0x292>
4200d51c:	4b9030ef          	jal	420111d4 <weather_request_update>
4200d520:	490d                	li	s2,3
4200d522:	a0a9                	j	4200d56c <clock_task+0x2de>
4200d524:	05914403          	lbu	s0,89(sp)
4200d528:	47d2                	lw	a5,20(sp)
4200d52a:	197d                	addi	s2,s2,-1
4200d52c:	01203933          	snez	s2,s2
4200d530:	8f81                	sub	a5,a5,s0
4200d532:	00f037b3          	snez	a5,a5
4200d536:	0127e7b3          	or	a5,a5,s2
4200d53a:	e799                	bnez	a5,4200d548 <clock_task+0x2ba>
4200d53c:	47f2                	lw	a5,28(sp)
4200d53e:	0167c7b3          	xor	a5,a5,s6
4200d542:	0ff7f793          	zext.b	a5,a5
4200d546:	cb91                	beqz	a5,4200d55a <clock_task+0x2cc>
4200d548:	01603533          	snez	a0,s6
4200d54c:	40a00533          	neg	a0,a0
4200d550:	117c                	addi	a5,sp,172
4200d552:	85a2                	mv	a1,s0
4200d554:	8d7d                	and	a0,a0,a5
4200d556:	569000ef          	jal	4200e2be <factory_draw_startup>
4200d55a:	35114603          	lbu	a2,849(sp)
4200d55e:	08000593          	li	a1,128
4200d562:	1808                	addi	a0,sp,48
4200d564:	ccbff0ef          	jal	4200d22e <timer_snapshot>
4200d568:	4905                	li	s2,1
4200d56a:	ca22                	sw	s0,20(sp)
4200d56c:	1f812783          	lw	a5,504(sp)
4200d570:	4529                	li	a0,10
4200d572:	10814d03          	lbu	s10,264(sp)
4200d576:	c83e                	sw	a5,16(sp)
4200d578:	1a59f0ef          	jal	420acf1c <vTaskDelay>
4200d57c:	47a2                	lw	a5,8(sp)
4200d57e:	4cb2                	lw	s9,12(sp)
4200d580:	5ba2                	lw	s7,40(sp)
4200d582:	d04e                	sw	s3,32(sp)
4200d584:	ce5a                	sw	s6,28(sp)
4200d586:	d23e                	sw	a5,36(sp)
4200d588:	b3b5                	j	4200d2f4 <clock_task+0x66>
4200d58a:	e60b1ce3          	bnez	s6,4200d402 <clock_task+0x174>
4200d58e:	4cb020ef          	jal	42010258 <network_ap_active>
4200d592:	c901                	beqz	a0,4200d5a2 <clock_task+0x314>
4200d594:	4409                	li	s0,2
4200d596:	fc890be3          	beq	s2,s0,4200d56c <clock_task+0x2de>
4200d59a:	48f000ef          	jal	4200e228 <factory_draw_setup>
4200d59e:	8922                	mv	s2,s0
4200d5a0:	b7f1                	j	4200d56c <clock_task+0x2de>
4200d5a2:	478d                	li	a5,3
4200d5a4:	fcf914e3          	bne	s2,a5,4200d56c <clock_task+0x2de>
4200d5a8:	b585                	j	4200d408 <clock_task+0x17a>
4200d5aa:	45d000ef          	jal	4200e206 <factory_scroll_description_ready>
4200d5ae:	ec0516e3          	bnez	a0,4200d47a <clock_task+0x1ec>
4200d5b2:	bde9                	j	4200d48c <clock_task+0x1fe>
4200d5b4:	e891                	bnez	s1,4200d5c8 <clock_task+0x33a>
4200d5b6:	10814783          	lbu	a5,264(sp)
4200d5ba:	c799                	beqz	a5,4200d5c8 <clock_task+0x33a>
4200d5bc:	000d0663          	beqz	s10,4200d5c8 <clock_task+0x33a>
4200d5c0:	0a05                	addi	s4,s4,1
4200d5c2:	47a9                	li	a5,10
4200d5c4:	02fa7a33          	remu	s4,s4,a5
4200d5c8:	ec0412e3          	bnez	s0,4200d48c <clock_task+0x1fe>
4200d5cc:	34c14403          	lbu	s0,844(sp)
4200d5d0:	00143413          	seqz	s0,s0
4200d5d4:	bd65                	j	4200d48c <clock_task+0x1fe>
4200d5d6:	f0094ae3          	bltz	s2,4200d4ea <clock_task+0x25c>
4200d5da:	34d14503          	lbu	a0,845(sp)
4200d5de:	0a000693          	li	a3,160
4200d5e2:	8636                	mv	a2,a3
4200d5e4:	85ca                	mv	a1,s2
4200d5e6:	7d5010ef          	jal	4200f5ba <media_draw_animation>
4200d5ea:	b701                	j	4200d4ea <clock_task+0x25c>
4200d5ec:	03b79463          	bne	a5,s11,4200d614 <clock_task+0x386>
4200d5f0:	35114603          	lbu	a2,849(sp)
4200d5f4:	18e8                	addi	a0,sp,124
4200d5f6:	45a5                	li	a1,9
4200d5f8:	c37ff0ef          	jal	4200d22e <timer_snapshot>
4200d5fc:	470a                	lw	a4,128(sp)
4200d5fe:	86a6                	mv	a3,s1
4200d600:	1170                	addi	a2,sp,172
4200d602:	00375793          	srli	a5,a4,0x3
4200d606:	8b85                	andi	a5,a5,1
4200d608:	8b05                	andi	a4,a4,1
4200d60a:	018c                	addi	a1,sp,192
4200d60c:	0448                	addi	a0,sp,516
4200d60e:	382010ef          	jal	4200e990 <factory_draw_simple>
4200d612:	bdf1                	j	4200d4ee <clock_task+0x260>
4200d614:	4709                	li	a4,2
4200d616:	0ae79163          	bne	a5,a4,4200d6b8 <clock_task+0x42a>
4200d61a:	0458                	addi	a4,sp,516
4200d61c:	4781                	li	a5,0
4200d61e:	4601                	li	a2,0
4200d620:	4695                	li	a3,5
4200d622:	15872583          	lw	a1,344(a4)
4200d626:	c581                	beqz	a1,4200d62e <clock_task+0x3a0>
4200d628:	00fd95b3          	sll	a1,s11,a5
4200d62c:	8e4d                	or	a2,a2,a1
4200d62e:	0785                	addi	a5,a5,1
4200d630:	0711                	addi	a4,a4,4
4200d632:	fed798e3          	bne	a5,a3,4200d622 <clock_task+0x394>
4200d636:	46c6                	lw	a3,80(sp)
4200d638:	35814583          	lbu	a1,856(sp)
4200d63c:	11dc                	addi	a5,sp,228
4200d63e:	8289                	srli	a3,a3,0x2
4200d640:	8a85                	andi	a3,a3,1
4200d642:	8ec5                	or	a3,a3,s1
4200d644:	4701                	li	a4,0
4200d646:	0ff6f693          	zext.b	a3,a3
4200d64a:	00a8                	addi	a0,sp,72
4200d64c:	2ac9                	jal	4200d81e <factory_photo_step>
4200d64e:	0e714783          	lbu	a5,231(sp)
4200d652:	c789                	beqz	a5,4200d65c <clock_task+0x3ce>
4200d654:	0e415503          	lhu	a0,228(sp)
4200d658:	ab7ff0ef          	jal	4200d10e <backlight_set_level>
4200d65c:	0e610503          	lb	a0,230(sp)
4200d660:	57fd                	li	a5,-1
4200d662:	02f54663          	blt	a0,a5,4200d68e <clock_task+0x400>
4200d666:	04f51563          	bne	a0,a5,4200d6b0 <clock_task+0x422>
4200d66a:	0f000693          	li	a3,240
4200d66e:	8636                	mv	a2,a3
4200d670:	4701                	li	a4,0
4200d672:	4581                	li	a1,0
4200d674:	4501                	li	a0,0
4200d676:	d7eff0ef          	jal	4200cbf4 <display_fill>
4200d67a:	6741                	lui	a4,0x10
4200d67c:	4805                	li	a6,1
4200d67e:	4781                	li	a5,0
4200d680:	177d                	addi	a4,a4,-1 # ffff <CSR_UINTSTATUS+0xf34e>
4200d682:	46c1                	li	a3,16
4200d684:	1170                	addi	a2,sp,172
4200d686:	0e100593          	li	a1,225
4200d68a:	4515                	li	a0,5
4200d68c:	2b61                	jal	4200dc24 <display_factory_text>
4200d68e:	0e814783          	lbu	a5,232(sp)
4200d692:	e4078ee3          	beqz	a5,4200d4ee <clock_task+0x260>
4200d696:	35114603          	lbu	a2,849(sp)
4200d69a:	1808                	addi	a0,sp,48
4200d69c:	4591                	li	a1,4
4200d69e:	b91ff0ef          	jal	4200d22e <timer_snapshot>
4200d6a2:	461e                	lw	a2,196(sp)
4200d6a4:	45ae                	lw	a1,200(sp)
4200d6a6:	86ce                	mv	a3,s3
4200d6a8:	0448                	addi	a0,sp,516
4200d6aa:	b37ff0ef          	jal	4200d1e0 <backlight_update>
4200d6ae:	b581                	j	4200d4ee <clock_task+0x260>
4200d6b0:	116c                	addi	a1,sp,172
4200d6b2:	1f9010ef          	jal	4200f0aa <factory_draw_photo>
4200d6b6:	bfe1                	j	4200d68e <clock_task+0x400>
4200d6b8:	35114603          	lbu	a2,849(sp)
4200d6bc:	4585                	li	a1,1
4200d6be:	0168                	addi	a0,sp,140
4200d6c0:	b6fff0ef          	jal	4200d22e <timer_snapshot>
4200d6c4:	47ca                	lw	a5,144(sp)
4200d6c6:	00f037b3          	snez	a5,a5
4200d6ca:	8fc5                	or	a5,a5,s1
4200d6cc:	0ff7f793          	zext.b	a5,a5
4200d6d0:	e399                	bnez	a5,4200d6d6 <clock_task+0x448>
4200d6d2:	e0040ee3          	beqz	s0,4200d4ee <clock_task+0x260>
4200d6d6:	8626                	mv	a2,s1
4200d6d8:	116c                	addi	a1,sp,172
4200d6da:	0188                	addi	a0,sp,192
4200d6dc:	4d6010ef          	jal	4200ebb2 <factory_draw_dial>
4200d6e0:	b539                	j	4200d4ee <clock_task+0x260>


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

40381f6c <factory_timer_tick>:
40381f6c:	87aa                	mv	a5,a0
40381f6e:	00e54503          	lbu	a0,14(a0)
40381f72:	c115                	beqz	a0,40381f96 <factory_timer_tick+0x2a>
40381f74:	00d7c703          	lbu	a4,13(a5)
40381f78:	0b400693          	li	a3,180
40381f7c:	0705                	addi	a4,a4,1
40381f7e:	0ff77713          	zext.b	a4,a4
40381f82:	00e786a3          	sb	a4,13(a5)
40381f86:	00e6f463          	bgeu	a3,a4,40381f8e <factory_timer_tick+0x22>
40381f8a:	00078723          	sb	zero,14(a5)
40381f8e:	43d8                	lw	a4,4(a5)
40381f90:	08076713          	ori	a4,a4,128
40381f94:	c3d8                	sw	a4,4(a5)
40381f96:	0087c703          	lbu	a4,8(a5)
40381f9a:	46a9                	li	a3,10
40381f9c:	0705                	addi	a4,a4,1
40381f9e:	0ff77713          	zext.b	a4,a4
40381fa2:	00e6e563          	bltu	a3,a4,40381fac <factory_timer_tick+0x40>
40381fa6:	00e78423          	sb	a4,8(a5)
40381faa:	8082                	ret
40381fac:	43d4                	lw	a3,4(a5)
40381fae:	00078423          	sb	zero,8(a5)
40381fb2:	4609                	li	a2,2
40381fb4:	0016e713          	ori	a4,a3,1
40381fb8:	c3d8                	sw	a4,4(a5)
40381fba:	0097c703          	lbu	a4,9(a5)
40381fbe:	0705                	addi	a4,a4,1
40381fc0:	0ff77713          	zext.b	a4,a4
40381fc4:	04e66b63          	bltu	a2,a4,4038201a <factory_timer_tick+0xae>
40381fc8:	00e784a3          	sb	a4,9(a5)
40381fcc:	00a7c703          	lbu	a4,10(a5)
40381fd0:	0705                	addi	a4,a4,1
40381fd2:	0ff77713          	zext.b	a4,a4
40381fd6:	04b77863          	bgeu	a4,a1,40382026 <factory_timer_tick+0xba>
40381fda:	00e78523          	sb	a4,10(a5)
40381fde:	00b7c703          	lbu	a4,11(a5)
40381fe2:	03b00693          	li	a3,59
40381fe6:	0705                	addi	a4,a4,1
40381fe8:	0ff77713          	zext.b	a4,a4
40381fec:	04e6e463          	bltu	a3,a4,40382034 <factory_timer_tick+0xc8>
40381ff0:	00e785a3          	sb	a4,11(a5)
40381ff4:	00c7c703          	lbu	a4,12(a5)
40381ff8:	0b400693          	li	a3,180
40381ffc:	0705                	addi	a4,a4,1
40381ffe:	0ff77713          	zext.b	a4,a4
40382002:	04e6e063          	bltu	a3,a4,40382042 <factory_timer_tick+0xd6>
40382006:	00e78623          	sb	a4,12(a5)
4038200a:	4398                	lw	a4,0(a5)
4038200c:	70800693          	li	a3,1800
40382010:	0705                	addi	a4,a4,1
40382012:	02e6ef63          	bltu	a3,a4,40382050 <factory_timer_tick+0xe4>
40382016:	c398                	sw	a4,0(a5)
40382018:	8082                	ret
4038201a:	0036e693          	ori	a3,a3,3
4038201e:	000784a3          	sb	zero,9(a5)
40382022:	c3d4                	sw	a3,4(a5)
40382024:	b765                	j	40381fcc <factory_timer_tick+0x60>
40382026:	43d8                	lw	a4,4(a5)
40382028:	00078523          	sb	zero,10(a5)
4038202c:	00476713          	ori	a4,a4,4
40382030:	c3d8                	sw	a4,4(a5)
40382032:	b775                	j	40381fde <factory_timer_tick+0x72>
40382034:	43d8                	lw	a4,4(a5)
40382036:	000785a3          	sb	zero,11(a5)
4038203a:	01876713          	ori	a4,a4,24
4038203e:	c3d8                	sw	a4,4(a5)
40382040:	bf55                	j	40381ff4 <factory_timer_tick+0x88>
40382042:	43d8                	lw	a4,4(a5)
40382044:	00078623          	sb	zero,12(a5)
40382048:	02076713          	ori	a4,a4,32
4038204c:	c3d8                	sw	a4,4(a5)
4038204e:	bf75                	j	4038200a <factory_timer_tick+0x9e>
40382050:	43d8                	lw	a4,4(a5)
40382052:	0007a023          	sw	zero,0(a5)
40382056:	04076713          	ori	a4,a4,64
4038205a:	c3d8                	sw	a4,4(a5)
4038205c:	8082                	ret

Disassembly of section .flash.text:


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200fc7a <wifi_event>:
4200fc7a:	3c1087b7          	lui	a5,0x3c108
4200fc7e:	01c7a783          	lw	a5,28(a5) # 3c10801c <IP_EVENT>
4200fc82:	02b79e63          	bne	a5,a1,4200fcbe <wifi_event+0x44>
4200fc86:	ee05                	bnez	a2,4200fcbe <wifi_event+0x44>
4200fc88:	cef1                	beqz	a3,4200fd64 <wifi_event+0xea>
4200fc8a:	42d8                	lw	a4,4(a3)
4200fc8c:	3fcb47b7          	lui	a5,0x3fcb4
4200fc90:	91478793          	addi	a5,a5,-1772 # 3fcb3914 <last_station_address>
4200fc94:	0310000f          	fence	rw,w
4200fc98:	c398                	sw	a4,0(a5)
4200fc9a:	0330000f          	fence	rw,rw
4200fc9e:	3fcb47b7          	lui	a5,0x3fcb4
4200fca2:	4705                	li	a4,1
4200fca4:	91c78793          	addi	a5,a5,-1764 # 3fcb391c <connected>
4200fca8:	0310000f          	fence	rw,w
4200fcac:	00e78023          	sb	a4,0(a5)
4200fcb0:	0330000f          	fence	rw,rw
4200fcb4:	3fcb47b7          	lui	a5,0x3fcb4
4200fcb8:	9007a623          	sw	zero,-1780(a5) # 3fcb390c <station_retries>
4200fcbc:	8082                	ret
4200fcbe:	3c1087b7          	lui	a5,0x3c108
4200fcc2:	0a07a783          	lw	a5,160(a5) # 3c1080a0 <WIFI_EVENT>
4200fcc6:	08b79f63          	bne	a5,a1,4200fd64 <wifi_event+0xea>
4200fcca:	4795                	li	a5,5
4200fccc:	08f61463          	bne	a2,a5,4200fd54 <wifi_event+0xda>
4200fcd0:	3fcb47b7          	lui	a5,0x3fcb4
4200fcd4:	91c78793          	addi	a5,a5,-1764 # 3fcb391c <connected>
4200fcd8:	0310000f          	fence	rw,w
4200fcdc:	00078023          	sb	zero,0(a5)
4200fce0:	0330000f          	fence	rw,rw
4200fce4:	3fcb46b7          	lui	a3,0x3fcb4
4200fce8:	9106c783          	lbu	a5,-1776(a3) # 3fcb3910 <station_configured>
4200fcec:	cfa5                	beqz	a5,4200fd64 <wifi_event+0xea>
4200fcee:	3fcb4737          	lui	a4,0x3fcb4
4200fcf2:	91a70793          	addi	a5,a4,-1766 # 3fcb391a <scanning>
4200fcf6:	0330000f          	fence	rw,rw
4200fcfa:	00078783          	lb	a5,0(a5)
4200fcfe:	0230000f          	fence	r,rw
4200fd02:	0ff7f793          	zext.b	a5,a5
4200fd06:	ef89                	bnez	a5,4200fd20 <wifi_event+0xa6>
4200fd08:	3fcb4637          	lui	a2,0x3fcb4
4200fd0c:	90c62783          	lw	a5,-1780(a2) # 3fcb390c <station_retries>
4200fd10:	458d                	li	a1,3
4200fd12:	00f5e763          	bltu	a1,a5,4200fd20 <wifi_event+0xa6>
4200fd16:	0785                	addi	a5,a5,1
4200fd18:	90f62623          	sw	a5,-1780(a2)
4200fd1c:	3342406f          	j	42034050 <esp_wifi_connect>
4200fd20:	9106c783          	lbu	a5,-1776(a3)
4200fd24:	c3a1                	beqz	a5,4200fd64 <wifi_event+0xea>
4200fd26:	91a70793          	addi	a5,a4,-1766
4200fd2a:	0330000f          	fence	rw,rw
4200fd2e:	00078783          	lb	a5,0(a5)
4200fd32:	0230000f          	fence	r,rw
4200fd36:	0ff7f793          	zext.b	a5,a5
4200fd3a:	e78d                	bnez	a5,4200fd64 <wifi_event+0xea>
4200fd3c:	3fcb47b7          	lui	a5,0x3fcb4
4200fd40:	4705                	li	a4,1
4200fd42:	91878793          	addi	a5,a5,-1768 # 3fcb3918 <station_failed>
4200fd46:	0310000f          	fence	rw,w
4200fd4a:	00e78023          	sb	a4,0(a5)
4200fd4e:	0330000f          	fence	rw,rw
4200fd52:	8082                	ret
4200fd54:	4789                	li	a5,2
4200fd56:	00f61763          	bne	a2,a5,4200fd64 <wifi_event+0xea>
4200fd5a:	3fcb47b7          	lui	a5,0x3fcb4
4200fd5e:	9107c783          	lbu	a5,-1776(a5) # 3fcb3910 <station_configured>
4200fd62:	ffcd                	bnez	a5,4200fd1c <wifi_event+0xa2>
4200fd64:	8082                	ret


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42010272 <network_address>:
42010272:	1101                	addi	sp,sp,-32
42010274:	ca26                	sw	s1,20(sp)
42010276:	ce06                	sw	ra,28(sp)
42010278:	cc22                	sw	s0,24(sp)
4201027a:	84aa                	mv	s1,a0
4201027c:	c62e                	sw	a1,12(sp)
4201027e:	3fcb47b7          	lui	a5,0x3fcb4
42010282:	91478793          	addi	a5,a5,-1772 # 3fcb3914 <last_station_address>
42010286:	0330000f          	fence	rw,rw
4201028a:	4380                	lw	s0,0(a5)
4201028c:	0230000f          	fence	r,rw
42010290:	fc9ff0ef          	jal	42010258 <network_ap_active>
42010294:	45b2                	lw	a1,12(sp)
42010296:	cc0d                	beqz	s0,420102d0 <network_address+0x5e>
42010298:	00154513          	xori	a0,a0,1
4201029c:	0ff57513          	zext.b	a0,a0
420102a0:	c905                	beqz	a0,420102d0 <network_address+0x5e>
420102a2:	01045793          	srli	a5,s0,0x10
420102a6:	00845713          	srli	a4,s0,0x8
420102aa:	01845813          	srli	a6,s0,0x18
420102ae:	0ff47693          	zext.b	a3,s0
420102b2:	4462                	lw	s0,24(sp)
420102b4:	40f2                	lw	ra,28(sp)
420102b6:	8526                	mv	a0,s1
420102b8:	44d2                	lw	s1,20(sp)
420102ba:	3c0b4637          	lui	a2,0x3c0b4
420102be:	0ff7f793          	zext.b	a5,a5
420102c2:	0ff77713          	zext.b	a4,a4
420102c6:	fa460613          	addi	a2,a2,-92 # 3c0b3fa4 <_esp_libc_clock_array_end+0x3e54>
420102ca:	6105                	addi	sp,sp,32
420102cc:	3f78d06f          	j	4209dec2 <snprintf>
420102d0:	4462                	lw	s0,24(sp)
420102d2:	40f2                	lw	ra,28(sp)
420102d4:	8526                	mv	a0,s1
420102d6:	44d2                	lw	s1,20(sp)
420102d8:	3c0b4637          	lui	a2,0x3c0b4
420102dc:	b6860613          	addi	a2,a2,-1176 # 3c0b3b68 <_esp_libc_clock_array_end+0x3a18>
420102e0:	6105                	addi	sp,sp,32
420102e2:	3e18d06f          	j	4209dec2 <snprintf>


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42010832 <time_sync_notify>:
42010832:	3fcb47b7          	lui	a5,0x3fcb4
42010836:	4705                	li	a4,1
42010838:	92878793          	addi	a5,a5,-1752 # 3fcb3928 <time_synced>
4201083c:	0310000f          	fence	rw,w
42010840:	00e78023          	sb	a4,0(a5)
42010844:	8082                	ret


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42011216 <weather_request_active>:
42011216:	3fcb47b7          	lui	a5,0x3fcb4
4201121a:	92c78793          	addi	a5,a5,-1748 # 3fcb392c <request_state>
4201121e:	0330000f          	fence	rw,rw
42011222:	4388                	lw	a0,0(a5)
42011224:	0230000f          	fence	r,rw
42011228:	00a03533          	snez	a0,a0
4201122c:	8082                	ret
