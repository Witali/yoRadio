
idf\esp32c3-oled-native\build-connect-retry\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420128ee <decoder_register_codecs>:
420128ee:	1101                	addi	sp,sp,-32
420128f0:	ce06                	sw	ra,28(sp)
420128f2:	2283e0ef          	jal	42050b1a <esp_mp3_dec_register>
420128f6:	c911                	beqz	a0,4201290a <decoder_register_codecs+0x1c>
420128f8:	c62a                	sw	a0,12(sp)
420128fa:	56d250ef          	jal	42038666 <esp_audio_simple_dec_unregister_default>
420128fe:	0c6290ef          	jal	4203b9c4 <esp_audio_dec_unregister_all>
42012902:	4532                	lw	a0,12(sp)
42012904:	40f2                	lw	ra,28(sp)
42012906:	6105                	addi	sp,sp,32
42012908:	8082                	ret
4201290a:	2cd290ef          	jal	4203c3d6 <esp_aac_dec_register>
4201290e:	f56d                	bnez	a0,420128f8 <decoder_register_codecs+0xa>
42012910:	2db130ef          	jal	420263ea <__wrap_esp_vorbis_dec_register>
42012914:	f175                	bnez	a0,420128f8 <decoder_register_codecs+0xa>
42012916:	2af360ef          	jal	420493c4 <esp_opus_dec_register>
4201291a:	fd79                	bnez	a0,420128f8 <decoder_register_codecs+0xa>
4201291c:	547250ef          	jal	42038662 <esp_audio_simple_dec_register_default>
42012920:	d175                	beqz	a0,42012904 <decoder_register_codecs+0x16>
42012922:	bfd9                	j	420128f8 <decoder_register_codecs+0xa>
