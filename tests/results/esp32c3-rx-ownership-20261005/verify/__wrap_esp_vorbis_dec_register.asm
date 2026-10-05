
idf\esp32c3-oled-native\build-rx-owner\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026252 <__wrap_esp_vorbis_dec_register>:
42026252:	3c1405b7          	lui	a1,0x3c140
42026256:	53425537          	lui	a0,0x53425
4202625a:	5e858593          	addi	a1,a1,1512 # 3c1405e8 <operations.0>
4202625e:	f5650513          	addi	a0,a0,-170 # 53424f56 <_rtc_reserved_end+0x3422f56>
42026262:	5091306f          	j	42039f6a <esp_audio_dec_register>
