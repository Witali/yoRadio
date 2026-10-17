
factory-analysis.elf:     file format elf32-littleriscv


Disassembly of section .flash.text:

4200dfdc <.flash.text+0xdfbc>:
4200dfdc:	1101                	addi	sp,sp,-32
4200dfde:	ce06                	sw	ra,28(sp)
4200dfe0:	cc22                	sw	s0,24(sp)
4200dfe2:	ca26                	sw	s1,20(sp)
4200dfe4:	842a                	mv	s0,a0
4200dfe6:	03000793          	li	a5,48
4200dfea:	00f10623          	sb	a5,12(sp)
4200dfee:	3fcb87b7          	lui	a5,0x3fcb8
4200dff2:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200dff6:	1687a783          	lw	a5,360(a5)
4200dffa:	c39d                	beqz	a5,0x4200e020
4200dffc:	4705                	li	a4,1
4200dffe:	00e78d63          	beq	a5,a4,0x4200e018
4200e002:	4709                	li	a4,2
4200e004:	06e78363          	beq	a5,a4,0x4200e06a
4200e008:	470d                	li	a4,3
4200e00a:	00e79b63          	bne	a5,a4,0x4200e020
4200e00e:	03300793          	li	a5,51
4200e012:	00f10623          	sb	a5,12(sp)
4200e016:	a029                	j	0x4200e020
4200e018:	03100793          	li	a5,49
4200e01c:	00f10623          	sb	a5,12(sp)
4200e020:	000106a3          	sb	zero,13(sp)
4200e024:	3c0c35b7          	lui	a1,0x3c0c3
4200e028:	40858593          	addi	a1,a1,1032 # 0x3c0c3408
4200e02c:	8522                	mv	a0,s0
4200e02e:	14a2d0ef          	jal	0x4203b178
4200e032:	3c0c3637          	lui	a2,0x3c0c3
4200e036:	1dc60613          	addi	a2,a2,476 # 0x3c0c31dc
4200e03a:	3c0c35b7          	lui	a1,0x3c0c3
4200e03e:	1e458593          	addi	a1,a1,484 # 0x3c0c31e4
4200e042:	8522                	mv	a0,s0
4200e044:	0d02d0ef          	jal	0x4203b114
4200e048:	0064                	addi	s1,sp,12
4200e04a:	8526                	mv	a0,s1
4200e04c:	fdff2097          	auipc	ra,0xfdff2
4200e050:	45c080e7          	jalr	1116(ra) # 0x400004a8
4200e054:	862a                	mv	a2,a0
4200e056:	85a6                	mv	a1,s1
4200e058:	8522                	mv	a0,s0
4200e05a:	1382d0ef          	jal	0x4203b192
4200e05e:	4501                	li	a0,0
4200e060:	40f2                	lw	ra,28(sp)
4200e062:	4462                	lw	s0,24(sp)
4200e064:	44d2                	lw	s1,20(sp)
4200e066:	6105                	addi	sp,sp,32
4200e068:	8082                	ret
4200e06a:	03200793          	li	a5,50
4200e06e:	00f10623          	sb	a5,12(sp)
4200e072:	b77d                	j	0x4200e020
