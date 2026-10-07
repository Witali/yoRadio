/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: esp_aac_dec_close @ ram:43000230
 * Types and parameter counts are inferred; verify against disassembly. */

undefined4 esp_aac_dec_close(aac_analysis_decoder_t *decoder)

{
  gp = &__global_pointer_;
  if (decoder != (aac_analysis_decoder_t *)0x0) {
    if (decoder->core != (aac_analysis_core_t *)0x0) {
      PVMP4AudioDecoderDeInit(&decoder->external,decoder->core);
      decoder->core = (aac_analysis_core_t *)0x0;
    }
    if (decoder->extra_output != (int16_t *)0x0) {
      media_lib_free();
      if (decoder->core != (aac_analysis_core_t *)0x0) {
        media_lib_free();
      }
    }
    media_lib_free(decoder);
    return 0;
  }
  return 0xfffffffb;
}
