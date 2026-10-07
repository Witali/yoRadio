
C:\Work\yoRadio\.worktree\aac-storage18\idf\esp32c3-oled-native\build-flac-bounds\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42012668 <decoder_register_codecs>:
42012668:	1101                	addi	sp,sp,-32
4201266a:	ce06                	sw	ra,28(sp)
4201266c:	6f43d0ef          	jal	4204fd60 <esp_mp3_dec_register>
42012670:	c911                	beqz	a0,42012684 <decoder_register_codecs+0x1c>
42012672:	c62a                	sw	a0,12(sp)
42012674:	238250ef          	jal	420378ac <esp_audio_simple_dec_unregister_default>
42012678:	592280ef          	jal	4203ac0a <esp_audio_dec_unregister_all>
4201267c:	4532                	lw	a0,12(sp)
4201267e:	40f2                	lw	ra,28(sp)
42012680:	6105                	addi	sp,sp,32
42012682:	8082                	ret
42012684:	799280ef          	jal	4203b61c <esp_aac_dec_register>
42012688:	f56d                	bnez	a0,42012672 <decoder_register_codecs+0xa>
4201268a:	2a7130ef          	jal	42026130 <__wrap_esp_vorbis_dec_register>
4201268e:	f175                	bnez	a0,42012672 <decoder_register_codecs+0xa>
42012690:	77b350ef          	jal	4204860a <esp_opus_dec_register>
42012694:	fd79                	bnez	a0,42012672 <decoder_register_codecs+0xa>
42012696:	212250ef          	jal	420378a8 <esp_audio_simple_dec_register_default>
4201269a:	d175                	beqz	a0,4201267e <decoder_register_codecs+0x16>
4201269c:	bfd9                	j	42012672 <decoder_register_codecs+0xa>
