
C:\Work\yoRadio\.worktree\small-tv-photo-upload-waits\.build\small-tv-esp32c2\small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200f8b4 <photo_upload_start>:
4200f8b4:	1101                	addi	sp,sp,-32
4200f8b6:	ca26                	sw	s1,20(sp)
4200f8b8:	64e5                	lui	s1,0x19
4200f8ba:	ce06                	sw	ra,28(sp)
4200f8bc:	cc22                	sw	s0,24(sp)
4200f8be:	c84a                	sw	s2,16(sp)
4200f8c0:	c64e                	sw	s3,12(sp)
4200f8c2:	c452                	sw	s4,8(sp)
4200f8c4:	c256                	sw	s5,4(sp)
4200f8c6:	ffc58713          	addi	a4,a1,-4
4200f8ca:	ffc48793          	addi	a5,s1,-4 # 18ffc <CSR_UINTSTATUS+0x1834b>
4200f8ce:	0ae7e963          	bltu	a5,a4,4200f980 <photo_upload_start+0xcc>
4200f8d2:	00553793          	sltiu	a5,a0,5
4200f8d6:	c7cd                	beqz	a5,4200f980 <photo_upload_start+0xcc>
4200f8d8:	6905                	lui	s2,0x1
4200f8da:	197d                	addi	s2,s2,-1 # fff <CSR_UINTSTATUS+0x34e>
4200f8dc:	992e                	add	s2,s2,a1
4200f8de:	00c95913          	srli	s2,s2,0xc
4200f8e2:	10200413          	li	s0,258
4200f8e6:	08c91363          	bne	s2,a2,4200f96c <photo_upload_start+0xb8>
4200f8ea:	3fcb4ab7          	lui	s5,0x3fcb4
4200f8ee:	89aa                	mv	s3,a0
4200f8f0:	908aa503          	lw	a0,-1784(s5) # 3fcb3908 <media_mutex>
4200f8f4:	8a2e                	mv	s4,a1
4200f8f6:	55fd                	li	a1,-1
4200f8f8:	0709d0ef          	jal	420ac968 <xQueueSemaphoreTake>
4200f8fc:	f6bff0ef          	jal	4200f866 <photo_upload_active_unlocked>
4200f900:	10300413          	li	s0,259
4200f904:	ed29                	bnez	a0,4200f95e <photo_upload_start+0xaa>
4200f906:	4581                	li	a1,0
4200f908:	854e                	mv	a0,s3
4200f90a:	d27fc0ef          	jal	4200c630 <settings_photo_size>
4200f90e:	842a                	mv	s0,a0
4200f910:	e539                	bnez	a0,4200f95e <photo_upload_start+0xaa>
4200f912:	029985b3          	mul	a1,s3,s1
4200f916:	3fcb47b7          	lui	a5,0x3fcb4
4200f91a:	90c7a503          	lw	a0,-1780(a5) # 3fcb390c <media_partition>
4200f91e:	8626                	mv	a2,s1
4200f920:	054080ef          	jal	42017974 <esp_partition_erase_range>
4200f924:	842a                	mv	s0,a0
4200f926:	ed05                	bnez	a0,4200f95e <photo_upload_start+0xaa>
4200f928:	3fcb04b7          	lui	s1,0x3fcb0
4200f92c:	a8048493          	addi	s1,s1,-1408 # 3fcafa80 <upload>
4200f930:	02000613          	li	a2,32
4200f934:	4581                	li	a1,0
4200f936:	8526                	mv	a0,s1
4200f938:	fdff1097          	auipc	ra,0xfdff1
4200f93c:	b50080e7          	jalr	-1200(ra) # 40000488 <memset>
4200f940:	4785                	li	a5,1
4200f942:	00f48023          	sb	a5,0(s1)
4200f946:	0134a223          	sw	s3,4(s1)
4200f94a:	0144a823          	sw	s4,16(s1)
4200f94e:	0124a423          	sw	s2,8(s1)
4200f952:	fe372097          	auipc	ra,0xfe372
4200f956:	224080e7          	jalr	548(ra) # 40381b76 <esp_timer_get_time>
4200f95a:	cc88                	sw	a0,24(s1)
4200f95c:	cccc                	sw	a1,28(s1)
4200f95e:	908aa503          	lw	a0,-1784(s5)
4200f962:	4681                	li	a3,0
4200f964:	4601                	li	a2,0
4200f966:	4581                	li	a1,0
4200f968:	3e19c0ef          	jal	420ac548 <xQueueGenericSend>
4200f96c:	40f2                	lw	ra,28(sp)
4200f96e:	8522                	mv	a0,s0
4200f970:	4462                	lw	s0,24(sp)
4200f972:	44d2                	lw	s1,20(sp)
4200f974:	4942                	lw	s2,16(sp)
4200f976:	49b2                	lw	s3,12(sp)
4200f978:	4a22                	lw	s4,8(sp)
4200f97a:	4a92                	lw	s5,4(sp)
4200f97c:	6105                	addi	sp,sp,32
4200f97e:	8082                	ret
4200f980:	10200413          	li	s0,258
4200f984:	b7e5                	j	4200f96c <photo_upload_start+0xb8>


