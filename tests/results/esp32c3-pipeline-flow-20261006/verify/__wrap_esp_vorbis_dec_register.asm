
idf\esp32c3-oled-native\build-pipeline-profile\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026686 <__wrap_esp_vorbis_dec_register>:
42026686:	3c1405b7          	lui	a1,0x3c140
4202668a:	53425537          	lui	a0,0x53425
4202668e:	5a058593          	addi	a1,a1,1440 # 3c1405a0 <operations.0>
42026692:	f5650513          	addi	a0,a0,-170 # 53424f56 <_rtc_reserved_end+0x3422f56>
42026696:	44e1506f          	j	4203bae4 <esp_audio_dec_register>
