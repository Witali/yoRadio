
idf\esp32c3-oled-native\build-flac-predictor\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42012674 <decoder_register_codecs>:
42012674:	1101                	addi	sp,sp,-32
42012676:	ce06                	sw	ra,28(sp)
42012678:	0333d0ef          	jal	4204feaa <esp_mp3_dec_register>
4201267c:	c911                	beqz	a0,42012690 <decoder_register_codecs+0x1c>
4201267e:	c62a                	sw	a0,12(sp)
42012680:	376250ef          	jal	420379f6 <esp_audio_simple_dec_unregister_default>
42012684:	6d0280ef          	jal	4203ad54 <esp_audio_dec_unregister_all>
42012688:	4532                	lw	a0,12(sp)
4201268a:	40f2                	lw	ra,28(sp)
4201268c:	6105                	addi	sp,sp,32
4201268e:	8082                	ret
42012690:	0d6290ef          	jal	4203b766 <esp_aac_dec_register>
42012694:	f56d                	bnez	a0,4201267e <decoder_register_codecs+0xa>
42012696:	2a7130ef          	jal	4202613c <__wrap_esp_vorbis_dec_register>
4201269a:	f175                	bnez	a0,4201267e <decoder_register_codecs+0xa>
4201269c:	0b8360ef          	jal	42048754 <esp_opus_dec_register>
420126a0:	fd79                	bnez	a0,4201267e <decoder_register_codecs+0xa>
420126a2:	350250ef          	jal	420379f2 <esp_audio_simple_dec_register_default>
420126a6:	d175                	beqz	a0,4201268a <decoder_register_codecs+0x16>
420126a8:	bfd9                	j	4201267e <decoder_register_codecs+0xa>
