
idf\esp32c3-oled-native\build-vorbis-repair-production\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4201253e <decoder_register_codecs>:
4201253e:	1101                	addi	sp,sp,-32
42012540:	ce06                	sw	ra,28(sp)
42012542:	65f3b0ef          	jal	4204e3a0 <esp_mp3_dec_register>
42012546:	c911                	beqz	a0,4201255a <decoder_register_codecs+0x1c>
42012548:	c62a                	sw	a0,12(sp)
4201254a:	1a3230ef          	jal	42035eec <esp_audio_simple_dec_unregister_default>
4201254e:	4fd260ef          	jal	4203924a <esp_audio_dec_unregister_all>
42012552:	4532                	lw	a0,12(sp)
42012554:	40f2                	lw	ra,28(sp)
42012556:	6105                	addi	sp,sp,32
42012558:	8082                	ret
4201255a:	702270ef          	jal	42039c5c <esp_aac_dec_register>
4201255e:	f56d                	bnez	a0,42012548 <decoder_register_codecs+0xa>
42012560:	4c6130ef          	jal	42025a26 <__wrap_esp_vorbis_dec_register>
42012564:	f175                	bnez	a0,42012548 <decoder_register_codecs+0xa>
42012566:	6e4340ef          	jal	42046c4a <esp_opus_dec_register>
4201256a:	fd79                	bnez	a0,42012548 <decoder_register_codecs+0xa>
4201256c:	17d230ef          	jal	42035ee8 <esp_audio_simple_dec_register_default>
42012570:	d175                	beqz	a0,42012554 <decoder_register_codecs+0x16>
42012572:	bfd9                	j	42012548 <decoder_register_codecs+0xa>
