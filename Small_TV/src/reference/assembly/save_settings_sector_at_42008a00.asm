
factory-irom.bin:     file format binary


Disassembly of section .data:

42008a00 <.data+0x89e0>:
42008a00:	1141                	addi	sp,sp,-16
42008a02:	c606                	sw	ra,12(sp)
42008a04:	6605                	lui	a2,0x1
42008a06:	003e75b7          	lui	a1,0x3e7
42008a0a:	4501                	li	a0,0
42008a0c:	fe389097          	auipc	ra,0xfe389
42008a10:	488080e7          	jalr	1160(ra) # 0x40391e94
42008a14:	1bc00693          	li	a3,444
42008a18:	003e7637          	lui	a2,0x3e7
42008a1c:	3fcb85b7          	lui	a1,0x3fcb8
42008a20:	b9c58593          	addi	a1,a1,-1124 # 0x3fcb7b9c
42008a24:	4501                	li	a0,0
42008a26:	fe38a097          	auipc	ra,0xfe38a
42008a2a:	a4c080e7          	jalr	-1460(ra) # 0x40392472
42008a2e:	40b2                	lw	ra,12(sp)
42008a30:	0141                	addi	sp,sp,16
42008a32:	8082                	ret
