
idf\esp32c3-oled-native\build-output-dma\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42025b1e <__wrap_esp_vorbis_dec_register>:
42025b1e:	3c1405b7          	lui	a1,0x3c140
42025b22:	53425537          	lui	a0,0x53425
42025b26:	41058593          	addi	a1,a1,1040 # 3c140410 <operations.0>
42025b2a:	f5650513          	addi	a0,a0,-170 # 53424f56 <_rtc_reserved_end+0x3422f56>
42025b2e:	0b91306f          	j	420393e6 <esp_audio_dec_register>
