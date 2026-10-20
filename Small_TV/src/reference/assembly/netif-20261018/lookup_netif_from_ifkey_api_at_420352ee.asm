
factory-irom.bin:     file format binary


Disassembly of section .data:

420352ee <.data+0x352ce>:
420352ee:	1141                	addi	sp,sp,-16
420352f0:	c606                	sw	ra,12(sp)
420352f2:	c422                	sw	s0,8(sp)
420352f4:	4540                	lw	s0,12(a0)
420352f6:	4908                	lw	a0,16(a0)
420352f8:	b3bff0ef          	jal	0x42034e32
420352fc:	c008                	sw	a0,0(s0)
420352fe:	4501                	li	a0,0
42035300:	40b2                	lw	ra,12(sp)
42035302:	4422                	lw	s0,8(sp)
42035304:	0141                	addi	sp,sp,16
42035306:	8082                	ret
42035308:	491c                	lw	a5,16(a0)
4203530a:	4558                	lw	a4,12(a0)
4203530c:	0007c883          	lbu	a7,0(a5)
