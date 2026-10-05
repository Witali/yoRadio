
idf\esp32c3-oled-native\build-heap-fragment\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4202630a <__wrap_esp_vorbis_dec_register>:
4202630a:	3c1405b7          	lui	a1,0x3c140
4202630e:	53425537          	lui	a0,0x53425
42026312:	60058593          	addi	a1,a1,1536 # 3c140600 <operations.0>
42026316:	f5650513          	addi	a0,a0,-170 # 53424f56 <_rtc_reserved_end+0x3422f56>
4202631a:	7751306f          	j	4203a28e <esp_audio_dec_register>
