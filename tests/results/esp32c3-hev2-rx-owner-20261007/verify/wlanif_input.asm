
idf\esp32c3-oled-native\build-rx-owner\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420f30c8 <wlanif_input>:
420f30c8:	4d58                	lw	a4,28(a0)
420f30ca:	1101                	addi	sp,sp,-32
420f30cc:	cc22                	sw	s0,24(sp)
420f30ce:	ca26                	sw	s1,20(sp)
420f30d0:	ce06                	sw	ra,28(sp)
420f30d2:	843a                	mv	s0,a4
420f30d4:	84b6                	mv	s1,a3
420f30d6:	cd8d                	beqz	a1,420f3110 <wlanif_input+0x48>
420f30d8:	03954703          	lbu	a4,57(a0)
420f30dc:	87aa                	mv	a5,a0
420f30de:	01f71513          	slli	a0,a4,0x1f
420f30e2:	01f55713          	srli	a4,a0,0x1f
420f30e6:	c70d                	beqz	a4,420f3110 <wlanif_input+0x48>
420f30e8:	8522                	mv	a0,s0
420f30ea:	c84a                	sw	s2,16(sp)
420f30ec:	c63e                	sw	a5,12(sp)
420f30ee:	e52330ef          	jal	42026740 <__wrap_esp_pbuf_allocate>
420f30f2:	47b2                	lw	a5,12(sp)
420f30f4:	892a                	mv	s2,a0
420f30f6:	cd15                	beqz	a0,420f3132 <wlanif_input+0x6a>
420f30f8:	4b98                	lw	a4,16(a5)
420f30fa:	85be                	mv	a1,a5
420f30fc:	9702                	jalr	a4
420f30fe:	87aa                	mv	a5,a0
420f3100:	4501                	li	a0,0
420f3102:	e395                	bnez	a5,420f3126 <wlanif_input+0x5e>
420f3104:	4942                	lw	s2,16(sp)
420f3106:	40f2                	lw	ra,28(sp)
420f3108:	4462                	lw	s0,24(sp)
420f310a:	44d2                	lw	s1,20(sp)
420f310c:	6105                	addi	sp,sp,32
420f310e:	8082                	ret
420f3110:	c489                	beqz	s1,420f311a <wlanif_input+0x52>
420f3112:	85a6                	mv	a1,s1
420f3114:	8522                	mv	a0,s0
420f3116:	ef6330ef          	jal	4202680c <__wrap_esp_netif_free_rx_buffer>
420f311a:	557d                	li	a0,-1
420f311c:	40f2                	lw	ra,28(sp)
420f311e:	4462                	lw	s0,24(sp)
420f3120:	44d2                	lw	s1,20(sp)
420f3122:	6105                	addi	sp,sp,32
420f3124:	8082                	ret
420f3126:	854a                	mv	a0,s2
420f3128:	a2a8c0ef          	jal	4207f352 <pbuf_free>
420f312c:	557d                	li	a0,-1
420f312e:	4942                	lw	s2,16(sp)
420f3130:	b7f5                	j	420f311c <wlanif_input+0x54>
420f3132:	8522                	mv	a0,s0
420f3134:	85a6                	mv	a1,s1
420f3136:	ed6330ef          	jal	4202680c <__wrap_esp_netif_free_rx_buffer>
420f313a:	10100513          	li	a0,257
420f313e:	4942                	lw	s2,16(sp)
420f3140:	b7d9                	j	420f3106 <wlanif_input+0x3e>
