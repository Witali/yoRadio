/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f
 * Function: byte_align @ ram:43000c0c
 * Types and parameter counts are inferred; verify against disassembly. */

void byte_align(int param_1)

{
  gp = &__global_pointer_;
  *(uint *)(param_1 + 4) = *(int *)(param_1 + 4) + 7U & 0xfffffff8;
  return;
}
