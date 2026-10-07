/* Ghidra pseudocode; NOT original source.
 * ELF SHA-256: 6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d
 * Function: media_lib_free @ ram:4202439a
 * Types and parameter counts are inferred; verify against disassembly. */

void media_lib_free(void *param_1)

{
  gp = &__global_pointer_;
  if (param_1 != (void *)0x0) {
    free(param_1);
    return;
  }
  return;
}
