
C:\Work\yoRadio\.worktree\aac-storage18\idf\esp32c3-oled-native\build-flac-bounds\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42026130 <__wrap_esp_vorbis_dec_register>:
42026130:	3c1405b7          	lui	a1,0x3c140
42026134:	53425537          	lui	a0,0x53425
42026138:	41058593          	addi	a1,a1,1040 # 3c140410 <operations.0>
4202613c:	f5650513          	addi	a0,a0,-170 # 53424f56 <_rtc_reserved_end+0x3422f56>
42026140:	14f1406f          	j	4203aa8e <esp_audio_dec_register>
