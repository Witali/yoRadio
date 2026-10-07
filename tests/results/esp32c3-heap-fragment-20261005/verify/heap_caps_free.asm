
idf\esp32c3-oled-native\build-heap-fragment\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200535e <heap_caps_free>:
4200535e:	cd3d                	beqz	a0,420053dc <heap_caps_free+0x7e>
42005360:	1101                	addi	sp,sp,-32
42005362:	bfc807b7          	lui	a5,0xbfc80
42005366:	ce06                	sw	ra,28(sp)
42005368:	97aa                	add	a5,a5,a0
4200536a:	00060737          	lui	a4,0x60
4200536e:	85aa                	mv	a1,a0
42005370:	06e7e063          	bltu	a5,a4,420053d0 <heap_caps_free+0x72>
42005374:	3fc957b7          	lui	a5,0x3fc95
42005378:	9ac7a783          	lw	a5,-1620(a5) # 3fc949ac <registered_heaps>
4200537c:	cb99                	beqz	a5,42005392 <heap_caps_free+0x34>
4200537e:	4fc8                	lw	a0,28(a5)
42005380:	c519                	beqz	a0,4200538e <heap_caps_free+0x30>
42005382:	47d8                	lw	a4,12(a5)
42005384:	00e5c563          	blt	a1,a4,4200538e <heap_caps_free+0x30>
42005388:	4b98                	lw	a4,16(a5)
4200538a:	02e5c663          	blt	a1,a4,420053b6 <heap_caps_free+0x58>
4200538e:	539c                	lw	a5,32(a5)
42005390:	f7fd                	bnez	a5,4200537e <heap_caps_free+0x20>
42005392:	3c1236b7          	lui	a3,0x3c123
42005396:	3c13e637          	lui	a2,0x3c13e
4200539a:	3c123537          	lui	a0,0x3c123
4200539e:	3cc68693          	addi	a3,a3,972 # 3c1233cc <_esp_trace_encoder_array_end+0x32ac>
420053a2:	bcc60613          	addi	a2,a2,-1076 # 3c13dbcc <__func__.1>
420053a6:	42250513          	addi	a0,a0,1058 # 3c123422 <_esp_trace_encoder_array_end+0x3302>
420053aa:	05000593          	li	a1,80
420053ae:	fe381097          	auipc	ra,0xfe381
420053b2:	e78080e7          	jalr	-392(ra) # 40386226 <__assert_func>
420053b6:	c62e                	sw	a1,12(sp)
420053b8:	ca5fd0ef          	jal	4200305c <multi_heap_aligned_free>
420053bc:	420277b7          	lui	a5,0x42027
420053c0:	9d678793          	addi	a5,a5,-1578 # 420269d6 <esp_heap_trace_free_hook>
420053c4:	cb89                	beqz	a5,420053d6 <heap_caps_free+0x78>
420053c6:	4532                	lw	a0,12(sp)
420053c8:	40f2                	lw	ra,28(sp)
420053ca:	6105                	addi	sp,sp,32
420053cc:	60a2106f          	j	420269d6 <esp_heap_trace_free_hook>
420053d0:	ffc52583          	lw	a1,-4(a0)
420053d4:	b745                	j	42005374 <heap_caps_free+0x16>
420053d6:	40f2                	lw	ra,28(sp)
420053d8:	6105                	addi	sp,sp,32
420053da:	8082                	ret
420053dc:	8082                	ret
