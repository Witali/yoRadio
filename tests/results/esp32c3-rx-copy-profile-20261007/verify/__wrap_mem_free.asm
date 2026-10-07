
idf\esp32c3-oled-native\build-rx-copy\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026d84 <__wrap_mem_free>:
42026d84:	1141                	addi	sp,sp,-16
42026d86:	c422                	sw	s0,8(sp)
42026d88:	c606                	sw	ra,12(sp)
42026d8a:	842a                	mv	s0,a0
42026d8c:	fe360097          	auipc	ra,0xfe360
42026d90:	fba080e7          	jalr	-70(ra) # 40386d46 <vPortEnterCritical>
42026d94:	3fc917b7          	lui	a5,0x3fc91
42026d98:	2ac78593          	addi	a1,a5,684 # 3fc912ac <s_owners>
42026d9c:	87ae                	mv	a5,a1
42026d9e:	4701                	li	a4,0
42026da0:	04000613          	li	a2,64
42026da4:	a021                	j	42026dac <__wrap_mem_free+0x28>
42026da6:	0705                	addi	a4,a4,1
42026da8:	04c70e63          	beq	a4,a2,42026e04 <__wrap_mem_free+0x80>
42026dac:	4394                	lw	a3,0(a5)
42026dae:	07b1                	addi	a5,a5,12
42026db0:	fe869be3          	bne	a3,s0,42026da6 <__wrap_mem_free+0x22>
42026db4:	daed                	beqz	a3,42026da6 <__wrap_mem_free+0x22>
42026db6:	00171793          	slli	a5,a4,0x1
42026dba:	97ba                	add	a5,a5,a4
42026dbc:	078a                	slli	a5,a5,0x2
42026dbe:	97ae                	add	a5,a5,a1
42026dc0:	00a7c603          	lbu	a2,10(a5)
42026dc4:	3fc91737          	lui	a4,0x3fc91
42026dc8:	23c70713          	addi	a4,a4,572 # 3fc9123c <s_counts>
42026dcc:	00161693          	slli	a3,a2,0x1
42026dd0:	96b2                	add	a3,a3,a2
42026dd2:	068a                	slli	a3,a3,0x2
42026dd4:	96ba                	add	a3,a3,a4
42026dd6:	0386a803          	lw	a6,56(a3)
42026dda:	4748                	lw	a0,12(a4)
42026ddc:	470c                	lw	a1,8(a4)
42026dde:	0047a883          	lw	a7,4(a5)
42026de2:	4b50                	lw	a2,20(a4)
42026de4:	187d                	addi	a6,a6,-1
42026de6:	157d                	addi	a0,a0,-1
42026de8:	0585                	addi	a1,a1,1
42026dea:	41160633          	sub	a2,a2,a7
42026dee:	0007a023          	sw	zero,0(a5)
42026df2:	0007a423          	sw	zero,8(a5)
42026df6:	0306ac23          	sw	a6,56(a3)
42026dfa:	c748                	sw	a0,12(a4)
42026dfc:	c70c                	sw	a1,8(a4)
42026dfe:	0007a223          	sw	zero,4(a5)
42026e02:	cb50                	sw	a2,20(a4)
42026e04:	fe360097          	auipc	ra,0xfe360
42026e08:	f7e080e7          	jalr	-130(ra) # 40386d82 <vPortExitCritical>
42026e0c:	8522                	mv	a0,s0
42026e0e:	4422                	lw	s0,8(sp)
42026e10:	40b2                	lw	ra,12(sp)
42026e12:	0141                	addi	sp,sp,16
42026e14:	4e15706f          	j	4207eaf4 <mem_free>
