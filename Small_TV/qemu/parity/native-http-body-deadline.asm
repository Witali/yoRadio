
small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42011d2a <reject_body.isra.0>:
42011d2a:	1141                	addi	sp,sp,-16
42011d2c:	c422                	sw	s0,8(sp)
42011d2e:	c606                	sw	ra,12(sp)
42011d30:	842e                	mv	s0,a1
42011d32:	5d1270ef          	jal	42039b02 <httpd_req_to_sockfd>
42011d36:	00054563          	bltz	a0,42011d40 <reject_body.isra.0+0x16>
42011d3a:	4581                	li	a1,0
42011d3c:	5560b0ef          	jal	4201d292 <lwip_shutdown>
42011d40:	8522                	mv	a0,s0
42011d42:	4422                	lw	s0,8(sp)
42011d44:	40b2                	lw	ra,12(sp)
42011d46:	0141                	addi	sp,sp,16
42011d48:	fe375317          	auipc	t1,0xfe375
42011d4c:	47a30067          	jr	1146(t1) # 403871c2 <cfree>

small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42011d50 <web_body>:
42011d50:	7141                	addi	sp,sp,-496
42011d52:	1e912223          	sw	s1,484(sp)
42011d56:	3c0b54b7          	lui	s1,0x3c0b5
42011d5a:	1f212023          	sw	s2,480(sp)
42011d5e:	892e                	mv	s2,a1
42011d60:	84448593          	addi	a1,s1,-1980 # 3c0b4844 <_esp_libc_clock_array_end+0x46f4>
42011d64:	1e812423          	sw	s0,488(sp)
42011d68:	1e112623          	sw	ra,492(sp)
42011d6c:	1d312e23          	sw	s3,476(sp)
42011d70:	1d412c23          	sw	s4,472(sp)
42011d74:	1d512a23          	sw	s5,468(sp)
42011d78:	1d612823          	sw	s6,464(sp)
42011d7c:	1d712623          	sw	s7,460(sp)
42011d80:	1d812423          	sw	s8,456(sp)
42011d84:	1d912223          	sw	s9,452(sp)
42011d88:	1da12023          	sw	s10,448(sp)
42011d8c:	842a                	mv	s0,a0
42011d8e:	4ad260ef          	jal	42038a3a <httpd_req_get_hdr_value_len>
42011d92:	c951                	beqz	a0,42011e26 <web_body+0xd6>
42011d94:	09f00793          	li	a5,159
42011d98:	02a7e663          	bltu	a5,a0,42011dc4 <web_body+0x74>
42011d9c:	0a000693          	li	a3,160
42011da0:	0110                	addi	a2,sp,128
42011da2:	84448593          	addi	a1,s1,-1980
42011da6:	8522                	mv	a0,s0
42011da8:	4bd260ef          	jal	42038a64 <httpd_req_get_hdr_value_str>
42011dac:	ed01                	bnez	a0,42011dc4 <web_body+0x74>
42011dae:	3c0b55b7          	lui	a1,0x3c0b5
42011db2:	08000693          	li	a3,128
42011db6:	860a                	mv	a2,sp
42011db8:	84c58593          	addi	a1,a1,-1972 # 3c0b484c <_esp_libc_clock_array_end+0x46fc>
42011dbc:	8522                	mv	a0,s0
42011dbe:	4a7260ef          	jal	42038a64 <httpd_req_get_hdr_value_str>
42011dc2:	c129                	beqz	a0,42011e04 <web_body+0xb4>
42011dc4:	4581                	li	a1,0
42011dc6:	8522                	mv	a0,s0
42011dc8:	f63ff0ef          	jal	42011d2a <reject_body.isra.0>
42011dcc:	4481                	li	s1,0
42011dce:	1ec12083          	lw	ra,492(sp)
42011dd2:	1e812403          	lw	s0,488(sp)
42011dd6:	1e012903          	lw	s2,480(sp)
42011dda:	1dc12983          	lw	s3,476(sp)
42011dde:	1d812a03          	lw	s4,472(sp)
42011de2:	1d412a83          	lw	s5,468(sp)
42011de6:	1d012b03          	lw	s6,464(sp)
42011dea:	1cc12b83          	lw	s7,460(sp)
42011dee:	1c812c03          	lw	s8,456(sp)
42011df2:	1c412c83          	lw	s9,452(sp)
42011df6:	1c012d03          	lw	s10,448(sp)
42011dfa:	8526                	mv	a0,s1
42011dfc:	1e412483          	lw	s1,484(sp)
42011e00:	617d                	addi	sp,sp,496
42011e02:	8082                	ret
42011e04:	3c0b5637          	lui	a2,0x3c0b5
42011e08:	0a000593          	li	a1,160
42011e0c:	868a                	mv	a3,sp
42011e0e:	85460613          	addi	a2,a2,-1964 # 3c0b4854 <_esp_libc_clock_array_end+0x4704>
42011e12:	1208                	addi	a0,sp,288
42011e14:	63a8c0ef          	jal	4209e44e <snprintf>
42011e18:	120c                	addi	a1,sp,288
42011e1a:	0108                	addi	a0,sp,128
42011e1c:	fe376097          	auipc	ra,0xfe376
42011e20:	836080e7          	jalr	-1994(ra) # 40387652 <strcmp>
42011e24:	f145                	bnez	a0,42011dc4 <web_body+0x74>
42011e26:	20c42783          	lw	a5,524(s0)
42011e2a:	17fd                	addi	a5,a5,-1
42011e2c:	f927fce3          	bgeu	a5,s2,42011dc4 <web_body+0x74>
42011e30:	8522                	mv	a0,s0
42011e32:	44c1                	li	s1,16
42011e34:	4cf270ef          	jal	42039b02 <httpd_req_to_sockfd>
42011e38:	c026                	sw	s1,0(sp)
42011e3a:	8baa                	mv	s7,a0
42011e3c:	f80544e3          	bltz	a0,42011dc4 <web_body+0x74>
42011e40:	6b05                	lui	s6,0x1
42011e42:	870a                	mv	a4,sp
42011e44:	0114                	addi	a3,sp,128
42011e46:	006b0613          	addi	a2,s6,6 # 1006 <CSR_UINTSTATUS+0x355>
42011e4a:	fffb0593          	addi	a1,s6,-1
42011e4e:	4e40b0ef          	jal	4201d332 <lwip_getsockopt>
42011e52:	f92d                	bnez	a0,42011dc4 <web_body+0x74>
42011e54:	4782                	lw	a5,0(sp)
42011e56:	f69797e3          	bne	a5,s1,42011dc4 <web_body+0x74>
42011e5a:	20c42503          	lw	a0,524(s0)
42011e5e:	0505                	addi	a0,a0,1
42011e60:	fe375097          	auipc	ra,0xfe375
42011e64:	35a080e7          	jalr	858(ra) # 403871ba <malloc>
42011e68:	84aa                	mv	s1,a0
42011e6a:	dd29                	beqz	a0,42011dc4 <web_body+0x74>
42011e6c:	004c5a37          	lui	s4,0x4c5
42011e70:	fe370097          	auipc	ra,0xfe370
42011e74:	d06080e7          	jalr	-762(ra) # 40381b76 <esp_timer_get_time>
42011e78:	b40a0a13          	addi	s4,s4,-1216 # 4c4b40 <CSR_UINTSTATUS+0x4c3e8f>
42011e7c:	9a2a                	add	s4,s4,a0
42011e7e:	00aa3533          	sltu	a0,s4,a0
42011e82:	00b509b3          	add	s3,a0,a1
42011e86:	4901                	li	s2,0
42011e88:	3e800a93          	li	s5,1000
42011e8c:	fffb0c13          	addi	s8,s6,-1
42011e90:	20c42783          	lw	a5,524(s0)
42011e94:	02f96063          	bltu	s2,a5,42011eb4 <web_body+0x164>
42011e98:	6605                	lui	a2,0x1
42011e9a:	6585                	lui	a1,0x1
42011e9c:	4741                	li	a4,16
42011e9e:	0114                	addi	a3,sp,128
42011ea0:	0619                	addi	a2,a2,6 # 1006 <CSR_UINTSTATUS+0x355>
42011ea2:	15fd                	addi	a1,a1,-1 # fff <CSR_UINTSTATUS+0x34e>
42011ea4:	855e                	mv	a0,s7
42011ea6:	52e0b0ef          	jal	4201d3d4 <lwip_setsockopt>
42011eaa:	e505                	bnez	a0,42011ed2 <web_body+0x182>
42011eac:	9926                	add	s2,s2,s1
42011eae:	00090023          	sb	zero,0(s2)
42011eb2:	bf31                	j	42011dce <web_body+0x7e>
42011eb4:	fe370097          	auipc	ra,0xfe370
42011eb8:	cc2080e7          	jalr	-830(ra) # 40381b76 <esp_timer_get_time>
42011ebc:	40aa07b3          	sub	a5,s4,a0
42011ec0:	00fa3733          	sltu	a4,s4,a5
42011ec4:	40b985b3          	sub	a1,s3,a1
42011ec8:	8d99                	sub	a1,a1,a4
42011eca:	00b04663          	bgtz	a1,42011ed6 <web_body+0x186>
42011ece:	e191                	bnez	a1,42011ed2 <web_body+0x182>
42011ed0:	e399                	bnez	a5,42011ed6 <web_body+0x186>
42011ed2:	85a6                	mv	a1,s1
42011ed4:	bdcd                	j	42011dc6 <web_body+0x76>
42011ed6:	3e778513          	addi	a0,a5,999
42011eda:	00f537b3          	sltu	a5,a0,a5
42011ede:	95be                	add	a1,a1,a5
42011ee0:	3e800613          	li	a2,1000
42011ee4:	4681                	li	a3,0
42011ee6:	fdfef097          	auipc	ra,0xfdfef
42011eea:	a12080e7          	jalr	-1518(ra) # 400008f8 <__divdi3>
42011eee:	3e800613          	li	a2,1000
42011ef2:	4681                	li	a3,0
42011ef4:	8caa                	mv	s9,a0
42011ef6:	8d2e                	mv	s10,a1
42011ef8:	12012623          	sw	zero,300(sp)
42011efc:	fdfef097          	auipc	ra,0xfdfef
42011f00:	9fc080e7          	jalr	-1540(ra) # 400008f8 <__divdi3>
42011f04:	12a12023          	sw	a0,288(sp)
42011f08:	857d                	srai	a0,a0,0x1f
42011f0a:	12a12223          	sw	a0,292(sp)
42011f0e:	3e800613          	li	a2,1000
42011f12:	4681                	li	a3,0
42011f14:	8566                	mv	a0,s9
42011f16:	85ea                	mv	a1,s10
42011f18:	fdfef097          	auipc	ra,0xfdfef
42011f1c:	a68080e7          	jalr	-1432(ra) # 40000980 <__moddi3>
42011f20:	03550533          	mul	a0,a0,s5
42011f24:	6605                	lui	a2,0x1
42011f26:	4741                	li	a4,16
42011f28:	1214                	addi	a3,sp,288
42011f2a:	0619                	addi	a2,a2,6 # 1006 <CSR_UINTSTATUS+0x355>
42011f2c:	85e2                	mv	a1,s8
42011f2e:	12a12423          	sw	a0,296(sp)
42011f32:	855e                	mv	a0,s7
42011f34:	4a00b0ef          	jal	4201d3d4 <lwip_setsockopt>
42011f38:	fd49                	bnez	a0,42011ed2 <web_body+0x182>
42011f3a:	20c42603          	lw	a2,524(s0)
42011f3e:	012485b3          	add	a1,s1,s2
42011f42:	8522                	mv	a0,s0
42011f44:	41260633          	sub	a2,a2,s2
42011f48:	355270ef          	jal	42039a9c <httpd_req_recv>
42011f4c:	8b2a                	mv	s6,a0
42011f4e:	f8a052e3          	blez	a0,42011ed2 <web_body+0x182>
42011f52:	fe370097          	auipc	ra,0xfe370
42011f56:	c24080e7          	jalr	-988(ra) # 40381b76 <esp_timer_get_time>
42011f5a:	f6b9cce3          	blt	s3,a1,42011ed2 <web_body+0x182>
42011f5e:	01359463          	bne	a1,s3,42011f66 <web_body+0x216>
42011f62:	f6aa68e3          	bltu	s4,a0,42011ed2 <web_body+0x182>
42011f66:	995a                	add	s2,s2,s6
42011f68:	b725                	j	42011e90 <web_body+0x140>
