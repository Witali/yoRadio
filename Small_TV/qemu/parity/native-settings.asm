
small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200bf08 <settings_country_valid>:
4200bf08:	cd35                	beqz	a0,4200bf84 <settings_country_valid+0x7c>
4200bf0a:	4701                	li	a4,0
4200bf0c:	46d1                	li	a3,20
4200bf0e:	00e507b3          	add	a5,a0,a4
4200bf12:	0007c783          	lbu	a5,0(a5)
4200bf16:	e7a5                	bnez	a5,4200bf7e <settings_country_valid+0x76>
4200bf18:	001007b7          	lui	a5,0x100
4200bf1c:	078d                	addi	a5,a5,3 # 100003 <CSR_UINTSTATUS+0xff352>
4200bf1e:	00e7d7b3          	srl	a5,a5,a4
4200bf22:	8b85                	andi	a5,a5,1
4200bf24:	4681                	li	a3,0
4200bf26:	ebb1                	bnez	a5,4200bf7a <settings_country_valid+0x72>
4200bf28:	4689                	li	a3,2
4200bf2a:	00d70c63          	beq	a4,a3,4200bf42 <settings_country_valid+0x3a>
4200bf2e:	460d                	li	a2,3
4200bf30:	4681                	li	a3,0
4200bf32:	04c70463          	beq	a4,a2,4200bf7a <settings_country_valid+0x72>
4200bf36:	00254583          	lbu	a1,2(a0)
4200bf3a:	02d00613          	li	a2,45
4200bf3e:	02c59e63          	bne	a1,a2,4200bf7a <settings_country_valid+0x72>
4200bf42:	4589                	li	a1,2
4200bf44:	4865                	li	a6,25
4200bf46:	02b78663          	beq	a5,a1,4200bf72 <settings_country_valid+0x6a>
4200bf4a:	00f506b3          	add	a3,a0,a5
4200bf4e:	0006c683          	lbu	a3,0(a3)
4200bf52:	fdf6f613          	andi	a2,a3,-33
4200bf56:	fbf60613          	addi	a2,a2,-65
4200bf5a:	0ff67613          	zext.b	a2,a2
4200bf5e:	00c87a63          	bgeu	a6,a2,4200bf72 <settings_country_valid+0x6a>
4200bf62:	fd068693          	addi	a3,a3,-48
4200bf66:	00a6b693          	sltiu	a3,a3,10
4200bf6a:	ce89                	beqz	a3,4200bf84 <settings_country_valid+0x7c>
4200bf6c:	0037b693          	sltiu	a3,a5,3
4200bf70:	ea91                	bnez	a3,4200bf84 <settings_country_valid+0x7c>
4200bf72:	0785                	addi	a5,a5,1
4200bf74:	fce7e9e3          	bltu	a5,a4,4200bf46 <settings_country_valid+0x3e>
4200bf78:	4685                	li	a3,1
4200bf7a:	8536                	mv	a0,a3
4200bf7c:	8082                	ret
4200bf7e:	0705                	addi	a4,a4,1
4200bf80:	f8d717e3          	bne	a4,a3,4200bf0e <settings_country_valid+0x6>
4200bf84:	4681                	li	a3,0
4200bf86:	bfd5                	j	4200bf7a <settings_country_valid+0x72>


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200bf88 <settings_valid>:
4200bf88:	1141                	addi	sp,sp,-16
4200bf8a:	c226                	sw	s1,4(sp)
4200bf8c:	4104                	lw	s1,0(a0)
4200bf8e:	c606                	sw	ra,12(sp)
4200bf90:	c422                	sw	s0,8(sp)
4200bf92:	4789                	li	a5,2
4200bf94:	14f49663          	bne	s1,a5,4200c0e0 <settings_valid+0x158>
4200bf98:	842a                	mv	s0,a0
4200bf9a:	02100613          	li	a2,33
4200bf9e:	4581                	li	a1,0
4200bfa0:	0511                	addi	a0,a0,4
4200bfa2:	fdff4097          	auipc	ra,0xfdff4
4200bfa6:	55a080e7          	jalr	1370(ra) # 400004fc <memchr>
4200bfaa:	4781                	li	a5,0
4200bfac:	12050463          	beqz	a0,4200c0d4 <settings_valid+0x14c>
4200bfb0:	04100613          	li	a2,65
4200bfb4:	4581                	li	a1,0
4200bfb6:	02540513          	addi	a0,s0,37
4200bfba:	fdff4097          	auipc	ra,0xfdff4
4200bfbe:	542080e7          	jalr	1346(ra) # 400004fc <memchr>
4200bfc2:	4781                	li	a5,0
4200bfc4:	10050863          	beqz	a0,4200c0d4 <settings_valid+0x14c>
4200bfc8:	04100613          	li	a2,65
4200bfcc:	4581                	li	a1,0
4200bfce:	06640513          	addi	a0,s0,102
4200bfd2:	fdff4097          	auipc	ra,0xfdff4
4200bfd6:	52a080e7          	jalr	1322(ra) # 400004fc <memchr>
4200bfda:	4781                	li	a5,0
4200bfdc:	cd65                	beqz	a0,4200c0d4 <settings_valid+0x14c>
4200bfde:	04100613          	li	a2,65
4200bfe2:	4581                	li	a1,0
4200bfe4:	0bb40513          	addi	a0,s0,187
4200bfe8:	fdff4097          	auipc	ra,0xfdff4
4200bfec:	514080e7          	jalr	1300(ra) # 400004fc <memchr>
4200bff0:	4781                	li	a5,0
4200bff2:	c16d                	beqz	a0,4200c0d4 <settings_valid+0x14c>
4200bff4:	04100613          	li	a2,65
4200bff8:	4581                	li	a1,0
4200bffa:	0fc40513          	addi	a0,s0,252
4200bffe:	fdff4097          	auipc	ra,0xfdff4
4200c002:	4fe080e7          	jalr	1278(ra) # 400004fc <memchr>
4200c006:	4781                	li	a5,0
4200c008:	c571                	beqz	a0,4200c0d4 <settings_valid+0x14c>
4200c00a:	0a740513          	addi	a0,s0,167
4200c00e:	efbff0ef          	jal	4200bf08 <settings_country_valid>
4200c012:	87aa                	mv	a5,a0
4200c014:	c161                	beqz	a0,4200c0d4 <settings_valid+0x14c>
4200c016:	14844683          	lbu	a3,328(s0)
4200c01a:	470d                	li	a4,3
4200c01c:	0cd76263          	bltu	a4,a3,4200c0e0 <settings_valid+0x158>
4200c020:	14944683          	lbu	a3,329(s0)
4200c024:	4711                	li	a4,4
4200c026:	0ad76d63          	bltu	a4,a3,4200c0e0 <settings_valid+0x158>
4200c02a:	14a44703          	lbu	a4,330(s0)
4200c02e:	0ae4e963          	bltu	s1,a4,4200c0e0 <settings_valid+0x158>
4200c032:	14b44703          	lbu	a4,331(s0)
4200c036:	4695                	li	a3,5
4200c038:	1739                	addi	a4,a4,-18
4200c03a:	0ff77713          	zext.b	a4,a4
4200c03e:	0ae6e163          	bltu	a3,a4,4200c0e0 <settings_valid+0x158>
4200c042:	14c44703          	lbu	a4,332(s0)
4200c046:	469d                	li	a3,7
4200c048:	176d                	addi	a4,a4,-5
4200c04a:	0ff77713          	zext.b	a4,a4
4200c04e:	08e6e963          	bltu	a3,a4,4200c0e0 <settings_valid+0x158>
4200c052:	14d44703          	lbu	a4,333(s0)
4200c056:	03900693          	li	a3,57
4200c05a:	1775                	addi	a4,a4,-3
4200c05c:	0ff77713          	zext.b	a4,a4
4200c060:	08e6e063          	bltu	a3,a4,4200c0e0 <settings_valid+0x158>
4200c064:	13e45683          	lhu	a3,318(s0)
4200c068:	3e800713          	li	a4,1000
4200c06c:	06d76a63          	bltu	a4,a3,4200c0e0 <settings_valid+0x158>
4200c070:	14045683          	lhu	a3,320(s0)
4200c074:	06d76663          	bltu	a4,a3,4200c0e0 <settings_valid+0x158>
4200c078:	14e44683          	lbu	a3,334(s0)
4200c07c:	4705                	li	a4,1
4200c07e:	06d76163          	bltu	a4,a3,4200c0e0 <settings_valid+0x158>
4200c082:	14f44683          	lbu	a3,335(s0)
4200c086:	04d76d63          	bltu	a4,a3,4200c0e0 <settings_valid+0x158>
4200c08a:	15044683          	lbu	a3,336(s0)
4200c08e:	04d76963          	bltu	a4,a3,4200c0e0 <settings_valid+0x158>
4200c092:	15144683          	lbu	a3,337(s0)
4200c096:	04d76563          	bltu	a4,a3,4200c0e0 <settings_valid+0x158>
4200c09a:	15244683          	lbu	a3,338(s0)
4200c09e:	04d76163          	bltu	a4,a3,4200c0e0 <settings_valid+0x158>
4200c0a2:	15344683          	lbu	a3,339(s0)
4200c0a6:	4729                	li	a4,10
4200c0a8:	02d76c63          	bltu	a4,a3,4200c0e0 <settings_valid+0x158>
4200c0ac:	15444683          	lbu	a3,340(s0)
4200c0b0:	477d                	li	a4,31
4200c0b2:	02d76763          	bltu	a4,a3,4200c0e0 <settings_valid+0x158>
4200c0b6:	15544683          	lbu	a3,341(s0)
4200c0ba:	02d4e363          	bltu	s1,a3,4200c0e0 <settings_valid+0x158>
4200c0be:	15840713          	addi	a4,s0,344
4200c0c2:	66e5                	lui	a3,0x19
4200c0c4:	16c40413          	addi	s0,s0,364
4200c0c8:	4310                	lw	a2,0(a4)
4200c0ca:	00c6eb63          	bltu	a3,a2,4200c0e0 <settings_valid+0x158>
4200c0ce:	0711                	addi	a4,a4,4
4200c0d0:	fe871ce3          	bne	a4,s0,4200c0c8 <settings_valid+0x140>
4200c0d4:	40b2                	lw	ra,12(sp)
4200c0d6:	4422                	lw	s0,8(sp)
4200c0d8:	4492                	lw	s1,4(sp)
4200c0da:	853e                	mv	a0,a5
4200c0dc:	0141                	addi	sp,sp,16
4200c0de:	8082                	ret
4200c0e0:	4781                	li	a5,0
4200c0e2:	bfcd                	j	4200c0d4 <settings_valid+0x14c>


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200c21c <settings_init>:
4200c21c:	cb010113          	addi	sp,sp,-848
4200c220:	4505                	li	a0,1
4200c222:	34112623          	sw	ra,844(sp)
4200c226:	34812423          	sw	s0,840(sp)
4200c22a:	34912223          	sw	s1,836(sp)
4200c22e:	35212023          	sw	s2,832(sp)
4200c232:	33312e23          	sw	s3,828(sp)
4200c236:	33412c23          	sw	s4,824(sp)
4200c23a:	33512a23          	sw	s5,820(sp)
4200c23e:	0a6a00ef          	jal	420ac2e4 <xQueueCreateMutex>
4200c242:	3fcb47b7          	lui	a5,0x3fcb4
4200c246:	8ea7a623          	sw	a0,-1812(a5) # 3fcb38ec <settings_mutex>
4200c24a:	e50d                	bnez	a0,4200c274 <settings_init+0x58>
4200c24c:	10100493          	li	s1,257
4200c250:	34c12083          	lw	ra,844(sp)
4200c254:	34812403          	lw	s0,840(sp)
4200c258:	34012903          	lw	s2,832(sp)
4200c25c:	33c12983          	lw	s3,828(sp)
4200c260:	33812a03          	lw	s4,824(sp)
4200c264:	33412a83          	lw	s5,820(sp)
4200c268:	8526                	mv	a0,s1
4200c26a:	34412483          	lw	s1,836(sp)
4200c26e:	35010113          	addi	sp,sp,848
4200c272:	8082                	ret
4200c274:	3fcb4437          	lui	s0,0x3fcb4
4200c278:	3c0b4537          	lui	a0,0x3c0b4
4200c27c:	8e840613          	addi	a2,s0,-1816 # 3fcb38e8 <settings_store>
4200c280:	4585                	li	a1,1
4200c282:	8f850513          	addi	a0,a0,-1800 # 3c0b38f8 <_esp_libc_clock_array_end+0x37a8>
4200c286:	af0fa0ef          	jal	42006576 <nvs_open>
4200c28a:	84aa                	mv	s1,a0
4200c28c:	f171                	bnez	a0,4200c250 <settings_init+0x34>
4200c28e:	8e842503          	lw	a0,-1816(s0)
4200c292:	3c0b45b7          	lui	a1,0x3c0b4
4200c296:	3fcb4937          	lui	s2,0x3fcb4
4200c29a:	16c00a13          	li	s4,364
4200c29e:	0034                	addi	a3,sp,8
4200c2a0:	1ad0                	addi	a2,sp,372
4200c2a2:	97858593          	addi	a1,a1,-1672 # 3c0b3978 <_esp_libc_clock_array_end+0x3828>
4200c2a6:	8e090023          	sb	zero,-1824(s2) # 3fcb38e0 <dirty>
4200c2aa:	c452                	sw	s4,8(sp)
4200c2ac:	e0cfa0ef          	jal	420068b8 <nvs_get_blob>
4200c2b0:	3fcaf9b7          	lui	s3,0x3fcaf
4200c2b4:	c911                	beqz	a0,4200c2c8 <settings_init+0xac>
4200c2b6:	4401                	li	s0,0
4200c2b8:	5d098513          	addi	a0,s3,1488 # 3fcaf5d0 <current_settings>
4200c2bc:	b55ff0ef          	jal	4200be10 <defaults>
4200c2c0:	4785                	li	a5,1
4200c2c2:	8ef90023          	sb	a5,-1824(s2)
4200c2c6:	a035                	j	4200c2f2 <settings_init+0xd6>
4200c2c8:	4622                	lw	a2,8(sp)
4200c2ca:	0b461b63          	bne	a2,s4,4200c380 <settings_init+0x164>
4200c2ce:	17412703          	lw	a4,372(sp)
4200c2d2:	4789                	li	a5,2
4200c2d4:	fef711e3          	bne	a4,a5,4200c2b6 <settings_init+0x9a>
4200c2d8:	1acc                	addi	a1,sp,372
4200c2da:	5d098513          	addi	a0,s3,1488
4200c2de:	fe37b097          	auipc	ra,0xfe37b
4200c2e2:	f5c080e7          	jalr	-164(ra) # 4038723a <memcpy>
4200c2e6:	4401                	li	s0,0
4200c2e8:	5d098513          	addi	a0,s3,1488
4200c2ec:	c9dff0ef          	jal	4200bf88 <settings_valid>
4200c2f0:	d561                	beqz	a0,4200c2b8 <settings_init+0x9c>
4200c2f2:	1bc00693          	li	a3,444
4200c2f6:	003e7637          	lui	a2,0x3e7
4200c2fa:	1acc                	addi	a1,sp,372
4200c2fc:	4501                	li	a0,0
4200c2fe:	fe37d097          	auipc	ra,0xfe37d
4200c302:	5d8080e7          	jalr	1496(ra) # 403898d6 <esp_flash_read>
4200c306:	e11d                	bnez	a0,4200c32c <settings_init+0x110>
4200c308:	0028                	addi	a0,sp,8
4200c30a:	b07ff0ef          	jal	4200be10 <defaults>
4200c30e:	002c                	addi	a1,sp,8
4200c310:	1ac8                	addi	a0,sp,372
4200c312:	2659                	jal	4200c698 <factory_settings_decode>
4200c314:	cd01                	beqz	a0,4200c32c <settings_init+0x110>
4200c316:	16c00613          	li	a2,364
4200c31a:	002c                	addi	a1,sp,8
4200c31c:	5d098513          	addi	a0,s3,1488
4200c320:	fe37b097          	auipc	ra,0xfe37b
4200c324:	f1a080e7          	jalr	-230(ra) # 4038723a <memcpy>
4200c328:	8e890023          	sb	s0,-1824(s2)
4200c32c:	8e094783          	lbu	a5,-1824(s2)
4200c330:	8c5d                	or	s0,s0,a5
4200c332:	8e890023          	sb	s0,-1824(s2)
4200c336:	fe376097          	auipc	ra,0xfe376
4200c33a:	840080e7          	jalr	-1984(ra) # 40381b76 <esp_timer_get_time>
4200c33e:	3fcb47b7          	lui	a5,0x3fcb4
4200c342:	8d878793          	addi	a5,a5,-1832 # 3fcb38d8 <last_change_us>
4200c346:	4405                	li	s0,1
4200c348:	c388                	sw	a0,0(a5)
4200c34a:	c3cc                	sw	a1,4(a5)
4200c34c:	80000837          	lui	a6,0x80000
4200c350:	3fcb47b7          	lui	a5,0x3fcb4
4200c354:	6605                	lui	a2,0x1
4200c356:	3c0b45b7          	lui	a1,0x3c0b4
4200c35a:	4200c537          	lui	a0,0x4200c
4200c35e:	8e87a223          	sw	s0,-1820(a5) # 3fcb38e4 <generation>
4200c362:	187d                	addi	a6,a6,-1 # 7fffffff <SYSTEM+0x1ff3ffff>
4200c364:	4781                	li	a5,0
4200c366:	8722                	mv	a4,s0
4200c368:	4681                	li	a3,0
4200c36a:	80060613          	addi	a2,a2,-2048 # 800 <ALIGN_VECTOR_TABLE+0x700>
4200c36e:	76458593          	addi	a1,a1,1892 # 3c0b4764 <_esp_libc_clock_array_end+0x4614>
4200c372:	1a250513          	addi	a0,a0,418 # 4200c1a2 <persistence_task>
4200c376:	49ea10ef          	jal	420ad814 <xTaskCreatePinnedToCore>
4200c37a:	ec8519e3          	bne	a0,s0,4200c24c <settings_init+0x30>
4200c37e:	bdc9                	j	4200c250 <settings_init+0x34>
4200c380:	15800793          	li	a5,344
4200c384:	f2f619e3          	bne	a2,a5,4200c2b6 <settings_init+0x9a>
4200c388:	17412a83          	lw	s5,372(sp)
4200c38c:	4785                	li	a5,1
4200c38e:	f2fa94e3          	bne	s5,a5,4200c2b6 <settings_init+0x9a>
4200c392:	460d                	li	a2,3
4200c394:	4581                	li	a1,0
4200c396:	21b10513          	addi	a0,sp,539
4200c39a:	fdff4097          	auipc	ra,0xfdff4
4200c39e:	162080e7          	jalr	354(ra) # 400004fc <memchr>
4200c3a2:	f0050ae3          	beqz	a0,4200c2b6 <settings_init+0x9a>
4200c3a6:	5d098413          	addi	s0,s3,1488
4200c3aa:	8652                	mv	a2,s4
4200c3ac:	4581                	li	a1,0
4200c3ae:	8522                	mv	a0,s0
4200c3b0:	fdff4097          	auipc	ra,0xfdff4
4200c3b4:	0d8080e7          	jalr	216(ra) # 40000488 <memset>
4200c3b8:	02100613          	li	a2,33
4200c3bc:	1aac                	addi	a1,sp,376
4200c3be:	4a09                	li	s4,2
4200c3c0:	00440513          	addi	a0,s0,4
4200c3c4:	01442023          	sw	s4,0(s0)
4200c3c8:	fe37b097          	auipc	ra,0xfe37b
4200c3cc:	e72080e7          	jalr	-398(ra) # 4038723a <memcpy>
4200c3d0:	04100613          	li	a2,65
4200c3d4:	19910593          	addi	a1,sp,409
4200c3d8:	02540513          	addi	a0,s0,37
4200c3dc:	fe37b097          	auipc	ra,0xfe37b
4200c3e0:	e5e080e7          	jalr	-418(ra) # 4038723a <memcpy>
4200c3e4:	04100613          	li	a2,65
4200c3e8:	1da10593          	addi	a1,sp,474
4200c3ec:	06640513          	addi	a0,s0,102
4200c3f0:	fe37b097          	auipc	ra,0xfe37b
4200c3f4:	e4a080e7          	jalr	-438(ra) # 4038723a <memcpy>
4200c3f8:	21b15783          	lhu	a5,539(sp)
4200c3fc:	04100613          	li	a2,65
4200c400:	21e10593          	addi	a1,sp,542
4200c404:	0af413a3          	sh	a5,167(s0)
4200c408:	21d14783          	lbu	a5,541(sp)
4200c40c:	0bb40513          	addi	a0,s0,187
4200c410:	0af404a3          	sb	a5,169(s0)
4200c414:	fe37b097          	auipc	ra,0xfe37b
4200c418:	e26080e7          	jalr	-474(ra) # 4038723a <memcpy>
4200c41c:	04100613          	li	a2,65
4200c420:	25f10593          	addi	a1,sp,607
4200c424:	0fc40513          	addi	a0,s0,252
4200c428:	fe37b097          	auipc	ra,0xfe37b
4200c42c:	e12080e7          	jalr	-494(ra) # 4038723a <memcpy>
4200c430:	2a012783          	lw	a5,672(sp)
4200c434:	2aa12703          	lw	a4,682(sp)
4200c438:	12f42f23          	sw	a5,318(s0)
4200c43c:	2a412783          	lw	a5,676(sp)
4200c440:	14e42423          	sw	a4,328(s0)
4200c444:	2ae12703          	lw	a4,686(sp)
4200c448:	14f42123          	sw	a5,322(s0)
4200c44c:	2a815783          	lhu	a5,680(sp)
4200c450:	14e42623          	sw	a4,332(s0)
4200c454:	2b212703          	lw	a4,690(sp)
4200c458:	14f41323          	sh	a5,326(s0)
4200c45c:	2b614783          	lbu	a5,694(sp)
4200c460:	14e42823          	sw	a4,336(s0)
4200c464:	14f40a23          	sb	a5,340(s0)
4200c468:	2b714783          	lbu	a5,695(sp)
4200c46c:	e791                	bnez	a5,4200c478 <settings_init+0x25c>
4200c46e:	17814703          	lbu	a4,376(sp)
4200c472:	87d2                	mv	a5,s4
4200c474:	c311                	beqz	a4,4200c478 <settings_init+0x25c>
4200c476:	87d6                	mv	a5,s5
4200c478:	15840513          	addi	a0,s0,344
4200c47c:	4651                	li	a2,20
4200c47e:	1d2c                	addi	a1,sp,696
4200c480:	14f40aa3          	sb	a5,341(s0)
4200c484:	fe37b097          	auipc	ra,0xfe37b
4200c488:	db6080e7          	jalr	-586(ra) # 4038723a <memcpy>
4200c48c:	4405                	li	s0,1
4200c48e:	bda9                	j	4200c2e8 <settings_init+0xcc>


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200c698 <factory_settings_decode>:
4200c698:	4781                	li	a5,0
4200c69a:	0ff00693          	li	a3,255
4200c69e:	1bc00713          	li	a4,444
4200c6a2:	00f50633          	add	a2,a0,a5
4200c6a6:	00064603          	lbu	a2,0(a2)
4200c6aa:	00d61763          	bne	a2,a3,4200c6b8 <factory_settings_decode+0x20>
4200c6ae:	0785                	addi	a5,a5,1
4200c6b0:	fee799e3          	bne	a5,a4,4200c6a2 <factory_settings_decode+0xa>
4200c6b4:	4501                	li	a0,0
4200c6b6:	8082                	ret
4200c6b8:	7179                	addi	sp,sp,-48
4200c6ba:	d04a                	sw	s2,32(sp)
4200c6bc:	892e                	mv	s2,a1
4200c6be:	00450613          	addi	a2,a0,4
4200c6c2:	d422                	sw	s0,40(sp)
4200c6c4:	04100693          	li	a3,65
4200c6c8:	842a                	mv	s0,a0
4200c6ca:	02100593          	li	a1,33
4200c6ce:	00490513          	addi	a0,s2,4
4200c6d2:	d606                	sw	ra,44(sp)
4200c6d4:	d226                	sw	s1,36(sp)
4200c6d6:	ce4e                	sw	s3,28(sp)
4200c6d8:	f6bff0ef          	jal	4200c642 <read_string>
4200c6dc:	04100693          	li	a3,65
4200c6e0:	85b6                	mv	a1,a3
4200c6e2:	04540613          	addi	a2,s0,69
4200c6e6:	02590513          	addi	a0,s2,37
4200c6ea:	f59ff0ef          	jal	4200c642 <read_string>
4200c6ee:	04100693          	li	a3,65
4200c6f2:	08640613          	addi	a2,s0,134
4200c6f6:	85b6                	mv	a1,a3
4200c6f8:	0bb90513          	addi	a0,s2,187
4200c6fc:	f47ff0ef          	jal	4200c642 <read_string>
4200c700:	0c744783          	lbu	a5,199(s0)
4200c704:	0fd00713          	li	a4,253
4200c708:	17fd                	addi	a5,a5,-1
4200c70a:	0ff7f793          	zext.b	a5,a5
4200c70e:	02f76e63          	bltu	a4,a5,4200c74a <factory_settings_decode+0xb2>
4200c712:	4651                	li	a2,20
4200c714:	4581                	li	a1,0
4200c716:	0c740513          	addi	a0,s0,199
4200c71a:	fdff4097          	auipc	ra,0xfdff4
4200c71e:	de2080e7          	jalr	-542(ra) # 400004fc <memchr>
4200c722:	ed01                	bnez	a0,4200c73a <factory_settings_decode+0xa2>
4200c724:	4651                	li	a2,20
4200c726:	0ff00593          	li	a1,255
4200c72a:	0c740513          	addi	a0,s0,199
4200c72e:	fdff4097          	auipc	ra,0xfdff4
4200c732:	dce080e7          	jalr	-562(ra) # 400004fc <memchr>
4200c736:	1e050a63          	beqz	a0,4200c92a <factory_settings_decode+0x292>
4200c73a:	46d1                	li	a3,20
4200c73c:	0c740613          	addi	a2,s0,199
4200c740:	85b6                	mv	a1,a3
4200c742:	0a790513          	addi	a0,s2,167
4200c746:	efdff0ef          	jal	4200c642 <read_string>
4200c74a:	04100693          	li	a3,65
4200c74e:	85b6                	mv	a1,a3
4200c750:	0db40613          	addi	a2,s0,219
4200c754:	06690513          	addi	a0,s2,102
4200c758:	eebff0ef          	jal	4200c642 <read_string>
4200c75c:	04100693          	li	a3,65
4200c760:	85b6                	mv	a1,a3
4200c762:	11c40613          	addi	a2,s0,284
4200c766:	0fc90513          	addi	a0,s2,252
4200c76a:	ed9ff0ef          	jal	4200c642 <read_string>
4200c76e:	00494703          	lbu	a4,4(s2)
4200c772:	4689                	li	a3,2
4200c774:	4601                	li	a2,0
4200c776:	00173713          	seqz	a4,a4
4200c77a:	0705                	addi	a4,a4,1
4200c77c:	16000593          	li	a1,352
4200c780:	8522                	mv	a0,s0
4200c782:	eafff0ef          	jal	4200c630 <bounded>
4200c786:	14a90aa3          	sb	a0,341(s2)
4200c78a:	4701                	li	a4,0
4200c78c:	4691                	li	a3,4
4200c78e:	4601                	li	a2,0
4200c790:	16400593          	li	a1,356
4200c794:	8522                	mv	a0,s0
4200c796:	e9bff0ef          	jal	4200c630 <bounded>
4200c79a:	14a904a3          	sb	a0,329(s2)
4200c79e:	4701                	li	a4,0
4200c7a0:	468d                	li	a3,3
4200c7a2:	4601                	li	a2,0
4200c7a4:	16800593          	li	a1,360
4200c7a8:	8522                	mv	a0,s0
4200c7aa:	e87ff0ef          	jal	4200c630 <bounded>
4200c7ae:	14a90423          	sb	a0,328(s2)
4200c7b2:	4701                	li	a4,0
4200c7b4:	4685                	li	a3,1
4200c7b6:	4601                	li	a2,0
4200c7b8:	16c00593          	li	a1,364
4200c7bc:	8522                	mv	a0,s0
4200c7be:	e73ff0ef          	jal	4200c630 <bounded>
4200c7c2:	14a90723          	sb	a0,334(s2)
4200c7c6:	4701                	li	a4,0
4200c7c8:	4685                	li	a3,1
4200c7ca:	4601                	li	a2,0
4200c7cc:	17000593          	li	a1,368
4200c7d0:	8522                	mv	a0,s0
4200c7d2:	e5fff0ef          	jal	4200c630 <bounded>
4200c7d6:	14a907a3          	sb	a0,335(s2)
4200c7da:	4701                	li	a4,0
4200c7dc:	4685                	li	a3,1
4200c7de:	4601                	li	a2,0
4200c7e0:	17400593          	li	a1,372
4200c7e4:	8522                	mv	a0,s0
4200c7e6:	e4bff0ef          	jal	4200c630 <bounded>
4200c7ea:	14a90823          	sb	a0,336(s2)
4200c7ee:	4701                	li	a4,0
4200c7f0:	4685                	li	a3,1
4200c7f2:	4601                	li	a2,0
4200c7f4:	17800593          	li	a1,376
4200c7f8:	8522                	mv	a0,s0
4200c7fa:	e37ff0ef          	jal	4200c630 <bounded>
4200c7fe:	4709                	li	a4,2
4200c800:	86ba                	mv	a3,a4
4200c802:	14a908a3          	sb	a0,337(s2)
4200c806:	4601                	li	a2,0
4200c808:	17c00593          	li	a1,380
4200c80c:	8522                	mv	a0,s0
4200c80e:	e23ff0ef          	jal	4200c630 <bounded>
4200c812:	14a90523          	sb	a0,330(s2)
4200c816:	4701                	li	a4,0
4200c818:	3e800693          	li	a3,1000
4200c81c:	4601                	li	a2,0
4200c81e:	18000593          	li	a1,384
4200c822:	8522                	mv	a0,s0
4200c824:	e0dff0ef          	jal	4200c630 <bounded>
4200c828:	64c1                	lui	s1,0x10
4200c82a:	80048713          	addi	a4,s1,-2048 # f800 <CSR_UINTSTATUS+0xeb4f>
4200c82e:	fff48693          	addi	a3,s1,-1
4200c832:	12a91f23          	sh	a0,318(s2)
4200c836:	4601                	li	a2,0
4200c838:	18400593          	li	a1,388
4200c83c:	8522                	mv	a0,s0
4200c83e:	df3ff0ef          	jal	4200c630 <bounded>
4200c842:	fe048713          	addi	a4,s1,-32
4200c846:	fff48693          	addi	a3,s1,-1
4200c84a:	14a91123          	sh	a0,322(s2)
4200c84e:	4601                	li	a2,0
4200c850:	18800593          	li	a1,392
4200c854:	8522                	mv	a0,s0
4200c856:	ddbff0ef          	jal	4200c630 <bounded>
4200c85a:	fff48713          	addi	a4,s1,-1
4200c85e:	86ba                	mv	a3,a4
4200c860:	14a91223          	sh	a0,324(s2)
4200c864:	4601                	li	a2,0
4200c866:	18c00593          	li	a1,396
4200c86a:	8522                	mv	a0,s0
4200c86c:	dc5ff0ef          	jal	4200c630 <bounded>
4200c870:	14a91323          	sh	a0,326(s2)
4200c874:	4701                	li	a4,0
4200c876:	4685                	li	a3,1
4200c878:	4601                	li	a2,0
4200c87a:	19000593          	li	a1,400
4200c87e:	8522                	mv	a0,s0
4200c880:	db1ff0ef          	jal	4200c630 <bounded>
4200c884:	14a90923          	sb	a0,338(s2)
4200c888:	4759                	li	a4,22
4200c88a:	46dd                	li	a3,23
4200c88c:	4649                	li	a2,18
4200c88e:	19400593          	li	a1,404
4200c892:	8522                	mv	a0,s0
4200c894:	d9dff0ef          	jal	4200c630 <bounded>
4200c898:	14a905a3          	sb	a0,331(s2)
4200c89c:	4725                	li	a4,9
4200c89e:	46b1                	li	a3,12
4200c8a0:	4615                	li	a2,5
4200c8a2:	19800593          	li	a1,408
4200c8a6:	8522                	mv	a0,s0
4200c8a8:	d89ff0ef          	jal	4200c630 <bounded>
4200c8ac:	14a90623          	sb	a0,332(s2)
4200c8b0:	1f400713          	li	a4,500
4200c8b4:	3e800693          	li	a3,1000
4200c8b8:	4601                	li	a2,0
4200c8ba:	19c00593          	li	a1,412
4200c8be:	8522                	mv	a0,s0
4200c8c0:	d71ff0ef          	jal	4200c630 <bounded>
4200c8c4:	14a91023          	sh	a0,320(s2)
4200c8c8:	4715                	li	a4,5
4200c8ca:	03c00693          	li	a3,60
4200c8ce:	460d                	li	a2,3
4200c8d0:	1a000593          	li	a1,416
4200c8d4:	8522                	mv	a0,s0
4200c8d6:	d5bff0ef          	jal	4200c630 <bounded>
4200c8da:	477d                	li	a4,31
4200c8dc:	14a906a3          	sb	a0,333(s2)
4200c8e0:	1a400593          	li	a1,420
4200c8e4:	86ba                	mv	a3,a4
4200c8e6:	4601                	li	a2,0
4200c8e8:	8522                	mv	a0,s0
4200c8ea:	d47ff0ef          	jal	4200c630 <bounded>
4200c8ee:	14a90a23          	sb	a0,340(s2)
4200c8f2:	15890493          	addi	s1,s2,344
4200c8f6:	1a800593          	li	a1,424
4200c8fa:	1bc00993          	li	s3,444
4200c8fe:	4098                	lw	a4,0(s1)
4200c900:	66e5                	lui	a3,0x19
4200c902:	4601                	li	a2,0
4200c904:	8522                	mv	a0,s0
4200c906:	c62e                	sw	a1,12(sp)
4200c908:	d29ff0ef          	jal	4200c630 <bounded>
4200c90c:	45b2                	lw	a1,12(sp)
4200c90e:	c088                	sw	a0,0(s1)
4200c910:	0491                	addi	s1,s1,4
4200c912:	0591                	addi	a1,a1,4
4200c914:	ff3595e3          	bne	a1,s3,4200c8fe <factory_settings_decode+0x266>
4200c918:	5422                	lw	s0,40(sp)
4200c91a:	50b2                	lw	ra,44(sp)
4200c91c:	5492                	lw	s1,36(sp)
4200c91e:	49f2                	lw	s3,28(sp)
4200c920:	854a                	mv	a0,s2
4200c922:	5902                	lw	s2,32(sp)
4200c924:	6145                	addi	sp,sp,48
4200c926:	e62ff06f          	j	4200bf88 <settings_valid>
4200c92a:	50b2                	lw	ra,44(sp)
4200c92c:	5422                	lw	s0,40(sp)
4200c92e:	5492                	lw	s1,36(sp)
4200c930:	5902                	lw	s2,32(sp)
4200c932:	49f2                	lw	s3,28(sp)
4200c934:	4501                	li	a0,0
4200c936:	6145                	addi	sp,sp,48
4200c938:	8082                	ret


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200c93a <factory_settings_encode>:
4200c93a:	7119                	addi	sp,sp,-128
4200c93c:	daa6                	sw	s1,116(sp)
4200c93e:	84ae                	mv	s1,a1
4200c940:	1bc00613          	li	a2,444
4200c944:	dca2                	sw	s0,120(sp)
4200c946:	4581                	li	a1,0
4200c948:	842a                	mv	s0,a0
4200c94a:	8526                	mv	a0,s1
4200c94c:	de86                	sw	ra,124(sp)
4200c94e:	d8ca                	sw	s2,112(sp)
4200c950:	d6ce                	sw	s3,108(sp)
4200c952:	fdff4097          	auipc	ra,0xfdff4
4200c956:	b36080e7          	jalr	-1226(ra) # 40000488 <memset>
4200c95a:	15444583          	lbu	a1,340(s0)
4200c95e:	8526                	mv	a0,s1
4200c960:	16448913          	addi	s2,s1,356
4200c964:	cc9ff0ef          	jal	4200c62c <write32>
4200c968:	00440593          	addi	a1,s0,4
4200c96c:	852e                	mv	a0,a1
4200c96e:	c62e                	sw	a1,12(sp)
4200c970:	fdff4097          	auipc	ra,0xfdff4
4200c974:	b38080e7          	jalr	-1224(ra) # 400004a8 <strlen>
4200c978:	45b2                	lw	a1,12(sp)
4200c97a:	862a                	mv	a2,a0
4200c97c:	00448513          	addi	a0,s1,4
4200c980:	fe37b097          	auipc	ra,0xfe37b
4200c984:	8ba080e7          	jalr	-1862(ra) # 4038723a <memcpy>
4200c988:	02540593          	addi	a1,s0,37
4200c98c:	852e                	mv	a0,a1
4200c98e:	c62e                	sw	a1,12(sp)
4200c990:	fdff4097          	auipc	ra,0xfdff4
4200c994:	b18080e7          	jalr	-1256(ra) # 400004a8 <strlen>
4200c998:	45b2                	lw	a1,12(sp)
4200c99a:	862a                	mv	a2,a0
4200c99c:	04548513          	addi	a0,s1,69
4200c9a0:	fe37b097          	auipc	ra,0xfe37b
4200c9a4:	89a080e7          	jalr	-1894(ra) # 4038723a <memcpy>
4200c9a8:	0bb40593          	addi	a1,s0,187
4200c9ac:	852e                	mv	a0,a1
4200c9ae:	c62e                	sw	a1,12(sp)
4200c9b0:	fdff4097          	auipc	ra,0xfdff4
4200c9b4:	af8080e7          	jalr	-1288(ra) # 400004a8 <strlen>
4200c9b8:	45b2                	lw	a1,12(sp)
4200c9ba:	862a                	mv	a2,a0
4200c9bc:	08648513          	addi	a0,s1,134
4200c9c0:	fe37b097          	auipc	ra,0xfe37b
4200c9c4:	87a080e7          	jalr	-1926(ra) # 4038723a <memcpy>
4200c9c8:	0a740593          	addi	a1,s0,167
4200c9cc:	852e                	mv	a0,a1
4200c9ce:	c62e                	sw	a1,12(sp)
4200c9d0:	fdff4097          	auipc	ra,0xfdff4
4200c9d4:	ad8080e7          	jalr	-1320(ra) # 400004a8 <strlen>
4200c9d8:	45b2                	lw	a1,12(sp)
4200c9da:	862a                	mv	a2,a0
4200c9dc:	0c748513          	addi	a0,s1,199
4200c9e0:	fe37b097          	auipc	ra,0xfe37b
4200c9e4:	85a080e7          	jalr	-1958(ra) # 4038723a <memcpy>
4200c9e8:	06640593          	addi	a1,s0,102
4200c9ec:	852e                	mv	a0,a1
4200c9ee:	c62e                	sw	a1,12(sp)
4200c9f0:	fdff4097          	auipc	ra,0xfdff4
4200c9f4:	ab8080e7          	jalr	-1352(ra) # 400004a8 <strlen>
4200c9f8:	45b2                	lw	a1,12(sp)
4200c9fa:	862a                	mv	a2,a0
4200c9fc:	0db48513          	addi	a0,s1,219
4200ca00:	fe37b097          	auipc	ra,0xfe37b
4200ca04:	83a080e7          	jalr	-1990(ra) # 4038723a <memcpy>
4200ca08:	0fc40593          	addi	a1,s0,252
4200ca0c:	852e                	mv	a0,a1
4200ca0e:	c62e                	sw	a1,12(sp)
4200ca10:	fdff4097          	auipc	ra,0xfdff4
4200ca14:	a98080e7          	jalr	-1384(ra) # 400004a8 <strlen>
4200ca18:	45b2                	lw	a1,12(sp)
4200ca1a:	862a                	mv	a2,a0
4200ca1c:	11c48513          	addi	a0,s1,284
4200ca20:	fe37b097          	auipc	ra,0xfe37b
4200ca24:	81a080e7          	jalr	-2022(ra) # 4038723a <memcpy>
4200ca28:	15544583          	lbu	a1,341(s0)
4200ca2c:	16048513          	addi	a0,s1,352
4200ca30:	01c10993          	addi	s3,sp,28
4200ca34:	bf9ff0ef          	jal	4200c62c <write32>
4200ca38:	14944783          	lbu	a5,329(s0)
4200ca3c:	1a848493          	addi	s1,s1,424
4200ca40:	ce3e                	sw	a5,28(sp)
4200ca42:	14844783          	lbu	a5,328(s0)
4200ca46:	d03e                	sw	a5,32(sp)
4200ca48:	14e44783          	lbu	a5,334(s0)
4200ca4c:	d23e                	sw	a5,36(sp)
4200ca4e:	14f44783          	lbu	a5,335(s0)
4200ca52:	d43e                	sw	a5,40(sp)
4200ca54:	15044783          	lbu	a5,336(s0)
4200ca58:	d63e                	sw	a5,44(sp)
4200ca5a:	15144783          	lbu	a5,337(s0)
4200ca5e:	d83e                	sw	a5,48(sp)
4200ca60:	14a44783          	lbu	a5,330(s0)
4200ca64:	da3e                	sw	a5,52(sp)
4200ca66:	13e45783          	lhu	a5,318(s0)
4200ca6a:	dc3e                	sw	a5,56(sp)
4200ca6c:	14245783          	lhu	a5,322(s0)
4200ca70:	de3e                	sw	a5,60(sp)
4200ca72:	14445783          	lhu	a5,324(s0)
4200ca76:	c0be                	sw	a5,64(sp)
4200ca78:	14645783          	lhu	a5,326(s0)
4200ca7c:	c2be                	sw	a5,68(sp)
4200ca7e:	15244783          	lbu	a5,338(s0)
4200ca82:	c4be                	sw	a5,72(sp)
4200ca84:	14b44783          	lbu	a5,331(s0)
4200ca88:	c6be                	sw	a5,76(sp)
4200ca8a:	14c44783          	lbu	a5,332(s0)
4200ca8e:	c8be                	sw	a5,80(sp)
4200ca90:	14045783          	lhu	a5,320(s0)
4200ca94:	cabe                	sw	a5,84(sp)
4200ca96:	14d44783          	lbu	a5,333(s0)
4200ca9a:	ccbe                	sw	a5,88(sp)
4200ca9c:	15444783          	lbu	a5,340(s0)
4200caa0:	cebe                	sw	a5,92(sp)
4200caa2:	0009a583          	lw	a1,0(s3)
4200caa6:	854a                	mv	a0,s2
4200caa8:	0911                	addi	s2,s2,4
4200caaa:	b83ff0ef          	jal	4200c62c <write32>
4200caae:	0991                	addi	s3,s3,4
4200cab0:	fe9919e3          	bne	s2,s1,4200caa2 <factory_settings_encode+0x168>
4200cab4:	15840913          	addi	s2,s0,344
4200cab8:	16c40413          	addi	s0,s0,364
4200cabc:	00092583          	lw	a1,0(s2)
4200cac0:	8526                	mv	a0,s1
4200cac2:	0911                	addi	s2,s2,4
4200cac4:	b69ff0ef          	jal	4200c62c <write32>
4200cac8:	0491                	addi	s1,s1,4
4200caca:	fe8919e3          	bne	s2,s0,4200cabc <factory_settings_encode+0x182>
4200cace:	50f6                	lw	ra,124(sp)
4200cad0:	5466                	lw	s0,120(sp)
4200cad2:	54d6                	lw	s1,116(sp)
4200cad4:	5946                	lw	s2,112(sp)
4200cad6:	59b6                	lw	s3,108(sp)
4200cad8:	6109                	addi	sp,sp,128
4200cada:	8082                	ret


