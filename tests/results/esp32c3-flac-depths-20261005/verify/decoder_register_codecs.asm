
idf\esp32c3-oled-native\build-flac-depths\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42012674 <decoder_register_codecs>:
42012674:	1101                	addi	sp,sp,-32
42012676:	ce06                	sw	ra,28(sp)
42012678:	7c83d0ef          	jal	4204fe40 <esp_mp3_dec_register>
4201267c:	c911                	beqz	a0,42012690 <decoder_register_codecs+0x1c>
4201267e:	c62a                	sw	a0,12(sp)
42012680:	30c250ef          	jal	4203798c <esp_audio_simple_dec_unregister_default>
42012684:	666280ef          	jal	4203acea <esp_audio_dec_unregister_all>
42012688:	4532                	lw	a0,12(sp)
4201268a:	40f2                	lw	ra,28(sp)
4201268c:	6105                	addi	sp,sp,32
4201268e:	8082                	ret
42012690:	06c290ef          	jal	4203b6fc <esp_aac_dec_register>
42012694:	f56d                	bnez	a0,4201267e <decoder_register_codecs+0xa>
42012696:	2a7130ef          	jal	4202613c <__wrap_esp_vorbis_dec_register>
4201269a:	f175                	bnez	a0,4201267e <decoder_register_codecs+0xa>
4201269c:	04e360ef          	jal	420486ea <esp_opus_dec_register>
420126a0:	fd79                	bnez	a0,4201267e <decoder_register_codecs+0xa>
420126a2:	2e6250ef          	jal	42037988 <esp_audio_simple_dec_register_default>
420126a6:	d175                	beqz	a0,4201268a <decoder_register_codecs+0x16>
420126a8:	bfd9                	j	4201267e <decoder_register_codecs+0xa>
