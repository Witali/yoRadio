
factory-irom.bin:     file format binary


Disassembly of section .data:

42036770 <.data+0x36750>:
42036770:	1101                	addi	sp,sp,-32
42036772:	ce06                	sw	ra,28(sp)
42036774:	862a                	mv	a2,a0
42036776:	c602                	sw	zero,12(sp)
42036778:	006c                	addi	a1,sp,12
4203677a:	42035537          	lui	a0,0x42035
4203677e:	2ee50513          	addi	a0,a0,750 # 0x420352ee
42036782:	931fe0ef          	jal	0x420350b2
42036786:	4532                	lw	a0,12(sp)
42036788:	40f2                	lw	ra,28(sp)
4203678a:	6105                	addi	sp,sp,32
4203678c:	8082                	ret
