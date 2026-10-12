
factory-irom.bin:     file format binary


Disassembly of section .data:

4200ce40 <.data+0xce20>:
4200ce40:	1141                	addi	sp,sp,-16
4200ce42:	c606                	sw	ra,12(sp)
4200ce44:	3fcb87b7          	lui	a5,0x3fcb8
4200ce48:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200ce4c:	1607a703          	lw	a4,352(a5)
4200ce50:	4785                	li	a5,1
4200ce52:	00f70a63          	beq	a4,a5,0x4200ce66
4200ce56:	3fcc47b7          	lui	a5,0x3fcc4
4200ce5a:	4705                	li	a4,1
4200ce5c:	9ee78523          	sb	a4,-1558(a5) # 0x3fcc39ea
4200ce60:	40b2                	lw	ra,12(sp)
4200ce62:	0141                	addi	sp,sp,16
4200ce64:	8082                	ret
4200ce66:	3fcc47b7          	lui	a5,0x3fcc4
4200ce6a:	a747c783          	lbu	a5,-1420(a5) # 0x3fcc3a74
4200ce6e:	c78d                	beqz	a5,0x4200ce98
4200ce70:	470d                	li	a4,3
4200ce72:	02e78363          	beq	a5,a4,0x4200ce98
4200ce76:	4711                	li	a4,4
4200ce78:	fee794e3          	bne	a5,a4,0x4200ce60
4200ce7c:	3fcb87b7          	lui	a5,0x3fcb8
4200ce80:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200ce84:	1607a023          	sw	zero,352(a5)
4200ce88:	b79fb0ef          	jal	0x42008a00
4200ce8c:	3fcc47b7          	lui	a5,0x3fcc4
4200ce90:	4705                	li	a4,1
4200ce92:	9ee78523          	sb	a4,-1558(a5) # 0x3fcc39ea
4200ce96:	b7e9                	j	0x4200ce60
4200ce98:	b99ff0ef          	jal	0x4200ca30
4200ce9c:	b7d1                	j	0x4200ce60