small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42011e68 <web_settings_post>:
42011e68:	7101                	addi	sp,sp,-512
42011e6a:	1e912a23          	sw	s1,500(sp)
42011e6e:	84aa                	mv	s1,a0
42011e70:	18c8                	addi	a0,sp,116
42011e72:	1e112e23          	sw	ra,508(sp)
42011e76:	1e812c23          	sw	s0,504(sp)
42011e7a:	1f212823          	sw	s2,496(sp)
42011e7e:	1f312623          	sw	s3,492(sp)
42011e82:	1f412423          	sw	s4,488(sp)
42011e86:	1f512223          	sw	s5,484(sp)
42011e8a:	e06fa0ef          	jal	4200c490 <settings_snapshot>
42011e8e:	3c0b45b7          	lui	a1,0x3c0b4
42011e92:	65058593          	addi	a1,a1,1616 # 3c0b4650 <_esp_libc_clock_array_end+0x4500>
42011e96:	00848513          	addi	a0,s1,8
42011e9a:	fe375097          	auipc	ra,0xfe375
42011e9e:	7b8080e7          	jalr	1976(ra) # 40387652 <strcmp>
42011ea2:	ed21                	bnez	a0,42011efa <web_settings_post+0x92>
42011ea4:	20c4a783          	lw	a5,524(s1)
42011ea8:	c3b9                	beqz	a5,42011eee <web_settings_post+0x86>
42011eaa:	08000593          	li	a1,128
42011eae:	8526                	mv	a0,s1
42011eb0:	9b7ff0ef          	jal	42011866 <web_body>
42011eb4:	e90d                	bnez	a0,42011ee6 <web_settings_post+0x7e>
42011eb6:	3c0b55b7          	lui	a1,0x3c0b5
42011eba:	88858593          	addi	a1,a1,-1912 # 3c0b4888 <_esp_libc_clock_array_end+0x4738>
42011ebe:	8526                	mv	a0,s1
42011ec0:	8d9ff0ef          	jal	42011798 <web_error>
42011ec4:	1fc12083          	lw	ra,508(sp)
42011ec8:	1f812403          	lw	s0,504(sp)
42011ecc:	1f412483          	lw	s1,500(sp)
42011ed0:	1f012903          	lw	s2,496(sp)
42011ed4:	1ec12983          	lw	s3,492(sp)
42011ed8:	1e812a03          	lw	s4,488(sp)
42011edc:	1e412a83          	lw	s5,484(sp)
42011ee0:	20010113          	addi	sp,sp,512
42011ee4:	8082                	ret
42011ee6:	fe375097          	auipc	ra,0xfe375
42011eea:	2dc080e7          	jalr	732(ra) # 403871c2 <cfree>
42011eee:	c14fe0ef          	jal	42010302 <network_restart_later>
42011ef2:	8526                	mv	a0,s1
42011ef4:	8ddff0ef          	jal	420117d0 <web_ok>
42011ef8:	b7f1                	j	42011ec4 <web_settings_post+0x5c>
42011efa:	3c0b45b7          	lui	a1,0x3c0b4
42011efe:	70458593          	addi	a1,a1,1796 # 3c0b4704 <_esp_libc_clock_array_end+0x45b4>
42011f02:	00848513          	addi	a0,s1,8
42011f06:	fe375097          	auipc	ra,0xfe375
42011f0a:	74c080e7          	jalr	1868(ra) # 40387652 <strcmp>
42011f0e:	89aa                	mv	s3,a0
42011f10:	c55d                	beqz	a0,42011fbe <web_settings_post+0x156>
42011f12:	3c0b45b7          	lui	a1,0x3c0b4
42011f16:	6ac58593          	addi	a1,a1,1708 # 3c0b46ac <_esp_libc_clock_array_end+0x455c>
42011f1a:	00848513          	addi	a0,s1,8
42011f1e:	fe375097          	auipc	ra,0xfe375
42011f22:	734080e7          	jalr	1844(ra) # 40387652 <strcmp>
42011f26:	0e051663          	bnez	a0,42012012 <web_settings_post+0x1aa>
42011f2a:	3c0b5937          	lui	s2,0x3c0b5
42011f2e:	87890913          	addi	s2,s2,-1928 # 3c0b4878 <_esp_libc_clock_array_end+0x4728>
42011f32:	08000593          	li	a1,128
42011f36:	8526                	mv	a0,s1
42011f38:	92fff0ef          	jal	42011866 <web_body>
42011f3c:	8a2a                	mv	s4,a0
42011f3e:	20050f63          	beqz	a0,4201215c <web_settings_post+0x2f4>
42011f42:	20c4a603          	lw	a2,524(s1)
42011f46:	4581                	li	a1,0
42011f48:	fdfee097          	auipc	ra,0xfdfee
42011f4c:	5b4080e7          	jalr	1460(ra) # 400004fc <memchr>
42011f50:	cd25                	beqz	a0,42011fc8 <web_settings_post+0x160>
42011f52:	4901                	li	s2,0
42011f54:	8552                	mv	a0,s4
42011f56:	fe375097          	auipc	ra,0xfe375
42011f5a:	26c080e7          	jalr	620(ra) # 403871c2 <cfree>
42011f5e:	1e090f63          	beqz	s2,4201215c <web_settings_post+0x2f4>
42011f62:	47a9                	li	a5,10
42011f64:	02f40433          	mul	s0,s0,a5
42011f68:	3e800793          	li	a5,1000
42011f6c:	40878433          	sub	s0,a5,s0
42011f70:	08099e63          	bnez	s3,4201200c <web_settings_post+0x1a4>
42011f74:	1a811923          	sh	s0,434(sp)
42011f78:	4981                	li	s3,0
42011f7a:	4901                	li	s2,0
42011f7c:	18c8                	addi	a0,sp,116
42011f7e:	d56fa0ef          	jal	4200c4d4 <settings_replace>
42011f82:	1c051d63          	bnez	a0,4201215c <web_settings_post+0x2f4>
42011f86:	00098463          	beqz	s3,42011f8e <web_settings_post+0x126>
42011f8a:	9e0ff0ef          	jal	4201116a <weather_request_update>
42011f8e:	00090463          	beqz	s2,42011f96 <web_settings_post+0x12e>
42011f92:	b70fe0ef          	jal	42010302 <network_restart_later>
42011f96:	3c0b45b7          	lui	a1,0x3c0b4
42011f9a:	64058593          	addi	a1,a1,1600 # 3c0b4640 <_esp_libc_clock_array_end+0x44f0>
42011f9e:	00848513          	addi	a0,s1,8
42011fa2:	fe375097          	auipc	ra,0xfe375
42011fa6:	6b0080e7          	jalr	1712(ra) # 40387652 <strcmp>
42011faa:	f521                	bnez	a0,42011ef2 <web_settings_post+0x8a>
42011fac:	3c0b55b7          	lui	a1,0x3c0b5
42011fb0:	567d                	li	a2,-1
42011fb2:	93c58593          	addi	a1,a1,-1732 # 3c0b493c <_esp_libc_clock_array_end+0x47ec>
42011fb6:	8526                	mv	a0,s1
42011fb8:	040270ef          	jal	42038ff8 <httpd_resp_send>
42011fbc:	b721                	j	42011ec4 <web_settings_post+0x5c>
42011fbe:	3c0b5937          	lui	s2,0x3c0b5
42011fc2:	86890913          	addi	s2,s2,-1944 # 3c0b4868 <_esp_libc_clock_array_end+0x4718>
42011fc6:	b7b5                	j	42011f32 <web_settings_post+0xca>
42011fc8:	46a1                	li	a3,8
42011fca:	0870                	addi	a2,sp,28
42011fcc:	85ca                	mv	a1,s2
42011fce:	8552                	mv	a0,s4
42011fd0:	520260ef          	jal	420384f0 <httpd_query_key_value>
42011fd4:	fd3d                	bnez	a0,42011f52 <web_settings_post+0xea>
42011fd6:	01c14783          	lbu	a5,28(sp)
42011fda:	dfa5                	beqz	a5,42011f52 <web_settings_post+0xea>
42011fdc:	0878                	addi	a4,sp,28
42011fde:	4905                	li	s2,1
42011fe0:	a801                	j	42011ff0 <web_settings_post+0x188>
42011fe2:	fd078793          	addi	a5,a5,-48
42011fe6:	00a7b793          	sltiu	a5,a5,10
42011fea:	00f97933          	and	s2,s2,a5
42011fee:	0705                	addi	a4,a4,1
42011ff0:	00074783          	lbu	a5,0(a4)
42011ff4:	f7fd                	bnez	a5,42011fe2 <web_settings_post+0x17a>
42011ff6:	4629                	li	a2,10
42011ff8:	4581                	li	a1,0
42011ffa:	0868                	addi	a0,sp,28
42011ffc:	46c8c0ef          	jal	4209e468 <strtoul>
42012000:	06553793          	sltiu	a5,a0,101
42012004:	842a                	mv	s0,a0
42012006:	00f97933          	and	s2,s2,a5
4201200a:	b7a9                	j	42011f54 <web_settings_post+0xec>
4201200c:	1a811a23          	sh	s0,436(sp)
42012010:	b7a5                	j	42011f78 <web_settings_post+0x110>
42012012:	8526                	mv	a0,s1
42012014:	953ff0ef          	jal	42011966 <web_parse_json>
42012018:	8a2a                	mv	s4,a0
4201201a:	e511                	bnez	a0,42012026 <web_settings_post+0x1be>
4201201c:	3c0b55b7          	lui	a1,0x3c0b5
42012020:	89858593          	addi	a1,a1,-1896 # 3c0b4898 <_esp_libc_clock_array_end+0x4748>
42012024:	bd69                	j	42011ebe <web_settings_post+0x56>
42012026:	3c0eb937          	lui	s2,0x3c0eb
4201202a:	54490913          	addi	s2,s2,1348 # 3c0eb544 <integers>
4201202e:	09090993          	addi	s3,s2,144
42012032:	4401                	li	s0,0
42012034:	00492583          	lw	a1,4(s2)
42012038:	00848513          	addi	a0,s1,8
4201203c:	fe375097          	auipc	ra,0xfe375
42012040:	616080e7          	jalr	1558(ra) # 40387652 <strcmp>
42012044:	e515                	bnez	a0,42012070 <web_settings_post+0x208>
42012046:	01492683          	lw	a3,20(s2)
4201204a:	01092603          	lw	a2,16(s2)
4201204e:	00892583          	lw	a1,8(s2)
42012052:	0878                	addi	a4,sp,28
42012054:	8552                	mv	a0,s4
42012056:	95dff0ef          	jal	420119b2 <web_integer>
4201205a:	842a                	mv	s0,a0
4201205c:	c911                	beqz	a0,42012070 <web_settings_post+0x208>
4201205e:	00c92783          	lw	a5,12(s2)
42012062:	0818                	addi	a4,sp,16
42012064:	1d078793          	addi	a5,a5,464
42012068:	97ba                	add	a5,a5,a4
4201206a:	4772                	lw	a4,28(sp)
4201206c:	e8e78a23          	sb	a4,-364(a5)
42012070:	0961                	addi	s2,s2,24
42012072:	fd3911e3          	bne	s2,s3,42012034 <web_settings_post+0x1cc>
42012076:	3c0b45b7          	lui	a1,0x3c0b4
4201207a:	77058593          	addi	a1,a1,1904 # 3c0b4770 <_esp_libc_clock_array_end+0x4620>
4201207e:	00848513          	addi	a0,s1,8
42012082:	fe375097          	auipc	ra,0xfe375
42012086:	5d0080e7          	jalr	1488(ra) # 40387652 <strcmp>
4201208a:	e531                	bnez	a0,420120d6 <web_settings_post+0x26e>
4201208c:	3c0eb937          	lui	s2,0x3c0eb
42012090:	51c90913          	addi	s2,s2,1308 # 3c0eb51c <switches>
42012094:	02890993          	addi	s3,s2,40
42012098:	4401                	li	s0,0
4201209a:	00092583          	lw	a1,0(s2)
4201209e:	8552                	mv	a0,s4
420120a0:	c62e                	sw	a1,12(sp)
420120a2:	43b020ef          	jal	42014cdc <cJSON_HasObjectItem>
420120a6:	45b2                	lw	a1,12(sp)
420120a8:	c115                	beqz	a0,420120cc <web_settings_post+0x264>
420120aa:	0878                	addi	a4,sp,28
420120ac:	4685                	li	a3,1
420120ae:	4601                	li	a2,0
420120b0:	8552                	mv	a0,s4
420120b2:	901ff0ef          	jal	420119b2 <web_integer>
420120b6:	842a                	mv	s0,a0
420120b8:	cd09                	beqz	a0,420120d2 <web_settings_post+0x26a>
420120ba:	00492783          	lw	a5,4(s2)
420120be:	0818                	addi	a4,sp,16
420120c0:	1d078793          	addi	a5,a5,464
420120c4:	97ba                	add	a5,a5,a4
420120c6:	4772                	lw	a4,28(sp)
420120c8:	e8e78a23          	sb	a4,-364(a5)
420120cc:	0921                	addi	s2,s2,8
420120ce:	fd2996e3          	bne	s3,s2,4201209a <web_settings_post+0x232>
420120d2:	4981                	li	s3,0
420120d4:	a219                	j	420121da <web_settings_post+0x372>
420120d6:	3c0b45b7          	lui	a1,0x3c0b4
420120da:	7c458593          	addi	a1,a1,1988 # 3c0b47c4 <_esp_libc_clock_array_end+0x4674>
420120de:	00848513          	addi	a0,s1,8
420120e2:	fe375097          	auipc	ra,0xfe375
420120e6:	570080e7          	jalr	1392(ra) # 40387652 <strcmp>
420120ea:	cd01                	beqz	a0,42012102 <web_settings_post+0x29a>
420120ec:	3c0b45b7          	lui	a1,0x3c0b4
420120f0:	63458593          	addi	a1,a1,1588 # 3c0b4634 <_esp_libc_clock_array_end+0x44e4>
420120f4:	00848513          	addi	a0,s1,8
420120f8:	fe375097          	auipc	ra,0xfe375
420120fc:	55a080e7          	jalr	1370(ra) # 40387652 <strcmp>
42012100:	e92d                	bnez	a0,42012172 <web_settings_post+0x30a>
42012102:	3c0bf5b7          	lui	a1,0x3c0bf
42012106:	02100693          	li	a3,33
4201210a:	18b0                	addi	a2,sp,120
4201210c:	1e058593          	addi	a1,a1,480 # 3c0bf1e0 <_esp_libc_clock_array_end+0xf090>
42012110:	8552                	mv	a0,s4
42012112:	ab3ff0ef          	jal	42011bc4 <copy_string>
42012116:	c91d                	beqz	a0,4201214c <web_settings_post+0x2e4>
42012118:	07814783          	lbu	a5,120(sp)
4201211c:	cb85                	beqz	a5,4201214c <web_settings_post+0x2e4>
4201211e:	3c0b55b7          	lui	a1,0x3c0b5
42012122:	04100693          	li	a3,65
42012126:	09910613          	addi	a2,sp,153
4201212a:	8b858593          	addi	a1,a1,-1864 # 3c0b48b8 <_esp_libc_clock_array_end+0x4768>
4201212e:	8552                	mv	a0,s4
42012130:	a95ff0ef          	jal	42011bc4 <copy_string>
42012134:	842a                	mv	s0,a0
42012136:	c919                	beqz	a0,4201214c <web_settings_post+0x2e4>
42012138:	09910513          	addi	a0,sp,153
4201213c:	fdfee097          	auipc	ra,0xfdfee
42012140:	36c080e7          	jalr	876(ra) # 400004a8 <strlen>
42012144:	157d                	addi	a0,a0,-1
42012146:	4799                	li	a5,6
42012148:	00a7ef63          	bltu	a5,a0,42012166 <web_settings_post+0x2fe>
4201214c:	4981                	li	s3,0
4201214e:	4901                	li	s2,0
42012150:	4401                	li	s0,0
42012152:	8552                	mv	a0,s4
42012154:	63a020ef          	jal	4201478e <cJSON_Delete>
42012158:	e20412e3          	bnez	s0,42011f7c <web_settings_post+0x114>
4201215c:	3c0b55b7          	lui	a1,0x3c0b5
42012160:	92058593          	addi	a1,a1,-1760 # 3c0b4920 <_esp_libc_clock_array_end+0x47d0>
42012164:	bba9                	j	42011ebe <web_settings_post+0x56>
42012166:	4785                	li	a5,1
42012168:	1cf104a3          	sb	a5,457(sp)
4201216c:	8922                	mv	s2,s0
4201216e:	4981                	li	s3,0
42012170:	b7cd                	j	42012152 <web_settings_post+0x2ea>
42012172:	3c0b45b7          	lui	a1,0x3c0b4
42012176:	64058593          	addi	a1,a1,1600 # 3c0b4640 <_esp_libc_clock_array_end+0x44f0>
4201217a:	00848513          	addi	a0,s1,8
4201217e:	fe375097          	auipc	ra,0xfe375
42012182:	4d4080e7          	jalr	1236(ra) # 40387652 <strcmp>
42012186:	ed21                	bnez	a0,420121de <web_settings_post+0x376>
42012188:	3c0b55b7          	lui	a1,0x3c0b5
4201218c:	04100693          	li	a3,65
42012190:	12f10613          	addi	a2,sp,303
42012194:	8c458593          	addi	a1,a1,-1852 # 3c0b48c4 <_esp_libc_clock_array_end+0x4774>
42012198:	8552                	mv	a0,s4
4201219a:	a2bff0ef          	jal	42011bc4 <copy_string>
4201219e:	e119                	bnez	a0,420121a4 <web_settings_post+0x33c>
420121a0:	4401                	li	s0,0
420121a2:	a81d                	j	420121d8 <web_settings_post+0x370>
420121a4:	3c0b55b7          	lui	a1,0x3c0b5
420121a8:	04100693          	li	a3,65
420121ac:	1a90                	addi	a2,sp,368
420121ae:	8c858593          	addi	a1,a1,-1848 # 3c0b48c8 <_esp_libc_clock_array_end+0x4778>
420121b2:	8552                	mv	a0,s4
420121b4:	a11ff0ef          	jal	42011bc4 <copy_string>
420121b8:	d565                	beqz	a0,420121a0 <web_settings_post+0x338>
420121ba:	3c0b55b7          	lui	a1,0x3c0b5
420121be:	0878                	addi	a4,sp,28
420121c0:	46a9                	li	a3,10
420121c2:	4601                	li	a2,0
420121c4:	8dc58593          	addi	a1,a1,-1828 # 3c0b48dc <_esp_libc_clock_array_end+0x478c>
420121c8:	8552                	mv	a0,s4
420121ca:	fe8ff0ef          	jal	420119b2 <web_integer>
420121ce:	842a                	mv	s0,a0
420121d0:	d961                	beqz	a0,420121a0 <web_settings_post+0x338>
420121d2:	47f2                	lw	a5,28(sp)
420121d4:	1cf103a3          	sb	a5,455(sp)
420121d8:	89a2                	mv	s3,s0
420121da:	4901                	li	s2,0
420121dc:	bf9d                	j	42012152 <web_settings_post+0x2ea>
420121de:	3c0b45b7          	lui	a1,0x3c0b4
420121e2:	72c58593          	addi	a1,a1,1836 # 3c0b472c <_esp_libc_clock_array_end+0x45dc>
420121e6:	00848513          	addi	a0,s1,8
420121ea:	fe375097          	auipc	ra,0xfe375
420121ee:	468080e7          	jalr	1128(ra) # 40387652 <strcmp>
420121f2:	e95d                	bnez	a0,420122a8 <web_settings_post+0x440>
420121f4:	3c0b55b7          	lui	a1,0x3c0b5
420121f8:	05700693          	li	a3,87
420121fc:	0870                	addi	a2,sp,28
420121fe:	8e858593          	addi	a1,a1,-1816 # 3c0b48e8 <_esp_libc_clock_array_end+0x4798>
42012202:	8552                	mv	a0,s4
42012204:	9c1ff0ef          	jal	42011bc4 <copy_string>
42012208:	dd41                	beqz	a0,420121a0 <web_settings_post+0x338>
4201220a:	02c00593          	li	a1,44
4201220e:	0868                	addi	a0,sp,28
42012210:	fdfee097          	auipc	ra,0xfdfee
42012214:	32c080e7          	jalr	812(ra) # 4000053c <strrchr>
42012218:	892a                	mv	s2,a0
4201221a:	4985                	li	s3,1
4201221c:	ed09                	bnez	a0,42012236 <web_settings_post+0x3ce>
4201221e:	3c0b55b7          	lui	a1,0x3c0b5
42012222:	8f058593          	addi	a1,a1,-1808 # 3c0b48f0 <_esp_libc_clock_array_end+0x47a0>
42012226:	0868                	addi	a0,sp,28
42012228:	fdfee097          	auipc	ra,0xfdfee
4201222c:	284080e7          	jalr	644(ra) # 400004ac <strstr>
42012230:	892a                	mv	s2,a0
42012232:	d53d                	beqz	a0,420121a0 <web_settings_post+0x338>
42012234:	498d                	li	s3,3
42012236:	99ca                	add	s3,s3,s2
42012238:	854e                	mv	a0,s3
4201223a:	fdfee097          	auipc	ra,0xfdfee
4201223e:	26e080e7          	jalr	622(ra) # 400004a8 <strlen>
42012242:	47cd                	li	a5,19
42012244:	f4a7eee3          	bltu	a5,a0,420121a0 <web_settings_post+0x338>
42012248:	854e                	mv	a0,s3
4201224a:	cbff90ef          	jal	4200bf08 <settings_country_valid>
4201224e:	842a                	mv	s0,a0
42012250:	d921                	beqz	a0,420121a0 <web_settings_post+0x338>
42012252:	00090023          	sb	zero,0(s2)
42012256:	0868                	addi	a0,sp,28
42012258:	fdfee097          	auipc	ra,0xfdfee
4201225c:	250080e7          	jalr	592(ra) # 400004a8 <strlen>
42012260:	157d                	addi	a0,a0,-1
42012262:	03f00793          	li	a5,63
42012266:	f2a7ede3          	bltu	a5,a0,420121a0 <web_settings_post+0x338>
4201226a:	086c                	addi	a1,sp,28
4201226c:	0da10513          	addi	a0,sp,218
42012270:	fe375097          	auipc	ra,0xfe375
42012274:	4f8080e7          	jalr	1272(ra) # 40387768 <strcpy>
42012278:	854e                	mv	a0,s3
4201227a:	fdfee097          	auipc	ra,0xfdfee
4201227e:	22e080e7          	jalr	558(ra) # 400004a8 <strlen>
42012282:	18d4                	addi	a3,sp,116
42012284:	4781                	li	a5,0
42012286:	4665                	li	a2,25
42012288:	00f98733          	add	a4,s3,a5
4201228c:	00074703          	lbu	a4,0(a4)
42012290:	f9f70593          	addi	a1,a4,-97
42012294:	00b66363          	bltu	a2,a1,4201229a <web_settings_post+0x432>
42012298:	1701                	addi	a4,a4,-32
4201229a:	0ae683a3          	sb	a4,167(a3)
4201229e:	0785                	addi	a5,a5,1
420122a0:	0685                	addi	a3,a3,1
420122a2:	fef573e3          	bgeu	a0,a5,42012288 <web_settings_post+0x420>
420122a6:	bf0d                	j	420121d8 <web_settings_post+0x370>
420122a8:	3c0b45b7          	lui	a1,0x3c0b4
420122ac:	6dc58593          	addi	a1,a1,1756 # 3c0b46dc <_esp_libc_clock_array_end+0x458c>
420122b0:	00848513          	addi	a0,s1,8
420122b4:	fe375097          	auipc	ra,0xfe375
420122b8:	39e080e7          	jalr	926(ra) # 40387652 <strcmp>
420122bc:	e945                	bnez	a0,4201236c <web_settings_post+0x504>
420122be:	3c0b55b7          	lui	a1,0x3c0b5
420122c2:	8f458593          	addi	a1,a1,-1804 # 3c0b48f4 <_esp_libc_clock_array_end+0x47a4>
420122c6:	8552                	mv	a0,s4
420122c8:	20f020ef          	jal	42014cd6 <cJSON_GetObjectItemCaseSensitive>
420122cc:	3c0ba5b7          	lui	a1,0x3c0ba
420122d0:	892a                	mv	s2,a0
420122d2:	0878                	addi	a4,sp,28
420122d4:	4689                	li	a3,2
420122d6:	4601                	li	a2,0
420122d8:	86458593          	addi	a1,a1,-1948 # 3c0b9864 <_esp_libc_clock_array_end+0x9714>
420122dc:	8552                	mv	a0,s4
420122de:	ed4ff0ef          	jal	420119b2 <web_integer>
420122e2:	842a                	mv	s0,a0
420122e4:	e119                	bnez	a0,420122ea <web_settings_post+0x482>
420122e6:	4401                	li	s0,0
420122e8:	b3ed                	j	420120d2 <web_settings_post+0x26a>
420122ea:	854a                	mv	a0,s2
420122ec:	3e9020ef          	jal	42014ed4 <cJSON_IsString>
420122f0:	d97d                	beqz	a0,420122e6 <web_settings_post+0x47e>
420122f2:	01092903          	lw	s2,16(s2)
420122f6:	854a                	mv	a0,s2
420122f8:	fdfee097          	auipc	ra,0xfdfee
420122fc:	1b0080e7          	jalr	432(ra) # 400004a8 <strlen>
42012300:	479d                	li	a5,7
42012302:	fef512e3          	bne	a0,a5,420122e6 <web_settings_post+0x47e>
42012306:	00094703          	lbu	a4,0(s2)
4201230a:	02300793          	li	a5,35
4201230e:	fcf71ce3          	bne	a4,a5,420122e6 <web_settings_post+0x47e>
42012312:	4705                	li	a4,1
42012314:	4625                	li	a2,9
42012316:	4595                	li	a1,5
42012318:	86aa                	mv	a3,a0
4201231a:	00e907b3          	add	a5,s2,a4
4201231e:	0007c783          	lbu	a5,0(a5)
42012322:	fd078513          	addi	a0,a5,-48
42012326:	00a67b63          	bgeu	a2,a0,4201233c <web_settings_post+0x4d4>
4201232a:	fbf78513          	addi	a0,a5,-65
4201232e:	00a5f763          	bgeu	a1,a0,4201233c <web_settings_post+0x4d4>
42012332:	f9f78793          	addi	a5,a5,-97
42012336:	0067b793          	sltiu	a5,a5,6
4201233a:	8c7d                	and	s0,s0,a5
4201233c:	0705                	addi	a4,a4,1
4201233e:	fcd71ee3          	bne	a4,a3,4201231a <web_settings_post+0x4b2>
42012342:	d055                	beqz	s0,420122e6 <web_settings_post+0x47e>
42012344:	4641                	li	a2,16
42012346:	4581                	li	a1,0
42012348:	00190513          	addi	a0,s2,1
4201234c:	11c8c0ef          	jal	4209e468 <strtoul>
42012350:	4972                	lw	s2,28(sp)
42012352:	b69f90ef          	jal	4200beba <rgb565_from_rgb888>
42012356:	0818                	addi	a4,sp,16
42012358:	0a090913          	addi	s2,s2,160
4201235c:	0906                	slli	s2,s2,0x1
4201235e:	1d090793          	addi	a5,s2,464
42012362:	00e78933          	add	s2,a5,a4
42012366:	e8a91b23          	sh	a0,-362(s2)
4201236a:	b3a5                	j	420120d2 <web_settings_post+0x26a>
4201236c:	3c0b45b7          	lui	a1,0x3c0b4
42012370:	5e458593          	addi	a1,a1,1508 # 3c0b45e4 <_esp_libc_clock_array_end+0x4494>
42012374:	00848513          	addi	a0,s1,8
42012378:	fe375097          	auipc	ra,0xfe375
4201237c:	2da080e7          	jalr	730(ra) # 40387652 <strcmp>
42012380:	d40519e3          	bnez	a0,420120d2 <web_settings_post+0x26a>
42012384:	3c0b55b7          	lui	a1,0x3c0b5
42012388:	8fc58593          	addi	a1,a1,-1796 # 3c0b48fc <_esp_libc_clock_array_end+0x47ac>
4201238c:	8552                	mv	a0,s4
4201238e:	149020ef          	jal	42014cd6 <cJSON_GetObjectItemCaseSensitive>
42012392:	3c0b55b7          	lui	a1,0x3c0b5
42012396:	842a                	mv	s0,a0
42012398:	90858593          	addi	a1,a1,-1784 # 3c0b4908 <_esp_libc_clock_array_end+0x47b8>
4201239c:	8552                	mv	a0,s4
4201239e:	139020ef          	jal	42014cd6 <cJSON_GetObjectItemCaseSensitive>
420123a2:	892a                	mv	s2,a0
420123a4:	8522                	mv	a0,s0
420123a6:	32f020ef          	jal	42014ed4 <cJSON_IsString>
420123aa:	da0501e3          	beqz	a0,4201214c <web_settings_post+0x2e4>
420123ae:	854a                	mv	a0,s2
420123b0:	30b020ef          	jal	42014eba <cJSON_IsBool>
420123b4:	d8050ce3          	beqz	a0,4201214c <web_settings_post+0x2e4>
420123b8:	4800                	lw	s0,16(s0)
420123ba:	8522                	mv	a0,s0
420123bc:	fdfee097          	auipc	ra,0xfdfee
420123c0:	0ec080e7          	jalr	236(ra) # 400004a8 <strlen>
420123c4:	47b1                	li	a5,12
420123c6:	d8f513e3          	bne	a0,a5,4201214c <web_settings_post+0x2e4>
420123ca:	3c0b55b7          	lui	a1,0x3c0b5
420123ce:	4611                	li	a2,4
420123d0:	91058593          	addi	a1,a1,-1776 # 3c0b4910 <_esp_libc_clock_array_end+0x47c0>
420123d4:	8522                	mv	a0,s0
420123d6:	fe375097          	auipc	ra,0xfe375
420123da:	e26080e7          	jalr	-474(ra) # 403871fc <memcmp>
420123de:	d60517e3          	bnez	a0,4201214c <web_settings_post+0x2e4>
420123e2:	3c0b55b7          	lui	a1,0x3c0b5
420123e6:	91858593          	addi	a1,a1,-1768 # 3c0b4918 <_esp_libc_clock_array_end+0x47c8>
420123ea:	00540513          	addi	a0,s0,5
420123ee:	fe375097          	auipc	ra,0xfe375
420123f2:	264080e7          	jalr	612(ra) # 40387652 <strcmp>
420123f6:	d4051be3          	bnez	a0,4201214c <web_settings_post+0x2e4>
420123fa:	00444403          	lbu	s0,4(s0)
420123fe:	4791                	li	a5,4
42012400:	fcf40413          	addi	s0,s0,-49
42012404:	0ff47713          	zext.b	a4,s0
42012408:	d4e7e2e3          	bltu	a5,a4,4201214c <web_settings_post+0x2e4>
4201240c:	854a                	mv	a0,s2
4201240e:	29f020ef          	jal	42014eac <cJSON_IsTrue>
42012412:	4785                	li	a5,1
42012414:	008797b3          	sll	a5,a5,s0
42012418:	1c814703          	lbu	a4,456(sp)
4201241c:	0ff7f793          	zext.b	a5,a5
42012420:	c901                	beqz	a0,42012430 <web_settings_post+0x5c8>
42012422:	8f5d                	or	a4,a4,a5
42012424:	1ce10423          	sb	a4,456(sp)
42012428:	4981                	li	s3,0
4201242a:	4901                	li	s2,0
4201242c:	4405                	li	s0,1
4201242e:	b315                	j	42012152 <web_settings_post+0x2ea>
42012430:	fff7c793          	not	a5,a5
42012434:	8f7d                	and	a4,a4,a5
42012436:	b7fd                	j	42012424 <web_settings_post+0x5bc>
