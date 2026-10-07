
idf\esp32c3-oled-native\build-rx-owner\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026744 <__wrap_esp_pbuf_allocate>:
42026744:	1101                	addi	sp,sp,-32
42026746:	cc22                	sw	s0,24(sp)
42026748:	ca26                	sw	s1,20(sp)
4202674a:	ce06                	sw	ra,28(sp)
4202674c:	84ae                	mv	s1,a1
4202674e:	8436                	mv	s0,a3
42026750:	700680ef          	jal	4208ee50 <esp_pbuf_allocate>
42026754:	cd3d                	beqz	a0,420267d2 <__wrap_esp_pbuf_allocate+0x8e>
42026756:	c62a                	sw	a0,12(sp)
42026758:	fe360097          	auipc	ra,0xfe360
4202675c:	5ee080e7          	jalr	1518(ra) # 40386d46 <vPortEnterCritical>
42026760:	3fc957b7          	lui	a5,0x3fc95
42026764:	e247a883          	lw	a7,-476(a5) # 3fc94e24 <allocations>
42026768:	3fc91837          	lui	a6,0x3fc91
4202676c:	23c80813          	addi	a6,a6,572 # 3fc9123c <owners>
42026770:	0885                	addi	a7,a7,1
42026772:	e317a223          	sw	a7,-476(a5)
42026776:	4532                	lw	a0,12(sp)
42026778:	87c2                	mv	a5,a6
4202677a:	00880713          	addi	a4,a6,8
4202677e:	4601                	li	a2,0
42026780:	02000593          	li	a1,32
42026784:	a021                	j	4202678c <__wrap_esp_pbuf_allocate+0x48>
42026786:	0605                	addi	a2,a2,1
42026788:	00b60563          	beq	a2,a1,42026792 <__wrap_esp_pbuf_allocate+0x4e>
4202678c:	4314                	lw	a3,0(a4)
4202678e:	0741                	addi	a4,a4,16
42026790:	fafd                	bnez	a3,42026786 <__wrap_esp_pbuf_allocate+0x42>
42026792:	20080593          	addi	a1,a6,512
42026796:	a021                	j	4202679e <__wrap_esp_pbuf_allocate+0x5a>
42026798:	07c1                	addi	a5,a5,16
4202679a:	00f58c63          	beq	a1,a5,420267b2 <__wrap_esp_pbuf_allocate+0x6e>
4202679e:	4798                	lw	a4,8(a5)
420267a0:	df65                	beqz	a4,42026798 <__wrap_esp_pbuf_allocate+0x54>
420267a2:	4398                	lw	a4,0(a5)
420267a4:	fee41ae3          	bne	s0,a4,42026798 <__wrap_esp_pbuf_allocate+0x54>
420267a8:	07c1                	addi	a5,a5,16
420267aa:	02000613          	li	a2,32
420267ae:	fef598e3          	bne	a1,a5,4202679e <__wrap_esp_pbuf_allocate+0x5a>
420267b2:	47fd                	li	a5,31
420267b4:	02c7f463          	bgeu	a5,a2,420267dc <__wrap_esp_pbuf_allocate+0x98>
420267b8:	3fc95737          	lui	a4,0x3fc95
420267bc:	e1c72783          	lw	a5,-484(a4) # 3fc94e1c <lost>
420267c0:	0785                	addi	a5,a5,1
420267c2:	e0f72e23          	sw	a5,-484(a4)
420267c6:	c62a                	sw	a0,12(sp)
420267c8:	fe360097          	auipc	ra,0xfe360
420267cc:	5ba080e7          	jalr	1466(ra) # 40386d82 <vPortExitCritical>
420267d0:	4532                	lw	a0,12(sp)
420267d2:	40f2                	lw	ra,28(sp)
420267d4:	4462                	lw	s0,24(sp)
420267d6:	44d2                	lw	s1,20(sp)
420267d8:	6105                	addi	sp,sp,32
420267da:	8082                	ret
420267dc:	3fc95737          	lui	a4,0x3fc95
420267e0:	e1872783          	lw	a5,-488(a4) # 3fc94e18 <live>
420267e4:	3fc956b7          	lui	a3,0x3fc95
420267e8:	0612                	slli	a2,a2,0x4
420267ea:	e146a583          	lw	a1,-492(a3) # 3fc94e14 <peak>
420267ee:	9832                	add	a6,a6,a2
420267f0:	0785                	addi	a5,a5,1
420267f2:	00882023          	sw	s0,0(a6)
420267f6:	00982223          	sw	s1,4(a6)
420267fa:	00a82423          	sw	a0,8(a6)
420267fe:	01182623          	sw	a7,12(a6)
42026802:	e0f72c23          	sw	a5,-488(a4)
42026806:	fcf5f0e3          	bgeu	a1,a5,420267c6 <__wrap_esp_pbuf_allocate+0x82>
4202680a:	e0f6aa23          	sw	a5,-492(a3)
4202680e:	bf65                	j	420267c6 <__wrap_esp_pbuf_allocate+0x82>
