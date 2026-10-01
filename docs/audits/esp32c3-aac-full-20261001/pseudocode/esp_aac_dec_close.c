/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: esp_aac_dec_close @ ram:43000230
 * Types and parameter counts are inferred; verify against disassembly. */

undefined4 esp_aac_dec_close(int *param_1)

{
  gp = &__global_pointer_;
  if (param_1 != (int *)0x0) {
    if (*param_1 != 0) {
      PVMP4AudioDecoderDeInit(param_1 + 4);
      *param_1 = 0;
    }
    if (param_1[1] != 0) {
      media_lib_free();
      if (*param_1 != 0) {
        media_lib_free();
      }
    }
    media_lib_free(param_1);
    return 0;
  }
  return 0xfffffffb;
}
