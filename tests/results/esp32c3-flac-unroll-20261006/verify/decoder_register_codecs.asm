
idf\esp32c3-oled-native\build-flac-predictor\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42012678 <decoder_register_codecs>:
42012678:	1101                	addi	sp,sp,-32
4201267a:	ce06                	sw	ra,28(sp)
4201267c:	44f3d0ef          	jal	420502ca <esp_mp3_dec_register>
42012680:	c911                	beqz	a0,42012694 <decoder_register_codecs+0x1c>
42012682:	c62a                	sw	a0,12(sp)
42012684:	792250ef          	jal	42037e16 <esp_audio_simple_dec_unregister_default>
42012688:	2ed280ef          	jal	4203b174 <esp_audio_dec_unregister_all>
4201268c:	4532                	lw	a0,12(sp)
4201268e:	40f2                	lw	ra,28(sp)
42012690:	6105                	addi	sp,sp,32
42012692:	8082                	ret
42012694:	4f2290ef          	jal	4203bb86 <esp_aac_dec_register>
42012698:	f56d                	bnez	a0,42012682 <decoder_register_codecs+0xa>
4201269a:	2a7130ef          	jal	42026140 <__wrap_esp_vorbis_dec_register>
4201269e:	f175                	bnez	a0,42012682 <decoder_register_codecs+0xa>
420126a0:	4d4360ef          	jal	42048b74 <esp_opus_dec_register>
420126a4:	fd79                	bnez	a0,42012682 <decoder_register_codecs+0xa>
420126a6:	76c250ef          	jal	42037e12 <esp_audio_simple_dec_register_default>
420126aa:	d175                	beqz	a0,4201268e <decoder_register_codecs+0x16>
420126ac:	bfd9                	j	42012682 <decoder_register_codecs+0xa>
