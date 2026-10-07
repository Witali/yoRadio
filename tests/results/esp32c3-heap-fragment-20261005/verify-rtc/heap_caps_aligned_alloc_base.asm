
idf\esp32c3-oled-native\build-heap-fragment\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420053de <heap_caps_aligned_alloc_base>:
420053de:	7179                	addi	sp,sp,-48
420053e0:	c62a                	sw	a0,12(sp)
420053e2:	c42e                	sw	a1,8(sp)
420053e4:	c232                	sw	a2,4(sp)
420053e6:	002c                	addi	a1,sp,8
420053e8:	0050                	addi	a2,sp,4
420053ea:	0068                	addi	a0,sp,12
420053ec:	d606                	sw	ra,44(sp)
420053ee:	5c1000ef          	jal	420061ae <esp_heap_adjust_alignment_to_hw>
420053f2:	47a2                	lw	a5,8(sp)
420053f4:	00064737          	lui	a4,0x64
420053f8:	fff78693          	addi	a3,a5,-1
420053fc:	08e6fb63          	bgeu	a3,a4,42005492 <heap_caps_aligned_alloc_base+0xb4>
42005400:	4712                	lw	a4,4(sp)
42005402:	d422                	sw	s0,40(sp)
42005404:	d226                	sw	s1,36(sp)
42005406:	d04a                	sw	s2,32(sp)
42005408:	ce4e                	sw	s3,28(sp)
4200540a:	cc52                	sw	s4,24(sp)
4200540c:	ca56                	sw	s5,20(sp)
4200540e:	8b09                	andi	a4,a4,2
42005410:	eb49                	bnez	a4,420054a2 <heap_caps_aligned_alloc_base+0xc4>
42005412:	4a81                	li	s5,0
42005414:	3fc954b7          	lui	s1,0x3fc95
42005418:	4991                	li	s3,4
4200541a:	490d                	li	s2,3
4200541c:	9ac4a403          	lw	s0,-1620(s1) # 3fc949ac <registered_heaps>
42005420:	c025                	beqz	s0,42005480 <heap_caps_aligned_alloc_base+0xa2>
42005422:	002a9a13          	slli	s4,s5,0x2
42005426:	a019                	j	4200542c <heap_caps_aligned_alloc_base+0x4e>
42005428:	5000                	lw	s0,32(s0)
4200542a:	c839                	beqz	s0,42005480 <heap_caps_aligned_alloc_base+0xa2>
4200542c:	4c48                	lw	a0,28(s0)
4200542e:	014407b3          	add	a5,s0,s4
42005432:	d97d                	beqz	a0,42005428 <heap_caps_aligned_alloc_base+0x4a>
42005434:	439c                	lw	a5,0(a5)
42005436:	4712                	lw	a4,4(sp)
42005438:	8ff9                	and	a5,a5,a4
4200543a:	d7fd                	beqz	a5,42005428 <heap_caps_aligned_alloc_base+0x4a>
4200543c:	401c                	lw	a5,0(s0)
4200543e:	4050                	lw	a2,4(s0)
42005440:	4414                	lw	a3,8(s0)
42005442:	8fd1                	or	a5,a5,a2
42005444:	8fd5                	or	a5,a5,a3
42005446:	8ff9                	and	a5,a5,a4
42005448:	fef710e3          	bne	a4,a5,42005428 <heap_caps_aligned_alloc_base+0x4a>
4200544c:	4632                	lw	a2,12(sp)
4200544e:	45a2                	lw	a1,8(sp)
42005450:	4681                	li	a3,0
42005452:	04c9e463          	bltu	s3,a2,4200549a <heap_caps_aligned_alloc_base+0xbc>
42005456:	b85fd0ef          	jal	42002fda <multi_heap_malloc>
4200545a:	d579                	beqz	a0,42005428 <heap_caps_aligned_alloc_base+0x4a>
4200545c:	420277b7          	lui	a5,0x42027
42005460:	83278793          	addi	a5,a5,-1998 # 42026832 <esp_heap_trace_alloc_hook>
42005464:	c799                	beqz	a5,42005472 <heap_caps_aligned_alloc_base+0x94>
42005466:	4612                	lw	a2,4(sp)
42005468:	45a2                	lw	a1,8(sp)
4200546a:	c02a                	sw	a0,0(sp)
4200546c:	3c6210ef          	jal	42026832 <esp_heap_trace_alloc_hook>
42005470:	4502                	lw	a0,0(sp)
42005472:	5422                	lw	s0,40(sp)
42005474:	5492                	lw	s1,36(sp)
42005476:	5902                	lw	s2,32(sp)
42005478:	49f2                	lw	s3,28(sp)
4200547a:	4a62                	lw	s4,24(sp)
4200547c:	4ad2                	lw	s5,20(sp)
4200547e:	a819                	j	42005494 <heap_caps_aligned_alloc_base+0xb6>
42005480:	0a85                	addi	s5,s5,1
42005482:	f92a9de3          	bne	s5,s2,4200541c <heap_caps_aligned_alloc_base+0x3e>
42005486:	5422                	lw	s0,40(sp)
42005488:	5492                	lw	s1,36(sp)
4200548a:	5902                	lw	s2,32(sp)
4200548c:	49f2                	lw	s3,28(sp)
4200548e:	4a62                	lw	s4,24(sp)
42005490:	4ad2                	lw	s5,20(sp)
42005492:	4501                	li	a0,0
42005494:	50b2                	lw	ra,44(sp)
42005496:	6145                	addi	sp,sp,48
42005498:	8082                	ret
4200549a:	d6ffd0ef          	jal	42003208 <multi_heap_aligned_alloc_offs>
4200549e:	d549                	beqz	a0,42005428 <heap_caps_aligned_alloc_base+0x4a>
420054a0:	bf75                	j	4200545c <heap_caps_aligned_alloc_base+0x7e>
420054a2:	078d                	addi	a5,a5,3
420054a4:	9bf1                	andi	a5,a5,-4
420054a6:	c43e                	sw	a5,8(sp)
420054a8:	b7ad                	j	42005412 <heap_caps_aligned_alloc_base+0x34>
