
factory-irom.bin:     file format binary


Disassembly of section .data:

4200bc36 <.data+0xbc16>:
4200bc36:	1141                	addi	sp,sp,-16
4200bc38:	c606                	sw	ra,12(sp)
4200bc3a:	3fcc47b7          	lui	a5,0x3fcc4
4200bc3e:	9f87c783          	lbu	a5,-1544(a5) # 0x3fcc39f8
4200bc42:	c3ad                	beqz	a5,0x4200bca4
4200bc44:	3fcc47b7          	lui	a5,0x3fcc4
4200bc48:	9d87c783          	lbu	a5,-1576(a5) # 0x3fcc39d8
4200bc4c:	efa1                	bnez	a5,0x4200bca4
4200bc4e:	3fcc47b7          	lui	a5,0x3fcc4
4200bc52:	a507c783          	lbu	a5,-1456(a5) # 0x3fcc3a50
4200bc56:	cf85                	beqz	a5,0x4200bc8e
4200bc58:	4705                	li	a4,1
4200bc5a:	04e78863          	beq	a5,a4,0x4200bcaa
4200bc5e:	4709                	li	a4,2
4200bc60:	06e78163          	beq	a5,a4,0x4200bcc2
4200bc64:	470d                	li	a4,3
4200bc66:	08e78863          	beq	a5,a4,0x4200bcf6
4200bc6a:	4711                	li	a4,4
4200bc6c:	0ae78163          	beq	a5,a4,0x4200bd0e
4200bc70:	4715                	li	a4,5
4200bc72:	02e79963          	bne	a5,a4,0x4200bca4
4200bc76:	4501                	li	a0,0
4200bc78:	f5bfc0ef          	jal	0x42008bd2
4200bc7c:	3fcc47b7          	lui	a5,0x3fcc4
4200bc80:	a4078823          	sb	zero,-1456(a5) # 0x3fcc3a50
4200bc84:	3fcc47b7          	lui	a5,0x3fcc4
4200bc88:	9e078c23          	sb	zero,-1544(a5) # 0x3fcc39f8
4200bc8c:	a821                	j	0x4200bca4
4200bc8e:	12c00513          	li	a0,300
4200bc92:	f41fc0ef          	jal	0x42008bd2
4200bc96:	3fcc4737          	lui	a4,0x3fcc4
4200bc9a:	a5074783          	lbu	a5,-1456(a4) # 0x3fcc3a50
4200bc9e:	0785                	addi	a5,a5,1
4200bca0:	a4f70823          	sb	a5,-1456(a4)
4200bca4:	40b2                	lw	ra,12(sp)
4200bca6:	0141                	addi	sp,sp,16
4200bca8:	8082                	ret
4200bcaa:	25800513          	li	a0,600
4200bcae:	f25fc0ef          	jal	0x42008bd2
4200bcb2:	3fcc4737          	lui	a4,0x3fcc4
4200bcb6:	a5074783          	lbu	a5,-1456(a4) # 0x3fcc3a50
4200bcba:	0785                	addi	a5,a5,1
4200bcbc:	a4f70823          	sb	a5,-1456(a4)
4200bcc0:	b7d5                	j	0x4200bca4
4200bcc2:	3e800513          	li	a0,1000
4200bcc6:	f0dfc0ef          	jal	0x42008bd2
4200bcca:	e83ff0ef          	jal	0x4200bb4c
4200bcce:	6741                	lui	a4,0x10
4200bcd0:	177d                	addi	a4,a4,-1 # 0xffff
4200bcd2:	46c1                	li	a3,16
4200bcd4:	3fcb8637          	lui	a2,0x3fcb8
4200bcd8:	b8460613          	addi	a2,a2,-1148 # 0x3fcb7b84
4200bcdc:	0e100593          	li	a1,225
4200bce0:	4515                	li	a0,5
4200bce2:	d3dfe0ef          	jal	0x4200aa1e
4200bce6:	3fcc4737          	lui	a4,0x3fcc4
4200bcea:	a5074783          	lbu	a5,-1456(a4) # 0x3fcc3a50
4200bcee:	0785                	addi	a5,a5,1
4200bcf0:	a4f70823          	sb	a5,-1456(a4)
4200bcf4:	bf45                	j	0x4200bca4
4200bcf6:	25800513          	li	a0,600
4200bcfa:	ed9fc0ef          	jal	0x42008bd2
4200bcfe:	3fcc4737          	lui	a4,0x3fcc4
4200bd02:	a5074783          	lbu	a5,-1456(a4) # 0x3fcc3a50
4200bd06:	0785                	addi	a5,a5,1
4200bd08:	a4f70823          	sb	a5,-1456(a4)
4200bd0c:	bf61                	j	0x4200bca4
4200bd0e:	12c00513          	li	a0,300
4200bd12:	ec1fc0ef          	jal	0x42008bd2
4200bd16:	3fcc4737          	lui	a4,0x3fcc4
4200bd1a:	a5074783          	lbu	a5,-1456(a4) # 0x3fcc3a50
4200bd1e:	0785                	addi	a5,a5,1
4200bd20:	a4f70823          	sb	a5,-1456(a4)
4200bd24:	b741                	j	0x4200bca4
