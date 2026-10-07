/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: esp_aac_dec_reset @ ram:43000468
 * Types and parameter counts are inferred; verify against disassembly. */

undefined4 esp_aac_dec_reset(undefined4 *param_1)

{
  undefined4 uVar1;

  gp = &__global_pointer_;
  if (param_1 == (undefined4 *)0x0) {
    uVar1 = esp_log_timestamp();
    esp_log(1,"ESP_AAC_DEC","E (%lu) %s: Invalid argument, decoder %p\n",uVar1,"ESP_AAC_DEC",0);
    uVar1 = 0xfffffffb;
  }
  else {
    param_1[2] = 0;
    param_1[0xb] = (uint)*(byte *)(param_1 + 0x14);
    if ((aac_core_abi_t *)*param_1 != (aac_core_abi_t *)0x0) {
      PVMP4AudioDecoderResetBuffer((aac_core_abi_t *)*param_1);
    }
    uVar1 = 0;
  }
  return uVar1;
}
