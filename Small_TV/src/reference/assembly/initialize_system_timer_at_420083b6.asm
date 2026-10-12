
factory-irom.bin:     file format binary


Disassembly of section .data:

420083b6 <.data+0x8396>:
420083b6:	715d                	addi	sp,sp,-80
420083b8:	c686                	sw	ra,76(sp)
420083ba:	3fcc07b7          	lui	a5,0x3fcc0
420083be:	fc878793          	addi	a5,a5,-56 # 0x3fcbffc8
420083c2:	7e900713          	li	a4,2025
420083c6:	c398                	sw	a4,0(a5)
420083c8:	4725                	li	a4,9
420083ca:	00e78223          	sb	a4,4(a5)
420083ce:	474d                	li	a4,19
420083d0:	00e782a3          	sb	a4,5(a5)
420083d4:	4745                	li	a4,17
420083d6:	00e78323          	sb	a4,6(a5)
420083da:	4711                	li	a4,4
420083dc:	00e783a3          	sb	a4,7(a5)
420083e0:	02800713          	li	a4,40
420083e4:	00e78423          	sb	a4,8(a5)
420083e8:	4715                	li	a4,5
420083ea:	00e784a3          	sb	a4,9(a5)
420083ee:	4785                	li	a5,1
420083f0:	3fcc46b7          	lui	a3,0x3fcc4
420083f4:	9ef685a3          	sb	a5,-1557(a3) # 0x3fcc39eb
420083f8:	3fcc46b7          	lui	a3,0x3fcc4
420083fc:	a4068b23          	sb	zero,-1450(a3) # 0x3fcc3a56
42008400:	3fcc46b7          	lui	a3,0x3fcc4
42008404:	9ef68523          	sb	a5,-1558(a3) # 0x3fcc39ea
42008408:	d602                	sw	zero,44(sp)
4200840a:	d802                	sw	zero,48(sp)
4200840c:	da02                	sw	zero,52(sp)
4200840e:	dc02                	sw	zero,56(sp)
42008410:	de02                	sw	zero,60(sp)
42008412:	d63a                	sw	a4,44(sp)
42008414:	d83e                	sw	a5,48(sp)
42008416:	000f47b7          	lui	a5,0xf4
4200841a:	24078793          	addi	a5,a5,576 # 0xf4240
4200841e:	da3e                	sw	a5,52(sp)
42008420:	3fcc45b7          	lui	a1,0x3fcc4
42008424:	9d058593          	addi	a1,a1,-1584 # 0x3fcc39d0
42008428:	1068                	addi	a0,sp,44
4200842a:	60ba50ef          	jal	0x420ae234
4200842e:	e925                	bnez	a0,0x4200849e
42008430:	3c0d67b7          	lui	a5,0x3c0d6
42008434:	29078793          	addi	a5,a5,656 # 0x3c0d6290
42008438:	4388                	lw	a0,0(a5)
4200843a:	43cc                	lw	a1,4(a5)
4200843c:	4790                	lw	a2,8(a5)
4200843e:	47d4                	lw	a3,12(a5)
42008440:	4b98                	lw	a4,16(a5)
42008442:	4bdc                	lw	a5,20(a5)
42008444:	c82a                	sw	a0,16(sp)
42008446:	ca2e                	sw	a1,20(sp)
42008448:	cc32                	sw	a2,24(sp)
4200844a:	ce36                	sw	a3,28(sp)
4200844c:	d03a                	sw	a4,32(sp)
4200844e:	d23e                	sw	a5,36(sp)
42008450:	080c                	addi	a1,sp,16
42008452:	3fcc47b7          	lui	a5,0x3fcc4
42008456:	9d07a503          	lw	a0,-1584(a5) # 0x3fcc39d0
4200845a:	256a60ef          	jal	0x420ae6b0
4200845e:	e135                	bnez	a0,0x420084c2
42008460:	420087b7          	lui	a5,0x42008
42008464:	26a78793          	addi	a5,a5,618 # 0x4200826a
42008468:	c63e                	sw	a5,12(sp)
4200846a:	4601                	li	a2,0
4200846c:	006c                	addi	a1,sp,12
4200846e:	3fcc47b7          	lui	a5,0x3fcc4
42008472:	9d07a503          	lw	a0,-1584(a5) # 0x3fcc39d0
42008476:	0bea60ef          	jal	0x420ae534
4200847a:	e535                	bnez	a0,0x420084e6
4200847c:	3fcc47b7          	lui	a5,0x3fcc4
42008480:	9d07a503          	lw	a0,-1584(a5) # 0x3fcc39d0
42008484:	406a60ef          	jal	0x420ae88a
42008488:	e149                	bnez	a0,0x4200850a
4200848a:	3fcc47b7          	lui	a5,0x3fcc4
4200848e:	9d07a503          	lw	a0,-1584(a5) # 0x3fcc39d0
42008492:	52aa60ef          	jal	0x420ae9bc
42008496:	ed41                	bnez	a0,0x4200852e
42008498:	40b6                	lw	ra,76(sp)
4200849a:	6161                	addi	sp,sp,80
4200849c:	8082                	ret
4200849e:	3c0c3737          	lui	a4,0x3c0c3
420084a2:	90870713          	addi	a4,a4,-1784 # 0x3c0c2908
420084a6:	3c0d66b7          	lui	a3,0x3c0d6
420084aa:	27868693          	addi	a3,a3,632 # 0x3c0d6278
420084ae:	0e100613          	li	a2,225
420084b2:	3c0c35b7          	lui	a1,0x3c0c3
420084b6:	93458593          	addi	a1,a1,-1740 # 0x3c0c2934
420084ba:	fe37f097          	auipc	ra,0xfe37f
420084be:	db0080e7          	jalr	-592(ra) # 0x4038726a
420084c2:	3c0c3737          	lui	a4,0x3c0c3
420084c6:	95070713          	addi	a4,a4,-1712 # 0x3c0c2950
420084ca:	3c0d66b7          	lui	a3,0x3c0d6
420084ce:	27868693          	addi	a3,a3,632 # 0x3c0d6278
420084d2:	0e800613          	li	a2,232
420084d6:	3c0c35b7          	lui	a1,0x3c0c3
420084da:	93458593          	addi	a1,a1,-1740 # 0x3c0c2934
420084de:	fe37f097          	auipc	ra,0xfe37f
420084e2:	d8c080e7          	jalr	-628(ra) # 0x4038726a
420084e6:	3c0c3737          	lui	a4,0x3c0c3
420084ea:	98470713          	addi	a4,a4,-1660 # 0x3c0c2984
420084ee:	3c0d66b7          	lui	a3,0x3c0d6
420084f2:	27868693          	addi	a3,a3,632 # 0x3c0d6278
420084f6:	0ee00613          	li	a2,238
420084fa:	3c0c35b7          	lui	a1,0x3c0c3
420084fe:	93458593          	addi	a1,a1,-1740 # 0x3c0c2934
42008502:	fe37f097          	auipc	ra,0xfe37f
42008506:	d68080e7          	jalr	-664(ra) # 0x4038726a
4200850a:	3c0c3737          	lui	a4,0x3c0c3
4200850e:	9bc70713          	addi	a4,a4,-1604 # 0x3c0c29bc
42008512:	3c0d66b7          	lui	a3,0x3c0d6
42008516:	27868693          	addi	a3,a3,632 # 0x3c0d6278
4200851a:	0f000613          	li	a2,240
4200851e:	3c0c35b7          	lui	a1,0x3c0c3
42008522:	93458593          	addi	a1,a1,-1740 # 0x3c0c2934
42008526:	fe37f097          	auipc	ra,0xfe37f
4200852a:	d44080e7          	jalr	-700(ra) # 0x4038726a
4200852e:	3c0c3737          	lui	a4,0x3c0c3
42008532:	9d470713          	addi	a4,a4,-1580 # 0x3c0c29d4
42008536:	3c0d66b7          	lui	a3,0x3c0d6
4200853a:	27868693          	addi	a3,a3,632 # 0x3c0d6278
4200853e:	0f200613          	li	a2,242
42008542:	3c0c35b7          	lui	a1,0x3c0c3
42008546:	93458593          	addi	a1,a1,-1740 # 0x3c0c2934
4200854a:	fe37f097          	auipc	ra,0xfe37f
4200854e:	d20080e7          	jalr	-736(ra) # 0x4038726a
