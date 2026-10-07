


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42045bf2 <esp_vorbis_dec_open>:
42045bf2:	ff058713          	addi	a4,a1,-16
42045bf6:	711d                	addi	sp,sp,-96
42045bf8:	00e03733          	snez	a4,a4
42045bfc:	00163793          	seqz	a5,a2
42045c00:	c8ca                	sw	s2,80(sp)
42045c02:	c4d2                	sw	s4,72(sp)
42045c04:	ce86                	sw	ra,92(sp)
42045c06:	caa6                	sw	s1,84(sp)
42045c08:	8fd9                	or	a5,a5,a4
42045c0a:	8a32                	mv	s4,a2
42045c0c:	892a                	mv	s2,a0
42045c0e:	10079b63          	bnez	a5,42045d24 <esp_vorbis_dec_open+0x132>
42045c12:	10050963          	beqz	a0,42045d24 <esp_vorbis_dec_open+0x132>
42045c16:	c6ce                	sw	s3,76(sp)
42045c18:	3c12a9b7          	lui	s3,0x3c12a
42045c1c:	5d098513          	addi	a0,s3,1488 # 3c12a5d0 <_esp_trace_encoder_array_end+0xa4b0>
42045c20:	03000613          	li	a2,48
42045c24:	4585                	li	a1,1
42045c26:	cca2                	sw	s0,88(sp)
42045c28:	ed3cc0ef          	jal	42012afa <__wrap_media_lib_module_calloc>
42045c2c:	842a                	mv	s0,a0
42045c2e:	54f9                	li	s1,-2
42045c30:	cd49                	beqz	a0,42045cca <esp_vorbis_dec_open+0xd8>
42045c32:	5d098513          	addi	a0,s3,1488
42045c36:	02000613          	li	a2,32
42045c3a:	4585                	li	a1,1
42045c3c:	ebfcc0ef          	jal	42012afa <__wrap_media_lib_module_calloc>
42045c40:	89aa                	mv	s3,a0
42045c42:	cd21                	beqz	a0,42045c9a <esp_vorbis_dec_open+0xa8>
42045c44:	2785                	jal	420463a4 <vorbis_info_init>
42045c46:	1024                	addi	s1,sp,40
42045c48:	0838                	addi	a4,sp,24
42045c4a:	4781                	li	a5,0
42045c4c:	d402                	sw	zero,40(sp)
42045c4e:	dc02                	sw	zero,56(sp)
42045c50:	de02                	sw	zero,60(sp)
42045c52:	ce02                	sw	zero,28(sp)
42045c54:	d202                	sw	zero,36(sp)
42045c56:	cc26                	sw	s1,24(sp)
42045c58:	da3a                	sw	a4,52(sp)
42045c5a:	c3c9                	beqz	a5,42045cdc <esp_vorbis_dec_open+0xea>
42045c5c:	00c92783          	lw	a5,12(s2)
42045c60:	00892703          	lw	a4,8(s2)
42045c64:	85a6                	mv	a1,s1
42045c66:	854e                	mv	a0,s3
42045c68:	d03e                	sw	a5,32(sp)
42045c6a:	d83e                	sw	a5,48(sp)
42045c6c:	d63a                	sw	a4,44(sp)
42045c6e:	175000ef          	jal	420465e2 <_vorbis_unpack_books>
42045c72:	84aa                	mv	s1,a0
42045c74:	e159                	bnez	a0,42045cfa <esp_vorbis_dec_open+0x108>
42045c76:	854e                	mv	a0,s3
42045c78:	2a5d                	jal	42045e2e <vorbis_dsp_create>
42045c7a:	c519                	beqz	a0,42045c88 <esp_vorbis_dec_open+0x96>
42045c7c:	c008                	sw	a0,0(s0)
42045c7e:	008a2023          	sw	s0,0(s4)
42045c82:	49b6                	lw	s3,76(sp)
42045c84:	4466                	lw	s0,88(sp)
42045c86:	a81d                	j	42045cbc <esp_vorbis_dec_open+0xca>
42045c88:	54f9                	li	s1,-2
42045c8a:	854e                	mv	a0,s3
42045c8c:	2fb1                	jal	420463e8 <vorbis_info_clear>
42045c8e:	854e                	mv	a0,s3
42045c90:	f47cc0ef          	jal	42012bd6 <__wrap_media_lib_free>
42045c94:	8522                	mv	a0,s0
42045c96:	f41cc0ef          	jal	42012bd6 <__wrap_media_lib_free>
42045c9a:	4008                	lw	a0,0(s0)
42045c9c:	c919                	beqz	a0,42045cb2 <esp_vorbis_dec_open+0xc0>
42045c9e:	00052903          	lw	s2,0(a0)
42045ca2:	2c45                	jal	42045f52 <vorbis_dsp_destroy>
42045ca4:	00090763          	beqz	s2,42045cb2 <esp_vorbis_dec_open+0xc0>
42045ca8:	854a                	mv	a0,s2
42045caa:	2f3d                	jal	420463e8 <vorbis_info_clear>
42045cac:	854a                	mv	a0,s2
42045cae:	f29cc0ef          	jal	42012bd6 <__wrap_media_lib_free>
42045cb2:	8522                	mv	a0,s0
42045cb4:	f23cc0ef          	jal	42012bd6 <__wrap_media_lib_free>
42045cb8:	4466                	lw	s0,88(sp)
42045cba:	49b6                	lw	s3,76(sp)
42045cbc:	40f6                	lw	ra,92(sp)
42045cbe:	4946                	lw	s2,80(sp)
42045cc0:	4a26                	lw	s4,72(sp)
42045cc2:	8526                	mv	a0,s1
42045cc4:	44d6                	lw	s1,84(sp)
42045cc6:	6125                	addi	sp,sp,96
42045cc8:	8082                	ret
42045cca:	4466                	lw	s0,88(sp)
42045ccc:	40f6                	lw	ra,92(sp)
42045cce:	49b6                	lw	s3,76(sp)
42045cd0:	4946                	lw	s2,80(sp)
42045cd2:	4a26                	lw	s4,72(sp)
42045cd4:	8526                	mv	a0,s1
42045cd6:	44d6                	lw	s1,84(sp)
42045cd8:	6125                	addi	sp,sp,96
42045cda:	8082                	ret
42045cdc:	00492783          	lw	a5,4(s2)
42045ce0:	00092683          	lw	a3,0(s2)
42045ce4:	85a6                	mv	a1,s1
42045ce6:	854e                	mv	a0,s3
42045ce8:	d03e                	sw	a5,32(sp)
42045cea:	d83e                	sw	a5,48(sp)
42045cec:	d636                	sw	a3,44(sp)
42045cee:	7f8000ef          	jal	420464e6 <_vorbis_unpack_info>
42045cf2:	0838                	addi	a4,sp,24
42045cf4:	e119                	bnez	a0,42045cfa <esp_vorbis_dec_open+0x108>
42045cf6:	4785                	li	a5,1
42045cf8:	bf91                	j	42045c4c <esp_vorbis_dec_open+0x5a>
42045cfa:	fe342097          	auipc	ra,0xfe342
42045cfe:	6c0080e7          	jalr	1728(ra) # 403883ba <esp_log_timestamp>
42045d02:	3c12d737          	lui	a4,0x3c12d
42045d06:	7c470713          	addi	a4,a4,1988 # 3c12d7c4 <_esp_trace_encoder_array_end+0xd6a4>
42045d0a:	3c12e637          	lui	a2,0x3c12e
42045d0e:	86aa                	mv	a3,a0
42045d10:	85ba                	mv	a1,a4
42045d12:	88060613          	addi	a2,a2,-1920 # 3c12d880 <_esp_trace_encoder_array_end+0xd760>
42045d16:	4505                	li	a0,1
42045d18:	fe342097          	auipc	ra,0xfe342
42045d1c:	59a080e7          	jalr	1434(ra) # 403882b2 <esp_log>
42045d20:	54f1                	li	s1,-4
42045d22:	b7a5                	j	42045c8a <esp_vorbis_dec_open+0x98>
42045d24:	c62e                	sw	a1,12(sp)
42045d26:	fe342097          	auipc	ra,0xfe342
42045d2a:	694080e7          	jalr	1684(ra) # 403883ba <esp_log_timestamp>
42045d2e:	48b2                	lw	a7,12(sp)
42045d30:	3c12d737          	lui	a4,0x3c12d
42045d34:	7c470713          	addi	a4,a4,1988 # 3c12d7c4 <_esp_trace_encoder_array_end+0xd6a4>
42045d38:	3c12d637          	lui	a2,0x3c12d
42045d3c:	86aa                	mv	a3,a0
42045d3e:	8852                	mv	a6,s4
42045d40:	87ca                	mv	a5,s2
42045d42:	85ba                	mv	a1,a4
42045d44:	5d860613          	addi	a2,a2,1496 # 3c12d5d8 <_esp_trace_encoder_array_end+0xd4b8>
42045d48:	4505                	li	a0,1
42045d4a:	fe342097          	auipc	ra,0xfe342
42045d4e:	568080e7          	jalr	1384(ra) # 403882b2 <esp_log>
42045d52:	54ed                	li	s1,-5
42045d54:	b7a5                	j	42045cbc <esp_vorbis_dec_open+0xca>
