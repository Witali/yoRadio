/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: codec_register.part.0 @ ram:42026258
 * Types and parameter counts are inferred; verify against disassembly. */

undefined4 codec_register_part_0(void)

{
  uint32_t uVar1;

  gp = &__global_pointer_;
  uVar1 = esp_log_timestamp();
  esp_log(1,"AUD_CODEC_REG","E (%lu) %s: No memory for codec node\n",uVar1);
  return 0xfffffffe;
}
