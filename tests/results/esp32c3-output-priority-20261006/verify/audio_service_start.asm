
idf/esp32c3-oled-native/build-pipeline-profile/yoradio_esp32c3_oled_native.elf:     file format elf32-littleriscv


Disassembly of section .iram0.text:

Disassembly of section .flash.text:

42012806 <audio_service_start>:
42012806:	7179                	addi	sp,sp,-48
42012808:	3fc957b7          	lui	a5,0x3fc95
4201280c:	d606                	sw	ra,44(sp)
4201280e:	d422                	sw	s0,40(sp)
42012810:	b0a7ae23          	sw	a0,-1252(a5) # 3fc94b1c <s_state>
42012814:	76a0f0ef          	jal	42021f7e <native_audio_output_init>
42012818:	1c051163          	bnez	a0,420129da <audio_service_start+0x1d4>
4201281c:	6c2200ef          	jal	42032ede <audio_level_led_init>
42012820:	842a                	mv	s0,a0
42012822:	1e051b63          	bnez	a0,42012a18 <audio_service_start+0x212>
42012826:	3fc957b7          	lui	a5,0x3fc95
4201282a:	d04a                	sw	s2,32(sp)
4201282c:	b0878793          	addi	a5,a5,-1272 # 3fc94b08 <s_generation>
42012830:	0007a023          	sw	zero,0(a5)
42012834:	3fc957b7          	lui	a5,0x3fc95
42012838:	b0478793          	addi	a5,a5,-1276 # 3fc94b04 <s_decoder_target_codec>
4201283c:	0007a023          	sw	zero,0(a5)
42012840:	3fc957b7          	lui	a5,0x3fc95
42012844:	b0078793          	addi	a5,a5,-1280 # 3fc94b00 <s_decoder_released_generation>
42012848:	0007a023          	sw	zero,0(a5)
4201284c:	3fc957b7          	lui	a5,0x3fc95
42012850:	ae878793          	addi	a5,a5,-1304 # 3fc94ae8 <s_measured_bitrate_ready>
42012854:	00078023          	sb	zero,0(a5)
42012858:	3fc907b7          	lui	a5,0x3fc90
4201285c:	a6078223          	sb	zero,-1436(a5) # 3fc8fa64 <s_last_url>
42012860:	3fc957b7          	lui	a5,0x3fc95
42012864:	ae07ae23          	sw	zero,-1284(a5) # 3fc94afc <s_last_codec>
42012868:	135080ef          	jal	4201b19c <runtime_settings_get_audio_buffer_blocks>
4201286c:	64000793          	li	a5,1600
42012870:	02f50933          	mul	s2,a0,a5
42012874:	4601                	li	a2,0
42012876:	20800593          	li	a1,520
4201287a:	4505                	li	a0,1
4201287c:	2f4ff0ef          	jal	42111b70 <xQueueGenericCreate>
42012880:	3fc957b7          	lui	a5,0x3fc95
42012884:	b0a7ac23          	sw	a0,-1256(a5) # 3fc94b18 <s_commands>
42012888:	4581                	li	a1,0
4201288a:	854a                	mv	a0,s2
4201288c:	386660ef          	jal	42078c12 <xRingbufferCreate>
42012890:	3fc95737          	lui	a4,0x3fc95
42012894:	b0a72a23          	sw	a0,-1260(a4) # 3fc94b14 <s_encoded>
42012898:	4581                	li	a1,0
4201289a:	6509                	lui	a0,0x2
4201289c:	376660ef          	jal	42078c12 <xRingbufferCreate>
420128a0:	3fc957b7          	lui	a5,0x3fc95
420128a4:	b187a783          	lw	a5,-1256(a5) # 3fc94b18 <s_commands>
420128a8:	3fc956b7          	lui	a3,0x3fc95
420128ac:	b0a6a823          	sw	a0,-1264(a3) # 3fc94b10 <s_pcm>
420128b0:	3fc95737          	lui	a4,0x3fc95
420128b4:	c7b9                	beqz	a5,42012902 <audio_service_start+0xfc>
420128b6:	b1472783          	lw	a5,-1260(a4) # 3fc94b14 <s_encoded>
420128ba:	c521                	beqz	a0,42012902 <audio_service_start+0xfc>
420128bc:	c3b9                	beqz	a5,42012902 <audio_service_start+0xfc>
420128be:	853e                	mv	a0,a5
420128c0:	d226                	sw	s1,36(sp)
420128c2:	698660ef          	jal	42078f5a <xRingbufferGetCurFreeSize>
420128c6:	420127b7          	lui	a5,0x42012
420128ca:	3fc95737          	lui	a4,0x3fc95
420128ce:	3c1265b7          	lui	a1,0x3c126
420128d2:	800004b7          	lui	s1,0x80000
420128d6:	6609                	lui	a2,0x2
420128d8:	b0a72623          	sw	a0,-1268(a4) # 3fc94b0c <s_encoded_usable_size>
420128dc:	fff48813          	addi	a6,s1,-1 # 7fffffff <SYSTEM+0x1ff3ffff>
420128e0:	cc078513          	addi	a0,a5,-832 # 42011cc0 <stream_task>
420128e4:	80060613          	addi	a2,a2,-2048 # 1800 <CSR_UINTSTATUS+0xb4f>
420128e8:	4781                	li	a5,0
420128ea:	17458593          	addi	a1,a1,372 # 3c126174 <_esp_trace_encoder_array_end+0x6054>
420128ee:	4715                	li	a4,5
420128f0:	4681                	li	a3,0
420128f2:	00101097          	auipc	ra,0x101
420128f6:	558080e7          	jalr	1368(ra) # 42113e4a <xTaskCreatePinnedToCore>
420128fa:	4785                	li	a5,1
420128fc:	00f50b63          	beq	a0,a5,42012912 <audio_service_start+0x10c>
42012900:	5492                	lw	s1,36(sp)
42012902:	5902                	lw	s2,32(sp)
42012904:	10100413          	li	s0,257
42012908:	50b2                	lw	ra,44(sp)
4201290a:	8522                	mv	a0,s0
4201290c:	5422                	lw	s0,40(sp)
4201290e:	6145                	addi	sp,sp,48
42012910:	8082                	ret
42012912:	cc2a                	sw	a0,24(sp)
42012914:	3c1265b7          	lui	a1,0x3c126
42012918:	42011537          	lui	a0,0x42011
4201291c:	18458593          	addi	a1,a1,388 # 3c126184 <_esp_trace_encoder_array_end+0x6064>
42012920:	c8050513          	addi	a0,a0,-896 # 42010c80 <decoder_task>
42012924:	fff48813          	addi	a6,s1,-1
42012928:	4781                	li	a5,0
4201292a:	471d                	li	a4,7
4201292c:	4681                	li	a3,0
4201292e:	6611                	lui	a2,0x4
42012930:	00101097          	auipc	ra,0x101
42012934:	51a080e7          	jalr	1306(ra) # 42113e4a <xTaskCreatePinnedToCore>
42012938:	48e2                	lw	a7,24(sp)
4201293a:	fd1513e3          	bne	a0,a7,42012900 <audio_service_start+0xfa>
4201293e:	6605                	lui	a2,0x1
42012940:	3c1265b7          	lui	a1,0x3c126
42012944:	42011537          	lui	a0,0x42011
42012948:	fff48813          	addi	a6,s1,-1
4201294c:	80060613          	addi	a2,a2,-2048 # 800 <ALIGN_VECTOR_TABLE+0x700>
42012950:	19458593          	addi	a1,a1,404 # 3c126194 <_esp_trace_encoder_array_end+0x6074>
42012954:	88850513          	addi	a0,a0,-1912 # 42010888 <output_task>
42012958:	4781                	li	a5,0
4201295a:	4721                	li	a4,8
4201295c:	4681                	li	a3,0
4201295e:	00101097          	auipc	ra,0x101
42012962:	4ec080e7          	jalr	1260(ra) # 42113e4a <xTaskCreatePinnedToCore>
42012966:	4362                	lw	t1,24(sp)
42012968:	f8651ce3          	bne	a0,t1,42012900 <audio_service_start+0xfa>
4201296c:	fe376097          	auipc	ra,0xfe376
42012970:	a60080e7          	jalr	-1440(ra) # 403883cc <esp_log_timestamp>
42012974:	ce2a                	sw	a0,28(sp)
42012976:	43b0f0ef          	jal	420225b0 <native_audio_output_name>
4201297a:	cc2a                	sw	a0,24(sp)
4201297c:	4511                	li	a0,4
4201297e:	e6def0ef          	jal	420027ea <heap_caps_get_free_size>
42012982:	3c126337          	lui	t1,0x3c126
42012986:	47e2                	lw	a5,24(sp)
42012988:	46f2                	lw	a3,28(sp)
4201298a:	80c30713          	addi	a4,t1,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
4201298e:	3c126637          	lui	a2,0x3c126
42012992:	884a                	mv	a6,s2
42012994:	85ba                	mv	a1,a4
42012996:	1a460613          	addi	a2,a2,420 # 3c1261a4 <_esp_trace_encoder_array_end+0x6084>
4201299a:	6889                	lui	a7,0x2
4201299c:	c02a                	sw	a0,0(sp)
4201299e:	450d                	li	a0,3
420129a0:	fe376097          	auipc	ra,0xfe376
420129a4:	924080e7          	jalr	-1756(ra) # 403882c4 <esp_log>
420129a8:	fe376097          	auipc	ra,0xfe376
420129ac:	a24080e7          	jalr	-1500(ra) # 403883cc <esp_log_timestamp>
420129b0:	3c126337          	lui	t1,0x3c126
420129b4:	80c30713          	addi	a4,t1,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
420129b8:	3c126637          	lui	a2,0x3c126
420129bc:	86aa                	mv	a3,a0
420129be:	85ba                	mv	a1,a4
420129c0:	1f460613          	addi	a2,a2,500 # 3c1261f4 <_esp_trace_encoder_array_end+0x60d4>
420129c4:	48a1                	li	a7,8
420129c6:	481d                	li	a6,7
420129c8:	4795                	li	a5,5
420129ca:	450d                	li	a0,3
420129cc:	fe376097          	auipc	ra,0xfe376
420129d0:	8f8080e7          	jalr	-1800(ra) # 403882c4 <esp_log>
420129d4:	5492                	lw	s1,36(sp)
420129d6:	5902                	lw	s2,32(sp)
420129d8:	bf05                	j	42012908 <audio_service_start+0x102>
420129da:	842a                	mv	s0,a0
420129dc:	fe376097          	auipc	ra,0xfe376
420129e0:	9f0080e7          	jalr	-1552(ra) # 403883cc <esp_log_timestamp>
420129e4:	3c126737          	lui	a4,0x3c126
420129e8:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
420129ec:	3c13e7b7          	lui	a5,0x3c13e
420129f0:	3c126637          	lui	a2,0x3c126
420129f4:	86aa                	mv	a3,a0
420129f6:	85ba                	mv	a1,a4
420129f8:	4505                	li	a0,1
420129fa:	5b078793          	addi	a5,a5,1456 # 3c13e5b0 <__FUNCTION__.0>
420129fe:	11460613          	addi	a2,a2,276 # 3c126114 <_esp_trace_encoder_array_end+0x5ff4>
42012a02:	62a00813          	li	a6,1578
42012a06:	fe376097          	auipc	ra,0xfe376
42012a0a:	8be080e7          	jalr	-1858(ra) # 403882c4 <esp_log>
42012a0e:	50b2                	lw	ra,44(sp)
42012a10:	8522                	mv	a0,s0
42012a12:	5422                	lw	s0,40(sp)
42012a14:	6145                	addi	sp,sp,48
42012a16:	8082                	ret
42012a18:	fe376097          	auipc	ra,0xfe376
42012a1c:	9b4080e7          	jalr	-1612(ra) # 403883cc <esp_log_timestamp>
42012a20:	3c126737          	lui	a4,0x3c126
42012a24:	80c70713          	addi	a4,a4,-2036 # 3c12580c <_esp_trace_encoder_array_end+0x56ec>
42012a28:	3c13e7b7          	lui	a5,0x3c13e
42012a2c:	3c126637          	lui	a2,0x3c126
42012a30:	86aa                	mv	a3,a0
42012a32:	85ba                	mv	a1,a4
42012a34:	5b078793          	addi	a5,a5,1456 # 3c13e5b0 <__FUNCTION__.0>
42012a38:	14460613          	addi	a2,a2,324 # 3c126144 <_esp_trace_encoder_array_end+0x6024>
42012a3c:	62c00813          	li	a6,1580
42012a40:	4505                	li	a0,1
42012a42:	fe376097          	auipc	ra,0xfe376
42012a46:	882080e7          	jalr	-1918(ra) # 403882c4 <esp_log>
42012a4a:	bd7d                	j	42012908 <audio_service_start+0x102>
