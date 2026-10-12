
factory-irom.bin:     file format binary


Disassembly of section .data:

4200bb4c <.data+0xbb2c>:
4200bb4c:	1141                	addi	sp,sp,-16
4200bb4e:	c606                	sw	ra,12(sp)
4200bb50:	4681                	li	a3,0
4200bb52:	a021                	j	0x4200bb5a
4200bb54:	0685                	addi	a3,a3,1
4200bb56:	06c2                	slli	a3,a3,0x10
4200bb58:	82c1                	srli	a3,a3,0x10
4200bb5a:	4791                	li	a5,4
4200bb5c:	04d7e063          	bltu	a5,a3,0x4200bb9c
4200bb60:	3fcc47b7          	lui	a5,0x3fcc4
4200bb64:	a517c783          	lbu	a5,-1455(a5) # 0x3fcc3a51
4200bb68:	4705                	li	a4,1
4200bb6a:	00f71733          	sll	a4,a4,a5
4200bb6e:	3fcb8637          	lui	a2,0x3fcb8
4200bb72:	b9c60613          	addi	a2,a2,-1124 # 0x3fcb7b9c
4200bb76:	1a462603          	lw	a2,420(a2)
4200bb7a:	8f71                	and	a4,a4,a2
4200bb7c:	e305                	bnez	a4,0x4200bb9c
4200bb7e:	0785                	addi	a5,a5,1
4200bb80:	0ff7f793          	zext.b	a5,a5
4200bb84:	3fcc4737          	lui	a4,0x3fcc4
4200bb88:	a4f708a3          	sb	a5,-1455(a4) # 0x3fcc3a51
4200bb8c:	4711                	li	a4,4
4200bb8e:	fcf773e3          	bgeu	a4,a5,0x4200bb54
4200bb92:	3fcc47b7          	lui	a5,0x3fcc4
4200bb96:	a40788a3          	sb	zero,-1455(a5) # 0x3fcc3a51
4200bb9a:	bf6d                	j	0x4200bb54
4200bb9c:	4795                	li	a5,5
4200bb9e:	02f68a63          	beq	a3,a5,0x4200bbd2
4200bba2:	3fcc47b7          	lui	a5,0x3fcc4
4200bba6:	a517c783          	lbu	a5,-1455(a5) # 0x3fcc3a51
4200bbaa:	cb85                	beqz	a5,0x4200bbda
4200bbac:	4705                	li	a4,1
4200bbae:	04e78f63          	beq	a5,a4,0x4200bc0c
4200bbb2:	4709                	li	a4,2
4200bbb4:	06e78363          	beq	a5,a4,0x4200bc1a
4200bbb8:	470d                	li	a4,3
4200bbba:	06e78763          	beq	a5,a4,0x4200bc28
4200bbbe:	4711                	li	a4,4
4200bbc0:	02e79363          	bne	a5,a4,0x4200bbe6
4200bbc4:	00264637          	lui	a2,0x264
4200bbc8:	4581                	li	a1,0
4200bbca:	4501                	li	a0,0
4200bbcc:	14d000ef          	jal	0x4200c518
4200bbd0:	a819                	j	0x4200bbe6
4200bbd2:	4501                	li	a0,0
4200bbd4:	e37fd0ef          	jal	0x42009a0a
4200bbd8:	a03d                	j	0x4200bc06
4200bbda:	00200637          	lui	a2,0x200
4200bbde:	4581                	li	a1,0
4200bbe0:	4501                	li	a0,0
4200bbe2:	137000ef          	jal	0x4200c518
4200bbe6:	3fcc4737          	lui	a4,0x3fcc4
4200bbea:	a5174783          	lbu	a5,-1455(a4) # 0x3fcc3a51
4200bbee:	0785                	addi	a5,a5,1
4200bbf0:	0ff7f793          	zext.b	a5,a5
4200bbf4:	a4f708a3          	sb	a5,-1455(a4)
4200bbf8:	4711                	li	a4,4
4200bbfa:	00f77663          	bgeu	a4,a5,0x4200bc06
4200bbfe:	3fcc47b7          	lui	a5,0x3fcc4
4200bc02:	a40788a3          	sb	zero,-1455(a5) # 0x3fcc3a51
4200bc06:	40b2                	lw	ra,12(sp)
4200bc08:	0141                	addi	sp,sp,16
4200bc0a:	8082                	ret
4200bc0c:	00219637          	lui	a2,0x219
4200bc10:	4581                	li	a1,0
4200bc12:	4501                	li	a0,0
4200bc14:	105000ef          	jal	0x4200c518
4200bc18:	b7f9                	j	0x4200bbe6
4200bc1a:	00232637          	lui	a2,0x232
4200bc1e:	4581                	li	a1,0
4200bc20:	4501                	li	a0,0
4200bc22:	0f7000ef          	jal	0x4200c518
4200bc26:	b7c1                	j	0x4200bbe6
4200bc28:	0024b637          	lui	a2,0x24b
4200bc2c:	4581                	li	a1,0
4200bc2e:	4501                	li	a0,0
4200bc30:	0e9000ef          	jal	0x4200c518
4200bc34:	bf4d                	j	0x4200bbe6
