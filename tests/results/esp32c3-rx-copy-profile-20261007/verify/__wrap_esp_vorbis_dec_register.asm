
idf\esp32c3-oled-native\build-rx-copy\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026964 <__wrap_esp_vorbis_dec_register>:
42026964:	3c1405b7          	lui	a1,0x3c140
42026968:	53425537          	lui	a0,0x53425
4202696c:	62458593          	addi	a1,a1,1572 # 3c140624 <operations.0>
42026970:	f5650513          	addi	a0,a0,-170 # 53424f56 <_rtc_reserved_end+0x3422f56>
42026974:	0c11506f          	j	4203c234 <esp_audio_dec_register>
