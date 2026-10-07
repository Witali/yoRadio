
idf\esp32c3-oled-native\build-output-staged\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4201255a <decoder_register_codecs>:
4201255a:	1101                	addi	sp,sp,-32
4201255c:	ce06                	sw	ra,28(sp)
4201255e:	07e3c0ef          	jal	4204e5dc <esp_mp3_dec_register>
42012562:	c911                	beqz	a0,42012576 <decoder_register_codecs+0x1c>
42012564:	c62a                	sw	a0,12(sp)
42012566:	3c3230ef          	jal	42036128 <esp_audio_simple_dec_unregister_default>
4201256a:	71d260ef          	jal	42039486 <esp_audio_dec_unregister_all>
4201256e:	4532                	lw	a0,12(sp)
42012570:	40f2                	lw	ra,28(sp)
42012572:	6105                	addi	sp,sp,32
42012574:	8082                	ret
42012576:	123270ef          	jal	42039e98 <esp_aac_dec_register>
4201257a:	f56d                	bnez	a0,42012564 <decoder_register_codecs+0xa>
4201257c:	4c6130ef          	jal	42025a42 <__wrap_esp_vorbis_dec_register>
42012580:	f175                	bnez	a0,42012564 <decoder_register_codecs+0xa>
42012582:	105340ef          	jal	42046e86 <esp_opus_dec_register>
42012586:	fd79                	bnez	a0,42012564 <decoder_register_codecs+0xa>
42012588:	39d230ef          	jal	42036124 <esp_audio_simple_dec_register_default>
4201258c:	d175                	beqz	a0,42012570 <decoder_register_codecs+0x16>
4201258e:	bfd9                	j	42012564 <decoder_register_codecs+0xa>
