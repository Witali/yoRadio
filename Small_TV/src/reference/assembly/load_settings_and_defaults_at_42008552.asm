
factory-irom.bin:     file format binary


Disassembly of section .data:

42008552 <.data+0x8532>:
42008552:	1141                	addi	sp,sp,-16
42008554:	c606                	sw	ra,12(sp)
42008556:	c422                	sw	s0,8(sp)
42008558:	1bc00693          	li	a3,444
4200855c:	003e7637          	lui	a2,0x3e7
42008560:	3fcb8437          	lui	s0,0x3fcb8
42008564:	b9c40593          	addi	a1,s0,-1124 # 0x3fcb7b9c
42008568:	4501                	li	a0,0
4200856a:	fe38a097          	auipc	ra,0xfe38a
4200856e:	dbc080e7          	jalr	-580(ra) # 0x40392326
42008572:	b9c42703          	lw	a4,-1124(s0)
42008576:	47f9                	li	a5,30
42008578:	00e7f563          	bgeu	a5,a4,0x42008582
4200857c:	477d                	li	a4,31
4200857e:	b8e42e23          	sw	a4,-1124(s0)
42008582:	3fcb87b7          	lui	a5,0x3fcb8
42008586:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200858a:	0867c783          	lbu	a5,134(a5)
4200858e:	c789                	beqz	a5,0x42008598
42008590:	0ff00713          	li	a4,255
42008594:	04e79f63          	bne	a5,a4,0x420085f2
42008598:	3fcb8537          	lui	a0,0x3fcb8
4200859c:	c2250413          	addi	s0,a0,-990 # 0x3fcb7c22
420085a0:	04100613          	li	a2,65
420085a4:	4581                	li	a1,0
420085a6:	c2250513          	addi	a0,a0,-990
420085aa:	fdff8097          	auipc	ra,0xfdff8
420085ae:	ede080e7          	jalr	-290(ra) # 0x40000488
420085b2:	3c0c37b7          	lui	a5,0x3c0c3
420085b6:	9ec78793          	addi	a5,a5,-1556 # 0x3c0c29ec
420085ba:	0007d803          	lhu	a6,0(a5)
420085be:	0027d503          	lhu	a0,2(a5)
420085c2:	0047d583          	lhu	a1,4(a5)
420085c6:	0067d603          	lhu	a2,6(a5)
420085ca:	0087d683          	lhu	a3,8(a5)
420085ce:	00a7d703          	lhu	a4,10(a5)
420085d2:	01041023          	sh	a6,0(s0)
420085d6:	00a41123          	sh	a0,2(s0)
420085da:	00b41223          	sh	a1,4(s0)
420085de:	00c41323          	sh	a2,6(s0)
420085e2:	00d41423          	sh	a3,8(s0)
420085e6:	00e41523          	sh	a4,10(s0)
420085ea:	00c7c783          	lbu	a5,12(a5)
420085ee:	00f40623          	sb	a5,12(s0)
420085f2:	3fcb87b7          	lui	a5,0x3fcb8
420085f6:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
420085fa:	0db7c783          	lbu	a5,219(a5)
420085fe:	c789                	beqz	a5,0x42008608
42008600:	0ff00713          	li	a4,255
42008604:	06e79763          	bne	a5,a4,0x42008672
42008608:	3fcb8537          	lui	a0,0x3fcb8
4200860c:	c7750413          	addi	s0,a0,-905 # 0x3fcb7c77
42008610:	04100613          	li	a2,65
42008614:	4581                	li	a1,0
42008616:	c7750513          	addi	a0,a0,-905
4200861a:	fdff8097          	auipc	ra,0xfdff8
4200861e:	e6e080e7          	jalr	-402(ra) # 0x40000488
42008622:	3c0c37b7          	lui	a5,0x3c0c3
42008626:	9fc78793          	addi	a5,a5,-1540 # 0x3c0c29fc
4200862a:	0007c303          	lbu	t1,0(a5)
4200862e:	0017c883          	lbu	a7,1(a5)
42008632:	0027c803          	lbu	a6,2(a5)
42008636:	0037c503          	lbu	a0,3(a5)
4200863a:	0047c583          	lbu	a1,4(a5)
4200863e:	0057c603          	lbu	a2,5(a5)
42008642:	0067c683          	lbu	a3,6(a5)
42008646:	0077c703          	lbu	a4,7(a5)
4200864a:	0087c783          	lbu	a5,8(a5)
4200864e:	00640023          	sb	t1,0(s0)
42008652:	011400a3          	sb	a7,1(s0)
42008656:	01040123          	sb	a6,2(s0)
4200865a:	00a401a3          	sb	a0,3(s0)
4200865e:	00b40223          	sb	a1,4(s0)
42008662:	00c402a3          	sb	a2,5(s0)
42008666:	00d40323          	sb	a3,6(s0)
4200866a:	00e403a3          	sb	a4,7(s0)
4200866e:	00f40423          	sb	a5,8(s0)
42008672:	3fcb87b7          	lui	a5,0x3fcb8
42008676:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200867a:	0c77c783          	lbu	a5,199(a5)
4200867e:	c789                	beqz	a5,0x42008688
42008680:	0ff00713          	li	a4,255
42008684:	02e79863          	bne	a5,a4,0x420086b4
42008688:	3fcb8537          	lui	a0,0x3fcb8
4200868c:	c6350413          	addi	s0,a0,-925 # 0x3fcb7c63
42008690:	4651                	li	a2,20
42008692:	4581                	li	a1,0
42008694:	c6350513          	addi	a0,a0,-925
42008698:	fdff8097          	auipc	ra,0xfdff8
4200869c:	df0080e7          	jalr	-528(ra) # 0x40000488
420086a0:	04300793          	li	a5,67
420086a4:	00f40023          	sb	a5,0(s0)
420086a8:	04e00793          	li	a5,78
420086ac:	00f400a3          	sb	a5,1(s0)
420086b0:	00040123          	sb	zero,2(s0)
420086b4:	3fcb87b7          	lui	a5,0x3fcb8
420086b8:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
420086bc:	11c7c783          	lbu	a5,284(a5)
420086c0:	c789                	beqz	a5,0x420086ca
420086c2:	0ff00713          	li	a4,255
420086c6:	04e79d63          	bne	a5,a4,0x42008720
420086ca:	3fcb8537          	lui	a0,0x3fcb8
420086ce:	cb850413          	addi	s0,a0,-840 # 0x3fcb7cb8
420086d2:	04100613          	li	a2,65
420086d6:	4581                	li	a1,0
420086d8:	cb850513          	addi	a0,a0,-840
420086dc:	fdff8097          	auipc	ra,0xfdff8
420086e0:	dac080e7          	jalr	-596(ra) # 0x40000488
420086e4:	3c0c37b7          	lui	a5,0x3c0c3
420086e8:	a0878793          	addi	a5,a5,-1528 # 0x3c0c2a08
420086ec:	0007a303          	lw	t1,0(a5)
420086f0:	0047a883          	lw	a7,4(a5)
420086f4:	0087a803          	lw	a6,8(a5)
420086f8:	47c8                	lw	a0,12(a5)
420086fa:	4b8c                	lw	a1,16(a5)
420086fc:	4bd0                	lw	a2,20(a5)
420086fe:	4f94                	lw	a3,24(a5)
42008700:	4fd8                	lw	a4,28(a5)
42008702:	00642023          	sw	t1,0(s0)
42008706:	01142223          	sw	a7,4(s0)
4200870a:	01042423          	sw	a6,8(s0)
4200870e:	c448                	sw	a0,12(s0)
42008710:	c80c                	sw	a1,16(s0)
42008712:	c850                	sw	a2,20(s0)
42008714:	cc14                	sw	a3,24(s0)
42008716:	cc58                	sw	a4,28(s0)
42008718:	0207c783          	lbu	a5,32(a5)
4200871c:	02f40023          	sb	a5,32(s0)
42008720:	3fcb87b7          	lui	a5,0x3fcb8
42008724:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
42008728:	1647a703          	lw	a4,356(a5)
4200872c:	4791                	li	a5,4
4200872e:	00e7f863          	bgeu	a5,a4,0x4200873e
42008732:	3fcb87b7          	lui	a5,0x3fcb8
42008736:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200873a:	1607a223          	sw	zero,356(a5)
4200873e:	3fcb87b7          	lui	a5,0x3fcb8
42008742:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
42008746:	1687a703          	lw	a4,360(a5)
4200874a:	478d                	li	a5,3
4200874c:	00e7f863          	bgeu	a5,a4,0x4200875c
42008750:	3fcb87b7          	lui	a5,0x3fcb8
42008754:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
42008758:	1607a423          	sw	zero,360(a5)
4200875c:	3fcb87b7          	lui	a5,0x3fcb8
42008760:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
42008764:	16c7a703          	lw	a4,364(a5)
42008768:	4785                	li	a5,1
4200876a:	00e7f863          	bgeu	a5,a4,0x4200877a
4200876e:	3fcb87b7          	lui	a5,0x3fcb8
42008772:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
42008776:	1607a623          	sw	zero,364(a5)
4200877a:	3fcb87b7          	lui	a5,0x3fcb8
4200877e:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
42008782:	1707a703          	lw	a4,368(a5)
42008786:	4785                	li	a5,1
42008788:	00e7f863          	bgeu	a5,a4,0x42008798
4200878c:	3fcb87b7          	lui	a5,0x3fcb8
42008790:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
42008794:	1607a823          	sw	zero,368(a5)
42008798:	3fcb87b7          	lui	a5,0x3fcb8
4200879c:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
420087a0:	1747a703          	lw	a4,372(a5)
420087a4:	4785                	li	a5,1
420087a6:	00e7f863          	bgeu	a5,a4,0x420087b6
420087aa:	3fcb87b7          	lui	a5,0x3fcb8
420087ae:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
420087b2:	1607aa23          	sw	zero,372(a5)
420087b6:	3fcb87b7          	lui	a5,0x3fcb8
420087ba:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
420087be:	1787a703          	lw	a4,376(a5)
420087c2:	4785                	li	a5,1
420087c4:	00e7f863          	bgeu	a5,a4,0x420087d4
420087c8:	3fcb87b7          	lui	a5,0x3fcb8
420087cc:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
420087d0:	1607ac23          	sw	zero,376(a5)
420087d4:	3fcb87b7          	lui	a5,0x3fcb8
420087d8:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
420087dc:	17c7a703          	lw	a4,380(a5)
420087e0:	4785                	li	a5,1
420087e2:	00e7f963          	bgeu	a5,a4,0x420087f4
420087e6:	3fcb87b7          	lui	a5,0x3fcb8
420087ea:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
420087ee:	4709                	li	a4,2
420087f0:	16e7ae23          	sw	a4,380(a5)
420087f4:	3fcb87b7          	lui	a5,0x3fcb8
420087f8:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
420087fc:	1807a703          	lw	a4,384(a5)
42008800:	3e800793          	li	a5,1000
42008804:	00e7f863          	bgeu	a5,a4,0x42008814
42008808:	3fcb87b7          	lui	a5,0x3fcb8
4200880c:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
42008810:	1807a023          	sw	zero,384(a5)
42008814:	3fcb87b7          	lui	a5,0x3fcb8
42008818:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200881c:	1847a703          	lw	a4,388(a5)
42008820:	67c1                	lui	a5,0x10
42008822:	00f76b63          	bltu	a4,a5,0x42008838
42008826:	3fcb87b7          	lui	a5,0x3fcb8
4200882a:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200882e:	6741                	lui	a4,0x10
42008830:	80070713          	addi	a4,a4,-2048 # 0xf800
42008834:	18e7a223          	sw	a4,388(a5)
42008838:	3fcb87b7          	lui	a5,0x3fcb8
4200883c:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
42008840:	1887a703          	lw	a4,392(a5)
42008844:	67c1                	lui	a5,0x10
42008846:	00f76a63          	bltu	a4,a5,0x4200885a
4200884a:	3fcb87b7          	lui	a5,0x3fcb8
4200884e:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
42008852:	6741                	lui	a4,0x10
42008854:	1701                	addi	a4,a4,-32 # 0xffe0
42008856:	18e7a423          	sw	a4,392(a5)
4200885a:	3fcb87b7          	lui	a5,0x3fcb8
4200885e:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
42008862:	18c7a703          	lw	a4,396(a5)
42008866:	67c1                	lui	a5,0x10
42008868:	00f76a63          	bltu	a4,a5,0x4200887c
4200886c:	3fcb87b7          	lui	a5,0x3fcb8
42008870:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
42008874:	6741                	lui	a4,0x10
42008876:	177d                	addi	a4,a4,-1 # 0xffff
42008878:	18e7a623          	sw	a4,396(a5)
4200887c:	3fcb87b7          	lui	a5,0x3fcb8
42008880:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
42008884:	1907a703          	lw	a4,400(a5)
42008888:	4785                	li	a5,1
4200888a:	00e7f863          	bgeu	a5,a4,0x4200889a
4200888e:	3fcb87b7          	lui	a5,0x3fcb8
42008892:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
42008896:	1807a823          	sw	zero,400(a5)
4200889a:	3fcb87b7          	lui	a5,0x3fcb8
4200889e:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
420088a2:	1947a783          	lw	a5,404(a5)
420088a6:	17b9                	addi	a5,a5,-18
420088a8:	4715                	li	a4,5
420088aa:	00f77963          	bgeu	a4,a5,0x420088bc
420088ae:	3fcb87b7          	lui	a5,0x3fcb8
420088b2:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
420088b6:	4759                	li	a4,22
420088b8:	18e7aa23          	sw	a4,404(a5)
420088bc:	3fcb87b7          	lui	a5,0x3fcb8
420088c0:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
420088c4:	1987a783          	lw	a5,408(a5)
420088c8:	17ed                	addi	a5,a5,-5
420088ca:	471d                	li	a4,7
420088cc:	00f77963          	bgeu	a4,a5,0x420088de
420088d0:	3fcb87b7          	lui	a5,0x3fcb8
420088d4:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
420088d8:	4725                	li	a4,9
420088da:	18e7ac23          	sw	a4,408(a5)
420088de:	3fcb87b7          	lui	a5,0x3fcb8
420088e2:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
420088e6:	19c7a703          	lw	a4,412(a5)
420088ea:	3e800793          	li	a5,1000
420088ee:	00e7fa63          	bgeu	a5,a4,0x42008902
420088f2:	3fcb87b7          	lui	a5,0x3fcb8
420088f6:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
420088fa:	1f400713          	li	a4,500
420088fe:	18e7ae23          	sw	a4,412(a5)
42008902:	3fcb87b7          	lui	a5,0x3fcb8
42008906:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200890a:	1a07a703          	lw	a4,416(a5)
4200890e:	03c00793          	li	a5,60
42008912:	00e7f963          	bgeu	a5,a4,0x42008924
42008916:	3fcb87b7          	lui	a5,0x3fcb8
4200891a:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200891e:	4715                	li	a4,5
42008920:	1ae7a023          	sw	a4,416(a5)
42008924:	3fcb87b7          	lui	a5,0x3fcb8
42008928:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200892c:	1a47a703          	lw	a4,420(a5)
42008930:	47fd                	li	a5,31
42008932:	00e7f963          	bgeu	a5,a4,0x42008944
42008936:	3fcb87b7          	lui	a5,0x3fcb8
4200893a:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200893e:	477d                	li	a4,31
42008940:	1ae7a223          	sw	a4,420(a5)
42008944:	3fcb87b7          	lui	a5,0x3fcb8
42008948:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200894c:	1a87a703          	lw	a4,424(a5)
42008950:	67e5                	lui	a5,0x19
42008952:	00e7fb63          	bgeu	a5,a4,0x42008968
42008956:	3fcb87b7          	lui	a5,0x3fcb8
4200895a:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
4200895e:	6745                	lui	a4,0x11
42008960:	fcf70713          	addi	a4,a4,-49 # 0x10fcf
42008964:	1ae7a423          	sw	a4,424(a5)
42008968:	3fcb87b7          	lui	a5,0x3fcb8
4200896c:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
42008970:	1ac7a703          	lw	a4,428(a5)
42008974:	67e5                	lui	a5,0x19
42008976:	00e7fb63          	bgeu	a5,a4,0x4200898c
4200897a:	3fcb87b7          	lui	a5,0x3fcb8
4200897e:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
42008982:	6765                	lui	a4,0x19
42008984:	8af70713          	addi	a4,a4,-1873 # 0x188af
42008988:	1ae7a623          	sw	a4,428(a5)
4200898c:	3fcb87b7          	lui	a5,0x3fcb8
42008990:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
42008994:	1b07a703          	lw	a4,432(a5)
42008998:	67e5                	lui	a5,0x19
4200899a:	00e7fb63          	bgeu	a5,a4,0x420089b0
4200899e:	3fcb87b7          	lui	a5,0x3fcb8
420089a2:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
420089a6:	6755                	lui	a4,0x15
420089a8:	6ce70713          	addi	a4,a4,1742 # 0x156ce
420089ac:	1ae7a823          	sw	a4,432(a5)
420089b0:	3fcb87b7          	lui	a5,0x3fcb8
420089b4:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
420089b8:	1b47a703          	lw	a4,436(a5)
420089bc:	67e5                	lui	a5,0x19
420089be:	00e7fb63          	bgeu	a5,a4,0x420089d4
420089c2:	3fcb87b7          	lui	a5,0x3fcb8
420089c6:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
420089ca:	6741                	lui	a4,0x10
420089cc:	39970713          	addi	a4,a4,921 # 0x10399
420089d0:	1ae7aa23          	sw	a4,436(a5)
420089d4:	3fcb87b7          	lui	a5,0x3fcb8
420089d8:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
420089dc:	1b87a703          	lw	a4,440(a5)
420089e0:	67e5                	lui	a5,0x19
420089e2:	00e7fb63          	bgeu	a5,a4,0x420089f8
420089e6:	3fcb87b7          	lui	a5,0x3fcb8
420089ea:	b9c78793          	addi	a5,a5,-1124 # 0x3fcb7b9c
420089ee:	6755                	lui	a4,0x15
420089f0:	ecd70713          	addi	a4,a4,-307 # 0x14ecd
420089f4:	1ae7ac23          	sw	a4,440(a5)
420089f8:	40b2                	lw	ra,12(sp)
420089fa:	4422                	lw	s0,8(sp)
420089fc:	0141                	addi	sp,sp,16
420089fe:	8082                	ret
