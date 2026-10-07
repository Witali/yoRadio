
idf\esp32c3-oled-native\build-pipeline-profile\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420266b2 <__wrap_esp_vorbis_dec_register>:
420266b2:	3c1405b7          	lui	a1,0x3c140
420266b6:	53425537          	lui	a0,0x53425
420266ba:	5f858593          	addi	a1,a1,1528 # 3c1405f8 <operations.0>
420266be:	f5650513          	addi	a0,a0,-170 # 53424f56 <_rtc_reserved_end+0x3422f56>
420266c2:	44e1506f          	j	4203bb10 <esp_audio_dec_register>
