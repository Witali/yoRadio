
factory-irom.bin:     file format binary


Disassembly of section .data:

42010864 <.data+0x10844>:
42010864:	7105                	addi	sp,sp,-480
42010866:	1c112e23          	sw	ra,476(sp)
4201086a:	1c812c23          	sw	s0,472(sp)
4201086e:	1c912a23          	sw	s1,468(sp)
42010872:	1d212823          	sw	s2,464(sp)
42010876:	10000613          	li	a2,256
4201087a:	4581                	li	a1,0
4201087c:	0988                	addi	a0,sp,208
4201087e:	fdff0097          	auipc	ra,0xfdff0
42010882:	c0a080e7          	jalr	-1014(ra) # 0x40000488
42010886:	d902                	sw	zero,176(sp)
42010888:	db02                	sw	zero,180(sp)
4201088a:	dd02                	sw	zero,184(sp)
4201088c:	df02                	sw	zero,188(sp)
4201088e:	c182                	sw	zero,192(sp)
42010890:	c382                	sw	zero,196(sp)
42010892:	c582                	sw	zero,200(sp)
42010894:	c782                	sw	zero,204(sp)
42010896:	3fcb8637          	lui	a2,0x3fcb8
4201089a:	c7760613          	addi	a2,a2,-905 # 0x3fcb7c77
4201089e:	191c                	addi	a5,sp,176
420108a0:	a839                	j	0x420108be
420108a2:	02500713          	li	a4,37
420108a6:	00e78023          	sb	a4,0(a5)
420108aa:	03200713          	li	a4,50
420108ae:	00e780a3          	sb	a4,1(a5)
420108b2:	03000713          	li	a4,48
420108b6:	00e78123          	sb	a4,2(a5)
420108ba:	078d                	addi	a5,a5,3
420108bc:	0605                	addi	a2,a2,1
420108be:	00064683          	lbu	a3,0(a2)
420108c2:	ce99                	beqz	a3,0x420108e0
420108c4:	1918                	addi	a4,sp,176
420108c6:	40e78733          	sub	a4,a5,a4
420108ca:	45f9                	li	a1,30
420108cc:	00e5ea63          	bltu	a1,a4,0x420108e0
420108d0:	02000713          	li	a4,32
420108d4:	fce687e3          	beq	a3,a4,0x420108a2
420108d8:	00d78023          	sb	a3,0(a5)
420108dc:	0785                	addi	a5,a5,1
420108de:	bff9                	j	0x420108bc
420108e0:	00078023          	sb	zero,0(a5)
420108e4:	d302                	sw	zero,164(sp)
420108e6:	d502                	sw	zero,168(sp)
420108e8:	0a011623          	sh	zero,172(sp)
420108ec:	3fcb8637          	lui	a2,0x3fcb8
420108f0:	c6360613          	addi	a2,a2,-925 # 0x3fcb7c63
420108f4:	115c                	addi	a5,sp,164
420108f6:	a839                	j	0x42010914
420108f8:	02500713          	li	a4,37
420108fc:	00e78023          	sb	a4,0(a5)
42010900:	03200713          	li	a4,50
42010904:	00e780a3          	sb	a4,1(a5)
42010908:	03000713          	li	a4,48
4201090c:	00e78123          	sb	a4,2(a5)
42010910:	078d                	addi	a5,a5,3
42010912:	0605                	addi	a2,a2,1
42010914:	00064683          	lbu	a3,0(a2)
42010918:	ce99                	beqz	a3,0x42010936
4201091a:	1158                	addi	a4,sp,164
4201091c:	40e78733          	sub	a4,a5,a4
42010920:	45a1                	li	a1,8
42010922:	00e5ea63          	bltu	a1,a4,0x42010936
42010926:	02000713          	li	a4,32
4201092a:	fce687e3          	beq	a3,a4,0x420108f8
4201092e:	00d78023          	sb	a3,0(a5)
42010932:	0785                	addi	a5,a5,1
42010934:	bff9                	j	0x42010912
42010936:	00078023          	sb	zero,0(a5)
4201093a:	0984                	addi	s1,sp,208
4201093c:	3fcb8737          	lui	a4,0x3fcb8
42010940:	cb870713          	addi	a4,a4,-840 # 0x3fcb7cb8
42010944:	1154                	addi	a3,sp,164
42010946:	1910                	addi	a2,sp,176
42010948:	3c0c45b7          	lui	a1,0x3c0c4
4201094c:	b5858593          	addi	a1,a1,-1192 # 0x3c0c3b58
42010950:	8526                	mv	a0,s1
42010952:	fdff0097          	auipc	ra,0xfdff0
42010956:	d56080e7          	jalr	-682(ra) # 0x400006a8
4201095a:	0060                	addi	s0,sp,12
4201095c:	09800613          	li	a2,152
42010960:	4581                	li	a1,0
42010962:	8522                	mv	a0,s0
42010964:	fdff0097          	auipc	ra,0xfdff0
42010968:	b24080e7          	jalr	-1244(ra) # 0x40000488
4201096c:	c626                	sw	s1,12(sp)
4201096e:	6789                	lui	a5,0x2
42010970:	71078793          	addi	a5,a5,1808 # 0x2710
42010974:	ccbe                	sw	a5,88(sp)
42010976:	420107b7          	lui	a5,0x42010
4201097a:	ccc78793          	addi	a5,a5,-820 # 0x4200fccc
4201097e:	d4be                	sw	a5,104(sp)
42010980:	8522                	mv	a0,s0
42010982:	3f42d0ef          	jal	0x4203dd76
42010986:	84aa                	mv	s1,a0
42010988:	6312d0ef          	jal	0x4203e7b8
4201098c:	842a                	mv	s0,a0
4201098e:	ed11                	bnez	a0,0x420109aa
42010990:	8526                	mv	a0,s1
42010992:	0602d0ef          	jal	0x4203d9f2
42010996:	1dc12083          	lw	ra,476(sp)
4201099a:	1d812403          	lw	s0,472(sp)
4201099e:	1d412483          	lw	s1,468(sp)
420109a2:	1d012903          	lw	s2,464(sp)
420109a6:	613d                	addi	sp,sp,480
420109a8:	8082                	ret
420109aa:	fe37d097          	auipc	ra,0xfe37d
420109ae:	a0a080e7          	jalr	-1526(ra) # 0x4038d3b4
420109b2:	892a                	mv	s2,a0
420109b4:	8522                	mv	a0,s0
420109b6:	099060ef          	jal	0x4201724e
420109ba:	87aa                	mv	a5,a0
420109bc:	3c0c45b7          	lui	a1,0x3c0c4
420109c0:	97458713          	addi	a4,a1,-1676 # 0x3c0c3974
420109c4:	86ca                	mv	a3,s2
420109c6:	3c0c4637          	lui	a2,0x3c0c4
420109ca:	b9860613          	addi	a2,a2,-1128 # 0x3c0c3b98
420109ce:	97458593          	addi	a1,a1,-1676
420109d2:	4505                	li	a0,1
420109d4:	fe37d097          	auipc	ra,0xfe37d
420109d8:	8ce080e7          	jalr	-1842(ra) # 0x4038d2a2
420109dc:	bf55                	j	0x42010990
