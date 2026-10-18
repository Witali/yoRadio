
factory-irom.bin:     file format binary


Disassembly of section .data:

4200d06e <.data+0xd04e>:
4200d06e:	7171                	addi	sp,sp,-176
4200d070:	d706                	sw	ra,172(sp)
4200d072:	d522                	sw	s0,168(sp)
4200d074:	590290ef          	jal	0x42036604
4200d078:	18051163          	bnez	a0,0x4200d1fa
4200d07c:	2b5a10ef          	jal	0x420aeb30
4200d080:	18051f63          	bnez	a0,0x4200d21e
4200d084:	502320ef          	jal	0x4203f586
4200d088:	6785                	lui	a5,0x1
4200d08a:	10d78793          	addi	a5,a5,269 # 0x110d
4200d08e:	1af50a63          	beq	a0,a5,0x4200d242
4200d092:	6785                	lui	a5,0x1
4200d094:	11078793          	addi	a5,a5,272 # 0x1110
4200d098:	1af50563          	beq	a0,a5,0x4200d242
4200d09c:	1c051b63          	bnez	a0,0x4200d272
4200d0a0:	fe37c097          	auipc	ra,0xfe37c
4200d0a4:	b5e080e7          	jalr	-1186(ra) # 0x40388bfe
4200d0a8:	3fcc47b7          	lui	a5,0x3fcc4
4200d0ac:	a6a7ae23          	sw	a0,-1412(a5) # 0x3fcc3a7c
4200d0b0:	4701                	li	a4,0
4200d0b2:	4681                	li	a3,0
4200d0b4:	4200c637          	lui	a2,0x4200c
4200d0b8:	6e260613          	addi	a2,a2,1762 # 0x4200c6e2
4200d0bc:	55fd                	li	a1,-1
4200d0be:	3c0f27b7          	lui	a5,0x3c0f2
4200d0c2:	eb87a503          	lw	a0,-328(a5) # 0x3c0f1eb8
4200d0c6:	1f1a10ef          	jal	0x420aeab6
4200d0ca:	1c051663          	bnez	a0,0x4200d296
4200d0ce:	4701                	li	a4,0
4200d0d0:	4681                	li	a3,0
4200d0d2:	4200c637          	lui	a2,0x4200c
4200d0d6:	6e260613          	addi	a2,a2,1762 # 0x4200c6e2
4200d0da:	4581                	li	a1,0
4200d0dc:	3c0f27b7          	lui	a5,0x3c0f2
4200d0e0:	8487a503          	lw	a0,-1976(a5) # 0x3c0f1848
4200d0e4:	1d3a10ef          	jal	0x420aeab6
4200d0e8:	1c051963          	bnez	a0,0x4200d2ba
4200d0ec:	bdc18793          	addi	a5,gp,-1060
4200d0f0:	c43e                	sw	a5,8(sp)
4200d0f2:	3c0f27b7          	lui	a5,0x3c0f2
4200d0f6:	e8c78793          	addi	a5,a5,-372 # 0x3c0f1e8c
4200d0fa:	0007ae83          	lw	t4,0(a5)
4200d0fe:	0047ae03          	lw	t3,4(a5)
4200d102:	0087a303          	lw	t1,8(a5)
4200d106:	00c7a883          	lw	a7,12(a5)
4200d10a:	0107a803          	lw	a6,16(a5)
4200d10e:	4bc8                	lw	a0,20(a5)
4200d110:	4f8c                	lw	a1,24(a5)
4200d112:	4fd0                	lw	a2,28(a5)
4200d114:	5394                	lw	a3,32(a5)
4200d116:	53d8                	lw	a4,36(a5)
4200d118:	579c                	lw	a5,40(a5)
4200d11a:	c676                	sw	t4,12(sp)
4200d11c:	c872                	sw	t3,16(sp)
4200d11e:	ca1a                	sw	t1,20(sp)
4200d120:	cc46                	sw	a7,24(sp)
4200d122:	ce42                	sw	a6,28(sp)
4200d124:	d02a                	sw	a0,32(sp)
4200d126:	d22e                	sw	a1,36(sp)
4200d128:	d432                	sw	a2,40(sp)
4200d12a:	d636                	sw	a3,44(sp)
4200d12c:	d83a                	sw	a4,48(sp)
4200d12e:	da3e                	sw	a5,52(sp)
4200d130:	47a9                	li	a5,10
4200d132:	dc3e                	sw	a5,56(sp)
4200d134:	02000713          	li	a4,32
4200d138:	de3a                	sw	a4,60(sp)
4200d13a:	4785                	li	a5,1
4200d13c:	c0be                	sw	a5,64(sp)
4200d13e:	c282                	sw	zero,68(sp)
4200d140:	c4ba                	sw	a4,72(sp)
4200d142:	c682                	sw	zero,76(sp)
4200d144:	4695                	li	a3,5
4200d146:	c8b6                	sw	a3,80(sp)
4200d148:	ca82                	sw	zero,84(sp)
4200d14a:	cc82                	sw	zero,88(sp)
4200d14c:	cebe                	sw	a5,92(sp)
4200d14e:	d0be                	sw	a5,96(sp)
4200d150:	d282                	sw	zero,100(sp)
4200d152:	d4be                	sw	a5,104(sp)
4200d154:	d6be                	sw	a5,108(sp)
4200d156:	4699                	li	a3,6
4200d158:	d8b6                	sw	a3,112(sp)
4200d15a:	da82                	sw	zero,116(sp)
4200d15c:	2f000693          	li	a3,752
4200d160:	dcb6                	sw	a3,120(sp)
4200d162:	deba                	sw	a4,124(sp)
4200d164:	0a100613          	li	a2,161
4200d168:	4681                	li	a3,0
4200d16a:	c132                	sw	a2,128(sp)
4200d16c:	c336                	sw	a3,132(sp)
4200d16e:	08f10423          	sb	a5,136(sp)
4200d172:	4709                	li	a4,2
4200d174:	c73a                	sw	a4,140(sp)
4200d176:	c93e                	sw	a5,144(sp)
4200d178:	08010a23          	sb	zero,148(sp)
4200d17c:	1f2f47b7          	lui	a5,0x1f2f4
4200d180:	f4f78793          	addi	a5,a5,-177 # 0x1f2f3f4f
4200d184:	cd3e                	sw	a5,152(sp)
4200d186:	0028                	addi	a0,sp,8
4200d188:	2c6380ef          	jal	0x4204544e
4200d18c:	14051963          	bnez	a0,0x4200d2de
4200d190:	450d                	li	a0,3
4200d192:	3255b0ef          	jal	0x42068cb6
4200d196:	16051663          	bnez	a0,0x4200d302
4200d19a:	d05ff0ef          	jal	0x4200ce9e
4200d19e:	842a                	mv	s0,a0
4200d1a0:	3675b0ef          	jal	0x42068d06
4200d1a4:	18051163          	bnez	a0,0x4200d326
4200d1a8:	06400513          	li	a0,100
4200d1ac:	fe37d097          	auipc	ra,0xfe37d
4200d1b0:	942080e7          	jalr	-1726(ra) # 0x40389aee
4200d1b4:	8522                	mv	a0,s0
4200d1b6:	fa0ff0ef          	jal	0x4200c956
4200d1ba:	827ff0ef          	jal	0x4200c9e0
4200d1be:	4415                	li	s0,5
4200d1c0:	3fcc47b7          	lui	a5,0x3fcc4
4200d1c4:	a6878a23          	sb	s0,-1420(a5) # 0x3fcc3a74
4200d1c8:	707a30ef          	jal	0x420b10ce
4200d1cc:	80000837          	lui	a6,0x80000
4200d1d0:	187d                	addi	a6,a6,-1 # 0x7fffffff
4200d1d2:	4781                	li	a5,0
4200d1d4:	8722                	mv	a4,s0
4200d1d6:	4681                	li	a3,0
4200d1d8:	6605                	lui	a2,0x1
4200d1da:	3c0c35b7          	lui	a1,0x3c0c3
4200d1de:	1d058593          	addi	a1,a1,464 # 0x3c0c31d0
4200d1e2:	4200c537          	lui	a0,0x4200c
4200d1e6:	74e50513          	addi	a0,a0,1870 # 0x4200c74e
4200d1ea:	fe37d097          	auipc	ra,0xfe37d
4200d1ee:	5ba080e7          	jalr	1466(ra) # 0x4038a7a4
4200d1f2:	50ba                	lw	ra,172(sp)
4200d1f4:	542a                	lw	s0,168(sp)
4200d1f6:	614d                	addi	sp,sp,176
4200d1f8:	8082                	ret
4200d1fa:	3c0c3737          	lui	a4,0x3c0c3
4200d1fe:	d0070713          	addi	a4,a4,-768 # 0x3c0c2d00
4200d202:	3c0d66b7          	lui	a3,0x3c0d6
4200d206:	62468693          	addi	a3,a3,1572 # 0x3c0d6624
4200d20a:	1d400613          	li	a2,468
4200d20e:	3c0c35b7          	lui	a1,0x3c0c3
4200d212:	d1458593          	addi	a1,a1,-748 # 0x3c0c2d14
4200d216:	fe37a097          	auipc	ra,0xfe37a
4200d21a:	054080e7          	jalr	84(ra) # 0x4038726a
4200d21e:	3c0c3737          	lui	a4,0x3c0c3
4200d222:	d2c70713          	addi	a4,a4,-724 # 0x3c0c2d2c
4200d226:	3c0d66b7          	lui	a3,0x3c0d6
4200d22a:	62468693          	addi	a3,a3,1572 # 0x3c0d6624
4200d22e:	1d500613          	li	a2,469
4200d232:	3c0c35b7          	lui	a1,0x3c0c3
4200d236:	d1458593          	addi	a1,a1,-748 # 0x3c0c2d14
4200d23a:	fe37a097          	auipc	ra,0xfe37a
4200d23e:	030080e7          	jalr	48(ra) # 0x4038726a
4200d242:	4f6320ef          	jal	0x4203f738
4200d246:	e501                	bnez	a0,0x4200d24e
4200d248:	33e320ef          	jal	0x4203f586
4200d24c:	bd81                	j	0x4200d09c
4200d24e:	3c0c3737          	lui	a4,0x3c0c3
4200d252:	ad070713          	addi	a4,a4,-1328 # 0x3c0c2ad0
4200d256:	3c0d66b7          	lui	a3,0x3c0d6
4200d25a:	62468693          	addi	a3,a3,1572 # 0x3c0d6624
4200d25e:	1da00613          	li	a2,474
4200d262:	3c0c35b7          	lui	a1,0x3c0c3
4200d266:	d1458593          	addi	a1,a1,-748 # 0x3c0c2d14
4200d26a:	fe37a097          	auipc	ra,0xfe37a
4200d26e:	000080e7          	jalr	ra # 0x4038726a
4200d272:	3c0c3737          	lui	a4,0x3c0c3
4200d276:	b1c70713          	addi	a4,a4,-1252 # 0x3c0c2b1c
4200d27a:	3c0d66b7          	lui	a3,0x3c0d6
4200d27e:	62468693          	addi	a3,a3,1572 # 0x3c0d6624
4200d282:	1dd00613          	li	a2,477
4200d286:	3c0c35b7          	lui	a1,0x3c0c3
4200d28a:	d1458593          	addi	a1,a1,-748 # 0x3c0c2d14
4200d28e:	fe37a097          	auipc	ra,0xfe37a
4200d292:	fdc080e7          	jalr	-36(ra) # 0x4038726a
4200d296:	3c0c3737          	lui	a4,0x3c0c3
4200d29a:	0e470713          	addi	a4,a4,228 # 0x3c0c30e4
4200d29e:	3c0d66b7          	lui	a3,0x3c0d6
4200d2a2:	62468693          	addi	a3,a3,1572 # 0x3c0d6624
4200d2a6:	1e300613          	li	a2,483
4200d2aa:	3c0c35b7          	lui	a1,0x3c0c3
4200d2ae:	d1458593          	addi	a1,a1,-748 # 0x3c0c2d14
4200d2b2:	fe37a097          	auipc	ra,0xfe37a
4200d2b6:	fb8080e7          	jalr	-72(ra) # 0x4038726a
4200d2ba:	3c0c3737          	lui	a4,0x3c0c3
4200d2be:	14870713          	addi	a4,a4,328 # 0x3c0c3148
4200d2c2:	3c0d66b7          	lui	a3,0x3c0d6
4200d2c6:	62468693          	addi	a3,a3,1572 # 0x3c0d6624
4200d2ca:	1e800613          	li	a2,488
4200d2ce:	3c0c35b7          	lui	a1,0x3c0c3
4200d2d2:	d1458593          	addi	a1,a1,-748 # 0x3c0c2d14
4200d2d6:	fe37a097          	auipc	ra,0xfe37a
4200d2da:	f94080e7          	jalr	-108(ra) # 0x4038726a
4200d2de:	3c0c3737          	lui	a4,0x3c0c3
4200d2e2:	d4c70713          	addi	a4,a4,-692 # 0x3c0c2d4c
4200d2e6:	3c0d66b7          	lui	a3,0x3c0d6
4200d2ea:	62468693          	addi	a3,a3,1572 # 0x3c0d6624
4200d2ee:	1f000613          	li	a2,496
4200d2f2:	3c0c35b7          	lui	a1,0x3c0c3
4200d2f6:	d1458593          	addi	a1,a1,-748 # 0x3c0c2d14
4200d2fa:	fe37a097          	auipc	ra,0xfe37a
4200d2fe:	f70080e7          	jalr	-144(ra) # 0x4038726a
4200d302:	3c0c3737          	lui	a4,0x3c0c3
4200d306:	1ac70713          	addi	a4,a4,428 # 0x3c0c31ac
4200d30a:	3c0d66b7          	lui	a3,0x3c0d6
4200d30e:	62468693          	addi	a3,a3,1572 # 0x3c0d6624
4200d312:	1f200613          	li	a2,498
4200d316:	3c0c35b7          	lui	a1,0x3c0c3
4200d31a:	d1458593          	addi	a1,a1,-748 # 0x3c0c2d14
4200d31e:	fe37a097          	auipc	ra,0xfe37a
4200d322:	f4c080e7          	jalr	-180(ra) # 0x4038726a
4200d326:	3c0c3737          	lui	a4,0x3c0c3
4200d32a:	e9070713          	addi	a4,a4,-368 # 0x3c0c2e90
4200d32e:	3c0d66b7          	lui	a3,0x3c0d6
4200d332:	62468693          	addi	a3,a3,1572 # 0x3c0d6624
4200d336:	1ff00613          	li	a2,511
4200d33a:	3c0c35b7          	lui	a1,0x3c0c3
4200d33e:	d1458593          	addi	a1,a1,-748 # 0x3c0c2d14
4200d342:	fe37a097          	auipc	ra,0xfe37a
4200d346:	f28080e7          	jalr	-216(ra) # 0x4038726a
