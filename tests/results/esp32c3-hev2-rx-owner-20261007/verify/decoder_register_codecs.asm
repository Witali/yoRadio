
idf\esp32c3-oled-native\build-rx-owner\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420127d6 <decoder_register_codecs>:
420127d6:	1101                	addi	sp,sp,-32
420127d8:	ce06                	sw	ra,28(sp)
420127da:	6803e0ef          	jal	42050e5a <esp_mp3_dec_register>
420127de:	c911                	beqz	a0,420127f2 <decoder_register_codecs+0x1c>
420127e0:	c62a                	sw	a0,12(sp)
420127e2:	1c4260ef          	jal	420389a6 <esp_audio_simple_dec_unregister_default>
420127e6:	51e290ef          	jal	4203bd04 <esp_audio_dec_unregister_all>
420127ea:	4532                	lw	a0,12(sp)
420127ec:	40f2                	lw	ra,28(sp)
420127ee:	6105                	addi	sp,sp,32
420127f0:	8082                	ret
420127f2:	725290ef          	jal	4203c716 <esp_aac_dec_register>
420127f6:	f56d                	bnez	a0,420127e0 <decoder_register_codecs+0xa>
420127f8:	2e3130ef          	jal	420262da <__wrap_esp_vorbis_dec_register>
420127fc:	f175                	bnez	a0,420127e0 <decoder_register_codecs+0xa>
420127fe:	707360ef          	jal	42049704 <esp_opus_dec_register>
42012802:	fd79                	bnez	a0,420127e0 <decoder_register_codecs+0xa>
42012804:	19e260ef          	jal	420389a2 <esp_audio_simple_dec_register_default>
42012808:	d175                	beqz	a0,420127ec <decoder_register_codecs+0x16>
4201280a:	bfd9                	j	420127e0 <decoder_register_codecs+0xa>
