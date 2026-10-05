
idf\esp32c3-oled-native\build-heap-fragment\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42012842 <decoder_register_codecs>:
42012842:	1101                	addi	sp,sp,-32
42012844:	ce06                	sw	ra,28(sp)
42012846:	51b3c0ef          	jal	4204f560 <esp_mp3_dec_register>
4201284a:	c911                	beqz	a0,4201285e <decoder_register_codecs+0x1c>
4201284c:	c62a                	sw	a0,12(sp)
4201284e:	05f240ef          	jal	420370ac <esp_audio_simple_dec_unregister_default>
42012852:	3b9270ef          	jal	4203a40a <esp_audio_dec_unregister_all>
42012856:	4532                	lw	a0,12(sp)
42012858:	40f2                	lw	ra,28(sp)
4201285a:	6105                	addi	sp,sp,32
4201285c:	8082                	ret
4201285e:	5be280ef          	jal	4203ae1c <esp_aac_dec_register>
42012862:	f56d                	bnez	a0,4201284c <decoder_register_codecs+0xa>
42012864:	2a7130ef          	jal	4202630a <__wrap_esp_vorbis_dec_register>
42012868:	f175                	bnez	a0,4201284c <decoder_register_codecs+0xa>
4201286a:	5a0350ef          	jal	42047e0a <esp_opus_dec_register>
4201286e:	fd79                	bnez	a0,4201284c <decoder_register_codecs+0xa>
42012870:	039240ef          	jal	420370a8 <esp_audio_simple_dec_register_default>
42012874:	d175                	beqz	a0,42012858 <decoder_register_codecs+0x16>
42012876:	bfd9                	j	4201284c <decoder_register_codecs+0xa>