C:\Work\yoRadio\.worktree\small-tv-photo-upload-waits\.build\small-tv-esp32c2\small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200f986 <photo_upload_chunk>:
4200f986:	7159                	addi	sp,sp,-112
4200f988:	ccd2                	sw	s4,88(sp)
4200f98a:	3fcb4a37          	lui	s4,0x3fcb4
4200f98e:	d0ca                	sw	s2,96(sp)
4200f990:	892a                	mv	s2,a0
4200f992:	908a2503          	lw	a0,-1784(s4) # 3fcb3908 <media_mutex>
4200f996:	cad6                	sw	s5,84(sp)
4200f998:	8aae                	mv	s5,a1
4200f99a:	55fd                	li	a1,-1
4200f99c:	d686                	sw	ra,108(sp)
4200f99e:	cece                	sw	s3,92(sp)
4200f9a0:	c8da                	sw	s6,80(sp)
4200f9a2:	d4a2                	sw	s0,104(sp)
4200f9a4:	d2a6                	sw	s1,100(sp)
4200f9a6:	c632                	sw	a2,12(sp)
4200f9a8:	8b36                	mv	s6,a3
4200f9aa:	89ba                	mv	s3,a4
4200f9ac:	7bd9c0ef          	jal	420ac968 <xQueueSemaphoreTake>
4200f9b0:	eb7ff0ef          	jal	4200f866 <photo_upload_active_unlocked>
4200f9b4:	0e050e63          	beqz	a0,4200fab0 <photo_upload_chunk+0x12a>
4200f9b8:	3fcb0437          	lui	s0,0x3fcb0
4200f9bc:	a8040413          	addi	s0,s0,-1408 # 3fcafa80 <upload>
4200f9c0:	405c                	lw	a5,4(s0)
4200f9c2:	10200493          	li	s1,258
4200f9c6:	07279163          	bne	a5,s2,4200fa28 <photo_upload_chunk+0xa2>
4200f9ca:	441c                	lw	a5,8(s0)
4200f9cc:	4632                	lw	a2,12(sp)
4200f9ce:	0ec79163          	bne	a5,a2,4200fab0 <photo_upload_chunk+0x12a>
4200f9d2:	0ccaff63          	bgeu	s5,a2,4200fab0 <photo_upload_chunk+0x12a>
4200f9d6:	4818                	lw	a4,16(s0)
4200f9d8:	00ca9793          	slli	a5,s5,0xc
4200f9dc:	6685                	lui	a3,0x1
4200f9de:	8f1d                	sub	a4,a4,a5
4200f9e0:	00e6f363          	bgeu	a3,a4,4200f9e6 <photo_upload_chunk+0x60>
4200f9e4:	8736                	mv	a4,a3
4200f9e6:	10200493          	li	s1,258
4200f9ea:	02e99f63          	bne	s3,a4,4200fa28 <photo_upload_chunk+0xa2>
4200f9ee:	4458                	lw	a4,12(s0)
4200f9f0:	05571e63          	bne	a4,s5,4200fa4c <photo_upload_chunk+0xc6>
4200f9f4:	6765                	lui	a4,0x19
4200f9f6:	02e905b3          	mul	a1,s2,a4
4200f9fa:	86ce                	mv	a3,s3
4200f9fc:	865a                	mv	a2,s6
4200f9fe:	95be                	add	a1,a1,a5
4200fa00:	3fcb47b7          	lui	a5,0x3fcb4
4200fa04:	90c7a503          	lw	a0,-1780(a5) # 3fcb390c <media_partition>
4200fa08:	635070ef          	jal	4201783c <esp_partition_write>
4200fa0c:	84aa                	mv	s1,a0
4200fa0e:	ed09                	bnez	a0,4200fa28 <photo_upload_chunk+0xa2>
4200fa10:	445c                	lw	a5,12(s0)
4200fa12:	0785                	addi	a5,a5,1
4200fa14:	c45c                	sw	a5,12(s0)
4200fa16:	485c                	lw	a5,20(s0)
4200fa18:	97ce                	add	a5,a5,s3
4200fa1a:	c85c                	sw	a5,20(s0)
4200fa1c:	fe372097          	auipc	ra,0xfe372
4200fa20:	15a080e7          	jalr	346(ra) # 40381b76 <esp_timer_get_time>
4200fa24:	cc08                	sw	a0,24(s0)
4200fa26:	cc4c                	sw	a1,28(s0)
4200fa28:	908a2503          	lw	a0,-1784(s4)
4200fa2c:	4681                	li	a3,0
4200fa2e:	4601                	li	a2,0
4200fa30:	4581                	li	a1,0
4200fa32:	3179c0ef          	jal	420ac548 <xQueueGenericSend>
4200fa36:	50b6                	lw	ra,108(sp)
4200fa38:	5426                	lw	s0,104(sp)
4200fa3a:	5906                	lw	s2,96(sp)
4200fa3c:	49f6                	lw	s3,92(sp)
4200fa3e:	4a66                	lw	s4,88(sp)
4200fa40:	4ad6                	lw	s5,84(sp)
4200fa42:	4b46                	lw	s6,80(sp)
4200fa44:	8526                	mv	a0,s1
4200fa46:	5496                	lw	s1,100(sp)
4200fa48:	6165                	addi	sp,sp,112
4200fa4a:	8082                	ret
4200fa4c:	df71                	beqz	a4,4200fa28 <photo_upload_chunk+0xa2>
4200fa4e:	177d                	addi	a4,a4,-1 # 18fff <CSR_UINTSTATUS+0x1834e>
4200fa50:	fd571ce3          	bne	a4,s5,4200fa28 <photo_upload_chunk+0xa2>
4200fa54:	00200737          	lui	a4,0x200
4200fa58:	97ba                	add	a5,a5,a4
4200fa5a:	6765                	lui	a4,0x19
4200fa5c:	02e90933          	mul	s2,s2,a4
4200fa60:	04000a93          	li	s5,64
4200fa64:	012784b3          	add	s1,a5,s2
4200fa68:	4901                	li	s2,0
4200fa6a:	01396a63          	bltu	s2,s3,4200fa7e <photo_upload_chunk+0xf8>
4200fa6e:	fe372097          	auipc	ra,0xfe372
4200fa72:	108080e7          	jalr	264(ra) # 40381b76 <esp_timer_get_time>
4200fa76:	cc08                	sw	a0,24(s0)
4200fa78:	cc4c                	sw	a1,28(s0)
4200fa7a:	4481                	li	s1,0
4200fa7c:	b775                	j	4200fa28 <photo_upload_chunk+0xa2>
4200fa7e:	41298633          	sub	a2,s3,s2
4200fa82:	00caf463          	bgeu	s5,a2,4200fa8a <photo_upload_chunk+0x104>
4200fa86:	04000613          	li	a2,64
4200fa8a:	080c                	addi	a1,sp,16
4200fa8c:	00990533          	add	a0,s2,s1
4200fa90:	c632                	sw	a2,12(sp)
4200fa92:	89dff0ef          	jal	4200f32e <media_read_unlocked>
4200fa96:	ed09                	bnez	a0,4200fab0 <photo_upload_chunk+0x12a>
4200fa98:	4632                	lw	a2,12(sp)
4200fa9a:	012b05b3          	add	a1,s6,s2
4200fa9e:	0808                	addi	a0,sp,16
4200faa0:	fe377097          	auipc	ra,0xfe377
4200faa4:	75c080e7          	jalr	1884(ra) # 403871fc <memcmp>
4200faa8:	e501                	bnez	a0,4200fab0 <photo_upload_chunk+0x12a>
4200faaa:	04090913          	addi	s2,s2,64
4200faae:	bf75                	j	4200fa6a <photo_upload_chunk+0xe4>
4200fab0:	10200493          	li	s1,258
4200fab4:	bf95                	j	4200fa28 <photo_upload_chunk+0xa2>


