
idf\esp32c3-oled-native\build-pipeline-profile\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42012b74 <decoder_register_codecs>:
42012b74:	1101                	addi	sp,sp,-32
42012b76:	ce06                	sw	ra,28(sp)
42012b78:	26a3e0ef          	jal	42050de2 <esp_mp3_dec_register>
42012b7c:	c911                	beqz	a0,42012b90 <decoder_register_codecs+0x1c>
42012b7e:	c62a                	sw	a0,12(sp)
42012b80:	5af250ef          	jal	4203892e <esp_audio_simple_dec_unregister_default>
42012b84:	108290ef          	jal	4203bc8c <esp_audio_dec_unregister_all>
42012b88:	4532                	lw	a0,12(sp)
42012b8a:	40f2                	lw	ra,28(sp)
42012b8c:	6105                	addi	sp,sp,32
42012b8e:	8082                	ret
42012b90:	30f290ef          	jal	4203c69e <esp_aac_dec_register>
42012b94:	f56d                	bnez	a0,42012b7e <decoder_register_codecs+0xa>
42012b96:	31d130ef          	jal	420266b2 <__wrap_esp_vorbis_dec_register>
42012b9a:	f175                	bnez	a0,42012b7e <decoder_register_codecs+0xa>
42012b9c:	2f1360ef          	jal	4204968c <esp_opus_dec_register>
42012ba0:	fd79                	bnez	a0,42012b7e <decoder_register_codecs+0xa>
42012ba2:	589250ef          	jal	4203892a <esp_audio_simple_dec_register_default>
42012ba6:	d175                	beqz	a0,42012b8a <decoder_register_codecs+0x16>
42012ba8:	bfd9                	j	42012b7e <decoder_register_codecs+0xa>
