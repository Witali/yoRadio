/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: GetNrBitsAvailable @ ram:4300cbd8
 * Types and parameter counts are inferred; verify against disassembly. */

int GetNrBitsAvailable(int param_1)

{
  gp = &__global_pointer_;
  return *(int *)(param_1 + 0x10) - *(int *)(param_1 + 0xc);
}
