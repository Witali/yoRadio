
idf\esp32c3-oled-native\build-rx-copy\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4201267c <decoder_register_codecs>:
4201267c:	1101                	addi	sp,sp,-32
4201267e:	ce06                	sw	ra,28(sp)
42012680:	22a3e0ef          	jal	420508aa <esp_mp3_dec_register>
42012684:	c911                	beqz	a0,42012698 <decoder_register_codecs+0x1c>
42012686:	c62a                	sw	a0,12(sp)
42012688:	56f250ef          	jal	420383f6 <esp_audio_simple_dec_unregister_default>
4201268c:	0c8290ef          	jal	4203b754 <esp_audio_dec_unregister_all>
42012690:	4532                	lw	a0,12(sp)
42012692:	40f2                	lw	ra,28(sp)
42012694:	6105                	addi	sp,sp,32
42012696:	8082                	ret
42012698:	2cf290ef          	jal	4203c166 <esp_aac_dec_register>
4201269c:	f56d                	bnez	a0,42012686 <decoder_register_codecs+0xa>
4201269e:	2db130ef          	jal	42026178 <__wrap_esp_vorbis_dec_register>
420126a2:	f175                	bnez	a0,42012686 <decoder_register_codecs+0xa>
420126a4:	2b1360ef          	jal	42049154 <esp_opus_dec_register>
420126a8:	fd79                	bnez	a0,42012686 <decoder_register_codecs+0xa>
420126aa:	549250ef          	jal	420383f2 <esp_audio_simple_dec_register_default>
420126ae:	d175                	beqz	a0,42012692 <decoder_register_codecs+0x16>
420126b0:	bfd9                	j	42012686 <decoder_register_codecs+0xa>
