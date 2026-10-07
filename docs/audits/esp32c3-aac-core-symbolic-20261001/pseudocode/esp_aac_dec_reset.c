/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: esp_aac_dec_reset @ ram:43000468
 * Types and parameter counts are inferred; verify against disassembly. */

undefined4 esp_aac_dec_reset(aac_analysis_decoder_t *decoder)

{
  undefined4 uVar1;
  aac_analysis_core_t *core;

  gp = &__global_pointer_;
  if (decoder == (aac_analysis_decoder_t *)0x0) {
    uVar1 = esp_log_timestamp();
    esp_log(1,"ESP_AAC_DEC","E (%lu) %s: Invalid argument, decoder %p\n",uVar1,"ESP_AAC_DEC",0);
    uVar1 = 0xfffffffb;
  }
  else {
    core = decoder->core;
    decoder->pending_output_bytes = 0;
    (decoder->external).plus_enabled = (uint)decoder->saved_plus_enabled;
    if (core != (aac_analysis_core_t *)0x0) {
      PVMP4AudioDecoderResetBuffer(core);
    }
    uVar1 = 0;
  }
  return uVar1;
}
