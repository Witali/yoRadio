
idf\esp32c3-oled-native\build-rx-copy\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42012c46 <decoder_register_codecs>:
42012c46:	1101                	addi	sp,sp,-32
42012c48:	ce06                	sw	ra,28(sp)
42012c4a:	0bd3e0ef          	jal	42051506 <esp_mp3_dec_register>
42012c4e:	c911                	beqz	a0,42012c62 <decoder_register_codecs+0x1c>
42012c50:	c62a                	sw	a0,12(sp)
42012c52:	400260ef          	jal	42039052 <esp_audio_simple_dec_unregister_default>
42012c56:	75a290ef          	jal	4203c3b0 <esp_audio_dec_unregister_all>
42012c5a:	4532                	lw	a0,12(sp)
42012c5c:	40f2                	lw	ra,28(sp)
42012c5e:	6105                	addi	sp,sp,32
42012c60:	8082                	ret
42012c62:	1602a0ef          	jal	4203cdc2 <esp_aac_dec_register>
42012c66:	f56d                	bnez	a0,42012c50 <decoder_register_codecs+0xa>
42012c68:	4fd130ef          	jal	42026964 <__wrap_esp_vorbis_dec_register>
42012c6c:	f175                	bnez	a0,42012c50 <decoder_register_codecs+0xa>
42012c6e:	142370ef          	jal	42049db0 <esp_opus_dec_register>
42012c72:	fd79                	bnez	a0,42012c50 <decoder_register_codecs+0xa>
42012c74:	3da260ef          	jal	4203904e <esp_audio_simple_dec_register_default>
42012c78:	d175                	beqz	a0,42012c5c <decoder_register_codecs+0x16>
42012c7a:	bfd9                	j	42012c50 <decoder_register_codecs+0xa>