C:\Work\yoRadio\.worktree\small-tv-photo-upload-waits\.build\small-tv-esp32c2\small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4200fab6 <photo_upload_finish>:
4200fab6:	7135                	addi	sp,sp,-160
4200fab8:	dede                	sw	s7,124(sp)
4200faba:	3fcb4bb7          	lui	s7,0x3fcb4
4200fabe:	c42a                	sw	a0,8(sp)
4200fac0:	908ba503          	lw	a0,-1784(s7) # 3fcb3908 <media_mutex>
4200fac4:	55fd                	li	a1,-1
4200fac6:	cf06                	sw	ra,156(sp)
4200fac8:	cb26                	sw	s1,148(sp)
4200faca:	cd22                	sw	s0,152(sp)
4200facc:	c94a                	sw	s2,144(sp)
4200face:	c74e                	sw	s3,140(sp)
4200fad0:	c552                	sw	s4,136(sp)
4200fad2:	c356                	sw	s5,132(sp)
4200fad4:	c15a                	sw	s6,128(sp)
4200fad6:	dce2                	sw	s8,120(sp)
4200fad8:	dae6                	sw	s9,116(sp)
4200fada:	d8ea                	sw	s10,112(sp)
4200fadc:	d6ee                	sw	s11,108(sp)
4200fade:	68b9c0ef          	jal	420ac968 <xQueueSemaphoreTake>
4200fae2:	d85ff0ef          	jal	4200f866 <photo_upload_active_unlocked>
4200fae6:	10300493          	li	s1,259
4200faea:	12050463          	beqz	a0,4200fc12 <photo_upload_finish+0x15c>
4200faee:	3fcb0437          	lui	s0,0x3fcb0
4200faf2:	a8040413          	addi	s0,s0,-1408 # 3fcafa80 <upload>
4200faf6:	405c                	lw	a5,4(s0)
4200faf8:	4722                	lw	a4,8(sp)
4200fafa:	10300493          	li	s1,259
4200fafe:	10e79a63          	bne	a5,a4,4200fc12 <photo_upload_finish+0x15c>
4200fb02:	4458                	lw	a4,12(s0)
4200fb04:	441c                	lw	a5,8(s0)
4200fb06:	10f71663          	bne	a4,a5,4200fc12 <photo_upload_finish+0x15c>
4200fb0a:	01042903          	lw	s2,16(s0)
4200fb0e:	485c                	lw	a5,20(s0)
4200fb10:	11279163          	bne	a5,s2,4200fc12 <photo_upload_finish+0x15c>
4200fb14:	47a2                	lw	a5,8(sp)
4200fb16:	64e5                	lui	s1,0x19
4200fb18:	8caa                	mv	s9,a0
4200fb1a:	029784b3          	mul	s1,a5,s1
4200fb1e:	002007b7          	lui	a5,0x200
4200fb22:	4609                	li	a2,2
4200fb24:	080c                	addi	a1,sp,16
4200fb26:	94be                	add	s1,s1,a5
4200fb28:	8526                	mv	a0,s1
4200fb2a:	805ff0ef          	jal	4200f32e <media_read_unlocked>
4200fb2e:	ed71                	bnez	a0,4200fc0a <photo_upload_finish+0x154>
4200fb30:	01014b03          	lbu	s6,16(sp)
4200fb34:	0ff00793          	li	a5,255
4200fb38:	0cfb1963          	bne	s6,a5,4200fc0a <photo_upload_finish+0x154>
4200fb3c:	01114703          	lbu	a4,17(sp)
4200fb40:	0d800793          	li	a5,216
4200fb44:	0cf71363          	bne	a4,a5,4200fc0a <photo_upload_finish+0x154>
4200fb48:	3c0d47b7          	lui	a5,0x3c0d4
4200fb4c:	eb078793          	addi	a5,a5,-336 # 3c0d3eb0 <codes.0+0x48>
4200fb50:	4989                	li	s3,2
4200fb52:	4c01                	li	s8,0
4200fb54:	ffe90d13          	addi	s10,s2,-2
4200fb58:	0e000d93          	li	s11,224
4200fb5c:	c63e                	sw	a5,12(sp)
4200fb5e:	00498793          	addi	a5,s3,4
4200fb62:	0af96463          	bltu	s2,a5,4200fc0a <photo_upload_finish+0x154>
4200fb66:	01348a33          	add	s4,s1,s3
4200fb6a:	4611                	li	a2,4
4200fb6c:	080c                	addi	a1,sp,16
4200fb6e:	8552                	mv	a0,s4
4200fb70:	fbeff0ef          	jal	4200f32e <media_read_unlocked>
4200fb74:	e959                	bnez	a0,4200fc0a <photo_upload_finish+0x154>
4200fb76:	01014783          	lbu	a5,16(sp)
4200fb7a:	09679863          	bne	a5,s6,4200fc0a <photo_upload_finish+0x154>
4200fb7e:	01114703          	lbu	a4,17(sp)
4200fb82:	09670463          	beq	a4,s6,4200fc0a <photo_upload_finish+0x154>
4200fb86:	01215683          	lhu	a3,18(sp)
4200fb8a:	0086d793          	srli	a5,a3,0x8
4200fb8e:	06a2                	slli	a3,a3,0x8
4200fb90:	97b6                	add	a5,a5,a3
4200fb92:	01079a93          	slli	s5,a5,0x10
4200fb96:	010ada93          	srli	s5,s5,0x10
4200fb9a:	4785                	li	a5,1
4200fb9c:	0757d763          	bge	a5,s5,4200fc0a <photo_upload_finish+0x154>
4200fba0:	413d06b3          	sub	a3,s10,s3
4200fba4:	0756e363          	bltu	a3,s5,4200fc0a <photo_upload_finish+0x154>
4200fba8:	f0270693          	addi	a3,a4,-254
4200fbac:	ceb9                	beqz	a3,4200fc0a <photo_upload_finish+0x154>
4200fbae:	f1f70693          	addi	a3,a4,-225
4200fbb2:	f3e70613          	addi	a2,a4,-194
4200fbb6:	00f6b693          	sltiu	a3,a3,15
4200fbba:	00163613          	seqz	a2,a2
4200fbbe:	8ed1                	or	a3,a3,a2
4200fbc0:	e6a9                	bnez	a3,4200fc0a <photo_upload_finish+0x154>
4200fbc2:	07b71f63          	bne	a4,s11,4200fc40 <photo_upload_finish+0x18a>
4200fbc6:	473d                	li	a4,15
4200fbc8:	05575163          	bge	a4,s5,4200fc0a <photo_upload_finish+0x154>
4200fbcc:	4615                	li	a2,5
4200fbce:	080c                	addi	a1,sp,16
4200fbd0:	004a0513          	addi	a0,s4,4
4200fbd4:	f5aff0ef          	jal	4200f32e <media_read_unlocked>
4200fbd8:	e90d                	bnez	a0,4200fc0a <photo_upload_finish+0x154>
4200fbda:	45b2                	lw	a1,12(sp)
4200fbdc:	4615                	li	a2,5
4200fbde:	0808                	addi	a0,sp,16
4200fbe0:	fe377097          	auipc	ra,0xfe377
4200fbe4:	61c080e7          	jalr	1564(ra) # 403871fc <memcmp>
4200fbe8:	e10d                	bnez	a0,4200fc0a <photo_upload_finish+0x154>
4200fbea:	ff0a8713          	addi	a4,s5,-16
4200fbee:	ef11                	bnez	a4,4200fc0a <photo_upload_finish+0x154>
4200fbf0:	4609                	li	a2,2
4200fbf2:	080c                	addi	a1,sp,16
4200fbf4:	010a0513          	addi	a0,s4,16
4200fbf8:	f36ff0ef          	jal	4200f32e <media_read_unlocked>
4200fbfc:	e519                	bnez	a0,4200fc0a <photo_upload_finish+0x154>
4200fbfe:	01014703          	lbu	a4,16(sp)
4200fc02:	01114683          	lbu	a3,17(sp)
4200fc06:	8f55                	or	a4,a4,a3
4200fc08:	cb2d                	beqz	a4,4200fc7a <photo_upload_finish+0x1c4>
4200fc0a:	10200493          	li	s1,258
4200fc0e:	00040023          	sb	zero,0(s0)
4200fc12:	908ba503          	lw	a0,-1784(s7)
4200fc16:	4681                	li	a3,0
4200fc18:	4601                	li	a2,0
4200fc1a:	4581                	li	a1,0
4200fc1c:	12d9c0ef          	jal	420ac548 <xQueueGenericSend>
4200fc20:	40fa                	lw	ra,156(sp)
4200fc22:	446a                	lw	s0,152(sp)
4200fc24:	494a                	lw	s2,144(sp)
4200fc26:	49ba                	lw	s3,140(sp)
4200fc28:	4a2a                	lw	s4,136(sp)
4200fc2a:	4a9a                	lw	s5,132(sp)
4200fc2c:	4b0a                	lw	s6,128(sp)
4200fc2e:	5bf6                	lw	s7,124(sp)
4200fc30:	5c66                	lw	s8,120(sp)
4200fc32:	5cd6                	lw	s9,116(sp)
4200fc34:	5d46                	lw	s10,112(sp)
4200fc36:	5db6                	lw	s11,108(sp)
4200fc38:	8526                	mv	a0,s1
4200fc3a:	44da                	lw	s1,148(sp)
4200fc3c:	610d                	addi	sp,sp,160
4200fc3e:	8082                	ret
4200fc40:	0c000693          	li	a3,192
4200fc44:	02d71f63          	bne	a4,a3,4200fc82 <photo_upload_finish+0x1cc>
4200fc48:	471d                	li	a4,7
4200fc4a:	fd5750e3          	bge	a4,s5,4200fc0a <photo_upload_finish+0x154>
4200fc4e:	4615                	li	a2,5
4200fc50:	080c                	addi	a1,sp,16
4200fc52:	004a0513          	addi	a0,s4,4
4200fc56:	ed8ff0ef          	jal	4200f32e <media_read_unlocked>
4200fc5a:	f945                	bnez	a0,4200fc0a <photo_upload_finish+0x154>
4200fc5c:	01014683          	lbu	a3,16(sp)
4200fc60:	4721                	li	a4,8
4200fc62:	fae694e3          	bne	a3,a4,4200fc0a <photo_upload_finish+0x154>
4200fc66:	01115703          	lhu	a4,17(sp)
4200fc6a:	66bd                	lui	a3,0xf
4200fc6c:	f8d71fe3          	bne	a4,a3,4200fc0a <photo_upload_finish+0x154>
4200fc70:	01315683          	lhu	a3,19(sp)
4200fc74:	f8e69be3          	bne	a3,a4,4200fc0a <photo_upload_finish+0x154>
4200fc78:	8c66                	mv	s8,s9
4200fc7a:	002a8793          	addi	a5,s5,2
4200fc7e:	99be                	add	s3,s3,a5
4200fc80:	bdf9                	j	4200fb5e <photo_upload_finish+0xa8>
4200fc82:	0da00693          	li	a3,218
4200fc86:	fed71ae3          	bne	a4,a3,4200fc7a <photo_upload_finish+0x1c4>
4200fc8a:	f80c00e3          	beqz	s8,4200fc0a <photo_upload_finish+0x154>
4200fc8e:	002a8793          	addi	a5,s5,2
4200fc92:	99be                	add	s3,s3,a5
4200fc94:	4b01                	li	s6,0
4200fc96:	04000c93          	li	s9,64
4200fc9a:	02010c13          	addi	s8,sp,32
4200fc9e:	0ff00d13          	li	s10,255
4200fca2:	4d9d                	li	s11,7
4200fca4:	f729f3e3          	bgeu	s3,s2,4200fc0a <photo_upload_finish+0x154>
4200fca8:	41390a33          	sub	s4,s2,s3
4200fcac:	014cf463          	bgeu	s9,s4,4200fcb4 <photo_upload_finish+0x1fe>
4200fcb0:	04000a13          	li	s4,64
4200fcb4:	8652                	mv	a2,s4
4200fcb6:	85e2                	mv	a1,s8
4200fcb8:	01348533          	add	a0,s1,s3
4200fcbc:	e72ff0ef          	jal	4200f32e <media_read_unlocked>
4200fcc0:	f529                	bnez	a0,4200fc0a <photo_upload_finish+0x154>
4200fcc2:	4701                	li	a4,0
4200fcc4:	00ec07b3          	add	a5,s8,a4
4200fcc8:	0007c783          	lbu	a5,0(a5)
4200fccc:	000b1b63          	bnez	s6,4200fce2 <photo_upload_finish+0x22c>
4200fcd0:	f0178793          	addi	a5,a5,-255
4200fcd4:	0017bb13          	seqz	s6,a5
4200fcd8:	0705                	addi	a4,a4,1
4200fcda:	feea15e3          	bne	s4,a4,4200fcc4 <photo_upload_finish+0x20e>
4200fcde:	99d2                	add	s3,s3,s4
4200fce0:	b7d1                	j	4200fca4 <photo_upload_finish+0x1ee>
4200fce2:	ffa78be3          	beq	a5,s10,4200fcd8 <photo_upload_finish+0x222>
4200fce6:	cf8d                	beqz	a5,4200fd20 <photo_upload_finish+0x26a>
4200fce8:	f3078693          	addi	a3,a5,-208
4200fcec:	02ddfa63          	bgeu	s11,a3,4200fd20 <photo_upload_finish+0x26a>
4200fcf0:	0d900693          	li	a3,217
4200fcf4:	f0d79be3          	bne	a5,a3,4200fc0a <photo_upload_finish+0x154>
4200fcf8:	0985                	addi	s3,s3,1
4200fcfa:	99ba                	add	s3,s3,a4
4200fcfc:	f13917e3          	bne	s2,s3,4200fc0a <photo_upload_finish+0x154>
4200fd00:	480c                	lw	a1,16(s0)
4200fd02:	0f000693          	li	a3,240
4200fd06:	8526                	mv	a0,s1
4200fd08:	8636                	mv	a2,a3
4200fd0a:	ff6ff0ef          	jal	4200f500 <media_validate_jpeg_unlocked>
4200fd0e:	84aa                	mv	s1,a0
4200fd10:	ee051fe3          	bnez	a0,4200fc0e <photo_upload_finish+0x158>
4200fd14:	480c                	lw	a1,16(s0)
4200fd16:	4522                	lw	a0,8(sp)
4200fd18:	919fc0ef          	jal	4200c630 <settings_photo_size>
4200fd1c:	84aa                	mv	s1,a0
4200fd1e:	bdc5                	j	4200fc0e <photo_upload_finish+0x158>
4200fd20:	4b01                	li	s6,0
4200fd22:	bf5d                	j	4200fcd8 <photo_upload_finish+0x222>


