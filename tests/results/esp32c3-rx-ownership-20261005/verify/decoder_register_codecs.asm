
idf\esp32c3-oled-native\build-rx-owner\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

4201278a <decoder_register_codecs>:
4201278a:	1101                	addi	sp,sp,-32
4201278c:	ce06                	sw	ra,28(sp)
4201278e:	2af3c0ef          	jal	4204f23c <esp_mp3_dec_register>
42012792:	c911                	beqz	a0,420127a6 <decoder_register_codecs+0x1c>
42012794:	c62a                	sw	a0,12(sp)
42012796:	5f2240ef          	jal	42036d88 <esp_audio_simple_dec_unregister_default>
4201279a:	14d270ef          	jal	4203a0e6 <esp_audio_dec_unregister_all>
4201279e:	4532                	lw	a0,12(sp)
420127a0:	40f2                	lw	ra,28(sp)
420127a2:	6105                	addi	sp,sp,32
420127a4:	8082                	ret
420127a6:	352280ef          	jal	4203aaf8 <esp_aac_dec_register>
420127aa:	f56d                	bnez	a0,42012794 <decoder_register_codecs+0xa>
420127ac:	2a7130ef          	jal	42026252 <__wrap_esp_vorbis_dec_register>
420127b0:	f175                	bnez	a0,42012794 <decoder_register_codecs+0xa>
420127b2:	334350ef          	jal	42047ae6 <esp_opus_dec_register>
420127b6:	fd79                	bnez	a0,42012794 <decoder_register_codecs+0xa>
420127b8:	5cc240ef          	jal	42036d84 <esp_audio_simple_dec_register_default>
420127bc:	d175                	beqz	a0,420127a0 <decoder_register_codecs+0x16>
420127be:	bfd9                	j	42012794 <decoder_register_codecs+0xa>
