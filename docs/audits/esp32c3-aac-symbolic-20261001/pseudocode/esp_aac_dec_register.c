/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: esp_aac_dec_register @ ram:430004ba
 * Types and parameter counts are inferred; verify against disassembly. */

void esp_aac_dec_register(void)

{
  gp = &__global_pointer_;
  esp_audio_dec_register(0x20434141,&dec_lib_0);
  return;
}
