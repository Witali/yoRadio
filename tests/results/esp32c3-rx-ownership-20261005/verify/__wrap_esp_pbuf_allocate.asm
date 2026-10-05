
idf\esp32c3-oled-native\build-rx-owner\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420266b8 <__wrap_esp_pbuf_allocate>:
420266b8:	1101                	addi	sp,sp,-32
420266ba:	cc22                	sw	s0,24(sp)
420266bc:	ca26                	sw	s1,20(sp)
420266be:	ce06                	sw	ra,28(sp)
420266c0:	84ae                	mv	s1,a1
420266c2:	8436                	mv	s0,a3
420266c4:	2ef660ef          	jal	4208d1b2 <esp_pbuf_allocate>
420266c8:	cd3d                	beqz	a0,42026746 <__wrap_esp_pbuf_allocate+0x8e>
420266ca:	c62a                	sw	a0,12(sp)
420266cc:	fe360097          	auipc	ra,0xfe360
420266d0:	67a080e7          	jalr	1658(ra) # 40386d46 <vPortEnterCritical>
420266d4:	3fc957b7          	lui	a5,0x3fc95
420266d8:	e247a883          	lw	a7,-476(a5) # 3fc94e24 <allocations>
420266dc:	3fc91837          	lui	a6,0x3fc91
420266e0:	23c80813          	addi	a6,a6,572 # 3fc9123c <owners>
420266e4:	0885                	addi	a7,a7,1
420266e6:	e317a223          	sw	a7,-476(a5)
420266ea:	4532                	lw	a0,12(sp)
420266ec:	87c2                	mv	a5,a6
420266ee:	00880713          	addi	a4,a6,8
420266f2:	4601                	li	a2,0
420266f4:	02000593          	li	a1,32
420266f8:	a021                	j	42026700 <__wrap_esp_pbuf_allocate+0x48>
420266fa:	0605                	addi	a2,a2,1
420266fc:	00b60563          	beq	a2,a1,42026706 <__wrap_esp_pbuf_allocate+0x4e>
42026700:	4314                	lw	a3,0(a4)
42026702:	0741                	addi	a4,a4,16
42026704:	fafd                	bnez	a3,420266fa <__wrap_esp_pbuf_allocate+0x42>
42026706:	20080593          	addi	a1,a6,512
4202670a:	a021                	j	42026712 <__wrap_esp_pbuf_allocate+0x5a>
4202670c:	07c1                	addi	a5,a5,16
4202670e:	00f58c63          	beq	a1,a5,42026726 <__wrap_esp_pbuf_allocate+0x6e>
42026712:	4798                	lw	a4,8(a5)
42026714:	df65                	beqz	a4,4202670c <__wrap_esp_pbuf_allocate+0x54>
42026716:	4398                	lw	a4,0(a5)
42026718:	fee41ae3          	bne	s0,a4,4202670c <__wrap_esp_pbuf_allocate+0x54>
4202671c:	07c1                	addi	a5,a5,16
4202671e:	02000613          	li	a2,32
42026722:	fef598e3          	bne	a1,a5,42026712 <__wrap_esp_pbuf_allocate+0x5a>
42026726:	47fd                	li	a5,31
42026728:	02c7f463          	bgeu	a5,a2,42026750 <__wrap_esp_pbuf_allocate+0x98>
4202672c:	3fc95737          	lui	a4,0x3fc95
42026730:	e1c72783          	lw	a5,-484(a4) # 3fc94e1c <lost>
42026734:	0785                	addi	a5,a5,1
42026736:	e0f72e23          	sw	a5,-484(a4)
4202673a:	c62a                	sw	a0,12(sp)
4202673c:	fe360097          	auipc	ra,0xfe360
42026740:	646080e7          	jalr	1606(ra) # 40386d82 <vPortExitCritical>
42026744:	4532                	lw	a0,12(sp)
42026746:	40f2                	lw	ra,28(sp)
42026748:	4462                	lw	s0,24(sp)
4202674a:	44d2                	lw	s1,20(sp)
4202674c:	6105                	addi	sp,sp,32
4202674e:	8082                	ret
42026750:	3fc95737          	lui	a4,0x3fc95
42026754:	e1872783          	lw	a5,-488(a4) # 3fc94e18 <live>
42026758:	3fc956b7          	lui	a3,0x3fc95
4202675c:	0612                	slli	a2,a2,0x4
4202675e:	e146a583          	lw	a1,-492(a3) # 3fc94e14 <peak>
42026762:	9832                	add	a6,a6,a2
42026764:	0785                	addi	a5,a5,1
42026766:	00882023          	sw	s0,0(a6)
4202676a:	00982223          	sw	s1,4(a6)
4202676e:	00a82423          	sw	a0,8(a6)
42026772:	01182623          	sw	a7,12(a6)
42026776:	e0f72c23          	sw	a5,-488(a4)
4202677a:	fcf5f0e3          	bgeu	a1,a5,4202673a <__wrap_esp_pbuf_allocate+0x82>
4202677e:	e0f6aa23          	sw	a5,-492(a3)
42026782:	bf65                	j	4202673a <__wrap_esp_pbuf_allocate+0x82>
