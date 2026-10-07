
idf\esp32c3-oled-native\build-rx-owner\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4208edb4 <esp_pbuf_free>:
4208edb4:	1141                	addi	sp,sp,-16
4208edb6:	c422                	sw	s0,8(sp)
4208edb8:	4d0c                	lw	a1,24(a0)
4208edba:	842a                	mv	s0,a0
4208edbc:	4948                	lw	a0,20(a0)
4208edbe:	c606                	sw	ra,12(sp)
4208edc0:	a4d970ef          	jal	4202680c <__wrap_esp_netif_free_rx_buffer>
4208edc4:	8522                	mv	a0,s0
4208edc6:	4422                	lw	s0,8(sp)
4208edc8:	40b2                	lw	ra,12(sp)
4208edca:	0141                	addi	sp,sp,16
4208edcc:	e7cef06f          	j	4207e448 <mem_free>
