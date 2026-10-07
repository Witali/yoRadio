
idf/esp32c3-oled-native/build-pipeline-profile/yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

40381476 <dma_queue_overrun>:
40381476:	3fc8c737          	lui	a4,0x3fc8c
4038147a:	42072783          	lw	a5,1056(a4) # 3fc8c420 <s_dma_overruns>
4038147e:	4501                	li	a0,0
40381480:	0785                	addi	a5,a5,1
40381482:	42f72023          	sw	a5,1056(a4)
40381486:	8082                	ret

Disassembly of section .flash.text:
