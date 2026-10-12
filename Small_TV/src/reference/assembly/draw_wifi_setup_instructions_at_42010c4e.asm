
factory-irom.bin:     file format binary


Disassembly of section .data:

42010c4e <.data+0x10c2e>:
42010c4e:	7179                	addi	sp,sp,-48
42010c50:	d606                	sw	ra,44(sp)
42010c52:	3fcc47b7          	lui	a5,0x3fcc4
42010c56:	aba7c783          	lbu	a5,-1350(a5) # 0x3fcc3aba
42010c5a:	c781                	beqz	a5,0x42010c62
42010c5c:	50b2                	lw	ra,44(sp)
42010c5e:	6145                	addi	sp,sp,48
42010c60:	8082                	ret
42010c62:	3fcc47b7          	lui	a5,0x3fcc4
42010c66:	4705                	li	a4,1
42010c68:	aae78d23          	sb	a4,-1350(a5) # 0x3fcc3aba
42010c6c:	4501                	li	a0,0
42010c6e:	d9df80ef          	jal	0x42009a0a
42010c72:	0048                	addi	a0,sp,4
42010c74:	3c0c47b7          	lui	a5,0x3c0c4
42010c78:	4e478793          	addi	a5,a5,1252 # 0x3c0c44e4
42010c7c:	438c                	lw	a1,0(a5)
42010c7e:	43d0                	lw	a2,4(a5)
42010c80:	4794                	lw	a3,8(a5)
42010c82:	47d8                	lw	a4,12(a5)
42010c84:	c22e                	sw	a1,4(sp)
42010c86:	c150                	sw	a2,4(a0)
42010c88:	c514                	sw	a3,8(a0)
42010c8a:	c558                	sw	a4,12(a0)
42010c8c:	0107d783          	lhu	a5,16(a5)
42010c90:	00f51823          	sh	a5,16(a0)
42010c94:	fdff0097          	auipc	ra,0xfdff0
42010c98:	814080e7          	jalr	-2028(ra) # 0x400004a8
42010c9c:	0ff57513          	zext.b	a0,a0
42010ca0:	47d1                	li	a5,20
42010ca2:	20a7e863          	bltu	a5,a0,0x42010eb2
42010ca6:	c515                	beqz	a0,0x42010cd2
42010ca8:	00151793          	slli	a5,a0,0x1
42010cac:	97aa                	add	a5,a5,a0
42010cae:	078a                	slli	a5,a5,0x2
42010cb0:	0ff7f793          	zext.b	a5,a5
42010cb4:	0f000513          	li	a0,240
42010cb8:	8d1d                	sub	a0,a0,a5
42010cba:	8505                	srai	a0,a0,0x1
42010cbc:	4781                	li	a5,0
42010cbe:	6741                	lui	a4,0x10
42010cc0:	177d                	addi	a4,a4,-1 # 0xffff
42010cc2:	46e1                	li	a3,24
42010cc4:	0050                	addi	a2,sp,4
42010cc6:	02400593          	li	a1,36
42010cca:	0fe57513          	andi	a0,a0,254
42010cce:	f21f90ef          	jal	0x4200abee
42010cd2:	0048                	addi	a0,sp,4
42010cd4:	3c0c47b7          	lui	a5,0x3c0c4
42010cd8:	4f878793          	addi	a5,a5,1272 # 0x3c0c44f8
42010cdc:	4390                	lw	a2,0(a5)
42010cde:	43d4                	lw	a3,4(a5)
42010ce0:	4798                	lw	a4,8(a5)
42010ce2:	47dc                	lw	a5,12(a5)
42010ce4:	c232                	sw	a2,4(sp)
42010ce6:	c154                	sw	a3,4(a0)
42010ce8:	c518                	sw	a4,8(a0)
42010cea:	c55c                	sw	a5,12(a0)
42010cec:	fdfef097          	auipc	ra,0xfdfef
42010cf0:	7bc080e7          	jalr	1980(ra) # 0x400004a8
42010cf4:	0ff57513          	zext.b	a0,a0
42010cf8:	47d1                	li	a5,20
42010cfa:	1aa7ee63          	bltu	a5,a0,0x42010eb6
42010cfe:	c515                	beqz	a0,0x42010d2a
42010d00:	00151793          	slli	a5,a0,0x1
42010d04:	97aa                	add	a5,a5,a0
42010d06:	078a                	slli	a5,a5,0x2
42010d08:	0ff7f793          	zext.b	a5,a5
42010d0c:	0f000513          	li	a0,240
42010d10:	8d1d                	sub	a0,a0,a5
42010d12:	8505                	srai	a0,a0,0x1
42010d14:	4781                	li	a5,0
42010d16:	6741                	lui	a4,0x10
42010d18:	177d                	addi	a4,a4,-1 # 0xffff
42010d1a:	46e1                	li	a3,24
42010d1c:	0050                	addi	a2,sp,4
42010d1e:	04000593          	li	a1,64
42010d22:	0fe57513          	andi	a0,a0,254
42010d26:	ec9f90ef          	jal	0x4200abee
42010d2a:	0048                	addi	a0,sp,4
42010d2c:	3c0c47b7          	lui	a5,0x3c0c4
42010d30:	50878793          	addi	a5,a5,1288 # 0x3c0c4508
42010d34:	438c                	lw	a1,0(a5)
42010d36:	43d0                	lw	a2,4(a5)
42010d38:	4794                	lw	a3,8(a5)
42010d3a:	47d8                	lw	a4,12(a5)
42010d3c:	c22e                	sw	a1,4(sp)
42010d3e:	c150                	sw	a2,4(a0)
42010d40:	c514                	sw	a3,8(a0)
42010d42:	c558                	sw	a4,12(a0)
42010d44:	0107d703          	lhu	a4,16(a5)
42010d48:	00e51823          	sh	a4,16(a0)
42010d4c:	0127c783          	lbu	a5,18(a5)
42010d50:	00f50923          	sb	a5,18(a0)
42010d54:	fdfef097          	auipc	ra,0xfdfef
42010d58:	754080e7          	jalr	1876(ra) # 0x400004a8
42010d5c:	0ff57513          	zext.b	a0,a0
42010d60:	47d1                	li	a5,20
42010d62:	14a7ec63          	bltu	a5,a0,0x42010eba
42010d66:	c515                	beqz	a0,0x42010d92
42010d68:	00151793          	slli	a5,a0,0x1
42010d6c:	97aa                	add	a5,a5,a0
42010d6e:	078a                	slli	a5,a5,0x2
42010d70:	0ff7f793          	zext.b	a5,a5
42010d74:	0f000513          	li	a0,240
42010d78:	8d1d                	sub	a0,a0,a5
42010d7a:	8505                	srai	a0,a0,0x1
42010d7c:	4781                	li	a5,0
42010d7e:	6741                	lui	a4,0x10
42010d80:	177d                	addi	a4,a4,-1 # 0xffff
42010d82:	46e1                	li	a3,24
42010d84:	0050                	addi	a2,sp,4
42010d86:	05c00593          	li	a1,92
42010d8a:	0fe57513          	andi	a0,a0,254
42010d8e:	e61f90ef          	jal	0x4200abee
42010d92:	0048                	addi	a0,sp,4
42010d94:	6c6177b7          	lui	a5,0x6c617
42010d98:	d5378793          	addi	a5,a5,-685 # 0x6c616d53
42010d9c:	c23e                	sw	a5,4(sp)
42010d9e:	565467b7          	lui	a5,0x56546
42010da2:	f6c78793          	addi	a5,a5,-148 # 0x56545f6c
42010da6:	c15c                	sw	a5,4(a0)
42010da8:	00050423          	sb	zero,8(a0)
42010dac:	fdfef097          	auipc	ra,0xfdfef
42010db0:	6fc080e7          	jalr	1788(ra) # 0x400004a8
42010db4:	0ff57513          	zext.b	a0,a0
42010db8:	47d1                	li	a5,20
42010dba:	10a7e263          	bltu	a5,a0,0x42010ebe
42010dbe:	c515                	beqz	a0,0x42010dea
42010dc0:	00151793          	slli	a5,a0,0x1
42010dc4:	97aa                	add	a5,a5,a0
42010dc6:	078a                	slli	a5,a5,0x2
42010dc8:	0ff7f793          	zext.b	a5,a5
42010dcc:	0f000513          	li	a0,240
42010dd0:	8d1d                	sub	a0,a0,a5
42010dd2:	8505                	srai	a0,a0,0x1
42010dd4:	4781                	li	a5,0
42010dd6:	6741                	lui	a4,0x10
42010dd8:	1701                	addi	a4,a4,-32 # 0xffe0
42010dda:	46e1                	li	a3,24
42010ddc:	0050                	addi	a2,sp,4
42010dde:	07800593          	li	a1,120
42010de2:	0fe57513          	andi	a0,a0,254
42010de6:	e09f90ef          	jal	0x4200abee
42010dea:	0048                	addi	a0,sp,4
42010dec:	3c0c47b7          	lui	a5,0x3c0c4
42010df0:	51c78793          	addi	a5,a5,1308 # 0x3c0c451c
42010df4:	438c                	lw	a1,0(a5)
42010df6:	43d0                	lw	a2,4(a5)
42010df8:	4794                	lw	a3,8(a5)
42010dfa:	47d8                	lw	a4,12(a5)
42010dfc:	c22e                	sw	a1,4(sp)
42010dfe:	c150                	sw	a2,4(a0)
42010e00:	c514                	sw	a3,8(a0)
42010e02:	c558                	sw	a4,12(a0)
42010e04:	0107d703          	lhu	a4,16(a5)
42010e08:	00e51823          	sh	a4,16(a0)
42010e0c:	0127c783          	lbu	a5,18(a5)
42010e10:	00f50923          	sb	a5,18(a0)
42010e14:	fdfef097          	auipc	ra,0xfdfef
42010e18:	694080e7          	jalr	1684(ra) # 0x400004a8
42010e1c:	0ff57513          	zext.b	a0,a0
42010e20:	47d1                	li	a5,20
42010e22:	0aa7e063          	bltu	a5,a0,0x42010ec2
42010e26:	c515                	beqz	a0,0x42010e52
42010e28:	00151793          	slli	a5,a0,0x1
42010e2c:	97aa                	add	a5,a5,a0
42010e2e:	078a                	slli	a5,a5,0x2
42010e30:	0ff7f793          	zext.b	a5,a5
42010e34:	0f000513          	li	a0,240
42010e38:	8d1d                	sub	a0,a0,a5
42010e3a:	8505                	srai	a0,a0,0x1
42010e3c:	4781                	li	a5,0
42010e3e:	6741                	lui	a4,0x10
42010e40:	177d                	addi	a4,a4,-1 # 0xffff
42010e42:	46e1                	li	a3,24
42010e44:	0050                	addi	a2,sp,4
42010e46:	09400593          	li	a1,148
42010e4a:	0fe57513          	andi	a0,a0,254
42010e4e:	da1f90ef          	jal	0x4200abee
42010e52:	0048                	addi	a0,sp,4
42010e54:	3c0c37b7          	lui	a5,0x3c0c3
42010e58:	ae878793          	addi	a5,a5,-1304 # 0x3c0c2ae8
42010e5c:	4390                	lw	a2,0(a5)
42010e5e:	43d4                	lw	a3,4(a5)
42010e60:	4798                	lw	a4,8(a5)
42010e62:	c232                	sw	a2,4(sp)
42010e64:	c154                	sw	a3,4(a0)
42010e66:	c518                	sw	a4,8(a0)
42010e68:	00c7c783          	lbu	a5,12(a5)
42010e6c:	00f50623          	sb	a5,12(a0)
42010e70:	fdfef097          	auipc	ra,0xfdfef
42010e74:	638080e7          	jalr	1592(ra) # 0x400004a8
42010e78:	0ff57513          	zext.b	a0,a0
42010e7c:	47d1                	li	a5,20
42010e7e:	04a7e463          	bltu	a5,a0,0x42010ec6
42010e82:	dc050de3          	beqz	a0,0x42010c5c
42010e86:	00151793          	slli	a5,a0,0x1
42010e8a:	97aa                	add	a5,a5,a0
42010e8c:	078a                	slli	a5,a5,0x2
42010e8e:	0ff7f793          	zext.b	a5,a5
42010e92:	0f000513          	li	a0,240
42010e96:	8d1d                	sub	a0,a0,a5
42010e98:	8505                	srai	a0,a0,0x1
42010e9a:	4781                	li	a5,0
42010e9c:	6741                	lui	a4,0x10
42010e9e:	1701                	addi	a4,a4,-32 # 0xffe0
42010ea0:	46e1                	li	a3,24
42010ea2:	0050                	addi	a2,sp,4
42010ea4:	0b000593          	li	a1,176
42010ea8:	0fe57513          	andi	a0,a0,254
42010eac:	d43f90ef          	jal	0x4200abee
42010eb0:	b375                	j	0x42010c5c
42010eb2:	4551                	li	a0,20
42010eb4:	bbd5                	j	0x42010ca8
42010eb6:	4551                	li	a0,20
42010eb8:	b5a1                	j	0x42010d00
42010eba:	4551                	li	a0,20
42010ebc:	b575                	j	0x42010d68
42010ebe:	4551                	li	a0,20
42010ec0:	b701                	j	0x42010dc0
42010ec2:	4551                	li	a0,20
42010ec4:	b795                	j	0x42010e28
42010ec6:	4551                	li	a0,20
42010ec8:	bf7d                	j	0x42010e86
