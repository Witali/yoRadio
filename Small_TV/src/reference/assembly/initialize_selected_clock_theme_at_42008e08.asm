
factory-irom.bin:     file format binary


Disassembly of section .data:

42008e08 <.data+0x8de8>:
42008e08:	1141                	addi	sp,sp,-16
42008e0a:	c606                	sw	ra,12(sp)
42008e0c:	4501                	li	a0,0
42008e0e:	3fd000ef          	jal	0x42009a0a
42008e12:	3fcb87b7          	lui	a5,0x3fcb8
42008e16:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
42008e1a:	1687a783          	lw	a5,360(a5)
42008e1e:	c385                	beqz	a5,0x42008e3e
42008e20:	4705                	li	a4,1
42008e22:	02e78163          	beq	a5,a4,0x42008e44
42008e26:	4709                	li	a4,2
42008e28:	02e78163          	beq	a5,a4,0x42008e4a
42008e2c:	470d                	li	a4,3
42008e2e:	02e78163          	beq	a5,a4,0x42008e50
42008e32:	4501                	li	a0,0
42008e34:	d9fff0ef          	jal	0x42008bd2
42008e38:	40b2                	lw	ra,12(sp)
42008e3a:	0141                	addi	sp,sp,16
42008e3c:	8082                	ret
42008e3e:	080020ef          	jal	0x4200aebe
42008e42:	bfc5                	j	0x42008e32
42008e44:	6e3020ef          	jal	0x4200bd26
42008e48:	b7ed                	j	0x42008e32
42008e4a:	4d7020ef          	jal	0x4200bb20
42008e4e:	b7d5                	j	0x42008e32
42008e50:	306010ef          	jal	0x4200a156
42008e54:	bff9                	j	0x42008e32
