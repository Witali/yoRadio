
idf\esp32c3-oled-native\build-output-dma-leased\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420260fc <__wrap_esp_vorbis_dec_register>:
420260fc:	3c1405b7          	lui	a1,0x3c140
42026100:	53425537          	lui	a0,0x53425
42026104:	44058593          	addi	a1,a1,1088 # 3c140440 <operations.0>
42026108:	f5650513          	addi	a0,a0,-170 # 53424f56 <_rtc_reserved_end+0x3422f56>
4202610c:	0bb1306f          	j	420399c6 <esp_audio_dec_register>
