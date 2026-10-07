
idf\esp32c3-oled-native\build-rx-owner\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

420127d6 <decoder_register_codecs>:
420127d6:	1101                	addi	sp,sp,-32
420127d8:	ce06                	sw	ra,28(sp)
420127da:	7003e0ef          	jal	42050eda <esp_mp3_dec_register>
420127de:	c911                	beqz	a0,420127f2 <decoder_register_codecs+0x1c>
420127e0:	c62a                	sw	a0,12(sp)
420127e2:	244260ef          	jal	42038a26 <esp_audio_simple_dec_unregister_default>
420127e6:	59e290ef          	jal	4203bd84 <esp_audio_dec_unregister_all>
420127ea:	4532                	lw	a0,12(sp)
420127ec:	40f2                	lw	ra,28(sp)
420127ee:	6105                	addi	sp,sp,32
420127f0:	8082                	ret
420127f2:	7a5290ef          	jal	4203c796 <esp_aac_dec_register>
420127f6:	f56d                	bnez	a0,420127e0 <decoder_register_codecs+0xa>
420127f8:	2e7130ef          	jal	420262de <__wrap_esp_vorbis_dec_register>
420127fc:	f175                	bnez	a0,420127e0 <decoder_register_codecs+0xa>
420127fe:	787360ef          	jal	42049784 <esp_opus_dec_register>
42012802:	fd79                	bnez	a0,420127e0 <decoder_register_codecs+0xa>
42012804:	21e260ef          	jal	42038a22 <esp_audio_simple_dec_register_default>
42012808:	d175                	beqz	a0,420127ec <decoder_register_codecs+0x16>
4201280a:	bfd9                	j	420127e0 <decoder_register_codecs+0xa>
