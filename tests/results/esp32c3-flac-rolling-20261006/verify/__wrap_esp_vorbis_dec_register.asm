
idf\esp32c3-oled-native\build-flac-predictor\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026184 <__wrap_esp_vorbis_dec_register>:
42026184:	3c1405b7          	lui	a1,0x3c140
42026188:	53425537          	lui	a0,0x53425
4202618c:	41858593          	addi	a1,a1,1048 # 3c140418 <operations.0>
42026190:	f5650513          	addi	a0,a0,-170 # 53424f56 <_rtc_reserved_end+0x3422f56>
42026194:	01f1506f          	j	4203b9b2 <esp_audio_dec_register>
