
factory-irom.bin:     file format binary


Disassembly of section .data:

42017ea0 <.data+0x17e80>:
42017ea0:	1141                	addi	sp,sp,-16
42017ea2:	c606                	sw	ra,12(sp)
42017ea4:	022040ef          	jal	0x4201bec6
42017ea8:	e509                	bnez	a0,0x42017eb2
42017eaa:	4501                	li	a0,0
42017eac:	40b2                	lw	ra,12(sp)
42017eae:	0141                	addi	sp,sp,16
42017eb0:	8082                	ret
42017eb2:	4581                	li	a1,0
42017eb4:	42018537          	lui	a0,0x42018
42017eb8:	d3450513          	addi	a0,a0,-716 # 0x42017d34
42017ebc:	796030ef          	jal	0x4201b652
42017ec0:	4505                	li	a0,1
42017ec2:	b7ed                	j	0x42017eac
