/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: GetNrBitsAvailable @ ram:420471e2
 * Types and parameter counts are inferred; verify against disassembly. */

int GetNrBitsAvailable(int param_1)

{
  gp = &__global_pointer_;
  return *(int *)(param_1 + 0x10) - *(int *)(param_1 + 0xc);
}
