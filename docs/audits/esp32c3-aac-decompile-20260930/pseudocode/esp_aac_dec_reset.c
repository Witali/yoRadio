/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: esp_aac_dec_reset @ ram:42026d76
 * Types and parameter counts are inferred; verify against disassembly. */

undefined4 esp_aac_dec_reset(int *param_1)

{
  undefined4 uVar1;
  uint32_t uVar2;

  gp = &__global_pointer_;
  if (param_1 == (int *)0x0) {
    uVar2 = esp_log_timestamp();
    esp_log(1,"ESP_AAC_DEC","E (%lu) %s: Invalid argument, decoder %p\n",uVar2,"ESP_AAC_DEC",0);
    uVar1 = 0xfffffffb;
  }
  else {
    param_1[2] = 0;
    param_1[0xb] = (uint)*(byte *)(param_1 + 0x14);
    if (*param_1 != 0) {
      PVMP4AudioDecoderResetBuffer(*param_1);
    }
    uVar1 = 0;
  }
  return uVar1;
}
