
idf\esp32c3-oled-native\build-custom-terminal\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026110 <__wrap_esp_vorbis_dec_register>:
42026110:	3c1405b7          	lui	a1,0x3c140
42026114:	53425537          	lui	a0,0x53425
42026118:	43858593          	addi	a1,a1,1080 # 3c140438 <operations.0>
4202611c:	f5650513          	addi	a0,a0,-170 # 53424f56 <_rtc_reserved_end+0x3422f56>
42026120:	0bb1306f          	j	420399da <esp_audio_dec_register>
