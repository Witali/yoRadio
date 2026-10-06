
idf\esp32c3-oled-native\build-pipeline-profile\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42012b48 <decoder_register_codecs>:
42012b48:	1101                	addi	sp,sp,-32
42012b4a:	ce06                	sw	ra,28(sp)
42012b4c:	26a3e0ef          	jal	42050db6 <esp_mp3_dec_register>
42012b50:	c911                	beqz	a0,42012b64 <decoder_register_codecs+0x1c>
42012b52:	c62a                	sw	a0,12(sp)
42012b54:	5af250ef          	jal	42038902 <esp_audio_simple_dec_unregister_default>
42012b58:	108290ef          	jal	4203bc60 <esp_audio_dec_unregister_all>
42012b5c:	4532                	lw	a0,12(sp)
42012b5e:	40f2                	lw	ra,28(sp)
42012b60:	6105                	addi	sp,sp,32
42012b62:	8082                	ret
42012b64:	30f290ef          	jal	4203c672 <esp_aac_dec_register>
42012b68:	f56d                	bnez	a0,42012b52 <decoder_register_codecs+0xa>
42012b6a:	31d130ef          	jal	42026686 <__wrap_esp_vorbis_dec_register>
42012b6e:	f175                	bnez	a0,42012b52 <decoder_register_codecs+0xa>
42012b70:	2f1360ef          	jal	42049660 <esp_opus_dec_register>
42012b74:	fd79                	bnez	a0,42012b52 <decoder_register_codecs+0xa>
42012b76:	589250ef          	jal	420388fe <esp_audio_simple_dec_register_default>
42012b7a:	d175                	beqz	a0,42012b5e <decoder_register_codecs+0x16>
42012b7c:	bfd9                	j	42012b52 <decoder_register_codecs+0xa>
