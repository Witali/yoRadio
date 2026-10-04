
idf\esp32c3-oled-native\build-vorbis-repair-production\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42025a26 <__wrap_esp_vorbis_dec_register>:
42025a26:	3c1405b7          	lui	a1,0x3c140
42025a2a:	53425537          	lui	a0,0x53425
42025a2e:	59458593          	addi	a1,a1,1428 # 3c140594 <operations.0>
42025a32:	f5650513          	addi	a0,a0,-170 # 53424f56 <_rtc_reserved_end+0x3422f56>
42025a36:	6981306f          	j	420390ce <esp_audio_dec_register>
