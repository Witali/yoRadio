/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: esp_aac_dec_close @ ram:42026b76
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
