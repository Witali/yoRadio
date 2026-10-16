
small_tv_reconstructed.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4201176e <advanced_page>:
4201176e:	3c0b45b7          	lui	a1,0x3c0b4
42011772:	1141                	addi	sp,sp,-16
42011774:	4e458593          	addi	a1,a1,1252 # 3c0b44e4 <_esp_libc_clock_array_end+0x4394>
42011778:	c422                	sw	s0,8(sp)
4201177a:	c606                	sw	ra,12(sp)
4201177c:	842a                	mv	s0,a0
4201177e:	17f270ef          	jal	420390fc <httpd_resp_set_type>
42011782:	8522                	mv	a0,s0
42011784:	4422                	lw	s0,8(sp)
42011786:	40b2                	lw	ra,12(sp)
42011788:	6605                	lui	a2,0x1
4201178a:	3c0eb5b7          	lui	a1,0x3c0eb
4201178e:	89f60613          	addi	a2,a2,-1889 # 89f <ALIGN_VECTOR_TABLE+0x79f>
42011792:	9fc58593          	addi	a1,a1,-1540 # 3c0ea9fc <html.0>
42011796:	0141                	addi	sp,sp,16
42011798:	1d12706f          	j	42039168 <httpd_resp_send>
