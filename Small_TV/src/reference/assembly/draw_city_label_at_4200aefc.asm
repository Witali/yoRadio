
factory-irom.bin:     file format binary


Disassembly of section .data:

4200aefc <.data+0xaedc>:
4200aefc:	1141                	addi	sp,sp,-16
4200aefe:	c606                	sw	ra,12(sp)
4200af00:	4701                	li	a4,0
4200af02:	46e1                	li	a3,24
4200af04:	0b400613          	li	a2,180
4200af08:	4581                	li	a1,0
4200af0a:	4501                	li	a0,0
4200af0c:	a2bfe0ef          	jal	0x42009936
4200af10:	3fcb8537          	lui	a0,0x3fcb8
4200af14:	c7750513          	addi	a0,a0,-905 # 0x3fcb7c77
4200af18:	fdff5097          	auipc	ra,0xfdff5
4200af1c:	590080e7          	jalr	1424(ra) # 0x400004a8
4200af20:	0ff57513          	zext.b	a0,a0
4200af24:	e501                	bnez	a0,0x4200af2c
4200af26:	40b2                	lw	ra,12(sp)
4200af28:	0141                	addi	sp,sp,16
4200af2a:	8082                	ret
4200af2c:	00151793          	slli	a5,a0,0x1
4200af30:	953e                	add	a0,a0,a5
4200af32:	050a                	slli	a0,a0,0x2
4200af34:	0ff57513          	zext.b	a0,a0
4200af38:	0b400793          	li	a5,180
4200af3c:	40a78533          	sub	a0,a5,a0
4200af40:	8505                	srai	a0,a0,0x1
4200af42:	0542                	slli	a0,a0,0x10
4200af44:	8141                	srli	a0,a0,0x10
4200af46:	4781                	li	a5,0
4200af48:	7e000713          	li	a4,2016
4200af4c:	46e1                	li	a3,24
4200af4e:	3fcb8637          	lui	a2,0x3fcb8
4200af52:	c7760613          	addi	a2,a2,-905 # 0x3fcb7c77
4200af56:	45a9                	li	a1,10
4200af58:	c97ff0ef          	jal	0x4200abee
4200af5c:	b7e9                	j	0x4200af26
