
idf\esp32c3-oled-native\build-custom-terminal\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42012648 <decoder_register_codecs>:
42012648:	1101                	addi	sp,sp,-32
4201264a:	ce06                	sw	ra,28(sp)
4201264c:	6603c0ef          	jal	4204ecac <esp_mp3_dec_register>
42012650:	c911                	beqz	a0,42012664 <decoder_register_codecs+0x1c>
42012652:	c62a                	sw	a0,12(sp)
42012654:	1a4240ef          	jal	420367f8 <esp_audio_simple_dec_unregister_default>
42012658:	4fe270ef          	jal	42039b56 <esp_audio_dec_unregister_all>
4201265c:	4532                	lw	a0,12(sp)
4201265e:	40f2                	lw	ra,28(sp)
42012660:	6105                	addi	sp,sp,32
42012662:	8082                	ret
42012664:	705270ef          	jal	4203a568 <esp_aac_dec_register>
42012668:	f56d                	bnez	a0,42012652 <decoder_register_codecs+0xa>
4201266a:	2a7130ef          	jal	42026110 <__wrap_esp_vorbis_dec_register>
4201266e:	f175                	bnez	a0,42012652 <decoder_register_codecs+0xa>
42012670:	6e7340ef          	jal	42047556 <esp_opus_dec_register>
42012674:	fd79                	bnez	a0,42012652 <decoder_register_codecs+0xa>
42012676:	17e240ef          	jal	420367f4 <esp_audio_simple_dec_register_default>
4201267a:	d175                	beqz	a0,4201265e <decoder_register_codecs+0x16>
4201267c:	bfd9                	j	42012652 <decoder_register_codecs+0xa>
