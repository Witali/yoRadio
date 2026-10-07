
idf\esp32c3-oled-native\build-rx-copy\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026e18 <__wrap_wlanif_input>:
42026e18:	4d5c                	lw	a5,28(a0)
42026e1a:	7139                	addi	sp,sp,-64
42026e1c:	d05a                	sw	s6,32(sp)
42026e1e:	ce5e                	sw	s7,28(sp)
42026e20:	de06                	sw	ra,60(sp)
42026e22:	8b36                	mv	s6,a3
42026e24:	8bbe                	mv	s7,a5
42026e26:	1e058e63          	beqz	a1,42027022 <__wrap_wlanif_input+0x20a>
42026e2a:	dc22                	sw	s0,56(sp)
42026e2c:	da26                	sw	s1,52(sp)
42026e2e:	03954703          	lbu	a4,57(a0)
42026e32:	67c1                	lui	a5,0x10
42026e34:	00f637b3          	sltu	a5,a2,a5
42026e38:	fff74713          	not	a4,a4
42026e3c:	8b05                	andi	a4,a4,1
42026e3e:	0017b793          	seqz	a5,a5
42026e42:	8fd9                	or	a5,a5,a4
42026e44:	84aa                	mv	s1,a0
42026e46:	8432                	mv	s0,a2
42026e48:	1c079b63          	bnez	a5,4202701e <__wrap_wlanif_input+0x206>
42026e4c:	d84a                	sw	s2,48(sp)
42026e4e:	892e                	mv	s2,a1
42026e50:	01041593          	slli	a1,s0,0x10
42026e54:	28000613          	li	a2,640
42026e58:	4501                	li	a0,0
42026e5a:	81c1                	srli	a1,a1,0x10
42026e5c:	d452                	sw	s4,40(sp)
42026e5e:	48d580ef          	jal	4207faea <pbuf_alloc>
42026e62:	8a2a                	mv	s4,a0
42026e64:	16050c63          	beqz	a0,42026fdc <__wrap_wlanif_input+0x1c4>
42026e68:	d256                	sw	s5,36(sp)
42026e6a:	cc62                	sw	s8,24(sp)
42026e6c:	ad7db0ef          	jal	42002942 <heap_caps_get_allocated_size>
42026e70:	08000793          	li	a5,128
42026e74:	0287f163          	bgeu	a5,s0,42026e96 <__wrap_wlanif_input+0x7e>
42026e78:	20000793          	li	a5,512
42026e7c:	1487fa63          	bgeu	a5,s0,42026fd0 <__wrap_wlanif_input+0x1b8>
42026e80:	48000793          	li	a5,1152
42026e84:	1887fa63          	bgeu	a5,s0,42027018 <__wrap_wlanif_input+0x200>
42026e88:	64000793          	li	a5,1600
42026e8c:	1487f563          	bgeu	a5,s0,42026fd6 <__wrap_wlanif_input+0x1be>
42026e90:	4c11                	li	s8,4
42026e92:	8ee2                	mv	t4,s8
42026e94:	a019                	j	42026e9a <__wrap_wlanif_input+0x82>
42026e96:	4c01                	li	s8,0
42026e98:	4e81                	li	t4,0
42026e9a:	c62a                	sw	a0,12(sp)
42026e9c:	c476                	sw	t4,8(sp)
42026e9e:	fe360097          	auipc	ra,0xfe360
42026ea2:	ea8080e7          	jalr	-344(ra) # 40386d46 <vPortEnterCritical>
42026ea6:	4ea2                	lw	t4,8(sp)
42026ea8:	3fc91ab7          	lui	s5,0x3fc91
42026eac:	23ca8a93          	addi	s5,s5,572 # 3fc9123c <s_counts>
42026eb0:	001e9e13          	slli	t3,t4,0x1
42026eb4:	01de07b3          	add	a5,t3,t4
42026eb8:	078a                	slli	a5,a5,0x2
42026eba:	97d6                	add	a5,a5,s5
42026ebc:	5bd4                	lw	a3,52(a5)
42026ebe:	004aa703          	lw	a4,4(s5)
42026ec2:	4532                	lw	a0,12(sp)
42026ec4:	0685                	addi	a3,a3,1
42026ec6:	dbd4                	sw	a3,52(a5)
42026ec8:	028aa683          	lw	a3,40(s5)
42026ecc:	00170793          	addi	a5,a4,1
42026ed0:	00faa223          	sw	a5,4(s5)
42026ed4:	0086f463          	bgeu	a3,s0,42026edc <__wrap_wlanif_input+0xc4>
42026ed8:	028aa423          	sw	s0,40(s5)
42026edc:	3fc917b7          	lui	a5,0x3fc91
42026ee0:	2ac78313          	addi	t1,a5,684 # 3fc912ac <s_owners>
42026ee4:	04000593          	li	a1,64
42026ee8:	869a                	mv	a3,t1
42026eea:	882e                	mv	a6,a1
42026eec:	4881                	li	a7,0
42026eee:	4701                	li	a4,0
42026ef0:	a039                	j	42026efe <__wrap_wlanif_input+0xe6>
42026ef2:	e211                	bnez	a2,42026ef6 <__wrap_wlanif_input+0xde>
42026ef4:	e7e9                	bnez	a5,42026fbe <__wrap_wlanif_input+0x1a6>
42026ef6:	0705                	addi	a4,a4,1
42026ef8:	06b1                	addi	a3,a3,12
42026efa:	01070e63          	beq	a4,a6,42026f16 <__wrap_wlanif_input+0xfe>
42026efe:	4290                	lw	a2,0(a3)
42026f00:	fc058793          	addi	a5,a1,-64
42026f04:	0017b793          	seqz	a5,a5
42026f08:	feca15e3          	bne	s4,a2,42026ef2 <__wrap_wlanif_input+0xda>
42026f0c:	0705                	addi	a4,a4,1
42026f0e:	4885                	li	a7,1
42026f10:	06b1                	addi	a3,a3,12
42026f12:	ff0716e3          	bne	a4,a6,42026efe <__wrap_wlanif_input+0xe6>
42026f16:	0a089763          	bnez	a7,42026fc4 <__wrap_wlanif_input+0x1ac>
42026f1a:	e7cd                	bnez	a5,42026fc4 <__wrap_wlanif_input+0x1ac>
42026f1c:	00159793          	slli	a5,a1,0x1
42026f20:	00caa703          	lw	a4,12(s5)
42026f24:	97ae                	add	a5,a5,a1
42026f26:	078a                	slli	a5,a5,0x2
42026f28:	979a                	add	a5,a5,t1
42026f2a:	010aa683          	lw	a3,16(s5)
42026f2e:	0007a423          	sw	zero,8(a5)
42026f32:	0705                	addi	a4,a4,1
42026f34:	0147a023          	sw	s4,0(a5)
42026f38:	c3c8                	sw	a0,4(a5)
42026f3a:	00879423          	sh	s0,8(a5)
42026f3e:	01878523          	sb	s8,10(a5)
42026f42:	00eaa623          	sw	a4,12(s5)
42026f46:	00e6f463          	bgeu	a3,a4,42026f4e <__wrap_wlanif_input+0x136>
42026f4a:	00eaa823          	sw	a4,16(s5)
42026f4e:	014aa703          	lw	a4,20(s5)
42026f52:	018aa783          	lw	a5,24(s5)
42026f56:	953a                	add	a0,a0,a4
42026f58:	00aaaa23          	sw	a0,20(s5)
42026f5c:	00a7f463          	bgeu	a5,a0,42026f64 <__wrap_wlanif_input+0x14c>
42026f60:	00aaac23          	sw	a0,24(s5)
42026f64:	01de07b3          	add	a5,t3,t4
42026f68:	078a                	slli	a5,a5,0x2
42026f6a:	97d6                	add	a5,a5,s5
42026f6c:	5f98                	lw	a4,56(a5)
42026f6e:	5fd4                	lw	a3,60(a5)
42026f70:	0705                	addi	a4,a4,1
42026f72:	df98                	sw	a4,56(a5)
42026f74:	00e6f363          	bgeu	a3,a4,42026f7a <__wrap_wlanif_input+0x162>
42026f78:	dfd8                	sw	a4,60(a5)
42026f7a:	fe360097          	auipc	ra,0xfe360
42026f7e:	e08080e7          	jalr	-504(ra) # 40386d82 <vPortExitCritical>
42026f82:	004a2503          	lw	a0,4(s4)
42026f86:	8622                	mv	a2,s0
42026f88:	85ca                	mv	a1,s2
42026f8a:	fe35f097          	auipc	ra,0xfe35f
42026f8e:	414080e7          	jalr	1044(ra) # 4038639e <memcpy>
42026f92:	85da                	mv	a1,s6
42026f94:	855e                	mv	a0,s7
42026f96:	12e680ef          	jal	4208f0c4 <esp_netif_free_rx_buffer>
42026f9a:	489c                	lw	a5,16(s1)
42026f9c:	85a6                	mv	a1,s1
42026f9e:	8552                	mv	a0,s4
42026fa0:	9782                	jalr	a5
42026fa2:	87aa                	mv	a5,a0
42026fa4:	4501                	li	a0,0
42026fa6:	e7d1                	bnez	a5,42027032 <__wrap_wlanif_input+0x21a>
42026fa8:	5462                	lw	s0,56(sp)
42026faa:	54d2                	lw	s1,52(sp)
42026fac:	5942                	lw	s2,48(sp)
42026fae:	5a22                	lw	s4,40(sp)
42026fb0:	5a92                	lw	s5,36(sp)
42026fb2:	4c62                	lw	s8,24(sp)
42026fb4:	50f2                	lw	ra,60(sp)
42026fb6:	5b02                	lw	s6,32(sp)
42026fb8:	4bf2                	lw	s7,28(sp)
42026fba:	6121                	addi	sp,sp,64
42026fbc:	8082                	ret
42026fbe:	4781                	li	a5,0
42026fc0:	85ba                	mv	a1,a4
42026fc2:	bf15                	j	42026ef6 <__wrap_wlanif_input+0xde>
42026fc4:	020aa783          	lw	a5,32(s5)
42026fc8:	0785                	addi	a5,a5,1
42026fca:	02faa023          	sw	a5,32(s5)
42026fce:	b775                	j	42026f7a <__wrap_wlanif_input+0x162>
42026fd0:	4c05                	li	s8,1
42026fd2:	8ee2                	mv	t4,s8
42026fd4:	b5d9                	j	42026e9a <__wrap_wlanif_input+0x82>
42026fd6:	4c0d                	li	s8,3
42026fd8:	8ee2                	mv	t4,s8
42026fda:	b5c1                	j	42026e9a <__wrap_wlanif_input+0x82>
42026fdc:	fe360097          	auipc	ra,0xfe360
42026fe0:	d6a080e7          	jalr	-662(ra) # 40386d46 <vPortEnterCritical>
42026fe4:	3fc917b7          	lui	a5,0x3fc91
42026fe8:	23c78793          	addi	a5,a5,572 # 3fc9123c <s_counts>
42026fec:	4fd8                	lw	a4,28(a5)
42026fee:	0705                	addi	a4,a4,1
42026ff0:	cfd8                	sw	a4,28(a5)
42026ff2:	fe360097          	auipc	ra,0xfe360
42026ff6:	d90080e7          	jalr	-624(ra) # 40386d82 <vPortExitCritical>
42026ffa:	855e                	mv	a0,s7
42026ffc:	85da                	mv	a1,s6
42026ffe:	0c6680ef          	jal	4208f0c4 <esp_netif_free_rx_buffer>
42027002:	50f2                	lw	ra,60(sp)
42027004:	5462                	lw	s0,56(sp)
42027006:	54d2                	lw	s1,52(sp)
42027008:	5942                	lw	s2,48(sp)
4202700a:	5a22                	lw	s4,40(sp)
4202700c:	5b02                	lw	s6,32(sp)
4202700e:	4bf2                	lw	s7,28(sp)
42027010:	10100513          	li	a0,257
42027014:	6121                	addi	sp,sp,64
42027016:	8082                	ret
42027018:	4c09                	li	s8,2
4202701a:	8ee2                	mv	t4,s8
4202701c:	bdbd                	j	42026e9a <__wrap_wlanif_input+0x82>
4202701e:	5462                	lw	s0,56(sp)
42027020:	54d2                	lw	s1,52(sp)
42027022:	000b0663          	beqz	s6,4202702e <__wrap_wlanif_input+0x216>
42027026:	85da                	mv	a1,s6
42027028:	855e                	mv	a0,s7
4202702a:	09a680ef          	jal	4208f0c4 <esp_netif_free_rx_buffer>
4202702e:	557d                	li	a0,-1
42027030:	b751                	j	42026fb4 <__wrap_wlanif_input+0x19c>
42027032:	fe360097          	auipc	ra,0xfe360
42027036:	d14080e7          	jalr	-748(ra) # 40386d46 <vPortEnterCritical>
4202703a:	024aa783          	lw	a5,36(s5)
4202703e:	0785                	addi	a5,a5,1
42027040:	02faa223          	sw	a5,36(s5)
42027044:	fe360097          	auipc	ra,0xfe360
42027048:	d3e080e7          	jalr	-706(ra) # 40386d82 <vPortExitCritical>
4202704c:	8552                	mv	a0,s4
4202704e:	177580ef          	jal	4207f9c4 <pbuf_free>
42027052:	557d                	li	a0,-1
42027054:	5462                	lw	s0,56(sp)
42027056:	54d2                	lw	s1,52(sp)
42027058:	5942                	lw	s2,48(sp)
4202705a:	5a22                	lw	s4,40(sp)
4202705c:	5a92                	lw	s5,36(sp)
4202705e:	4c62                	lw	s8,24(sp)
42027060:	bf91                	j	42026fb4 <__wrap_wlanif_input+0x19c>
