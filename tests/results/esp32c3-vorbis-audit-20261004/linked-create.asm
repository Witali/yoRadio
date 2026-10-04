


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42045e2e <vorbis_dsp_create>:
42045e2e:	7179                	addi	sp,sp,-48
42045e30:	d226                	sw	s1,36(sp)
42045e32:	3c12a4b7          	lui	s1,0x3c12a
42045e36:	ce4e                	sw	s3,28(sp)
42045e38:	05000613          	li	a2,80
42045e3c:	89aa                	mv	s3,a0
42045e3e:	4585                	li	a1,1
42045e40:	5d048513          	addi	a0,s1,1488 # 3c12a5d0 <_esp_trace_encoder_array_end+0xa4b0>
42045e44:	d04a                	sw	s2,32(sp)
42045e46:	c85a                	sw	s6,16(sp)
42045e48:	d606                	sw	ra,44(sp)
42045e4a:	d422                	sw	s0,40(sp)
42045e4c:	cafcc0ef          	jal	42012afa <__wrap_media_lib_module_calloc>
42045e50:	0049a783          	lw	a5,4(s3)
42045e54:	01c9a903          	lw	s2,28(s3)
42045e58:	01352023          	sw	s3,0(a0)
42045e5c:	00279613          	slli	a2,a5,0x2
42045e60:	8b2a                	mv	s6,a0
42045e62:	0ec05263          	blez	a2,42045f46 <vorbis_dsp_create+0x118>
42045e66:	4585                	li	a1,1
42045e68:	5d048513          	addi	a0,s1,1488
42045e6c:	c8fcc0ef          	jal	42012afa <__wrap_media_lib_module_calloc>
42045e70:	0049a783          	lw	a5,4(s3)
42045e74:	00ab2e23          	sw	a0,28(s6)
42045e78:	00279613          	slli	a2,a5,0x2
42045e7c:	0cc05963          	blez	a2,42045f4e <vorbis_dsp_create+0x120>
42045e80:	4585                	li	a1,1
42045e82:	5d048513          	addi	a0,s1,1488
42045e86:	c75cc0ef          	jal	42012afa <__wrap_media_lib_module_calloc>
42045e8a:	0049a783          	lw	a5,4(s3)
42045e8e:	02ab2023          	sw	a0,32(s6)
42045e92:	5d048493          	addi	s1,s1,1488
42045e96:	4401                	li	s0,0
42045e98:	06f05263          	blez	a5,42045efc <vorbis_dsp_create+0xce>
42045e9c:	cc52                	sw	s4,24(sp)
42045e9e:	ca56                	sw	s5,20(sp)
42045ea0:	c65e                	sw	s7,12(sp)
42045ea2:	00492783          	lw	a5,4(s2)
42045ea6:	01cb2a83          	lw	s5,28(s6)
42045eaa:	00241b93          	slli	s7,s0,0x2
42045eae:	4017d613          	srai	a2,a5,0x1
42045eb2:	060a                	slli	a2,a2,0x2
42045eb4:	4585                	li	a1,1
42045eb6:	8526                	mv	a0,s1
42045eb8:	9ade                	add	s5,s5,s7
42045eba:	4701                	li	a4,0
42045ebc:	00c05763          	blez	a2,42045eca <vorbis_dsp_create+0x9c>
42045ec0:	c3bcc0ef          	jal	42012afa <__wrap_media_lib_module_calloc>
42045ec4:	00492783          	lw	a5,4(s2)
42045ec8:	872a                	mv	a4,a0
42045eca:	020b2a03          	lw	s4,32(s6)
42045ece:	ffc7f613          	andi	a2,a5,-4
42045ed2:	00eaa023          	sw	a4,0(s5)
42045ed6:	4585                	li	a1,1
42045ed8:	8526                	mv	a0,s1
42045eda:	9a5e                	add	s4,s4,s7
42045edc:	4781                	li	a5,0
42045ede:	00c05563          	blez	a2,42045ee8 <vorbis_dsp_create+0xba>
42045ee2:	c19cc0ef          	jal	42012afa <__wrap_media_lib_module_calloc>
42045ee6:	87aa                	mv	a5,a0
42045ee8:	0049a703          	lw	a4,4(s3)
42045eec:	0405                	addi	s0,s0,1
42045eee:	00fa2023          	sw	a5,0(s4)
42045ef2:	fae448e3          	blt	s0,a4,42045ea2 <vorbis_dsp_create+0x74>
42045ef6:	4a62                	lw	s4,24(sp)
42045ef8:	4ad2                	lw	s5,20(sp)
42045efa:	4bb2                	lw	s7,12(sp)
42045efc:	000b2783          	lw	a5,0(s6)
42045f00:	020b2623          	sw	zero,44(s6)
42045f04:	020b2823          	sw	zero,48(s6)
42045f08:	c795                	beqz	a5,42045f34 <vorbis_dsp_create+0x106>
42045f0a:	4fdc                	lw	a5,28(a5)
42045f0c:	c785                	beqz	a5,42045f34 <vorbis_dsp_create+0x106>
42045f0e:	577d                	li	a4,-1
42045f10:	57fd                	li	a5,-1
42045f12:	56fd                	li	a3,-1
42045f14:	02db2423          	sw	a3,40(s6)
42045f18:	02db2223          	sw	a3,36(s6)
42045f1c:	02eb2c23          	sw	a4,56(s6)
42045f20:	02fb2e23          	sw	a5,60(s6)
42045f24:	04eb2023          	sw	a4,64(s6)
42045f28:	04fb2223          	sw	a5,68(s6)
42045f2c:	04eb2423          	sw	a4,72(s6)
42045f30:	04fb2623          	sw	a5,76(s6)
42045f34:	50b2                	lw	ra,44(sp)
42045f36:	5422                	lw	s0,40(sp)
42045f38:	5492                	lw	s1,36(sp)
42045f3a:	5902                	lw	s2,32(sp)
42045f3c:	49f2                	lw	s3,28(sp)
42045f3e:	855a                	mv	a0,s6
42045f40:	4b42                	lw	s6,16(sp)
42045f42:	6145                	addi	sp,sp,48
42045f44:	8082                	ret
42045f46:	00052e23          	sw	zero,28(a0)
42045f4a:	4501                	li	a0,0
42045f4c:	b789                	j	42045e8e <vorbis_dsp_create+0x60>
42045f4e:	4501                	li	a0,0
42045f50:	bf3d                	j	42045e8e <vorbis_dsp_create+0x60>
