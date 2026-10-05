
idf\esp32c3-oled-native\build-output-staged\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42025a42 <__wrap_esp_vorbis_dec_register>:
42025a42:	3c1405b7          	lui	a1,0x3c140
42025a46:	53425537          	lui	a0,0x53425
42025a4a:	58458593          	addi	a1,a1,1412 # 3c140584 <operations.0>
42025a4e:	f5650513          	addi	a0,a0,-170 # 53424f56 <_rtc_reserved_end+0x3422f56>
42025a52:	0b91306f          	j	4203930a <esp_audio_dec_register>
