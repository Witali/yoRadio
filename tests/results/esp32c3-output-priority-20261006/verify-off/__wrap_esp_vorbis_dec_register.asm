
idf\esp32c3-oled-native\build-flac-predictor\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4202617c <__wrap_esp_vorbis_dec_register>:
4202617c:	3c1405b7          	lui	a1,0x3c140
42026180:	53425537          	lui	a0,0x53425
42026184:	41858593          	addi	a1,a1,1048 # 3c140418 <operations.0>
42026188:	f5650513          	addi	a0,a0,-170 # 53424f56 <_rtc_reserved_end+0x3422f56>
4202618c:	4501506f          	j	4203b5dc <esp_audio_dec_register>
