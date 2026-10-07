
idf\esp32c3-oled-native\build-flac-predictor\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42012680 <decoder_register_codecs>:
42012680:	1101                	addi	sp,sp,-32
42012682:	ce06                	sw	ra,28(sp)
42012684:	22a3e0ef          	jal	420508ae <esp_mp3_dec_register>
42012688:	c911                	beqz	a0,4201269c <decoder_register_codecs+0x1c>
4201268a:	c62a                	sw	a0,12(sp)
4201268c:	56f250ef          	jal	420383fa <esp_audio_simple_dec_unregister_default>
42012690:	0c8290ef          	jal	4203b758 <esp_audio_dec_unregister_all>
42012694:	4532                	lw	a0,12(sp)
42012696:	40f2                	lw	ra,28(sp)
42012698:	6105                	addi	sp,sp,32
4201269a:	8082                	ret
4201269c:	2cf290ef          	jal	4203c16a <esp_aac_dec_register>
420126a0:	f56d                	bnez	a0,4201268a <decoder_register_codecs+0xa>
420126a2:	2db130ef          	jal	4202617c <__wrap_esp_vorbis_dec_register>
420126a6:	f175                	bnez	a0,4201268a <decoder_register_codecs+0xa>
420126a8:	2b1360ef          	jal	42049158 <esp_opus_dec_register>
420126ac:	fd79                	bnez	a0,4201268a <decoder_register_codecs+0xa>
420126ae:	549250ef          	jal	420383f6 <esp_audio_simple_dec_register_default>
420126b2:	d175                	beqz	a0,42012696 <decoder_register_codecs+0x16>
420126b4:	bfd9                	j	4201268a <decoder_register_codecs+0xa>
