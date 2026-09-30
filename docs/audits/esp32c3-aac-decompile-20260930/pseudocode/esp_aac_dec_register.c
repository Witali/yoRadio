/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: esp_aac_dec_register @ ram:42026dc0
 * Types and parameter counts are inferred; verify against disassembly. */

void esp_aac_dec_register(void)

{
  gp = &__global_pointer_;
  esp_audio_dec_register(0x20434141,&dec_lib_0);
  return;
}
