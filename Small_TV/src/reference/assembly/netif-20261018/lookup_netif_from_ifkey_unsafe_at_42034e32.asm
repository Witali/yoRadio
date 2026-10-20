
factory-irom.bin:     file format binary


Disassembly of section .data:

42034e32 <.data+0x34e12>:
42034e32:	1141                	addi	sp,sp,-16
42034e34:	c606                	sw	ra,12(sp)
42034e36:	c422                	sw	s0,8(sp)
42034e38:	c226                	sw	s1,4(sp)
42034e3a:	c04a                	sw	s2,0(sp)
42034e3c:	892a                	mv	s2,a0
42034e3e:	3fcc47b7          	lui	a5,0x3fcc4
42034e42:	c0c7a403          	lw	s0,-1012(a5) # 0x3fcc3c0c
42034e46:	a011                	j	0x42034e4a
42034e48:	4040                	lw	s0,4(s0)
42034e4a:	cc09                	beqz	s0,0x42034e64
42034e4c:	4004                	lw	s1,0(s0)
42034e4e:	8526                	mv	a0,s1
42034e50:	148020ef          	jal	0x42036f98
42034e54:	85aa                	mv	a1,a0
42034e56:	854a                	mv	a0,s2
42034e58:	fdfcb097          	auipc	ra,0xfdfcb
42034e5c:	648080e7          	jalr	1608(ra) # 0x400004a0
42034e60:	f565                	bnez	a0,0x42034e48
42034e62:	8426                	mv	s0,s1
42034e64:	8522                	mv	a0,s0
42034e66:	40b2                	lw	ra,12(sp)
42034e68:	4422                	lw	s0,8(sp)
42034e6a:	4492                	lw	s1,4(sp)
42034e6c:	4902                	lw	s2,0(sp)
42034e6e:	0141                	addi	sp,sp,16
42034e70:	8082                	ret
42034e72:	451c                	lw	a5,8(a0)
42034e74:	0007a023          	sw	zero,0(a5)
42034e78:	451c                	lw	a5,8(a0)
42034e7a:	0007a423          	sw	zero,8(a5)
42034e7e:	451c                	lw	a5,8(a0)
