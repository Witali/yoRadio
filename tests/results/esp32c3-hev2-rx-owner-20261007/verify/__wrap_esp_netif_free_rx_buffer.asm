
idf\esp32c3-oled-native\build-rx-owner\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4202680c <__wrap_esp_netif_free_rx_buffer>:
4202680c:	1141                	addi	sp,sp,-16
4202680e:	c422                	sw	s0,8(sp)
42026810:	c226                	sw	s1,4(sp)
42026812:	842e                	mv	s0,a1
42026814:	c606                	sw	ra,12(sp)
42026816:	84aa                	mv	s1,a0
42026818:	fe360097          	auipc	ra,0xfe360
4202681c:	52e080e7          	jalr	1326(ra) # 40386d46 <vPortEnterCritical>
42026820:	3fc917b7          	lui	a5,0x3fc91
42026824:	23c78593          	addi	a1,a5,572 # 3fc9123c <owners>
42026828:	87ae                	mv	a5,a1
4202682a:	4701                	li	a4,0
4202682c:	02000613          	li	a2,32
42026830:	a029                	j	4202683a <__wrap_esp_netif_free_rx_buffer+0x2e>
42026832:	0705                	addi	a4,a4,1
42026834:	07c1                	addi	a5,a5,16
42026836:	04c70d63          	beq	a4,a2,42026890 <__wrap_esp_netif_free_rx_buffer+0x84>
4202683a:	4794                	lw	a3,8(a5)
4202683c:	dafd                	beqz	a3,42026832 <__wrap_esp_netif_free_rx_buffer+0x26>
4202683e:	4394                	lw	a3,0(a5)
42026840:	fe8699e3          	bne	a3,s0,42026832 <__wrap_esp_netif_free_rx_buffer+0x26>
42026844:	3fc95837          	lui	a6,0x3fc95
42026848:	3fc95537          	lui	a0,0x3fc95
4202684c:	e1882603          	lw	a2,-488(a6) # 3fc94e18 <live>
42026850:	e2052683          	lw	a3,-480(a0) # 3fc94e20 <releases>
42026854:	0712                	slli	a4,a4,0x4
42026856:	00e587b3          	add	a5,a1,a4
4202685a:	167d                	addi	a2,a2,-1
4202685c:	00168713          	addi	a4,a3,1
42026860:	0007a023          	sw	zero,0(a5)
42026864:	0007a223          	sw	zero,4(a5)
42026868:	0007a423          	sw	zero,8(a5)
4202686c:	0007a623          	sw	zero,12(a5)
42026870:	e0c82c23          	sw	a2,-488(a6)
42026874:	e2e52023          	sw	a4,-480(a0)
42026878:	fe360097          	auipc	ra,0xfe360
4202687c:	50a080e7          	jalr	1290(ra) # 40386d82 <vPortExitCritical>
42026880:	85a2                	mv	a1,s0
42026882:	4422                	lw	s0,8(sp)
42026884:	40b2                	lw	ra,12(sp)
42026886:	8526                	mv	a0,s1
42026888:	4492                	lw	s1,4(sp)
4202688a:	0141                	addi	sp,sp,16
4202688c:	1c66806f          	j	4208ea52 <esp_netif_free_rx_buffer>
42026890:	3fc95737          	lui	a4,0x3fc95
42026894:	e1072783          	lw	a5,-496(a4) # 3fc94e10 <untracked_releases>
42026898:	0785                	addi	a5,a5,1
4202689a:	e0f72823          	sw	a5,-496(a4)
4202689e:	bfe9                	j	42026878 <__wrap_esp_netif_free_rx_buffer+0x6c>
