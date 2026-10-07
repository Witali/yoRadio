/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: esp_aac_dec_open @ ram:4300027c
 * Types and parameter counts are inferred; verify against disassembly. */

undefined4
esp_aac_dec_open(aac_analysis_config_t *config,uint param_2,aac_analysis_decoder_t **decoder)

{
  uint8_t uVar1;
  aac_analysis_decoder_t *decoder_00;
  undefined4 uVar2;
  aac_analysis_core_t *core;
  int iVar3;
  uint uVar4;
  uint32_t uVar5;
  uint32_t *puVar6;

  gp = &__global_pointer_;
  if ((decoder == (aac_analysis_decoder_t **)0x0) || ((param_2 & 0xfffffff7) != 0)) {
    uVar2 = esp_log_timestamp();
    esp_log(1,"ESP_AAC_DEC","E (%lu) %s: Invalid argument, decoder:%p cfg_sz:%d\n",uVar2,
            "ESP_AAC_DEC",decoder,param_2);
    uVar2 = 0xfffffffb;
  }
  else {
    decoder_00 = (aac_analysis_decoder_t *)media_lib_module_calloc("AUD_Codec",1,0x54);
    if (decoder_00 != (aac_analysis_decoder_t *)0x0) {
      uVar2 = PVMP4AudioDecoderGetMemRequirements();
      core = (aac_analysis_core_t *)media_lib_module_calloc("AUD_Codec",1,uVar2);
      decoder_00->core = core;
      if (core == (aac_analysis_core_t *)0x0) {
        uVar2 = esp_log_timestamp();
        esp_log(1,"ESP_AAC_DEC","E (%lu) %s: There is no enough memory for AAC buffer\n",uVar2);
        uVar2 = 0xfffffffe;
      }
      else {
        if (config == (aac_analysis_config_t *)0x0) {
          decoder_00->output_block_bytes = 0x1000;
          (decoder_00->external).output_format = 1;
          (decoder_00->external).consumed_bytes = 0;
          (decoder_00->external).remainder_bits = 0;
          (decoder_00->external).frame_length = 0;
          decoder_00->saved_plus_enabled = 0;
          uVar4 = 0;
          iVar3 = 0;
          uVar2 = 0xffffffff;
        }
        else {
          if (config->no_adts_header != 0) {
            puVar6 = &sample_rates_2;
            iVar3 = 0;
            do {
              uVar5 = *puVar6;
              puVar6 = puVar6 + 1;
              if (config->sample_rate == uVar5) {
                uVar4 = (uint)config->channels;
                uVar2 = 0;
                goto LAB_ram_430002e0;
              }
              iVar3 = iVar3 + 1;
            } while (iVar3 != 0xc);
            uVar2 = esp_log_timestamp();
            esp_log(1,"ESP_AAC_DEC","E (%lu) %s: Sample rate:%d not supported\n",uVar2,"ESP_AAC_DEC"
                    ,config->sample_rate);
            uVar2 = 0xfffffffb;
            goto LAB_ram_4300039e;
          }
          uVar4 = 0;
          iVar3 = 0;
          uVar2 = 0xffffffff;
LAB_ram_430002e0:
          uVar1 = config->plus_enabled;
          (decoder_00->external).consumed_bytes = 0;
          (decoder_00->external).remainder_bits = 0;
          (decoder_00->external).frame_length = 0;
          decoder_00->saved_plus_enabled = 0;
          decoder_00->output_block_bytes = 0x1000;
          (decoder_00->external).output_format = 1;
          if (uVar1 != 0) {
            (decoder_00->external).plus_enabled = 1;
            decoder_00->saved_plus_enabled = 1;
          }
        }
        iVar3 = PVMP4AudioDecoderInitLibrary(&decoder_00->external,core,uVar2,iVar3,uVar4);
        if (iVar3 == 0) {
          *decoder = decoder_00;
          gp = &__global_pointer_;
          return 0;
        }
        uVar2 = esp_log_timestamp();
        esp_log(1,"ESP_AAC_DEC","E (%lu) %s: Fail to init AAC library %d\n",uVar2,"ESP_AAC_DEC",
                0xfffffffe);
        uVar2 = 0xffffffff;
      }
LAB_ram_4300039e:
      esp_aac_dec_close(decoder_00);
      return uVar2;
    }
    uVar2 = esp_log_timestamp();
    esp_log(1,"ESP_AAC_DEC","E (%lu) %s: There is no enough memory for AAC decoder\n",uVar2);
    uVar2 = 0xfffffffe;
  }
  return uVar2;
}
