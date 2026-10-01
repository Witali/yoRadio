/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: reset_adts_sync_para @ ram:43007558
 * Types and parameter counts are inferred; verify against disassembly. */

void reset_adts_sync_para(undefined4 *param_1)

{
  gp = &__global_pointer_;
  param_1[7] = 0;
  *param_1 = 0;
  param_1[0x229a] = 0;
  return;
}
