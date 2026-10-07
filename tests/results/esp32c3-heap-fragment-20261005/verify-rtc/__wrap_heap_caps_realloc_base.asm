
idf\esp32c3-oled-native\build-heap-fragment\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026a8a <__wrap_heap_caps_realloc_base>:
42026a8a:	1101                	addi	sp,sp,-32
42026a8c:	cc22                	sw	s0,24(sp)
42026a8e:	ce06                	sw	ra,28(sp)
42026a90:	842a                	mv	s0,a0
42026a92:	c62e                	sw	a1,12(sp)
42026a94:	c432                	sw	a2,8(sp)
42026a96:	fe360097          	auipc	ra,0xfe360
42026a9a:	2b0080e7          	jalr	688(ra) # 40386d46 <vPortEnterCritical>
42026a9e:	4622                	lw	a2,8(sp)
42026aa0:	45b2                	lw	a1,12(sp)
42026aa2:	8522                	mv	a0,s0
42026aa4:	a0fde0ef          	jal	420054b2 <heap_caps_realloc_base>
42026aa8:	c119                	beqz	a0,42026aae <__wrap_heap_caps_realloc_base+0x24>
42026aaa:	00a41c63          	bne	s0,a0,42026ac2 <__wrap_heap_caps_realloc_base+0x38>
42026aae:	c42a                	sw	a0,8(sp)
42026ab0:	fe360097          	auipc	ra,0xfe360
42026ab4:	2d2080e7          	jalr	722(ra) # 40386d82 <vPortExitCritical>
42026ab8:	40f2                	lw	ra,28(sp)
42026aba:	4462                	lw	s0,24(sp)
42026abc:	4522                	lw	a0,8(sp)
42026abe:	6105                	addi	sp,sp,32
42026ac0:	8082                	ret
42026ac2:	d475                	beqz	s0,42026aae <__wrap_heap_caps_realloc_base+0x24>
42026ac4:	500017b7          	lui	a5,0x50001
42026ac8:	ab878593          	addi	a1,a5,-1352 # 50000ab8 <owners>
42026acc:	872e                	mv	a4,a1
42026ace:	4781                	li	a5,0
42026ad0:	08000613          	li	a2,128
42026ad4:	a021                	j	42026adc <__wrap_heap_caps_realloc_base+0x52>
42026ad6:	0785                	addi	a5,a5,1
42026ad8:	fcc78be3          	beq	a5,a2,42026aae <__wrap_heap_caps_realloc_base+0x24>
42026adc:	4314                	lw	a3,0(a4)
42026ade:	0761                	addi	a4,a4,24
42026ae0:	fed41be3          	bne	s0,a3,42026ad6 <__wrap_heap_caps_realloc_base+0x4c>
42026ae4:	500018b7          	lui	a7,0x50001
42026ae8:	50001837          	lui	a6,0x50001
42026aec:	aa48a603          	lw	a2,-1372(a7) # 50000aa4 <live>
42026af0:	a9882683          	lw	a3,-1384(a6) # 50000a98 <free_events>
42026af4:	00179713          	slli	a4,a5,0x1
42026af8:	97ba                	add	a5,a5,a4
42026afa:	078e                	slli	a5,a5,0x3
42026afc:	97ae                	add	a5,a5,a1
42026afe:	167d                	addi	a2,a2,-1
42026b00:	00168713          	addi	a4,a3,1
42026b04:	c42a                	sw	a0,8(sp)
42026b06:	0007a023          	sw	zero,0(a5)
42026b0a:	0007a223          	sw	zero,4(a5)
42026b0e:	0007a423          	sw	zero,8(a5)
42026b12:	0007a623          	sw	zero,12(a5)
42026b16:	0007a823          	sw	zero,16(a5)
42026b1a:	0007aa23          	sw	zero,20(a5)
42026b1e:	aac8a223          	sw	a2,-1372(a7)
42026b22:	a8e82c23          	sw	a4,-1384(a6)
42026b26:	fe360097          	auipc	ra,0xfe360
42026b2a:	25c080e7          	jalr	604(ra) # 40386d82 <vPortExitCritical>
42026b2e:	40f2                	lw	ra,28(sp)
42026b30:	4462                	lw	s0,24(sp)
42026b32:	4522                	lw	a0,8(sp)
42026b34:	6105                	addi	sp,sp,32
42026b36:	8082                	ret
