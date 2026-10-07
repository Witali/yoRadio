
idf\esp32c3-oled-native\build-rx-owner\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420f14aa <wlanif_input>:
420f14aa:	4d58                	lw	a4,28(a0)
420f14ac:	1101                	addi	sp,sp,-32
420f14ae:	cc22                	sw	s0,24(sp)
420f14b0:	ca26                	sw	s1,20(sp)
420f14b2:	ce06                	sw	ra,28(sp)
420f14b4:	843a                	mv	s0,a4
420f14b6:	84b6                	mv	s1,a3
420f14b8:	cd8d                	beqz	a1,420f14f2 <wlanif_input+0x48>
420f14ba:	03954703          	lbu	a4,57(a0)
420f14be:	87aa                	mv	a5,a0
420f14c0:	01f71513          	slli	a0,a4,0x1f
420f14c4:	01f55713          	srli	a4,a0,0x1f
420f14c8:	c70d                	beqz	a4,420f14f2 <wlanif_input+0x48>
420f14ca:	8522                	mv	a0,s0
420f14cc:	c84a                	sw	s2,16(sp)
420f14ce:	c63e                	sw	a5,12(sp)
420f14d0:	9e8350ef          	jal	420266b8 <__wrap_esp_pbuf_allocate>
420f14d4:	47b2                	lw	a5,12(sp)
420f14d6:	892a                	mv	s2,a0
420f14d8:	cd15                	beqz	a0,420f1514 <wlanif_input+0x6a>
420f14da:	4b98                	lw	a4,16(a5)
420f14dc:	85be                	mv	a1,a5
420f14de:	9702                	jalr	a4
420f14e0:	87aa                	mv	a5,a0
420f14e2:	4501                	li	a0,0
420f14e4:	e395                	bnez	a5,420f1508 <wlanif_input+0x5e>
420f14e6:	4942                	lw	s2,16(sp)
420f14e8:	40f2                	lw	ra,28(sp)
420f14ea:	4462                	lw	s0,24(sp)
420f14ec:	44d2                	lw	s1,20(sp)
420f14ee:	6105                	addi	sp,sp,32
420f14f0:	8082                	ret
420f14f2:	c489                	beqz	s1,420f14fc <wlanif_input+0x52>
420f14f4:	85a6                	mv	a1,s1
420f14f6:	8522                	mv	a0,s0
420f14f8:	a8c350ef          	jal	42026784 <__wrap_esp_netif_free_rx_buffer>
420f14fc:	557d                	li	a0,-1
420f14fe:	40f2                	lw	ra,28(sp)
420f1500:	4462                	lw	s0,24(sp)
420f1502:	44d2                	lw	s1,20(sp)
420f1504:	6105                	addi	sp,sp,32
420f1506:	8082                	ret
420f1508:	854a                	mv	a0,s2
420f150a:	a2a8c0ef          	jal	4207d734 <pbuf_free>
420f150e:	557d                	li	a0,-1
420f1510:	4942                	lw	s2,16(sp)
420f1512:	b7f5                	j	420f14fe <wlanif_input+0x54>
420f1514:	8522                	mv	a0,s0
420f1516:	85a6                	mv	a1,s1
420f1518:	a6c350ef          	jal	42026784 <__wrap_esp_netif_free_rx_buffer>
420f151c:	10100513          	li	a0,257
420f1520:	4942                	lw	s2,16(sp)
420f1522:	b7d9                	j	420f14e8 <wlanif_input+0x3e>
