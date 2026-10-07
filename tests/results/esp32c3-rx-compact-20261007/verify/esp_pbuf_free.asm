
idf\esp32c3-oled-native\build-rx-owner\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4208ee34 <esp_pbuf_free>:
4208ee34:	1141                	addi	sp,sp,-16
4208ee36:	c422                	sw	s0,8(sp)
4208ee38:	4d0c                	lw	a1,24(a0)
4208ee3a:	842a                	mv	s0,a0
4208ee3c:	4948                	lw	a0,20(a0)
4208ee3e:	c606                	sw	ra,12(sp)
4208ee40:	9d1970ef          	jal	42026810 <__wrap_esp_netif_free_rx_buffer>
4208ee44:	8522                	mv	a0,s0
4208ee46:	4422                	lw	s0,8(sp)
4208ee48:	40b2                	lw	ra,12(sp)
4208ee4a:	0141                	addi	sp,sp,16
4208ee4c:	e7cef06f          	j	4207e4c8 <mem_free>
