
idf\esp32c3-oled-native\build-rx-owner\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026784 <__wrap_esp_netif_free_rx_buffer>:
42026784:	1141                	addi	sp,sp,-16
42026786:	c422                	sw	s0,8(sp)
42026788:	c226                	sw	s1,4(sp)
4202678a:	842e                	mv	s0,a1
4202678c:	c606                	sw	ra,12(sp)
4202678e:	84aa                	mv	s1,a0
42026790:	fe360097          	auipc	ra,0xfe360
42026794:	5b6080e7          	jalr	1462(ra) # 40386d46 <vPortEnterCritical>
42026798:	3fc917b7          	lui	a5,0x3fc91
4202679c:	23c78593          	addi	a1,a5,572 # 3fc9123c <owners>
420267a0:	87ae                	mv	a5,a1
420267a2:	4701                	li	a4,0
420267a4:	02000613          	li	a2,32
420267a8:	a029                	j	420267b2 <__wrap_esp_netif_free_rx_buffer+0x2e>
420267aa:	0705                	addi	a4,a4,1
420267ac:	07c1                	addi	a5,a5,16
420267ae:	04c70d63          	beq	a4,a2,42026808 <__wrap_esp_netif_free_rx_buffer+0x84>
420267b2:	4794                	lw	a3,8(a5)
420267b4:	dafd                	beqz	a3,420267aa <__wrap_esp_netif_free_rx_buffer+0x26>
420267b6:	4394                	lw	a3,0(a5)
420267b8:	fe8699e3          	bne	a3,s0,420267aa <__wrap_esp_netif_free_rx_buffer+0x26>
420267bc:	3fc95837          	lui	a6,0x3fc95
420267c0:	3fc95537          	lui	a0,0x3fc95
420267c4:	e1882603          	lw	a2,-488(a6) # 3fc94e18 <live>
420267c8:	e2052683          	lw	a3,-480(a0) # 3fc94e20 <releases>
420267cc:	0712                	slli	a4,a4,0x4
420267ce:	00e587b3          	add	a5,a1,a4
420267d2:	167d                	addi	a2,a2,-1
420267d4:	00168713          	addi	a4,a3,1
420267d8:	0007a023          	sw	zero,0(a5)
420267dc:	0007a223          	sw	zero,4(a5)
420267e0:	0007a423          	sw	zero,8(a5)
420267e4:	0007a623          	sw	zero,12(a5)
420267e8:	e0c82c23          	sw	a2,-488(a6)
420267ec:	e2e52023          	sw	a4,-480(a0)
420267f0:	fe360097          	auipc	ra,0xfe360
420267f4:	592080e7          	jalr	1426(ra) # 40386d82 <vPortExitCritical>
420267f8:	85a2                	mv	a1,s0
420267fa:	4422                	lw	s0,8(sp)
420267fc:	40b2                	lw	ra,12(sp)
420267fe:	8526                	mv	a0,s1
42026800:	4492                	lw	s1,4(sp)
42026802:	0141                	addi	sp,sp,16
42026804:	6306606f          	j	4208ce34 <esp_netif_free_rx_buffer>
42026808:	3fc95737          	lui	a4,0x3fc95
4202680c:	e1072783          	lw	a5,-496(a4) # 3fc94e10 <untracked_releases>
42026810:	0785                	addi	a5,a5,1
42026812:	e0f72823          	sw	a5,-496(a4)
42026816:	bfe9                	j	420267f0 <__wrap_esp_netif_free_rx_buffer+0x6c>
