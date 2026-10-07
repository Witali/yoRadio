
idf\esp32c3-oled-native\build-connect-retry\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420263ea <__wrap_esp_vorbis_dec_register>:
420263ea:	3c1405b7          	lui	a1,0x3c140
420263ee:	53425537          	lui	a0,0x53425
420263f2:	44858593          	addi	a1,a1,1096 # 3c140448 <operations.0>
420263f6:	f5650513          	addi	a0,a0,-170 # 53424f56 <_rtc_reserved_end+0x3422f56>
420263fa:	44e1506f          	j	4203b848 <esp_audio_dec_register>
