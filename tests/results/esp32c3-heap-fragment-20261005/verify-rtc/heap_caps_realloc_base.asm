
idf\esp32c3-oled-native\build-heap-fragment\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420054b2 <heap_caps_realloc_base>:
420054b2:	7139                	addi	sp,sp,-64
420054b4:	dc22                	sw	s0,56(sp)
420054b6:	ce2e                	sw	a1,28(sp)
420054b8:	cc32                	sw	a2,24(sp)
420054ba:	4791                	li	a5,4
420054bc:	086c                	addi	a1,sp,28
420054be:	842a                	mv	s0,a0
420054c0:	0830                	addi	a2,sp,24
420054c2:	1068                	addi	a0,sp,44
420054c4:	de06                	sw	ra,60(sp)
420054c6:	da26                	sw	s1,52(sp)
420054c8:	d63e                	sw	a5,44(sp)
420054ca:	4e5000ef          	jal	420061ae <esp_heap_adjust_alignment_to_hw>
420054ce:	45f2                	lw	a1,28(sp)
420054d0:	12040463          	beqz	s0,420055f8 <heap_caps_realloc_base+0x146>
420054d4:	12058763          	beqz	a1,42005602 <heap_caps_realloc_base+0x150>
420054d8:	000647b7          	lui	a5,0x64
420054dc:	12b7e563          	bltu	a5,a1,42005606 <heap_caps_realloc_base+0x154>
420054e0:	bfc80737          	lui	a4,0xbfc80
420054e4:	3fc957b7          	lui	a5,0x3fc95
420054e8:	9722                	add	a4,a4,s0
420054ea:	000606b7          	lui	a3,0x60
420054ee:	9ac7a783          	lw	a5,-1620(a5) # 3fc949ac <registered_heaps>
420054f2:	04d77263          	bgeu	a4,a3,42005536 <heap_caps_realloc_base+0x84>
420054f6:	cf89                	beqz	a5,42005510 <heap_caps_realloc_base+0x5e>
420054f8:	ffc42683          	lw	a3,-4(s0)
420054fc:	4fc8                	lw	a0,28(a5)
420054fe:	c519                	beqz	a0,4200550c <heap_caps_realloc_base+0x5a>
42005500:	47d8                	lw	a4,12(a5)
42005502:	00e6c563          	blt	a3,a4,4200550c <heap_caps_realloc_base+0x5a>
42005506:	4b98                	lw	a4,16(a5)
42005508:	0ae6c463          	blt	a3,a4,420055b0 <heap_caps_realloc_base+0xfe>
4200550c:	539c                	lw	a5,32(a5)
4200550e:	f7fd                	bnez	a5,420054fc <heap_caps_realloc_base+0x4a>
42005510:	3c1236b7          	lui	a3,0x3c123
42005514:	3c13e637          	lui	a2,0x3c13e
42005518:	3c123537          	lui	a0,0x3c123
4200551c:	43468693          	addi	a3,a3,1076 # 3c123434 <_esp_trace_encoder_array_end+0x3314>
42005520:	bb460613          	addi	a2,a2,-1100 # 3c13dbb4 <__func__.0>
42005524:	42250513          	addi	a0,a0,1058 # 3c123422 <_esp_trace_encoder_array_end+0x3302>
42005528:	0f700593          	li	a1,247
4200552c:	fe381097          	auipc	ra,0xfe381
42005530:	cfa080e7          	jalr	-774(ra) # 40386226 <__assert_func>
42005534:	539c                	lw	a5,32(a5)
42005536:	10078163          	beqz	a5,42005638 <heap_caps_realloc_base+0x186>
4200553a:	4fc8                	lw	a0,28(a5)
4200553c:	dd65                	beqz	a0,42005534 <heap_caps_realloc_base+0x82>
4200553e:	47d8                	lw	a4,12(a5)
42005540:	fee44ae3          	blt	s0,a4,42005534 <heap_caps_realloc_base+0x82>
42005544:	4b98                	lw	a4,16(a5)
42005546:	fee457e3          	bge	s0,a4,42005534 <heap_caps_realloc_base+0x82>
4200554a:	4805                	li	a6,1
4200554c:	4681                	li	a3,0
4200554e:	4e01                	li	t3,0
42005550:	4398                	lw	a4,0(a5)
42005552:	0047a303          	lw	t1,4(a5)
42005556:	0087a883          	lw	a7,8(a5)
4200555a:	4662                	lw	a2,24(sp)
4200555c:	00676733          	or	a4,a4,t1
42005560:	01176733          	or	a4,a4,a7
42005564:	8f71                	and	a4,a4,a2
42005566:	04c71863          	bne	a4,a2,420055b6 <heap_caps_realloc_base+0x104>
4200556a:	04080663          	beqz	a6,420055b6 <heap_caps_realloc_base+0x104>
4200556e:	5732                	lw	a4,44(sp)
42005570:	4691                	li	a3,4
42005572:	06e6f263          	bgeu	a3,a4,420055d6 <heap_caps_realloc_base+0x124>
42005576:	853a                	mv	a0,a4
42005578:	c63e                	sw	a5,12(sp)
4200557a:	3595                	jal	420053de <heap_caps_aligned_alloc_base>
4200557c:	84aa                	mv	s1,a0
4200557e:	c541                	beqz	a0,42005606 <heap_caps_realloc_base+0x154>
42005580:	47b2                	lw	a5,12(sp)
42005582:	4fc8                	lw	a0,28(a5)
42005584:	85a2                	mv	a1,s0
42005586:	9d9fd0ef          	jal	42002f5e <multi_heap_get_allocated_size>
4200558a:	c549                	beqz	a0,42005614 <heap_caps_realloc_base+0x162>
4200558c:	4672                	lw	a2,28(sp)
4200558e:	00c57363          	bgeu	a0,a2,42005594 <heap_caps_realloc_base+0xe2>
42005592:	862a                	mv	a2,a0
42005594:	85a2                	mv	a1,s0
42005596:	8526                	mv	a0,s1
42005598:	fe381097          	auipc	ra,0xfe381
4200559c:	e06080e7          	jalr	-506(ra) # 4038639e <memcpy>
420055a0:	8522                	mv	a0,s0
420055a2:	3b75                	jal	4200535e <heap_caps_free>
420055a4:	50f2                	lw	ra,60(sp)
420055a6:	5462                	lw	s0,56(sp)
420055a8:	8526                	mv	a0,s1
420055aa:	54d2                	lw	s1,52(sp)
420055ac:	6121                	addi	sp,sp,64
420055ae:	8082                	ret
420055b0:	4801                	li	a6,0
420055b2:	4e05                	li	t3,1
420055b4:	bf71                	j	42005550 <heap_caps_realloc_base+0x9e>
420055b6:	5532                	lw	a0,44(sp)
420055b8:	ca3e                	sw	a5,20(sp)
420055ba:	c636                	sw	a3,12(sp)
420055bc:	c872                	sw	t3,16(sp)
420055be:	3505                	jal	420053de <heap_caps_aligned_alloc_base>
420055c0:	84aa                	mv	s1,a0
420055c2:	c131                	beqz	a0,42005606 <heap_caps_realloc_base+0x154>
420055c4:	47d2                	lw	a5,20(sp)
420055c6:	4e42                	lw	t3,16(sp)
420055c8:	4fc8                	lw	a0,28(a5)
420055ca:	fa0e0de3          	beqz	t3,42005584 <heap_caps_realloc_base+0xd2>
420055ce:	45b2                	lw	a1,12(sp)
420055d0:	98ffd0ef          	jal	42002f5e <multi_heap_get_allocated_size>
420055d4:	bf5d                	j	4200558a <heap_caps_realloc_base+0xd8>
420055d6:	862e                	mv	a2,a1
420055d8:	85a2                	mv	a1,s0
420055da:	c63e                	sw	a5,12(sp)
420055dc:	aebfd0ef          	jal	420030c6 <multi_heap_realloc>
420055e0:	84aa                	mv	s1,a0
420055e2:	c505                	beqz	a0,4200560a <heap_caps_realloc_base+0x158>
420055e4:	420277b7          	lui	a5,0x42027
420055e8:	83278793          	addi	a5,a5,-1998 # 42026832 <esp_heap_trace_alloc_hook>
420055ec:	dfc5                	beqz	a5,420055a4 <heap_caps_realloc_base+0xf2>
420055ee:	4662                	lw	a2,24(sp)
420055f0:	45f2                	lw	a1,28(sp)
420055f2:	240210ef          	jal	42026832 <esp_heap_trace_alloc_hook>
420055f6:	b77d                	j	420055a4 <heap_caps_realloc_base+0xf2>
420055f8:	4662                	lw	a2,24(sp)
420055fa:	5532                	lw	a0,44(sp)
420055fc:	33cd                	jal	420053de <heap_caps_aligned_alloc_base>
420055fe:	84aa                	mv	s1,a0
42005600:	b755                	j	420055a4 <heap_caps_realloc_base+0xf2>
42005602:	8522                	mv	a0,s0
42005604:	3ba9                	jal	4200535e <heap_caps_free>
42005606:	4481                	li	s1,0
42005608:	bf71                	j	420055a4 <heap_caps_realloc_base+0xf2>
4200560a:	5732                	lw	a4,44(sp)
4200560c:	4662                	lw	a2,24(sp)
4200560e:	45f2                	lw	a1,28(sp)
42005610:	47b2                	lw	a5,12(sp)
42005612:	b795                	j	42005576 <heap_caps_realloc_base+0xc4>
42005614:	3c1236b7          	lui	a3,0x3c123
42005618:	3c13e637          	lui	a2,0x3c13e
4200561c:	3c123537          	lui	a0,0x3c123
42005620:	47068693          	addi	a3,a3,1136 # 3c123470 <_esp_trace_encoder_array_end+0x3350>
42005624:	bb460613          	addi	a2,a2,-1100 # 3c13dbb4 <__func__.0>
42005628:	42250513          	addi	a0,a0,1058 # 3c123422 <_esp_trace_encoder_array_end+0x3302>
4200562c:	13900593          	li	a1,313
42005630:	fe381097          	auipc	ra,0xfe381
42005634:	bf6080e7          	jalr	-1034(ra) # 40386226 <__assert_func>
42005638:	3c1236b7          	lui	a3,0x3c123
4200563c:	3c13e637          	lui	a2,0x3c13e
42005640:	3c123537          	lui	a0,0x3c123
42005644:	43468693          	addi	a3,a3,1076 # 3c123434 <_esp_trace_encoder_array_end+0x3314>
42005648:	bb460613          	addi	a2,a2,-1100 # 3c13dbb4 <__func__.0>
4200564c:	42250513          	addi	a0,a0,1058 # 3c123422 <_esp_trace_encoder_array_end+0x3302>
42005650:	10000593          	li	a1,256
42005654:	fe381097          	auipc	ra,0xfe381
42005658:	bd2080e7          	jalr	-1070(ra) # 40386226 <__assert_func>
