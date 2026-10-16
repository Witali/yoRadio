
factory-analysis.elf:     file format elf32-littleriscv


Disassembly of section .flash.text:

4201105c <.flash.text+0x1103c>:
4201105c:	1101                	addi	sp,sp,-32
4201105e:	ce06                	sw	ra,28(sp)
42011060:	cc22                	sw	s0,24(sp)
42011062:	ca26                	sw	s1,20(sp)
42011064:	c84a                	sw	s2,16(sp)
42011066:	c64e                	sw	s3,12(sp)
42011068:	84aa                	mv	s1,a0
4201106a:	8432                	mv	s0,a2
4201106c:	a835                	j	0x420110a8
4201106e:	3c0ef7b7          	lui	a5,0x3c0ef
42011072:	26478793          	addi	a5,a5,612 # 0x3c0ef264
42011076:	97b6                	add	a5,a5,a3
42011078:	0007c783          	lbu	a5,0(a5)
4201107c:	0005c603          	lbu	a2,0(a1)
42011080:	3c0ef737          	lui	a4,0x3c0ef
42011084:	00179813          	slli	a6,a5,0x1
42011088:	1e470713          	addi	a4,a4,484 # 0x3c0ef1e4
4201108c:	9742                	add	a4,a4,a6
4201108e:	00075703          	lhu	a4,0(a4)
42011092:	02e60733          	mul	a4,a2,a4
42011096:	078a                	slli	a5,a5,0x2
42011098:	97aa                	add	a5,a5,a0
4201109a:	c398                	sw	a4,0(a5)
4201109c:	0685                	addi	a3,a3,1
4201109e:	0585                	addi	a1,a1,1
420110a0:	03f00793          	li	a5,63
420110a4:	fcd7f5e3          	bgeu	a5,a3,0x4201106e
420110a8:	cc15                	beqz	s0,0x420110e4
420110aa:	04000793          	li	a5,64
420110ae:	0487f363          	bgeu	a5,s0,0x420110f4
420110b2:	fbf40413          	addi	s0,s0,-65
420110b6:	00158993          	addi	s3,a1,1
420110ba:	0005c783          	lbu	a5,0(a1)
420110be:	473d                	li	a4,15
420110c0:	02f76c63          	bltu	a4,a5,0x420110f8
420110c4:	0037f913          	andi	s2,a5,3
420110c8:	10000593          	li	a1,256
420110cc:	8526                	mv	a0,s1
420110ce:	f73ff0ef          	jal	0x42011040
420110d2:	c50d                	beqz	a0,0x420110fc
420110d4:	01490793          	addi	a5,s2,20
420110d8:	078a                	slli	a5,a5,0x2
420110da:	97a6                	add	a5,a5,s1
420110dc:	c388                	sw	a0,0(a5)
420110de:	85ce                	mv	a1,s3
420110e0:	4681                	li	a3,0
420110e2:	bf7d                	j	0x420110a0
420110e4:	8522                	mv	a0,s0
420110e6:	40f2                	lw	ra,28(sp)
420110e8:	4462                	lw	s0,24(sp)
420110ea:	44d2                	lw	s1,20(sp)
420110ec:	4942                	lw	s2,16(sp)
420110ee:	49b2                	lw	s3,12(sp)
420110f0:	6105                	addi	sp,sp,32
420110f2:	8082                	ret
420110f4:	4519                	li	a0,6
420110f6:	bfc5                	j	0x420110e6
420110f8:	4519                	li	a0,6
420110fa:	b7f5                	j	0x420110e6
420110fc:	450d                	li	a0,3
420110fe:	b7e5                	j	0x420110e6
