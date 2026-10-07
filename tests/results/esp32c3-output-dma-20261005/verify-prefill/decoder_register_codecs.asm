
idf\esp32c3-oled-native\build-output-dma-leased\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42012634 <decoder_register_codecs>:
42012634:	1101                	addi	sp,sp,-32
42012636:	ce06                	sw	ra,28(sp)
42012638:	6603c0ef          	jal	4204ec98 <esp_mp3_dec_register>
4201263c:	c911                	beqz	a0,42012650 <decoder_register_codecs+0x1c>
4201263e:	c62a                	sw	a0,12(sp)
42012640:	1a4240ef          	jal	420367e4 <esp_audio_simple_dec_unregister_default>
42012644:	4fe270ef          	jal	42039b42 <esp_audio_dec_unregister_all>
42012648:	4532                	lw	a0,12(sp)
4201264a:	40f2                	lw	ra,28(sp)
4201264c:	6105                	addi	sp,sp,32
4201264e:	8082                	ret
42012650:	705270ef          	jal	4203a554 <esp_aac_dec_register>
42012654:	f56d                	bnez	a0,4201263e <decoder_register_codecs+0xa>
42012656:	2a7130ef          	jal	420260fc <__wrap_esp_vorbis_dec_register>
4201265a:	f175                	bnez	a0,4201263e <decoder_register_codecs+0xa>
4201265c:	6e7340ef          	jal	42047542 <esp_opus_dec_register>
42012660:	fd79                	bnez	a0,4201263e <decoder_register_codecs+0xa>
42012662:	17e240ef          	jal	420367e0 <esp_audio_simple_dec_register_default>
42012666:	d175                	beqz	a0,4201264a <decoder_register_codecs+0x16>
42012668:	bfd9                	j	4201263e <decoder_register_codecs+0xa>
