/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: byte_align @ ram:42040f4e
 * Types and parameter counts are inferred; verify against disassembly. */

void byte_align(int param_1)

{
  gp = &__global_pointer_;
  *(uint *)(param_1 + 4) = *(int *)(param_1 + 4) + 7U & 0xfffffff8;
  return;
}
