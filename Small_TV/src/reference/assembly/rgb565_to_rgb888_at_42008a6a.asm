
factory-irom.bin:     file format binary


Disassembly of section .data:

42008a6a <.data+0x8a4a>:
42008a6a:	1101                	addi	sp,sp,-32
42008a6c:	ce06                	sw	ra,28(sp)
42008a6e:	00d10693          	addi	a3,sp,13
42008a72:	00e10613          	addi	a2,sp,14
42008a76:	00f10593          	addi	a1,sp,15
42008a7a:	3f6d                	addiw	t5,t5,-5
42008a7c:	00f14783          	lbu	a5,15(sp)
42008a80:	07c2                	slli	a5,a5,0x10
42008a82:	00e14703          	lbu	a4,14(sp)
42008a86:	0722                	slli	a4,a4,0x8
42008a88:	8fd9                	or	a5,a5,a4
42008a8a:	00d14503          	lbu	a0,13(sp)
42008a8e:	8d5d                	or	a0,a0,a5
42008a90:	40f2                	lw	ra,28(sp)
42008a92:	6105                	addi	sp,sp,32
42008a94:	8082                	ret
