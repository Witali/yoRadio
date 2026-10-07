
idf\esp32c3-oled-native\build-output-staged\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42025a56 <process_checked>:
42025a56:	0015b713          	seqz	a4,a1
42025a5a:	00163793          	seqz	a5,a2
42025a5e:	8f5d                	or	a4,a4,a5
42025a60:	e351                	bnez	a4,42025ae4 <process_checked+0x8e>
42025a62:	c149                	beqz	a0,42025ae4 <process_checked+0x8e>
42025a64:	02c52883          	lw	a7,44(a0)
42025a68:	20474737          	lui	a4,0x20474
42025a6c:	74f70713          	addi	a4,a4,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
42025a70:	06e89863          	bne	a7,a4,42025ae0 <process_checked+0x8a>
42025a74:	4558                	lw	a4,12(a0)
42025a76:	7139                	addi	sp,sp,-64
42025a78:	dc22                	sw	s0,56(sp)
42025a7a:	da26                	sw	s1,52(sp)
42025a7c:	d84a                	sw	s2,48(sp)
42025a7e:	d64e                	sw	s3,44(sp)
42025a80:	de06                	sw	ra,60(sp)
42025a82:	01c10893          	addi	a7,sp,28
42025a86:	01022803          	lw	a6,16(tp) # 10 <active_scope>
42025a8a:	893a                	mv	s2,a4
42025a8c:	01122823          	sw	a7,16(tp) # 10 <active_scope>
42025a90:	4958                	lw	a4,20(a0)
42025a92:	4914                	lw	a3,16(a0)
42025a94:	c242                	sw	a6,4(sp)
42025a96:	89ba                	mv	s3,a4
42025a98:	8432                	mv	s0,a2
42025a9a:	84ae                	mv	s1,a1
42025a9c:	00010e23          	sb	zero,28(sp)
42025aa0:	c436                	sw	a3,8(sp)
42025aa2:	c62a                	sw	a0,12(sp)
42025aa4:	4d1100ef          	jal	42036774 <esp_audio_simple_dec_process>
42025aa8:	4812                	lw	a6,4(sp)
42025aaa:	01022823          	sw	a6,16(tp) # 10 <active_scope>
42025aae:	00850713          	addi	a4,a0,8
42025ab2:	ef09                	bnez	a4,42025acc <process_checked+0x76>
42025ab4:	46a2                	lw	a3,8(sp)
42025ab6:	ca99                	beqz	a3,42025acc <process_checked+0x76>
42025ab8:	47b2                	lw	a5,12(sp)
42025aba:	0127a623          	sw	s2,12(a5)
42025abe:	cb94                	sw	a3,16(a5)
42025ac0:	0137aa23          	sw	s3,20(a5)
42025ac4:	0004a623          	sw	zero,12(s1)
42025ac8:	00042623          	sw	zero,12(s0)
42025acc:	01c14783          	lbu	a5,28(sp)
42025ad0:	ef81                	bnez	a5,42025ae8 <process_checked+0x92>
42025ad2:	50f2                	lw	ra,60(sp)
42025ad4:	5462                	lw	s0,56(sp)
42025ad6:	54d2                	lw	s1,52(sp)
42025ad8:	5942                	lw	s2,48(sp)
42025ada:	59b2                	lw	s3,44(sp)
42025adc:	6121                	addi	sp,sp,64
42025ade:	8082                	ret
42025ae0:	4951006f          	j	42036774 <esp_audio_simple_dec_process>
42025ae4:	556d                	li	a0,-5
42025ae6:	8082                	ret
42025ae8:	00042623          	sw	zero,12(s0)
42025aec:	5579                	li	a0,-2
42025aee:	b7d5                	j	42025ad2 <process_checked+0x7c>
