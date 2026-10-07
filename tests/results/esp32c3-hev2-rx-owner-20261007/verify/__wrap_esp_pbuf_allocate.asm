
idf\esp32c3-oled-native\build-rx-owner\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026740 <__wrap_esp_pbuf_allocate>:
42026740:	1101                	addi	sp,sp,-32
42026742:	cc22                	sw	s0,24(sp)
42026744:	ca26                	sw	s1,20(sp)
42026746:	ce06                	sw	ra,28(sp)
42026748:	84ae                	mv	s1,a1
4202674a:	8436                	mv	s0,a3
4202674c:	684680ef          	jal	4208edd0 <esp_pbuf_allocate>
42026750:	cd3d                	beqz	a0,420267ce <__wrap_esp_pbuf_allocate+0x8e>
42026752:	c62a                	sw	a0,12(sp)
42026754:	fe360097          	auipc	ra,0xfe360
42026758:	5f2080e7          	jalr	1522(ra) # 40386d46 <vPortEnterCritical>
4202675c:	3fc957b7          	lui	a5,0x3fc95
42026760:	e247a883          	lw	a7,-476(a5) # 3fc94e24 <allocations>
42026764:	3fc91837          	lui	a6,0x3fc91
42026768:	23c80813          	addi	a6,a6,572 # 3fc9123c <owners>
4202676c:	0885                	addi	a7,a7,1
4202676e:	e317a223          	sw	a7,-476(a5)
42026772:	4532                	lw	a0,12(sp)
42026774:	87c2                	mv	a5,a6
42026776:	00880713          	addi	a4,a6,8
4202677a:	4601                	li	a2,0
4202677c:	02000593          	li	a1,32
42026780:	a021                	j	42026788 <__wrap_esp_pbuf_allocate+0x48>
42026782:	0605                	addi	a2,a2,1
42026784:	00b60563          	beq	a2,a1,4202678e <__wrap_esp_pbuf_allocate+0x4e>
42026788:	4314                	lw	a3,0(a4)
4202678a:	0741                	addi	a4,a4,16
4202678c:	fafd                	bnez	a3,42026782 <__wrap_esp_pbuf_allocate+0x42>
4202678e:	20080593          	addi	a1,a6,512
42026792:	a021                	j	4202679a <__wrap_esp_pbuf_allocate+0x5a>
42026794:	07c1                	addi	a5,a5,16
42026796:	00f58c63          	beq	a1,a5,420267ae <__wrap_esp_pbuf_allocate+0x6e>
4202679a:	4798                	lw	a4,8(a5)
4202679c:	df65                	beqz	a4,42026794 <__wrap_esp_pbuf_allocate+0x54>
4202679e:	4398                	lw	a4,0(a5)
420267a0:	fee41ae3          	bne	s0,a4,42026794 <__wrap_esp_pbuf_allocate+0x54>
420267a4:	07c1                	addi	a5,a5,16
420267a6:	02000613          	li	a2,32
420267aa:	fef598e3          	bne	a1,a5,4202679a <__wrap_esp_pbuf_allocate+0x5a>
420267ae:	47fd                	li	a5,31
420267b0:	02c7f463          	bgeu	a5,a2,420267d8 <__wrap_esp_pbuf_allocate+0x98>
420267b4:	3fc95737          	lui	a4,0x3fc95
420267b8:	e1c72783          	lw	a5,-484(a4) # 3fc94e1c <lost>
420267bc:	0785                	addi	a5,a5,1
420267be:	e0f72e23          	sw	a5,-484(a4)
420267c2:	c62a                	sw	a0,12(sp)
420267c4:	fe360097          	auipc	ra,0xfe360
420267c8:	5be080e7          	jalr	1470(ra) # 40386d82 <vPortExitCritical>
420267cc:	4532                	lw	a0,12(sp)
420267ce:	40f2                	lw	ra,28(sp)
420267d0:	4462                	lw	s0,24(sp)
420267d2:	44d2                	lw	s1,20(sp)
420267d4:	6105                	addi	sp,sp,32
420267d6:	8082                	ret
420267d8:	3fc95737          	lui	a4,0x3fc95
420267dc:	e1872783          	lw	a5,-488(a4) # 3fc94e18 <live>
420267e0:	3fc956b7          	lui	a3,0x3fc95
420267e4:	0612                	slli	a2,a2,0x4
420267e6:	e146a583          	lw	a1,-492(a3) # 3fc94e14 <peak>
420267ea:	9832                	add	a6,a6,a2
420267ec:	0785                	addi	a5,a5,1
420267ee:	00882023          	sw	s0,0(a6)
420267f2:	00982223          	sw	s1,4(a6)
420267f6:	00a82423          	sw	a0,8(a6)
420267fa:	01182623          	sw	a7,12(a6)
420267fe:	e0f72c23          	sw	a5,-488(a4)
42026802:	fcf5f0e3          	bgeu	a1,a5,420267c2 <__wrap_esp_pbuf_allocate+0x82>
42026806:	e0f6aa23          	sw	a5,-492(a3)
4202680a:	bf65                	j	420267c2 <__wrap_esp_pbuf_allocate+0x82>
