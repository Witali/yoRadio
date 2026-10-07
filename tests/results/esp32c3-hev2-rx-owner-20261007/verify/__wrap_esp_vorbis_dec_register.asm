
idf\esp32c3-oled-native\build-rx-owner\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420262da <__wrap_esp_vorbis_dec_register>:
420262da:	3c1405b7          	lui	a1,0x3c140
420262de:	53425537          	lui	a0,0x53425
420262e2:	5c858593          	addi	a1,a1,1480 # 3c1405c8 <operations.0>
420262e6:	f5650513          	addi	a0,a0,-170 # 53424f56 <_rtc_reserved_end+0x3422f56>
420262ea:	09f1506f          	j	4203bb88 <esp_audio_dec_register>
