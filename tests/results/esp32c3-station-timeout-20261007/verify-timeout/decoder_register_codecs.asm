
idf\esp32c3-oled-native\build-connect-retry\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42012bf2 <decoder_register_codecs>:
42012bf2:	1101                	addi	sp,sp,-32
42012bf4:	ce06                	sw	ra,28(sp)
42012bf6:	4483e0ef          	jal	4205103e <esp_mp3_dec_register>
42012bfa:	c911                	beqz	a0,42012c0e <decoder_register_codecs+0x1c>
42012bfc:	c62a                	sw	a0,12(sp)
42012bfe:	78d250ef          	jal	42038b8a <esp_audio_simple_dec_unregister_default>
42012c02:	2e6290ef          	jal	4203bee8 <esp_audio_dec_unregister_all>
42012c06:	4532                	lw	a0,12(sp)
42012c08:	40f2                	lw	ra,28(sp)
42012c0a:	6105                	addi	sp,sp,32
42012c0c:	8082                	ret
42012c0e:	4ed290ef          	jal	4203c8fa <esp_aac_dec_register>
42012c12:	f56d                	bnez	a0,42012bfc <decoder_register_codecs+0xa>
42012c14:	4f9130ef          	jal	4202690c <__wrap_esp_vorbis_dec_register>
42012c18:	f175                	bnez	a0,42012bfc <decoder_register_codecs+0xa>
42012c1a:	4cf360ef          	jal	420498e8 <esp_opus_dec_register>
42012c1e:	fd79                	bnez	a0,42012bfc <decoder_register_codecs+0xa>
42012c20:	767250ef          	jal	42038b86 <esp_audio_simple_dec_register_default>
42012c24:	d175                	beqz	a0,42012c08 <decoder_register_codecs+0x16>
42012c26:	bfd9                	j	42012bfc <decoder_register_codecs+0xa>
