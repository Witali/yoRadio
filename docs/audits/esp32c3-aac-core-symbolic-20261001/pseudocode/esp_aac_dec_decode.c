/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: esp_aac_dec_decode @ ram:43000000
 * Types and parameter counts are inferred; verify against disassembly. */

undefined4
esp_aac_dec_decode(aac_analysis_decoder_t *decoder,aac_analysis_raw_t *input,
                  aac_analysis_output_t *output,aac_analysis_info_t *info)

{
  uint8_t *puVar1;
  int iVar2;
  undefined4 uVar3;
  aac_analysis_core_t *paVar4;
  uint32_t uVar5;
  uint uVar6;
  uint8_t *puVar7;
  int iVar8;
  uint32_t uVar9;
  uint uVar10;
  uint uVar11;

  gp = &__global_pointer_;
  if ((((decoder == (aac_analysis_decoder_t *)0x0) || (input == (aac_analysis_raw_t *)0x0)) ||
      (input->buffer == (uint8_t *)0x0)) ||
     ((output == (aac_analysis_output_t *)0x0 || (puVar1 = output->buffer, puVar1 == (uint8_t *)0x0)
      ))) {
    uVar3 = esp_log_timestamp();
    esp_log(1,"ESP_AAC_DEC",
            "E (%lu) %s: Invalid parameter, handle(%p), in_frame(%p), in_frame_buf(%p), out_frame(%p), out_frame_buf(%p) on %s\n"
            ,uVar3,"ESP_AAC_DEC",decoder,input,input->buffer,output,output->buffer,
            "esp_aac_dec_decode");
    uVar3 = 0xfffffffb;
  }
  else if (info == (aac_analysis_info_t *)0x0) {
    uVar3 = esp_log_timestamp();
    esp_log(1,"ESP_AAC_DEC","E (%lu) %s: Invalid parameter \'%s\' on %s\n",uVar3,"ESP_AAC_DEC",
            "aac information","esp_aac_dec_decode");
    uVar3 = 0xfffffffb;
  }
  else {
    uVar6 = decoder->output_block_bytes;
    uVar11 = output->length;
    if (uVar6 <= uVar11) {
      if (decoder->pending_output_bytes == 0) {
        puVar7 = input->buffer;
        uVar9 = input->length;
        uVar5 = input->length;
        (decoder->external).output = (int16_t *)puVar1;
        (decoder->external).input = puVar7;
        (decoder->external).input_length = uVar9;
        (decoder->external).input_capacity = uVar5;
        (decoder->external).consumed_bytes = 0;
        puVar1 = puVar1 + uVar6;
        if (uVar6 << 1 <= uVar11) goto LAB_ram_43000060;
        paVar4 = decoder->core;
        (decoder->external).output_plus = decoder->extra_output;
        iVar2 = PVMP4AudioDecodeFrame(&decoder->external,paVar4);
        while (iVar2 != 0) {
          if (iVar2 != 0x28) {
            uVar3 = esp_log_timestamp();
            esp_log(1,"ESP_AAC_DEC","E (%lu) %s: Failed to decode aac frame, error:%d.\n",uVar3,
                    "ESP_AAC_DEC",iVar2);
            return 0xffffffff;
          }
          if (decoder->extra_output != (int16_t *)0x0) {
            return 0xffffffff;
          }
          puVar1 = (uint8_t *)media_lib_module_malloc("AUD_Codec",decoder->output_block_bytes);
          decoder->extra_output = (int16_t *)puVar1;
          if (puVar1 == (uint8_t *)0x0) {
            uVar3 = esp_log_timestamp();
            esp_log(1,"ESP_AAC_DEC","E (%lu) %s: No memory for AAC-Plus output\n",uVar3);
            return 0xfffffffe;
          }
LAB_ram_43000060:
          paVar4 = decoder->core;
          (decoder->external).output_plus = (int16_t *)puVar1;
          iVar2 = PVMP4AudioDecodeFrame(&decoder->external,paVar4);
        }
        uVar10 = (decoder->external).requested_channels;
        info->sample_rate = (decoder->external).sample_rate;
        if (uVar10 == 0) {
          uVar10 = (decoder->external).encoded_channels;
        }
        info->channels = (uint8_t)uVar10;
        info->bits_per_sample = 0x10;
        iVar8 = (decoder->external).frame_length;
        uVar10 = uVar10 & 0xff;
        iVar2 = iVar8 * uVar10;
        uVar5 = (decoder->external).consumed_bytes;
        info->bitrate = (decoder->external).bitrate;
        output->decoded = iVar2 * 2;
        input->consumed = uVar5;
        if ((0x400 < iVar8) && (uVar11 < uVar6 << 1)) {
          output->decoded = uVar10 << 0xb;
          decoder->pending_output_bytes = (iVar2 + uVar10 * -0x400) * 2;
          input->consumed = 0;
        }
      }
      else {
        memcpy(puVar1,decoder->extra_output);
        uVar5 = (decoder->external).consumed_bytes;
        output->decoded = decoder->pending_output_bytes;
        input->consumed = uVar5;
        decoder->pending_output_bytes = 0;
      }
      return 0;
    }
    output->needed = uVar6;
    output->decoded = 0;
    uVar3 = 0xfffffff8;
  }
  return uVar3;
}
