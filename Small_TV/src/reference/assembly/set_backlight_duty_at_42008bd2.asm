
factory-irom.bin:     file format binary


Disassembly of section .data:

42008bd2 <.data+0x8bb2>:
42008bd2:	1141                	addi	sp,sp,-16
42008bd4:	c606                	sw	ra,12(sp)
42008bd6:	00d51613          	slli	a2,a0,0xd
42008bda:	8e09                	sub	a2,a2,a0
42008bdc:	106257b7          	lui	a5,0x10625
42008be0:	dd378793          	addi	a5,a5,-557 # 0x10624dd3
42008be4:	02f63633          	mulhu	a2,a2,a5
42008be8:	8219                	srli	a2,a2,0x6
42008bea:	4581                	li	a1,0
42008bec:	4501                	li	a0,0
42008bee:	11f0c0ef          	jal	0x4201550c
42008bf2:	e909                	bnez	a0,0x42008c04
42008bf4:	4581                	li	a1,0
42008bf6:	4501                	li	a0,0
42008bf8:	2700c0ef          	jal	0x42014e68
42008bfc:	e515                	bnez	a0,0x42008c28
42008bfe:	40b2                	lw	ra,12(sp)
42008c00:	0141                	addi	sp,sp,16
42008c02:	8082                	ret
42008c04:	3c0c3737          	lui	a4,0x3c0c3
42008c08:	a2c70713          	addi	a4,a4,-1492 # 0x3c0c2a2c
42008c0c:	3c0d66b7          	lui	a3,0x3c0d6
42008c10:	26468693          	addi	a3,a3,612 # 0x3c0d6264
42008c14:	2a000613          	li	a2,672
42008c18:	3c0c35b7          	lui	a1,0x3c0c3
42008c1c:	93458593          	addi	a1,a1,-1740 # 0x3c0c2934
42008c20:	fe37e097          	auipc	ra,0xfe37e
42008c24:	64a080e7          	jalr	1610(ra) # 0x4038726a
42008c28:	3c0c3737          	lui	a4,0x3c0c3
42008c2c:	a6070713          	addi	a4,a4,-1440 # 0x3c0c2a60
42008c30:	3c0d66b7          	lui	a3,0x3c0d6
42008c34:	26468693          	addi	a3,a3,612 # 0x3c0d6264
42008c38:	2a200613          	li	a2,674
42008c3c:	3c0c35b7          	lui	a1,0x3c0c3
42008c40:	93458593          	addi	a1,a1,-1740 # 0x3c0c2934
42008c44:	fe37e097          	auipc	ra,0xfe37e
42008c48:	626080e7          	jalr	1574(ra) # 0x4038726a