C:\Work\yoRadio\.worktree\small-tv-photo-upload-waits\.build\small-tv-esp32c2\small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42012e3c <web_photo_post>:
42012e3c:	7139                	addi	sp,sp,-64
42012e3e:	3c0b55b7          	lui	a1,0x3c0b5
42012e42:	da26                	sw	s1,52(sp)
42012e44:	82458593          	addi	a1,a1,-2012 # 3c0b4824 <_esp_libc_clock_array_end+0x46d4>
42012e48:	84aa                	mv	s1,a0
42012e4a:	0521                	addi	a0,a0,8
42012e4c:	de06                	sw	ra,60(sp)
42012e4e:	dc22                	sw	s0,56(sp)
42012e50:	d84a                	sw	s2,48(sp)
42012e52:	d64e                	sw	s3,44(sp)
42012e54:	fe374097          	auipc	ra,0xfe374
42012e58:	7fe080e7          	jalr	2046(ra) # 40387652 <strcmp>
42012e5c:	e911                	bnez	a0,42012e70 <web_photo_post+0x34>
42012e5e:	5462                	lw	s0,56(sp)
42012e60:	50f2                	lw	ra,60(sp)
42012e62:	5942                	lw	s2,48(sp)
42012e64:	59b2                	lw	s3,44(sp)
42012e66:	8526                	mv	a0,s1
42012e68:	54d2                	lw	s1,52(sp)
42012e6a:	6121                	addi	sp,sp,64
42012e6c:	9c3ff06f          	j	4201282e <upload_multipart>
42012e70:	8526                	mv	a0,s1
42012e72:	d5dfe0ef          	jal	42011bce <web_parse_json>
42012e76:	892a                	mv	s2,a0
42012e78:	ed11                	bnez	a0,42012e94 <web_photo_post+0x58>
42012e7a:	5462                	lw	s0,56(sp)
42012e7c:	50f2                	lw	ra,60(sp)
42012e7e:	5942                	lw	s2,48(sp)
42012e80:	59b2                	lw	s3,44(sp)
42012e82:	8526                	mv	a0,s1
42012e84:	54d2                	lw	s1,52(sp)
42012e86:	3c0b55b7          	lui	a1,0x3c0b5
42012e8a:	b8058593          	addi	a1,a1,-1152 # 3c0b4b80 <_esp_libc_clock_array_end+0x4a30>
42012e8e:	6121                	addi	sp,sp,64
42012e90:	b71fe06f          	j	42011a00 <web_error>
42012e94:	3c0b55b7          	lui	a1,0x3c0b5
42012e98:	0038                	addi	a4,sp,8
42012e9a:	4695                	li	a3,5
42012e9c:	4605                	li	a2,1
42012e9e:	abc58593          	addi	a1,a1,-1348 # 3c0b4abc <_esp_libc_clock_array_end+0x496c>
42012ea2:	d79fe0ef          	jal	42011c1a <web_integer>
42012ea6:	10200413          	li	s0,258
42012eaa:	c90d                	beqz	a0,42012edc <web_photo_post+0xa0>
42012eac:	3c0b55b7          	lui	a1,0x3c0b5
42012eb0:	83458593          	addi	a1,a1,-1996 # 3c0b4834 <_esp_libc_clock_array_end+0x46e4>
42012eb4:	00848513          	addi	a0,s1,8
42012eb8:	fe374097          	auipc	ra,0xfe374
42012ebc:	79a080e7          	jalr	1946(ra) # 40387652 <strcmp>
42012ec0:	ed39                	bnez	a0,42012f1e <web_photo_post+0xe2>
42012ec2:	3c0b55b7          	lui	a1,0x3c0b5
42012ec6:	0078                	addi	a4,sp,12
42012ec8:	66e5                	lui	a3,0x19
42012eca:	4611                	li	a2,4
42012ecc:	b9858593          	addi	a1,a1,-1128 # 3c0b4b98 <_esp_libc_clock_array_end+0x4a48>
42012ed0:	854a                	mv	a0,s2
42012ed2:	d49fe0ef          	jal	42011c1a <web_integer>
42012ed6:	e10d                	bnez	a0,42012ef8 <web_photo_post+0xbc>
42012ed8:	10200413          	li	s0,258
42012edc:	854a                	mv	a0,s2
42012ede:	375010ef          	jal	42014a52 <cJSON_Delete>
42012ee2:	ec41                	bnez	s0,42012f7a <web_photo_post+0x13e>
42012ee4:	8526                	mv	a0,s1
42012ee6:	b53fe0ef          	jal	42011a38 <web_ok>
42012eea:	50f2                	lw	ra,60(sp)
42012eec:	5462                	lw	s0,56(sp)
42012eee:	54d2                	lw	s1,52(sp)
42012ef0:	5942                	lw	s2,48(sp)
42012ef2:	59b2                	lw	s3,44(sp)
42012ef4:	6121                	addi	sp,sp,64
42012ef6:	8082                	ret
42012ef8:	3c0b55b7          	lui	a1,0x3c0b5
42012efc:	0818                	addi	a4,sp,16
42012efe:	46e5                	li	a3,25
42012f00:	4605                	li	a2,1
42012f02:	ad458593          	addi	a1,a1,-1324 # 3c0b4ad4 <_esp_libc_clock_array_end+0x4984>
42012f06:	854a                	mv	a0,s2
42012f08:	d13fe0ef          	jal	42011c1a <web_integer>
42012f0c:	d571                	beqz	a0,42012ed8 <web_photo_post+0x9c>
42012f0e:	4522                	lw	a0,8(sp)
42012f10:	4642                	lw	a2,16(sp)
42012f12:	45b2                	lw	a1,12(sp)
42012f14:	157d                	addi	a0,a0,-1
42012f16:	99ffc0ef          	jal	4200f8b4 <photo_upload_start>
42012f1a:	842a                	mv	s0,a0
42012f1c:	b7c1                	j	42012edc <web_photo_post+0xa0>
42012f1e:	3c0b55b7          	lui	a1,0x3c0b5
42012f22:	81458593          	addi	a1,a1,-2028 # 3c0b4814 <_esp_libc_clock_array_end+0x46c4>
42012f26:	00848513          	addi	a0,s1,8
42012f2a:	fe374097          	auipc	ra,0xfe374
42012f2e:	728080e7          	jalr	1832(ra) # 40387652 <strcmp>
42012f32:	f54d                	bnez	a0,42012edc <web_photo_post+0xa0>
42012f34:	3c0b55b7          	lui	a1,0x3c0b5
42012f38:	ba458593          	addi	a1,a1,-1116 # 3c0b4ba4 <_esp_libc_clock_array_end+0x4a54>
42012f3c:	854a                	mv	a0,s2
42012f3e:	05c020ef          	jal	42014f9a <cJSON_GetObjectItemCaseSensitive>
42012f42:	46a2                	lw	a3,8(sp)
42012f44:	45c1                	li	a1,16
42012f46:	3c0b5637          	lui	a2,0x3c0b5
42012f4a:	89aa                	mv	s3,a0
42012f4c:	bb060613          	addi	a2,a2,-1104 # 3c0b4bb0 <_esp_libc_clock_array_end+0x4a60>
42012f50:	00b10533          	add	a0,sp,a1
42012f54:	3ac8b0ef          	jal	4209e300 <snprintf>
42012f58:	854e                	mv	a0,s3
42012f5a:	23e020ef          	jal	42015198 <cJSON_IsString>
42012f5e:	dd3d                	beqz	a0,42012edc <web_photo_post+0xa0>
42012f60:	0109a503          	lw	a0,16(s3)
42012f64:	080c                	addi	a1,sp,16
42012f66:	fe374097          	auipc	ra,0xfe374
42012f6a:	6ec080e7          	jalr	1772(ra) # 40387652 <strcmp>
42012f6e:	f53d                	bnez	a0,42012edc <web_photo_post+0xa0>
42012f70:	4522                	lw	a0,8(sp)
42012f72:	157d                	addi	a0,a0,-1
42012f74:	b43fc0ef          	jal	4200fab6 <photo_upload_finish>
42012f78:	b74d                	j	42012f1a <web_photo_post+0xde>
42012f7a:	3c0b55b7          	lui	a1,0x3c0b5
42012f7e:	bbc58593          	addi	a1,a1,-1092 # 3c0b4bbc <_esp_libc_clock_array_end+0x4a6c>
42012f82:	8526                	mv	a0,s1
42012f84:	a7dfe0ef          	jal	42011a00 <web_error>
42012f88:	b78d                	j	42012eea <web_photo_post+0xae>
