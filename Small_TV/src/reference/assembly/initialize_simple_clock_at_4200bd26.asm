
factory-irom.bin:     file format binary


Disassembly of section .data:

4200bd26 <.data+0xbd06>:
4200bd26:	1141                	addi	sp,sp,-16
4200bd28:	c606                	sw	ra,12(sp)
4200bd2a:	6741                	lui	a4,0x10
4200bd2c:	177d                	addi	a4,a4,-1 # 0xffff
4200bd2e:	46c1                	li	a3,16
4200bd30:	3fcb8637          	lui	a2,0x3fcb8
4200bd34:	b8460613          	addi	a2,a2,-1148 # 0x3fcb7b84
4200bd38:	0e100593          	li	a1,225
4200bd3c:	4515                	li	a0,5
4200bd3e:	ce1fe0ef          	jal	0x4200aa1e
4200bd42:	4701                	li	a4,0
4200bd44:	66b1                	lui	a3,0xc
4200bd46:	61868693          	addi	a3,a3,1560 # 0xc618
4200bd4a:	4609                	li	a2,2
4200bd4c:	04600593          	li	a1,70
4200bd50:	4501                	li	a0,0
4200bd52:	f5dfe0ef          	jal	0x4200acae
4200bd56:	4701                	li	a4,0
4200bd58:	66b1                	lui	a3,0xc
4200bd5a:	61868693          	addi	a3,a3,1560 # 0xc618
4200bd5e:	4609                	li	a2,2
4200bd60:	04600593          	li	a1,70
4200bd64:	08c00513          	li	a0,140
4200bd68:	f47fe0ef          	jal	0x4200acae
4200bd6c:	4785                	li	a5,1
4200bd6e:	3fcc4737          	lui	a4,0x3fcc4
4200bd72:	9ef70ba3          	sb	a5,-1545(a4) # 0x3fcc39f7
4200bd76:	3fcc4737          	lui	a4,0x3fcc4
4200bd7a:	9ef70b23          	sb	a5,-1546(a4) # 0x3fcc39f6
4200bd7e:	3fcc4737          	lui	a4,0x3fcc4
4200bd82:	9ef70aa3          	sb	a5,-1547(a4) # 0x3fcc39f5
4200bd86:	40b2                	lw	ra,12(sp)
4200bd88:	0141                	addi	sp,sp,16
4200bd8a:	8082                	ret
