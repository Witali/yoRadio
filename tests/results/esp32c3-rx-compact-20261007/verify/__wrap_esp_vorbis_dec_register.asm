
idf\esp32c3-oled-native\build-rx-owner\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420262de <__wrap_esp_vorbis_dec_register>:
420262de:	3c1405b7          	lui	a1,0x3c140
420262e2:	53425537          	lui	a0,0x53425
420262e6:	55058593          	addi	a1,a1,1360 # 3c140550 <operations.0>
420262ea:	f5650513          	addi	a0,a0,-170 # 53424f56 <_rtc_reserved_end+0x3422f56>
420262ee:	11b1506f          	j	4203bc08 <esp_audio_dec_register>
