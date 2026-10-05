
idf\esp32c3-oled-native\build-output-dma\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42025b32 <process_checked>:
42025b32:	0015b713          	seqz	a4,a1
42025b36:	00163793          	seqz	a5,a2
42025b3a:	8f5d                	or	a4,a4,a5
42025b3c:	e351                	bnez	a4,42025bc0 <process_checked+0x8e>
42025b3e:	c149                	beqz	a0,42025bc0 <process_checked+0x8e>
42025b40:	02c52883          	lw	a7,44(a0)
42025b44:	20474737          	lui	a4,0x20474
42025b48:	74f70713          	addi	a4,a4,1871 # 2047474f <CSR_UINTSTATUS+0x20473a9e>
42025b4c:	06e89863          	bne	a7,a4,42025bbc <process_checked+0x8a>
42025b50:	4558                	lw	a4,12(a0)
42025b52:	7139                	addi	sp,sp,-64
42025b54:	dc22                	sw	s0,56(sp)
42025b56:	da26                	sw	s1,52(sp)
42025b58:	d84a                	sw	s2,48(sp)
42025b5a:	d64e                	sw	s3,44(sp)
42025b5c:	de06                	sw	ra,60(sp)
42025b5e:	01c10893          	addi	a7,sp,28
42025b62:	01022803          	lw	a6,16(tp) # 10 <active_scope>
42025b66:	893a                	mv	s2,a4
42025b68:	01122823          	sw	a7,16(tp) # 10 <active_scope>
42025b6c:	4958                	lw	a4,20(a0)
42025b6e:	4914                	lw	a3,16(a0)
42025b70:	c242                	sw	a6,4(sp)
42025b72:	89ba                	mv	s3,a4
42025b74:	8432                	mv	s0,a2
42025b76:	84ae                	mv	s1,a1
42025b78:	00010e23          	sb	zero,28(sp)
42025b7c:	c436                	sw	a3,8(sp)
42025b7e:	c62a                	sw	a0,12(sp)
42025b80:	4d1100ef          	jal	42036850 <esp_audio_simple_dec_process>
42025b84:	4812                	lw	a6,4(sp)
42025b86:	01022823          	sw	a6,16(tp) # 10 <active_scope>
42025b8a:	00850713          	addi	a4,a0,8
42025b8e:	ef09                	bnez	a4,42025ba8 <process_checked+0x76>
42025b90:	46a2                	lw	a3,8(sp)
42025b92:	ca99                	beqz	a3,42025ba8 <process_checked+0x76>
42025b94:	47b2                	lw	a5,12(sp)
42025b96:	0127a623          	sw	s2,12(a5)
42025b9a:	cb94                	sw	a3,16(a5)
42025b9c:	0137aa23          	sw	s3,20(a5)
42025ba0:	0004a623          	sw	zero,12(s1)
42025ba4:	00042623          	sw	zero,12(s0)
42025ba8:	01c14783          	lbu	a5,28(sp)
42025bac:	ef81                	bnez	a5,42025bc4 <process_checked+0x92>
42025bae:	50f2                	lw	ra,60(sp)
42025bb0:	5462                	lw	s0,56(sp)
42025bb2:	54d2                	lw	s1,52(sp)
42025bb4:	5942                	lw	s2,48(sp)
42025bb6:	59b2                	lw	s3,44(sp)
42025bb8:	6121                	addi	sp,sp,64
42025bba:	8082                	ret
42025bbc:	4951006f          	j	42036850 <esp_audio_simple_dec_process>
42025bc0:	556d                	li	a0,-5
42025bc2:	8082                	ret
42025bc4:	00042623          	sw	zero,12(s0)
42025bc8:	5579                	li	a0,-2
42025bca:	b7d5                	j	42025bae <process_checked+0x7c>
