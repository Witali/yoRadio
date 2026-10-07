
idf\esp32c3-oled-native\build-rx-owner\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420f3148 <wlanif_input>:
420f3148:	4d58                	lw	a4,28(a0)
420f314a:	1101                	addi	sp,sp,-32
420f314c:	cc22                	sw	s0,24(sp)
420f314e:	ca26                	sw	s1,20(sp)
420f3150:	ce06                	sw	ra,28(sp)
420f3152:	843a                	mv	s0,a4
420f3154:	84b6                	mv	s1,a3
420f3156:	cd8d                	beqz	a1,420f3190 <wlanif_input+0x48>
420f3158:	03954703          	lbu	a4,57(a0)
420f315c:	87aa                	mv	a5,a0
420f315e:	01f71513          	slli	a0,a4,0x1f
420f3162:	01f55713          	srli	a4,a0,0x1f
420f3166:	c70d                	beqz	a4,420f3190 <wlanif_input+0x48>
420f3168:	8522                	mv	a0,s0
420f316a:	c84a                	sw	s2,16(sp)
420f316c:	c63e                	sw	a5,12(sp)
420f316e:	dd6330ef          	jal	42026744 <__wrap_esp_pbuf_allocate>
420f3172:	47b2                	lw	a5,12(sp)
420f3174:	892a                	mv	s2,a0
420f3176:	cd15                	beqz	a0,420f31b2 <wlanif_input+0x6a>
420f3178:	4b98                	lw	a4,16(a5)
420f317a:	85be                	mv	a1,a5
420f317c:	9702                	jalr	a4
420f317e:	87aa                	mv	a5,a0
420f3180:	4501                	li	a0,0
420f3182:	e395                	bnez	a5,420f31a6 <wlanif_input+0x5e>
420f3184:	4942                	lw	s2,16(sp)
420f3186:	40f2                	lw	ra,28(sp)
420f3188:	4462                	lw	s0,24(sp)
420f318a:	44d2                	lw	s1,20(sp)
420f318c:	6105                	addi	sp,sp,32
420f318e:	8082                	ret
420f3190:	c489                	beqz	s1,420f319a <wlanif_input+0x52>
420f3192:	85a6                	mv	a1,s1
420f3194:	8522                	mv	a0,s0
420f3196:	e7a330ef          	jal	42026810 <__wrap_esp_netif_free_rx_buffer>
420f319a:	557d                	li	a0,-1
420f319c:	40f2                	lw	ra,28(sp)
420f319e:	4462                	lw	s0,24(sp)
420f31a0:	44d2                	lw	s1,20(sp)
420f31a2:	6105                	addi	sp,sp,32
420f31a4:	8082                	ret
420f31a6:	854a                	mv	a0,s2
420f31a8:	a2a8c0ef          	jal	4207f3d2 <pbuf_free>
420f31ac:	557d                	li	a0,-1
420f31ae:	4942                	lw	s2,16(sp)
420f31b0:	b7f5                	j	420f319c <wlanif_input+0x54>
420f31b2:	8522                	mv	a0,s0
420f31b4:	85a6                	mv	a1,s1
420f31b6:	e5a330ef          	jal	42026810 <__wrap_esp_netif_free_rx_buffer>
420f31ba:	10100513          	li	a0,257
420f31be:	4942                	lw	s2,16(sp)
420f31c0:	b7d9                	j	420f3186 <wlanif_input+0x3e>
