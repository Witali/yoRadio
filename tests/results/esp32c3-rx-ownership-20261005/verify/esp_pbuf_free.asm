
idf\esp32c3-oled-native\build-rx-owner\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4208d196 <esp_pbuf_free>:
4208d196:	1141                	addi	sp,sp,-16
4208d198:	c422                	sw	s0,8(sp)
4208d19a:	4d0c                	lw	a1,24(a0)
4208d19c:	842a                	mv	s0,a0
4208d19e:	4948                	lw	a0,20(a0)
4208d1a0:	c606                	sw	ra,12(sp)
4208d1a2:	de2990ef          	jal	42026784 <__wrap_esp_netif_free_rx_buffer>
4208d1a6:	8522                	mv	a0,s0
4208d1a8:	4422                	lw	s0,8(sp)
4208d1aa:	40b2                	lw	ra,12(sp)
4208d1ac:	0141                	addi	sp,sp,16
4208d1ae:	e7cef06f          	j	4207c82a <mem_free>
