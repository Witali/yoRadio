
idf\esp32c3-oled-native\build-output-dma\yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42012556 <decoder_register_codecs>:
42012556:	1101                	addi	sp,sp,-32
42012558:	ce06                	sw	ra,28(sp)
4201255a:	15e3c0ef          	jal	4204e6b8 <esp_mp3_dec_register>
4201255e:	c911                	beqz	a0,42012572 <decoder_register_codecs+0x1c>
42012560:	c62a                	sw	a0,12(sp)
42012562:	4a3230ef          	jal	42036204 <esp_audio_simple_dec_unregister_default>
42012566:	7fd260ef          	jal	42039562 <esp_audio_dec_unregister_all>
4201256a:	4532                	lw	a0,12(sp)
4201256c:	40f2                	lw	ra,28(sp)
4201256e:	6105                	addi	sp,sp,32
42012570:	8082                	ret
42012572:	203270ef          	jal	42039f74 <esp_aac_dec_register>
42012576:	f56d                	bnez	a0,42012560 <decoder_register_codecs+0xa>
42012578:	5a6130ef          	jal	42025b1e <__wrap_esp_vorbis_dec_register>
4201257c:	f175                	bnez	a0,42012560 <decoder_register_codecs+0xa>
4201257e:	1e5340ef          	jal	42046f62 <esp_opus_dec_register>
42012582:	fd79                	bnez	a0,42012560 <decoder_register_codecs+0xa>
42012584:	47d230ef          	jal	42036200 <esp_audio_simple_dec_register_default>
42012588:	d175                	beqz	a0,4201256c <decoder_register_codecs+0x16>
4201258a:	bfd9                	j	42012560 <decoder_register_codecs+0xa>
