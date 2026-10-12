
factory-irom.bin:     file format binary


Disassembly of section .data:

4200af5e <.data+0xaf3e>:
4200af5e:	1141                	addi	sp,sp,-16
4200af60:	c606                	sw	ra,12(sp)
4200af62:	4701                	li	a4,0
4200af64:	46e1                	li	a3,24
4200af66:	0b400613          	li	a2,180
4200af6a:	02800593          	li	a1,40
4200af6e:	4501                	li	a0,0
4200af70:	9c7fe0ef          	jal	0x42009936
4200af74:	3fcbb537          	lui	a0,0x3fcbb
4200af78:	9b850513          	addi	a0,a0,-1608 # 0x3fcba9b8
4200af7c:	fdff5097          	auipc	ra,0xfdff5
4200af80:	52c080e7          	jalr	1324(ra) # 0x400004a8
4200af84:	0ff57513          	zext.b	a0,a0
4200af88:	47bd                	li	a5,15
4200af8a:	02a7ef63          	bltu	a5,a0,0x4200afc8
4200af8e:	c915                	beqz	a0,0x4200afc2
4200af90:	00151793          	slli	a5,a0,0x1
4200af94:	953e                	add	a0,a0,a5
4200af96:	050a                	slli	a0,a0,0x2
4200af98:	0ff57513          	zext.b	a0,a0
4200af9c:	0b400793          	li	a5,180
4200afa0:	40a78533          	sub	a0,a5,a0
4200afa4:	8505                	srai	a0,a0,0x1
4200afa6:	0542                	slli	a0,a0,0x10
4200afa8:	8141                	srli	a0,a0,0x10
4200afaa:	4781                	li	a5,0
4200afac:	6741                	lui	a4,0x10
4200afae:	177d                	addi	a4,a4,-1 # 0xffff
4200afb0:	46e1                	li	a3,24
4200afb2:	3fcbb637          	lui	a2,0x3fcbb
4200afb6:	9b860613          	addi	a2,a2,-1608 # 0x3fcba9b8
4200afba:	02800593          	li	a1,40
4200afbe:	c31ff0ef          	jal	0x4200abee
4200afc2:	40b2                	lw	ra,12(sp)
4200afc4:	0141                	addi	sp,sp,16
4200afc6:	8082                	ret
4200afc8:	453d                	li	a0,15
4200afca:	b7d9                	j	0x4200af90
